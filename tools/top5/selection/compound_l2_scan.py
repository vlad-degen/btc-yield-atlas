# Compound v3 on Base/Arbitrum: SupplyCollateral logs via Blockscout (paged by block), current collateral/borrow via RPC
import json
from addrinfo import getjson, ecall
T0='0xfa56f7b24f17183d81894d3ac2ee654e3c26388d17a28dbd9549b8114304e1f4'
JOBS=[(8453,'https://base.blockscout.com','cUSDCv3','0xb125E6687d4313864e53df431d5425969c15Eb2F','cbBTC','0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',8),
      (42161,'https://arbitrum.blockscout.com','cUSDCv3','0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf','WBTC','0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',8),
      (42161,'https://arbitrum.blockscout.com','cUSDTv3','0xd98Be00b5D27fc98112BdE293e487f8D4cA57d07','WBTC','0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',8)]
out=[]
for ch,bs,name,comet,sym,asset,dec in JOBS:
    users=set(); fb=0
    while True:
        j=getjson(bs+'/api?module=logs&action=getLogs&fromBlock=%d&toBlock=latest&address=%s&topic0=%s&topic3=0x%s&topic0_3_opr=and'%(fb,comet,T0,asset[2:].lower().rjust(64,'0')))
        r=j.get('result') or []
        for l in r: users.add('0x'+l['topics'][2][-40:])
        if len(r)<1000: break
        fb=int(r[-1]['blockNumber'],16)  # may re-read some logs; set dedups
    res=[]
    for a in users:
        c=ecall(ch,comet,'0x5c2549ee'+a[2:].rjust(64,'0')+asset[2:].lower().rjust(64,'0')); d=ecall(ch,comet,'0x374c49b4'+a[2:].rjust(64,'0'))
        res.append((a,(int(c[2:66],16) if c else 0)/10**dec,(int(d,16) if d else 0)/1e6))
    big=[x for x in res if x[2]>=2e6]
    print(ch,name,sym,'accounts',len(users),'BTC now',round(sum(x[1] for x in res),2),'debt>=2M',[(a,round(c,2),round(d/1e6,2)) for a,c,d in big],flush=True)
    out+= [dict(chain=ch,comet=name,asset=sym,user=a,btc=c,debt_usd=d) for a,c,d in big]
json.dump(out,open('../raw/compound_l2_btc_borrowers.json','w'),indent=1)
