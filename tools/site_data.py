"""Build the chart data object embedded in index.html as `const V3 = {...}` (market map donut, category history, top-5 series).
The page recomputes the map and the history for any mix of its five "What to count" switches, so this also writes the map and
the history by segment: `rows` (every product in today's map, with its segment and the Babylon stake inside it), `hseg` (month-end
history by segment and category), `groups` (what is in farming and pools: kind, BTC tokens and an optional table label per
product, from data/c6_groups.csv), `info` (what each product does, its yield and who runs it, from data/product_notes.csv) and
`outside` (products listed but not counted, and why, from data/outside_totals.csv). Segments: 1 Babylon staking
(the direct stakers' row; the stake inside listed products is `cut` on their rows and `babcut<segment>` in the history), 2 lending
(data/lending_products.csv), and inside farming and pools 3 points farming, 4 strategy vaults, 5 pools; 0 is always counted.
`hist` is the full history (everything counted). With --check=<file> it also writes fixed variants to test the page's sums
against: `map` (everything), `mapx`/`histx` (no Babylon), `mapl`/`histl` (no lending), `mapxl`/`histxl` (neither).
Reads data/*.csv and data/top5/<product>/*; writes JSON to paste over the V3 object, or with --inject writes it into index.html.
Usage: python3 tools/site_data.py [repo root] [out json] [--inject] [--check=<file>]"""
import csv, json, os, re, sys, collections

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
V3 = ARGS[0] if len(ARGS) > 0 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = ARGS[1] if len(ARGS) > 1 else os.path.join(os.path.dirname(__file__), 'v3data.json')
MM = os.path.join(V3, 'data')
TP = lambda *a: os.path.join(V3, 'data', 'top5', *a)
rd = lambda p: list(csv.DictReader(open(p)))
PRICE = 81178  # BTC/USD at the 2026-09-20 snapshot (Binance close), as in data/marketmap_notes.md
CAT = {'C1': ('Carry: BTC collateral, dollar loan', 's2'), 'C2': ('Staking and restaking', 's1'), 'C3': ('Basis and delta-neutral', 's3'),
       'C4': ('Options selling', 's7'), 'C5': ('Credit to institutions', 's4'), 'C6': ('Farming, pools and emissions', 's5')}
ORDER = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
# BTC that earns about 0%, shown as its own segments and off by default on the page: supplied to money markets (C7) or posted as
# collateral for stablecoins in CDPs (C8); only the part no product above already counts (data/money_markets*.csv)
CAT.update({'C7': ('Money markets: BTC supplied, earns about 0%', 'muted'), 'C8': ('CDP collateral: BTC behind stablecoins', 'ink-2')})
EXTRA = ['C7', 'C8']
SHORT = {'Kraken Bitcoin Vault (Advanced Strategies BTC)': 'Kraken Bitcoin Vault', 'Lombard LBTC - direct / other holders': 'Lombard LBTC',
         'Symbiotic (BTC vaults) - direct / other holders': 'Symbiotic', 'Bedrock uniBTC - direct / other holders': 'Bedrock uniBTC',
         'Veda (other BTC vaults, excl. Kraken)': 'Veda, other BTC vaults', 'Solv Basis Trading (SolvBTC.TRADING)': 'Solv Basis Trading',
         'BitFi bfBTC (EVM chains)': 'BitFi bfBTC', 'Hilbert Xapo Byzantine BTC Credit Fund': 'Xapo Byzantine credit fund',
         'Lombard Vaults (LBTCv / BTCe)': 'Lombard Vaults', 'Bitget bgBTC Onchain Earn': 'Bitget bgBTC Earn', 'Midas mHyperBTC (Hyperithm)': 'Midas mHyperBTC',
         'CIAN Yield Layer (BTC vaults)': 'CIAN Yield Layer', 'Core BTC staking (Satoshi Plus)': 'Core staking', 'Accountable YieldApp (cbBTC/wcBTC)': 'Accountable',
         'Starboard Sygnum BTC Alpha Fund': 'Sygnum BTC Alpha', 'Solv Strategies': 'Solv Strategies', 'Mezo Earn (veBTC)': 'Mezo Earn', 'Zest v2 (sBTC supply)': 'Zest v2'}

def short(n):
    if n.startswith('Babylon (BTC staking) - other'): return 'Babylon, other stakers (mostly Kraken)'
    return SHORT.get(n, n)

