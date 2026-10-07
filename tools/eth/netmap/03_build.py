"""Build the ETH counted-once market map: snapshot (2026-10-02) and 24 month-ends (2024-10 .. 2026-09).

Inputs: raw/eth/netmap-2026-10-07/{screen.json, proto/*.json.gz, yield_pools.json, pool_charts/},
        eth/data/carry-history-all-eth.csv and data/eth/carry-status-and-capital.csv (on-chain product books).
Outputs (data/eth/netmap/): market_map_current.csv, market_map_history_monthly.csv, category_history_monthly.csv,
        netting_ledger.csv, map.json (everything the site needs), plus a printed summary.

Rules:
- Every product counts once. A staking or restaking token held inside another counted product leaves its issuer's row.
- Products report equity: a looped vault counts what its depositors own; the ETH it borrowed is the lenders' and stays
  with the staking token's issuer (the borrowed ETH was staked) or, if idle, in money markets.
- Money markets and CDPs count plain ETH/WETH only (idle supply / collateral); staking tokens posted there stay with
  their issuer. Both are off by default.
- Restaking platforms (EigenLayer, Symbiotic) count only what restaking-token issuers on the map have not already
  counted (estimate, flagged).
- On-chain product books replace DefiLlama rows for the examined carry products.
"""
import csv, collections, datetime, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import OUT, RAW, ROOT, eth_part, load, month_points, pick, price, series
from products import BY_DL_CATEGORY, CATEGORIES, ISSUERS
import decisions as DEC

os.makedirs(OUT, exist_ok=True)
PTS = month_points()
LABELS = [p[0] for p in PTS]
SNAP = LABELS[-1]


def plain_eth(br):
    return sum(v for k, v in br.items() if k in ('ETH', 'WETH', 'WETH.E', 'ETH.E', 'SPETH'))  # spETH: WETH lent into SparkLend


def lst_holdings(br, products=True):
    """{row slug: value} for staking tokens (and, with products=True, tokens of other products on the map) in a breakdown"""
    out = collections.defaultdict(float)
    for k, v in br.items():
        if k in ISSUERS:
            out[ISSUERS[k]] += v
        elif products and k in DEC.PRODUCT_TOKENS:
            out[DEC.PRODUCT_TOKENS[k]] += v
    return out


def held_elsewhere(k):
    """tokens whose ETH another row counts: staking tokens and tokens of products on the map"""
    return k in ISSUERS or k in DEC.PRODUCT_TOKENS


def borrowed_part(slug, pdate):
    """ETH-family value lent out (DefiLlama '{chain}-borrowed' keys), USD by symbol"""
    out = collections.defaultdict(float)
    for k in (load(slug).get('chainTvls') or {}):
        if k.endswith('-borrowed'):
            tok, _d = pick(series(slug, k), pdate)
            for sym, v in eth_part(tok)[1].items():
                out[sym] += v
    return out


def dl_rows():
    """DefiLlama rows kept by the screen, with per-period token breakdowns (USD)"""
    screen = json.load(open(os.path.join(RAW, 'screen.json')))
    for slug, cat in DEC.EXTRA_ROWS.items():  # credit rows the idle-only screen misses
        if slug not in screen:
            d = load(slug)
            screen[slug] = dict(name=d.get('name'), category=d.get('category'), snap_eth=0.0)
    rows = {}
    for slug, s in screen.items():
        if slug in DEC.EXCLUDE:
            continue
        cat = DEC.CATEGORY.get(slug) or DEC.EXTRA_ROWS.get(slug) or BY_DL_CATEGORY.get(s['category'])
        if cat is None:
            DEC.UNCLASSIFIED.append((slug, s['category'], round(s['snap_eth'])))
            continue
        ser = series(slug)
        per = {}
        for label, pdate, _ in PTS:
            tok, _d = pick(ser, pdate)
            if tok is None:
                continue
            usd, br = eth_part(tok)
            if slug in DEC.CREDIT_SUPPLIED:  # supplied = idle + lent out
                for sym, v in borrowed_part(slug, pdate).items():
                    br[sym] = br.get(sym, 0.0) + v
            per[label] = br
        rows[slug] = dict(slug=slug, name=DEC.NAMES.get(slug, s['name']), dl_category=s['category'], category=cat,
                          kind=DEC.KIND.get(slug) or DEC.kind_default(cat), source='DefiLlama protocol token breakdown', per=per)
    return rows


