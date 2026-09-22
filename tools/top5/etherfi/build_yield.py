# Builds yield_monthly.csv (+ raw/yield_detail.json)
import lib,json,csv,bisect,os,datetime
OUT=os.path.join(os.path.dirname(__file__),'..')
mb=lib.load('month_blocks.json'); VAL={r['month']:r for r in lib.load('valuation_monthly2.json')}
P=lib.load('positions_raw.json'); IDX=lib.load('aave_spark_idx.json'); SP=lib.load('share_prices.json')
ITB=lib.load('itb_positions.json'); LL=lib.load('llama_monthly.json'); RC=lib.load('reward_claims.json')
rates=lib.load('rate_updates.json'); rts=[r['ts'] for r in rates]
def rate_at(t):
    i=bisect.bisect_right(rts,t)-1
    return 1.0 if i<0 else rates[i]['new']/1e8
months=[k for k in mb if k not in ('2024-11-14launch',)]
months.sort(key=lambda k:mb[k]['ts'])
def apy(x0,x1,days):
    if not x0 or not x1 or days<=0: return None
    return ((x1/x0)**(365/days)-1)*100
# fee schedule (bps) from PlatformFeeUpdated events
FEES=[(1731626531,200),(1735022640,0),(1736182771,200),(1744261860,100),(1747714560,0),(1763347440,50),(1764370200,100),(1783979340,50),(1787612940,0)]
def fee_avg(t0,t1):
    tot=0
    for i,(ts,f) in enumerate(FEES):
        te=FEES[i+1][0] if i+1<len(FEES) else 4e9
        a,b=max(t0,ts),min(t1,te)
        if b>a: tot+=f*(b-a)
    return tot/(t1-t0)
# reward USD by month and bucket
rew={}
def addr(m,bucket,usd): rew.setdefault(m,{}); rew[m][bucket]=rew[m].get(bucket,0)+usd
def month_of_date(d):  # 'YYYY-MM-DD HH:MM' -> month key (Sep 2026 -> '2026-09-20' if <= 20th 14:00)
    ym=d[:7]
    if ym=='2026-09': return '2026-09-20' if d<='2026-09-20 14:00' else None
    return ym
for r in RC:
    m=month_of_date(r['date'])
    if not m: continue
    if r['token'] in ('RLUSD','PYUSD'):
        u=r['user'].lower()
        b={'0x8950daa8c142e63eae0e8efef4c970c4e6602d56':'itb1_euler_rlusd','0x832fe608c50ade63700d216636ca48b9e8a7d89e':'itb2_euler_rlusd','0x075734ae0d7a4c89db7799f73de32f6c53feafd6':'itb3_euler_pyusd'}.get(u,'vault_merkl_pyusd')
        addr(m,b,r['amount'])
RTV=lib.load('reward_token_values.json')['rows']
for s,d,amt,p,usd in RTV:
    m=d[:7]
    addr(m,{'ETHFI':'ethfi_incentive','MORPHO':'morpho_rewards','CRV':'curve_convex_rewards','FXN':'curve_convex_rewards'}[s],usd or 0)
# leg rate helpers
def borrow_rate(leg,k0,k1,days):
    if leg.startswith('aave:'): a='aave_'+leg.split(':')[1]; return apy(IDX[k0][a]['debt_idx'],IDX[k1][a]['debt_idx'],days)
    if leg.startswith('spark:') or leg=='ITB spark:PYUSD': a='spark_'+leg.split(':')[1]; return apy(IDX[k0][a]['debt_idx'],IDX[k1][a]['debt_idx'],days)
    if leg=='ITB aave:RLUSD': return apy(SP[k0]['aave_RLUSD_debt_idx'],SP[k1]['aave_RLUSD_debt_idx'],days)
    if leg.startswith('morpho:'): kk='morpho_borrow_idx:'+leg.split(':',1)[1]; return apy(SP[k0].get(kk),SP[k1].get(kk),days)