# ---------- donut ----------
def build_map(rows):
    rows = [r for r in rows if float(r['tvl_btc']) > 0]  # products holding BTC today (closed ones stay in the history)
    tot_btc = sum(float(r['tvl_btc']) for r in rows); tot_usd = sum(float(r['tvl_usd']) for r in rows)
    by = collections.defaultdict(list)
    for r in rows: by[r['category_code']].append(r)
    cats = []
    for c in sorted(by, key=lambda c: -sum(float(r['tvl_btc']) for r in by[c])):
        L = sorted(by[c], key=lambda r: -float(r['tvl_btc']))
        items, rest = [], []
        for r in L:
            b, u = float(r['tvl_btc']), float(r['tvl_usd'])
            if (b / tot_btc >= 0.012 or (c == 'C1' and b >= 100)) and len(items) < 6: items.append(dict(name=short(r['product']), value=round(u / 1e6, 1), btc=round(b, 1)))
            else: rest.append((r, b, u))
        if len(rest) == 1: items.append(dict(name=short(rest[0][0]['product']), value=round(rest[0][2] / 1e6, 1), btc=round(rest[0][1], 1)))
        elif rest: items.append(dict(name=f'{len(rest)} smaller products', value=round(sum(x[2] for x in rest) / 1e6, 1), btc=round(sum(x[1] for x in rest), 1)))
        cats.append(dict(k=c, name=CAT[c][0], color=CAT[c][1], value=round(sum(float(r['tvl_usd']) for r in L) / 1e6, 1),
                         btc=round(sum(float(r['tvl_btc']) for r in L), 1), n=len(L), items=items))
    return dict(cats=cats, total_btc=round(tot_btc), total_usd=round(tot_usd / 1e6), n=len(rows)), by

allrows = rd(os.path.join(MM, 'market_map_current.csv'))
cur = [r for r in allrows if r['include_net'] == '1' and r['tvl_btc'] and r['category_code'] in CAT]
mp, by = build_map(cur)
# C1 detail (all rows incl. tiny)
mp['c1'] = [dict(name=short(r['product']), btc=round(float(r['tvl_btc']), 1), usd=round(float(r['tvl_usd']) / 1e6, 1)) for r in sorted(by['C1'], key=lambda r: -float(r['tvl_btc']))]

# ---------- without Babylon staking (the site's Babylon switch) ----------
# Removes all BTC staked in Babylon: the direct stakers' row, and the Babylon stake inside listed LSTs. The net count keeps
# that stake at the LST (Gate GTBTC and others); the attributed row's double_count_note says how much sits in which row.
bab_direct = next(r for r in allrows if r['product'].startswith('Babylon (BTC staking) - other'))
bab_attr = next(r for r in allrows if r['product'].startswith('Babylon (BTC staking) - stake attributed'))
lst = {}
for part in bab_attr['double_count_note'].removeprefix('counted in: ').split(', '):
    name, amt = part.removesuffix(' BTC').rsplit(' ', 1)
    lst[name] = float(amt.replace(',', ''))
assert abs(sum(lst.values()) - float(bab_attr['tvl_btc'])) < 1, (lst, bab_attr['tvl_btc'])
lst_row = {n: next(r['product'] for r in cur if r['product'] == n or r['product'].startswith(n + ' - direct')) for n in lst}
cur_x = []
for r in cur:
    if r is bab_direct: continue
    cut = next((lst[n] for n, p in lst_row.items() if p == r['product']), 0.0)
    if cut:
        b = float(r['tvl_btc']); r = dict(r, tvl_btc=str(b - cut), tvl_usd=str(float(r['tvl_usd']) * (b - cut) / b))
    cur_x.append(r)
mapx, _ = build_map(cur_x)
bab = dict(direct_btc=round(float(bab_direct['tvl_btc'])), lst_btc=round(float(bab_attr['tvl_btc'])), lst={n: round(v) for n, v in lst.items()},
           usd=round((float(bab_direct['tvl_usd']) + float(bab_attr['tvl_usd'])) / 1e6))

# ---------- without lending (the site's lending switch) ----------
LENDSET = {r['product'] for r in rd(os.path.join(MM, 'lending_products.csv'))}
mapl, _ = build_map([r for r in cur if r['product'] not in LENDSET])
mapxl, _ = build_map([r for r in cur_x if r['product'] not in LENDSET])
lrows = [r for r in cur if r['product'] in LENDSET]
lend = dict(btc=round(sum(float(r['tvl_btc']) for r in lrows)), usd=round(sum(float(r['tvl_usd']) for r in lrows) / 1e6), n=len(lrows))

