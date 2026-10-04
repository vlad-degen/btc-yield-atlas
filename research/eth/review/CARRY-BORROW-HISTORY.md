# Liquid ETH borrowing-rate history

Financial state remains anchored at T, 2 October 2026, 23:59:59 UTC. The new captures were made on 4 October using the 24 completed-month Ethereum blocks already used in carry_category_candidates.json, from October 2024 through September 2026. No original financial input or canonical chapter data was changed.

## What the chart can show

The dataset has 48 rows, one monthly point for each of two distinct loan-principal rate series. All 24 blocks were checked against their next block to prove the retained block is the last one at or before that month end. APR values are annual fractions, not percentages or investor return.

- E4 series: Liquid ETH main vault borrowing RLUSD against weETH in the observed Morpho market. Values are null when the market has not been created or the main account has no borrowing.
- E3 series: Liquid ETH main vault variable WETH debt on Aave V3 Ethereum. This is an ETH-debt loop funding benchmark. It is not stablecoin carry.

The main weETH/RLUSD market is absent for the first 17 month ends, October 2024 through February 2026. The market exists from March 2026, but the main account has no debt at the March-June month ends. Its first sampled nonzero borrowing and collateral occur in July 2026. The controlled LoanManager is funded in June, so that separately measured June quote is preserved in loan_manager_observed_borrow_apr. It does not backfill the main-account series.

The absence of this specific RLUSD loan does not establish that the product had no other stablecoin loans or carry strategies in earlier months.

## Actual month-end rates

| Month | Main weETH/RLUSD borrow APR | Main RLUSD funding status | Aave WETH borrow APR | Main Aave variable WETH debt |
|---|---:|---|---:|---:|
| 2024-10 | n/a | market_not_created | 2.686677% | 110,355.461730 |
| 2024-11 | n/a | market_not_created | 2.672457% | 211,914.294020 |
| 2024-12 | n/a | market_not_created | 2.560681% | 199,221.022429 |
| 2025-01 | n/a | market_not_created | 2.682763% | 264,498.656019 |
| 2025-02 | n/a | market_not_created | 2.578413% | 313,061.452327 |
| 2025-03 | n/a | market_not_created | 2.673336% | 360,006.143711 |
| 2025-04 | n/a | market_not_created | 2.583449% | 374,860.528896 |
| 2025-05 | n/a | market_not_created | 2.615426% | 505,785.064842 |
| 2025-06 | n/a | market_not_created | 2.503536% | 506,856.492497 |
| 2025-07 | n/a | market_not_created | 2.893367% | 570,541.078236 |
| 2025-08 | n/a | market_not_created | 2.642768% | 490,042.724100 |
| 2025-09 | n/a | market_not_created | 2.248037% | 478,003.093325 |
| 2025-10 | n/a | market_not_created | 2.460414% | 478,985.976184 |
| 2025-11 | n/a | market_not_created | 1.932409% | 480,350.557256 |
| 2025-12 | n/a | market_not_created | 1.976318% | 568,953.434700 |
| 2026-01 | n/a | market_not_created | 2.221037% | 572,734.227634 |
| 2026-02 | n/a | market_not_created | 2.417758% | 490,971.745091 |
| 2026-03 | n/a | main_account_not_borrowing | 2.235376% | 534,498.583138 |
| 2026-04 | n/a | main_account_not_borrowing | 4.605538% | 450,867.589032 |
| 2026-05 | n/a | main_account_not_borrowing | 2.089203% | 263,394.110405 |
| 2026-06 | n/a | main_account_not_borrowing | 2.105369% | 258,960.241873 |
| 2026-07 | 3.598605% | observed_funded_main_account | 2.149067% | 284,802.637193 |
| 2026-08 | 3.760671% | observed_funded_main_account | 2.182505% | 409,399.708805 |
| 2026-09 | 16.677406% | observed_funded_main_account | 2.052137% | 410,087.799738 |

The separate June LoanManager quote is 3.015027% APR. The main account is unfunded in that sample, so its borrow_apr remains null.

## September spike independently verified

The September main-account quote is 16.677405676% APR at block 26,093,737. Stored market borrow assets equal stored market supply assets, so utilization is exactly 100%. The verified AdaptiveCurveIrm places full utilization at roughly four times the learned target rate, with adaptation across the pending interval. That interval is 912 seconds in the captured state.

A second independent archive endpoint, Tenderly, returned byte-for-byte identical market parameters, market balances, main-account position and borrowRateView result to the first Blast endpoint at the same block. The comparison is archived in carry_borrow_history_crosscheck.json. A PublicNode attempt returned HTTP 403; it is retained as an unsuccessful source attempt and is not used as rate evidence.

The much lower 4.210021% APR quote at the 2 October snapshot is another date and utilization state. It must not be copied across the earlier months. September is a point observation, not a claim that the account paid 16.677406% throughout that month.

## Rate conventions and evidence limits

For Morpho, each historical market parameter getter identifies the actual loan token, collateral token and model address. The model MORPHO binding and deployed code are checked against the verified source. The actual historical market state is then passed into borrowRateView at that archived block. APR equals the per-second WAD rate multiplied by 365 days. The model returns an average over its pending accrual interval. This is not the time-weighted monthly borrowing cost or a prospective instantaneous funding offer.

For Aave, the historical WETH reserve getter supplies its stored variable borrow APR in ray units. Its own historical variable-debt token is used to query balanceOf(main vault) at the same block. Every retained Aave rate has nonzero main-account variable WETH debt. The 24 observed APRs range from 1.932409% to 4.605538%. They are loan-principal rates, not the leveraged account return or total product income.

These samples cannot reconstruct historical carry allocation, the amount of debt parked in a destination, reward receipts, hedging, exit costs or attribution of published Liquid ETH returns. A comparison with share returns must label the rates as funding-cost indicators and preserve their different denominators. There is no interpolation across missing RLUSD observations.

## Artifacts and reproducibility

- [carry_borrow_rate_history.json](../../../data/eth/carry_borrow_rate_history.json): final rows, series summaries, block checks and source hashes.
- [carry_borrow_history_rpc.json](../../../data/eth/carry_borrow_history_rpc.json): all primary responses grouped by month.
- [carry_borrow_history_crosscheck.json](../../../data/eth/carry_borrow_history_crosscheck.json): independent September provider comparison.
- [carry_borrow_history_review.json](../../../data/eth/carry_borrow_history_review.json): independent offline verification record.
- [carry_borrow_history.py](../../../tools/eth/carry_borrow_history.py): run without arguments to rebuild offline; --verify checks the rebuilt data. Network calls occur only with --capture or --crosscheck.
- [Separate raw manifest](../../../raw/eth/carry-borrow-history-2026-10-04/requests.jsonl): preserved request payloads, response paths, hashes and capture timestamps.

The independent review passed 447 assertions, including all source hashes, 24 block/next-block checks, primary account funding, model/runtime bindings, APR conversions, debt-token identity and the second-provider September results. A second offline build produced identical bytes.

Dataset SHA-256: `60ab984de707d9ff3bbb0d0f8502a3cc405aed8cbba35a933ee0d9c0cf97ddff`.
