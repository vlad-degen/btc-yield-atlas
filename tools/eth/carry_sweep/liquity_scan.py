"""Liquity v1 (ETH/LUSD) and Liquity v2 plus forks (BOLD, Felix feUSD, Nerite USND, Ebisu ebUSD, USDaf, DefiDollar, Orki, Quill, Enosys)
with ETH-family branches. Every trove at T: debt and collateral from getLatestTroveData (v2) or getEntireDebtAndColl (v1);
v2 owner = TroveNFT.ownerOf(troveId); batch manager from Troves(id); individual interest delegate from BorrowerOperations.
ETH value of LST/LRT collateral = Aave v3 Core oracle price / WETH oracle price on Ethereum at T (mapped by symbol).
Collateral registries come from the DefiLlama Liquity registry (registries/liquity.js). Output venues/liquity.json."""
from vcommon import *  # noqa

L.RPCS[14] = ['https://flare-api.flare.network/ext/C/rpc', 'https://flare.rpc.thirdweb.com']
L.RPCS[1923] = ['https://swell.drpc.org']
L.RPCS.setdefault(534352, ['https://rpc.scroll.io', 'https://scroll.drpc.org'])
MIN = 100.0
REGISTRIES = [
    ('Liquity v2 (BOLD, pre-relaunch)', 1, '0xd99dE73b95236F69A559117ECD6F519Af780F3f7'),
    ('Liquity v2 (BOLD)', 1, '0xf949982b91c8c61e952b3ba942cbbfaef5386684'),
    ('Asymmetry USDaf', 1, '0xCFf0DcAb01563e5324ef9D0AdB0677d9C167d791'),
    ('Asymmetry USDaf', 1, '0x33D68055Cd54061991B2e98b9ab326fFCE4d60Fe'),
    ('DefiDollar CDP', 1, '0x1ec9287465ef04a7486779e81370c15624c939e8'),
    ('Ebisu (ebUSD)', 1, '0x5e159fAC2D137F7B83A12B9F30ac6aB2ba6d45E7'),
    ('Ebisu (ebUSD)', 9745, '0x602096a2f43b43d11dcb3713702dda963c45adc6'),
    ('Enosys Loans', 14, '0x9474206bc035D03d142264fd9913d1D51246d3AC'),
    ('Felix CDP (feUSD)', 999, '0x9De1e57049c475736289Cb006212F3E1DCe4711B'),
    ('Nerite (USND)', 42161, '0x7f7fbc2711c0d6e8ef757dbb82038032dd168e68'),
    ('Orki (USDK)', 1923, '0xce9f80a0dcd51fb3dd4f0d6bec3afdcaea10c912'),
    ('Quill (USDQ)', 534352, '0xcc4f29f9d1b03c8e77fc0057a120e2c370d6863d'),
    ('Quill (USDQ)', 534352, '0x358d90036e70542ae24b3813c0efecc1f8811442'),
]
AAVE_ORACLE = '0x54586bE62E3c3580375aE3723C145253060Ca0C2'
MAINNET = {'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'WSTETH': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0',
           'RETH': '0xae78736Cd615f374D3085123A210448E74Fc6393', 'WEETH': '0xCd5fE23C85820F7B72D0926FC9b05b43E359b7ee',
           'CBETH': '0xBe9895146f7AF43049ca1c1AE358B0541Ea49704', 'RSETH': '0xA1290d69c65A6Fe4DF752f95823fae25cB99e5A7',
           'EZETH': '0xbf5495Efe5DB9ce00f80364C8B423567e58d2110', 'OSETH': '0xf1C9acDc66974dFB6dEcB12aA385b9cD01190E38',
           'ETHX': '0xA35b1B31Ce002FBF2058D22F30f95D405200A15b', 'TETH': '0xD11c452fc99cF405034ee446803b6F6c1F6d5ED8'}
PLAIN = {'WETH', 'ETH', 'UETH', 'WETH.E'}

def eth_rates():
    b = vblk(1)
    syms = list(MAINNET)
    r = mcall(1, [(AAVE_ORACLE, cd('getAssetPrice(address)', MAINNET[s])) for s in syms], b)
    px = {s: U(x) for s, x in zip(syms, r)}
    w = px['WETH']
    return {s: px[s] / w for s in syms if px[s]}, w / 1e8

