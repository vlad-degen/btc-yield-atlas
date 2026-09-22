# Daily borrow cost of the strategy's on-chain debt (Morpho per-market APY x debt; Aave/Spark per-reserve rate x debt), aggregated monthly
import json,datetime,collections,csv
R='raw/'
mp=json.load(open(R+'morpho_pos_history.json')); ma=json.load(open(R+'morpho_market_apy.json')); META=json.load(open(R+'morpho_market_meta.json'))
A=json.load(open(R+'aave_spark_daily.json')); AR=json.load(open(R+'aave_rates_daily.json'))
def dayof(x): return datetime.datetime.fromtimestamp(int(x),datetime.UTC).strftime('%Y-%m-%d')
px={}
for p in json.load(open(R+'btc_daily.json'))['coins']['coingecko:bitcoin']['prices']: px[dayof(p['timestamp'])]=p['price']
daily=collections.defaultdict(lambda:collections.defaultdict(float))  # day -> key -> value
for k,v in mp['markets'].items():
    meta=META[k]; ca,cd,la,ld,lltv=meta
    hs=v['hist']['data']['marketPosition']['historicalState']
    bu={dayof(p['x']):float(p['y'] or 0) for p in hs['borrowAssetsUsd']}
    apy={dayof(p['x']):float(p['y'] or 0) for p in (ma.get(k,{}).get('data',{}).get('marketById') or {}).get('historicalState',{}).get('borrowApy',[]) if p['y'] is not None}
    btccoll = ca in ('WBTC','cbBTC','LBTC','vbWBTC','triBTC')
    for d,debt in bu.items():
        if debt<100: continue
        rate=apy.get(d)
        if rate is None: continue
        leg='btc_coll_usd_debt' if (btccoll and la!='cbBTC') else ('btc_coll_btc_debt' if la=='cbBTC' else 'stable_coll')
        daily[d][leg+'_debt']+=debt; daily[d][leg+'_int']+=debt*rate/365
        daily[d]['venue:morpho_'+k.split(':')[0]+':'+ca+'/'+la]+=debt
for d,r in A.items():
    if d not in AR: continue
    rates=AR[d]
    for tok,res,dec in [('core_vdUSDC','core_USDC',0),('core_vdUSDT','core_USDT',0),('core_vdRLUSD','core_RLUSD',0),('core_vdUSDe','core_USDe',0),('core_vdUSDG','core_USDG',0),('spark_vdUSDS','spark_USDS',0),('spark_vdUSDT','spark_USDT',0)]:
        debt=r.get(tok) or 0
        if debt<100: continue
        rt=rates.get(res) or 0
        daily[d]['btc_coll_usd_debt_debt']+=debt; daily[d]['btc_coll_usd_debt_int']+=debt*rt/365
        daily[d]['venue:'+tok]+=debt
    cb=(r.get('core_vdcbBTC') or 0)
    if cb>0.01:
        p=px.get(d,0); daily[d]['btc_coll_btc_debt_debt']+=cb*p; daily[d]['btc_coll_btc_debt_int']+=cb*p*(rates.get('core_cbBTC') or 0)/365
json.dump(daily,open(R+'borrow_cost_daily.json','w'),indent=0)
mon=collections.defaultdict(lambda:collections.defaultdict(float))
for d,r in daily.items():
    m=d[:7]
    for k,v in r.items():
        if not k.startswith('venue:'): mon[m][k]+=v
    mon[m]['days']+=1
for m in sorted(mon):
    r=mon[m]; n=r['days']
    avg=r['btc_coll_usd_debt_debt']/max(1,n)
    ann=(r['btc_coll_usd_debt_int']/r['btc_coll_usd_debt_debt']*365) if r['btc_coll_usd_debt_debt'] else 0
    print(m,'USD debt vs BTC: avg $%.2fM (over days with debt), wAPR %.2f%%, interest $%.0f | stable-loop avg $%.2fM int $%.0f | BTC-debt avg $%.2fM int $%.0f'%(avg/1e6,100*ann,r['btc_coll_usd_debt_int'],r['stable_coll_debt']/max(1,n)/1e6,r['stable_coll_int'],r['btc_coll_btc_debt_debt']/max(1,n)/1e6,r['btc_coll_btc_debt_int']))
