"""Reconcile the protocol-based snapshot with the page's C0 row (169,406 BTC = DefiLlama yields BTC lending pools on 09-20, $13.86B
less Zest v2 and Accountable) and with its per-protocol $B split. -> out/reconcile.json, printed tables."""
import collections, csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mmlib import *

PX = PRICE_SNAP
POOLS = json.load(open(os.path.join(RAW, 'btc_lending_pools.json')))
SUMM = json.load(open(os.path.join(D, 'out', 'summary.json')))
SEL = SUMM['selection']
MM = {r['slug']: r for r in csv.DictReader(open(os.path.join(D, 'mm_monthly.csv'))) if r['month'] == '2026-09'}
L = json.load(open(os.path.join(D, 'out', 'mm_long.json')))
PAGE_BTC, PAGE_USD = 169406.02, 13752041806
PAGE_SPLIT = [('Aave v3', ['aave-v3'], 5.32), ('Morpho Blue', ['morpho-blue'], 4.98), ('SparkLend', ['sparklend'], 0.86), ('Venus', ['venus-core-pool'], 0.64),
              ('Compound v3', ['compound-v3'], 0.61), ('JustLend', ['justlend-v1'], 0.54), ('Tydro (Ink)', ['tydro'], 0.09), ('Aave v4', ['aave-v4'], 0.09), ('Kamino', ['kamino-lend'], 0.09)]

def chart(pid):
    f = os.path.join(RAW, 'charts', pid + '.json')
    return {r['timestamp'][:10]: r for r in json.load(open(f))['data']} if os.path.exists(f) else None
y = collections.defaultdict(lambda: collections.defaultdict(float))  # project -> kind -> usd at 09-20
cat = {}
for p in POOLS:
    if p['category'] not in ('Lending', 'CDP', 'Uncollateralized Lending'):
        continue
    ch = chart(p['pool'])
    if ch is None:
        v = p['tvlUsd'] * PX / 85362.09
    else:
        r = ch.get('2026-09-20'); v = r['tvlUsd'] if r else 0.0
    y[p['project']]['extra' if p['extra_symbol'] else 'list'] += v
    cat[p['project']] = p['category']
tot_y = sum(sum(k.values()) for k in y.values())
zest, acc = sum(y['zest-v2'].values()), sum(y['accountable'].values())
recon = dict(page_btc=PAGE_BTC, yields_all_usd=tot_y, yields_less_zest_acc_btc=(tot_y - zest - acc) / PX, zest_btc=zest / PX, acc_btc=acc / PX)

def seg(s):
    return SEL.get(s, [None])[0]
lines = collections.OrderedDict()
lines['page C0 row (yields pools, Lending+CDP+Uncollateralized, 09-20, less Zest v2 and Accountable)'] = PAGE_BTC
lines['reconstruction difference (pool set read 09-23; Jupiter Lend pools without a 09-20 point)'] = recon['yields_less_zest_acc_btc'] - PAGE_BTC
lines['+ Zest v2 and Accountable (yields)'] = (zest + acc) / PX
by_seg = collections.defaultdict(float)
for pj, k in y.items():
    by_seg[seg(pj) or 'not selected'] += sum(k.values()) / PX
lines['- CDP projects in the yields set (my cdp segment)'] = -by_seg['cdp']
lines['- lending-venue projects in the yields set (my venue segment)'] = -by_seg['venue']
lines['- yields projects below the $1M protocol threshold (not selected)'] = -by_seg['not selected']
lines['= yields BTC of the money-market projects'] = by_seg['money_market']
# symbol-list differences (yields BTC family broader than the map list)
extra_mm = sum(k['extra'] for pj, k in y.items() if seg(pj) == 'money_market') / PX
lines['- yields symbols outside the map BTC list (vault shares, SVBTC, CDCBTC, stSTXbtc ...)'] = -extra_mm
# per-project protocol vs yields(list) for money-market projects
diffs = {}
for pj, k in y.items():
    if seg(pj) != 'money_market':
        continue
    diffs[pj] = float(MM[pj]['btc_total']) - k['list'] / PX
