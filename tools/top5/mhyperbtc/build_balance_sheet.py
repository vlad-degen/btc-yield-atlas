# Daily identified balance sheet of the mHyperBTC strategy (on-chain venues + PoR CEX lines) vs NAV
import json,datetime,collections,csv
R='raw/'
# --- BTC price (DefiLlama daily; last print per UTC date)
px={}
for p in json.load(open(R+'btc_daily.json'))['coins']['coingecko:bitcoin']['prices']:
    px[datetime.datetime.fromtimestamp(p['timestamp'],datetime.UTC).strftime('%Y-%m-%d')]=p['price']
def price(day):
    d=datetime.date.fromisoformat(day)
    for i in range(5):
        k=(d-datetime.timedelta(days=i)).isoformat()
        if k in px: return px[k]
# --- NAV / supply (Midas tvl snapshots, 23:00 UTC of previous day ~ start of day)
nav={}
for x in json.load(open(R+'tvl_snapshots.json')):
    day=(datetime.datetime.fromisoformat(x['timestamp'].replace('Z','+00:00'))+datetime.timedelta(hours=1)).strftime('%Y-%m-%d')
    nav[day]=x
BTCSYM={'WBTC','cbBTC','LBTC','vbWBTC'}
DEC={'WBTC':8,'cbBTC':8,'LBTC':8,'vbWBTC':8,'triBTC':18,'stUSDS':18,'mHyperBTC':18,'aHYPER':6}
LDEC={'USDC':6,'USDT':6,'EURC':6,'AUSD':6,'pathUSD':6,'vbUSDC':6,'vbUSDT':6,'USDS':18,'RLUSD':18,'EURCV':18,'WETH':18,'cbBTC':8}
mp=json.load(open(R+'morpho_pos_history.json'))
META=json.load(open(R+'morpho_market_meta.json'))
M=collections.defaultdict(lambda:collections.defaultdict(float))
def dayof(x): return datetime.datetime.fromtimestamp(x,datetime.UTC).strftime('%Y-%m-%d')
for k,v in mp['markets'].items():
    cid=k.split(':')[0]; m=v['market']; ca=(m['collateralAsset'] or {}).get('symbol'); la=m['loanAsset']['symbol']
    hs=v['hist']['data']['marketPosition']['historicalState']
    col={p['x']:float(p['y'] or 0) for p in hs['collateral']}; colu={p['x']:float(p['y'] or 0) for p in hs['collateralUsd']}
    ba={p['x']:float(p['y'] or 0) for p in hs['borrowAssets']}; bu={p['x']:float(p['y'] or 0) for p in hs['borrowAssetsUsd']}; su={p['x']:float(p['y'] or 0) for p in hs['supplyAssetsUsd']}
    for x in col:
        r=M[dayof(x)]; c=col[x]/10**META[k][1]; ldec=META[k][3]
        if c<=0 and bu.get(x,0)<1 and su.get(x,0)<1: continue
        tag={'1':'eth','143':'monad','747474':'katana','4217':'tempo'}.get(cid,cid)
        if ca in BTCSYM or ca=='triBTC':
            r[f'{tag}_morpho_btc_coll']+=c
            if la=='cbBTC': r[f'{tag}_morpho_btc_debt']+=ba.get(x,0)/10**ldec
            else: r[f'{tag}_morpho_usd_debt']+=bu.get(x,0)
        else:
            r['stable_coll_usd']+=colu.get(x,0); r['stable_coll_debt_usd']+=bu.get(x,0)
        r['morpho_mkt_supply_usd']+=su.get(x,0)
for k,v in list(mp['v2'].items())+list(mp['v1'].items()):
    name=v['vault']['name']; h=v['hist']['data']
    h=(h.get('vaultV2PositionByAddress') or {}).get('history') if 'vaultV2PositionByAddress' in h else (h.get('vaultPosition') or {}).get('historicalState')
    for p in (h or {}).get('assetsUsd') or []:
        y=float(p['y'] or 0)
        if y<100: continue
        r=M[dayof(p['x'])]
        if 'cbBTC' in name: r['btc_vault_usd']+=y; r['v:'+name]=y
        elif 'ETH' in name: r['eth_vault_usd']+=y
        else: r['usd_vault_usd']+=y; r['v:'+name]=y
A=json.load(open(R+'aave_spark_daily.json'))
MON=json.load(open(R+'monad_daily_balances.json'))
POR=json.load(open(R+'por_table.json'))
por={}
for x in POR:
    if x['snapshot']: por[x['snapshot'][:10]]=x
