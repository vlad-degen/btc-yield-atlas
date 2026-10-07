"""Liquidity ladder at T for each product's ETH-collateral dollar debt -> data/eth/gap_top5_liquidity_ladder.json"""
import json, csv
from glib import *
L = json.load(open(RAW / 'ladder_T_raw.json'))
S = [r for r in csv.DictReader(open(ROOT / 'data/eth/gap_top5_risk_series.csv')) if r['period'] == 'T']
def sv(prod, acct_sub, metric):
    v = [float(r['value']) for r in S if r['product'] == prod and acct_sub in r['account'] and r['metric'] == metric]
    return sum(v)
ETH = L['ethusd']
def leg(prod, acct, label):
    d = sv(prod, acct, 'dollar_debt_usd'); cl = sv(prod, acct, 'collateral_usd')
    return {'leg': label, 'account': acct.split('@')[0], 'debtUSD': d, 'collateralUSD': cl, 'ltv': d / cl if cl else None}
def release(lg, repaid):
    """ETH-equivalent collateral releasable when `repaid` of the leg is repaid, keeping the leg's LTV unchanged"""
    if lg['debtUSD'] <= 0: return 0
    f = min(repaid / lg['debtUSD'], 1.0)
    return f * lg['collateralUSD'] / ETH
out = {'snapshot': {'timestamp': T, 'utc': '2026-10-02T23:59:59Z', 'block': TB}, 'ethUsdChainlinkAtT': ETH,
       'conventions': ['Tiers measure what the position controller (curator/strategist) can repay, not what an investor can redeem.',
                       'Same block = executable in one transaction/block from destination liquidity readable at T (idle + permissionless forceDeallocate / instant ERC4626 withdraw / LP removal).',
                       'ETH released = collateral USD x (repaid / leg debt), i.e. keeping each leg\'s LTV unchanged, converted at Chainlink ETH/USD at T; LST/LRT collateral shown as ETH-equivalent USD/ETH.',
                       'Assumes no competing withdrawals by other depositors of shared destination vaults in the same block; stablecoins at $1.',
                       'Raw reads: raw/eth/gap-2026-10-07/top5-risk/ladder_T_raw.json, positions_raw.json, aave_legs_raw.json'], 'products': {}}
