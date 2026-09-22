"""Snapshot of the whole bgBTC Earn stack at a Morph block (archive RPC reads)."""
from rpc import *
M='0xad10d07901dc3195c3cb5e78e061f4ea8d9b4905'
MID='37d156e96a4230c1fe9545579086e4b40d08b4aae8b3c78ee91031f2a22c1a5c'
V='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'
G='0x9131eb40bd0bdce73c72755f1bb2cf39a9453341'
AD='0x2214a206b3647523c6aeca1dc91b8824a7108e62'
BG='0x31011317764e097b28d159a8145b92bfa453f606'
USDC='0xcfb1186f4e93d60e60a8bdd997427d1f33bc372b'
PFC='0x89963ff339c4a6194ea77381c204884e4503f8fb'
ORA='0x22b3d92703ee73af5e31a6ba56cca2fdced6c412'
IRM='0xfb69467de332e03ff502b85bb2249d2f721f3319'
def w(r): h=r[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
def snap(blk):
    b=hex(blk) if isinstance(blk,int) else blk
    calls=[
     ('market',M,sel('market(bytes32)')+MID),
     ('posV',M,sel('position(bytes32,address)')+MID+enc_addr(V)),
     ('posAD',M,sel('position(bytes32,address)')+MID+enc_addr(AD)),
     ('oracle',ORA,sel('price()')),
     ('rat',IRM,sel('rateAtTarget(bytes32)')+MID),
     ('g_ta',G,sel('totalAssets()')),
     ('g_ts',G,sel('totalSupply()')),
     ('g_px',G,sel('convertToAssets(uint256)')+enc_uint(10**24)),
     ('g_balV',G,sel('balanceOf(address)')+enc_addr(V)),
     ('g_idle',USDC,sel('balanceOf(address)')+enc_addr(G)),
     ('v_ts',V,sel('totalSupply()')),
     ('v_state',PFC,sel('getVaultState(address)')+enc_addr(V)),
     ('bg_supply',BG,sel('totalSupply()')),
     ('bg_idleV',BG,sel('balanceOf(address)')+enc_addr(V)),
     ('usdc_idleV',USDC,sel('balanceOf(address)')+enc_addr(V)),
     ('mp',M,sel('idToMarketParams(bytes32)')+MID),
    ]
    res=batch('morph',[('eth_call',[{'to':to,'data':d},b]) for _,to,d in calls])
    R={}
    for (n,to,d),r in zip(calls,res):
        if isinstance(r,tuple) or r in (None,'0x'):
            r=None
            for ch in ['morph2','morph3','morph']:
                try:
                    r=eth_call(ch,to,d,b)
                    if r and r!='0x': break
                except Exception as e: r=None
        R[n]=r
    o={'block':blk}
    mk=w(R['market']) if R['market'] else [0]*6
    o['supply']=mk[0]/1e6; o['borrow']=mk[2]/1e6; o['util']=mk[2]/mk[0] if mk[0] else 0
    pv=w(R['posV']) if R['posV'] else [0,0,0]
    o['aera_debt']=(pv[1]*mk[2]/mk[3]/1e6) if mk[3] else 0
    o['aera_coll']=pv[2]/1e8
    pa=w(R['posAD']) if R['posAD'] else [0,0,0]
    o['adapter_supply']=(pa[0]*mk[0]/mk[1]/1e6) if mk[1] else 0
    o['btc_usd']=int(R['oracle'],16)/1e34 if R['oracle'] else None
    o['rateAtTarget_apr']=int(R['rat'],16)*31536000/1e18 if R['rat'] else None
    # borrow rate view
    if R['mp'] and R['market'] and mk[0]:
        try:
            r=eth_call('morph',IRM,sel('borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))')+R['mp'][2:]+R['market'][2:],b)
            o['borrow_apr']=int(r,16)*31536000/1e18
        except Exception as e: o['borrow_apr']=None
    else: o['borrow_apr']=None
    o['g_totalAssets']=int(R['g_ta'],16)/1e6 if R['g_ta'] else 0
    o['g_totalSupply']=int(R['g_ts'],16)/1e18 if R['g_ts'] else 0
    o['g_price']=int(R['g_px'],16)/1e12 if R['g_px'] else None
    o['g_aera_shares']=int(R['g_balV'],16)/1e18 if R['g_balV'] else 0
    o['g_idle']=int(R['g_idle'],16)/1e6 if R['g_idle'] else 0
    o['v_units']=int(R['v_ts'],16)/1e18 if R['v_ts'] else 0
    st=w(R['v_state']) if R['v_state'] else None
    o['v_unit_price']=st[10]/1e8 if st else None
    o['v_anchor_ts']=st[8] if st else None
    o['bgbtc_supply_morph']=int(R['bg_supply'],16)/1e8 if R['bg_supply'] else 0
    o['v_idle_bgbtc']=int(R['bg_idleV'],16)/1e8 if R['bg_idleV'] else 0
    o['v_idle_usdc']=int(R['usdc_idleV'],16)/1e6 if R['usdc_idleV'] else 0
    return o
