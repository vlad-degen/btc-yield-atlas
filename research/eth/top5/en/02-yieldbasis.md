# YieldBasis WETH: deep dive (yield history, risk, depositors, growth, economics)

*Data: [`data/eth/top5/yieldbasis/`](../../../../data/eth/top5/yieldbasis/) (`weekly.csv` is new in this pass; `keys.csv`, `fees.csv`, `events.csv`, `holder_buckets.csv`, `holders_monthly.csv` from the 7 Oct pull). Scripts: [`tools/eth/top5/yieldbasis/`](../../../../tools/eth/top5/yieldbasis/). Russian version: [../02-yieldbasis.md](../02-yieldbasis.md).*

**Snapshot T:** 2 Oct 2026 23:59:59 UTC, Ethereum block 26,108,081. Benchmark: stETH (wstETH `stEthPerToken`) over the same blocks. Pool: WETH market #10 of the YieldBasis Factory, LT `0x2b9c9f3b…3cea`, LEVAMM `0x5f8d24f3…233c`, gauge `0xd829456f…e3d8`, live since 25 May 2026. The January 2026 WETH market (LT `0x931d40dd`) is a separate contract and is not merged here. BTC mechanism reference: [BTC YieldBasis dive](../../../top5/en/02-yield-basis.md).

---

## Key findings

1. **The unstaked LT trailed stETH over every window longer than a month.** 90 days to T: −2.96% a year against stETH +2.25%. Since 31 May: +2.10% a year against +2.30%. Only June beat stETH (+1.41% in the month).
2. **The pool loses when ETH rises fast.** Weekly LT return against the weekly ETH move: correlation −0.57 (18 weeks). The week ETH rose 34% (to 21 Aug) was the worst week (−0.43%); the week ETH fell 21% (to 5 Jun) was one of the two best (+0.78%). Since 12 Jun the LT is down 0.89% while ETH rose 60%.
3. **Fees do cover the loan; tracking loss eats the rest.** Since 31 May, LP fee growth minus the 10% crvUSD rate added +8.97 pp a year; re-levering and tracking took −6.88 pp a year. Over the last 90 days the split was +5.5 pp and −8.5 pp.
4. **Depositors as a group lost about 50 ETH.** The share price is +0.71% since 31 May, but money came in after the good June: month-end shares times price change give −49.7 ETH since 31 May (est.).
5. **Staked holders take losses and none of the gains.** The gauge share fell from 0.99995 to 0.98514 LT in the first three weeks of June while the LT rose; it has not moved since 19 Jun. In ETH, a staked share is −0.82% from 29 May to T, the unstaked share +0.68%.
6. **YB emissions are the staked holder's whole return, and they are shrinking per ETH.** 90 days: +1.69% a year with YB, −2.96% without. Since 31 May: +6.13% with, −2.29% without. Run-rate at T: $504k a year, 3.16% of staked TVL, so a staked holder now nets about +0.2% a year (est.).
7. **The protocol earned about 5.5 ETH and paid out about $152k of YB.** Admin fee is 40.5% at T on paper, but all 5 fee withdrawals since 20 Jul minted 0 LT; the only fee ever taken was 5.47 LT in June.
8. **No liquidation, and exit is near book.** Debt stayed at 49.8% to 50.2% of collateral at every month-end against a 56.25% critical ratio. A 1 LT exit priced within −0.16% to +0.11% of book at every weekly point; 99% of the pool would exit at −1.17% at T. 99.6% of the crvUSD debt is repaid in the same call.
9. **A third of the pool is HybridVault money.** 81 personal crvUSD-backed vaults hold 36.7% of LT (27.5% directly, 16.3% of the gauge). The largest owner (21.8%) sits behind one of them.
10. **Flows ignored yield.** +9,835 ETH of net inflow since 31 May against −49.7 ETH of yield. The biggest inflow week (book +5,884 ETH to 21 Aug) was the worst return week; September saw 28 exits and −1,874 ETH of net outflow.
11. **Parameters move by token vote with no timelock.** veYB vote (7 days, early execution allowed); two contracts can raise the crvUSD allocation without a vote, one added on 10 Sep; a 5-of-9 Safe can kill the market.

