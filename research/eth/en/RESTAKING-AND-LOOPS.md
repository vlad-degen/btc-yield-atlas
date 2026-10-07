# Restaking in practice and the ETH loop regime

Snapshot T: 2 October 2026 23:59:59 UTC, Ethereum block 26,108,081. Data: [gap_restaking_reality.csv](../../../data/eth/gap_restaking_reality.csv) and [gap_loop_regime_monthly.csv](../../../data/eth/gap_loop_regime_monthly.csv). Raw data is in `raw/eth/gap-2026-10-07/cases/restaking/` and `raw/eth/gap-2026-10-07/cases/loops/`.

## Findings

- **Restaking now pays ETH restakers almost nothing.**
  - EigenLayer paid $137M in year 1 (Oct 2024 to Sep 2025), 1.04% of restaked TVL. Of that, $103M (0.78%) went to ETH and LST restakers.
  - Year 2 paid $36M (0.38%), of which $16.7M (0.18%) went to ETH and LST restakers.
  - Since 30 Jul 2026, ETH and LST restakers receive no programmatic EIGEN. What is left from AVSs is about $4k a month.
- **99.6% of EigenLayer rewards were EIGEN that Eigen itself issued.** Fees paid by AVSs over two years total $0.75M, mostly WETH from EigenDA and RED from RedStone.
- **weETH earned less than stETH over 730 days:** 5.29% against 5.49%, 0.19 pp in total. Restaking added nothing to the weETH exchange rate. Any EIGEN or ETHFI value came as separate claims, and EIGEN fell from about $3.4 to about $0.20.
- **No restaker has been slashed for operator fault.**
  - EigenLayer's 13 non-test slashes (about 32,400 ETH-equivalent of LSTs, Jan to Jun 2026) all came from one operator, `0x5ACCC9…`, and two related AVSs using redistributable operator sets.
  - In each case the slashed LSTs were deposited into third-party vaults, and the vault shares were sent back to delegators as "rewards". This is a custody and redistribution risk, not a penalty record.
  - Symbiotic has two test-size slashes (0.046 wstETH).
- **The ETH loop spread is thin and can turn negative.**
  - Over 24 months, stETH minus the Aave Ethereum WETH borrow rate averaged +0.15 pp in year 1 and +0.10 pp in year 2.
  - The spread was negative in 6 of 24 months. The worst was April 2026 (-1.04 pp), the Kelp exploit month.
  - A 10x wstETH/WETH loop earned 3.81% a year on average, against 2.68% for plain stETH. In its worst month it lost money at a -6.9% annualized rate.
- **ETH loop debt peaked at 3.27M ETH (January 2026) and is 2.27M ETH at T.** This is WETH debt on Aave Core, Aave Prime and Spark. Aave Core fell from 2.98M to 1.54M ETH between January and May 2026. Spark grew from 0.23M to 0.49M ETH.
- **Staking yield is shrinking from both sides.**
  - Lido's gross consensus APR fell from 2.78% to 2.38% as stake grew.
  - Execution rewards (tips and MEV) fell from 0.55% to about 0.09%, from 16% of gross to 4%.
  - stETH holders went from 3.01% to 2.22%.

## B1. EigenLayer rewards by token and year

Source: RewardsCoordinator `0x7750…dda`. There are 364 submissions, and 118 distribution roots were posted (about weekly). USD is valued at the DefiLlama price on each submission's start day.

| | Y1: Oct 2024 to Sep 2025 | Y2: Oct 2025 to Sep 2026 |
|---|---:|---:|
| Programmatic EIGEN, USD | $136.9M (66.9M EIGEN) | $36.0M (74.5M EIGEN) |
| of which to ETH/LST strategies | $102.7M | $16.4M |
| AVS-paid tokens (WETH, RED, AUSD, USDC, ARPA) | $0.50M | $0.25M |
| Average EigenLayer TVL excluding EIGEN (DefiLlama) | $13.23B | $9.47B |
| Yield, all rewards | 1.04% | 0.38% |
| Yield to ETH/LST restakers | 0.78% | 0.18% |
| Redistributed slashed stake paid as vault shares (not yield) | 0 | $74.3M |

