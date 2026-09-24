# Midas mHyperBTC (Hyperithm): deep dive

*Scripts: [`tools/top5/mhyperbtc/`](../../../tools/top5/mhyperbtc/), data: [`data/top5/mhyperbtc/`](../../../data/top5/mhyperbtc/). Mentions of `scripts/` and `raw/` below refer to the working folder; the `raw/` dumps are not published.*

**Dates.** Snapshot 2026-09-20 12:00 UTC (Ethereum block 26,018,582, 11:59:59 UTC); written 2026-09-22.

**Prices.** BTC was $80,276 at the snapshot (Chainlink BTC/USD at that block) and $86,488 on 09-22. Midas' own USD figures ($30.67M NAV) use the 09-21 price of about $86.6k.

**Conventions.**
- Every number comes from a file in `raw/` or a URL.
- "Estimate" marks my own derivations.
- mHyperBTC is priced in BTC. "BTC-eq" means mHyperBTC × NAV (1.02606813).

---

## Summary

- **What it is.** A Midas-issued, NAV-priced BTC certificate. Hyperithm trades it from one Midas-controlled MPC wallet, `0x933adedd85824da75ec8a334a7907e69e7c02833` ("mHyperBTC_SMA1_EVM").
- **Current portfolio** (NAV 354.1 BTC). The carry leg is about 68% of NAV. Gross assets are about 1.38× NAV.
  - **Collateral.** 239.4 cbBTC is posted on Ethereum: 126.0 on Morpho cbBTC/USDT and 113.4 on Spark. A further 1.36 WBTC sits idle on Aave.
  - **Debt.** $10.76M: USDT on Morpho and USDS on Spark. LTV is 55.7% at the snapshot and 52% on 09-22. Both legs liquidate at about **$53.3–53.6k BTC**, 33% below the snapshot price.
  - **Where the borrowed dollars sit.** All $10.79M is in three Morpho USD vaults:
    - Hyperithm USDC Apex on Monad, $3.99M;
    - StableEarn on Stable, $5.81M;
    - Pendle Ecosystem USDC on Ethereum, $0.99M.
  - **BTC lent out.** Another 104.5 cbBTC (29.5% of NAV) is lent on Monad through two Hyperithm-curated vaults. Their only borrowers are leveraged holders of Hyperithm's own products (mHyperBTC and aHyperBTC).
- **The dollar leg has earned almost nothing.** Dec-2025 to Sep-2026, on-chain borrow interest was $122k and income from the Morpho dollar vaults was $137k.
  - Of the 9.98 BTC NAV gain paid to holders ($745k), **about 43% ($319k) matches reward tokens the wallet received**, mostly WMON on Monad. In Mar–May that share was 61–67%. (Estimate.)
  - The rest came from sleeves that are only partly visible on-chain: CEX basis/funding trades, BTC lending and LP.
- **Realised yield** is 2.61% since the NAV started moving, about **3.2% a year** from the first mint.
  - It has fallen from about 4.5–4.9% annualised (Dec–Feb) to 0.7–2.3% (Jun–Sep). The last 90 days run at 1.65% a year.
  - No month has been negative. Two weekly prints were slightly negative: −0.025% on 2026-06-02 and −0.059% on 2026-07-13.
- **Where the risk sits:**
  - Holders have a qualified-subordinated claim on Midas Software GmbH. There is no custodian or security agent.
  - Strategy capital is lent into Hyperithm's own product stack, so capital circulates in a loop among Hyperithm products.
  - Holders are very concentrated: 4 beneficial holders own 82%.
  - About 37% of the dollar leg sits in a Monad vault that currently shows $0 of withdrawable liquidity.

---

## A. Passport

