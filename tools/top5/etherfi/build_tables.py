import lib,json,csv,os,bisect
OUT=os.path.join(os.path.dirname(__file__),'..')
mb=lib.load('month_blocks.json'); VALS=lib.load('valuation_monthly2.json'); VAL={r['month']:r for r in VALS}
P=lib.load('positions_raw.json'); S=lib.load('supply_monthly.json'); FL={r['month']:r for r in lib.load('flows_monthly.json')}
EH=lib.load('eth_holder_snapshots.json')
try: OH=lib.load('op_holder_snapshots_rpc.json')
except Exception: OH={}
months=sorted([k for k in mb if k!='2024-11-14launch'],key=lambda k:mb[k]['ts'])
# ---- positions_monthly ----
def f(x,n=2): return '' if x is None else round(x,n)
prow=[]
for k in months:
    v=VAL[k]; p=P[k]; bp=v['btc_px']
    usd=dict(v['usd']); debt=dict(v['debt']); btc=dict(v['btc'])
    # health factors
    hfs=[]
    for nm,a in (v.get('acct') or {}).items():
        if a.get('hf') and a['debt_usd']>1000: hfs.append((f'{nm}(vault)',a['hf']))
    for nm,a in (v.get('itb_acct') or {}).items():
        if a.get('hf') and a['debt_usd']>1000: hfs.append((nm,a['hf']))
    for m,x in p['morpho'].items():
        c,l=m.split('/')
        if x['debt']>1000 and l!='WBTC':
            mult=(p['rate_lbtc'] or 1) if c=='LBTC' else (p['rate_ebtc'] or 1) if c=='eBTC' else 1
            hfs.append((f'morpho {m} (est.)',x['collateral']*mult*bp*x['lltv']/x['debt']))
    minhf=min(hfs,key=lambda z:z[1]) if hfs else None
    liq_px=bp/minhf[1] if minhf else None
    top=sorted([(kk,val) for kk,val in usd.items() if val>50000],key=lambda z:-z[1])
    hold='; '.join([f'{kk} ${val/1e6:.2f}M' for kk,val in top[:6]])
    tb=sorted([(kk,val) for kk,val in btc.items() if val>1],key=lambda z:-z[1])
    hold_btc='; '.join([f'{kk} {val:.1f}' for kk,val in tb[:8]])
    dstr='; '.join([f'{kk} ${val/1e6:.2f}M' for kk,val in sorted(debt.items(),key=lambda z:-z[1]) if val>1000])
    usd_debt=v['usd_debt']; coll=v['coll_posted_btc']
    ltv=(usd_debt/(coll*bp)) if coll>0 and usd_debt>1000 else None
    btc_debt=v['btc_debt']
    prow.append({'month':k,'btc_usd':round(bp),'nav_btc':f(v['nav_btc']),'collateral_btc':f(coll),'debt_usd':round(usd_debt),'ltv':f(ltv*100 if ltv else None),
        'min_health_factor':f(minhf[1],3) if minhf else '','min_hf_account':minhf[0] if minhf else '','liq_btc_price_est':round(liq_px) if liq_px else '',
        'btc_debt_btc':f(btc_debt),'deployed_usd':round(v['usd_assets']),
        'debt_by_venue':dstr,'holdings':'BTC-side: '+hold_btc+' | USD-side: '+hold,
        'reconstructed_net_btc':f(v['net_btc']),'residual_vs_nav_btc':'' })
# residual incl. Scroll shares
rates=lib.load('rate_updates.json'); rts=[r['ts'] for r in rates]
def rate_at(t):
    i=bisect.bisect_right(rts,t)-1
    return 1.0 if i<0 else rates[i]['new']/1e8
for r in prow:
    k=r['month']; sc=(S[k].get('scroll') or 0)/1e8
    nav_all=VAL[k]['nav_btc']
    r['nav_btc']=f(nav_all)
    r['residual_vs_nav_btc']=f(nav_all-(r['reconstructed_net_btc'] or 0))
cols=list(prow[0].keys())
with open(os.path.join(OUT,'positions_monthly.csv'),'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); [w.writerow(r) for r in prow]
for r in prow: print(r['month'],r['nav_btc'],r['collateral_btc'],r['debt_usd'],r['ltv'],r['min_health_factor'],r['liq_btc_price_est'],r['residual_vs_nav_btc'])
# ---- tvl_monthly ----
trows=[]; prev=None
for k in months:
    t=mb[k]['ts']; r=rate_at(t); bp=VAL[k]['btc_px']
    se=(S[k]['eth'] or 0)/1e8; so=(S[k]['op'] or 0)/1e8; ss=(S[k].get('scroll') or 0)/1e8; st=se+so+ss
    nav=st*r; tvl=nav*bp
    fl=FL.get(k,{})
    row={'month':k,'month_end_utc':lib.dt(t),'rate_btc_per_share':round(r,8),'shares_ethereum':round(se,4),'shares_optimism':round(so,4),'shares_scroll':round(ss,4),'shares_total':round(st,4),
         'nav_btc':round(nav,3),'btc_usd':round(bp),'tvl_usd':round(tvl),'eth_deposits_btc':round(fl.get('dep',0),3),'eth_withdrawals_btc':round(fl.get('wd',0),3),
         'eth_net_real_flow_btc':round(fl.get('dep',0)-fl.get('wd',0),3),'n_deposits_eth':fl.get('n_dep',0),'n_withdrawals_eth':fl.get('n_wd',0),
         'deposits_by_asset_btc':'; '.join(f"{a}:{fl.get('dep_'+a,0):.1f}" for a in ['eBTC','WBTC','LBTC','cbBTC'] if fl.get('dep_'+a,0)>0.05),
         'bridge_out_from_eth_btc':round(fl.get('wd_bridge',0),3),'bridge_in_to_eth_btc':round(fl.get('dep_bridge',0),3),
         'holders_ethereum':len(EH.get(k,{})),'holders_optimism':len(OH.get(k,{})) if OH.get(k) else ''}
    if prev:
        pst=prev['shares_total']; pr=prev['rate_btc_per_share']; ppx=prev['btc_usd']
        yld=(pst+st)/2*(r-pr); flow=(nav-prev['nav_btc'])-yld
        row.update({'net_flow_all_chains_btc':round(flow,3),'yield_btc':round(yld,4),'tvl_change_usd':round(tvl-prev['tvl_usd']),
                    'price_effect_usd':round(prev['nav_btc']*(bp-ppx)),'flow_effect_usd':round(flow*bp),'yield_effect_usd':round(yld*bp)})
    trows.append(row); prev=row
cols=['month','month_end_utc','rate_btc_per_share','shares_ethereum','shares_optimism','shares_scroll','shares_total','nav_btc','btc_usd','tvl_usd','net_flow_all_chains_btc','yield_btc','tvl_change_usd','price_effect_usd','flow_effect_usd','yield_effect_usd','eth_deposits_btc','eth_withdrawals_btc','eth_net_real_flow_btc','n_deposits_eth','n_withdrawals_eth','deposits_by_asset_btc','bridge_out_from_eth_btc','bridge_in_to_eth_btc','holders_ethereum','holders_optimism']
with open(os.path.join(OUT,'tvl_monthly.csv'),'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); [w.writerow({c:r.get(c,'') for c in cols}) for r in trows]
for r in trows: print(r['month'],r['nav_btc'],r['tvl_usd'],r.get('net_flow_all_chains_btc'),r.get('yield_btc'),r['holders_ethereum'],r['holders_optimism'])
