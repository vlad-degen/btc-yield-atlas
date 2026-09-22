"""6-hourly LTV / health path of the Aera vault position (Morph archive RPC) -> raw/ltv_path.json"""
import json, datetime
from rpc import *
S=json.load(open('../raw/weekly_snaps.json'))
M='0xad10d07901dc3195c3cb5e78e061f4ea8d9b4905'; MID='37d156e96a4230c1fe9545579086e4b40d08b4aae8b3c78ee91031f2a22c1a5c'
V='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'; ORA='0x22b3d92703ee73af5e31a6ba56cca2fdced6c412'
kp=[(s['ts'],s['block']) for s in S]
def interp(ts):
    for (t0,b0),(t1,b1) in zip(kp[:-1],kp[1:]):
        if t0<=ts<=t1: return int(b0+(b1-b0)*(ts-t0)/(t1-t0))
    return kp[-1][1]
def w(r): h=r[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
t=kp[1][0]; out=[]
while t<=kp[-1][0]:
    b=hex(interp(t))
    calls=[('eth_call',[{'to':M,'data':sel('market(bytes32)')+MID},b]),('eth_call',[{'to':M,'data':sel('position(bytes32,address)')+MID+enc_addr(V)},b]),('eth_call',[{'to':ORA,'data':sel('price()')},b]),('eth_getBlockByNumber',[b,False])]
    for ch in ['morph','morph2','morph3']:
        try:
            r=batch(ch,calls)
            if any(isinstance(x,tuple) or x is None for x in r): raise Exception('partial')
            break
        except Exception as e: r=None
    if r:
        mk=w(r[0]); p=w(r[1]); px=int(r[2],16)/1e34; ts=int(r[3]['timestamp'],16)
        debt=p[1]*mk[2]/mk[3]/1e6 if mk[3] else 0; coll=p[2]/1e8
        ltv=debt/(coll*px) if coll else None
        out.append(dict(ts=ts,date=datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M'),block=int(b,16),btc=px,debt=debt,coll=coll,ltv=ltv,liq_price=debt/(coll*0.77) if coll else None))
    t+=6*3600
json.dump(out,open('../raw/ltv_path.json','w'),indent=0)
v=[o for o in out if o['ltv'] and o['coll']>100]
mx=max(v,key=lambda o:o['ltv']); mn=min(v,key=lambda o:o['ltv'])
print('points',len(out),'max LTV',round(mx['ltv']*100,2),mx['date'],'btc',round(mx['btc']),'liq',round(mx['liq_price']),' min LTV',round(mn['ltv']*100,2),mn['date'])
for o in out[::4]: print(o['date'], round(o['btc']), round(o['debt']/1e6,2), round(o['coll'],2), o['ltv'] and round(o['ltv']*100,2), o['liq_price'] and round(o['liq_price']))
