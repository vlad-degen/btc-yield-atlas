# Liquity ETH Carry (IPOR Fusion): deep dive (yield history, risk, depositors, growth, economics)

*Data: [`data/eth/top5/liquity/`](../../../../data/eth/top5/liquity/) (`weekly.csv` and `march_daily.csv` are new in this pass; `keys.csv`, `fees.csv`, `events.csv`, `holder_buckets.csv`, `holders_monthly.csv` from the 7 Oct pull). Scripts: [`tools/eth/top5/liquity/`](../../../../tools/eth/top5/liquity/). Russian version: [../05-liquity.md](../05-liquity.md).*

**Snapshot T:** 2 Oct 2026 23:59:59 UTC, Ethereum block 26,108,081. Benchmark: stETH (wstETH `stEthPerToken`) over the same blocks. Vault: IPOR Fusion PlasmaVault `0xb9e806e8…663c` (on-chain name "rETH Liquity LP Carry", WETH-denominated, 20-decimal shares), deployed 30 Jan 2026. Curator: Safe 2-of-3 `0x32787cd5…6543`; the curator brand on the interface (Sentinel, per the brief) is not provable on-chain.

---

## Key findings

1. **The name says Liquity; the loan is Ebisu.** The live trove is on Ebisu (a Liquity v2 fork), wstETH branch: 4,585.5 wstETH against 6.75M ebUSD at a 2.55% rate the vault sets itself. The dollars sit in ebUSD/USDC on Curve and Uniswap v4; the BOLD exposure is in the reward and LP side.
2. **Without rewards the vault equals stETH.** 90 days: 3.84% a year actual, 2.26% without rewards, stETH 2.25%. Rewards are 99% of the lead.
3. **The reward is ten times the site's "about $15k a year".** BOLD from the Curve BOLD/USDC gauge runs at $153k a year (0.95% of TVL); the Merkl BOLD campaign on Uniswap v4 is $2.6k a year and ends 8 Oct.
4. **The measured legs lose money; an unexplained residual carries the rest.** 90 days annualized: staking +1.96 pp, dollar leg −2.03 pp, fees −0.98 pp (est.), rewards +1.54 pp, residual +3.28 pp. Staking, dollar leg and fees alone give −1.0% a year.
5. **The share price has never been back to 1.0.** The whitelist phase lost 6.0% in March (1.0 to 0.940) on 1.4 to 32 ETH of test capital, mostly around trove opens and closes. It is 0.973 at T, sitting on the performance-fee high-water mark (0.973052).
6. **Since public opening the vault paid 5.36% a year.** From 22 May (first week after opening) to T: +1.95% against stETH +0.83% (2.29% a year). The 7.06% since 31 Mar is inflated by a +2.15% month (May) on about 280 ETH.
7. **Trove churn costs show up as down weeks.** The week a new trove opened (6 Jun) was −0.89%; trove churn in March cost −2.7% to −2.8% in single days, and −0.5% and −1.2% in two April weeks. Since 24 Jul no week has been negative.
8. **The borrow rate moved from 0.88% to 6.35% and back to 2.55%.** Month-end quotes: 0.88% (Apr, May), 3.27%, 5.55%, 6.35% (Aug), 2.55% (Sep, T). A low self-set rate puts the trove early in Ebisu's redemption order.
9. **Repayment is easy; depositor exit is not.** 97.5% of the debt can be bought back on Curve in one block, but at T a 10% or 30% holder withdrawal reverts; only the 1% test goes through.
10. **One Safe with zero delays runs it.** Owner, guardian, atomist and fuse manager are the same 2-of-3 Safe; every role has a 0-second execution delay. Fees went from 2% / 0.3% to 10% / 0.5% on 28 May, plus 0.2% on deposit, withdrawal and request since 19 May.
11. **Two holders explain September's doubling.** A 3-of-6 Safe (36.9%, entered 25 Aug, borrows WETH on Morpho to deposit) and Rocksolid's execution account (12.1%, entered 23 Sep; Rocksolid went into Closing on 29 Sep). The book went from 2,814 to 6,017 ETH in September.

