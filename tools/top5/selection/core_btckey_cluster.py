# cluster Core BTC staking delegations by the Bitcoin key material in the CLTV redeem script
import json,sys,collections,datetime
logs=json.load(open(sys.argv[1]))['logs']
exp={l['topics'][1]:int(l['blockNumber'],16) for l in logs['btcExpired']}
B0,T0=18000000,1727301502
def bd(b): return datetime.datetime.fromtimestamp(T0+(b-B0)*3,datetime.timezone.utc).strftime('%Y-%m-%d')
def keys(h):
    b=bytes.fromhex(h); i=0; out=[]; first=True; lt=None
    while i<len(b):
        op=b[i]; i+=1
        if 1<=op<=75:
            d=b[i:i+op]; i+=op
            if first: lt=int.from_bytes(d,'little')
            elif len(d) in (20,33,65): out.append(d.hex()[:12])
        first=False
    return lt,tuple(sorted(out))
keymap=collections.defaultdict(lambda: collections.defaultdict(float))
keyrange=collections.defaultdict(lambda:[10**12,0,0])
dele_keys=collections.defaultdict(set)
for l in logs['delegated']:
    data=l['data'][2:]; w=[data[i:i+64] for i in range(0,len(data),64)]
    off=int(w[0],16)//32; ln=int(w[off],16); script=''.join(w[off+1:])[:ln*2]
    lt,k=keys(script); amt=int(w[2],16)/1e8; dele='0x'+l['topics'][3][-40:]; b=int(l['blockNumber'],16)
    keymap[k][dele]+=amt; dele_keys[dele].add(k)
    r=keyrange[k]; r[0]=min(r[0],b); r[1]=max(r[1],b); r[2]=max(r[2],lt or 0)
targets=[a.lower() for a in sys.argv[2].split(',')]
for t in targets:
    print('== delegator',t)
    for k in dele_keys[t]:
        r=keyrange[k]
        print('  key',k,'first',bd(r[0]),'last',bd(r[1]),'maxlock',datetime.datetime.fromtimestamp(r[2],datetime.timezone.utc).strftime('%Y-%m-%d') if r[2]>5e8 else r[2])
        for d,a in sorted(keymap[k].items(),key=lambda x:-x[1]): print('     used by',d,f'{a:.2f} BTC cumulative')
