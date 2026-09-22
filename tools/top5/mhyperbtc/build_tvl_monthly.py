# tvl_monthly.csv: month-end supply / NAV / TVL per chain (Midas tvl-snapshots-by-network), plus total with flows vs NAV effect
import json,csv,datetime,collections
R='raw/'
n=json.load(open(R+'tvl_by_network.json')); tot=json.load(open(R+'tvl_snapshots.json'))
def me(series):
    by=collections.OrderedDict()
    for x in series:
        ts=datetime.datetime.fromisoformat(x['timestamp'].replace('Z','+00:00'))+datetime.timedelta(hours=1)  # 23:00 UTC snapshot -> next day 00:00
        by[(ts-datetime.timedelta(seconds=1)).strftime('%Y-%m')]=x   # last snapshot within month (as of month end)
    return by
rows=[]
T=me(tot)
chains={'ethereum':me(n['ethereum']),'monad':me(n['monad']),'rootstock':me(n['rootstock'])}
prev=None
for m,x in T.items():
    for c,s in chains.items():
        y=s.get(m)
        if y: rows.append(dict(month=m,chain=c,supply=round(y['supply'],4),nav=y['price'],tvl_btc=round(y['tvl'],4),tvl_usd=round(y['tvlUsd'],0),share_of_supply=round(y['supply']/x['supply'],4) if x['supply'] else 0,net_flow_btc='',nav_effect_btc='',as_of=y['timestamp']))
    flow=navf=''
    if prev:
        flow=round((x['supply']-prev['supply'])*x['price'],4); navf=round(prev['supply']*(x['price']-prev['price']),4)
    rows.append(dict(month=m,chain='total',supply=round(x['supply'],4),nav=x['price'],tvl_btc=round(x['tvl'],4),tvl_usd=round(x['tvlUsd'],0),share_of_supply=1.0,net_flow_btc=flow,nav_effect_btc=navf,as_of=x['timestamp']))
    prev=x
with open('tvl_monthly.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows:
    if r['chain']=='total' or r['chain']=='monad': print(r)
# peak
pk=max(tot,key=lambda x:x['tvl']); print('peak',pk)
pku=max(tot,key=lambda x:x['tvlUsd']); print('peak usd',pku)
