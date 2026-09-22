# Holding-period (cohort) returns in BTC terms: book PPS and redeemable value, per generation and chained across migrations
import json,datetime
from load import *
S=snaps()
def g(mid,d,k): 
    ks=[x for x in S[mid] if x<=d]; return S[mid][max(ks)][k]
def ann(r,d0,d1):
    days=(datetime.date.fromisoformat(d1)-datetime.date.fromisoformat(d0)).days; return (r**(365/days)-1)*100,days
out=[]
for a,(v1,v2,v3) in {'WBTC':(0,3,7),'cbBTC':(1,4,8),'tBTC':(2,5,9)}.items():
    segs=[(v1,'2025-09-24','2025-11-12'),(v2,'2025-11-12','2026-05-24'),(v3,'2026-05-25','2026-09-20')]
    cb=cr=1
    for mid,d0,d1 in segs:
        rb=g(mid,d1,'pps')/g(mid,d0,'pps'); rr=g(mid,d1,'wd')/g(mid,d0,'wd'); cb*=rb; cr*=rr
        ab,days=ann(rb,d0,d1); ar,_=ann(rr,d0,d1)
        out.append(dict(asset=a,market=NAMES[mid],start=d0,end=d1,days=days,book_return_pct=round((rb-1)*100,2),book_apy=round(ab,2),redeem_return_pct=round((rr-1)*100,2),redeem_apy=round(ar,2)))
    ab,days=ann(cb,'2025-09-24','2026-09-20'); ar,_=ann(cr,'2025-09-24','2026-09-20')
    out.append(dict(asset=a,market='chained v1->v2->v3 (unstaked, ignores migration frictions)',start='2025-09-24',end='2026-09-20',days=days,book_return_pct=round((cb-1)*100,2),book_apy=round(ab,2),redeem_return_pct=round((cr-1)*100,2),redeem_apy=round(ar,2)))
# v2 cohort exiting at worst TRD day and at v2 peak redeem
for mid in (3,4,5):
    s=S[mid]; ds=[d for d in s if d<='2026-05-24' and s[d]['wd']]
    w=min(ds,key=lambda d:s[d]['wd']); 
    out.append(dict(asset=NAMES[mid],market='v2 cohort from launch, exit at worst redeem day',start='2025-11-12',end=w,days=(datetime.date.fromisoformat(w)-datetime.date(2025,11,12)).days,book_return_pct=round((s[w]['pps']/s['2025-11-12']['pps']-1)*100,2),book_apy=None,redeem_return_pct=round((s[w]['wd']/s['2025-11-12']['wd']-1)*100,2),redeem_apy=None))
for r in out: print(r)
json.dump(out,open('../raw/holding_period.json','w'),indent=1)
