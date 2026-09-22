import sys,json
sys.path.insert(0,'.')
from morpho import gql
out={}
q1='''{ vaults(first:100, where:{chainId_in:[143]}){ items{ address name symbol asset{symbol address} curators{name} state{ totalAssets totalAssetsUsd apy netApy allocation{ supplyAssets supplyAssetsUsd market{ marketId loanAsset{symbol} collateralAsset{symbol} lltv state{ borrowAssetsUsd supplyAssetsUsd utilization } } } } } } }'''
try:
    r=gql(q1); out['v1']=r
    for v in r['data']['vaults']['items']:
        print('V1',v['address'],v['name'],v['asset']['symbol'],round(v['state']['totalAssetsUsd'] or 0), v['state']['netApy'])
except Exception as e: print('v1 err',e)
q2='''{ vaultV2s(first:100, where:{chainId_in:[143]}){ items{ address name symbol asset{symbol address} totalAssetsUsd totalAssets avgNetApy netApy curators{items{name}} adapters{items{ address type assetsUsd }} } } }'''
try:
    r=gql(q2); out['v2']=r
    for v in r['data']['vaultV2s']['items']:
        print('V2',v['address'],v['name'],v['asset']['symbol'],round(v.get('totalAssetsUsd') or 0), v.get('netApy'), v.get('avgNetApy'))
except Exception as e: print('v2 err',e)
json.dump(out,open('../raw/mechA/morpho_monad_vaults.json','w'),indent=1)