DEPL4626={'USUALUSDC+':'USUALUSDC+','MC-USR':'MC-USR','wstUSR':'wstUSR','stcUSD':'stcUSD','senPYUSDmain':'senPYUSDmain','senPYUSDPRIMEv2':'senPYUSDPRIMEv2','ITB:eRLUSD-1':'eRLUSD-1','ITB:eRLUSD-7':'eRLUSD-7','ITB:ePYUSD-6':'ePYUSD-6'}
def deploy_rate(leg,k0,k1,days):
    if leg in DEPL4626: s=DEPL4626[leg]; return apy(SP[k0].get(s),SP[k1].get(s),days)
    if leg in ('convexLP_USDC/fxUSD','USDCfxUSD'): return apy(SP[k0]['curveLP_vp'],SP[k1]['curveLP_vp'],days)
    if leg.startswith('OP:liquidRWA'): return ((1761357.47/1750000)**(365/37.0)-1)*100
    return 0.0
def legs(k):
    v=VAL[k]; d={}
    # debt legs: split morpho by market
    for lab,amt in v['debt'].items():
        if lab.startswith('morpho:'): continue
        d[('B',lab)]=amt
    for m,x in P[k]['morpho'].items():
        if x['debt']>1 and not m.endswith('/WBTC'): d[('B','morpho:'+m)]=x['debt']
    for lab,amt in v['usd'].items(): d[('D',lab)]=amt
    return d
rows=[]; detail={}
for i,k in enumerate(months):
    if i==0: continue
    k0=months[i-1]; t0,t1=mb[k0]['ts'],mb[k]['ts']; days=(t1-t0)/86400
    r0,r1=rate_at(t0),rate_at(t1)
    net=apy(r0,r1,days) if r0>0 else None
    if VAL[k0]['nav_btc']<1 and k!='2025-01': net=None
    fee=fee_avg(t0,t1)
    L0,L1=legs(k0),legs(k)
    keys=set(L0)|set(L1)
    bcost=0; bavg=0; dinc=0; davg=0; det={}
    for key in keys:
        a=(L0.get(key,0)+L1.get(key,0))/2
        typ,lab=key
        rr=borrow_rate(lab,k0,k,days) if typ=='B' else deploy_rate(lab,k0,k,days)
        if rr is None: rr=0.0
        det[f'{typ}:{lab}']={'avg_usd':round(a),'apy':round(rr,3)}
        if typ=='B': bcost+=a*rr/100; bavg+=a
        else: dinc+=a*rr/100; davg+=a
    rw=rew.get(k,{})
    depl_rewards=sum(v for b,v in rw.items() if b not in ('ethfi_incentive',))*365/days
    vault_inc=rw.get('ethfi_incentive',0)*365/days
    bp=(VAL[k0]['btc_px']+VAL[k]['btc_px'])/2; nav_usd=(VAL[k0]['nav_btc']+VAL[k]['nav_btc'])/2*bp
    carry_org=dinc-bcost; carry_tot=carry_org+depl_rewards
    row={'month':k if k!='2026-09-20' else '2026-09 (1-20)','realized_net_apy':net,
         'borrow_pyusd':apy(IDX[k0]['spark_PYUSD']['debt_idx'],IDX[k]['spark_PYUSD']['debt_idx'],days) if IDX[k0]['spark_PYUSD']['debt_idx'] and IDX[k0]['spark_PYUSD']['debt_idx']>10**27 else None,
         'borrow_usdc':apy(IDX[k0]['spark_USDC']['debt_idx'],IDX[k]['spark_USDC']['debt_idx'],days),
         'depl_stcusd':apy(SP[k0].get('stcUSD'),SP[k].get('stcUSD'),days) if SP[k0].get('stcUSD') and SP[k0]['stcUSD']>1.0001 else None,
         'depl_paypal_main_organic':apy(SP[k0].get('senPYUSDmain'),SP[k].get('senPYUSDmain'),days) if SP[k0].get('senPYUSDmain') and SP[k0]['senPYUSDmain']>1.99 else None}
    llm=LL['senpyusdmain'].get(k[:7])
    row['depl_paypal_main_total']=(row['depl_paypal_main_organic']+llm['apyReward']) if (row['depl_paypal_main_organic'] is not None and llm) else None
    row['avg_debt_usd']=bavg; row['avg_deployed_usd']=davg
    row['actual_borrow_apy']=bcost/bavg*100 if bavg>1000 else None
    row['actual_deploy_organic_apy']=dinc/davg*100 if davg>1000 and bavg>1000 else None
    row['actual_deploy_reward_apy']=depl_rewards/davg*100 if davg>1000 and bavg>1000 else None
    row['spread']=carry_tot/bavg*100 if bavg>1000 else None
    row['organic_spread']=carry_org/bavg*100 if bavg>1000 else None
    row['carry_contrib_to_nav_apy']=carry_tot/nav_usd*100 if nav_usd>0 and bavg>1000 else None
    row['vault_token_incentives_to_nav_apy']=vault_inc/nav_usd*100 if nav_usd>0 and vault_inc else None
    row['platform_fee_bps_avg']=fee
    row['avg_nav_btc']=(VAL[k0]['nav_btc']+VAL[k]['nav_btc'])/2
    # hypothetical current structure: 5.93M Spark PYUSD + 4.37M Spark USDC vs 6.14M stcUSD + 4.15M Paypal Main total
    if row['borrow_pyusd'] is not None and row['depl_stcusd'] is not None and row['depl_paypal_main_total'] is not None:
        c=(6.139*row['depl_stcusd']+4.155*row['depl_paypal_main_total'])-(5.927*row['borrow_pyusd']+4.372*row['borrow_usdc'])
        c_org=(6.139*row['depl_stcusd']+4.155*row['depl_paypal_main_organic'])-(5.927*row['borrow_pyusd']+4.372*row['borrow_usdc'])
        row['hypo_current_structure_spread']=c/10.299; row['hypo_current_structure_organic_spread']=c_org/10.299
    else: row['hypo_current_structure_spread']=None; row['hypo_current_structure_organic_spread']=None
    detail[k]={'legs':det,'rewards_usd':rw,'days':days}
    rows.append(row)
