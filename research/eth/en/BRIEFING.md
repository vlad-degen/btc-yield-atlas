# ETH yield research: team briefing

Financial snapshot: **2 October 2026**. This briefing and the main page use the same generated analytical contract. Filters affect Market charts, not these answers.

## Answer

**Staking is the base income layer.** The archived consensus state contains **43.81M actual active ETH**, with 874,362 active validators and 43.74M ETH of effective stake. The protocol panel separately reports 20.19M ETH-equivalent staking and restaking claims. Receipts and security-layer balances overlap. This is neither unique validator stake nor the size of the complete yield market.

**Carry is a financing mechanism inside products.** We examine 13 books: 10 with current traced routes, one in Closing, one with historical dust debt, and one declared arbitrage book with unresolved shared custody. Their sizes cannot establish a global carry-equity total.

**Complexity must pay beyond staking.** Liquid's ETH book gained 6.85% over 730 days versus 5.49% for stETH, an excess of 1.36 percentage points. This whole-product result cannot be assigned entirely to carry. The RLUSD worked scenario contributes -0.84 percentage points annually without destination rewards, before the outer fee; it is an illustration, not a measured market return.

## Market and two years of history

The eight Market groups organise protocol families. Loop-focused vaults, carry-linked parents and liquidity / mixed vaults retain full parent exposure. Lending infrastructure and CDP collateral are optional financing layers. Historical grouping is consistent across dates, but does not reconstruct changing portfolio weights. ETH equivalents normalise reported USD by each date's ETH reference quote; they are not always native token quantities. Missing and stale observations remain absent. The constant-cohort control holds protocol membership fixed, not the survival of the entire historical market.

Native consensus staking is measured separately from the protocol panel. Five archived monthly active-balance states cover May to September 2026; tested public sources prune the earlier states. Missing native history is not estimated from validator counts or interpolated. The verified physical-custody subset is 457,182 ETH; some cash is idle, so it is not an earning-capital floor. The separately traced 28-pool liquidity subset holds 69,531 ETH of custody. Neither subset is added to receipt claims. [Counting and custody](CAPITAL-INCOME-EXIT.md).

## Carry product development

The 24-month stacked bars show whole books for all thirteen examined products, with a small-book zoom. Liquid is the early large hybrid; new wrappers and Concrete's issued claim appear in 2025; Liquity and YieldBasis become funded in 2026. TAU unwinds and Rocksolid enters Closing. Avant becomes materially funded in September 2025; Lido Earn exceeds 1 ETH in the sampled March 2026 book. Vesper, Makina and ZenSats add smaller but distinct financing routes. The bars establish changing books and routes, not new deposits or historical carry allocation.

## Largest examined books with carry links

The five largest examined books are Concrete Delta, Liquid ETH, Lido Earn ETH, Avant and YieldBasis WETH. Smaller products, Closing and historical routes remain available as additional cases. Avant’s size uses avETH face supply; its return uses the senior savETH claim. Lido uses oracle-valued shares including allocated shares. These conventions are explicit. The first two represent 79.38% of the thirteen-book sample, a sample concentration measure rather than a market share. Concrete's unassigned shared backing and Rocksolid's Closing status remain explicit.

