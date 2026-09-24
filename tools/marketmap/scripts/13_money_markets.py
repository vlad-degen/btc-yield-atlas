"""Post-build step: BTC in money markets and CDPs that the map does not count yet, for the site's two optional segments.

Reads the money-market data set in tools/marketmap/money_markets/ (built 2026-09-23 from DefiLlama protocol and yields data,
Morpho, Aave and IPOR reads; method in mm_notes.md there) and writes:
  data/money_markets.csv          one row per protocol at the 2026-09-20 snapshot
  data/money_markets_monthly.csv  the same, month-end 2024-09 .. 2026-09
"Counted" BTC = the protocol's plain BTC wrappers (WBTC, cbBTC, BTCB, kBTC, Tron BTC ...) in DefiLlama TVL (collateral plus supplied
BTC that is not lent out), less the positions of products the map already counts (mm_overlap.csv group B: Kraken's kBTC on
Morpho, Bitget, ether.fi, mHyperBTC, Upshift, IPOR, Yearn, Concrete, lend-only vaults). Yield-bearing tokens (LBTC, SolvBTC LSTs,
eBTC ...) are left out because the map counts them at their issuer, and protocols that are map products themselves (Zest v2,
Accountable, Wildcat, Native Credit Pool; group C) are left out whole. Lending venues go with the money markets; curated BTC
lending vaults are left out (their BTC sits inside Morpho and Euler, or in map rows). Overlaps measured only at the snapshot are
subtracted from the snapshot only, so earlier months are an upper bound.
Usage: python3 tools/marketmap/scripts/13_money_markets.py [repo root]
"""
import collections, csv, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
SRC = os.path.join(ROOT, 'tools', 'marketmap', 'money_markets')
DATA = os.path.join(ROOT, 'data')
SNAP_MONTH, PRICE = '2026-09', 81178
rd = lambda f: list(csv.DictReader(open(os.path.join(SRC, f))))
f = lambda v: float(v) if v not in ('', None) else 0.0

monthly = rd('mm_monthly.csv')
overlap = rd('mm_overlap.csv')
SELF = {r['slug'] for r in overlap if r['group'] == 'C'}  # protocols that are map products themselves
SEG = {'money_market': 'money_market', 'venue': 'money_market', 'cdp': 'cdp'}

# group B: positions of counted products, in the TVL column, by (protocol slug, month); a "a/b/c" slug goes to the first protocol
posB = collections.Counter()
for r in overlap:
    if r['group'] == 'B' and r['in_column'].startswith('btc_total'):
        posB[(r['slug'].split('/')[0], r['month'])] += f(r['btc'])

# supply rate of each protocol's BTC pools, weighted by pool size (DefiLlama yields, read 2026-09-23)
apy = collections.defaultdict(lambda: [0.0, 0.0, True])
for r in rd('mm_apy.csv'):
    a = apy[r['project']]; w = f(r['btc_0923'])
    a[0] += w * f(r['supply_apy_total_pct']); a[1] += w; a[2] = a[2] and r['btc_can_be_lent'] == 'no'
def rate(slug, seg):
    if seg == 'cdp': return '0 (collateral for a stablecoin)'
    if slug not in apy or apy[slug][1] == 0: return 'about 0'
    s, w, coll = apy[slug]
    if coll: return '0 (collateral only)'
    v = s / w
    return '<0.01' if v < 0.01 else f'{v:.2f}'

# the tokens and chains behind each protocol's plain BTC
toks = collections.defaultdict(collections.Counter)
for r in rd('mm_tokens_snapshot.csv'):
    if r['class'] == 'plain': toks[r['slug']][r['token']] += f(r['btc_in_tvl'])
chains = {r['slug']: r['chains_0920'] for r in rd('mm_protocols.csv')}
NAME = {'CBBTC': 'cbBTC', 'WBTC': 'WBTC', 'BTCB': 'BTCB', 'KBTC': 'kBTC', 'TBTC': 'tBTC', 'BTC.B': 'BTC.b', 'FBTC': 'FBTC', 'BTC': 'BTC',
        'SOLVBTC': 'SolvBTC', 'ENZOBTC': 'enzoBTC', 'UBTC': 'UBTC', 'XBTC': 'xBTC', 'BGBTC': 'bgBTC', 'SBTC': 'sBTC', 'WBTC.E': 'WBTC.e'}
NOTE = {'morpho-blue': ' Most of the cbBTC on Base (about 37,900 BTC) backs Coinbase\'s BTC-backed loans.',
        'justlend': ' Tron BTC; one holder took out about 80,000 BTC in September and October 2024.',
        'aave-v3': ' Lost about 24,000 BTC in the week after the KelpDAO exploit of 18 April 2026.'}
def how(slug, seg, name):
    t = ', '.join(NAME.get(k, k) for k, _ in toks[slug].most_common(3))
    ch = chains.get(slug, '')
    ch = (' on ' + ', '.join(ch.split()[:4]) + (' and others' if len(ch.split()) > 4 else '')) if ch else ''
    if seg == 'cdp':
        return f'BTC posted to {name}{ch} to mint a stablecoin; it earns nothing' + (f' ({t})' if t else '') + '.'
    return f'BTC supplied to {name}{ch}' + (f' ({t})' if t else '') + ', almost all of it as collateral for loans.' + NOTE.get(slug.split('-')[0] if slug.startswith('justlend') else slug, '')

snap, series = {}, []
for r in monthly:
    seg = SEG.get(r['segment'])
    if not seg or r['slug'] in SELF: continue
    plain, tot, usd = f(r['btc_plain']), f(r['btc_total']), f(r['usd'])
    counted = max(0.0, plain - posB[(r['slug'], r['month'])])
    px = usd / tot if tot > 0 else PRICE
    series.append(dict(segment=seg, protocol=r['protocol'], slug=r['slug'], month=r['month'], btc_counted=round(counted, 4),
                       usd_counted=round(counted * px)))
    if r['month'] == SNAP_MONTH:
        snap[r['slug']] = dict(segment=seg, protocol=r['protocol'], slug=r['slug'], btc_supplied=round(tot, 4), btc_plain=round(plain, 4),
                               btc_yieldbearing=round(f(r['btc_yieldbearing']), 4), btc_lent_out=round(f(r['btc_borrowed']), 4),
                               btc_in_counted_products=round(posB[(r['slug'], r['month'])], 4), btc_counted=round(counted, 4),
                               supply_apy=rate(r['slug'], seg), how=how(r['slug'], seg, r['protocol']),
                               url='https://defillama.com/protocol/' + r['slug'])

cols = ['segment', 'protocol', 'slug', 'btc_supplied', 'btc_plain', 'btc_yieldbearing', 'btc_lent_out', 'btc_in_counted_products',
        'btc_counted', 'supply_apy', 'how', 'url']
with open(os.path.join(DATA, 'money_markets.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n'); w.writeheader()
    for r in sorted(snap.values(), key=lambda r: (r['segment'] != 'money_market', -r['btc_counted'])): w.writerow(r)
with open(os.path.join(DATA, 'money_markets_monthly.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['segment', 'protocol', 'slug', 'month', 'btc_counted', 'usd_counted'], lineterminator='\n'); w.writeheader()
    for r in sorted(series, key=lambda r: (r['segment'], r['slug'], r['month'])): w.writerow(r)

tot = collections.Counter()
for r in snap.values(): tot[r['segment']] += r['btc_counted']
print('snapshot, BTC not counted elsewhere:', {k: round(v, 1) for k, v in tot.items()}, '| protocols:', collections.Counter(r['segment'] for r in snap.values()))