---

## A. Scope and snapshot

| Item | Value at T | Source |
|---|---|---|
| Book | 6,014.0 ETH ($16.05M) | `totalAssets`; 0.973079 WETH per share |
| Trove | 4,585.48 wstETH, 6,752,065 ebUSD, rate 2.55%, LTV 44.3%, liquidation LTV 83.3% (MCR 120%), HF-equivalent 1.88 | trove getters, branch `lastGoodPrice` |
| ETH move to liquidation | −47% | |
| Dollar side | Curve ebUSD/USDC LP (vault owns 65.6%; one-coin exit 6.58M ebUSD), Uniswap v4 book 0.16M, idle 300.7 WETH | [TOP5-RISK-LIQUIDITY](../../en/TOP5-RISK-LIQUIDITY.md) |
| Stored market books | market 29: 3,265.35 ETH; market 53: 59.73 ETH (keeper-stored, not re-marked) | [CARRY-PRODUCTS](../../en/CARRY-PRODUCTS.md) |
| Holders | 130 | Transfer replay |
| Return | 90d 3.84% (2.26% without rewards); since 31 Mar 7.06% (5.34%); stETH 2.25% / 2.36% | `rewards_split.csv` |

## B. Structure and legs

| Leg | Collateral | Debt | Destination | Rate at T |
|---|---|---|---|---|
| Ebisu wstETH trove `0x17fde209` (since 6 Jun) | 4,585.5 wstETH (about 95% of the book) | 6.75M ebUSD | Curve ebUSD/USDC LP, Uniswap v4 | 2.55% borrower-set; pool fees 0.45% (30d) |
| Reward side | Curve BOLD/USDC gauge `0x07a01471`; Merkl BOLD on Uniswap v4 BOLD/USDC | | BOLD to the vault | |

Earlier troves: rETH branch 5 to 9 Mar; wstETH `0xcc51` (Mar) and `0xa7f1` (Apr to May). Nine opens and closes in total.

## C. Positions (month-end)

| Month | wstETH | Collateral $M | Debt $M | LTV | HF | Borrow | Curve ebUSD/USDC fees |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mar | 6.3 | 0.02 | 0.01 | 39.1% | 2.13 | 1.41% | 0.56% |
| Apr | 25.6 | 0.07 | 0.04 | 53.1% | 1.57 | 0.88% | 0.60% |
| May | 377.8 | 0.94 | 0.41 | 43.6% | 1.91 | 0.88% | 0.45% |
| Jun | 427.3 | 0.83 | 0.47 | 55.9% | **1.49** | 3.27% | 0.91% |
| Jul | 1,029.2 | 2.39 | 1.22 | 50.9% | 1.64 | 5.55% | 0.49% |
| Aug | 1,979.9 | 6.11 | 3.28 | 53.7% | 1.55 | **6.35%** | 0.50% |
| Sep | 4,586.7 | 15.33 | 6.75 | 44.0% | 1.89 | 2.55% | 0.43% |
| T | 4,585.5 | 15.23 | 6.75 | 44.3% | 1.88 | 2.55% | 0.45% (30d) |

The dollar side never paid for its loan at any month-end: pool fees 0.43% to 0.91% against 0.88% to 6.35%.

## D. Governance and security

| Role | Holder | Can do | Delay |
|---|---|---|---|
| Owner, guardian, atomist, fuse manager, oracle, withdraw config | Safe 2-of-3 `0x32787cd5` (no modules, no guard) | grant roles, set fees, cap, oracle, withdraw window; choose which protocols the strategist may touch; close the vault | 0 s on every role |
| Strategist (ALPHA) | PlasmaVaultWrapper `0x8ff4d4a1`; EOA `0xad34f0fe` (since 28 Jul) | execute inside granted fuses; release withdrawals | 0 s |
| IPOR DAO | Safe 4-of-6 `0xf6a9bd8f` | DAO fee recipient; 2% / 0.3% is a constant | 0 s |
| ADMIN_ROLE | nobody (revoked at init) | | |
| Implementation | EIP-1167 clone, immutable | | |

