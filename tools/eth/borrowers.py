"""Current API discovery of ETH collateral borrowers; not carry classification or T accounting."""
import concurrent.futures,json
from collect import ROOT,request,read_latest
from discover import FAMILY

def run():
 markets=read_latest('morpho_markets_discovery')['data']['markets']['items']
 selected=[m for m in markets if m.get('collateralAsset') and m['collateralAsset']['symbol'].upper() in FAMILY and m['loanAsset']['symbol'] in ['WETH','USDC','USDT','PYUSD','RLUSD','DAI']]
 selected.sort(key=lambda m:m['state']['borrowAssetsUsd'],reverse=True)
 q='''query($markets:[String!]){marketPositions(first:10,orderBy:BorrowShares,orderDirection:Desc,where:{marketUniqueKey_in:$markets,chainId_in:[1,8453,42161,10],borrowShares_gte:"1"}){items{user{address}market{marketId chain{id} lltv loanAsset{symbol address decimals}collateralAsset{symbol address decimals}}state{collateral collateralUsd borrowShares borrowAssets borrowAssetsUsd}}pageInfo{count countTotal}}}'''
 jobs=[('morpho_borrowers_'+m['marketId'],'https://api.morpho.org/graphql',{'query':q,'variables':{'markets':[m['marketId']]}}) for m in selected]
 first=request(*jobs[0]) if jobs else None
 if jobs and (not first or not first.get('data')):raise RuntimeError('Validate the first query before a batch')
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=[first]+list(pool.map(lambda j:request(*j),jobs[1:]))
 out=[]
 for m,r in zip(selected,results):
  out.append({'market':m,'source_status':'success' if r and r.get('data') else 'failed','positions':r.get('data',{}).get('marketPositions',{}) if r else None,'target_snapshot_verified':False,'carry_mechanism_verified':False})
 (ROOT/'data/eth/morpho_borrower_screen.json').write_text(json.dumps(out,indent=2))
 print('Selected markets',len(selected),'successful',sum(x['source_status']=='success' for x in out))

if __name__=='__main__':run()
