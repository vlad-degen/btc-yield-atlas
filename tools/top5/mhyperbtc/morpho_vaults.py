# Morpho V2 vaults touched by the mHyperBTC strategy: fees, curator, allocation, positions (share of vault held by strategy)
import json,urllib.request
def gql(q,v=None):
    req=urllib.request.Request('https://api.morpho.org/graphql',data=json.dumps({'query':q,'variables':v or {}}).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
    try: return json.load(urllib.request.urlopen(req,timeout=90))
    except urllib.error.HTTPError as e: return {'errors':e.read()[:2500].decode()}
q='''query($a:String!,$c:Int!){vaultV2ByAddress(address:$a,chainId:$c){name symbol address creationTimestamp asset{symbol} curator{address} owner{address} totalAssetsUsd totalAssets performanceFee managementFee performanceFeeRecipient avgNetApy netApy apy
 adapters(first:10){items{address type assetsUsd ... on MorphoMarketV1Adapter{positions(first:10){items{market{marketId collateralAsset{symbol} loanAsset{symbol} state{borrowApy supplyApy utilization}} state{supplyAssetsUsd}}}} ... on MetaMorphoAdapter{metaMorpho{name address}}}}
 positions(first:50){items{user{address} assetsUsd}}
}}'''
V=[(143,'0xe09A93786275546690247d70f1767cF0b69e8Ea0'),(143,'0x78999cc96d2Ba0341588C60CcB0E91c6C33CF371'),(988,'0xb7Df8db22A5DBBFA9ebeb94b3910aec6a4f05c08'),(1,'0x55C1B6e461a6334B567bAF0FEb5D728715446f05'),(1,'0x093272C07700d3cA5301C3Bf9B3A392624179E2F'),(1,'0xCdbe4A5B5bAd2BC04492052Df2F881B5727d034d')]
out={}
for c,a in V:
    r=gql(q,{'a':a,'c':c}); out[f'{c}:{a}']=r
    if 'errors' in r: print(c,a,r['errors']); continue
    v=r['data']['vaultV2ByAddress']
    print('==',c,v['name'],v['symbol'],a,'asset',v['asset']['symbol'],'TVL $%.2fM'%(v['totalAssetsUsd']/1e6),'perfFee',v['performanceFee'],'mgmtFee',v['managementFee'],'netApy %.2f%%'%(100*(v['netApy'] or 0)),'curator',v['curator'] and v['curator']['address'],'created',v['creationTimestamp'])
    for ad in v['adapters']['items']:
        print('   adapter',ad['address'],ad['type'],'$%.2fM'%((ad['assetsUsd'] or 0)/1e6), (ad.get('metaMorpho') or {}).get('name',''))
        for p in ((ad.get('positions') or {}).get('items') or []):
            m=p['market']
            if (p['state']['supplyAssetsUsd'] or 0)>1000: print('      %s/%s $%.2fM borrowApy %.2f%% util %.0f%%'%((m['collateralAsset'] or {}).get('symbol'),m['loanAsset']['symbol'],p['state']['supplyAssetsUsd']/1e6,100*m['state']['borrowApy'],100*m['state']['utilization']))
    for p in sorted(v['positions']['items'],key=lambda p:-(p['assetsUsd'] or 0))[:6]: print('   holder',p['user']['address'],'$%.2fM'%((p['assetsUsd'] or 0)/1e6))
json.dump(out,open('raw/morpho_vaults_used.json','w'),indent=0)