def pool_rows():
    """DEX projects without a token breakdown: ETH side of each ETH pool above $1M (DefiLlama yields pools)."""
    pools = json.load(open(os.path.join(RAW, 'yield_pools.json')))['data']
    charts_dir = os.path.join(RAW, 'pool_charts')
    out = {}
    for proj, (name, kind) in DEC.POOL_PROJECTS.items():
        if 'pools:' + proj in DEC.EXCLUDE:
            continue
        per = collections.defaultdict(lambda: collections.defaultdict(float))
        n = 0
        for p in pools:
            if p['project'] != proj or p['tvlUsd'] < 1e6:
                continue
            parts = [x.upper() for x in p['symbol'].replace('/', '-').split('-')]
            share = DEC.pool_eth_share(parts)
            if share <= 0:
                continue
            path = os.path.join(charts_dir, p['pool'] + '.json')
            if not os.path.exists(path):
                continue
            n += 1
            ch = {datetime.date.fromisoformat(r['timestamp'][:10]): r['tvlUsd'] for r in json.load(open(path)).get('data', [])}
            for label, pdate, prdate in PTS:
                v, _ = pick(ch, prdate, back=3)
                if v:
                    # the ETH side stays plain ETH; the staking-token side of an ETH/LST pool stays with its issuer
                    per[label]['WETH'] += v * share
        out['pools:' + proj] = dict(slug='pools:' + proj, name=name, dl_category='Dexs', category='farming', kind=kind,
                                    source=f'DefiLlama yields pools above $1M ({n} pools), ETH side only', per=per)
    return out


def carry_rows():
    """on-chain whole-product books of the examined carry products (ETH)"""
    hist = list(csv.DictReader(open(os.path.join(ROOT, 'eth', 'data', 'carry-history-all-eth.csv'))))
    snap = {r['product']: float(r['whole_book_ETH']) for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'eth', 'carry-status-and-capital.csv')))}
    out = {}
    for prod, meta in DEC.CARRY.items():
        vals = {}
        for r in hist:
            v = r.get(prod + '_ETH')
            if v not in (None, ''):
                vals[r['month']] = float(v)
        vals[SNAP] = meta.get('snapshot_eth', snap.get(prod))
        out['carry:' + meta['id']] = dict(slug='carry:' + meta['id'], name=meta['name'], dl_category='on-chain',
                                          category=meta['category'], kind=meta.get('kind'), source='on-chain product book (this study)',
                                          eth=vals, issuer_mix=meta['issuer_mix'], replaces=meta.get('replaces', {}))
    return out


