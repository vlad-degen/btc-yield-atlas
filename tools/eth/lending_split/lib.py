"""Shared helpers for the lending split (what is borrowed against ETH and BTC collateral).

ETH snapshot T = 2026-10-02 23:59:59 UTC (Ethereum block 26,108,081). BTC snapshot S = 2026-09-20 12:00:00 UTC (Ethereum block 26,018,583).
L2 blocks: last block with timestamp <= the snapshot time. All reads are archive eth_call at those blocks, batched through Multicall3.
"""
import json, os, re, sys, time, random, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RAW = os.path.join(ROOT, 'raw', 'eth', 'lending-split-2026-10-08')
OLD = os.path.join(ROOT, 'raw', 'eth', 'gap-2026-10-07', 'borrower-scan')
os.makedirs(RAW, exist_ok=True)
SNAP = {'eth': dict(ts=1790985599, block1=26108081, label='2026-10-02 23:59:59 UTC'),
        'btc': dict(ts=1790510400, block1=26018583, label='2026-09-20 12:00:00 UTC')}
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/129 Safari/537.36'
RPCS = {
    1: ['https://gateway.tenderly.co/public/mainnet', 'https://eth.drpc.org'],
    8453: ['https://gateway.tenderly.co/public/base', 'https://base.drpc.org'],
    42161: ['https://gateway.tenderly.co/public/arbitrum', 'https://arbitrum.drpc.org'],
    10: ['https://gateway.tenderly.co/public/optimism', 'https://optimism.drpc.org'],
    59144: ['https://gateway.tenderly.co/public/linea', 'https://linea.drpc.org'],
    130: ['https://unichain.drpc.org'],
    137: ['https://polygon.drpc.org', 'https://gateway.tenderly.co/public/polygon'],
    100: ['https://gnosis.drpc.org', 'https://gateway.tenderly.co/public/gnosis'],
    43114: ['https://avalanche.drpc.org', 'https://gateway.tenderly.co/public/avalanche'],
    56: ['https://bsc.drpc.org', 'https://gateway.tenderly.co/public/bsc'],
    747474: ['https://rpc.katana.network'],
    143: ['https://rpc.monad.xyz', 'https://monad.drpc.org'],
    999: ['https://rpc.hyperliquid.xyz/evm'],
    480: ['https://worldchain.drpc.org', 'https://worldchain-mainnet.g.alchemy.com/public'],
    57073: ['https://ink.drpc.org', 'https://rpc-gel.inkonchain.com'],
    988: ['https://rpc.stable.xyz'],
    4217: ['https://rpc.mainnet.tempo.xyz'],
    5042: ['https://rpc.mainnet.arc.io'],
    2818: ['https://rpc.morphl2.io'],
    9745: ['https://rpc.plasma.to', 'https://plasma.drpc.org'],
}
MC3 = '0xcA11bde05977b3631167028862bE2a173976CA11'
STATS = {'req': 0}


def post_raw(url, payload, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'content-type': 'application/json', 'user-agent': UA})
    STATS['req'] += 1
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def rpc(chain, method, params, retries=12):
    urls = RPCS[chain]; last = None
    for i in range(retries):
        u = urls[i % len(urls)] if i < 2 else random.choice(urls)
        try:
            r = post_raw(u, {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})
            if 'error' in r:
                msg = json.dumps(r['error']).lower()
                if 'revert' in msg or 'execution' in msg: return None
                raise Exception(msg[:200])
            return r['result']
        except Exception as e:
            last = e; time.sleep(min(20, 1.5 * (i + 1)))
    raise Exception('rpc failed %s %s: %s' % (chain, method, last))


def tag(b): return b if isinstance(b, str) else hex(b)
def a32(a): return a.lower().replace('0x', '').rjust(64, '0')
def u32(n): return hex(n)[2:].rjust(64, '0')
def words(h):
    h = h[2:] if h and h.startswith('0x') else (h or '')
    return [int(h[i:i + 64], 16) for i in range(0, len(h) - len(h) % 64, 64)]
def U(h, i=0):
    if not h or h == '0x': return 0
    h = h[2:] if h.startswith('0x') else h
    return int(h[64 * i:64 * (i + 1)] or '0', 16)
