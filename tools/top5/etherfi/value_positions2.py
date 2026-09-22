# Full month-end balance sheet: Ethereum vault + ITB managers + Morpho + off-Ethereum (Berachain/Corn in-flight, Optimism vault)
import lib,json,bisect
P=lib.load('positions_raw.json'); S=lib.load('supply_monthly.json'); mb=lib.load('month_blocks.json')
ITB=lib.load('itb_positions.json'); OPH=lib.load('op_vault_holdings.json'); SCH=lib.load('scroll_vault_holdings.json')
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
UDEBT={'variableDebtEthUSDC':'aave:USDC','variableDebtEthUSDT':'aave:USDT','variableDebtPYUSD':'spark:PYUSD','variableDebtUSDC':'spark:USDC'}
OFFCHAIN={'2025-04':{'Berachain eBTC (LZ, 26-28 Apr -> 16 May)':100.0011},
          '2025-06':{'Corn BTCN+LBTC (OFT 2-3 Jun -> 4-20 Nov)':150.0015},'2025-07':{'Corn BTCN+LBTC (OFT 2-3 Jun -> 4-20 Nov)':150.0015},
          '2025-08':{'Corn BTCN+LBTC (OFT 2-3 Jun -> 4-20 Nov)':150.0015},'2025-09':{'Corn BTCN+LBTC (OFT 2-3 Jun -> 4-20 Nov)':150.0015},
          '2025-10':{'Corn BTCN+LBTC (OFT 2-3 Jun -> 4-20 Nov)':150.0015},
          '2025-11':{'tacBTC shares in tacBTC withdraw queue (req 16 Nov, solved 10-17 Dec)':38.99}}
rows=[]
for k,p in P.items():
    t=mb[k]['ts']; bp=btc_px(t); rl=p['rate_lbtc'] or 1; re=p['rate_ebtc'] or 1
    b=p['bals']; get=lambda s:b.get(s,{}).get('amt',0)
    btc={}; coll={}; debt={}; depl={}; idle_usd={}
    def addb(key,val):
        if val and abs(val)>1e-6: btc[key]=btc.get(key,0)+val
    for s in BTC1: addb(s,get(s))
    for s in LB: addb(s,get(s)*rl)
    for s in EB: addb(s,get(s)*re)
    for s in PT: addb(s,get(s))
    for s in B4626: addb(s,b.get(s,{}).get('assets') or 0)
    btc_debt=get('variableDebtEthWBTC')
    # collateral posted (for LTV)
    for s,venue in [('aEthWBTC','aave'),('aEthcbBTC','aave'),('aEthLBTC','aave'),('aEtheBTC','aave'),('spWBTC','spark'),('spcbBTC','spark'),('spLBTC','spark')]:
        v=get(s)*(rl if 'LBTC' in s else re if 'eBTC' in s else 1)
        if v>1e-3: coll[venue]=coll.get(venue,0)+v
    usd={}
    for s in USD1:
        if get(s): usd[s]=get(s)
    for s in U4626:
        if b.get(s,{}).get('assets'): usd[s]=b[s]['assets']
    if get('stUSR'): usd['stUSR']=get('stUSR')
    if p.get('convex_lp'): usd['convexLP_USDC/fxUSD']=p['convex_lp']*(p['lp_vp'] or 1)
    if get('USDCfxUSD'): usd['USDCfxUSD']=get('USDCfxUSD')*1.0
    for s,lab in UDEBT.items():
        if get(s)>1: debt[lab]=debt.get(lab,0)+get(s)
    for m,v in p['morpho'].items():
        c,l=m.split('/')
        if v['collateral']>1e-3:
            mult=rl if c=='LBTC' else re if c=='eBTC' else 1
            addb('morpho:'+c,v['collateral']*mult); coll['morpho']=coll.get('morpho',0)+v['collateral']*mult
        if l=='WBTC': btc_debt+=v['debt']
        elif v['debt']>1: debt['morpho:'+l]=debt.get('morpho:'+l,0)+v['debt']
    # ITB
    it=ITB.get(k,{}).get('agg',{})
    for s,v in it.items():
        if s in ('aEtheBTC','eBTC'): addb('ITB:'+s,v*re)
        elif s in ('spLBTC','LBTC'): addb('ITB:'+s,v*rl)
        elif s=='variableDebtEthRLUSD': debt['ITB aave:RLUSD']=v
        elif s=='variableDebtPYUSD': debt['ITB spark:PYUSD']=v
        elif s.endswith('->assets'): usd['ITB:'+s.replace('->assets','')]=v
        elif s in ('RLUSD','PYUSD'): usd['ITB:'+s]=v
    if it.get('aEtheBTC'): coll['ITB-aave']=coll.get('ITB-aave',0)+it['aEtheBTC']*re
    if it.get('spLBTC'): coll['ITB-spark']=coll.get('ITB-spark',0)+it['spLBTC']*rl
    # off-Ethereum
    for lab,v in OFFCHAIN.get(k,{}).items(): addb('offchain:'+lab,v)
    oph=OPH.get(k,{})
    if oph.get('eBTC') or oph.get('WBTC'):
        addb('OP-vault:eBTC',oph.get('eBTC',0)*re); addb('OP-vault:WBTC',oph.get('WBTC',0))
    if oph.get('USDC'): usd['OP-vault:USDC']=oph['USDC']
    sch=SCH.get(k,{})
    if sch.get('eBTC') or sch.get('WBTC'):
        addb('Scroll-vault:eBTC',sch.get('eBTC',0)*re); addb('Scroll-vault:WBTC',sch.get('WBTC',0))
    if k=='2026-07': usd['OP:liquidRWA (1.75M USDC via CCTP 21 Jul; est. value)']=1750000*(1.761357/1.75)**(10/37)
    btc_assets=sum(btc.values()); usd_a=sum(usd.values()); usd_d=sum(debt.values())
    net=btc_assets-btc_debt+(usd_a-usd_d)/bp
    sup=((S[k]['eth'] or 0)+(S[k]['op'] or 0)+(S[k].get('scroll') or 0))/1e8; r=rate_at(t); nav=sup*r
    coll_btc=sum(coll.values())
    ltv=(usd_d/bp)/coll_btc if coll_btc>0 and usd_d>1000 else None
    rows.append(dict(month=k,ts=t,btc_px=bp,rate=r,shares_eth=(S[k]['eth'] or 0)/1e8,shares_op=(S[k]['op'] or 0)/1e8,shares_scroll=(S[k].get('scroll') or 0)/1e8,nav_btc=nav,
        btc_assets=btc_assets,btc_debt=btc_debt,usd_assets=usd_a,usd_debt=usd_d,net_btc=net,residual_btc=nav-net,
        coll_posted_btc=coll_btc,ltv=ltv,btc=btc,usd=usd,debt=debt,coll=coll,acct=p['acct'],itb_acct=ITB.get(k,{}).get('acct',{})))
    print(f"{k:10s} NAV {nav:7.2f} | btcA {btc_assets:7.2f} btcD {btc_debt:5.2f} usdA {usd_a/1e6:6.2f}M usdD {usd_d/1e6:6.2f}M | net {net:7.2f} resid {nav-net:7.2f} ({(nav-net)/nav*100 if nav else 0:+.1f}%) coll {coll_btc:6.1f} ltv {ltv and round(ltv*100,1)}")
lib.save('valuation_monthly2.json',rows)
