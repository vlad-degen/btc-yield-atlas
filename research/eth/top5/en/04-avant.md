# Avant avETH / savETH: deep dive (yield history, risk, depositors, growth, economics)

*Data: [`data/eth/top5/avant/`](../../../../data/eth/top5/avant/) (`weekly.csv` is new in this pass; `keys.csv`, `fees.csv`, `events.csv`, `holder_buckets.csv`, `holders_monthly.csv` from the 7 Oct pull). Scripts: [`tools/eth/top5/avant/`](../../../../tools/eth/top5/avant/). Russian version: [../04-avant.md](../04-avant.md).*

**Snapshot T:** 2 Oct 2026 23:59:59 UTC, Ethereum block 26,108,081. Benchmark: stETH (wstETH `stEthPerToken`) over the same blocks. Contracts: avETH `0x9469470c…f7ee` (issuer token, earns nothing unstaked), savETH `0xda06ee2d…e341` (senior ERC-4626 share of avETH), AvantMintingV2 `0x09becf6e…32d7`, strategy wallet `0x6cc60a0b…c4bd` (EOA). Issuer: Avant Protocol Foundation (BVI).

---

## Key findings

1. **savETH beat stETH every single week for a year.** 54 weeks (19 Sep 2025 to T): never negative, never below stETH; mean 5.54% a year, standard deviation 1.96 pp. 90 days 4.74% (stETH 2.25%), 365 days 5.47% (stETH 2.48%).
2. **That smoothness is set by a push, not marked to the strategy.** The yield reaches savETH only when the rewarder EOA calls `transferInRewards` (daily, vested). 248.6 avETH has been pushed since Sep 2025; no fee or rate exists on-chain to check it against.
3. **Rewards are not the story; own credit is.** Priced rewards are 7% of the 90-day lead over stETH (CRV $37k a year run-rate). The dollar leg earns the rate of savUSD, Avant's own dollar product, which holds 98% of the issuer's disclosed net NAV ($32.53M of $33.18M, 29 Sep).
4. **The dollar spread is at its thinnest at T.** Borrow 6.30% against savUSD 7.54% (+1.24 pp) on $10.0M. At the August month-end it was 3.79% against 8.57% (+4.8 pp). Between the two month-ends the debt mix moved from Aave ($5.58M) to Spark ($7.82M) and the blended quote rose to 6.34%.
5. **Only half the book is visible on Ethereum.** The strategy wallet holds about 6.1k ETH-equivalent of collateral against 12,583 avETH. The issuer reports $72.65M of assets and $39.47M of liabilities (2.19× gross); Ethereum shows $10.0M of ETH-backed dollar debt on Aave and Spark plus $3.7M on Morpho.
6. **Repayment takes a week.** 2.4% of the debt is repayable in the same block; 97.6% needs savUSD on Avalanche: 24h cooldown, a bridge, then avUSD redemption of up to 7 days. A 20% ETH fall needs about $2.0M of repayment to restore HF 1.37 (est.).
7. **Half of savETH is itself levered.** A Gearbox credit account (32.1%) and two Morpho savETH/WETH markets (17.6%) hold 49.7% of savETH as loan collateral (Morpho markets lend WETH). One EOA owns 37.8% of the product through all three routes.
8. **One EOA controls everything, with no delay.** `0xd4d23209` owns avETH (can add any minter), administers savETH and the minting contract, and owns both CCIP bridge pools. It cut the 24h exit cooldown to 60 seconds 30 times in Apr to Sep 2026 (219 hours in total), with no notice.
9. **First-loss is thin.** Reserve fund 38.01 savETH (about 40.3 ETH, 0.36% of savETH) at T. The junior avETHx holds no avETH or savETH on Ethereum.
10. **Growth did not stop when points did.** AvantPoints ran 13 Nov 2025 to 15 May 2026 (savETH 1,381 to 5,491 avETH). After they ended, savETH doubled again to 11,081. Cumulative net inflow 10,857 avETH against 224 avETH of yield.
11. **A large unstaked holder earns nothing.** EOA `0xdd71cdd6` holds 1,411 avETH (11.2%) outside savETH; per the docs, the yield on unstaked avETH is kept by the protocol.

