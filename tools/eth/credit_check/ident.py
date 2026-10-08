"""Identify holder contracts (name, symbol, code size, totalSupply, owner) at T."""
import sys
from common import *
for x in sys.argv[1:]:
    code = rpc(1, 'eth_getCode', [x, hex(B1)])
    r = {'addr': x, 'code_bytes': (len(code) - 2) // 2}
    for s in ['name()', 'symbol()']:
        try: r[s] = dec_str(c(1, x, s))
        except Exception: pass
    for s in ['totalSupply()', 'totalAssets()', 'decimals()']:
        try: r[s] = U(c(1, x, s))
        except Exception: pass
    for s in ['owner()', 'asset()', 'getThreshold()', 'curator()', 'vault()', 'underlyingAsset()']:
        try:
            v = c(1, x, s)
            if v and v != '0x': r[s] = A(v) if s != 'getThreshold()' else U(v)
        except Exception: pass
    print(json.dumps(r))
