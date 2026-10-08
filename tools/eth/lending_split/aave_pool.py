"""Aave v3 style pools (Aave Core/Prime/EtherFi, Spark, Aave L2 deployments): every account holding the side's collateral family at the snapshot.

Usage: python3 aave_pool.py <eth|btc> <venue> [<venue> ...]
Enumeration: holders of every ETH-family (or BTC-family) aToken now (Blockscout on Ethereum, Etherscan-family holder pages on L2s), down to
MIN_USD, plus every address that sent or burned the aToken after the snapshot (Transfer logs, snapshot+1 -> head; Ethereum, Arbitrum, Base).
State at the snapshot block: getUserConfiguration, aToken balanceOf (own family), getUserAccountData, variable-debt balanceOf for borrow bits.
"""
import sys
from lib import *

POOLS = {'aave-core': (1, '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'), 'aave-prime': (1, '0x4e033931ad43597d96D6bcc25c280717730B58B1'),
         'aave-etherfi': (1, '0x0AA97c284e98396202b6A04024F5E2c65026F3c0'), 'spark': (1, '0xC13e21B648A5Ee794902342038FF3aDAB66BE987'),
         'aave-base': (8453, '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5'), 'aave-arbitrum': (42161, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'),
         'aave-optimism': (10, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'), 'aave-linea': (59144, '0xc47b8C00b0f69a36fa203Ffeac0334874574a8Ac'),
         'aave-polygon': (137, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'), 'aave-avalanche': (43114, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'),
         'aave-gnosis': (100, '0xb50201558B00496A145fE76f7424749556E326D8'), 'aave-bnb': (56, '0x6807dc923806fE8Fd134338EABCA509979a7e0cB')}
MIN_USD = {1: 1000}
LOG_CHAINS = (1, 42161, 8453)


def reserves_at(ch, pool, B, side):
    assets = addr_list(call1(ch, pool, '0xd1946dbc', B))
    r1 = mcall(ch, [(a, '0x95d89b41') for a in assets] + [(a, '0x313ce567') for a in assets] + [(pool, '0x35ea6a75' + a32(a)) for a in assets], B)
    n = len(assets); syms = [dec_str(x) for x in r1[:n]]; decs = [U(x) for x in r1[n:2 * n]]; rd = r1[2 * n:]
    prov = A(call1(ch, pool, '0x0542975c', B)); orc = A(call1(ch, prov, '0xfca513a8', B))
    unit = U(call1(ch, orc, '0x8c89b64f', B)) or 10**8
    pr = mcall(ch, [(orc, '0xb3596f07' + a32(a)) for a in assets], B)
    res = []
    for a, s, d, r, p in zip(assets, syms, decs, rd, pr):
        w = r[2:]
        res.append(dict(asset=a, sym=s, dec=d, id=int(w[64 * 7:64 * 8], 16), aToken='0x' + w[64 * 8 + 24:64 * 9], vDebt='0x' + w[64 * 10 + 24:64 * 11],
                        price=U(p) / unit, fam=fam(s, side)))
    ts = mcall(ch, [(r['aToken'], '0x18160ddd') for r in res] + [(r['vDebt'], '0x18160ddd') for r in res], B)
    for i, r in enumerate(res):
        r['supply'] = U(ts[i]) / 10**r['dec']; r['debt'] = U(ts[n + i]) / 10**r['dec']
        r['supply_usd'] = r['supply'] * r['price']; r['debt_usd'] = r['debt'] * r['price']
        if r['fam'] == 'own': r['form'] = form(r['sym'], side)
    return res, orc, unit


def ref_price(res, side):
    by = {r['sym'].upper(): r['price'] for r in res if r['price']}
    for k in (('WETH', 'WETH.E', 'ETH') if side == 'eth' else ('WBTC', 'CBBTC', 'BTCB', 'BTC.B', 'WBTC.E', 'TBTC')):
        if k in by: return by[k]
    return None


def scan(side, name):
    ch, pool = POOLS[name]
    B = block_at(ch, side)
    head = int(rpc(ch, 'eth_blockNumber', []), 16)
    res, orc, unit = reserves_at(ch, pool, B, side)
    ref = ref_price(res, side)
    if ref is None:
        core = '0x54586bE62E3c3580375aE3723C145253060Ca0C2'
        tok = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2' if side == 'eth' else '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'
        ref = U(call1(1, core, '0xb3596f07' + a32(tok), SNAP[side]['block1'])) / 1e8
    own = [r for r in res if r['fam'] == 'own' and r['supply'] > 0]
    log('==', side, name, 'block', B, 'ref price', ref, 'own reserves', [(r['sym'], round(r['supply'], 1), round(r['debt'], 1)) for r in own])
    cands = set(); hc = {}
    for r in own:
        if r['supply_usd'] < 50_000: continue
        thr_units = MIN_USD.get(ch, 20_000) / max(r['price'], 1e-9)
        if ch == 1:
            hs = bs_holders(ch, r['aToken'], int(thr_units * 10**r['dec']))
            hs = [(a, v / 10**r['dec']) for a, v in hs]
        elif ch in ESCAN:
            hs = es_holders(ch, r['aToken'], thr_units)
        else:
            hs = []
        n0 = len(cands)
        for a, v in hs: cands.add(a)
        ex = set()
        if ch in LOG_CHAINS:
            try:
                lg = get_logs(ch, r['aToken'], [TRANSFER], B + 1, head)
                for l in lg:
                    if len(l['topics']) >= 2: ex.add('0x' + l['topics'][1][-40:])
            except Exception as e:
                log('  logs fail', r['sym'], str(e)[:120])
        cands |= ex
        hc[r['sym']] = dict(holders_listed=len(hs), senders_after_snapshot=len(ex))
        log('  ', r['sym'], 'holders', len(hs), 'senders after', len(ex), 'cands total', len(cands))
    cands.discard('0x0000000000000000000000000000000000000000')
    users = sorted(cands)
    # pass 1: own aToken balances + configuration
    cl = []
    for u in users:
        cl.append((pool, '0x4417a583' + a32(u)))
        for r in own: cl.append((r['aToken'], '0x70a08231' + a32(u)))
    out = mcall(ch, cl, B)
    k = len(own) + 1; held = []
    for i, u in enumerate(users):
        chunk = out[i * k:(i + 1) * k]
        cfg = U(chunk[0]); bals = {r['sym']: U(x) / 10**r['dec'] for r, x in zip(own, chunk[1:])}
        if any(v > 0 for v in bals.values()): held.append((u, cfg, bals))
    log('  candidates', len(users), 'holding own family at snapshot', len(held))
    byid = {r['id']: r for r in res}
    need = []
    for u, cfg, bals in held:
        need.append((u, None, 'acct'))
        for rid, r in byid.items():
            if (cfg >> (2 * rid)) & 1: need.append((u, r, 'd'))
    vals = mcall(ch, [((pool, '0xbf92857c' + a32(u)) if r is None else (r['vDebt'], '0x70a08231' + a32(u))) for u, r, kk in need], B)
    per = {}
    for (u, r, kk), v in zip(need, vals):
        per.setdefault(u, []).append((r, kk, v))
    rows = []
    for u, cfg, bals in held:
        coll = debt = 0; debts = {}
        for r, kk, v in per.get(u, []):
            if kk == 'acct':
                w = words(v) if v else [0] * 6
                coll = w[0] / unit; debt = w[1] / unit
            else:
                x = U(v) / 10**r['dec']
                if x > 0: debts[r['sym']] = dict(units=x, usd=x * r['price'], fam=r['fam'])
        colls = {}
        for r in own:
            x = bals[r['sym']]
            if x <= 0: continue
            en = bool((cfg >> (2 * r['id'] + 1)) & 1)
            colls[r['sym']] = dict(units=x, usd=x * r['price'], native=x * r['price'] / ref, form=r['form'], enabled=en)
        rows.append(dict(user=u, coll_usd=coll, debt_usd=debt, colls=colls, debts=debts))
    tot_native = {r['sym']: r['supply'] * r['price'] / ref for r in own}
    read_native = {}
    for x in rows:
        for s, c in x['colls'].items(): read_native[s] = read_native.get(s, 0) + c['native']
    cov = sum(read_native.values()) / sum(tot_native.values()) if tot_native else None
    log('  coverage %.2f%%' % (100 * cov if cov else 0), {s: round(read_native.get(s, 0) / v, 4) for s, v in tot_native.items() if v})
    obj = dict(venue=name, side=side, chain=ch, pool=pool, block=B, head_at_scan=head, oracle=orc, ref_price=ref, reserves=res, holder_counts=hc,
               candidates=len(users), accounts=len(rows), coverage=cov, rows=rows)
    save('aave_%s_%s.json' % (side, name), obj)


if __name__ == '__main__':
    side = sys.argv[1]
    for nm in sys.argv[2:]:
        scan(side, nm)
