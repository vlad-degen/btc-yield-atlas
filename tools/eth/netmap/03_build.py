"""Build the ETH counted-once market map: snapshot (2026-10-02) and 24 month-ends (2024-10 .. 2026-09).

Inputs: raw/eth/netmap-2026-10-07/{screen.json, proto/*.json.gz, yield_pools.json, pool_charts/},
        data/eth/reader_carry_category.json, reader_product_chapters.json and carry-status-and-capital.csv (on-chain product
        books), data/eth/lending_split.json and the lending layer inputs read by layers.py.
Outputs (data/eth/netmap/): market_map_current.csv, market_map_history_monthly.csv, category_history_monthly.csv,
        netting_ledger.csv, map.json (everything the site needs), plus a printed summary.

Rules (ETH map, since 8 Oct 2026):
- Every product counts once. A staking or restaking token held inside another counted product, or posted in a lending
  market, leaves its issuer's row: staking and restaking are ETH staked and held, not used anywhere else.
- Lending markets (layers.py) split into leveraged staking (staking tokens or ETH against borrowed ETH: cells A1+B1 of
  data/eth/lending_split.json, collateral counted once), the carry products' own collateral against dollar loans (carry) and
  money markets (everything else, off by default). Lent-out WETH is not added. Loop vaults whose book sits in lending
  markets count 0 (inside leveraged staking).
- Carry rows are only the part of a product's book that is ETH collateral for a dollar loan (YieldBasis and Liquity ETH
  Carry: the whole book), in months with at least $10k of dollar debt; the whole book still replaces the DefiLlama row.
- CDPs count plain ETH only; staking tokens there stay with their issuer. Off by default.
- Restaking platforms (EigenLayer, Symbiotic) count only what restaking-token issuers on the map have not already
  counted (estimate, flagged).
"""
import csv, collections, datetime, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import OUT, RAW, ROOT, eth_part, load, month_points, pick, price, series
from products import BY_DL_CATEGORY, CATEGORIES, ISSUERS
import decisions as DEC
import layers as LAY

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
    """whole-product books of the examined carry products (ETH) at every month-end and the snapshot.

    Month-ends: data/eth/reader_carry_category.json (Rocksolid: reader_product_chapters.json), the archive book series the
    research built; read directly so the map does not depend on its own output (data/eth/carry-history-all-eth.csv is
    written downstream from this map and zeroes months without dollar debt). Snapshot: carry-status-and-capital.csv."""
    cat = json.load(open(os.path.join(ROOT, 'data', 'eth', 'reader_carry_category.json')))['products']
    chapters = json.load(open(os.path.join(ROOT, 'data', 'eth', 'reader_product_chapters.json')))['products']
    snap = {r['product']: float(r['whole_book_ETH']) for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'eth', 'carry-status-and-capital.csv')))}
    out = {}
    for prod, meta in DEC.CARRY.items():
        p = next((x for x in cat if x['product'] == prod), None)
        hist = (p or {}).get('history') or next((c['charts']['capitalHistory']['rows'] for c in chapters if c['name'] == prod), [])
        vals = {r['month']: float(r['sizeETH']) for r in hist if r.get('sizeETH') is not None and r['month'] in LABELS}
        vals[SNAP] = meta.get('snapshot_eth', snap.get(prod))
        out['carry:' + meta['id']] = dict(slug='carry:' + meta['id'], name=meta['name'], dl_category='on-chain',
                                          category=meta['category'], kind=meta.get('kind'), source='on-chain product book (this study)',
                                          eth=vals, issuer_mix=meta['issuer_mix'], replaces=meta.get('replaces', {}),
                                          host_token=meta.get('host_token'))
    return out