| Product | Whole book, ETH | Status | What is attributable |
| --- | --- | --- | --- |
| Concrete Delta weETH | 307,363 | Declared arbitrage; shared custody | Dollar debt is observed in a shared Safe; assets and debt attributable to Delta are unresolved. |
| ether.fi Liquid ETH | 177,171 | Active hybrid | Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled. |
| Lido Earn ETH | 83,309 | Active hybrid | Earn ETH reports 83,309 ETH. Its main holding is stRATEGY, whose book must not be added again. The nested portfolio owes about 355,217 WETH in staking loops and 25.55M USDT in its main dollar-carry account. Those are gross loans, not the carry sleeve’s equity. |
| Avant avETH / savETH | 12,583 | Active hybrid | The published 29 September portfolio has a $33.18M net NAV and a $32.53M savUSD position. Ethereum reads at T confirm USDC, USDS and PYUSD borrowing against ETH collateral. The large own-credit destination makes this a concentrated issuer dependency. |
| YieldBasis WETH | 10,426 | Active dollar-financed LP | Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate. |
| Rocksolid rETH | 9,728 | Closing; nested carry | 728.48 ETH of Liquity shares is the evidenced nested carry claim; direct Aave debt is zero. |
| Liquity ETH Carry | 6,014 | Active minted-dollar LP | Ebisu collateral, ebUSD debt and dollar LP positions are measured; do not equate collateral with sleeve equity. |
| Makina DETH | 2,499 | Active hybrid | DETH reports 2,499 ETH in a cached book. Its hub has 15,065 WETH of Aave debt against weETH, plus a Morpho USDT / wstETH carry route. Verified accounting instructions identify the credit receipts instead of relying on the vault name. |
| Vesper vaETH | 1,052 | Active hybrid | vaETH reports 1,052 ETH. Its XY strategy supplies 57.35 WETH, owes 68,998 DAI and holds 60,034 vDAI shares. Other strategies in the same pool are lending or liquidity positions, so the whole pool cannot be labelled carry. |
| Royco ETH | 116 | Loan traced; parent marks stale | Morpho PYUSD debt and the senior credit receipt are traced; parent accounting and immediate exit remain restricted. |
| TAU InfiniFi ETH Carry | 82 | Historical; dust debt at T | Accrued debt is 0.022132 USDC at T; the old whole book is not current active carry equity. |
| Reservoir ETH Yield | 24 | Small current nested savings | Outer dollar borrowing and borrowing inside the savings destination are distinct liabilities. |
| ZenSats wstETH | 1 | Active micro-position | The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category. |

## What returns can be compared

All eleven detailed products have the same **2 September to 2 October 2026** return window. These are ETH book marks, excluding external payouts and exit costs. YieldBasis uses unstaked LT fair value. Recognised book income is not stripped into organic carry. Whole-product fees already recognised in share value are not deducted twice.

| Product | 30-day ETH book return | Excess vs stETH, pp |
| --- | --- | --- |
| Concrete Delta weETH | 0.1915% | +0.0066 |
| ether.fi Liquid ETH | 0.2610% | +0.0761 |
| Lido Earn ETH | 0.2513% | +0.0664 |
| Avant avETH / savETH | 0.3385% | +0.1536 |
| YieldBasis WETH | -0.1622% | -0.3471 |
| Rocksolid rETH | 0.2192% | +0.0343 |
| Liquity ETH Carry | 0.4597% | +0.2748 |
| Makina DETH | 0.3468% | +0.1619 |
| Vesper vaETH | 0.0698% | -0.1151 |
| Royco ETH | 0.1849% | +0.0000 |
| ZenSats wstETH | 0.2480% | +0.0630 |

stETH's matched book return is **0.1849%**. Concrete follows weETH conversion with a flat weETH share price; no separate arbitrage profit is established by that price. These rows compare accounting claims, not independently verified realised cash returns.

## Financing, income and rewards

Three traced exit / repayment lots and one directly matched open Lido investment compare destination income with funding on the same borrowed principal through the measured exit or repayment date. They are selected cases, not a market average. The USDC lots use proportional redemption allocation; the PYUSD case includes the residual debt liability. Gas, collateral income and whole-wallet profit remain separate.

| Borrowed amount | Investment income | Funding cost | Result before gas |
| --- | --- | --- | --- |
| 350,000 USDC | 59.633841 | 146.057155 | -86.423314 USDC |
| 350,000 USDC | 32.206543 | 93.832732 | -61.626189 USDC |
| 1,000,000 PYUSD | 1.948867 | 2.347298 | -0.398431 PYUSD |
| 5,000,000 USDT | 3651.565058 | 2250.992481 | 1400.572577 USDT |

Liquid's longer claim-growth, loan-interest and paid-reward ledgers have different principals and reward earning periods. Do not subtract their totals as complete carry profit. Payment through Merkl identifies a delivery route, not necessarily the economic sponsor or a committed future budget. [Financed lots](CARRY-LIFECYCLES.md) and [income attribution](CAPITAL-INCOME-EXIT.md).

## Product design

Secure a positive base spread in the debt currency after fees. Test every borrowing account and nested loan. Match the investment's redemption time to debt repayment and the investor queue. Compare cash after exit with staking on the same dates. Distribution, subsidy budgets and partner capacity require evidenced commercial terms; observed integrations alone do not establish them.

