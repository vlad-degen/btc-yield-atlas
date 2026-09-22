# Build tvl_monthly.csv and yield_monthly.csv from YB API daily snapshots (verified vs archive eth_call),
# archive month-end reads (rate, xcp_profit, virtual_price, watermark) and API event aggregates.
import json,csv,collections,datetime,math,statistics as st
from load import *
S=snaps()
T=series('token_apr',None)
A={ (r['market'],r['date']):r for r in json.load(open('../raw/archive_monthend.json'))}
E=json.load(open('../raw/agg_events_monthly.json'))
ME=['2025-09-30','2025-10-31','2025-11-30','2025-12-31','2026-01-31','2026-02-28','2026-03-31','2026-04-30','2026-05-31','2026-06-30','2026-07-31','2026-08-31','2026-09-20']
def dd(a,b): return (datetime.date.fromisoformat(b)-datetime.date.fromisoformat(a)).days
def ann(r,days): return (r**(365/days)-1) if days>0 and r>0 else None
tvl_rows=[];y_rows=[]
for mid in [0,1,2,3,4,5,7,8,9,6,10]:
    nm=NAMES[mid]; s=S[mid]; first=min(s); asset=nm.split('-')[1]
    pts=[first]+[m for m in ME if m in s and m>first]
    for i in range(1,len(pts)):
        a,b=pts[i-1],pts[i]; xa,xb=s[a],s[b]; days=dd(a,b); mon=b[:7]
        pps_r=xb['pps']/xa['pps']; wd_r=(xb['wd']/xa['wd']) if xa['wd'] and xb['wd'] else None
        # token APR: mean of daily API values within (a,b]
        tv=[int(T[mid][d]['tokenApr'])/1e18 for d in T[mid] if a<d<=b]
        tok=st.mean(tv) if tv else None
        ra,rb=A.get((nm,a)),A.get((nm,b))
        rate=rb['rate_apr'] if rb else None
        wm=(rb['staked']/rb['ideal_staked']-1) if rb and rb['ideal_staked'] else None
        # Cryptoswap decomposition (pool level, LP-value terms) -> equity terms x2
        gross=reb=None
        if ra and rb and ra['xcp_profit'] and rb['xcp_profit']:
            g=math.log(rb['xcp_profit']/ra['xcp_profit']); n=math.log(rb['vp']/ra['vp'])
            gross=2*g*365/days; reb=2*(g-n)*365/days
        ev=E.get('%s|%s'%(nm,mon),{})
        eq_usd_avg=(xa['tot']*xa['px']+xb['tot']*xb['px'])/2
        int_usd=ev.get('interest_usd',0.0)
        int_pct=int_usd/eq_usd_avg*365/days if eq_usd_avg>0 else None
        trd=(xb['wd']/xb['pps']-1) if xb['wd'] else None
        # net flows: v1/v2 -> API LT Deposit/Withdraw events (incl. migrations); v3 -> implied from TVL (API misses the
        # withdraw leg of atomic flash deposit/withdraw arbs in v3); first period of a market counts the launch-day TVL as inflow
        ev_=E.get('%s|%s'%(nm,mon),{})
        if nm.startswith('v3'):
            flow=xb['tot']-xa['tot']*pps_r+(xa['tot'] if i==1 else 0); fm='implied (dTVL - PPS effect)'
        else:
            flow=sum(ev_.get(k,0) for k in ('deposit','mig_deposit'))-sum(ev_.get(k,0) for k in ('withdraw','mig_withdraw')); fm='API LT Deposit/Withdraw events (calendar month)'
        notes=[]
        if days<20: notes.append('partial month (%d d) - annualised figure noisy'%days)
        if nm.startswith('v1') and b>'2025-11-30': notes.append('deprecated legacy market, TVL<30 BTC: not meaningful')
        if nm.startswith('v2') and b>'2026-05-31': notes.append('deprecated after v3 (2026-05-25); residual TVL')
        if nm.endswith('WETH'): notes.append('ETH market (units ETH)')
        if pps_r<1: notes.append('NEGATIVE: book PPS fell')
        if wd_r and wd_r<1: notes.append('NEGATIVE: redeemable value per share fell')
        if wm is not None and wm<-0.001: notes.append('staked side in recovery mode (watermark gap %.2f%%)'%(wm*100))
        if trd is not None and trd<-0.01: notes.append('TRD %.1f%% at month end'%(trd*100))
        y_rows.append(dict(month=mon,pool=nm,period='%s..%s'%(a,b),days=days,
            unstaked_realized_apy=round(ann(pps_r,days)*100,2),
            unstaked_redeemable_apy=round(ann(wd_r,days)*100,2) if wd_r else None,
            staked_reward_apy=round(tok*100,2) if tok is not None else None,
            crvusd_rate=round(rate*100,2) if rate is not None else None,
            interest_paid_usd=round(int_usd),
            interest_cost_pct_equity_ann=round(int_pct*100,2) if int_pct is not None else None,
            gross_pool_income_est=round(gross*100,2) if gross is not None else None,
            rebalancing_loss_est=round(reb*100,2) if reb is not None else None,
            watermark_gap_end_pct=round(wm*100,2) if wm is not None else None,
            trd_end_pct=round(trd*100,2) if trd is not None else None,
            pps_start=round(xa['pps'],6),pps_end=round(xb['pps'],6),redeem_start=round(xa['wd'],6) if xa['wd'] else None,redeem_end=round(xb['wd'],6) if xb['wd'] else None,
            notes='; '.join(notes)))
        tvl_rows.append(dict(month=mon,pool=nm,asset=asset,date=b,tvl_btc=round(xb['tot'],4),tvl_usd=round(xb['tot']*xb['px']),
            tvl_btc_redeemable=round(xb['tot']*(xb['wd']/xb['pps']),4) if xb['wd'] else None,
            tvl_usd_redeemable=round(xb['tot']*(xb['wd']/xb['pps'])*xb['px']) if xb['wd'] else None,
            asset_price_usd=round(xb['px'],2),net_flow_asset=round(flow,4),flow_method=fm,
            cap_usd=round(rb['alloc']/2) if rb else None, debt_crvusd=round(rb['debt']) if rb else None))
