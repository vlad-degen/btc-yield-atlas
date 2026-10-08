"""Silo (v1 and v2) carry sweep at T (2026-10-02 23:59:59 UTC).

v2: every SiloFactory deployment in silo-finance/silo-contracts-v2 (git history of silo-core/deployments/<chain>/SiloFactory.sol.json)
    -> idToSiloConfig for every id -> getSilos, assets, getTotalAssetsStorage(0 protected, 1 collateral, 2 debt) at T.
    Market = one ETH-family silo plus one stablecoin silo with debt. Market ETH collateral (protected + collateral) is an upper bound
    for any single position, so borrowers are enumerated only where it is >= 100 ETH: debt share token Transfer logs (mints to
    borrowers), then at T maxRepay, borrowerCollateralSilo, collateral and protected share balances, convertToAssets.
v1: SiloFactory NewSiloCreated logs (DefiLlama list) -> getAssetsWithState at T. A v1 silo pools its asset plus bridge assets
    (WETH, USDC/XAI); any depositor of an ETH-family asset can borrow the stable asset in the same silo. Silos with >= 100 ETH
    of ETH-family deposits and stable borrows -> Borrow logs -> per user at T: debt and collateral token balances converted pro rata.
ETH-equivalent: Aave Core oracle ratio by symbol at T (plain WETH = 1); else the market solvency oracle quote / 2,666.40.
eth_backing_dollar = eth_collateral x dollar_debt / total_debt.
Usage: python3 silo_scan.py [v1|v2] [chainId ...]
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from chains import *

V2F = {1: ['0x22a3cF6149bFa611bAFc89Fd721918EC3Cf7b581', '0x1DAb4A310447185144467076b116DAC7aec3b48F', '0x2534b2e33076787142246750E9340696267B96be'],
       42161: ['0x384DC7759d35313F0b567D42bf2f611B285B657C', '0x408822E4E8682413666809b0655161093cd36f2b', '0x44347A91Cf3E9B30F80e2161438E0f10fCeDA0a0',
               '0x504B8ca9C664AFe72324388122caBAFb72F9269f', '0x51824653425e40Cd6253B71AcC8Def602A21427f', '0x621Eacb756c7fa8bC0EA33059B881055d1693a33',
               '0x8C1b49B1A45d9FD50c5846a6Cd19a5ADaA376B1B', '0xAFd8F792cb025A76C4916652CfC8e20eee3b6fe2', '0xCb6CcBd979aa167b81411e672050c01826d715EC',
               '0xaE94617314381809C2a195fcDE469e7998132B40', '0xb562b6CdEEE3ec10E4803B8dcfef81a32074e6B5', '0xb720078680Dc65B54568673410aBb81195E08122',
               '0xe376888fD6E5D5Afc12FEa0a8C18f283051c23aD', '0xf7dc975C96B434D436b9bF45E7a45c95F0521442'],
       43114: ['0x92cECB67Ed267FF98026F814D813fDF3054C6Ff9', '0x931e59f06b83dD3d9A622FD4537989B6C63B9bde', '0x9e64f0CD206cce2Da5dE08E7F482D62F57013D0e'],
       8453: ['0x98F231070354F3a541081368b107155232CFfb1c', '0xeB3C9fcE37A355df8f4a01CdaFA75b370607a21f'],
       56: ['0x1C7861978D11E9fd13257607d3FCf7bF3478f6EB', '0x977e9b368E5aBEe020B5096A03cE6f78cb3439cf'],
       57073: ['0xD13921239e3832FDC4141FDE544D3D058B529A5D'],
       10: ['0x01c6dc3bD8B175a9494F00b6D224b14EdC67CD34', '0x047801ED4F53Ad3dc28649ab972b3C949f27505c', '0x17B0FD3eB9CFbdA5B46A0C896e28b3F0c5a7F61d',
            '0x4D43E78E669eD90bb125eF161F530E173f03834b', '0x55a4983949f8a3156Ad483c4003218a7F33D466b', '0x8458396264bAaAfC9F6E6437a264636ce7c07c43',
            '0x8ab5D81d342f14e594c65a6B33582b57e78E4a9d', '0xB25255036f210D7E32FC96e25460aB121FF0C25d', '0xFa773e2c7df79B43dc4BCdAe398c5DCA94236BC5',
            '0xb58B331b9cf46c597A34F9e198e8bB9ec5f17ADf'],
       146: ['0x4e9dE3a64c911A37f7EB2fCb06D1e68c3cBe9203', '0x55C5b74BC138C42dCb0deb206AE325a828Cd1372', '0x89E3Cf1c67C0c0701EF7926A79f65EeEb52904eF',
             '0xa42001D6d2237d2c74108FE360403C4b796B7170', '0xf81d90DF1B63d48536E78564d24d5DD8F2BE58aD']}
V1F = {1: [('0x4D919CEcfD4793c0D47866C8d0a02a0950737589', 15307294), ('0x6d4A256695586F61b77B09bc3D28333A91114d5a', 17391885),
           ('0x2c0fA05281730EFd3ef71172d8992500B36b56eA', 17782576), ('0xB7d391192080674281bAAB8B3083154a5f64cd0a', 20367992)],
       42161: [('0x4166487056A922D784b073d4d928a516B074b719', 51894508)], 10: [('0x6B14c4450a29Dd9562c20259eBFF67a577b540b9', 120480601)],
       8453: [('0x408822E4E8682413666809b0655161093cd36f2b', 16262586)]}
L.RPCS[57073] = ['https://rpc-gel.inkonchain.com', 'https://ink.drpc.org']
TRANSFER = topic('Transfer(address,address,uint256)')
MINTHRESH = 100.0


def tok_meta(ch, toks, B):
    toks = sorted({t for t in toks if t})
    r = mcall(ch, [(t, S(x)) for t in toks for x in ('symbol()', 'decimals()')], B)
    return {t: dict(sym=dec_str(r[2 * i]), dec=(U(r[2 * i + 1]) if r[2 * i + 1] else 18)) for i, t in enumerate(toks)}


def quote_usd(ch, oracle, amount, token, B, tm):
    """USD value of amount (raw) of token through a Silo oracle (quote in its quoteToken)."""
    if not oracle or int(oracle, 16) == 0: return None
    q = call1(ch, oracle, S('quote(uint256,address)') + u32(amount) + a32(token), B)
    qt = A(call1(ch, oracle, S('quoteToken()'), B))
    if not q or not qt: return None
    m = tm.get(qt) or tok_meta(ch, [qt], B)[qt]
    r = usd_rate(m['sym'])
    return U(q) / 10 ** m['dec'] * r if r else None


def eth_value(ch, sym, dec, amount_raw, oracle, token, B, tm):
    r = eth_rate(sym)
    if r is not None: return amount_raw / 10 ** dec * r, 'aave_core_symbol_ratio'
    u = quote_usd(ch, oracle, amount_raw, token, B, tm)
    if u is not None: return u / ETH_USD, 'silo_oracle'
    return None, 'unpriced'


def creation_block(ch, addr, B):
    """first block where addr has code (binary search)"""
    lo, hi = 1, B
    if (rpc(ch, 'eth_getCode', [addr, hex(B)]) or '0x') == '0x': return B
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if (rpc(ch, 'eth_getCode', [addr, hex(mid)]) or '0x') != '0x': hi = mid
        else: lo = mid
    return hi


def v2_chain(ch):
    B = bT(ch); cfgs = set()
    for f in V2F[ch]:
        f = f.lower()
        n = U(call1(ch, f, S('getNextSiloId()'), B))
        if not n: continue
        r = mcall(ch, [(f, S('idToSiloConfig(uint256)') + u32(i)) for i in range(n)], B)
        cfgs |= {A(x) for x in r if x and int(x, 16)}
    cfgs = sorted(cfgs)
    r = mcall(ch, [(c, S('getSilos()')) for c in cfgs], B)
    mk = [(c, A(x, 0), A(x, 1)) for c, x in zip(cfgs, r) if x]
    silos = [s for _, a, b in mk for s in (a, b)]
    r = mcall(ch, [(s, S(x)) for s in silos for x in ('asset()',)] + [(s, S('getTotalAssetsStorage(uint8)') + u32(k)) for s in silos for k in (0, 1, 2)], B)
    asset = {s: A(r[i]) for i, s in enumerate(silos)}; o = len(silos)
    tas = {s: [U(r[o + 3 * i + k]) for k in range(3)] for i, s in enumerate(silos)}
    tm = tok_meta(ch, asset.values(), B)
    markets = []
    for c, s0, s1 in mk:
        for se, ss in ((s0, s1), (s1, s0)):
            me, ms = tm.get(asset[se], {}), tm.get(asset[ss], {})
            if not (is_eth_sym(me.get('sym')) and is_stable_sym(ms.get('sym'))): continue
            if tas[ss][2] == 0: continue
            markets.append(dict(config=c, eth_silo=se, stable_silo=ss, eth_sym=me['sym'], eth_dec=me['dec'], eth_token=asset[se], st_sym=ms['sym'], st_dec=ms['dec'],
                                st_token=asset[ss], eth_coll_raw=tas[se][0] + tas[se][1], stable_debt=tas[ss][2] / 10 ** ms['dec']))
    log('v2 chain', ch, 'block', B, 'configs', len(cfgs), 'ETH/stable markets with debt', len(markets))
    meta = []; rows = []
    for m in markets:
        cfg = call1(ch, m['config'], S('getConfig(address)') + a32(m['eth_silo']), B)
        m['eth_oracle'] = A(cfg, 7) if cfg else None
        m['eth_collateral_total'], m['price_src'] = eth_value(ch, m['eth_sym'], m['eth_dec'], m['eth_coll_raw'], m['eth_oracle'], m['eth_token'], B, tm)
        st = call1(ch, m['config'], S('getShareTokens(address)') + a32(m['stable_silo']), B)
        m['debt_share_token'] = A(st, 2)
        et = call1(ch, m['config'], S('getShareTokens(address)') + a32(m['eth_silo']), B)
        m['eth_protected_share'] = A(et, 0)
        rec = dict(version='v2', chain=ch, block=B, config=m['config'], eth_silo=m['eth_silo'], stable_silo=m['stable_silo'], eth_sym=m['eth_sym'], st_sym=m['st_sym'],
                   eth_collateral_total=m['eth_collateral_total'], stable_debt=m['stable_debt'], price_src=m['price_src'], enumerated=False)
        meta.append(rec)
        if (m['eth_collateral_total'] or 0) < MINTHRESH: continue
        if ch not in LOGS:
            rec['note'] = 'no eth_getLogs endpoint for this chain'; continue
        fb = creation_block(ch, m['debt_share_token'], B)
        lg = logs(ch, m['debt_share_token'], [TRANSFER], fb, B)
        users = sorted({'0x' + l['topics'][2][-40:] for l in lg} - {'0x' + '0' * 40})
        rec['enumerated'] = True; rec['log_users'] = len(users)
        cl = []
        for u in users:
            cl += [(m['stable_silo'], S('maxRepay(address)') + a32(u)), (m['config'], S('borrowerCollateralSilo(address)') + a32(u)),
                   (m['eth_silo'], S('balanceOf(address)') + a32(u)), (m['eth_protected_share'], S('balanceOf(address)') + a32(u))]
        r = mcall(ch, cl, B)
        dsum = 0; esum = 0
        for i, u in enumerate(users):
            d, cs, b1, b0 = r[4 * i:4 * i + 4]
            debt = U(d) / 10 ** m['st_dec']
            if not debt: continue
            dsum += debt
            if (A(cs) or '').lower() != m['eth_silo'].lower(): continue
            a1 = U(call1(ch, m['eth_silo'], S('convertToAssets(uint256,uint8)') + u32(U(b1)) + u32(1), B)) if U(b1) else 0
            a0 = U(call1(ch, m['eth_silo'], S('convertToAssets(uint256,uint8)') + u32(U(b0)) + u32(0), B)) if U(b0) else 0
            ev, src = eth_value(ch, m['eth_sym'], m['eth_dec'], a0 + a1, m['eth_oracle'], m['eth_token'], B, tm)
            ev = ev or 0; esum += ev
            dusd = debt * (usd_rate(m['st_sym']) or 1.0)
            rows.append(dict(venue='silo-v2', chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, market=m['config'], market_label='%s/%s (silo %s borrow %s)' % (m['eth_sym'], m['st_sym'], m['eth_silo'], m['stable_silo']),
                             account=u, owner=None, eth_collateral=ev, collateral=[dict(sym=m['eth_sym'], units=(a0 + a1) / 10 ** m['eth_dec'], eth_eq=ev, price_src=src)],
                             dollar_debt_usd=dusd, other_debt_usd=0.0, eth_backing_dollar=ev))
        rec['debt_read'] = dsum; rec['coverage'] = dsum / m['stable_debt'] if m['stable_debt'] else None; rec['eth_collateral_of_borrowers'] = esum
        log('  v2', ch, m['eth_sym'], '/', m['st_sym'], 'ETH coll %.0f' % m['eth_collateral_total'], 'debt $%.2fM' % (m['stable_debt'] / 1e6), 'users', len(users), 'borrowers ETH %.0f' % esum, 'cov %.3f' % (rec['coverage'] or 0))
    return meta, rows


def dec_aws(h):
    """decode getAssetsWithState() -> (assets, [(collTok, collOnlyTok, debtTok, totalDeposits, collOnlyDeposits, totalBorrow)])"""
    w = L.words(h); o1 = w[0] // 32; o2 = w[1] // 32
    n = w[o1]; assets = ['0x' + hex(w[o1 + 1 + i])[2:].rjust(40, '0') for i in range(n)]
    st = []
    for i in range(w[o2]):
        x = w[o2 + 1 + 6 * i:o2 + 7 + 6 * i]
        st.append(['0x' + hex(x[0])[2:].rjust(40, '0'), '0x' + hex(x[1])[2:].rjust(40, '0'), '0x' + hex(x[2])[2:].rjust(40, '0'), x[3], x[4], x[5]])
    return assets, st


# Base v1: no usable eth_getLogs endpoint (tenderly 1,000-block limit, Blockscout behind a challenge). Silos found by
# SiloRepository(0xa42001d6...).getSilo(asset) for WETH, cbETH, wstETH, weETH, ezETH, wrsETH, USDC, USDbC, DEGEN, AERO, cbBTC, BRETT.
V1_PROBED = {8453: ['0x839aa8b0641b77db2c9effec724dd2df46290fa2', '0xeb42de7d17dfaffd03af48c2a51c3fb7274d3396', '0x8095806d8753c0443c118d1c5e5eec472e30bfec',
                    '0xd54a83d47934d889364dd5af2d6855dcf05745c3', '0xd56e1b712885d516e5918b099e0fde439cdaa10c', '0xcac9d4df6c98da614639f71400145f163b5f77c5',
                    '0xda79416990e7fa79e310ab938b01ed75cbb64a90']}


def v1_chain(ch):
    B = bT(ch); silos = set(V1_PROBED.get(ch, []))
    if ch in V1_PROBED: V1F_ = []
    else: V1F_ = V1F[ch]
    for f, sb in V1F_:
        try:
            lg = logs(ch, f, [topic('NewSiloCreated(address,address,uint128)')], sb, B)
        except Exception as e:
            log('v1 logs failed', ch, f, e); return [dict(version='v1', chain=ch, factory=f, note='factory logs failed: %s' % e)], []
        silos |= {'0x' + l['topics'][1][-40:] for l in lg}
    silos = sorted(silos)
    r = mcall(ch, [(s, S('getAssetsWithState()')) for s in silos], B)
    info = {s: dec_aws(x) for s, x in zip(silos, r) if x}
    tm = tok_meta(ch, [a for s in info for a in info[s][0]], B)
    meta = []; rows = []
    for s, (assets, st) in info.items():
        eth_dep = 0.0; sdebt = 0.0; odebt = 0.0
        for a, x in zip(assets, st):
            m = tm.get(a, {}); sym = m.get('sym'); dec = m.get('dec', 18)
            if is_eth_sym(sym): eth_dep += (x[3] + x[4]) / 10 ** dec * (eth_rate(sym) or 0)
            if is_stable_sym(sym): sdebt += x[5] / 10 ** dec
        if sdebt <= 0 or eth_dep <= 0: continue
        rec = dict(version='v1', chain=ch, block=B, silo=s, assets=[tm.get(a, {}).get('sym') for a in assets], eth_deposits=eth_dep, stable_debt=sdebt, enumerated=False)
        meta.append(rec)
        if eth_dep < MINTHRESH: continue
        fb = creation_block(ch, s, B)
        lg = logs(ch, s, [topic('Borrow(address,address,uint256)')], fb, B)
        users = sorted({'0x' + l['topics'][2][-40:] for l in lg})
        rec['enumerated'] = True; rec['log_users'] = len(users)
        toks = [t for x in st for t in x[:3]]
        sup = dict(zip(toks, [U(y) for y in mcall(ch, [(t, S('totalSupply()')) for t in toks], B)]))
        cl = [(t, S('balanceOf(address)') + a32(u)) for u in users for t in toks]
        r = mcall(ch, cl, B); k = 0; dsum = 0; esum = 0
        for u in users:
            ec = 0.0; dd = 0.0; od = 0.0; coll = []
            for a, x in zip(assets, st):
                m = tm.get(a, {}); sym = m.get('sym'); dec = m.get('dec', 18)
                bc, bco, bd = U(r[k]), U(r[k + 1]), U(r[k + 2]); k += 3
                amt_c = (bc * x[3] // sup[x[0]] if sup[x[0]] else 0) + (bco * x[4] // sup[x[1]] if sup[x[1]] else 0)
                amt_d = bd * x[5] // sup[x[2]] if sup[x[2]] else 0
                if amt_c and is_eth_sym(sym):
                    ev = amt_c / 10 ** dec * (eth_rate(sym) or 0); ec += ev
                    coll.append(dict(sym=sym, units=amt_c / 10 ** dec, eth_eq=ev, price_src='aave_core_symbol_ratio'))
                if amt_d:
                    if is_stable_sym(sym): dd += amt_d / 10 ** dec * (usd_rate(sym) or 1.0)
                    else: od += amt_d / 10 ** dec * (usd_rate(sym) or 0)
            if not dd: continue
            dsum += dd; esum += ec
            share = dd / (dd + od) if dd + od else 0
            rows.append(dict(venue='silo-v1', chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, market=s, market_label='silo %s (%s)' % (s, '/'.join(rec['assets'])),
                             account=u, owner=None, eth_collateral=ec, collateral=coll, dollar_debt_usd=dd, other_debt_usd=od, eth_backing_dollar=ec * share))
        rec['debt_read'] = dsum; rec['coverage'] = dsum / sdebt; rec['eth_collateral_of_stable_borrowers'] = esum
        log('  v1', ch, s, rec['assets'], 'ETH dep %.0f' % eth_dep, 'stable debt $%.2fM' % (sdebt / 1e6), 'users', len(users), 'cov %.3f' % rec['coverage'], 'ETH of borrowers %.0f' % esum)
    log('v1 chain', ch, 'silos', len(silos), 'with ETH deposits and stable debt', len(meta))
    return meta, rows


def main():
    which = [x for x in sys.argv[1:] if x in ('v1', 'v2')] or ['v1', 'v2']
    only = [int(x) for x in sys.argv[1:] if x.isdigit()]
    parts = load('venues/silo_parts.json', {})
    for v in which:
        for ch in (V1F if v == 'v1' else V2F):
            if only and ch not in only: continue
            try:
                m, rows = (v1_chain if v == 'v1' else v2_chain)(ch)
            except Exception as e:
                log(v, ch, 'FAILED', e); m, rows = [dict(version=v, chain=ch, error=str(e))], []
            parts['%s_%d' % (v, ch)] = dict(meta=m, rows=rows)
            save('venues/silo_parts.json', parts)
    allrows = [r for p in parts.values() for r in p['rows']]
    pos = [r for r in allrows if r['eth_backing_dollar'] >= 100]
    for r in pos:
        r['account_code'], r['account_delegate'] = code_kind(r['chain'], r['account'], r['block'])
    pos.sort(key=lambda r: -r['eth_backing_dollar'])
    mm = [x for p in parts.values() for x in p['meta']]
    v2tot = sum(x.get('eth_collateral_total') or 0 for x in mm if x.get('version') == 'v2')
    v1tot = sum(x.get('eth_deposits') or 0 for x in mm if x.get('version') == 'v1')
    summary = dict(venue='silo', snapshot='2026-10-02 23:59:59 UTC', eth_usd=ETH_USD,
                   v2_eth_collateral_in_eth_stable_markets_with_debt=v2tot, v1_eth_deposits_in_silos_with_stable_debt=v1tot,
                   eth_collateral_of_enumerated_stable_borrowers=sum(r['eth_collateral'] for r in allrows),
                   positions_ge100=len(pos), positions_ge100_eth=sum(r['eth_backing_dollar'] for r in pos), method=__doc__.strip())
    save('venues/silo.json', dict(meta=[summary] + mm, positions=pos))
    log('silo positions >= 100', len(pos), 'ETH %.0f' % summary['positions_ge100_eth'], 'v2 market ETH %.0f' % v2tot, 'v1 ETH dep %.0f' % v1tot)


if __name__ == '__main__':
    main()