Findings:
- Control sat with one EIP-7702 EOA (`0x81fa729b`, also the first depositor) until 6 to 11 Jun, then moved to the Safe.
- The guardian closed the vault for 15 minutes on 26 May (all user functions blocked).
- The fuse manager can add protocols and substrates with no delay, so the strategy can change completely before a depositor can exit.

---

## E. Yield history

**Method.** Vault `convertToAssets(1e20)` (WETH per share). Splits from [REWARDS-SPLIT](../../en/REWARDS-SPLIT.md): a = wstETH staking on trove collateral; c = Curve ebUSD/USDC virtual-price growth on a claim set equal to the debt, minus trove interest; d = BOLD from the Curve gauge and Merkl; e = fees estimated at 0.5% a year plus 10% of gains; f = residual. Weekly reads every 7 days back from T; March daily reads (`march_daily.csv`).

### E.1 Monthly

| Month | Avg book ETH | APY | Without rewards | stETH | Excess (pp, not annualized) | Rewards share of excess |
|---|---:|---:|---:|---:|---:|---:|
| Apr | 32 | −0.74% | −2.95% | 2.52% | −0.27 | |
| May | 280 | 28.41% | 28.01% | 2.48% | +1.94 | 1% |
| Jun | 585 | 4.58% | 1.86% | 2.45% | +0.17 | 128% |
| Jul | 1,034 | 1.17% | −0.22% | 2.24% | −0.09 | |
| Aug | 2,158 | 5.05% | 3.05% | 2.23% | +0.23 | 71% |
| Sep | 4,415 | 5.78% | 4.34% | 2.27% | +0.28 | 41% |
| 1 to 2 Oct | 6,015 | 8.56% | 7.56% | 2.24% | +0.03 | 16% |
| **90d to T** | 2,676 | **3.84%** | **2.26%** | 2.25% | +0.38 | **99%** |
| **Since 31 Mar** | 1,463 | **7.06%** | 5.34% | 2.36% | +2.32 | 36% |

### E.2 Weekly since deposits opened (`weekly.csv`)

| Week to | Week | APY | stETH APY | Book ETH |
|---|---:|---:|---:|---:|
| 22 May | +1.398% | +72.9% | 2.39% | 290 |
| 29 May | +0.408% | +21.3% | 2.39% | 502 |
| 5 Jun | +0.335% | +17.5% | 2.48% | 597 |
| **12 Jun** | **−0.894%** | **−46.6%** | 2.55% | 664 |
| 19 Jun | +1.080% | +56.3% | 2.36% | 541 |
| 26 Jun | +0.327% | +17.0% | 2.37% | 626 |
| 3 Jul | −0.264% | −13.8% | 2.29% | 677 |
| 10 Jul | +0.113% | +5.9% | 2.23% | 765 |
| 17 Jul | −0.232% | −12.1% | 2.20% | 848 |
| 24 Jul | +0.089% | +4.6% | 2.19% | 1,382 |
| 31 Jul | +0.059% | +3.1% | 2.20% | 1,502 |
| 7 Aug | +0.115% | +6.0% | 2.19% | 1,506 |
| 14 Aug | +0.160% | +8.3% | 2.18% | 1,523 |
| 21 Aug | +0.074% | +3.9% | 2.21% | 1,747 |
| 28 Aug | +0.028% | +1.5% | 2.25% | 3,010 |
| 4 Sep | +0.117% | +6.1% | 2.22% | 3,995 |
| 11 Sep | +0.117% | +6.1% | 2.25% | 4,083 |
| 18 Sep | +0.149% | +7.7% | 2.26% | 5,258 |
| 25 Sep | +0.051% | +2.6% | 2.25% | 6,009 |
| 2 Oct | +0.116% | +6.1% | 2.24% | 6,014 |

### E.3 Stability