| Item | Value | Source |
|---|---|---|
| Token | mHyperBTC, "Midas Hyperithm BTC", 18 decimals | registry `raw/registry_mhyperbtc.txt` |
| Ethereum | token `0xC8495EAFf71D3A563b906295fCF2f685b1783085`, oracle `0x3359…517C`, issuance vault `0xeD22…E65e`, redemption vault `0x16d4…db67`, OFT adapter `0xb67f…445C` | https://docs.midas.app/resources/smart-contracts-registry |
| Monad | token `0xF7Cf282eC810fDed974F99c0163E792f432892BC` (arrives only via the OFT bridge; no issuance vault), oracle `0x165d…FD8c` | same |
| Rootstock | token `0x7F71f02aE0945364F658860d67dbc10c86Ca3a3C`, issuance and redemption vaults | same |
| Stable | **no token.** Stable only hosts a strategy position (StableEarn). The brief's "Ethereum/Monad/Stable" mixes up where the token lives with where the assets are deployed. | Midas marketplace API: networks mainnet, rootstock, monad |
| Launch | Oracle round 1 = 1.0 on **2025-10-15**. First real mint: 25.0 on **2025-11-24**. Final Terms Initial Issue Date **2025-11-25** (ISIN DE000A4AQV70). First NAV increase 2025-11-26. | `raw/oracle_rounds.csv`, Final Terms |
| Status | Live. Deposits and redemptions open; not paused (`paused()=0`). | RPC |
| NAV | 1.02606813 (round 56, 2026-09-21 15:02 UTC) | oracle |
| TVL | 354.1 BTC / 345.12 tokens: Ethereum 284.07, Monad 57.07, Rootstock 3.98. Peak **583.5 BTC** on 2026-03-29; peak USD **$45.1M** on 2026-04-22. | Midas API tvl-snapshots |
| Holders | 117 addresses (Ethereum 90, Monad 7, Rootstock 20). Look-through (Morpho collateral credited to its borrower): 4 holders own 82%. | `holders_buckets.csv` |
| Issuer | **Midas Software GmbH**, Berlin (HRB 254645). Sole shareholder Midas Protocol Ltd (UK). | Final Terms |
| Prospectus | Base prospectus approved by the Liechtenstein FMA (17-Jul-2024, prolonged 17-Jul-2025; new one 17-Jul-2026) and passported to 14 EU states. | FT / MFSA mirror |
| Legal form | The 2025 Final Terms and the KID: a German-law bearer debt instrument. The 17-Jul-2026 Final Terms: a Swiss-law actively managed certificate (AMC). | `raw/docs/notes.md` §1 |
| Holder claim | **Qualified subordinated.** No payment while the issuer is illiquid or over-indebted. The portfolio is "notional only". Custodian, collateral and security agent are all "n/a". | FT |
| Issuer balance sheet | FY2025 deficit not covered by equity: €5.78M. Subordinated token liabilities: €389.6M. Going concern described as "predominantly probable". | FT summary |
| Manager | Named manager in the FT: "Hyperithm LLC" (Korea, Seoul). Parent: **Hyperithm Co., Ltd.**, Tokyo, founded 2018-01-29, capital ¥90M, 41 staff. | hyperithm.com/about |
| Manager licences | Japan: an FSA Article-63 notification for a qualified-institutional-investor fund, which is **not** a licence. Korea: VASP registration from 2021-12-23; renewal still pending after 621 days (Edaily, 2026-08-06). | FSA list; PR Newswire; Edaily |
| Manager people | Co-CEOs Lloyd (Wonjun) Lee and Sangrok Oh; CIO Jonggu Lee; CFO Jinho Choi; COO Sukyung Na; CSO Yoshikazu Abe; DeFi lead Sangwoo Kim | hyperithm.com/team |
| Eligibility | KYC / greenlist to mint and redeem with Midas; US persons excluded (Reg S). The MiFID target market includes retail; Switzerland is professional-only. **On-chain `greenlistEnabled = false`**, so the token moves freely (Pendle, Morpho). | FT; RPC |

---

## B. Mechanics, step by step

**1. Deposit.** You send WBTC or cbBTC to the issuance vault `0xeD22…`.

| Parameter | Value |
|---|---|
| WBTC fee | 0.22% |
| cbBTC fee | 0% |
| Remaining allowance | 347 WBTC and 70.9 cbBTC |
| Instant mint limit | 300 per day |
| Price tolerance | 0.2% |

- Deposits go to the tokensReceiver `0xa8b7…d29c` ("Proceeds_Recipient", an MPC EOA). It has forwarded 421.7 cbBTC and 150.8 WBTC to the strategy wallet.
- Fees go to the strategy wallet itself: the vault's `feeReceiver` is SMA1. (Source: `raw/depositvault_views.json`.)

**2. Where the BTC goes.** Everything moves through SMA1, a Fordefi/Fireblocks MPC wallet.
- Midas co-signs every transaction and controls the destination whitelist. "Assets always remain the property of Midas."
- Around it, the wallet uses:
  - swap routes: WBTC↔cbBTC through KyberSwap and an aggregator settlement contract, `0x8f10…f996`;
  - bridges: LayerZero WBTC OFT to Monad, Katana vault-bridge (vbWBTC/vbUSDC), CCTP for USDC, USDT0 OFT to Stable;
  - exchanges (see section C).

**3. The borrow leg.** It has moved between venues seven times in ten months:

