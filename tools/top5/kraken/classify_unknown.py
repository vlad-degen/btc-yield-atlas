"""Classify snapshot holders that later exited (absent from the Blockscout holder list) via eth_getCode on Ink
at the snapshot block. EIP-7702 delegated accounts have code 0xef0100 || delegate(20 bytes). Output raw/unknown_type_codes.json"""
import json, os, sys, collections, subprocess, concurrent.futures as cf
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
U = json.load(open(os.path.join(RAW, 'unknown_type_addrs.json')))
bal = json.load(open(os.path.join(RAW, 'balances_snapshot.json')))
def code(a):
    for url in ['https://rpc-gel.inkonchain.com', 'https://rpc-qnd.inkonchain.com', 'https://ink.drpc.org']:
        r = subprocess.run(['curl', '-s', '-m', '20', '-X', 'POST', '-H', 'Content-Type: application/json', '--data',
                            json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getCode', 'params': [a, hex(56407189)]}), url], capture_output=True)
        try: return a, json.loads(r.stdout.decode())['result']
        except Exception: continue
    return a, None
out = {}
with cf.ThreadPoolExecutor(6) as ex:
    for a, c in ex.map(code, U): out[a] = c
cnt = collections.Counter(); btc = collections.Counter()
for a, c in out.items():
    if c is None: k = 'unresolved'
    elif c.startswith('0xef0100'): k = 'EIP-7702 -> ZeroDev Kernel (Kraken/Privy embedded wallet)' if c[8:].lower() == 'd6cedde84be40893d153be9d467cd6ad37875b28' else 'EIP-7702 -> 0x' + c[8:]
    elif c in ('0x', '0x0'): k = 'plain EOA'
    else: k = 'contract'
    cnt[k] += 1; btc[k] += bal['balances'][a] * bal['rate']
print(dict(cnt), {k: round(v, 3) for k, v in btc.items()})
json.dump({'counts': cnt, 'btc': btc, 'codes': out}, open(os.path.join(RAW, 'unknown_type_codes.json'), 'w'))
