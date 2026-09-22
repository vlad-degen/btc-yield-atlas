# Supplement: aEthWBTC / aEthcbBTC / spcbBTC / aBascbBTC holders ranks 101-400 (pages 3-8) -> getUserAccountData -> debt >= $2M
import json, urllib.parse
from addrinfo import getjson, post, RPC, BS
import addrinfo
TOK=[(1,'aave-eth-core','0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2','0x5ee5bf7ae06d1be5997a1a72006fe6c607ec6de8','WBTC'),
     (1,'aave-eth-core','0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2','0x5c647ce0ae10658ec44fa4e11a51c96e94efd1dd','cbBTC'),
     (1,'spark-eth','0xC13e21B648A5Ee794902342038FF3aDAB66BE987','0xb3973d459df38ae57797811f2a1fd061da1bc123','cbBTC'),
     (8453,'aave-base','0xA238Dd80C259a72e81d7e4664a9801593F98d1c5','0xbdb9300b7cde636d9cd4aff00f6f009ffbbc8ee6','cbBTC')]
out=[]
for ch,name,pool,at,sym in TOK:
    url=BS[ch]+'/api/v2/tokens/%s/holders'%at; nxt=None; items=[]
    for page in range(8):
        j=getjson(url+('?'+urllib.parse.urlencode(nxt) if nxt else ''))
        if page>=2: items+=j.get('items',[])
        nxt=j.get('next_page_params')
        if not nxt: break
    hs=[(it['address']['hash'],int(it['value'])/1e8) for it in items]
    calls=[{'jsonrpc':'2.0','id':i,'method':'eth_call','params':[{'to':pool,'data':'0xbf92857c'+a[2:].lower().rjust(64,'0')},'latest']} for i,(a,b) in enumerate(hs)]
    res=[]
    for i in range(0,len(calls),40):
        r=post(RPC[ch],calls[i:i+40]); res+=sorted(r,key=lambda x:x['id'])
    big=[]
    for (a,b),r in zip(hs,res):
        x=r.get('result')
        if not x: continue
        h=x[2:]; coll=int(h[0:64],16)/1e8; debt=int(h[64:128],16)/1e8
        if debt>=2e6: big.append(dict(chain=ch,market=name,user=a,btc=b,sym=sym,coll_usd=coll,debt_usd=debt))
    print(name,sym,'holders rank 101-%d:'%(100+len(hs)),'min bal',round(min([b for a,b in hs] or [0]),2),'debt>=2M:',len(big),flush=True)
    for b in big: print('   ',b['user'],round(b['btc'],2),sym,'debt $%.2fM'%(b['debt_usd']/1e6))
    out+=big
json.dump(out,open('../raw/aave_deep_pages.json','w'),indent=1)