# notes
NOTES={
'2024-12':'Launch month; ~0.001 share test deposits; first Aave USDC borrow (1 USDC) and USD0++/Usual test positions (20 Dec).',
'2025-01':'Deposits 220 BTC. BTC-side: PT-LBTC Morpho loop (borrow 30 WBTC vs PT-LBTC), Pendle PTs (liquidBeraBTC, LBTC), MEV Capital Pendle WBTC vault. Stable leg: Morpho WBTC/USDT 4.2M -> MEV Capital Usual USDC. 120.1k ETHFI (~$152k in Jan) sent by a Safe and sold -> rate steps +0.38%/+0.24% (22/28 Jan). APY from first rate update 9 Jan.',
'2025-02':'NAV peak-1 (609 BTC). Debt up to $18.8M: Aave USDC 4.4M, Morpho WBTC/USDC 5.2M, eBTC/USDC 8.9M, eBTC/USR 0.3M -> Usual USDC (16.8M) + MC-USR. ETHFI sale $35k (6 Feb +0.23%). MORPHO claims $15k.',
'2025-03':'Stable leg $19M (Usual USDC 5.5M, MC-USR 10.1M). Rate flat/negative from mid-March: USD0++/Usual yields collapsed while Morpho USDC borrow ~5-10%.',
'2025-04':'Big unwind 9-10 Apr: Morpho USDC/USR debt repaid, Usual & MC-USR exited; Aave USDC 3M vs Curve USDC/fxUSD LP (Convex) remains. 100 eBTC bridged to Berachain 24-28 Apr (points). Negative carry month.',
'2025-05':'Aave USDC 3.0M vs fxUSD LP 3.0M (fxUSD LP + FXN/CRV ~$17.5k). Berachain eBTC back 16 May. Fee 1%->0% (20 May).',
'2025-06':'No stablecoin debt. 150 BTC (90 BTCN + 60 LBTC) bridged to Corn 2-3 Jun (points). Rate ~flat: pure BTC points strategy.',
'2025-07':'No debt. Whale deposit 380 shares (16-18 Jul) -> NAV peak 836 BTC. Rate flat.',
'2025-08':'Whale exit 381 shares (11 Aug). ITB #1 starts 8-14 Aug: 150 eBTC on Aave -> RLUSD -> Euler eRLUSD-1 (+Merkl RLUSD).',
'2025-09':'ITB #1 scaled to $10.2M RLUSD debt (HF 1.2).',
'2025-10':'ITB #1 $8.7M. Corn assets still bridged.',
'2025-11':'Corn funds back (4-20 Nov). ITB #3 (LBTC on Spark -> PYUSD -> Euler ePYUSD-6, +Merkl PYUSD) $6.8M; ITB #1 closed; fee 0->0.5%->1%.',
'2025-12':'ITB #2 (eBTC Aave -> RLUSD -> Euler eRLUSD-7) $6.7M + ITB #3 $6.8M. tacBTC redeemed via queue.',
'2026-01':'Vault-direct Aave USDT 5.0M (aEthWBTC 51 + aEtheBTC 81 collateral) -> wstUSR 3.5M + stcUSD 1.0M; ITB #2/#3 ~$6M each. Total debt $17.1M (peak).',
'2026-02':'Exited wstUSR (17 Feb; before March Resolv incident). stcUSD 3.8M.',
'2026-03':'ITB #2 closed; ITB #3 halved. Aave USDT 4.0M + USDC 2.1M vs stcUSD 5.8M.',
'2026-04':'Full deleverage by 2 May; whale exit 237.7 shares via BoringSolver (1 Apr); Scroll shares migrated to Optimism (Cash). Optimism chain added 5 Apr.',
'2026-05':'Morpho LBTC/PYUSD 7.0M (12 May) -> Sentora Paypal USD Main 2.5M + stcUSD 1.9M (+ PRIME later).',
'2026-06':'Morpho LBTC/PYUSD 7.0M -> Sentora PRIME Main 2.3M + stcUSD 2.3M; vault Merkl PYUSD claims begin (17.7k on 24 Jun).',
'2026-07':'Debt up to 8.5M PYUSD; stcUSD exited 14 Jul; 1.75M USDC bridged by CCTP to Optimism and parked in ether.fi liquidRWA (21 Jul-24 Aug). Fee 1%->0.5% (13 Jul).',
'2026-08':'Migration Morpho LBTC/PYUSD -> Spark (25 Aug): LBTC collateral swapped to WBTC/cbBTC; Spark PYUSD 7.7M -> Sentora Paypal USD Main 2.9M + stcUSD 1.6M; fee 0.5%->0% (24 Aug).',
'2026-09-20':'Spark 153.08 WBTC + 54.80 cbBTC; debt 5.93M PYUSD + 4.37M USDC (18 Sep); stcUSD 6.14M + Paypal USD Main 4.15M.'}
cols=['month','realized_net_apy','borrow_pyusd','borrow_usdc','depl_stcusd','depl_paypal_main_total','depl_paypal_main_organic','spread','organic_spread','notes',
      'actual_borrow_apy','actual_deploy_organic_apy','actual_deploy_reward_apy','avg_debt_usd','avg_deployed_usd','carry_contrib_to_nav_apy','vault_token_incentives_to_nav_apy','platform_fee_bps_avg','avg_nav_btc','hypo_current_structure_spread','hypo_current_structure_organic_spread']
with open(os.path.join(OUT,'yield_monthly.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for r in rows:
        key=r['month'] if not r['month'].startswith('2026-09') else '2026-09-20'
        r['notes']=NOTES.get(key,'')
        w.writerow([ (round(r[c],3) if isinstance(r.get(c),float) else ('' if r.get(c) is None else r.get(c))) for c in cols])
lib.save('yield_detail.json',detail)
for r in rows: print(r['month'],*(f"{c}={r[c]:.2f}" if isinstance(r.get(c),float) else f"{c}=-" for c in ['realized_net_apy','actual_borrow_apy','actual_deploy_organic_apy','actual_deploy_reward_apy','spread','organic_spread','carry_contrib_to_nav_apy','vault_token_incentives_to_nav_apy','platform_fee_bps_avg','hypo_current_structure_spread']))