The programmatic EIGEN schedule went through four phases:

| Period | EIGEN per week | ETH/LST share |
|---|---:|---:|
| Oct 2024 to 2 Oct 2025 | 1,287,420 | 75% |
| 9 Oct 2025 to 12 Mar 2026 | 2,356,970 | 43% |
| 19 Mar to 23 Jul 2026 (via EigenDA) | 841,438 | 60% |
| From 30 Jul 2026 | 336,575 | 0% |

## B2. Slashing to date

| Date | Venue | Operator / AVS | Assets | Nature |
|---|---|---|---|---|
| 25 to 26 Sep 2025 | EigenLayer | `0x01d120…` / `0x26ddbf…` | 0.0002 WETH | Test |
| 15 Aug 2025 | Symbiotic | wstETH vault `0x77d2d43e…` | 0.046 wstETH | Test |
| 5 Jan to 13 Feb 2026 | EigenLayer | `0x5ACCC9…`, `0x4Cd208…` / Aleph AVS `0x90c68b…` | 1,859 rETH; 517 stETH; 147 rETH (about 2,524 ETH) | Redistributable slash of about 100% of allocation, paid out as vault shares |
| 29 Mar to 14 Jun 2026 | EigenLayer | `0x5ACCC9…` / AVS `0x12b75d…` ("eigenyields") | 14,421 osETH; 12,886 stETH; 1,011 swETH; 569 cbETH; 402 wBETH; 198 ankrETH; 195 ETHx; 113 mETH; 72 sfrxETH | Same pattern, 10 events, about $66M |

- **Delegator reports:** one secondary source says delegators reported their stETH was moved into the operator's vaults. We found no primary EigenLayer statement on this.
- **What a restaker should check:** the useful question is not "has anyone been slashed?" It is whether their operator opted into redistributable operator sets.

## B3. Symbiotic rewards

- **Paid onchain:** DefaultStakerRewards contracts paid about $2.04M from April 2025 to T.
  - HYPER: $1.39M.
  - USDC: $0.64M.
  - These came from about 30 staker-rewards contracts. Recent months pay $0.1M to $0.2M.
- **Not counted:** most of the incentive was off-chain Symbiotic points, and Merkle-based Rewards V2 claims are not in this count.
- **Against TVL:** set against restaked TVL that was $2.1B in January 2025 and $0.48B now, the onchain rewards are negligible.

## B4. weETH vs stETH: what the 0.19 pp gap means

| | 730 days | First year | Last year | Annualized |
|---|---:|---:|---:|---:|
| stETH | 5.4875% | 2.9362% | 2.4785% | 2.7071% |
| weETH | 5.2947% | 2.7436% | 2.4830% | 2.6132% |

- **Where restaking income went:** it did not reach the weETH exchange rate. Year 1 was the period of large EIGEN payouts, yet weETH trailed stETH by 0.19 pp that year.
- **Underlying staking is the same:** weETH's base staking return is effectively stETH-like.
- **Separate claims were the only upside:**
  - EIGEN and ETHFI drops were claimed separately.
  - At year-1 prices they were worth at most about 0.78% a year on all ETH restaked.
  - EIGEN has since lost about 95% of its value.
- **Year 2:** the rates are equal, at 2.48% and 2.48%.

## B5. What issuers take from rewards

