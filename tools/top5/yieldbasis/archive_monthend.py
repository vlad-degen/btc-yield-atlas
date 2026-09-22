# Archive eth_call at month-end sample blocks (from API snapshot sampleBlockNumber) to verify PPS and read debt/rate/allocation/staked/watermark
import json
from load import *
from ybrpc import *
from markets import M
S=snaps()
idx={v['idx']:v for v in M.values()}
ME=['2025-09-30','2025-10-31','2025-11-30','2025-12-31','2026-01-31','2026-02-28','2026-03-31','2026-04-30','2026-05-31','2026-06-30','2026-07-31','2026-08-31','2026-09-20']
out=[]
for mid in range(11):
    m=idx[mid]
    days=sorted(S[mid]); first=days[0]
    for me in [first]+ME:
        if me not in S[mid]: continue
        b=S[mid][me]['blk']
        r=dict(market=NAMES[mid],date=me,block=b)
        r['pps']=u(ec(m['lt'],'pricePerShare()',block=b))/1e18
        r['supply']=u(ec(m['lt'],'totalSupply()',block=b))/1e18
        liq=words(ec(m['lt'],'liquidity()',block=b))
        adm=liq[0]-(1<<256) if liq[0]>=(1<<255) else liq[0]
        r.update(liq_admin=adm/1e18,liq_total=liq[1]/1e18,ideal_staked=liq[2]/1e18,staked=liq[3]/1e18)
        r['staker_bal']=u(ec(m['lt'],'balanceOf(address)',ea(m['staker']),block=b))/1e18
        r['alloc']=u(ec(m['lt'],'stablecoin_allocation()',block=b))/1e18
        r['debt']=u(ec(m['amm'],'get_debt()',block=b))/1e18
        r['rate_apr']=u(ec(m['amm'],'rate()',block=b))*365*86400/1e18
        r['amm_fee']=u(ec(m['amm'],'fee()',block=b))/1e18
        r['max_debt']=u(ec(m['amm'],'max_debt()',block=b))/1e18
        r['ps']=u(ec(m['pool'],'price_scale()',block=b))/1e18
        r['po']=u(ec(m['pool'],'price_oracle()',block=b))/1e18
        r['vp']=u(ec(m['pool'],'virtual_price()',block=b))/1e18
        try: r['xcp_profit']=u(ec(m['pool'],'xcp_profit()',block=b))/1e18
        except Exception: r['xcp_profit']=None
        out.append(r); print(r)
json.dump(out,open('../raw/archive_monthend.json','w'),indent=1)