def build():
    dl = dl_rows()
    pools = pool_rows()
    carry = carry_rows()
    prices = {label: price(pdate) for label, pdate, _ in PTS}
    # rows read only to net others (excluded from the map themselves)
    dl_src = {src: {label: eth_part(pick(series(src), pdate)[0])[1] for label, pdate, _ in PTS} for src, *_ in DEC.BASE_VALUED.values()}
    ledger = []
    result = {}  # slug -> {label: eth}
    meta = {}
    replaced = {d for r in carry.values() for d in r['replaces']}
    carry_tokens = {k for k, t in DEC.PRODUCT_TOKENS.items() if t.startswith('carry:')}
    # tokens of loop products whose book sits in lending markets: claims on the leveraged-staking cell, counted there
    loop_tokens = {k for k, t in {**ISSUERS, **DEC.PRODUCT_TOKENS}.items() if t in DEC.LOOPS_IN_LENDING}
    inner_tokens = carry_tokens | loop_tokens

    def row_value(slug, r, br):
        """step-1 value of a DefiLlama row (ETH) and the breakdown whose tokens it takes from other rows (None: takes none)"""
        cat = r['category']
        if cat == 'lending':
            return plain_eth(br), None
        if cat == 'cdp':  # staking tokens posted in a CDP are used, not just held: they count here and leave their issuer
            return sum(br.values()), br
        br = {k: v for k, v in br.items() if k not in loop_tokens}
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

    # the lending layer (tools/eth/netmap/layers.py): lending-market ETH, loops, carry products' positions
    row_category = {s: r['category'] for s, r in dl.items()}
    layer, LM = LAY.build_layer(dl, PTS, prices, leftover_from, row_category)
    parts = LAY.carry_parts(LABELS, prices, SNAP)
    cmeta = {m['id']: m for m in DEC.CARRY.values()}
    lend_rows = LAY.lending_rows(dl, leftover_from)
    loops_meta, rest_meta = {}, {}

    gross_step1 = {}
    for label, pdate, _ in PTS:
        pr = prices[label]
        L = layer[label]
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
            if slug in DEC.LOOPS_IN_LENDING:
                ledger.append((label, slug, 'loops', row_value(slug, r, br)[0], 'loop product: its positions are inside leveraged staking on lending markets'))
                vals[slug] = 0.0
                continue
            v, hbr = row_value(slug, r, br)
            if slug in leftover_from and label >= leftover_from[slug]:
                ledger.append((label, slug, slug, v, 'leftover: balance unchanged since ' + leftover_from[slug]))
                vals[slug] = 0.0
                continue
            vals[slug] = v
            if hbr is not None and (slug not in DEC.ISSUER_SLUGS or slug in DEC.LRT_ISSUERS or slug in DEC.HOLDS_TOKENS):
                held[slug] = (v, {i: x for i, x in lst_holdings(hbr).items() if i != slug})
        gross_step1[label] = {k: v for k, v in vals.items() if v}  # issuer value before any netting (site toggle: all staked ETH)
        # 2. carry products: the carry part of the book is the row; the whole book replaces the DefiLlama rows that count it
        taken = collections.defaultdict(float)
        for slug, r in carry.items():
            cid = slug.split(':', 1)[1]
            p = parts[cid][label]
            book = r['eth'].get(label)
            off = p['carry_off'] if p['carry_off'] is not None else (book or 0.0)
            cv = p['carry_lend'] + off
            rest = p['other_lend']
            if cid == 'zensats' and book:  # no lending account known: the whole (micro) book stays a farming row
                rest += book
            if book is None and not cv and not rest:
                continue
            vals[slug] = cv
            if rest:
                vals[slug + ':rest'] = rest
                rest_meta[slug + ':rest'] = slug
            for iss, w in r['issuer_mix'].items():  # only what does not sit in a lending market (the layer takes the rest)
                x = (off + (book if cid == 'zensats' and book else 0.0)) * w
                if x:
                    sub[iss] += x
                    ledger.append((label, slug, iss, x, 'carry outside lending markets; staking token per research'))
            left = book if book is not None else cv + rest
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
        # tokens held by DefiLlama rows, scaled to what is left of the row after steps 2-3. A carry book that the row values in
        # plain WETH (host_token, the carry-sweep vaults) leaves the row's WETH, not its staking tokens, so it does not scale them
        for slug, (gross, hold) in held.items():
            wt = sum(t for (a, b), t in taken.items() if b == slug and a.startswith('carry:') and carry[a].get('host_token') == 'WETH')
            f = min(1.0, (vals[slug] + wt) / gross) if gross else 0.0
            if sum(hold.values()) * f > vals[slug]:  # never take out of issuers more than the row still counts
                f = vals[slug] / sum(hold.values())
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
                    if vals.get(s2) or taken.get(('cap', s2)):
                        x = min((ebr.get(s2) or {}).get(t_row, 0.0), br.get(t_plat, 0.0), (vals.get(s2) or 0.0) + taken.get(('cap', s2), 0.0))
                        inner += x
                        if x >= 1:
                            ledger.append((label, s2, plat, x, 'position in a Symbiotic vault, counted in the row that holds it'))
            if plat == 'symbiotic':
                for s2, share in DEC.SYMBIOTIC_EXTRA:
                    x = min((vals.get(s2) or 0.0) * share, max(0.0, gross - inner))
                    inner += x
                    if x >= 1:
                        ledger.append((label, s2, plat, x, 'position in a Symbiotic vault, counted in the row that holds it'))
            net = max(0.0, gross - inner)
            vals[plat] = net
            ledger.append((label, plat, plat, gross - net, 'restaking-token issuers already count this'))
            if gross > 0 and net > 0:
                for iss, x in lst_holdings(br, products=False).items():
                    sub[iss] += x * net / gross
        # 5. the lending layer: staking tokens posted in lending markets leave their issuers (counted in leveraged staking
        # or money markets); loops by venue; money markets = lending-market ETH less loops less the carry products' positions
        for iss, x in L['issuer'].items():
            sub[iss] += x
            ledger.append((label, 'lending markets', iss, x, 'staking token posted in a lending market (leveraged staking or money markets)'))
        for slug, x in L['loops_by_row'].items():
            g = 'loops:' + DEC.LOOP_VENUES.get(slug, ('other', ''))[0]
            vals[g] = vals.get(g, 0.0) + x
            loops_meta[g] = DEC.LOOP_VENUES.get(slug, ('other', DEC.LOOP_OTHER))[1]
        prod = sum(parts[c][label]['carry_lend'] + parts[c][label]['other_lend'] for c in parts)
        # a carry product booked by a lending row (Yearn books yvWETH-2 as WETH): the row's own WETH already counts the
        # collateral the lending market holds, so the book leaves that row's share of money markets too
        dup = {d: t for (a, d), t in taken.items() if d in lend_rows and a.startswith('carry:') and t > 0 and d in L['rows']}
        L['lend_dup'] = sum(dup.values())
        mm = L['total'] - L['loops'] - prod - L['lend_dup']
        if mm < 0:
            raise SystemExit(f'money markets negative in {label}: {mm:.0f}')
        room = {s: max(0.0, x['total'] - L['loops_by_row'].get(s, 0.0) - dup.get(s, 0.0)) for s, x in L['rows'].items()}
        rt = sum(room.values())
        for slug in lend_rows:
            vals[slug] = mm * room.get(slug, 0.0) / rt if rt else 0.0
        ledger.append((label, 'lending markets', 'loops', L['loops'], 'loops: ETH borrowed against staking tokens (collateral counted once)'))
        ledger.append((label, 'lending markets', 'carry', prod, "carry products' own lending positions"))
        for d, t in dup.items():
            ledger.append((label, d, 'carry', t, 'lending row already books a carry product (its vault shares), taken out of money markets'))
        # 6. take held tokens out of their issuer or product rows
        L['mm_taken'], L['mm_cut'] = 0.0, 0.0
        for iss, x in sub.items():
            if iss in vals and vals[iss] is not None:
                take = min(vals[iss], x)
                vals[iss] -= take
                if iss in lend_rows:  # a lending vault's share token held by another counted product (Pendle's superWETH)
                    L['mm_taken'] += take
                if x - take > 1:
                    ledger.append((label, iss, iss, x - take, 'held exceeds issuer row (cross-chain supply or adapter gap); floored at 0'))
                # tokens of this issuer counted in lending markets beyond what the issuer backs leave money markets (off by
                # default), so the ETH behind a staking token is never counted twice across categories
                cut = min(x - take, L['issuer'].get(iss, 0.0))
                if cut > 1e-9:
                    L['mm_cut'] = L.get('mm_cut', 0.0) + cut
                    ledger.append((label, 'lending markets', iss, cut, 'staking tokens in lending markets beyond the issuer\'s backing: taken out of money markets'))
        if L.get('mm_cut'):
            mmv = sum(vals[s2] for s2 in lend_rows)
            if L['mm_cut'] > mmv:
                raise SystemExit(f'money-market cut exceeds money markets in {label}')
            for s2 in lend_rows:
                vals[s2] -= L['mm_cut'] * vals[s2] / mmv
        for slug, v in vals.items():
            result.setdefault(slug, {})[label] = v
    for d in (dl, pools, carry):
        for slug, r in d.items():
            meta[slug] = {k: r.get(k) for k in ('slug', 'name', 'dl_category', 'category', 'kind', 'source')}
    for slug, base in rest_meta.items():
        cid = base.split(':', 1)[1]
        cat = DEC.DEBT_MONTHS[cid][1]
        cat = 'lending' if cat == 'loops' else cat
        meta[slug] = dict(meta[base]); meta[slug].update(slug=slug, name=meta[base]['name'] + ' (outside carry)', category=cat,
                                                        kind='vaults' if cat == 'farming' else None,
                                                        source='lending collateral that backs no dollar loan (months under $10k of dollar debt) and holdings outside lending markets')
    for slug, name in loops_meta.items():
        meta[slug] = dict(slug=slug, name='Leveraged staking on ' + name, dl_category='Lending', category='loops',
                          kind=None, source='lending split at the snapshot (ETH borrowed against staking tokens, counted once); month-ends '
                          'estimated from the venue\'s ETH debt')
    LAYER.update(layer=layer, meta=LM, parts=parts)
    json.dump(gross_step1, open(os.path.join(OUT, 'issuer_gross.json'), 'w'), indent=0, sort_keys=True)
    return result, meta, ledger


