"""-> ../tvl_weekly.csv  (weekly TVL, bgBTC and USD; on-chain snapshots + ETH supply events + Chainlink PoR + DefiLlama)"""
import json, csv, datetime
S=json.load(open('../raw/weekly_snaps.json'))
E=json.load(open('../raw/bgbtc_eth_supply_events.json'))
P=json.load(open('../raw/por_rounds.json'))
L=json.load(open('../raw/web/llama_protocol_bitget-bgbtc.json'))
def ts_of(s): return datetime.datetime.strptime(s[:19],'%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()
def eth_at(t):
    sup=pool=None
    for e in E:
        if ts_of(e['ts'])<=t: sup=e['supply']; pool=e['pool']
    return sup,pool
def por_at(t):
    v=None
    for r in P:
        if r['updatedAt']<=t: v=r['answer']
    return v
def llama_at(t):
    v=None
    for p in L['tvl']:
        if p['date']<=t+86400/2: v=p['totalLiquidityUSD']
    return v
rows=[]
for s in S:
    t=s['ts']; px=s['btc_usd']
    nav=s['v_units']*s['v_unit_price']
    ext=s['g_totalAssets']-s['g_aera_shares']*s['g_price']
    sup,pool=eth_at(t); por=por_at(t); ll=llama_at(t)
    rows.append(dict(date=s['date'],morph_block=s['block'],btc_usd_redstone=round(px,2),
        vault_collateral_bgbtc=round(s['aera_coll'],4),vault_nav_bgbtc=round(nav,4),vault_nav_usd=round(nav*px),
        vault_debt_usdc=round(s['aera_debt']),vault_ltv_pct=round(s['aera_debt']/(s['aera_coll']*px)*100,2) if s['aera_coll']>0.5 else '',
        gtusdc_tvl_usd=round(s['g_totalAssets']),gtusdc_owned_by_vault_usd=round(s['g_aera_shares']*s['g_price']),gtusdc_external_usd=round(ext),gtusdc_idle_usd=round(s['g_idle']),
        market_supply_usd=round(s['supply']),market_borrow_usd=round(s['borrow']),
        headline_tvl_usd=round(s['aera_coll']*px+s['g_totalAssets']),net_external_capital_usd=round(s['aera_coll']*px+ext),
        bgbtc_supply_morph=round(s['bgbtc_supply_morph'],4),bgbtc_supply_ethereum=sup,bgbtc_ccip_locked_eth=pool,por_reserves_btc=por,
        defillama_bitget_bgbtc_usd=round(ll) if ll and ll>1000 else 'n/a (DefiLlama tracked ~0 BTC before 19 Aug)'))
with open('../tvl_weekly.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
