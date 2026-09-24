"""Build the chart data object embedded in index.html as `const V3 = {...}` (market map, category history, top-5 series).
The page's switches are the categories themselves: each one takes its category out of every market number. Money markets (C7)
and CDP collateral (C8) earn about 0% and are off by default. So this writes the map by product and the history by category:
`rows` (every product in today's map: name, category, BTC, $M, kind), `hist` (month-end BTC and $M by category, C1-C8), `kinds`
(farming and pools by kind, month-end BTC), `info` (what each product does, its yield and who runs it, from
data/product_notes.csv), `names` (display names), `tokens` (the BTC tokens of farming and pools products), `ended` (products that
held BTC in the history but not today, by category) and `outside` (products listed but not counted, from data/outside_totals.csv).
Vaults that only lend BTC and Zest's sBTC market (kind 'lending' in data/c6_groups.csv) count as money markets: they supply BTC to
lending markets like any other depositor.
Reads data/*.csv and data/top5/<product>/*; writes JSON to paste over the V3 object, or with --inject writes it into index.html.
With --check=<file> it also writes the default map and history to test the page's sums against.
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
       'C4': ('Options selling', 's7'), 'C5': ('Credit to institutions', 's4'), 'C6': ('Farming, pools and emissions', 's5'),
       'C7': ('Money markets and lending vaults', 'muted'), 'C8': ('CDP collateral', 'ink-2')}
ORDER = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
DEFAULT_OFF = {'C7', 'C8'}  # earn about 0%: off unless switched on
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

def disp(n):
    """Name for the category tables: no holder suffix, no size note, and no bracket that only repeats the coin; a bracket naming a
    chain stays."""
    n = re.sub(r' \(over \$1M[^)]*\)|, over \$1M', '', short(n).replace(' - direct / other holders', ''))
    m = re.search(r' \(([^)]*)\)$', n)
    return n if m and m.group(1) in ('Solana', 'Starknet', 'Polkadot', 'Base', 'Berachain') else re.sub(r' \(.*\)$', '', n)

GROUPS = {r['product']: r for r in rd(os.path.join(MM, 'c6_groups.csv'))}
LENDVAULT = {p for p, g in GROUPS.items() if g['group'] == 'lending'}
def cat_of(r):
    """The page's category of a map or history row: vaults that only lend count as money markets."""
    return 'C7' if r['product'] in LENDVAULT else r['category_code']
def kind_of(product, cat):
    if cat == 'C6':
        assert product in GROUPS, 'farming and pools product without a group in data/c6_groups.csv: ' + product
        return GROUPS[product]['group']
    return 'vault' if product in LENDVAULT else ''

# ---------- today's map ----------
def build_map(rows):
    rows = [r for r in rows if float(r['tvl_btc']) > 0]  # products holding BTC today (closed ones stay in the history)
    tot_btc = sum(float(r['tvl_btc']) for r in rows); tot_usd = sum(float(r['tvl_usd']) for r in rows)
    by = collections.defaultdict(list)
    for r in rows: by[r['category_code']].append(r)
    cats = [dict(k=c, btc=round(sum(float(r['tvl_btc']) for r in by[c]), 1), n=len(by[c])) for c in sorted(by, key=lambda c: -sum(float(r['tvl_btc']) for r in by[c]))]
    return dict(cats=cats, total_btc=round(tot_btc), total_usd=round(tot_usd / 1e6), n=len(rows)), by

allrows = rd(os.path.join(MM, 'market_map_current.csv'))
cur = [dict(r, category_code=cat_of(r)) for r in allrows if r['include_net'] == '1' and r['tvl_btc'] and r['category_code'] in CAT]
mp, by = build_map([r for r in cur if r['category_code'] not in DEFAULT_OFF])
rows_out = []
for r in sorted(cur, key=lambda r: -float(r['tvl_btc'])):
    b, u = float(r['tvl_btc']), float(r['tvl_usd'])
    if b <= 0: continue  # closed products with no BTC today (Maple) stay in the history only
    rows_out.append([short(r['product']), r['category_code'], round(b, 4), round(u / 1e6, 4), kind_of(r['product'], r['category_code'])])
# what each product does, its yield where known, who runs it (data/product_notes.csv, one row per product in today's map), and the
# products listed but not counted (data/outside_totals.csv)
NOTES = {r['product']: r for r in rd(os.path.join(MM, 'product_notes.csv'))}
missing = [r['product'] for r in cur if float(r['tvl_btc']) > 0 and r['product'] not in NOTES]
assert not missing, 'products without a row in data/product_notes.csv: ' + ', '.join(missing)
info = {short(p): [n['how'], n['yield_btc'], n['run_by'], n['url']] for p, n in NOTES.items()}
assert len(info) == len(NOTES), 'two products share a short name'
tokens = {short(p): g['btc_tokens'] for p, g in GROUPS.items() if g['btc_tokens']}
names = {}
for r in cur:
    n = short(r['product'])
    d = (GROUPS[r['product']]['label'] or disp(r['product'])) if r['product'] in GROUPS else n.replace(' - direct / other holders', '')
    if d != n: names[n] = d
