import sys, json; sys.path.insert(0,'.')
from mechB_morpho import gql
out=[]; skip=0
while True:
    q='''{ vaults(first:500, skip:%d, where:{totalAssetsUsd_gte:100000, chainId_in:[1,8453,747474,999,42161,137,130,10,480,143,988,4217,4663,5042]}){ items{ address name symbol chain{id network} asset{symbol address} state{ totalAssets totalAssetsUsd curators{name} allocation{ supplyAssetsUsd market{ marketId loanAsset{symbol} collateralAsset{symbol} } } } } } }'''%skip
    d=gql(q)
    if 'errors' in d: print(d['errors']); break
    it=d['data']['vaults']['items']; out+=it
    if len(it)<500: break
    skip+=500
json.dump(out, open('../raw/mechB/morpho_v1_vaults.json','w'))
btc=[v for v in out if 'BTC' in (v['asset']['symbol'] or '').upper()]
print(len(out), 'v1 vaults >100k;', len(btc),'BTC-asset')
for v in sorted(btc, key=lambda v:-(v['state']['totalAssetsUsd'] or 0)):
    cur=','.join(c['name'] for c in v['state'].get('curators') or [])
    colls=sorted(set(str((a['market']['collateralAsset'] or {}).get('symbol')) for a in v['state']['allocation'] if (a['supplyAssetsUsd'] or 0)>1000))
    print(f"{v['chain']['network']}|{v['name']}|{v['address']}|{v['asset']['symbol']}|${v['state']['totalAssetsUsd']/1e6:.2f}M|{cur}|coll:{colls}")