- 19 weeks from 29 May: mean 5.34% a year, standard deviation 18.6 pp; 3 negative weeks, 4 below stETH; range −46.6% to +56.3%.
- Since 24 Jul (11 weeks): every week positive, 1.5% to 8.3% a year, one week below stETH (28 Aug).
- The share price uses keeper-stored market balances. In the whitelist phase it fell 5.4% on 27 Mar and recovered 5.4% on 30 Mar on about 30 ETH: mark updates, not trades.

### E.4 P&L by leg (share of start capital, pp)

| Window | Return | Staking (a) | Dollar leg (c) | Rewards (d) | Fees (e, est.) | Residual (f) |
|---|---:|---:|---:|---:|---:|---:|
| 90d | 0.934 | 0.484 | −0.499 | 0.382 | −0.241 | 0.808 |
| Since 31 Mar | 3.516 | 1.003 | −0.595 | 0.844 | −0.679 | 2.943 |

In ETH over 90 days: staking +13.0, dollar leg −13.4, BOLD +10.2, fees −6.4, residual +21.6 (total +25.0 on 2,676 average). The residual is the largest single term: Uniswap v4 BOLD/USDC fees and stored market books that the model cannot reprice.

### E.5 Negative periods

| When | Move | Cause (inferred from timing) |
|---|---|---|
| 5 Mar | −2.8% in a day | rETH trove opened (fees and swap on 1.4 ETH) |
| 10 to 11 Mar | −2.7% | rETH trove closed, move to wstETH branch |
| 27 Mar | −5.4%, reversed 30 Mar | stored mark update |
| 4 to 17 Apr | −0.5%, −1.2% weeks | trove churn on 32 ETH |
| Week to 12 Jun | −0.89% | current trove opened 6 Jun (upfront fee, inferred) |
| Jul | −0.26%, −0.23% weeks; month −0.22% without rewards | rate 5.55% against 0.49% pool fees |

---

## F. Risk management

### F.1 Collateral ratio over time

HF-equivalent (ICR/MCR) 1.49 to 2.13 at month-ends; the low was June (LTV 55.9%). LTV has been cut from 53.7% (Aug) to 44.3% (T) while the book doubled. No liquidation or redemption of the vault's troves was found in the month-end reads; redemption events were not scanned.

### F.2 Rate management

The trove's rate is the vault's choice. It ran 0.88% in April and May, rose to 6.35% by the August month-end and was cut to 2.55% in September. A higher rate protects against redemptions (Ebisu redeems the lowest-rate troves first) but makes the dollar leg more negative; the September cut chose carry over redemption safety.

### F.3 Liquidity ladder at T

| Tier | Repayable | % of debt | How |
|---|---:|---:|---|
| Same block | $6.58M | 97.5% | Curve `remove_liquidity_one_coin` to ebUSD (pool holds 7.26M ebUSD, 2.78M USDC) |
| Same block, swap | $0.17M | 2.5% | idle 300.7 WETH and the v4 book |
| Slower | 0 | 0% | |

Repaying everything releases 4,585.5 wstETH. Depositor exit: instant if liquid (0.2% fee), otherwise request plus a 24h window (0.2% fee). At T a 1% withdrawal test succeeds; 10% and 30% revert.

### F.4 Stress (instant ETH moves, est.)

| ETH move | HF-equivalent | Liquidatable | Note |
|---|---:|---|---|
| −20% | 1.50 | no | |
| −30% | 1.32 | no | |
| −47% | 1.00 | yes | |

ETH price risk is remote. The live risks are an ebUSD depeg (the LP holds ebUSD, the debt is ebUSD, so a depeg mostly nets; a depeg up raises the cost of buying back debt), redemptions against a low-rate trove, and the 10% to 30% exit failure.

---

## G. Depositors (T)

### G.1 Size buckets (direct; no wrappers to look through except Rocksolid)

