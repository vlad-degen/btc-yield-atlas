# adds month_min_btc_close / hf_at_month_low_est to positions_monthly.csv (run after build_tables.py)
import lib,json,csv,os,datetime
px=json.load(open(lib.RAW+'/btc_px.json')); bym={}
for ts,p in px:
    m=datetime.datetime.fromtimestamp(ts,datetime.UTC).strftime('%Y-%m'); bym.setdefault(m,[]).append((p,ts))
f=os.path.join(os.path.dirname(__file__),'..','positions_monthly.csv')
rows=list(csv.DictReader(open(f)))
for r in rows:
    lo=min(bym.get(r['month'][:7],[(None,0)]))
    if lo[0] is None: continue
    if float(r['btc_usd'])<lo[0]: lo=(float(r['btc_usd']),None)
    r['month_min_btc_close']=round(lo[0]); r['month_min_date']=datetime.datetime.fromtimestamp(lo[1],datetime.UTC).strftime('%Y-%m-%d') if lo[1] else r['month'][:7]+'-end'
    r['hf_at_month_low_est']=round(float(r['min_health_factor'])*lo[0]/float(r['btc_usd']),3) if r['min_health_factor'] else ''
cols=list(rows[0].keys())
for c in ['month_min_btc_close','month_min_date','hf_at_month_low_est']:
    if c not in cols: cols.append(c)
first=['month','collateral_btc','debt_usd','ltv','holdings']
cols=first+[c for c in cols if c not in first]
with open(f,'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]
