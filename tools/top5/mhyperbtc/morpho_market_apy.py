# Daily borrow APY history of every Morpho market the strategy wallet touched (Morpho API)
import json,urllib.request,time
def gql(q,v=None):
    for i in range(4):
        req=urllib.request.Request('https://api.morpho.org/graphql',data=json.dumps({'query':q,'variables':v or {}}).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
        try: return json.load(urllib.request.urlopen(req,timeout=120))
        except urllib.error.HTTPError as e: err=e.read()[:1500].decode()
        except Exception as e: err=str(e)
        time.sleep(3)
    return {'errors':err}
S,E=1761955200,1790035200
opt='{startTimestamp:%d,endTimestamp:%d,interval:DAY}'%(S,E)
pos=json.load(open('raw/morpho_user_positions.json')); out={}
extra=[(1,'0x51c6fa2e3ab990af15e95a8c91e93482d7a87068c60133e1c7e8000f91ec7618'),(143,'0x1456e298a2eb4a0cda636aedf75cb694e66748500bea6f664d2250c33edd3ead')]
keys=[(int(c),p['market']['marketId']) for c,r in pos.items() for p in r['data']['userByAddress']['marketPositions']]+extra
for c,mk in keys:
    q='''query($m:String!,$c:Int!){marketById(marketId:$m,chainId:$c){historicalState{borrowApy(options:%s){x y} supplyApy(options:%s){x y} borrowAssetsUsd(options:%s){x y} collateralAssets(options:%s){x y} supplyAssetsUsd(options:%s){x y}}}}'''%(opt,opt,opt,opt,opt)
    r=gql(q,{'m':mk,'c':c}); out[f'{c}:{mk}']=r; print(c,mk[:10],'ok' if 'data' in r else r)
json.dump(out,open('raw/morpho_market_apy.json','w'))
