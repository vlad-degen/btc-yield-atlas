# ether.fi Liquid BTC (liquidBTC): deep dive

*Scripts: [`tools/top5/etherfi/`](../../../tools/top5/etherfi/), data: [`data/top5/etherfi/`](../../../data/top5/etherfi/). Mentions of `scripts/` and `raw/` below refer to the working folder; the `raw/` dumps are not published.*

Snapshot: 2026-09-20 14:00 UTC (Ethereum block 26,019,182; Optimism block 157,157,012). Written 2026-09-22.

Everything below comes from archive `eth_call`/`eth_getLogs` against Ethereum, Optimism and Scroll, from Blockscout, DefiLlama and the ether.fi docs (`llms-full`). Scripts and raw dumps are in `scripts/` and `raw/`.

**Labels used in this document:**
- **(est.)** marks a modelled number.
- **(unverified)** marks a claim that was not checked on-chain.
- **NOT FOUND** means the item was searched for and not found.

**Main check:** a month-end balance sheet was rebuilt from on-chain positions. It covers:
- the vault itself;
- 9 IntoTheBlock (ITB) position-manager contracts owned by the vault;
- Morpho, Aave and Spark accounts;
- assets bridged to Berachain, Corn, Scroll and Optimism.

This rebuilt balance matches the accountant's NAV (share supply on every chain × exchange rate) within **±0.5% in every one of the 21 funded months**. The position history below is therefore complete, not a sample.

---

## 0. Ten findings that change the picture

1. **The strategy did not start as "BTC rate arbitrage + points" and switch to stablecoin carry later.**
   - Stablecoin carry was there from the start. On 2024-12-20, the vault's first strategy transactions borrowed USDC on Aave against WBTC and put it into Usual USD0++ and MEV Capital's Usual USDC vault.
   - Q1-2025 ran both books together, with up to **$19.1M of stablecoin debt**:
     - BTC side: PT-LBTC loops, Pendle points PTs, MEV Capital BTC vaults.
     - Stablecoin side: Morpho WBTC/USDC, eBTC/USDC and eBTC/USR loans into Usual and Resolv.
   - The regimes after that are in §B.
2. **Borrowing on Spark started in Nov-2025, not Aug-2026.**
   - From Nov-2025 it ran through an ITB contract: LBTC on Spark → PYUSD borrowed → Euler ePYUSD vault, plus Merkl PYUSD rewards.
   - Direct Spark borrowing by the vault began on **2026-08-25**.
   - Cap stcUSD first appeared on 2026-01-17. Sentora Paypal USD Main first appeared on 2026-05-13.
3. **Much of the strategy ran outside the vault address.**
   - Aug-2025 to Apr-2026: three **ITB (IntoTheBlock Corp.) "SupervisedLoanPositionManager"** loops held up to 275 BTC of collateral (285 BTC including idle eBTC, 65–73% of NAV) and up to $13.5M of debt in separate contracts. The vault owns these contracts; ITB bots are the executors.
   - About 150 BTC sat on Corn from Jun-2025 to Nov-2025, and 100 eBTC sat on Berachain in Apr–May 2025. Both were for points.
   - None of this is visible from the vault address's token balances alone.
4. **Realized yield is thin and mostly came from incentives (est.).**
   - Realized net APY: 1.96% over the last year and **~1.84%/yr since launch** (+3.42% cumulative).
   - The vault earned depositors **≈10.0 BTC net** (≈$0.84M), and the platform took **4.53 BTC ($0.42M) in claimed fees**.
   - **Identified incentives were ≈$0.63M, about 50% of gross yield**:
     - $187k of ETHFI sent into the vault in Jan–Feb 2025;
     - $355k of Merkl RLUSD/PYUSD;
     - $43k of MORPHO;
     - $41k of FXN/CRV.
   - Our leg-level estimate of organic stablecoin carry is roughly **zero to negative (−$0.08M)**.
5. **The vault ran at negative carry for months.**
   - The share price fell from 1.01432 (24-Mar-2025) to 1.01369 (June 2025) and stayed flat until August 2025. That is **5 months with ~0% or negative realized APY**, while the vault held 480–850 BTC.
   - Organic spread (with incentives removed) was negative in 12 of 20 months with debt (11 if May-26 at −0.006% is counted as zero).
6. **The current trade is the same Spark → Cap + Sentora structure, and it only pays because of PYUSD rewards.**
   - If today's composition had been held since Jan-2026, the organic spread would have been negative every month until Aug-2026.
   - The total spread, including Sentora's PYUSD rewards, was +0.1% to +1.9%.
   - At the snapshot the carry adds about +0.9% APY to NAV (est.).