def A(h, i=0):
    if not h: return None
    h = h[2:] if h.startswith('0x') else h
    if len(h) < 64 * (i + 1): return None
    return '0x' + h[64 * i + 24:64 * (i + 1)]
def dec_str(h):
    if not h or h == '0x': return None
    h = h[2:] if h.startswith('0x') else h
    try:
        if len(h) == 64: return bytes.fromhex(h).rstrip(b'\0').decode(errors='replace')
        off = int(h[:64], 16) * 2; ln = int(h[off:off + 64], 16)
        return bytes.fromhex(h[off + 64:off + 64 + ln * 2]).decode(errors='replace')
    except Exception: return None
def addr_list(h):
    h = h[2:]; n = int(h[64:128], 16)
    return ['0x' + h[128 + 64 * i + 24:128 + 64 * (i + 1)] for i in range(n)]


def _enc_agg3(cl):
    n = len(cl); heads = []; tails = []; off = 32 * n
    for to, data in cl:
        d = bytes.fromhex(data[2:] if data.startswith('0x') else data)
        pad = d + b'\0' * ((32 - len(d) % 32) % 32)
        t = a32(to) + u32(1) + u32(0x60) + u32(len(d)) + pad.hex()
        heads.append(u32(off)); tails.append(t); off += len(t) // 2
    return '0x82ad56cb' + u32(0x20) + u32(n) + ''.join(heads) + ''.join(tails)


def _dec_agg3(h):
    h = h[2:]; n = int(h[64:128], 16); base = 128; out = []
    for i in range(n):
        o = int(h[base + 64 * i:base + 64 * (i + 1)], 16) * 2 + base
        ok = int(h[o:o + 64], 16); do = int(h[o + 64:o + 128], 16) * 2 + o; ln = int(h[do:do + 64], 16)
        out.append('0x' + h[do + 64:do + 64 + ln * 2] if ok else None)
    return out


GAS = {1: 1_500_000_000, 42161: 1_500_000_000, 8453: 1_500_000_000}
def mcall(chain, cl, block, size=250, workers=4):
    """cl: list of (to, calldata). Returns hex results (None on revert). Multicall3 aggregate3 at the block."""
    if not cl: return []
    if chain not in GAS: size = min(size, 100)
    chunks = [cl[i:i + size] for i in range(0, len(cl), size)]
    def run(ch):
        data = _enc_agg3(ch)
        for attempt in range(10):
            try:
                r = rpc(chain, 'eth_call', [{'to': MC3, 'data': data, 'gas': hex(GAS.get(chain, 50_000_000))}, tag(block)])
                if r is None: raise Exception('multicall reverted')
                return _dec_agg3(r)
            except Exception as e:
                if attempt >= 3 and len(ch) > 20:
                    h = len(ch) // 2
                    return run(ch[:h]) + run(ch[h:])
                time.sleep(2 + attempt)
        raise Exception('mcall failed')
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(run, chunks))
    return [x for c in res for x in c]


def call1(chain, to, data, block):
    return rpc(chain, 'eth_call', [{'to': to, 'data': data}, tag(block)])


def getjson(url, retries=8, data=None, headers=None):
    last = None
    for i in range(retries):
        try:
            h = {'user-agent': UA, 'accept': 'application/json'}
            if headers: h.update(headers)
            req = urllib.request.Request(url, data=data, headers=h)
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            last = e; time.sleep(min(30, 3 * (i + 1)))
    return {'_error': str(last)}


def gql(q, variables=None):
    body = json.dumps({'query': q, 'variables': variables or {}}).encode()
    for i in range(6):
        j = getjson('https://api.morpho.org/graphql', data=body, headers={'content-type': 'application/json'})
        if j.get('data') is not None or 'errors' in j: return j
        time.sleep(3 * (i + 1))
    return j