| Issuer | Token | Fee on rewards | Base | Net APR, 2 Oct 2025 to 2 Oct 2026 |
|---|---|---|---|---:|
| Lido | stETH | 10% (modules 3.84%, treasury 6.15%, onchain) | Staking CL+EL | 2.49% |
| ether.fi | eETH/weETH | 10% staking; about 10% on EIGEN | Staking plus restaking rewards | 2.50% |
| Rocket Pool | rETH | 5% base node commission plus up to 9% for RPL-staking nodes (Saturn One, Feb 2026) | Staking | 2.26% |
| Binance | wBETH | 10% (DefiLlama) or 5% (Nansen); unresolved | Staking | 2.55% |
| Coinbase | cbETH | 10% per DefiLlama. The 25% to 35% figure is Coinbase retail staking, not cbETH. | Staking | 2.60% |
| Kelp | rsETH | 5% (onchain, cap 15%) | LST yield plus restaking | 2.48% |
| Renzo | ezETH | 15% (onchain) | Staking plus restaking | 2.44% |
| Puffer | pufETH | 5% (4% protocol, 1% guardians) | Staking and restaking | 2.46% |
| Swell | swETH / rswETH | 10% (5% operators, 5% treasury) | Staking | 2.50% / 2.64% |
| Mantle | mETH | 10% (onchain) | Staking | 2.16% |
| Frax | sfrxETH | 10% | Staking | 3.09% |
| StakeWise | osETH | about 5% osToken fee plus vault operator fee | Staking | 2.30% |
| Stader | ETHx | 10% | Staking | 2.57% |
| Origin | OETH | 20% performance fee (onchain) | All vault yield | n/a |

- **Fees explain only part of the spread.** Net APRs sit within 2.2% to 2.6% (sfrxETH is the outlier at 3.09%). Validator performance and buffers move returns as much as fees do.

## C. The loop regime, monthly

Method:
- Month-end archive reads at the study's 24 verified blocks via the Tenderly public gateway.
- Borrow rate is the month average from growth of Aave's variable borrow index. Utilization is a month-end point.
- stETH APR is the growth of `getPooledEthByShares` over the month.
- Lido's gross consensus (CL) and execution-layer (EL) APRs come from 732 onchain oracle report events (`ETHDistributed`, `TokenRebased`):
  - CL = postCL + withdrawals − preCL.
  - EL = execution-layer rewards withdrawn.
  - Both are divided by pre-report total ether.
  - Gross × 0.9 reproduces the stETH holder APR within about 0.02 pp.
- Spread = stETH APR minus the Aave Ethereum WETH borrow rate.
- Debt is WETH variable debt on Aave v3 Core, Aave Prime and Spark.