outside = [[r['kind'], r['product'], r['yield_btc'], r['size'], r['why_not_counted'], r['url']] for r in rd(os.path.join(MM, 'outside_totals.csv'))]
# money markets and CDP collateral: one row per protocol, only the BTC no product above already counts (data/money_markets*.csv)
MMCAT = {'money_market': ('C7', 'market'), 'cdp': ('C8', 'cdp')}
mmrows, mmgross = [], []
for r in rd(os.path.join(MM, 'money_markets.csv')):
    cat, kind = MMCAT[r['segment']]
    b = float(r['btc_counted'])
    if r['segment'] == 'money_market': mmgross.append([r['protocol'], round(float(r['btc_supplied']), 1)])
    if b <= 0: continue
    mmrows.append([r['protocol'], cat, round(b, 4), round(b * PRICE / 1e6, 4), kind])
    info[r['protocol']] = [r['how'], r['supply_apy'], r['protocol'], r['url']]
rows_out += sorted(mmrows, key=lambda x: -x[2])
mmgross.sort(key=lambda x: -x[1])

# ---------- history: month-end BTC and $M by category ----------
ph = [dict(r, category_code=cat_of(r)) for r in rd(os.path.join(MM, 'market_map_history_monthly.csv'))]
months = sorted({r['month'] for r in rd(os.path.join(MM, 'category_history_monthly.csv'))})
H = {u: {c: [0.0] * len(months) for c in ORDER} for u in ('btc', 'usd')}
KH = {k: [0.0] * len(months) for k in ('points', 'vaults', 'pools')}
for r in ph:
    if r['include_net'] != '1' or r['category_code'] not in ORDER: continue
    i, b, u = months.index(r['month']), float(r['tvl_btc']), float(r['tvl_usd']) / 1e6
    H['btc'][r['category_code']][i] += b; H['usd'][r['category_code']][i] += u
    if r['category_code'] == 'C6': KH[kind_of(r['product'], 'C6')][i] += b
for r in rd(os.path.join(MM, 'money_markets_monthly.csv')):
    if r['month'] not in months: continue
    cat, _ = MMCAT[r['segment']]
    i = months.index(r['month'])
    H['btc'][cat][i] += float(r['btc_counted']); H['usd'][cat][i] += float(r['usd_counted']) / 1e6
hist = dict(x=months, btc={c: [round(v) for v in H['btc'][c]] for c in ORDER}, usd={c: [round(v) for v in H['usd'][c]] for c in ORDER})
kinds = {k: [round(v) for v in vals] for k, vals in KH.items()}
# snapshot products with no month-end history (the history leaves them out)
with_hist = {r['product'] for r in ph}
nohist = [[short(r['product']), r['category_code']] for r in cur if r['product'] not in with_hist and float(r['tvl_btc']) > 0]
# products that held BTC in the history but not today, by the category (and kind) they were in when they last did: name, peak BTC
# and month, last month with at least 2% of the peak. Holder-split names are joined, so a renamed row is not "ended".
base = lambda p: p.replace(' - direct / other holders', '')
live = {base(r['product']) for r in cur if float(r['tvl_btc']) > 0}
pk, lastm = {}, {}
for r in sorted(ph, key=lambda r: r['month']):
    if r['include_net'] != '1' or r['category_code'] not in ORDER: continue
    q, b = base(r['product']), float(r['tvl_btc'])
    if b > pk.get(q, (0,))[0]: pk[q] = (b, r['month'])
for r in sorted(ph, key=lambda r: r['month']):
    if r['include_net'] != '1' or r['category_code'] not in ORDER: continue
    q, b = base(r['product']), float(r['tvl_btc'])
    if q in pk and b >= max(1.0, 0.02 * pk[q][0]): lastm[q] = (r['month'], r['category_code'], kind_of(r['product'], r['category_code']))
ended = collections.defaultdict(list)
for q, (b, m) in pk.items():
    if q in live or b < 20 or q not in lastm: continue
    lm, c, k = lastm[q]
    ended[c].append([disp(q), round(b), m, lm, k])
for c in ended: ended[c].sort(key=lambda x: -x[1])
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

data = json.dumps(dict(hist=hist, kinds=kinds, c1hist=c1hist, top=T, nohist=nohist, rows=rows_out, names=names, ended=ended,
                       cats={c: list(CAT[c]) for c in ORDER}, info=info, tokens=tokens, outside=outside, mmgross=mmgross), separators=(',', ':'))
with open(OUT, 'w') as f: f.write(data)
for a in sys.argv[1:]:
    if a.startswith('--check='):
        with open(a[8:], 'w') as f: json.dump(dict(map=mp, hist=hist), f)
print('ok', OUT, 'default map', mp['total_btc'], 'BTC', mp['total_usd'], '$M', mp['n'], 'products', [(c['k'], c['btc'], c['n']) for c in mp['cats']])
catbtc = collections.Counter()
for r in rows_out: catbtc[r[1]] += r[2]
print('by category now', {k: round(v) for k, v in sorted(catbtc.items())}, '| no history', nohist)
print('ended', {c: [(x[0], x[1]) for x in L] for c, L in sorted(ended.items())})
if '--inject' in sys.argv:
    page = os.path.join(V3, 'index.html')
    with open(page, encoding='utf-8') as f: src = f.read()
    src, n = re.subn(r'^const V3 = \{.*\};$', lambda m: 'const V3 = ' + data + ';', src, count=1, flags=re.M)
    assert n == 1, 'const V3 line not found in index.html'
    with open(page, 'w', encoding='utf-8') as f: f.write(src)
    print('injected into', page)