BLOCKS_FILE = os.path.join(RAW, 'blocks.json')
def block_at(chain, side):
    kb = json.load(open(BLOCKS_FILE)) if os.path.exists(BLOCKS_FILE) else {}
    key = '%s_%s' % (side, chain)
    if chain == 1: return SNAP[side]['block1']
    if key in kb: return kb[key]
    if side == 'eth':
        old = json.load(open(os.path.join(OLD, 'blocks_at_T.json')))
        if str(chain) in old:
            kb[key] = old[str(chain)]; json.dump(kb, open(BLOCKS_FILE, 'w'), indent=1); return old[str(chain)]
    ts = SNAP[side]['ts']
    def bt(b): return int(rpc(chain, 'eth_getBlockByNumber', [hex(b), False])['timestamp'], 16)
    head = int(rpc(chain, 'eth_blockNumber', []), 16); hts = bt(head)
    b2 = max(1, head - 200000); t2 = bt(b2); avg = (hts - t2) / (head - b2)
    est = int(head - (hts - ts) / avg)
    lo = max(1, est - 100000); hi = min(head, est + 100000)
    while bt(lo) > ts: lo = max(1, lo - 500000)
    while bt(hi) <= ts and hi < head: hi = min(head, hi + 500000)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if bt(mid) <= ts: lo = mid
        else: hi = mid
    kb[key] = lo; json.dump(kb, open(BLOCKS_FILE, 'w'), indent=1)
    return lo


def save(name, obj):
    p = os.path.join(RAW, name)
    json.dump(obj, open(p, 'w'), indent=1, default=str)
    return p
def load(name):
    p = os.path.join(RAW, name)
    return json.load(open(p)) if os.path.exists(p) else None


# ---------- asset classes ----------
STABLE_RE = re.compile(r'(USD|DAI|GHO|FRAX|LUSD|BOLD|DOLA|EUR|PYUSD|RLUSD|USDS|USDT|USDC|CRVUSD|AUSD|FDUSD|TUSD|USDG|FRXUSD|MIM|RUSD|USR|USD0|USDTB|USDF|USDâ‚®|USD₮)', re.I)
def is_stable(sym):
    if not sym: return False
    s = sym.upper()
    if 'ETH' in s or 'BTC' in s: return False
    return bool(STABLE_RE.search(s))
ETH_EXCL = ('ETHFI', 'ETHENA', 'METHOD', 'ETHX-ALT', 'SETHX', 'ETHW')
PLAIN_ETH = {'WETH', 'ETH', 'WETH.E', 'ETH.E', 'AXLETH', 'WETH9', 'VBETH', 'UETH', 'SUPERWETH', 'WETH.B'}
def is_eth(sym):
    if not sym: return False
    s = sym.upper()
    if any(x in s for x in ETH_EXCL): return False
    if 'USD' in s or 'BTC' in s: return False
    return 'ETH' in s
def eth_form(sym):
    return 'B' if sym.upper() in PLAIN_ETH else 'A'
# BTC: yield-bearing / staking tokens per the BTC study (money_markets ISSUER list); everything else BTC-family is a plain wrapper
BTC_YB = {'LBTC', 'BTCOC', 'LBTCV', 'UNIBTC', 'BRBTC', 'PUMPBTC', 'SOLVBTC.BBN', 'XSOLVBTC', 'SOLVBTC.CORE', 'SOLVBTC.TRADING', 'SOLVBTC.ENA',
          'SOLVBTC.JUP', 'BFBTC', 'GTBTC', 'MHYPERBTC', 'MRE7BTC', 'AHYPERBTC', 'EBTC', 'AVBTC', 'SAVBTC', 'STBTC', 'ASBTC', 'YOBTC',
          'WFRAGBTC', 'SCBTC', 'BEMBTC'}
def is_btc(sym):
    if not sym: return False
    s = sym.upper()
    if 'USD' in s or 'ETH' in s: return False
    return 'BTC' in s
def btc_form(sym):
    s = sym.upper()
    if s.startswith('PT-'): return 'A'
    return 'A' if s in BTC_YB else 'B'
def fam(sym, side):
    """family of an asset relative to the side: 'own' (ETH for eth side, BTC for btc side), 'stable', 'other'"""
    if side == 'eth' and is_eth(sym): return 'own'
    if side == 'btc' and is_btc(sym): return 'own'
    if is_stable(sym): return 'stable'
    return 'other'
def form(sym, side):
    return eth_form(sym) if side == 'eth' else btc_form(sym)