special = {'accountable': 'Accountable: yields shows supplied BTC, protocol TVL excludes the lent BTC (587 BTC in btc_borrowed)',
           'takara-lend': 'Takara Lend: protocol data 0 from 2026-02, filled from its yields pools (so no difference)',
           'dolomite': 'Dolomite: stBTC on Berachain (247) dropped from the protocol data in 2026-08, still in yields',
           'zest-v2': 'Zest v2: yields shows supply (idle + lent); protocol TVL is idle only',
           'morpho-blue': 'Morpho Blue: protocol covers more chains / idle loan supply (Morph bgBTC 802, Citrea 100, Tempo 146, Arc 204, ...)',
           'lista-lending': 'Lista Lending: 3,075 BTCB in protocol TVL, one small yields pool',
           'euler-v2': 'Euler v2: yields lists a few EVK vaults only (aHyperBTC collateral vault 107 etc. missing)',
           'jupiter-lend': 'Jupiter Lend: yields pools have no 09-20 point', 'compound-v3': 'Compound v3: more markets/chains in protocol TVL'}
for pj in sorted(diffs, key=lambda k: -abs(diffs[k])):
    if pj in special:
        lines['  ' + special[pj]] = diffs[pj]
rest = sum(v for pj, v in diffs.items() if pj not in special)
lines['  other coverage / timing differences (00:00 vs 23:00 UTC points), 40 projects'] = rest
only = sum(float(MM[s]['btc_total']) for s in MM if MM[s]['segment'] == 'money_market' and s not in y)
lines['+ money-market protocols with BTC but no BTC yields pool (Aave v2 420, Suilend 163, Alpaca 120, AlphaFi 104, ...)'] = only
lines['= this data set: money_market btc_total (DefiLlama protocol TVL, token units)'] = sum(float(r['btc_total']) for r in MM.values() if r['segment'] == 'money_market')
chk = PAGE_BTC + sum(v for k, v in list(lines.items())[1:-1] if not k.startswith('= yields'))
lines['(check: sum of the bridge lines)'] = chk
for k, v in lines.items():
    print(f'{v:12,.1f}  {k}')
# page split vs protocol
split = []
for name, slugs, b in PAGE_SPLIT:
    yb = sum(sum(y[s].values()) for s in slugs) / 1e9
    pb = sum(float(MM[s]['btc_total']) for s in slugs)
    pu = sum(float(MM[s]['usd']) for s in slugs) / 1e9
    split.append(dict(protocol=name, page_usd_b=b, yields_0920_usd_b=round(yb, 3), protocol_btc_total=round(pb, 1), protocol_usd_b=round(pu, 3),
                      protocol_btc_x_81178_b=round(pb * PX / 1e9, 3), btc_borrowed=round(sum(float(MM[s]['btc_borrowed']) for s in slugs), 1)))
others_page = 0.62
split.append(dict(protocol='Others', page_usd_b=others_page, yields_0920_usd_b=round(tot_y / 1e9 - sum(r['yields_0920_usd_b'] for r in split), 3)))
for r in split: print(r)
json.dump(dict(recon=recon, bridge=lines, split=split), open(os.path.join(D, 'out', 'reconcile.json'), 'w'), indent=0)
# weighted supply APY of the BTC lending pools (yields, 09-23)
num = den = numb = numr = 0.0
for p in POOLS:
    if p['category'] in ('Lending', 'Uncollateralized Lending') and not p['extra_symbol']:
        den += p['tvlUsd']; num += p['tvlUsd'] * (p['apy'] or 0); numb += p['tvlUsd'] * (p['apyBase'] or 0); numr += p['tvlUsd'] * (p['apyReward'] or 0)
print('TVL-weighted APY % total', round(num / den, 4), 'base', round(numb / den, 4), 'reward', round(numr / den, 4), 'over $', round(den / 1e9, 2), 'B')
