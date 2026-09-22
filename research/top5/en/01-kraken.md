# Kraken Bitcoin Vault — deep dive v3 (yield history, risk, depositors, growth, economics)

*Scripts: [`tools/top5/kraken/`](../../../tools/top5/kraken/), data: [`data/top5/kraken/`](../../../data/top5/kraken/). Mentions of `scripts/` and `raw/` below refer to the working folder; the `raw/` dumps are not published.*

Veda BoringVault "Advanced Strategies BTC" (`sentoraBTC`, `0x7dee…19b2`, Ink), strategy by Sentora.

**Date:** 21 Sep 2026. **Snapshot:** 20 Sep 2026 12:00 UTC (Ethereum block 26,018,583; Ink block 56,407,189). A second "live" read was taken on 21 Sep at 22:33 UTC (Ethereum block 26,028,885).

**Sources.** Figures come from archive `eth_call` / `eth_getLogs` on Ethereum and Ink, the Blockscout APIs (Ink and Ethereum), the Merkl v4 API, the DefiLlama yields API, and Chainlink feeds read on-chain.

**Labels.** Figures marked **(est.)** are my own model estimates. Everything else is read from a chain or an API. Addresses that are not publicly labelled are called "unlabelled".

**Reuse.** A–D reuse the verified work in `BTC-Carry-Vaults-Dossiers.md` §4.1, `BTC-Yield-Deep-Dive.md` §1. Sections E–K are new.

**Files.** In this folder:
- `yield_weekly.csv`
- `tvl_weekly.csv`
- `ltv_weekly.csv`
- `holders_buckets.csv`
- `holders_types.csv`
- `liquidity_ladder.csv`
- `events.csv`
- `scripts/` (every number below can be regenerated from these scripts)
- `raw/` (source data)

---

## Summary: 12 new findings

1. **Why yield fell (1.80% in June → 1.03% in September).** Almost all of the decline is the borrow side re-pricing. Deployment yields did not fall.
   - **Borrow cost rose.**
     - kBTC/RLUSD: 1.60% (June average) → 3.07% (September).
     - kBTC/PYUSD: 1.20% → 3.97%.
   - **The cause is the interest-rate model.** Both markets sat almost unused from 17 Apr to 18 May. During that time Morpho's AdaptiveCurveIRM `rateAtTarget` decayed:
     - PYUSD: 4.05% → 0.62%;
     - RLUSD: 4.07% → 1.90%.

     Launch-period depositors therefore got cheap borrowing. It then took until August for the rates to climb back to about 3%.
   - **Deployment yields stayed flat.**
     - Sentora RLUSD Main: about 6.0–6.4% in total.
     - PRIME: about 6–7%.
2. **Rewards are about 82% of the carry since launch (est.).** They are about 90% at today's rates.
   - **The debt-weighted model reproduces realized net yield within 0.02–0.24 pp every month.** Model vs realized:

     | Month | Model | Realized |
     |---|---|---|
     | June | 1.90% | 1.80% |
     | September | 1.05% | 1.03% |

   - **Without Merkl rewards the vault would net:**
     - 0.59% in June;
     - 0.12% in September;
     - 0.05% in the week of 14 Sep.
   - **The A-legs lose money without rewards.** The A-legs are the stablecoins lent back into Sentora's V2 vaults. Their organic carry since launch was −$0.25M. All the unsubsidized profit (+$0.60M) comes from the PRIME legs, i.e. Figure HELOC credit.
3. **Negative carry including rewards was rare but real.** On a daily-average basis:
   - **A-RLUSD:** 0 days out of 117.
   - **A-PYUSD:** 2 days (18–19 Sep).
   - **B-PYUSD:** 1 day (18 Sep).

   Measured by the hour, though, the kBTC/PYUSD borrow rate sat above what the parked dollars earned for about 65–70 hours in total.

   **Excluding rewards, the A-legs were under water most of the time:**
   - A-RLUSD on 95 of 117 days;
   - A-PYUSD on 90 of 117 days.
4. **Rate spikes come from full Sentora V2 caps, and most are self-inflicted.**
   - **How often the caps were full:** the kBTC/RLUSD market was at ≥99% of its V2 cap on 70 of 127 days, and kBTC/PYUSD on 33.
   - **The caps rise in steps behind a 3-day timelock.** RLUSD went up in 10 steps (30M → 220M) and PYUSD in 7 (30M → 165M).
   - **The vault causes most spikes itself.** On 21 Aug, 24 Aug, 11 Sep, 14 Sep and 21 Sep the spike (9.6–13.75%) started within 0–2 minutes of a vault borrow of $9.8–23.9M into a full or just-raised cap. The vault then repaid part of it within 4 minutes to 6.6 hours.
   - **External spikes:** 12 Aug (8.7 hours, 9.6%) and 17–19 Sep (45 hours above 6%, which ended with the 19 Sep cap raise).
5. **Delevering reacts slowly to price.**
   - **Early June price drawdown:** all four kBTC positions reached 78.6–79.3% LTV (health factor about 1.09). The first repayments came **40–48 hours** after LTV breached the 71% target. That left a buffer of only about 7.8% of BTC price before liquidation.
   - **August–September repayments are mostly rate management:** trimming the vault's own borrow-to-cap within minutes to hours.
   - **Same-block automatic delevering, as claimed, was never observed.**
   - **The positions often run above target.** Each kBTC position spent 486–950 hours (17–34% of the time since launch) above the 71% target LTV.
6. **The Aave WBTC→USDT leg is the most fragile.** It runs at a health factor of about 1.20 against a 78% liquidation threshold.
   - It is liquidated by an **instant −18.6% move** (liquidation price $65,381).
   - An instant −20% move would also make PYUSD-1 liquidatable.
7. **Liquidity ladder at the snapshot** (debt $298.3M):
   - **Same block, from what is liquid right now (static):** 48.3%. This comes from V2 idle cash plus permissionless `forceDeallocate` (1 bp penalty).
   - **Same block, with repay-recycle:** 68.9%. Each repayment re-creates liquidity in the same market, which can then be withdrawn again.
   - **PRIME legs:** 31.1%. These need the Hastra operator and take 1–2 business days.

   The static tier alone covers the repayments needed to get back to target health factor even after a gradual −40% move. It does **not** prevent liquidations after an instant gap. The estimated worst-case liquidation bonus is $3.6M, $11.3M and $13.1M at −20%, −30% and −40% (est.).
8. **Depositors are 100% Kraken app distribution.**
   - **Wallet type:** 99.957% of holders (99.996% of BTC) are EIP-7702 accounts delegated to one ZeroDev Kernel implementation (`0xd6CEDDe8…`). These are the Privy embedded wallets. There are 15 plain EOAs (0.26 BTC) and **no Safes or DeFi contracts at all**.
   - **Size split:** 88.4% of holders hold under 0.1 BTC but own only 6.0% of the BTC. 85 wallets holding 10 BTC or more own 52.7%.
   - **Concentration:**
     - Top 1 wallet: 5.5% (352 BTC). It is a Kraken embedded wallet.
     - Top 10: 26.7%.
     - Top 100: 54.7%.
     - HHI: 104.
     - Median holding: 0.0037 BTC (about $300).
9. **Growth has been driven by flows, not yield.**
   - **Where the TVL came from** (weekly decomposition): of the $527.7M TVL on 20 Sep, net inflows contributed +$436M, the BTC price +$90M and yield +$1.4M.
   - **Scale:** 8,203 BTC deposited, 1,724 BTC withdrawn, and 48,776 wallets that have ever deposited (37,626 still hold).
   - **Flows do not follow yield.** Weekly net flow has almost no correlation with the previous week's realized APY (ρ = −0.01). It moves against same-week BTC returns (ρ = −0.43): deposits arrive on dips.
   - **The inflow is slowing:**
     - new depositors per week: 8,935 at launch → about 1,300 in September;
     - August gross withdrawals: 722 BTC;
     - first net-outflow week: 24 Aug, the week the performance fee was raised.
