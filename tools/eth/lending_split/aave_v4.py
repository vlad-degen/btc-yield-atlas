"""Aave v4 on Ethereum: every (spoke, user) pair that ever supplied or borrowed (Supply / Borrow / SetUsingAsCollateral logs on the 15 spokes,
launch -> head), read at the snapshot: supplied assets and debt per reserve. Prices: Aave v3 Core oracle at the snapshot (same underlyings).
Supplied family assets of an account with debt are treated as collateral (v4 per-reserve collateral flags not read; labelled).
Usage: python3 aave_v4.py <eth|btc>
"""
import sys
from lib import *

TOPICS = ['0xd986db228cb1fe8392c5f45ff5f2c639b7db6cbd9ca7d1fe70b2de90c2c8c961', '0xef18174796a5d2f91d51dc5e907a4d7867bbd6e800f6225168e0453d581d0dcd',
          '0x4763df430bc5274807f8ab4ce0734e7898513638418d6eec0c5285ef85f7f51f']
CORE_ORACLE = '0x54586bE62E3c3580375aE3723C145253060Ca0C2'


def L_pairs():
    p = os.path.join(RAW, 'aave_v4_pairs_all.json')
    return json.load(open(p)) if os.path.exists(p) else None


def main(side):
    B = SNAP[side]['block1']; head = int(rpc(1, 'eth_blockNumber', []), 16)
    spokes = sorted({s for s, _ in json.load(open(os.path.join(OLD, 'aave_v4_pairs.json')))})
    cached = L_pairs()
    pairs = set(map(tuple, cached)) if cached else set(); b = head + 1 if cached else 23_000_000; step = 200_000
    while b <= head:
        e = min(head, b + step - 1)
        try:
            r = post_raw(RPCS[1][0], {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{'address': spokes, 'fromBlock': hex(b), 'toBlock': hex(e), 'topics': [TOPICS]}]})
            if 'error' in r: raise Exception(str(r['error'])[:100])
        except Exception as ex:
            step = max(2000, step // 2); time.sleep(2); continue
        for l in r['result']:
            if len(l['topics']) == 4: pairs.add((l['address'].lower(), '0x' + l['topics'][3][-40:]))
        b = e + 1; step = min(200_000, step * 2)
    if not cached: save('aave_v4_pairs_all.json', sorted(pairs))
    log('pairs', len(pairs))
    ref = U(call1(1, CORE_ORACLE, '0xb3596f07' + a32('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2' if side == 'eth' else '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'), B)) / 1e8
    res = {}
    for sp in spokes:
        n = U(call1(1, sp, '0x99806546', B))
        rr = mcall(1, [(sp, '0x77778db3' + u32(i)) for i in range(n)], B)
        unds = [(i, '0x' + r[26:66], int(r[2 + 64 * 3:2 + 64 * 4], 16)) for i, r in enumerate(rr) if r]
        x = mcall(1, [(u, '0x95d89b41') for _, u, _ in unds] + [(CORE_ORACLE, '0xb3596f07' + a32(u)) for _, u, _ in unds], B)
        rs = []
        for k, (i, und, dec) in enumerate(unds):
            sym = dec_str(x[k]); p = U(x[len(unds) + k]) / 1e8 if x[len(unds) + k] else 0
            if not p and is_stable(sym): p = 1.0
            rs.append(dict(i=i, und=und, sym=sym, dec=dec, price=p, fam=fam(sym, side)))
        res[sp] = rs
    P = sorted(pairs); rows = []
    cl = []
    for sp, u in P:
        for r in res[sp]: cl += [(sp, '0xf1568a89' + u32(r['i']) + a32(u)), (sp, '0x9b7172a6' + u32(r['i']) + a32(u))]
    out = mcall(1, cl, B); k = 0
    for sp, u in P:
        colls = {}; debts = {}; tc = 0
        for r in res[sp]:
            a = U(out[k]) / 10**r['dec']; d = U(out[k + 1]) / 10**r['dec']; k += 2
            if a > 0:
                tc += a * r['price']
                if r['fam'] == 'own': colls[r['sym']] = dict(units=a, usd=a * r['price'], native=a * r['price'] / ref, form=form(r['sym'], side), enabled=True)
            if d > 0: debts[r['sym']] = dict(units=d, usd=d * r['price'], fam=r['fam'])
        if colls:
            rows.append(dict(user=u, spoke=sp, coll_usd=tc, debt_usd=sum(v['usd'] for v in debts.values()), colls=colls, debts=debts))
    save('aave_v4_%s.json' % side, dict(side=side, block=B, ref_price=ref, spokes=res, pairs=len(P), rows=rows))
    log('rows', len(rows), 'native %.0f' % sum(c['native'] for r in rows for c in r['colls'].values()))


if __name__ == '__main__':
    main(sys.argv[1])
