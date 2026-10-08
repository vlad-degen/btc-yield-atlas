"""Gearbox v3 carry sweep at T (2026-10-02 23:59:59 UTC).

Credit managers from the Gearbox DefiLlama compressor v3.10 (0x81cb9eA2d59414Ab13ec0567EFB09767Ddbe897a, same address on every chain):
getCreditManagers() plus getCreditManagers(legacy market configurators). For each credit manager with a stablecoin underlying:
getCreditAccounts(cm, offset, limit) at the T block -> (creditAccount, debt, token balances). A credit account's debt is all in the
underlying, so eth_backing_dollar = ETH-family holdings of the account. ETH-equivalent: Aave Core symbol ratio at T, else the credit
manager price oracle convertToUSD / 2,666.40. Borrower: creditManager.getBorrowerOrRevert(creditAccount); the borrower can be a
strategy contract. Debt = principal from the compressor (excludes accrued interest; noted).
Usage: python3 gearbox_scan.py [chainId ...]
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from chains import *

COMP = '0x81cb9eA2d59414Ab13ec0567EFB09767Ddbe897a'
LEGACY = {1: ['0x354fe9f450F60b8547f88BE042E4A45b46128a06', '0x4d427D418342d8CE89a7634c3a402851978B680A'], 42161: ['0x01023850b360b88de0d0f84015bbba1eba57fe7e'],
          10: ['0x2a15969CE5320868eb609680751cF8896DD92De5'], 146: ['0x8FFDd1F1433674516f83645a768E8900A2A5D076']}
CHAINS = [1, 42161, 10, 146, 56, 43111, 1135, 42793, 9745, 143, 5031]
L.RPCS.setdefault(5031, ['https://api.infra.mainnet.somnia.network'])
CHAIN_NAME[5031] = 'somnia'


_NOMC = set()
def mc(ch, cl, B):
    """Multicall3 batch, or one eth_call per item on chains without Multicall3 (Somnia)."""
    if ch in _NOMC: return [call1(ch, t, d, B) for t, d in cl]
    return mcall(ch, cl, B)


def enc_addr_array(xs):
    return u32(0x20) + u32(len(xs)) + ''.join(a32(x) for x in xs)


def dec_cas(h):
    w = L.words(h); base = w[0] // 32; n = w[base]; out = []
    for i in range(n):
        o = base + 1 + w[base + 1 + i] // 32
        ca = '0x' + hex(w[o])[2:].rjust(40, '0'); debt = w[o + 1]; to = o + w[o + 2] // 32; m = w[to]
        toks = [('0x' + hex(w[to + 1 + 2 * j])[2:].rjust(40, '0'), w[to + 2 + 2 * j]) for j in range(m)]
        out.append((ca, debt, toks))
    return out


def scan(ch):
    B = bT(ch)
    if (rpc(ch, 'eth_getCode', [L.MC3, hex(B)]) or '0x') == '0x': _NOMC.add(ch)
    if (rpc(ch, 'eth_getCode', [COMP, hex(B)]) or '0x') == '0x':
        return dict(chain=ch, block=B, note='compressor not deployed at T'), []
    cms = L.addr_list(call1(ch, COMP, S('getCreditManagers()'), B) or '0x' + u32(0x20) + u32(0))
    if LEGACY.get(ch):
        r = call1(ch, COMP, S('getCreditManagers(address[])') + enc_addr_array(LEGACY[ch]), B)
        if r: cms += L.addr_list(r)
    cms = sorted({c.lower() for c in cms})
    r = mc(ch, [(c, S(x)) for c in cms for x in ('underlying()', 'priceOracle()', 'version()', 'name()')], B)
    cmi = {c: dict(underlying=A(r[4 * i]), oracle=A(r[4 * i + 1]), version=U(r[4 * i + 2]), name=dec_str(r[4 * i + 3])) for i, c in enumerate(cms)}
    toks = sorted({x['underlying'] for x in cmi.values() if x['underlying']})
    r = mc(ch, [(t, S(x)) for t in toks for x in ('symbol()', 'decimals()')], B)
    tm = {t: dict(sym=dec_str(r[2 * j]), dec=U(r[2 * j + 1]) if r[2 * j + 1] else 18) for j, t in enumerate(toks)}
    stcms = [c for c in cms if is_stable_sym((tm.get(cmi[c]['underlying']) or {}).get('sym'))]
    log('gearbox', ch, 'block', B, 'credit managers', len(cms), 'stable', len(stcms))
    rows = []; cmmeta = []
    for c in stcms:
        u = cmi[c]['underlying']; ud = tm[u]['dec']; us = tm[u]['sym']
        cas = []; off = 0
        while True:
            h = call1(ch, COMP, S('getCreditAccounts(address,uint256,uint256)') + a32(c) + u32(off) + u32(500), B)
            if not h: break
            page = dec_cas(h); cas += page
            if len(page) < 500: break
            off += 500
        cas = [x for x in cas if x[1] > 0]
        newt = sorted({t for _, _, ts in cas for t, b in ts if b > 1 and t not in tm})
        if newt:
            r = mc(ch, [(t, S(x)) for t in newt for x in ('symbol()', 'decimals()')], B)
            for j, t in enumerate(newt): tm[t] = dict(sym=dec_str(r[2 * j]), dec=U(r[2 * j + 1]) if r[2 * j + 1] else 18)
        need = [(ca, t, b) for ca, _, ts in cas for t, b in ts if b > 1 and is_eth_sym(tm[t]['sym']) and eth_rate(tm[t]['sym']) is None]
        r = mc(ch, [(cmi[c]['oracle'], S('convertToUSD(uint256,address)') + u32(b) + a32(t)) for ca, t, b in need], B) if need else []
        qusd = {(ca, t): (U(x) / 1e8 if x else None) for (ca, t, b), x in zip(need, r)}
        r = mc(ch, [(c, S('getBorrowerOrRevert(address)') + a32(ca)) for ca, _, _ in cas], B)
        bor = {ca: A(x) for (ca, _, _), x in zip(cas, r)}
        esum = 0.0; dsum = 0.0
        for ca, debt, ts in cas:
            ec = 0.0; coll = []; other = []
            for t, b in ts:
                if b <= 1: continue
                sym = tm[t]['sym']; units = b / 10 ** tm[t]['dec']
                if is_eth_sym(sym):
                    rt = eth_rate(sym)
                    if rt is not None: e, src = units * rt, 'aave_core_symbol_ratio'
                    else:
                        q = qusd.get((ca, t)); e, src = ((q / ETH_USD) if q is not None else 0.0), ('gearbox_oracle' if q is not None else 'unpriced')
                    ec += e; coll.append(dict(token=t, sym=sym, units=units, eth_eq=e, price_src=src))
                else:
                    other.append(dict(token=t, sym=sym, units=units))
            dd = debt / 10 ** ud * (usd_rate(us) or 1.0)
            dsum += dd; esum += ec
            rows.append(dict(venue='gearbox-v3', chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, market=c, market_label='%s (%s)' % (cmi[c]['name'], us),
                             account=ca, owner=bor.get(ca), eth_collateral=ec, collateral=coll, other_holdings=other, dollar_debt_usd=dd, other_debt_usd=0.0,
                             eth_backing_dollar=ec, debt_note='principal only (compressor debt field)'))
        cmmeta.append(dict(credit_manager=c, name=cmi[c]['name'], version=cmi[c]['version'], underlying=us, open_accounts=len(cas), debt_principal_usd=dsum, eth_holdings=esum))
        log('  ', cmi[c]['name'], us, 'accounts', len(cas), 'debt $%.2fM' % (dsum / 1e6), 'ETH %.0f' % esum)
    meta = dict(chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, credit_managers=len(cms), stable_credit_managers=cmmeta,
                eth_holdings_total=sum(r['eth_collateral'] for r in rows), stable_debt_usd=sum(r['dollar_debt_usd'] for r in rows))
    return meta, rows


def main():
    only = [int(x) for x in sys.argv[1:]]
    parts = load('venues/gearbox_parts.json', {})
    for ch in CHAINS:
        if only and ch not in only: continue
        try:
            m, rows = scan(ch)
        except Exception as e:
            log('gearbox', ch, 'FAILED', e); m, rows = dict(chain=ch, error=str(e)), []
        parts[str(ch)] = dict(meta=m, rows=rows)
        save('venues/gearbox_parts.json', parts)
    allrows = [r for p in parts.values() for r in p['rows']]
    pos = sorted([r for r in allrows if r['eth_backing_dollar'] >= 100], key=lambda r: -r['eth_backing_dollar'])
    def ck(r):
        r['account_code'], r['account_delegate'] = code_kind(r['chain'], r['account'], r['block'])
        if r['owner']: r['owner_code'], r['owner_delegate'] = code_kind(r['chain'], r['owner'], r['block'])
        return r
    with ThreadPoolExecutor(8) as ex: pos = list(ex.map(ck, pos))
    meta = [p['meta'] for p in parts.values()]
    summary = dict(venue='gearbox-v3', snapshot='2026-10-02 23:59:59 UTC', eth_usd=ETH_USD,
                   eth_holdings_in_stable_credit_accounts=sum(m.get('eth_holdings_total') or 0 for m in meta),
                   positions_ge100=len(pos), positions_ge100_eth=sum(r['eth_backing_dollar'] for r in pos), method=__doc__.strip())
    save('venues/gearbox.json', dict(meta=[summary] + meta, positions=pos))
    log('gearbox positions >= 100', len(pos), 'ETH %.0f' % summary['positions_ge100_eth'], 'total %.0f' % summary['eth_holdings_in_stable_credit_accounts'])


if __name__ == '__main__':
    main()
