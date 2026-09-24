# Top 5 live BTC-collateral dollar-carry products (snapshot 2026-09-20 12:00 UTC)

*Scripts: [`tools/top5/selection/`](../../../tools/top5/selection/), data: [`data/top5/selection/`](../../../data/top5/selection/). Mentions of `scripts/` and `raw/` below refer to the working folder; the `raw/` dumps are not published.*

**Definition used.** A live product with outside depositors: a vault, fund or protocol. It takes BTC (or a BTC wrapper) from depositors, posts it as collateral, borrows dollars against it, and puts those dollars into a strategy that earns yield for the BTC depositors.

**Out of scope:**
- EOAs.
- Individual smart accounts: Instadapp DSA, Summer.fi DPM, DSProxy, Coinbase Smart Wallet, EIP-7702 wallets.
- Treasuries and funds trading for themselves.

**Ranking metric.** BTC deposits (the depositors' claim, in BTC). Collateral posted is shown next to it; the order is the same under either metric.

**Timing and prices.**
- All position figures are read on-chain at Ethereum block 26,018,582, the last block before 2026-09-20 12:00 UTC (11:59:59; the Kraken deep dive and the site cite 26,018,583, the first block after, 12:00:11). For other chains we used the block at the same timestamp, unless the row says otherwise.
- BTC was about $80.5k at the snapshot. USD values are converted at that price and are estimates.

## Ranked result

| # | Product | BTC deposits | BTC collateral posted | Dollar debt | Borrowed / venue | Fit |
|---|---|---|---|---|---|---|
| 1 | **Kraken Bitcoin Vault** (Veda "Advanced Strategies BTC") | **6,492.5 BTC** (~$523M) | 5,832.5 BTC: 5,395.4 kBTC + 90.0 WBTC on Morpho; 347.1 WBTC on Aave v3 | **$298.3M** | RLUSD, PYUSD (Morpho kBTC markets); USDT (Morpho WBTC/USDT, Aave v3) | Yes |
| 2 | **Yield Basis**, BTC markets (yb-WBTC, yb-cbBTC, yb-tBTC, plus deprecated v2/legacy) | **1,326 BTC-eq** (~$107M) | 949.6 BTC inside the LEVAMM-owned Curve LP, which also holds ~$121M crvUSD | **$92.9M crvUSD** | crvUSD from the Curve DAO credit line; own LEVAMM | Yes (hybrid, see below) |
| 3 | **Bitget bgBTC Onchain Earn** (Gauntlet Aera vault, Morph) | **801.6 bgBTC** (~$64.5M) | 801.6 bgBTC (0 idle) | **$40.6M** (09-21: $43.0M) | USDC on Morpho (Morph); LLTV 77%, LTV 62% | Yes (circular) |
| 4 | **Midas mHyperBTC** (Hyperithm) | **~350 BTC-eq**, estimate from NAV $30.67M on 09-21 | 239.4 cbBTC: 126.0 on Morpho + 113.4 on Spark | **$10.76M** | USDT (Morpho cbBTC/USDT), USDS (Spark) | Yes |
| 5 | **ether.fi Liquid BTC** (Veda) | **~232 BTC** (~$18.7M) | 207.9 BTC: 153.08 WBTC + 54.80 cbBTC | **$10.30M** | 5.93M PYUSD + 4.37M USDC on Spark; health factor 1.28 | Yes |
| 6 (alternate) | Upshift Sentora BTC | 47.2 BTC | 46.7 WBTC | $2.50M | RLUSD + PYUSD on Morpho | Yes |
| 7 (alternate) | Upshift Gamma BTC | 40.8 cbBTC | 41.0 cbBTC | $1.79M | USDG on an Aave v4 Spoke (held by an operator EOA) | Yes |

**Smaller products that also fit, all read on 09-21:**
- Concrete ctWBTC v2: 29.5 BTC, $1.13M USDT on Aave.
- Yearn Katana WBTC yVault: 19.7 BTC, $0.68M vbUSDC on Morpho Katana.
- IPOR "wBTC Dollar Carry": 5.6 WBTC, $0.17M.
- Reservoir BTC Yield: 0.7 WBTC.

**How the list changed from the candidate list.**
- **Maple leaves the list.** It was wound down in November 2025 (details below).
- **Midas mHyperBTC enters at #4.** Its strategy wallet is an MPC EOA, so it only surfaced through Midas' transparency API.

## Evidence per product

### 1. Kraken Bitcoin Vault

**Deposits.** Read on Ink at block 56,407,189: 6,462.56 shares × `getRateSafe` 1.0046285 = **6,492.48 BTC**.
- Vault: `0x7dee0120739b7ec048b469939efb178adbbb19b2`.
- Accountant: `0x4Bb6C416a00561ad6657110b76552c42d55Ff1d6`.
- Latest read, 09-21: 6,579.2 BTC.

**Collateral and debt legs.** These are `LoanManagerOwnable2StepWithShortcut` contracts; Blockscout shows `owner()` is the BoringVault.

| Leg | Contract | Collateral | Debt |
|---|---|---|---|
| kBTC/RLUSD | `0x0774b5B1…78CcF5` | 2,462.1 kBTC | $124.8M |
| kBTC/RLUSD | `0x7fB9f8F7…9205E` | 928.1 kBTC | $51.0M |
| kBTC/PYUSD | `0xd18DF3c0…bd986` | 1,081.3 kBTC | $60.8M |
| kBTC/PYUSD | `0x1E8f4752…9489` | 923.9 kBTC | $41.7M |
| WBTC/USDT, Morpho | `0x5EE1E2e3…f884` | 90.0 WBTC | $2.24M |
| WBTC/USDT, Aave v3 | `0xF5232592…53B7` | 347.1 WBTC | $17.70M |

**Where the dollars go.** The stables go to the Sentora RLUSD Main and Paypal USD Main Morpho V2 vaults, Hastra PRIME, and Sentora PRIME Main / Huma PST.

**Latest read, 09-21.** Morpho legs total $297.7M. The RLUSD-1 leg rose to $138.9M after the vault drew another 20.5M RLUSD. Total debt is ≈$315M.

**Scripts:** `scripts/kraken_vault.py`, `scripts/snapshot_0920.py`.

### 2. Yield Basis: confirmed as BTC collateral plus dollar debt

**Where the crvUSD comes from:**
1. The crvUSD ControllerFactory (`0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC`) returns `debt_ceiling(Factory) = 1,000,000,000 crvUSD` for the YB Factory (`0x370a449FeBb9411c95bf897021377fe0B7D100c0`). This is the Curve DAO credit line, and the crvUSD is minted to the Factory.
2. The Factory allocates crvUSD to each market's LT, where `stablecoin_allocation` is set. 330.1M is allocated; 669.9M sits idle in the Factory.

**How a deposit works:**
1. The LT takes the deposited BTC.
2. It borrows an equal value of crvUSD from its allocation (`add_liquidity([debt, assets])`).
3. It deposits both into the Curve Cryptoswap BTC/crvUSD pool.
4. The LP token is held as collateral by the LEVAMM. `AMM.get_debt()` is the crvUSD debt, and leverage is held at 2×.

**What depositors earn.** The yield is trading fees for unstaked LP, or YB emissions for staked LP; 66–96% of LP is staked.

**Why "hybrid".** The collateral is the BTC/crvUSD LP, not bare BTC, and the borrowed dollars are deployed into that same LP.

**Per-pool figures at block 26,018,582:**

| Market (LT) | Depositor value (BTC-eq, pricePerShare × supply) | BTC in LP | crvUSD in LP | crvUSD debt | Allocation | Staked |
|---|---|---|---|---|---|---|
| yb-WBTC `0x651D…BAa` | 476.5 | 295.9 | $44.6M | $31.16M | 100M | 77% |
| yb-cbBTC `0x722F…9F9` | 352.1 | 356.1 | $27.9M | $28.26M | 100M | 73% |
| yb-tBTC `0x771F…3Ec` | 257.4 | 161.9 | $24.1M | $16.94M | 35.7M | 67% |
| cbBTC v2, deprecated (`0xac0c…`) | 140.5 | 81.3 | $14.2M | $9.74M | 16.8M | 96% |
| tBTC v2, deprecated (`0xac0a…`) | 53.4 | 27.3 | $5.5M | $3.54M | 6.5M | 96% |
| WBTC v2, deprecated (`0xfbf3…`) | 43.0 | 25.2 | $4.3M | $2.99M | 5.6M | 39% |
| legacy WBTC / cbBTC / tBTC | 3.3 | 2.0 | $0.4M | $0.25M | 0.3M each | – |
| **BTC total** | **1,326.2** | **949.6** | **~$121M** | **$92.88M** | | |

The ETH market is excluded from these totals: 10,620 ETH and $27.1M debt. Latest read, 09-21: 1,328.8 BTC-eq, 841.9 BTC in LP, $93.47M debt.

**Scripts:** `scripts/yieldbasis.py`, `scripts/yb_value.py`, run with `/usr/bin/python3`.

### 3. Bitget bgBTC Onchain Earn

**Position.** The Aera vault `0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510` (Morph) holds 801.58 bgBTC and owes $40.64M USDC at the 09-20 snapshot. On 09-21 it was 801.71 bgBTC and $43.03M.
- Morpho on Morph: `0xad10…4905`.
- Market: `0x37d156e9…1a5c`.

**Where the USDC goes, and why it is circular.**
- The USDC sits in the Gauntlet USDC vault `0x9131EB40…3341`. Aera owns 82.1% of it, about $43.0M.
- That vault lends back into the same bgBTC/USDC market, so the carry is circular and depends on incentives.

**Supply.** 835.0 bgBTC exist on Morph.

**Script:** `scripts/bitget_morph.py`.

### 4. Midas mHyperBTC

**Positions.** Strategy wallet `0x933adedd85824da75ec8a334a7907e69e7c02833`, an MPC EOA. Midas labels it "mHyperBTC_SMA1_EVM".
- Morpho cbBTC/USDT: 126.00 cbBTC against $5.80M USDT.
- Spark: 113.42 cbBTC against $4.96M USDS.

**Midas transparency API** (updated 2026-09-21T22:07Z):
- Liabilities $10.76M, equity $30.67M.
- The wallet's own value is 345.7 BTC-eq.

**Where the dollars go:** Hyperithm USDC Apex on Monad (~$4.0M), Morpho on Stable (~$5.8M) and pendleUSDC (~$1.0M).

Token: `0xC8495EAFf71D3A563b906295fCF2f685b1783085`.

### 5. ether.fi Liquid BTC

**Position.** BoringVault `0x5f46d540b6eD704C3c8789105F30E075AA900726`. Spark `getUserAccountData` at the snapshot shows collateral $16.69M, debt $10.30M and health factor 1.281.
- Collateral: spWBTC 153.08 and spcbBTC 54.80.
- Debt: vdPYUSD 5.927M and vdUSDC 4.372M.

**Vault size.** About 232 BTC, taken from the earlier verified read: 133.6 shares on Ethereum plus 90.28 on Optimism.

**Where the dollars go:** Cap stcUSD (~$6.1M) and Sentora Paypal USD Main (~$4.15M).

## Maple BTC Yield: wound down, 0 BTC

- **Core staking is gone.** An address cluster we inferred to be Maple's Core stakers (unlabeled; for example `0x74bb2c9f…cd52`) began staking on 2025-02-06. It peaked at about 1,480–1,570 BTC (estimate), made its last stake on 2025-10-01, and all its timelocks ended on 2025-11-19. It has 0 BTC staked today.
- **The BTC was swept and paid out.** On 2025-11-19 the unlocked outputs were swept to `bc1pm9v0…c3c0pc4`. That wallet paid 1,133.69 BTC to 66 addresses in 85% amounts, which matches Maple's statement that it would return 85% of principal first, and moved the remaining 200.09 BTC on 2026-06-05 to an undisclosed owner (see `06-maple.md`). Its balance is now 0.
- **Nothing replaced it.** The Maple site and API list no BTC pool and there is no syrupBTC. Core's docs deprecated lstBTC on 2025-12-23. Total BTC staked on Core is only 2,210 BTC.
- **The settlement did not change this.** It was announced 2026-05-22 and says syrupBTC "will proceed", but gives no date.
- **Peak size:** 1,757.85 BTC on 2025-05-14 (`data/top5/maple/size_history.csv`); 1,500+ BTC in July 2025. The 1,480–1,570 BTC above is the inferred Core-staking cluster, not the product's size.
- **Confidence.** That the product is wound down: high. That these addresses are Maple's: medium-high.
- **Raw data:** `raw/maple/`.

## Excluded, with reasons

| Candidate | Size | Why excluded |
|---|---|---|
| Mezo Prime (Enclaves) | 750.18 BTC locked + 250 idle; 14.53M MUSD across 2 Enclaves | A credit facility for 1–2 institutional clients (Bullish is the launch client). Each client has a segregated account and decides how its MUSD is used: Enclave 1 put it into an sMUSD gauge and a mUSDC/MUSD LP, with rewards going to an EOA; Enclave 2 sent 4M MUSD to a Safe. The client runs the trade for itself. It would rank #3 if it were counted. |
| River Smart/Prime Vaults | ~2,214 BTC-wrapper units (655 bfBTC, 1,041 uniBTC, 518 brBTC); 95.9M satUSD minted, 43.5M staked | Borderline. The mechanics match, but the dollar is River's own satUSD. The satUSD+ pool pays about 0%: its price per share has been flat for 12 months, and the API shows 0.02–0.04% paid in points. It is whitelist-only with 1–3 depositors per vault, some River-affiliated. There has been no rebalance since Nov–Dec 2025. It would rank #2 by units if it were counted. |
| Avalon CeDeFi | 1,364 BTC vs $47.6M USDT | A lending pool for 4 institutional Safes. The USDT went to Binance deposit addresses, and there has been no activity since 11.2024. |
| Lombard LBTCv | ~$80M | No dollar debt. The yield comes from credit cover (BTCoc on Cap) and LP. |
| Hermetica hBTC | 46.9 sBTC idle | Unwound: Zest debt repaid 2026-06-04, deposits disabled. |
| Tesseract IPOR vaults | ~31.5 WBTC / $1.5M | Dedicated client vaults; 97–100% of shares belong to one EOA. |
| Hyperithm cbBTC Apex, all Morpho BTC vaults | – | They lend BTC; they don't borrow against it. |
| Solv BTC+ / .AVAX / .BNB; Bedrock; BitFi; Vishwa; Bitlayer YBTC; other Veda BTC vaults | – | No dollar borrowing found. SolvBTC.BNB borrows BNB. |
| Treehouse, Level, Lazy Summer, Fluid Lite, Beefy, Harvest | – | No BTC-carry product (checked via DefiLlama and docs, not account by account). |
| Gearbox, Contango, DeFi Saver, Summer.fi, Instadapp | – | Per-user tools. |
| Coinbase Loans | $1.44B on Morpho Base | Retail borrowing, not a yield product. |
| Large contract borrowers | – | Safe `0xe40d…03bf` (1,849 cbBTC + 33.4k aWETH, $121.7M stables), Safe `0x4093…9987` (900.6 WBTC + wstETH, $39.7M on Compound) and Origin-linked Safe `0x70fC…7137` are treasuries or funds with no share token. |
| Unidentified borrower `0x9dc8F41A…a175` | 174.6 FBTC vs $6.2M | An unverified proxy; the USDT went to an EOA. Unresolved, but smaller than #5 either way. |

## Borrower scan: coverage and results

We kept every position with at least $2M of debt. The full list is in `scan_borrowers_all.csv` (319 rows, 2026-09-21).

- **Morpho:** all 14 API chains. 56 markets with BTC collateral and ≥$100k borrowed; 107 positions.
  - Classified as 57 contracts, 35 EOAs and 12 EIP-7702 wallets.
  - The contracts are 46 Coinbase Smart Wallets, 5 Kraken LoanManagers, and a few Safes and smart accounts.
  - Morph was checked by RPC, which found only Bitget.
- **Aave v3 and Spark:** Aave v3 on Ethereum (Core, Prime, EtherFi), Base and Arbitrum, plus Spark.
  - We took the top 100 holders of every BTC aToken and spToken, and ranks 101–400 for aEthWBTC, aEthcbBTC, spcbBTC and aBascbBTC.
  - 174 positions (171 addresses). The only products among them are Kraken (Aave), ether.fi Liquid BTC and mHyperBTC (both Spark).
- **Compound v3, Ethereum:** complete. Accounts were enumerated from `SupplyCollateral` logs, and their BTC adds up to `totalsCollateral`. 31 positions (28 addresses), no products.
- **Compound v3, Base and Arbitrum:** partial, because Blockscout rate-limited us (429s). Nothing ≥$2M found. The uncovered part is under 70 BTC.
- **Euler v2** (Ethereum, Base, Arbitrum; 1,444 vaults): only 2 BTC vaults hold ≥20 BTC, with no ≥$2M dollar debt against them.
- **Fluid:** every position on Ethereum. 2 positions ≥$2M, both EOAs. On Base and Arbitrum each vault has under $2M borrowed in total.
- **Kamino, main market:** 2,936 obligations with BTC deposits. 3 are ≥$2M, and all are system-owned wallets.
- **Aave v4, Ethereum:** all spokes seen in `Borrow` events over the last ~12 months, 3,549 (spoke, user) pairs. 27 positions have ≥$2M debt; only 2 have BTC collateral (150 WBTC + 13 cbBTC and 10.6 cbBTC, against USDG/frxUSD), and both are EOAs.

**Scan caveat: product wallets can look like EOAs.** Some products run from MPC or operator EOAs, such as mHyperBTC's `0x933a…` and Upshift Gamma's operator. The four largest EOA borrowers were checked for links to a product and none was found: `0xbCd16D36…` with $172.9M against ~4,680 cbBTC, `0x56eC…`, `0x2835…` and `0x5130…`.

**Re-check, 24 September.** All 27 EOA or unlabelled borrowers with over $20M of debt in `scan_borrowers_all.csv` were traced through their funding and outflows (Blockscout token transfers, Etherscan funding labels). None is a pooled product. `0x7CD0…` (Aave, $191M) and `0xbCd1…` (Morpho, $173M) are one unidentified institutional book of about 9,900 cbBTC against $364M of USDC: funded from Coinbase hot wallets, the borrowed dollars swept nightly to its own hub and redeemed through Circle and Paxos. `0xABdb…` (Aave, $178M) and `0x56eC…` are one client on Paxos rails. `0xb99a…` (Spark, $134M) is Abraxas Capital's Heka funds; `0x2835…` (Spark, $112M) a Binance-funded whale cluster; `0xD485…` and `0xF506…` Galaxy Digital desks. The only borderline case is `0xB561…`: Nexo's operational wallet with 1,031 cbBTC against $40M of USDS on Spark, the on-chain leg of its CeFi earn program, which would rank near Bitget if CeFi programs were counted.

**Venues beyond the original scan, 24 September.** Tydro on Ink: the largest position (913 kBTC against $45.1M of USDC, 85% of the pool) is a Kraken-linked book, not a product: the kBTC arrives from Kraken's Ink hot wallet and the borrowed dollars are swept back to a Kraken hot wallet; the next positions are single wallets. Aave v3 on Avalanche and Polygon, Frankencoin, Curve's crvUSD BTC markets, Takara on Sei and Zest on Stacks: single-owner positions only. Vesu on Starknet has one carry vault with outside depositors, Noon's WBTC vault (37.7 WBTC since 28 January 2026, share price 1.1235), added to the map as C1. Not completed: Venus, Aave and Lista on BNB (Lista alone carries about $116M of stablecoin debt against BTCB; the 22 active borrowers found so far are EOAs, the largest $10.6M), JustLend on Tron ($550M of BTC, no holder data), Morpho on Pharos and Citrea, Dolomite, NAVI and Suilend on Sui, Kamino's other markets and Jupiter Lend.

**Not scanned:**
- Venus on BNB, about $682M of BTC collateral including SolvBTC.
- Aave v3 on Avalanche, BNB and Polygon.
- Jupiter Lend and HyperLend.
- Euler on Monad.
- Morpho on chains the API doesn't cover, other than Morph.

## Files

- `carry_products_scan.csv`: one row per product checked.
- `scan_borrowers_all.csv`: every ≥$2M borrower found.
- `raw/` (not in the repository): API and RPC dumps, including the Maple and product-mechanics pulls.
- `scripts/`: the scripts that produced them, in Python 3; the Yield Basis scripts need `/usr/bin/python3` for keccak.
