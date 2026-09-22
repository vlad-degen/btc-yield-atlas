# Monthly realized yield from the NAV oracle, vs on-chain borrow cost, dollar-vault income and incentives -> yield_monthly.csv
import json,csv,datetime,collections,statistics
R='raw/'
rounds=[(int(r['timestamp']),float(r['nav'])) for r in csv.DictReader(open(R+'oracle_rounds.csv'))]
def nav_at(ts):
    v=None
    for t,n in rounds:
        if t<=ts: v=n
    return v
snap=json.load(open(R+'tvl_snapshots.json'))
sup={ (datetime.datetime.fromisoformat(x['timestamp'].replace('Z','+00:00'))+datetime.timedelta(hours=1)).strftime('%Y-%m-%d'):x for x in snap}
px={}
for p in json.load(open(R+'btc_daily.json'))['coins']['coingecko:bitcoin']['prices']: px[datetime.datetime.fromtimestamp(p['timestamp'],datetime.UTC).strftime('%Y-%m-%d')]=p['price']
def pxf(day):
    dd=datetime.date.fromisoformat(day)
    for i in range(7):
        k=(dd-datetime.timedelta(days=i)).isoformat()
        if k in px: return px[k]
    return 0
bc=json.load(open(R+'borrow_cost_daily.json')); vi=json.load(open(R+'vault_income_monthly.json')); inc=json.load(open(R+'incentives_monthly.json'))
months=[('2025-10','2025-10-15','2025-11-01'),('2025-11','2025-11-01','2025-12-01')]+[(f'{y}-{m:02d}',f'{y}-{m:02d}-01',(f'{y+(m==12)}-{(m%12)+1:02d}-01')) for y,m in [(2025,12),(2026,1),(2026,2),(2026,3),(2026,4),(2026,5),(2026,6),(2026,7),(2026,8)]]+[('2026-09','2026-09-01','2026-09-21T15:10')]
rows=[]
for m,a,b in months:
    ta=int(datetime.datetime.fromisoformat(a).replace(tzinfo=datetime.UTC).timestamp()); tb=int(datetime.datetime.fromisoformat(b).replace(tzinfo=datetime.UTC).timestamp())
    na,nb=nav_at(ta) or 1.0,nav_at(tb)
    days=(tb-ta)/86400; ret=nb/na-1; apy=(1+ret)**(365/days)-1
    # BTC gain ~ sum over days of supply x daily NAV change (supply from Midas snapshots)
    g=0.0; d=datetime.datetime.fromtimestamp(ta,datetime.UTC).date(); gusd=0.0; supd=[]
    while datetime.datetime(d.year,d.month,d.day,tzinfo=datetime.UTC).timestamp()<tb:
        t0=int(datetime.datetime(d.year,d.month,d.day,tzinfo=datetime.UTC).timestamp()); t1=min(t0+86400,tb)
        s=(sup.get(d.isoformat()) or {}).get('supply',0); dn=(nav_at(t1) or 1)-(nav_at(t0) or 1)
        g+=s*dn; gusd+=s*dn*pxf(d.isoformat()); supd.append(s); d+=datetime.timedelta(days=1)
    # borrow cost (on-chain USD debt against BTC collateral)
    debt=0; intr=0; sdebt=0; sint=0; n=0
    for day,r in bc.items():
        if day[:7]==m:
            debt+=r.get('btc_coll_usd_debt_debt',0); intr+=r.get('btc_coll_usd_debt_int',0); sdebt+=r.get('stable_coll_debt',0); sint+=r.get('stable_coll_int',0)
    bapr=intr/debt*365 if debt else None
    v=vi.get(m,{}); usd_inc=v.get('usd_income',0); btc_inc=v.get('btc_income',0)
    ic=sum(val for k,val in inc.get(m,{}).items() if k.endswith('_usd') or k.endswith('_usd_est'))
    rows.append(dict(month=m,nav_start=na,nav_end=nb,days=round(days,1),realized_return=ret,realized_apy=apy,avg_supply=statistics.mean(supd) if supd else 0,
        nav_gain_btc=g,nav_gain_usd=gusd,borrow_cost=bapr,avg_usd_debt=debt/max(1,days),borrow_interest_usd=intr,stable_loop_interest_usd=sint,
        usd_vault_income=usd_inc,btc_vault_income_usd=btc_inc,incentives_usd=ic,incentives_share_of_gain=(ic/gusd if gusd>0 else None)))
json.dump(rows,open(R+'yield_monthly_full.json','w'),indent=0)
for r in rows: print(r['month'],'ret %.3f%% apy %.2f%% gainBTC %.2f ($%.0f) | debt avg $%.2fM bAPR %s int $%.0f | usdVaultInc $%.0f | incent $%.0f (%s of gain)'%(100*r['realized_return'],100*r['realized_apy'],r['nav_gain_btc'],r['nav_gain_usd'],r['avg_usd_debt']/1e6,('%.2f%%'%(100*r['borrow_cost'])) if r['borrow_cost'] else '-',r['borrow_interest_usd'],r['usd_vault_income'],r['incentives_usd'],('%.0f%%'%(100*r['incentives_share_of_gain'])) if r['incentives_share_of_gain'] else '-'))
tot_g=sum(r['nav_gain_usd'] for r in rows); tot_i=sum(r['incentives_usd'] for r in rows)
print('TOTAL NAV gain $%.0f (%.2f BTC); incentives $%.0f = %.0f%%; borrow interest $%.0f; usd vault income $%.0f'%(tot_g,sum(r['nav_gain_btc'] for r in rows),tot_i,100*tot_i/tot_g,sum(r['borrow_interest_usd'] for r in rows),sum(r['usd_vault_income'] for r in rows)))
mr=[r['realized_return'] for r in rows if r['month'] not in ('2025-10','2025-11','2026-09')]
print('monthly returns Dec-Aug: mean %.3f%% stdev %.3f%% min %.3f%% max %.3f%%'%(100*statistics.mean(mr),100*statistics.stdev(mr),100*min(mr),100*max(mr)))
