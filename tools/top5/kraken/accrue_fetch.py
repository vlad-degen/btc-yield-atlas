"""Morpho Blue AccrueInterest events (id, prevBorrowRate per second, interest, feeShares) for the markets the
vault borrows from / deploys into. prevBorrowRate is the average rate the IRM applied over the elapsed interval,
so the event stream is an exact, piecewise record of the borrow rate. Also Borrow/Repay/Supply/Withdraw for utilization.
Output raw/accrue_<name>.json rows [block, logIndex, rate_per_sec, interest_raw, tx]"""
import json, os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from klib import *
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
MORPHO = '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
MK = {
    'kBTC_RLUSD': '0x15bb2a6af0c909eed19fb1f2ceeead34ecbdcba626de752c6b09389ee14eec32',
    'kBTC_PYUSD': '0xe51f9aaad25d0e755429cf77076b3c2d37cb1228ed81f8a5482f2102c220eef5',
    'WBTC_USDT': '0xa921ef34e2fc7a27ccc50ae7e4b154e16c9799d3387076c421423ef52ac4df99',
    'PRIME_PYUSD': '0x41c41d0c9aadbf4751f5ee215ed5a16954a4b34e1b70fca5393d4b08858fa3fa',
    'PST_PYUSD': '0xb4977179610abfecfc8b76255a002c16b33f46d077beb86e5911e1fe9ee6e512',
}
T_ACC = topic('AccrueInterest(bytes32,uint256,uint256,uint256)')
START = 24_850_000   # ~2026-04-15 (kBTC markets created 2026-04-17)
END = int(sys.argv[1]) if len(sys.argv) > 1 else blocknum('eth')
STEP = 10000
def fetch(b):
    e = min(END, b + STEP - 1)
    for attempt in range(8):
        r = getlogs('eth', {'address': MORPHO, 'fromBlock': hex(b), 'toBlock': hex(e), 'topics': [T_ACC, list(MK.values())]})
        if isinstance(r, list):
            return [[l['topics'][1], int(l['blockNumber'], 16), int(l['logIndex'], 16)] + words(l['data'])[:2] + [l['transactionHash']] for l in r]
        time.sleep(1 + attempt)
    raise RuntimeError(f'fail {b}: {r}')
rows = []
with cf.ThreadPoolExecutor(3) as ex:
    for res in ex.map(fetch, range(START, END + 1, STEP)):
        rows += res
inv = {v: k for k, v in MK.items()}
out = {k: [] for k in MK}
for r in sorted(rows, key=lambda r: (r[1], r[2])):
    out[inv[r[0]]].append(r[1:])
for k, v in out.items():
    print(k, len(v))
json.dump({'end_block': END, 'markets': MK, 'rows': out}, open(os.path.join(RAW, 'accrue_events.json'), 'w'))
