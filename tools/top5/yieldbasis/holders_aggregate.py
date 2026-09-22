# Aggregate per-address BTC-equivalent across all live BTC markets (v3 + deprecated v2 + v1)
import json,collections,csv
d=json.load(open('../raw/holders_btc.json'))
BUCKETS=[(0,0.01,'<0.01'),(0.01,0.1,'0.01-0.1'),(0.1,1,'0.1-1'),(1,10,'1-10'),(10,100,'10-100'),(100,1e9,'>100')]
def agg(mks,label):
    tot=collections.defaultdict(float); st=collections.defaultdict(float); ty={}
    for mk in mks:
        for a,p in d['positions'][mk].items(): tot[a]+=p['btc']; st[a]+=p['st']; ty[a]=p['type']
    T=sum(tot.values()); srt=sorted(tot.items(),key=lambda x:-x[1])
    hhi=sum((v/T*100)**2 for _,v in srt)
    b=collections.OrderedDict((lab,[0,0.0]) for _,_,lab in BUCKETS)
    for _,v in srt:
        for lo,hi,lab in BUCKETS:
            if lo<=v<hi: b[lab][0]+=1; b[lab][1]+=v
    s=dict(label=label,holders=len(srt),total_btc=T,staked_share=sum(st.values())/T,top1=srt[0][1]/T,top10=sum(v for _,v in srt[:10])/T,top100=sum(v for _,v in srt[:100])/T,hhi=hhi,buckets=b,top15=[(a,round(v,3),ty[a],round(st[a]/v,2)) for a,v in srt[:15]])
    return s
out=[agg(['v3-WBTC','v3-cbBTC','v3-tBTC'],'v3 BTC markets combined'),agg(['v3-WBTC','v3-cbBTC','v3-tBTC','v2-WBTC','v2-cbBTC','v2-tBTC','v1-WBTC','v1-cbBTC','v1-tBTC'],'all BTC markets combined (v1+v2+v3)')]
for s in out:
    print(json.dumps({k:v for k,v in s.items() if k!='top15'}))
    for x in s['top15']: print('   ',x)
json.dump(out,open('../raw/holders_aggregate.json','w'),indent=1)
with open('../holders_buckets.csv','a',newline='') as f:
    w=csv.writer(f)
    for s in out:
        for lab,(n,v) in s['buckets'].items(): w.writerow([s['label'],lab,n,round(v,4),round(v/s['total_btc']*100,2)])
