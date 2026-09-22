"""Fetch every Transfer event of the vault share token (sentoraBTC) on Ink.
Primary: Ink RPC eth_getLogs in 10k-block windows (parallel). Output raw/share_transfers.json
rows: [block, logIndex, from, to, value_raw, tx]
"""
import json, sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from klib import *

V = '0x7dee0120739b7ec048b469939efb178adbbb19b2'
T = topic('Transfer(address,address,uint256)')
START = 43_150_000   # vault created shortly before first rate update (block 43,231,099, 2026-04-20)
END = int(sys.argv[1]) if len(sys.argv) > 1 else blocknum('ink')
OUT = os.path.join(os.path.dirname(__file__), '..', 'raw', 'share_transfers.json')

def fetch(b):
    e = min(END, b + 9999)
    for attempt in range(6):
        r = getlogs('ink', {'address': V, 'fromBlock': hex(b), 'toBlock': hex(e), 'topics': [T]})
        if isinstance(r, list):
            return [[int(l['blockNumber'], 16), int(l['logIndex'], 16), '0x' + l['topics'][1][-40:], '0x' + l['topics'][2][-40:],
                     int(l['data'], 16), l['transactionHash']] for l in r]
        time.sleep(1 + attempt)
    raise RuntimeError(f'failed {b} {r}')

starts = list(range(START, END + 1, 10000))
rows = []
with cf.ThreadPoolExecutor(8) as ex:
    for i, res in enumerate(ex.map(fetch, starts)):
        rows += res
        if i % 100 == 0:
            print(i, len(starts), len(rows), flush=True)
rows.sort(key=lambda r: (r[0], r[1]))
json.dump({'end_block': END, 'rows': rows}, open(OUT, 'w'))
print('done', len(rows))
