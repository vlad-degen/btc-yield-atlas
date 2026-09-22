import json,sys,collections
d=json.load(open(sys.argv[1]))
L=d['logs']
tx={}
for l in L['delegated']:
    txid=l['topics'][1]; cand='0x'+l['topics'][2][-40:]; dele='0x'+l['topics'][3][-40:]
    data=l['data'][2:]; w=[data[i:i+64] for i in range(0,len(data),64)]
    outidx=int(w[1],16); amt=int(w[2],16); fee=int(w[3],16)
    tx[txid]=dict(cand=cand,dele=dele,amt=amt,block=int(l['blockNumber'],16),exp=None)
expired_unknown=0
for l in L['btcExpired']:
    txid=l['topics'][1]
    if txid in tx: tx[txid]['exp']=int(l['blockNumber'],16)
    else: expired_unknown+=1
print('delegated txs',len(tx),'expired matched',sum(1 for t in tx.values() if t['exp']),'expired unmatched (pre-1014 txs)',expired_unknown)
agg=collections.defaultdict(lambda: dict(n=0,total=0,active=0,first=10**12,last=0,lastexp=0,cands=set()))
for t in tx.values():
    a=agg[t['dele']]; a['n']+=1; a['total']+=t['amt']; a['first']=min(a['first'],t['block']); a['last']=max(a['last'],t['block']); a['cands'].add(t['cand'])
    if t['exp'] is None: a['active']+=t['amt']
    else: a['lastexp']=max(a['lastexp'],t['exp'])
print('total active (no btcExpired) BTC:',sum(t['amt'] for t in tx.values() if t['exp'] is None)/1e8)
print('distinct delegators',len(agg))
rows=sorted(agg.items(),key=lambda kv:-kv[1]['total'])
print(f"{'delegator':44} {'n':>5} {'sumDelegBTC':>12} {'activeBTC':>10} {'firstBlk':>9} {'lastBlk':>9} {'lastExpBlk':>10} ncand")
for k,a in rows[:int(sys.argv[2]) if len(sys.argv)>2 else 30]:
    print(f"{k:44} {a['n']:5} {a['total']/1e8:12.2f} {a['active']/1e8:10.2f} {a['first']:9} {a['last']:9} {a['lastexp']:10} {len(a['cands'])}")
json.dump({k:{**a,'cands':sorted(a['cands'])} for k,a in agg.items()},open(sys.argv[1].replace('.json','_by_delegator.json'),'w'))
json.dump(tx,open(sys.argv[1].replace('.json','_txs.json'),'w'))