10. **Public claims check out on-chain.**
    - **$30M in 10 hours:** matched. Between 12:00 and 22:00 UTC on 27 May, 382 BTC (about $29M) came in.
    - **The "4,000 wallets" figure** was only reached the next morning. About 1,940 new wallets deposited in those 10 hours.
    - **Other milestones:** ">$100M" (1 Jun), ">$220M" (16 Jun) and "$320M+" (July) all match on-chain TVL.
    - **Payward's "~$400M" (14 Aug)** is about 9% above on-chain TVL on that day ($367M).
11. **Who earns what.**
    - **Kraken vault performance fees:** 5.50 kBTC so far (5.23 claimed in 8 biweekly claims plus 0.27 owed). The run-rate is about 21.6 kBTC/yr (about $1.87M/yr, 0.33% of TVL).
    - **Sentora's downstream fees** from its four V2 vaults run at about $7.0M/yr, of which about $1.1M/yr comes from the Kraken vault's own positions.
    - **The 15% payee of the vault's fee splitter** (`0xbE6b7dCa…3EDF3`) is also the fee recipient of all four Sentora V2 vaults, per their on-chain fee settings.
    - **Issuer-linked Merkl incentives** run at $31.1M/yr across those four V2 vaults. About $6.6M/yr of that lands on the Kraken vault's positions, **1.26% of vault NAV per year**. That is more than the entire net yield paid to depositors (about $5.3M/yr).
12. **New governance findings.**
    - **Penalty change on 20 Sep:** at 20:41–20:54 UTC Sentora raised the `forceDeallocatePenalty` on Sentora PRIME Main and Huma PST Main from 0 to 1%, with no timelock.
    - **Morpho WBTC/USDT leg:** between the snapshot and 21 Sep it went from 31% to 71% LTV ($2.24M → $5.19M debt) in a market at 95.7% utilization.

---

## A. Scope and snapshot (summary; details in Dossiers §4.1, Deep-Dive §1)

| Item | Value | Source |
|---|---|---|
| Vault NAV at snapshot | 6,492.5 BTC-equivalent (6,462.56 shares on Ink × rate 1.0046285); **all shares live on Ink** (Ethereum `totalSupply` = 0) | Ink replay of all 111,832 share transfers; matches `totalSupply` to the satoshi |
| NAV in USD | $521.2M at the Morpho oracle ($80,276); $566M at $86.6k on 21 Sep | Chainlink BTC/USD |
| Debt | $298.3M: kBTC legs $278.35M, Aave USDT $17.70M, Morpho WBTC/USDT $2.24M | archive reads |
| Holders | 37,572 at the snapshot (excluding the withdrawal queue, which held 35.25 BTC pending); 37,662 on Blockscout on 21 Sep | replay / Blockscout |
| Realized net yield | 1.41% since launch; 1.03% in September to date | accountant rate |

## B. Structure and legs (summary; details in Dossiers §4.1.1–4.1.2)

Deposits flow: Kraken app → Privy embedded wallet on Ink → vault. The kBTC is bridged to the vault's Ethereum copy (LayerZero) and runs six debt legs:

| Leg | Collateral → debt | Borrow venue | Where the stablecoins go |
|---|---|---|---|
| A-RLUSD | kBTC → RLUSD (position manager RLUSD-1 `0x0774…`) | Morpho kBTC/RLUSD | Sentora RLUSD Main (senRLUSDv2) |
| B-RLUSD | kBTC → RLUSD (RLUSD-2 `0x7fB9…`) | Morpho kBTC/RLUSD | PRIME, bought via 1inch |
| A-PYUSD | kBTC → PYUSD (PYUSD-1 `0xd18D…`) | Morpho kBTC/PYUSD | Paypal USD Main (senPYUSDmain) |
| B-PYUSD | kBTC → PYUSD (PYUSD-2 `0x1E8f…`) | Morpho kBTC/PYUSD | PRIME |
| C (since 3 Jul) | WBTC → USDT | Aave v3 (manager `0xf523…`) | swapped to PYUSD → Sentora PRIME Main |
| D (since 19 Sep) | WBTC → USDT | Morpho WBTC/USDT (`0x5EE1E2e3…f884`) | swapped to PYUSD → Sentora Huma PST Main |

The vault also holds a Uniswap v3 WBTC/kBTC LP position (267.9 BTC) and idle BTC. Neither is included in the carry model.

## C. Positions (summary; snapshot table in Dossiers §4.1.3)

| | RLUSD-1 | RLUSD-2 | PYUSD-1 | PYUSD-2 | Aave | Morpho WBTC/USDT |
|---|---|---|---|---|---|---|
| Snapshot LTV / health factor | 63.2% / 1.36 | 68.5% / 1.26 | 70.1% / 1.23 | 56.2% / 1.53 | health factor 1.228 | 31.1% |
| BTC price at which it liquidates | $58,956 | $63,914 | $65,401 | $52,465 | $65,381 | — |
| 21 Sep 22:33 (BTC $86.6k) | 65.2%, liquidates at $65,594 | 63.5% | 65.0% | 52.1% | health factor 1.323 | **66.7%** ($5.19M debt) |

RLUSD-1's liquidation price rose from $58,956 to $65,594 on 21 Sep. That day it borrowed 20.54M RLUSD with no new collateral and repaid only 6.5M (see E.5).

## D. Governance and security (summary; details in Dossiers §4.1.7)

The earlier findings still stand:
- a single EOA controls kBTC;
- the oracle is BTC/USD with no kBTC/BTC or proof-of-reserve feed;
- the vault's admin timelock is 1 hour;
- Sentora's V2 owner and curator are each a 1-of-1 Safe.

**New in this pass:**

- **Cap schedule.** All changes are `IncreaseAbsoluteCap`, each executed after a 3-day timelock:

  | Vault / market | Cap path |
  |---|---|
  | Sentora RLUSD Main, kBTC | 30M (18 May) → 50M (2 Jun) → 80M (8 Jun) → 100M (18 Jun) → 125M (7 Jul) → 145M (13 Jul) → 160M (27 Jul) → 175M (24 Aug) → 190M (2 Sep) → 205M (11 Sep) → **220M (21 Sep 15:39)** |
  | Paypal USD Main, kBTC | 30M (18 May) → 50M (2 Jun) → 80M (8 Jun) → 100M (24 Jun) → 120M (13 Jul) → 135M (19 Aug) → 150M (14 Sep) → **165M (19 Sep)** |
  | Sentora PRIME Main, PRIME | 20M (8 May) → … → 210M (14 Aug) |

- **Force-deallocate penalties.**
  - Set to **1 bp** on RLUSD Main and PYUSD Main on 20 Jul. This makes same-block exits from the V2 vaults permissionless.
  - Raised from **0 to 1%** on Huma PST Main (20 Sep 20:41) and PRIME Main (20 Sep 20:54). This was done with `Submit`+`Accept` in one block, i.e. no timelock.
  - Sentora can therefore reprice the emergency exit from these vaults at will.
- **Fee recipients.** The Kraken vault's PaymentSplitter pays 80/15/5 to three addresses (`0xb66e2948…`, `0xbE6b7dCa…3EDF3`, `0x68ec1fdd…`). The **15% payee is the performance/management fee recipient of all four Sentora V2 vaults**, read from the Morpho API and the V2 contracts. That makes it Sentora's fee address (inference). The 80% EOA and the 5% 2-of-3 Safe are unlabelled.
- **Fee mechanics confirmed.** A replay of all 151 accountant updates reproduces the fees. It uses 2500 bps (3333 bps from 24 Aug 12:32 UTC) on the increase of the **net** rate above the high-water mark, times shares outstanding.
  - Modeled accrual is 5.56 kBTC; actual is 5.50 kBTC claimed plus owed (a difference of −1.1%).
  - This confirms the fee equals 20% of gross before 24 Aug and 25% after.
  - The platform (management) fee is 0.

---

## E. Yield history since launch

