"""Carry sweep chain setup: extra RPCs for chains the lending-split lib lacks, snapshot blocks, ETH price, asset helpers.
Imports common.py (shared helpers) and only extends lib.RPCS in memory."""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from common import *  # noqa
from common import L, RAW

T_TS = 1790985599
ETH_USD = 2666.40  # Aave Core oracle WETH at T
EXTRA_RPCS = {
    146: ['https://rpc.soniclabs.com', 'https://sonic.drpc.org'],
    239: ['https://rpc.tac.build', 'https://tac.drpc.org'],
    60808: ['https://rpc.gobob.xyz', 'https://bob.drpc.org'],
    80094: ['https://rpc.berachain.com', 'https://berachain.drpc.org'],
    5000: ['https://rpc.mantle.xyz', 'https://mantle.drpc.org'],
    1923: ['https://swell-mainnet.alt.technology', 'https://rpc.ankr.com/swell'],
    42793: ['https://node.mainnet.etherlink.com'],
    1135: ['https://rpc.api.lisk.com', 'https://lisk.drpc.org'],
    43111: ['https://rpc.hemi.network/rpc'],
    196: ['https://rpc.xlayer.tech', 'https://xlayer.drpc.org'],
    3637: ['https://rpc.botanixlabs.com'],
    1101: ['https://zkevm-rpc.com', 'https://polygon-zkevm.drpc.org'],
}
for k, v in EXTRA_RPCS.items():
    L.RPCS.setdefault(k, v)
    for u in v:
        if u not in L.RPCS[k]: L.RPCS[k].append(u)
for k, v in {130: ['https://mainnet.unichain.org'], 43114: ['https://api.avax.network/ext/bc/C/rpc'], 56: ['https://bsc-dataseed.bnbchain.org'],
             999: ['https://hyperliquid.drpc.org'], 59144: ['https://rpc.linea.build'], 143: ['https://rpc-mainnet.monadinfra.com']}.items():
    for u in v:
        if u not in L.RPCS[k]: L.RPCS[k].append(u)

BLOCKS = os.path.join(RAW, 'blocks_at_T.json')
def bT(chain):
    """Last block with timestamp <= T. Cached in raw/.../carry-sweep-2026-10-08/blocks_at_T.json (seeded from the lending-split caches)."""
    if chain == 1: return 26108081
    kb = json.load(open(BLOCKS)) if os.path.exists(BLOCKS) else {}
    if str(chain) in kb: return kb[str(chain)]
    b = L.block_at(chain, 'eth')
    kb = json.load(open(BLOCKS)) if os.path.exists(BLOCKS) else {}
    kb[str(chain)] = b; json.dump(kb, open(BLOCKS, 'w'), indent=1)
    return b

CHAIN_NAME = {1: 'ethereum', 8453: 'base', 42161: 'arbitrum', 10: 'optimism', 59144: 'linea', 130: 'unichain', 137: 'polygon', 43114: 'avalanche',
              56: 'bnb', 146: 'sonic', 239: 'tac', 60808: 'bob', 80094: 'berachain', 9745: 'plasma', 999: 'hyperevm', 143: 'monad',
              5000: 'mantle', 1923: 'swell', 42793: 'etherlink', 1135: 'lisk', 43111: 'hemi', 196: 'xlayer', 3637: 'botanix', 1101: 'polygon-zkevm',
              747474: 'katana', 480: 'worldchain', 100: 'gnosis'}

def code_kind(chain, a, block):
    c = rpc(chain, 'eth_getCode', [a, hex(block)]) or '0x'
    if c in ('0x', ''): return 'EOA', None
    if c.startswith('0xef0100'): return 'EIP-7702', '0x' + c[8:48]
    return 'contract', None

def is_eth_sym(sym):
    return L.is_eth(sym)
def is_stable_sym(sym):
    return L.is_stable(sym)

