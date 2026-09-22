# Daily (00:00 UTC) Aave v3 Core / Prime / Horizon and Spark account data + per-asset balances of the strategy wallet (Ethereum archive)
import json,urllib.request,sys
URLS=['https://rpc.mevblocker.io','https://gateway.tenderly.co/public/mainnet','https://eth.drpc.org']
W='933adedd85824da75ec8a334a7907e69e7c02833'.rjust(64,'0')
def batch(calls):
    body=json.dumps([{'jsonrpc':'2.0','id':i,'method':'eth_call','params':[{'to':t,'data':d},hex(b)]} for i,(t,d,b) in enumerate(calls)]).encode()
    for u in URLS:
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(u,data=body,headers={'content-type':'application/json','user-agent':'Mozilla/5.0'}),timeout=120))
            r=sorted(r,key=lambda x:x['id']); return [x.get('result') for x in r]
        except Exception as e: print('batch fail',u,e,file=sys.stderr)
    raise Exception('all rpc failed')
POOLS={'aave_core':'0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2','aave_prime':'0x4e033931ad43597d96D6bcc25c280717730B58B1','aave_horizon':'0xAe05Cd22df81871bc7cC2a04BeCfb516bFe332C8','spark':'0xC13e21B648A5Ee794902342038FF3aDAB66BE987'}
TOK={ # name: (address, decimals)
 'core_aWBTC':('0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8',8),'core_acbBTC':('0x5c647cE0Ae10658ec44FA4E11A51c96e94efd1Dd',8),'core_aLBTC':('0x65906988ADEe75306021C417a1A3458040239602',8),
 'core_vdUSDC':('0x72E95b8931767C79bA4EeE721354d6E99a61D004',6),'core_vdUSDT':('0x6df1C1E379bC5a00a7b4C6e67A203333772f45A8',6),'core_vdRLUSD':('0xBdFe7aD7976d5d7E0965ea83a81Ca1bCfF7e84a9',18),
 'core_vdUSDe':('0x015396E1F286289aE23a762088E863b3ec465145',18),'core_vdUSDG':('0x4f97B950a30321c181E974971E156E19fAD184A3',6),'core_vdcbBTC':('0xeB284A70557EFe3591b9e6D9D720040E02c54a4d',8),
 'spark_acbBTC':('0xb3973D459df38ae57797811F2A1fd061DA1BC123',8),'spark_aWBTC':('0x4197ba364AE6698015AE5c1468f54087602715b2',8),
 'spark_vdUSDS':('0x8c147debea24Fb98ade8dDa4bf142992928b449e',18),'spark_vdUSDT':('0x529b6158d1D2992E3129F7C69E81a7c677dc3B12',6),
 'w_WBTC':('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',8),'w_cbBTC':('0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',8),'w_LBTC':('0x8236a87084f8B84306f72007F36F2618A5634494',8),
 'w_USDC':('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',6),'w_USDT':('0xdAC17F958D2ee523a2206206994597C13D831ec7',6),'w_USDS':('0xdC035D45d973E3EC169d2276DDab16f1e407384F',18),
}
if __name__=="__main__":
 blocks=json.load(open('raw/eth_daily_blocks.json'))
 out={}
 items=list(blocks.items())
 for i in range(0,len(items),4):
     chunk=items[i:i+4]; calls=[]
     for day,b in chunk:
         for p,a in POOLS.items(): calls.append((a,'0xbf92857c'+W,b))
         for n,(a,dc) in TOK.items(): calls.append((a,'0x70a08231'+W,b))
     res=batch(calls); k=0
     for day,b in chunk:
         r={'block':b}
         for p in POOLS:
             h=res[k]; k+=1
             if h and len(h)>=2+64*6:
                 w=[int(h[2+64*j:2+64*(j+1)],16) for j in range(6)]
                 r[p]={'coll_usd':w[0]/1e8,'debt_usd':w[1]/1e8,'hf':w[5]/1e18 if w[1] else None}
         for n,(a,dc) in TOK.items():
             h=res[k]; k+=1
             r[n]=int(h,16)/10**dc if h and h!='0x' else None
         out[day]=r
 json.dump(out,open('raw/aave_spark_daily.json','w'),indent=0)
 for day in list(out)[::15]+['2026-09-20T12']:
     r=out[day]; print(day,{p:(round(r[p]['coll_usd']/1e6,2),round(r[p]['debt_usd']/1e6,2)) for p in POOLS if p in r and r[p]['coll_usd']>1000},{k:round(v,3) for k,v in r.items() if k not in POOLS and k!='block' and v and v>0.001})
