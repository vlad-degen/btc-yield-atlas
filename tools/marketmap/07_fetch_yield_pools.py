"""Selected DefiLlama yields pools (for products without a protocol-level token series) + their daily charts.
Output: raw/yield_pools_selected.json, raw/pool_charts/{pool}.json"""
import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import RAW
P = json.load(open(os.path.join(RAW, 'pools_0921.json'))); P = P.get('data', P)
SEL = []
for x in P:
    sym = (x.get('symbol') or '').upper(); meta = x.get('poolMeta') or ''; proj = x.get('project')
    if proj == 'midas-rwa' and sym == 'BTC': SEL.append(dict(x, product={'mHyperBTC': 'Midas mHyperBTC (Hyperithm)', 'mRe7BTC': 'Midas mRe7BTC (Re7)', 'mBTC': 'Midas mBTC'}.get(meta, 'Midas ' + meta)))
    elif proj == 'fusion-by-ipor' and ('BTC' in sym):
        if (meta.startswith('TESS') or 'Debt Vault Loop' in meta) and ('Loop' in meta or 'LOOP' in meta) and 'cbETH' not in meta: prod = 'Tesseract TESS wBTC debt-loop vaults (IPOR Fusion)'
        elif meta in ('wBTC Dollar Carry', 'TAU InfiniFi BTC Carry'): prod = 'BTCD Labs / TAU BTC dollar-carry vaults (IPOR Fusion)'
        else: continue
        SEL.append(dict(x, product=prod))
    elif proj == 'ether.fi-stake' and sym == 'EBTC': SEL.append(dict(x, product='ether.fi eBTC'))
json.dump(SEL, open(os.path.join(RAW, 'yield_pools_selected.json'), 'w'), indent=1)
os.makedirs(os.path.join(RAW, 'pool_charts'), exist_ok=True)
for x in SEL:
    f = os.path.join(RAW, 'pool_charts', x['pool'] + '.json')
    if os.path.exists(f): continue
    for a in range(4):
        try:
            d = urllib.request.urlopen(urllib.request.Request('https://yields.llama.fi/chart/' + x['pool'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read()
            json.loads(d); open(f, 'wb').write(d); break
        except Exception as e: print('retry', x['pool'], e); time.sleep(5)
    time.sleep(0.5)
for x in SEL: print(x['product'], x['chain'], x.get('poolMeta'), round(x['tvlUsd'] / 1e6, 2), x['pool'])