| Bucket | Holders | % holders | ETH | % ETH |
|---|---:|---:|---:|---:|
| < 1 ETH | 34 | 26.2% | 8.1 | 0.13% |
| 1 to 10 | 43 | 33.1% | 148.4 | 2.47% |
| 10 to 100 | 47 | 36.2% | 1,539.4 | 25.60% |
| 100 to 1k | 5 | 3.8% | 2,100.1 | 34.92% |
| > 1k | 1 | 0.8% | 2,218.0 | 36.88% |
| **Total** | **130** | | **6,014.0** | median 5.01 ETH |

Top 1 36.9%, top 10 77.4%, top 100 99.9%, HHI 1,723. The median holder is far larger than in the other four products.

### G.2 Address types (top 10)

| Holder | ETH | % | Type |
|---|---:|---:|---|
| `0x1676d237` | 2,218.0 | 36.88% | Safe 3-of-6; borrows WETH on Morpho to deposit; also borrows GHO and USDS; signers funded by noca.eth and "Gnosis: Active Treasury Management" |
| `0x9ca1d6e7` | 728.5 | 12.11% | Rocksolid rETH execution account (nested product) |
| `0x8a25d8c9` | 714.4 | 11.88% | EOA |
| `0xe5ebcde1` | 401.4 | 6.68% | EOA |
| `0x59e369d9` | 150.6 | 2.50% | EOA |
| `0x1cde180f` | 105.3 | 1.75% | Safe 2-of-5 (also a top-10 savETH holder at Avant) |
| others | 333.4 | 5.54% | 3 EOAs, Safe 2-of-3 |

Half the book (49%) belongs to two professional holders: a fund-like Safe running leverage into the vault, and another vault that went into Closing six days after entering.

### G.3 Holders over time (month-end)

| Month | Holders | ≥ 0.01 ETH | New | Exited | Book ETH | Top 1 |
|---|---:|---:|---:|---:|---:|---:|
| Mar | 4 | 3 | 4 | 0 | 32 | 93.3% |
| Apr | 5 | 4 | 1 | 0 | 32 | 93.7% |
| May | 43 | 42 | 38 | 0 | 528 | 10.0% |
| Jun | 61 | 55 | 25 | 7 | 641 | 9.3% |
| Jul | 92 | 83 | 34 | 3 | 1,502 | 13.3% |
| Aug | 112 | 100 | 26 | 6 | 2,814 | 30.1% |
| Sep | 131 | 116 | 31 | 12 | 6,017 | 36.9% |
| T | 130 | 116 | 1 | 2 | 6,014 | 36.9% |

## H. TVL growth

| Month | Change | = net flows | + yield |
|---|---:|---:|---:|
| May | +496 | +495.5 | +0.7 |
| Jun | +113 | +111.0 | +2.0 |
| Jul | +861 | +860.7 | +0.6 |
| Aug | +1,311 | +1,305.1 | +6.3 |
| Sep | +3,203 | +3,189.9 | +13.0 |
| 1 to 2 Oct | −3 | −5.4 | +2.7 |
| **Since 31 Mar** | **+5,982** | **+5,957** | **+25.3** |

Yield = month-end shares × change in price per share (est.). In September the top holder's stake rose from about 846 ETH (30.1% of 2,814) to 2,218 ETH and Rocksolid added 728 ETH: about 2,100 of the 3,190 ETH net inflow (est.).

## I. Growth drivers (dated)

| Date | Event | Effect |
|---|---|---|
| 30 Jan 2026 | Vault, AccessManager, FeeManager, WithdrawManager deployed; whitelist only | empty until March |
| 3 Mar | First deposit (EIP-7702 EOA `0x81fa729b`, also owner) | |
| 5 to 9 Mar | First trove (rETH branch), closed; moves to wstETH | price 1.0 to 0.963 |
| 28 Feb to 30 Nov | IPOR Fusion points season (deposit WETH in the vault) | unpriced |
| 19 May | Deposits public; 0.2% in, out and request fees | 43 holders by 31 May |
| 26 May | Guardian closes the vault for 15 minutes | |
| 28 May | Performance 2% to 10%, management 0.3% to 0.5% | |
| 6 to 11 Jun | Current trove opens; control to Safe 2-of-3 | −0.89% week |
| 28 Jul | New strategist EOA | |
| 25 Aug | Safe 3-of-6 enters | 36.9% holder by T |
| Sep | Rate cut to 2.55% | |
| 23 Sep | Rocksolid execution account enters; Rocksolid Closing on 29 Sep, reopened 7 Oct | 12.1% holder |

