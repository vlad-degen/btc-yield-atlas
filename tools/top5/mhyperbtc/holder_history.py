# Month-end holdings of mHyperBTC by holder type (Ethereum + Monad logs): Morpho collateral, Pendle SY, EOAs; top-holder concentration
import json,datetime,collections
z='0x'+'0'*40
def month_ends():
    out=[]
    for y,m in [(2025,11),(2025,12),(2026,1),(2026,2),(2026,3),(2026,4),(2026,5),(2026,6),(2026,7),(2026,8)]:
        nx=datetime.datetime(y+(m==12),(m%12)+1,1,tzinfo=datetime.timezone.utc); out.append((f'{y}-{m:02d}',int(nx.timestamp())))
    out.append(('2026-09',int(datetime.datetime(2026,9,21,23,tzinfo=datetime.timezone.utc).timestamp())))
    return out
LAB={'0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb':'Morpho Blue (ETH)','0x95fc228a926828b4d95f52c1d52b345e743153f0':'Pendle SY (ETH)','0xd5d960e8c380b724a48ac59e2dff1b2cb4a1eaee':'Morpho Blue (Monad)',
     '0x16d4f955b0aa1b1570fe3e9bb2f8c19c407cdb67':'Midas redemption vault','0xb67f81069e890a1b3e02c7bed3a9f78ba54a445c':'OFT adapter'}
def series(fn):
    L=json.load(open(fn))['logs']; ev=[]
    for l in L:
        ev.append((int(l['blockTimestamp'],16),'0x'+l['topics'][1][-40:],'0x'+l['topics'][2][-40:],int(l['data'],16)/1e18))
    ev.sort(); return ev
res={}
for chain,fn in [('ethereum','raw/eth_mhyperbtc_transfers.json'),('monad','raw/monad_mhyperbtc_transfers.json')]:
    ev=series(fn); bal=collections.Counter(); i=0
    for m,T in month_ends():
        while i<len(ev) and ev[i][0]<T:
            _,f,t,v=ev[i]; bal[f]-=v; bal[t]+=v; i+=1
        hold={a:v for a,v in bal.items() if a!=z and v>1e-9}
        res.setdefault(m,{})[chain]=hold
out={}
for m,_ in month_ends():
    agg=collections.Counter(); per=collections.Counter()
    for chain,h in res[m].items():
        for a,v in h.items():
            per[a]+=v
            agg[LAB.get(a,'other')]+=v
    tot=sum(per.values())
    top=sorted(per.items(),key=lambda kv:-kv[1])
    out[m]={'total_eth_monad':tot,'by_type':dict(agg),'top1':top[0][1]/tot if tot else 0,'top5':sum(v for _,v in top[:5])/tot if tot else 0,'n_holders':sum(1 for v in per.values() if v>1e-6),'top':[(a,round(v,2)) for a,v in top[:5]]}
    print(m,'total %.1f'%tot,'holders',out[m]['n_holders'],{k:round(v,1) for k,v in agg.items()},'top1 %.0f%% top5 %.0f%%'%(100*out[m]['top1'],100*out[m]['top5']),out[m]['top'][:3])
json.dump(out,open('raw/holder_history.json','w'),indent=0)