# ---------------- Liquid
A = leg('liquid', '0xf0bb20865277abd641a307ece5ee04e79073416c@Morpho:weETH/RLUSD', 'Morpho weETH/RLUSD (main vault)')
B = leg('liquid', '0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3@Morpho:weETH/RLUSD', 'Morpho weETH/RLUSD (LoanManager)')
Cc = leg('liquid', '0xf0bb20865277abd641a307ece5ee04e79073416c@Morpho:weETH/USDC', 'Morpho weETH/USDC (main vault)')
D = leg('liquid', '0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c@AaveV3', 'Aave V3 USDC+USDT vs weETH (drone)')
E = leg('liquid', '0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c@SparkV3', 'Spark PYUSD vs wstETH (drone)')
H = L['holders']['0xf0bb20865277abd641a307ece5ee04e79073416c']
rl = L['v2']['senRLUSDv2']; py = L['v2']['senPYUSDPRIMEv2']
rl_liq = rl['idle'] + sum(m['vaultWithdrawable'] for m in rl['markets'])
py_liq = py['idle'] + sum(m['vaultWithdrawable'] for m in py['markets'])
rl_claim = H['senRLUSDv2']['assets']; py_claim = H['senPYUSDPRIMEv2']['assets']; stc = H['stcUSD']['assets']
rl_out = min(rl_claim, rl_liq); py_out = min(py_claim, py_liq)
cap_usdc = L['cap']['reserves']['USDC']['availableBalance']
usdc_out = min(stc, cap_usdc)
debt = sum(x['debtUSD'] for x in [A, B, Cc, D, E])
# currency-matched same block
repA = min(rl_out, A['debtUSD']); repB = min(rl_out - repA, B['debtUSD'])
repE = min(py_out, E['debtUSD']); repC = min(usdc_out, Cc['debtUSD'])
t1a = repA + repB + repE + repC
rel1a = release(A, repA) + release(B, repB) + release(E, repE) + release(Cc, repC)
# with swap: leftover PYUSD from static senPYUSDPRIMEv2 liquidity into USDC/USDT for Aave drone
swap_py = py_out - repE
repD_swap = min(swap_py, D['debtUSD'])
rel1b = release(D, repD_swap)
cusd_left = stc - usdc_out
prime_coll = 26355966.0; prime_debt = 21017988.0  # fixed-block Morpho PRIME/PYUSD read (see md), main vault
prime_net = prime_coll - prime_debt
rem_after = debt - t1a - repD_swap
t3_cap = min(cusd_left, rem_after)
py_stuck = py_claim - py_out
t3_py = min(py_stuck, rem_after - t3_cap)
t3_prime = min(prime_net, rem_after - t3_cap - t3_py)
unmatched = debt - t1a - repD_swap - t3_cap - t3_py - t3_prime
out['products']['liquid'] = {
    'dollarDebtUSD': debt, 'legs': [A, B, Cc, D, E],
    'destinationClaimsAtT': {'senRLUSDv2': {'claimRLUSD': rl_claim, 'vaultIdle': rl['idle'], 'forceDeallocatableLiquidity': rl_liq - rl['idle'], 'forceDeallocatePenalty': list(rl['forceDeallocatePenalty'].values())[0],
                                            'note': f"weETH/RLUSD market (where Liquid borrows) holds {next(m['vaultSupply'] for m in rl['markets'] if m['collateral']=='weETH')/1e6:.2f}M of the vault"},
                             'senPYUSDPRIMEv2': {'claimPYUSD': py_claim, 'vaultIdle': py['idle'], 'forceDeallocatableLiquidity': py_liq - py['idle'], 'forceDeallocatePenalty': list(py['forceDeallocatePenalty'].values())[0],
                                                 'note': 'only market is PRIME/PYUSD, where Liquid main vault itself borrows 21.02M PYUSD against 24.81M PRIME'},
                             'stcUSD': {'claimCUSD': stc, 'maxWithdraw': H['stcUSD']['maxWithdraw'], 'capUSDCavailable': cap_usdc, 'capUSDCsupplied': L['cap']['reserves']['USDC']['totalSupplies'], 'capUSDCborrowed': L['cap']['reserves']['USDC']['totalBorrows']},
                             'PRIME_morpho_collateral': {'valueUSD': prime_coll, 'PYUSDdebtAgainstIt': prime_debt, 'net': prime_net},
                             'idle': {k: H[k] for k in ['RLUSD', 'USDC', 'USDT', 'cUSD', 'WETH']}},
    'tiers': [
        {'tier': 'T1a same block, currency-matched', 'usd': t1a, 'pct': t1a / debt, 'ethReleased': rel1a,
         'detail': f'senRLUSDv2 {rl_out/1e6:.2f}M RLUSD (idle {rl["idle"]/1e6:.2f}M + forceDeallocate {(rl_liq-rl["idle"])/1e6:.2f}M, 1 bp) repays RLUSD legs; senPYUSDPRIMEv2 -> {repE/1e6:.2f}M PYUSD repays Spark; stcUSD->cUSD->USDC {repC/1e6:.2f}M (Cap available USDC) repays Morpho USDC'},
        {'tier': 'T1b same block, needs PYUSD->USDC/USDT swap', 'usd': repD_swap, 'pct': repD_swap / debt, 'ethReleased': rel1b,
         'detail': f'remaining static senPYUSDPRIMEv2 liquidity {swap_py/1e6:.2f}M PYUSD (idle {py["idle"]/1e6:.2f}M + forceDeallocate {(py_liq-py["idle"])/1e6:.2f}M at 1% penalty) swapped for Aave USDC/USDT; DEX depth not verified'},
        {'tier': 'T2 within ~1 day', 'usd': 0.0, 'pct': 0.0, 'ethReleased': 0.0, 'detail': 'no queue with a <=1-day settlement found for the remaining claims'},
        {'tier': 'T3 slower / conditional', 'usd': t3_cap + t3_py + t3_prime, 'pct': (t3_cap + t3_py + t3_prime) / debt, 'ethReleased': release(D, t3_cap + t3_py + t3_prime) if D['debtUSD'] - repD_swap >= t3_cap + t3_py + t3_prime else None,
         'detail': f'senPYUSDPRIMEv2 remainder {py_stuck/1e6:.2f}M locked in PRIME/PYUSD (frees only as PRIME borrowers repay; Liquid itself owes 21.02M there); cUSD left after Cap USDC is exhausted {cusd_left/1e6:.2f}M (needs Cap agents to repay {L["cap"]["reserves"]["USDC"]["totalBorrows"]/1e6:.1f}M USDC or DEX exit); PRIME net of own PYUSD loan {prime_net/1e6:.2f}M (Hastra wYLDS->USDC, 1-2 business days per BTC study)'},
        {'tier': 'Unmatched: no dollar destination claim found at T', 'usd': unmatched, 'pct': unmatched / debt, 'ethReleased': None,
         'detail': 'debt exceeds the destination claims found on the three Liquid accounts (senRLUSDv2, senPYUSDPRIMEv2, stcUSD, PRIME); the remainder would have to come from selling ETH collateral or other book assets'}],
    'totalEthCollateralIfAllRepaid': sum(x['collateralUSD'] for x in [A, B, Cc, D, E]) / ETH,
    'notes': ['Ladder excludes the separate PRIME/PYUSD loan (21.02M PYUSD against PRIME, LTV 79.7%, LLTV 86%) because its collateral is not ETH; repaying it with senPYUSDPRIMEv2 PYUSD only recycles the same liquidity.',
              'senPYUSDPRIMEv2 forceDeallocate penalty is 1% (vs 1 bp on senRLUSDv2).']}