LAYER = {}


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
    # the lending layer, month by month (read by 07_lending_gross.py and the coverage note)
    lay, LM, parts = LAYER['layer'], LAYER['meta'], LAYER['parts']
    out_l = dict(snapshot=SNAP, method=LAY.__doc__, meta=LM, months={})
    for label in LABELS:
        x = lay[label]
        prod = {c: {k: v for k, v in parts[c][label].items() if k != 'method'} for c in parts}
        pos = sum(v['carry_lend'] + v['other_lend'] for v in prod.values())
        out_l['months'][label] = dict(
            lending_eth=x['total'], staking_tokens_by_issuer=x['issuer'], plain_eth=sum(r['plain'] for r in x['rows'].values()),
            tokens_without_row=sum(r['no_row'] for r in x['rows'].values()), product_shares_left_out=x['shares'],
            eth_debt=x['debt_total'], eth_debt_by_row=x['debt'], loops=x['loops'],
            loops_equity_estimate=x['loops'] * LM['loop_equity_share'],
            carry_products_positions=pos, lending_vault_shares_held_by_products=x['mm_taken'],
            staking_tokens_beyond_issuer_backing=x['mm_cut'], carry_books_in_lending_rows=x.get('lend_dup', 0.0),
            money_markets=x['total'] - x['loops'] - pos - x['mm_taken'] - x['mm_cut'] - x.get('lend_dup', 0.0),
            rows={k: {kk: vv for kk, vv in r.items()} for k, r in x['rows'].items()}, carry_products=prod,
            loops_estimated=label != SNAP)
    out_l['carry_methods'] = {c: sorted({parts[c][l]['method'] for l in LABELS if parts[c][l]['method']}) for c in parts}
    json.dump(out_l, open(os.path.join(OUT, 'lending_layer.json'), 'w'), indent=1)
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
