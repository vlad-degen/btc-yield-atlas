"""Venue sweep helpers (Curve, Liquity, Maker): selectors, block lookup that does not touch other study folders, code kind, ETH price at T."""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from common import *  # noqa
from common import L
from lib import words, is_eth, is_stable, addr_list  # noqa
sys.path.insert(0, os.path.join(ROOT, 'tools', 'top5', 'etherfi'))
from keccak_lib import keccak  # noqa

VRAW = os.path.join(RAW, 'venues')
os.makedirs(VRAW, exist_ok=True)
T = 1790985599
ETH_USD = 2666.40
# extra RPCs for chains the lending split did not need
L.RPCS.setdefault(252, ['https://rpc.frax.com', 'https://fraxtal.drpc.org'])
L.RPCS.setdefault(146, ['https://rpc.soniclabs.com', 'https://sonic.drpc.org'])
L.RPCS.setdefault(1923, ['https://swell-mainnet.alt.technology', 'https://rpc.swellnetwork.io'])
L.RPCS.setdefault(80094, ['https://rpc.berachain.com', 'https://berachain.drpc.org'])
L.RPCS.setdefault(34443, ['https://mainnet.mode.network', 'https://mode.drpc.org'])
L.RPCS.setdefault(5000, ['https://rpc.mantle.xyz', 'https://mantle.drpc.org'])

_SEL = {}
def sel(sig):
    if sig not in _SEL: _SEL[sig] = '0x' + keccak(sig.encode())[:4].hex()
    return _SEL[sig]
def cd(sig, *args):
    s = sel(sig)
    for a in args:
        s += a32(a) if isinstance(a, str) else u32(a)
    return s

def vsave(name, obj):
    p = os.path.join(VRAW, name)
    json.dump(obj, open(p, 'w'), indent=1, default=str)
    return p
def vload(name, default=None):
    p = os.path.join(VRAW, name)
    return json.load(open(p)) if os.path.exists(p) else default

_BF = os.path.join(VRAW, 'blocks.json')
def vblk(chain):
    """Last block with timestamp <= T. Reads the existing caches, never writes them; new lookups go to venues/blocks.json."""
    if chain == 1: return 26108081
    kb = json.load(open(os.path.join(L.RAW, 'blocks.json')))
    if 'eth_%d' % chain in kb: return kb['eth_%d' % chain]
    old = json.load(open(os.path.join(L.OLD, 'blocks_at_T.json')))
    if str(chain) in old: return old[str(chain)]
    mine = json.load(open(_BF)) if os.path.exists(_BF) else {}
    if str(chain) in mine: return mine[str(chain)]
    def bt(b): return int(rpc(chain, 'eth_getBlockByNumber', [hex(b), False])['timestamp'], 16)
    head = int(rpc(chain, 'eth_blockNumber', []), 16); hts = bt(head)
    lo, hi = 1, head
    b2 = max(1, head - 200000); t2 = bt(b2); avg = (hts - t2) / max(1, head - b2)
    est = int(head - (hts - T) / avg)
    lo = max(1, est - 200000); hi = min(head, est + 200000)
    while bt(lo) > T: lo = max(1, lo - 1000000)
    while bt(hi) <= T and hi < head: hi = min(head, hi + 1000000)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if bt(mid) <= T: lo = mid
        else: hi = mid
    mine[str(chain)] = lo; json.dump(mine, open(_BF, 'w'), indent=1)
    return lo

def kinds(chain, addrs, block):
    """address -> EOA / EIP-7702 / contract, from eth_getCode at the block."""
    addrs = sorted(set(a.lower() for a in addrs if a))
    def one(a):
        c = rpc(chain, 'eth_getCode', [a, hex(block)]) or '0x'
        if c in ('0x', ''): return a, 'EOA'
        if c.startswith('0xef0100'): return a, 'EIP-7702'
        return a, 'contract'
    with ThreadPoolExecutor(8) as ex:
        return dict(ex.map(one, addrs))

def sym(chain, token, block):
    r = call1(chain, token, sel('symbol()'), block)
    return dec_str(r) if r else None