**What explains the growth.** Two allocators and a rate that looked high in August and September (5.05% and 5.78%). The vault's own carry did not change: the September rate cut and BOLD rewards did the work.

## J. Operator economics

| Item | Amount |
|---|---|
| Fees harvested 8 May to T (on-chain) | 8.25 shares, about 8.0 WETH: curator Safe 5.05, IPOR DAO 3.21; 36 management and 37 performance harvests; largest 3.27 shares on 25 Sep |
| Fees at T run-rate (est.) | management 0.5% × 6,014 = 30 ETH a year; performance 10% of about 290 ETH gross = 29 ETH a year; about 59 ETH ($157k) |
| Entry fee on September inflows (est.) | 0.2% × 3,190 ETH = 6.4 ETH, if all flows were deposits; recipient not traced |
| BOLD rewards to the vault | $25.9k realized in 216 days; $153k a year run-rate (0.95% of TVL) |
| Merkl BOLD | $0.2k realized; $2.6k a year run-rate; ends 8 Oct |

Reading: at T run-rates the BOLD reward (about $153k a year) roughly equals what the curator and IPOR charge (about $157k a year, est.). The depositor's lead over stETH is the reward net of fees.

---

## K. Verdict: what to copy, what to avoid

**Copy:**
1. **A same-currency repayment source inside one pool.** 97.5% of the debt is bought back in one block from the LP the loan funded.
2. **Low LTV for an ETH-collateral dollar loan.** 44% against an 83% line; −47% ETH to liquidation.
3. **Fees with a high-water mark and harvest history on-chain.** Every harvest and fee change can be replayed.

**Avoid:**
1. **A dollar leg that earns less than it costs.** Pool fees of 0.4% to 0.9% never covered the loan; the lead over stETH is BOLD.
2. **A product name that describes a different protocol.**
3. **A 2-of-3 Safe with zero delay on fuses, fees and closing.** The strategy can be replaced before a depositor can leave.
4. **Exits that fail above 1% of the book.**
5. **Testing with depositor-visible capital.** The March test losses left the share price below 1.0 for its whole life.
6. **Concentration in allocators who can leave together:** 49% in two holders, one of them a vault that started closing six days after entering.

---

## Method, limits, reproducibility

- **New data:** `weekly.csv`, 28 points (27 Mar to T, every 7 days back from T): `convertToAssets(1e20)`, `totalAssets`, `totalSupply`, wstETH `stEthPerToken`; `march_daily.csv`, 30 daily points (2 to 31 Mar). Scripts `weekly.py`, `march_daily.py` (helper `tools/eth/top5/weekly_lib.py`). RPC: Tenderly public gateway, fallback drpc. T read 0.973079 matches the 7 Oct pull.
- **Reused:** returns and splits, incentive cost, month-end trove data (`gap_top5_risk_series.csv`), ladder (`atlas_top5_risk.json`), keys, fees, events, holders, holder identities ([BORROWER-IDENTITIES](../../en/BORROWER-IDENTITIES.md)).
- **Limits:**
  - The share price rests on keeper-stored market balances; fresh accounting updates could not be simulated (no permission). The residual (+3.3 pp a year) is therefore unverified.
  - Fees in E.4 are an estimate (0.5% plus 10% of gains), not the harvest ledger.
  - The dollar leg assumes the LP claim equals the debt; Uniswap v4 fees are not measured.
  - Redemption events against the troves were not scanned; Ebisu governance and ebUSD backing were not reviewed.
  - The cause of the 12 Jun week (upfront fee on the new trove) is inferred from timing.
  - IPOR Fusion points are unpriced, so the rewards share is a lower bound.