# ---------- segments for the site's "What to count" switches ----------
GROUPS = {r['product']: r for r in rd(os.path.join(MM, 'c6_groups.csv'))}
GSEG = {'points': 3, 'vaults': 4, 'pools': 5, 'lending': 2}
def seg(product, cat):
    """0 always counted, 1 Babylon direct stakers, 2 lending, 3 points farming, 4 strategy vaults, 5 pools (the last three only in C6)."""
    if product == bab_direct['product']: return 1
    if product in LENDSET: return 2
    if cat == 'C6':
        assert product in GROUPS, 'farming and pools product without a group in data/c6_groups.csv: ' + product
        return GSEG[GROUPS[product]['group']]
    return 0
cut_by = {p: lst[n] for n, p in lst_row.items()}
rows_out = []
for r in sorted(cur, key=lambda r: -float(r['tvl_btc'])):
    b, u, c = float(r['tvl_btc']), float(r['tvl_usd']), cut_by.get(r['product'], 0.0)
    if b <= 0: continue  # closed products with no BTC today (Maple) stay in the history only
    rows_out.append([short(r['product']), r['category_code'], round(b, 4), round(u / 1e6, 4), seg(r['product'], r['category_code']),
                     round(c, 4), round(u / 1e6 * c / b, 4) if c else 0])
# what is in farming and pools: groups, products, BTC tokens (products with BTC in today's map; the rest are history only)
def disp(n):
    """Name for the farming-and-pools tables: no holder suffix, no size note, and no bracket that only repeats the coin (the table has a
    column for the BTC tokens); a bracket naming a chain stays."""
    n = re.sub(r' \(over \$1M[^)]*\)|, over \$1M', '', short(n).replace(' - direct / other holders', ''))
    m = re.search(r' \(([^)]*)\)$', n)
    return n if m and m.group(1) in ('Solana', 'Starknet', 'Polkadot', 'Base', 'Berachain') else re.sub(r' \(.*\)$', '', n)
groups = {}
for name, g in GROUPS.items():
    row = next((r for r in cur if r['product'] == name), None)
    G = groups.setdefault(g['group'], dict(now=[], ended=[]))
    if row and row['category_code'] == 'C6' and float(row['tvl_btc']) >= 0.5:
        G['now'].append([g['label'] or disp(name), round(float(row['tvl_btc'])), g['btc_tokens']])
    elif not row and disp(name) not in G['ended'] and disp(name) not in {disp(r['product']) for r in cur}: G['ended'].append(disp(name))
for g in groups.values(): g['now'].sort(key=lambda x: -x[1])
# the product table: what each product does, its yield where known, who runs it (data/product_notes.csv, one row per product
# in today's map), and the products listed but not counted (data/outside_totals.csv)
NOTES = {r['product']: r for r in rd(os.path.join(MM, 'product_notes.csv'))}
missing = [r['product'] for r in cur if float(r['tvl_btc']) > 0 and r['product'] not in NOTES]
assert not missing, 'products without a row in data/product_notes.csv: ' + ', '.join(missing)
info = {short(p): [n['how'], n['yield_btc'], n['run_by'], n['url']] for p, n in NOTES.items()}
assert len(info) == len(NOTES), 'two products share a short name'
tokens = {short(p): g['btc_tokens'] for p, g in GROUPS.items() if g['btc_tokens']}
outside = [[r['kind'], r['product'], r['yield_btc'], r['size'], r['why_not_counted'], r['url']] for r in rd(os.path.join(MM, 'outside_totals.csv'))]
# money markets and CDP collateral: one row per protocol (segment 6 = money markets, C7; 7 = CDP collateral, C8)
MMSEG = {'money_market': ('C7', 6), 'cdp': ('C8', 7)}
mmrows, mmgross = [], []
if os.path.exists(os.path.join(MM, 'money_markets.csv')):
    for r in rd(os.path.join(MM, 'money_markets.csv')):
        cat, sg = MMSEG[r['segment']]
        b = float(r['btc_counted'])
        if r['segment'] == 'money_market': mmgross.append([r['protocol'], round(float(r['btc_supplied']), 1)])
        if b <= 0: continue
        mmrows.append([r['protocol'], cat, round(b, 4), round(b * PRICE / 1e6, 4), sg, 0, 0])
        info[r['protocol']] = [r['how'], r['supply_apy'], r['protocol'], r['url']]
    rows_out += sorted(mmrows, key=lambda x: -x[2])
    mmgross.sort(key=lambda x: -x[1])

