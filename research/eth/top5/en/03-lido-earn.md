# Lido Earn ETH: deep dive (yield history, risk, depositors, growth, economics)

*Scripts: [`tools/eth/top5/lido-earn/`](../../../../tools/eth/top5/lido-earn/), data: [`data/eth/top5/lido-earn/`](../../../../data/eth/top5/lido-earn/). Mentions of `raw/` refer to the working folder; raw dumps are not published.*

Earn ETH (Mellow Core vault [`0x6a37…249e`](https://etherscan.io/address/0x6a37725ca7f4ce81c004c955f7280d5c704a249e), share token earnETH [`0xBBFC…a0A4`](https://etherscan.io/address/0xBBFC8683C8fE8cF73777feDE7ab9574935fea0A4)), interface by Lido DAO contributors, curator Mellow. Almost all of it sits in stRATEGY (strETH, [`0x277c…ccc5`](https://etherscan.io/address/0x277c6a642564a91ff78b008022d65683cee5ccc5)), launched 6 Nov 2025. Count the outer book once.

**Date:** 7 Oct 2026. **Snapshot T:** 2 Oct 2026 23:59:59 UTC, Ethereum block 26,108,081. Windows: stRATEGY from 7 Nov 2025, Earn ETH from its first priced week (6 Mar 2026).

**Benchmark.** Every return is set against stETH (wstETH `stEthPerToken`) on the same blocks.

**Labels.** **(est.)** marks our estimates; everything else is read from chain or an API.

**Reuse.** Rewards from [REWARDS-SPLIT](../../en/REWARDS-SPLIT.md); dollar leg and ladder from [TOP5-RISK-LIQUIDITY](../../en/TOP5-RISK-LIQUIDITY.md); keys, fees, holders from [TOP5-KEYS-HOLDERS-TERMS](../../en/TOP5-KEYS-HOLDERS-TERMS.md); the April freeze from [CLOSED-CASES](../../en/CLOSED-CASES.md). New in this pass: weekly share prices of both layers, weekly health factors and collateral of the stRATEGY loop accounts, the redeem queue during the freeze, and the path of the DAO's first-loss shares.

**Files** in `data/eth/top5/lido-earn/`:
- `yield_weekly.csv` (new; 48 Friday blocks)
- `loops_weekly.csv` (new; loop accounts and the rsETH position)
- `keys.csv`, `fees.csv`, `events.csv`, `holder_buckets.csv`, `holders_monthly.csv`

---

## Key findings

1. **Earn ETH beats stETH, organically, but by less than a point.** From 6 Mar 2026 to T: 3.20% against 2.39% a year. Last 90 days: 3.14% against 2.25%, with no rewards in the price. Since the freeze ended (15 May to T): 3.40% against 2.31%, and no week below stETH in 20.
2. **The launch months were the high ones, and they are not explained.** stRATEGY paid 15.8% annualized in Nov 2025, 6.1% in December and 5.3% in January. The price stepped up 0.64% in the week to 7 Nov. Counted incentives on stRATEGY (Ethena $449k, Resolv $258k, sENA $22k) are about 0.57% of its book a year.
3. **The rsETH loop that froze the vault is still there.** Subvault [`0xcdfa…9c89`](https://etherscan.io/address/0xcdfa7efe670869c6b6be4375654e0b206ef49c89) holds 113,215.7 rsETH (122,412 ETH) against 112,310 WETH on Aave at T, health factor 1.035. Collateral has not moved since 22 May. It is 32% of the 355k WETH of loop debt and about 10.1k ETH of equity, 12% of the book.
4. **Aave has frozen rsETH.** At T the reserve has the frozen flag, base LTV 0 and base liquidation threshold 75%; the position lives in e-mode category 3 (rsETH and wstETH against ETH: LTV 93%, threshold 95%, bonus 1%). A 3.4% cut in rsETH's price, or rsETH leaving that e-mode, liquidates it (health factor about 0.82 at 75%).
5. **The rsETH loop was built in the three weeks before the exploit.** It grew from 28,686 rsETH (27 Mar) to 113,214 rsETH (17 Apr 2026), the day before the bridge exploit.
6. **Half the book asked to leave in three days.** 54,171 earnETH shares went into the redeem queue on 18 to 20 Apr from 343 addresses (largest 10.6%). With requests to 14 May, 56,342 shares (about 51% of the book) waited 27 days and were paid on 15 May.
7. **The first-loss capital arrived after the loss.** The DAO's 1,506.8 earnETH were minted on 8 May 2026, 20 days after the exploit. 143.98 were burned on 15 May. The other 1,362.8 moved on 25 Jun to a 5-of-9 Safe that holds nothing else of Earn ETH.
8. **stRATEGY took a -0.062% markdown in the week to 15 May; Earn ETH did not.** The outer price stayed flat from 24 Apr to 15 May, then the DAO burn covered the outer layer. stRATEGY holders outside Earn ETH took the mark.
9. **The ETH loops carry 4.2× the book in WETH debt at health factors 1.035 to 1.039.** Gross loop collateral is about 392k ETH against an 84.7k ETH stRATEGY book. The USDT account (HF 2.12) is the only conservative leg.
10. **No key has a delay.** A 5-of-8 Safe can upgrade all five core contracts and grant itself any role in one transaction. It paused deposits on 18 Apr this way. Fees went from 0 to 10% + 1% (1 Jul), back to 0 (21 Jul), then to 15% + 0.2% (3 Sep 2026).
11. **The fee costs about 0.6 pp a year at the current setting.** In September stRATEGY earned 3.72% and Earn ETH 3.12%. The 20 days at 10% + 1% in July minted 114.73 earnETH, about 2.6% of the book a year at that pace (est.).
12. **The USDT sleeve is small and positive.** $25.55M at 4.33% parked in earnUSD at 4.80% earns about +$120k a year (est.), about 0.05 pp of the book. Lido's carry account owns 48.5% of earnUSD, so its exit is earnUSD's own queue (about 24 h).

---

## A. Scope and snapshot

| Item | Value at T | Source |
|---|---|---|
| Earn ETH book | 83,309 ETH ($222M), price 1.018484 ETH per share | oracle `getReport(WETH)`, `totalShares` |
| stRATEGY book | 84,664 ETH, price 1.049305 | stRATEGY oracle `getReport(ETH)` |
| Earn ETH's stake in stRATEGY | 79,267 strETH shares (main subvault) | |
| Holders | 2,500 earnETH addresses; 788.3 allocated but unclaimed shares outside the token supply | Transfer replay |
| Oracle age | about 17 h at T | |

## B. Structure and legs (at T)

| Account (stRATEGY subvault) | Venue | Collateral to debt | Debt | HF |
|---|---|---|---|---|
| `0x893a…0080` | Aave Core | wstETH to WETH | 80,273 WETH | 1.0376 |
| [`0x3883…e4d7`](https://etherscan.io/address/0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7) | Spark | wstETH to WETH | 162,635 WETH | 1.0390 |
| [`0xcdfa…9c89`](https://etherscan.io/address/0xcdfa7efe670869c6b6be4375654e0b206ef49c89) | Aave Core | **rsETH** to WETH | 112,310 WETH | 1.0355 |
| [`0x181c…a76d`](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | Aave, Spark | wstETH to USDT, into earnUSD | $22.24M + $3.31M | 2.124 / 2.488 |
| `0x9938…1da0` | Aave Core | USDe/sUSDe to USDC (Nov 2025 to Mar 2026) | closed; 2.6k USDe left | |

Loop collateral at T: 87,652 + 181,704 + 122,378 = 391,734 ETH, 4.6× the stRATEGY book. Fees inside stRATEGY and earnUSD are 0 at T.

## C. Governance and security

| Who | Power | Delay |
|---|---|---|
| Proxy Admin Safe 5-of-8 [`0x8169…0af0`](https://etherscan.io/address/0x81698f87c6482bf1ce9bfcfc0f103c4a0adf0af0) | upgrade Vault, ShareManager, FeeManager, Oracle, RiskManager; owns the stRATEGY and subvault proxies | none |
| Lazy Vault Admin Safe 5-of-8 [`0x0dd7…076e`](https://etherscan.io/address/0x0dd73341d6158a72b4d224541f1094188f57076e) | grant any role to itself and use it in the same transaction; owner of FeeManager | none |
| Active Vault Admin Safe 3-of-8 | deposit limits, subvault limits, allowed assets | none |
| Curator Safe 3-of-6 (docs say 3/5) | move assets between the vault and subvaults | none |
| Oracle Updater Safe 3-of-8 | post prices; the 5-of-8 accepts reports outside bounds | redeem settles at the first report ≥24 h after request |
| Pause timelock (`getMinDelay` 0) | 16 pre-scheduled pause calls; executors Lido Pauser 3-of-5 and **Mellow Pauser 1-of-8** | 0 s |
| stRATEGY Curator Safe 5-of-8 | all stRATEGY settings | none |

- **Used without delay:** the Lazy Admin took a role and used it in the same transaction on 3 Mar, 18 Apr (paused all six deposit queues), 7 Jul and 23 Jul 2026. It also took the oracle submit role for one transaction on 15 May (the recovery report).
- **Upgrade used:** the ShareManager became burnable on 2 Mar 2026; that is the function the DAO cover used on 15 May.
- **Oracle bounds:** maximum deviation 0.5%, suspicious 0.1%, timeout 20 h, redeem interval 24 h.
- **Exit terms:** request, then claim, in wstETH. Requests cannot be cancelled. Typical settlement about 3 days. Interface terms: Cayman law, LCIA arbitration, US and UK persons excluded.

---

## D. Yield history

### D.1 Month by month against stETH

stRATEGY APY from month-end oracle reports; Earn ETH APY and the split (ETH) from `rewards_split.csv`. "Fees, timing" is Earn's return minus stRATEGY's, less the DAO cover.

| Month | stRATEGY APY | Earn ETH APY | stETH APY | Earn lead, pp | Staking | Loops | USDT leg | Rewards and cover | Fees, timing | Residual |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-11 | 15.84% | | 2.69% | | | | | | | |
| 2025-12 | 6.06% | | 2.58% | | | | | | | |
| 2026-01 | 5.34% | | 2.48% | | | | | | | |
| 2026-02 | 3.01% | | 2.50% | | | | | | | |
| 2026-03 | 4.24% | 4.50% | 2.53% | +1.96 | 92 | 24 | -7 | 26 | 9 | 18 |
| 2026-04 | 1.82% | 2.17% | 2.52% | -0.35 | 202 | -186 | 32 | 37 | 28 | 61 |
| 2026-05 | 1.15% | 1.65% | 2.48% | -0.84 | 162 | 93 | 44 | 154 | -113 | -233 |
| 2026-06 | 4.50% | 4.25% | 2.45% | +1.80 | 134 | 75 | 28 | 0 | -14 | 7 |
| 2026-07 | 3.35% | 3.33% | 2.24% | +1.09 | 162 | 51 | 28 | 0 | -1 | 1 |
| 2026-08 | 3.10% | 3.09% | 2.23% | +0.86 | 147 | 33 | 28 | 0 | 0 | -4 |
| 2026-09 | 3.72% | 3.12% | 2.27% | +0.85 | 150 | 79 | 0 | 0 | -39 | 15 |
| 1 to 2 Oct 2026 | 2.53% | 2.00% | 2.24% | -0.24 | 10 | 0 | 1 | 0 | -2 | 0 |

- **Nov 2025** includes the launch week: the stRATEGY price went from 1.006240 (31 Oct) to 1.012708 (7 Nov), +0.64% in a week.
- **May 2026:** the DAO cover (+145 ETH) offsets the residual (-233 ETH). Without rewards the month was -0.71% annualized.
- **Since June** the split is clean (annualized on average equity): staking 2.2 to 2.4 pp, loops 0.5 to 1.4 pp, USDT leg 0 to 0.5 pp, residual near 0.

### D.2 Periods

| Period | stRATEGY | Earn ETH | stETH |
|---|---:|---:|---:|
| 7 Nov 2025 to 30 Jan 2026 (launch, Ethena and Resolv incentives) | 6.71% | | 2.58% |
| 30 Jan to 17 Apr 2026 (rsETH loop built) | 3.54% | | 2.49% |
| 17 Apr to 15 May 2026 (freeze) | -0.68% | 0.12% | 2.60% |
| 15 May to 2 Oct 2026 | 3.65% | 3.40% | 2.31% |
| 6 Mar to 2 Oct 2026 (Earn ETH priced) | 3.09% | 3.20% | 2.39% |
| 7 Nov 2025 to T | 4.02% | | 2.45% |

Since 28 Feb, REWARDS-SPLIT gives Earn ETH 3.14% actual, 2.63% without rewards and cover, against 2.39%: rewards and cover are 67% of the lead. Over the last 90 days the lead is all organic.

### D.3 Weekly (`yield_weekly.csv`)

| Series | Weeks | Mean | Std dev | Worst week | Best week | Weeks below stETH | Weeks at or below 0 |
|---|---:|---:|---:|---|---|---:|---:|
| stRATEGY, from 14 Nov 2025 | 47 | 4.04% | 2.31 pp | -3.16% (15 May 2026) | 10.63% (14 Nov 2025) | 5 | 3 |
| Earn ETH, from 13 Mar 2026 | 30 | 3.21% | 1.46 pp | 0.00% (1, 8, 15 May) | 5.82% (13 Mar) | 4 | 3 |
| Earn ETH, from 22 May 2026 | 20 | 3.40% | 0.65 pp | | | 0 | 0 |

- **The freeze in prices:** both prices stood still from 24 Apr to 8 May. In the week to 15 May stRATEGY fell from 1.035625 to 1.034987 (-0.062%); Earn ETH stayed at 1.005515.
- **The lowest week before the freeze** was stRATEGY 1.28% (20 Feb 2026), the week the Aave wstETH loop hit HF 1.0195.

### D.4 Carry P&L by leg (Earn ETH; pp of start capital, REWARDS-SPLIT)

| Window | Staking | ETH loops | USDT / USDe leg | Rewards and cover | Fees, timing | Residual | Return |
|---|---:|---:|---:|---:|---:|---:|---:|
| 28 Feb to T (216 days) | 1.409 | 0.300 | 0.187 | 0.297 | -0.170 | -0.175 | 1.848 |
| 90d to T, annualized | 2.23 | 0.80 | 0.26 | 0 | -0.24 | 0.07 | 3.14 |

Rewards since 28 Feb: DAO cover 0.188 pp, Ethena aEthUSDe 0.093, sENA 0.012, aEthrsETH 0.004.

**The USDT sleeve at T:** $25.55M at 4.33% against earnUSD's 30-day 4.80%. A 5M USDT loan into earnUSD on 29 Sep earned +1,401 USDT net by 2 Oct.

### D.5 Negative-carry periods

- **April 2026:** the loops lost 186 ETH in the month (Aave WETH 5.00% on 24 Apr, 8.35% at the peak) and the Earn lead was -0.35 pp.
- **May 2026:** the lead was -0.84 pp even with the cover.
- **Weeks below stETH:** stRATEGY 5 of 47, Earn ETH 4 of 30, all inside 20 Feb to 15 May 2026.

---

## E. Risk management

### E.1 Loop accounts over time (`loops_weekly.csv`, Friday blocks)

| Week end | wstETH loop, Aave: WETH debt / HF | wstETH loop, Spark | rsETH loop, Aave: rsETH / WETH debt / HF | Total loop WETH | Earn ETH book |
|---|---|---|---|---:|---:|
| 12 Dec 2025 | 56,461 / 1.035 | 16,923 / 1.066 | none | 73,384 | (stRATEGY 33,799) |
| 30 Jan 2026 | 75,978 / 1.058 | 45,129 / 1.041 | 28,686 / 28,016 / 1.034 | 149,123 | (stRATEGY 42,108) |
| 20 Feb 2026 | 77,086 / **1.0195** | 48,475 / 1.032 | 28,686 / 28,064 / 1.034 | | |
| 17 Apr 2026 | 141,889 / 1.122 | 28,799 / 1.088 | **113,214 / 111,073** / 1.035 | 281,967 | 110,126 |
| 15 May 2026 | 60,747 / 1.092 | 27,777 / 1.130 | 113,214 / 111,411 / 1.034 | 199,882 | 53,776 |
| 3 Jul 2026 | 167,347 / 1.061 | 77,629 / 1.037 | 113,216 / 111,727 / 1.034 | 356,723 | 91,835 |
| 11 Sep 2026 | 98,833 / 1.122 | 129,164 / **1.0229** | 113,216 / 112,177 / 1.035 | | 79,902 |
| 2 Oct 2026 (T) | 80,251 / 1.038 | 162,635 / 1.039 | 113,216 / 112,310 / 1.035 | 355,164 | 83,309 |

ETH figures for debt use Aave's USD values at Chainlink ETH/USD; the rsETH columns are token balances.

- **Lowest weekly HF:** Aave wstETH loop 1.0195 (20 Feb 2026); Spark 1.0229 (11 Sep 2026); rsETH loop 1.033 (8 May 2026). Weeks below 1.03: one, two and none.
- **The rsETH loop since 22 May:** collateral fixed at 113,215.7 rsETH; debt up from 111,455 to 112,310 WETH (2.10% a year); rsETH price up 2.33% a year. Equity gained +176 ETH in 19 weeks.
- **Dollar account in the freeze:** its Spark debt peaked near $90.8M (24 Apr, HF 1.41) in the week the Aave wstETH loop fell from 141,889 to 81,923 WETH. That suggests dollars were borrowed to help unwind (inference; flows not traced). By May end the dollar debt was $12.5M.

### E.2 The April 2026 freeze

| UTC | Event |
|---|---|
| 27 Mar to 17 Apr | rsETH loop grows from 28,686 to 113,214 rsETH |
| 18 Apr 17:35 | rsETH bridge exploit; Lido detects it at 18:53 |
| 18 Apr 20:29 to 20:33 | UI deposits off; Lazy Admin pauses the six deposit queues |
| 18 to 20 Apr | 54,171 shares requested for redemption by 343 addresses |
| 8 May 08:18 | DAO first-loss shares minted: 1,506.8 earnETH |
| 15 May 16:00 | DAO burns 143.98 earnETH (144.77 ETH); queues resume; 56,371 escrowed shares settled that day |
| 25 Jun 17:56 | remaining 1,362.8 DAO shares move to Safe 5-of-9 `0xf6f0…1e96` |

- **Loss:** 143.98 ETH, about 0.13% of the book, from WETH borrow cost during the freeze and slow unwinds, not from rsETH principal (Lido review).
- **Depositors:** 0% loss in Earn ETH; 27 days without an exit.
- **After reopening:** the Earn ETH book went from 110,594 ETH (8 May) to 53,776 ETH (15 May) and 44,686 ETH (12 Jun).
- **Reaction:** the price stood still for three weeks; no loop was liquidated; the rsETH position was never unwound.

### E.3 Liquidity ladder at T

| Leg | Debt | Same block | About 1 day | Slower |
|---|---:|---|---|---|
| USDT account | $25.55M | 0 | 100% via earnUSD's redeem queue (claim $25.57M) | |
| wstETH loops | 242,908 WETH | DEX depth for wstETH/stETH about 16,200 ETH at ≤0.5% (shared with every other seller) | | Lido withdrawal queue, days |
| rsETH loop | 112,310 WETH | not measured | | Kelp withdrawals; reserve frozen on Aave |

The depositor's exit sits behind the strategist's: a redemption settles at the next oracle report at least 24 h after the request, and the vault can be paused by one signer of the Mellow Pauser Safe.

### E.4 Stress at T

| Shock | Effect |
|---|---|
| rsETH price cut 3.4% | rsETH loop HF reaches 1.0; equity 10.1k ETH at risk |
| rsETH moved out of e-mode (threshold 95% to 75%) | HF about 0.82: liquidatable at once |
| wstETH exchange-rate cut 3.6 to 3.8% | both wstETH loops reach HF 1.0 |
| WETH borrow +1 pp on 355k WETH | about -3,550 ETH a year, -4.2 pp of the book (est.) |
| ETH/USD -53% | USDT account (HF 2.12) liquidatable |
| Market depeg of wstETH or rsETH | no HF change (exchange-rate oracles); exit cost only |

The WETH rate is the operative risk. Over 90 days the loops added +0.80 pp a year on 4.2× the book in debt, about 0.2 pp of spread per unit of debt, so a WETH rate about 0.2 pp higher erases their contribution (est.).

---

## F. Depositors

### F.1 Size buckets at T (`holder_buckets.csv`)

| Bucket | Addresses | % addresses | ETH | % ETH |
|---|---:|---:|---:|---:|
| under 1 ETH | 1,353 | 54.12 | 229 | 0.28 |
| 1 to 10 | 665 | 26.60 | 2,231 | 2.70 |
| 10 to 100 | 366 | 14.64 | 11,759 | 14.25 |
| 100 to 1k | 106 | 4.24 | 28,954 | 35.09 |
| over 1k | 10 | 0.40 | 39,333 | 47.67 |
| **Total** | **2,500** | | **82,506** | median 0.66 ETH, HHI 563 |

- **Top 1:** 19.84%, EOA [`0xee95…e39e`](https://etherscan.io/address/0xee9535a8a408e13acc8b65cf4163257af240e39e) (16,372 ETH). It held up to 16.5k Liquid ETH shares from Oct 2024, left Liquid in April 2026 and entered Earn ETH in June.
- **Top 2:** 10.15%, EOA `0x97fe…9e9d`, entered in Aug 2026.
- **Safes in the top 10:** 2-of-2 `0xf5c7…3089` (also a Liquid top-10 holder), 2-of-2 `0xaf3f…b9ef`, and 5-of-9 `0xf6f0…1e96` (the moved DAO first-loss shares, 1,388 ETH).
- **Top 10:** 47.7%. **Top 100:** 80.8%.

### F.2 Holders over time (month-end)

| Month end | Addresses | Holding ≥0.01 ETH | ETH | Net flow | Yield |
|---|---:|---:|---:|---:|---:|
| Mar 2026 | 1,195 | 1,136 | 77,576 | (migration) | |
| Apr 2026 | 1,199 | 1,108 | 107,422 | +29,710 | +137 |
| May 2026 | 1,118 | 1,015 | 42,805 | -64,766 | +149 |
| Jun 2026 | 1,527 | 1,400 | 89,320 | +46,368 | +147 |
| Jul 2026 | 2,389 | 1,802 | 76,658 | -12,911 | +249 |
| Aug 2026 | 2,429 | 1,838 | 78,178 | +1,321 | +199 |
| Sep 2026 | 2,500 | 1,895 | 82,241 | +3,865 | +198 |
| T | 2,500 | 1,895 | 82,506 | +257 | +9 |

The April "top 1" of 52.6% in the source file is the redeem escrow, not a holder.

- **June inflow:** `0xee95` brought 30,886 shares and took 20,886 back out in July.
- **Run shape:** April's exit came from 343 addresses with no wallet above 10.6%, unlike Liquid, where two wallets moved the book.

## G. TVL growth

| Stage | Book |
|---|---|
| stRATEGY, 7 Nov 2025 to 30 Jan 2026 | 2,812 to 42,108 ETH |
| Earn ETH launch and 13 Mar migration (8,703 strETH, 3,280 GG, 2,884 DVstETH, 1,404 wstETH) | 17,408 ETH (13 Mar) to 101,549 ETH (3 Apr) |
| Peak | 110,594 ETH (24 Apr to 8 May, frozen) |
| Low | 44,686 ETH (12 Jun) |
| T | 83,309 ETH |

From Mar 2026 month-end to T: net flows +3,844 ETH, yield +1,087 ETH. The book is where it was before the freeze; the holder count has doubled.

## H. Growth drivers (dated)

| Date | Event | Effect |
|---|---|---|
| 6 Nov 2025 | stRATEGY launches (Aave, Ethena, Uniswap routes) | 15.8% annualized in Nov |
| Nov 2025 to Apr 2026 | Ethena aEthUSDe ($449k) and sENA ($22k) on the USDe loop; Resolv wstUSR ($258k, Dec to Feb) | launch-phase yield |
| 23 Jan 2026 | rsETH loop opened (28,686 rsETH) | |
| 2 Feb 2026 | Earn ETH contracts deployed, fees 0 | |
| 19 Feb 2026 | DAO proposes first-loss allocation ($3M wstETH for Earn ETH) | shares not minted until 8 May |
| 13 Mar 2026 | bulk migration from strETH, GG, DVstETH | 1,195 holders, 77,576 ETH by 31 Mar |
| 27 Mar to 17 Apr 2026 | rsETH loop quadrupled | |
| 18 Apr 2026 | exploit; deposits paused | 27-day freeze; book -51% after |
| 15 May 2026 | DAO burns 143.98 earnETH; queues resume | |
| Jun 2026 | `0xee95` arrives from Liquid | book 44.7k to 91.8k ETH by 3 Jul |
| 1 to 21 Jul 2026 | fees 10% + 1% | 114.73 earnETH to the Treasury |
| 3 Sep 2026 | fees 15% + 0.2% | Earn trails stRATEGY by 0.6 pp |
| 29 Sep 2026 | 5M USDT into earnUSD | +1,401 USDT by 2 Oct |

## I. Operator economics

| Item | Value |
|---|---|
| Fee setting at T | 15% of performance above high-water mark + 0.2% a year; deposit and redeem 0; stRATEGY and earnUSD 0 |
| Fee shares minted to Treasury Safe 4-of-6 | 154.28 earnETH (about 157 ETH): July 114.73, September 37.33, 1 to 2 Oct 2.22 |
| Run-rate at T (Sep pace) | about 490 shares a year, about 500 ETH ($1.33M), 0.6% of the book (est.) |
| DAO cost | 144.77 ETH first-loss burn; separately 2,500 stETH to DeFi United |
| Counted incentives on stRATEGY (365d) | Ethena $449k, Resolv $258k, sENA $22k; none live at T |

The fee goes to Lido's Treasury Safe; how it splits with Mellow is not on-chain.

## J. Verdict

**Copy:**
1. **First-loss capital that burns shares.** One transaction moved the loss off depositors; no holder lost principal.
2. **A clean, organic split since June:** staking, loops, one small dollar sleeve, residual near zero. It is easy to audit by leg.
3. **A conservative dollar leg (HF 2.1 to 2.5)** next to the loops, parked in a vault with no Merkl subsidy.

**Avoid:**
1. **A reserve that arrives after the event.** Approved in February, minted on 8 May, three weeks into the freeze; then moved to another Safe in June.
2. **Keeping the position that caused the freeze.** 113,216 rsETH on a frozen reserve, at HF 1.035, five months on. Its exit depends on Aave keeping rsETH in e-mode.
3. **Building a concentrated loop days before a stress.** The rsETH loop quadrupled in the 21 days before the exploit.
4. **Admin power with no delay,** including upgrades of every core contract and fee changes three times in two months.
5. **An exit that can close for 27 days.** First-loss kept depositors whole and still lost half the book.

---

## Method, limits, reproducibility

**Scripts** (`tools/eth/top5/lido-earn/`):

| Script | What it does |
|---|---|
| `weekly_yield.py` | 48 Friday blocks (7 Nov 2025 to T) from `data/eth/top5/liquid/loop_weekly.csv`: both oracles' `getReport`, `totalShares` of both layers, `getUserAccountData` of four subvaults on Aave Core and Spark, rsETH aToken and WETH debt balances of `0xcdfa`, rsETH and wstETH rates, Chainlink ETH/USD, WETH borrow rates. Writes `yield_weekly.csv` and `loops_weekly.csv` |

Other inputs: `raw/eth/gap-2026-10-07/rewards-split/bs_decoded.json` (month-end oracle reports and subvault balances), `raw/eth/gap-2026-10-07/keys-holders/logs/transfers_lido_earnETH.json` (9,173 Transfer logs; redeem escrow and DAO share paths). The rsETH reserve flags come from `getConfiguration(rsETH)` on Aave Core at block 26,108,081. RPC: drpc, mevblocker, Blast, public Tenderly.

**Limits:**
- **Launch yield not explained.** The Nov 2025 step (+0.64% in a week) and the Nov to Jan lead are not split by leg; REWARDS-SPLIT starts at 28 Feb.
- **e-mode terms** were read at T (`getUserEMode` = 3, `getEModeCategoryCollateralConfig(3)`); whether Aave governance plans to change category 3 was not checked.
- **Prices are oracle reports**, about 17 h old at T, not an exit NAV.
- **The DAO's first-loss status after 25 Jun** cannot be read on-chain; the Safe `0xf6f0` is unlabelled and the reserve balance is not published.
- **USDT leg history before April** is from month-end reads; part of the Nov 2025 to Mar 2026 dollar debt was a USDe/sUSDe loop, not ETH-backed carry.
- **Exit depth for rsETH and the Lido withdrawal queue timing were not measured.**
- **Weekly ETH figures for debt** convert Aave USD values at Chainlink ETH/USD and differ from token units by up to 0.1%.
