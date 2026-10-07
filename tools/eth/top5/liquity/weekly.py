"""Liquity ETH Carry (IPOR Fusion PlasmaVault): weekly convertToAssets(1 share = 1e20), totalAssets, totalSupply; wstETH benchmark.
Output: data/eth/top5/liquity/weekly.csv"""
import sys, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from weekly_lib import *
V='0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c'
rows=[]
for ts in weekly_grid(int(dt.datetime(2026,3,27,tzinfo=dt.timezone.utc).timestamp())):
    b=block_at(ts)
    c,u=call(V,'convertToAssets(uint256)',u256(10**20),b)
    ta,_=call(V,'totalAssets()',block=b)
    sup,_=call(V,'totalSupply()',block=b)
    w,_=call(WSTETH,'stEthPerToken()',block=b)
    rows.append({'date':dt.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d'),'block':b,'weth_per_share':c/1e18,'total_assets_weth':ta/1e18,
      'shares':sup/1e20,'wsteth_steth_per_token':w/1e18,'source':f'archive eth_call via {u}: vault.convertToAssets(1e20), totalAssets, totalSupply (20-decimal shares), wstETH.stEthPerToken'})
    print(rows[-1]['date'],b,rows[-1]['weth_per_share'],flush=True)
write_csv(ROOT/'data/eth/top5/liquity/weekly.csv',rows)
