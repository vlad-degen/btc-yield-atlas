"""Avant savETH: weekly convertToAssets (avETH per savETH), savETH totalAssets, avETH supply; wstETH benchmark.
Output: data/eth/top5/avant/weekly.csv"""
import sys, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from weekly_lib import *
S='0xda06ee2dacf9245aa80072a4407debdea0d7e341'; A='0x9469470c9878bf3d6d0604831d9a3a366156f7ee'
rows=[]
for ts in weekly_grid(int(dt.datetime(2025,9,18,tzinfo=dt.timezone.utc).timestamp())):
    b=block_at(ts)
    c,u=call(S,'convertToAssets(uint256)',u256(10**18),b)
    ta,_=call(S,'totalAssets()',block=b)
    av,_=call(A,'totalSupply()',block=b)
    w,_=call(WSTETH,'stEthPerToken()',block=b)
    rows.append({'date':dt.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d'),'block':b,'saveth_aveth_per_share':c/1e18,'saveth_total_assets_aveth':ta/1e18,
      'aveth_supply':av/1e18,'wsteth_steth_per_token':w/1e18,'source':f'archive eth_call via {u}: savETH.convertToAssets(1e18), savETH.totalAssets, avETH.totalSupply, wstETH.stEthPerToken'})
    print(rows[-1]['date'],b,rows[-1]['saveth_aveth_per_share'],flush=True)
write_csv(ROOT/'data/eth/top5/avant/weekly.csv',rows)