# ---------------- Lido Earn
la = leg('lido-earn', '0x181cb55f872450d16ae858d532b4e35e50eaa76d@AaveV3', 'Aave V3 USDT vs wstETH'); ls_ = leg('lido-earn', '0x181cb55f872450d16ae858d532b4e35e50eaa76d@SparkV3', 'Spark USDT vs wstETH')
ea = L['earnUSD']; claim = ea['balance'] * ea['usdtPerShare']; ldebt = la['debtUSD'] + ls_['debtUSD']
redq = sum(q['assetBalance'] for a in ea['assets'].values() for q in a['queues'] if not q['isDeposit'])
out['products']['lido-earn'] = {'dollarDebtUSD': ldebt, 'legs': [la, ls_],
    'destinationClaimsAtT': {'earnUSD': {'shares': ea['balance'], 'usdtPerShare': ea['usdtPerShare'], 'claimUSDT': claim, 'shareOfEarnUSDSupply': ea['balance'] / ea['totalSupply'],
                                         'vaultIdle': {k: v['vaultIdle'] for k, v in ea['assets'].items()}, 'redeemQueueBalances': redq}},
    'tiers': [{'tier': 'T1 same block', 'usd': 0.0, 'pct': 0.0, 'ethReleased': 0.0, 'detail': f'earnUSD vault idle is 0; redeem queues hold only {redq/1e3:.0f}k already reserved for earlier requests; account idle 41 USDe'},
              {'tier': 'T2 within ~1 day (earnUSD redeem queue, settles at next oracle report; reports ~every 24h, T report 17.3h old)', 'usd': min(claim, ldebt), 'pct': min(claim, ldebt) / ldebt,
               'ethReleased': (la['collateralUSD'] + ls_['collateralUSD']) / ETH * min(claim, ldebt) / ldebt,
               'detail': f'claim {claim/1e6:.2f}M USDT-equivalent = {ea["balance"]/ea["totalSupply"]*100:.1f}% of earnUSD supply; settlement depends on earnUSD unwinding its own strategies (not verified)'},
              {'tier': 'T3 slower', 'usd': max(ldebt - claim, 0), 'pct': max(ldebt - claim, 0) / ldebt, 'ethReleased': 0.0, 'detail': ''}],
    'totalEthCollateralIfAllRepaid': (la['collateralUSD'] + ls_['collateralUSD']) / ETH}
