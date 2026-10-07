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


def lst_holdings(br):
    """{issuer_slug: usd} for staking tokens in a token breakdown"""
    out = collections.defaultdict(float)
    for k, v in br.items():
        if k in ISSUERS:
            out[ISSUERS[k]] += v
    return out


def dl_rows():
    """DefiLlama rows kept by the screen, with per-period token breakdowns (USD)"""
    screen = json.load(open(os.path.join(RAW, 'screen.json')))
    rows = {}
    for slug, s in screen.items():
        if slug in DEC.EXCLUDE:
            continue
        cat = DEC.CATEGORY.get(slug) or BY_DL_CATEGORY.get(s['category'])
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
    ledger = []
    result = {}  # slug -> {label: eth}
    meta = {}
    for label, pdate, _ in PTS:
        pr = price(pdate)
        vals, sub = {}, collections.defaultdict(float)  # sub[issuer] = ETH to take out of the issuer row
        # 1. DefiLlama rows (gross ETH-family value; staking tokens they hold are recorded, taken out of issuers in step 5)
        held = {}
        for slug, r in list(dl.items()) + list(pools.items()):
            br = r['per'].get(label)
            if br is None:
                continue
            br = {k: v / pr for k, v in br.items()}
            cat = r['category']
            if slug in DEC.ONCHAIN_ISSUER:
                oc = json.load(open(os.path.join(OUT, DEC.ONCHAIN_ISSUER[slug])))
                vals[slug] = oc[label]['eth'] if label in oc else sum(br.values())
                continue
            if cat in ('lending', 'cdp'):
                vals[slug] = plain_eth(br)
            elif slug in DEC.RESTAKING_PLATFORMS:
                vals[slug] = None  # computed after the issuers
            else:
                vals[slug] = sum(br.values()) * DEC.SCALE.get(slug, 1.0)
                if slug not in DEC.ISSUER_SLUGS or slug in DEC.LRT_ISSUERS or slug in DEC.HOLDS_TOKENS:
                    held[slug] = (vals[slug], {i: x for i, x in lst_holdings(br).items() if i != slug})
        # 2. on-chain carry rows replace the DefiLlama rows that already count them
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
                    ledger.append((label, slug, dslug, take, 'DefiLlama row already counts this product'))
        # 3. explicit overlaps between rows
        for a, b, how in DEC.OVERLAPS:
            if vals.get(a) is not None and vals.get(b) is not None:
                take = min(vals[b], how(vals, label))
                vals[b] -= take
                ledger.append((label, a, b, take, 'nested holding'))
        # staking tokens held by DefiLlama rows, scaled to what is left of the row after steps 2-3
        for slug, (gross, hold) in held.items():
            f = (vals[slug] / gross) if gross else 0.0
            for iss, x in hold.items():
                if x * f > 0:
                    sub[iss] += x * f
                    ledger.append((label, slug, iss, x * f, 'staking token held by a counted product'))
        # 4. restaking platforms: what restaking-token issuers on the map have not already counted
        lrt_total = sum(vals.get(s) or 0 for s in DEC.LRT_ISSUERS if s in vals)
        for plat, deducts in DEC.RESTAKING_PLATFORMS.items():
            r = dl.get(plat)
            if not r or r['per'].get(label) is None:
                continue
            br = {k: v / pr for k, v in r['per'][label].items()}
            gross = sum(br.values())
            inner = sum(vals.get(s) or 0 for s in deducts) if deducts != 'LRT' else lrt_total
            if plat == 'symbiotic':
                inner += sum((vals.get(s) or 0) * f for s, f in DEC.SYMBIOTIC_ALSO.items())
            net = max(0.0, gross - inner)
            vals[plat] = net
            ledger.append((label, plat, plat, gross - net, 'restaking-token issuers already count this'))
            if gross > 0 and net > 0:
                for iss, x in lst_holdings(br).items():
                    sub[iss] += x * net / gross
        # 5. take staking tokens out of their issuers
        for iss, x in sub.items():
            if iss in vals and vals[iss] is not None:
                take = min(vals[iss], x)
                vals[iss] -= take
                if x - take > 1:
                    ledger.append((label, iss, iss, x - take, 'held exceeds issuer row (cross-chain supply or adapter gap); floored at 0'))
        for slug, v in vals.items():
            result.setdefault(slug, {})[label] = v
    # leftovers: balance flat (<0.5% change) for 3+ consecutive month-ends counts as 0 from the start of the run
    for slug in DEC.LEFTOVER:
        v = result.get(slug)
        if not v:
            continue
        seq = [l for l in LABELS if v.get(l) is not None]
        start = None
        for i in range(len(seq)):
            run = seq[i:i + 3]
            if len(run) == 3 and all(v[run[0]] > 0 and abs(v[x] / v[run[0]] - 1) < 0.005 for x in run):
                start = i
                break
        if start is not None:
            for l in seq[start:]:
                ledger.append((l, slug, slug, v[l], 'leftover: balance unchanged since ' + seq[start]))
                v[l] = 0.0
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
