"""Native Credit Pool: WETH LP markets on Ethereum, Base, Arbitrum at T (idle WETH in the vault, totalUnderlying, lent out)."""
from common import *
V = {1: ('0xe3D41d19564922C9952f692C5Dd0563030f5f2EF', 22173196), 8453: ('0x74a4Cd023e5AfB88369E3f22b02440F2614a1367', 32578350),
     42161: ('0xbA1cf8A63227b46575AF823BEB4d83D1025eff09', 355397381)}
out = {}
for ch, (v, fb) in V.items():
    blk = B1 if ch == 1 else L2[ch]
    lps = [A(c(ch, v, 'lpTokens(address)', WETH[ch]))]  # the vault's WETH market (lpTokens(WETH); same LP as the MarketListed log on Ethereum)
    res = []
    for lp in lps:
        und = A(c(ch, lp, 'underlying()'))
        if und.lower() != WETH[ch]: continue
        tu = U(c(ch, lp, 'totalUnderlying()')); cash = bal(ch, und, v)
        r = dict(lp=lp, underlying=und, totalUnderlying=tu / 1e18, vault_weth=cash / 1e18, lent=max(0, tu - cash) / 1e18,
                 lp_supply=U(c(ch, lp, 'totalSupply()')) / 1e18, name=dec_str(c(ch, lp, 'name()')))
        res.append(r)
    out[ch] = dict(vault=v, block=blk, markets=res)
    print(ch, json.dumps(res))
save('native.json', out)