---

## A. Scope and snapshot

| Item | Value at T | Source |
|---|---|---|
| avETH supply (book, face) | 12,582.7 avETH ($33.6M at $2,667) | `totalSupply` |
| In savETH | 11,082.7 avETH (88.08%); savETH supply 10,462.0, 1.059208 avETH per share | `totalAssets`, `convertToAssets` |
| ETH-backed dollar debt (Aave, Spark) | $10.03M at 6.30%: 2.21M USDC (Aave), 7.32M USDS and 0.50M PYUSD (Spark) | `getUserAccountData`, reserve reads |
| Other debt of the same wallet | Morpho savUSD/USDC $3.05M, weETH/RLUSD $0.65M | [`gap_borrowers.csv`](../../../../data/eth/gap_borrowers.csv) |
| Health factor | Aave 1.382, Spark 1.370; −27% ETH to liquidation | |
| Holders | savETH 83, avETH 37, look-through 109 owners | Transfer replay |
| Return | 90d 4.74% (4.55% without priced rewards); 365d 5.47% (5.42%) | `rewards_split.csv` |

## B. Structure and legs

| Leg | Collateral | Debt | Destination | Rate at T |
|---|---|---|---|---|
| A: Aave Core | WETH 809.4, weETH 536.4 | 2.21M USDC | savUSD (Avalanche) | 6.30% blended |
| B: Spark | WETH 2,664.7, wstETH 1,650.7 | 7.32M USDS, 0.50M PYUSD | savUSD (Avalanche) | |
| C: Morpho | weETH 364.0 | 0.65M RLUSD | not traced | |
| D: Morpho (stable loop) | 4.0M savUSD | 3.05M USDC | not ETH-backed | |
| Other chains | Monad, Sei, Berachain per issuer | not read | | |

Income to savETH: staking on the posted ETH, plus savUSD yield minus borrow cost, minus off-chain fees and the junior carve-out, pushed daily by the rewarder EOA.

The same wallet also uses the Aave v4 Core Hub for stablecoins (USDG, frxUSD) per [BORROWER-IDENTITIES](../../en/BORROWER-IDENTITIES.md); not part of the ETH-backed legs.

## C. Positions over time (month-end, Aave and Spark ETH-backed legs)

| Month | Collateral $M | Debt $M | LTV | HF | Borrow | savUSD | Spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sep 2025 | 3.4 | 2.04 | 60.7% | **1.32** | 2.39% | | |
| Oct | 8.2 | 4.33 | 52.7% | 1.54 | 4.43% | | |
| Nov | 5.6 | 3.10 | 55.3% | 1.46 | 5.00% | | |
| Dec | 7.8 | 2.89 | 36.9% | 2.17 | 4.65% | | |
| Jan 2026 | 6.3 | 2.36 | 37.4% | 2.16 | 4.41% | 12.50% | +8.1 pp |
| Feb | 7.4 | 4.30 | 58.3% | 1.40 | 3.38% | 7.95% | +4.6 pp |
| Mar | 7.4 | 4.38 | 59.1% | 1.37 | 3.09% | 7.50% | +4.4 pp |
| Apr to May | | < 0.1 | | | | | WETH loop instead |
| Jun | 6.2 | 3.71 | 60.0% | 1.37 | 5.72% | 7.82% | +2.1 pp |
| Jul | 14.3 | 8.67 | 60.5% | 1.35 | 3.21% | 8.09% | +4.9 pp |
| Aug | 19.4 | 11.28 | 58.2% | 1.42 | 3.79% | 8.57% | +4.8 pp |
| Sep | 16.2 | 10.03 | 62.1% | 1.36 | 6.34% | 7.70% | +1.4 pp |
| T | 16.3 | 10.03 | 61.5% | 1.37 | 6.30% | 7.54% (30d) | **+1.2 pp** |

Borrow rates are point quotes at each block, not monthly averages. Debt moved from Aave to Spark between July and September (Aave $8.67M and Spark 0 in July; Aave $5.58M and Spark $5.70M in August; Aave $2.21M and Spark $7.82M in September).