**How each series is measured:**
- **Realized net:** accountant `ExchangeRateUpdated` events on Ink.
- **Borrow rates:** time-weighted `prevBorrowRate` from every Morpho `AccrueInterest` event (599 events for kBTC/RLUSD, 950 for kBTC/PYUSD, 25,592 for WBTC/USDT). The Aave rate comes from `variableBorrowIndex` growth between daily archive reads.
- **Deployment organic yield:** growth of the V2 share price between daily archive reads. This is net of Sentora's V2 fees, i.e. what the vault actually receives.
- **Reward APR:** Merkl campaign budget (weekly RLUSD/PYUSD amounts) divided by average V2 `totalAssets`, capped at the campaigns' `MAX_APR` of 3.9%. The budget, not the cap, binds.
- **PRIME:** Chainlink PRIME/wYLDS feed `0xf17C0Edc…58d1`.
- **Weighted spread:** debt-weighted (deployment yield − borrow cost) across the legs.
- **Model net on NAV:** weighted spread × debt / NAV ÷ the fee gross-up (1.25 before 24 Aug, 1.333 after).

### E.1 Monthly (APY, %)

| Month | Realized net | Borrow kBTC/RLUSD | Borrow kBTC/PYUSD | Borrow Aave USDT | RLUSD Main total (organic) | Paypal USD Main total (organic) | PRIME | PRIME Main total (organic) | Weighted spread | Organic spread | Model net on NAV (no rewards) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05 (from 27 May) | 0.42* | 2.49 | 0.76 | – | 5.26 (1.81) | 5.14 (1.69) | 7.25 | – | 3.62 | 0.30 | 1.47 (0.12) |
| 2026-06 | **1.80** | 1.60 | 1.20 | – | 5.64 (1.78) | 5.02 (1.71) | 6.07 | – | 4.11 | 1.29 | 1.90 (0.59) |
| 2026-07 | **1.37** | 3.09 | 3.08 | 3.70 | 6.28 (2.55) | 5.14 (2.02) | 7.04 | 6.53 (3.52) | 3.09 | 0.63 | 1.61 (0.33) |
| 2026-08 | **1.30** | 3.43 | 3.49 | 3.92 | 6.41 (2.80) | 5.82 (2.33) | 6.48 | 6.42 (3.95) | 2.83 | 0.43 | 1.35 (0.21) |
| 2026-09 (1–20) | **1.03** | 3.07 | 3.97 | 4.29 | 6.00 (2.55) | 5.73 (2.78) | 5.89 | 6.11 (3.63) | 2.48 | 0.27 | 1.05 (0.12) |
| Since launch (27 May–20 Sep) | **1.41** | 2.73 | 2.74 | 3.78 | 6.02 (2.38) | 5.38 (2.14) | 6.40 | 6.41 (3.54) | 3.24 | 0.82 | 1.51 (0.38) |

\* The May row covers the whole calendar month, including the pre-launch weeks with almost no debt. Launch week alone was 1.16%.

**Other deployment venues:**
- **Huma PST Main** (September, leg D): 8.35% total, 5.15% organic.
- **Morpho WBTC/USDT borrow:** 3.45% (September average), but about 10% on 21 Sep at 95.7% utilization.

**Reward APR** (budget ÷ TVL):
- RLUSD Main: 3.45–3.86%.
- Paypal USD Main: 2.95–3.49%.
- PRIME Main: about 2.6% (also PYUSD, from the same Sentora Safe).
- Huma PST Main: about 3.0%.

**Why the borrow rate was low early:** IRM `rateAtTarget`, read on-chain:

| Date | kBTC/RLUSD | kBTC/PYUSD |
|---|---|---|
| 20 Apr | 4.07% | 4.05% |
| 18 May | 4.07% | 0.65% |
| 27 May (launch) | 1.90% | 0.62% |
| 8 Jun | 1.71% | 0.54% |
| 22 Jun | 1.38% | 0.76% |
| 6 Jul | 1.83% | 1.57% |
| 3 Aug | 2.88% | 2.68% |
| 20 Sep | 3.07% | 3.73% |

