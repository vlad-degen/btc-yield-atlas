# ether.fi Liquid ETH: deep dive (yield history, risk, depositors, growth, economics)

*Scripts: [`tools/eth/top5/liquid/`](../../../../tools/eth/top5/liquid/), data: [`data/eth/top5/liquid/`](../../../../data/eth/top5/liquid/). Mentions of `raw/` refer to the working folder; raw dumps are not published.*

Veda BoringVault "Liquid ETH" ([`0xf0bb…416c`](https://etherscan.io/address/0xf0bb20865277abd641a307ece5ee04e79073416c), Ethereum, shares also on Optimism), strategy by Nonce for ether.fi.

**Date:** 7 Oct 2026. **Snapshot T:** 2 Oct 2026 23:59:59 UTC, Ethereum block 26,108,081. Main window: 1 Oct 2024 to T (2.003 years).

**Benchmark.** Every return is set against stETH (wstETH `stEthPerToken`) over the same blocks. Carry that does not beat stETH has not earned its risk.

**Labels.** **(est.)** marks our model estimates. Everything else is read from chain or an API. Addresses with no public label are "unlabelled".

**Reuse.** [LIQUID-LOOP](../../en/LIQUID-LOOP.md) (loop, P&L, stress), [REWARDS-SPLIT](../../en/REWARDS-SPLIT.md), [TOP5-RISK-LIQUIDITY](../../en/TOP5-RISK-LIQUIDITY.md) (dollar legs, ladder, reward payers), [TOP5-KEYS-HOLDERS-TERMS](../../en/TOP5-KEYS-HOLDERS-TERMS.md). New here: weekly and month-end price against stETH, the year split of the lead, whale tracing, Accountant bounds.

**Files** in `data/eth/top5/liquid/`:
- `yield_weekly.csv` (new; 105 Friday blocks)
- `yield_monthly.csv` (new; 25 month-end blocks)
- `loop_weekly.csv`, `loop_events.csv`, `pnl_monthly.csv`
- `holder_buckets.csv`, `holders_monthly.csv`

---

## Key findings

1. **The whole two-year lead over stETH came in year two.** Weekly chained, 4 Oct 2024 to 3 Oct 2025: Liquid 2.86%, stETH 2.93%. 3 Oct 2025 to T: Liquid 3.86%, stETH 2.47%. Over two years: 3.37% against 2.71% a year (+0.66 pp).
2. **The biggest cause of the turn is the fee, not the strategy.** The management fee took 1.10 pp of NAV in year one (100 to 150 bp) and 0.26 pp in year two (0 for most months). That is +0.84 pp of the +1.49 pp swing in the lead. The ETH loop turning positive added +0.45 pp and ether.fi's KING drops +0.38 pp; the dollar leg took -0.40 pp.
3. **The loop added nothing over two years:** +68 ETH over the same equity unlevered, +0.02 pp a year. Two rate spikes did the damage: 4 Jul to 8 Aug 2025 (6 weeks, loop net -278 ETH) and 24 Apr to 8 May 2026 (3 weeks, -577 ETH).
4. **The share price is posted, not marked.** The Accountant accepts at most +0.5% or -0.5% per update, at most one update every 6 hours. From 20 Mar to 17 Apr 2026 the weekly rate sat at 3.55 to 3.57% five weeks running. The April 2026 loop loss (-437 ETH against unlevered) never showed in the price. The only weekly fall in two years was 11 to 25 Jul 2025 (-0.057%).
5. **Our model cannot explain 1.51 pp a year of what holders got.** It is +4,710 ETH over two years, and it is largest in the months the loop lost (Jul 2025 +418 ETH, Apr 2026 +496 ETH). About 0.17 pp of it is KING drops that the loop P&L model does not count as rewards.
6. **The dollar sleeve loses about $6.8M a year at T rates, 1.4 pp of NAV.** $181.1M of debt costs $14.1M a year; $64.6M of it is Aave USDC at 13.93%. Claims earn $4.7M of base yield plus $2.6M of rewards. $46.4M (25.6%) of the debt has no dollar claim on Liquid's three accounts.
7. **Rewards are 34% of last year's lead (365d: 3.87% actual, 3.39% without rewards, stETH 2.48%).** Today's payer is the RLUSD and PYUSD issuer side, through Sentora-created campaigns: $2.73M a year at T, 0.58% of the book.
8. **Liquid sits on both sides of the Sentora vaults.** It parks $55.1M in Sentora RLUSD Main and borrows $70.2M RLUSD from the weETH/RLUSD market that vault lends into. In PRIME it borrows PYUSD against PRIME to deposit in a vault whose only market is PRIME/PYUSD. Sentora RLUSD Main is also the Kraken BTC vault's lender.
9. **The ETH loop runs at health factor 1.027 with one-block exit depth of about 7,200 WETH against 410,134 WETH of Aave debt.** It sat below 1.03 for 357 hours at T. A 2.64% cut in weETH's exchange rate liquidates it; a market depeg does not move the health factor.
10. **Four wallets drive the book.** Two wallets (0xc518, 0xee95; 37.9k shares) left in Feb 2026, returned in March, and left again in the week of the 18 Apr rsETH exploit. Three wallets made 97% of the Jul to Aug 2026 net inflow. 0xee95 is now Lido Earn's largest holder.
11. **The fee changed 12 times in two years** (100, 150, 0, 50, 0, 25, 50, 65, 80, 70, 10, 35 bp). The fee setter at role 55 has no delay; the owner timelock has 24 hours. 2,130.6 ETH was claimed in 19 payments.

---

## A. Scope and snapshot

| Item | Value at T | Source |
|---|---|---|
| Book NAV | 177,171 ETH ($472.7M): 125,538.6 Ethereum shares + 34,533.3 Optimism shares × 1.106822 | Accountant `getRate`, `totalSupply` on both chains |
| Rate age | posted 2 Oct 06:26:47 UTC, 17 h 33 min before T | Accountant state |
| ETH loop | Aave: 443,412 ETH weETH against 410,134 WETH, HF 1.0271. Spark: 34,585 ETH wstETH against 31,042 WETH, HF 1.0361 | `getUserAccountData` |
| Dollar debt | $181.08M on three accounts, debt-weighted borrow 7.79% | Aave, Spark, Morpho reads |
| Holders | 7,793 Ethereum addresses, 1,511 Optimism | Transfer replay |
| Realized | 3.37% a year over 730 days; stETH 2.71%; weETH 2.61% | share price, same blocks |

Positions explain $458.6M of the $472.7M book; $14.1M (2.98%) is unmapped, not a proven deficit (CAPITAL-INCOME-EXIT).

## B. Structure and legs

| Leg | Account | Collateral to debt | Where the money goes | Size at T |
|---|---|---|---|---|
| ETH loop, Aave | main vault | weETH to WETH, e-mode (LTV 93%, LT 95%) | more weETH | 410,134 WETH debt, 13.3× |
| ETH loop, Spark (since 24 Mar 2026) | main vault | wstETH to WETH, e-mode (LTV 92%, LT 93%) | more wstETH | 31,042 WETH debt, 9.8× |
| Aave dollars (since Aug 2025) | drone [`0x0a42…c02c`](https://etherscan.io/address/0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c) | weETH to USDC, USDT | Cap stcUSD, Sentora vaults | $64.6M USDC at 13.93%, $12.0M USDT |
| Spark PYUSD | drone | wstETH to PYUSD | Sentora PRIME PYUSD | $3.6M |
| Morpho dollars (from Jun 2026) | main vault, loan manager [`0xc936…45f3`](https://etherscan.io/address/0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3) | weETH to RLUSD, USDC | Sentora RLUSD Main, Cap | $70.2M RLUSD, $30.7M USDC |
| PRIME loop (from 25 Sep 2026) | main vault | PRIME to PYUSD, Morpho LLTV 86% | Sentora PRIME Main | 21.0M PYUSD at HF 1.08 |
| Other | main vault | none | Uniswap v3 WETH/weETH (6,876 ETH), Fluid weETH/ETH (3,074 ETH net), Liquid Monad claim ($21.7M) | |

Dollar claims at T: 55.10M senRLUSDv2, 49.61M senPYUSDPRIMEv2 (one share is 2.025 PYUSD), 24.63M stcUSD. 129.3M in all, 71.4% of debt.

## C. Governance and security

| Who | Can change | Delay |
|---|---|---|
| TimelockController [`0xd829…2c89`](https://etherscan.io/address/0xd829f278016b90fec735f9a12bf8b75e06102c89), owner of Authority [`0x485b…8122`](https://etherscan.io/address/0x485bde66bb668a51f2372e34e45b1c6226798122) | roles, fee (role 8) | 24 h (`getMinDelay` 86,400) |
| [`0x607d…7306`](https://etherscan.io/address/0x607d0c7e3578802eb46d388cb86cfba8ff657306), role 55 | management fee, capped at 20% in code | none |
| Three role-11 addresses | post the share price | none; bounded per update |
| Payout address `0xf6bd…a863` (unlabelled) | receives fees | n/a |

Accountant state at T (block 26,108,081): rate 1.106822, upper bound 10,050 and lower 9,950 (±0.5% per update), minimum 21,600 s between updates, management fee 35 bp, fees owed 1.31 ETH, not paused. These are the same bounds as the Kraken BTC vault. 36 addresses have ever held a role; 22 are active at T.

Exit: the BoringOnChainQueue takes weETH only (WETH withdrawals disabled): maturity 1 h, minimum deadline 3 days, discount 0 to 10 bp. 2,822 Ethereum requests paid to T: median 12.56 h, p90 56.39 h, longest 12.26 days.

---

## D. Yield history since 1 Oct 2024

### D.1 Month by month against stETH

APYs from month-end share prices (`yield_monthly.csv`). ETH columns from `pnl_monthly.csv`: loop excess over the same equity unlevered, dollar leg (est.), rewards claimed (in brackets: all priced rewards incl. KING from `rewards_split.csv`), fee, and the residual the model cannot assign.

| Month | Liquid APY | stETH APY | Lead, pp | Loop excess | Dollar leg (est.) | Rewards | Fee | Residual |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-10 | 3.00% | 3.05% | -0.05 | -14 | 0 | 0 | -120 | 171 |
| 2024-11 | 3.45% | 3.07% | +0.38 | 31 | 0 | 0 | -122 | 150 |
| 2024-12 | 2.77% | 2.96% | -0.20 | -39 | 0 | 0 | -129 | 169 |
| 2025-01 | 2.80% | 3.02% | -0.22 | 30 | 0 | 0 | -191 | 168 |
| 2025-02 | 2.55% | 3.32% | -0.77 | 52 | 0 | 0 | -180 | 84 |
| 2025-03 | 1.47% | 2.99% | -1.52 | -26 | 0 | 0 | -204 | 62 |
| 2025-04 | 4.58% | 3.06% | +1.52 | 67 | 0 | 0 | -209 | 331 |
| 2025-05 | 1.71% | 2.88% | -1.17 | 27 | 0 | 0 | -237 | 68 |
| 2025-06 | 1.09% | 2.79% | -1.70 | 3 | 0 | 0 | -238 | -4 |
| 2025-07 | 1.07% | 2.75% | -1.68 | -421 | 0 | 0 | -250 | 418 |
| 2025-08 | 5.47% | 2.73% | +2.73 | -64 | 35 | 0 | 0 | 495 |
| 2025-09 | 4.71% | 2.67% | +2.03 | 43 | 58 | 0 | 0 | 235 |
| 2025-10 | 5.67% | 2.79% | +2.88 | 71 | 34 | 0 (322) | -2 | 355 |
| 2025-11 | 5.08% | 2.69% | +2.39 | 160 | 0 | 0 (173) | -67 | 220 |
| 2025-12 | 5.33% | 2.58% | +2.75 | 201 | 0 | 0 (83) | -63 | 211 |
| 2026-01 | 4.84% | 2.48% | +2.36 | 190 | 0 | 6 (66) | -2 | 98 |
| 2026-02 | 2.52% | 2.50% | +0.03 | -144 | 0 | 0 | 0 | 140 |
| 2026-03 | 3.32% | 2.54% | +0.79 | 77 | 0 | 0 | 0 | 11 |
| 2026-04 | 3.05% | 2.52% | +0.53 | -437 | 0 | 0 | 0 | 496 |
| 2026-05 | 2.95% | 2.48% | +0.47 | -91 | 0 | 0 | -13 | 160 |
| 2026-06 | 3.67% | 2.45% | +1.22 | 93 | -3 | 0 | -40 | 38 |
| 2026-07 | 3.70% | 2.24% | +1.46 | 80 | -35 | 0 (2) | -65 | 129 |
| 2026-08 | 3.01% | 2.23% | +0.78 | 72 | -187 | 48 (55) | -60 | 202 |
| 2026-09 | 3.21% | 2.27% | +0.94 | 99 | -277 | 73 (76) | -47 | 274 |
| 1 to 2 Oct 2026 | 3.12% | 2.24% | +0.88 | 9 | -31 | 4 (16) | -3 | 28 |

- **Year one trailed stETH in 8 of 12 months**, under a 150 bp fee from Jan 2025.
- **Aug 2025 to Jan 2026 was the strong run** (+2.0 to +2.9 pp a month): fee near 0, KING drops, large residual.
- **Since Feb 2026 the lead is +0.03 to +1.46 pp a month.**

### D.2 Year one against year two (pp of average NAV a year, `pnl_monthly.csv`)

| Component | Oct 2024 to Sep 2025 | Oct 2025 to T | Change |
|---|---:|---:|---:|
| Average NAV | 171,758 ETH | 140,607 ETH | |
| Staking on non-loop assets | 2.00 | 1.58 | -0.42 |
| Loop net (staking on loop minus WETH interest) | 0.52 | 1.14 | +0.62 |
| of which excess over unlevered | -0.18 | +0.27 | +0.45 |
| Dollar leg (est.) | +0.05 | -0.35 | -0.40 |
| Merkl rewards claimed | 0 | 0.09 | +0.09 |
| Management fee | **-1.10** | **-0.26** | **+0.84** |
| Residual (includes KING drops in year two) | 1.37 | 1.67 | +0.30 |
| **Realized** | **2.85** | **3.88** | **+1.03** |
| stETH | 2.93 | 2.47 | -0.46 |
| **Lead over stETH** | **-0.08** | **+1.41** | **+1.49** |

The 2-year table in LIQUID-LOOP (realized 3.31 pp a year, model 1.81, residual 1.51) is the sum of these two columns.

### D.3 Weekly (`yield_weekly.csv`; APY from Friday-to-Friday share price, compounded)

| Window | Weeks | Mean | Std dev | Worst week | Best week | Weeks below stETH | Weeks below zero |
|---|---:|---:|---:|---|---|---:|---:|
| 4 Oct 2024 to 3 Oct 2025 | 52 | 2.88% | 1.94 pp | -2.70% (25 Jul 2025) | 8.64% (11 Apr 2025) | 31 | 2 |
| 3 Oct 2025 to T | 52 | 3.87% | 1.19 pp | 1.13% (20 Feb 2026) | 6.87% (17 Oct 2025) | 5 | 0 |
| Last 13 weeks | 13 | 3.33% | 0.44 pp | 2.50% (21 Aug 2026) | 4.37% (17 Jul 2026) | 0 | 0 |

- **Longest run below stETH:** 13 weeks, to 25 Jul 2025.
- **The only fall:** 1.056131 (11 Jul 2025) to 1.055526 (25 Jul 2025). The next week printed +7.13%, the catch-up.
- **The flat stretch:** the five weeks to 20 Mar, 27 Mar, 3 Apr, 10 Apr and 17 Apr 2026 printed 3.56, 3.55, 3.56, 3.55, 3.57%. The Aave WETH rate jumped to 8.35% on 18 Apr; the following weeks printed 2.49, 2.13, 2.54%. The loop lost 577 ETH over those three weeks.


### D.4 Carry P&L by leg

| Window | Staking | ETH loop spread | Dollar leg | Rewards | Fees | Residual | Return |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2 years to T (ETH; LIQUID-LOOP) | 8,095 (unlevered weETH on the whole book) | +68 (excess) | -408 (est.) | 131 (Merkl only) | -2,242 | 4,710 | 10,354 |
| 365d to T (pp; REWARDS-SPLIT) | 2.50 | 0.29 | -0.11 | 0.48 | -0.29 | 1.01 | 3.87 |
| 90d to T (pp, annualized) | 2.38 | 0.75 | -0.63 | 0.37 | -0.52 | 0.92 | 3.32 |

REWARDS-SPLIT counts KING drops (531 ETH over 365d) as rewards; LIQUID-LOOP leaves them in the residual.

**The dollar leg at T rates** (TOP5-RISK-LIQUIDITY): interest $14.1M a year on $181.1M; income $7.3M ($4.7M base yield: senRLUSDv2 2.80%, senPYUSDPRIMEv2 3.61%, stcUSD 5.64%, 30-day; $2.6M Merkl). Net **-$6.8M a year**, -1.44 pp of the $472.7M book. Over the last 90 days the measured dollar leg ran -0.63 pp a year before rewards and -0.26 pp after. The 25 Sep 2026 18M PYUSD tranche is negative after funding under every withdrawal convention tested (-5,360 to -4,584 PYUSD to T).

### D.5 Negative-carry periods

The Aave loop spread (weETH staking minus realized WETH borrow) was negative in 33 of 104 weeks: 25 in year one, 8 in year two. Episodes that cost ETH:

| Weeks ending | Weeks | Loop net | Worst weekly spread | Peak weekly borrow | Trigger |
|---|---:|---:|---:|---:|---|
| 4 Jul to 8 Aug 2025 | 6 | **-278 ETH** | -1.81 pp | 4.43% | Aave WETH spike (5.83% on 15 Jul 2025) |
| 21 to 28 Mar 2025 | 2 | -6 ETH | -0.49 pp | 3.04% | |
| 13 Feb to 13 Mar 2026 | 5 | -26 ETH | -1.10 pp | 3.58% | Aave WETH 5.48% in week of 6 Feb |
| 24 Apr to 8 May 2026 | 3 | **-577 ETH** | -2.76 pp | 5.36% | rsETH exploit, Aave WETH 8.35%, 99.2% utilization |

In months, the loop lost against unlevered in 8 of 25. The two spike months (Jul 2025 -421 ETH, Apr 2026 -437 ETH) cancel two thirds of the +1,304 ETH earned in the 17 positive months.

---

## E. Risk management

### E.1 Leverage and health factor over time (Aave, weekly; `loop_weekly.csv`)

| Week end | Collateral ETH | WETH debt | HF | Leverage | Share of Aave WETH debt |
|---|---:|---:|---:|---:|---:|
| 4 Oct 2024 | 94,919 | 78,719 | 1.145 | 5.9× | 7.0% |
| 4 Apr 2025 | 399,354 | 360,611 | 1.052 | 10.3× | 18.3% |
| 4 Jul 2025 | 661,899 | 591,001 | 1.064 | 9.3× | 25.1% |
| 2 Jan 2026 | 637,765 | 569,015 | 1.065 | 9.3× | 23.8% |
| 6 Feb 2026 | 592,837 | 550,225 | 1.024 | 13.9× | 18.5% |
| 1 May 2026 | 483,137 | 447,054 | 1.027 | 13.4× | 21.7% |
| 5 Jun 2026 | 304,218 | 263,469 | 1.097 | 7.5× | 16.7% |
| 2 Oct 2026 (T) | 443,412 | 410,134 | 1.027 | 13.3× | 23.3% |

- **Peak debt:** 591,295 WETH (11 Jul 2025), 26.9% of all Aave WETH debt.
- **The target band moved down.** Median HF after a releverage: 1.098 (2024), 1.064 (2025), 1.054 (H1 2026), 1.048 (from Jul 2026, minimum 1.023).
- **Dollar legs** are far safer: the weakest at T is Morpho weETH/RLUSD on the main vault, HF 1.268, liquidated by an ETH fall of 21%. Lowest month-end HF of the dollar legs: 1.23 (Jun 2026).

### E.2 Deleveraging episodes and reaction lag

323 Pool events in 130 transactions, 9 Oct 2024 to 18 Sep 2026; no liquidation.

| Threshold (Aave HF) | Episodes | Lag to restoring action | Cause |
|---|---|---|---|
| below 1.03 | 19 closed + 1 open at T | median 13.5 h, max 125.7 h (30 Apr to 6 May 2026) | 18 collateral withdrawals into redemption queues, 1 releverage borrow (19 Aug 2026) |
| below 1.02 | 12 (5 May to 16 Sep 2026) | 1.4 to 29.4 h | collateral withdrawals |
| below 1.015 | 9 (5 to 11 May 2026) | 1.4 to 12.9 h | collateral withdrawals |

- **Breaches are planned, not price-driven:** the vault queues weETH at ether.fi and repays when ETH arrives. Lowest HF 1.0108 (11 May 2026 17:59 UTC).
- **rsETH exploit, 18 Apr 2026:** the Aave WETH rate jumped at 19:28 UTC. The vault reacted 2 h 18 min later by queueing collateral (HF 1.0539 to 1.0248). First repay 93.6 h after the spike. Aave debt fell 51% from 3 Apr to 5 Jun.
- **Open at T:** below 1.03 since 18 Sep 2026 03:15 UTC (357 h), after a 4,000 weETH withdrawal.

### E.3 Liquidity ladder at T

**ETH loop** (block 26,108,081):

| Source | WETH | Note |
|---|---:|---|
| Vault idle | 20.6 WETH (+230 weETH, 91 eETH) | |
| weETH sold on Uniswap v3 and Curve at ≤0.5% | about 7,170 | 1.75% of Aave debt |
| wstETH/stETH venues at ≤0.5% | about 16,200 | 52% of Spark debt |
| ether.fi priority queue | all, in hours | median 4.6 h since 25 Apr 2026 |

To lift the Aave HF to 1.03 needs 14,960 WETH of repayment; to 1.05, 93,994; to 1.10, 199,374. Fluid, Balancer and aggregator routes were not quoted, so DEX depth is a lower bound.

**Dollar legs** ($181.08M):

| Tier | Amount | Share | Source |
|---|---:|---:|---|
| Same block, same currency | $64.82M | 35.8% | senRLUSDv2 55.10M (idle 42.03M + 42.12M deallocatable at 1 bp), 3.61M PYUSD, 6.11M of Cap's free USDC |
| Same block, with a PYUSD swap | $24.32M | 13.4% | PYUSD idle and deallocatable at a **1% penalty**; DEX depth not checked |
| Slower | $45.53M | 25.1% | 21.68M PYUSD locked in PRIME/PYUSD at 91.8% utilization; 18.52M cUSD waiting on Cap agents; 5.34M PRIME via Hastra in 1 to 2 business days |
| No claim found | $46.40M | 25.6% | debt with no dollar destination on Liquid's accounts |

### E.4 Stress at T

| Shock | Aave HF | Spark HF | Effect |
|---|---:|---:|---|
| None | 1.0271 | 1.0361 | loop earns +2,011 ETH a year (1.14 pp of NAV), +1,153 ETH over unlevered |
| WETH borrow +1 pp | unchanged now | | -2,401 ETH a year (-1.35 pp of NAV); break-even is +45.6 bp |
| weETH/stETH market depeg -3% | unchanged (exchange-rate oracle) | unchanged | mark-to-market -14,340 ETH, 38.9% of loop equity, 8.1% of NAV |
| Exchange-rate cut -3% | **0.9963, liquidatable** | 1.0051 | 1% liquidation bonus on seized collateral |
| ETH/USD -21% | | | Morpho weETH/RLUSD (main vault) reaches HF 1.0 |

The two risks are distinct: a weETH exchange-rate cut of 2.64% (slashing or loss socialisation at ether.fi) liquidates the loop that holds 2.7× NAV; a 21% ETH fall liquidates the weakest dollar leg.

---

## F. Depositors

### F.1 Size buckets at T (Ethereum shares only; `holder_buckets.csv`)

| Bucket | Addresses | % addresses | ETH | % ETH |
|---|---:|---:|---:|---:|
| under 1 ETH | 6,425 | 82.45 | 366 | 0.26 |
| 1 to 10 | 881 | 11.31 | 2,925 | 2.10 |
| 10 to 100 | 374 | 4.80 | 10,637 | 7.66 |
| 100 to 1k | 102 | 1.31 | 27,399 | 19.72 |
| over 1k | 11 | 0.14 | 97,623 | 70.26 |
| **Total** | **7,793** | | **138,949** | median 0.0025 ETH, HHI 1,230 |

- **Top 1:** 25.4% (EOA `0xc518…7b4b`, 35,319 ETH). **Top 2:** 47.3% (with EOA `0xf23c…a2ca`, 30,424 ETH). **Top 10:** 69.5%. **Top 100:** 89.0%.
- **Types in the top 10:** six plain EOAs, two EIP-7702 accounts, one Safe 2-of-2 (`0xf5c7…3089`, also a Lido Earn top-10 holder), and the 2024 migration contract "Ether.fi-Liquid1" (3.19%).
- **Optimism:** 34,533 shares (about 38,222 ETH, 21.6% of the book), 1,511 addresses; the ether.fi Cash hub there holds 7,012 positive account positions.

### F.2 Holders over time (Ethereum, month-end)

| Month end | Addresses | Holding ≥0.01 ETH | ETH | Top 10 |
|---|---:|---:|---:|---:|
| Jul 2024 | 3,352 | 3,197 | 167,198 | 78.6% |
| Aug 2025 | 4,957 | 4,394 | 203,045 | 55.8% |
| Oct 2025 | 9,710 | 4,439 | 177,464 | 59.4% |
| Feb 2026 | 8,988 | 4,040 | 108,292 | 36.5% |
| Jun 2026 | 8,135 | 3,369 | 61,867 | 33.5% |
| Aug 2026 | 7,934 | 3,248 | 141,143 | 68.2% |
| T | 7,793 | 3,151 | 138,949 | 69.5% |

The Oct 2025 jump (+5,389 addresses) is dust. Holders with at least 0.01 ETH fell from 4,606 (Oct 2024) to 3,151 (T).

### F.3 Who moved the book (Transfer replay)

| Wallet | Path (shares) |
|---|---|
| EOA `0xc518…7b4b` | in Jul 2024, 21,354 by Nov 2025; **all out Feb 2026**; back 21,341 in Mar; **all out Apr 2026**; back 31,910 in Aug 2026 (#1 at T) |
| EOA `0xee95…e39e` | in Oct 2024, 16,548 by Oct 2025; out Feb, back Mar, **out Apr 2026**; from Jun 2026 the largest holder of Lido Earn ETH (16,372 ETH at T) |
| EOA `0xf23c…a2ca` | first in Jul 2026; 27,488 by Aug (#2 at T) |
| EIP-7702 `0x49c5…f1f2` | +10,000 in Jul 2026 (#3 at T) |

- **Feb 2026:** the two wallets left with 37.9k shares; the Ethereum book fell from 158,839 to 108,403 ETH in the week ending 27 Feb.
- **Apr 2026:** they left again in the week of the rsETH exploit; the Ethereum book fell from 145,479 ETH (17 Apr) to 87,491 ETH (24 Apr).
- **Jul to Aug 2026:** 75,585 shares minted and 4,077 burned; `0xc518`, `0xf23c` and `0x49c5` took 69,398, which is 97% of the net. The dollar sleeve grew from $42.6M to $165.8M in the same two months.

## G. TVL growth

| Period | Book at end (both chains) | Rate effect | Share effect |
|---|---:|---:|---:|
| Sep 2024 to Sep 2026 | 146,909 to 176,962 ETH | +10,336 ETH | +19,717 ETH |

Ethereum alone, Jun 2024 to T: net share flows -69,229 ETH (part of it moved to Optimism), yield +11,174 ETH. Average monthly NAV peaked at 201,770 ETH (Aug 2025), bottomed at 98,432 ETH (Jun 2026).

Net Ethereum flows by period (ETH): Jul to Dec 2024 -46,661; H1 2025 +37,156; Jul to Dec 2025 -48,796; H1 2026 -87,192; Jul 2026 to T +76,264.

## H. Growth drivers (dated)

| Date | Event | Effect on book or yield |
|---|---|---|
| 11 Jun 2024 | first share mint; migration contract receives 191,654 shares | book 197,004 ETH at Jun 2024 end |
| 25 Jun 2024 | first Aave WETH loop | |
| Jan 2025 | fee 100 to 150 bp | year-one lag behind stETH begins |
| Jul 2025 | Aave WETH 5.83% (15 Jul); loop -421 ETH vs unlevered | share price falls 11 to 25 Jul |
| Aug 2025 | fee to 0; first dollar loan, $47M Aave USDC (repaid Oct) | lead +2.73 pp in Aug |
| Oct 2025 to 23 Jan 2026 | 3,410 KING in 16 weekly drops, $2.36M | +0.38 pp of 365d return |
| Feb 2026 | two whales exit; HF 1.024, Aave WETH 5.48% | Ethereum book -46k ETH |
| 24 Mar 2026 | Spark wstETH loop starts | |
| 18 Apr 2026 | rsETH exploit; WETH 8.35%; priority queue from 25 Apr | book -61k ETH in April; Aave debt -51% by 5 Jun |
| 23 Jun 2026 | Morpho RLUSD via the loan manager | |
| Jul to Aug 2026 | three wallets add 69k shares; Sentora RLUSD V2 deposits from 7 Aug; Merkl RLUSD/PYUSD received | dollar debt $42.6M to $165.8M |
| 25 Sep 2026 | 18M PYUSD against PRIME into Sentora PRIME Main | negative after funding to T |

Growth follows a few wallets and the loop's health, not the posted APY: the best yield months (Aug 2025 to Jan 2026, 4.7 to 5.7%) saw net Ethereum outflows of 50,707 ETH.

## I. Operator economics

| Item | Value |
|---|---|
| Management fee at T | 35 bp: about 620 ETH a year at T NAV (about $1.65M at $2,667, est.) |
| Fee charged, 2 years | 2,242 ETH by the accountant setting (0.72 pp a year); time-weighted average setting 0.686% |
| Fee claimed, 2 years | 2,130.6 ETH in 19 payments (121.7 weETH in 3, 1,996.4 WETH in 16) |
| Performance fee | none on Ethereum; Optimism Accountant stores one at 0 |
| Rewards received by the vault | KING $2.36M (Oct 2025 to Jan 2026), Merkl RLUSD $194k, PYUSD $167k, ETHFI $19k (365d) |
| Issuer-side incentive run-rate at T | $2.73M a year (0.58% of book) |

Sentora earns its own fees on the vaults Liquid parks in (RLUSD Main 10% performance, PRIME Main 15%, per the Kraken dive); on Liquid's claims that is about $0.5M a year at T yields (est.). Hastra's 50 bp applies to PRIME held. Cap's take on stcUSD was not measured.

## J. Verdict

**Copy:**
1. **Use the issuer's fast redemption queue as the deleverage path.** The priority queue (median 4.6 h) let Liquid cut its Aave WETH debt by 51% in nine weeks (3 Apr to 5 Jun 2026) with no liquidation.
2. **Publish the rate bounds.** ±0.5% per update and 6 hours between updates are on-chain and limit how far a strategist can move the price in one step.
3. **Size dollar legs at HF 1.27 to 1.46** while the ETH loop runs at 1.03; the dollar side survives a 21% ETH fall.

**Avoid:**
1. **A posted price with no mark.** The April 2026 loop loss never appeared in the price, so the wallets that left that week exited at a price that did not carry it.
2. **Claiming an edge that is the fee schedule.** More than half of the swing from a lag to a lead is a fee cut; the loop added 0.02 pp a year over two years.
3. **Borrowing dollars at 13.93% to park at 2.8 to 5.6%,** and borrowing from the market that your own deposit funds. Issuer rewards covered about 60% of the organic loss over 90 days and 28% at T rates.
4. **Running the loop at HF 1.027 with 1.75% of debt exitable in one block.** Every deleverage depends on a queue that pays in hours, and the 2.64% exchange-rate buffer is the whole margin.
5. **A book that a few wallets can cut by a third in a week.** Twice in 2026 (Feb, Apr) the Ethereum book fell 32% and 40% within seven days as two wallets left.

---

## Method, limits, reproducibility

**Scripts** (`tools/eth/top5/liquid/`):

| Script | What it does |
|---|---|
| `weekly_yield.py` | 105 Friday blocks from `loop_weekly.csv`: Accountant `getRate`, Ethereum `totalSupply`, wstETH `stEthPerToken`, weETH `getRate`; writes `yield_weekly.csv` |
| `monthly_yield.py` | same reads at the 25 month-end blocks of `pnl_monthly.csv`; writes `yield_monthly.csv` |

Loop, P&L and event files come from `raw/eth/gap-2026-10-07/liquid-loop/scripts/build.py`; holders from `raw/eth/gap-2026-10-07/keys-holders/scripts/`. Whale paths come from `raw/eth/gap-2026-10-07/keys-holders/logs/transfers_liquid.json` (85,302 Transfer logs). Accountant state was read with `accountantState()` at block 26,108,081. RPC: public Tenderly, drpc, mevblocker, Blast.

**Limits:**
- **The posted rate is not a NAV.** All share-price returns are the strategist's posted rate, 17.5 h old at T.
- **The residual (1.51 pp a year) is not decomposed.** It holds Uniswap and Fluid LPs, the Monad book, Pendle and other positions, KING (0.17 pp a year in the 2-year view), timing of the posted rate, and errors in the dollar-leg estimate.
- **Fee basis.** We assume the posted rate is net of the management fee. If it is gross, the residual falls to 2,468 ETH (0.79 pp a year).
- **Dollar leg history is estimated** from month-end debt, the T claim mix for 2026, and stcUSD for 2025.
- **Year split.** D.2 uses 12 and 13 calendar months; the weekly split in finding 1 uses 52 Fridays each. They agree within 0.02 pp.
- **Optimism holders** are counted, not bucketed; their flows are not traced.
- **Wallet identities** are unlabelled; "whale" means size, not a known entity.
- **Sentora and Cap fee take on Liquid's claims** is an estimate from vault fee settings, not a ledger.
