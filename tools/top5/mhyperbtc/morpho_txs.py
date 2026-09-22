# All Morpho market + vault transactions of the mHyperBTC strategy wallet (Morpho API), Ethereum/Monad/Stable
import json, sys, datetime, urllib.request
def gql(q,v=None):
    req=urllib.request.Request('https://api.morpho.org/graphql',data=json.dumps({'query':q,'variables':v or {}}).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
    try: return json.load(urllib.request.urlopen(req,timeout=90))
    except urllib.error.HTTPError as e: return {'errors':e.read()[:1000]}
W='0x933adedd85824da75ec8a334a7907e69e7c02833'
qm='''query($a:[String!],$c:[Int!],$skip:Int){marketTransactions(first:500,skip:$skip,orderBy:Timestamp,orderDirection:Asc,where:{userAddress_in:$a,chainId_in:$c}){items{txHash timestamp type chain{id} market{marketId loanAsset{symbol decimals} collateralAsset{symbol decimals}} data{
 ... on MarketTransactionTransferData{assets shares}
 ... on MarketTransactionCollateralTransferData{assets}
 ... on MarketTransactionLiquidationData{repaidAssets seizedAssets badDebtAssets liquidator}}}}}'''
qv1='''query($a:[String!],$c:[Int!]){vaultV1Transactions(first:1000,orderBy:Time,orderDirection:Asc,where:{userAddress_in:$a,chainId_in:$c}){items{txHash timestamp type chain{id} assets shares vault{name address asset{symbol decimals}}}}}'''
qv2='''query($a:[String!],$c:[Int!],$skip:Int){vaultV2transactions(first:500,skip:$skip,orderBy:Time,orderDirection:Asc,where:{userAddress_in:$a,chainId_in:$c}){items{txHash timestamp type chain{id} assets shares vault{name address asset{symbol decimals}}}}}'''
out={'market':[],'v1':[],'v2':[]}
for c in [1,143,988]:
    skip=0
    while True:
        r=gql(qm,{'a':[W],'c':[c],'skip':skip})
        if 'errors' in r: print('ERR m',c,r['errors']); break
        it=r['data']['marketTransactions']['items']; out['market']+=it
        if len(it)<500: break
        skip+=500
    r=gql(qv1,{'a':[W],'c':[c]})
    if 'errors' in r: print('ERR v1',c,r['errors'])
    else: out['v1']+=r['data']['vaultV1Transactions']['items']
    r=gql(qv2,{'a':[W],'c':[c],'skip':0})
    if 'errors' in r: print('ERR v2',c,r['errors'])
    else: out['v2']+=r['data']['vaultV2transactions']['items']
json.dump(out,open('raw/morpho_txs.json','w'),indent=0)
rows=[]
for t in out['market']:
    m=t['market']; d=t['data']; ca=m.get('collateralAsset') or {}
    if 'COLLATERAL' in t['type'].upper(): amt=int(d['assets'])/10**ca.get('decimals',8); unit=ca.get('symbol')
    elif 'repaidAssets' in d: amt=int(d['repaidAssets'])/10**m['loanAsset']['decimals']; unit=m['loanAsset']['symbol']
    else: amt=int(d['assets'])/10**m['loanAsset']['decimals']; unit=m['loanAsset']['symbol']
    rows.append((int(t['timestamp']),t['chain']['id'],t['type'],'%s/%s'%(ca.get('symbol'),m['loanAsset']['symbol']),amt,unit,t['txHash']))
for t in out['v1']:
    a=t['vault']['asset']; rows.append((int(t['timestamp']),t['chain']['id'],t['type'],'V1 '+t['vault']['name'],int(t['assets'] or 0)/10**a['decimals'],a['symbol'],t['txHash']))
for t in out['v2']:
    a=t['vault']['asset']; rows.append((int(t['timestamp']),t['chain']['id'],t['type'],'V2 '+t['vault']['name'],int(t['assets'] or 0)/10**a['decimals'],a['symbol'],t['txHash']))
rows.sort()
with open('raw/morpho_txs.csv','w') as f:
    f.write('utc,chain,type,market_or_vault,amount,unit,tx\n')
    for r in rows: f.write('%s,%d,%s,%s,%.6f,%s,%s\n'%(datetime.datetime.utcfromtimestamp(r[0]).strftime('%Y-%m-%d %H:%M'),r[1],r[2],r[3],r[4],r[5],r[6]))
print(len(rows))
