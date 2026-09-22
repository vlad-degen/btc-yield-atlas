"""Weekly yield decomposition -> ../yield_weekly.csv (+ raw/yield_detail.json)
Sources: raw/weekly_snaps.json (RPC), raw/morpho_market_decoded.json (Morpho events),
raw/campaigns.json (reward distributor 0x53d2...), raw/aera_swaps_claims.json (vault claims/swaps)."""
import json, math, datetime, csv
S=json.load(open('../raw/weekly_snaps.json'))
EV=json.load(open('../raw/morpho_market_decoded.json'))
C=json.load(open('../raw/campaigns.json'))
SC=json.load(open('../raw/aera_swaps_claims.json'))
V='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'
Y=365*86400
acc=[e for e in EV if e['ev']=='AccrueInterest']
def twa_borrow_apr(t0,t1):
    # prevBorrowRate applies from previous accrual to this accrual
    num=0; den=0; prev_t=None
    for e in acc:
        if prev_t is not None:
            a=max(prev_t,t0); b=min(e['ts'],t1)
            if b>a: num+=e['prevBorrowRate']*(b-a); den+=(b-a)
        prev_t=e['ts']
    return (num/den)*Y/1e18 if den else None
def flows(t0,t1,who=V):
    b=sum(e['assets'] for e in EV if e['ev']=='Borrow' and e['onBehalf']==who and t0<e['ts']<=t1)/1e6
    r=sum(e['assets'] for e in EV if e['ev']=='Repay' and e['onBehalf']==who and t0<e['ts']<=t1)/1e6
    return b,r
def camp_paid(t0,t1):
    tot=0
    for c in C:
        if c['token']!='USDC' or c['deposited']<1000: continue
        a=max(c['start'],t0); b=min(c['end'],t1)
        if b>a: tot+=c['amount']*(b-a)/(c['end']-c['start'])
    return tot
def aera_claims(t0,t1):
    return sum(c[2] for c in SC['claims'] if t0< datetime.datetime.strptime(c[0][:19],'%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()<=t1)
rows=[]; detail=[]
pts=[s for s in S if s['date']>='2026-07-31']
for s0,s1 in zip(pts[:-1],pts[1:]):
    t0,t1=s0['ts'],s1['ts']; dt=(t1-t0)/86400; ann=365/dt
    v_apy=(s1['v_unit_price']/s0['v_unit_price'])**ann-1
    g_apy=(s1['g_price']/s0['g_price'])**ann-1
    br_apr=twa_borrow_apr(t0,t1); br_apy=math.exp(br_apr)-1
    avg_tvl=(s0['g_totalAssets']+s1['g_totalAssets'])/2
    inc=camp_paid(t0,t1); inc_apr=inc/avg_tvl*ann
    # Aera USD leg
    b,r=flows(t0,t1); interest=(s1['aera_debt']-s0['aera_debt'])-(b-r)
    avg_sh=(s0['g_aera_shares']+s1['g_aera_shares'])/2
    g_gain=avg_sh*(s1['g_price']-s0['g_price'])
    cl=aera_claims(t0,t1)
    avg_px=(s0['btc_usd']+s1['btc_usd'])/2
    nav=(s0['v_units']*s0['v_unit_price']+s1['v_units']*s1['v_unit_price'])/2
    net_usd=g_gain+cl-interest
    aera_share=(s0['g_aera_shares']/s0['g_totalSupply']+s1['g_aera_shares']/s1['g_totalSupply'])/2
    avg_debt=(s0['aera_debt']+s1['aera_debt'])/2
    d=dict(week=f"{s0['date']}..{s1['date'][:10]}",days=round(dt,2),vault_realized_apy=v_apy,borrow_apy=br_apy,borrow_apr=br_apr,gtusdc_apy_organic=g_apy,incentives_apr=inc_apr,
           spread_total=(g_apy+inc_apr)-br_apy, spread_organic=g_apy-br_apy, incentives_usd=inc, gtusdc_avg_tvl=avg_tvl, aera_share_gtusdc=aera_share,
           aera_interest_usd=interest, aera_gtusdc_organic_usd=g_gain, aera_incentives_claimed_usd=cl, aera_net_usd=net_usd, aera_net_btc=net_usd/avg_px,
           aera_net_btc_apy_on_nav=(net_usd/avg_px)/nav*ann if nav>1 else None, aera_organic_carry_usd=g_gain-interest,
           aera_organic_carry_apy_on_nav=((g_gain-interest)/avg_px)/nav*ann if nav>1 else None, avg_debt=avg_debt, nav_btc=nav)
    detail.append(d)
json.dump(detail,open('../raw/yield_detail.json','w'),indent=1)
def pct(x): return '' if x is None else f"{x*100:.2f}"
with open('../yield_weekly.csv','w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['week','days','vault_realized_apy','borrow_rate','gtusdc_apy_organic','incentives_apy','spread','notes'])
    for d in detail:
        note=(f"incentives ${d['incentives_usd']:,.0f} on avg gtusdc TVL ${d['gtusdc_avg_tvl']/1e6:.1f}M (APR); vault owns {d['aera_share_gtusdc']*100:.0f}% of gtusdc; "
              f"vault USD leg: interest -${d['aera_interest_usd']:,.0f}, gtusdc organic +${d['aera_gtusdc_organic_usd']:,.0f}, rewards claimed +${d['aera_incentives_claimed_usd']:,.0f}; "
              f"organic carry {'NEGATIVE' if d['spread_organic']<0 else 'positive'} ({pct(d['spread_organic'])} pp); spread = organic+incentives-borrow")
        w.writerow([d['week'],d['days'],pct(d['vault_realized_apy']),pct(d['borrow_apy']),pct(d['gtusdc_apy_organic']),pct(d['incentives_apr']),pct(d['spread_total']),note])
for d in detail:
    print(d['week'], 'vault',pct(d['vault_realized_apy']),'borrow',pct(d['borrow_apy']),'g_org',pct(d['gtusdc_apy_organic']),'inc',pct(d['incentives_apr']),'spread',pct(d['spread_total']),'org_spread',pct(d['spread_organic']),
          '| aera int',round(d['aera_interest_usd']),'g',round(d['aera_gtusdc_organic_usd']),'cl',round(d['aera_incentives_claimed_usd']),'netBTC',round(d['aera_net_btc'],4),'netAPY',pct(d['aera_net_btc_apy_on_nav']),'orgcarryAPY',pct(d['aera_organic_carry_apy_on_nav']))
