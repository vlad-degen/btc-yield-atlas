"""Shared helpers for the top-5 ETH weekly share-price pulls (archive eth_call, public RPCs).

Weekly grid: T and every 7 days back from T (T = 2 Oct 2026 23:59:59 UTC, block 26,108,081).
Blocks are found by timestamp search (last block with timestamp <= target).
"""
import json, sys, time, urllib.request, csv, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'top5' / 'etherfi'))
from keccak_lib import sel  # noqa: E402

T_TS, T_BLOCK = 1790985599, 26108081
RPCS = ['https://gateway.tenderly.co/public/mainnet', 'https://eth.drpc.org']
WSTETH = '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'
_cache = {}


def rpc(method, params, tries=6):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    last = None
    for i in range(tries):
        url = RPCS[i % len(RPCS)]
        try:
            req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'User-Agent': 'research'})
            r = json.loads(urllib.request.urlopen(req, timeout=40).read())
            if 'error' in r:
                last = r['error']; time.sleep(1.5 * (i + 1)); continue
            return r['result'], url
        except Exception as e:  # rate limit or network
            last = e; time.sleep(1.5 * (i + 1))
    raise RuntimeError(f'{method} failed: {last}')


def block_ts(b):
    if b not in _cache:
        res, _ = rpc('eth_getBlockByNumber', [hex(b), False])
        _cache[b] = int(res['timestamp'], 16)
    return _cache[b]


def block_at(ts):
    """Last block with timestamp <= ts."""
    lo = T_BLOCK - (T_TS - ts) // 12 - 2000
    hi = T_BLOCK - (T_TS - ts) // 12 + 2000
    hi = min(hi, T_BLOCK)
    while block_ts(lo) > ts: lo -= 5000
    while hi < T_BLOCK and block_ts(hi) <= ts: hi += 5000
    hi = min(hi, T_BLOCK)
    if block_ts(hi) <= ts: return hi
    while hi - lo > 1:
        m = (lo + hi) // 2
        if block_ts(m) <= ts: lo = m
        else: hi = m
    return lo


def call(to, sig, args_hex='', block=T_BLOCK):
    res, url = rpc('eth_call', [{'to': to, 'data': '0x' + sel(sig) + args_hex}, hex(block)])
    return (int(res[:66], 16) if res and res != '0x' else None), url


def u256(x):
    return format(int(x), '064x')


def weekly_grid(start_ts):
    pts = []
    t = T_TS
    while t >= start_ts:
        pts.append(t); t -= 7 * 86400
    return sorted(pts)


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
