# For each Morpho BTC-collateral market with borrow >= $2M: list positions with debt >= $2M
from morpho import gql
import json
mk=json.load(open('../raw/morpho_btc_markets.json'))
rows=[]
for m in mk:
    if (m['state']['borrowAssetsUsd'] or 0) < 2e6: continue
    q='''{ marketPositions(first:60, orderBy:BorrowShares, orderDirection:Desc, where:{marketUniqueKey_in:["%s"], chainId_in:[%d], borrowShares_gte:"1"}){ items{ user{address} state{collateral collateralUsd borrowAssets borrowAssetsUsd} } } }'''%(m['marketId'],m['chain']['id'])
    r=gql(q)
    for it in r['data']['marketPositions']['items']:
        s=it['state']
        if (s['borrowAssetsUsd'] or 0) >= 2e6:
            dec=8 if m['collateralAsset']['symbol'] in ('cbBTC','WBTC','kBTC','LBTC','cirBTC','vbWBTC','tBTC') else 18
            rows.append(dict(chain=m['chain']['network'],chainId=m['chain']['id'],market=m['marketId'],pair=m['collateralAsset']['symbol']+'/'+m['loanAsset']['symbol'],
               user=it['user']['address'],coll_raw=s['collateral'],coll_usd=s['collateralUsd'],debt_usd=s['borrowAssetsUsd']))
    print(m['chain']['network'],m['collateralAsset']['symbol'],m['loanAsset']['symbol'],len(rows),flush=True)
json.dump(rows,open('../raw/morpho_top_borrowers.json','w'),indent=1)
for r in sorted(rows,key=lambda r:-r['debt_usd']):
    print(f"{r['pair']:<16} {r['chain']:<10} {r['user']} debt ${r['debt_usd']/1e6:7.2f}M coll ${ (r['coll_usd'] or 0)/1e6:7.2f}M")
