# Staked-side principal in BTC per gauge share at month-end (archive eth_call): gauge.totalAssets()/totalSupply() * LT.pricePerShare()
import json
from load import *
from ybrpc import *
from markets import M
S=snaps(); idx={v['idx']:v for v in M.values()}
ME=['2025-11-30','2025-12-31','2026-01-31','2026-02-28','2026-03-31','2026-04-30','2026-05-24','2026-05-31','2026-06-30','2026-07-31','2026-08-31','2026-09-20']
out=[]
for mid in [0,1,2,3,4,5,7,8,9]:
    m=idx[mid]; s=S[mid]
    for d in [min(s)]+ME:
        if d not in s: continue
        b=s[d]['blk']
        ts=u(ec(m['staker'],'totalSupply()',block=b)); ta=u(ec(m['staker'],'totalAssets()',block=b))
        if not ts: continue
        v=ta/ts*s[d]['pps']
        out.append(dict(market=NAMES[mid],date=d,gauge_share_btc=round(v,6),gauge_share_redeem_btc=round(ta/ts*(s[d]['wd'] or 0),6)))
        print(out[-1])
json.dump(out,open('../raw/staked_principal.json','w'),indent=1)
