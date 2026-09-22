import sys, json; sys.path.insert(0,'.')
from mechB_morpho import gql
out=[]; skip=0
while True:
    q='''{ vaultV2s(first:100, skip:%d, where:{totalAssetsUsd_gte:50000, chainId_in:[1,8453,747474,999,42161,137,130,10,480,143,988,4217,4663,5042]}){ items{ address name symbol chain{network} asset{symbol address} totalAssets totalAssetsUsd idleAssetsUsd curators{items{name}} adapters{ items{ address type assetsUsd } } } } }'''%skip
    d=gql(q)
    if 'errors' in d: print(d['errors']); break
    it=d['data']['vaultV2s']['items']; out+=it
    if len(it)<100: break
    skip+=100
json.dump(out, open('../raw/mechB/morpho_v2_vaults.json','w'))
print(len(out),'v2 vaults >50k')
types={}
for v in out:
    for a in v['adapters']['items']: types[a['type']]=types.get(a['type'],0)+1
print('adapter types across all v2 vaults:',types)
btc=[v for v in out if 'BTC' in (v['asset']['symbol'] or '').upper()]
print(len(btc),'BTC-asset v2 vaults')
for v in sorted(btc, key=lambda v:-(v['totalAssetsUsd'] or 0)):
    cur=','.join(c['name'] for c in v['curators']['items'])
    ad=[(a['type'],round((a['assetsUsd'] or 0)/1e6,2)) for a in v['adapters']['items']]
    print(f"{v['chain']['network']}|{v['name']}|{v['address']}|{v['asset']['symbol']}|${(v['totalAssetsUsd'] or 0)/1e6:.2f}M|{cur}|{ad}")
