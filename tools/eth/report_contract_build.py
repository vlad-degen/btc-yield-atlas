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
 'Concrete Delta weETH': ('unverified', 'Declared arbitrage; shared custody', 'Dollar debt is observed in a shared Safe; assets and debt attributable to Delta are unresolved.'),
 'ether.fi Liquid ETH': ('active', 'Active hybrid', 'Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled.'),
 'YieldBasis WETH': ('active', 'Active dollar-financed LP', 'Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate.'),
 'Rocksolid rETH': ('closing', 'Closing; nested carry', '728.48 ETH of Liquity shares is the evidenced nested carry claim; direct Aave debt is zero.'),
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
                                 'ETH book share value; external payouts and exit costs excluded',
                        'carryOnlyProfit': None})
    census = [{'name': p['product'], 'status': PRODUCT_STATUS[p['product']][0],
               'statusLabel': PRODUCT_STATUS[p['product']][1], 'allocationEvidence': PRODUCT_STATUS[p['product']][2],
               'bookETH': p['sizeETH'], 'bookUSD': p['sizeUSD'], 'carryEquityETH': p['sizeETH'] if p['product'] == 'YieldBasis WETH' else None,
               'nestedClaimETH': 728.48 if p['product'] == 'Rocksolid rETH' else None,
               'sources': p.get('sourceURLs', [])} for p in products]
    # The native custody and receipt series are separate layers. No sum is a net market total.
    coverage = [
      ['Native validator staking', 'Consensus issuance, tips and MEV', 'No exact all-validator balance at T', 'No full market history', 'Issuer benchmarks only', 'staking-restaking'],
      ['Liquid staking / restaking', 'Validator income; additional service rewards where realised', 'Issuer and security-layer claims; overlapping', '24-month protocol observations', 'Matched share conversions for selected issuers', 'staking-restaking'],
      ['ETH lending', 'Borrower interest', 'Lending claims, cash and debt measured separately', 'Protocol histories; selected reserve histories', 'Selected rates and share returns', 'LENDING-MARKETS'],
      ['ETH-debt loops', 'Leveraged staking-minus-ETH-funding spread', 'Fluid / Treehouse parents; Liquid, CIAN and Yearn positions', 'Selected product books, not monthly loop weights', 'Selected matched ETH book returns', 'PRODUCT-FINANCIAL-HISTORY'],
      ['Dollar carry', 'Dollar investment income minus dollar funding', 'Eight examined books; five have current traced routes; unassigned sleeves retained', '24 monthly whole-book observations; allocation weights incomplete', 'Matched 30-day books; three financed investment lots', 'CARRY-PRODUCTS'],
      ['Spot / short basis', 'Funding or dated-futures premium', 'Frozen ETH slice unmeasured; later Ethena disclosure separate', 'No complete frozen ETH-slice history', 'No matched ETH-long strategy comparison', 'ethena-basis'],
      ['Fixed maturity', 'Underlying income or principal-claim discount', 'Pendle / Spectra parent claims; market registries screened', 'Parent histories; maturity-level coverage partial', 'Payoff denomination checked; no full investor-return panel', 'pendle-pt'],
      ['DEX / trading liquidity', 'Swap fees; inventory and trader P&L', '28 verified ETH-custody pools; broader adapters incomplete', '24 month ends for that same pool subset', 'Custody is not LP profit; selected positions traced', 'CAPITAL-INCOME-EXIT'],
      ['Options / structured yield', 'Option premiums in exchange for contingent payoff', 'Materiality and funded capacity not established at T', 'Historical / retired product screens', 'No full premium, settlement and cash-return ledger', 'STRATEGY-UNIVERSE-EXPANSION'],
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
    material = src['carry_coverage_audit']['materialPools']
    parent_join = sum(r['disposition'].startswith('Parent covered') for r in material)
    out = {'schemaVersion': 1, 'snapshot': '2026-10-02T23:59:59Z',
           'headline': {'receiptClaimsETH': m['current']['by_category']['staking']['eth_ref'],
                        'receiptClaimsUSD': m['current']['by_category']['staking']['usd'],
                        'examinedBooks': len(census), 'currentRoutes': sum(r['status'] == 'active' for r in census),
                        'liquid730dExcessPP': two_year['liquidETH_minus_stETH_cumulative_pp'],
                        'scenarioCarryWithoutRewardsPP': src['carry_economics_chapter']['worked_example']['modeled_income']['result']['no_reward_carry_uplift_before_outer_fee'] * 100},
           'globalUniqueETH': None, 'globalCarryEquityETH': None,
           'sampleGrossBooksETH': sum(p['bookETH'] for p in census),
           'sampleTopTwoShare': sum(p['bookETH'] for p in census[:2]) / sum(p['bookETH'] for p in census),
           'census': census, 'matched30dReturns': returns, 'financedLots': loan_cases,
           'coverage': [{'family': r[0], 'income': r[1], 'capital': r[2], 'history': r[3], 'returns': r[4], 'report': r[5]} for r in coverage],
           'discovery': {'materialPools': len(material), 'parentDispositions': parent_join,
                         'otherDispositions': len(material) - parent_join, 'exhaustiveStrategyCensus': False},
           'custodySubsetETH': src['market_netting_closure']['headline']['physical_custody_floor_ETH'],
           'lpCustodyETH': src['market_netting_closure']['lp']['current_root_custody_ETH'],
           'sources': {n: hashlib.sha256((D / (n + '.json')).read_bytes()).hexdigest() for n in names}}
    (D / 'report_contract.json').write_text(json.dumps(out, indent=2) + '\n')
    for filename, heads, rows in [
      ('carry-common-30d.csv', ['product', 'start', 'end', 'days', 'ETH_book_return_pct', 'stETH_return_pct', 'excess_pp', 'basis'], [[r['name'], r['start'], r['end'], 30, r['bookReturnPct'], r['benchmarkReturnPct'], r['excessPercentagePoints'], r['basis']] for r in returns]),
      ('carry-status-and-capital.csv', ['product', 'status', 'whole_book_ETH', 'verified_carry_equity_ETH', 'evidence'], [[p['name'], p['status'], p['bookETH'], p['carryEquityETH'], p['allocationEvidence']] for p in census])]:
        with (D / filename).open('w', newline='') as f:
            w = csv.writer(f); w.writerow(heads); w.writerows(rows)
    h = out['headline']
    overview = f'''# ETH yield research: team briefing

Financial snapshot: **2 October 2026**. This briefing and the main page use the same generated analytical contract. Filters affect Market charts, not these answers.

## Answer

**Staking is the base income layer.** The protocol panel reports {h['receiptClaimsETH']/1e6:.2f}M ETH-equivalent staking and restaking claims. Receipts and security-layer balances overlap. This is neither unique validator stake nor the size of the complete yield market.

**Carry is a financing mechanism inside products.** We examine {h['examinedBooks']} books: {h['currentRoutes']} with current traced routes, one in Closing, one with historical dust debt, and one declared arbitrage book with unresolved shared custody. Their sizes cannot establish a global carry-equity total.

**Complexity must pay beyond staking.** Liquid's ETH book gained 6.85% over 730 days versus 5.49% for stETH, an excess of {h['liquid730dExcessPP']:.2f} percentage points. This whole-product result cannot be assigned entirely to carry. The RLUSD worked scenario contributes {h['scenarioCarryWithoutRewardsPP']:.2f} percentage points annually without destination rewards, before the outer fee; it is an illustration, not a measured market return.

## Market and two years of history

The eight Market groups organise protocol families. Loop-focused vaults, carry-linked parents and liquidity / mixed vaults retain full parent exposure. Lending infrastructure and CDP collateral are optional financing layers. Historical grouping is consistent across dates, but does not reconstruct changing portfolio weights. ETH equivalents normalise reported USD by each date's ETH reference quote; they are not always native token quantities. Missing and stale observations remain absent. The constant-cohort control holds protocol membership fixed, not the survival of the entire historical market.

Native consensus staking is outside the protocol panel. The verified physical-custody subset is {out['custodySubsetETH']:,.0f} ETH; some cash is idle, so it is not an earning-capital floor. The separately traced 28-pool liquidity subset holds {out['lpCustodyETH']:,.0f} ETH of custody. Neither subset is added to receipt claims. [Counting and custody](CAPITAL-INCOME-EXIT.md).

## Carry product development

The 24-month stacked bars show whole books for all eight examined products, with a small-book zoom. Liquid is the early large hybrid; new wrappers and Concrete's issued claim appear in 2025; Liquity and YieldBasis become funded in 2026. TAU unwinds and Rocksolid enters Closing. The bars establish changing books and routes, not new deposits or historical carry allocation.

## Largest examined books with carry links

The five largest whole books are Concrete Delta, Liquid ETH, YieldBasis WETH, Rocksolid and Liquity ETH Carry. Royco is an additional deep case. The first two represent {100*out['sampleTopTwoShare']:.2f}% of the eight-book sample, a sample concentration measure rather than a market share. Concrete's unassigned shared backing and Rocksolid's Closing status remain explicit.

{table(['Product', 'Whole book, ETH', 'Status', 'What is attributable'], [[p['name'], f"{p['bookETH']:,.0f}", p['statusLabel'], p['allocationEvidence']] for p in census])}

## What returns can be compared

All six detailed products have the same **2 September to 2 October 2026** return window. These are ETH book marks, excluding external payouts and exit costs. YieldBasis uses unstaked LT fair value. Recognised book income is not stripped into organic carry. Whole-product fees already recognised in share value are not deducted twice.

{table(['Product', '30-day ETH book return', 'Excess vs stETH, pp'], [[r['name'], f"{r['bookReturnPct']:.4f}%", f"{r['excessPercentagePoints']:+.4f}"] for r in returns])}

stETH's matched book return is **{benchmark['stETH_cumulative_return']*100:.4f}%**. Concrete follows weETH conversion with a flat weETH share price; no separate arbitrage profit is established by that price. These rows compare accounting claims, not independently verified realised cash returns.

## Financing, income and rewards

Three traced investment lots compare destination income with funding on the same borrowed principal through the measured exit or repayment date. They are selected cases, not a market average. The USDC lots use proportional redemption allocation; the PYUSD case includes the residual debt liability. Gas, collateral income and whole-wallet profit remain separate.

{table(['Borrowed amount', 'Investment income', 'Funding cost', 'Result before gas'], [[f"{r['borrowed']:,.0f} {r['currency']}", f"{r['income']:.6f}", f"{r['fundingCost']:.6f}", f"{r['resultBeforeGas']:.6f} {r['currency']}"] for r in loan_cases])}

Liquid's longer claim-growth, loan-interest and paid-reward ledgers have different principals and reward earning periods. Do not subtract their totals as complete carry profit. Payment through Merkl identifies a delivery route, not necessarily the economic sponsor or a committed future budget. [Financed lots](CARRY-LIFECYCLES.md) and [income attribution](CAPITAL-INCOME-EXIT.md).

## Product design

Secure a positive base spread in the debt currency after fees. Test every borrowing account and nested loan. Match the investment's redemption time to debt repayment and the investor queue. Compare cash after exit with staking on the same dates. Distribution, subsidy budgets and partner capacity require evidenced commercial terms; observed integrations alone do not establish them.

## Coverage

The material discovery screen contains {len(material)} ETH-name pools above $5M. {parent_join} dispositions join an already-covered parent; they do not prove that each pool's strategy has been reconstructed. Other public documentation adds ZenSats routes and mixed allocators. The family map is broad; unique market capital, historical sleeve weights, complete organic carry profit and funded options capacity remain unmeasured. [Coverage matrix](MARKET-COVERAGE.md).

## Reproduce the answers

[Canonical data](../../../data/eth/report_contract.json), [common return CSV](../../../data/eth/carry-common-30d.csv), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv). The main page, this briefing and the coverage matrix are rebuilt together from these frozen sources.
'''
    (EN / 'BRIEFING.md').write_text(overview)
    coverage_md = '''# Coverage of the ETH yield market

Financial snapshot: **2 October 2026**. This is a family-by-family map of measured evidence, not a claim that every wallet, private strategy or protocol is fully reconstructed.

## Capital, history and investor returns

''' + table(['Family', 'Income mechanism', 'Capital evidence', 'History evidence', 'Return evidence'], [r[:5] for r in coverage]) + f'''

## Discovery is not strategy attribution

The saved DefiLlama screen contains **{len(material)}** ETH-name pools above $5M from **{src['carry_coverage_audit']['materialProjects']}** projects. **{parent_join}** are joined to an existing parent; the other **{len(material)-parent_join}** receive separate dispositions. These are discovery decisions, not {len(material)} independently reconstructed strategies or additive ETH capital. [Individual decisions](CARRY-COVERAGE-AUDIT.md).

## Three boundaries that affect the answer

1. **Capital:** receipt claims, lending collateral, managed shares and underlying custody overlap. Global unique ETH and global carry equity are not measured. Native consensus balances are outside the protocol panel. Four major liquidity adapters lack usable token history at T; the 28-pool custody reconstruction is a separate bounded subset.
2. **History:** categories group protocol families consistently. Their monthly NAV is not a history of strategy allocations or external deposits. A constant cohort controls observation availability, while current discovery can omit dead products.
3. **Income:** matched book returns, financed investment-lot results and complete strategy profit answer different questions. Reward sponsor, earning period, own-credit flows, outer fees and exit cash must be assigned before stating organic carry profit.

## Carry routes and current status

{table(['Product', 'Status', 'Attribution boundary'], [[p['name'], p['statusLabel'], p['allocationEvidence']] for p in census])}

Five examined products have current traced routes, including the small Reservoir position and stale-mark Royco. Rocksolid is Closing, TAU's current debt is dust, and Concrete's published arbitrage mandate does not establish a product-attributed sleeve. ZenSats documents active LlamaLend / Curve / StakeDAO and legacy withdraw-only Aave / RAAC designs, with frozen capital unmeasured. [Official strategy documentation](https://www.zensats.app/docs/strategy).

## How to read TVL

DefiLlama separates borrowed balances and flags reused receipt assets. Native validator staking also has a different scope from chain DeFi TVL. Our token panel is a custom ETH-family exposure view, so it must not be labelled as their global TVL or unique market capital. [DefiLlama definitions](https://docs.llama.fi/analysts/data-definitions).

## Supporting research

[Team briefing](BRIEFING.md), [market structure](MARKET-STRUCTURE.md), [carry product evidence](CARRY-PRODUCTS.md), [custody and exits](CAPITAL-INCOME-EXIT.md), [additional product histories](PRODUCT-FINANCIAL-HISTORY.md), [strategy families](STRATEGY-UNIVERSE-EXPANSION.md). Financial observations retain their dates; later documentation does not fill missing values at T.
'''
    (EN / 'MARKET-COVERAGE.md').write_text(coverage_md)
    category_rows = []
    for c in m['categories']:
        cur = m['current']['by_category'][c['id']]
        first, last = m['months'][0]['by_category'][c['id']], m['months'][-1]['by_category'][c['id']]
        change = f"{100*(last['eth_ref']/first['eth_ref']-1):+.2f}%" if first['eth_ref'] and last['eth_ref'] is not None else 'Not measured'
        category_rows.append([c['label'], cur['coverage']['observed'], f"{cur['eth_ref']:,.0f}" if cur['eth_ref'] is not None else 'Not measured', change, 'Default' if c['default'] else 'Optional financing layer'])
    (EN / 'MARKET-STRUCTURE.md').write_text('''# ETH market structure and two years of history

Financial snapshot: **2 October 2026**. Monthly window: October 2024 to September 2026.

## A layered market

Staking is the base income source. Receipts move into lending, restaking and managed products; the same underlying ETH can support claims in multiple layers. The protocol panel groups full parent exposure by family. It does not measure unique ETH, investor equity or precise strategy weights. Native validator balances are outside the panel.

''' + table(['Protocol family', 'Observed parents at T', 'ETH-equivalent exposure', 'Oct 2024 to Sep 2026 change', 'Chart scope'], category_rows) + '''

## How to interpret history

The stacked bars retain a stable protocol-family mapping through 24 monthly snapshots. A mixed parent's entire book stays in its family. Changes reflect reported claims, conversion, membership and coverage; they are neither historical carry allocations nor external deposit flows. Constant cohort fixes the protocols observed at every date, while current discovery can still omit dead products. ETH equivalents use the dated ETH reference price; dollar values use reported token balances and marks. Missing and stale observations remain absent.

## Carry-linked parents versus product books

Concrete, ether.fi Liquid and YieldBasis form the three carry-linked protocol parents. Their adapter histories use different asset scopes and valuation dates from the eight contract-level product books. The latter include nested Liquity claims, historical carry and a declared arbitrage book. Neither series establishes global carry equity. The five largest examined books are Concrete Delta, Liquid, YieldBasis WETH, Rocksolid and Liquity. [Product status and attribution](CARRY-CATEGORY.md).

## Chains and missing liquidity history

The chain chart reports where adapters place balances, rather than validator geography or every strategy destination. Product chapters identify actual loan and investment chains. Unverified Tron mapped ETH stays excluded. Four major liquidity adapters lack token history at T; the separate 28-pool custody subset does not fill the whole DEX market. [Coverage by mechanism](MARKET-COVERAGE.md).

## Sources

[Reader ledger](../../../data/eth/market_reader_chapter.json), [original captured grouping](../../../data/eth/research_market_chapter.json), [custody and overlap evidence](CAPITAL-INCOME-EXIT.md), [current briefing](BRIEFING.md).
''')
    (EN / 'CARRY-CATEGORY.md').write_text('''# ETH dollar carry: products, positions and history

Financial snapshot: **2 October 2026**. Eight examined books have current, historical or declared carry links. A carry route retains ETH-family exposure, incurs dollar debt and deploys the financing to income-generating assets. Dollar-financed ETH liquidity is shown as its own subtype. An ETH loan used to buy more staking exposure is a loop; an offsetting ETH short is basis. Debt with no evidenced income destination is financing, not confirmed carry.

## Status and attributable capital

''' + table(['Product', 'Whole book ETH', 'Status', 'What is established'], [[p['name'], f"{p['bookETH']:,.0f}", p['statusLabel'], p['allocationEvidence']] for p in census]) + f'''

The gross sum is **{out['sampleGrossBooksETH']:,.0f} ETH** of overlapping sample book claims. Concrete and Liquid represent **{out['sampleTopTwoShare']*100:.2f}%** of that sample. These are not market size or concentration. Concrete's shared borrowing account cannot be assigned to Delta; Rocksolid's 728.48 ETH Liquity claim overlaps the underlying Liquity book. Current TAU debt is dust. YieldBasis net equity, actual crvUSD debt and staked gauge rights are different measurements.

## Two years of product development

The stacked bars show 24 month-end observations for all eight books; a small-book zoom uses the same records. Missing observations remain absent. Current labels are not historical allocation weights. Share issuance, staking conversion, portfolio movements and discovery coverage can change book NAV without outside deposits or new carry capital.

Liquid is the early large hybrid. Rocksolid and Reservoir acquire material books in September 2025, and Concrete's issued claim appears in December. Liquity becomes funded in March 2026; YieldBasis WETH is funded by May. TAU reduces its dollar liability and Rocksolid enters Closing on 29 September. These dates describe observed books and route changes.

## Carry variants

The examined routes include dollar lending, nested savings borrowing, senior credit, minted-dollar stablecoin LP, dollar-financed ETH LP and a manager's declared neutral arbitrage. Fixed-maturity and cross-chain destinations need separately verified loans and positions. ZenSats documents an active wstETH / LlamaLend / Curve / StakeDAO route and a legacy withdraw-only Aave / RAAC route; their frozen books are not measured. Mixed ETH allocators stay candidates until the actual loan and investment are traced. [Route decisions](CARRY-COVERAGE-AUDIT.md).

## Return and profit

The main comparison uses one 30-day ETH book window. Historical carry-only profit is not independently isolated for the whole sample. Three financed investment lots have matched principal and period evidence; their results cannot be scaled into market-wide carry returns. [Common returns and funded results](BRIEFING.md).

## Sources

[Status and capital CSV](../../../data/eth/carry-status-and-capital.csv), [24-month product ledger](../../../data/eth/reader_analysis.json), [deep product evidence](CARRY-PRODUCTS.md), [nested routes](CARRY-VARIANTS-EXPANSION.md), [capital and exits](CAPITAL-INCOME-EXIT.md).
''')
    (EN / 'PRODUCT-SELECTION.md').write_text('# Which products are compared?\n\nThe five largest examined whole books with carry links are Concrete Delta, Liquid ETH, YieldBasis WETH, Rocksolid and Liquity ETH Carry. Royco remains an additional deep case. This is a size ordering within the sample, not a ranking of active carry equity, realised profit or investment quality.\n\n' + table(['Product', 'Status', 'Whole book ETH'], [[p['name'], p['statusLabel'], f"{p['bookETH']:,.0f}"] for p in census]) + '\n\nThe common return comparison uses 30 days ending 2 October 2026. [Current briefing and matched results](BRIEFING.md).\n')
    print('Report contract: fixed answers, eight statuses, six common returns, ten coverage families.')
    return out


if __name__ == '__main__':
    run()