## Coverage

The material discovery screen contains 299 ETH-name pools above $5M. 287 dispositions join an already-covered parent; they do not prove that each pool's strategy has been reconstructed. Fixed-block reconstruction adds Lido Earn, Avant, Makina DETH, Vesper and ZenSats; YO ETH is separately classified as ETH lending / staking after inspecting its deployments. The family map is broad; global unique capital and complete historical sleeve weights remain unresolved. The reconstruction now measures native stake, five additional carry-linked books, four active PT faces and the residual Ribbon option book. Own-credit, fees and exit cash still limit complete organic carry attribution. [Coverage matrix](MARKET-COVERAGE.md).

## Reproduce the answers

[Canonical data](../../../data/eth/report_contract.json), [common return CSV](../../../data/eth/carry-common-30d.csv), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv). The main page, this briefing and the coverage matrix are rebuilt together from these frozen sources.


## Native stake: measured backing, not another wrapper

The archived consensus state at T has **43,805,557.723 actual active ETH**, **43,739,959 effective active ETH** and **874,362 active validators**. Actual balance and effective stake answer different questions. The active set includes 22,432 exiting validators. These balances are measured directly from validator objects, including compounding validators; they are not validator count multiplied by 32. Receipt claims are a separate, overlapping layer.

The archived slot is **15346798**, state root `0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282`. The public provider marks the response finalized and execution optimistic. The header state root agrees with the saved header; we do not claim an independent state-root recomputation from the validator JSON. Five successful monthly state reads cover May to September 2026. Earlier headers exist but their complete states are pruned at the tested public endpoints. Those missing balances remain absent.

[Archived state endpoint](http://testing.mainnet.beacon-api.nimbus.team/eth/v1/beacon/states/15346798/validators?status=active_ongoing,active_exiting,active_slashed), [monthly observations](../../../data/eth/native-staking-observations.csv), [normalised reconstruction and receipt hashes](../../../data/eth/finalization_reconstruction.json).


## Two additional dollar investment and funding ledgers

All figures below use **2 September to 2 October 2026**. New borrowing and repayments are removed from debt growth; share acquisitions and redemptions are removed from investment-value growth. External rewards, gas and executable exit costs are separate.

| Account | Debt token | Investment share-price income | Full-account interest | Difference, before other items |
| --- | --- | --- | --- | --- |
| lido | USDT | 84,397.186521 | 64,970.446482 | +19,426.740039 |
| vesper | DAI | 13.495808 | 452.498002 | -439.002194 |

Lido’s opening investment includes **9,855,091 already allocated but unclaimed earnUSD shares**. Their later mint is not new capital. The account also sends **13,304,800 USDT back to the stRATEGY parent** during the window. Its investment claim starts around $20.49M while debt starts around $7.18M; the full-account difference is therefore not a matched-principal carry return.

Vesper’s opening and closing vDAI balances reconcile exactly to the saved mint and burn events. The **13.50 DAI** of share-price income is below **452.50 DAI** of accrued funding. Reinvested reward purchases are treated as acquisition flows, so this comparison does not establish the result after external incentives.

### A directly matched 5M USDT investment

On **29 September 2026 at 05:59:35 UTC**, one transaction borrows **5,000,000 USDT** from Aave and transfers it to the earnUSD deposit queue. The newly allocated economic claim is **4,838,244.259 earnUSD shares**, worth exactly 5M USDT at the transaction’s archived oracle mark. The 9.855M old allocated shares minted in the same transaction are excluded.

At T, the new claim has gained **3,651.565 USDT**. The allocated indexed loan interest is **2,250.992 USDT**, leaving **1,400.573 USDT before gas and outer fees**. This is a positive recognised-claim spread over about 3.75 days; it is not a realised cash exit, an organic-income decomposition or a sustainable annual quote. No later account repayment appears before T.

[Borrowing and investment transaction](https://etherscan.io/tx/0x48c24a9436a519bd778454ff6946404afa79f943afc1952e36c08d69949adbc1), [flow-adjusted CSV](../../../data/eth/carry-flow-adjusted-ledgers.csv), [normalised ledger](../../../data/eth/finalization_financial_ledgers.json).
