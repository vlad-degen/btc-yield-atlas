# ETH yield research: team briefing

Financial snapshot: **2 October 2026**. This briefing and the main page use the same generated analytical contract. Filters affect Market charts, not these answers.

## Answer

**18,349,193 ETH earns a yield** in 170 products counted once ($49.0B on 2 October 2026): 81% staking, 13% restaking, 3.8% farming and pools. About 14.4M ETH more is staked off-chain with exchanges, institutional providers and BitMine.

**Carry is 1.7%**: 305,991 ETH in 14 products that borrow dollars against ETH (in BTC it is 9.9%). They owe $261M; Liquid ETH and Lido Earn hold 85% of the books.

**Carry barely beats staking.** Liquid ETH beat stETH by 0.66 pp a year over two years, but its dollar leg loses about $6.8M a year at 2 October rates ($9.0M of interest on one 13.93% Aave USDC loan). YieldBasis is the only top-five product whose fees cover its loan.

## Market and two years of history

| Category | ETH, 2 Oct 2026 | Share | Oct 2024 | Switch |
| --- | --- | --- | --- | --- |
| Staking | 14,783,197 | 80.6% | 12,231,280 | on |
| Restaking | 2,430,237 | 13.2% | 4,173,272 | on |
| Leveraged staking | 97,209 | 0.5% | 121,804 | on |
| Carry | 305,991 | 1.7% | 147,309 | on |
| Fixed yield | 9,315 | 0.1% | 307,484 | on |
| Basis | 372 | 0.0% | 25,423 | on |
| Options | 3,182 | 0.0% | 5,449 | on |
| Credit | 24,279 | 0.1% | 2,496 | on |
| Farming and pools | 695,413 | 3.8% | 1,918,324 | on |
| Money markets | 787,912 | off | 809,351 | off |
| CDP collateral | 657,327 | off | 1,277,081 | off |

Each product is counted once: a staking token held by another product leaves its issuer's row. Money markets count only idle plain WETH and are off by default, because lent ETH is staked again by its borrowers. Binance's wBETH grew by 2.19M ETH, the largest change on the map; restaking fell from 4.67M ETH (July 2025) and farming and pools from 2.09M (February 2025) as points programmes ended. [Method and every netting step](../../../data/eth/netmap/netting_ledger.csv).

## Top five carry products

Ranked by dollars borrowed against ETH. Concrete Delta (307,363 ETH) is left out of the map and the ranking: its whole supply was minted to one address after a Bitfinex-linked wallet moved its own Aave position into the vault's Safe; there are no outside depositors ([evidence](CONCRETE-DELTA.md)).

| Product | Dollars borrowed | Loan rate | Book, ETH |
| --- | --- | --- | --- |
| ether.fi Liquid ETH | $181.1M | 7.79% | 177,171 |
| YieldBasis WETH | $27.8M | 10.00% | 10,426 |
| Lido Earn ETH | $25.6M | 4.33% | 83,309 |
| Avant avETH / savETH | $10.0M | 6.30% | 12,583 |
| Liquity ETH Carry | $6.8M | 2.55% | 6,014 |

[Risk, repayment ladder and reward payers](TOP5-RISK-LIQUIDITY.md).

## What returns can be compared

All eleven detailed products have the same **2 September to 2 October 2026** return window. These are ETH book marks, excluding external payouts and exit costs. YieldBasis uses unstaked LT fair value. Recognised book income is not stripped into organic carry. Whole-product fees already recognised in share value are not deducted twice.

| Product | 30-day ETH book return | Excess vs stETH, pp |
| --- | --- | --- |
| ether.fi Liquid ETH | 0.2610% | +0.0761 |
| YieldBasis WETH | -0.1622% | -0.3471 |
| Lido Earn ETH | 0.2513% | +0.0664 |
| Avant avETH / savETH | 0.3385% | +0.1536 |
| Liquity ETH Carry | 0.4597% | +0.2748 |
| Concrete Delta weETH | 0.1915% | +0.0066 |
| Rocksolid rETH | 0.2192% | +0.0343 |
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

The material discovery screen contains 299 ETH-name pools above $5M. 224 dispositions join an already-covered parent; they do not prove that each pool's strategy has been reconstructed. Fixed-block reconstruction adds Lido Earn, Avant, Makina DETH, Vesper and ZenSats; YO ETH is separately classified as ETH lending / staking after inspecting its deployments. The family map is broad; global unique capital and complete historical sleeve weights remain unresolved. The reconstruction now measures native stake, five additional carry-linked books, four active PT faces and the residual Ribbon option book. Own-credit, fees and exit cash still limit complete organic carry attribution. [Coverage matrix](MARKET-COVERAGE.md).

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

<!-- substantive-parity -->

## Product history behind the snapshot

Liquid’s stablecoin borrowing predates its current Morpho routes: Aave USDC financing is observed in August 2025. Its 18M PYUSD cohort is negative after funding under three explicit withdrawal conventions, before rewards and other costs. Cash Hub ownership now resolves to 7,012 positive account positions. Lido’s current wrapper follows its November 2025 underlying strategy; its April crisis required a 27-day pause and DAO loss absorption. YieldBasis’s present LT history starts after an earlier WETH pool, and gauge investors have different income rights from unstaked holders. Avant’s senior holder analysis traces Gearbox and Morpho custody instead of treating their contracts as single investors.

[Full product development, accounting assumptions and source evidence](PRODUCT-EVOLUTION.md).

<!-- economic-answers -->
## Current financing comparison

| Product | Direct dollar debt at T | Debt-weighted quoted APR | Whole book ETH | Scope |
| --- | --- | --- | --- | --- |
| ether.fi Liquid ETH | $181,084,944 | 7.79% | 177,171 | attributed product account / direct loan |
| YieldBasis WETH | $27,814,856 | 10.00% | 10,426 | attributed product account / direct loan |
| Lido Earn ETH | $25,555,160 | 4.33% | 83,309 | attributed product account / direct loan |
| Avant avETH / savETH | $10,034,777 | 6.30% | 12,583 | attributed product account / direct loan |
| Liquity ETH Carry | $6,752,065 | 2.55% | 6,014 | attributed product account / direct loan |
| NEMO ETH Prime | $5,611,801 | 4.75% | Not reconstructed | attributed product account / direct loan (vault book reconciles with the loan) |
| Rocksolid rETH | $2,727,060 | 4.61% | 9,728 | attributed product account / direct loan (second strategy wallet) |
| Sentora ETH | $1,163,324 | 11.79% | Not reconstructed | attributed product account / direct loan (vault book reconciles with the loan) |
| Makina DETH | $384,701 | 3.21% | 2,499 | attributed product account / direct loan |
| Royco ETH | $90,891 | 30.24% | 116 | attributed product account / direct loan |
| Vesper vaETH | $68,998 | 5.00% | 1,052 | attributed product account / direct loan |
| Reservoir ETH Yield | $36,790 | 13.93% | Not reconstructed | attributed product account / direct loan |
| TAU InfiniFi ETH Carry | $0 | Unavailable | Not reconstructed | attributed product account / direct loan |


The principal five are ordered by attributed direct dollar financing. Monthly quotes and whole-book ETH returns measure different units. Concrete is an unresolved case, not a verified member of the five. [Economic answers and historical debt](ECONOMIC-ANSWERS.md).
