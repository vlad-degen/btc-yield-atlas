# Morpho markets using mHyperBTC as collateral (Ethereum, Monad): state, borrowers, suppliers (vaults)
import json, sys, urllib.request
def gql(q,v=None):
    req=urllib.request.Request('https://api.morpho.org/graphql',data=json.dumps({'query':q,'variables':v or {}}).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
    try: return json.load(urllib.request.urlopen(req,timeout=90))
    except urllib.error.HTTPError as e: return {'errors':e.read()[:1500]}
TOK={1:'0xC8495EAFf71D3A563b906295fCF2f685b1783085',143:'0xF7Cf282eC810fDed974F99c0163E792f432892BC'}
q='''query($c:[Int!],$t:[String!]){markets(where:{chainId_in:$c,collateralAssetAddress_in:$t}){items{marketId lltv creationTimestamp oracleAddress irmAddress loanAsset{symbol address decimals} collateralAsset{symbol}
 state{collateralAssets collateralAssetsUsd borrowAssets borrowAssetsUsd supplyAssets supplyAssetsUsd utilization borrowApy supplyApy avgBorrowApy avgNetSupplyApy}
 supplyingVaults{address name symbol}
}}}'''
qp='''query($m:[String!],$c:[Int!]){marketPositions(first:100,where:{marketUniqueKey_in:$m,chainId_in:$c}){items{user{address} state{collateral collateralUsd borrowAssets borrowAssetsUsd supplyAssets supplyAssetsUsd}}}}'''
out={}
for c,t in TOK.items():
    r=gql(q,{'c':[c],'t':[t]}); out[c]=r
    if 'errors' in r: print(r); continue
    for m in r['data']['markets']['items']:
        s=m['state']
        print(c,m['marketId'],'%s/%s'%(m['collateralAsset']['symbol'],m['loanAsset']['symbol']),'lltv',int(m['lltv'])/1e18,'created',m['creationTimestamp'],'oracle',m['oracleAddress'])
        print('   collateral %.4f ($%.0f) borrow $%.0f supply $%.0f util %.1f%% borrowApy %.2f%% supplyApy %.2f%%'%(int(s['collateralAssets'] or 0)/1e18,s['collateralAssetsUsd'] or 0,s['borrowAssetsUsd'] or 0,s['supplyAssetsUsd'] or 0,100*(s['utilization'] or 0),100*(s['borrowApy'] or 0),100*(s['supplyApy'] or 0)))
        print('   supplying vaults',[(v['name'],v['address']) for v in m['supplyingVaults']])
        p=gql(qp,{'m':[m['marketId']],'c':[c]}); m['positions']=p
        for it in p['data']['marketPositions']['items']:
            st=it['state']
            if (st['collateral'] and int(st['collateral'])>0) or (st['supplyAssetsUsd'] or 0)>1:
                print('     %s coll %.4f borrow $%.0f supply $%.0f'%(it['user']['address'],int(st['collateral'] or 0)/1e18,st['borrowAssetsUsd'] or 0,st['supplyAssetsUsd'] or 0))
json.dump(out,open('raw/morpho_mhyper_markets.json','w'),indent=0)
