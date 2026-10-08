"""Token inflows to the Safe that holds the Cap Stakestone vault stake (wstETH/stETH/WETH Transfer logs to it)."""
from common import *
SAFE = '0x3e32d3ffd97edd79f7e4922bc3bf6ad0adf95f34'; T = topic('Transfer(address,address,uint256)')
STETH = '0xae7ab96520de3a18e5e111b5eaab095312d7fe84'
res = {}
for nm, tok in [('wstETH', WSTETH), ('stETH', STETH), ('WETH', WETH[1])]:
    inn = logs(1, tok, [T, None, '0x' + a32(SAFE)], 22800000, B1, step=2000000)
    out = logs(1, tok, [T, '0x' + a32(SAFE)], 22800000, B1, step=2000000)
    res[nm] = dict(inflow=[('0x' + l['topics'][1][-40:], int(l['data'], 16) / 1e18, int(l['blockNumber'], 16), l['transactionHash']) for l in inn],
                   outflow=[('0x' + l['topics'][2][-40:], int(l['data'], 16) / 1e18, int(l['blockNumber'], 16), l['transactionHash']) for l in out])
    print(nm, 'IN', [(a, round(x, 1), b) for a, x, b, _ in res[nm]['inflow'] if x > 10])
    print(nm, 'OUT', [(a, round(x, 1), b) for a, x, b, _ in res[nm]['outflow'] if x > 10])
save('stakestone_safe_flows.json', res)
