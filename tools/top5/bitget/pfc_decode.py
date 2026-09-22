import json, datetime
from rpc import k256
sigs={'AnchorPriceUpdated(address,uint128,uint32)':'Anchor','DriftPriceUpdated(address,uint128,uint32)':'Drift','ThresholdsSet(address,uint16,uint16,uint16,uint16,uint8)':'Thresholds','VaultFeesSet(address,uint16,uint16)':'Fees','VaultAccountantSet(address,address)':'Accountant','VaultRegistered(address)':'Registered','VaultPausedChanged(address,bool)':'Paused','HighestPriceReset(address,uint128)':'HPReset','PauseOnBadAnchorUpdateChanged(address,bool)':'PauseOnBad'}
T={'0x'+k256(s.encode()).hex():n for s,n in sigs.items()}
def load():
    logs=json.load(open('../raw/pfc_logs_vault.json'))
    rows=[]
    for l in logs:
        n=T.get(l['topics'][0],l['topics'][0][:10]); d=l['data'][2:]; w=[int(d[i:i+64],16) for i in range(0,len(d),64)]
        rows.append(dict(ts=int(l['timeStamp'],16),ev=n,w=w,block=int(l['blockNumber'],16),tx=l['transactionHash']))
    return rows
if __name__=='__main__':
    rows=load()
    from collections import Counter
    print(Counter(r['ev'] for r in rows))
    for r in rows:
        if r['ev'] not in ('Anchor','Drift'): print(datetime.datetime.utcfromtimestamp(r['ts']), r['ev'], r['w'], r['block'], r['tx'])
    an=[r for r in rows if r['ev']=='Anchor']
    print('first anchors'); [print(datetime.datetime.utcfromtimestamp(r['ts']), r['w'][0]/1e8) for r in an[:8]]
    # daily last anchor
    daily={}
    for r in an: daily[datetime.datetime.utcfromtimestamp(r['ts']).date()]=r['w'][0]/1e8
    for d,p in sorted(daily.items()): print(d,p)
    dr=[r for r in rows if r['ev']=='Drift']; print('drift sample',[(str(datetime.datetime.utcfromtimestamp(r['ts'])),r['w'][0]/1e8) for r in dr[:3]], len(dr))
