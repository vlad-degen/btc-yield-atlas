"""Morpho Blue API (blue-api.morpho.org/graphql): all markets with state, saved to raw/morpho/markets.json. Read 2026-09-23 (current state)."""
import json, os, subprocess, time
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, 'raw', 'morpho')
os.makedirs(OUT, exist_ok=True)

def gql(q, v=None):
    body = json.dumps({'query': q, 'variables': v or {}})
    for a in range(5):
        r = subprocess.run(['curl', '-sS', '-m', '120', '-A', 'Mozilla/5.0', '-H', 'Content-Type: application/json',
                            'https://blue-api.morpho.org/graphql', '-d', body], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            if 'errors' in d and not d.get('data'):
                print('errors', d['errors'][:1]); time.sleep(3); continue
            return d
        except Exception as e:
            print('retry', e, r.stdout[:200]); time.sleep(5)
    raise SystemExit('gql failed')

Q = '''query($skip:Int){ markets(first: 1000, skip: $skip) { pageInfo { countTotal count }
  items { marketId lltv listed chain { id network }
    loanAsset { address symbol decimals priceUsd } collateralAsset { address symbol decimals priceUsd }
    state { collateralAssets collateralAssetsUsd supplyAssets supplyAssetsUsd borrowAssets borrowAssetsUsd liquidityAssetsUsd supplyApy borrowApy netSupplyApy utilization } } } }'''
items = []
skip = 0
while True:
    d = gql(Q, {'skip': skip})
    m = d['data']['markets']
    items += m['items']
    print('got', len(items), 'of', m['pageInfo']['countTotal'], flush=True)
    if len(m['items']) < 1000:
        break
    skip += 1000
    time.sleep(1)
json.dump(items, open(os.path.join(OUT, 'markets.json'), 'w'))