| Period | BTC collateral → dollar loan | Notes |
|---|---|---|
| Dec 2025 – Apr 2026 | **Katana** Morpho vbWBTC/vbUSDC + vbUSDT, up to 330 BTC / $13.2M | Native borrow APR 0.1–1% plus KAT/MORPHO rewards |
| Dec 2025 – Feb 2026 | **Monad** Morpho WBTC/AUSD | $1–2.7M → Steakhouse AUSD vault |
| Jan – May 2026 | **Ethereum** Morpho WBTC/USDC, cbBTC/USDC, WBTC/EURC, LBTC/EURCV, WBTC/WETH, WBTC/USDT ($11M for one day, 04-22) | Many short trades |
| Jan – Apr 2026 | stUSDS → USDS/USDT/USDC loops, $4–5M | Dollar-on-dollar, not BTC carry |
| Mar – May 2026 | **BTC-on-BTC loops** on Monad: WBTC/cbBTC (LLTV 94.5%) and triBTC/cbBTC, up to 162 cbBTC borrowed | Estimate: incentive farming. The same period had 250–300 BTC in Hyperithm cbBTC Apex. |
| Jun 2026 | **Binance book** (1Token report inside the Midas proof of reserve): assets $52.7–56.7M vs liabilities $29.7–36.3M; plus Gate.io $5.0M / $2.4M | Composition not disclosed; the FT's "50% basis trading" sleeve |
| Jul – Aug 2026 | Aave v3 cbBTC → USDC ($0.4–1.1M at 11–14%). From 08-19: Aave, Morpho cbBTC/RLUSD, Monad cbBTC/USDC, Tempo cbBTC/pathUSD | |
| **Sep 2026 → now** | **Morpho cbBTC/USDT** (LLTV 86%) **+ Spark cbBTC → USDS** (LT 82%) | $10.76M |

**4. Where the borrowed dollars go.** The trail was followed on-chain; the current picture:

| Vault | Chain | Amount | Net APY | What it lends to |
|---|---|---|---|---|
| Hyperithm USDC Apex (Morpho V2) | Monad | $3.99M | 7.10% | PT-USDat-14JAN2027/USDC $18.8M; **aHYPER/USDC $18.5M** (Hyperithm Delta Neutral Vault loopers); aHyperBTC/USDC $1.7M |
| StableEarn (gtusdtb) | Stable | $5.81M | 7.36% | sthUSD/USDT0 loopers |
| Pendle Ecosystem USDC | Ethereum | $0.99M | 7.12% | PT-reUSD, PT-sUSDS, PT-sUSDE, PT-USDG loops |

- Earlier destinations included:
  - Hyperithm USDC Core/Apex (Ethereum), Steakhouse AUSD, sky.money Risk Capital/Savings, EURCV Prime, Gauntlet EURC, PayPal USD Main;
  - Maple syrupUSDC/USDT, Fluid, Ethena USDe mint/redeem, Pendle PTs;
  - exchanges: USDC/USDT/USD1 to deposit address `0x2991…c190`, swept to `0x28C6…1d60` (the public Etherscan label reads Binance 14); USD1/USDT to `0x2f18…b9f3`, swept to `0x0D07…92Fe` (Etherscan label Gate.io). Both happened in June 2026 and match the PoR lines `binance_exch` / `gt_exch`. RLUSD $5.0M went to an unidentified venue from 08-20 to 09-08.
- Sources: `raw/sma1_eth_flow_summary.txt`, `raw/counterparty_profiles.txt`, `raw/morpho_txs.csv`.

**5. How profits come back to BTC.** Interest and rewards arrive in dollars or reward tokens.
- Reward tokens (WMON, KAT, MORPHO, PENDLE, CRV, EUL, FLUID) are sold through aggregators soon after they are claimed.
- NAV is struck in BTC, so any dollar surplus counts at spot. (Estimate: I found no dedicated USD→BTC conversion step. The dollar book is kept roughly equal to the debt: $10.79M of dollar assets vs $10.76M of debt.)

**6. NAV calculation and cadence.**
- Hyperithm values the book in 1Token. Midas checks it and deducts fees. At least 2 co-signers approve.
- Updater `0x4046…0956` calls `setRoundDataSafe`. The feed contract caps each change at **0.2%** and requires at least 1 hour between updates. The admin path `setRoundData` only checks hard bounds of 0.1–1000.
- A second layer, the DataFeed, rejects a price older than **30 days** or outside 0.90–1.13.
- Cadence was about twice a week until mid-May 2026 and **weekly since then**. That is less often than the "twice per calendar week" in the 2026 FT.
- Since June 2026, a weekly proof-of-reserve attestation (Chainlink CRE, LlamaRisk/Canary verifiers) publishes the ops NAV, the cross-chain supply and a 1Token balance sheet. It "does not currently condition the on-chain price update".

**7. Redemption.**

*Standard route:*
- You send tokens to the redemption vault `0x16d4…`.
- SMA1 funds the request-redeemer EOA `0x9d35…7eb7` with cbBTC; that EOA pays you and the tokens are burned.
- 72 requests so far; 235.1 cbBTC paid out.
- The largest was **147.3 mHyperBTC (≈150 BTC) on 2026-04-28**: requested 01:17, funded 05:17 (181.7 cbBTC), paid 12:13 UTC.

