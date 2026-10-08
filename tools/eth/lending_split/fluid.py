"""Fluid vaults (pair based) on Ethereum, Arbitrum and Base: every position of every vault whose collateral includes the side's family,
from VaultPositionsResolver.getAllVaultPositions(vault) at the snapshot block. Smart-collateral / smart-debt shares are valued with the
API's per-share token amounts read on the scan day (labelled). Also fWETH / fwstETH lender supply at the snapshot.

Usage: python3 fluid.py <eth|btc> <chainId> [...]
"""
import sys
from lib import *

R = '0xaA21a86030EAa16546A759d2d10fd3bF9D053Bc7'


def toks(v, k):
    return [x for x in (v[k]['token0'], v[k]['token1']) if x.get('symbol')]


def scan(side, ch):
    B = block_at(ch, side)
    vs = getjson('https://api.fluid.instadapp.io/v2/%d/vaults' % ch)
    save('fluid_vaults_api_%s_%d.json' % (side, ch), vs)
    refsym = 'ETH' if side == 'eth' else None
    px = {}
    for v in vs:
        for k in ('supplyToken', 'borrowToken'):
            for t in toks(v, k): px[t['symbol'].upper()] = float(t.get('price') or 0)
    ref = px.get('ETH') or px.get('WETH') if side == 'eth' else (px.get('WBTC') or px.get('CBBTC'))
    rows = []; meta = []
    for v in vs:
        st = toks(v, 'supplyToken'); bt = toks(v, 'borrowToken')
        own = [t for t in st if fam(t['symbol'], side) == 'own']
        if not own: continue
        try:
            if ch != 1: raise Exception('resolver not used off Ethereum (calls fail); vault totals from the API')
            r = rpc(ch, 'eth_call', [{'to': R, 'data': '0xf752d757' + a32(v['address']), 'gas': hex(3_000_000_000)}, tag(B)])
        except Exception as e:
            r = None
        typ = v['type']
        # value of one unit of supply (collateral) in native units, and of one unit of borrow in USD
        def unit_val(ts, key, dexkey):
            if len(ts) == 1:
                t = ts[0]; return [(t, 1 / 10**t['decimals'])]
            dx = v.get(dexkey) or {}
            return [(ts[0], int(dx.get('token0PerShare', 0)) / 10**ts[0]['decimals'] / 1e18), (ts[1], int(dx.get('token1PerShare', 0)) / 10**ts[1]['decimals'] / 1e18)]
        sv = unit_val(st, 'supply', 'supplyDexData'); bv = unit_val(bt, 'borrow', 'borrowDexData')
        own_native_per_unit = sum(q * float(t.get('price') or 0) / ref for t, q in sv if fam(t['symbol'], side) == 'own')
        form_split = {}
        for t, q in sv:
            if fam(t['symbol'], side) == 'own':
                f = form(t['symbol'], side); form_split[f] = form_split.get(f, 0) + q * float(t.get('price') or 0) / ref
        bfam = {}
        for t, q in bv:
            fm = fam(t['symbol'], side); bfam[fm] = bfam.get(fm, 0) + q * float(t.get('price') or 0)
        pair = '+'.join(t['symbol'] for t in st) + ' -> ' + '+'.join(t['symbol'] for t in bt)
        if not r:
            meta.append(dict(vault=v['address'], id=v['id'], type=typ, pair=pair, error='resolver failed or not used', api_totalSupply=v['totalSupply'], api_totalBorrow=v['totalBorrow'],
                             own_native_per_unit=own_native_per_unit, form_native_per_unit=form_split, borrow_usd_per_unit_by_fam=bfam))
            log('FAIL', ch, v['id'], pair); continue
        h = r[2:]; n = int(h[64:128], 16); ps = []
        for i in range(n):
            w = h[128 + i * 256:128 + (i + 1) * 256]
            ps.append(('0x' + w[88:128], int(w[128:192], 16), int(w[192:256], 16)))
        cn = 0; dn = 0
        for owner, sup, bor in ps:
            if sup == 0: continue
            c = sup * own_native_per_unit
            rows.append(dict(user=owner.lower(), vault=v['address'], vault_id=v['id'], pair=pair, coll_native=c,
                             coll_by_form={f: sup * x for f, x in form_split.items()}, debt_usd_by_fam={f: bor * x for f, x in bfam.items()}))
            cn += c; dn += sum(bor * x for x in bfam.values())
        meta.append(dict(vault=v['address'], id=v['id'], type=typ, pair=pair, positions=n, coll_native=cn, debt_usd=dn))
        log(ch, v['id'], typ, pair, 'positions', n, 'coll native %.1f debt $%.1fM' % (cn, dn / 1e6))
    lend = []
    lt = getjson('https://api.fluid.instadapp.io/v2/lending/%d/tokens' % ch)
    lt = lt.get('data', lt) if isinstance(lt, dict) else lt
    for t in lt:
        s = t['asset']['symbol']
        if fam(s, side) != 'own': continue
        x = U(call1(ch, t['address'], '0x01e1d114', B)) / 10**t['decimals']
        lend.append(dict(ftoken=t['address'], sym=s, form=form(s, side), assets=x, native=x * float(t['asset'].get('price') or ref) / ref))
    save('fluid_%s_%d.json' % (side, ch), dict(side=side, chain=ch, block=B, ref_price_now=ref, vaults=meta, rows=rows, lending=lend))
    log('== fluid', ch, 'coll native %.0f' % sum(m.get('coll_native', 0) for m in meta), 'lending', lend)


if __name__ == '__main__':
    side = sys.argv[1]
    for c in sys.argv[2:]:
        try: scan(side, int(c))
        except Exception as e: log('chain', c, 'failed', repr(e)[:300])
