"""Chainlink BTC/USD (proxy 0xF403...E88c, aggregator 0x4a34...84f1, phase 7 unchanged over the window) AnswerUpdated rounds.
Output raw/cl_btc_rounds.json rows [block, answer_usd, updatedAt]"""
import json, os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
import klib
from klib import topic, words
AGG = '0x4a3411ac2948b33c69666b35cc6d055b27ea84f1'
T = topic('AnswerUpdated(int256,uint256,uint256)')
URL = 'https://mainnet.gateway.tenderly.co'
def fetch(b):
    e = b + 49999
    for t in range(8):
        r = klib._post(URL, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{'address': AGG, 'fromBlock': hex(b), 'toBlock': hex(e), 'topics': [T]}]})
        if isinstance(r, dict) and 'result' in r:
            return [[int(l['blockNumber'], 16), int(l['topics'][1], 16) / 1e8, int(l['data'], 16)] for l in r['result']]
        klib.time.sleep(2 + t)
    raise RuntimeError(str(r)[:200])
rows = []
with cf.ThreadPoolExecutor(2) as ex:
    for res in ex.map(fetch, range(24_850_000, 26_030_000, 50000)):
        rows += res
rows.sort()
json.dump(rows, open(os.path.join(os.path.dirname(__file__), '..', 'raw', 'cl_btc_rounds.json'), 'w'))
print(len(rows), rows[0], rows[-1])
