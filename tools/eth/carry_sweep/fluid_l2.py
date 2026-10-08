"""Fluid vaults on Base and Arbitrum (vault totals only in the lending split): every position of every vault with ETH-family collateral,
from VaultPositionsResolver.getAllVaultPositions(vault) (0xaA21...3bC7, same address as Ethereum) at the snapshot block. The resolver
runs out of gas on the default Arbitrum endpoint; Arbitrum reads go through arbitrum-one.public.blastapi.io (archive), Base through
Tenderly with a 1.5bn gas cap. Valuation as tools/eth/lending_split/fluid.py: Fluid API token prices and DEX per-share amounts on the
scan day (labelled), collateral in ETH at the API ETH price.

eth_backing_dollar = ETH-family collateral x stablecoin debt USD / total debt USD of the position.
Usage: python3 fluid_l2.py [chain ...]   (default 8453 42161)
Output: raw/eth/carry-sweep-2026-10-08/venues/fluid_<chain>.json
"""
import collections, json, os, sys
import sweep_lib as S
import lib as L
from lib import a32, fam, form, log

R = '0xaA21a86030EAa16546A759d2d10fd3bF9D053Bc7'
EP = {8453: ('https://gateway.tenderly.co/public/base', 1_500_000_000), 42161: ('https://arbitrum-one.public.blastapi.io', None)}


def toks(v, k): return [x for x in (v[k]['token0'], v[k]['token1']) if x.get('symbol')]


def call(ch, data, B):
    url, gas = EP[ch]; p = {'to': R, 'data': data}
    if gas: p['gas'] = hex(gas)
    for i in range(6):
        try:
            r = L.post_raw(url, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call', 'params': [p, hex(B)]}, timeout=180)
            if 'error' in r: raise Exception(str(r['error'])[:200])
            return r['result']
        except Exception as e:
            last = e
            import time; time.sleep(2 + 2 * i)
    raise Exception(str(last))


def scan(ch):
    B = S.block_at(ch)
    vs = json.load(open(os.path.join(L.RAW, 'fluid_vaults_api_eth_%d.json' % ch)))  # the lending split's API capture (scan day)
    px = {}
    for v in vs:
        for k in ('supplyToken', 'borrowToken'):
            for t in toks(v, k): px[t['symbol'].upper()] = float(t.get('price') or 0)
    ref = px.get('ETH') or px.get('WETH')
    peru = collections.defaultdict(lambda: dict(coll=0.0, syms=set(), st=0.0, oth=0.0, back=0.0, vaults=[]))
    meta = []; back_all = 0.0
    for v in vs:
        st = toks(v, 'supplyToken'); bt = toks(v, 'borrowToken')
        if not any(fam(t['symbol'], 'eth') == 'own' for t in st): continue
        def unit_val(ts, dexkey):
            if len(ts) == 1: return [(ts[0], 1 / 10**ts[0]['decimals'])]
            dx = v.get(dexkey) or {}
            return [(ts[0], int(dx.get('token0PerShare', 0)) / 10**ts[0]['decimals'] / 1e18), (ts[1], int(dx.get('token1PerShare', 0)) / 10**ts[1]['decimals'] / 1e18)]
        sv = unit_val(st, 'supplyDexData'); bv = unit_val(bt, 'borrowDexData')
        own_per = sum(q * float(t.get('price') or 0) / ref for t, q in sv if fam(t['symbol'], 'eth') == 'own')
        bfam = collections.Counter()
        for t, q in bv: bfam[fam(t['symbol'], 'eth')] += q * float(t.get('price') or 0)
        pair = '+'.join(t['symbol'] for t in st) + ' -> ' + '+'.join(t['symbol'] for t in bt)
        try: r = call(ch, '0xf752d757' + a32(v['address']), B)
        except Exception as e:
            meta.append(dict(vault=v['address'], id=v['id'], pair=pair, error=str(e)[:200])); log('FAIL', ch, v['id'], pair, str(e)[:100]); continue
        h = r[2:]; n = int(h[64:128], 16); cn = dn = vb = 0.0
        for i in range(n):
            w = h[128 + i * 256:128 + (i + 1) * 256]
            owner = '0x' + w[88:128]; sup = int(w[128:192], 16); bor = int(w[192:256], 16)
            if sup == 0: continue
            c = sup * own_per; dsum = sum(bor * x for x in bfam.values()); dst = bor * bfam.get('stable', 0)
            d = peru[owner]; d['coll'] += c; d['syms'] |= {t['symbol'] for t in st if fam(t['symbol'], 'eth') == 'own'}
            d['st'] += dst; d['oth'] += dsum - dst; d['vaults'].append('%s (%s)' % (v['id'], pair))
            if dsum > 0 and dst > 0:
                b = c * dst / dsum; d['back'] += b; vb += b
            cn += c; dn += dsum
        back_all += vb
        meta.append(dict(vault=v['address'], id=v['id'], pair=pair, positions=n, coll_native=round(cn, 3), debt_usd=round(dn), eth_backing_dollar=round(vb, 3)))
        log(ch, v['id'], pair, 'positions', n, 'coll %.1f backing$ %.1f' % (cn, vb))
    pos = [S.pos('fluid', ch, B, u, d['coll'], d['syms'], d['st'], d['oth'], d['back'], vaults=d['vaults']) for u, d in peru.items() if d['back'] >= 100]
    kinds = S.code_kinds((ch, B, p['account']) for p in pos)
    for p in pos: p['code_kind'] = kinds[(ch, p['account'])]
    pos.sort(key=lambda p: -p['eth_backing_dollar'])
    head = dict(venue='fluid', chain=ch, block=B, eth_price_api_scan_day=ref, eth_backing_dollar_total=round(back_all, 2),
                positions_ge100=len(pos), positions_ge100_eth=round(sum(p['eth_backing_dollar'] for p in pos), 2),
                note='vault positions at the snapshot block; token prices and DEX per-share amounts from the Fluid API on the scan day')
    S.write('fluid_%d' % ch, [head] + meta, pos)


if __name__ == '__main__':
    for c in (sys.argv[1:] or ['8453', '42161']):
        try: scan(int(c))
        except Exception as e: log('FAILED', c, repr(e)[:300])
