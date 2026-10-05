"""Read-only month-end YieldBasis carry-book verification; no broadcasting."""
import sys,json,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/eth'))
import strategy_universe_deep_capture as c
c.RAW=ROOT/'raw/eth/parity-sweep-2026-10-05'
pool=c.CONTRACTS['yb_weth']
old=json.loads((ROOT/'data/eth/carry_category_candidates.json').read_text())
blocks=sorted({(r['timestamp'],r['block']) for r in old['history_rpc_records']})
rows=[]
for ts,b in blocks:
 rows.append({'label':f'yb_{ts}_code','timestamp':ts,'block':b,'method':'eth_getCode','params':[pool,hex(b)]})
 for sig in ['updated_balances()','pricePerShare()']:
  r=c.call(f'yb_{ts}_{sig}',pool,sig,tag=hex(b));r.update(timestamp=ts,block=b);rows.append(r)
for sig in ['admin()','minimum_admin_fee()']:
 rows.append(c.call('yb_T_'+sig,pool,sig))
c.rpc('yb_monthly_frozen',rows)