def build():
    dl = dl_rows()
    pools = pool_rows()
    carry = carry_rows()
    # rows read only to net others (excluded from the map themselves)
    dl_src = {src: {label: eth_part(pick(series(src), pdate)[0])[1] for label, pdate, _ in PTS} for src, *_ in DEC.BASE_VALUED.values()}
    ledger = []
    result = {}  # slug -> {label: eth}
    meta = {}
    replaced = {d for r in carry.values() for d in r['replaces']}
    carry_tokens = {k for k, t in DEC.PRODUCT_TOKENS.items() if t.startswith('carry:')}

    def row_value(slug, r, br):
        """step-1 value of a DefiLlama row (ETH) and the breakdown whose tokens it takes from other rows (None: takes none)"""
        cat = r['category']
        if cat in ('lending', 'cdp'):
            return plain_eth(br), None
        if r.get('kind') == 'pools' and not slug.startswith('pools:'):
            # DEX, perp and bridge pools count the ETH no other row counts: the staking-token or product-token side of a
            # pool stays with its row, as in the yields-pool rows and the BTC map
            return sum(v for k, v in br.items() if not held_elsewhere(k)), None
        if slug not in replaced:  # tokens of an on-chain carry book stay in the book; the holder does not count them
            br = {k: v for k, v in br.items() if k not in carry_tokens}
        return sum(br.values()) * DEC.SCALE.get(slug, 1.0), br

    # leftovers: a row on the LEFTOVER list whose own balance stays flat (<0.5% change) for 3+ consecutive month-ends counts
    # as 0 from the start of the run. Decided on the row's own value before netting, so a leftover row takes nothing out
    # of the issuers whose tokens it holds (they stay counted there).
    leftover_from = {}
    for slug in DEC.LEFTOVER:
        r = dl.get(slug)
        if not r:
            continue
        v = {}
        for label, pdate, _ in PTS:
            if r['per'].get(label) is not None:
                v[label] = row_value(slug, r, {k: x / price(pdate) for k, x in r['per'][label].items()})[0]
        seq = [l for l in LABELS if l in v]
        for i in range(len(seq)):
            run = seq[i:i + 3]
            if len(run) == 3 and all(v[run[0]] > 0 and abs(v[x] / v[run[0]] - 1) < 0.005 for x in run):
                leftover_from[slug] = seq[i]
                break

    for label, pdate, _ in PTS:
        pr = price(pdate)
        vals, sub = {}, collections.defaultdict(float)  # sub[row] = ETH to take out of a staking-token issuer or product row
        # 1. DefiLlama rows (gross ETH-family value; tokens they hold are recorded, taken out of their rows in step 5)
        held, ebr = {}, {}
        for slug, r in list(dl.items()) + list(pools.items()):
            br = r['per'].get(label)
            if br is None:
                continue
            br = {k: v / pr for k, v in br.items()}
            ebr[slug] = br
            if slug in DEC.ONCHAIN_ISSUER:
                oc = json.load(open(os.path.join(OUT, DEC.ONCHAIN_ISSUER[slug])))
                vals[slug] = oc[label]['eth'] if label in oc else sum(br.values())
                continue
            if slug in DEC.RESTAKING_PLATFORMS:
                vals[slug] = None  # computed after the issuers
                continue
            v, hbr = row_value(slug, r, br)
            if slug in leftover_from and label >= leftover_from[slug]:
                ledger.append((label, slug, slug, v, 'leftover: balance unchanged since ' + leftover_from[slug]))
                vals[slug] = 0.0
                continue
            vals[slug] = v
            if hbr is not None and (slug not in DEC.ISSUER_SLUGS or slug in DEC.LRT_ISSUERS or slug in DEC.HOLDS_TOKENS):
                held[slug] = (v, {i: x for i, x in lst_holdings(hbr).items() if i != slug})
        # 2. on-chain carry rows replace the DefiLlama rows that already count them
        taken = collections.defaultdict(float)
        for slug, r in carry.items():
            v = r['eth'].get(label)
            if v is None:
                continue
            vals[slug] = v
            for iss, w in r['issuer_mix'].items():
                sub[iss] += v * w
                ledger.append((label, slug, iss, v * w, 'on-chain product book; staking token per research'))
            left = v
            for dslug in r['replaces']:
                if vals.get(dslug):
                    take = min(vals[dslug], left)
                    vals[dslug] -= take
                    left -= take
                    taken[(slug, dslug)] += take
                    ledger.append((label, slug, dslug, take, 'DefiLlama row already counts this product'))
        # 3. explicit overlaps between rows
        for a, b, how in DEC.OVERLAPS:
            if vals.get(a) is not None and vals.get(b) is not None:
                take = min(vals[b], how(vals, label))
                vals[b] -= take
                taken[(a, b)] += take
                ledger.append((label, a, b, take, 'nested holding'))
        # rows that value another protocol's vaults in their base asset (Veda books ether.fi Liquid vaults as WETH)
        for slug, (src, tok, iss, book) in DEC.BASE_VALUED.items():
            if slug not in held or not vals.get(slug):
                continue
            br = ebr[slug]
            sbr = dl_src.get(src, {}).get(label) or {}
            base = sbr.get(tok, 0.0) / pr - sum(t for (a, b), t in taken.items() if a == book and b == slug)
            weth = br.get('WETH', 0.0) - sum(t for (a, b), t in taken.items() if b == slug and a.startswith('carry:'))
            other = {i: max(0.0, x - sum(t for (a, b), t in taken.items() if b == slug and a == 'mantle-restaking'))
                     if i == 'meth-protocol' else x for i, x in held[slug][1].items()}
            extra = max(0.0, min(weth, base, vals[slug] - sum(other.values())))
            if extra > 0:
                other[iss] = other.get(iss, 0.0) + extra
            for i, x in other.items():
                if x > 0:
                    sub[i] += x
                    ledger.append((label, slug, i, x, 'staking token held by a counted product' if i != iss else
                                   'ether.fi Liquid vaults booked as WETH by the Veda adapter hold eETH'))
            del held[slug]
        # tokens held by DefiLlama rows, scaled to what is left of the row after steps 2-3
        for slug, (gross, hold) in held.items():
            f = (vals[slug] / gross) if gross else 0.0
            for iss, x in hold.items():
                if x * f > 0:
                    sub[iss] += x * f
                    ledger.append((label, slug, iss, x * f, 'staking token held by a counted product' if iss not in
                                   DEC.PRODUCT_TOKENS.values() else 'product token held by a counted product'))
        # 4. restaking platforms: what restaking-token issuers on the map have not already counted
        lrt_total = sum(vals.get(s) or 0 for s in DEC.LRT_ISSUERS if s in vals)
        for plat, deducts in DEC.RESTAKING_PLATFORMS.items():
            r = dl.get(plat)
            if not r or r['per'].get(label) is None:
                continue
            br = ebr[plat]
            gross = sum(br.values())
            inner = sum(vals.get(s) or 0 for s in deducts) if deducts != 'LRT' else lrt_total
            if plat == 'symbiotic':  # positions of counted rows that sit in a Symbiotic vault, the smaller of the two each month
                for s2, (t_row, t_plat) in DEC.SYMBIOTIC_ALSO.items():
                    if vals.get(s2):
                        x = min((ebr.get(s2) or {}).get(t_row, 0.0), br.get(t_plat, 0.0), vals[s2])
                        inner += x
                        if x >= 1:
                            ledger.append((label, s2, plat, x, 'position in a Symbiotic vault, counted in the row that holds it'))
            net = max(0.0, gross - inner)
            vals[plat] = net
            ledger.append((label, plat, plat, gross - net, 'restaking-token issuers already count this'))
            if gross > 0 and net > 0:
                for iss, x in lst_holdings(br, products=False).items():
                    sub[iss] += x * net / gross
        # 5. take held tokens out of their issuer or product rows
        for iss, x in sub.items():
            if iss in vals and vals[iss] is not None:
                take = min(vals[iss], x)
                vals[iss] -= take
                if x - take > 1:
                    ledger.append((label, iss, iss, x - take, 'held exceeds issuer row (cross-chain supply or adapter gap); floored at 0'))
        for slug, v in vals.items():
            result.setdefault(slug, {})[label] = v
    # months without dollar debt leave carry (split into a second row in the category the product worked in)
    eq = json.load(open(os.path.join(ROOT, 'data', 'eth', 'economic_questions.json')))
    debt = {p['id']: {h['month']: h.get('debtUSD') for h in p['history']} | {SNAP: p['current'].get('debtUSD')} for p in eq['products']}
    extra_meta = {}
    for cid, (eid, cat_then) in DEC.DEBT_MONTHS.items():
        slug = 'carry:' + cid
        if slug not in result:
            continue
        d = debt.get(eid, {})
        moved = {}
        for l, v in list(result[slug].items()):
            if v and (eid is None or (d.get(l) or 0) < 10000):  # under $10k of dollar debt: not a carry month
                moved[l] = v
                result[slug][l] = 0.0
        if moved:
            result[slug + ':nodebt'] = moved
            extra_meta[slug + ':nodebt'] = (slug, cat_then)
    for d in (dl, pools, carry):
        for slug, r in d.items():
            meta[slug] = {k: r.get(k) for k in ('slug', 'name', 'dl_category', 'category', 'kind', 'source')}
    for s2, (base, cat_then) in extra_meta.items():
        meta[s2] = dict(meta[base]); meta[s2].update(slug=s2, name=meta[base]['name'] + ' (months without dollar debt)', category=cat_then, kind='vaults' if cat_then == 'farming' else None,
                                                    source=meta[base]['source'] + '; months without dollar debt')
    return result, meta, ledger


