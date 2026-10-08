"""Curve crvUSD mint markets (Ethereum) and LlamaLend one-way markets (Ethereum, Arbitrum, Optimism, Fraxtal, Sonic) with ETH-family collateral.
Enumerates loans at T via n_loans()/loans(i), reads user_state(user) = [collateral, borrowed in soft liquidation, debt, N].
ETH value of collateral = collateral x AMM price_oracle (dollar units) / ETH price at T ($2,666.40, Aave Core WETH oracle).
Output raw/eth/carry-sweep-2026-10-08/venues/curve.json."""
from vcommon import *  # noqa
from lib import is_eth, is_stable

CRVUSD_FACTORY = '0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC'
API = {1: 'ethereum', 42161: 'arbitrum', 10: 'optimism', 252: 'fraxtal', 146: 'sonic'}
MIN = 100.0

def controllers():
    out = []
    b = vblk(1)
    n = U(call1(1, CRVUSD_FACTORY, sel('n_collaterals()'), b))
    res = mcall(1, [(CRVUSD_FACTORY, cd('controllers(uint256)', i)) for i in range(n)], b)
    for r in res:
        if r: out.append((1, 'crvUSD mint', A(r)))
    for ch, nm in API.items():
        page = 1
        while True:
            j = getjson('https://prices.curve.finance/v1/lending/markets/%s?page=%d&per_page=100' % (nm, page))
            d = j.get('data', [])
            for m in d: out.append((ch, 'LlamaLend', m['controller'].lower()))
            if len(d) < 100: break
            page += 1
    return out

def scan_market(ch, kind, ctl):
    b = vblk(ch)
    code = rpc(ch, 'eth_getCode', [ctl, hex(b)])
    if code in (None, '0x', ''): return None, []
    r = mcall(ch, [(ctl, sel('collateral_token()')), (ctl, sel('amm()')), (ctl, sel('n_loans()')), (ctl, sel('total_debt()')),
                   (ctl, sel('borrowed_token()'))], b)
    coll = A(r[0]); amm = A(r[1]); nl = U(r[2]); td = U(r[3])
    borrowed = A(r[4]) if r[4] else '0xf939e0a03fb07f59a73314e73794be0e57ac1b4e'  # crvUSD mint markets lend crvUSD
    rr = mcall(ch, [(coll, sel('symbol()')), (coll, sel('decimals()')), (borrowed, sel('symbol()')), (borrowed, sel('decimals()')),
                    (amm, sel('price_oracle()')), (coll, cd('balanceOf(address)', amm))], b)
    csym = dec_str(rr[0]); cdec = U(rr[1]); bsym = dec_str(rr[2]); bdec = U(rr[3]); po = U(rr[4]) / 1e18; cbal = U(rr[5]) / 10 ** cdec
    meta = dict(venue='Curve ' + kind, chain=ch, block=b, controller=ctl, amm=amm, collateral=coll, collateral_symbol=csym,
                borrowed=borrowed, borrowed_symbol=bsym, n_loans=nl, total_debt=td / 10 ** bdec, collateral_in_amm=cbal,
                price_oracle=po)
    if not is_eth(csym or '') or not is_stable(bsym or ''):
        meta['skip'] = 'not ETH-family collateral against a dollar debt'
        return meta, []
    users = [A(x) for x in mcall(ch, [(ctl, cd('loans(uint256)', i)) for i in range(nl)], b)]
    st = mcall(ch, [(ctl, cd('user_state(address)', u)) for u in users], b)
    pos = []; tot_c = 0.0; tot_d = 0.0
    for u, s in zip(users, st):
        w = words(s) if s else [0, 0, 0, 0]
        c = w[0] / 10 ** cdec; x = w[1] / 10 ** bdec; d = w[2] / 10 ** bdec
        tot_c += c; tot_d += d
        eth = c * po / ETH_USD
        pos.append(dict(venue='Curve ' + kind, chain=ch, block=b, market='%s/%s' % (csym, bsym), controller=ctl, account=u,
                        collateral_symbol=csym, collateral_units=c, eth_collateral=eth, soft_liq_dollar_in_amm=x,
                        dollar_debt_usd=d, eth_backing_dollar=eth, bands=w[3] if len(w) > 3 else None, manager=None))
    meta.update(eth_per_unit=po / ETH_USD, enumerated_collateral=tot_c, enumerated_debt=tot_d,
                total_collateral_eth=cbal * po / ETH_USD,
                coverage_collateral=(tot_c / cbal) if cbal else None, coverage_debt=(tot_d / meta['total_debt']) if meta['total_debt'] else None)
    return meta, pos

def main():
    metas = []; allpos = []
    for ch, kind, ctl in controllers():
        try:
            m, p = scan_market(ch, kind, ctl)
        except Exception as e:
            log('FAIL', ch, ctl, e); metas.append(dict(chain=ch, controller=ctl, venue='Curve ' + kind, error=str(e)[:200])); continue
        if m is None: continue
        metas.append(m); allpos += p
        if 'skip' not in m: log(ch, kind, m['collateral_symbol'], m['borrowed_symbol'], 'loans', m['n_loans'], 'cov %.4f' % (m['coverage_collateral'] or 0), round(m['total_collateral_eth']), 'ETH')
    big = [p for p in allpos if p['eth_collateral'] >= MIN]
    for ch in sorted({p['chain'] for p in big}):
        k = kinds(ch, [p['account'] for p in big if p['chain'] == ch], vblk(ch))
        for p in big:
            if p['chain'] == ch: p['kind'] = k[p['account'].lower()]
    big.sort(key=lambda p: -p['eth_collateral'])
    eth_metas = [m for m in metas if 'skip' not in m and 'error' not in m]
    summary = dict(eth_price_usd=ETH_USD, markets=len(eth_metas),
                   total_collateral_eth=sum(m['total_collateral_eth'] for m in eth_metas),
                   total_debt_usd=sum(m['total_debt'] for m in eth_metas),
                   enumerated_eth=sum(p['eth_collateral'] for p in allpos),
                   positions_ge_100=len(big), eth_in_positions_ge_100=sum(p['eth_collateral'] for p in big),
                   debt_in_positions_ge_100=sum(p['dollar_debt_usd'] for p in big))
    vsave('curve.json', {'summary': summary, 'meta': metas, 'positions': big})
    log(json.dumps(summary, indent=1))

if __name__ == '__main__':
    main()
