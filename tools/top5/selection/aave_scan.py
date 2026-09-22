# Aave v3 (Ethereum core/prime/etherfi, Base, Arbitrum) + Spark: top holders of BTC aTokens -> debt via getUserAccountData -> stable debt breakdown
import json, sys, urllib.parse
from addrinfo import RPC, BS, post, ecall, getjson, dec_str
from concurrent.futures import ThreadPoolExecutor
POOLS=[('aave-eth-core',1,'0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'),
       ('aave-eth-prime',1,'0x4e033931ad43597d96D6bcc25c280717730B58B1'),
       ('aave-eth-etherfi',1,'0x0AA97c284e98396202b6A04024F5E2c65026F3c0'),
       ('spark-eth',1,'0xC13e21B648A5Ee794902342038FF3aDAB66BE987'),
       ('aave-base',8453,'0xA238Dd80C259a72e81d7e4664a9801593F98d1c5'),
       ('aave-arb',42161,'0x794a61358D6845594F94dc1DB02A252b5b4814aD')]
STABLE=('USD','DAI','GHO','FRAX','LUSD','RLUSD','PYUSD','EUR')
def bcall(chain,calls):
    out=[]
    for i in range(0,len(calls),40):
        chunk=calls[i:i+40]
        payload=[{'jsonrpc':'2.0','id':k,'method':'eth_call','params':[{'to':to,'data':data},'latest']} for k,(to,data) in enumerate(chunk)]
        r=post(RPC[chain],payload)
        r=sorted(r,key=lambda x:x['id']); out+=[x.get('result') for x in r]
    return out
def words(h): h=h[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
res={}
for name,ch,pool in POOLS:
    lst=ecall(ch,pool,'0xd1946dbc')  # getReservesList()
    if not lst: print(name,'no reserves'); continue
    w=lst[2:]; n=int(w[64:128],16); assets=['0x'+w[128+64*i+24:128+64*(i+1)] for i in range(n)]
    syms=[dec_str(x) for x in bcall(ch,[(a,'0x95d89b41') for a in assets])]
    rd=bcall(ch,[(pool,'0x35ea6a75'+a[2:].rjust(64,'0')) for a in assets])
    dec=[int(x,16) if x else 18 for x in bcall(ch,[(a,'0x313ce567') for a in assets])]
    reserves=[]
    for a,s,r,d in zip(assets,syms,rd,dec):
        ww=r[2:]; aT='0x'+ww[64*8+24:64*9]; vD='0x'+ww[64*10+24:64*11]
        reserves.append(dict(asset=a,sym=s,aToken=aT,vDebt=vD,dec=d))
    btcres=[r for r in reserves if r['sym'] and 'BTC' in r['sym'].upper()]
    print('==',name,'reserves',len(reserves),'BTC:',[(r['sym'],r['aToken']) for r in btcres],flush=True)
    holders={}
    for r in btcres:
        if ch not in BS: continue
        url=BS[ch]+'/api/v2/tokens/%s/holders'%r['aToken']; items=[]; nxt=None
        for page in range(2):  # top 100
            j=getjson(url+('?'+urllib.parse.urlencode(nxt) if nxt else ''))
            items+=j.get('items',[]); nxt=j.get('next_page_params')
            if not nxt: break
        for it in items:
            bal=int(it['value'])/10**r['dec']
            if bal>=10: holders.setdefault(it['address']['hash'],{})[r['sym']]=bal
    addrs=list(holders); print('  holders>=10 BTC:',len(addrs),flush=True)
    acct=bcall(ch,[(pool,'0xbf92857c'+a[2:].lower().rjust(64,'0')) for a in addrs])  # getUserAccountData
    cands=[]
    for a,x in zip(addrs,acct):
        if not x: continue
        v=words(x); coll=v[0]/1e8; debt=v[1]/1e8
        if debt>=2e6: cands.append((a,coll,debt,v[5]/1e18))
    for a,coll,debt,hf in sorted(cands,key=lambda c:-c[2]):
        bals=bcall(ch,[(r['vDebt'],'0x70a08231'+a[2:].lower().rjust(64,'0')) for r in reserves])
        debts={r['sym']:int(b,16)/10**r['dec'] for r,b in zip(reserves,bals) if b and int(b,16)>0}
        colls=None
        stable=sum(v for k,v in debts.items() if any(s in k.upper() for s in STABLE))
        res.setdefault(name,[]).append(dict(chain=ch,pool=pool,user=a,coll_usd=coll,debt_usd=debt,hf=hf,debts=debts,colls=colls,stable_debt=stable,btc_coll=holders[a]))
        json.dump(res,open('../raw/aave_spark_btc_borrowers.json','w'),indent=1)
        print(f"  {a} coll ${coll/1e6:.1f}M debt ${debt/1e6:.1f}M stable~{stable/1e6:.1f}M HF {hf:.2f} btc {holders[a]} debts { {k:round(v,1) for k,v in debts.items()} }",flush=True)