## D. Governance and security

| Role | Holder | Can do | Delay |
|---|---|---|---|
| avETH owner | EOA `0xd4d23209` | add or remove any minter (unlimited avETH) | none |
| Minting admin | same EOA | roles, custodians, assets, per-block caps (5,000 avETH since 15 Oct 2025), disable mint and redeem | none |
| Collateral manager (since 2 Jun 2026) | same EOA | move minting collateral to custody | none |
| savETH admin | same EOA | cooldown 0 to 90 days, blacklist, move a restricted balance, rescue tokens | none |
| Minter / redeemer | EOA `0xaf6fd55a` | execute mint and redeem orders; users cannot redeem on-chain | none |
| Rewarder | EOA `0xdb87e930` | push daily yield into savETH | none |
| CCIP pools (avETH, savETH) | same owner EOA | remote chains (Avalanche, Linea, Arbitrum), rate limits | none |
| Strategy wallet, reserve fund | EOAs `0x6cc60a0b`, `0x4a6f696a` | all Ethereum legs; first-loss buffer | n/a |

Findings:
- No contract is upgradeable, but the owner can mint without limit by adding a minter. Docs say the keys are MPC; that cannot be checked.
- Cooldown history: 7 days at launch, 1 day from 5 Sep 2025, then 64 `CooldownDurationUpdated` events. 30 windows at 60 seconds between 20 Apr and 27 Sep 2026; the longest ran 30 Jul to 6 Aug (166 h).
- The strategy wallet's gas comes from `0xd0f02713`, the minting custodian; the borrower study labels the wallet "individual", which is wrong for this product.

---

## E. Yield history

**Method.** savETH `convertToAssets` (avETH per share; avETH valued at 1 ETH). Splits from [REWARDS-SPLIT](../../en/REWARDS-SPLIT.md): a = staking on measured collateral; c = savUSD growth on a claim set equal to the debt, minus borrow index growth; d = CRV and Merkl receipts on the wallet; f = residual (other chains, unmeasured books). Fees are not separable. Weekly reads every 7 days back from T (`weekly.csv`).

### E.1 Monthly

| Month | savETH APY | Without priced rewards | stETH APY | Excess (pp, not annualized) | avETH pushed to savETH |
|---|---:|---:|---:|---:|---:|
| Oct 2025 (from 2 Oct) | 7.38% | 7.37% | 2.80% | +0.35 | 6.86 |
| Nov | 8.86% | 8.86% | 2.69% | +0.48 | 10.23 |
| Dec | 5.47% | 5.47% | 2.59% | +0.24 | 7.45 |
| Jan 2026 | 4.54% | 4.53% | 2.48% | +0.17 | 7.95 |
| Feb | 5.95% | 5.95% | 2.50% | +0.26 | 10.90 |
| Mar | 4.04% | 4.03% | 2.54% | +0.12 | 12.96 |
| Apr | 4.73% | 4.71% | 2.52% | +0.18 | 20.52 |
| May | 5.63% | 5.63% | 2.48% | +0.26 | 23.87 |
| Jun | 5.17% | 5.09% | 2.45% | +0.22 | 27.59 |
| Jul | 5.27% | 5.03% | 2.24% | +0.25 | 35.60 |
| Aug | 4.77% | 4.60% | 2.23% | +0.21 | 43.04 |
| Sep | 4.26% | 4.13% | 2.27% | +0.16 | 37.19 |
| **90d to T** | **4.74%** | **4.55%** | 2.25% | +0.60 | |
| **365d to T** | **5.47%** | **5.42%** | 2.48% | +2.99 | |
| **19 Sep 2025 to T** | 5.70% | | 2.49% | | 248.62 in total (from Sep 2025) |

### E.2 Weekly, last quarter (`weekly.csv`)