# ---------------- Avant
aa = leg('avant', '0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd@AaveV3', 'Aave V3 USDC vs WETH/weETH'); as_ = leg('avant', '0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd@SparkV3', 'Spark USDS+PYUSD vs WETH/wstETH')
av = L['avant']; adebt = aa['debtUSD'] + as_['debtUSD']; acoll = aa['collateralUSD'] + as_['collateralUSD']
t1 = av['eUSDC']['maxWithdraw']; t1b = av['sdBOLD']['assets']
out['products']['avant'] = {'dollarDebtUSD': adebt, 'legs': [aa, as_],
    'destinationClaimsAtT': {'ethereumWallet': av, 'offChainOrOtherChain': 'issuer portfolio (29 Sep) shows ~32.5M savUSD; savUSD lives mainly on Avalanche (0x06d47F3f...)'},
    'tiers': [{'tier': 'T1a same block', 'usd': t1, 'pct': t1 / adebt, 'ethReleased': acoll / ETH * t1 / adebt, 'detail': 'Euler eUSDC maxWithdraw -> USDC repays Aave USDC'},
              {'tier': 'T1b same block with LP exit/swap', 'usd': t1b, 'pct': t1b / adebt, 'ethReleased': acoll / ETH * t1b / adebt, 'detail': 'Stake DAO sdBOLD (asset BOLD/avUSD Curve LP) -> remove liquidity -> swap to USDS/USDC'},
              {'tier': 'T2 ~1 day', 'usd': 0.0, 'pct': 0.0, 'ethReleased': 0.0, 'detail': 'savUSD->avUSD cooldown is 24h (docs), then bridge + avUSD sale/redemption; not counted here because the next step is longer'},
              {'tier': 'T3 1-7 days', 'usd': adebt - t1 - t1b, 'pct': (adebt - t1 - t1b) / adebt, 'ethReleased': acoll / ETH * (adebt - t1 - t1b) / adebt,
               'detail': 'savUSD on Avalanche: 24h unstake cooldown + bridge to Ethereum + avUSD redemption up to 7 days (docs) or DEX sale'}],
    'totalEthCollateralIfAllRepaid': acoll / ETH, 'docs': ['raw http/avant_unstaking-savassets.md', 'raw http/avant_redeeming-avassets.md']}
# ---------------- Liquity ETH Carry
lq = L['liquity']; tr = [r for r in S if r['product'] == 'liquity' and r['metric'] == 'dollar_debt_usd' and r['account'] != 'ALL']
ldebt = sum(float(r['value']) for r in tr); lcoll = sv('liquity', 'trove', 'collateral_usd'); wst = sv('liquity', 'trove', 'collateral_wsteth')
lp_out = min(lq['withdrawOneCoin_ebUSD'], ldebt)
out['products']['liquity'] = {'dollarDebtUSD': ldebt, 'legs': [{'leg': 'Ebisu wstETH trove 0x17fde209', 'debtUSD': ldebt, 'collateralUSD': lcoll, 'collateralWstETH': wst}],
    'destinationClaimsAtT': {'curve_ebUSD_USDC_LP': lq, 'idle': L['holders']['0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c'], 'uniswapV4_storedBookUSD': 159364.4},
    'tiers': [{'tier': 'T1a same block (Curve remove_liquidity_one_coin -> ebUSD)', 'usd': lp_out, 'pct': lp_out / ldebt, 'ethReleased': lcoll / ETH * lp_out / ldebt,
               'detail': f'calc_withdraw_one_coin(LP, ebUSD) = {lq["withdrawOneCoin_ebUSD"]/1e6:.3f}M; pool holds {lq["balances"][0]/1e6:.2f}M ebUSD / {lq["balances"][1]/1e6:.2f}M USDC; vault owns {lq["lp"]/lq["poolSupply"]*100:.1f}% of LP'},
              {'tier': 'T1b same block (swap idle WETH / Uniswap V4 position into ebUSD)', 'usd': ldebt - lp_out, 'pct': (ldebt - lp_out) / ldebt, 'ethReleased': lcoll / ETH * (ldebt - lp_out) / ldebt,
               'detail': f'idle {L["holders"]["0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c"]["WETH"]:.1f} WETH (~{L["holders"]["0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c"]["WETH"]*ETH/1e6:.2f}M) + V4 book 0.16M cover the residual; ebUSD left in the Curve pool after the one-coin exit ~{(lq["balances"][0]-lq["withdrawOneCoin_ebUSD"])/1e6:.2f}M'},
              {'tier': 'T2/T3', 'usd': 0.0, 'pct': 0.0, 'ethReleased': 0.0, 'detail': ''}],
    'totalEthCollateralIfAllRepaid': lcoll / ETH, 'collateralWstETH': wst,
    'notes': ['The vault depositor path is narrower: the 10% and 30% holder withdrawals revert at T (CAPITAL-INCOME-EXIT.md); this ladder is what the strategist can unwind.']}
