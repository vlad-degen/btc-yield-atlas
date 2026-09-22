# Build positions.csv, yield_monthly.csv, liquidity_ladder.csv from the raw datasets
import json,csv,datetime
R='raw/'
P=80276.04   # Chainlink BTC/USD at block 26,018,582 (2026-09-20 12:00 UTC)
# ---------- positions.csv
pos=[]
def add(**k): pos.append(k)
snap='2026-09-20 12:00 UTC'
add(date=snap,venue='Morpho Blue cbBTC/USDT (0x4fe72543…)',chain='Ethereum',role='BTC collateral + dollar loan',collateral='cbBTC',collateral_amount=126.0002,collateral_usd=round(126.0002*P),debt_asset='USDT',debt_usd=5802800,ltv=round(5802800/(126.0002*P),4),lltv_or_lt=0.86,liq_price_usd=round(5802800/(126.0002*0.86)),source='RPC position() at block 26018582; oracle 0x9f98…34d2',note='daily borrow APY 2.97% (Morpho API 09-21); instantaneous 9.40% at API read 09-21')
add(date=snap,venue='Spark (SparkLend) cbBTC -> USDS',chain='Ethereum',role='BTC collateral + dollar loan',collateral='cbBTC (spcbBTC)',collateral_amount=113.416,collateral_usd=round(113.416*P),debt_asset='USDS',debt_usd=4955984,ltv=round(4955984/(113.416*P),4),lltv_or_lt=0.82,liq_price_usd=round(4955984/(113.416*0.82)),source='getUserAccountData + spcbBTC/vdUSDS balances at block 26018582',note='HF 1.507; USDS variable rate 3.93%')
add(date=snap,venue='Aave v3 Core',chain='Ethereum',role='idle collateral',collateral='WBTC (aEthWBTC)',collateral_amount=1.3643,collateral_usd=round(1.3643*P),debt_asset='',debt_usd=0,ltv=0,lltv_or_lt=0.78,liq_price_usd='',source='RPC at block 26018582',note='no debt')
add(date=snap,venue='TOTAL BTC posted vs dollar debt',chain='Ethereum',role='carry leg',collateral='cbBTC+WBTC',collateral_amount=240.7805,collateral_usd=round(240.7805*P),debt_asset='USDT+USDS',debt_usd=10758784,ltv=round(10758784/(240.7805*P),4),lltv_or_lt='',liq_price_usd='~53.3-53.6k',source='sum of above',note='LTV 52.0% at BTC $86,488 (09-22)')
lent=[('Euler "Hyperithm Earn cbBTC" (hyperEcbBTC; EVK ecbBTC-4 60.01 + ecbBTC-6 9.41)','Monad','BTC lent',69.4233,'cbBTC','RPC balanceOf/convertToAssets 2026-09-22 (no public Monad archive)','strategy owns ~100% of the Euler Earn vault; ecbBTC-4 lends only against eaHyperBTC-1 (Hyperithm Accountable vault) at 94% utilisation, borrow APR ~2.26%'),
      ('Morpho V2 "Hyperithm cbBTC Apex" (0xe09A…8Ea0)','Monad','BTC lent',35.0545,'cbBTC','RPC convertToAssets 2026-09-22','vault lends to mHyperBTC/cbBTC ($4.09M, 5.98%) and aHyperBTC/cbBTC ($3.11M); strategy = 42% of vault')]
for v,c,role,amt,a,src,note in lent:
    add(date='2026-09-22',venue=v,chain=c,role=role,collateral=a,collateral_amount=amt,collateral_usd=round(amt*P),debt_asset='',debt_usd=0,ltv='',lltv_or_lt='',liq_price_usd='',source=src,note=note)
