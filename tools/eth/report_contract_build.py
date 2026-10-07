"""One analytical contract for the reader, briefing and coverage report.

All financial inputs are frozen captures. Never infer portfolio weights from a
parent's name, or convert a discovery disposition into a measured strategy.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'data/eth'
EN = ROOT / 'research/eth/en'

PRODUCT_STATUS = {
 'Concrete Delta weETH': ('unverified', 'One wallet\'s own position', 'A Bitfinex-linked wallet moved its own Aave position into the vault\'s Safe and holds 100% of the shares; $176.2M of stablecoin debt (Aave $105.7M, Morpho $70.4M). Not a pooled product; left out of the map.'),
 'ether.fi Liquid ETH': ('active', 'Active hybrid', 'Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled.'),
 'YieldBasis WETH': ('active', 'Active dollar-financed LP', 'Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate.'),
 'Rocksolid rETH': ('closing', 'Closing at T (29 Sep); reopened 7 Oct', 'Book reconciles to within 0.04% across Monad, Ethereum and a second wallet; $2.73M USDC carry (10.5% of book) plus 728.48 ETH of Liquity shares.'),
 'Liquity ETH Carry': ('active', 'Active minted-dollar LP', 'Ebisu collateral, ebUSD debt and dollar LP positions are measured; do not equate collateral with sleeve equity.'),
 'Royco ETH': ('active', 'Loan traced; parent marks stale', 'Morpho PYUSD debt and the senior credit receipt are traced; parent accounting and immediate exit remain restricted.'),
 'TAU InfiniFi ETH Carry': ('historical', 'Historical; dust debt at T', 'Accrued debt is 0.022132 USDC at T; the old whole book is not current active carry equity.'),
 'Reservoir ETH Yield': ('active', 'Small current nested savings', 'Outer dollar borrowing and borrowing inside the savings destination are distinct liabilities.'),
}


def table(head, rows):
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(['---'] * len(head)) + ' |',
                      *['| ' + ' | '.join(map(str, r)) + ' |' for r in rows]])


def run():
    names = ['market_reader_chapter', 'reader_carry_category', 'reader_product_chapters',
             'etherfi_staking_comparison', 'carry_economics_chapter', 'carry_coverage_audit',
             'market_netting_closure', 'credit_expansion_deep', 'carry_attribution_closure']
    src = {n: json.loads((D / (n + '.json')).read_text()) for n in names}
    m, pc = src['market_reader_chapter'], src['reader_product_chapters']['products']
    final = json.loads((D / 'finalization_reconstruction.json').read_text())
    for p in pc:
        if p.get('newReconstruction'):
            PRODUCT_STATUS[p['name']] = (p['status'], p['statusLabel'], p['allocationEvidence'])
    products = sorted([p for p in src['reader_carry_category']['products'] if p['classification'] == 'E4'], key=lambda p: -p['sizeETH'])
    benchmark = next(r for r in src['etherfi_staking_comparison'] if r['days'] == 30)
    two_year = next(r for r in src['etherfi_staking_comparison'] if r['days'] == 730)
    returns = []
    for p in pc:
        w = next(r for r in p['charts']['returnVsBorrow']['windowReturns'] if r['windowDays'] == 30)
        assert w['date'] == '2026-10-02T23:59:59Z' and w['startDate'] == '2026-09-02T23:59:59Z'
        returns.append({'id': p['id'], 'name': p['name'], 'start': w['startDate'], 'end': w['date'], 'days': 30,
                        'bookReturnPct': w['cumulativeReturnPct'],
                        'benchmarkReturnPct': benchmark['stETH_cumulative_return'] * 100,
                        'excessPercentagePoints': w['cumulativeReturnPct'] - benchmark['stETH_cumulative_return'] * 100,
                        'basis': 'Unstaked fair-value LT mark; gauge income excluded' if p['id'] == 'yieldbasis' else
                                 p.get('returnBasis', 'ETH book share value; external payouts and exit costs excluded'),
                        'carryOnlyProfit': None})
    census = [{'name': p['product'], 'status': PRODUCT_STATUS[p['product']][0],
               'statusLabel': PRODUCT_STATUS[p['product']][1], 'allocationEvidence': PRODUCT_STATUS[p['product']][2],
               'bookETH': p['sizeETH'], 'bookUSD': p['sizeUSD'], 'carryEquityETH': p['sizeETH'] if p['product'] == 'YieldBasis WETH' else None,
               'nestedClaimETH': 728.48 if p['product'] == 'Rocksolid rETH' else None,
               'sources': p.get('sourceURLs', [])} for p in products]
    # The native custody and receipt series are separate layers. No sum is a net market total.
    coverage = [
      ['Native validator staking', 'Consensus issuance, tips and MEV', '43.806M actual active ETH; 43.740M effective active ETH', 'Five archived month ends; earlier states pruned at tested public endpoints', 'Issuer benchmarks only', 'staking-restaking'],
      ['Liquid staking / restaking', 'Validator income; additional service rewards where realised', 'Issuer and security-layer claims; overlapping', '24-month protocol observations', 'Matched share conversions for selected issuers', 'staking-restaking'],
      ['ETH lending', 'Borrower interest', 'Lending claims, cash and debt measured separately', 'Protocol histories; selected reserve histories', 'Selected rates and share returns', 'LENDING-MARKETS'],
      ['ETH-debt loops', 'Leveraged staking-minus-ETH-funding spread', 'Fluid / Treehouse parents; Liquid, CIAN and Yearn positions', 'Selected product books, not monthly loop weights', 'Selected matched ETH book returns', 'PRODUCT-FINANCIAL-HISTORY'],
      ['Dollar carry', 'Dollar investment income minus dollar funding', 'Thirteen examined books; ten current traced routes; carry equity remains distinct from whole books', '24 monthly whole-book observations; allocation weights incomplete', 'Matched 30-day claims; four financed lots plus two flow-adjusted investment / funding ledgers', 'CARRY-PRODUCTS'],
      ['Spot / short basis', 'Funding or dated-futures premium', 'Frozen ETH slice unmeasured; later Ethena disclosure separate', 'No complete frozen ETH-slice history', 'No matched ETH-long strategy comparison', 'ethena-basis'],
      ['Fixed maturity', 'Underlying income or principal-claim discount', 'Pendle / Spectra parent claims; market registries screened', 'Parent histories; four active Ethereum PT faces verified at T; maturity coverage remains partial', 'Payoff denomination checked; no full investor-return panel', 'pendle-pt'],
      ['DEX / trading liquidity', 'Swap fees; inventory and trader P&L', '28 verified ETH-custody pools; broader adapters incomplete', '24 month ends for that same pool subset', 'Custody is not LP profit; selected positions traced', 'CAPITAL-INCOME-EXIT'],
      ['Options / structured yield', 'Option premiums in exchange for contingent payoff', 'Ribbon residual book: 713 ETH; current option expired in December 2025; other funded capacity partial', 'Historical / retired product screens', 'No full premium, settlement and cash-return ledger', 'STRATEGY-UNIVERSE-EXPANSION'],
      ['Mixed allocators / tranches', 'A blend of the mechanisms above', 'Parent books and selected sleeves; never add both as unique capital', 'Parent NAV; changing allocation weights incomplete', 'Selected share marks; strategy attribution incomplete', 'PRODUCT-FINANCIAL-HISTORY'],
    ]
    loan_cases = []
    for r in src['credit_expansion_deep']['cases']:
        income = r.get('allocated_vault_income_units', r.get('vault_income_units'))
        cost = r.get('funding_cost_through_redemption_units', r.get('funding_cost_through_repayment_units'))
        result = r.get('allocated_funded_result_before_gas_units', r.get('funded_result_before_gas_units'))
        loan_cases.append({'id': r['id'], 'currency': r['debt_currency'], 'borrowed': r['borrowed_units'],
                           'income': income, 'fundingCost': cost, 'resultBeforeGas': result,
                           'start': r['borrow_timestamp_UTC'], 'end': r.get('repay_timestamp_UTC', r['redeem_timestamp_UTC']),
                           'receipt': 'https://etherscan.io/tx/' + r['redeem_transaction'],
                           'completeWalletProfit': None})
    direct = final['directFinancedLot']
    loan_cases.append({**direct, 'completeWalletProfit': None})
    material = src['carry_coverage_audit']['materialPools']
    parent_join = sum(r['disposition'].startswith('Parent covered') for r in material)
    out = {'schemaVersion': 1, 'snapshot': '2026-10-02T23:59:59Z',
           'headline': {'nativeActiveETH': final['native']['activeBalanceETH'], 'nativeEffectiveETH': final['native']['activeEffectiveBalanceETH'], 'nativeActiveValidators': final['native']['activeValidatorCount'], 'receiptClaimsETH': m['current']['by_category']['staking']['eth_ref'],
                        'receiptClaimsUSD': m['current']['by_category']['staking']['usd'],
                        'examinedBooks': len(census), 'currentRoutes': sum(r['status'] == 'active' for r in census),
                        'liquid730dExcessPP': two_year['liquidETH_minus_stETH_cumulative_pp'],
                        'scenarioCarryWithoutRewardsPP': src['carry_economics_chapter']['worked_example']['modeled_income']['result']['no_reward_carry_uplift_before_outer_fee'] * 100},
           'globalUniqueETH': None, 'globalCarryEquityETH': None,
           'sampleGrossBooksETH': sum(p['bookETH'] for p in census),
           'sampleTopTwoShare': sum(p['bookETH'] for p in census[:2]) / sum(p['bookETH'] for p in census),
           'census': census, 'matched30dReturns': returns, 'financedLots': loan_cases, 'flowAdjustedLedgers': final.get('flowAdjustedLedgers', []),
           'coverage': [{'family': r[0], 'income': r[1], 'capital': r[2], 'history': r[3], 'returns': r[4], 'report': r[5]} for r in coverage],
           'discovery': {'materialPools': len(material), 'parentDispositions': parent_join,
                         'otherDispositions': len(material) - parent_join, 'exhaustiveStrategyCensus': False},
           'custodySubsetETH': src['market_netting_closure']['headline']['physical_custody_floor_ETH'],
           'lpCustodyETH': src['market_netting_closure']['lp']['current_root_custody_ETH'],
           'sources': {n: hashlib.sha256((D / (n + '.json')).read_bytes()).hexdigest() for n in names}}
    economic_path=D/'economic_questions.json'
    if economic_path.exists():
        economic=json.loads(economic_path.read_text())
        out['verifiedDollarFinancing']={'source':'data/eth/economic_questions.json','sourceSHA256':hashlib.sha256(economic_path.read_bytes()).hexdigest(),'directDebtUSD':economic['attributedDollarDebtUSD'],'topFive':economic['topFive'],'topTwoDebtShare':economic['topTwoDebtShare'],'unit':'Outstanding nominal-dollar financing; not TVL or equity'}
    (D / 'report_contract.json').write_text(json.dumps(out, indent=2) + '\n')
    for filename, heads, rows in [
      ('carry-common-30d.csv', ['product', 'start', 'end', 'days', 'ETH_book_return_pct', 'stETH_return_pct', 'excess_pp', 'basis'], [[r['name'], r['start'], r['end'], 30, r['bookReturnPct'], r['benchmarkReturnPct'], r['excessPercentagePoints'], r['basis']] for r in returns]),
      ('carry-status-and-capital.csv', ['product', 'status', 'whole_book_ETH', 'verified_carry_equity_ETH', 'evidence'], [[p['name'], p['status'], p['bookETH'], p['carryEquityETH'], p['allocationEvidence']] for p in census])]:
        with (D / filename).open('w', newline='') as f:
            w = csv.writer(f, lineterminator="\n"); w.writerow(heads); w.writerows(rows)
    h = out['headline']
    # Reader text below follows the counted-once market map (data/eth/netmap) and the
    # debt-ranked carry census (economic_questions.json). It never changes the JSON contract.
    _MN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    _mon = lambda p: f"{_MN[int(p[5:7]) - 1]} {p[:4]}"
    _M = lambda v: f"{v/1e6:.2f}M"
    _usdm = lambda v: f"${v/1e6:,.1f}M" if v >= 1e6 else (f"${v/1e3:,.0f}k" if v >= 1e3 else 'dust')
    _net = json.loads((D / 'netmap' / 'market_chapter.json').read_text())
    _eq = json.loads((D / 'economic_questions.json').read_text())
    _xc = json.loads((D / 'netmap' / 'crosscheck.json').read_text()) if (D / 'netmap' / 'crosscheck.json').exists() else None
    native = h['nativeActiveETH']
    _cat = {c['id']: _net['current']['by_category'][c['id']]['eth_ref'] or 0 for c in _net['categories']}
    _first = {c['id']: _net['months'][0]['by_category'][c['id']]['eth_ref'] or 0 for c in _net['categories']}
    _peak = lambda cid: max(_net['months'], key=lambda mm: mm['by_category'][cid]['eth_ref'] or 0)
    _peak_txt = lambda cid: f"{_M(_peak(cid)['by_category'][cid]['eth_ref'])} ETH ({_mon(_peak(cid)['period'])})"
    _tot = _net['default_current']['eth_ref']
    _carry_map = {p['name']: p['current']['eth_ref'] or 0 for p in _net['products'] if p['category'] == 'carry'}
    _cv = sorted(_carry_map.values(), reverse=True)
    _ncarry = sum(1 for v in _cv if v >= 0.5)
    _top2 = 100 * sum(_cv[:2]) / (sum(_cv) or 1)
    _debt = _eq['attributedDollarDebtUSD']
    _wbeth = next(p for p in _net['products'] if p['id'] == 'binance-staked-eth')
    _wbeth_growth = _wbeth['current']['eth_ref'] - _wbeth['history'][0]['eth_ref']
    _onchain_staked = _cat['staking'] + _cat['restaking']
    _offchain = 14.4e6  # OUTSIDE-AND-SMALL.md, data/eth/gap_outside_totals.csv
    _carry_rows = sorted(_eq['products'], key=lambda p: -(p['current']['debtUSD'] or 0))
    _top5_ids = _eq['topFive']
    _status = {
        'ether.fi Liquid ETH': 'Top five',
        'YieldBasis WETH': 'Top five',
        'Lido Earn ETH': 'Top five',
        'Avant avETH / savETH': 'Top five',
        'Liquity ETH Carry': 'Top five',
        'NEMO ETH Prime': 'Live; vault book reconciles with the loan',
        'Rocksolid rETH': 'Closed 29 Sep, reopened 7 Oct',
        'Sentora ETH': 'Live; vault book reconciles with the loans',
        'Makina DETH': 'Live; mostly a weETH loop',
        'Royco ETH': 'Live; parent marks stale, no immediate exit',
        'Vesper vaETH': 'Live; dollar leg trails its loan',
        'Reservoir ETH Yield': 'Emptied after a 2025 peak',
        'TAU InfiniFi ETH Carry': 'Unwound; 0.02 USDC of debt at T',
    }
    _book = lambda p: f"{p['bookETH']:,.0f}" if p.get('bookETH') else (f"{_carry_map[p['name']]:,.0f}" if _carry_map.get(p['name']) else '-')
    _carry_table = table(['Product', 'Dollars borrowed', 'Loan rate', 'Whole book, ETH', 'Status'],
                         [[p['name'], _usdm(p['current']['debtUSD'] or 0), f"{100*p['current']['apr']:.2f}%" if p['current']['apr'] is not None else '-', _book(p), _status.get(p['name'], '')] for p in _carry_rows])
    _others = [p for p in _carry_rows if p['id'] not in _top5_ids]
    _others_txt = ', '.join(f"{p['name']} ({_usdm(p['current']['debtUSD'] or 0)})" for p in _others)
    _answer = (f"**{_tot:,.0f} ETH earns a yield** in {_net['products_count_default']} products counted once (${_net['default_current']['usd']/1e9:.2f}B on 2 October 2026): "
               f"{100*_cat['staking']/_tot:.0f}% staking, {100*_cat['restaking']/_tot:.0f}% restaking, {100*_cat['farming']/_tot:.1f}% farming and pools. "
               "About 14.4M ETH more is staked off-chain with exchanges, institutional providers and BitMine; it is listed, not counted.\n\n"
               f"**Carry is {100*_cat['carry']/_tot:.1f}%**: {_cat['carry']:,.0f} ETH in {_ncarry} products that borrow dollars against ETH (in BTC it is 9.9%). "
               f"They owe {_usdm(_debt)}; Liquid ETH and Lido Earn hold {_top2:.0f}% of the books.\n\n"
               "**Carry barely beats staking.** Liquid ETH beat stETH by 0.66 pp a year over two years (3.37% against 2.71%). Its ETH loop added +0.02 pp a year and its dollar leg -0.13 pp; the rest is income our model cannot assign. "
               "At 2 October rates the dollar leg loses about $6.8M a year ($9.0M of interest on one 13.93% Aave USDC loan). YieldBasis is the only top-five product whose fees cover its loan.")
    _staking_txt = (f"The beacon chain holds **{native/1e6:.2f}M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: "
                    f"{_M(_cat['staking'])} ETH of staking and {_M(_cat['restaking'])} ETH of restaking, after removing staking tokens held by other products. "
                    f"About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. "
                    f"The remaining {_M(native - _onchain_staked - _offchain)} ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. "
                    "[Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).")
    _market = table(['Category', 'ETH, 2 Oct 2026', 'Share', 'Oct 2024', 'Switch'], [[c['label'], f"{_cat[c['id']]:,.0f}", f"{100*_cat[c['id']]/_tot:.1f}%" if c['default'] else 'off', f"{_first[c['id']]:,.0f}", 'on' if c['default'] else 'off'] for c in _net['categories']]) + \
        f"\n\nEach product is counted once: a staking token held by another product leaves its issuer's row. Money markets count only idle plain WETH and are off by default, because lent ETH is staked again by its borrowers. Binance's wBETH grew by {_M(_wbeth_growth)} ETH, the largest change on the map; restaking fell from {_peak_txt('restaking')} and farming and pools from {_peak_txt('farming')} as points programmes ended. [Method and every netting step](../../../data/eth/netmap/netting_ledger.csv)."
    _rows5 = [p for p in _carry_rows if p['id'] in _top5_ids]
    _top5 = table(['Product', 'Dollars borrowed', 'Loan rate', 'Book, ETH'], [[p['name'], _usdm(p['current']['debtUSD'] or 0), f"{100*(p['current']['apr'] or 0):.2f}%", f"{p['bookETH']:,.0f}" if p.get('bookETH') else ''] for p in _rows5])
    _concrete = ("Concrete Delta weETH (307,363 ETH, $176.15M of stablecoin debt) is left out of the map and the ranking: its whole supply was minted to one address after a Bitfinex-linked wallet moved its own Aave position into the vault's Safe; there are no outside depositors ([evidence](CONCRETE-DELTA.md)).")
    overview = f'''# ETH yield research: team briefing

Financial snapshot: **2 October 2026**. Same data as the main page.

## Answer

{_answer}

## Market and two years of history

{_market}

{_staking_txt}

## Top five carry products

Ranked by dollars borrowed against ETH. {_concrete}

{_top5}

Other carry: {_others_txt}. Rocksolid closed on 29 September and reopened on 7 October. ZenSats wstETH is a micro-position. [All carry products](CARRY-CATEGORY.md), [risk, repayment ladder and reward payers](TOP5-RISK-LIQUIDITY.md).

## 30-day returns

All products below use **2 September to 2 October 2026**: ETH book marks, before external payouts and exit costs. YieldBasis is the unstaked LT fair value. Fees already in the share price are not deducted again.

{table(['Product', '30-day ETH book return', 'Excess vs stETH, pp'], [[r['name'] + (' (excluded, reference only)' if r['name'].startswith('Concrete') else ''), f"{r['bookReturnPct']:.4f}%", f"{r['excessPercentagePoints']:+.4f}"] for r in returns])}

stETH returned **{benchmark['stETH_cumulative_return']*100:.4f}%** over the same days. Concrete's share price is flat in weETH, so its row is weETH staking and nothing else.

## Financed lots

Four loans traced from borrowing to the investment and back to repayment (or to T for the open Lido lot). Selected cases, not a market average; gas and collateral income excluded.

{table(['Borrowed amount', 'Investment income', 'Funding cost', 'Result before gas'], [[f"{r['borrowed']:,.0f} {r['currency']}", f"{r['income']:.6f}", f"{r['fundingCost']:.6f}", f"{r['resultBeforeGas']:.6f} {r['currency']}"] for r in loan_cases])}

[Financed lots and the two flow-adjusted ledgers](CARRY-LIFECYCLES.md), [Liquid income ledger](CAPITAL-INCOME-EXIT.md), [rewards split](REWARDS-SPLIT.md).

## Coverage

DefiLlama lists {len(material)} ETH-name pools above $5M; {parent_join} belong to a product already on the map and the other {len(material)-parent_join} have a written decision ([CARRY-COVERAGE-AUDIT](CARRY-COVERAGE-AUDIT.md)). What the map counts, lists and leaves out: [coverage](MARKET-COVERAGE.md).

## Reproduce the answers

[Canonical data](../../../data/eth/report_contract.json), [common return CSV](../../../data/eth/carry-common-30d.csv), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv), [market map CSV](../../../data/eth/netmap/market_map_current.csv).
'''
    (EN / 'BRIEFING.md').write_text(overview)
    _cov_rows = [
        ['Staking', _cat['staking'], 'Issuer backing (DefiLlama token breakdown), net of staking tokens held by other products', f"About 14.4M ETH staked off-chain (listed); beacon chain {native/1e6:.2f}M ETH active is the ceiling"],
        ['Restaking', _cat['restaking'], 'Restaking-token issuers; EigenLayer and Symbiotic only for what no restaking token counts (estimate)', 'Points and AVS rewards are not in the size'],
        ['Leveraged staking', _cat['loops'], 'Loop vaults (Fluid Lite, Treehouse, CIAN and others)', 'Loops inside Liquid ETH, Lido Earn and Makina stay in those products'],
        ['Carry', _cat['carry'], f"On-chain books and loans at block 26,108,081: {_ncarry} products, {_usdm(_debt)} of dollar debt", 'Concrete Delta (307k ETH) and three rSHARE vaults (about 83k WETH): private mandates, not products'],
        ['Fixed yield', _cat['fixed_yield'], 'Pendle and Spectra principal tokens on ETH-family assets', 'Expired markets count only their residual'],
        ['Basis, options, credit', _cat['basis'] + _cat['options'] + _cat['credit'], 'Protocol token series', 'Exchange margin and CeFi lenders (no ETH balances published)'],
        ['Farming and pools', _cat['farming'], 'DEX ETH pools above $1M (plain-ETH side), managed vaults, points programmes', 'History covers only pools that still exist'],
        ['Money markets (off)', _cat['lending'], 'Idle WETH no product counts', 'Off by default: lent ETH is staked again by borrowers'],
        ['CDP collateral (off)', _cat['cdp'], 'ETH posted to mint stablecoins', 'Off by default: the collateral earns nothing'],
    ]
    _excl = sorted(_net['excluded_protocols'], key=lambda x: -(x['eth'] or 0))[:6]
    _xc_txt = ''
    if _xc:
        _tv = _xc['tvl_by_status']; _all = sum(_tv.values())
        _xc_txt = (f"DefiLlama's yields page lists {_xc['pools_checked']} ETH pools above $1M. {100*_tv.get('map', 0)/_all:.1f}% of their TVL belongs to products on the map and "
                   f"{100*_tv.get('excluded', 0)/_all:.1f}% to rows left out for a stated reason; the rest (${(_all - _tv.get('map', 0) - _tv.get('excluded', 0))/1e6:,.0f}M) is pools under 100 ETH. ")
    coverage_md = f'''# Coverage of the ETH yield market

Financial snapshot: **2 October 2026**. What the counted-once map includes, what it lists without counting, and what it leaves out. Map total: **{_tot:,.0f} ETH** in {_net['products_count_default']} products.

## By category

{table(['Category', 'ETH counted', 'How it is counted', 'Not counted'], [[r[0], f"{r[1]:,.0f}", r[2], r[3]] for r in _cov_rows])}

## Staking: on-chain, off-chain and the beacon chain

{_staking_txt}

## Left out with a reason (largest)

{table(['Row', 'ETH', 'Why'], [[x['name'], f"{x['eth']:,.0f}", x['reason'].replace(' (research/eth/en/gaps/CONCRETE-DELTA.md)', '')] for x in _excl])}

Full list: Data, Listed but not counted, on the site; [netting ledger](../../../data/eth/netmap/netting_ledger.csv).

## Nothing large missed

{_xc_txt}The {len(material)} ETH-name pools above $5M in the carry screen: {parent_join} belong to a product already counted, the other {len(material)-parent_join} have a written decision ([CARRY-COVERAGE-AUDIT](CARRY-COVERAGE-AUDIT.md)).

## Carry products and status

{_carry_table}

## Supporting research

[Team briefing](BRIEFING.md), [market structure](MARKET-STRUCTURE.md), [carry category](CARRY-CATEGORY.md), [off-chain and small categories](OUTSIDE-AND-SMALL.md), [Concrete Delta](CONCRETE-DELTA.md), [private mandates](BORROWER-IDENTITIES.md).
'''
    (EN / 'MARKET-COVERAGE.md').write_text(coverage_md)
    (EN / 'MARKET-STRUCTURE.md').write_text('# ETH market: every product, counted once\n\nFinancial snapshot: **2 October 2026**. Month-ends October 2024 to September 2026.\n\n' + _market + '\n\n## Staking: on-chain, off-chain and the beacon chain\n\n' + _staking_txt + '\n\n## Method\n\nCategories follow where the yield comes from, as in the BTC study. Restaking platforms count only what no restaking token on the map already counts (estimate). DEX projects without a token breakdown are their ETH pools above $1M, plain-ETH side only; their history covers pools that still exist. Off-chain staking, ETFs, treasuries and the rows left out are listed with reasons on the site (Data, Listed but not counted) and in [coverage](MARKET-COVERAGE.md).\n\n[Map CSV](../../../data/eth/netmap/market_map_current.csv), [month-ends](../../../data/eth/netmap/market_map_history_monthly.csv), [netting ledger](../../../data/eth/netmap/netting_ledger.csv), [product notes](../../../data/eth/netmap/product_notes.csv).\n')
    _hist = [x for x in _eq['history'] if x['debtUSD']]
    _hist_txt = '; '.join(f"{_mon(x['month'])[:3]} {x['month'][:4]}: {_usdm(x['debtUSD'])}" for x in _eq['history'] if x['month'] in ('2025-08', '2025-09', '2025-10', '2026-04', '2026-05', '2026-07', '2026-08', '2026-09'))
    (EN / 'CARRY-CATEGORY.md').write_text(f'''# ETH dollar carry: products, debt and history

Financial snapshot: **2 October 2026**, Ethereum block 26,108,081.

## Findings

- **Carry is {100*_cat['carry']/_tot:.1f}% of ETH that earns a yield**: {_cat['carry']:,.0f} ETH in {_ncarry} products, owing **{_usdm(_debt)}** of dollar debt (BTC: 9.9%).
- **Two products dominate.** Liquid ETH and YieldBasis hold {100*_eq['topTwoDebtShare']:.0f}% of the debt; Liquid ETH and Lido Earn hold {_top2:.0f}% of the books.
- **Private mandates borrow as much as all the products.** Concrete Delta ($176.15M, one Bitfinex-linked wallet) and three whitelist-only rSHARE vaults run by one operator owe about $252M between them; both are left out of the map.
- **The spread is thin.** Liquid ETH beat stETH by 0.66 pp a year over two years; its loop added +0.02 pp and its dollar leg -0.13 pp. Only YieldBasis covers its loan from fees.
- **The book is new.** Carry debt was under $1M until August 2025 and grew from {_usdm(next(x['debtUSD'] for x in _eq['history'] if x['month']=='2026-05'))} in May 2026 to {_usdm(_debt)} at T.

## Products

Ranked by dollars borrowed against ETH. Whole book includes ETH loops and other sleeves; Rocksolid's 728 ETH of Liquity shares are counted once, in Liquity.

{_carry_table}

## Left out

- **Concrete Delta weETH** (307,363 ETH, $176.15M of USDT, USDC and PYUSD at 21.5% LTV): one principal's own position, minted to one address; ctwstETH+ (45,382 ETH) is the same Safe's circular holding. [CONCRETE-DELTA](CONCRETE-DELTA.md).
- **Three rSHARE vaults** (about 83k WETH): whitelist-only, one operator, NAV set off-chain. [BORROWER-IDENTITIES](BORROWER-IDENTITIES.md).
- **ETH-debt loops** (WETH borrowed to stake again) are leveraged staking, not carry. Liquid's inner PRIME/PYUSD loan ($21.0M) finances a dollar asset, not ETH, and is outside the direct total.

## Two years of debt

Month-end dollar debt: {_hist_txt}. Liquid ETH took its first Aave USDC loan in August 2025 and repaid in October; Reservoir peaked and emptied; Liquity borrowed from March 2026, YieldBasis WETH from May, Liquid's Morpho RLUSD, USDC and PYUSD loans from June. TAU unwound to dust. Rocksolid closed on 29 September and reopened on 7 October.

## Return and profit

The 30-day comparison and the four financed lots are in the [briefing](BRIEFING.md). Liquid's loop and dollar-leg split: [LIQUID-LOOP](LIQUID-LOOP.md); rewards: [REWARDS-SPLIT](REWARDS-SPLIT.md).

## Sources

[Canonical answers](../../../data/eth/economic_questions.json), [loan CSV](../../../data/eth/economic-dollar-loans.csv), [financing history CSV](../../../data/eth/economic-carry-history.csv), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv), [product evidence](CARRY-PRODUCTS.md), [route decisions](CARRY-COVERAGE-AUDIT.md).
''')
    (EN / 'PRODUCT-SELECTION.md').write_text('# Which products are compared\n\nThe top five are the carry products with the most dollars borrowed against ETH at the snapshot. By book size Lido Earn (83,309 ETH) would rank second; by debt YieldBasis ($27.8M) is above it. Concrete Delta is left out as one wallet\'s own position ([CONCRETE-DELTA](CONCRETE-DELTA.md)).\n\n' + table(['Rank', 'Product', 'Dollars borrowed', 'Whole book, ETH'], [[i + 1, p['name'], _usdm(p['current']['debtUSD'] or 0), f"{p['bookETH']:,.0f}"] for i, p in enumerate(_rows5)]) + '\n\nEvery other carry product: [CARRY-CATEGORY](CARRY-CATEGORY.md). 30-day returns: [briefing](BRIEFING.md).\n')
    print(f'Report contract: {len(census)} books, {len(returns)} matched claim returns, ten coverage families.')
    return out


if __name__ == '__main__':
    run()
