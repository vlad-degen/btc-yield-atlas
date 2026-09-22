import lib,csv,json,bisect,os
rows=list(csv.DictReader(open('../tvl_monthly.csv')))
Y=list(csv.DictReader(open('../yield_monthly.csv')))
px=json.load(open(lib.RAW+'/btc_px.json')); pts=[p[0] for p in px]
def P(ts): return px[max(bisect.bisect_right(pts,ts)-1,0)][1]
# yield to depositors
yb=sum(float(r['yield_btc'] or 0) for r in rows); yu=sum(float(r['yield_effect_usd'] or 0) for r in rows)
print('cumulative net yield to depositors: %.2f BTC, $%.0f (valued at month-end prices)'%(yb,yu))
# fee accrual theoretical: fee_bps_avg * avg_nav * days/365
acc_btc=0; acc_usd=0
mb=lib.load('month_blocks.json')
for y in Y:
    if not y['platform_fee_bps_avg'] or not y['avg_nav_btc']: continue
    k=y['month'] if not y['month'].startswith('2026-09') else '2026-09-20'
    idx=[r['month'] for r in rows].index(k); days=(mb[k]['ts']-mb[rows[idx-1]['month']]['ts'])/86400
    f=float(y['platform_fee_bps_avg'])/1e4*float(y['avg_nav_btc'])*days/365
    acc_btc+=f; acc_usd+=f*float(rows[idx]['btc_usd'])
print('theoretical platform-fee accrual: %.3f BTC ($%.0f)'%(acc_btc,acc_usd))
# claimed
acc=lib.load('acc_logs_rpc.json'); T=lib.topic('FeesClaimed(address,uint256)')
tot=0; totu=0; lst=[]
for l in acc:
    if l['topics'][0]!=T: continue
    b=int(l['blockNumber'],16); amt=int(l['data'],16)/1e8
    ts=int(lib.rpc('eth_getBlockByNumber',[hex(b),False])['timestamp'],16)
    tok={'2260fac5':'WBTC','8236a870':'LBTC','cbb7c000':'cbBTC'}[l['topics'][1][26:34]]
    lst.append((lib.dt(ts),tok,round(amt,4),round(amt*P(ts)))); tot+=amt; totu+=amt*P(ts)
for x in lst: print(x)
print('claimed fees: %.4f BTC ($%.0f)'%(tot,totu))
# incentives
rtv=lib.load('reward_token_values.json')['tot']
rc=lib.load('reward_claims.json')
merkl={}
for r in rc:
    if r['token'] in ('RLUSD','PYUSD'): merkl[r['user'][:10]+'_'+r['token']]=merkl.get(r['user'][:10]+'_'+r['token'],0)+r['amount']
print('ETHFI/MORPHO/CRV/FXN USD',rtv); print('Merkl stable rewards',merkl, sum(merkl.values()))
json.dump({'yield_btc':yb,'yield_usd':yu,'fee_accrual_btc':acc_btc,'fee_accrual_usd':acc_usd,'fees_claimed':lst,'fees_claimed_btc':tot,'fees_claimed_usd':totu,'token_rewards_usd':rtv,'merkl':merkl},open(lib.RAW+'/economics.json','w'),indent=1)