# first-day rows for tvl
json.dump(dict(tvl=tvl_rows,yld=y_rows),open('../raw/monthly_built.json','w'),indent=1)
# protocol-level from DefiLlama
L=json.load(open('../raw/llama_protocol.json'))['tvl']
Ld={datetime.datetime.fromtimestamp(x['date'],datetime.UTC).strftime('%Y-%m-%d'):x['totalLiquidityUSD'] for x in L}
btc={}
v=list(json.load(open('../raw/price_coingecko_bitcoin.json'))['coins'].values())[0]['prices']
for x in v: btc[datetime.datetime.fromtimestamp(x['timestamp'],datetime.UTC).strftime('%Y-%m-%d')]=x['price']
agg=collections.defaultdict(lambda:[0.0,0.0,0.0])
for r in tvl_rows:
    if r['asset']!='WETH': agg[r['date']][0]+=r['tvl_btc']; agg[r['date']][1]+=r['tvl_usd']; agg[r['date']][2]+=r['tvl_btc_redeemable'] or 0
with open('../tvl_monthly.csv','w',newline='') as f:
    cols=['month','pool','asset','date','tvl_btc','tvl_usd','tvl_btc_redeemable','tvl_usd_redeemable','asset_price_usd','net_flow_asset','flow_method','cap_usd','debt_crvusd']
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in sorted(tvl_rows,key=lambda r:(r['date'],r['pool'])): w.writerow(r)
    for d in sorted(agg):
        w.writerow(dict(month=d[:7],pool='ALL_BTC_MARKETS (onchain sum)',asset='BTC',date=d,tvl_btc=round(agg[d][0],3),tvl_usd=round(agg[d][1]),tvl_btc_redeemable=round(agg[d][2],3)))
    for d in ME:
        if d in Ld: w.writerow(dict(month=d[:7],pool='PROTOCOL_TOTAL (DefiLlama; incl. WETH)',asset='mixed',date=d,tvl_usd=round(Ld[d]),tvl_btc=round(Ld[d]/btc[max(k for k in btc if k<=d)],2)))
with open('../yield_monthly.csv','w',newline='') as f:
    first=['month','pool','unstaked_realized_apy','staked_reward_apy','crvusd_rate','rebalancing_loss_est','notes']
    cols=first+[c for c in y_rows[0].keys() if c not in first]
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in sorted(y_rows,key=lambda r:(r['month'],r['pool'])): w.writerow(r)
print(len(tvl_rows),len(y_rows))
