# Transitive cluster (Core delegator <-> BTC key) from a seed; then active-BTC time series for the cluster
import json,sys,collections,datetime
logs=json.load(open(sys.argv[1]))['logs']
seed=sys.argv[2].lower()
exp={l['topics'][1]:int(l['blockNumber'],16) for l in logs['btcExpired']}
B0,T0=18000000,1727301502
def bd(b): return datetime.datetime.fromtimestamp(T0+(b-B0)*3,datetime.timezone.utc).strftime('%Y-%m-%d')
def blk(date): return int(B0+(datetime.datetime.strptime(date,'%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp()-T0)/3)
recs=[]
for l in logs['delegated']:
    data=l['data'][2:]; w=[data[i:i+64] for i in range(0,len(data),64)]
    off=int(w[0],16)//32; ln=int(w[off],16); b=bytes.fromhex(''.join(w[off+1:])[:ln*2])
    i=0; ks=[]; lt=None; first=True
    while i<len(b):
        op=b[i]; i+=1
        if 1<=op<=75:
            d=b[i:i+op]; i+=op
            if first: lt=int.from_bytes(d,'little')
            elif len(d) in (20,33,65): ks.append(d.hex())
        first=False
    recs.append(dict(txid=l['topics'][1],dele='0x'+l['topics'][3][-40:],cand='0x'+l['topics'][2][-40:],amt=int(w[2],16)/1e8,block=int(l['blockNumber'],16),lock=lt,key=tuple(sorted(ks))))
D={seed}; K=set(); changed=True
while changed:
    changed=False
    for r in recs:
        if r['dele'] in D and r['key'] not in K: K.add(r['key']); changed=True
        if r['key'] in K and r['dele'] not in D: D.add(r['dele']); changed=True
C=[r for r in recs if r['dele'] in D or r['key'] in K]
print('cluster delegators:',sorted(D)); print('cluster keys:',[k[0][:12]+('..multisig' if len(k)>1 else '') for k in K])
print('n tx',len(C),'first',bd(min(r['block'] for r in C)),'last',bd(max(r['block'] for r in C)),'max lock',datetime.datetime.fromtimestamp(max(r['lock'] for r in C),datetime.timezone.utc).date())
# active by lock expiry (Bitcoin-side CLTV), which is the economically meaningful end
dates=['2025-02-01','2025-02-15','2025-03-01','2025-03-15','2025-04-01','2025-04-15','2025-05-01','2025-05-15','2025-06-01','2025-06-15','2025-07-01','2025-07-15','2025-08-01','2025-08-15','2025-09-01','2025-09-15','2025-10-01','2025-10-15','2025-11-01','2025-11-15','2025-11-19','2025-11-20','2025-12-01','2026-01-01','2026-06-01','2026-09-20']
print('date        clusterActiveBTC(by CLTV lock)   ndelegs  by-delegator')
for d in dates:
    b=blk(d); ts=datetime.datetime.strptime(d,'%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp()
    act=[r for r in C if r['block']<=b and r['lock']>ts]
    per=collections.Counter()
    for r in act: per[r['dele'][:8]]+=r['amt']
    print(d, f"{sum(r['amt'] for r in act):10.2f}", f"{len(act):5}", dict((k,round(v,1)) for k,v in per.items()))
json.dump(dict(delegators=sorted(D),keys=[list(k) for k in K],txs=C),open(sys.argv[3],'w'),indent=0)