usd=[('Morpho V2 "Hyperithm USDC Apex" (0x7899…F371)','Monad',3988156,'USDC','netAPY 7.10%; allocation 09-22: PT-USDat-14JAN2027/USDC $18.84M, aHYPER/USDC $18.48M (Hyperithm Delta Neutral Vault loopers), aHyperBTC/USDC $1.72M; API liquidity $0'),
     ('Morpho V2 "StableEarn" (gtusdtb, 0xb7Df…5c08)','Stable',5811455,'USDT0','netAPY 7.36%; lends to sthUSD/USDT0 (91-95% util); vault idle ~$5-11M'),
     ('Morpho V2 "Pendle Ecosystem USDC" (0x55C1…6f05)','Ethereum',992760,'USDC','netAPY 7.12%; lends to PT-reUSD/PT-sUSDS/PT-sUSDE/PT-USDG loops; vault liquidity $10.2M')]
for v,c,amt,a,note in usd:
    add(date='2026-09-21',venue=v,chain=c,role='borrowed dollars deployed',collateral=a,collateral_amount=amt,collateral_usd=amt,debt_asset='',debt_usd=0,ltv='',lltv_or_lt='',liq_price_usd='',source='Morpho API userByAddress 2026-09-21/22',note=note)
add(date='2026-09-21 22:07 UTC',venue='cex_1 (name withheld by Midas)',chain='CEX',role='residual CEX balance',collateral='n/a',collateral_amount='',collateral_usd=413683,debt_asset='',debt_usd=0,ltv='',lltv_or_lt='',liq_price_usd='',source='api-prod.midas.app/api/transparency?token=mHyperBTC',note='1.35% of NAV')
# PoR (1Token) CEX books
por=json.load(open(R+'por_table.json'))
for x in sorted(por,key=lambda r:r['created']):
    if not x['snapshot']: continue
    for k in x['liab']:
        if k=='total': continue
        a=x['assets'].get(k,0); l=-x['liab'].get(k,0)
        if l>0.001 or k.startswith('cex') or k.endswith('exch'):
            add(date=x['snapshot'].replace('T',' '),venue=f'{k} (1Token report inside Midas PoR attestation)',chain='CEX' if ('exch' in k or 'cex' in k) else 'on-chain',role='gross book',collateral='mixed (not disclosed)',collateral_amount='',collateral_usd=round(a*1e6),debt_asset='mixed',debt_usd=round(l*1e6),ltv=round(l/a,4) if a else '',lltv_or_lt='',liq_price_usd='',source='Midas Attestation Engine PoR, IPFS (raw/por/)',note='liabilities/assets of that venue line; 1Token coverage partial before 2026-08-10')
# month-end on-chain history from daily balance sheet
bs={r['date']:r for r in csv.DictReader(open(R+'balance_sheet_daily.csv'))}
for d in ['2025-12-01','2026-01-01','2026-02-01','2026-02-05','2026-03-01','2026-04-01','2026-04-18','2026-05-01','2026-06-01','2026-07-01','2026-08-01','2026-09-01','2026-09-21']:
    r=bs[d]; f=lambda k: float(r.get(k) or 0); p=f('btc_usd')
    for lab,ck,dk,ch in [('Katana Morpho vbWBTC/vbUSDC+vbUSDT','katana_morpho_btc_coll','katana_morpho_usd_debt','Katana'),('Ethereum Morpho (BTC collateral markets)','eth_morpho_btc_coll','eth_morpho_usd_debt','Ethereum'),('Aave v3 Core/Horizon','aave_btc_coll','aave_debt_usd','Ethereum'),('Spark','spark_btc_coll','spark_debt_usd','Ethereum'),('Monad Morpho (BTC collateral -> USD)','monad_morpho_btc_coll','monad_morpho_usd_debt','Monad'),('Tempo Morpho cbBTC/pathUSD','tempo_morpho_btc_coll','tempo_morpho_usd_debt','Tempo')]:
        c=f(ck); dbt=f(dk)
        if c>0.5 or dbt>1000:
            add(date=d+' 00:00 UTC',venue=lab,chain=ch,role='BTC collateral + dollar loan',collateral='BTC wrappers',collateral_amount=round(c,3),collateral_usd=round(c*p),debt_asset='USD stables',debt_usd=round(dbt),ltv=round(dbt/(c*p),4) if c>0.5 else '',lltv_or_lt='',liq_price_usd='',source='Morpho API position history / Aave-Spark archive reads (raw/balance_sheet_daily.csv)',note='BTC price DefiLlama daily %.0f; Monad lines also carry BTC-denominated debt %.1f cbBTC'%(p,f('monad_morpho_btc_debt')) if 'Monad' in lab else 'BTC price DefiLlama daily %.0f'%p)
    add(date=d+' 00:00 UTC',venue='TOTAL identified on-chain',chain='all',role='summary',collateral='BTC posted',collateral_amount=round(f('btc_posted'),3),collateral_usd=round(f('btc_posted')*p),debt_asset='USD debt vs BTC',debt_usd=round(f('usd_debt_vs_btc')),ltv=round(float(r['ltv_onchain']),4) if r['ltv_onchain'] else '',lltv_or_lt='',liq_price_usd='',source='raw/balance_sheet_daily.csv',note='NAV %.1f BTC; BTC lent %.1f; USD vaults $%.2fM; stable-collateral loops $%.2fM debt; unidentified (CEX/other) %.1f BTC-eq'%(f('nav_btc'),f('btc_lent_btc'),f('usd_vaults_usd')/1e6,f('stable_coll_debt_usd')/1e6,f('unidentified_btc')))
