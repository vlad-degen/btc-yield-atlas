"""Carry sweep helpers: reuse the lending-split RPC helpers, write raw captures to raw/eth/carry-sweep-2026-10-08/."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lending_split'))
import lib as L  # noqa
from lib import rpc, mcall, call1, getjson, dec_str, A, U, a32, u32, log, block_at  # noqa
ROOT = L.ROOT
RAW = os.path.join(ROOT, 'raw', 'eth', 'carry-sweep-2026-10-08')
os.makedirs(RAW, exist_ok=True)
def save(name, obj):
    json.dump(obj, open(os.path.join(RAW, name), 'w'), indent=1, default=str)
def load(name, default=None):
    p = os.path.join(RAW, name)
    return json.load(open(p)) if os.path.exists(p) else default
def blk(chain):
    """Block at T. Reads the existing caches only (never writes the lending-split cache); 'latest' if no cached block."""
    if chain == 1: return L.SNAP['eth']['block1']
    for p in (os.path.join(L.RAW, 'blocks.json'), os.path.join(RAW, 'blocks_at_T.json'), os.path.join(RAW, 'venues', 'blocks.json'),
              os.path.join(RAW, 'venues', 'blocks_extra.json')):
        if os.path.exists(p):
            d = json.load(open(p))
            for k in ('eth_%d' % chain, str(chain), chain):
                if k in d and isinstance(d[k], int): return d[k]
    return None
BSCOUT = {1: 'https://eth.blockscout.com', 8453: 'https://base.blockscout.com', 42161: 'https://arbitrum.blockscout.com',
          10: 'https://optimism.blockscout.com', 480: 'https://worldchain-mainnet.explorer.alchemy.com', 747474: 'https://explorer.katanarpc.com',
          100: 'https://gnosis.blockscout.com', 59144: 'https://explorer.linea.build', 137: 'https://polygon.blockscout.com',
          999: 'https://www.hyperscan.com', 9745: 'https://plasmascan.to'}
