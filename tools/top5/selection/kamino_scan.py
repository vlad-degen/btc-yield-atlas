# Kamino (Solana) main market: obligations with BTC-wrapper deposits; parse owner, deposits/borrows market values (Sf = value * 2^60); keep borrowed >= $2M
import json, base64, urllib.request, time
RPC='https://api.mainnet-beta.solana.com'; PROG='KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD'; MKT='7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'
A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58(b):
    n=int.from_bytes(b,'big'); s=''
    while n: n,r=divmod(n,58); s=A[r]+s
    return '1'*(len(b)-len(b.lstrip(b'\0')))+s
def post(p):
    for i in range(6):
        try:
            req=urllib.request.Request(RPC,data=json.dumps(p).encode(),headers={'content-type':'application/json'})
            return json.load(urllib.request.urlopen(req,timeout=120))
        except Exception as e: time.sleep(5*(i+1)); last=e
    raise last
res=json.load(open('../raw/kamino_main_reserves.json'))
sym={r['reserve']:r['liquidityToken'] for r in res}
btc=[r['reserve'] for r in res if 'BTC' in r['liquidityToken'].upper() and float(r['totalSupplyUsd'])>1e6]
SF=2**60; seen={}; out=[]
for rv in btc:
    for slot in range(8):
        off=96+136*slot
        r=post({'jsonrpc':'2.0','id':1,'method':'getProgramAccounts','params':[PROG,{'encoding':'base64','filters':[{'dataSize':3344},{'memcmp':{'offset':32,'bytes':MKT}},{'memcmp':{'offset':off,'bytes':rv}}]}]})
        accs=r.get('result') or []
        for a in accs:
            if a['pubkey'] in seen: continue
            d=base64.b64decode(a['account']['data'][0]); owner=b58(d[64:96])
            deps=[]
            for i in range(8):
                o=96+136*i; res_=b58(d[o:o+32]); amt=int.from_bytes(d[o+32:o+40],'little'); mv=int.from_bytes(d[o+40:o+56],'little')/SF
                if amt: deps.append((sym.get(res_,res_[:6]),mv))
            bors=[]
            for i in range(5):
                o=1208+200*i; res_=b58(d[o:o+32]); mv=int.from_bytes(d[o+32+48+8+16:o+32+48+8+32],'little')/SF
                if mv>0: bors.append((sym.get(res_,res_[:6]),mv))
            seen[a['pubkey']]=1
            tb=sum(v for _,v in bors); tbtc=sum(v for s,v in deps if 'BTC' in s.upper())
            if tb>=2e6: out.append(dict(obligation=a['pubkey'],owner=owner,btc_coll_usd=tbtc,deposits=deps,borrows=bors,borrow_usd=tb))
        print(sym[rv],'slot',slot,'obligations',len(accs),flush=True)
        time.sleep(1)
json.dump(out,open('../raw/kamino_btc_borrowers.json','w'),indent=1)
print('obligations with BTC deposits:',len(seen))
for o in sorted(out,key=lambda o:-o['borrow_usd']): print(o['owner'],'BTC coll $%.2fM'%(o['btc_coll_usd']/1e6),'borrow $%.2fM'%(o['borrow_usd']/1e6),[(s,round(v/1e6,2)) for s,v in o['deposits']],[(s,round(v/1e6,2)) for s,v in o['borrows']])
