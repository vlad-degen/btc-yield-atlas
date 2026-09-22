# Daily variable borrow rates of Aave Core / Spark reserves used by the strategy (getReserveData at daily blocks, days with debt only)
import json,sys; sys.path.insert(0,'scripts')
from aave_daily import batch
D=json.load(open('raw/aave_spark_daily.json'))
RES={'core':('0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',{'USDC':'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48','USDT':'0xdAC17F958D2ee523a2206206994597C13D831ec7','RLUSD':'0x8292Bb45bf1Ee4d140127049757C2E0fF06317eD','USDe':'0x4c9EDD5852cd905f086C759E8383e09bff1E68B3','USDG':'0xe343167631d89B6Ffc58B88d6b7fB0228795491D','cbBTC':'0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf'}),
     'spark':('0xC13e21B648A5Ee794902342038FF3aDAB66BE987',{'USDS':'0xdC035D45d973E3EC169d2276DDab16f1e407384F','USDT':'0xdAC17F958D2ee523a2206206994597C13D831ec7'})}
days=[d for d,r in D.items() if any((r.get(p) or {}).get('debt_usd',0)>1000 for p in ('aave_core','spark'))]
out={}
for i in range(0,len(days),5):
    ch=days[i:i+5]; calls=[]
    for d in ch:
        for p,(pool,assets) in RES.items():
            for s,a in assets.items(): calls.append((pool,'0x35ea6a75'+a[2:].lower().rjust(64,'0'),D[d]['block']))
    res=batch(calls); k=0
    for d in ch:
        out[d]={}
        for p,(pool,assets) in RES.items():
            for s,a in assets.items():
                h=res[k]; k+=1
                out[d][f'{p}_{s}']=int(h[2+64*4:2+64*5],16)/1e27 if h and len(h)>2+64*5 else None
json.dump(out,open('raw/aave_rates_daily.json','w'),indent=0)
for d in days[::7]: print(d,{k:round(v*100,2) for k,v in out[d].items() if v})
