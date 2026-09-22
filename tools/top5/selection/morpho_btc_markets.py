# Fetch all Morpho Blue markets (all chains covered by blue-api) with BTC-like collateral and borrow >= $100k
from morpho import gql
import json
Q='''query($skip:Int){ markets(first:500, skip:$skip, where:{borrowAssetsUsd_gte:100000}){ pageInfo{countTotal count} items{ marketId listed lltv
 chain{id network} collateralAsset{symbol address name price{usd}} loanAsset{symbol address decimals price{usd}}
 state{ collateralAssets collateralAssetsUsd borrowAssets borrowAssetsUsd supplyAssetsUsd utilization borrowApy timestamp} } } }'''
out=[];skip=0
while True:
    r=gql(Q,{'skip':skip}); d=r['data']['markets']; out+=d['items']
    print(skip,d['pageInfo'])
    if len(d['items'])<500: break
    skip+=500
btc=[m for m in out if m['collateralAsset'] and 'BTC' in (m['collateralAsset']['symbol'] or '').upper()]
json.dump(btc,open('../raw/morpho_btc_markets.json','w'),indent=1)
print('all markets w/ borrow>=100k:',len(out),'btc-collateral:',len(btc))
tc=sum(m['state']['collateralAssetsUsd'] or 0 for m in btc); tb=sum(m['state']['borrowAssetsUsd'] or 0 for m in btc)
print('BTC-coll markets: coll $%.1fM borrow $%.1fM'%(tc/1e6,tb/1e6))
for m in sorted(btc,key=lambda m:-(m['state']['borrowAssetsUsd'] or 0))[:60]:
    s=m['state']; print(f"{m['collateralAsset']['symbol']:>14}/{m['loanAsset']['symbol']:<8} {m['chain']['network']:<12} coll ${ (s['collateralAssetsUsd'] or 0)/1e6:8.2f}M bor ${(s['borrowAssetsUsd'] or 0)/1e6:8.2f}M {m["marketId"]}")
r=gql('{chains{id network}}'); print(r['data'])