| Week to | savETH week | APY | stETH APY | avETH supply | In savETH |
|---|---:|---:|---:|---:|---:|
| 3 Jul | +0.093% | 4.83% | 2.29% | 9,173 | 7,954 |
| 10 Jul | +0.105% | 5.45% | 2.23% | 9,132 | 7,962 |
| 17 Jul | +0.102% | 5.31% | 2.20% | 9,183 | 8,007 |
| 24 Jul | +0.112% | 5.82% | 2.19% | 9,703 | 8,383 |
| 31 Jul | +0.078% | 4.06% | 2.20% | 10,330 | 8,976 |
| 7 Aug | +0.085% | 4.41% | 2.19% | 11,908 | 10,448 |
| 14 Aug | +0.086% | 4.50% | 2.18% | 12,687 | 11,205 |
| 21 Aug | +0.095% | 4.96% | 2.21% | 12,676 | 11,188 |
| 28 Aug | +0.103% | 5.35% | 2.25% | 12,573 | 11,073 |
| 4 Sep | +0.080% | 4.16% | 2.22% | 12,584 | 10,932 |
| 11 Sep | +0.084% | 4.39% | 2.25% | 12,458 | 10,961 |
| 18 Sep | +0.079% | 4.14% | 2.26% | 12,363 | 10,866 |
| 25 Sep | +0.073% | 3.79% | 2.25% | 12,362 | 10,854 |
| 2 Oct | +0.076% | 3.97% | 2.24% | 12,583 | 11,081 |

### E.3 Stability (54 weeks)

- Mean 5.54% a year, standard deviation 1.96 pp; highest 14.12% (first week, 26 Sep 2025, on 647 avETH), lowest 3.41% (week to 20 Mar 2026).
- 0 negative weeks, 0 weeks below stETH. Since June the weekly range is 3.79% to 5.82%.
- The rate is a managed push, like an accountant rate: losses on the strategy, if any, would show only as smaller pushes. The September 2026 trend (3.79% to 4.39% a week) matches the spread compression in C.

### E.4 P&L by leg (share of start capital, pp)

| Window | Return | Staking (a) | Dollar leg (c) | Priced rewards (d) | Residual (f) |
|---|---:|---:|---:|---:|---:|
| 90d | 1.148 (4.74%/yr) | 0.489 | 0.403 | 0.044 | 0.212 |
| 365d | 5.473 | 2.321 | 1.988 | 0.056 | 1.108 |

In ETH over 90 days: staking 55.2, dollar leg 45.6, CRV 4.9, residual 23.9 (total 129.7 avETH on 11,302 average). The dollar leg is modelled (claim = debt), so 35% of the 90-day return rests on an assumption about savUSD that cannot be checked from Ethereum. The residual is nearly a fifth of the return and covers the books on other chains.

### E.5 Negative periods

None at weekly or monthly resolution. The lowest month vs stETH was March 2026 (+0.12 pp); the issuer stopped dollar borrowing in April and May and ran a WETH loop instead.

---

## F. Risk management

### F.1 Health factor over time

Month-end HF ranged 1.32 (Sep 2025) to 2.17 (Dec 2025); 1.35 to 1.42 since June 2026. Since June LTV 58% to 62% against an 81% to 84% liquidation threshold. No liquidation of the wallet was found.

### F.2 Delever episodes

| When | What | Trigger (inference) |
|---|---|---|
| Nov to Dec 2025 | Debt 4.33M to 2.89M, HF 1.46 to 2.17 | ETH −22% in November ($3,846 to $3,005) |
| Apr to May 2026 | Dollar debt below $0.1M; WETH borrowed instead | not disclosed |
| Sep 2026 | Debt 11.28M to 10.03M, mix moved to Spark | not disclosed; blended quote 3.79% to 6.34% |

### F.3 Liquidity ladder at T

| Tier | Repayable | % of debt | Source |
|---|---:|---:|---|
| Same block | $0.08M | 0.8% | Euler eUSDC withdraw to Aave USDC |
| Same block, LP exit | $0.16M | 1.6% | Stake DAO sdBOLD (BOLD/avUSD Curve LP) to USDS/USDC |
| About 1 day | 0 | 0% | savUSD cooldown 24h, not enough alone |
| 1 to 7 days | $9.79M | 97.6% | savUSD on Avalanche: cooldown, bridge, avUSD redemption up to 7 days or DEX sale |