with open('positions.csv','w',newline='') as fo:
    w=csv.DictWriter(fo,fieldnames=list(pos[0].keys())); w.writeheader(); w.writerows(pos)
# ---------- yield_monthly.csv
Y=json.load(open(R+'yield_monthly_full.json'))
notes={'2025-10':'oracle initialised 10-15 at 1.0; no supply until 11-24',
 '2025-11':'first 25 mHyperBTC minted 11-24 (one holder); first NAV step 11-26',
 '2025-12':'Monad WBTC/AUSD + Katana vbWBTC loans; Steakhouse AUSD / Hyperithm USDC vaults; 3BTC LP on Monad (WMON)',
 '2026-01':'Katana is main BTC-collateral venue (borrow APR <1%); stUSDS loops start; big mints (0xD338 150.5 on 01-22)',
 '2026-02':'BTC -35% (Jan 15 -> Feb 5); on-chain debt cut $19.9M -> $11.3M (02-02..02-06); no liquidation',
 '2026-03':'Monad launch 03-19; 250-300 BTC parked in Hyperithm cbBTC Apex (Monad) earning ~0-1% + WMON; incentives 61% of NAV gain',
 '2026-04':'Apr 18-20 pause; Katana unwound 04-21; 0xD338 redeems 147.3 on 04-28 (paid in ~11 h); WMON incentives 67% of gain',
 '2026-05':'Monad WBTC->cbBTC BTC loops (debt in cbBTC) unwound 05-13; incentives ~66% of gain',
 '2026-06':'book mostly on Binance (PoR: liabilities $29.7-36.3M vs assets $52.7-56.7M); NAV -0.025% on 06-02; BTC -19% in June',
 '2026-07':'CEX leverage removed by 07-06; NAV -0.059% on 07-13; small Aave USDC loan at ~11-14% (negative carry)',
 '2026-08':'re-levered on-chain from 08-19 (Aave, Morpho RLUSD, Monad cbBTC/USDC); RLUSD $5.0M parked at an unidentified venue (cex_2)',
 '2026-09':'to 09-21: migrated to Morpho cbBTC/USDT + Spark USDS; dollars to Hyperithm USDC Apex (Monad), StableEarn (Stable), Pendle USDC'}