7. **Risk now:**
   - LTV 61.6% and health factor 1.283 on Spark (Spark's own oracle, WBTC at $80,442), with Spark's liquidation threshold at 79.05%.
   - Liquidation at **BTC ≈ $62.7k (−22%)**.
   - The peak-risk month was July 2026: Morpho LBTC/PYUSD at 70.7% LTV against an 86% LLTV, HF ≈1.22 at month-end and **≈1.13 at the 1-July low** (est.).
   - Leverage was cut in only two drawdowns: the Apr-2025 unwind (done at the BTC low of ~$76k) and the Apr-2026 Kelp/LayerZero emergency. In Jun–Jul 2026 LTV was allowed to drift to 71%.
8. **Governance runs without a timelock.**
   - A 4-of-6 "Liquid Safe" (`0xcea8…ec96`) owns the RolesAuthority. It can change the Merkle root, fees, rate providers and authority **instantly**.
   - A strategist EOA (`0x18de…7e99`) can post the NAV rate (±0.5% per update, at least 6 h apart).
   - A strategist Safe (2-of-5) holds the fee-setting role.
   - For comparison, eBTC has a 5-day timelock and Kraken's vault has a 1-hour timelock.
9. **Fees on-chain do not match the fact sheet.**
   - The fact sheet says "1% platform / 0% performance".
   - On-chain the platform fee has been changed **8 times**: 2% → 0 → 2% → 1% → 0 → 0.5% → 1% → 0.5% → **0% since 2026-08-24**.
10. **TVL collapsed because the source asset collapsed.**
    - **70% of all Ethereum deposits were eBTC** (1,469 of 2,096 BTC).
    - eBTC supply on Ethereum fell **6,858 → 277 (−96%)** after the points programs ended.
    - Two whales explain most of the swings: +380 shares in Jul-2025 then −381 in Aug-2025, and −238 shares in Apr-2026.
    - Today **39% of all liquidBTC (87 shares, ~90 BTC)** sits as collateral in ether.fi's Aave-v4-based Borrow/Cash market on Optimism.

---

## A. Passport

| Item | Value |
|---|---|
| Token | liquidBTC, "Ether.Fi Liquid BTC", 8 decimals; base asset WBTC; share price 1.03425 BTC at the snapshot (launched at 1.0) |
| BoringVault | `0x5f46d540b6eD704C3c8789105F30E075AA900726`, same address on Ethereum, Optimism and Scroll |
| Accountant | `0xEa23aC6D7D11f6b181d6B98174D334478ADAe6b0` (AccountantWithRateProviders) |
| Teller | `0x8Ea0B382D054dbEBeB1d0aE47ee4AC433C730353` (LayerZeroTellerWithRateLimiting; deployed 2025-03-12, replacing an earlier teller) |
| Manager | `0xaFa8c08bedB2eC1bbEb64A7fFa44c604e7cca68d` (ManagerWithMerkleVerification) |
| RolesAuthority | `0x49F954c67ff235034b69b8a59fbe309A40256c8d` |
| Queue / Solver | BoringOnChainQueue `0x77A2…1Edf` and BoringSolver `0xed41…8929` (since 2025-12-12). Before that: AtomicSolverV3 `0x9894…66d7` plus the legacy AtomicQueue |
| Deployed | **2024-11-14 23:22 UTC** (tx `0xd20924a2…00d7`, block 21,189,184) |
| First deposit / first rate update | 2024-12-18 (test amount), first large deposit 2025-01-07, first rate update 2025-01-09 |
| Chains | Ethereum (strategy and assets); **Scroll** (shares only, for ether.fi Cash, 2025-03-18 → migrated out in Apr-2026); **Optimism** (shares plus a withdrawal buffer, 2026-04-05 →) |
| Status | Live. Deposits in WBTC, cbBTC and eBTC (LBTC disabled 2026-09-17). **Withdrawals only in eBTC** (WBTC/LBTC/cbBTC withdrawals disabled in the queue) |
| Size (snapshot) | **231.56 BTC NAV ≈ $18.8M**: 133.61 shares on Ethereum, 90.28 on Optimism, 0.002 on Scroll. DefiLlama pool LIQUIDBTC shows $12.0M (Ethereum shares only). The app shows $20.1M (at a higher BTC price) |
| Peak | 848.7 BTC / **$98.2M** at the end of Jul-2025 |
| Holders | Ethereum **401**; Optimism **132** (full `balanceOf` sweep; sum equals supply), of which one, the Aave v4 Hub, holds 96%. Optimism peaked at 691 in Jul-2026, before Cash balances moved into the Hub. Ethereum holder count peaked at 421 (Mar-2026) |
| Operator | ether.fi. Distributed in the ether.fi app (Liquid/Cash); not available in the US, Canada or UK (fact sheet). Legal entity: NOT FOUND in docs |
| Infrastructure | Veda (Seven Seas team) BoringVault |
| Strategy provider | "Nonce" / Nonce Capital (docs: "primary strategy provider for all live vaults"). Much of the execution in Aug-2025–Apr-2026 was delegated to **IntoTheBlock** position-manager contracts |

**Size history (month-end, BTC NAV):**

| Month | NAV (BTC) |
|---|---|
| Jan-25 | 214 |
| Feb-25 | 609 |
| Mar-25 | 625 |
| Apr-25 | 638 |
| May-25 | 488 |
| Jun-25 | 554 |
| Jul-25 | **849** |
| Aug-25 | 452 |
| Sep-25 | 475 |
| Oct-25 | 398 |
| Nov-25 | 373 |
| Dec-25 | 388 |
| Jan-26 | 422 |
| Feb-26 | 446 |
| Mar-26 | 470 |
| Apr-26 | 215 |
| May-26 | 212 |
| Jun-26 | 192 |
| Jul-26 | 198 |
| Aug-26 | 214 |
| 20-Sep-26 | 232 |

USD figures are in `tvl_monthly.csv`.

---

## B. Mechanics and how the strategy changed

**Mechanics today:**
1. The user deposits WBTC, cbBTC or eBTC through the Teller (Ethereum) or through the Optimism teller. Cash users top up via TopUp contracts. The user receives liquidBTC at the accountant rate.
2. The strategist executes Merkle-whitelisted calls through the Manager.
3. Today that means:
   - WBTC and cbBTC are supplied to **Spark**;
   - **PYUSD and USDC** are borrowed;
   - USDC → cUSD → **Cap stcUSD**;
   - PYUSD → **Sentora "Paypal USD Main"** (a Morpho VaultV2);
   - Merkl PYUSD rewards are claimed almost daily;
   - about 13 eBTC on Ethereum plus 7.5 eBTC and 1.8 WBTC on Optimism are kept as the withdrawal float.
4. The rate is posted to the accountant roughly daily (524 updates). Withdrawals go through the BoringOnChainQueue and are filled by the BoringSolver in eBTC.

**Strategy regimes.** These come from month-end positions (`positions_monthly.csv`) and event logs (`events.csv`).

| Period | BTC side | Stablecoin side | Debt peak | Realized APY |
|---|---|---|---|---|
| Dec-24 → Mar-25: "everything at once" | PT-LBTC/WBTC Morpho loop (30 WBTC debt); Pendle PT-liquidBeraBTC, PT-LBTC, PT-corn-LBTC/eBTC; MEV Capital Pendle-WBTC; Aave WBTC/cbBTC/LBTC supply | Aave USDC plus Morpho WBTC/USDT, WBTC/USDC, eBTC/USDC and eBTC/USR, deployed into **Usual (USD0++, MEV Capital Usual USDC)**, **MEV Capital Resolv USR**, and the f(x) USDC/fxUSD LP on Convex | **$19.1M** (Mar-25), LTV 47–51% | 9.6% (Jan), 8.6% (Feb). About 0.6 pp of January's 0.78% monthly gain came from **120.1k ETHFI** sent in and sold |
| Apr-25 → Jul-25: "points only, carry off" | 100 eBTC to Berachain (Apr–May); tacBTC (TAC) 39 BTC; **150 BTC to Corn** (90 BTCN + 60 LBTC, 2-Jun → Nov); Aave LBTC supply 139–199 | Stablecoin book unwound 9–10 Apr-25 during the BTC ~$76k drawdown. Only $3M Aave USDC vs fxUSD LP remained until June | $3M | **−0.4% to +0.04%** (negative carry) |
| Aug-25 → Mar-26: "ITB outsourced loops" | Collateral held in ITB contracts: 150 eBTC (Aave), then 140 eBTC (Aave) plus 135 LBTC (**Spark**) | ITB #1/#2: Aave **RLUSD** → Euler eRLUSD vaults (+Merkl RLUSD). ITB #3: Spark **PYUSD** → Euler ePYUSD (+Merkl PYUSD). From Jan-26 also direct Aave USDT/USDC → **wstUSR** (to Feb-17) and **Cap stcUSD** | **$17.1M** (Jan-26), LTV 50–60%, HF 1.2–1.4 | 1.0–3.2% |
| Apr-26: forced deleverage | Kelp rsETH / LayerZero exploit (18-Apr). Vault paused ~1 day, bridging off to 24-Apr. All debt repaid by 2-May. A whale exited 238 shares on 1-Apr | — | 0 | 1.9% |
| May-26 → Aug-26: "Morpho LBTC/PYUSD" | 174–192 LBTC collateral on Morpho (LLTV 86%) | 7.0–8.5M PYUSD → **Sentora Paypal USD Main / PRIME Main** plus stcUSD. In Jul–Aug-26, 1.75M USDC went via CCTP to Optimism into sibling vault **liquidRWA** | $8.5M; LTV **70.7%** (Jul) | 1.2–2.1% |
| 25-Aug-26 → now: "Spark" | LBTC swapped to WBTC/cbBTC *through the eBTC vault* (related-party swap). 207.9 BTC on Spark | 5.93M PYUSD + 4.37M USDC → **stcUSD 6.14M + Paypal USD Main 4.15M** | $10.3M, LTV 61.6% | 1.2–1.7% |

**Answer to "when did it start borrowing stablecoins on Spark and deploying into Cap/Sentora?"**
- Stablecoin borrowing: 2024-12-20 (Aave).
- Spark borrowing: 2025-11-07, via ITB, as PYUSD.
- Cap: 2026-01-17.
- Sentora: 2026-05-13.
- Spark as the vault's own borrowing venue: 2026-08-25.
- USDC on Spark: 2026-09-18.

---

## C. Counterparty chain and who controls each link

**Custody and assets:**
- WBTC: BitGo / BiT Global custody (per the earlier dossier, unverified here).
- cbBTC: Coinbase.
- eBTC: ether.fi's own BTC LRT, a Veda vault with a 5-day timelock (ether.fi incident page). It is also used as the withdrawal asset and as a swap counterparty.
- LBTC: Lombard (rate provider variable since 2025-08-06).
- Borrowed: PYUSD (Paxos Trust Co.; PayPal brand) and USDC (Circle).

| Link | Contract | Who controls it (read on-chain) |
|---|---|---|
| Vault admin (OWNER role 8: Merkle root, fees, rate providers, authority, bridge peers) | RolesAuthority `0x49f9…8c8d` | **Safe 4-of-6 `0xcea8…ec96`** ("Liquid Safe", confirmed by the ether.fi incident page); **no timelock**. Owners: `0x95a2…4bef`, `0x4a4e…3eeb`, `0x3de2…329f`, `0x8395…a1c`, `0xe637…05c9`, `0x9eac…843f` (identities not public; docs say Veda plus ether.fi members) |
| Strategist (role 7, Merkle-verified `manage`) | Manager `0xafa8…976` | EOA `0x18de…7e99` (nonce 173), EOA `0xc811…23a2` (bot, nonce 1,586), Safe **2-of-5** `0x607d…7306` |
| NAV rate updater (role 11) | Accountant | Safe 2-of-4 `0x41df…a6ae`, Safe 2-of-4 `0x71e2…cd6` (they share 3 owners) and **EOA `0x18de…7e99`**. Bounds ±0.5% per update, minimum 6 h (21,600 s), otherwise auto-pause |
| Fee setting (role 55) | Accountant | Strategist Safe 2-of-5 `0x607d…7306` (granted 2026-01-28) plus the owner |
| Pausers (roles 5/14/16/20) | all modules | Veda `Pauser` contract `0xe71f…af6c`; EOAs `0x9af1…844d`, `0x13ed…b07f`, `0x4a21…6b66`; Safe 2-of-N `0x7859…74ea`; strategist Safes (Hypernative per docs) |
| Solver / queue | BoringSolver, queue | Solver-origin EOAs `0xf855…909e` (interim RolesAuthority owner at deployment, then the AtomicQueue-era solver; 12k txs), `0xd230…6ca2`, `0xdb83…b0a2` |
| Fee payout | `0xf6bd…a863` | Safe 2-of-5 (earlier: Safe 3-of-6 `0x68ec…8cfa`, Safe 3-of-5 `0xa996…b95a`, PaymentSplitter) |
| ITB position managers (Aug-25→Apr-26) | SLPM `0x7aaf…3726`, `0xfbca…f436`, `0x11fd…d2`; LoanManagers `0xcb67…2877`, `0x8676…49a3`, `0x2afb…8656`; YieldPositions `0x8950…6d56`, `0x832f…9e`, `0x0757…6fd6` | `owner()` is the vault; only the owner can withdraw. Executors are ITB EOAs `0x50b3…2737` and `0x6990…3f1a`, which can supply, borrow, repay and unwind within the loop. Target HF 1.16, 1.35 and 1.25. Code is UNLICENSED (`@itb/quant-common`); **audit NOT FOUND** |
| Spark (lending) | Pool `0xC13e…E987` | ACL admin and PoolAddressesProvider owner `0x3300…f8c4` (Spark SubProxy under Sky governance; delay not read). WBTC price = Chainlink WBTC/BTC × BTC/USD. cbBTC price = Chronicle "Aggor" BTC/USD (Chronicle + Chainlink + RedStone), with **no cbBTC/BTC check**. PYUSD and USDC use a **fixed $1** oracle. WBTC LTV/LT/bonus 77/78/7%; cbBTC 81/82/8%; LBTC LTV 0 (frozen) |
| Morpho (May–Aug-26) | LBTC/PYUSD market, LLTV 86% (oracle `0x0aea…64b1f`) | Immutable market |
| Cap stcUSD / cUSD | `0x8888…8888` / `0xcccc…cccc` (UUPS proxies) | Cap access-control admin (not traced further). cUSD reserves are USDC plus wWTGXX (WisdomTree), lent to Cap "operators" (institutions) with restaking cover (unverified here) |
| Sentora Paypal USD Main | Morpho VaultV2 `0xb576…9FB2` | Owner Safe **1-of-1** `0xe8c9…8008`, curator Safe 1-of-1 `0x9e39…aac0`. Lends PYUSD into Morpho markets incl. Kraken's kBTC/PYUSD. Rewards are PYUSD via Merkl |
| ether.fi Borrow on Optimism (holds 39% of liquidBTC) | Aave v4 Hub `0x6675…C572` (TransparentUpgradeableProxy → HubInstance by Aave Labs) | liquidBTC Product LTV 50%, CF 70%, liquidation bonus 15%. Priced by the **Veda accountant rate × Chainlink BTC/USD** (ether.fi docs) |

**Related-party flows:**
- Swaps between LBTC and WBTC/cbBTC routed through eBTC (Sep-2026).
- The 1.75M USDC parked in liquidRWA (Jul–Aug-2026).
- eBTC as the only withdrawal asset.
- The strategist Safe sent 2,750 cUSD into the vault on 16/17-Sep-2026 (block 25,993,319).

---

## D. Who manages it

- **ether.fi** is the product owner, distributor, fee recipient and co-signer on the admin Safe.
  - CEO and co-founder **Mike Silagadze** (confirmed by CoinDesk, Jan-2026, and Crunchbase); co-founder Rok Kopp (per search results).
  - ETHFI incentives came in from Safe `0xd022…c90b`, which is likely an ether.fi treasury (unverified).
- **Nonce Capital** (nonce-capital.xyz) is named strategy provider for Liquid ETH ($487M), USD ($104M) and BTC ($20.1M), about $611M in total.
  - No team names, legal entity or location are published.
  - It lists Certora and Hypernative as security partners.
  - Its relationship to Seven Seas: NOT FOUND. Older docs named Seven Seas as the strategist of Liquid. Seven Seas Capital is run by Sun Raghupathi (CEO) and Stephanie Vaughan (COO) (PRNewswire, 10-Dec-2024).
  - Nonce Classic (the Seoul VC that invested in ether.fi) is a different entity as far as we could find.
- **Veda** provides the BoringVault, accountant, teller, queue, solver and Merkle manager, and co-signs the admin.
- **IntoTheBlock Corp.** designed and executed the Aug-2025–Apr-2026 loops through its position-manager contracts.
- **Audits:**
  - BoringVault stack: Spearbit, Macro (0xMacro), Secure3 and Hexens (per ether.fi docs; repo `Se7en-Seas/boring-vault/audit`); earlier dossier also lists Sigma Prime and Certora.
  - ITB contracts, the vault's Merkle root/decoders, and the BoringOnChainQueue deployment specific to liquidBTC: no public audit found.
- **Incidents:**
  - 2026-04-18: Kelp rsETH/LayerZero exploit. Precautionary pause of all Liquid vaults, bridging off for 5 days, deleveraging, no loss.
  - 2026-09-11: legacy AtomicQueue exploit (≈$40k user losses across Liquid tokens). liquidBTC's transfer hook now denies the old queue (`DenyOperator 0xd458…ea07`).
  - The vault itself had no loss. Morpho "Liquidate" on 2026-05-16 was dust bad-debt on a legacy PT position (0.00076 WBTC).

---

## E. Yield

**Realized, from the accountant's 524 rate updates:**
- 7d 1.47%, 14d 1.71%, 30d 1.37%, 90d 1.56%, 180d 1.79%, **365d 1.96%**.
- Since launch: +3.425% cumulative, 1.84%/yr.
- These match the app's figures and DefiLlama's (1.36% 30-day).

**Monthly table.** Full version in `yield_monthly.csv`. Borrow rates come from Spark/Aave `getReserveNormalizedVariableDebt` and Morpho share indices. Deployment rates come from ERC-4626 share prices. Rewards come from Merkl, URD and ETHFI flows valued with DefiLlama prices. Legs are weighted by the average of start and end month balances (est.).

| Month | Net APY | Spark PYUSD | Spark USDC | stcUSD | Paypal Main total / organic | Actual borrow | Actual deployment organic / +rewards | Spread / organic |
|---|---|---|---|---|---|---|---|---|
| Jan-25 | 9.55 | – | 13.3 | – | – | 9.2 | 14.4 / +0 | +5.2 / +5.2 |
| Feb-25 | 8.62 | – | 8.9 | – | – | 5.9 | 11.7 / +1.7 | +7.5 / +5.8 |
| Mar-25 | **−0.15** | – | 4.8 | – | – | 5.9 | 5.7 / +1.2 | +1.0 / **−0.2** |
| Apr-25 | **−0.42** | – | 3.3 | – | – | 9.2 | 2.9 / +3.7 | **−2.6 / −6.3** |
| May-25 | 0.04 | – | 4.9 | – | – | 5.0 | 0.6 / +7.0 | +2.5 / **−4.4** |
| Jun-25 | **−0.07** | – | 4.4 | – | – | 5.3 | 0.3 / 0 | **−5.0 / −5.0** |
| Jul-25 | 0.01 | – | 8.3 | – | – | no debt | – | – |
| Sep-25 | 1.08 | 2.8 | 6.0 | 12.3 | – | 4.5 | 6.3 / +3.7 | +5.5 / +1.8 |
| Dec-25 | 3.15 | 5.2 | 4.7 | 6.2 | – | 4.7 | 1.4 / +4.8 | +1.6 / **−3.2** |
| Jan-26 | 2.20 | 5.0 | 4.8 | 6.9 | 6.7 / 1.5 | 4.3 | 2.0 / +7.4 | +5.1 / **−2.3** |
| Apr-26 | 1.94 | 4.1 | 4.7 | 5.7 | 5.9 / 1.7 | 5.6 | 4.5 / +0.7 | **−0.2 / −0.9** |
| Jun-26 | 2.01 | 3.8 | 4.6 | 5.2 | 5.0 / 1.7 | 3.6 | 3.3 / +3.1 | +2.8 / **−0.3** |
| Aug-26 | 1.16 | 3.8 | 4.3 | 5.2 | 5.9 / 2.3 | 4.9 | 3.8 / +1.9 | +0.7 / **−1.2** |
| Sep-26 (1–20) | 1.74 | 4.0 | 4.3 | 5.7 | 5.8 / 2.8 | 4.1 | 4.1 / +1.9 | +1.9 / 0.0 |

**Negative-carry episodes:**
1. **Mar–Jul 2025**:
   - The accountant rate fell on most days from 15-Mar to 1-Jul-2025.
   - Cause: Usual/USD0++ yields collapsed while Morpho USDC borrow cost 5–10%.
   - This was followed by an idle points-only book (Corn, Berachain, TAC), which earned **0 BTC**. The 150 BTC sent to Corn came back as 150 BTC.
2. **Dec-25 → Mar-26 (organic)**:
   - Euler RLUSD/PYUSD vaults paid 1–2% organic against 3.6–5.2% borrow cost.
   - Merkl rewards (RLUSD/PYUSD) carried the whole spread.
3. **Apr-26 / May-26**: total spread ≈0 because of the deleverage and the Kelp-driven rate spikes.
4. **Aug-26**: organic −1.2%.

**Held-structure test.** Take today's mix (6.14 stcUSD + 4.15 Paypal Main against 5.93 PYUSD + 4.37 USDC on Spark) and hold it from Jan-2026:
- organic spread: **−1.7% to +0.4%** (negative until Aug-26);
- total spread with Sentora rewards: **+0.1% to +1.9%**.

**Incentives and points (est.):**

| Source | Amount | Share of gross yield |
|---|---|---|
| ETHFI into NAV (Jan–Feb-25) | 120.1k ETHFI ≈ $187k | 15% |
| Merkl RLUSD (Euler, ITB #1/#2) | 149.5k RLUSD | 12% |
| Merkl PYUSD (Euler, ITB #3) | 148.6k PYUSD | 12% |
| Merkl PYUSD (Sentora/Morpho, from Jun-26) | 56.9k PYUSD | 5% |
| MORPHO (URD) | 26.5k MORPHO ≈ $43k | 3% |
| FXN + CRV (Convex f(x)) | ≈ $41k | 3% |
| **Total identified** | **≈$626k** | **≈50%** of gross yield ($1.25M = $0.84M net + $0.42M fees) |

Off-NAV incentives were paid by ether.fi directly to users and could not be sized per vault:
- "Summer Mint" (Aug–Sep-25, 250k ETHFI deposit pool shared across Liquid USD/ETH/BTC);
- "Triple Dip" (Oct–Nov-25, 100k ETHFI deposit pool);
- the eBTC-level "Golden Bull" campaign (>$2M ETHFI plus 4× Lombard Lux);
- Babylon, Lombard, Corn Kernels, Berachain and ether.fi points.

These points and campaigns were the real reason to hold liquidBTC in H1-2025, but the vault's BTC yield in that period was about zero.

**Stability.**
- Monthly net APY swung between −0.4% and +9.6%.
- Since Sep-2025 it has held within 1.0–3.2% with no negative month.
- 30-day APY dropped from ~2.0% (H1-26) to 1.2–1.4% (Aug–Sep-26). The fee went to 0, but the spread narrowed by more.

---

## F. Risk management

**LTV and health factor by month (month-end).** HF is the minimum across the vault's accounts. "Low" is the HF at the month's lowest daily BTC close (est.).

| Month | Collateral BTC | Debt | LTV | HF | HF at month low | Liquidation BTC price (est.) |
|---|---|---|---|---|---|---|
| Feb-25 | 433 | $18.8M | 51% | 1.42 | 1.42 | ~$59k |
| Mar-25 | 494 | $19.1M | 47% | 1.31 | 1.24 | ~$63k |
| Sep-25 | 150 | $10.2M | 60% | **1.21** (ITB #1) | 1.14 | ~$95k |
| Jan-26 | 408 | $17.1M | 53% | 1.32 | 1.32 | ~$60k |
| Feb-26 | 408 | $13.8M | 50% | 1.38 | 1.29 | ~$49k |
| Jun-26 | 174 | $7.0M | **69%** | 1.25 | 1.25 | ~$47k |
| Jul-26 | 192 | $8.5M | **71%** | 1.22 | **1.13** | ~$52k |
| Aug-26 | 196 | $7.7M | 50% | 1.52 | 1.21 | ~$52k |
| 20-Sep-26 | 208 | $10.3M | 61.6% (Spark oracle) | **1.283** | 1.19 (16-Sep) | **$62.7k (−22%)** |

**How the vault deleveraged:**
- **9–10 Apr-2025**: all Morpho stablecoin debt repaid (≈$9M) and Usual/Resolv exited, at the BTC low of $76k.
- **Mar–Apr-2026**: ITB loops closed.
- **18-Apr → 2-May-2026**: full repay under the Kelp emergency.
- **Aug-2026**: migration from Morpho to Spark.
- No rule-based deleverage policy is published (NOT FOUND). ITB contracts carried target HFs (1.16/1.25/1.35). Morpho LBTC/PYUSD was allowed to reach 71% LTV against an 86% LLTV.

**Liquidity ladder for repaying the $10.30M** (`liquidity_ladder.csv`):
1. **Sentora Paypal USD Main** redeem: 4.155M PYUSD in the same block. `eth_call` simulation from the vault succeeded at the snapshot. The Sentora vault held $21.7M idle PYUSD out of $436M.
2. **stcUSD** redeem: 6.139M cUSD, instant ERC-4626 with no cooldown. Only new profit vests over 24 h.
   - Then **cUSD.burn → USDC** for 6.139M USDC, fee 0, in the same transaction.
   - Limit: Cap's available USDC was $19.8M at 76.6% utilization, so the vault would take 31% of it.
3. Stablecoins ≈ debt ×1.000. Currency mismatch: about **$1.77M of USDC has to be swapped into PYUSD** (DEX slippage not measured).
4. After repayment, 207.9 BTC (153.08 WBTC + 54.80 cbBTC) is released.

**User withdrawals:**
- Queue parameters: eBTC only, maturity 1 h, deadline at least 3 days, discount 0–10 bps.
- Buffer: 13.3 eBTC plus about 9.4 BTC on Optimism, around 10% of NAV.
- Larger exits need the strategist to deleverage and mint eBTC (the vault did 294 eBTC `Enter`s).
- The docs say withdrawals "may take up to 3 days".

**Oracles:**
- Spark WBTC: Chainlink WBTC/BTC × BTC/USD.
- Spark cbBTC: Chronicle/Chainlink/RedStone BTC/USD aggregate, with no depeg check.
- PYUSD/USDC debt: fixed at $1.
- liquidBTC collateral in ether.fi Borrow: accountant rate × Chainlink BTC/USD. A mis-posted rate would feed straight into Optimism liquidations.

---

## G. Depositors (snapshot)

`holders_buckets.csv`. BTC-equivalent = shares × 1.03425.

| Bucket (BTC-eq) | Ethereum holders | Ethereum BTC | Optimism holders | Optimism BTC |
|---|---|---|---|---|
| <0.01 | 189 | 0.25 | 111 | 0.10 |
| 0.01–0.1 | 107 | 3.8 | 13 | 0.30 |
| 0.1–1 | 78 | 23.0 | 6 | 1.47 |
| 1–10 | 24 | 71.8 (52%) | 1 (queue) | 1.56 |
| 10–100 | 3 | 39.4 (28.5%) | 1 (**Aave v4 Hub**) | 89.9 (96.3%) |
| >100 | 0 | 0 | 0 | 0 |

**Concentration:**
- Ethereum: top-1 11.5%, top-10 59.4%, top-100 96.7%, HHI 460 (low by DOJ thresholds, but top-10 hold 59%).
- Optimism: HHI 9,283 because of the Hub.
- Combined (address level, 528 addresses): top-1 38.8%, top-10 72.9%, top-100 97.5%, HHI 1,673.

**Address types (Ethereum):**

| Type | Holders | Share of supply |
|---|---|---|
| Plain EOAs | 331 | 85.6% |
| EIP-7702-delegated smart-wallet EOAs | 47 | 14.2% |
| Safes | 4 | 0.2% |
| Contracts (ether.fi Cash TopUp, Hourglass lock depositor, Uniswap v4 PoolManager, queue) | ~19 | <0.1% |

- Optimism is the ether.fi Cash/Borrow side. The Aave v4 Hub holds the collateral of Cash borrowers. Cash accounts (**EtherFiSafe**; 75 identified plus 12 Safe-type contracts) are 87 small holders with 1.3% of Optimism supply. The rest is 2 Cash TopUpDest contracts, 32 EOAs and 6 EIP-7702 wallets.
- No Pendle market for liquidBTC exists; we checked all 444 Ethereum Pendle markets. No Morpho market or other DeFi collateral use exists on Ethereum.
- **Retail vs whale:** 374 Ethereum holders under 1 BTC-eq hold 19.5%; 3 holders at 10 BTC or more hold 28.5%.
- Historically, three wallets deposited 380, 211 and 208 shares. The largest (`0xd1ed…1d0e`) came in 16-Jul-2025 and left 11-Aug-2025.

**Holder count over time (Ethereum):**

| Month | Holders |
|---|---|
| Jan-25 | 165 |
| Feb-25 | 289 |
| Mar-25 | 404 |
| May-25 | 409 |
| Nov-25 | 329 |
| Mar-26 | 421 |
| Jun-26 | 388 |
| Sep-26 | 401 |

**Holder count over time (Optimism):**

| Month | Holders |
|---|---|
| Apr-26 | 502 |
| May-26 | 543 |
| Jun-26 | 616 |
| Jul-26 | 691 |
| Aug-26 | 127 |
| Sep-26 | 132 |

The August drop does not mean users left. Cash accounts moved their liquidBTC into the Aave v4 Hub (ether.fi Borrow), so it is now held by one address. Supply kept rising (57 → 90 shares).

---

## H. TVL growth and flows versus price

`tvl_monthly.csv` decomposes each month's USD change into price, flow and yield. Totals across chains:
- **Cumulative real deposits on Ethereum: 2,096 BTC. Withdrawals: 1,890 BTC.** Optimism-side deposits (mostly eBTC, since Apr-2026) are not itemized; they are included in the all-chain net flow column.
- Deposits by asset: eBTC 1,469, WBTC 442, LBTC 151, cbBTC 35.
- Withdrawals: eBTC 1,536, WBTC 354.

| Period | What happened |
|---|---|
| Jan–Feb-25 | +605 BTC of flows (eBTC points era); TVL $0 → $51M even as BTC fell 18% |
| Mar–Apr-25 | Flows about flat; −207 BTC out in March is offset by new money |
| May-25 | −150 BTC |
| Jul-25 | **+294 BTC** (one whale): peak $98M |
| Aug-25 | **−397 BTC** (the same whale leaves) |
| Sep-25 → Mar-26 | Slow bleed (−77, −26 BTC) then small inflows. USD TVL fell from $54M to $30M mainly on price (BTC $114k → $67k) |
| Apr-26 | **−256 BTC** (whale exit 1-Apr plus Kelp stress); TVL halves to $16M |
| May–Sep-26 | −21 to +18 BTC per month. Recent growth is mostly Optimism/Cash (OP shares 46 → 90) and the BTC rebound |

Yield added only **≈10 BTC over 21 months**; flows and price drove everything else.

---

## I. Growth drivers and why TVL is small now

**Timeline:**
- 2024-11 vault deployed during the eBTC/Lombard/Babylon points boom. The eBTC "Golden Bull" campaign offered >$2M ETHFI plus 4× Lux.
- 2025-01 → 02 ETHFI top-ups inside the vault (9.6% and 8.6% APY in those two months, annualized).
- 2025-03 Scroll/Cash distribution.
- 2025-04 → 06 points farming (Berachain, TAC, Corn).
- 2025-08 → 09 "Summer Mint".
- 2025-10 → 11 "Triple Dip" (ETHFI to Cash users).
- 2026-04 Optimism, Cash and Borrow launch. liquidBTC becomes 50%-LTV collateral in ether.fi Borrow.

**Why TVL is small now:**
1. **The feeder asset died.** eBTC supply on Ethereum fell 6,858 → 277 BTC (−96%). liquidBTC was effectively "eBTC-plus", and 70% of its deposits were eBTC.
2. **Points ended and the base yield was never competitive.** 0% for five months in 2025 and about 2% since. That is not enough to compensate for leverage, cross-chain and curator risk once points are gone.
3. **Whales dominated.** Two exits (−381 and −238 shares) removed about 74% of peak supply (837 shares).
4. **BTC price fell** from $116k (Jul-25) to $59k (Jun-26).
5. **Operational churn.** Eight fee changes, withdrawals restricted to eBTC, many cross-chain moves and outsourced ITB loops make the product hard to underwrite for size.
6. **No DeFi composability on Ethereum** (no Pendle market, no money-market listing). Its only integration is ether.fi's own Borrow/Cash on Optimism, which now holds 39% of supply.

---

## J. Economics

- **Platform fee revenue:**
  - **4.526 BTC claimed ≈ $441k** (11 claims, 2025-08-27 → 2026-09-02, paid in WBTC, LBTC and cbBTC).
  - Theoretical accrual from the fee schedule × NAV: 5.09 BTC ($419k at month-end prices).
  - The first claim alone was 2.67 BTC for the 2%-fee period in H1-2025.
  - Performance fee: 0 throughout.
  - The current on-chain fee is **0%**.
- **Depositors received about 10.0 BTC net**, so fees took about 31% of gross yield (4.5 of 14.5 BTC).
- **Incentive spend:**
  - Inside NAV, ether.fi's ETHFI: ≈$187k.
  - Third-party incentives captured: Merkl RLUSD/PYUSD via Euler and Sentora ≈ $355k (campaign funders presumed Ripple and PayPal/Paxos, unverified); MORPHO $43k; FXN/CRV $41k.
  - Off-NAV ETHFI campaigns: not allocable.
- **Unit economics:**
  - At $18.8M NAV and 0% fee, the vault earns ether.fi nothing.
  - At 1%, it would earn about $190k/yr, less than a third of the ≈$626k of incentives already captured.

---

## K. Verdict

**Copy:**
- Veda-style transparency. Every position, rate and fee change is on-chain and reconstructible to ±0.5%. Publish a monthly position statement off the same data.
- A same-block liquidity ladder. Both deployments redeem atomically, and the stablecoin legs roughly match the debt. Keep that, and match currencies (PYUSD debt ↔ PYUSD asset) so no swap is needed.
- A multi-venue borrow book (Aave → Morpho → Spark) chosen by cost, with fixed-$1 debt oracles and Chainlink WBTC/BTC.
- Using the product as collateral in your own lending app (ether.fi Borrow), which gives sticky retail distribution.

**Avoid:**
- **Incentive-dependent carry marketed as BTC yield.** About half the gross came from ETHFI and Merkl rewards; organic carry was about zero.
- **Points detours with 0% BTC yield** (Corn 150 BTC for 5 months, Berachain, TAC), which cost 5 months of flat NAV.
- **Hidden sub-managers.** The ITB loops held more than half of NAV in separate contracts with bot executors and no public audit.
- **Related-party routing** (swaps through eBTC, parking in liquidRWA) without disclosure.
- **A rate-posting EOA and a 4-of-6 admin with no timelock.** Use ≥24 h timelocks on Merkle root and fee changes, as eBTC does (5 days).
- **Fee instability** (8 changes, docs out of date) and **exit only in eBTC**.
- **Letting LTV drift to 71%** with no published deleverage rule. Deleverage was forced only by the Kelp emergency.

---

## Methodology and limits

- **Month-end blocks** are the last block at or before 23:59:59 UTC. The snapshot is 2026-09-20 14:00 UTC. BTC/USD is DefiLlama's daily close (the snapshot row uses $81,169, while Spark's oracle read $80,442).
- **NAV** = (Ethereum + Optimism + Scroll totalSupply) × accountant rate.
- **Reconstruction** covers:
  - vault balances of about 60 tokens (ERC-4626 legs converted);
  - Morpho `position()`;
  - Aave/Spark aToken and debt tokens;
  - ITB contract balances;
  - the Optimism and Scroll vault holdings;
  - in-flight bridges (Berachain eBTC, Corn BTCN+LBTC, tacBTC in queue, liquidRWA);
  - Pendle PTs valued at face, a slight overstatement in Jan–Mar-25.
- **Yield decomposition** uses average balances and is approximate (est.). Merkl claims are attributed by claim date, not accrual date.
- **DefiLlama lend/borrow history is paywalled**, so on-chain indices were used instead.
- **Optimism holder history** was read with `balanceOf` over all 1,363 addresses seen in Optimism Transfer logs.