Depositor exit: savETH cooldown 24h to avETH; avETH to ETH only through the permissioned redeemer, up to 7 days, with a fee shown in the app. CCIP bridge pools hold 16.3% of savETH for holders on other chains.

### F.4 Stress (instant ETH moves from $2,667, est.)

| ETH move | HF (both venues ~1.37 at T) | Liquidatable | Repayment to restore HF 1.37 | Same-block sources |
|---|---:|---|---:|---:|
| −10% | 1.23 | no | $1.0M | $0.24M |
| −20% | 1.10 | no | $2.0M | $0.24M |
| −27% | 1.00 | yes | | |
| −30% | 0.96 | yes | | |

HF scales linearly with ETH because all collateral is ETH or ETH LSTs. Everything above $0.24M waits on the 1 to 7 day savUSD path, so a 20% move inside a week is the operative risk.

---

## G. Depositors (T)

### G.1 Look-through (avETH + savETH; Gearbox and Morpho resolved; CCIP pool one row)

| Bucket | Owners | % owners | ETH | % ETH |
|---|---:|---:|---:|---:|
| < 1 ETH | 51 | 46.8% | 9.6 | 0.08% |
| 1 to 10 | 30 | 27.5% | 123.6 | 0.98% |
| 10 to 100 | 17 | 15.6% | 677.3 | 5.38% |
| 100 to 1k | 7 | 6.4% | 2,503.7 | 19.90% |
| > 1k | 4 | 3.7% | 9,267.3 | 73.66% |
| **Total** | **109** | | **12,581.4** | median 1.21 ETH |

Top 1 37.8% (`0x3d461625`: savETH directly, Gearbox credit account, Morpho collateral), top 10 92.6%, HHI 1,953. Top 2 is the CCIP pool (14.3%), top 3 the unstaked EOA `0xdd71cdd6` (11.2%).

### G.2 Address types (direct savETH)

| Holder | % of savETH |
|---|---:|
| Gearbox credit account (borrower `0x3d461625`) | 32.06% |
| Morpho Blue (savETH/WETH collateral, 3 material positions) | 17.63% |
| CCIP pool (bridged holders) | 16.27% |
| EOAs in the top 10 | 25.5% |
| Safe 2-of-5 `0x1cde180f` (also a top-10 holder of Liquity ETH Carry) | 1.91% |

### G.3 Holders over time (month-end)

| Month | savETH holders | New | Exited | savETH (avETH) | avETH supply |
|---|---:|---:|---:|---:|---:|
| Sep 2025 | 22 | 21 | 0 | 870 | 1,059 |
| Dec | 29 | 5 | 6 | 2,198 | 2,889 |
| Mar 2026 | 42 | 9 | 6 | 4,630 | 5,739 |
| May | 73 | 30 | 1 | 5,491 | 6,530 |
| Jun | 78 | 9 | 4 | 7,953 | 9,164 |
| Aug | 78 | 7 | 5 | 11,076 | 12,573 |
| Sep | 82 | 7 | 3 | 10,853 | 12,357 |
| T | 83 | 1 | 0 | 11,081 | 12,583 |

## H. TVL growth (savETH, avETH units)

| Period | Change | = net flows | + yield |
|---|---:|---:|---:|
| Sep to Dec 2025 | +2,198 | +2,176 | +21.6 |
| Jan to Mar 2026 | +2,432 | +2,404 | +28.2 |
| Apr to Jun | +3,324 | +3,260 | +63.6 |
| Jul to Sep | +2,900 | +2,791 | +108.4 |
| 1 to 2 Oct | +228 | +226 | +2.4 |
| **Total** | **+11,081** | **+10,857** | **+224.2** |

Yield = month-end shares × change in price per share (est.). In ETH terms yield is 2% of growth; the rest is deposits.

## I. Growth drivers (dated)

