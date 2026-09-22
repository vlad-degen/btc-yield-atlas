# Aave v4 stage 2: batch getUserAccountData for saved (spoke,user) pairs via publicnode; keep debt >= $2M; list BTC collateral + debts
import json, time
from addrinfo import post, dec_str, ecall
RPC='https://ethereum-rpc.publicnode.com'
P=[tuple(x) for x in json.load(open('../raw/aave_v4_pairs.json'))]
acct={}
for i in range(0,len(P),25):
    ch=P[i:i+25]
    r=post(RPC,[{'jsonrpc':'2.0','id':k,'method':'eth_call','params':[{'to':sp,'data':'0xbf92857c'+u[2:].rjust(64,'0')},'latest']} for k,(sp,u) in enumerate(ch)])
    for x in r: acct[ch[x['id']]]=x.get('result')
    time.sleep(0.2)
print('pairs',len(P),'read',sum(1 for v in acct.values() if v),flush=True)
res={}
def reserves(sp):
    if sp in res: return res[sp]
    n=int(ecall(1,sp,'0x99806546'),16); rs=[]
    for i in range(n):
        r=ecall(1,sp,'0x77778db3'+hex(i)[2:].rjust(64,'0'))
        und='0x'+r[26:66]; dec=int(r[2+64*3:2+64*4],16); rs.append((i,und,dec_str(ecall(1,und,'0x95d89b41')),dec))
    res[sp]=rs; return rs
out=[]
for (sp,u),x in acct.items():
    if not x: continue
    h=x[2:]; w=[int(h[i:i+64],16) for i in range(0,len(h),64)]
    coll=w[3]/1e26; debt=w[4]/1e53
    if debt<2e6: continue
    btc={}; debts={}
    for i,und,sym,dec in reserves(sp):
        a=ecall(1,sp,'0xf1568a89'+hex(i)[2:].rjust(64,'0')+u[2:].rjust(64,'0'))
        if sym and 'BTC' in sym.upper() and a and int(a,16)>0: btc[sym]=int(a,16)/10**dec
        d=ecall(1,sp,'0x9b7172a6'+hex(i)[2:].rjust(64,'0')+u[2:].rjust(64,'0'))
        if d and int(d,16)>0: debts[sym]=int(d,16)/10**dec
    row=dict(spoke=sp,user=u,coll_usd=coll,debt_usd=debt,btc_coll=btc,debts=debts); out.append(row)
    print(sp[:10],u,'coll $%.2fM debt $%.2fM'%(coll/1e6,debt/1e6),btc,{k:round(v) for k,v in debts.items()},flush=True)
json.dump(out,open('../raw/aave_v4_btc_borrowers.json','w'),indent=1)
print('debt>=2M:',len(out),'with BTC collateral:',sum(1 for o in out if o['btc_coll']))