# ---------------- YieldBasis
yb = L['yb']; share = yb['ammCollateralLP'] / yb['poolSupply']; crv_from_lp = share * yb['poolBalances'][0]; weth_from_lp = share * yb['poolBalances'][1]
ydebt = yb['ammDebt']
out['products']['yieldbasis'] = {'dollarDebtUSD': ydebt, 'legs': [{'leg': 'LEVAMM crvUSD debt vs Curve WETH/crvUSD LP', 'debtUSD': ydebt, 'collateralUSD': sv('yieldbasis', 'LEVAMM', 'collateral_usd')}],
    'destinationClaimsAtT': {'ammShareOfCurvePool': share, 'crvUSDinLPshare': crv_from_lp, 'WETHinLPshare': weth_from_lp, 'preview_withdraw_99pct_WETH': yb['preview_withdraw_99pct'], 'preview_withdraw_50pct_WETH': yb['preview_withdraw_50pct'],
                             'preview_withdraw_100pct': 'reverts'},
    'tiers': [{'tier': 'T1a same block (LT.withdraw removes LP pro rata and repays crvUSD in the same call)', 'usd': min(crv_from_lp, ydebt), 'pct': min(crv_from_lp, ydebt) / ydebt,
               'ethReleased': yb['preview_withdraw_99pct'] / 0.99 * min(crv_from_lp, ydebt) / ydebt,
               'detail': f'AMM owns {share*100:.2f}% of the Curve pool -> {crv_from_lp/1e6:.2f}M crvUSD vs {ydebt/1e6:.2f}M debt; preview_withdraw(99% of LT supply) = {yb["preview_withdraw_99pct"]:.1f} WETH'},
              {'tier': 'T1b same block (shortfall swapped from WETH inside the same pool)', 'usd': max(ydebt - crv_from_lp, 0), 'pct': max(ydebt - crv_from_lp, 0) / ydebt, 'ethReleased': None, 'detail': ''},
              {'tier': 'T2/T3', 'usd': 0.0, 'pct': 0.0, 'ethReleased': 0.0, 'detail': 'no external destination: the borrowed crvUSD never leaves the pool'}],
    'totalEthCollateralIfAllRepaid': weth_from_lp,
    'notes': ['preview_withdraw for 100% of LT supply reverts; 99% previews 10,200.9 WETH, 50% previews 5,212.8 WETH.']}
json.dump(out, open(ROOT / 'data/eth/gap_top5_liquidity_ladder.json', 'w'), indent=1)
for p, v in out['products'].items():
    print(p, f"debt {v['dollarDebtUSD']/1e6:.2f}M", [(t['tier'][:30], round(t['usd'] / 1e6, 2), round(100 * t['pct'], 1), round(t['ethReleased']) if t['ethReleased'] else t['ethReleased']) for t in v['tiers']], 'ETH if all repaid', round(v['totalEthCollateralIfAllRepaid']))
