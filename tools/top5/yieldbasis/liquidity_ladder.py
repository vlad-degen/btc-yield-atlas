# Exit liquidity ladder: LT.preview_withdraw(shares) vs pricePerShare at the current block, per market and size
import json,csv
from ybrpc import *
from markets import M
blk=int(rpc('eth_blockNumber',[]),16)-5
blkinfo=rpc('eth_getBlockByNumber',[hex(blk),False]); import datetime
ts=datetime.datetime.fromtimestamp(int(blkinfo['timestamp'],16),datetime.UTC).isoformat()
rows=[]
for mk in ['v3-WBTC','v3-cbBTC','v3-tBTC','v2-WBTC','v2-cbBTC','v2-tBTC','v3-WETH']:
    m=M[mk]
    pps=u(ec(m['lt'],'pricePerShare()',block=blk))/1e18
    sup=u(ec(m['lt'],'totalSupply()',block=blk))/1e18
    po=u(ec(m['pool'],'price_oracle()',block=blk))/1e18; ps=u(ec(m['pool'],'price_scale()',block=blk))/1e18
    b0=u(ec(m['pool'],'balances(uint256)',eu(0),block=blk))/1e18; b1=u(ec(m['pool'],'balances(uint256)',eu(1),block=blk))/10**m['dec']
    alloc=u(ec(m['lt'],'stablecoin_allocation()',block=blk))/1e18
    liq=words(ec(m['lt'],'liquidity()',block=blk)); tot=liq[1]/1e18
    for sh in [0.01,0.1,1,5,10,25,50,100,200,300,450]:
        if sh>sup*0.98: continue
        r=ec(m['lt'],'preview_withdraw(uint256)',eu(int(sh*1e18)),block=blk)
        out=u(r)/10**m['dec'] if r not in (None,'0x') else None
        rows.append(dict(block=blk,time=ts,market=mk,shares=sh,share_of_supply_pct=round(sh/sup*100,2),book_value_asset=round(sh*pps,6),redeem_asset=round(out,6) if out else None,
            haircut_vs_book_pct=round((out/(sh*pps)-1)*100,3) if out else None,pps=round(pps,6),pool_price_scale=round(ps,2),pool_price_oracle=round(po,2),
            ps_lag_pct=round((po/ps-1)*100,2),pool_crvusd=round(b0),pool_asset=round(b1,4),pool_crvusd_share_pct=round(b0/(b0+b1*po)*100,1),cap_usd=round(alloc/2),tvl_asset=round(tot,4)))
    print(mk,[ (r['shares'],r['haircut_vs_book_pct']) for r in rows if r['market']==mk], 'ps_lag %.1f%% crvUSD share %.1f%%'%(rows[-1]['ps_lag_pct'],rows[-1]['pool_crvusd_share_pct']))
with open('../liquidity_ladder.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