# ---------- explorers ----------
BS = {1: 'https://eth.blockscout.com'}
def bs_holders(chain, token, min_value_raw=0, max_pages=2000):
    url = BS[chain] + '/api/v2/tokens/%s/holders' % token; items = []; nxt = None
    for p in range(max_pages):
        j = getjson(url + ('?' + urllib.parse.urlencode(nxt) if nxt else ''))
        if '_error' in j: items.append({'_error': j['_error']}); break
        its = j.get('items', []); items += its; nxt = j.get('next_page_params')
        if not nxt or not its: break
        if int(its[-1]['value']) < min_value_raw: break
    return [(it['address']['hash'].lower(), int(it['value'])) for it in items if '_error' not in it]

ESCAN = {8453: 'basescan.org', 42161: 'arbiscan.io', 10: 'optimistic.etherscan.io', 59144: 'lineascan.build', 1: 'etherscan.io',
         137: 'polygonscan.com', 100: 'gnosisscan.io', 43114: 'snowscan.xyz', 56: 'bscscan.com'}
def es_holders(chain, token, min_units, max_pages=60):
    out = []
    for p in range(1, max_pages + 1):
        url = 'https://%s/token/generic-tokenholders2?m=light&a=%s&s=0&sid=&p=%d' % (ESCAN[chain], token, p)
        h = ''
        for i in range(4):
            try:
                req = urllib.request.Request(url, headers={'user-agent': UA})
                h = urllib.request.urlopen(req, timeout=60).read().decode('utf8', 'ignore'); break
            except Exception: time.sleep(4 * (i + 1))
        rows = re.findall(r'<tr>(.*?)</tr>', h, re.S); got = 0; last = None
        for r in rows:
            txt = ' '.join(re.sub('<[^>]+>', ' ', r).split()).split(' ')
            ad = [a for a in re.findall(r'0x[0-9a-fA-F]{40}', r) if a.lower() != token.lower()]
            if not ad or len(txt) < 3 or not txt[0].isdigit(): continue
            try: q = float(txt[2].replace(',', ''))
            except Exception: continue
            out.append((ad[0].lower(), q)); got += 1; last = q
        time.sleep(0.8)
        if not got or (last is not None and last < min_units): break
    return out

TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
LOGRPC = {1: ('https://gateway.tenderly.co/public/mainnet', 2_000_000), 42161: ('https://gateway.tenderly.co/public/arbitrum', 20_000_000),
          8453: ('https://gateway.tenderly.co/public/base', 1000), 10: ('https://gateway.tenderly.co/public/optimism', 1000),
          59144: ('https://gateway.tenderly.co/public/linea', 1000), 137: ('https://gateway.tenderly.co/public/polygon', 1000),
          100: ('https://gateway.tenderly.co/public/gnosis', 1000), 43114: ('https://gateway.tenderly.co/public/avalanche', 1000),
          56: ('https://gateway.tenderly.co/public/bsc', 1000)}
def get_logs(chain, address, topics, fb, tb, workers=6):
    url, step0 = LOGRPC[chain]
    if step0 <= 1000:
        rngs = [(b, min(tb, b + step0 - 1)) for b in range(fb, tb + 1, step0)]
        def one(rg):
            for i in range(30):
                try:
                    r = post_raw(url, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{'address': address, 'fromBlock': hex(rg[0]), 'toBlock': hex(rg[1]), 'topics': topics}]})
                    if 'error' in r: raise Exception(str(r['error'])[:200])
                    return r['result']
                except Exception: time.sleep(1 + i)
            raise Exception('logs failed %s' % (rg,))
        with ThreadPoolExecutor(workers) as ex: res = list(ex.map(one, rngs))
        return [l for x in res for l in x]
    out = []; b = fb; step = step0; fails = 0
    while b <= tb:
        e = min(tb, b + step - 1)
        try:
            r = post_raw(url, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{'address': address, 'fromBlock': hex(b), 'toBlock': hex(e), 'topics': topics}]})
            if 'error' in r: raise Exception(str(r['error'])[:200])
            out += r['result']; b = e + 1
            if len(r['result']) < 5000: step = min(step0, int(step * 1.5))
        except Exception as ex:
            fails += 1
            if fails > 300: raise
            if step > 500: step //= 3
            else: time.sleep(3)
    return out


def log(*a):
    print(*a, flush=True)
