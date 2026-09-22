# Daily history of every Morpho market position and vault position of the mHyperBTC strategy wallet (Morpho API)
import json,urllib.request,time
def gql(q,v=None):
    for i in range(4):
        req=urllib.request.Request('https://api.morpho.org/graphql',data=json.dumps({'query':q,'variables':v or {}}).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
        try: return json.load(urllib.request.urlopen(req,timeout=120))
        except urllib.error.HTTPError as e: err=e.read()[:2000].decode()
        except Exception as e: err=str(e)
        time.sleep(3)
    return {'errors':err}
W='0x933adedd85824da75ec8a334a7907e69e7c02833'
S,E=1761955200,1790035200  # 2025-11-01 .. 2026-09-22
opt='{startTimestamp:%d,endTimestamp:%d,interval:DAY}'%(S,E)
pos=json.load(open('raw/morpho_user_positions.json'))
out={'markets':{},'v1':{},'v2':{}}
for cid,r in pos.items():
    u=r['data']['userByAddress']
    for p in u['marketPositions']:
        mk=p['market']['marketId']
        q='''query($u:String!,$m:String!,$c:Int!){marketPosition(userAddress:$u,marketUniqueKey:$m,chainId:$c){historicalState{collateral(options:%s){x y} collateralUsd(options:%s){x y} borrowAssets(options:%s){x y} borrowAssetsUsd(options:%s){x y} supplyAssetsUsd(options:%s){x y}}}}'''%(opt,opt,opt,opt,opt)
        h=gql(q,{'u':W,'m':mk,'c':int(cid)})
        out['markets'][f'{cid}:{mk}']={'market':p['market'],'hist':h}
        print(cid,mk[:10],'%s/%s'%((p['market']['collateralAsset'] or {}).get('symbol'),p['market']['loanAsset']['symbol']),'ok' if 'data' in h else h)
    for v in u['vaultV2Positions']:
        a=v['vault']['address']
        q='''query($u:String!,$v:String!,$c:Int!){vaultV2PositionByAddress(userAddress:$u,vaultAddress:$v,chainId:$c){history{assets(options:%s){x y} assetsUsd(options:%s){x y}}}}'''%(opt,opt)
        h=gql(q,{'u':W,'v':a,'c':int(cid)}); out['v2'][f'{cid}:{a}']={'vault':v['vault'],'hist':h}
        print(cid,'V2',v['vault']['name'],'ok' if 'data' in h else h)
    for v in u['vaultPositions']:
        a=v['vault']['address']
        q='''query($u:String!,$v:String!,$c:Int!){vaultPosition(userAddress:$u,vaultAddress:$v,chainId:$c){historicalState{assetsUsd(options:%s){x y}}}}'''%(opt)
        h=gql(q,{'u':W,'v':a,'c':int(cid)}); out['v1'][f'{cid}:{a}']={'vault':v['vault'],'hist':h}
        print(cid,'V1',v['vault']['name'],'ok' if 'data' in h else h)
json.dump(out,open('raw/morpho_pos_history.json','w'))