def eth_rate(symbol, rates):
    s = (symbol or '').upper()
    if s in PLAIN: return 1.0, 'plain ETH'
    for k in rates:
        if s == k or s.endswith(k): return rates[k], 'Aave Core oracle ratio %s/WETH' % k
    return None, 'no rate'

def scan_v2(name, ch, reg, rates):
    b = vblk(ch)
    if rpc(ch, 'eth_getCode', [reg, hex(b)]) in (None, '0x', ''): return [dict(venue=name, chain=ch, registry=reg, note='registry not deployed at T')], []
    n = U(call1(ch, reg, sel('totalCollaterals()'), b))
    metas = []; pos = []
    for i in range(n):
        r = mcall(ch, [(reg, cd('getToken(uint256)', i)), (reg, cd('getTroveManager(uint256)', i)), (reg, sel('boldToken()'))], b)
        tok = A(r[0]); tm = A(r[1]); debt_tok = A(r[2]) if r[2] else tok
        rr = mcall(ch, [(tok, sel('symbol()')), (tok, sel('decimals()')), (tm, sel('troveNFT()')), (tm, sel('borrowerOperations()')),
                        (tm, sel('getTroveIdsCount()')), (tm, sel('getEntireBranchColl()')), (tm, sel('getEntireBranchDebt()')),
                        (debt_tok, sel('symbol()'))], b)
        csym = dec_str(rr[0]); cdec = U(rr[1]) or 18; nft = A(rr[2]); bo = A(rr[3]); nt = U(rr[4])
        bcoll = U(rr[5]) / 10 ** cdec; bdebt = U(rr[6]) / 1e18; dsym = dec_str(rr[7])
        ap = A(call1(ch, tm, sel('activePool()'), b))
        apr = mcall(ch, [(ap, sel('getCollBalance()')), (ap, sel('getBoldDebt()'))], b) if ap else [None, None]
        ap_coll = U(apr[0]) / 10 ** cdec if apr[0] else None; ap_debt = U(apr[1]) / 1e18 if apr[1] else None
        if ap_coll is not None and ap_coll > bcoll:  # shut-down branches can report zero from getEntireBranchColl
            bcoll = ap_coll; bdebt = max(bdebt, ap_debt or 0)
        m = dict(venue=name, chain=ch, block=b, registry=reg, branch=i, collateral=tok, collateral_symbol=csym, debt_token=debt_tok,
                 debt_symbol=dsym if r[2] else None, trove_manager=tm, trove_nft=nft, borrower_operations=bo, n_troves=nt, active_pool=ap, active_pool_coll=ap_coll, active_pool_debt=ap_debt,
                 branch_collateral=bcoll, branch_debt=bdebt)
        if not is_eth(csym or ''):
            m['skip'] = 'not ETH-family collateral'; metas.append(m); continue
        rate, how = eth_rate(csym, rates)
        m.update(eth_per_unit=rate, rate_source=how, branch_collateral_eth=bcoll * rate if rate else None)
        ids = [U(x) for x in mcall(ch, [(tm, cd('getTroveFromTroveIdsArray(uint256)', k)) for k in range(nt)], b)]
        ltd = mcall(ch, [(tm, cd('getLatestTroveData(uint256)', t)) for t in ids], b)
        own = mcall(ch, [(nft, cd('ownerOf(uint256)', t)) for t in ids], b)
        trv = mcall(ch, [(tm, cd('Troves(uint256)', t)) for t in ids], b)
        dlg = mcall(ch, [(bo, cd('getInterestIndividualDelegateOf(uint256)', t)) for t in ids], b)
        ec = 0.0; ed = 0.0
        for t, l, o, tv, dg in zip(ids, ltd, own, trv, dlg):
            w = words(l) if l else [0, 0]
            debt = w[0] / 1e18; coll = w[1] / 10 ** cdec
            ec += coll; ed += debt
            eth = coll * rate if rate else None
            if eth is None or eth < MIN: continue
            tw = words(tv) if tv else []
            batch = ('0x' + hex(tw[8])[2:].rjust(40, '0')) if len(tw) > 8 and tw[8] else None
            dl = A(dg) if dg else None
            if dl and int(dl, 16) == 0: dl = None
            pos.append(dict(venue=name, chain=ch, block=b, market='%s branch %d (%s/%s)' % (name, i, csym, dsym), trove_manager=tm,
                            trove_id=hex(t), account=A(o) if o else None, collateral_symbol=csym, collateral_units=coll, eth_collateral=eth,
                            dollar_debt_usd=debt, eth_backing_dollar=eth, annual_interest_rate=(w[6] / 1e18 if len(w) > 6 else None),
                            batch_manager=batch, interest_delegate=dl))
        m.update(enumerated_collateral=ec, enumerated_debt=ed, coverage_collateral=ec / bcoll if bcoll else None,
                 coverage_debt=ed / bdebt if bdebt else None)
        log(name, ch, i, csym, 'troves', nt, 'coll %.1f' % bcoll, 'cov %.4f' % (m['coverage_collateral'] or 0))
        metas.append(m)
    return metas, pos

