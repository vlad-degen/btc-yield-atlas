"""Build the chart data object embedded in index.html as `const V3 = {...}` (market map donut, category history, top-5 series).
Reads data/*.csv and data/top5/<product>/*; writes JSON to paste over the V3 object.
Usage: python3 tools/site_data.py [repo root] [out json]"""
import csv, json, os, sys, collections

V3 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), 'v3data.json')
MM = os.path.join(V3, 'data')
TP = lambda *a: os.path.join(V3, 'data', 'top5', *a)
rd = lambda p: list(csv.DictReader(open(p)))
CAT = {'C1': ('Carry: BTC collateral, dollar loan', 's2'), 'C2': ('Staking and restaking', 's1'), 'C3': ('Basis and delta-neutral', 's3'),
       'C4': ('Options selling', 's7'), 'C5': ('Credit to institutions', 's4'), 'C6': ('Farming, LP and emissions', 's5')}
ORDER = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
SHORT = {'Babylon (BTC staking) - other stakers (Kraken, Binance, custodians, direct)': 'Babylon, other stakers (mostly Kraken)',
         'Kraken Bitcoin Vault (Advanced Strategies BTC)': 'Kraken Bitcoin Vault', 'Lombard LBTC - direct / other holders': 'Lombard LBTC',
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
cur = [r for r in rd(os.path.join(MM, 'market_map_current.csv')) if r['include_net'] == '1' and r['tvl_btc'] and r['category_code'] in CAT]
tot_btc = sum(float(r['tvl_btc']) for r in cur); tot_usd = sum(float(r['tvl_usd']) for r in cur)
by = collections.defaultdict(list)
for r in cur: by[r['category_code']].append(r)
cats = []
for c in sorted(by, key=lambda c: -sum(float(r['tvl_btc']) for r in by[c])):
    L = sorted(by[c], key=lambda r: -float(r['tvl_btc']))
    items, other_b, other_u, other_n = [], 0.0, 0.0, 0
    for r in L:
        b, u = float(r['tvl_btc']), float(r['tvl_usd'])
        if (b / tot_btc >= 0.012 or (c == 'C1' and b >= 100)) and len(items) < 6: items.append(dict(name=short(r['product']), value=round(u / 1e6, 1), btc=round(b, 1)))
        else: other_b += b; other_u += u; other_n += 1
    if other_n: items.append(dict(name=f'{other_n} smaller products', value=round(other_u / 1e6, 1), btc=round(other_b, 1)))
    cats.append(dict(k=c, name=CAT[c][0], color=CAT[c][1], value=round(sum(float(r['tvl_usd']) for r in L) / 1e6, 1),
                     btc=round(sum(float(r['tvl_btc']) for r in L), 1), n=len(L), items=items))
# C1 detail (all rows incl. tiny)
c1 = [dict(name=short(r['product']), btc=round(float(r['tvl_btc']), 1), usd=round(float(r['tvl_usd']) / 1e6, 1)) for r in sorted(by['C1'], key=lambda r: -float(r['tvl_btc']))]

# ---------- history ----------
h = rd(os.path.join(MM, 'category_history_monthly.csv'))
months = sorted({r['month'] for r in h})
hist = dict(x=months, btc={c: [0.0] * len(months) for c in ORDER}, usd={c: [0.0] * len(months) for c in ORDER})
for r in h:
    i = months.index(r['month'])
    hist['btc'][r['category_code']][i] = round(float(r['tvl_btc_net']))
    hist['usd'][r['category_code']][i] = round(float(r['tvl_usd_net']) / 1e6)
# C1 by product (history)
ph = rd(os.path.join(MM, 'market_map_history_monthly.csv'))
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
        dict(name='Borrow rate, RLUSD', color='s8', values=[1.60, 3.09, 3.43, 3.07]),
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
        dict(name='Borrow rate, USDC', color='s8', values=[float(r['borrow_rate']) for r in by_]),
        dict(name='Where the USDC goes, without rewards', color='s3', values=[float(r['gtusdc_apy_organic']) for r in by_])]))
# optional: ether.fi and mHyperBTC (filled when their CSVs exist)
for key, d in [('etherfi', 'etherfi'), ('mhyper', 'mhyperbtc')]:
    p = TP(d, 'site_series.json')
    if os.path.exists(p): T[key] = json.load(open(p))

json.dump(dict(map=dict(cats=cats, total_btc=round(tot_btc), total_usd=round(tot_usd / 1e6), c1=c1), hist=hist, c1hist=c1hist, top=T), open(OUT, 'w'), separators=(',', ':'))
print('ok', OUT, round(tot_btc), round(tot_usd / 1e6), [(c['k'], c['btc']) for c in cats])
