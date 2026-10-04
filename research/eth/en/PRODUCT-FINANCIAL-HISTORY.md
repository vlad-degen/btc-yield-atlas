# Measured ETH products: capital, funded share history and exit constraints

The strategy atlas now has a financial layer for five large onchain cases and a separately qualified cmETH principal claim. Every current-state call uses Ethereum block **26,108,081**, the frozen research snapshot for **2 October 2026 at 23:59:59 UTC**. Thirteen sampled historical blocks supply capital and funded share-price endpoints. The stETH benchmark uses those same blocks, with no interpolation.

These are contract book values and oracle claims. They are more useful than a forward APY quote, but they are not independent backing audits or proof that every share can immediately be sold for its mark. Read-only withdrawal simulations change no chain state and are not paid cash receipts. The [structured data](../../../data/eth/strategy_universe_deep.json) and [capture manifest](../../../data/eth/strategy_universe_deep_manifest.json) preserve the distinction.

## Capital and fees at the frozen block

USD translations use the original snapshot ETH quote of **$2,667.9504418816**, whose supplied timestamp is one second after the target. No later discovery quote replaces the frozen product state.

| Product | ETH-equivalent book/principal mark | USD mark | Measured fee or exit state |
| --- | ---: | ---: | --- |
| osETH controller | 157,019.0113 ETH | $418.919m | Controller reward fee 5%; queue/checkpoint state measured separately |
| mETH | 235,473.9161 ETH | $628.233m | Entry adjustment 4 bps; lending-buffer interest fee 10% |
| Yearn WETH-1 | 7,296.2038 WETH | $19.466m | Accountant management fee 0%; performance fee 10%; 3.6 WETH idle |
| autoETH | 7,755.9321 WETH | $20.692m | Periodic and streaming rates both zero; about 0.7475 WETH idle |
| YieldBasis WETH LT pool | 10,425.9986 WETH | $27.816m | Minimum admin-fee parameter 10%; actual fee treatment depends on staking and loss state |
| cmETH, Ethereum token | 16,186.3205 ETH nominal principal claim | $43.184m | Nested mETH claim, with separate restaking rewards and fees; portfolio backing not reconstructed |

The rows are **not additive market capital**. cmETH is nested in mETH. osETH is a claim against staking vaults. Yearn, autoETH and YieldBasis can also contain claims on assets already counted elsewhere. The same restriction applies to the staked and unstaked classes within the YieldBasis pool.

## Comparable funded share histories

The first four products have a common **732-day** window from 30 September 2024 to 2 October 2026. The table reports cumulative ETH-equivalent share-value changes, not annual APY. “Excess” means the arithmetic difference in percentage points from stETH over the same window.

| Product | Book share-value change | stETH on identical blocks | Book excess, percentage points |
| --- | ---: | ---: | ---: |
| osETH | +5.0958% | +5.5051% | -0.4094 |
| mETH | +5.2512% | +5.5051% | -0.2539 |
| Yearn WETH-1 | +4.3886% | +5.5051% | -1.1165 |
| autoETH | +4.1824% | +5.5051% | -1.3228 |

All four book marks grow less than the matched stETH benchmark in this window. That finding does **not** establish complete investor or organic underperformance. Separately distributed rewards, entry/exit costs and executable market discounts are excluded. The comparison nevertheless tests whether extra strategy complexity appears in the onchain ETH share mark rather than merely in a quoted APY.

