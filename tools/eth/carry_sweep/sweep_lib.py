"""Shared bits for the carry sweep venue scripts: CSV exclusion set, code kind at the snapshot block, output writer."""
import csv, json, os
from concurrent.futures import ThreadPoolExecutor
from common import ROOT, rpc, log  # noqa  (common inserts tools/eth/lending_split on sys.path)
import lib as L

ETH_PX = 2666.40
VOUT = os.path.join(ROOT, 'raw', 'eth', 'carry-sweep-2026-10-08', 'venues')
os.makedirs(VOUT, exist_ok=True)


def csv_keys():
    """(venue, chain, account-lower) already in data/eth/lending_split_accounts.csv (ETH side)"""
    ks = set()
    for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'eth', 'lending_split_accounts.csv'))):
        if r['side'] == 'eth': ks.add((r['venue'], int(r['chain']), r['account'].lower()))
    return ks


def code_kinds(pairs, workers=8):
    """pairs: iterable of (chain, block, address). Returns {(chain, address): kind}"""
    pairs = sorted(set(pairs))
    def one(p):
        ch, b, a = p
        try: c = rpc(ch, 'eth_getCode', [a, hex(b)]) or '0x'
        except Exception as e: return p, 'unknown'
        if c in ('0x', ''): return p, 'EOA'
        if c.startswith('0xef0100'): return p, 'EIP-7702'
        return p, 'contract'
    with ThreadPoolExecutor(workers) as ex:
        res = dict(ex.map(one, pairs))
    return {(ch, a): k for (ch, b, a), k in res.items()}


def write(name, meta, positions):
    p = os.path.join(VOUT, name + '.json')
    json.dump({'meta': meta, 'positions': positions}, open(p, 'w'), indent=1, default=str)
    log('wrote', p, len(positions), 'positions')
    return p


def pos(venue, chain, block, account, eth_coll, syms, dollar_debt, other_debt, backing, kind=None, **kw):
    d = dict(venue=venue, chain=chain, block=block, account=account, eth_collateral=round(eth_coll, 4), collateral_symbols=sorted(syms),
             dollar_debt_usd=round(dollar_debt), other_debt_usd=round(other_debt), eth_backing_dollar=round(backing, 4), code_kind=kind)
    d.update(kw)
    return d


def aave_rows_positions(venue, chain, block, rows, ref, min_eth=100, skip=frozenset()):
    """Aave v3 style rows (aave_pool.py format) -> positions with eth_backing_dollar >= min_eth (pro rata by debt USD, enabled collateral)"""
    out = []
    for r in rows:
        D = sum(d['usd'] for d in r['debts'].values())
        st = sum(d['usd'] for d in r['debts'].values() if d['fam'] == 'stable')
        if D <= 0 or st <= 0: continue
        en = sum(c['native'] for c in r['colls'].values() if c.get('enabled', True))
        back = en * st / D
        if back < min_eth: continue
        if (venue, chain, r['user']) in skip: continue
        out.append(pos(venue, chain, block, r['user'], sum(c['native'] for c in r['colls'].values()), r['colls'].keys(), st, D - st, back,
                       collateral_enabled_eth=round(en, 4), debts={s: round(d['usd']) for s, d in r['debts'].items()}))
    return out


# ---------- extra chains (runtime additions to lib.RPCS; nothing in tools/eth/lending_split is edited) ----------
EXTRA_RPCS = {
    146: ['https://rpc.soniclabs.com', 'https://sonic-rpc.publicnode.com'],
    534352: ['https://rpc.scroll.io', 'https://scroll-rpc.publicnode.com'],
    324: ['https://mainnet.era.zksync.io'],
    5000: ['https://rpc.mantle.xyz', 'https://mantle.drpc.org'],
    1088: ['https://andromeda.metis.io/?owner=1088', 'https://metis-rpc.publicnode.com'],
    42220: ['https://forno.celo.org', 'https://rpc.ankr.com/celo'],
    9745: ['https://rpc.plasma.to'],
    56: ['https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3'],
    100: ['https://rpc.gnosischain.com', 'https://gnosis.drpc.org'],
    137: ['https://gateway.tenderly.co/public/polygon', 'https://polygon.drpc.org'],
    43114: ['https://gateway.tenderly.co/public/avalanche', 'https://api.avax.network/ext/bc/C/rpc'],
    59144: ['https://gateway.tenderly.co/public/linea', 'https://rpc.linea.build'],
    10: ['https://gateway.tenderly.co/public/optimism', 'https://mainnet.optimism.io'],
    999: ['https://hyperliquid-json-rpc.stakely.io', 'https://rpc.hyperlend.finance'],  # rpc.hyperliquid.xyz/evm ignores the block tag (returns latest state)
}
EXTRA_RPCS[42161] = ['https://gateway.tenderly.co/public/arbitrum', 'https://arbitrum-one.public.blastapi.io']
for _c, _u in EXTRA_RPCS.items():
    L.RPCS[_c] = _u
