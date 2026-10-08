"""Euler v2 (EVK) carry sweep at T (2026-10-02 23:59:59 UTC), every chain in euler-interfaces/addresses.

Extends raw/eth/gap-2026-10-07/borrower-scan/scripts/euler_scan.py (Ethereum/Base/Arbitrum, big vaults and accounts only):
1. every EVK vault from the eVaultFactory proxy list at the T block; stablecoin-asset vaults with totalBorrows > 0.
2. borrower candidates from the Euler simple subgraph (Goldsky). The subgraph is pruned before T, so candidates are
   TrackingVaultBalance rows on those vaults with debt > 0 now OR last updated after the T block (an account that had
   debt at T and has none now must have been touched after T). Entities persist at zero, so this is a superset.
3. on chain at T: debtOf, EVC getCollaterals, controller LTVBorrow per collateral, balanceOf, collateral asset symbol,
   USD value through the controller oracle getQuote(shares, collateralVault, unitOfAccount). ETH-equivalent = USD / 2,666.40.
   Debt in USD via the same oracle (fallback 1:1).
4. EVC getAccountOwner for sub-accounts, eth_getCode for account and owner.
An Euler account has one controller, so dollar_debt = all debt and eth_backing_dollar = ETH collateral (enabled, LTV > 0).
Usage: python3 euler_scan.py [chainId ...]
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from chains import *

SG = {1: 'mainnet', 8453: 'base', 42161: 'arbitrum', 43114: 'avalanche', 56: 'bsc', 146: 'sonic', 130: 'unichain', 80094: 'berachain',
      59144: 'linea', 9745: 'plasma', 999: 'hyperevm', 239: 'tac', 60808: 'bob', 143: 'monad', 137: 'polygon'}
SGURL = 'https://api.goldsky.com/api/public/project_cm4iagnemt1wp01xn4gh1agft/subgraphs/euler-simple-%s/latest/gn'
USD = '0x0000000000000000000000000000000000000348'
WETH_UOA = {'0x0000000000000000000000000000000000000000'}
s_ = S


def sg(ch, q):
    body = json.dumps({'query': q}).encode()
    for i in range(8):
        j = getjson(SGURL % SG[ch], data=body, headers={'content-type': 'application/json'})
        if 'data' in j and j['data'] is not None: return j['data']
        time.sleep(3 * (i + 1))
    raise Exception('subgraph failed %s %s' % (ch, str(j)[:300]))


def candidates(ch, vaults, B):
    out = set(); vl = json.dumps(sorted(vaults))
    for cond in ('debt_gt: "0"', 'blockNumber_gt: "%d"' % B):
        last = '0x'
        while True:
            q = '{trackingVaultBalances(first: 1000, orderBy: id, where: {vault_in: %s, %s, id_gt: "%s"}) {id account vault debt}}' % (vl, cond, last)
            rows = sg(ch, q)['trackingVaultBalances']
            for r in rows: out.add((r['vault'].lower(), r['account'].lower()))
            if len(rows) < 1000: break
            last = rows[-1]['id']
    return sorted(out)


def scan(ch):
    import time as _t
    j = getjson('https://raw.githubusercontent.com/euler-xyz/euler-interfaces/master/addresses/%d/CoreAddresses.json' % ch)
    fac, evc = j['eVaultFactory'].lower(), j['evc'].lower()
    B = bT(ch)
    n = U(call1(ch, fac, s_('getProxyListLength()'), B))
    vaults = []
    for s in range(0, n, 300):
        vaults += [v.lower() for v in L.addr_list(call1(ch, fac, s_('getProxyListSlice(uint256,uint256)') + u32(s) + u32(min(n, s + 300)), B))]
    sels = ['asset()', 'totalBorrows()', 'oracle()', 'unitOfAccount()', 'symbol()']
    r = mcall(ch, [(v, s_(x)) for v in vaults for x in sels], B)
    vi = {}
    for i, v in enumerate(vaults):
        a, tb, orc, uoa, vs = r[i * 5:(i + 1) * 5]
        vi[v] = dict(asset=A(a), tb_raw=U(tb), oracle=A(orc), uoa=A(uoa), vsym=dec_str(vs))
    assets = sorted({x['asset'] for x in vi.values() if x['asset']})
    r = mcall(ch, [(a, s_(x)) for a in assets for x in ('symbol()', 'decimals()')], B)
    am = {a: dict(sym=dec_str(r[2 * i]), dec=U(r[2 * i + 1]) if r[2 * i + 1] else 18) for i, a in enumerate(assets)}
    for v, x in vi.items():
        x.update(sym=(am.get(x['asset']) or {}).get('sym'), dec=(am.get(x['asset']) or {}).get('dec', 18))
        x['tb'] = x['tb_raw'] / 10 ** x['dec']
    stv = [v for v, x in vi.items() if x['sym'] and is_stable_sym(x['sym']) and x['tb_raw'] > 0]
    log('chain', ch, 'block', B, 'vaults', n, 'stable vaults with borrows', len(stv), 'borrows $%.2fM' % (sum(vi[v]['tb'] for v in stv) / 1e6))
    if not stv:
        return dict(chain=ch, block=B, vaults=n, stable_vaults=[]), []
    cands = candidates(ch, stv, B)
    log('  candidates', len(cands))
    r = mcall(ch, [(v, s_('debtOf(address)') + a32(a)) for v, a in cands], B)
    debt = {}
    for (v, a), d in zip(cands, r):
        if U(d): debt[(v, a)] = U(d)
    accts = sorted({a for v, a in debt})
    # EVC collaterals and owner
    r = mcall(ch, [(evc, s_('getCollaterals(address)') + a32(a)) for a in accts] + [(evc, s_('getAccountOwner(address)') + a32(a)) for a in accts], B)
    colls = {a: ([c.lower() for c in L.addr_list(r[i])] if r[i] else []) for i, a in enumerate(accts)}
    owner = {a: A(r[len(accts) + i]) for i, a in enumerate(accts)}
    # collateral vault metadata (may be outside the factory list only in odd cases)
    extra = sorted({c for cs in colls.values() for c in cs if c not in vi})
    if extra:
        r = mcall(ch, [(c, s_('asset()')) for c in extra], B)
        ea = {c: A(x) for c, x in zip(extra, r)}
        na = sorted({x for x in ea.values() if x and x not in am})
        r2 = mcall(ch, [(a, s_(x)) for a in na for x in ('symbol()', 'decimals()')], B)
        for i, a in enumerate(na): am[a] = dict(sym=dec_str(r2[2 * i]), dec=U(r2[2 * i + 1]) if r2[2 * i + 1] else 18)
        for c in extra:
            a = ea.get(c); vi[c] = dict(asset=a, sym=(am.get(a) or {}).get('sym'), dec=(am.get(a) or {}).get('dec', 18), tb=0, oracle=None, uoa=None)
    # per (controller vault, account, collateral): balance, LTV, quote
    trip = [(v, a, c) for (v, a) in debt for c in colls[a]]
    r = mcall(ch, [(c, s_('balanceOf(address)') + a32(a)) for v, a, c in trip] + [(v, s_('LTVBorrow(address)') + a32(c)) for v, a, c in trip], B)
    bal = {t: U(r[i]) for i, t in enumerate(trip)}
    ltv = {t: U(r[len(trip) + i]) for i, t in enumerate(trip)}
    q = [t for t in trip if bal[t]]
    r = mcall(ch, [(vi[v]['oracle'], s_('getQuote(uint256,address,address)') + u32(bal[(v, a, c)]) + a32(c) + a32(vi[v]['uoa'])) for v, a, c in q]
              + [(c, s_('convertToAssets(uint256)') + u32(bal[(v, a, c)])) for v, a, c in q], B)
    quote = {t: (U(r[i]) if r[i] else None) for i, t in enumerate(q)}
    units = {t: (U(r[len(q) + i]) if r[len(q) + i] else None) for i, t in enumerate(q)}
    dk = list(debt)
    r = mcall(ch, [(vi[v]['oracle'], s_('getQuote(uint256,address,address)') + u32(debt[(v, a)]) + a32(vi[v]['asset']) + a32(vi[v]['uoa'])) for v, a in dk], B)
    dquote = {k: (U(x) if x else None) for k, x in zip(dk, r)}
    # unit of account price in USD (for non-USD units such as WETH)
    uoas = sorted({vi[v]['uoa'] for v in stv if vi[v]['uoa']})
    uoa_usd = {}
    for u in uoas:
        if u == USD: uoa_usd[u] = 1.0
        else:
            sym = (am.get(u) or {}).get('sym') or dec_str(call1(ch, u, s_('symbol()'), B))
            uoa_usd[u] = ETH_USD if (sym and sym.upper() in ('WETH', 'ETH')) else (1.0 if is_stable_sym(sym) else None)
            log('  non-USD unit of account', u, sym)
    rows = []
    for (v, a), d in debt.items():
        x = vi[v]; u = uoa_usd.get(x['uoa'])
        dunits = d / 10 ** x['dec']
        dusd = dquote[(v, a)] / 1e18 * u if (dquote[(v, a)] is not None and u) else dunits
        cl = []; eth = 0.0; oth = 0.0
        for c in colls[a]:
            t = (v, a, c)
            if not bal.get(t): continue
            ci = vi[c]; usd = quote[t] / 1e18 * u if (quote.get(t) is not None and u) else None
            iseth = is_eth_sym(ci['sym'])
            amt = units[t] / 10 ** ci['dec'] if units.get(t) is not None else None
            src = 'oracle'
            if usd is None and amt is not None and usd_rate(ci['sym']):
                usd = amt * usd_rate(ci['sym']); src = 'aave_core_symbol_price'
            counted = ltv[t] > 0 and usd is not None
            cl.append(dict(vault=c, sym=ci['sym'], units=amt, usd=usd, eth_eq=(usd / ETH_USD if usd is not None and iseth else None), ltv_bps=ltv[t], is_eth=iseth, counted=counted, price_src=src))
            if counted:
                if iseth: eth += usd / ETH_USD
                else: oth += usd
        rows.append(dict(venue='euler', chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, market=v, market_label='%s (%s)' % (x['vsym'], x['sym']),
                         debt_sym=x['sym'], account=a, owner=owner.get(a), dollar_debt_usd=dusd, other_debt_usd=0.0,
                         eth_collateral=eth, other_collateral_usd=oth, collateral=cl, eth_backing_dollar=eth,
                         eth_share_of_collateral_value=(eth * ETH_USD / (eth * ETH_USD + oth)) if eth * ETH_USD + oth else 0))
    vm = []
    for v in stv:
        rr = [x for x in rows if x['market'] == v]
        rd = sum(debt[(v, x['account'])] for x in rr) / 10 ** vi[v]['dec']
        vm.append(dict(vault=v, sym=vi[v]['sym'], vsym=vi[v]['vsym'], total_borrows=vi[v]['tb'], debt_read=rd, coverage=rd / vi[v]['tb'] if vi[v]['tb'] else None,
                       borrowers=len(rr), eth_collateral=sum(x['eth_collateral'] for x in rr), eth_collateral_debt_usd=sum(x['dollar_debt_usd'] for x in rr if x['eth_collateral'] > 0)))
    tot_tb = sum(vi[v]['tb'] for v in stv); tot_rd = sum(m['debt_read'] for m in vm)
    meta = dict(chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, factory=fac, evc=evc, vaults=n, stable_vaults_with_borrows=len(stv),
                stable_borrows_usd=tot_tb, debt_read_usd=tot_rd, coverage=tot_rd / tot_tb if tot_tb else None, candidates=len(cands), borrowers=len(rows),
                eth_collateral_total=sum(x['eth_collateral'] for x in rows), eth_collateral_ge100=sum(x['eth_collateral'] for x in rows if x['eth_backing_dollar'] >= 100),
                stable_vaults=vm)
    log('  chain', ch, 'borrowers', len(rows), 'coverage %.4f' % (meta['coverage'] or 0), 'ETH collateral %.0f' % meta['eth_collateral_total'], 'ge100 %.0f' % meta['eth_collateral_ge100'])
    return meta, rows


def main():
    chains = [int(x) for x in sys.argv[1:]] or [1, 8453, 42161, 43114, 56, 146, 130, 80094, 59144, 9745, 999, 239, 60808, 143, 137]
    out = load('venues/euler_parts.json', {})
    for ch in chains:
        try:
            m, rows = scan(ch)
            out[str(ch)] = dict(meta=m, rows=rows)
        except Exception as e:
            log('chain', ch, 'FAILED', e)
            out[str(ch)] = dict(meta=dict(chain=ch, error=str(e)), rows=[])
        save('venues/euler_parts.json', out)
    # final file: positions >= 100 ETH, with code kinds
    meta = [v['meta'] for k, v in sorted(out.items(), key=lambda kv: int(kv[0]))]
    pos = [r for v in out.values() for r in v['rows'] if r['eth_backing_dollar'] >= 100]
    def ck(r):
        r['account_code'], r['account_delegate'] = code_kind(r['chain'], r['account'], r['block'])
        if r['owner'] and r['owner'] != r['account']:
            r['owner_code'], r['owner_delegate'] = code_kind(r['chain'], r['owner'], r['block'])
        return r
    with ThreadPoolExecutor(8) as ex: pos = list(ex.map(ck, pos))
    pos.sort(key=lambda r: -r['eth_backing_dollar'])
    allrows = [r for v in out.values() for r in v['rows']]
    summary = dict(venue='euler', snapshot='2026-10-02 23:59:59 UTC', eth_usd=ETH_USD,
                   eth_collateral_vs_stable_debt_total=sum(r['eth_collateral'] for r in allrows),
                   positions_ge100=len(pos), positions_ge100_eth=sum(r['eth_backing_dollar'] for r in pos),
                   stable_borrows_usd=sum(m.get('stable_borrows_usd') or 0 for m in meta), debt_read_usd=sum(m.get('debt_read_usd') or 0 for m in meta),
                   method=__doc__.strip())
    save('venues/euler.json', dict(meta=[summary] + meta, positions=pos))
    log('positions >= 100 ETH', len(pos), 'ETH %.0f' % summary['positions_ge100_eth'], 'total ETH collateral %.0f' % summary['eth_collateral_vs_stable_debt_total'])


if __name__ == '__main__':
    main()