rows=[]
day=datetime.date(2025,11,20)
while day<=datetime.date(2026,9,21):
    d=day.isoformat(); p=price(d); m=M.get(d,{}); a=A.get(d,{}); mo=MON.get(d,{}); n=nav.get(d)
    r={'date':d,'btc_usd':round(p,0)}
    if n: r.update(nav_btc=n['tvl'],supply=n['supply'],nav_price=n['price'])
    # BTC posted as collateral against dollar loans
    eth_aave_btc=sum((a.get(k) or 0) for k in ('core_aWBTC','core_acbBTC','core_aLBTC'))
    spark_btc=sum((a.get(k) or 0) for k in ('spark_acbBTC','spark_aWBTC'))
    core=a.get('aave_core') or {}; spk=a.get('spark') or {}; hor=a.get('aave_horizon') or {}; pri=a.get('aave_prime') or {}
    r['eth_morpho_btc_coll']=m.get('eth_morpho_btc_coll',0); r['eth_morpho_usd_debt']=m.get('eth_morpho_usd_debt',0)
    r['aave_btc_coll']=eth_aave_btc; r['aave_debt_usd']=core.get('debt_usd',0)+hor.get('debt_usd',0)+pri.get('debt_usd',0)
    r['aave_other_coll_usd']=max(0,core.get('coll_usd',0)+hor.get('coll_usd',0)+pri.get('coll_usd',0)-eth_aave_btc*p)
    r['spark_btc_coll']=spark_btc; r['spark_debt_usd']=spk.get('debt_usd',0)
    r['monad_morpho_btc_coll']=m.get('monad_morpho_btc_coll',0); r['monad_morpho_usd_debt']=m.get('monad_morpho_usd_debt',0); r['monad_morpho_btc_debt']=m.get('monad_morpho_btc_debt',0)
    r['katana_morpho_btc_coll']=m.get('katana_morpho_btc_coll',0); r['katana_morpho_usd_debt']=m.get('katana_morpho_usd_debt',0)
    r['tempo_morpho_btc_coll']=m.get('tempo_morpho_btc_coll',0); r['tempo_morpho_usd_debt']=m.get('tempo_morpho_usd_debt',0)
    r['stable_coll_usd']=m.get('stable_coll_usd',0); r['stable_coll_debt_usd']=m.get('stable_coll_debt_usd',0)
    r['usd_vaults_usd']=m.get('usd_vault_usd',0)+m.get('morpho_mkt_supply_usd',0)
    r['btc_lent_btc']=m.get('btc_vault_usd',0)/p+mo.get('hyperEcbBTC',0)+mo.get('aMoncbBTC',0)
    r['btc_lp_wallet_btc']=sum(mo.get(k,0) for k in ('WBTC','cbBTC','LBTC','BTC.b','3BTC_LP','triBTC'))+sum((a.get(k) or 0) for k in ('w_WBTC','w_cbBTC','w_LBTC'))
    r['wallet_usd']=sum((a.get(k) or 0) for k in ('w_USDC','w_USDT','w_USDS'))+sum(mo.get(k,0) for k in ('USDC','AUSD','USDT0'))
    btc_posted=r['eth_morpho_btc_coll']+eth_aave_btc+spark_btc+r['monad_morpho_btc_coll']+r['katana_morpho_btc_coll']+r['tempo_morpho_btc_coll']
    usd_debt_btc=r['eth_morpho_usd_debt']+r['aave_debt_usd']+r['spark_debt_usd']+r['monad_morpho_usd_debt']+r['katana_morpho_usd_debt']+r['tempo_morpho_usd_debt']
    r['btc_posted']=btc_posted; r['usd_debt_vs_btc']=usd_debt_btc
    r['ltv_onchain']=usd_debt_btc/(btc_posted*p) if btc_posted>0.5 else None
    assets_btc=btc_posted+r['btc_lent_btc']+r['btc_lp_wallet_btc']+(r['aave_other_coll_usd']+r['stable_coll_usd']+r['usd_vaults_usd']+r['wallet_usd'])/p
    liab_btc=(usd_debt_btc+r['stable_coll_debt_usd'])/p+r['monad_morpho_btc_debt']
    r['onchain_assets_btc']=assets_btc; r['onchain_liab_btc']=liab_btc; r['onchain_equity_btc']=assets_btc-liab_btc
    if n and n['tvl']>0: r['unidentified_btc']=n['tvl']-(assets_btc-liab_btc)
    rows.append(r); day+=datetime.timedelta(days=1)
keys=list(rows[-1].keys())
for r in rows:
    for k in r: 
        if k not in keys: keys.append(k)
with open(R+'balance_sheet_daily.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys); w.writeheader()
    for r in rows: w.writerow({k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items()})
for r in rows:
    if r['date'][8:] in ('01','15') or r['date']=='2026-09-21':
        print(r['date'],'NAV %.1f'%r.get('nav_btc',0),'posted %.1f'%r['btc_posted'],'debt $%.2fM'%(r['usd_debt_vs_btc']/1e6),'LTV %s'%(('%.0f%%'%(100*r['ltv_onchain'])) if r['ltv_onchain'] else '-'),
              'lent %.1f'%r['btc_lent_btc'],'lp/wal %.1f'%r['btc_lp_wallet_btc'],'usdVaults $%.2fM'%(r['usd_vaults_usd']/1e6),'stableLoop $%.1fM/%.1fM'%(r['stable_coll_usd']/1e6,r['stable_coll_debt_usd']/1e6),
              'eq %.1f'%r['onchain_equity_btc'],'unident %.1f'%r.get('unidentified_btc',0))
