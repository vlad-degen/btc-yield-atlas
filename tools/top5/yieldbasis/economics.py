# Monthly protocol economics: admin-fee revenue, veYB distributions, YB emissions (units and USD), TVL, cost per $ TVL
import json,collections,datetime,csv
from load import *
S=snaps()
def pr(n):
    v=list(json.load(open('../raw/price_%s.json'%n))['coins'].values())[0]['prices']
    return {datetime.datetime.fromtimestamp(x['timestamp'],datetime.UTC).strftime('%Y-%m-%d'):x['price'] for x in v}
yb=pr('ethereum_0x01791F726B4103694969820be083196cC7c045fF'); btc=pr('coingecko_bitcoin')
def ybp(d):
    if d in yb: return yb[d]
    ks=sorted(k for k in yb if k<=d); return yb[ks[-1]] if ks else None
g=json.load(open('../raw/api/gauge_snapshots.json'))['data']
em=collections.defaultdict(lambda: collections.defaultdict(float)); emu=collections.defaultdict(lambda: collections.defaultdict(float))
for r in g:
    d=day(r['bucketStart']); m=d[:7]; q=int(r['dailyYBMintedRaw'])/1e18
    grp='BTC' if 'WETH' not in NAMES[int(r['marketId'])] else 'ETH'
    em[m][grp]+=q; p=ybp(d); emu[m][grp]+=q*(p or 0)
# admin fees accrued: delta of (cumulative collected + pending) per market, USD
ME=['2025-09-24','2025-09-30','2025-10-31','2025-11-30','2025-12-31','2026-01-31','2026-02-28','2026-03-31','2026-04-30','2026-05-31','2026-06-30','2026-07-31','2026-08-31','2026-09-20']
adm=collections.defaultdict(lambda: collections.defaultdict(float))
for mid,s in S.items():
    grp='BTC' if 'WETH' not in NAMES[mid] else 'ETH'
    prev=0.0
    for d in ME:
        ks=[k for k in s if k<=d]
        if not ks: continue
        v=s[max(ks)]['admin_usd']+s[max(ks)]['pend_usd']
        adm[d[:7]][grp]+=v-prev; prev=v
# veYB distributions by epoch start month
fe=json.load(open('../raw/api/fee_epochs.json'))['data']
vd=collections.defaultdict(float)
for e in fe: vd[day(e['startTimestamp'])[:7]]+=int(e['epochRewardsUsd'])/1e18
# TVL: BTC markets from snapshots daily avg; protocol from DefiLlama daily avg
L=json.load(open('../raw/llama_protocol.json'))['tvl']
Ld=collections.defaultdict(list)
for x in L: Ld[day(x['date'])[:7]].append(x['totalLiquidityUSD'])
bt=collections.defaultdict(lambda: collections.defaultdict(float)); cnt=collections.defaultdict(set)
for mid,s in S.items():
    if 'WETH' in NAMES[mid]: continue
    for d,x in s.items(): bt[d[:7]][d]+=x['tot']*x['px']
rows=[]
for m in sorted(set(em)|set(adm)|set(Ld)):
    if m<'2025-09': continue
    btc_tvl=sum(bt[m].values())/len(bt[m]) if bt[m] else 0
    prot=sum(Ld[m])/len(Ld[m]) if Ld[m] else 0
    days=len(bt[m]) or 30
    r=dict(month=m,avg_tvl_usd_protocol_defillama=round(prot),avg_tvl_usd_btc_markets=round(btc_tvl),
       yb_emitted_btc_gauges=round(em[m]['BTC']),yb_emitted_eth_gauges=round(em[m]['ETH']),
       yb_emissions_usd_btc_gauges=round(emu[m]['BTC']),yb_emissions_usd_all=round(emu[m]['BTC']+emu[m]['ETH']),
       avg_yb_price=(round(sum(yb[d] for d in bt[m] if d in yb)/max(1,len([d for d in bt[m] if d in yb])),4) if any(d in yb for d in bt[m]) else None),
       admin_fee_accrued_usd_btc=round(adm[m]['BTC']),admin_fee_accrued_usd_all=round(adm[m]['BTC']+adm[m]['ETH']),
       veyb_distributed_usd=round(vd[m]),
       emission_cost_pct_btc_tvl_ann=round(emu[m]['BTC']/btc_tvl*365/days*100,2) if btc_tvl else None,
       admin_rev_pct_btc_tvl_ann=round(adm[m]['BTC']/btc_tvl*365/days*100,2) if btc_tvl else None)
    rows.append(r)
with open('../economics_monthly.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
tot=lambda k: sum(r[k] or 0 for r in rows)
print('TOTALS emissions USD all %.0f (BTC %.0f), YB emitted %.0f, admin fees %.0f (BTC %.0f), veYB distributed %.0f'%(tot('yb_emissions_usd_all'),tot('yb_emissions_usd_btc_gauges'),tot('yb_emitted_btc_gauges')+tot('yb_emitted_eth_gauges'),tot('admin_fee_accrued_usd_all'),tot('admin_fee_accrued_usd_btc'),tot('veyb_distributed_usd')))
for r in rows: print(r)
