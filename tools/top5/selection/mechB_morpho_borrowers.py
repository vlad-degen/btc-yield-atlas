import sys, json; sys.path.insert(0,'.')
from mechB_morpho import gql
ms=json.load(open('../raw/mechB/morpho_btc_stable_markets.json'))
chainid={'Ethereum':1,'Base':8453,'Arc':5042,'World Chain':480,'Arbitrum One':42161,'Monad':143,'HyperEVM':999}
res=[]
for m in ms:
    cid=chainid[m['chain']['network']]
    q='''{ marketPositions(first:12, orderBy:BorrowShares, orderDirection:Desc, where:{marketUniqueKey_in:["%s"], chainId_in:[%d]}){ items{ user{ address } state{ borrowAssetsUsd collateralUsd collateral } } } }'''%(m['marketId'],cid)
    import time
    for i in range(4):
        d=gql(q)
        if 'data' in d: break
        time.sleep(3)
    if 'data' not in d: print(m['marketId'],d); continue
    for p in d['data']['marketPositions']['items']:
        b=p['state']['borrowAssetsUsd'] or 0
        if b<500000: continue
        res.append((m['chain']['network'],m['collateralAsset']['symbol']+'/'+m['loanAsset']['symbol'],p['user']['address'],None,b,p['state']['collateralUsd']))
json.dump(res, open('../raw/mechB/morpho_btc_top_borrowers.json','w'))
for r in res: print(f"{r[0]}|{r[1]}|{r[2]}|{r[3]}|borrow ${r[4]/1e6:.2f}M|coll ${r[5]/1e6:.2f}M")
