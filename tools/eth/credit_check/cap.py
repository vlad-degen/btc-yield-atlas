"""Cap: agents (borrowers), their Symbiotic vaults / EigenLayer allocations (cover) and cUSD debt at T."""
from common import *
DELEG = '0xF3E3Eae671000612CE3Fd15e1019154C1a4d693F'; LENDER = '0x15622c3dbbc5614E6DFa9446603c1779647f01FC'
ORACLE = '0xcD7f45566bc0E7303fB92A93969BB4D3f6e662bb'; CUSD = '0xcCcc62962d17b8914c62D74FfB843d73B2a3cccC'
SYM = {'0x8c9140fe6650e56a0a07e86455d745f8f7843b6d': '0x44f7e678e8412dbef1fd930f60af2bd125095962',
       '0x09a3976d8d63728d20dcdfee1e531c206ba91225': '0x98e52ea7578f2088c152e81b17a9a459bf089f2a'}
EIG_SM = '0xe65c3eccd18879e103dbc96d854e376ced4cc7dd'; ALLOC = '0x948a420b8CC1d6BFd0B6087C2E7c344a2CD0bc39'
lg = logs(1, DELEG, [topic('AddAgent(address,address,uint256,uint256)')], 22867447, B1)
agents = []
for l in lg:
    w = l['data'][2:]; agents.append(dict(agent='0x' + w[24:64], mw='0x' + w[88:128], ltv=int(w[128:192], 16) / 1e27,
                                         liq=int(w[192:256], 16) / 1e27, block=int(l['blockNumber'], 16), tx=l['transactionHash']))
ra = logs(1, CUSD, [topic('AddAsset(address)')], 22874015, B1)
assets = sorted({'0x' + l['data'][-40:] for l in ra})
ra2 = logs(1, LENDER, [topic('ReserveAssetAdded(address,address,address,address,uint256)')], 22867447, B1)
assets = sorted(set(assets) | {'0x' + l['topics'][1][-40:] for l in ra2})
for a in agents:
    a['debt'] = {}
    for s in assets:
        d = U(c(1, LENDER, 'debt(address,address)', a['agent'], s))
        if d: a['debt'][s] = d
    if a['mw'] in SYM:
        v = A(c(1, a['mw'], 'vaults(address)', a['agent'])); a['vault'] = v
        a['collateral'] = A(c(1, v, 'collateral()'))
        a['vault_activeStake'] = U(c(1, v, 'activeStake()'))
        a['vault_bal'] = bal(1, a['collateral'], v)
        r = c(1, a['mw'], 'coverageByVault(address,address,address,address,uint48)', SYM[a['mw']], a['agent'], v, ORACLE, TS)
        a['coverage_value'] = U(r, 0); a['coverage_tokens'] = U(r, 1)
        a['delegator'] = A(c(1, v, 'delegator()')); a['slasher'] = A(c(1, v, 'slasher()'))
        try: a['vault_owner'] = A(c(1, v, 'owner()'))
        except Exception: pass
    elif a['mw'] == EIG_SM:
        st = A(c(1, EIG_SM, 'operatorToStrategy(address)', a['agent'])); op = A(c(1, EIG_SM, 'getEigenOperator(address)', a['agent']))
        a['strategy'] = st; a['eigen_operator'] = op; a['collateral'] = A(c(1, st, 'underlyingToken()')) if st and int(st, 16) else None
        if st and int(st, 16):
            data = sel('getAllocatedStake((address,uint32),address[],address[])') + a32(EIG_SM) + u32(1) + u32(0x80) + u32(0xc0) + u32(1) + a32(op) + u32(1) + a32(st)
            r = call1(1, ALLOC, data, B1); a['alloc_raw'] = r
            ww = words(r); a['coverage_tokens'] = ww[-1] if ww else None
            a['strategy_shares_total'] = U(c(1, st, 'totalShares()'))
            a['strategy_bal'] = bal(1, a['collateral'], st)
    else:
        a['note'] = 'unknown middleware'
    try:
        r = c(1, DELEG, 'coverage(address)', a['agent']); a['deleg_coverage_usd'] = U(r) / 1e8
    except Exception: pass
    try: a['deleg_slashable'] = U(c(1, DELEG, 'slashableCollateral(address)', a['agent'])) / 1e8
    except Exception: pass
    a['wst_rate'] = None
wst = U(c(1, WSTETH, 'stEthPerToken()')) / 1e18; we = U(c(1, WEETH, 'getRate()')) / 1e18
syms = {s: dec_str(c(1, s, 'symbol()')) for s in assets}
dec = {s: U(c(1, s, 'decimals()')) for s in assets}
save('cap.json', dict(block=B1, agents=agents, assets=assets, syms=syms, dec=dec, wsteth_rate=wst, weeth_rate=we,
                      cusd_supply=U(c(1, CUSD, 'totalSupply()'))))
tot = {}
for a in agents:
    col = (a.get('collateral') or '').lower(); ct = a.get('coverage_tokens') or 0
    tot[col] = tot.get(col, 0) + ct
    print(a['agent'], a['mw'][:10], a.get('vault'), col[:10], 'cov', round(ct / 1e18, 2), 'debt', {syms[k]: round(v / 10 ** dec[k], 0) for k, v in a['debt'].items()},
          'covUSD', a.get('deleg_coverage_usd'), 'ltv', a['ltv'])
print({k: v / 1e18 for k, v in tot.items()}, 'wst', wst, 'we', we)
