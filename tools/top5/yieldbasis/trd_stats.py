# Temporary Redemption Discount (TRD) statistics from daily snapshots
import json
from load import *
S=snaps()
out={}
for mid in [0,1,2,3,4,5,7,8,9,10,6]:
    s=S[mid]; nm=NAMES[mid]
    ds=sorted(d for d in s if s[d]['wd'])
    if nm.startswith('v1') and 'WETH' not in nm: ds=[d for d in ds if d<='2025-11-30']
    if nm=='v1-WETH': ds=[d for d in ds if d<='2026-05-31']
    if nm.startswith('v2'): ds=[d for d in ds if d<='2026-05-31']
    trd=[(d,s[d]['wd']/s[d]['pps']-1) for d in ds]
    worst=min(trd,key=lambda x:x[1])
    # longest streak with TRD < -1%
    best=cur=0; start=None; bs=None
    for d,t in trd:
        if t<-0.01:
            cur+=1
            if cur==1: start=d
            if cur>best: best=cur; bs=(start,d)
        else: cur=0
    out[nm]=dict(days=len(trd),worst_trd_pct=round(worst[1]*100,2),worst_date=worst[0],days_below_1pct=sum(1 for _,t in trd if t<-0.01),days_below_3pct=sum(1 for _,t in trd if t<-0.03),days_below_10pct=sum(1 for _,t in trd if t<-0.10),longest_streak_below_1pct_days=best,streak=bs)
    print(nm,out[nm])
json.dump(out,open('../raw/trd_stats.json','w'),indent=1)