# eth_getLogs endpoints and the widest block range each accepts (measured 2026-10-08)
LOGS = {
    1: [('https://gateway.tenderly.co/public/mainnet', 2_000_000), ('https://ethereum-rpc.publicnode.com', 50_000)],
    42161: [('https://gateway.tenderly.co/public/arbitrum', 20_000_000)],
    8453: [('https://gateway.tenderly.co/public/base', 500_000), ('https://base-rpc.publicnode.com', 50_000), ('https://mainnet.base.org', 10_000)],
    10: [('https://gateway.tenderly.co/public/optimism', 2_000_000)],
    137: [('https://gateway.tenderly.co/public/polygon', 2_000_000)],
    59144: [('https://gateway.tenderly.co/public/linea', 2_000_000)],
    43114: [('https://gateway.tenderly.co/public/avalanche', 2_000_000), ('https://api.avax.network/ext/bc/C/rpc', 1_000_000)],
    100: [('https://rpc.gnosischain.com', 100_000)],
    146: [('https://rpc.soniclabs.com', 1_000_000)],
    534352: [('https://rpc.scroll.io', 1_000_000)],
    324: [('https://mainnet.era.zksync.io', 1_000_000)],
    5000: [('https://mantle-rpc.publicnode.com', 50_000)],
    1088: [('https://andromeda.metis.io/?owner=1088', 1_000_000), ('https://metis-rpc.publicnode.com', 50_000)],
    42220: [('https://celo-json-rpc.stakely.io', 100_000)],
    9745: [('https://rpc.plasma.to', 100_000)],
    56: [('https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3', 50_000)],
    999: [('https://hyperliquid-json-rpc.stakely.io', 1000), ('https://rpc.hyperliquid.xyz/evm', 1000), ('https://rpc.hyperlend.finance', 1000)],  # logs are fine on all three
}
BLOCKS_FILE = os.path.join(VOUT, 'blocks_extra.json')
SNAP_TS = 1790985599


def block_at(chain):
    """last block with timestamp <= snapshot; lending-split cache first (read only), then our own cache"""
    kb = json.load(open(L.BLOCKS_FILE)) if os.path.exists(L.BLOCKS_FILE) else {}
    if chain == 1: return 26108081
    if 'eth_%d' % chain in kb: return kb['eth_%d' % chain]
    own = json.load(open(BLOCKS_FILE)) if os.path.exists(BLOCKS_FILE) else {}
    if str(chain) in own: return own[str(chain)]
    def bt(b): return int(rpc(chain, 'eth_getBlockByNumber', [hex(b), False])['timestamp'], 16)
    head = int(rpc(chain, 'eth_blockNumber', []), 16); hts = bt(head)
    b2 = max(1, head - 200000); t2 = bt(b2); avg = (hts - t2) / (head - b2)
    est = int(head - (hts - SNAP_TS) / avg)
    lo = max(1, est - 200000); hi = min(head, est + 200000)
    while bt(lo) > SNAP_TS: lo = max(1, lo - 1_000_000)
    while bt(hi) <= SNAP_TS and hi < head: hi = min(head, hi + 1_000_000)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if bt(mid) <= SNAP_TS: lo = mid
        else: hi = mid
    own[str(chain)] = lo; json.dump(own, open(BLOCKS_FILE, 'w'), indent=1)
    return lo


def logs(chain, address, topics, fb, tb, workers=4, step=None):
    """eth_getLogs over [fb, tb] in fixed windows, splitting a window on error or on oversize responses"""
    import random, time
    from concurrent.futures import ThreadPoolExecutor
    eps = LOGS[chain]; st = step or eps[0][1]
    def get(lo, hi, depth=0):
        last = None
        for i in range(40):
            url = eps[(i + depth) % len(eps)][0]
            try:
                r = L.post_raw(url, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs',
                                     'params': [{'address': address, 'fromBlock': hex(lo), 'toBlock': hex(hi), 'topics': topics}]}, timeout=90)
                if 'error' in r: raise Exception(str(r['error'])[:200])
                return r['result']
            except Exception as e:
                last = str(e)
                if 'HTTP Error 429' in last or 'too many requests' in last.lower():
                    time.sleep(min(60, 3 * (i + 1)) + random.random() * 5); continue
                if hi > lo and any(k in last.lower() for k in ('range', 'limit', 'too large', 'exceed', 'size', '413', 'timeout', 'timed out', 'max', 'more than', 'results')):
                    m = (lo + hi) // 2
                    return get(lo, m, depth + 1) + get(m + 1, hi, depth + 1)
                time.sleep(1 + i + random.random())
        raise Exception('logs failed %s %s-%s: %s' % (chain, lo, hi, last))
    rngs = [(b, min(tb, b + st - 1)) for b in range(fb, tb + 1, st)]
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(lambda r: get(*r), rngs))
    return [l for x in res for l in x]


def ref_price(res, chain=None, block=None):
    """ETH price used to convert ETH-family collateral to ETH units: the pool's own WETH price, else Aave Core's WETH price at the snapshot"""
    by = {r['sym'].upper(): r['price'] for r in res if r.get('price')}
    for k in ('WETH', 'WETH.E', 'ETH', 'UETH', 'WETH.B'):
        if k in by: return by[k]
    core = '0x54586bE62E3c3580375aE3723C145253060Ca0C2'
    return L.U(L.call1(1, core, '0xb3596f07' + L.a32('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'), 26108081)) / 1e8
