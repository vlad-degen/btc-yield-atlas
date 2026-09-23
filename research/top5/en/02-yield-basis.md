# Yield Basis (YB): deep dive, as a "BTC collateral + dollar loan deployed into a strategy" product

*Scripts: [`tools/top5/yieldbasis/`](../../../tools/top5/yieldbasis/), data: [`data/top5/yieldbasis/`](../../../data/top5/yieldbasis/). Mentions of `scripts/` and `raw/` below refer to the working folder; the `raw/` dumps are not published.*

Snapshot: 2026-09-20 (daily bucket, block ≈26,028,6xx). A few live reads are from 2026-09-21 (block ≈26,029,7xx) and are labelled as such. Research date: 2026-09-21.
Scope: every YB market on Ethereum: v1 (legacy), v2 (deprecated) and v3 (current), for WBTC, cbBTC and tBTC. WETH is shown only for context.

## 0. Ten things to know first

1. **What the product is.**
   - It is not a carry trade. It is a 2x-levered BTC/crvUSD Curve LP.
   - The dollar leg is a crvUSD credit line that the Curve DAO minted to the YB Factory: 60M → 300M → 1B crvUSD. It pays Curve no interest.
   - The "borrow rate" (7% in v1/v2; 0.82% → 2.64% → 1.80% in v3) is an internal transfer. The protocol donates it back into the Curve pool as a rebalancing subsidy.
2. **Book value and exit value can diverge by 5–20% for weeks.** The docs say the gap (TRD) "resolves within hours". The data says otherwise:
   - **Feb-2026:** redemption value fell to **−19.5% below book** (v2-WBTC, 2026-02-05). TRD stayed below −1% for **76–77 consecutive days** (Jan 30 – Apr 16).
   - **Today (2026-09-21):** v3-WBTC and v3-tBTC TRD is **−6.0% / −5.8%**, because the Curve pool's `price_scale` ($69.6k) lags BTC ($86.2k) by 24%. A 100-share exit takes a −8% / −11% haircut.
3. **Realised unstaked BTC yield is modest and very uneven.** Figures are in BTC terms, on redemption value.
   - v1 (Sep–Nov 2025, high volatility): +2.5% (WBTC), +10.3% (cbBTC), +8.9% (tBTC) in 49 days.
   - v2 (193 days): +3.5% / +4.3% / +2.6%.
   - v3 (118 days, to Sep 20): **−2.7% / +0.6% / −3.0%**.
   - Chained for one year (unstaked, ignoring migration costs): **+3.1% (WBTC), +15.7% (cbBTC), +8.3% (tBTC)**.
4. **Most depositors stake, and staked lost principal.**
   - 73% of v3 BTC TVL is staked and earns only YB emissions.
   - The staked side of v2 sat in "recovery mode" almost the whole time. The gauge share fell to **0.966 / 0.969 / 0.974 BTC** by the May-2026 migration.
   - YB fell from $0.677 at listing to $0.088 today (−87%). The 4–6% "staked APR" is paid in a token that has lost most of its value.
5. **Incentives dwarf organic yield after 2025.**
   - Oct-25 to Sep-26: **$10.95M of YB was emitted to BTC gauges**, against about $2.5M net book gain to unstaked LPs (much of it reversed in Mar–Apr 2026).
   - Since Apr-2026, admin-fee revenue has been **0–1.2% of BTC TVL (annualised)**, while emissions cost about 3–4%.
6. **TVL is driven by caps, not yield.**
   - Each cap increase filled within minutes in 2025: 28 → 252 BTC (Oct 2), 266 → 1,355 BTC (Oct 14), 1,662 → 2,412 BTC (Dec 12).
   - After the Feb-2026 stress, cap raises stopped attracting deposits. The Jul-24 and Sep-1 raises were followed by outflows.
   - BTC TVL peaked at **2,412 BTC (2025-12-19)**. It is now **1,328.5 BTC** (−45% in BTC terms).
7. **There are no liquidations, but crvUSD depends on it.**
   - On 2026-02-05 the BTC markets owed $229M crvUSD while the LPs held only $78M crvUSD. A full unwind would have needed **$153M of net crvUSD buying**.
   - The DAO responded by cutting allocations to 2/3 and raising the LEVAMM fee to 5%.
8. **Curve dependency is total.** Curve controls:
   - the credit line (it can pull back the idle 670M at any time);
   - the Cryptoswap pool parameters (ownership votes 1486, 1491, 1494);
   - the crvUSD oracle.

   The YB Factory's `emergency_admin` is **Curve's EmergencyDAO (5-of-9 Safe 0x4679…1E0c)**.
9. **Governance is fast and concentrated.** 55 of 59 YB DAO proposals were executed, with a median of 20.6 h from start to execution. CliffEscrow contracts (team and investors) hold ≈42% of locked YB. The core contracts are immutable, but every economic parameter can change within about a day.
10. **Security: 10 audits plus a Sherlock contest, and no exploit found.** The **bug bounty is still "in preparation"** (docs, status as of 2026-05-19). There was one operational incident: some HybridVault withdrawals reverted and had to be unblocked by DAO vote #47 (2026-06-03).

### Data and method