*Final Terms (Jul-2026):* 1 business-day settlement; **gate of 15% of supply per settlement day**; standard fee 0%.

*Instant route:*
- Fee 0.3%.
- Up to 50% can be held back and settled later at the next price ("deferred price").
- On-chain `instantDailyLimit` = 15 mHyperBTC. The product page shows capacity of ₿1.74.
- Midas Staked Liquidity (MSL), Midas' pool that funds instant redemptions, is capped at 10% of TVL and ranks senior to holders.

---

## C. Counterparty chain and who owns the liquidity at each step

| Step | Who holds the asset | Counterparty exposure |
|---|---|---|
| Holder's claim | Holder → **Midas Software GmbH** | Qualified-subordinated unsecured claim; no ring-fencing; no custodian or trustee |
| Deposit / proceeds | Midas-owned MPC wallets: `0xa8b7…` → SMA1 | Fordefi and Fireblocks MPC, Blockaid co-signer; Hyperithm initiates, Midas approves |
| BTC wrappers | cbBTC (Coinbase), WBTC (BitGo); historically LBTC, vbWBTC (Katana), BTC.b, triBTC/3BTC LPs | Wrapper custodians |
| Collateral venues | Morpho Blue (oracle `0x9f98…34d2`); SparkLend (Sky) | Smart contracts, oracles, liquidation |
| Dollar venues | Morpho V2 vaults curated by **Hyperithm** (Monad), by Gauntlet/Stable (StableEarn) and by Pendle (Ethereum) | Borrowers in those vaults (see D) and the collateral they post (aHYPER, PT-USDat, sthUSD, PT-reUSD) |
| Bridges | LayerZero (WBTC OFT, USDT0, mHyperBTC OFT with 4/4 DVNs), Circle CCTP, Katana vault-bridge | Bridge risk. OFT bridging was paused 04-18 to 04-28. |
| Exchanges | cex_1 $0.41M today. Jun-2026 Binance book up to $56.7M gross. Gate.io $5.0M. Coinbase withdrawals (`0xa9d1…` hot wallet → SMA1: 2,134 cbBTC cumulative). | Exchange credit and custody. The FT allows Binance, OKX, Bybit, Coinbase and Kraken. |
| Oracle and NAV | Midas ops (1Token) plus 2 co-signers → feed | Manager-reported marks; 0.2%/update cap |

---

## D. Who manages it and what controls exist

**Hyperithm** runs the trades (see section A for people and licences).
- DefiLlama puts its curator TVL at $273.7M, of which $198.6M is on Monad.
- It also runs mHYPER, mHyperETH, mXRP and the **Accountable "Hyperithm Delta Neutral" vaults (aHYPER, aHyperBTC)**.

**Midas controls:**
- **Controller.** The Midas Controller (`0x0312…ac4b`) acts on a 1-of-3 quorum: one Safe with at least 4 signers, one Fordefi MPC with at least 4, one Fireblocks MPC with at least 4.
- **Timelock.** Verified on-chain: every proxy's ProxyAdmin `0xbf25…0aAC` is owned by the **TimelockController `0xe3ee…1852`, whose `getMinDelay` = 172,800 s (48 h)**.
- **Upgrades.** Only one post-launch upgrade so far: the NAV oracle implementation on 2026-06-12.
- **Pauses.** The pauser is `0x2acb…9a12`. Pause events so far: 2026-02-03 (28 min, redemption functions) and 2026-04-18 to 04-20 (below).
- **Audits.** Côme du Crest (2025–07/2026), Sherlock, Halborn, Hacken. Bug bounty up to $500k.

