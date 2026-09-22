import lib,json,bisect
P=lib.load('positions_raw.json'); S=lib.load('supply_monthly.json'); mb=lib.load('month_blocks.json')
rates=lib.load('rate_updates.json'); rts=[r['ts'] for r in rates]
def rate_at(t):
    i=bisect.bisect_right(rts,t)-1
    return 1.0 if i<0 else rates[i]['new']/1e8
px=json.load(open(lib.RAW+'/btc_px.json')); pts=[p[0] for p in px]
def btc_px(t):
    i=bisect.bisect_right(pts,t+43200)-1
    return px[max(i,0)][1]
BTC1={'WBTC','cbBTC','aEthWBTC','aEthcbBTC','spWBTC','spcbBTC','BTCN','SY-EBTC','SY-LBTC','SY-cornLBTC','SY-corn-eBTC','SY-liquidBeraBTC','liquidBeraBTC','tacBTC'}
LB={'LBTC','aEthLBTC','spLBTC'}; EB={'eBTC','aEtheBTC'}
PT={'PT-LBTC-27MAR2025','PT-cornLBTC-27FEB2025','PT-corn-eBTC-27MAR2025','PT-liquidBeraBTC-10APR2025'}
B4626={'MCwBTC','MCcbBTC','pWBTC'}
USD1={'USDC','USDT','PYUSD','RLUSD','USR','cUSD','fxUSD','aEthUSDC','bUSD0','SY-USD0++'}
U4626={'USUALUSDC+','MC-USR','wstUSR','stcUSD','senPYUSDmain','senPYUSDPRIMEv2'}
UDEBT={'variableDebtEthUSDC','variableDebtEthUSDT','variableDebtPYUSD','variableDebtUSDC'}
rows=[]
for k,p in P.items():
    t=mb[k]['ts']; bp=btc_px(t); rl=p['rate_lbtc'] or 1; re=p['rate_ebtc'] or 1
    b=p['bals']; get=lambda s:b.get(s,{}).get('amt',0)
    btc={}
    for s in BTC1: 
        if get(s): btc[s]=get(s)
    for s in LB:
        if get(s): btc[s]=get(s)*rl
    for s in EB:
        if get(s): btc[s]=get(s)*re
    for s in PT:
        if get(s): btc[s]=get(s)  # face value upper bound
    for s in B4626:
        if b.get(s,{}).get('assets'): btc[s]=b[s]['assets']
    btc_debt=get('variableDebtEthWBTC')
    usd={}
    for s in USD1:
        if get(s): usd[s]=get(s)
    for s in U4626:
        if b.get(s,{}).get('assets'): usd[s]=b[s]['assets']
    if get('stUSR'): usd['stUSR']=get('stUSR')
    if p.get('convex_lp'): usd['convexLP_USDC/fxUSD']=p['convex_lp']*(p['lp_vp'] or 1)
    if get('USDCfxUSD'): usd['USDCfxUSD']=get('USDCfxUSD')
    usd_debt={s:get(s) for s in UDEBT if get(s)}
    for m,v in p['morpho'].items():
        c,l=m.split('/')
        if v['collateral']>1e-4:
            mult=rl if c=='LBTC' else re if c=='eBTC' else 1
            btc['morpho:'+c]=btc.get('morpho:'+c,0)+v['collateral']*mult
        if v['debt']>1:
            if l=='WBTC': btc_debt+=v['debt']
            else: usd_debt['morpho:'+l]=v['debt']
        elif l=='WBTC' and v['debt']>1e-3: btc_debt+=v['debt']
    coll_btc=sum(btc.values())
    usd_a=sum(usd.values()); usd_d=sum(usd_debt.values())
    net_btc=coll_btc-btc_debt+(usd_a-usd_d)/bp
    sup=(S[k]['eth'] or 0)+(S[k]['op'] or 0); r=rate_at(t)
    nav=sup/1e8*r
    rows.append(dict(month=k,btc_px=bp,rate=r,shares_eth=(S[k]['eth'] or 0)/1e8,shares_op=(S[k]['op'] or 0)/1e8,nav_btc=nav,btc_assets=coll_btc,btc_debt=btc_debt,usd_assets=usd_a,usd_debt=usd_d,visible_net_btc=net_btc,residual_btc=nav-net_btc,btc=btc,usd=usd,usd_debt_d=usd_debt,acct=p['acct']))
    print(f"{k:10s} px {bp:8.0f} NAV {nav:8.2f} BTC | btcA {coll_btc:7.2f} btcD {btc_debt:6.2f} usdA {usd_a/1e6:6.2f}M usdD {usd_d/1e6:6.2f}M | visible {net_btc:8.2f} resid {nav-net_btc:8.2f}")
lib.save('valuation_monthly.json',rows)
