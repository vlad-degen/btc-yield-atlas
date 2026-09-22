# Euler v2 (EVK) Ethereum/Base/Arbitrum: BTC-asset vaults -> top share holders -> EVC controllers -> debtOf -> keep debt >= $2M in stablecoins
import json, sys, urllib.parse
from addrinfo import post, RPC, BS, getjson, dec_str
from concurrent.futures import ThreadPoolExecutor
ADDR={1:('0x29a56a1b8214D9Cf7c5561811750D5cBDb45CC8e','0x0C9a3dd6b8F28529d72d7f9cE918D493519EE383')}
for ch,net in [(8453,'8453'),(42161,'42161')]:
    try:
        j=getjson('https://raw.githubusercontent.com/euler-xyz/euler-interfaces/master/addresses/%s/CoreAddresses.json'%net)
        ADDR[ch]=(j['eVaultFactory'],j['evc'])
    except Exception as e: print('no addrs',ch,e)
def bcall(ch,calls):
    out=[]
    for i in range(0,len(calls),50):
        chunk=calls[i:i+50]
        r=post(RPC[ch],[{'jsonrpc':'2.0','id':k,'method':'eth_call','params':[{'to':t,'data':d},'latest']} for k,(t,d) in enumerate(chunk)])
        r=sorted(r,key=lambda x:x['id']); out+=[x.get('result') for x in r]
    return out
def U(h): return int(h[2:66],16) if h and len(h)>=66 else 0
def A(h): return '0x'+h[26:66] if h and len(h)>=66 else None
STAB=('USD','DAI','GHO','EUR','FRAX')
res=[]
for ch,(fac,evc) in ADDR.items():
    n=U(bcall(ch,[(fac,'0x0a68b7ba')])[0])  # getProxyListLength()
    vaults=[]
    for s in range(0,n,500):
        r=bcall(ch,[(fac,'0xc0e96df6'+hex(s)[2:].rjust(64,'0')+hex(min(n,s+500))[2:].rjust(64,'0'))])[0]  # getProxyListSlice(uint256,uint256)
        h=r[2:]; m=int(h[64:128],16); vaults+=['0x'+h[128+64*i+24:128+64*(i+1)] for i in range(m)]
    assets=bcall(ch,[(v,'0x38d52e0f') for v in vaults])  # asset()
    assets=[A(a) for a in assets]
    ua=list({a for a in assets if a})
    syms=dict(zip(ua,[dec_str(x) for x in bcall(ch,[(a,'0x95d89b41') for a in ua])]))
    decs=dict(zip(ua,[U(x) for x in bcall(ch,[(a,'0x313ce567') for a in ua])]))
    ta=bcall(ch,[(v,'0x01e1d114') for v in vaults])  # totalAssets()
    info={v:(a,syms.get(a),decs.get(a),U(t)) for v,a,t in zip(vaults,assets,ta)}
    btcv=[v for v,(a,s,d,t) in info.items() if s and 'BTC' in s.upper() and d and t/10**d>=20]
    print('chain',ch,'vaults',n,'BTC vaults >=20 BTC:',[(v,info[v][1],round(info[v][3]/10**info[v][2],1)) for v in btcv],flush=True)
    for v in btcv:
        a,s,d,t=info[v]
        items=[];nxt=None
        for p in range(2):
            j=getjson(BS[ch]+'/api/v2/tokens/%s/holders'%v+('?'+urllib.parse.urlencode(nxt) if nxt else ''))
            items+=j.get('items',[]); nxt=j.get('next_page_params')
            if not nxt: break
        holders=[it['address']['hash'] for it in items]
        # EVC.getControllers(address) 0xfd6046d7
        ctr=bcall(ch,[(evc,'0xfd6046d7'+h[2:].lower().rjust(64,'0')) for h in holders])
        for h,c in zip(holders,ctr):
            if not c or len(c)<194: continue
            k=int(c[66:130],16)
            for i in range(k):
                cv='0x'+c[130+64*i+24:130+64*(i+1)]
                da=bcall(ch,[(cv,'0xd283e75f'+h[2:].lower().rjust(64,'0')),(cv,'0x38d52e0f')])  # debtOf(address), asset()
                dasset=A(da[1]); dsym=dec_str(bcall(ch,[(dasset,'0x95d89b41')])[0]); ddec=U(bcall(ch,[(dasset,'0x313ce567')])[0])
                debt=U(da[0])/10**ddec
                bal=U(bcall(ch,[(v,'0x70a08231'+h[2:].lower().rjust(64,'0')),])[0])
                if debt>=2e6 and dsym and any(x in dsym.upper() for x in STAB):
                    row=dict(chain=ch,collateral_vault=v,coll_sym=s,account=h,controller=cv,debt_sym=dsym,debt=debt,coll_shares=bal/10**d)
                    res.append(row); print('  ',row,flush=True)
json.dump(res,open('../raw/euler_btc_borrowers.json','w'),indent=1)
print('done',len(res))
