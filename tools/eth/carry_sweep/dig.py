"""Dig one contract: creation block (binary search on eth_getCode), creation tx sender, implementation function names
(selectors from bytecode resolved through the openchain signature database). Usage: python3 dig.py <chain> <address> [impl]"""
import json, re, sys, urllib.request
from common import *

def code_at(ch, a, b):
    return rpc(ch, 'eth_getCode', [a, hex(b)]) or '0x'

def creation(ch, a):
    hi = int(rpc(ch, 'eth_blockNumber', []), 16); lo = 1
    if len(code_at(ch, a, hi)) <= 2: return None
    while hi - lo > 1:
        m = (lo + hi) // 2
        try: c = code_at(ch, a, m)
        except Exception: c = '0x'
        if len(c) > 2: hi = m
        else: lo = m
    blkd = rpc(ch, 'eth_getBlockByNumber', [hex(hi), True])
    # find tx that touches the address: receipts with contractAddress or logs from the address
    logs = rpc(ch, 'eth_getLogs', [{'fromBlock': hex(hi), 'toBlock': hex(hi), 'address': a}]) or []
    txh = logs[0]['transactionHash'] if logs else None
    tx = None
    if txh:
        tx = next((t for t in blkd['transactions'] if t['hash'] == txh), None)
    else:
        for t in blkd['transactions']:
            if t.get('to') is None:
                r = rpc(ch, 'eth_getTransactionReceipt', [t['hash']])
                if r and (r.get('contractAddress') or '').lower() == a.lower(): tx = t; break
    return dict(block=hi, ts=int(blkd['timestamp'], 16), tx=tx and tx['hash'], sender=tx and tx['from'], to=tx and tx['to'])

SIGC = {}
def selectors(code):
    sels = sorted(set(re.findall(r'63([0-9a-f]{8})', code[2:])))
    out = {}
    for i in range(0, len(sels), 40):
        chunk = sels[i:i + 40]
        j = getjson('https://api.openchain.xyz/signature-database/v1/lookup?filter=true&function=' + ','.join('0x' + s for s in chunk), retries=3)
        for s, v in ((j.get('result') or {}).get('function') or {}).items():
            if v: out[s] = v[0]['name']
    return out

if __name__ == '__main__':
    ch = int(sys.argv[1]); a = sys.argv[2].lower()
    print('creation', creation(ch, a))
    tgt = sys.argv[3] if len(sys.argv) > 3 else a
    names = selectors(rpc(ch, 'eth_getCode', [tgt, 'latest']))
    print(len(names), sorted(names.values()))
