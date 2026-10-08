"""Compound v3 on Base and Optimism (Comet totals only in the lending split): every account of the stablecoin-base Comets with ETH-family
collateral, from SupplyCollateral logs (deployment -> snapshot block), read at the snapshot block: collateralBalanceOf, borrowBalanceOf.
One base asset per Comet, so eth_backing_dollar = all ETH-family collateral of an account with debt in a stablecoin Comet.
ETH-family tokens converted to ETH at the Aave oracle ratios of the lending-split captures (build.rate_map), 1.0 if missing.

Usage: python3 compound_l2.py [chain ...]   (default 8453 10)
Output: raw/eth/carry-sweep-2026-10-08/venues/compound_<chain>.json
"""
import sys
import sweep_lib as S
from build import rate_map
from lib import mcall, call1, rpc, dec_str, U, A, a32, u32, fam, log, is_stable

SC = '0xfa56f7b24f17183d81894d3ac2ee654e3c26388d17a28dbd9549b8114304e1f4'
COMETS = {8453: [('cUSDCv3', '0xb125E6687d4313864e53df431d5425969c15Eb2F'), ('cUSDbCv3', '0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf'),
                 ('cUSDSv3', '0x2c776041CCFe903071AF44aa147368a9c8EEA518')],
          10: [('cUSDCv3', '0x2e44e174f7D53F0212823acC11C01A11d58c5bCB'), ('cUSDTv3', '0x995E394b8B2437aC8Ce61Ee0bC610D617962B214')]}


def deploy_block(ch, addr, B):
    lo, hi = 0, B
    while hi - lo > 1:
        m = (lo + hi) // 2
        c = rpc(ch, 'eth_getCode', [addr, hex(m)])
        if c and c != '0x': hi = m
        else: lo = m
    return hi


def scan(ch):
    B = S.block_at(ch); rm = rate_map('eth'); pos = []; meta = []
    for name, comet in COMETS[ch]:
        base = A(call1(ch, comet, '0xc55dae63', B))
        r = mcall(ch, [(base, '0x95d89b41'), (base, '0x313ce567'), (comet, '0xa46fe83b'), (comet, '0x8285ef40')], B)
        bsym = dec_str(r[0]); bdec = U(r[1]); n = U(r[2]); tbor = U(r[3]) / 10**bdec
        infos = mcall(ch, [(comet, '0xc8c7fe6b' + u32(i)) for i in range(n)], B)
        assets = [dict(asset='0x' + x[2:][64 + 24:128], scale=int(x[2:][192:256], 16)) for x in infos]
        r2 = mcall(ch, [(x['asset'], '0x95d89b41') for x in assets] + [(x['asset'], '0x70a08231' + a32(comet)) for x in assets], B)
        for i, x in enumerate(assets):
            x['sym'] = dec_str(r2[i]); x['total'] = U(r2[len(assets) + i]) / x['scale']
        own = [x for x in assets if fam(x['sym'], 'eth') == 'own' and x['total'] > 0]
        m = dict(comet=name, address=comet, base=bsym, total_borrow=round(tbor), block=B, eth_collateral={x['sym']: round(x['total'], 3) for x in own})
        if not own or not is_stable(bsym): meta.append(m); continue
        start = deploy_block(ch, comet, B)
        users = set(); nl = 0
        for x in own:
            lg = S.logs(ch, comet, [SC, None, None, '0x' + a32(x['asset'])], start, B)
            nl += len(lg); users |= {'0x' + l['topics'][2][-40:] for l in lg}
        us = sorted(users)
        cl = [(comet, '0x374c49b4' + a32(u)) for u in us]
        for x in own: cl += [(comet, '0x5c2549ee' + a32(u) + a32(x['asset'])) for u in us]
        res = mcall(ch, cl, B); k = len(us)
        read = {x['sym']: 0.0 for x in own}; back_all = 0.0; debt_read = 0.0
        for i, u in enumerate(us):
            debt = U(res[i]) / 10**bdec; colls = {}
            for j, x in enumerate(own):
                v = U(res[k * (j + 1) + i]) / x['scale']
                if v > 0: colls[x['sym']] = v; read[x['sym']] += v
            nat = sum(v * rm.get(s.upper(), 1.0) for s, v in colls.items())
            if debt > 0 and nat > 0:
                back_all += nat; debt_read += debt
                if nat >= 100:
                    pos.append(S.pos('compound-v3', ch, B, u, nat, colls.keys(), debt, 0.0, nat, comet=name, colls_units={s: round(v, 4) for s, v in colls.items()}))
        m.update(deploy_block=start, logs=nl, accounts=len(us), collateral_read={s: round(v, 3) for s, v in read.items()},
                 coverage_collateral=round(sum(read.values()) / sum(x['total'] for x in own), 4), eth_backing_dollar_total=round(back_all, 2),
                 debt_of_eth_collateral_accounts_usd=round(debt_read))
        meta.append(m); log(ch, m)
    kinds = S.code_kinds((ch, B, p['account']) for p in pos)
    for p in pos: p['code_kind'] = kinds[(ch, p['account'])]
    pos.sort(key=lambda p: -p['eth_backing_dollar'])
    S.write('compound_%d' % ch, meta, pos)


if __name__ == '__main__':
    for c in (sys.argv[1:] or ['8453', '10']):
        try: scan(int(c))
        except Exception as e: log('FAILED', c, repr(e)[:300])
