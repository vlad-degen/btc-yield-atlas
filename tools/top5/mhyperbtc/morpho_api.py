import json, urllib.request, sys
def gql(q,v=None):
    req=urllib.request.Request('https://api.morpho.org/graphql',data=json.dumps({'query':q,'variables':v or {}}).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req,timeout=60))
if __name__=='__main__':
    W='0x933adedd85824da75ec8a334a7907e69e7c02833'
    out={}
    for cid in [1,143,988,747474,4217,8453,42161,999,10,130,137,480,4663,5042]:
        q='''query($a:String!,$c:Int!){userByAddress(address:$a,chainId:$c){marketPositions{market{marketId loanAsset{symbol address} collateralAsset{symbol address} lltv state{borrowApy supplyApy}} state{collateral collateralUsd borrowAssets borrowAssetsUsd supplyAssets supplyAssetsUsd}} vaultPositions{vault{address name symbol asset{symbol}} state{assets assetsUsd shares}} vaultV2Positions{vault{address name symbol asset{symbol}} assets assetsUsd shares}}}'''
        r=gql(q,{'a':W,'c':cid}); out[cid]=r
        print(cid, json.dumps(r)[:1500])
    json.dump(out,open('raw/morpho_user_positions.json','w'),indent=1)
