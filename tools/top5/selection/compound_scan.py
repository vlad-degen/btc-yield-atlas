# Compound v3: enumerate accounts that supplied BTC collateral (SupplyCollateral logs), read current collateral + borrow, keep debt >= $2M
import json
from addrinfo import post, ecall
from concurrent.futures import ThreadPoolExecutor
LOGRPC={1:'https://gateway.tenderly.co/public/mainnet',8453:'https://gateway.tenderly.co/public/base',42161:'https://gateway.tenderly.co/public/arbitrum'}
T0='0xfa56f7b24f17183d81894d3ac2ee654e3c26388d17a28dbd9549b8114304e1f4'
COMETS=[(1,'cUSDCv3','0xc3d688B66703497DAA19211EEdff47f25384cdc3',15331586),(1,'cUSDTv3','0x3Afdc9BCA9213A35503b077a6072F3D0d5AB0840',20190000),
        (8453,'cUSDCv3','0xb125E6687d4313864e53df431d5425969c15Eb2F',2197000),(42161,'cUSDCv3','0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf',87335000),(42161,'cUSDTv3','0xd98Be00b5D27fc98112BdE293e487f8D4cA57d07',210000000)]
BTC={1:{'WBTC':('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',8),'cbBTC':('0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',8),'tBTC':('0x18084fbA666a33d37592fA2633fD49a74DD93a88',18)},
     8453:{'cbBTC':('0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',8)},42161:{'WBTC':('0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',8)}}
def rpc(ch,m,p):
    r=post(LOGRPC[ch],{'jsonrpc':'2.0','id':1,'method':m,'params':p})
    if 'error' in r: raise Exception(r['error'])
    return r['result']
out=[]
for ch,name,comet,start in COMETS:
    head=int(rpc(ch,'eth_blockNumber',[]),16)
    step=2_000_000 if ch==1 else 20_000_000
    for sym,(asset,dec) in BTC[ch].items():
        users=set(); b=start
        while b<=head:
            e=min(head,b+step-1)
            try:
                logs=rpc(ch,'eth_getLogs',[{'address':comet,'fromBlock':hex(b),'toBlock':hex(e),'topics':[T0,None,None,'0x'+asset[2:].lower().rjust(64,'0')]}])
            except Exception as ex:
                step//=2; print('shrink',ch,step,str(ex)[:80]); continue
            for l in logs: users.add('0x'+l['topics'][2][-40:])
            b=e+1
        def w(a):
            c=ecall(ch,comet,'0x5c2549ee'+a[2:].rjust(64,'0')+asset[2:].lower().rjust(64,'0'))
            d=ecall(ch,comet,'0x374c49b4'+a[2:].rjust(64,'0'))
            return a,(int(c[2:66],16) if c else 0)/10**dec,(int(d,16) if d else 0)/1e6
        with ThreadPoolExecutor(8) as ex: res=list(ex.map(w,sorted(users)))
        big=[r for r in res if r[2]>=2e6]
        print(ch,name,sym,'accounts',len(users),'with BTC now',sum(1 for r in res if r[1]>0),'BTC now',round(sum(r[1] for r in res),2),'debt>=2M:',len(big),flush=True)
        for a,c,d in sorted(big,key=lambda r:-r[2]):
            print('   ',a,'BTC coll',round(c,2),'debt $%.2fM'%(d/1e6)); out.append(dict(chain=ch,comet=name,asset=sym,user=a,btc=c,debt_usd=d))
json.dump(out,open('../raw/compound_btc_borrowers.json','w'),indent=1)