The June yield of 1.8% (Sentora's "1.8% 30-day") was therefore helped by an IRM that had decayed during the pre-launch idle weeks. It was not a sustainable spread.

### E.2 Weekly (APY, %; full columns in `yield_weekly.csv`)

| Week (Mon) | Net | Borrow RLUSD | Borrow PYUSD | RLUSD Main tot/org | PYUSD Main tot/org | PRIME | W. spread | Org. spread | Debt $M | Debt/NAV | Model net (no rew.) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-25 | 1.16 | 1.79 | 0.56 | 4.98 / 1.64 | 5.06 / 1.66 | 6.10 | 3.82 | 0.56 | 28 | 0.51 | 1.56 (0.23) |
| 2026-06-01 | 1.15 | 1.59 | 0.53 | 5.47 / 1.77 | 5.08 / 1.62 | 5.85 | 4.26 | 0.99 | 62 | 0.45 | 1.54 (0.36) |
| 2026-06-08 | **2.16** | 1.39 | 0.56 | 5.70 / 1.79 | 4.98 / 1.45 | 5.85 | 4.48 | 1.50 | 103 | 0.53 | 1.89 (0.63) |
| 2026-06-15 | 2.04 | 1.40 | 1.37 | 5.61 / 1.65 | 4.86 / 1.67 | 6.33 | 4.15 | 1.39 | 137 | 0.61 | 2.02 (0.68) |
| 2026-06-22 | 1.97 | 1.82 | 2.03 | 5.72 / 1.83 | 5.12 / 1.98 | 6.33 | 3.75 | 1.01 | 148 | 0.62 | 1.85 (0.50) |
| 2026-06-29 | 1.34 | 2.79 | 2.76 | 6.32 / 2.33 | 5.40 / 2.20 | 5.92 | 3.15 | 0.45 | 158 | 0.59 | 1.49 (0.22) |
| 2026-07-06 | 1.47 | 2.98 | 3.07 | 6.18 / 2.41 | 5.08 / 2.01 | 7.87 | 3.27 | 0.69 | 177 | 0.60 | 1.58 (0.33) |
| 2026-07-13 | 1.39 | 3.04 | 3.01 | 6.11 / 2.54 | 4.89 / 1.91 | 7.34 | 3.06 | 0.56 | 201 | 0.65 | 1.60 (0.30) |
| 2026-07-20 | 1.37 | 3.02 | 3.17 | 6.22 / 2.59 | 4.97 / 1.90 | 6.76 | 2.95 | 0.50 | 216 | 0.65 | 1.53 (0.26) |
| 2026-07-27 | 1.28 | 3.71 | 3.14 | 6.71 / 2.90 | 5.64 / 2.09 | 6.96 | 3.05 | 0.47 | 222 | 0.63 | 1.54 (0.24) |
| 2026-08-03 | 1.53 | 3.12 | 3.02 | 6.25 / 2.55 | 6.06 / 2.00 | 7.00 | 3.34 | 0.70 | 231 | 0.64 | 1.70 (0.36) |
| 2026-08-10 | 1.72 | 3.29 | 3.46 | 6.22 / 2.64 | 6.01 / 2.34 | 6.85 | 3.00 | 0.59 | 239 | 0.65 | 1.55 (0.30) |
| 2026-08-17 | 1.06 | 3.78 | 3.99 | 6.77 / 3.18 | 5.78 / 2.50 | 6.41 | 2.55 | 0.30 | 244 | 0.59 | 1.20 (0.14) |
| 2026-08-24 | **0.94** | 3.33 | 3.66 | 6.28 / 2.77 | 5.57 / 2.59 | 5.68 | 2.41 | 0.24 | 255 | 0.55 | 1.00 (0.10) |
| 2026-08-31 | 1.04 | 3.10 | 3.84 | 6.12 / 2.57 | 5.87 / 2.95 | 5.73 | 2.52 | 0.35 | 264 | 0.55 | 1.04 (0.14) |
| 2026-09-07 | 1.09 | 3.06 | 3.44 | 6.01 / 2.56 | 5.73 / 2.69 | 5.83 | 2.64 | 0.50 | 274 | 0.56 | 1.10 (0.21) |
| 2026-09-14 | 0.97 | 3.07 | **4.55** | 5.87 / 2.51 | 5.55 / 2.66 | 6.08 | 2.28 | 0.13 | 291 | 0.58 | 0.99 (0.05) |

The "Debt $M" column includes all legs with more than $0.1M of debt. The weighted spread fell almost monotonically, from 4.48 to 2.28, while debt/NAV stayed at 0.55–0.65. **Leverage did not change; the spread did.**

### E.3 Stability

**Realized net, weekly** (17 weeks from 25 May):
- Mean 1.39%, standard deviation 0.38 pp.
- Best week 2.16% (8 Jun); worst week **0.94% (24 Aug)**.

**Realized net, monthly** (June–September): standard deviation 0.32 pp, falling steadily (1.80 → 1.37 → 1.30 → 1.03).

**Per update:** the accountant posted 117 rate updates since launch, roughly one a day. Annualized:
- range 0.10%–4.27%;
- median 1.28%;
- the rate never decreased.

The share price is a **managed, harvest-based rate**: ±0.5% per update, at most one update every 6 hours. It is not marked to market. Intraday negative carry and changes in PRIME's NAV only show up through smaller increments, never as a drawdown.

### E.4 Carry P&L by leg since launch (daily model, est.)

Daily debt × (7-day trailing deployment yield − daily average borrow), summed from 27 May to 20 Sep:

| Leg | Average debt | Carry incl. rewards | Organic only | Rewards |
|---|---|---|---|---|
| A-RLUSD → RLUSD Main | $83.5M | +$0.85M | **−$0.12M** | $0.98M |
| B-RLUSD → PRIME | $30.6M | +$0.31M | +$0.31M | 0 |
| A-PYUSD → Paypal USD Main | $47.9M | +$0.38M | **−$0.12M** | $0.50M |
| B-PYUSD → PRIME | $29.1M | +$0.29M | +$0.29M | 0 |
| C Aave USDT → PRIME Main | $11.8M (80 days) | +$0.06M | −$0.01M | $0.07M |
| D WBTC/USDT → PST | new | ≈0 | ≈0 | ≈0 |
| **Total** | | **$1.89M** | **$0.35M** | **$1.54M (82%)** |

**Check against realized:** 20.6 BTC of yield went to depositors and 5.5 kBTC to fees, about 26 BTC at $70–75k, i.e. about $1.9M. That matches the model.

**Monthly carry incl. rewards / organic only:**

| Month | Incl. rewards | Organic only |
|---|---|---|
| June | $0.40M | $0.12M |
| July | $0.51M | $0.08M |
| August | $0.60M | $0.10M |
| September (1–20) | $0.37M | $0.04M |

### E.5 Negative-carry periods

**Negative-carry days since 27 May.** A day counts when the daily average borrow rate exceeds the leg's 7-day trailing deployment yield.

| Leg | Days with debt | Negative incl. rewards | Negative excl. rewards | Hours borrow > total deployment yield | Hours borrow > organic yield |
|---|---|---|---|---|---|
| A-RLUSD | 117 | 0 | **95** | 6.4 | 2,272 |
| B-RLUSD | 111 | 0 | 0 | 6.7 | 6.7 |
| A-PYUSD | 117 | **2** (18 Sep: 6.58% vs 5.55%; 19 Sep: 5.75% vs 5.59%) | **90** | 70.4 | 2,137 |
| B-PYUSD | 114 | **1** (18 Sep: 6.58% vs PRIME 6.04%) | 1 | 65.3 | 65.3 |
| C Aave | 80 | 0 | 52 | n/a (daily index only) | n/a |

**Spike episodes** (kBTC markets, borrow above 6%; the full list is in `raw/analysis_yield.json` → `spikes`):

| When (UTC) | Market | Duration | Peak | Cause and response |
|---|---|---|---|---|
| 12 Aug 08:13–16:56 | kBTC/PYUSD | 8.7 h | 9.6% | **External** (no vault borrow). PYUSD-1 repaid $6.4M and withdrew 142 kBTC at 16:57 |
| 21 Aug 07:44–14:19 | kBTC/PYUSD | 6.6 h | 11.8% | **Self-inflicted:** PYUSD-1 borrowed $9.8M at 07:44 (two days after the cap went to 135M) and repaid the same $9.8M, withdrawing 180 kBTC, at 14:19 |
| 24 Aug 20:06–21:10 | kBTC/RLUSD | 1.0 h | **13.75%** | **Self-inflicted:** cap raised to 175M at 15:49; RLUSD-1 borrowed $16.0M + $7.8M at 20:05–20:08 and repaid $11.1M at 21:09 |
| 11 Sep 22:21–22:42 | kBTC/RLUSD | 0.3 h | 7.7% | **Self-inflicted:** RLUSD-1 borrowed $8.8M at 22:20 and $15.1M at 22:36 (cap raised to 205M at 22:31); repaid $10.0M at 22:41 |
| 14 Sep 14:11 and 19:57 | kBTC/PYUSD | minutes | 12.9–13.6% | **Self-inflicted:** PYUSD-1 borrowed $14.3M at 14:09 and repaid $15.0M at 14:13; borrowed $15.8M at 19:56, the same minute the cap went to 150M |
| 17 Sep 19:10 – 19 Sep 16:12 | kBTC/PYUSD | **45 h** | 6.9% | **External**, with the cap full (no vault action). Ended when the cap was raised 150M → 165M (19 Sep 16:03) |
| **21 Sep 13:50–15:43** | kBTC/RLUSD | 1 h 53 min | **12.93%** | **Self-inflicted:** RLUSD-1 borrowed 20.54M without collateral into a full cap; cap raised to 220M at 15:39; repaid 6.5M at 19:10 |

**21 Sep in detail** (kBTC/RLUSD): 3.07% (00:00–13:50) → 12.93% → 6.24% (15:43–19:01) → 3.48% (after 19:06). The day's time-weighted average was 4.55%, against 6.0% total and 2.5% organic on RLUSD Main.

**Share of time above a given borrow rate since launch:**

| Market | Above 5% | Above 6% | Above 8% | Above 10% |
|---|---|---|---|---|
| kBTC/RLUSD | 1.98% | 0.43% | 0.10% | 0.07% |
| kBTC/PYUSD | 4.01% | 2.31% | 0.36% | 0.26% |
| WBTC/USDT (leg D's market, structurally tight) | 17.9% | 10.9% | 4.1% | 2.0% |

**Why the spikes happen.** The kBTC market's supply comes almost entirely from the Sentora V2 adapters (at least 99.999%), and V2 supply is capped. When the cap is full, any new borrow or rebalance pushes utilization toward 100% and the curve toward 12.9% (RLUSD) or 15.8% (PYUSD).

The executor's pattern is:
1. borrow the available headroom, often the minute a cap raise executes;
2. let the rate spike;
3. trim the excess within minutes to hours.

The spike cost falls on all of the vault's debt in that market, not only on the new tranche. **The lender is captive, the cap is the throttle, and the throttle has a 3-day timelock.**

---

## F. Risk management

### F.1 LTV per position over time (Monday 00:00 UTC; full table in `ltv_weekly.csv`)

| Date | BTC | RLUSD-1 LTV / liquidation price | RLUSD-2 | PYUSD-1 | PYUSD-2 | kBTC legs total | Aave health factor / liquidation price |
|---|---|---|---|---|---|---|---|
| 25 May | 76,790 | 71.0% / 63,397 | – | 71.8% / 64,104 | – | 71.1% | – |
| 1 Jun | 73,651 | 71.1% / 60,911 | – | 70.8% / 60,645 | 70.6% / 60,470 | 71.0% | – |
| 8 Jun | 63,147 | 66.4% / 48,779 | 29.6% | 66.4% / 48,763 | 52.7% | 61.3% | – |
| 22 Jun | 63,352 | 70.1% / 51,674 | 56.1% | 72.1% / 53,133 | 60.9% | 67.8% | – |
| 29 Jun | 59,486 | 71.1% / 49,179 | 54.1% | **72.8%** / 50,352 | 68.6% | 69.3% | – |
| 13 Jul | 63,743 | 70.4% / 52,184 | 65.2% | 71.1% / 52,672 | 64.6% | 69.2% | – |
| 3 Aug | 63,456 | 72.1% / 53,210 | 73.0% | 71.4% / 52,721 | 72.3% | **72.1%** | 2.12 |
| 17 Aug | 62,874 | **73.2%** / 53,523 | 72.8% | 72.1% | 72.1% | **72.7%** | 1.199 / 52,455 |
| 24 Aug | 77,561 | 59.4% / 53,547 | 59.1% | 70.2% / 63,320 | 58.1% | 61.1% | 1.207 / 64,252 |
| 14 Sep | 76,800 | 66.0% / 58,943 | 71.6% / 63,907 | 69.8% / 62,313 | 58.7% | 66.3% | **1.173** / 65,449 |
| 20 Sep 12:00 | 80,276 | 63.2% / 58,956 | 68.5% / 63,914 | 70.1% / 65,401 | 56.2% / 52,465 | 64.3% | 1.228 / 65,381 |
| 21 Sep 22:33 | 86,573 | 65.2% / 65,594 | 63.5% | 65.0% / 65,408 | 52.1% | 62.6% | 1.323 / 65,416 |

**Intraday path.** This is rebuilt from the daily archive state, every collateral, borrow and repay event (706), and 4,958 Chainlink BTC/USD rounds.

**Peak LTV per position:**

| Position | Peak LTV | When (UTC) |
|---|---|---|
| RLUSD-1 | **79.24%** | 4 Jun 00:27 |
| RLUSD-2 | **79.27%** | 4 Jun 00:26 |
| PYUSD-1 | 78.60% | 2 Jun 19:33 |
| PYUSD-2 | 79.05% | 3 Jun 03:43 |

At those peaks the health factor was about 1.085. A further **−7.8%** BTC move (to about $58.9k) would have hit the 86% LLTV. BTC's later intraday low of $57,783 (1 Jul 01:13) came after the positions had delevered.

**Hours above each LTV level** (about 2,808 hours since launch):

| Position | Above 71% (target) | Above 75% | Above 78% | Above 80% |
|---|---|---|---|---|
| RLUSD-1 | 950 h | 27 h | 1.4 h | 0 |
| RLUSD-2 | 841 h | 33 h | 2.2 h | 0 |
| PYUSD-1 | 911 h | 13 h | 0.4 h | 0 |
| PYUSD-2 | 486 h | 16 h | 2.3 h | 0 |

The positions are operated **at** the target, not below it. Every BTC dip therefore pushes them over.

**BTC path since launch** (Chainlink): the worst moves were:

| Window | Worst move | Ending |
|---|---|---|
| 1 h | −4.9% | — |
| 4 h | −5.9% | — |
| 24 h | −8.8% | — |
| 48 h | −13.3% | 4 Jun 02:04 |
| 7 days | **−20.0%** | 5 Jun, $74,082 → $59,238 |
| 30 days | −28.2% | — |

At target LTV the buffer to LLTV is 17.4% (1 − 71.0/86). That is more than the worst 48-hour move but less than the worst 7-day move.

### F.2 Delever events and reaction lag

| Repayment (UTC) | Position | Amount | LTV just before | BTC vs 7-day high | Lag from target-LTV breach | Lag from rate-spike start | Trigger |
|---|---|---|---|---|---|---|---|
| 3 Jun 03:44 | PYUSD-2 | $0.19M | 79.1% | −13.2% | **45.4 h** | – | price |
| 4 Jun 00:26–00:27 | RLUSD-2 / RLUSD-1 | $0.26M / $4.22M | 79.3% / 79.2% | −14.0% | **48.4 h / 46.7 h** | – | price |
| 4 Jun 03:01–03:37 | PYUSD-1, RLUSD-1, PYUSD-2, RLUSD-2 | $3.22M, $2.58M, $0.30M, $0.06M | 70.5–73.1% | −14.5% | 2–5 h (second breach) | – | price |
| 24 Jun 14:19 | RLUSD-1 + PYUSD-1 | $3.44M + $2.58M | 74.9% | −7.6% | **40.3 h** | – | price |
| 1 Jul 14:14 | RLUSD-1 | $5.30M | 70.9% | −3.6% | none (pre-emptive, near the BTC low) | – | price |
| 12 Aug 16:57 | PYUSD-1 (+142 kBTC withdrawn) | $6.44M | 71.5% | −2.9% | 2.9 h | **8.7 h** | external rate spike |
| 21 Aug 14:19 | PYUSD-1 (+180 kBTC withdrawn) | $9.80M | 70.9% | −1.4% | – | 6.6 h | unwinding its own $9.8M borrow of 07:44 |
| 24 Aug 21:09 | RLUSD-1 | $11.12M | 70.6% | −0.6% | – | 1.1 h | trimming its own $23.8M borrow |
| 4 Sep 14:05 / 15:52 | PYUSD-1 (+49 kBTC withdrawn) | $0.96M / $2.50M | 68.5–71.1% | −2.6% | 1.5 h | – | rebalance |
| 11 Sep 22:41 | RLUSD-1 | $10.00M | 71.0% | −4.0% | 0.1 h | 0.3 h | trimming its own $23.9M borrow |
| 14 Sep 14:13 | PYUSD-1 | $14.99M | 71.0% | −2.0% | – | 0.1 h | unwinding its own $14.3M borrow of 14:09 |
| 21 Sep 19:10 | RLUSD-1 | $6.50M | 68.6% | −0.1% | – | 5.4 h | trimming its own $20.5M borrow |

**Reading.**
- **Price-driven delevering reacted with a lag of about 2 days in June.** The positions sat at 75–79% LTV for 13–33 hours before any repayment.
- **Only one repayment answered an external rate spike:** 12 Aug, 8.7 hours after the spike started. After July, almost every other repayment trims the vault's own borrow-to-cap. Some were paired with collateral withdrawals, i.e. moving kBTC to other legs.
- **Sentora's "same-block" autonomous delevering was never observed.** Every repayment is a separate executor transaction, and none followed a price move within the same block.
- **No liquidations** of vault positions.

### F.3 Liquidity ladder at the snapshot (`liquidity_ladder.csv`)

The debt is **$298.30M**. The vault's claims:
- senRLUSDv2: $124.85M;
- senPYUSDmain: $60.82M;
- PRIME: $92.70M;
- Sentora PRIME Main: $17.69M;
- Huma PST Main: $2.24M.

RLUSD Main and PYUSD Main have **no liquidity adapter**, so ordinary withdrawals come from idle cash only. `forceDeallocate` is permissionless at a 1 bp penalty, so any market liquidity can be pulled into idle within the same transaction.

| Tier | Repayable | % of debt | Cumulative | Source |
|---|---|---|---|---|
| T1a: same block, static | $63.28M | 21.2% | 21.2% | RLUSD Main: idle $29.44M + deallocatable market liquidity $33.84M (kBTC/RLUSD $20.57M, weETH $10.44M, …) → RLUSD-1 |
| T1a | $60.82M | 20.4% | 41.6% | Paypal USD Main: idle $21.74M + $53.28M deallocatable (kBTC/PYUSD $25.84M, sUSDe $11.15M, …), which covers all of PYUSD-A → PYUSD-1 |
| T1a (needs a PYUSD→USDT swap) | $17.69M | 5.9% | 47.5% | PRIME Main: idle $3.73M + PRIME/PYUSD liquidity $20.03M → Aave USDT |
| T1a (needs a swap) | $2.24M | 0.8% | **48.3%** | Huma PST Main: PST/PYUSD liquidity $4.50M → Morpho WBTC/USDT |
| T1b: same block or minutes, repay-recycle | $61.55M | 20.6% | **68.9%** | Each repayment into kBTC/RLUSD re-creates the same market liquidity, which the V2 can deallocate again (flash loan or a few executor transactions plus Sentora's allocator) |
| T2: within 1 day | $0 committed | 0% | 68.9% | Capacity only: PRIME sold on DEX (Uniswap v3 PRIME/USDC, about $9.0M TVL) or posted to Morpho PRIME/PYUSD (liquidity $20.0M, shared with Sentora PRIME Main exits) |
| T3: 1–7 days | $92.70M | 31.1% | 100% | PRIME → wYLDS (instant) → USDC via the Hastra operator, 1–2 business days. The on-chain payout wallet holds about $85k |
| T4: longer or uncertain | $0 (base case) | – | – | Only if other V2 depositors drain the liquidity first, or Hastra/Figure cannot meet $92.7M |

**Caveats.**
- T1 assumes nobody else withdraws first. RLUSD Main and PYUSD Main also hold about $619M of non-Kraken deposits ($830M across all four V2 vaults).
- Using T1 proceeds for the PRIME legs assumes the Merkle root lets the strategist route the A-leg's RLUSD or PYUSD to RLUSD-2 or PYUSD-2. The contracts allow it technically; the root was not decoded.
- On 21 Sep the static T1 was similar:
  - RLUSD Main: idle $25.24M + $34.2M deallocatable;
  - PYUSD Main: idle $21.31M + $36.3M.

### F.4 Stress test: instant BTC shocks from the snapshot ($80,276)

| Shock | BTC | LTV RLUSD-1 / RLUSD-2 / PYUSD-1 / PYUSD-2 | Aave health factor | Liquidatable immediately | Repayment to restore target health factor (1.2113; Aave 1.20) | RLUSD needed vs static T1 | PYUSD needed vs static T1 | Max liquidation bonus if liquidated first (est.) |
|---|---|---|---|---|---|---|---|---|
| −10% | 72,248 | 70.2 / 76.1 / 77.8 / 62.4 | 1.105 | none | $10.2M | $3.4M vs $63.3M | $5.4M vs $60.8M | 0 |
| −20% | 64,221 | 78.9 / 85.6 / **87.6** / 70.3 | **0.982** | PYUSD-1, Aave | $36.0M | $21.3M vs $63.3M | $11.5M vs $60.8M | $3.6M |
| −30% | 56,193 | **90.2 / 97.8 / 100.1** / 80.3 | **0.859** | RLUSD-1, RLUSD-2, PYUSD-1, Aave | $68.1M | $40.6M vs $63.3M | $22.5M vs $60.8M | $11.3M |
| −40% | 48,166 | **105.3 / 114.1 / 116.8 / 93.7** | **0.737** | all four kBTC legs + Aave | $100.7M | $59.9M vs $63.3M | $33.9M vs $60.8M | $13.1M |

The Morpho WBTC/USDT leg (31% LTV at the snapshot) survives every shock. At its 21 Sep level of about 67–71% it would fail at −20%.

**Answer.** For a gradual decline, static tier 1 alone covers the repayments needed to restore target health factor even at −40%, with a thin RLUSD margin ($59.9M needed vs $63.3M available). For an instant gap it does not help:
- at −20%, PYUSD-1 and the Aave leg are liquidatable before any transaction;
- at −30%, three of the four kBTC legs are too.

The liquidation bonus is 4.38% at 86% LLTV and about 5% on Aave WBTC. The bonus-cost column assumes the whole debt of each liquidatable position is liquidated.

Given the 40–48-hour reaction seen in June, the operative risk is a **2–3 day slide of more than 17%**, which the 7-day record (−20%) shows is plausible.

---

## G. Depositors (Ink, snapshot 20 Sep 12:00)

The balances come from a full replay of 111,832 share transfers. The replay reproduces `totalSupply` exactly. BTC-equivalent = shares × 1.0046285. Blockscout's paginated holder list (754 pages, 37,663 rows, 21 Sep about 22:00) was used to classify addresses.

### G.1 Buckets (`holders_buckets.csv`)

| Bucket (BTC) | Holders | % holders | BTC | % BTC | Average BTC |
|---|---|---|---|---|---|
| < 0.001 | 12,493 | 33.25 | 4.18 | 0.06 | 0.00033 |
| 0.001–0.01 | 11,015 | 29.32 | 43.33 | 0.67 | 0.0039 |
| 0.01–0.1 | 9,698 | 25.81 | 341.77 | 5.29 | 0.035 |
| 0.1–1 | 3,557 | 9.47 | 1,010.69 | 15.65 | 0.284 |
| 1–10 | 724 | 1.93 | 1,655.88 | 25.64 | 2.29 |
| 10–100 | 77 | 0.20 | 1,804.13 | 27.94 | 23.4 |
| > 100 | 8 | 0.02 | 1,597.25 | 24.74 | 199.7 |
| **Total** | **37,572** | | **6,457.22** | | 0.172 (median 0.0037) |

**Concentration:**
- Top 1: 5.46% (352.5 BTC).
- Top 10: 26.66% (352, 301, 201, 186, 175, 144, 138, 100, 63 and 61 BTC).
- Top 100: 54.72%.
- Top 1,000: 80.83%.
- **HHI: 104** (unconcentrated by the usual 1,500 threshold, but a long-tailed book).

Another 35.25 BTC sat in the withdrawal queue.

**Retail vs whale vs institutional** (by size; there is no on-chain institutional wrapper):

| Segment | Holders (% of holders) | BTC (% of BTC) |
|---|---|---|
| Retail, under 0.1 BTC | 33,206 (88.4%) | 389 (6.0%) |
| Upper retail, 0.1–1 | 3,557 (9.5%) | 1,011 (15.7%) |
| High net worth, 1–10 | 724 (1.9%) | 1,656 (25.6%) |
| Whales / institutional size, 10 or more | 85 wallets (0.23%) | 3,401 (**52.7%**) |

### G.2 Address types (`holders_types.csv`)

| Type (on-chain code) | Holders | % | BTC | % BTC |
|---|---|---|---|---|
| EIP-7702 (`0xef0100` + delegate) → ZeroDev **Kernel `0xd6CEDDe8…5b28`** (Kraken/Privy embedded wallets) | 37,556 | 99.957 | 6,456.96 | 99.996 |
| Plain EOA | 15 | 0.040 | 0.26 | 0.004 |
| EIP-7702 → AmbireAccount7702 | 1 | 0.003 | 0.00 | 0 |
| Safe / multisig / other contract | **0** | 0 | 0 | 0 |

Addresses 1–10 are all embedded Kernel wallets. The 431 snapshot holders who had exited before the Blockscout pull were classified by `eth_getCode` at the snapshot block; all 431 are Kernel wallets.

**Reading:**
- The vault has **no DeFi-native or institutional on-chain holders**, no composability and no secondary market.
- Every whale is a Kraken account (the $30M+ wallets included), so "institutional" can only be inferred from size.
- The 15 plain EOAs are dust. They may be exported embedded keys or direct Teller users.

### G.3 Holders and flows over time (weekly in `tvl_weekly.csv`)

**Holders at month end:**

| Month end | Holders |
|---|---|
| May | 10,575 |
| June | 24,768 |
| July | 31,219 |
| August | 35,482 |
| 20 Sep | 37,626 |

**Lifetime:** 48,776 depositing addresses by 20 Sep, so 11,150 (22.9%) have fully exited. There were 94,886 deposit transactions, averaging 0.09 BTC.

**Monthly net inflows (BTC):**

| Month | Deposits | Withdrawals | Net | New depositors |
|---|---|---|---|---|
| May | 1,359.6 | 23.9 | **+1,335.7** | 10,940 |
| June | 3,369.4 | 350.9 | **+3,018.6** | 16,644 |
| July | 1,608.5 | 443.7 | **+1,164.8** | 9,226 |
| August | 1,122.3 | 721.7 | **+400.5** | 7,885 |
| September (1–20) | 740.6 | 184.1 | **+556.4** | 4,060 |

Withdrawals are measured at the solver's burn, which settles about twice a day.

---

## H. TVL growth (`tvl_weekly.csv`)

TVL = Ink share supply × accountant rate; in USD, × Chainlink BTC/USD at the end of each period. The USD change is split into flows (net BTC flow × end price), BTC price (starting BTC TVL × price change) and yield.

| Month | TVL end, BTC | TVL end, $M | ΔTVL $M | = flows | + BTC price | + yield |
|---|---|---|---|---|---|---|
| May | 1,338.5 | 98.6 | +98.4 | +98.4 | −0.0 | +0.02 |
| June | 4,362.0 | 255.3 | +156.7 | +176.7 | −20.2 | +0.29 |
| July | 5,532.4 | 347.5 | +92.2 | +73.2 | +18.7 | +0.36 |
| August | 5,939.3 | 466.5 | +118.9 | +31.5 | +87.0 | +0.50 |
| 1–20 Sep | 6,499.3 | 527.7 | +61.3 | +45.2 | +15.8 | +0.29 |

**Cumulative** (sum of weekly effects, 9 Apr → 20 Sep end of day):

| Driver | Contribution | Share |
|---|---|---|
| Flows | **+$436.4M** | 82.7% |
| BTC price | +$89.9M | 17.0% |
| Yield | +$1.4M | 0.3% |
| **Total TVL** | **$527.7M** | |

In BTC terms: +6,478.6 BTC of net flows and +20.65 BTC of yield.

**Weekly highlights:**

| Week of | Net flow | New depositors / TVL | Note |
|---|---|---|---|
| 18 May | +102 BTC | 2,001 new depositors | Pre-launch |
| 25 May | +1,233 BTC | 8,935 new depositors | Launch |
| 1 Jun | +1,356 BTC | TVL $170M | BTC −14% that week |
| 8 Jun | +655 BTC | TVL $220M | |
| July | +174 to +467 BTC per week | | |
| 10 Aug | +66 BTC | | |
| 24 Aug | **−59 BTC** | | 260 BTC withdrawn |
| 31 Aug | +307 BTC | | |
| 7 Sep | +46 BTC | | |
| 14 Sep | +219 BTC | | |

**Public claims vs on-chain TVL** (end of day):

| Date | Claim | On-chain |
|---|---|---|
| 27 May | "$30M in 10 hours" (Veda/Cointelegraph) | +382 BTC (about $29M) between 12:00 and 22:00 UTC; day-end TVL $47.3M (previous day $14.3M). The 4,000th wallet was reached around the morning of 28 May, not within 10 hours |
| 29 May | "> $70M" (Sentora on X, secondary source) | $79.5M |
| 1 Jun | "Over $100M" (Kraken on X, search snippet) | $124.8M (previous day $98.6M) |
| 10 Jun | "> $100M, 12,000+ users" (Veda blog) | $195.8M, 17,376 holders |
| 16 Jun | "> $220M in < 3 weeks" (Veda on X, snippet) | $224.8M |
| July | "$320M+" (Sentora case study) | $347.5M (31 Jul) |
| 14 Aug | "~$400M" (Payward Q2 release) | **$367.4M**, about 9% below the claim (possibly gross deposits or a different date) |

---

## I. Growth drivers (full dated list in `events.csv`: 78 rows, on-chain + primary + secondary)

**Timeline aligned with TVL:**

| Date | Event | TVL / flows |
|---|---|---|
| 26 Jan | DeFi Earn launches (Veda, USDC vaults) | – |
| 26 Feb | Vault deployed on Ink | 0 |
| 9 Apr | First deposit | – |
| 17 Apr | kBTC markets created. The IRM starts decaying while the markets sit idle | – |
| 18 May | kBTC caps of 30M set; **pre-launch deposits** | +102 BTC, 2,001 wallets that week |
| 27 May | **Public launch** on app, Pro, web and Krak: "up to 2.5%", 5-day exit, 100+ countries, BTC purchase built into the deposit flow (Veda) | +382 BTC in 10 h; $98.6M by 31 May |
| 2–8 Jun | Caps 50M → 80M; BTC falls 20% in 7 days | Record +1,356 BTC week (deposits into the dip); first delever 3–4 Jun |
| 9–10 Jun | FIFA World Cup sponsorship (brand); Veda "$400M Kraken Earn" | +655 BTC |
| 19 Jun–31 Jul | EEA €1M deposit sweepstakes (vault allocations excluded) | – |
| July | Caps 100–160M; Aave leg added; Sentora case study "1.8% 30-day"; Veda CEO "BTC vault is the inflection point" | +1,165 BTC |
| 14 Aug | Payward Q2: BTC vault about $400M, to anchor "vaults-as-a-service" | – |
| 24 Aug | **Performance fee 2500 → 3333 bps** (no announcement) and first net-outflow week | −59 BTC |
| 2 Sep | Support article: 3-day exit | – |
| 3 Sep | Sentora's Euler incentive programmes end | – |
| 14 Sep | xStocks vaults (same rails); "DeFi Earn > $800M" | +219 BTC |
| 19–21 Sep | Caps 165M / 220M; PYUSD 45-hour spike; RLUSD loop at 12.93% | – |

**What explains the growth.**
1. **Distribution, not rate.**
   - Weekly net flows show no relationship with the previous week's realized APY (ρ = −0.01, n = 16).
   - They are negatively related to the same week's BTC return (ρ = −0.43). Daily deposits vs daily BTC return: ρ = −0.16.
   - The biggest weeks (+1,233 and +1,356 BTC) coincided with launch publicity and a BTC drawdown, not with peak yield. The peak yield came two weeks later (2.16% in the week of 8 Jun).
   - Deposits kept arriving at 170–470 BTC a week while yield fell from about 2% to about 1%.
2. **The product itself.** A one-tap Allocate button inside the Kraken apps, embedded wallets with gas sponsored, and BTC purchasable inside the deposit flow. That is why 99.96% of holders are Kraken embedded wallets. The median ticket is 0.0037 BTC.
3. **No vault-specific promotions were found.** No boosted APY, referral or bonus-BTC campaign was found. The exchange-wide campaigns found are listed in `events.csv`: Beholder deposit match (March–April), the EEA sweepstakes (vault excluded), the FIFA sponsorship, and Ink Points (vault deposits are not a points activity; there is no INK token yet). We searched primary and secondary sources; blog.kraken.com blocks automated access, so post-launch Kraken blog posts were not checked.
4. **Capacity was rationed.** Stable-leg capacity grew only through 10 RLUSD and 7 PYUSD cap raises. Debt/NAV stayed at 0.55–0.65, so borrowing capacity was not the limit on deposits. The cost was rate spikes, not rejected deposits.
5. **Signs of fatigue.**
   - New depositors per week fell from 8,935 to about 1,300.
   - Gross withdrawals peaked at 722 BTC in August, the month yield hit 1.30% and the fee was raised.
   - 22.9% of all addresses that ever deposited have fully exited.

---

## J. Operator economics

**Vault performance fee:**

| Item | Value |
|---|---|
| Claimed so far | 5.2256 kBTC in 8 biweekly claims (12 Jun → 16 Sep); **$353k** at claim-time prices |
| Owed now | 0.2729 kBTC |
| Total | 5.498 kBTC, about **$476k** at $86.6k |
| Modeled accrual | 5.56 kBTC (accrual: June 1.22, July 1.42, August 1.69, September 1–20: 1.18 kBTC) |
| Run-rate (September accrual annualized) | **21.6 kBTC/yr, about $1.87M/yr = 0.33% of TVL** (6,579 BTC) |
| Split 80 / 15 / 5 | **$1.49M / $0.28M / $0.09M** to `0xb66e2948…` (EOA, unlabelled; Kraken/Payward is plausible but unverified) / `0xbE6b7dCa…` (Sentora's V2 fee recipient; on-chain link) / `0x68ec1fdd…` (2-of-3 Safe, unlabelled) |

**Sentora's downstream V2 fees** (annualized at snapshot sizes and September organic yields, est.):

| V2 vault | Fee | Vault TVL | Fee $/yr | Kraken vault's position | Of which from Kraken |
|---|---|---|---|---|---|
| Sentora RLUSD Main | 10% performance | $369.2M | $1.05M | $124.85M (33.8%) | $0.35M |
| Paypal USD Main | 1% management | $435.8M | **$4.36M** | $60.82M (14.0%) | $0.61M |
| Sentora PRIME Main | 15% performance | $185.2M | $1.19M | $17.69M (9.5%) | $0.11M |
| Sentora Huma PST Main | 15% performance | $45.0M | $0.41M | $2.24M (5.0%) | $0.02M |
| **Total** | | $1,035M | **$7.0M** | | **$1.10M** |

Hastra's 50 bp fee on the vault's $92.7M of PRIME comes to about $0.46M/yr.

**Fee stack on the vault's capital (est.):** vault fee $1.87M + Sentora downstream $1.10M + Hastra $0.46M ≈ **$3.4M/yr**, against depositors' net of about **$5.3M/yr** (1.01% × $521M). Intermediaries therefore take about 39% of all the yield the structure generates.

Sentora's direct take from the Kraken stack (15% of the vault fee plus downstream fees) is about $1.4M/yr. On top of that, it earns $5.9M/yr from the V2 vaults whose largest borrower is the Kraken vault: the kBTC markets are 55.5% of RLUSD Main and 37.9% of PYUSD Main.

**Issuer-linked incentives** (Merkl, weekly campaigns created by Sentora Safes; the funder is not disclosed; see Dossiers §4.1.6):

| V2 vault | Token | Since | Paid to date | Current per week | Run-rate $/yr | Budget APR on TVL | To Kraken's positions $/yr |
|---|---|---|---|---|---|---|---|
| Sentora RLUSD Main | RLUSD | 5 Mar | 4.67M | 246,250 | **$12.84M** | 3.48% | **$4.34M** |
| Paypal USD Main | PYUSD | 23 Dec 2025 | 7.51M | 231,475 | **$12.07M** | 2.77% | **$1.68M** |
| Sentora PRIME Main | PYUSD | 13 May | 1.52M | 93,575 | $4.88M | 2.63% | $0.47M |
| Sentora Huma PST Main | PYUSD | 26 Aug | 0.07M | 25,610 | $1.34M | 2.97% | $0.07M |
| **Total** | | | 13.8M | | **$31.1M** | 3.0% of $1.035B | **$6.56M** |

**Cost per dollar of TVL:**
- Issuers spend about **3.0¢ per $ of Sentora V2 TVL per year**.
- Through those vaults they spend about **1.26¢ per $ of Kraken vault NAV per year**. That is more than depositors' entire net yield (≈1.0¢) and about 93% of the vault's gross yield (≈1.35¢).
- Per dollar of stablecoin the Kraken vault keeps borrowed:
  - RLUSD: $4.34M / $175.9M ≈ **2.5%/yr**;
  - PYUSD (A-leg only): $1.68M / $60.8M ≈ 2.8%/yr on the redeposited dollars.

**Since launch (model):** $1.54M of the vault's $1.89M carry came from these rewards.

**The loop is circular.** RLUSD Main lends $175.9M to the Kraken vault, which parks $124.85M straight back in RLUSD Main. The issuer pays 3.5% on the whole RLUSD Main balance.

---

## K. Verdict: what to copy, what to avoid

**Copy:**
1. **Distribution inside an exchange app.** One-tap allocate, embedded wallets (Privy + EIP-7702 Kernel), sponsored gas, BTC purchase inside the flow and a 0.00006 BTC minimum. This alone produced 48.8k depositing wallets and $436M of net inflows in under 4 months, **regardless of yield**.
2. **A BTC-denominated share with a smoothed, bounded accountant rate** (±0.5% per update, 6-hour minimum, high-water-mark fee). The share never showed a down day, and the fee arithmetic reproduces within 1%.
3. **Stable debt across several venues with explicit liquidity paths.** V2 idle cash plus 1 bp permissionless `forceDeallocate` gives about 48% of debt repayable in the same block, and about 69% with repay-recycle.
4. **Split stable legs by source of return:**
   - (a) subsidized, liquid ("A");
   - (b) credit, illiquid ("B").

   B is the only leg with positive unsubsidized carry. Make that split explicit and size B to what the liquidity ladder can carry.
5. **Frequent, small fee claims (biweekly) and full on-chain auditability.** Every number here could be reconstructed.

**Avoid:**
1. **Yield that depends on issuer subsidies** (82–93% of carry) while telling users it does not. Price the product on the organic spread (≈0.1–0.6%) and treat rewards as upside with a disclosed end date.
2. **Borrowing from one curator's capped V2 behind a 3-day timelock.** That creates predictable 12–14% spikes, 45-hour negative-carry episodes, and a curator who both lends and borrows. Use multiple independent lenders, or pre-negotiated capacity above the book, and keep utilization headroom (≤85%) rather than borrowing up to the cap.
3. **Operating at the target LTV with a roughly 2-day manual reaction.** June showed 79% LTV and HF 1.085. Either run lower (for example about 60%, which buys a 30% buffer) or automate a real trigger (HF < 1.15 → unwind in the same transaction). Don't claim same-block delevering without evidence.
4. **An Aave leg at HF 1.20** (liquidated by an instant −18.6% move), and adding a WBTC/USDT leg at 71% LTV in a 95%-utilized market. Keep side legs at least as conservative as the core.
5. **31% of debt in an asset that exits through an operator in 1–2 business days** (PRIME, with an $85k on-chain buffer). Cap operator-redeemed assets at what T1 can cover under −30%, or hold a dedicated liquid buffer.
6. **Unannounced parameter changes:** the fee increase on 24 Aug, the 0 → 1% force-deallocate penalty on 20 Sep with no timelock, and a single-EOA kBTC key. These cost nothing to fix and differentiate a competitor.
7. **Marketing "up to 2.5%"** when the best realized week was 2.16% and the run-rate is 1.0%.

---

## Method, limits, reproducibility

**Scripts** (all in `scripts/`; reuse `klib.py`, a copy of the earlier `lib.py` plus batch RPC):

| Script | What it does |
|---|---|
| `blocks.py` | Daily block map (Ethereum by RPC timestamps; Ink by its exact 1-second block time) |
| `daily_eth.py` | 175 daily plus snapshot/live archive reads (≈45 calls each) |
| `accrue_fetch.py` | Morpho `AccrueInterest` logs |
| `chainlink_btc.py` | BTC/USD rounds |
| `transfers_fetch.py`, `ink_flows.py` | Full share-transfer replay |
| `holders_fetch.py`, `classify_unknown.py` | Holders and address types |
| `merkl_fetch.py` | Campaigns |
| `v2_caps.py` | Cap, fee and penalty events |
| `accountant_logs.py` | Fee claims and fee changes |
| `ladder_reads.py` | V2 market liquidity at snapshot and live |
| `analysis.py`, `analysis_risk.py`, `analysis_growth.py`, `analysis_carry.py`, `analysis_econ.py`, `events_csv.py`, `md_tables.py` | Analysis and output tables |

**RPCs.** `ethereum-rpc.publicnode.com` now refuses archive requests ("Archive requests require a personal token"). Archive reads used `rpc.mevblocker.io` and `eth-mainnet.public.blastapi.io`; logs came from `mainnet.gateway.tenderly.co`.

**Estimates and assumptions:**
- **Deployment-yield method.** The organic yields are realized share-price growth (daily or weekly), net of V2 fees. The daily negative-carry test uses 7-day trailing deployment yields.
- **Rewards.** Reward APR is the campaign budget over average TVL. It is not the realized per-user claim, and Merkl's own APR history was not downloaded (DefiLlama's `apyReward` on 21 Sep of 3.41 / 2.89 matches).
- **Excluded from the carry model:** the Uniswap LP and idle BTC. The model still matches realized yield within 0.02–0.24 pp.
- **LTV path.** The intraday LTV path ignores interest accrued inside a day, which is under $10k.
- **Stress test:** the liquidation-bonus costs are upper bounds, and PRIME is valued at NAV (no haircut).
- **Liquidity ladder:** the ladder assumes no competing V2 withdrawals, and that the Merkle root permits cross-leg routing (not decoded).
- **Holder types.** Holder types for 21 Sep come from Blockscout `proxy_type`/`implementations`. Snapshot holders who later exited were classified by `eth_getCode`.
- **Payee identity.** The 80% and 5% payees remain unlabelled.
- **Milestone sources.** Some milestone sources are search snippets or secondary; they are marked as such in `events.csv`.
- **Not done:** the Merkle root / strategist permissions were not decoded. Kraken blog posts after launch could not be fetched (bot check).