sys.path.insert(0, os.path.join(L.ROOT, 'tools', 'top5', 'etherfi'))
from keccak_lib import keccak as _keccak  # pure python keccak256
def S(sig):
    """4-byte selector (0x-prefixed) of a function signature."""
    return '0x' + _keccak(sig.encode())[:4].hex()
def topic(sig):
    return '0x' + _keccak(sig.encode()).hex()
# prune RPCs that fail archive reads at T
L.RPCS[56] = ['https://bsc-mainnet.public.blastapi.io', 'https://bsc.drpc.org']
L.RPCS[43114] = ['https://api.avax.network/ext/bc/C/rpc', 'https://gateway.tenderly.co/public/avalanche']
L.RPCS[9745] = ['https://rpc.plasma.to']
L.RPCS[42161] = ['https://arbitrum-one.public.blastapi.io', 'https://gateway.tenderly.co/public/arbitrum']

# ETH-equivalent per unit by symbol, from the Aave Core oracle at T (USD price / WETH price), used when a venue oracle gives no quote
_AAVE = {}
try:
    for _r in json.load(open(os.path.join(L.ROOT, 'raw', 'eth', 'lending-split-2026-10-08', 'aave_eth_aave-core.json')))['reserves']:
        _AAVE[_r['sym'].upper()] = _r['price']
except Exception:
    pass
def eth_rate(sym):
    """ETH per unit for an ETH-family symbol (Aave Core oracle ratio at T); 1.0 for plain ETH wrappers; None if unknown."""
    if not sym: return None
    s = sym.upper()
    if s in L.PLAIN_ETH: return 1.0
    if s in _AAVE and is_eth_sym(sym): return _AAVE[s] / ETH_USD
    return None
def usd_rate(sym):
    if not sym: return None
    s = sym.upper()
    if s in _AAVE: return _AAVE[s]
    if is_stable_sym(sym) and 'EUR' not in s: return 1.0
    r = eth_rate(sym)
    return r * ETH_USD if r else None

# eth_getLogs endpoints with the block range they accepted in a probe on 2026-10-08
LOGS = {1: [('https://gateway.tenderly.co/public/mainnet', 1_000_000)], 42161: [('https://gateway.tenderly.co/public/arbitrum', 10_000_000), ('https://arb1.arbitrum.io/rpc', 1_000_000)],
        10: [('https://gateway.tenderly.co/public/optimism', 1_000_000)], 146: [('https://rpc.soniclabs.com', 1_000_000)],
        43114: [('https://api.avax.network/ext/bc/C/rpc', 1_000_000), ('https://gateway.tenderly.co/public/avalanche', 1_000_000)],
        5000: [('https://rpc.mantle.xyz', 10_000)], 80094: [('https://rpc.berachain.com', 10_000)], 8453: [('https://gateway.tenderly.co/public/base', 1000)]}
def logs(chain, address, topics, fb, tb, workers=6):
    """eth_getLogs over [fb, tb] in chunks; address may be a list. Splits a chunk on error (too many results)."""
    eps = LOGS[chain]
    step0 = eps[0][1]
    rngs = [(b, min(tb, b + step0 - 1)) for b in range(fb, tb + 1, step0)]
    def one(rg):
        lo, hi = rg
        for i in range(12):
            url, mx = eps[i % len(eps)]
            if hi - lo + 1 > mx: url, mx = eps[0]
            try:
                r = L.post_raw(url, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{'address': address, 'fromBlock': hex(lo), 'toBlock': hex(hi), 'topics': topics}]}, timeout=120)
                if 'error' in r: raise Exception(str(r['error'])[:200])
                return r['result']
            except Exception as e:
                if hi - lo > 2000 and i >= 1:
                    mid = (lo + hi) // 2
                    return one((lo, mid)) + one((mid + 1, hi))
                time.sleep(1 + i)
        raise Exception('logs failed %s %s' % (chain, rg))
    with ThreadPoolExecutor(workers) as ex: res = list(ex.map(one, rngs))
    return [l for x in res for l in x]