def main():
    result, meta, ledger = build()
    prices = {label: price(pdate) for label, pdate, _ in PTS}
    with open(os.path.join(OUT, 'market_map_history_monthly.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['month', 'slug', 'product', 'category', 'kind', 'eth', 'usd', 'eth_usd'])
        for slug, vals in sorted(result.items()):
            for label in LABELS:
                v = vals.get(label)
                if v is not None:
                    w.writerow([label, slug, meta[slug]['name'], meta[slug]['category'], meta[slug]['kind'] or '', round(v, 4), round(v * prices[label], 2), round(prices[label], 4)])
    cur = sorted(((s, v.get(SNAP)) for s, v in result.items() if v.get(SNAP)), key=lambda x: -x[1])
    with open(os.path.join(OUT, 'market_map_current.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['slug', 'product', 'category', 'kind', 'eth', 'usd', 'source'])
        for s, v in cur:
            if v >= 0.5:
                w.writerow([s, meta[s]['name'], meta[s]['category'], meta[s]['kind'] or '', round(v, 2), round(v * prices[SNAP], 0), meta[s]['source']])
    with open(os.path.join(OUT, 'netting_ledger.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['month', 'from', 'to', 'eth', 'reason'])
        for r in sorted(ledger, key=lambda r: (r[0], r[1], r[2], r[4], r[3])):
            if r[3] >= 1:
                w.writerow([r[0], r[1], r[2], round(r[3], 2), r[4]])
    cats = collections.defaultdict(lambda: collections.defaultdict(float))
    for slug, vals in result.items():
        for label, v in vals.items():
            if v:
                cats[label][meta[slug]['category']] += v
    with open(os.path.join(OUT, 'category_history_monthly.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        ids = [c['id'] for c in CATEGORIES]
        w.writerow(['month', *ids, 'default_total_eth', 'eth_usd'])
        for label in LABELS:
            w.writerow([label, *[round(cats[label][i], 1) for i in ids],
                        round(sum(cats[label][c['id']] for c in CATEGORIES if c['default']), 1), round(prices[label], 2)])
    json.dump(dict(snapshot=SNAP, months=LABELS, prices=prices, categories=CATEGORIES, meta=meta,
                   values={s: v for s, v in result.items()}, unclassified=DEC.UNCLASSIFIED),
              open(os.path.join(OUT, 'map.json'), 'w'), indent=1)
    # summary
    print('snapshot', SNAP, 'ETH/USD', round(prices[SNAP], 2))
    for c in CATEGORIES:
        rows = [(s, v) for s, v in cur if meta[s]['category'] == c['id'] and v >= 0.5]
        print(f"{c['label']:20} {sum(v for _, v in rows):>12,.0f} ETH  {len(rows):3} products  {'default' if c['default'] else 'optional'}")
    tot = sum(v for s, v in cur if next(c for c in CATEGORIES if c['id'] == meta[s]['category'])['default'])
    print(f"{'default total':20} {tot:>12,.0f} ETH  ${tot * prices[SNAP] / 1e9:.2f}B")
    if DEC.UNCLASSIFIED:
        print('unclassified:', DEC.UNCLASSIFIED)


if __name__ == '__main__':
    main()
