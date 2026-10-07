"""Liquity ETH Carry: daily share price, assets and supply 2 to 31 Mar 2026 (test phase, whitelist-only).
Output: data/eth/top5/liquity/march_daily.csv"""
import sys, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from weekly_lib import *
V='0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c'
rows=[]
for d in range(2,32):
    ts=int(dt.datetime(2026,3,d,23,59,59,tzinfo=dt.timezone.utc).timestamp()); b=block_at(ts)
    c,u=call(V,'convertToAssets(uint256)',u256(10**20),b); ta,_=call(V,'totalAssets()',block=b); s,_=call(V,'totalSupply()',block=b)
    rows.append({'date':f'2026-03-{d:02d}','block':b,'weth_per_share':c/1e18,'total_assets_weth':ta/1e18,'shares':s/1e20,
      'source':f'archive eth_call via {u}: convertToAssets(1e20), totalAssets, totalSupply at last block of the day'})
write_csv(ROOT/'data/eth/top5/liquity/march_daily.csv',rows)