The stETH series measures `getPooledEthByShares(1e18)`, so the benchmark follows a fixed share of Lido's pooled ETH rather than treating the rebasing stETH token count as fixed. Lido's applied reward and fee accounting is therefore already reflected in the observed growth. [Lido share accounting](https://docs.lido.fi/contracts/lido/), [exact-block benchmark capture](../../../raw/eth/strategy-universe-deep-2026-10-04/steth_exact_timestamp_benchmark.json).

AutoETH's sampled mark falls **3.0379%** between 30 September and 31 December 2025, before recovering. This is an observed endpoint decline, not a continuous maximum drawdown or an attributed cause. Separate rewarder payouts are not included. [Historical calls](../../../raw/eth/strategy-universe-deep-2026-10-04/historical_endpoints_Blast.json), [bounded rate-limit repair](../../../raw/eth/strategy-universe-deep-2026-10-04/holder_exits_and_bounded_history_repair_T.json).

YieldBasis has a shorter usable window of **94 days**, from 30 June 2026 to the snapshot. Its fair ETH price per unstaked LT unit falls **0.6926%** while the matched stETH share mark rises **0.5741%**. This per-token price series does not include the changing LT balance of a staked gauge receipt or YB rewards. It must not be presented as the complete return of all YieldBasis depositors.

## Yearn WETH contains a measured ETH-debt loop

The original official registry request was restricted to strategies in the withdrawal queue and omitted a fourth strategy. Querying the official registry with all strategies identified the **wstETH/WETH Spark Looper**, then archive calls verified its state at the snapshot.

| Strategy | Parent book allocation in WETH | In default withdrawal queue |
| --- | ---: | --- |
| stETH Accumulator | 2,773.147975 | Yes |
| Spark WETH Lender | 3,237.362360 | Yes |
| Yearn OG WETH | 247.307012 | Yes |
| wstETH/WETH Spark Looper | 1,034.786440 | No |
| Idle WETH | 3.600000 | Direct vault liquidity |

The four strategy debts plus idle WETH reconcile the parent `totalAssets` within rounding. The loop represents approximately **14.18%** of the parent book. Its actual Spark account has **6,633.68809 wstETH** collateral and **7,225.78096 WETH** debt. The strategy reports **7.97585 times** leverage, an **87.46217%** LTV and a **1.06332** health factor. Gross collateral is not extra capital to add to Yearn NAV.

This is a concrete E3 staking loop inside a WETH allocator. Calling the entire product pure lending would hide its leverage and the difference between the book strategy set and the default exit queue. [Official all-strategy registry](https://ydaemon.yearn.fi/1/vaults/0xc56413869c6cdf96496f2b1ef801fedbdfa7ddb0?strategiesDetails=withDetails&strategiesCondition=all), [frozen allocation calls](../../../raw/eth/strategy-universe-deep-2026-10-04/demand_and_fee_allocation_T.json), [Spark loan state](../../../raw/eth/strategy-universe-deep-2026-10-04/yearn_spark_loop_position_T.json).

## The mETH lending buffer has measured income and a separate cash boundary

The buffer controls **20,000.5272 ETH**, about **8.49%** of the mETH controlled book. Its available-balance getter reports **20,000 ETH**, while the buffer contract itself holds **zero native ETH**. The assets are allocated through a position manager. An available strategy getter is therefore different from a wallet cash balance.

The cumulative buffer counters through the snapshot reconcile:

| Counter | ETH |
| --- | ---: |
| Gross interest claimed | 492.609869 |
| Fees collected | 49.260987 |
| Net interest topped up | 443.348882 |

These are cumulative contract accounting counters, not an annualized return on today's allocation and not a newly collected receipt-by-receipt payment census. Their arithmetic supports a real borrower-income mechanism and a 10% buffer fee without pretending that the capital denominator was constant.

The unstake manager holds **1,213.140858 ETH** of native cash. Cumulative allocated claims minus cumulative claimed ETH match that balance. Its funding deficit getter reports **33.108320 ETH**, and the configured finalization threshold is **3,600 blocks**. These numbers describe queue funding and the current threshold; they do not promise a completion time for a new large request. [Buffer, units and queue calls](../../../raw/eth/strategy-universe-deep-2026-10-04/units_buffer_and_yb_history_T.json), [native cash reconciliation](../../../raw/eth/strategy-universe-deep-2026-10-04/effective_yb_supply_and_meth_cash_T.json), [published mETH mechanics](https://docs.mantle.xyz/meth/introduction/overview.md).

## Withdrawal size changes the result

The caller in each demand test has sufficient shares at the frozen block. The denominator is whole-vault book NAV, not the caller's wallet balance. Each request uses the ordinary `withdraw` path and a non-persistent archive `eth_call`.

| Demand as a share of whole book NAV | Yearn WETH-1 | autoETH |
| --- | --- | --- |
| 1% | Simulation succeeds | Simulation succeeds |
| 10% | Simulation succeeds | Simulation succeeds |
| 30% | Simulation succeeds | Simulation reverts |

AutoETH's 30% revert decodes to **PositivePriceRecoupNotCovered(uint256)**. This is a pricing/recoup constraint in the withdrawal implementation, not proof of an asset deficit or a permanently insolvent pool. The largest sampled holder's `maxWithdraw` also reverts with **TooFewAssets(uint256,uint256)**, while `maxRedeem` returns its share balance and smaller withdrawal calls succeed. [Demand and fee calls](../../../raw/eth/strategy-universe-deep-2026-10-04/demand_and_fee_allocation_T.json), [holder getter and small-exit calls](../../../raw/eth/strategy-universe-deep-2026-10-04/holder_exits_and_bounded_history_repair_T.json).

No simulated return is described as a historical cash payment. The sample also does not establish simultaneous liquidity for all holders, since their getter maxima draw on the same underlying assets.

## YieldBasis needs the correct claim denominator

The fair-price getter uses the effective updated LT supply. It can differ from raw ERC-20 supply under the fee calculation; at this snapshot, both are **10,364.971983 LT**. The effective staked balance is **5,840.630258 LT**. At the common oracle mark, staked and unstaked claim classes correspond to **5,875.018591 WETH** and **4,550.980043 WETH**, respectively, and partition the **10,425.998634 WETH** pool book.

The AMM's measured debt is approximately **27.815m crvUSD**. The separately recorded **64.136m crvUSD** allocation is not the outstanding debt. At a nominal one-dollar crvUSD assumption, debt is approximately equal to net pool equity, consistent with a roughly twofold gross exposure. Withdrawal previews for 1%, 10% and 30% of raw LT supply are retained as quotes, not successful withdrawals. [Effective supply and previews](../../../raw/eth/strategy-universe-deep-2026-10-04/effective_yb_supply_and_meth_cash_T.json), [actual AMM debt](../../../raw/eth/strategy-universe-deep-2026-10-04/yb_actual_loan_state_T.json).

## Reproduction and remaining scope

Run `python3 tools/eth/strategy_universe_deep_build.py` and `python3 tools/eth/strategy_universe_deep_verify.py`. The verifier checks hashes, fixed-block boundaries, benchmark alignment, fee units, allocation and cashflow arithmetic, demand callers and the distinction between simulations and paid receipts.

The measured sample does not complete the whole ETH market. Large GMX products, other chains, options auctions, external reward histories, full restaking backing and signer/delay maps still require separate work. These gaps are attached to the relevant family and product records rather than hidden behind a global completeness claim.
