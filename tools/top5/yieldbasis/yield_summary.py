# Protocol-level (TVL-weighted) monthly BTC yield series, organic vs incentive split, stability stats
import csv,json,collections,statistics as st,math
Y=list(csv.DictReader(open('../yield_monthly.csv')))
Tv={(r['pool'],r['month']):r for r in csv.DictReader(open('../tvl_monthly.csv')) if r['asset'] in('WBTC','cbBTC','tBTC')}
A={(r['market'],r['date']):r for r in json.load(open('../raw/archive_monthend.json'))}
EC={r['month']:r for r in csv.DictReader(open('../economics_monthly.csv'))}
f=lambda x: float(x) if x not in ('',None) else None
out=[]
for mon in sorted(set(r['month'] for r in Y)):
    # v1 excluded from Nov-2025 on: migration to v2 (Nov 12) makes v1 unstaked-PPS accounting unrepresentative
    rs=[r for r in Y if r['month']==mon and 'WETH' not in r['pool'] and not (r['pool'].startswith('v1') and mon>='2025-11')]
    W=0; acc=collections.defaultdict(float); org_usd=0
    for r in rs:
        a,b=r['period'].split('..'); days=int(r['days'])
        ra=A.get((r['pool'],a)); rb=A.get((r['pool'],b))
        tvl_s=float(ra['liq_total']) if ra else 0; tvl_e=float(rb['liq_total']) if rb else 0
        w=(tvl_s+tvl_e)/2*days
        if w<=0: continue
        sf=(rb['staker_bal']/rb['supply']) if rb and rb['supply'] else 0
        W+=w
        for k in ('unstaked_realized_apy','unstaked_redeemable_apy','staked_reward_apy'):
            if f(r[k]) is not None: acc[k]+=f(r[k])*w
        acc['staked_frac']+=sf*w
        px=float(Tv[(r['pool'],mon)]['asset_price_usd']) if (r['pool'],mon) in Tv else 0
        org_usd+=(1-sf)*(tvl_s+tvl_e)/2*(float(r['pps_end'])/float(r['pps_start'])-1)*px
    if W==0: continue
    d={k:v/W for k,v in acc.items()}
    d['blended_lp_apy']=(1-d['staked_frac'])*d['unstaked_realized_apy']+d['staked_frac']*d['staked_reward_apy']
    e=EC.get(mon,{})
    inc=float(e.get('yb_emissions_usd_btc_gauges') or 0); adm=float(e.get('admin_fee_accrued_usd_btc') or 0)
    out.append(dict(month=mon,unstaked_book_apy=round(d['unstaked_realized_apy'],2),unstaked_redeemable_apy=round(d['unstaked_redeemable_apy'],2),staked_token_apr=round(d['staked_reward_apy'],2),staked_frac=round(d['staked_frac'],3),blended_lp_apy=round(d['blended_lp_apy'],2),organic_to_unstaked_usd=round(org_usd),admin_fees_usd=round(adm),incentive_yb_usd=round(inc),organic_share_of_lp_income=round(org_usd/(org_usd+inc),3) if org_usd+inc>0 and org_usd>0 else (0.0 if inc>0 else None)))
with open('../yield_protocol_monthly.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); [w.writerow(r) for r in out]
for r in out: print(r)
def stats(series,label):
    v=[x for x in series if x is not None]
    print(label,'n',len(v),'mean %.2f median %.2f stdev %.2f min %.2f max %.2f'%(st.mean(v),st.median(v),st.stdev(v),min(v),max(v)))
full=[r for r in out if r['month']>='2025-10']
stats([r['unstaked_book_apy'] for r in full],'protocol unstaked book APY (Oct25-Sep26)')
stats([r['unstaked_redeemable_apy'] for r in full],'protocol unstaked redeemable APY')
stats([r['staked_token_apr'] for r in full],'protocol staked token APR')
stats([r['blended_lp_apy'] for r in full],'blended LP APY')
# generation-level stats from per-pool rows, active windows only
Yp=collections.defaultdict(list)
for r in Y:
    p=r['pool']; m=r['month']
    act=(p.startswith('v1') and 'WETH' not in p and '2025-10'<=m<='2025-10') or (p.startswith('v2') and '2025-12'<=m<='2026-05') or (p.startswith('v3') and 'WETH' not in p and '2026-06'<=m<='2026-09')
    if act: Yp[p].append((m,f(r['unstaked_realized_apy']),f(r['unstaked_redeemable_apy'])))
for p,v in sorted(Yp.items()):
    b=[x[1] for x in v]; rd=[x[2] for x in v]
    wb=min(v,key=lambda x:x[1]); wr=min(v,key=lambda x:x[2])
    print(p,'months',len(v),'book mean %.1f sd %.1f worst %s %.1f | redeem mean %.1f sd %.1f worst %s %.1f'%(st.mean(b),st.stdev(b) if len(b)>1 else 0,wb[0],wb[1],st.mean(rd),st.stdev(rd) if len(rd)>1 else 0,wr[0],wr[2]))
