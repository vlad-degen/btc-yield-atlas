# Ethereum last block at/before 00:00 UTC for each day 2025-10-14..2026-09-21 (batched RPC, iterative correction)
import json,datetime,urllib.request
URL='https://rpc.mevblocker.io'
def batch(calls):
    req=urllib.request.Request(URL,data=json.dumps([{'jsonrpc':'2.0','id':i,'method':m,'params':p} for i,(m,p) in enumerate(calls)]).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
    r=json.load(urllib.request.urlopen(req,timeout=120)); r=sorted(r,key=lambda x:x['id']); return [x.get('result') for x in r]
def ts_of(bs):
    out=[]
    for i in range(0,len(bs),50):
        out+= [int(x['timestamp'],16) for x in batch([('eth_getBlockByNumber',[hex(b),False]) for b in bs[i:i+50]])]
    return out
ref=26018582; tref=ts_of([ref])[0]
days=[]; d=datetime.datetime(2025,10,14,tzinfo=datetime.timezone.utc)
while d<=datetime.datetime(2026,9,21,tzinfo=datetime.timezone.utc): days.append(int(d.timestamp())); d+=datetime.timedelta(days=1)
bs=[ref+(t-tref)//12 for t in days]
for it in range(6):
    tb=ts_of(bs); tn=ts_of([b+1 for b in bs]); done=True; nb=[]
    for b,t,t1,T in zip(bs,tb,tn,days):
        if t<=T<t1: nb.append(b)
        else:
            done=False; step=(T-t)//12
            nb.append(b+(step if step!=0 else (1 if t<T else -1)))
    bs=nb
    if done: break
out={datetime.datetime.fromtimestamp(T,datetime.timezone.utc).strftime('%Y-%m-%d'):b for T,b in zip(days,bs)}
out['2026-09-20T12']=26018582
json.dump(out,open('raw/eth_daily_blocks.json','w'),indent=0); print('iters',it,len(out),list(out.items())[:2],list(out.items())[-3:])