Sources:
- **Primary data:** `api.yieldbasis.com` (the protocol's own indexer). Daily per-market snapshots of `pricePerShare`, `preview_withdraw(1e18)`, `liquidity.total` and asset price; token APR, trading APY, veYB epochs, admin-fee claims, flows, interest collections, proposals.
  - I checked 6 month-end points against archive `eth_call` (drpc, tenderly, blastapi). **All matched to the last digit.**
  - The month-end archive script also reads debt, rate, fee, allocation, watermark and Cryptoswap `price_scale / price_oracle / virtual_price / xcp_profit` (`scripts/archive_monthend.py`).
- **Other APIs:** DefiLlama (`api.llama.fi/protocol/yield-basis`, `coins.llama.fi`), Curve DAO API (`prices.curve.finance`), Blockscout (creation transactions, holder lists; balances re-read on-chain), and docs.yieldbasis.com (65 pages, including the MiCA whitepaper and Terms).
- **DefiLlama yields limitation.** `yields.llama.fi` only has YB pools from **2026-09-20 (2 data points)**, so there is no apyReward history there. The staked APR history uses the protocol's own `token-apr` series. That series is YB emissions × YB price ÷ staked TVL; I did not recompute it independently.

Definitions:
- **Book PPS** = `LT.pricePerShare()`. This is the value of an unstaked share in asset units. The pool's `price_scale` values the position, not the market price.
- **Redeemable** = `LT.preview_withdraw(1e18)`, i.e. what an exit actually returns. **TRD** = redeemable / book − 1.
- "APY" figures are annualised month-on-month ratios. Partial months are flagged as noisy.

## A. Passport

| Item | Value |
|---|---|
| Legal entity | **Basis Yield AG** ("Yield Basis AG"). Swiss public limited company, Bahnhofstrasse 10, 6300 Zug. Registered 2024-12-27. No LEI (MiCA whitepaper). Terms (13-Mar-2026): Swiss law; arbitration seated in Zurich (Swiss Arbitration Centre). The Terms name only "YieldBasis", not the AG |
| Chain | Ethereum only |
| Launch | **v1** 2025-09-24: LTs deployed 16:11 UTC; credit line live 10:05 UTC. **v2** 2025-11-12: "liquidity migration" to new LT implementation and fee receiver; same Curve pools. **v3** 2026-05-25: new Curve pools with governance-set reserved-profit fraction, new AMM/LT, HybridVault limits. WETH: legacy 2026-01-07, v3 2026-05-25 |
| Live BTC markets (v3) | WBTC (market #7), cbBTC (#8), tBTC (#9). Plus WETH (#10). Deprecated (withdraw-only): v2 #3–5, v1 #0–2, WETH-legacy #6 |
| Caps (v3, after DAO #58 on 2026-09-10) | WBTC $50M, cbBTC $50M, tBTC $17.87M, WETH $32.3M. Cap = crvUSD allocation / 2 |

TVL on 2026-09-20 (book value; asset units × oracle price):

| Market | Asset units | USD | Redeemable asset | TRD (09-20) | TRD live 09-21 |
|---|---|---|---|---|---|
| v3-WBTC | 478.7 | $38.65M | 462.1 | −3.46% | **−5.97%** |
| v3-cbBTC | 352.1 | $28.54M | 352.1 | −0.02% | −0.07% |
| v3-tBTC | 257.4 | $20.81M | 248.8 | −3.33% | **−5.79%** |
| v2 (3 markets) | 236.9 | $19.17M | 228.8 | −3.0 to −4.7% | −5.8 to −7.8% |
| v1 (3 markets) | 3.4 | $0.28M | – | – | – |
| **All BTC** | **1,328.5 BTC** | **$107.4M** | **1,295.6 BTC** | | |
| v3-WETH (context) | 10,655 ETH | $28.2M | | | |

- DefiLlama protocol TVL is **$133.6M** (09-20 daily) and $140.3M (09-21 live). It includes WETH and uses book value.
- Peaks: DefiLlama $247.3M (2026-01-15). BTC markets: **2,412 BTC (2025-12-19)**; $221.4M (2026-01-14).

Holders (Blockscout holder lists, balances re-read on-chain via `balanceOf`, staked plus unstaked per address):
- v3: WBTC 475, cbBTC 444, tBTC 367 (**744 unique across v3**).
- v2: 231 / 187 / 297. v1: 936 / 94 / 384.
- **2,436 unique addresses** across all BTC markets.

Token (YB, 0x01791F…45fF):
- Cap 1B. Deployed 2025-09-15. **TGE and emissions began 2025-10-15, 10:00 UTC.**
- Total supply now 752.0M (248.0M still in the emission reserve). 52.0M YB have been emitted to gauges.
- Allocation: 30% incentives, 25% team, 12.5% ecosystem, 12.1% investors, 7.5% Curve licensing, 7.4% development reserve, 2.5% public sale, remainder other buckets.
- Public sale (Legion × Kraken): 11–12 Sep 2025, **25M YB at $0.20 ($5M, $200M FDV)**, paid in USDC. Kraken listing at TGE (MiCA whitepaper).
- Price: first print $0.677 (2025-10-15); low $0.0636 (2026-07-29); **$0.088 now**.

veYB:
- 150.4M YB locked across 1,220 locks, of which 126.0M are permanent locks.
- veYB supply 142.9M at epoch 42.
- Fee revenue is paid in yb-LP tokens, smoothed over 4 weeks.

## B. Mechanics, step by step

1. **Deposit.**
   - The user calls `LT.deposit(assets, debt, min_shares)` on the market's LT (yb-asset ERC-20, 18 decimals).
   - The LT pulls `debt` crvUSD **from the LEVAMM's idle crvUSD balance**. That balance is the market's allocation, allocated from the Factory.
   - It pairs the crvUSD with the user's BTC and calls `CRYPTOPOOL.add_liquidity([debt, assets])`. The LP tokens are credited to the LEVAMM together with the debt (`amm._deposit`).
   - `debt ≈ assets × price`. The LP value is therefore about 2× equity, and debt is 50% of LP value.
   - The deposit reverts if the projected debt exceeds `AMM.max_debt()/2`. This is the cap.
2. **Where the crvUSD comes from.**
   - The Curve DAO's crvUSD ControllerFactory (0xC933…8BC) set `debt_ceiling(YB Factory 0x370a…00c0)`, which **mints crvUSD directly into the YB Factory**.
   - Ceiling history (archive bisect): 60M (block 23,432,188, 2025-09-24); 300M (23,575,503, 2025-10-14); **1,000M (23,996,893, 2025-12-12)**.
   - YB governance moves crvUSD from the Factory into each LT and AMM (`allocate_stablecoins` / HybridFactoryOwner limits).
   - Today: **669.9M idle in the Factory**, 330.1M allocated to AMMs, and **123.4M actually borrowed** by positions.
   - For scale: crvUSD total supply is 2,104.8M, so about 47% of all crvUSD is YB's credit line, mostly idle.
3. **Constant 2x leverage (LEVAMM).**
   - LEVAMM quotes LP ↔ crvUSD along a leveraged invariant anchored to an oracle (`LEVERAGE = 2e18`).
   - When BTC moves, leverage drifts and the LEVAMM quote goes stale. Arbitrageurs trade against it (usually via the VirtualPool, with flash loans), which pushes leverage back to 2x.
   - Arbitrageurs pay the LEVAMM fee: v1/v2 0.92–0.91%; raised to 5% and then 3% in Feb–Mar 2026; v3 1.30% → 1.82% → **1.20%** since 2026-09-08.
   - No keeper and no liquidation are involved. The 2x leverage turns the √p shape of an LP into linear p, but only relative to the pool's `price_scale` (see F).
4. **Interest (the "dollar-loan cost").**
   - The AMM debt accrues `rate` per second (the cap in code is 100% APR).
   - `collect_fees()` moves the accrued amount from the AMM's idle crvUSD into the LT. `distribute_borrower_fees()` then **donates it into the Cryptoswap pool** (it unlocks over the donation window, default 7 days).
   - So the "rate" is paid by LPs to their own pool's rebalance reserve. **Curve DAO receives no interest.** Curve's compensation is:
     - 75M YB of licensing, vesting pro rata with emissions;
     - a 5M YB airdrop to veCRV voters;
     - adjacent volume and PegKeeper revenue (Curve News, 2025-10-22).
   - Rate history:
     - v1: 3.5% at creation, then 7% from 2025-09-26 ("2x donation rate", DAO #7). v2: 7%.
     - v3: 0.82%, then 2.64% (Aug 17 / Aug 29, DAO #54/55), then **1.80%** (Sep 8, DAO #57).
     - Interest actually collected: see `yield_monthly.csv` (for example v2-cbBTC $624k in Jan-2026, ≈7.7% of equity annualised).
5. **Fees.**
   - (a) Curve Cryptoswap swap fees accrue to the LP (the LEVAMM owns 97–100% of each pool's LP). The pool keeps a governance-set share for its own re-pegging: 50% originally; `reserved_profit_fraction` of 36% and then **30%** after Curve votes 1491 and 1494. v3 pool fee is a flat 130 bp (`mid_fee = out_fee = 1.3e8`) after vote 1494.
   - (b) LEVAMM fees paid by arbitrageurs.
   - (c) Donations (the interest above).
   - Cumulative swap volume in the BTC pools: **$3.06B, with $33.5M of swap fees**. LEVAMM volume $574M.
6. **Split between unstaked LPs, staked LPs and veYB** (`LT._calculate_values`).
   - Positive value change first repays the staked "watermark" gap (recovery mode).
   - The rest is split by an admin-fee curve `f_a = 1 − (1 − 0.10)·√(1 − staked/supply)`: 10% at 0% staked, 36.4% at 50%, 71.5% at 90%.
   - The **staked side gets no fee growth**, only YB emissions. Losses are shared pro rata.
   - So when 95% of supply is staked, unstaked holders get about 4.3x the pool-level gain per unit.
7. **Admin fees.**
   - `withdraw_admin_fees()` mints yb-LP to the fee receiver.
   - The fee receiver is the **FeeSplitter 0x4b77…c346** (since DAO #51, 2026-07-20). It sends 15% (`split_fraction`) to the net-pressure PID reserve (crvUSD incentives for the crvUSD/pyUSD sink pool via Merkl) and the rest to the veYB **FeeDistributor 0xD11b…7A90**.
   - The fee switch went live 2025-12-04: 17.55 BTC of accrued fees distributed over 4 weeks.
8. **Gauges and emissions.**
   - Weekly YB emission = reserve × (1 − e^(−Δt·max_mint_rate·rate_factor)), with a 4-year e-folding time at full utilisation.
   - Per-gauge weight = veYB votes × √(staked/supply).
   - Currently about 3.4–3.7M YB per month go to BTC gauges.
9. **HybridVaults** (DAO #35, 2026-04-07; v3 limits DAO #42).
   - These are per-user vaults. The user posts crvUSD into scrvUSD (an allow-listed ERC-4626) equal to `stablecoin_fraction` (**45%**, down from 55% by DAO #49) of the YB position. In return the user gets a personal cap above pool caps (pool limit 50M crvUSD each).
   - Current backing: **3.34M crvUSD** (`crvusd_vault_total_required[scrvUSD]`), limit 100M.
   - HybridVault contracts hold only about 5.7 BTC of the v3 BTC markets, so the feature is marginal for BTC.
10. **Withdrawal.**
    - `LT.withdraw(shares, min_assets)` removes a pro-rata slice of (LP, debt) from the LEVAMM. It unwinds the LP through `CRYPTOPOOL.calc_withdraw_fixed_out`, repaying exactly the debt share in crvUSD, and pays the rest in the asset.
    - It is instant and has no queue or lock. Staked shares first leave the gauge, which is also instant.
    - What the user receives = redemption value (see F for TRD).
    - If the AMM is killed, the only exit is `emergency_withdraw`, where the user may have to **bring crvUSD** to settle the debt leg.

Key contracts (docs.yieldbasis.com/user/reference/contract-addresses; checked on-chain via `Factory.markets(i)`, `market_count = 11`):

| Role | Address |
|---|---|
| Factory | 0x370a449FeBb9411c95bf897021377fe0B7D100c0 (admin = HybridFactoryOwner 0xb8BA…C5C6 → ADMIN = YB DAO 0x42F2…95Fa; emergency_admin = 0x4679…1E0c) |
| v3 WBTC: LT / LEVAMM / Curve pool / gauge | 0x651D4b81…BAa / 0x7b9817eb…FFFE / 0x31369866…729A / 0xAa0b1d26…58F5 |
| v3 cbBTC | 0x722FC364…29F9 / 0x49F51d7e…B196 / 0x862CB4E9…c6A0 / 0xF8764cBc…1b6f |
| v3 tBTC | 0x771F7290…23Ec / 0x0e357Af5…cF5a / 0x4F52C3a8…9c2e / 0xe83D888F…8483 |
| v2 (deprecated) LTs | WBTC 0xfBF3…E763, cbBTC 0xAC0c…F8D2, tBTC 0xaC0a…AC92 |
| v1 (legacy) LTs | WBTC 0x6095…5204, cbBTC 0xD6a1…1112, tBTC 0x2B51…32FF |
| YB / veYB / GaugeController / FeeDistributor | 0x0179…45fF / 0x8235…C211 / 0x1Be1…1c21 / 0xD11b…7A90 |
| HybridVaultFactory | 0xBdC32268851C324c6185809271dfe6d8dab8dC5b |
| crvUSD aggregator (oracle) | 0x18672b1b0c623a30089a280ed9256379fb0e4e62 |

## C. Counterparty chain and who can change what

**Where the BTC and the crvUSD sit, step by step:**

1. The user's BTC wrapper carries its own custodian risk: BitGo/WBTC, Coinbase/cbBTC, Threshold/tBTC.
2. At deposit, the BTC goes **into the Curve Cryptoswap pool** (Curve factory contract; pool admin is Curve DAO via proxy 0x97aa…980a).
3. The LP token is held by the **LEVAMM** (immutable Vyper contract).
4. The crvUSD leg is minted by Curve's ControllerFactory into the YB Factory, then sits idle in the LEVAMM. When borrowed, it sits in the Cryptoswap pool.
5. The user holds the LT share. If staked, the **LiquidityGauge** (ERC-4626) holds it.
6. Nothing is held by a person or an off-chain custodian. There is no curator.

**Who can change parameters:**

| Actor | Powers | Speed |
|---|---|---|
| **YB DAO** (Aragon OSx DAO 0x42F2…95Fa, token-voting plugin 0x2be6…ec78). 30% quorum, 55% support, 7-day minimum, early execution when the outcome is certain | Via the HybridFactoryOwner (Factory admin): market creation; `set_rate` (≤100% APR); `set_amm_fee` (≤10%); allocations and caps; gauges; fee receiver; min admin fee; implementations for *new* markets; kill/unkill | Median **20.6 h** from start to execution (55 of 59 executed). #7 executed about 4 minutes after start. Docs mention a timelock and an Emergency-DAO veto, but the observed executions show no material delay |
| **Emergency admin** = **Curve EmergencyDAO**, 5-of-9 Safe 0x467947EE34aF926cF1DCac093870f613C96B1E0c. Curve's docs list this address as its "original EmergencyDAO" | `set_killed` on markets. Can sweep stuck positions via `emergency_withdraw` (proceeds go to the owner) | Immediate |
| **Curve DAO** (ownership votes, 51% support / 30% quorum) | crvUSD `debt_ceiling` for the YB Factory (the credit line). The **mint factory has unlimited approval over the YB Factory's crvUSD** ("can take back as much as it wants", Factory code). Cryptoswap pool fees, reserved-profit fraction, `price_scale` "driver policy" (votes 1486, 1491, 1494), donation protection (1213, 1434). crvUSD aggregator and PegKeepers | ≈7-day votes |
| Core code | LT, LEVAMM and Factory are **immutable** (Vyper 0.4.3). Fixes happen by deploying new markets and migrating (v1→v2 in Nov-2025, v2→v3 in May-2026 via LTMigrator; the migrator was replaced 3 times: #44, #48, #58) | – |

**Curve DAO dependency.**
- Without Curve, YB has no leverage (the credit line), no venue (the Cryptoswap pools) and no oracle (the crvUSD aggregator).
- Curve also carries the peg externality. It has tuned PegKeepers (vote 1241: ×3 to 324M) and incentives for YB pools because of it.

**veYB concentration.** Top 40 locks hold 86.5% of the 150.4M locked YB:
- CliffEscrow (team and investor vesting escrows): **63.3M (42.1%)**;
- two Safe multisigs: 28.5M (18.9%);
- EOAs: 30.0M (19.9%);
- a "Locker" contract: 7.1M (4.7%).

The team and investors can meet the 30% quorum largely on their own.

## D. Who manages it

- **There is no curator.** The protocol and DAO govern it; Basis Yield AG develops it.
- **People** (MiCA whitepaper, "management body"):
  - **Michael Egorov** (founder; also founder of Curve);
  - "Alltime" (pseudonymous co-founder);
  - Carylyne Chan (Growth);
  - Jerry Liu (operations and marketing lead);
  - Alan Li (APAC).
- **Deployer** 0xa39E…C80d (ENS deployer._yb.eth). It creates the proposals.
- **Investors.**
  - $5M private round at a $50M valuation (DefiLlama raises, 2025-02-18).
  - The whitepaper says **$6M** raised in total from SevenX, Delphi Ventures, AntAlpha, Amber Group, Aquarius, Bitscale, Mirana, Chorus One, Karatage and NoLimitsHoldings, plus 20+ angels (from Bitfury, Brevan Howard, Ethereal, Quantstamp).
  - Public sale of $5M via Legion × Kraken.
- **Audits** (docs): Statemind; ChainSecurity ×3 (core, HybridVault, 2026-07-24 AMM/LT hardening plus YBLendingOracle); Quantstamp; MixBytes ×2; Electisec; Pashov; Firepan AI (FeeDistributor); and a Sherlock contest (Aug–Sep 2025). The docs warn that a published report does not mean every finding is fixed.
- **Bug bounty:** docs still read "**in preparation**" (status 2026-05-19). I found no live program on the docs.
- **Incidents:** no exploit found. Operational issues:
  - the v1 market was replaced after 7 weeks;
  - HybridVault withdrawals reverted until DAO #47 (2026-06-03) installed a fixed HybridFactoryOwner;
  - the LTMigrator was re-deployed three times.

## E. Yield

Files: `yield_monthly.csv` (per pool and month), `yield_protocol_monthly.csv` (TVL-weighted BTC), `raw/holding_period.json`.

### E1. Protocol level: TVL-weighted across live BTC markets (annualised, BTC terms)

v1 is used through Oct-2025 and v2 from its launch on Nov-12; v1 is excluded after migration.

| Month | Unstaked book APY | Unstaked redeemable APY | Staked token APR (YB) | Staked share | Blended LP APY* |
|---|---|---|---|---|---|
| 2025-10 | 24.2% | 40.0% | 15.5% | 85% | 16.7% |
| 2025-11 | 43.3% | 13.9% | 28.5% | 67% | 33.4% |
| 2025-12 | 13.8% | 29.0% | 22.9% | 65% | 19.7% |
| 2026-01 | 2.2% | **−31.1%** | 12.0% | 81% | 10.2% |
| 2026-02 | 53.3% | **−74.8%** | 8.1% | 59% | 26.7% |
| 2026-03 | **−16.6%** | 68.4% | 6.8% | 64% | −1.6% |
| 2026-04 | **−12.6%** | 244.9% | 5.1% | 62% | −1.7% |
| 2026-05 | −0.0% | 0.4% | 5.8% | 75% | 4.4% |
| 2026-06 | 10.1% | **−14.6%** | 5.6% | 66% | 7.1% |
| 2026-07 | 3.8% | 40.4% | 4.8% | 64% | 4.4% |
| 2026-08 | 1.0% | **−24.7%** | 4.9% | 74% | 3.8% |
| 2026-09 (to 20th) | **−1.1%** | 9.2% | 5.1% | 75% | 3.6% |

\*Blended = (1 − s) × book + s × token APR. This is an upper bound for stakers, because it ignores watermark losses and the YB price collapse after emission.

**Stability, Oct-25 to Sep-26 (12 months):**
- Unstaked book: mean 10.1%, median 3.0%, σ 20.9 pp, worst −16.6% (Mar-26).
- Unstaked redeemable: σ ≈ 80 pp, worst −74.8% (Feb-26).
- Staked token APR: mean 10.9%, median 6.4%. It fell from 28% to about 5% as YB fell from $0.48 to $0.08.

### E2. Holding-period returns in BTC (unstaked; `raw/holding_period.json`)

| Cohort | WBTC book / redeem | cbBTC book / redeem | tBTC book / redeem |
|---|---|---|---|
| v1: Sep-24 → Nov-12, 2025 (49 d) | +3.5% / +2.5% | +11.1% / +10.3% | +9.5% / +8.9% |
| v2: Nov-12 → May-24, 2026 (193 d) | +3.9% / +3.5% (6.6% APY) | +4.5% / +4.3% (8.3%) | +2.5% / +2.6% (4.9%) |
| v3: May-25 → Sep-20, 2026 (118 d) | +0.75% / **−2.7%** | +0.61% / +0.59% | +0.31% / **−3.0%** |
| Chained, 361 d | +8.3% / **+3.1%** | +16.8% / **+15.7%** | +12.6% / **+8.3%** |
| v2 cohort exiting on 2026-02-05 | +4.2% / **−16.1%** | +4.4% / **−14.9%** | +1.5% / **−15.6%** |

**Staked principal** (gauge share → LT → BTC, archive reads; `raw/staked_principal.json`):
- v2 gauge shares fell from 1.000 to **0.966 (WBTC), 0.969 (cbBTC), 0.974 (tBTC) BTC** by 2026-05-24, the v3 migration day.
- Since then they have recovered to 0.992–0.994 BTC.
- v3 staked shares: 0.9975–0.9984 BTC.
- So a v2 staker who migrated in May crystallised a **−2.6% to −3.4% BTC principal loss**. The offset was about **4.6–7.8%** of BTC-equivalent in YB emissions (WBTC 5.5%, cbBTC 7.8%, tBTC 4.6%; sum of monthly token APR × days, *estimate*), but only if the YB was sold as it was emitted. YB fell 75% between Dec-25 and May-26.

### E3. Costs: the dollar loan and rebalancing

Monthly per pool, in `yield_monthly.csv`. All annualised as % of equity.

| Period | crvUSD "rate" | Interest actually paid | Gross Cryptoswap income (Δln xcp_profit ×2, incl. donations) | Rebalancing spend estimate (Δ(xcp_profit − virtual_price) ×2) |
|---|---|---|---|---|
| v1 Oct-25 | 7% | 8.6–8.8% | 52–57% | **31–44%** |
| v2 Dec-25 | 7% | 7.5–7.6% | 33–42% | 16–21% |
| v2 Feb-26 (`price_scale` frozen) | 7% | 9.6–9.9% | 22% | ≈ −0.8% (no re-pegging happened; the loss was deferred) |
| v2 Mar/Apr-26 (re-peg) | 7% | 8.7–9.8% | 16–24% | **12–20%** |
| v3 Jun-26 | 0.82% | 0.9% | 26–31% | 17–21% |
| v3 Sep-26 | 1.80% | 1.8–2.0% | 10–31% | 7–20% |

Notes on the rebalancing estimate (**estimate**, Cryptoswap level only):
- It uses the Curve twocrypto accounting identity: the part of lifetime profit spent on re-pegging equals `xcp_profit − virtual_price`.
- It excludes the arbitrage P&L of the LEVAMM re-leverage trades and the admin-fee take.
- The "interest" is not paid to anyone external. It is donated back into the same pool and shows up inside "gross income".

In plain terms:
- about 30–60% of the pool's gross fee income is spent keeping the pool re-pegged;
- the admin fee takes up to 70%+ of the remaining positive value change when most LPs stake;
- unstaked holders keep the rest.

### E4. Negative-APR and stress episodes (active windows only)

- **Book PPS fell:**
  - v1-WBTC Oct-25 (−12% annualised; redeemable −0.6%);
  - v2-tBTC Jan-26 (−4%);
  - all v2 markets **Mar-26 (−13% to −20%) and Apr-26 (−10% to −14%)**, when `price_scale` finally re-pegged after the Feb crash;
  - v2-tBTC May-26 (−0.5%);
  - v3 opening week May-26 (−6% annualised over 6 days, entry costs);
  - v3-cbBTC Aug-26 (−1.1%); v3-WBTC and v3-tBTC Sep-26 (−1.2%, −1.9%).
- **Redeemable value fell:**
  - v2 Jan-26 (−28% to −34% annualised);
  - v2 **Feb-26 (−73% to −77% annualised; −16% to −17% in absolute terms)**;
  - v3 Jun-26 (−17% to −34%);
  - v3-WBTC and v3-tBTC Aug-26 (−34% to −36%).
- **Recovery mode (staked below watermark):**
  - v2 staked sides were below the watermark for most of their life, reaching **−3.43% (WBTC), −3.15% (cbBTC), −2.48% (tBTC) on 2026-04-30**. They are still −0.56% to −0.74% today.
  - v1: −4% to −7% in Oct-25; −8.6% to −11.4% in Nov-25; the legacy remainder sits at −26%.
  - v3: −0.1% to −0.25% (mild).
- **Frequency of TRD < −1%** (`raw/trd_stats.json`):
  - v2: 80–108 of 201 days; worst −21.2% (2026-02-24); longest streak 76–77 days.
  - v3-WBTC: 55 of 120 days; v3-tBTC: 63 of 120 days, currently in a 32–33-day streak.
  - v3-cbBTC: 39 of 120 days.

### E5. Organic versus incentive

| Year-to-date (Oct-25 to Sep-26) | Amount |
|---|---|
| YB emissions to BTC gauges | **$10.95M** (52.0M YB to all gauges) |
| Admin fees accrued in BTC markets | $8.70M (**$6.2M of it in Oct–Nov-25**, mostly v1) |
| Net book gain to unstaked LPs (sum of monthly) | ≈ $2.5M (*estimate*; the +$2.1M booked in Feb-26 was largely reversed in Mar–Apr) |

- The organic share of LP income was 70–80% only in the volatile months (Nov-25, Feb-26).
- It has been **0–42% since Mar-2026**, and 0% in Mar, Apr, May and Sep (3% in Aug).
- Current staked yield: DefiLlama (09-21) shows staked apyReward of 4.61% (WBTC), 6.99% (cbBTC), 3.49% (tBTC). Unstaked apyBase: 2.52% / 0.00% / 0.04%.

## F. Risk management

**What replaces liquidation.**
- Nothing is liquidated. LEVAMM keeps 2x leverage via arbitrage.
- In a fast move, arbitrageurs extract the spread until the fee stops them. The Cryptoswap pool then has to re-peg `price_scale`, but only when its rebalance reserve allows. Before v3 the reserve was capped at 50% of lifetime profit; now it is `rpf` 30%.
- If the reserve is insufficient, **`price_scale` freezes**. The position then carries ordinary LP impermanent loss against the true market price until volume refills the reserve.
- The protocol's own accounting (PPS and the LP oracle) uses `price_scale`, so the book does not show this. Only the redemption value does. In other words, the IL is "cancelled" relative to `price_scale`, not relative to market.

**Observed stress:**

| Episode | BTC | What happened |
|---|---|---|
| **2025-10-10/11** | 121.7k → 110.8k close (−14.5% intraday) | v1 book PPS fell 2–5% in a day, but redeemable held at about 1.00–1.01 (TRD positive). Recovered within about 4 days. Net crvUSD pressure was negative (pools crvUSD-rich). The 300M allocation went live 3 days later |
| **2026-01-29 → 02-05** | 89k → 62.7k | `price_scale` stuck at about 88.8k. TRD −19.5% / −18.5% / −16.9% on Feb-5 and −21% on Feb-24. Pools became about 83% BTC: debt $229M against $78M crvUSD in the LPs, so **+$153M net crvUSD buy pressure** if unwound. DAO responses: #28 cut allocations to 2/3 ("for safety of crvUSD"); #29 set the LEVAMM fee to 5% while `price_scale` was unchanged; #30–33 stepped it down to 3%, 2% and back once the scale moved. TRD < −1% until Apr-16. The loss surfaced as a book PPS decline in Mar–Apr and a −3.4% staked watermark gap |
| **2026-06 (−21%)** | 73.5k (Jun-1) → 59.5k (Jun-29) | v3 TRD reached −4.7% (tBTC, Jun-6) and closed by about Jul-6. Net crvUSD pressure about +$33M. HybridVault withdrawals were reverting until the fix in DAO #47 (Jun-3) |
| **2026-08/09 rally** | 63k → 86.6k | WBTC and tBTC pools did not re-peg: `price_scale` $69.6k against BTC $86.2k (+24%). TRD −3.5% for a month, **−6% on 09-21**. The pools hold about 69% crvUSD. Curve votes 1486, 1491 and 1494 installed `price_scale` "driver policies", but the lag persists for WBTC and tBTC. cbBTC re-pegged in early September |

**crvUSD peg.**
- A YB unwind after a crash requires buying crvUSD (the net-pressure concept). The PID controller streams crvUSD incentives to the crvUSD/pyUSD pool, funded by 15% of admin fees.
- Observed crvUSD daily range over the year: $0.9922 (2026-02-01) to $1.0051 (DefiLlama).

**Oracle.**
- LP price = 2·virtual_price·√price_scale·p_agg.
- p_agg is Curve's crvUSD aggregator (an EMA), checked to be inside (0.90, 1.10) **only when it is set**, not on every call.
- There is no staleness check and no fallback. The design is manipulation-resistant within a block, but it lags by construction. That lag is the source of the book-versus-redemption gap.

**Liquidity ladder** (live 2026-09-21, `LT.preview_withdraw` against book; `liquidity_ladder.csv`):

| Shares | v3-WBTC | v3-cbBTC | v3-tBTC | v2-cbBTC |
|---|---|---|---|---|
| 0.1 | −5.95% | −0.07% | −5.76% | −6.09% |
| 10 | −6.12% | −0.07% | −6.06% | −6.88% |
| 50 | −6.89% | −0.08% | −7.68% | −13.8% |
| 100 | −8.17% | −0.10% | −11.3% | −39.3% |
| 200 | −12.7% | −0.16% | −32.2% | – |
| 300 | −22.7% | −0.47% | – | – |

- Exits are always **instant**: no queue, lock or withdrawal window. The price, however, depends on pool state.
- A 50 BTC holder (the top-20 size) in WBTC or tBTC would give up 7–8% today. Waiting for `price_scale` to catch up could take weeks, and it may never happen if BTC stays higher, because the loss then becomes real.

**Can the protocol repay crvUSD on demand?**
- **Idle 669.9M crvUSD in the Factory:** Curve's mint factory can reclaim it at any time (unlimited approval).
- **About 207M allocated but unborrowed inside the AMMs:** YB governance can de-allocate it down to a floor of 3/4 of LP-priced collateral.
- **The 123.4M actually borrowed:** repaid only as LPs withdraw, pro rata. Neither Curve nor YB can force repayment. The kill switch (Curve EmergencyDAO) only freezes trading and routes exits through `emergency_withdraw`, where the exiting user supplies crvUSD if needed.
- Net pressure today is **−$29M across BTC markets** (the pools hold more crvUSD than the debt), because BTC rallied.

## G. Depositors: yb-LP holders (2026-09-21)

Method: Blockscout holder lists for the LT and the gauge. Balances were re-read on-chain, because Blockscout balances were stale by up to 50% for v2. Gauge shares were converted via `totalAssets/totalSupply × pricePerShare`. Staked and unstaked holdings are summed per address. The gauge contract itself is excluded. Full data: `holders_buckets.csv`, `raw/holders_btc.json`, `raw/holders_aggregate.json`.

| Market | Holders | BTC-eq | <0.01 | 0.01–0.1 | 0.1–1 | 1–10 | 10–100 | >100 | Top-1 | Top-10 | Top-100 | HHI | Staked |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v3-WBTC | 475 | 469.9 | 197 | 94 | 115 | 58 | 11 | 0 | 15.1% | 57.1% | 95.1% | 523 | 77.7% |
| v3-cbBTC | 444 | 351.9 | 206 | 95 | 87 | 45 | 11 | 0 | 14.0% | 52.8% | 96.5% | 422 | 73.2% |
| v3-tBTC | 367 | 251.7 | 218 | 72 | 52 | 22 | 2 | 1 | **47.7%** | 80.3% | 99.5% | 2,477 | 65.8% |
| v2-cbBTC | 187 | 140.7 | 151 | 20 | 10 | 4 | 2 | 0 | **70.8%** | 98.7% | 100% | 5,279 | 95.6% |
| v2-tBTC | 297 | 53.4 | 255 | 27 | 12 | 2 | 1 | 0 | **87.6%** | 97.0% | 100% | 7,692 | 95.8% |
| v2-WBTC | 231 | 43.0 | 182 | 32 | 10 | 6 | 1 | 0 | 42.3% | 92.9% | 100% | 2,455 | 38.6% |
| **v3 BTC combined** | **744** | **1,073.4** | 253 | 170 | 187 | 112 | 20 | 2 | 11.2% | 49.8% | 89.2% | 386 | 73.4% |
| **All BTC (v1+v2+v3)** | **2,436** | **1,313.6** | 1,814 | 260 | 217 | 121 | 21 | 3 | 9.1% | 52.6% | 89.0% | 372 | 75.5% |

- **Concentration.** By value, **64%** of v3 sits in 22 addresses holding more than 10 BTC (68% across all BTC markets, 24 addresses). Across all BTC markets (v1 to v3), addresses holding under 0.1 BTC are 85% of the count but 0.8% of the value; in v3 alone they are 57% of the count and 0.6% of the value. The two largest v3 addresses each hold about 119.96 BTC-equivalent (0x63e3…d8e7 across WBTC and cbBTC; 0xa79a…6dd4c in tBTC).
- **Holder types** (v3, by value):
  - EOAs: ≈91% (WBTC 421 BTC, cbBTC 320, tBTC 241).
  - Smart accounts and EIP-7702 wallets: 150 positions, ≈47 BTC.
  - Safe multisigs: 24 positions, ≈26 BTC.
  - HybridVaults: 56 contracts, ≈5.7 BTC.
  - `StrategyYieldBasis` beacon proxies: ≈2.5 BTC (StakeDAO-style strategy; operator not verified).
  - YB FeeDistributor: 0.5 BTC.
  - Morpho, Silo, Uniswap v4 PoolManager: dust.
- **Integrations are negligible.**
  - **Pendle:** no Yield Basis market among 492 Ethereum markets (Pendle API).
  - **Convex:** the Convex and StakeDAO items on DefiLlama are YB/yYB and YB/sdYB token-locker pools, not yb-LP wrappers.
- **Staked versus unstaked:** 73–78% of v3 BTC value is staked (it earns YB). The share was 95–96% in v2-cbBTC and v2-tBTC, where the remaining depositors are largely one to two whales.

## H. TVL growth

Protocol-level BTC markets at month-end (from `tvl_monthly.csv`):

| Month-end | BTC (book) | BTC (redeemable) | USD | Net flow BTC | Cap context |
|---|---|---|---|---|---|
| Sep-25 | 27.6 | 27.6 | $3.1M | +27.7 | $1M per market |
| Oct-25 | 1,369.8 | 1,382.6 | $150.2M | **+1,371** | $10M (Oct-2), then $50M per market (Oct-14) |
| Nov-25 | 1,601.0 | 1,580.4 | $146.0M | +183 | v1→v2 migration (Nov-12) |
| Dec-25 | 2,320.4 | 2,319.9 | $203.9M | **+705** | cbBTC $100M (Dec-12); 1B credit line |
| Jan-26 | 2,318.0 | 2,238.9 | $180.9M | −2 | – |
| Feb-26 | 2,337.5 | 1,962.6 | $156.6M | −21 | Allocation cut to 2/3 (Feb-15) |
| Mar-26 | 2,270.8 | 2,026.0 | $154.2M | −32 | – |
| Apr-26 | 1,796.8 | 1,796.6 | $136.6M | **−444** | HybridVaults (Apr-7) |
| May-26 | 1,580.8 | 1,580.9 | $116.1M | −215 | v3 launch (May-25) |
| Jun-26 | 1,531.8 | 1,494.4 | $90.3M | −61 | – |
| Jul-26 | 1,564.6 | 1,563.8 | $98.8M | +28 | WBTC $22M → $32M (Jul-24) |
| Aug-26 | 1,614.5 | 1,572.5 | $126.8M | +50 | – |
| Sep-20-26 | 1,328.5 | 1,295.6 | $107.4M | **−285** | WBTC and cbBTC → $50M (Sep-1). cbBTC outflow of 290 BTC on Sep 7–9 |

**Flows versus price.**
- Growth to Dec-2025 was 100% net inflow, gated by caps that filled within minutes.
- From Jan-2026 USD TVL fell with BTC price, and BTC TVL fell through outflows. There were about −659 BTC of net outflows from Apr to May, when yields were 5% or less and after the Feb TRD scare.
- The USD figure moves mostly with the BTC price. For example, Jun-26: −$25.8M in USD against −49 BTC.

The caps timeline is in `events.csv`: DAO proposals #3–6, #8, #10, #23, #28, #38–42, #50, #52, #56, #58, plus the Curve credit-line votes.

## I. Growth drivers (dated; full list in `events.csv`)

**What moved TVL** (7-day before/after windows in `events.csv`):
1. **Credit-line and cap increases (by far the biggest):**
   - Oct-2 ($10M caps): 28 → 252 BTC.
   - Oct-14 (300M credit line, $50M caps): 266 → 1,355 BTC.
   - Dec-12 (1B credit line, cbBTC $100M): 1,662 → 2,412 BTC.
2. **The YB TGE and emissions (Oct-15)** coincided with launch demand; staked APR was 15–30% while YB was $0.45–0.68.
3. **Curve distribution:**
   - DAO votes 1206, 1222 and 1279 (97–100% yes);
   - a 5M YB airdrop to veCRV voters who voted yes;
   - YB/crvUSD, sdYB/YB and YB/yYB gauges (votes 1230, 1270, 1291);
   - vote-incentive routing of Curve's YB (55% Votium / 45% Votemarket, vote 1267);
   - PegKeeper capacity ×3 (vote 1241).
4. **Kraken listing plus the Legion sale** (Sep–Oct 2025): brand and distribution.

**What did not move TVL:**
- the WETH market (Jan-26);
- HybridVaults (Apr-26; about $3.3M of backing today);
- the v3 relaunch (May-26; net −215 BTC in May);
- cap raises in Jul and Sep-26 (followed by outflows);
- the fee switch (Dec-4), which rewarded veYB, not LPs;
- Merkl PID crvUSD incentives (Jul-26), which target the crvUSD sink pool;
- integrations: Pendle, Aave and ether.fi were promised for Q4-2025 in the MiCA whitepaper and **not found**.

**Marketing:** Kraken and Legion launchpad, Curve News coverage, and a public launch in which "pools filled within a minute" (Curve News 2025-10-22). No paid LP bribes into YB gauges were measured in this work.

## J. Economics

Monthly figures in `economics_monthly.csv`.

| Month | Avg BTC TVL | YB to BTC gauges | Emission $ | Emission cost (% TVL, ann.) | Admin fees accrued (BTC mkts) | Revenue (% TVL, ann.) | veYB distributed |
|---|---|---|---|---|---|---|---|
| Oct-25 | $99.2M | 3.08M | $1.63M | 19.4% | $2.13M | 25.3% | 0 |
| Nov-25 | $143.3M | 5.09M | $2.45M | 20.8% | $4.09M* | 34.7%* | 0 |
| Dec-25 | $184.8M | 4.79M | $2.12M | 13.5% | $0.33M | 2.1% | $1.68M |
| Jan-26 | $207.6M | 4.89M | $1.68M | 9.5% | $0.29M | 1.7% | $0.24M |
| Feb-26 | $161.6M | 3.68M | $0.61M | 4.9% | $1.49M | 12.0% | $1.36M |
| Mar-26 | $158.9M | 4.02M | $0.56M | 4.2% | $0.18M | 1.3% | $0.48M |
| Apr-26 | $154.3M | 3.43M | $0.41M | 3.2% | $0 | 0.0% | $0.01M |
| May-26 | $132.7M | 3.40M | $0.39M | 3.5% | $0.0006M | 0.0% | $0.007M |
| Jun-26 | $98.4M | 3.60M | $0.29M | 3.7% | $0.09M | 1.2% | $0.08M |
| Jul-26 | $98.9M | 3.53M | $0.26M | 3.1% | $0.05M | 0.7% | $0.09M |
| Aug-26 | $110.1M | 3.72M | $0.30M | 3.2% | $0.04M | 0.4% | $0.03M |
| Sep-26 (to 20th) | $112.4M | 2.69M | $0.24M | 3.7% | $0.004M | 0.06% | $0.03M |

\*Nov-25 includes v1 admin fees realised at migration.

- **Fee switch (2025-12-04):** 17.55 BTC accrued (PR Newswire). The first four epochs paid $409k, $419k, $407k and $448k. Epochs after April 2026 paid $0.7k–$30k per week. Epoch 41–42 paid about $1.1–1.2k per week against 142.9M veYB.
- **Totals, Oct-25 to Sep-26:**
  - emissions $11.69M, of which $10.95M went to BTC gauges;
  - admin fees accrued $8.86M (BTC $8.70M);
  - veYB distributions $4.01M.
- DAO #21 (2025-12-01) sent the converted v1 fees, 6.02 WBTC + 20.24 cbBTC + 18.54 tBTC, to 0xa410…a9DF "for distribution". I did not verify how that address distributed them.
- **Cost per $ of TVL:**
  - About **$0.14–0.21 of YB per $1 of BTC TVL per year** in Q4-2025.
  - About **$0.03–0.04 per year since Mar-2026**. This is mostly because the YB price fell 80%+, not because the schedule changed: YB emitted per month is flat at 3.4–5.1M.
  - Revenue per $ of TVL has been below 1.2% annualised for six straight months.
- **The protocol pays no interest to Curve.** Curve's "price" is 7.5% of YB (75M, vesting with emissions) plus the peg and PegKeeper externality.

## K. Verdict: fit for our "BTC collateral + dollar loan" product

**What to copy:**
- **An on-chain, rules-based dollar leg.** The credit line is sized by governance votes and reclaimable. No off-chain lender is needed, and debt scales with deposits.
- **Hard, governance-set caps (cap = allocation / 2).** Growth was fully visible and controllable. Every cap step filled instantly, which proved demand before capacity was added.
- **A "net pressure" metric** (debt − stable inside the LP), with an automatic, pre-funded incentive (15% of fees → PID → sink pool) to protect the dollar leg in a crash. This is a useful risk KPI for any BTC-plus-stablecoin strategy.
- **An explicit book-value versus exit-value disclosure (TRD)** on the dashboard and in the API. Our product should publish the realisable number, not only the book NAV.
- **Immutable core, with migration instead of upgrades.** Plus clean public APIs: every panel maps to a contract field and daily snapshots are exposed.

**What to avoid:**
- **Marking NAV at a lagging internal price** (`price_scale`). It hides impermanent loss for weeks. Book PPS rose in Feb-26 while exits paid 16–21% less.
- **Promising "no IL" or "TRD resolves in hours".** The data shows 76-day TRD streaks and a 24% `price_scale` lag today.
- **Headline APR paid in a governance token** (YB −87%) while the LPs who stake forfeit fees and absorb losses first (watermark). Retail stakers in v2 lost 2.6–3.4% of BTC principal at migration.
- **A single-counterparty, single-venue dependency.** Curve controls the credit line, the pool parameters and the oracle, and Curve's EmergencyDAO holds the kill switch. Governance is fast (median about 21 h) and team-concentrated (about 42% of locked YB in CliffEscrows).
- **Yield that only exists in high volatility.** Fees are about 30–40% of equity gross in volatile months, but about 30–60% of that goes to re-pegging, and in calm months net unstaked yield is 0–4%.
- **No live bug bounty at a $100M+ TVL protocol.**

**Fit.**
- **As a component (for example, allocating part of the BTC sleeve into unstaked v3-cbBTC): only opportunistic.**
  - Expected BTC yield is about 0–5% net in calm regimes and higher in volatile ones.
  - Tail risk is a 5–20% exit discount lasting weeks, crvUSD peg and Curve-governance risk, and BTC-wrapper risk.
  - Staking for YB is not suitable for a BTC-denominated mandate.
- **As a design template: partly.**
  - The "protocol-minted dollar credit line, capped and governance-sized" model and the net-pressure and TRD transparency are worth copying.
  - The AMM-based 2x LP strategy is not. Its economics are short-volatility against a lagging peg.
  - A carry product with explicit loan pricing (a borrow rate paid to an external lender and a mark-to-market NAV) is easier to explain and to risk-manage.

## Files

- `deepdive.md` (this file)
- `tvl_monthly.csv`: month, pool, asset, book and redeemable TVL in asset and USD, net flows (method column), cap, debt. Also the all-BTC sum and DefiLlama protocol rows
- `yield_monthly.csv`: month, pool, `unstaked_realized_apy` (book), `staked_reward_apy`, `crvusd_rate`, `rebalancing_loss_est`, notes, plus redeemable APY, interest paid, interest % of equity, gross pool income, watermark gap, TRD, PPS start and end
- `yield_protocol_monthly.csv`: TVL-weighted BTC series and the organic/incentive split
- `economics_monthly.csv`: emissions (YB and $), admin fees, veYB distributions, cost per $ TVL
- `holders_buckets.csv`: buckets per market and combined
- `events.csv`: 110 dated events (YB DAO, Curve DAO, on-chain credit-line changes, launches, stress), with BTC TVL at d−1 and d+7
- `liquidity_ladder.csv`: preview_withdraw haircuts by size, `price_scale` lag, pool composition
- `raw/`: API dumps, archive month-end reads (`archive_monthend.json`), credit-line bisect, TRD stats, staked principal, holding-period returns, holder positions, MiCA whitepaper and Terms text, docs text
- `scripts/`: `ybrpc.py` (RPC and batch helpers), `fetch_docs.py`, `ybapi.py`, `pager.py`, `archive_monthend.py`, `credit_line.py`, `snap.py`, `build_monthly.py`, `agg_events.py`, `economics.py`, `yield_summary.py`, `holding_period.py`, `staked_principal.py`, `trd_stats.py`, `liquidity_ladder.py`, `holders.py`, `holders_analysis.py`, `holders_aggregate.py`, `build_events.py`
