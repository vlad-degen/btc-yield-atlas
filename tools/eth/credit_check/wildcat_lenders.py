"""Wildcat Wintermute Trading WETH market: lenders and their balances at T (do counted products supply to it?)."""
from common import *
M = '0xbad1b632e90ce02af868f07c572adb067eb98353'
lg = logs(1, M, [topic('Deposit(address,uint256,uint256)')], 20000000, B1, step=500000)
tr = logs(1, M, [topic('Transfer(address,address,uint256)')], 20000000, B1, step=500000)
acc = sorted({'0x' + l['topics'][1][-40:] for l in lg} | {'0x' + l['topics'][2][-40:] for l in tr})
first = min(int(l['blockNumber'], 16) for l in lg) if lg else None
out = {}
for a in acc:
    b = bal(1, M, a) / 1e18
    if b > 0.001:
        nm = None
        try: nm = dec_str(c(1, a, 'name()'))
        except Exception: pass
        code = (len(rpc(1, 'eth_getCode', [a, hex(B1)])) - 2) // 2
        out[a] = dict(balance=b, name=nm, code_bytes=code)
for a, v in sorted(out.items(), key=lambda x: -x[1]['balance']): print(a, v)
save('wildcat_lenders.json', dict(market=M, first_deposit_block=first, lenders=out))
