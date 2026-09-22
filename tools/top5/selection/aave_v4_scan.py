# Aave v4 (Ethereum): enumerate Spoke Borrow events (all spokes), per (spoke,user) getUserAccountData; for debt>=$2M, list BTC collateral reserves
import json
from addrinfo import post, dec_str
RPC='https://gateway.tenderly.co/public/mainnet'
T0='0xef18174796a5d2f91d51dc5e907a4d7867bbd6e800f6225168e0453d581d0dcd'
def rpc(m,p):
    r=post(RPC,{'jsonrpc':'2.0','id':1,'method':m,'params':p})
    if 'error' in r: raise Exception(r['error'])
    return r['result']
def call(to,data):
    try: return rpc('eth_call',[{'to':to,'data':data},'latest'])
    except Exception as e: return None
head=int(rpc('eth_blockNumber',[]),16)
pairs=set(); b=head-2_600_000; step=250_000   # ~ last 12 months
while b<head:
    e=min(head,b+step)
    try: logs=rpc('eth_getLogs',[{'fromBlock':hex(b),'toBlock':hex(e),'topics':[T0]}])
    except Exception as ex:
        step//=2; print('shrink',step,str(ex)[:60],flush=True); continue
    for l in logs:
        if len(l['topics'])==4: pairs.add((l['address'].lower(),'0x'+l['topics'][3][-40:]))
    b=e+1
spokes=sorted({s for s,_ in pairs}); print('spokes',spokes,'pairs',len(pairs),flush=True)
json.dump(sorted(pairs),open('../raw/aave_v4_pairs.json','w'))
res={}
for sp in spokes:
    n=call(sp,'0x99806546'); n=int(n,16) if n else 0
    rs=[]
    for i in range(n):
        r=call(sp,'0x77778db3'+hex(i)[2:].rjust(64,'0'))
        if not r: continue
        und='0x'+r[26:66]; dec=int(r[2+64*3:2+64*4],16); sym=dec_str(call(und,'0x95d89b41'))
        rs.append((i,und,sym,dec))
    res[sp]=rs
    print('spoke',sp,'reserves',[(i,s) for i,_,s,_ in rs],flush=True)
out=[]
P=sorted(pairs); acct={}
for i in range(0,len(P),40):
    ch=P[i:i+40]
    r=post(RPC,[{'jsonrpc':'2.0','id':k,'method':'eth_call','params':[{'to':sp,'data':'0xbf92857c'+u[2:].rjust(64,'0')},'latest']} for k,(sp,u) in enumerate(ch)])
    for x in r: acct[ch[x['id']]]=x.get('result')
print('account data read',len(acct),flush=True)
for sp,u in P:
    x=acct.get((sp,u))
    if not x: continue
    h=x[2:]; w=[int(h[i:i+64],16) for i in range(0,len(h),64)]
    coll=w[3]; debt=w[4]
    # value units: try 1e26 for ray-debt in base 1e8? print raw and scaled guesses
    debt_usd=debt/1e53   # totalDebtValueRay: USD * 1e26 (value units) * 1e27 (ray)
    coll_usd=coll/1e26   # totalCollateralValue: USD * 1e26 (checked vs per-reserve debts)
    if debt_usd>=2e6:
        btc={}
        for i,und,sym,dec in res[sp]:
            if sym and 'BTC' in sym.upper():
                a=call(sp,'0xf1568a89'+hex(i)[2:].rjust(64,'0')+u[2:].rjust(64,'0'))
                if a and int(a,16)>0: btc[sym]=int(a,16)/10**dec
        debts={}
        for i,und,sym,dec in res[sp]:
            d=call(sp,'0x9b7172a6'+hex(i)[2:].rjust(64,'0')+u[2:].rjust(64,'0'))
            if d and int(d,16)>0: debts[sym]=int(d,16)/10**dec
        row=dict(spoke=sp,user=u,coll_usd=coll_usd,debt_usd=debt_usd,btc_coll=btc,debts=debts,raw=[w[3],w[4]])
        out.append(row); print(row,flush=True)
json.dump(out,open('../raw/aave_v4_btc_borrowers.json','w'),indent=1)
print('done',len(out))