| Date | Event | Effect |
|---|---|---|
| 11 to 12 Aug 2025 | avETH, savETH, minting deployed; first mint | |
| 4 to 5 Sep 2025 | Control to EOA `0xd4d23209`; cooldown 7 days to 1 day | |
| 19 Sep 2025 | First daily push to savETH | 870 avETH in savETH by month-end |
| 15 Oct 2025 | Per-block mint and redeem caps 250 to 5,000 avETH | avETH doubles in October |
| 4 Nov 2025 | First savETH posted to Morpho savETH/WETH (loops) | 17.6% of savETH by T |
| 13 Nov 2025 to 15 May 2026 | AvantPoints (savETH, avETH, avETHx, Morpho, Pendle, Curve) | savETH 1,381 to 5,491 |
| 20 Apr 2026 | First 60-second cooldown window (30 windows to 27 Sep) | |
| 2 Jun 2026 | Admin gives itself the collateral-manager role | |
| Jun to Aug 2026 | Largest inflows (+2,440, +988, +2,064 avETH) | after points ended |
| 29 Sep 2026 | Issuer discloses $72.65M assets, $39.47M liabilities, $32.53M savUSD | |

**What explains the growth.** A rate 2 to 3 pp above stETH that never had a bad week, plus leverage on top: half of savETH sits in Gearbox and Morpho loops, so large holders borrow WETH to hold more of it. Points mattered less than the rate: inflows were larger after they ended.

## J. Operator economics (est. unless stated)

| Item | Amount |
|---|---|
| Paid to savETH, Sep 2025 to T (on-chain) | 248.62 avETH |
| Docs: 10% performance fee plus 10% of yield to junior avETHx | implies about 60 avETH withheld before savETH (est.) |
| Yield on unstaked avETH (1,500 avETH, kept by protocol per docs) | about 70 avETH a year at the savETH rate (est.) |
| Spread on Ethereum dollar debt at T | +1.24 pp × $10.0M ≈ $124k a year |
| Priced rewards on the wallet | CRV $10.4k realized in 365d; $37k a year run-rate |
| Reserve fund | 40.3 ETH |

Nothing in this table except the pushes and rewards can be verified on-chain: fees are taken off-chain before the push.

---

## K. Verdict: what to copy, what to avoid

**Copy:**
1. **Senior/junior split with a first-loss order** (reserve, then junior, then senior). The structure is right even if the buffer is thin.
2. **A savETH share that never had a down week.** Depositors value it; 50% of savETH is recycled as loan collateral, which also deepens demand.
3. **A steady health factor.** 1.35 to 1.42 at every month-end since June 2026 (a 27% ETH buffer at T), above Liquid's weakest leg at 1.27.

**Avoid:**
1. **Parking borrowed dollars in your own dollar product.** One credit bet, 98% of disclosed net NAV, and a week-long repayment path.
2. **A single EOA with mint rights and no delay,** plus unannounced 60-second cooldown windows.
3. **Off-chain fees and a managed push rate.** Depositors cannot reconcile 248.6 avETH of pushes to a P&L; half the book is on other chains.
4. **A 0.36% reserve fund** behind a 2.19× levered multi-chain book.
5. **Redemption only through a permissioned redeemer.**

---

## Method, limits, reproducibility

- **New data:** `weekly.csv`, 55 points (19 Sep 2025 to T, every 7 days back from T): savETH `convertToAssets(1e18)`, `totalAssets`, avETH `totalSupply`, wstETH `stEthPerToken`. Script `weekly.py` (helper `tools/eth/top5/weekly_lib.py`). RPC: Tenderly public gateway, fallback drpc. T read 1.059208 matches the 7 Oct pull.
- **Reused:** returns and splits (`rewards_split.csv`), incentive cost, month-end positions (`gap_top5_risk_series.csv`), ladder (`atlas_top5_risk.json`), keys, fees, events, holders.
- **Limits:**
  - avETH is valued at 1 ETH. Its backing NAV is the issuer's disclosure, not a reserve audit.
  - The dollar leg assumes the savUSD claim equals the debt; savUSD yield comes from the Chainlink SAVUSD/AVUSD feed and assumes avUSD at $1.
  - Fees, the junior carve-out and other-chain books are not on-chain; J is an estimate from docs.
  - AvantPoints are unpriced, so the rewards share is a lower bound.
  - The Morpho legs (C, D) come from the borrower study and were not re-read at T in this pass.
  - Stress assumes HF scales with ETH and ignores LST depegs (weETH, wstETH).