---

## A. Scope and snapshot

| Item | Value at T | Source |
|---|---|---|
| Book | 10,426.0 ETH ($27.82M) | LT `totalSupply` 10,364.97 × `pricePerShare` 1.005888 |
| Staked / unstaked | 5,875.0 ETH (56.35%) / 4,551.0 ETH | LT `balanceOf(gauge)` |
| Debt | 27,814,856 crvUSD at a fixed 10.00% | LEVAMM `get_state`, `rate()` |
| Debt / collateral | 50.0% (critical 56.25%, HF-equivalent 1.12) | [TOP5-RISK-LIQUIDITY](../../en/TOP5-RISK-LIQUIDITY.md) |
| crvUSD allocation | 64.14M (capacity, not debt) | [CARRY-PRODUCTS](../../en/CARRY-PRODUCTS.md) |
| Holders | 332 addresses; 407 owners after look-through | Transfer replay, matches supply |
| Return, 90d | unstaked −2.96%/yr; staked with YB +1.69%/yr; stETH 2.25% | `rewards_split.csv` |

## B. Structure and legs

One leg. The LT takes WETH, draws an equal crvUSD amount from the market's allocation (Curve DAO credit line to the YieldBasis Factory) and adds both to a Curve WETH/crvUSD pool. The LEVAMM holds the LP at 2× and is re-levered by arbitrageurs who pay its 1.30% fee.

| Leg | Collateral | Debt | Where the dollars go | Rate |
|---|---|---|---|---|
| WETH/crvUSD 2× LP | Curve LP (AMM owns 99.90% of the pool) | crvUSD, 27.81M | stay in the same pool | 10.00% fixed, paid into the pool, not to Curve |

The interest is a transfer from LT holders back into the pool they own. Curve DAO earns no interest on this line.

## C. Positions (month-end)

| Month-end | Collateral $M | Debt $M | Debt / collateral | HF-eq. | Pool fee APR (virtual price) | Fees on 2× minus 10% rate, on equity |
|---|---:|---:|---:|---:|---:|---:|
| May | 2.6 | 1.29 | 49.9% | 1.13 | | |
| Jun | 15.8 | 7.95 | 50.2% | 1.12 | 15.79% | +21.6 pp (est.) |
| Jul | 28.2 | 14.12 | 50.1% | 1.12 | 7.42% | +4.8 pp (est.) |
| Aug | 61.2 | 30.48 | 49.8% | 1.13 | 6.82% | +3.6 pp (est.) |
| Sep | 56.2 | 28.06 | 49.9% | 1.13 | 9.18% | +8.4 pp (est.) |
| T | 55.6 | 27.81 | 50.0% | 1.12 | 9.19% (30d) | +8.4 pp (est.) |

Last column = 2 × pool APR − 10%, since equity equals debt at 2×.

## D. Governance and security

