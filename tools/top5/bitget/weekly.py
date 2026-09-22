"""Weekly snapshots (Morph archive RPC) -> raw/weekly_snaps.json"""
from snap import *
from blocks import *
import json, datetime, time
pts=['2026-07-30','2026-07-31','2026-08-07','2026-08-14','2026-08-21','2026-08-28','2026-09-04','2026-09-11','2026-09-18']
out=[]
for d in pts:
    ts=int(datetime.datetime.strptime(d,'%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp())
    b=block_at(ts); o=snap(b); o['date']=d; o['ts']=bts(b); out.append(o)
L=latest()-50
o=snap(L); o['date']=datetime.datetime.utcfromtimestamp(bts(L)).strftime('%Y-%m-%d %H:%M'); o['ts']=bts(L); out.append(o)
for o in out:
    assert o['g_price'] and o['btc_usd'] and o['v_unit_price'], o
json.dump(out,open('../raw/weekly_snaps.json','w'),indent=1)
for o in out: print(o['date'], o['block'], round(o['g_price'],8), o['btc_usd'] and round(o['btc_usd']), o['v_unit_price'], round(o['aera_coll'],4), round(o['aera_debt']), round(o['g_totalAssets']), round(o['g_idle']))
