"""StakeStone STONE: strategies and their values at T; does the Cap Stakestone vault holder (Safe 0x3e32...) sit inside STONE?"""
from common import *
VS = '0x396aBF9fF46E21694F4eF01ca77C6d7893A017B2'; SAFE = '0x3e32d3ffd97edd79f7e4922bc3bf6ad0adf95f34'
r = c(1, VS, 'getStrategies()')
h = r[2:]; off = int(h[:64], 16) * 2; n = int(h[off:off + 64], 16)
strats = ['0x' + h[off + 64 + 64 * i + 24: off + 64 + 64 * (i + 1)] for i in range(n)]
out = {'all_value': U(c(1, VS, 'getAllStrategiesValue()')) / 1e18, 'strategies': {}}
for s in strats:
    v = c(1, VS, 'getStrategyValue(address)', s)
    nm = None
    try: nm = dec_str(c(1, s, 'name()'))
    except Exception: pass
    out['strategies'][s] = dict(value=U(v) / 1e18, name=nm, safe_wsteth=bal(1, WSTETH, s))
    for f in ['safeWallet()', 'safe()', 'wallet()', 'owner()']:
        try:
            x = c(1, s, f)
            if x and x != '0x' and int(x, 16): out['strategies'][s][f] = A(x)
        except Exception: pass
out['safe_owners'] = addr_list(c(1, SAFE, 'getOwners()'))
out['safe_wsteth'] = bal(1, WSTETH, SAFE) / 1e18
print(json.dumps(out, indent=1)); save('stakestone.json', out)