**Related-party and circular links.**
- Hyperithm invested in Midas' **$50M Series A (2026-03-30)** and lists Midas as a portfolio company.
- On-chain loops:
  - SMA1 holds 35.05 cbBTC in Hyperithm cbBTC Apex on Monad (42% of that vault). The vault lends only to:
    - **mHyperBTC/cbBTC**: $4.09M, borrowed entirely by one wallet, `0xCc63…9a74`, at LTV about 74% vs a 77% LLTV;
    - **aHyperBTC/cbBTC**: $3.11M.
  - SMA1 owns about 100% of the Euler "Hyperithm Earn cbBTC" vault (69.4 cbBTC). Its active market, ecbBTC-4, accepts **only eaHyperBTC** (Hyperithm's Accountable vault) as collateral and is 94% utilised.
  - SMA1's $3.99M in Hyperithm USDC Apex is about 47% lent against aHYPER.
  - On Ethereum, Hyperithm USDC Apex (V1 and V2) is the main lender to the mHyperBTC/USDC market (70.2 mHyperBTC collateral, 9.8% APY).
  - **Net effect (estimate):** about 30–36% of mHyperBTC's NAV funds leverage on Hyperithm products, including leverage on mHyperBTC itself. That is all 104.5 BTC lent on Monad (29.5%) plus the aHYPER/aHyperBTC share of the USDC Apex deposit (about 6%). Hyperithm also earns curator fees (5–10%) on the Apex vaults that SMA1 deposits into.

---

## E. Yield

Detail is in `yield_monthly.csv`. NAV is net of fees.

| Month | Realised APY | On-chain dollar-debt APR | Interest $ | Dollar-vault income $ | Incentives $ | Share of NAV gain |
|---|---|---|---|---|---|---|
| 2025-12 | 4.86% | 1.64% | 3.2k | 1.0k | 8.0k | 19% |
| 2026-01 | 4.47% | 1.11% | 9.2k | 14.6k | 37.3k | 35% |
| 2026-02 | 4.61% | 2.24% | 19.0k | 23.0k | 30.0k | 23% |
| 2026-03 | 3.42% | 1.09% | 11.0k (+10.8k dollar-on-dollar loops) | 24.7k | 68.9k | 61% |
| 2026-04 | 4.74% | 2.23% | 15.5k (+7.2k) | 18.2k | 107.4k | 67% |
| 2026-05 | 2.60% | 4.66% | 6.2k | 4.3k | 43.4k | 66% |
| 2026-06 | 2.31% | 8.80% | 5.5k | 3.5k | 6.0k | 14% |
| 2026-07 | **0.67%** | 11.49% | 3.7k | 2.2k | 2.8k | 21% |
| 2026-08 | 2.29% | 4.91% | 22.6k | 17.2k | 7.7k | 16% |
| 2026-09 (to 21st) | 1.54% | 3.76% | 26.1k | 27.9k | 6.9k | 27% |

- **Since launch:** +2.607%, about 3.2% a year from the first mint (2.8% from oracle initialisation). Last 90 days: 1.65% a year. Midas quotes 1.90% over 30 days.
- **Stability (Dec–Aug):** mean +0.272% a month, standard deviation 0.116%. Worst month July 2026 (+0.057%), best December 2025 (+0.404%). No negative month.
- **Markdowns:** −0.025% (06-02) and −0.059% (07-13). No cause was published. Both fell during and just after the June Binance deleverage while BTC fell 19%.
- **Decomposition (estimate).**
  - Total NAV gain to holders: 9.98 BTC ≈ $745k.
  - Reward tokens received ≈ $319k (43%):
    - WMON on Monad: 9.48M tokens via Merkl, about $247k at claim-date prices;
    - Katana KAT/MORPHO/vbUSDC: about $30k, an estimate because claim timing is unknown;
    - MORPHO, PENDLE, CRV and stablecoin Merkl rewards on Ethereum.
  - The on-chain **"BTC collateral → dollars → vault" carry netted about +$15k** in ten months, roughly 0.2 BTC or 2% of the gain.
  - The remaining ~55% came from sleeves that are only partly observable: CEX basis/funding (the FT's initial mix was 50% basis, 30% DeFi, 20% LP), BTC lending (about 1–2.5% a year on the cbBTC vaults), LP positions and fee timing.
  - Caveat: dollar-vault income counts only Morpho vaults. PT, Fluid, Maple and Ethena legs are not valued.
- **Negative-carry periods (on-chain dollar leg, interest above vault income):** Dec 2025, May–Aug 2026. Worst: August, −$5.4k. In July the small Aave USDC loan cost about 11–14%. Jan–Apr was positive only thanks to near-zero Katana and Monad borrow rates plus incentives.
- **At today's rates (estimate):**
  - Borrowing $5.80M at about 3–9% (Morpho USDT: 2.97% daily average, 9.40% instantaneous on 09-21) and $4.96M at 3.93% (Spark USDS).
  - Deploying at about 7.1–7.4%.
  - Result: +0% to +3.8% on $10.8M, i.e. 0–1.4% of NAV a year. The 104.5 BTC lent on Monad adds about 0.8% of NAV.
  - That fits the 1.5–1.9% net APY now shown.

---

## F. Risk management

**LTV over time.** On-chain USD debt divided by the BTC posted against it; detail in `positions.csv` and `raw/balance_sheet_daily.csv`.

| Period | Monthly average | Peak | Notes |
|---|---|---|---|
| Dec–Mar | 57–63% | 65–67% | A 75% print on 02-05 mixes 00:00 positions with that day's lower BTC price |
| Apr–May | not comparable | ~88% (estimate) | BTC-on-BTC loops (cbBTC debt against WBTC/triBTC) |
| Jun | 55–59% on small on-chain debt | 56–64% (Binance book) | Binance book: liabilities/assets |
| Aug–Sep | 55–57% | ~60% | |

- **Now:** 55.7% at the snapshot and 52.0% on 09-22.
  - Morpho: 57.4% vs 86% LLTV; liquidation at $53,551.
  - Spark: 54.4%, health factor 1.51, liquidation threshold 82%; liquidation at $53,290.
- **No liquidation ever:** zero Morpho liquidation transactions and zero Aave Core, Spark or Horizon `LiquidationCall` events for SMA1.

**Liquidity ladder for the $10.76M debt** (`liquidity_ladder.csv`):
- **Same block:** Pendle USDC vault $0.99M (the vault holds $10.2M liquid) and wallet $0.31M, about 12% of the debt. A flash-loan unwind of the cbBTC collateral also works in one block, but it sells BTC.
- **Minutes:** StableEarn $5.81M (idle $5–11M) plus a USDT0 bridge. Cumulative about 66%.
- **Hours to days:** Hyperithm USDC Apex on Monad, $3.99M (37% of the debt). Morpho's API shows $0 withdrawable. Its markets are 89–91% utilised, so exit depends on aHYPER and PT-USDat borrowers repaying, plus a CCTP transfer.
- **CEX:** cex_1 $0.41M.
- **BTC lent on Monad:** only about 14.4 of the 104.5 cbBTC is liquid now.
- The FT's own rule (100% exitable in 2 days, 66% in 4, 33% in 6) looks met for the dollar leg only if the Monad vault can be drained. (Estimate.)

**Stress behaviour:**
- **Oct 10–11, 2025:** not live yet. The first mint came on 11-24.
- **Jan 15 → Feb 5, 2026 (BTC −35%):**
  - On-chain debt was about $20M on about 397 BTC. LTV reached about 65% on 02-02 (daily data; intraday higher).
  - Hyperithm repaid on Ethereum, Monad and Katana on 02-02 to 02-05, cutting debt to $11.3M by 02-06.
  - NAV kept rising (+0.35% in February).
- **June 2026 (BTC −19%, lowest close $58.6k on 06-30, intraday $57.8k on 07-01):**
  - About 95% of equity was on Binance with $29.7–36.3M of liabilities.
  - It was fully deleveraged by 07-06.
  - NAV printed −0.025% and then −0.059%. July was the weakest month.
- **Platform-wide Midas pause, Apr 18–21, 2026 (KelpDAO rsETH):**
  - On-chain for mHyperBTC: vaults paused 04-18 19:53 UTC; global unpause 04-19 13:18; the last function-level pauses lifted 04-20 19:09 (about 47 h in total).
  - OFT bridging was paused until 04-28, when the LayerZero verifier set moved from 3/3 to 4/4.
  - Hyperithm said it had no rsETH exposure and had "fully unwound leveraged positions on Aave".
  - A week later (04-28) the largest holder redeemed 147.3 tokens (−31.7% of supply) and was paid the same day.
- **Oracle deviation limits:** 0.2% per safe update; hard bounds 0.1–1000; DataFeed bounds 0.90–1.13 with a 30-day staleness limit.
  - A drawdown larger than 0.2% needs several updates at least 1 hour apart, or the higher-quorum admin path.
  - Loopers who borrow against mHyperBTC on Morpho face an oracle priced off NAV, so they are liquidated only by markdowns or interest accrual. `0xCc63` on Monad pays 5.7–6% against a NAV growing about 1.6%, so its position drifts toward the 77% LLTV. (Estimate: about 9–10 months at current rates.)

---

## G. Depositors

Detail is in `holders_buckets.csv` (NAV 1.02606813).

**By chain:**

| Chain | Holders | BTC-eq |
|---|---|---|
| Ethereum | 90 | 291.5 |
| Monad | 7 | 58.6 (100% held by Morpho Blue as collateral for one wallet) |
| Rootstock | 20 | 4.1 (largest: an EOA with 2.67 and a Uniswap V3 pool with 1.16) |

**By size (all chains):**

| Bucket (BTC-eq) | Holders | BTC-eq |
|---|---|---|
| < 0.01 | 85 | 0.06 |
| 0.01–0.1 | 13 | 0.38 |
| 0.1–1 | 6 | 2.53 |
| 1–10 | 7 | 13.0 |
| 10–100 | 6 | 338.1 (95.5%) |
| > 100 | 0 | 0 |

**Concentration:**
- Address level: top-1 21.4%, top-10 98.2%, top-100 100%.
- **Look-through**, with Morpho collateral credited to borrowers:
  - `0xCc63…9a74`: 111.4 BTC-eq (31.5%). It holds 40.7 in its wallet, 10.9 as Ethereum Morpho collateral and 57.1 as Monad Morpho collateral. It also redeems mHyperETH and provides Pendle LP.
  - `0xD338…08c6`: 75.8 (21.4%). It minted 270.4, redeemed 147.3 and holds $2.9M in Hyperithm USDC Apex.
  - `0xd6F4…e427`: 52.9.
  - `0x763f…603F`: 50.6 (all of it Morpho collateral).
  - Top 4 = **82%**.
  - None of these could be linked to Hyperithm or Midas.

**Holder types:**
- Contracts: Morpho Blue (Ethereum 70.21, Monad 57.07), Pendle SY 36.13 (PT/YT/LP), Rootstock Uniswap V3 and a lending aToken.
- EOAs hold the rest; a few are EIP-7702 delegated.
- **47.7% of supply is inside DeFi contracts. 36.9% is re-used as Morpho collateral.** The share of supply in Morpho was 46% in December 2025, 17–19% in Jan–Mar, and has been about 37% since April (`raw/holder_history.json`).

---

## H. TVL growth

Detail is in `tvl_monthly.csv`, which includes net flows vs NAV effect.

| Month-end | Supply | TVL BTC | TVL $M | Net flow BTC | NAV effect BTC | Monad share of supply |
|---|---|---|---|---|---|---|
| 2025-11 | 25.0 | 25.0 | 2.3 | +25.0 | 0.0 | – |
| 2025-12 | 202.4 | 203.3 | 17.8 | +178.2 | +0.1 | – |
| 2026-01 | 510.9 | 515.1 | 40.2 | +311.0 | +0.8 | – |
| 2026-02 | 541.0 | 547.3 | 36.9 | +30.4 | +1.8 | – |
| 2026-03 | 567.2 | 575.5 | 39.1 | +26.5 | +1.6 | 10.1% |
| 2026-04 | 384.7 | 391.7 | 29.7 | **−185.8** | +2.1 | 16.1% |
| 2026-05 | 364.5 | 372.0 | 27.4 | −20.6 | +0.9 | 15.7% |
| 2026-06 | 359.2 | 367.3 | 22.1 | −5.4 | +0.7 | 15.9% |
| 2026-07 | 352.9 | 361.1 | 23.4 | −6.4 | +0.2 | 16.2% |
| 2026-08 | 347.2 | 355.9 | 28.0 | −5.9 | +0.7 | 16.4% |
| 2026-09 (21st) | 345.1 | 354.1 | 30.7 | −2.1 | +0.3 | 16.5% |

- Growth came entirely from flows, and three wallets drove them (`0xD338`, `0xCc63`, `0xd6F4`). The NAV effect added about 9 BTC.
- Rootstock has stayed below 26 tokens (1.2% of supply today).
- **Monad has two different "shares":**
  - of token supply: 16.5%, all of it one looper's collateral;
  - of strategy assets: 42.5% of NAV (Euler 69.4 cbBTC, cbBTC Apex, USDC Apex).

---

## I. Growth drivers

The dated timeline is in `events.csv`.

1. **Nov 2025 – Jan 2026: three whales mint about 440 BTC.** 0xD338 minted 270 (150.5 on 2026-01-22 alone), 0xCc63 118.8 and 0xd6F4 51.6.
   - 0xCc63 looped from the start: mHyperBTC/cbBTC on Morpho Ethereum at 1.3–2.7% borrow cost, up to 94 mHyperBTC of collateral.
   - Pendle PT-30APR2026 (2026-01-08, peak about $4.4M) and a USDC YT incentive (01-15 to 02-19) added about 50–80 tokens through the SY.
   - The Morpho Ethereum mHyperBTC/USDC market opened 2026-01-15, funded by Hyperithm USDC Apex.
2. **Mar 2026: Monad.**
   - The token went live on Monad (03-19). The only use there is 0xCc63 looping 57.07 against cbBTC from Hyperithm cbBTC Apex.
   - Strategy capital on Monad earned **WMON incentives: 9.48M WMON, about $247k**, the single biggest yield driver. Merkl attributes them to the 3BTC and triBTC LPs, Morpho vault positions (Hyperithm Apex vaults) and a k3AUSD vault token (`0x5980…51b5`).
   - TVL peaked at 583.5 BTC on 03-29. Rootstock received a small LayerBank campaign (0.2134 WRBTC).
3. **Apr 2026: the reversal.** After the Apr 18–21 pause, 0xD338 redeemed 147.3 on 04-28 (−31.7%). Supply has drifted down since. No new large depositor has arrived.
4. **Not found:** no Hyperbeat integration, no Monad incentive programme naming mHyperBTC, and no Merkl campaign on Ethereum or Monad for holding mHyperBTC. Midas' monthly recaps mention it only once ($25.61M on 2026-08-20).
   - Integrations listed on the product page: Pendle, Morpho, Stargate.
   - A second Pendle market, PT-24SEP2026 (04-17, $2.79M), expires 2026-09-24.

---

## J. Economics

**Fees — the documents disagree:**

| Source | Terms |
|---|---|
| Product page | 0% management / **10% performance** |
| Nov-2025 FT and KID | 20% performance + 10% "interest fee" + 0.5% redemption fee |
| Jul-2026 FT | No management or performance line; 0.3% instant-redemption fee only |

Other fees: 0.22% on WBTC mints (paid to the strategy wallet). Fees are taken inside the NAV. A high-water mark is described only generically.

**Revenue (estimate):**
- Net gain to holders: 9.98 BTC.
- At 10% performance fee: gross ≈ 11.1 BTC, fee ≈ 1.1 BTC (≈ $80–90k) in ten months.
- At 20% + 10%: fee up to about 4.3 BTC (≈ $330k).
- How the fee is split between Midas and Hyperithm: not disclosed.
- Hyperithm also earns curator fees on Apex vault deposits made by the strategy wallet: about $25–30k a year at current balances (estimate).

**Incentive spend:**
- By Midas/Hyperithm on holders: small (Pendle YT USDC incentives; LayerBank 0.2134 WRBTC).
- **Received by the strategy:** about $319k from Monad (WMON), Katana (KAT/MORPHO), Morpho, Pendle, Curve and Merkl. This is third-party subsidy, and it was the largest single source of returns.

---

## K. Verdict

**Copy:**
- **Issuer-controlled MPC custody with manager-initiated / issuer-approved transactions and a destination whitelist.** The single strategy wallet is labelled, publicly readable and reconciles to NAV: the transparency API matched on-chain positions to within about 1%.
- **Weekly proof-of-reserve attestations that include the 1Token balance sheet per venue**, liabilities included. This is the only disclosure that revealed the June 2026 Binance leverage.
- **On-chain safety rails:** a 0.2% per-update NAV cap with 1-hour spacing, a 30-day staleness limit, a verified 48-hour upgrade timelock, and per-function pause switches.
- **Fast, documented redemptions:** 150 BTC paid in about 11 hours, with a 15%/day gate written into the terms.
- **Moderate carry-leg LTV** (52–58%, liquidation about −33%), an active deleverage record (Feb and Jun 2026) and zero liquidations.

**Avoid:**
- **Circularity and related parties.** Strategy BTC and USD are lent into vaults curated by the manager, whose borrowers loop the manager's own products (mHyperBTC, aHyperBTC, aHYPER). The manager is also an equity investor in the issuer.
- **Carry that depends on incentives.** The BTC-collateral dollar leg netted about 0% over ten months. About 43% of holders' gains matched third-party rewards, 61–67% at the peak. Yield fell from ~4.7% to ~1.5–2% once WMON and KAT rewards faded.
- **Opaque venue-hopping.** Seven borrow venues and about 30 dollar venues in ten months, plus CEX books up to about 2.6× NAV gross (Binance $56.7M assets vs ~$22M NAV on 2026-06-29). The only limits holders can check are in the Final Terms: 8× gross leverage and delta-neutral. Stated NAV cadence (twice weekly) is not met (weekly).
- **Legal wrapper.** A qualified-subordinated claim on a thinly capitalised issuer (FY2025 negative equity €5.8M), no custodian or security agent, a "notional" portfolio, and fee terms that conflict between the documents.
- **Concentration and exit liquidity.**
  - Four holders own 82%, and 36% of supply is Morpho collateral held mainly by two loopers. The Monad looper sits near its LLTV.
  - 37% of the dollar leg sits in a Monad vault with no withdrawable liquidity. Bridges (OFT, CCTP, USDT0) sit in the repayment path.

---

### Files

**Main outputs:**
- `deepdive.md` (this file)
- `tvl_monthly.csv`
- `yield_monthly.csv`
- `positions.csv`
- `holders_buckets.csv`
- `liquidity_ladder.csv`
- `events.csv`

**Supporting data** (`raw/`):
- Balance sheet: `balance_sheet_daily.csv`
- Proof-of-reserve: `por/` and `por_table.json`
- NAV oracle: `oracle_rounds.csv`
- Morpho: `morpho_*.json`
- Aave and Spark: `aave_spark_daily.json`, `aave_rates_daily.json`
- Transfers and flows: `sma1_*_transfers/logs`, `*_flow_summary.txt`, `counterparty_profiles.txt`
- Holders: `holders_*.json`
- Incentives: `incentives_monthly.json`
- Documents and notes: `raw/docs/` (not in the repository)

**Scripts** (`scripts/`, Python 3; RPC helpers use `/usr/bin/python3` for keccak): `rpc.py`, `oracle_history.py`, `fetch_por.py`, `morpho_*.py`, `aave_daily.py`, `aave_rates_daily.py`, `build_balance_sheet.py`, `borrow_cost.py`, `vault_income.py`, `incentives.py`, `yield_monthly.py`, `build_tvl_monthly.py`, `holders_buckets.py`, `holder_history.py`, `admin_events.py`, `build_outputs.py`, `build_events.py`.