| Month | Aave WETH borrow (month avg) | Utilization (month end) | stETH holder APR | Lido gross CL | Lido gross EL | Spread | WETH debt Aave+Prime+Spark (k ETH) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024-10 | 2.87% | 89.6% | 3.01% | 2.78% | 0.55% | +0.14 pp | 1,640 |
| 2024-11 | 2.63% | 89.1% | 3.02% | 2.78% | 0.57% | +0.40 pp | 1,850 |
| 2024-12 | 2.96% | 85.4% | 2.92% | 2.78% | 0.45% | -0.04 pp | 1,940 |
| 2025-01 | 2.56% | 89.4% | 2.98% | 2.80% | 0.49% | +0.42 pp | 2,083 |
| 2025-02 | 2.64% | 86.0% | 3.27% | 2.79% | 0.82% | +0.63 pp | 2,187 |
| 2025-03 | 2.78% | 89.1% | 2.95% | 2.79% | 0.47% | +0.17 pp | 2,481 |
| 2025-04 | 2.85% | 86.1% | 3.02% | 2.78% | 0.55% | +0.16 pp | 2,592 |
| 2025-05 | 2.54% | 87.2% | 2.85% | 2.77% | 0.36% | +0.30 pp | 2,798 |
| 2025-06 | 2.58% | 83.5% | 2.75% | 2.75% | 0.30% | +0.17 pp | 2,664 |
| 2025-07 | 3.44% | 93.8% | 2.72% | 2.72% | 0.27% | -0.73 pp | 2,606 |
| 2025-08 | 2.74% | 90.0% | 2.70% | 2.72% | 0.23% | -0.04 pp | 2,528 |
| 2025-09 | 2.43% | 79.5% | 2.64% | 2.71% | 0.16% | +0.21 pp | 2,451 |
| 2025-10 | 2.42% | 87.1% | 2.75% | 2.71% | 0.34% | +0.33 pp | 2,458 |
| 2025-11 | 2.20% | 71.1% | 2.66% | 2.70% | 0.24% | +0.46 pp | 2,425 |
| 2025-12 | 1.95% | 72.7% | 2.56% | 2.71% | 0.12% | +0.61 pp | 2,631 |
| 2026-01 | 2.05% | 87.0% | 2.45% | 2.61% | 0.10% | +0.40 pp | 3,268 |
| 2026-02 | 2.89% | 92.8% | 2.47% | 2.44% | 0.29% | -0.42 pp | 3,071 |
| 2026-03 | 2.30% | 87.5% | 2.51% | 2.53% | 0.22% | +0.21 pp | 2,859 |
| 2026-04 | 3.53% | 99.2% | 2.49% | 2.53% | 0.20% | -1.04 pp | 2,438 |
| 2026-05 | 2.51% | 79.5% | 2.46% | 2.53% | 0.14% | -0.05 pp | 1,912 |
| 2026-06 | 2.11% | 80.3% | 2.42% | 2.50% | 0.18% | +0.31 pp | 2,062 |
| 2026-07 | 2.09% | 82.0% | 2.22% | 2.37% | 0.08% | +0.13 pp | 2,153 |
| 2026-08 | 2.13% | 83.3% | 2.21% | 2.36% | 0.09% | +0.08 pp | 2,214 |
| 2026-09 | 2.04% | 83.7% | 2.25% | 2.39% | 0.10% | +0.20 pp | 2,255 |
| T | 2.07% | 84.5% | 2.22% | 2.38% | 0.09% | +0.15 pp | 2,269 |

T is the partial month to 2 October.

**Loop return at fixed leverage.** Return on equity = stETH + (L − 1) × spread, using month-average rates and before rebalancing and gas.

| Leverage | Y1 average | Y2 average | 24-month average | Worst month (annualized) |
|---|---:|---:|---:|---:|
| 1x (plain stETH) | 2.90% | 2.45% | 2.68% | 2.21% |
| 5x | 3.50% | 2.86% | 3.18% | -1.66% |
| 10x | 4.26% | 3.37% | 3.81% | -6.86% |

**Reading the regime:**
- **The spread is close to zero by design.** Aave's WETH rate curve keeps borrow cost just under staking yield while utilization stays at 80% to 90%. Loopers collect what remains, about 0.1 to 0.15 pp per turn of leverage.
- **Shocks are where the spread breaks.** The negative months match utilization spikes:
  - July 2025: 93.8%.
  - February 2026: 92.8%.
  - April 2026: 99.2% after the Kelp exploit.
  - In those months a 10x loop paid out more than it earned.
- **Falling execution rewards cut the cushion.** EL rewards were 0.55% in October 2024 and are 0.09% now. Combined with the lower consensus APR, stETH has lost 0.8 pp in two years, while the WETH borrow rate fell by a similar amount (2.87% to 2.04%). The spread stayed thin rather than closing.
- **Debt moved to Spark after April.** Aave Core WETH debt fell 1.44M ETH from January to May 2026, as Lido Earn and other loops shrank and Aave cut WETH LTVs. Spark WETH debt doubled to 0.49M ETH.

**Limits:**
- **Debt is a proxy.** Total WETH debt stands in for loop size. Not every WETH borrower is an LST looper, and the e-mode share was not measured.
- **The weETH loop pays slightly less** than the wstETH loop shown here, because weETH accrues below stETH.
- **Source of the CL/EL split.** It comes from Lido's oracle data. Other issuers' splits will differ with their MEV policy.