# ---------- history ----------
h = rd(os.path.join(MM, 'category_history_monthly.csv'))
months = sorted({r['month'] for r in h})
hist = dict(x=months, btc={c: [0.0] * len(months) for c in ORDER}, usd={c: [0.0] * len(months) for c in ORDER})
for r in h:
    i = months.index(r['month'])
    hist['btc'][r['category_code']][i] = round(float(r['tvl_btc_net']))
    hist['usd'][r['category_code']][i] = round(float(r['tvl_usd_net']) / 1e6)
ph = rd(os.path.join(MM, 'market_map_history_monthly.csv'))
# Without Babylon staking: take the direct stakers' row and the stake attributed to listed products out of each month. The
# attributed stake is split by product and month in data/marketmap_overlap.md (section 4, from the pipeline's finality-provider
# attribution); each month is scaled to that month's attributed row. Each product's part comes out of the category and segment
# the product sits in that month: LBTC's part moves to options (C4) from 2026-08, and B2 Buzz Farming's is farming (points).
def babylon_split():
    txt = open(os.path.join(MM, 'marketmap_overlap.md'), encoding='utf-8').read()
    lines = [l for l in txt[txt.index('Babylon stake attributed to listed products, by product'):].split('\n') if l.startswith('|')]
    head = [c.strip() for c in lines[0].strip('|').split('|')]
    out = {}
    for l in lines[2:]:
        c = [x.strip() for x in l.strip('|').split('|')]
        if not re.match(r'\d{4}-\d{2}$', c[0]): break
        out[c[0]] = {head[j]: float(c[j].replace(',', '')) for j in range(1, len(head))}
    return out
bsplit = babylon_split()
attr_rows = {r['month']: r for r in ph if r['product'] == bab_attr['product']}
netrow = {}
for r in ph:
    if r['include_net'] != '1': continue
    for n in next(iter(bsplit.values())):
        if r['product'] == n or r['product'].startswith(n + ' - direct'): netrow[(r['month'], n)] = (r['product'], r['category_code'])
bcut = collections.defaultdict(list)  # month -> [(product row, category, btc, usd)]
for m, parts in bsplit.items():
    ar, tot = attr_rows.get(m), sum(parts.values())
    if not ar or tot <= 0: continue
    assert abs(tot - float(ar['tvl_btc'])) < 10, (m, tot, ar['tvl_btc'])
    for n, v in parts.items():
        if v > 0:
            prod, cat = netrow[(m, n)]
            bcut[m].append((prod, cat, float(ar['tvl_btc']) * v / tot, float(ar['tvl_usd']) * v / tot))
def hist_without(babylon, lending):
    """Category history less Babylon staking and/or less the lending products (their net rows, month by month)."""
    x = dict(x=months, btc={c: [0.0] * len(months) for c in ORDER}, usd={c: [0.0] * len(months) for c in ORDER})
    for r in h:
        i = months.index(r['month'])
        x['btc'][r['category_code']][i] = float(r['tvl_btc_net'])
        x['usd'][r['category_code']][i] = float(r['tvl_usd_net'])
    for r in ph:
        i, b, u = months.index(r['month']), float(r['tvl_btc']), float(r['tvl_usd'])
        if lending and r['product'] in LENDSET and r['include_net'] == '1' and r['category_code'] in ORDER:
            x['btc'][r['category_code']][i] -= b; x['usd'][r['category_code']][i] -= u
        if not babylon or not r['product'].startswith('Babylon (BTC staking)'): continue
        if r['product'] == bab_direct['product'] and r['include_net'] == '1':
            x['btc'][r['category_code']][i] -= b; x['usd'][r['category_code']][i] -= u
        elif r['product'] == bab_attr['product']:
            for prod, c, pb, pu in bcut[r['month']]:
                x['btc'][c][i] -= pb; x['usd'][c][i] -= pu
    for unit, div in (('btc', 1), ('usd', 1e6)):
        for c in ORDER:
            assert min(x[unit][c]) > -1, (unit, c)
            x[unit][c] = [round(max(0.0, v) / div) for v in x[unit][c]]
    return x