def scan_v1():
    ch = 1; b = vblk(1); tm = '0xA39739EF8b0231DbFA0DcdA07d7e29faAbCf4bb2'
    r = mcall(ch, [(tm, sel('getTroveOwnersCount()')), (tm, sel('getEntireSystemColl()')), (tm, sel('getEntireSystemDebt()'))], b)
    n = U(r[0]); scoll = U(r[1]) / 1e18; sdebt = U(r[2]) / 1e18
    owners = [A(x) for x in mcall(ch, [(tm, cd('getTroveFromTroveOwnersArray(uint256)', i)) for i in range(n)], b)]
    st = mcall(ch, [(tm, cd('getEntireDebtAndColl(address)', o)) for o in owners], b)
    pos = []; ec = 0.0; ed = 0.0
    for o, s in zip(owners, st):
        w = words(s); debt = w[0] / 1e18; coll = w[1] / 1e18
        ec += coll; ed += debt
        if coll >= MIN:
            pos.append(dict(venue='Liquity v1 (LUSD)', chain=1, block=b, market='ETH/LUSD', trove_manager=tm, account=o, collateral_symbol='ETH',
                            collateral_units=coll, eth_collateral=coll, dollar_debt_usd=debt, eth_backing_dollar=coll,
                            batch_manager=None, interest_delegate=None))
    m = dict(venue='Liquity v1 (LUSD)', chain=1, block=b, trove_manager=tm, collateral_symbol='ETH', debt_symbol='LUSD', n_troves=n,
             branch_collateral=scoll, branch_collateral_eth=scoll, branch_debt=sdebt, eth_per_unit=1.0, enumerated_collateral=ec, enumerated_debt=ed,
             coverage_collateral=ec / scoll, coverage_debt=ed / sdebt,
             note='system totals include pending redistribution rewards; Liquity v1 debt includes the 200 LUSD gas compensation per trove')
    log('v1 troves', n, 'coll %.1f' % scoll, 'cov %.4f' % m['coverage_collateral'])
    return [m], pos

def main():
    rates, wpx = eth_rates()
    log('rates', rates, 'WETH $', wpx)
    metas, pos = scan_v1()
    for name, ch, reg in REGISTRIES:
        try:
            m, p = scan_v2(name, ch, reg, rates)
        except Exception as e:
            log('FAIL', name, ch, e); metas.append(dict(venue=name, chain=ch, registry=reg, error=str(e)[:300])); continue
        metas += m; pos += p
    for ch in sorted({p['chain'] for p in pos}):
        k = kinds(ch, [p['account'] for p in pos if p['chain'] == ch], vblk(ch))
        for p in pos:
            if p['chain'] == ch: p['kind'] = k.get((p['account'] or '').lower())
    pos.sort(key=lambda p: -p['eth_collateral'])
    em = [m for m in metas if m.get('branch_collateral_eth') is not None]
    summary = dict(eth_price_usd_aave=wpx, eth_rates=rates, branches=len(em),
                   total_collateral_eth=sum(m['branch_collateral_eth'] for m in em), total_debt_usd=sum(m['branch_debt'] for m in em),
                   positions_ge_100=len(pos), eth_in_positions_ge_100=sum(p['eth_collateral'] for p in pos),
                   debt_in_positions_ge_100=sum(p['dollar_debt_usd'] for p in pos))
    vsave('liquity.json', {'summary': summary, 'meta': metas, 'positions': pos})
    log(json.dumps(summary, indent=1))

if __name__ == '__main__':
    main()
