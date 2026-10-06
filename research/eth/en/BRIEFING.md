# ETH yield research: team briefing

Financial snapshot: **2 October 2026**. This briefing and the main page use the same generated analytical contract. Filters affect Market charts, not these answers.

## Answer

**Staking is the base income layer.** The protocol panel reports 20.19M ETH-equivalent staking and restaking claims. Receipts and security-layer balances overlap. This is neither unique validator stake nor the size of the complete yield market.

**Carry is a financing mechanism inside products.** We examine 8 books: 5 with current traced routes, one in Closing, one with historical dust debt, and one declared arbitrage book with unresolved shared custody. Their sizes cannot establish a global carry-equity total.

**Complexity must pay beyond staking.** Liquid's ETH book gained 6.85% over 730 days versus 5.49% for stETH, an excess of 1.36 percentage points. This whole-product result cannot be assigned entirely to carry. The RLUSD worked scenario contributes -0.84 percentage points annually without destination rewards, before the outer fee; it is an illustration, not a measured market return.

## Market and two years of history

The eight Market groups organise protocol families. Loop-focused vaults, carry-linked parents and liquidity / mixed vaults retain full parent exposure. Lending infrastructure and CDP collateral are optional financing layers. Historical grouping is consistent across dates, but does not reconstruct changing portfolio weights. ETH equivalents normalise reported USD by each date's ETH reference quote; they are not always native token quantities. Missing and stale observations remain absent. The constant-cohort control holds protocol membership fixed, not the survival of the entire historical market.

Native consensus staking is outside the protocol panel. The verified physical-custody subset is 457,182 ETH; some cash is idle, so it is not an earning-capital floor. The separately traced 28-pool liquidity subset holds 69,531 ETH of custody. Neither subset is added to receipt claims. [Counting and custody](CAPITAL-INCOME-EXIT.md).

## Carry product development

The 24-month stacked bars show whole books for all eight examined products, with a small-book zoom. Liquid is the early large hybrid; new wrappers and Concrete's issued claim appear in 2025; Liquity and YieldBasis become funded in 2026. TAU unwinds and Rocksolid enters Closing. The bars establish changing books and routes, not new deposits or historical carry allocation.

## Largest examined books with carry links

The five largest whole books are Concrete Delta, Liquid ETH, YieldBasis WETH, Rocksolid and Liquity ETH Carry. Royco is an additional deep case. The first two represent 94.83% of the eight-book sample, a sample concentration measure rather than a market share. Concrete's unassigned shared backing and Rocksolid's Closing status remain explicit.

| Product | Whole book, ETH | Status | What is attributable |
| --- | --- | --- | --- |
| Concrete Delta weETH | 307,363 | Declared arbitrage; shared custody | Dollar debt is observed in a shared Safe; assets and debt attributable to Delta are unresolved. |
| ether.fi Liquid ETH | 177,171 | Active hybrid | Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled. |
| YieldBasis WETH | 10,426 | Active dollar-financed LP | Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate. |
| Rocksolid rETH | 9,728 | Closing; nested carry | 728.48 ETH of Liquity shares is the evidenced nested carry claim; direct Aave debt is zero. |
| Liquity ETH Carry | 6,014 | Active minted-dollar LP | Ebisu collateral, ebUSD debt and dollar LP positions are measured; do not equate collateral with sleeve equity. |
| Royco ETH | 116 | Loan traced; parent marks stale | Morpho PYUSD debt and the senior credit receipt are traced; parent accounting and immediate exit remain restricted. |
| TAU InfiniFi ETH Carry | 82 | Historical; dust debt at T | Accrued debt is 0.022132 USDC at T; the old whole book is not current active carry equity. |
| Reservoir ETH Yield | 24 | Small current nested savings | Outer dollar borrowing and borrowing inside the savings destination are distinct liabilities. |

## What returns can be compared

All six detailed products have the same **2 September to 2 October 2026** return window. These are ETH book marks, excluding external payouts and exit costs. YieldBasis uses unstaked LT fair value. Recognised book income is not stripped into organic carry. Whole-product fees already recognised in share value are not deducted twice.

| Product | 30-day ETH book return | Excess vs stETH, pp |
| --- | --- | --- |
| Concrete Delta weETH | 0.1915% | +0.0066 |
| ether.fi Liquid ETH | 0.2610% | +0.0761 |
| YieldBasis WETH | -0.1622% | -0.3471 |
| Rocksolid rETH | 0.2192% | +0.0343 |
| Liquity ETH Carry | 0.4597% | +0.2748 |
| Royco ETH | 0.1849% | +0.0000 |

stETH's matched book return is **0.1849%**. Concrete follows weETH conversion with a flat weETH share price; no separate arbitrage profit is established by that price. These rows compare accounting claims, not independently verified realised cash returns.

## Financing, income and rewards

Three traced investment lots compare destination income with funding on the same borrowed principal through the measured exit or repayment date. They are selected cases, not a market average. The USDC lots use proportional redemption allocation; the PYUSD case includes the residual debt liability. Gas, collateral income and whole-wallet profit remain separate.

| Borrowed amount | Investment income | Funding cost | Result before gas |
| --- | --- | --- | --- |
| 350,000 USDC | 59.633841 | 146.057155 | -86.423314 USDC |
| 350,000 USDC | 32.206543 | 93.832732 | -61.626189 USDC |
| 1,000,000 PYUSD | 1.948867 | 2.347298 | -0.398431 PYUSD |

Liquid's longer claim-growth, loan-interest and paid-reward ledgers have different principals and reward earning periods. Do not subtract their totals as complete carry profit. Payment through Merkl identifies a delivery route, not necessarily the economic sponsor or a committed future budget. [Financed lots](CARRY-LIFECYCLES.md) and [income attribution](CAPITAL-INCOME-EXIT.md).

## Product design

Secure a positive base spread in the debt currency after fees. Test every borrowing account and nested loan. Match the investment's redemption time to debt repayment and the investor queue. Compare cash after exit with staking on the same dates. Distribution, subsidy budgets and partner capacity require evidenced commercial terms; observed integrations alone do not establish them.

## Coverage

The material discovery screen contains 299 ETH-name pools above $5M. 287 dispositions join an already-covered parent; they do not prove that each pool's strategy has been reconstructed. Other public documentation adds ZenSats routes and mixed allocators. The family map is broad; unique market capital, historical sleeve weights, complete organic carry profit and funded options capacity remain unmeasured. [Coverage matrix](MARKET-COVERAGE.md).

## Reproduce the answers

[Canonical data](../../../data/eth/report_contract.json), [common return CSV](../../../data/eth/carry-common-30d.csv), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv). The main page, this briefing and the coverage matrix are rebuilt together from these frozen sources.