histx, histl, histxl = hist_without(True, False), hist_without(False, True), hist_without(True, True)
# the same history by segment (sums kept to 0.001 BTC and $1,000), so the page can add up any mix of switches;
# 'babcut<segment>' is the Babylon stake inside listed products, by the segment of the product that holds it; the page takes it off
# when Babylon is hidden, unless that segment is hidden already
hs = collections.defaultdict(lambda: {u: {c: [0.0] * len(months) for c in ORDER} for u in ('btc', 'usd')})
for k in ('0', '1', '2', '3', '4', '5'): hs[k]
for r in ph:
    i, b, u = months.index(r['month']), float(r['tvl_btc']), float(r['tvl_usd']) / 1e6
    if r['include_net'] == '1' and r['category_code'] in ORDER:
        k = str(seg(r['product'], r['category_code']))
        hs[k]['btc'][r['category_code']][i] += b; hs[k]['usd'][r['category_code']][i] += u
    elif r['product'] == bab_attr['product']:
        for prod, c, pb, pu in bcut[r['month']]:
            k = 'babcut' + str(seg(prod, c))
            hs[k]['btc'][c][i] += pb; hs[k]['usd'][c][i] += pu / 1e6
# money markets (segment 6, C7) and CDP collateral (7, C8), month by month
if os.path.exists(os.path.join(MM, 'money_markets_monthly.csv')):
    for r in rd(os.path.join(MM, 'money_markets_monthly.csv')):
        if r['month'] not in months: continue
        cat, sg = MMSEG[r['segment']]
        i, k = months.index(r['month']), str(sg)
        hs[k]['btc'].setdefault(cat, [0.0] * len(months)); hs[k]['usd'].setdefault(cat, [0.0] * len(months))
        hs[k]['btc'][cat][i] += float(r['btc_counted']); hs[k]['usd'][cat][i] += float(r['usd_counted']) / 1e6
hseg = {k: {u: {c: [round(v, 3) for v in vals] for c, vals in d[u].items() if any(vals)} for u in d} for k, d in hs.items()}
# snapshot products with no month-end history (the history leaves them out)
with_hist = {r['product'] for r in ph}
nohist = [dict(n=short(r['product']), lend=int(r['product'] in LENDSET), seg=seg(r['product'], r['category_code'])) for r in cur if r['product'] not in with_hist]
# C1 by product (history)
c1h = collections.defaultdict(lambda: [0.0] * len(months))
for r in ph:
    if r['category_code'] == 'C1' and r['include_net'] == '1':
        c1h[short(r['product'])][months.index(r['month'])] += float(r['tvl_btc'])
c1hist = {k: [round(v) for v in vals] for k, vals in c1h.items() if max(vals) >= 40}

# ---------- top-5 series ----------
T = {}
# Kraken: month-end TVL + flows; monthly yield (deep dive E.1)
T['kraken'] = dict(
    tvl=dict(x=['2026-05', '2026-06', '2026-07', '2026-08', '2026-09'], btc=[1338.5, 4362.0, 5532.4, 5939.3, 6499.3], usd=[98.6, 255.3, 347.5, 466.5, 527.7],
             flow=[1335.7, 3018.6, 1164.8, 400.5, 556.4], newdep=[10940, 16644, 9226, 7885, 4060]),
    yld=dict(x=['2026-06', '2026-07', '2026-08', '2026-09'], series=[
        dict(name='Paid to depositors', color='s2', values=[1.80, 1.37, 1.30, 1.03]),
        dict(name='Same, without rewards (model)', color='s1', values=[0.59, 0.33, 0.21, 0.12]),
        dict(name='Borrow rate, RLUSD', color='s7', values=[1.60, 3.09, 3.43, 3.07]),
        dict(name='Where the RLUSD goes, without rewards', color='s3', values=[1.78, 2.55, 2.80, 2.55])]),
    buckets=[dict(label=r['bucket_btc'] + ' BTC', holders=int(r['holders']), btc=float(r['btc']), pct=float(r['btc_pct'])) for r in rd(TP('kraken', 'holders_buckets.csv')) if not r['bucket_btc'].startswith('#')])
