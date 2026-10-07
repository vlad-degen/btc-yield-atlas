"""Shared helpers for the 2026-10-07 top-5 risk/liquidity/rewards gap pull.
Read-only: eth_call / eth_getLogs / HTTP GET only. Every RPC batch is appended to
raw/eth/gap-2026-10-07/top5-risk/rpc_log.jsonl and cached in rpc_cache.json."""
import json, os, sys, time, hashlib, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/top5/kraken'))
import klib
from klib import sel, enc_addr, enc_uint, enc_b32, words, dec_addr, dec_string, keccak, topic
RAW = ROOT / 'raw/eth/gap-2026-10-07/top5-risk'
RAW.mkdir(parents=True, exist_ok=True)
RPCS = ['https://eth-mainnet.public.blastapi.io', 'https://gateway.tenderly.co/public/mainnet', 'https://eth.drpc.org']
klib.RPCS['eth'] = RPCS
T = 1790985599
TB = 26108081
CACHE_P = RAW / 'rpc_cache.json'
CACHE = json.load(open(CACHE_P)) if CACHE_P.exists() else {}
def save_cache():
    json.dump(CACHE, open(CACHE_P, 'w'))
def _post(url, payload, timeout=90):
    r = subprocess.run(['curl', '-s', '-m', str(timeout), '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', '@-', url],
                       input=json.dumps(payload).encode(), capture_output=True)
    try: return json.loads(r.stdout.decode())
    except Exception: return None
def log(entry):
    with open(RAW / 'rpc_log.jsonl', 'a') as f: f.write(json.dumps(entry) + '\n')
def ck(to, data, block): return f'{to.lower()}|{data}|{block}'
def batch(calls, chunk=10, tag=''):
    """calls: list of (to, data_hex_without_or_with_0x, block_int). returns list of hex or None (revert)."""
    calls = [(to, d if d.startswith('0x') else '0x' + d, b) for to, d, b in calls]
    out = [None] * len(calls)
    todo = [i for i, c in enumerate(calls) if ck(*c) not in CACHE]
    for i, c in enumerate(calls):
        if ck(*c) in CACHE: out[i] = CACHE[ck(*c)]
    for s in range(0, len(todo), chunk):
        idx = todo[s:s + chunk]
        payload = [{'jsonrpc': '2.0', 'id': j, 'method': 'eth_call', 'params': [{'to': calls[i][0], 'data': calls[i][1]}, hex(calls[i][2]) if isinstance(calls[i][2], int) else calls[i][2]]} for j, i in enumerate(idx)]
        done = False
        for attempt in range(6):
            for url in RPCS:
                res = _post(url, payload)
                if not (isinstance(res, list) and len(res) == len(idx)): print('rpc bad', url, str(res)[:200])
                if isinstance(res, list) and len(res) == len(idx):
                    bad = [r for r in res if 'error' in r and not any(w in str(r['error']).lower() for w in ('revert', 'execution', 'invalid opcode', 'out of gas'))]
                    if bad:
                        print('rpc err', url, str(bad[0])[:200]); continue
                    for r in res:
                        i = idx[r['id']]
                        v = r.get('result')
                        if v == '0x': v = None
                        out[i] = v; CACHE[ck(*calls[i])] = v
                    log({'tag': tag, 'url': url, 'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'n': len(idx),
                         'calls': [{'to': calls[i][0], 'data': calls[i][1], 'block': calls[i][2], 'result': out[i]} for i in idx]})
                    done = True; break
            if done: break
            time.sleep(2 + attempt * 2)
        if not done:
            raise RuntimeError('batch failed ' + tag)
    save_cache()
    return out
def c(to, sig, args='', block=TB): return (to, '0x' + sel(sig) + args, block)
def W(h): return words(h) if h else None
def http_json(url, key, data=None, timeout=90):
    cmd = ['curl', '-s', '-m', str(timeout), '-H', 'User-Agent: eth-yield-research/1.0']
    if data is not None:
        cmd += ['-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', '@-']
        r = subprocess.run(cmd + [url], input=json.dumps(data).encode(), capture_output=True)
    else:
        r = subprocess.run(cmd + [url], capture_output=True)
    body = r.stdout
    (RAW / 'http').mkdir(exist_ok=True)
    p = RAW / 'http' / (key + '.json')
    p.write_bytes(body)
    with open(RAW / 'http_log.jsonl', 'a') as f:
        f.write(json.dumps({'key': key, 'url': url, 'post': data, 'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}) + '\n')
    try: return json.loads(body)
    except Exception: return None
def months():
    import csv
    rows = list(csv.DictReader(open(ROOT / 'data/eth/economic-dollar-loans.csv')))
    seen = {}
    for r in rows: seen.setdefault(r['month'], (int(r['timestamp']), int(r['block'])))
    out = [(m, ts, b) for m, (ts, b) in seen.items()]
    return [o for o in out if o[0] != 'snapshot'] + [('T', T, TB)]
def s32(x): return x - (1 << 256) if x >= (1 << 255) else x
