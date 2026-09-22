import sys, json; sys.path.insert(0,'.')
from mechB_morpho import gql
STABLES=['USDC','USDT','USDT0','PYUSD','USDS','DAI','USDE','RLUSD','USD0','GHO','FRXUSD','AUSD','USDA','USDH','USDTB','EURC','CRVUSD','LVLUSD','USR','DEUSD','SUSDS','USDBC','USD₮0','USDT0','USDC.E','USD1','MUSD']
out=[]; skip=0
while True:
    q='''{ markets(first:200, skip:%d, orderBy:BorrowAssetsUsd, orderDirection:Desc, where:{chainId_in:[1,8453,747474,999,42161,137,130,10,480,143,988,4217,4663,5042], borrowAssetsUsd_gte:1000000}){ items{ marketId chain{id network} loanAsset{symbol} collateralAsset{symbol address} lltv state{ borrowAssetsUsd collateralAssetsUsd } } } }'''%skip
    d=gql(q)
    if 'errors' in d: print(d['errors']); break
    it=d['data']['markets']['items']; out+=it
    if len(it)<200: break
    skip+=200
btcm=[m for m in out if m['collateralAsset'] and 'BTC' in m['collateralAsset']['symbol'].upper() and m['loanAsset']['symbol'].upper() in STABLES]
json.dump(btcm, open('../raw/mechB/morpho_btc_stable_markets.json','w'))
tot=0
for m in btcm:
    tot+=m['state']['borrowAssetsUsd']
    print(f"{m['chain']['network']}|{m['collateralAsset']['symbol']}/{m['loanAsset']['symbol']}|{m['marketId']}|borrow ${m['state']['borrowAssetsUsd']/1e6:.1f}M|coll ${m['state']['collateralAssetsUsd']/1e6:.1f}M|lltv {int(m['lltv'])/1e16:.1f}")
print('total borrow $M', tot/1e6, 'markets',len(btcm))