with open('yield_monthly.csv','w',newline='') as fo:
    w=csv.writer(fo)
    w.writerow(['month','realized_apy','borrow_cost','notes','nav_start','nav_end','days','realized_return','avg_supply','nav_gain_btc','nav_gain_usd','avg_usd_debt_onchain','borrow_interest_usd','stable_loop_interest_usd','usd_vault_income_usd','btc_vault_income_usd','incentives_usd','incentives_share_of_gain'])
    for r in Y:
        w.writerow([r['month'],round(r['realized_apy'],5),round(r['borrow_cost'],5) if r['borrow_cost'] else '',notes.get(r['month'],''),r['nav_start'],r['nav_end'],r['days'],round(r['realized_return'],6),round(r['avg_supply'],2),round(r['nav_gain_btc'],3),round(r['nav_gain_usd']),round(r['avg_usd_debt']),round(r['borrow_interest_usd']),round(r['stable_loop_interest_usd']),round(r['usd_vault_income']),round(r['btc_vault_income_usd']),round(r['incentives_usd']),round(r['incentives_share_of_gain'],3) if r['incentives_share_of_gain'] else ''])
# ---------- liquidity_ladder.csv
L=[
 ('1 same-block','Flash-loan deleverage: withdraw cbBTC collateral, swap to USDT/USDS, repay (Morpho/Spark)','Ethereum',10758784,'','seconds (atomic)','Converts BTC to USD: repays debt but cuts BTC exposure unless re-hedged; needs DEX depth for ~134 BTC; manager-initiated, Midas co-sign','RPC positions'),
 ('1 same-block','Pendle Ecosystem USDC (Morpho V2) withdraw','Ethereum',992760,'','seconds','vault liquidity $10.24M','Morpho API'),
 ('1 same-block','Strategy wallet balances (ETH)','Ethereum',310783,'','seconds','composition not disclosed','Midas transparency API'),
 ('2 minutes-hours','StableEarn (gtusdtb) withdraw on Stable + USDT0 OFT bridge to Ethereum','Stable -> Ethereum',5811455,'','minutes (withdraw) + LayerZero delivery','vault idle $10.9M then $5.1M in two 09-22 reads (strategy share $5.81M); bridge risk; pausable by Midas whitelist policy','Morpho API; USDT0 adapter 0x6C96…1dee flows'),
 ('3 hours-days','Hyperithm USDC Apex (Monad) withdraw + CCTP to Ethereum','Monad -> Ethereum',3988156,'','depends on borrower repayments','API liquidity $0: allocated to PT-USDat/USDC, aHYPER/USDC and aHyperBTC/USDC (89-91% util); strategy is ~10% of the $39M vault','Morpho API'),
 ('3 hours-days','cex_1 balance','CEX',413683,'','hours (withdrawal)','exchange name withheld','Midas transparency API'),
 ('BTC side','Euler Hyperithm Earn cbBTC (69.42 cbBTC)','Monad','',69.4233,'partly same-block','only ~14.4 cbBTC cash (ecbBTC-4 cash 4.95 + ecbBTC-6 9.41); rest lent to aHyperBTC loopers at 94% util','RPC'),
 ('BTC side','Hyperithm cbBTC Apex (35.05 cbBTC)','Monad','',35.0545,'hours-days','API liquidity $0; markets mHyperBTC/cbBTC 92% and aHyperBTC/cbBTC 93% utilised','Morpho API'),
 ('memo','Debt to repay','Ethereum',-10758784,'','','Morpho USDT $5.80M + Spark USDS $4.96M; liquidation ~ $53.3k-53.6k BTC (-33% from $80.3k)','RPC'),
 ('memo','Holder redemptions: instant capacity / daily limit','Ethereum','',1.74,'instant','instant fee 0.3%, holdback up to 50%; redemption vault instantDailyLimit 15 mHyperBTC; standard: 1 business day, gate 15%/day; biggest exit (147.3) paid in ~11 h','Final Terms 17-Jul-2026; RPC vault params; product page'),
]
with open('liquidity_ladder.csv','w',newline='') as fo:
    w=csv.writer(fo); w.writerow(['tier','source','chain','amount_usd','amount_btc','time_to_cash','constraint','data_source']); w.writerows(L)
print('ok',len(pos))
