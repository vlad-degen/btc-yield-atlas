"""StakeStone Assets Management Strategy: where its value sits (is the Safe that holds the Cap Stakestone vault stake part of it)."""
from common import *
S = '0x8f4998661618c5cc5dbcc0ae19923d6537622180'; SAFE = '0x3e32d3ffd97edd79f7e4922bc3bf6ad0adf95f34'
out = {}
for f in ['safeWallet()', 'safe()', 'wallet()', 'owner()', 'governance()', 'manager()', 'getAllValue()', 'getInvestedValue()', 'getPendingValue()',
          'stoneVault()', 'controller()', 'oracle()', 'assetsManager()', 'custodian()', 'bridge()', 'receiver()']:
    try:
        x = c(1, S, f)
        if x and x != '0x': out[f] = x if len(x) > 66 else (A(x) if int(x, 16) < 2 ** 160 and int(x, 16) > 10 ** 30 else U(x))
    except Exception as e: pass
code = rpc(1, 'eth_getCode', [S, hex(B1)]); out['code_has_safe'] = SAFE[2:] in code
impl = rpc(1, 'eth_getStorageAt', [S, '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc', hex(B1)])
out['impl'] = impl
for i in range(12):
    out['slot%d' % i] = rpc(1, 'eth_getStorageAt', [S, hex(i), hex(B1)])
out['strategy_eth'] = int(rpc(1, 'eth_getBalance', [S, hex(B1)]), 16) / 1e18
print(json.dumps(out, indent=1)); save('stakestone_strategy.json', out)
