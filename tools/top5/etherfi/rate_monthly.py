import lib,bisect
rows=lib.load('rate_updates.json'); mb=lib.load('month_blocks.json')
ts=[r['ts'] for r in rows]
def rate_at(t):
    i=bisect.bisect_right(ts,t)-1
    return 1e8 if i<0 else rows[i]['new']
def apy(t0,t1):
    r0,r1=rate_at(t0),rate_at(t1)
    return ((r1/r0)**(365*86400/(t1-t0))-1)*100, (r1/r0-1)*100
snap=mb['2026-09-20']['ts']
now=rows[-1]['ts']
for lab,t in [('snap',snap),('now',now)]:
    print(lab,rate_at(t),{d:round(apy(t-d*86400,t)[0],3) for d in [7,14,30,90,180,365]})
print('since launch (2024-11-14):',apy(1731626531,snap))
print('since first update 2025-01-09',apy(rows[0]['ts'],snap))
months=[k for k in mb if k[:4] in('2024','2025','2026') and len(k)==7]
prev=None
for k in months:
    t=mb[k]['ts']; r=rate_at(t)
    if prev: 
        a,p=apy(prev[1],t); print(k,r,f'{p:+.4f}% m/m  APY {a:+.3f}%')
    else: print(k,r)
    prev=(k,t)
a,p=apy(prev[1],snap); print('2026-09(1-20)',rate_at(snap),f'{p:+.4f}% APY {a:+.3f}%')
