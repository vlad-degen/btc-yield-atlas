import json,sys,datetime,collections
tx=json.load(open(sys.argv[1]))
B0,T0=18000000,1727301502
def blk(date):
    ts=datetime.datetime.strptime(date,'%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp()
    return int(B0+(ts-T0)/3)
dates=['2024-12-01','2025-01-01','2025-02-01','2025-03-01','2025-04-01','2025-05-01','2025-06-01','2025-07-01','2025-08-01','2025-09-01','2025-10-01','2025-11-01','2025-11-20','2025-12-01','2025-12-10','2026-01-01','2026-02-01','2026-03-01','2026-04-01','2026-05-01','2026-06-01','2026-07-01','2026-08-01','2026-09-01','2026-09-20']
focus=sys.argv[2].split(',') if len(sys.argv)>2 else []
tot={}
per=collections.defaultdict(dict)
for d in dates:
    b=blk(d); s=0
    for t in tx.values():
        if t['block']<=b and (t['exp'] is None or t['exp']>b):
            s+=t['amt']
            if t['dele'] in focus: per[t['dele']][d]=per[t['dele']].get(d,0)+t['amt']
    tot[d]=s
print('date        totalActiveBTC(0x1014 only) '+' '.join(f[:8] for f in focus))
for d in dates:
    print(d, f"{tot[d]/1e8:10.1f}", ' '.join(f"{per[f].get(d,0)/1e8:8.1f}" for f in focus))
