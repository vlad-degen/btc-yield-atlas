"""YieldBasis WETH LT: weekly pricePerShare, gauge share value, exit preview, supply, staked share; wstETH benchmark.
Output: data/eth/top5/yieldbasis/weekly.csv"""
import sys, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from weekly_lib import *
LT='0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea'; G='0xd829456fd63ada7de0657714a3a7a26de403e3d8'
rows=[]
for ts in weekly_grid(int(dt.datetime(2026,5,29,tzinfo=dt.timezone.utc).timestamp())):
    b=block_at(ts)
    pps,u=call(LT,'pricePerShare()',block=b)
    g,_=call(G,'convertToAssets(uint256)',u256(10**18),b)
    pw,_=call(LT,'preview_withdraw(uint256)',u256(10**18),b)
    ts_,_=call(LT,'totalSupply()',block=b)
    st,_=call(LT,'balanceOf(address)',u256(int(G,16)),b)
    w,_=call(WSTETH,'stEthPerToken()',block=b)
    rows.append({'date':dt.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d'),'block':b,'lt_pps':pps/1e18,'gauge_lt_per_share':g/1e18,
      'preview_withdraw_1lt':pw/1e18 if pw else '','lt_supply':ts_/1e18,'staked_share':st/ts_ if ts_ else '','book_eth':ts_*pps/1e36,
      'wsteth_steth_per_token':w/1e18,'source':f'archive eth_call at block via {u}: LT.pricePerShare, gauge.convertToAssets(1e18), LT.preview_withdraw(1e18), LT.totalSupply, LT.balanceOf(gauge), wstETH.stEthPerToken'})
    print(rows[-1]['date'],b,rows[-1]['lt_pps'],flush=True)
write_csv(ROOT/'data/eth/top5/yieldbasis/weekly.csv',rows)