| Layer | Who | Power | Delay at T |
|---|---|---|---|
| LT and LEVAMM code | nobody | immutable Vyper 0.4.3, no proxy | n/a |
| Factory admin | HybridFactoryOwner `0xb8ba33cd` (since 3 Jun), forwards only for the DAO | rate, AMM fee, min admin fee, fee receiver, implementations, kill | veYB vote |
| DAO | Aragon TokenVoting `0x2be6670d` (veYB) | executes proposals; can upgrade itself | 7-day vote, 55% support, 30% quorum, early execution; no timelock |
| Limit setters | HybridVaultFactory `0xbdc32268`; LTMigrator `0xd5b450fd` (since 10 Sep) | raise this LT's crvUSD allocation (floored at 95% of LP value) | none |
| Emergency admin | Safe 5-of-9 `0x467947ee` (Curve's EmergencyDAO per the BTC dive) | kill: blocks deposit and normal withdraw | none |
| Fee receiver | FeeSplitter `0x4b7782fd` (since 20 Jul), owner DAO | 15% split, rest to veYB | DAO vote |

Findings:
- The admin path changed twice before and after launch (7 Apr, 3 Jun). The LTMigrator became a limit setter on 10 Sep, so migrations from legacy markets can enlarge this pool's credit line without a vote.
- No `SetFee` or `SetRate` on this market through T: fee 1.30% and rate 10% unchanged since 25 May. The BTC v3 markets were re-rated by DAO votes in the same period (0.82% to 2.64% to 1.80%).
- Kill leaves `emergency_withdraw` open; a holder may then need to bring crvUSD for the debt leg (per BTC dive mechanics).

---

## E. Yield history since launch

**Method.** Unstaked: LT `pricePerShare`. Staked: gauge `convertToAssets` × `pricePerShare`, plus YB emissions valued at the DefiLlama price on receipt. Splits from [REWARDS-SPLIT](../../en/REWARDS-SPLIT.md): c = pool virtual-price growth on LP value minus AMM `rate_mul` growth on debt; f = residual. Weekly points are archive reads every 7 days back from T (`weekly.csv`).

### E.1 Monthly (APY, unstaked LT)

| Month | Return in month | APY | stETH APY | Excess (pp, not annualized) | Staked share value, month |
|---|---:|---:|---:|---:|---:|
| Jun | +1.412% | 18.61% | 2.45% | +1.21 | −0.09% |
| Jul | −0.130% | −1.52% | 2.24% | −0.32 | −0.13% |
| Aug | −0.371% | −4.29% | 2.23% | −0.56 | −0.37% |
| Sep | −0.176% | −2.12% | 2.27% | −0.36 | −0.18% |
| 1 to 2 Oct | −0.017% | −3.08% | 2.24% | −0.03 | −0.02% |
| **90d to T** | −0.737% | **−2.96%** | 2.25% | −1.29 | |
| **Since 31 May** | +0.710% | **2.10%** | 2.30% | −0.06 | |

Staked share value excludes YB. It never rose: gains go to unstaked holders, losses are shared.

### E.2 Weekly (week ending; `weekly.csv`)

| Week to | LT week | LT APY | stETH APY | ETH/USD week | Book ETH | Staked |
|---|---:|---:|---:|---:|---:|---:|
| 5 Jun | +0.784% | +40.9% | 2.48% | −21.3% | 1,101 | 78.9% |
| 12 Jun | +0.784% | +40.9% | 2.55% | +5.2% | 4,717 | 33.1% |
| 19 Jun | −0.258% | −13.4% | 2.36% | +2.6% | 4,895 | 38.8% |
| 26 Jun | +0.128% | +6.7% | 2.37% | −7.6% | 5,021 | 39.8% |
| 3 Jul | +0.020% | +1.1% | 2.29% | +11.6% | 5,569 | 40.1% |
| 10 Jul | −0.097% | −5.0% | 2.23% | +2.1% | 7,850 | 45.5% |
| 17 Jul | +0.001% | +0.1% | 2.20% | +2.2% | 7,725 | 44.8% |
| 24 Jul | −0.043% | −2.2% | 2.19% | +1.3% | 7,638 | 45.3% |
| 31 Jul | −0.077% | −4.0% | 2.20% | +0.2% | 7,632 | 45.4% |
| 7 Aug | +0.008% | +0.4% | 2.19% | +2.8% | 7,700 | 45.7% |
| 14 Aug | −0.074% | −3.9% | 2.18% | −1.9% | 7,739 | 46.0% |
| **21 Aug** | **−0.426%** | **−22.2%** | 2.21% | **+34.0%** | **13,623** | 63.5% |
| 28 Aug | +0.254% | +13.2% | 2.25% | −3.1% | 13,623 | 62.9% |
| 4 Sep | −0.236% | −12.3% | 2.22% | +0.5% | 10,543 | 52.7% |
| 11 Sep | −0.177% | −9.2% | 2.25% | +2.6% | 10,788 | 56.6% |
| 18 Sep | +0.029% | +1.5% | 2.26% | +3.7% | 10,657 | 56.9% |
| 25 Sep | +0.026% | +1.3% | 2.25% | +3.2% | 10,611 | 56.8% |
| 2 Oct | +0.033% | +1.7% | 2.24% | −0.9% | 10,426 | 56.3% |

### E.3 Stability (18 weeks, 29 May to T)

- Mean weekly APY 1.97%, standard deviation 15.8 pp. Best +40.9% (two June weeks), worst −22.2% (21 Aug).
- 8 negative weeks; 14 of 18 weeks below stETH. The last three weeks were +1.3% to +1.7% a year, still below stETH.
- Weekly LT return vs ETH weekly move: correlation −0.57; vs the absolute ETH move: +0.06. Direction matters, not volatility: up-moves cost, down-moves pay. The LP's internal price lags a fast rally (same mechanism as the BTC v3 `price_scale` lag, where it showed up as a −6% exit discount; here it shows up in the share price instead).
- The share price is marked to the pool, not smoothed. Unlike a managed accountant rate it shows every loss in the week it happens.

### E.4 P&L by leg (ETH, from REWARDS-SPLIT)

| Window | Avg equity | Fees minus interest (c) | Re-levering and tracking (f) | Admin fee | Return |
|---|---:|---:|---:|---:|---:|
| Since 31 May (124 days) | 7,790 | +237.4 ETH (+8.97 pp/yr) | −182.1 ETH (−6.88 pp/yr) | 0 | +55.3 ETH (+0.71%) |
| 90 days to T | 9,541 | +129.8 ETH (+5.5 pp/yr) | −200.1 ETH (−8.5 pp/yr) | 0 | −70.3 ETH (−0.74%) |

The table is time-weighted. ETH-weighted (month-end shares × price change) the pool made +9.1 ETH in June, then −6.6, −28.3, −22.0 and −1.8 ETH: **−49.7 ETH since 31 May** (est.). Most capital arrived after the only good month.

Staked side, since 31 May: YB emissions $149.7k; 90 days $108.8k. Without them, staked lost 0.78% of principal over 124 days.

### E.5 Negative periods

- Monthly: Jul, Aug, Sep and 1 to 2 Oct negative in absolute terms; every month after June below stETH.
- Weekly: 8 of 18 weeks negative. Two of the three largest losses coincide with the largest flows: 21 Aug (ETH +34%, book +5,884 ETH) and 4 Sep (book −3,080 ETH).
- Admin fee in "recovery": since 20 Jul all positive value change first refills the staked side; 5 `WithdrawAdminFees` calls returned 0.

---

## F. Risk management

### F.1 Leverage over time

There is no LTV to manage and no liquidation. Debt/collateral at month-ends: 49.9%, 50.2%, 50.1%, 49.8%, 49.9%, 50.0% (May to T), HF-equivalent 1.12 to 1.13. Leverage is restored by arbitrageurs, not by an operator; no delever events exist to time.

### F.2 What replaces liquidation risk

- **Tracking loss in rallies.** E.3 above: −0.43% in the week ETH rose 34%. A 2× pool that re-levers late pays for it in the share price.
- **crvUSD dependency.** The credit line is Curve DAO's; in the BTC markets in Feb 2026 a full unwind would have needed $151M of net crvUSD buying and the DAO cut allocations. The WETH pool's 27.8M crvUSD sits inside a pool the AMM owns 99.9% of, so the unwind source is the pool itself.
- **Kill switch.** The 5-of-9 Safe can block normal withdrawals at any time; `emergency_withdraw` remains.

### F.3 Liquidity ladder at T

| Tier | Repayable | % of debt | How |
|---|---:|---:|---|
| Same block | $27.70M | 99.6% | `LT.withdraw` removes LP pro rata and repays crvUSD in the same call |
| Same block, in-pool swap | $0.11M | 0.4% | shortfall swapped from WETH in the same pool |
| Slower | 0 | 0% | no external destination |

Exit quotes at T: 1% of supply 104 WETH, 10% 1,043, 30% 3,128 (all within rounding of book); 99% 10,200.9 WETH against 10,321.7 of book (−1.17%). Weekly 1 LT quote vs book: −0.16% (21 Aug) to +0.11% (5 Jun).

### F.4 Stress (est.)

No price level liquidates the pool. Stress shows up as tracking loss. Scaling the 21 Aug week (−0.43% for ETH +34%), a +50% ETH week would cost about 0.6% of the LT in ETH terms (est., one-point extrapolation; not modelled). Down-moves have paid so far (+0.78% for −21% to 5 Jun).

---

## G. Depositors (T)

### G.1 Size buckets, look-through (gauge and HybridVaults resolved to owners)

| Bucket | Owners | % owners | ETH | % ETH |
|---|---:|---:|---:|---:|
| < 1 ETH | 265 | 65.1% | 27.8 | 0.27% |
| 1 to 10 | 73 | 17.9% | 277.0 | 2.66% |
| 10 to 100 | 51 | 12.5% | 1,632.8 | 15.66% |
| 100 to 1k | 17 | 4.2% | 6,218.5 | 59.64% |
| > 1k | 1 | 0.25% | 2,270.0 | 21.77% |
| **Total** | **407** | | **10,426.0** | median 0.097 ETH |

Concentration: top 1 21.8%, top 10 70.7%, top 100 99.0%, HHI 801. Direct view (gauge as one address): 332 addresses, gauge 56.4%, top 10 93.3%, HHI 3,580.

### G.2 Address types

- **HybridVaults:** 81 personal vaults (owner posts crvUSD into scrvUSD to get a cap above the pool's) hold 36.7% of LT: 2,847 LT directly and 16.3% of the gauge. Four of the direct top 10 are HybridVaults; owner `0x0b077c44` holds 2,270 ETH through one.
- **Plain EOAs** dominate the rest of the top 10; one top-5 owner is an EIP-7702 EOA (`0x2cc4e9d6`, 638 ETH).

### G.3 Holders over time

| Month-end | LT addresses | ≥ 0.01 ETH | New | Exited | Gauge stakers | Staked share | Book ETH |
|---|---:|---:|---:|---:|---:|---:|---:|
| May | 26 | 19 | 26 | 0 | 32 | 57.3% | 641 |
| Jun | 164 | 85 | 143 | 5 | 79 | 39.9% | 5,085 |
| Jul | 243 | 126 | 93 | 14 | 104 | 45.4% | 7,632 |
| Aug | 324 | 181 | 92 | 11 | 147 | 59.9% | 12,512 |
| Sep | 334 | 158 | 38 | 28 | 159 | 56.9% | 10,616 |
| T | 332 | 154 | 4 | 6 | 155 | 56.4% | 10,426 |

The count of holders with at least 0.01 ETH peaked in August (181) and fell to 154 by T.

## H. TVL growth

| Month | Book end ETH | Change | = net flows | + yield |
|---|---:|---:|---:|---:|
| Jun | 5,085 | +4,444 | +4,435 | +9.1 |
| Jul | 7,632 | +2,547 | +2,554 | −6.6 |
| Aug | 12,512 | +4,880 | +4,908 | −28.3 |
| Sep | 10,616 | −1,896 | −1,874 | −22.0 |
| 1 to 2 Oct | 10,426 | −190 | −188 | −1.8 |
| **Since 31 May** | | **+9,785** | **+9,835** | **−49.7** |

Yield = previous month-end shares × change in price per share (est.). In dollars the book went from $1.3M (May) to $61.2M collateral at the August peak; ETH/USD rose from $1,998 to $2,466 over the same months, so dollar TVL overstates ETH growth.

## I. Growth drivers (dated)

| Date | Event | Book / flows |
|---|---|---|
| 7 Jan 2026 | Earlier WETH market (LT `0x931d40dd`) created | separate history |
| 7 Apr | Factory admin to HybridFactoryOwner v1; HybridVault factory becomes a limit setter | |
| 25 May | Current WETH market deployed; gauge set; fee 1.3%, rate 10% | 641 ETH, 26 holders by 31 May |
| 3 Jun | Admin to HybridFactoryOwner `0xb8ba33cd` | |
| 5 to 12 Jun | Best two weeks (+0.78% each) as ETH falls then rebounds | book 1,101 to 4,717 ETH |
| 20 Jul | Fee receiver to FeeSplitter; admin fee withdrawals return 0 from here | |
| 15 to 21 Aug | ETH +34% in a week; largest inflow | book +5,884 ETH, worst week −0.43% |
| 31 Aug | Peak 12,512 ETH, 324 holders, 59.9% staked | debt $30.5M |
| 29 Aug to 4 Sep | Largest outflow | book −3,080 ETH |
| 10 Sep | LTMigrator becomes limit setter | |
| Sep | 28 exits, book −15% | −1,874 ETH net |

**What explains the growth.** Capacity and the HybridVault route, not yield: inflow kept coming through July and August while every month was negative, and one week of ETH strength brought the largest deposit. The exits in September follow three negative months.

## J. Operator economics

| Who | What | Amount |
|---|---|---|
| veYB (FeeDistributor `0xd11b4165`) | admin fee, 7 withdrawals 31 May to 18 Jun | 5.47 LT (about 5.5 ETH, $14.7k at T price, est.) |
| veYB / FeeSplitter | admin fee since 20 Jul | 0 in 5 withdrawals |
| Curve DAO | interest on 27.8M crvUSD | 0 (the 10% is paid into the pool) |
| YB emissions to stakers | realized since launch (25 May) | $151.9k ($149.7k since 31 May); run-rate $504k/yr (3.16% of staked TVL, 1.8% of the whole book) |
| Arbitrageurs | pay the 1.30% LEVAMM fee | into the pool |

Reading: the protocol has spent about ten times in YB what it has collected in fees from this pool (est., $152k vs $14.7k). Admin fee at 40.5% only matters after the staked side's losses are refilled; at T that has not happened since July.

---

## K. Verdict: what to copy, what to avoid

**Copy:**
1. **A loan that pays for itself inside the venue.** Fees on 2× the debt covered the 10% rate at every month-end reading (+3.6 to +21.6 pp on equity). No external parking, no rate spikes, no redemption queue.
2. **Same-call repayment.** 99.6% of debt repaid in the withdraw transaction; exits near book. This is the best exit of the five products.
3. **No liquidation engine.** Leverage is held at 50% by arbitrage, not by an operator reacting late.
4. **Immutable core code.** The only levers are parameters.

**Avoid:**
1. **Selling an ETH product that lags ETH rallies.** Since 12 Jun the LT is −0.89% while ETH rose 60%. A depositor measuring in ETH is short the ETH trend.
2. **Two share classes with opposite deals.** Staked: losses, no gains, paid in a token. Unstaked: gains after the staked side is refilled. Publishing "40.5% admin fee" or "10% minimum fee" hides that no fee has been taken since July.
3. **Emission-led returns.** $504k a year of YB is what separates a staked holder from a loss.
4. **Parameter changes by early-executed vote with no timelock, and credit-line increases with no vote.**
5. **Reporting the APY of the first month.** June's 18.6% was earned on 641 to 5,085 ETH; the ETH-weighted outcome is −49.7 ETH.

---

## Method, limits, reproducibility

- **New data:** `weekly.csv`, 19 points (29 May to T, every 7 days back from T): LT `pricePerShare`, gauge `convertToAssets(1e18)`, LT `preview_withdraw(1e18)`, `totalSupply`, `balanceOf(gauge)`, wstETH `stEthPerToken`, Chainlink ETH/USD `latestAnswer`. Scripts `weekly.py`, `eth_price_weekly.py` (shared helper `tools/eth/top5/weekly_lib.py`). RPC: `gateway.tenderly.co/public/mainnet`, fallback `eth.drpc.org`. T reads match the 7 Oct pull to the last digit (pps 1.005888, gauge 0.985138).
- **Reused:** monthly returns and splits (`rewards_split.csv`), incentive cost (`incentive_cost.csv`), month-end risk (`gap_top5_risk_series.csv`), keys, fees, holders (7 Oct pull).
- **Limits:**
  - The 9.19% pool APR is virtual-price growth. In YieldBasis pools the 10% interest is donated back into the pool, so part of that growth may be recycled interest rather than trader fees. The split between swap fees and donations was not separated; the "fees cover the loan" reading depends on it.
  - The ETH-weighted −49.7 ETH uses month-end shares and ignores intra-month flow timing.
  - Correlation with ETH uses 18 weekly points; it is a description, not a model.
  - YB is valued at receipt price; the token's later price is not applied.
  - HybridVault share uses gauge holdings from `parity-ybGauge-holders.csv` (155 stakers, matches the T gauge supply).
  - Fee withdrawals to veYB are counted in LT, not converted at claim-time price.
