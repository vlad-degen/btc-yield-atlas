# ether.fi Liquid ETH: the WETH loop

Snapshot **T = 2 Oct 2026 23:59:59 UTC, Ethereum block 26,108,081**. Window: 1 Oct 2024 23:59:59 UTC (block 20,874,085) to T, 2.003 years. Pulled 7 Oct 2026.

Accounts: both loops sit on the share contract itself, [`0xf0bb…416c`](https://etherscan.io/address/0xf0bb20865277abd641a307ece5ee04e79073416c): Aave V3 Core (weETH collateral, WETH debt, e-mode 1: LTV 93%, LT 95%, bonus 1%) and Spark (wstETH collateral, WETH debt, e-mode 1: LTV 92%, LT 93%, bonus 1%; first borrow 24 Mar 2026). No other Aave instance (Prime, EtherFi) holds a position.

Data: [`loop_weekly.csv`](../../../data/eth/top5/liquid/loop_weekly.csv) (105 weekly blocks × 2 pools), [`loop_events.csv`](../../../data/eth/top5/liquid/loop_events.csv) (323 Pool events), [`pnl_monthly.csv`](../../../data/eth/top5/liquid/pnl_monthly.csv). Raw reads and scripts: `raw/eth/gap-2026-10-07/liquid-loop/` (`scripts/build.py` regenerates all three files).

## Findings

1. **The loop added almost nothing over two years.** Loop collateral earned +22,678 ETH of staking; WETH interest cost −20,185 ETH; loop net **+2,499 ETH**. Holding the same loop equity unlevered in weETH would have earned 2,431 ETH. The leverage itself added **+68 ETH, 0.02 pp a year** of average NAV (156,118 ETH), 1 Oct 2024 to T.
2. **Two rate spikes erased the carry.** In weeks where WETH borrow cost exceeded staking, the loop lost money: Jul 2025 (loop −268 ETH, −421 ETH vs unlevered; Aave WETH 5.83% on 15 Jul 2025) and Apr 2026 (−318 ETH, −437 ETH vs unlevered; rsETH incident). Aave spread was negative in 33 of 104 weeks.
3. **The gap over stETH is 0.66 pp a year, not 1.36 pp.** Accountant rate over 730 days to T: Liquid **3.368%/yr**, wstETH rate (stETH) **2.707%/yr**, weETH **2.613%/yr**.
4. **Where the 3.31 pp/yr paid to holders comes from** (ETH, 1 Oct 2024 to T; pp of average NAV per year):

   | Component | ETH | pp/yr |
   |---|---:|---:|
   | weETH staking on the whole book, unlevered | 8,095 | 2.59 |
   | Loop excess over unlevered | 68 | 0.02 |
   | Dollar leg, parking minus interest (est.) | −408 | −0.13 |
   | Merkl rewards claimed (ETHFI, RLUSD, PYUSD, rEUL) | 131 | 0.04 |
   | Management fee (accountant setting) | −2,242 | −0.72 |
   | **Model** | **5,644** | **1.81** |
   | **Realized (Δ accountant rate × shares)** | **10,354** | **3.31** |
   | **Residual (not explained)** | **4,710** | **1.51** |

   The outperformance comes from the unexplained residual, not from the loop. The residual is **negatively correlated with loop excess** (ρ = −0.50 over 25 months): in Apr 2026 the loop lost 437 ETH vs unlevered and the residual was +496 ETH. The share price did not show the loop losses in the month they occurred. If the posted rate is gross of the management fee, the residual falls to 2,468 ETH (0.79 pp/yr).
5. **At T the loop is thin but positive.** At T rates (30-day weETH 2.330%, wstETH 2.250%; WETH 2.074% Aave, 1.907% Spark), the loop earns **+2,011 ETH/yr** (1.14 pp of NAV), of which **+1,153 ETH/yr (0.65 pp)** is excess over unlevered. Break-even is **+45.6 bp** on the WETH borrow rate.
6. **Health-factor breaches are self-inflicted and planned.** Of 19 closed Aave episodes below HF 1.03 (Feb to Sep 2026), 18 started with a collateral withdrawal into a redemption queue and 1 with a releverage borrow (19 Aug 2026). None came from price or rate drift. Each ended with a repay once the queue paid. Median lag **13.5 h**, max **125.7 h**. Lowest HF **1.0108** (11 May 2026 17:59 UTC, block 25,073,511). Before Feb 2026 the Aave HF never closed below **1.0488** (31 Jul 2025, block 23,042,513).
7. **The rsETH incident did not touch the HF; the vault's response did.** Aave WETH rate jumped at block 24,908,845 (18 Apr 2026 19:28 UTC). The vault reacted **2 h 18 min later**: it withdrew collateral into native redemption queues, taking HF from 1.0539 to 1.0248. The first repay came **93.6 h** after the spike. Aave debt then fell **51%**, from 534,598 WETH (3 Apr) to 263,469 WETH (5 Jun 2026).
8. **Same-block WETH is about 7.5k against 410k of Aave debt (1.8%).** On-chain DEX depth at T: weETH→WETH ≈ **7.2k WETH** at ≤0.5% slippage; wstETH/stETH→ETH ≈ **16.2k ETH**. Vault idle: 20.6 WETH. Restoring Aave HF to 1.03 by delevering needs **14,960 WETH**; to 1.05, **93,994 WETH**. Real exits go through ether.fi's priority queue (median 4.6 h since 25 Apr 2026).
9. **The tail risk is the exchange rate, not the market price.** Both oracles price collateral at the token exchange rate times ETH/USD (Aave: "Capped weETH / eETH(ETH) / USD", ratio to WETH 1.104943 = `getRate()` at T). A market depeg leaves HF unchanged. A **2.64% cut to weETH's exchange rate** (slashing or loss socialization) liquidates the Aave leg. Spark liquidates at a 3.49% cut to wstETH.

## A. Position at T (block 26,108,081)

| | Aave V3 Core | Spark |
|---|---:|---:|
| Collateral units | 401,298.58 weETH | 27,770.15 wstETH |
| Exchange rate | 1.104943 | 1.245402 |
| Collateral, ETH | 443,412 | 34,585 |
| WETH debt | 410,134 | 31,042 |
| Equity, ETH | 33,278 | 3,543 |
| Health factor | 1.0271 | 1.0361 |
| Leverage (collateral / equity) | 13.32× | 9.76× |
| WETH borrow APR, instant | 2.074% | 1.907% |
| Share of pool WETH debt | 23.3% of 1,761,598 | 6.3% of 492,184 |
| Pool WETH cash (flash-loanable) | 269,693 | 116,148 |

Loop equity 36,821 ETH is **20.8%** of the book NAV of 177,171 ETH. Gross loop collateral is **2.70×** NAV.

## B. Leverage history (weekly; Aave unless stated)

| Week end | Block | Collateral ETH | WETH debt | HF | Leverage | WETH APR | weETH APR (week) | Share of Aave WETH debt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-10-04 | 20,895,606 | 94,919 | 78,719 | 1.145 | 5.9× | 2.97% | | 7.0% |
| 2025-01-03 | 21,547,396 | 224,454 | 199,263 | 1.070 | 8.9× | 2.57% | 2.62% | 13.3% |
| 2025-04-04 | 22,198,999 | 399,354 | 360,611 | 1.052 | 10.3× | 2.61% | 2.80% | 18.3% |
| 2025-07-04 | 22,849,297 | 661,899 | 591,001 | 1.064 | 9.3× | 2.57% | 2.50% | 25.1% |
| 2025-10-03 | 23,500,695 | 535,675 | 478,093 | 1.064 | 9.3× | 2.31% | 2.51% | 22.7% |
| 2026-01-02 | 24,150,396 | 637,765 | 569,015 | 1.065 | 9.3× | 1.97% | 2.38% | 23.8% |
| 2026-02-06 | 24,401,222 | 592,837 | 550,225 | 1.024 | 13.9× | 5.48% | 2.69% | 18.5% |
| 2026-04-03 | 24,802,549 | 593,047 | 534,597 | 1.054 | 10.1× | 2.20% | 2.52% | 20.6% |
| 2026-05-01 | 25,003,545 | 483,137 | 447,054 | 1.027 | 13.4× | 4.09% | 2.29% | 21.7% |
| 2026-06-05 | 25,254,619 | 304,218 | 263,469 | 1.097 | 7.5× | 2.07% | 2.51% | 16.7% |
| 2026-09-04 | 25,907,399 | 444,497 | 409,491 | 1.031 | 12.7× | 2.01% | 2.29% | 23.1% |
| 2026-10-02 (T) | 26,108,081 | 443,412 | 410,134 | 1.027 | 13.3× | 2.07% | 2.35% | 23.3% |

- **Peak debt:** 591,295 WETH (11 Jul 2025), 26.9% of Aave WETH debt.
- **Target band moved down.** Median HF right after a releverage: 1.098 in 2024 (6 txs), 1.064 in 2025 (11), 1.054 in H1 2026 (3), **1.048 from Jul 2026** (11; min 1.023). Weekly leverage median 9.3× over the window; 12.0 to 13.3× since Aug 2026.
- **Spark** (from 24 Mar 2026): HF 1.027 to 1.169; it sat at 1.027 to 1.036 after 18 Apr 2026.

## C. Deleverage and releverage events

323 Pool events in 130 transaction-pool pairs, 9 Oct 2024 to 18 Sep 2026; no `LiquidationCall`.

| Transaction type (per pool) | Aave | Spark |
|---|---:|---:|
| Releverage (borrow + supply) | 31 | 5 |
| Borrow only | 6 | 0 |
| Collateral withdraw only | 34 | 1 |
| Repay only | 38 | 0 |
| Repay + withdraw | 10 | 0 |
| Collateral add only | 5 | 0 |

**How a deleverage works.** The vault withdraws weETH and unwraps it to eETH, then requests redemption from ether.fi. Once the ETH is paid out, it wraps to WETH and repays. HF therefore dips first and recovers on repay. Redemption queues used by the vault (`withdrawal_queue_logs_raw.json`):

| Queue | Requests | Amount | Request to claim |
|---|---:|---:|---|
| ether.fi WithdrawRequestNFT `0x7d57…4e2c` | 31 (21 Jul 2025 to 18 Apr 2026) | 182,284 eETH | median 5.29 d, max 20.57 d |
| ether.fi PriorityWithdrawalQueue `0x35e7…45fa` | 219 (25 Apr to 18 Sep 2026) | 337,607 eETH | median 4.6 h, p90 16.9 h, max 68.6 h |
| Lido WithdrawalQueue `0x889e…f9b1` | 23 (4 Apr 2025 to 21 Apr 2026) | 20,734 stETH | 22 claims, 20,709 ETH |

One priority request of 6,038 eETH (18 Sep 2026) has no matching claim event by T.

**Breaches** (HF timeline from 732 day-end reads plus HF at block−1 and block for each of 127 event blocks):

| Threshold | Aave episodes | Lag to restoring action | Cause |
|---|---|---|---|
| < 1.03 | 19 closed + 1 open at T | median 13.5 h; max 125.7 h (30 Apr 23:39 to 6 May 05:18 2026) | 18 collateral withdrawals (1 inside a repay+withdraw tx), 1 releverage borrow (19 Aug 2026) |
| < 1.02 | 12 (5 May to 16 Sep 2026) | 1.4 to 29.4 h | collateral withdrawals |
| < 1.015 | 9 (5 to 11 May 2026) | 1.4 to 12.9 h | collateral withdrawals |

- **Open at T:** HF 1.0271 has been below 1.03 since 18 Sep 2026 03:15 UTC, 357 h, after a 4,000 weETH withdrawal.
- **Day-ends:** the Aave HF closed below 1.03 on 38 of 732 days and below 1.02 on 7.
- **Spark** stayed below 1.03 from 18 Apr 22:51 to 28 May 22:59 2026 (960 h; min 1.0272).

**April 2026 rsETH window** (hourly reads 17 Apr to 1 May, `hourly_apr2026_raw.json`):

| UTC | Block | Event | Aave HF |
|---|---:|---|---:|
| 18 Apr 19:00 | 24,908,703 | Aave WETH 2.31%, Spark 2.12% | 1.0539 |
| 18 Apr 19:28 | 24,908,845 | Aave WETH rate 4.98%; 8.33% by 20:00; 8.35% held to 20 Apr, then 5.00% to 30 Apr | 1.0539 |
| 18 Apr 21:46 | 24,909,534 | Withdraw 15,000 weETH from Aave; 18,064 weETH unwrapped and 19,742 eETH queued at ether.fi | 1.0248 |
| 18 Apr 22:00 | 24,909,601 | Spark WETH peaks 91.7%; back to 1.84% by 19 Apr 08:00 | 1.0248 |
| 18 Apr 22:51 | 24,909,861 | Withdraw 3,140 wstETH from Spark; 3,869 stETH queued at Lido (Spark HF 1.1685 → 1.0276) | 1.0248 |
| 22 Apr 19:24 | 24,937,540 | First repay, 11,235 WETH | 1.0464 |
| 30 Apr to 11 May | 24,996,265 to 25,074,829 | 24 transactions, 13 repays totalling 182,660 WETH, funded via the priority queue; HF floor 1.0108 | 1.011 to 1.074 |

The Aave WETH rate stayed above 4% for 293 of 337 hourly reads. April loop interest was 1,556 ETH vs 991 ETH in March. In the April 2026 loop accounts, HF moved only on the vault's own transactions.

## D. Monthly P&L in ETH, reconciled to the share price

Columns are ETH over each month (day-end reads, last day 23:59:59 UTC).
- **Loop:** daily Σ collateral units × Δ exchange rate, minus scaled debt × Δ normalized variable-debt index. A month-by-month check against equity change net of event flows agrees within 7.5 ETH.
- **Loop excess:** loop net minus loop equity × weETH growth.
- **Other assets staking:** (NAV − loop equity) × weETH growth.
- **Dollar leg (est.):** average month-end dollar debt × (claims share × parking APR − borrow APR), all from [`gap_top5_risk_series.csv`](../../../data/eth/gap_top5_risk_series.csv) and [TOP5-RISK-LIQUIDITY.md](TOP5-RISK-LIQUIDITY.md).
  - Parking: stcUSD for 2025. For 2026 it is the T claim mix (55.10M senRLUSDv2, 49.61M senPYUSDPRIMEv2, 24.6M stcUSD = 71.4% of debt).
  - Sep 2026 uses the T borrow quote (7.79%), not the 14.25% one-block month-end spike.
- **Rewards:** Merkl `Claimed` events to the vault, priced at the claim date (ETHFI and EUL at DefiLlama; stablecoins at $1).
- **Fee:** accountant `managementFee` × NAV. The setting is 100 bp (Oct 2024), 150 (Jan 2025), 0 (Aug 2025), 50 (Nov 2025), 0 (Jan 2026), then 25 to 80 bp and 35 bp at T.
- **Realized:** Δ accountant rate × total shares (Ethereum + Optimism, interpolated from month-end book NAV).

| Month | End block | Avg NAV | Loop staking | WETH interest | Loop net | Loop excess | Other assets staking | Dollar leg (est.) | Rewards | Mgmt fee | Model | Realized | Residual |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-10 | 21,089,068 | 146,045 | 236 | -204 | 33 | -14 | 270 | 0 | 0 | -120 | 184 | 355 | 171 |
| 2024-11 | 21,303,933 | 148,210 | 389 | -307 | 83 | 31 | 302 | 0 | 0 | -122 | 263 | 414 | 150 |
| 2024-12 | 21,525,890 | 151,481 | 548 | -506 | 43 | -39 | 268 | 0 | 0 | -129 | 182 | 351 | 169 |
| 2025-01 | 21,747,949 | 153,035 | 570 | -477 | 94 | 30 | 288 | 0 | 0 | -191 | 191 | 359 | 168 |
| 2025-02 | 21,948,291 | 156,303 | 690 | -562 | 128 | 52 | 268 | 0 | 0 | -180 | 216 | 301 | 84 |
| 2025-03 | 22,170,334 | 160,331 | 886 | -823 | 63 | -26 | 277 | 0 | 0 | -204 | 136 | 199 | 62 |
| 2025-04 | 22,385,293 | 169,225 | 1,021 | -854 | 167 | 67 | 328 | 0 | 0 | -209 | 286 | 618 | 331 |
| 2025-05 | 22,606,142 | 185,924 | 1,054 | -922 | 132 | 27 | 306 | 0 | 0 | -237 | 201 | 269 | 68 |
| 2025-06 | 22,820,673 | 193,353 | 1,200 | -1,071 | 128 | 3 | 285 | 0 | 0 | -238 | 175 | 172 | -4 |
| 2025-07 | 23,042,513 | 196,086 | 1,415 | -1,684 | -268 | -421 | 278 | 0 | 0 | -250 | -240 | 178 | 418 |
| 2025-08 | 23,264,565 | 201,770 | 1,299 | -1,203 | 96 | -64 | 286 | 35 | 0 | 0 | 417 | 912 | 495 |
| 2025-09 | 23,479,243 | 197,693 | 1,148 | -960 | 188 | 43 | 267 | 58 | 0 | 0 | 513 | 748 | 235 |
| 2025-10 | 23,700,766 | 184,877 | 1,181 | -983 | 198 | 71 | 280 | 34 | 0 | -2 | 509 | 864 | 355 |
| 2025-11 | 23,914,920 | 162,645 | 1,147 | -865 | 283 | 160 | 224 | 0 | 0 | -67 | 440 | 660 | 220 |
| 2025-12 | 24,136,052 | 147,487 | 1,202 | -871 | 331 | 201 | 172 | 0 | 0 | -63 | 440 | 651 | 211 |
| 2026-01 | 24,358,292 | 150,701 | 1,324 | -991 | 333 | 190 | 169 | 0 | 6 | -2 | 506 | 604 | 98 |
| 2026-02 | 24,558,867 | 131,311 | 1,103 | -1,128 | -25 | -144 | 134 | 0 | 0 | 0 | 110 | 249 | 140 |
| 2026-03 | 24,781,026 | 127,742 | 1,186 | -991 | 195 | 77 | 151 | 0 | 0 | 0 | 346 | 357 | 11 |
| 2026-04 | 24,996,367 | 135,938 | 1,238 | -1,556 | -318 | -437 | 159 | 0 | 0 | 0 | -159 | 336 | 496 |
| 2026-05 | 25,218,797 | 116,383 | 742 | -757 | -15 | -91 | 153 | 0 | 0 | -13 | 125 | 285 | 160 |
| 2026-06 | 25,433,938 | 98,432 | 673 | -505 | 167 | 93 | 128 | -3 | 0 | -40 | 252 | 290 | 38 |
| 2026-07 | 25,656,292 | 105,412 | 661 | -527 | 134 | 80 | 162 | -35 | 0 | -65 | 196 | 325 | 129 |
| 2026-08 | 25,878,704 | 148,008 | 794 | -650 | 144 | 72 | 227 | -187 | 48 | -60 | 171 | 373 | 202 |
| 2026-09 | 26,093,737 | 175,416 | 908 | -737 | 171 | 99 | 262 | -277 | 73 | -47 | 182 | 456 | 274 |
| 2026-10 (to T) | 26,108,081 | 177,068 | 64 | -50 | 14 | 9 | 19 | -31 | 4 | -3 | 2 | 30 | 28 |

**What the residual contains.**
- Income of non-loop strategies above the weETH rate, such as LP fees, Pendle and lending positions, and restaking rewards paid outside the exchange rate.
- Timing differences in the strategist's rate.
- Errors in the dollar-leg estimate.

The positive residual in 24 of 25 months shows that non-loop assets earn more than plain weETH. It is the largest single source of excess return.

**Rewards are small.** Merkl claims to the vault total 22,179 ETHFI, 172,802 RLUSD, 150,679 PYUSD and 1,057 rEUL (24 Jan 2026 to 2 Oct 2026, blocks 24,300,979 to 26,101,710). That is 131 ETH at claim-date prices. ETHFI campaigns were for "Lend weETH on Aave", i.e. for the loop collateral.

**Not in the model.** If the dollar debt with no claim (28.6%) was converted to ETH, the ETH/USD move would add +3,379 ETH over Jun to Sep 2026. The column `sens_unmatched_dollar_price_effect_eth_not_in_model` holds this. The realized share price shows no such gain, so it is excluded.

## E. Stress at T (block 26,108,081)

| Shock | Aave HF | Spark HF | Loop P&L / equity effect |
|---|---:|---:|---|
| None | 1.0271 | 1.0361 | +2,011 ETH/yr (1.14 pp NAV); +1,153 ETH/yr (0.65 pp) vs unlevered |
| WETH borrow +1 pp, both pools | unchanged now; drift −0.74%/yr → 1.02 in 0.93 yr, 1.00 in 3.6 yr | similar | **−2,401 ETH/yr** (−1.35 pp NAV). Break-even +45.6 bp (Aave alone +44.5 bp) |
| weETH/stETH market depeg −1% | unchanged (exchange-rate oracle) | unchanged | mark-to-market −4,780 ETH = 13.0% of loop equity, 2.70% of NAV |
| market depeg −3% | unchanged | unchanged | −14,340 ETH = 38.9% of loop equity, 8.09% of NAV |
| exchange-rate cut −1% | 1.0168 | 1.0258 | same mark-to-market as above |
| exchange-rate cut −3% | **0.9963 (liquidatable)** | 1.0051 | Aave liquidation bonus 1% on seized collateral |
| Liquidation distance | −2.64% exchange rate | −3.49% | |

**WETH available for repayment in the same block** (quotes at block 26,108,081):

| Source | WETH (or ETH) | Note |
|---|---:|---|
| Vault idle | 20.6 WETH + 230.2 weETH + 90.9 eETH; 6.1 aWETH | balances at T |
| Uniswap v3 weETH/WETH 0.05% | 4,961 | ≤0.25% below exchange rate; pool exhausted above |
| Uniswap v3 weETH/WETH 0.01% | 1,379 | ≤0.17%; exhausted at ~1,250 weETH in |
| Curve weETH/WETH-ng | 826 | ≤0.29%; 8.6% slippage at 1,000 weETH |
| **weETH venues total** | **≈7,170** | 1.75% of Aave debt |
| Curve stETH/ETH + stETH/ETH-ng + Uni wstETH/WETH | ≈16,200 at ≤0.5% | covers 52% of Spark debt |
| Aave / Spark WETH cash for flash loans | 269,693 / 116,148 | funding only; the collateral still has to be sold or redeemed |

Fluid, Balancer and aggregator multi-hop routes were not quoted, so the DEX totals are a lower bound. Even so, restoring Aave HF needs far more than the quoted depth:
- **to 1.03:** repay 14,960 WETH, or add 1,260 ETH of weETH;
- **to 1.05:** repay 93,994 WETH, or add 9,894 ETH;
- **to 1.10:** repay 199,374 WETH, or add 31,480 ETH.

The working exit is the ether.fi priority queue, which takes hours (section C). A sudden exchange-rate cut above 2.64% cannot be answered within one block.

## Method notes

- **Weekly blocks:** last block at or before T − 7k days, 23:59:59 UTC, found by timestamp search (`weekly_blocks.json`). Archive `eth_call` via drpc and publicnode; `eth_getLogs` via Tenderly.
- **ETH units:** weETH × `getRate()`, wstETH × `stEthPerToken()`. Both Aave and Spark oracles use the same rates, verified at T (`oracle_check_T_raw.json`: price ratio to WETH 1.1049430 vs `getRate()` 1.1049430; 1.2454019 vs `stEthPerToken()` 1.2454019).
- **Staking APR:** annualized simple exchange-rate growth over the week (weekly file) or 30 days (T stress).
- **Realized borrow APR:** normalized variable-debt index growth. The index is computed from `variableBorrowIndex`, `currentVariableBorrowRate` and `lastUpdateTimestamp` in `getReserveData`.
- **HF:** `getUserAccountData`. **Leverage:** collateral ETH / (collateral ETH − WETH debt).
- **Breach timing:** episode start is the event block when an event pushed HF below the threshold. Episode end is the first event that lifted it back. Drift crossings would be interpolated between day-ends, but none occurred.