# Yield Basis
yb_t = [r for r in rd(TP('yieldbasis', 'tvl_monthly.csv')) if r['pool'].startswith('ALL_BTC')]
yp = rd(TP('yieldbasis', 'yield_protocol_monthly.csv'))
yp = [r for r in yp if r['month'] >= '2025-10']
ybb = [r for r in rd(TP('yieldbasis', 'holders_buckets.csv')) if r['market'].startswith('v3 BTC markets combined')]
T['yb'] = dict(
    tvl=dict(x=[r['month'] for r in yb_t], btc=[round(float(r['tvl_btc']), 1) for r in yb_t], usd=[round(float(r['tvl_usd']) / 1e6, 1) for r in yb_t]),
    yld=dict(x=[r['month'] for r in yp], series=[
        dict(name='Unstaked, book value', color='s2', values=[float(r['unstaked_book_apy']) for r in yp]),
        dict(name='Staked, paid in YB token', color='s1', values=[float(r['staked_token_apr']) for r in yp])]),
    buckets=[dict(label=r['bucket_btc_equiv'] + ' BTC', holders=int(r['holders']), btc=float(r['btc_equiv']), pct=float(r['share_of_market_pct'])) for r in ybb])
# Bitget (weekly)
bt = [r for r in rd(TP('bitget', 'tvl_weekly.csv')) if r['date'] >= '2026-07-31']
by_ = rd(TP('bitget', 'yield_weekly.csv'))
T['bitget'] = dict(
    tvl=dict(x=[r['date'][:10] for r in bt], btc=[round(float(r['vault_nav_bgbtc']), 1) for r in bt], usd=[round(float(r['vault_nav_usd']) / 1e6, 1) for r in bt]),
    yld=dict(x=[r['week'][:10] for r in by_], series=[
        dict(name='Paid by the vault', color='s2', values=[float(r['vault_realized_apy']) for r in by_]),
        dict(name='Borrow rate, USDC', color='s7', values=[float(r['borrow_rate']) for r in by_]),
        dict(name='Where the USDC goes, without rewards', color='s3', values=[float(r['gtusdc_apy_organic']) for r in by_])]))
# optional: ether.fi and mHyperBTC (filled when their CSVs exist)
for key, d in [('etherfi', 'etherfi'), ('mhyper', 'mhyperbtc')]:
    p = TP(d, 'site_series.json')
    if os.path.exists(p): T[key] = json.load(open(p))

data = json.dumps(dict(hist=hist, c1hist=c1hist, top=T, bab=bab, lend=lend, nohist=nohist, rows=rows_out, hseg=hseg, groups=groups,
                       cats={c: list(CAT[c]) for c in ORDER + EXTRA}, info=info, tokens=tokens, outside=outside, mmgross=mmgross), separators=(',', ':'))
with open(OUT, 'w') as f: f.write(data)
for a in sys.argv[1:]:
    if a.startswith('--check='):
        with open(a[8:], 'w') as f: json.dump(dict(map=mp, hist=hist, mapx=mapx, histx=histx, mapl=mapl, histl=histl, mapxl=mapxl, histxl=histxl), f)
print('ok', OUT, mp['total_btc'], mp['total_usd'], [(c['k'], c['btc']) for c in mp['cats']])
print('without Babylon', mapx['total_btc'], mapx['total_usd'], [(c['k'], c['btc']) for c in mapx['cats']])
print('without lending', mapl['total_btc'], mapl['total_usd'], '| without both', mapxl['total_btc'], mapxl['total_usd'], '| lending', lend, '| no history', nohist)
segbtc = collections.Counter()
for r in rows_out: segbtc[r[4]] += r[2]
print('by segment now', {k: round(v) for k, v in sorted(segbtc.items())}, '| Babylon stake in tokens', round(sum(r[5] for r in rows_out)),
      '| groups', {g: (len(d['now']), sum(x[1] for x in d['now']), len(d['ended'])) for g, d in groups.items()})
if '--inject' in sys.argv:
    page = os.path.join(V3, 'index.html')
    with open(page, encoding='utf-8') as f: src = f.read()
    src, n = re.subn(r'^const V3 = \{.*\};$', lambda m: 'const V3 = ' + data + ';', src, count=1, flags=re.M)
    assert n == 1, 'const V3 line not found in index.html'
    with open(page, 'w', encoding='utf-8') as f: f.write(src)
    print('injected into', page)
