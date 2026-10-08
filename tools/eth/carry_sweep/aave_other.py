"""Aave v3 style pools not enumerated by the lending split (and a borrower-complete re-read of the partly enumerated ones):
every account with a dollar (stablecoin) debt at the snapshot, from the pool's Borrow events on stablecoin reserves
(deployment -> snapshot block; a variable debt can only arise from a Borrow event whose onBehalfOf is the account),
then state at the snapshot block: getUserConfiguration, ETH-family aToken balances, getUserAccountData, debt token balances.

eth_backing_dollar = enabled ETH-family collateral x dollar debt / total debt (USD), as tools/eth/lending_split/build.py does.
Coverage is complete by construction for dollar debt (every stablecoin borrower read); rows keep only accounts holding ETH-family aTokens.

Usage: python3 aave_other.py <venue> [<venue> ...]   (venues in POOLS; 'all' = every pool not on Ethereum)
Output: raw/eth/carry-sweep-2026-10-08/venues/aave_<venue>.json (positions >= 100 ETH) and aave_<venue>_rows.json (every account read)
"""
import json, os, sys, time
import sweep_lib as S
import lib as L
from lib import mcall, call1, rpc, addr_list, dec_str, U, A, a32, words, fam, form, log

BORROW = '0xb3d084820fb1a9decffb176436bd02558d15fac9b0ddfed8c465bc7359d7dce0'
POOLS = {
    'aave-optimism': (10, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'),
    'aave-polygon': (137, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'),
    'aave-linea': (59144, '0xc47b8C00b0f69a36fa203Ffeac0334874574a8Ac'),
    'aave-gnosis': (100, '0xb50201558B00496A145fE76f7424749556E326D8'),
    'spark-gnosis': (100, '0x2Dae5307c5E3FD1CF5A72Cb6F698f915860607e0'),
    'aave-avalanche': (43114, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'),
    'aave-bnb': (56, '0x6807dc923806fE8Fd134338EABCA509979a7e0cB'),
    'aave-plasma': (9745, '0x925a2A7214Ed92428B5b1B090F80b25700095e12'),
    'aave-mantle': (5000, '0x458F293454fE0d67EC0655f3672301301DD51422'),
    'aave-sonic': (146, '0x5362dBb1e601abF3a4c14c22ffEdA64042E5eAA3'),
    'aave-celo': (42220, '0x3E59A31363E2ad014dcbc521c4a0d5757d9f3402'),
    'aave-scroll': (534352, '0x11fCfe756c05AD438e312a7fd934381537D3cFfe'),
    'aave-zksync': (324, '0x78e30497a3c7527d953c6B1E3541b021A98Ac43c'),
    'aave-metis': (1088, '0x90df02551bB792286e8D4f13E0e357b4Bf1D6a57'),
    'aave-arbitrum': (42161, '0x794a61358D6845594F94dc1DB02A252b5b4814aD'),
    'aave-base': (8453, '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5'),
    'aave-core': (1, '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'),
    # HyperEVM Aave v3 forks
    'hyperlend': (999, '0x00A89d7a5A02160f20150EbEA7a2b5E4879A1A8b'),
    'hypurrfi': (999, '0xceCcE0EB9DD2Ef7996e01e25DD70e461F918A14b'),
}
MC3 = {324: '0xF9cda624FBC7e059355ce98a31693d299FACd963'}
ALREADY = {'aave-arbitrum', 'aave-base', 'aave-core'}  # enumerated in the lending split; report only accounts not in the CSV or lowband list


def reserves_at(ch, pool, B):
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
                        price=U(p) / unit, fam=fam(s, 'eth')))
    ts = mcall(ch, [(r['aToken'], '0x18160ddd') for r in res] + [(r['vDebt'], '0x18160ddd') for r in res], B)
    for i, r in enumerate(res):
        r['supply'] = U(ts[i]) / 10**r['dec']; r['debt'] = U(ts[n + i]) / 10**r['dec']
        r['supply_usd'] = r['supply'] * r['price']; r['debt_usd'] = r['debt'] * r['price']
        if r['fam'] == 'own': r['form'] = form(r['sym'], 'eth')
    return res, orc, unit


def deploy_block(ch, addr, B):
    lo, hi = 0, B
    if rpc(ch, 'eth_getCode', [addr, hex(B)]) in ('0x', None): return None
    while hi - lo > 1:
        m = (lo + hi) // 2
        try: c = rpc(ch, 'eth_getCode', [addr, hex(m)])
        except Exception: c = '0x'  # pruned / unavailable state: treat as not deployed (search moves later, logs start earlier is safe)
        if c and c != '0x': hi = m
        else: lo = m
    return hi


def read_accounts(ch, pool, B, res, unit, users):
    own = [r for r in res if r['fam'] == 'own' and r['supply'] > 0]
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
    byid = {r['id']: r for r in res}
    need = []
    for u, cfg, bals in held:
        need.append((u, None))
        for rid, r in byid.items():
            if (cfg >> (2 * rid)) & 1: need.append((u, r))
    vals = mcall(ch, [((pool, '0xbf92857c' + a32(u)) if r is None else (r['vDebt'], '0x70a08231' + a32(u))) for u, r in need], B)
    per = {}
    for (u, r), v in zip(need, vals): per.setdefault(u, []).append((r, v))
    ref = S.ref_price(res, ch, B)
    rows = []
    for u, cfg, bals in held:
        coll = debt = 0; debts = {}
        for r, v in per.get(u, []):
            if r is None:
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
    return rows, ref


def scan(name, skip):
    ch, pool = POOLS[name]
    if ch in MC3: L.MC3 = MC3[ch]
    else: L.MC3 = '0xcA11bde05977b3631167028862bE2a173976CA11'
    B = S.block_at(ch)
    res, orc, unit = reserves_at(ch, pool, B)
    ref = S.ref_price(res, ch, B)
    own = [r for r in res if r['fam'] == 'own' and r['supply'] > 0]
    stab = [r for r in res if r['fam'] == 'stable' and r['debt'] > 0]
    own_native = sum(r['supply'] * r['price'] / ref for r in own)
    stable_debt = sum(r['debt_usd'] for r in stab)
    log('==', name, ch, 'block', B, 'ref', round(ref, 2), 'ETH-family supply %.1f' % own_native, [(r['sym'], round(r['supply'], 1)) for r in own],
        'stable debt $%.1fM' % (stable_debt / 1e6))
    meta = dict(venue=name, chain=ch, pool=pool, block=B, ref_eth_price=ref, oracle=orc,
                eth_family_supply_native=round(own_native, 3), eth_family_reserves={r['sym']: round(r['supply'], 4) for r in own},
                stable_debt_usd=round(stable_debt), stable_reserves={r['sym']: round(r['debt_usd']) for r in stab})
    if own_native < 100 or not stab:
        meta['note'] = 'ETH-family supply under 100 ETH or no stablecoin debt: no position can reach 100 ETH; not enumerated'
        S.write('aave_' + name, [meta], []); return meta
    t0 = time.time()
    start = deploy_block(ch, pool, B) or 1
    lg = S.logs(ch, pool, [BORROW, ['0x' + a32(r['asset']) for r in stab]], start, B)
    users = sorted({'0x' + l['topics'][2][-40:] for l in lg})
    log('  borrow logs', len(lg), 'from block', start, 'accounts', len(users), '%.0fs' % (time.time() - t0))
    rows, ref = read_accounts(ch, pool, B, res, unit, users)
    st_read = sum(d['usd'] for r in rows for d in r['debts'].values() if d['fam'] == 'stable')
    back_all = 0.0
    for r in rows:
        D = sum(d['usd'] for d in r['debts'].values()); st = sum(d['usd'] for d in r['debts'].values() if d['fam'] == 'stable')
        if D > 0: back_all += sum(c['native'] for c in r['colls'].values() if c['enabled']) * st / D
    allpos = S.aave_rows_positions(name, ch, B, rows, ref, 100)
    pos = [p for p in allpos if (name, ch, p['account']) not in skip]
    kinds = S.code_kinds((ch, B, p['account']) for p in pos)
    for p in pos: p['code_kind'] = kinds[(ch, p['account'])]
    pos.sort(key=lambda p: -p['eth_backing_dollar'])
    meta.update(enumeration='Borrow events on stablecoin reserves, block %d -> %d (%d logs, %d accounts)' % (start, B, len(lg), len(users)),
                borrowers_read=len(users), accounts_read=len(rows), stable_debt_read_usd=round(st_read), stable_debt_of_eth_collateral_accounts_share=round(st_read / stable_debt, 4) if stable_debt else None,
                eth_backing_dollar_total=round(back_all, 2), positions_ge100=len(allpos), positions_ge100_eth=round(sum(p['eth_backing_dollar'] for p in allpos), 2),
                share_in_ge100=round(sum(p['eth_backing_dollar'] for p in allpos) / back_all, 4) if back_all else None,
                new_positions_ge100=len(pos), new_positions_ge100_eth=round(sum(p['eth_backing_dollar'] for p in pos), 2))
    if name in ALREADY: meta['note'] = 'positions: only accounts not in data/eth/lending_split_accounts.csv and not in venues/lowband_existing.json'
    json.dump(dict(meta=meta, reserves=res, rows=rows), open(os.path.join(S.VOUT, 'aave_%s_rows.json' % name), 'w'), indent=1, default=str)
    S.write('aave_' + name, [meta], pos)
    log('  ', {k: meta[k] for k in ('accounts_read', 'stable_debt_of_eth_collateral_accounts_share', 'eth_backing_dollar_total', 'positions_ge100', 'positions_ge100_eth', 'new_positions_ge100', 'new_positions_ge100_eth')})
    return meta


def main():
    names = sys.argv[1:]
    if names == ['all']: names = [n for n, (c, _) in POOLS.items() if c != 1 and n not in ALREADY and n not in ('hyperlend', 'hypurrfi')]
    skip = set(S.csv_keys())
    lb = os.path.join(S.VOUT, 'lowband_existing.json')
    if os.path.exists(lb):
        for p in json.load(open(lb))['positions']: skip.add((p['venue'], p['chain'], p['account']))
    for n in names:
        try: scan(n, skip)
        except Exception as e:
            log('FAILED', n, repr(e)[:300])
            S.write('aave_' + n, [dict(venue=n, chain=POOLS[n][0], pool=POOLS[n][1], error=repr(e)[:500])], [])


if __name__ == '__main__':
    main()
