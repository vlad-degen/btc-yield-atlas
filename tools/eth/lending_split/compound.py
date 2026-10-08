"""Compound v3 (one base asset per Comet): collateral of the side's family split by the Comet's base asset; collateral of accounts with no
borrow goes to 'nothing'. Base asset of the side's family (cWETHv3, cwstETHv3, cWBTCv3): lender supply and the part lent out.

Usage: python3 compound.py <eth|btc> <chainId> [...]
Accounts: every SupplyCollateral log for a family asset (deployment -> head) on Ethereum and Arbitrum, read at the snapshot:
collateralBalanceOf(user, asset), borrowBalanceOf(user). Base and Optimism: Comet totals only (totalsCollateral at the snapshot),
the no-borrow share estimated from the Ethereum Comets with the same base asset.
"""
import sys
from lib import *

SC = '0xfa56f7b24f17183d81894d3ac2ee654e3c26388d17a28dbd9549b8114304e1f4'
COMETS = {1: [('cUSDCv3', '0xc3d688B66703497DAA19211EEdff47f25384cdc3', 15331586), ('cWETHv3', '0xA17581A9E3356d9A858b789D68B4d866e593aE94', 16400000),
              ('cUSDTv3', '0x3Afdc9BCA9213A35503b077a6072F3D0d5AB0840', 20190000), ('cwstETHv3', '0x3D0bb1ccaB520A66e607822fC55BC921738fAFE3', 20600000),
              ('cUSDSv3', '0x5D409e56D886231aDAf00c8775665AD0f9897b56', 21000000), ('cWBTCv3', '0xe85Dc543813B8c2CFEaAc371517b925a166a9293', 21500000)],
          42161: [('cUSDC.ev3', '0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA', 87000000), ('cUSDCv3', '0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf', 87335000),
                  ('cWETHv3', '0x6f7D514bbD4aFf3BcD1140B7344b32f063dEe486', 150000000), ('cUSDTv3', '0xd98Be00b5D27fc98112BdE293e487f8D4cA57d07', 210000000)],
          8453: [('cUSDCv3', '0xb125E6687d4313864e53df431d5425969c15Eb2F', 0), ('cUSDbCv3', '0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf', 0),
                 ('cWETHv3', '0x46e6b214b524310239732D51387075E0e70970bf', 0), ('cAEROv3', '0x784efeB622244d2348d4F2522f8860B96fbEcE89', 0),
                 ('cUSDSv3', '0x2c776041CCFe903071AF44aa147368a9c8EEA518', 0)],
          10: [('cUSDCv3', '0x2e44e174f7D53F0212823acC11C01A11d58c5bCB', 0), ('cUSDTv3', '0x995E394b8B2437aC8Ce61Ee0bC610D617962B214', 0),
               ('cWETHv3', '0xE36A30D249f7761327fd973001A32010b521b6Fd', 0)]}
ENUM = (1, 42161)


def scan(side, ch):
    B = block_at(ch, side); head = int(rpc(ch, 'eth_blockNumber', []), 16)
    out = []; rows = []
    for name, comet, start in COMETS[ch]:
        base = A(call1(ch, comet, '0xc55dae63', B))
        if not base or base == '0x' + '0' * 40: log(ch, name, 'not deployed'); continue
        r = mcall(ch, [(base, '0x95d89b41'), (base, '0x313ce567'), (comet, '0xa46fe83b'), (comet, '0x18160ddd'), (comet, '0x8285ef40')], B)
        bsym = dec_str(r[0]); bdec = U(r[1]); n = U(r[2]); tsup = U(r[3]) / 10**bdec; tbor = U(r[4]) / 10**bdec
        infos = mcall(ch, [(comet, '0xc8c7fe6b' + u32(i)) for i in range(n)], B)
        assets = []
        for x in infos:
            w = x[2:]; assets.append(dict(asset='0x' + w[64 + 24:128], scale=int(w[192:256], 16)))
        r2 = mcall(ch, [(x['asset'], '0x95d89b41') for x in assets] + [(x['asset'], '0x70a08231' + a32(comet)) for x in assets], B)
        for i, x in enumerate(assets):
            x['sym'] = dec_str(r2[i]); x['total'] = U(r2[len(assets) + i]) / x['scale']; x['fam'] = fam(x['sym'], side)  # total = token balance held by the Comet (collateral plus absorbed collateral not yet sold)
        own = [x for x in assets if x['fam'] == 'own' and x['total'] > 0]
        meta = dict(chain=ch, comet=name, address=comet, base=bsym, base_fam=fam(bsym, side), base_form=(form(bsym, side) if fam(bsym, side) == 'own' else None),
                    total_supply=tsup, total_borrow=tbor, collateral={x['sym']: x['total'] for x in own}, enumerated=ch in ENUM)
        if own and ch in ENUM:
            users = set(); nl = 0
            for x in own:
                lg = get_logs(ch, comet, [SC, None, None, '0x' + a32(x['asset'])], start or 1, head)
                nl += len(lg)
                for l in lg: users.add('0x' + l['topics'][2][-40:])
            us = sorted(users)
            cl = [(comet, '0x374c49b4' + a32(u)) for u in us]
            for x in own: cl += [(comet, '0x5c2549ee' + a32(u) + a32(x['asset'])) for u in us]
            res = mcall(ch, cl, B); m = len(us)
            read = {x['sym']: 0 for x in own}
            for i, u in enumerate(us):
                debt = U(res[i]) / 10**bdec
                colls = {}
                for j, x in enumerate(own):
                    v = U(res[m * (j + 1) + i]) / x['scale']
                    if v > 0: colls[x['sym']] = v; read[x['sym']] += v
                if colls:
                    rows.append(dict(user=u, comet=name, base=bsym, colls=colls, debt_units=debt))
            meta.update(logs=nl, accounts=len(us), collateral_read=read)
        out.append(meta)
        log(ch, name, bsym, 'supply %.1f borrow %.1f' % (tsup, tbor), 'own collateral', meta['collateral'], 'read', meta.get('collateral_read'))
    save('compound_%s_%d.json' % (side, ch), dict(side=side, chain=ch, block=B, comets=out, rows=rows))


if __name__ == '__main__':
    side = sys.argv[1]
    for c in sys.argv[2:]:
        try: scan(side, int(c))
        except Exception as e: log('chain', c, 'failed', repr(e)[:300])
