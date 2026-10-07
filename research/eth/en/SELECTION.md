# Top 5 live ETH-collateral dollar-carry products: selection and borrower scan (T = 2026-10-02 23:59:59 UTC)

*Data: [`data/eth/gap_borrower_scan.csv`](../../../data/eth/gap_borrower_scan.csv) (one row per account), [`data/eth/gap_borrower_scan_coverage.json`](../../../data/eth/gap_borrower_scan_coverage.json) (per market). Raw pulls and scripts: `raw/eth/gap-2026-10-07/borrower-scan/` (not published).*

**Definition used.** As in the [BTC selection](../../top5/en/00-selection.md): a live product with outside depositors that takes ETH (or an ETH wrapper or LST/LRT), posts it as collateral, borrows dollars, and puts the dollars into a strategy that earns yield for the ETH depositors.

**Out of scope:** EOAs; per-user smart accounts (Instadapp DSA and Avocado, Summer.fi DPM, DSProxy, DeFi Saver Safes, Contango, Coinbase Smart Wallet, EIP-7702 wallets); treasuries and funds trading for themselves; ETH-debt staking loops; leverage tokens that turn the dollars back into ETH.

**Ranking metric.** Dollar debt attributed to the product at T, as in `economic_questions.json`.

**Timing and prices.** Ethereum block 26,108,081. L2s at the last block with timestamp at or before T: Base 52,098,126; Arbitrum 511,139,919; Optimism 157,693,411; Linea 32,215,437; other Morpho chains in `coverage.json`. Collateral and debt are valued with each venue's oracle at T (Aave, Spark, Compound) or at loan-asset units x API price (Morpho, Fluid). EUR stablecoins are not counted. ETH was about $2,666.

## Ranked result

| # | Product | Dollar debt at T | Accounts in the scan | Scan check |
|---|---|---|---|---|
| 1 | **ether.fi Liquid ETH** | **$181.1M** | BoringDrone `0x0a42…fc02c` $80.2M (Aave Core, Spark); vault `0xf0bb…416c` $66.6M (Morpho); loan manager `0xc936…f3` $34.3M (Morpho) | Matches to the dollar |
| 2 | **YieldBasis WETH** | **$27.8M** crvUSD | Curve credit line, not a lending venue | Outside the scan by design |
| 3 | **Lido Earn ETH** (Mellow strETH) | **$25.6M** | Sub Vault 3 `0x181c…76d`: $22.2M USDT Aave Core + $3.3M USDT Spark | Matches |
| 4 | **Avant avETH** | **$10.0M** attributed | Wallet `0x6cc6…c4bd` owes **$19.7M** at T: also $9.0M USDG/frxUSD on an Aave v4 spoke and $0.65M RLUSD on Morpho | Under-counted by $9.6M; still #4 |
| 5 | **Liquity ETH Carry** | **$6.8M** ebUSD | Ebisu, not a scanned venue | Outside the scan |
| 6 (alternate) | NEMO ETH Prime | $5.6M | `0x9088…5e90`, Morpho wstETH/USDC | Matches |
| 7 (alternate) | Rocksolid rETH | $2.7M | Strategy wallets off Ethereum lending venues | Not in scan |
| 8 (new, alternate) | **Yearn WETH-2 yVault**, Spark wstETH/USDS lender-borrower strategy | **$1.49M** USDS | Strategy `0x41cf…b380` (742 wstETH on Spark); 100% of its shares sit in an accumulator owned 99.9% by the public WETH-2 yVault `0xac37…7571`; dollars go to yvUSD | New product |

The selection does not change: the scan finds no pooled product above Avant that the study missed.

**Smaller products already in the study** (under the $5M scan line, not re-traced): Sentora ETH $1.2M, Makina DETH $0.4M, Royco, Vesper, Reservoir, TAU InfiniFi, ZenSats.

**Private mandates beside the census** (single principal, permissioned):
- Concrete Delta weETH Safe `0x7ee2…5178`: $176.1M.
- Three rSHARE WETH vault managers (`0xa122…`, `0x4f87…`, `0xa56d…`): $80.4M, including $5.1M on Aave Base and $2.0M on Aave v4 that the earlier pass did not count.

## Borrower scan: coverage

Every account with at least $5M of stablecoin debt and any ETH-family collateral enabled. "Read at T" is the share of each market's stablecoin debt sitting in the accounts we read at T; above $5M the list is complete where the method says so.

| Venue | Stablecoin debt at T | Read at T | Method | Accounts ≥$5M (with ETH) | ETH-backed debt in them |
|---|---|---|---|---|---|
| Aave v3 Core, Ethereum | $5,211.7M | 79% | Blockscout holders of every stablecoin debt token down to $1M, plus every Repay user after T (879 on Core) | 139 (97) | $1,710.5M |
| Spark | $1,567.8M | 91% | Same | 43 (33) | $929.8M |
| Aave v3 Prime (Lido) | $51.2M | 87% | Same | 3 (3) | $40.3M |
| Aave v3 EtherFi | $0 | n/a | Same | 0 | 0 |
| Morpho, Ethereum (125 ETH/USD markets) | $350.1M | 93% | API positions to $0.3M plus repay/liquidation users after T; archive reads at T | 10 | $256.3M |
| Compound cUSDCv3, Ethereum | $346.8M | 90% | All 8,103 accounts in ETH-asset SupplyCollateral logs | 15 | $100.2M |
| Compound cUSDTv3, Ethereum | $145.9M | 55% (rest is non-ETH collateral) | All 935 accounts, same | 4 | $33.8M |
| Fluid, Ethereum (ETH/USD vaults) | $74.9M | 93% | Every position via VaultPositionsResolver at T | 4 | $44.3M |
| Euler v2, Ethereum (8 USD vaults ≥$1M) | $33.9M | 100% | Every Borrow-log account; debtOf at T | 1 (0) | 0 |
| Aave v4 (15 spokes) | $129.2M in positions ≥$0.5M (all assets $303.0M) | 100% of 3,997 (spoke, user) pairs | Borrow logs since block 23.0M; account data at T | 6 | $28.0M |
| Aave v3 Base | $163.0M | 18% | Basescan holder pages to $0.5M | 1 (1) | $7.7M |
| Aave v3 Arbitrum | $202.0M | 22% | Arbiscan holder pages to $0.5M | 0 (largest $4.9M) | 0 |
| Aave v3 Optimism, Linea | $13.5M, $1.5M | n/a | Holder lists; no account ≥$1M | 0 | 0 |
| Morpho Base (128 markets) | $111.2M | 31% | As Ethereum | 0 (largest $1.7M; Coinbase loan wallets) | 0 |
| Morpho, 11 other API chains | $8.1M | n/a | As Ethereum (Stable, Robinhood: API state) | 0 | 0 |
| Fluid Base, Arbitrum | $3.5M, $5.4M | 50%, 41% | As Ethereum | 0 | 0 |

**Totals.** 162 accounts hold $3,839M of stablecoin debt with some ETH collateral; $3,206M of it is ETH-backed after allocating mixed accounts by collateral value. 47 accounts are above $20M; they hold $2,369M ETH-backed.

**By type, ≥$5M accounts:** 97 EOAs, 31 Safes, 8 Instadapp DSAs, 5 EIP-7702 wallets, 2 DSProxies, 2 Summer.fi DPMs, 1 Avocado, 1 Ambire and 4 product contracts. The other 11 have less than $1M of ETH-backed debt and were not code-checked.

**Every contract among the ≥$1M ETH-backed accounts was screened.** Apart from Liquid ETH, Lido Earn, Yearn and Index Coop's ETH2X, all are Safes or per-user smart accounts.

## The >$20M wallets

| # | Address | Who | Category | Venues | Stablecoin debt | ETH-backed | Pooled? |
|---|---|---|---|---|---|---|---|
| 1 | [`0xd848…f452`](https://etherscan.io/address/0xd848f54280f8fe8661b796e3bb8d8922c87af452) | DSProxy #142,759 of EOA 0x7d6149ad (unlabeled, 2016-era funding) | individual | Aave Core, Spark | $212.4M | $212.4M | no |
| 2 | [`0x9992…f242`](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | 1-of-1 Safe of 7702 EOA 0x54d25040, funded from a 2015 genesis allocation | individual | Aave Core, Spark | $205.9M | $205.9M | no |
| 3 | [`0x7ee2…5178`](https://etherscan.io/address/0x7ee29373f075ee1d83b1b93b4fe94ae242df5178) | Concrete Delta weETH Safe; one Bitfinex-linked principal | private mandate | Aave Core, Morpho | $176.1M | $176.1M | no |
| 4 | [`0x741a…31f3`](https://etherscan.io/address/0x741aa7cfb2c7bf2a1e7d4da2e3df6a56ca4131f3) | Kraken-funded EOA (2019); cluster C-7S with #7 and #11 | individual | Aave Core | $126.1M | $126.1M | no |
| 5 | [`0xed0c…4312`](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | Kraken-funded trading wallet: $1.95B through the Spark PSM, $1.10B to a Binance deposit in 120 days | fund / market maker (unnamed) | Spark | $125.3M | $125.3M | no |
| 6 | [`0xb99a…bcf5`](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | Abraxas Capital: Heka Funds (Etherscan label) | fund | Spark | $115.4M | $84.9M | no |
| 7 | [`0x28a5…a6b0`](https://etherscan.io/address/0x28a55c4b4f9615fde3cdaddf6cc01fcf2e38a6b0) | Unlabeled EOA; created DSA #11; cluster C-7S | individual | Aave Core, Spark | $112.2M | $112.2M | no |
| 8 | [`0xe40d…03bf`](https://etherscan.io/address/0xe40d278afd00e6187db21ff8c96d572359ef03bf) | 2-of-5 Safe; 3 signers funded by CEX.IO; $172.4M stables in from CEX.IO | exchange (CEX.IO) | Aave Core, Spark | $109.9M | $40.8M | no |
| 9 | [`0x2835…62b1`](https://etherscan.io/address/0x28355886a65848488cf0a3646fca395db0a762b1) | Binance-funded whale cluster (funder 0x4352cc84) | individual | Spark | $84.2M | $39.6M | no |
| 10 | [`0x0a42…c02c`](https://etherscan.io/address/0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c) | ether.fi Liquid ETH BoringDrone | product | Aave Core, Spark | $80.2M | $80.2M | yes |
| 11 | [`0x3a0d…97d9`](https://etherscan.io/address/0x3a0dc3fc4b84e2427ced214c9ce858ea218e97d9) | Instadapp DSA of #7, funded with $179.0M by #4 | individual | Spark | $79.4M | $79.4M | no |
| 12 | [`0x3478…dcf`](https://etherscan.io/address/0x34780c209d5c575cc1c1ceb57af95d4d2a69ddcf) | Binance client: $310M in from Binance hot wallets, $362.5M to a Binance deposit | individual | Aave Core | $66.9M | $66.9M | no |
| 13 | [`0xf0bb…416c`](https://etherscan.io/address/0xf0bb20865277abd641a307ece5ee04e79073416c) | ether.fi Liquid ETH vault | product | Morpho | $66.6M | $66.6M | yes |
| 14 | [`0xabbd…e7f1`](https://etherscan.io/address/0xabbd5b2b0b034781e58434736728b9d0673de7f1) | Coinbase Prime client (funded by Coinbase 54; $55.8M from Coinbase Prime 1) | fund (unnamed) | Aave Core | $65.2M | $65.2M | no |
| 15 | [`0xdc3a…1a95`](https://etherscan.io/address/0xdc3abf85e090528669cf1b44ef4082b269c21a95) | EOA with a fresh 2025 funding chain | unknown after checks | Aave Core | $63.8M | $63.8M | no |
| 16 | [`0xe84a…7487`](https://etherscan.io/address/0xe84a061897afc2e7ff5fb7e3686717c528617487) | 4-of-9 Safe, cluster C-BitGo (signers funded from a BitGo wallet) | fund | Aave Core | $52.2M | $52.2M | no |
| 17 | [`0xc3fe…31e4`](https://etherscan.io/address/0xc3fe8b63ea05e8e27b3f3358d646915d7ed931e4) | 1-of-1 Safe, cluster C-Bfx3 (owners funded via Bitfinex 3 on one day); USDT sold through DeFi Saver | individual | Aave Core | $51.0M | $51.0M | no |
| 18 | [`0xb656…9514`](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) | EOA funded in July 2026 through fresh wallets | unknown after checks | Spark | $49.4M | $49.4M | no |
| 19 | [`0x2bd7…fb82`](https://etherscan.io/address/0x2bd72f8fb377337c9cc16da4dd2dd274537ffb82) | EOA funded through THORChain; dormant | unknown after checks | Aave Core | $47.0M | $47.0M | no |
| 20 | [`0x4093…9987`](https://etherscan.io/address/0x4093f559f38c4c87c280d64c85396f649c0d9987) | 4-of-8 Safe, cluster C-BitGo | fund | Compound USDC | $39.8M | $12.1M | no |
| 21 | [`0x34d1…4ac1`](https://etherscan.io/address/0x34d1231f15da58762a84ead35242896e7fec4ac1) | 1-of-1 Safe, cluster C-Bfx3 | individual | Aave Core | $38.7M | $38.7M | no |
| 22 | [`0x9cc6…0f98`](https://etherscan.io/address/0x9cc65c0560acdb03c4e7cef83e02fbe413920f98) | EOA, Poloniex-rooted funding (cluster C-Polo); trades with the "7 Siblings Recursive Farmer" DSA | individual | Spark | $38.7M | $38.7M | no |
| 23 | [`0x7ba7…3520`](https://etherscan.io/address/0x7ba7f4773fa7890bad57879f0a1faa0edffb3520) | Gemini-funded EOA (2017), mostly WBTC | individual | Compound USDC | $37.8M | $3.0M | no |
| 24 | [`0x086e…7197`](https://etherscan.io/address/0x086eb5c592329213ef2ede5ed2ad5f630ce95197) | 1-of-1 Safe; borrowed USDT resupplied to Aave | individual | Aave Core | $37.6M | $37.6M | no |
| 25 | [`0x0a0f…476e`](https://etherscan.io/address/0x0a0fa2b02ae73bd9eb4c1e086458099eca42476e) | Binance-funded EOA, mostly WBTC | individual | Aave Core | $36.5M | $11.4M | no |
| 26 | [`0xc936…45f3`](https://etherscan.io/address/0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3) | ether.fi Liquid ETH loan manager | product | Morpho | $34.3M | $34.3M | yes |
| 27 | [`0x2269…3588`](https://etherscan.io/address/0x2269ce2753e2967dd5322a56188c3d24435b3588) | 1-of-1 Safe, cluster C-Bfx3 | individual | Aave Core | $33.8M | $33.8M | no |
| 28 | [`0xa122…c7e6`](https://etherscan.io/address/0xa122687285dc5012141055a801045f069112e7c6) | rSHARE vault #1 manager | private mandate | Spark, Morpho, Aave Base | $33.8M | $33.8M | borderline |
| 29 | [`0xcaf1…666e`](https://etherscan.io/address/0xcaf1943ce973c1de423fe6e9f1a255049e51666e) | EOA, cluster C-Polo | individual | Spark | $28.4M | $28.4M | no |
| 30 | [`0xa3d8…b6fb`](https://etherscan.io/address/0xa3d843b6a057504284006bef6f34a2e9bc80fb6b) | Binance-funded EOA, mostly WBTC | individual | Compound USDC, Aave Arbitrum | $28.2M | $10.6M | no |
| 31 | [`0x5ffc…3c37`](https://etherscan.io/address/0x5ffcdb28b8cc958afe052947d43cb6af04833c37) | Binance-funded EOA (2021), 110,725 wstETH | individual | Spark | $28.1M | $28.1M | no |
| 32 | [`0xfdd8…6a92`](https://etherscan.io/address/0xfdd86a96f47015d9c457c841e1d52d06ede16a92) | 2-of-3 Safe, signers from a 2015 genesis allocation | individual | Spark | $27.4M | $27.4M | no |
| 33 | [`0x44e8…3b1d`](https://etherscan.io/address/0x44e8c2451e916c87dde3977dc80f6fb8a1e33b1d) | Binance-funded EOA, mixed BTC/ETH | individual | Aave Core | $25.9M | $9.0M | no |
| 34 | [`0x181c…a76d`](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | Mellow strETH Sub Vault 3 (Lido Earn ETH) | product | Aave Core, Spark | $25.5M | $25.5M | yes |
| 35 | [`0xb5c9…dc4`](https://etherscan.io/address/0xb5c98c0d2861d39c538aff4e87cee946ffa1adf4) | Uphold-rooted EOA, mixed weETH/BTC | individual | Aave Core, Spark | $24.3M | $14.8M | no |
| 36 | [`0xa028…b4`](https://etherscan.io/address/0xa028bef2835cab01d39dc3ff34abc46a2f665bb4) | 3-of-6 Safe, signers funded by KuCoin; dollars to KuCoin deposits | unknown (KuCoin-linked) | Aave Core | $24.0M | $23.8M | no |
| 37 | [`0xa56d…846f`](https://etherscan.io/address/0xa56da9bb528fedf8379b02e95fbbdad34d45846f) | rSHARE vault #3 manager | private mandate | Spark, Morpho, Aave v4, Aave Base | $23.7M | $23.7M | borderline |
| 38 | [`0x7f6d…85bd`](https://etherscan.io/address/0x7f6d23e436099ec78a73c430b16782b0d68585bd) | 4-of-7 Safe, cluster C-BitGo | fund | Aave Core | $23.6M | $23.6M | no |
| 39 | [`0x160f…ab5b`](https://etherscan.io/address/0x160f6ef9fcdde6ff3febc7a57edbfd476a8aab5b) | Binance-funded EOA | individual | Aave Core, Spark | $23.3M | $22.9M | no |
| 40 | [`0x4f87…0545`](https://etherscan.io/address/0x4f87de7d21aef48090958f7342e1f69dff790545) | rSHARE vault #2 manager | private mandate | Spark, Morpho | $22.9M | $22.9M | borderline |
| 41 | [`0x96f4…cb94`](https://etherscan.io/address/0x96f49d0e9724dfd8780fa667ac37a993f005cb94) | 3-of-4 Safe borrowing GHO; Binance flows | unknown after checks | Aave Prime | $22.8M | $22.8M | no |
| 42 | [`0xee28…1268`](https://etherscan.io/address/0xee2826453a4fd5afeb7ceffeef3ffa2320081268) | Etherscan label "Fee Recipient" (block builder/validator) | fund / market maker (unnamed) | Spark | $22.7M | $22.7M | no |
| 43 | [`0x5bf7…caa3`](https://etherscan.io/address/0x5bf7883a7551fd03ed8d710ac2d1c86db321caa3) | 1-of-1 Safe via DeFi Saver | individual | Fluid | $22.7M | $22.7M | no |
| 44 | [`0x989b…ae18`](https://etherscan.io/address/0x989b96317735d70a7762bf96c034b203713aae18) | EOA; FTX in funding chain; BTSE counterparties | individual | Aave Core | $22.0M | $22.0M | no |
| 45 | [`0xd71f…1f64`](https://etherscan.io/address/0xd71f4423e097888af07e2ceac0e71b9a43f64a1f) | EOA, mostly WBTC | individual | Aave Core | $21.6M | $5.1M | no |
| 46 | [`0xc687…f369`](https://etherscan.io/address/0xc6877a65349b0fa45cc61a267ee682c7abf2b369) | EOA, mostly cbBTC | individual | Spark | $20.9M | $6.5M | no |
| 47 | [`0x54b3…bca4`](https://etherscan.io/address/0x54b338e6cfd605dad2264b96b0a730fb2bdca9e4) | Binance-funded EOA | individual | Aave Core | $20.3M | $18.6M | no |

**Summary of the 47** ($2,369M ETH-backed):
- **Pooled products: 4 wallets, $206.6M.** Liquid ETH (3) and Lido Earn.
- **Private mandates: 4 wallets, $256.5M.** Concrete Delta and the three rSHARE managers.
- **Funds, desks and exchanges: 8 wallets, $426.8M.** Abraxas Heka, CEX.IO, the BitGo-custodied Safe trio, a Coinbase Prime client, the Kraken-funded trading wallet and the "Fee Recipient" wallet.
- **Individuals and unlabeled wallets: 31, $1,479.5M**, of which 5 remain unknown after checks.

**Clusters found:**
- **C-7S, $317.7M.** `0x741a`, `0x28a5` and its DSA `0x3a0d`. `0x28a5` created the DSA, and `0x741a` funded it with $179.0M. Both trade with the DSA Etherscan labels "7 Siblings Recursive Farmer".
- **C-Bfx3, $123.5M.** Three 1-of-1 Safes whose owners were funded via Bitfinex 3 on the same day. Their borrowed USDT went into DeFi Saver swaps: leveraged ETH, not carry.
- **C-BitGo, $87.9M.** Three Safes with shared signers funded from a BitGo WalletSimple.
- **C-Polo, $67.1M.** Two EOAs with a common Poloniex funding root.

**Where the dollars went (first hops).** Per row in the CSV.
- Products: into stable vaults (Sentora, Hastra, Cap, Mellow earnUSD, yvUSD).
- Individuals: CoW and Uniswap swaps, the Spark PSM, back to owners, and exchange deposits (Binance, KuCoin, Bitget).

## Excluded, with reasons

| Candidate | Size | Why excluded |
|---|---|---|
| Concrete Delta weETH | $176.1M | Private mandate: one principal holds 100% of shares |
| rSHARE vaults #1-#3 | $80.4M | Whitelisted, NAV never posted, depositors look like one principal |
| Index Coop ETH2X `0x65c4…48a2` | $3.0M USDC | Pooled, but the dollars buy more ETH: leverage, not carry |
| Seamless wstETH/ETH 25x, Mellow strETH Sub Vault 2 | WETH debt only | ETH-debt staking loops |
| Abraxas Heka Funds `0xb99a…` | $115.4M | Fund trading for itself, no on-chain share token (as in the BTC study) |
| CEX.IO Safe `0xe40d…` | $109.9M | Exchange book |
| BitGo Safe trio, Coinbase Prime client, Kraken-funded desk, Fasanara | see table | Funds or desks, no share token |
| Coinbase loan wallets on Morpho Base | $1.0-1.7M each | Retail borrowing |
| Per-user accounts (DSA, DPM, DSProxy, Avocado, Ambire, DeFi Saver Safes) | see CSV | Per-user tools |

## Gaps

- **Post-T exits on L2 Aave are not enumerated.** Public log endpoints cap Base at 1,000 blocks and drpc at 10,000. Holder lists go down to $0.5M, so only a position that was at least $5M at T and fully closed by 7 October would be missed.
- **Compound v3 on Base ($11.6M) and Arbitrum ($22.7M) was not enumerated**, for the same reason. Only total borrow at T was read.
- **Euler v2 on Base and Arbitrum holds only $1.8M of stablecoin debt**, so no account there can reach $5M.
- **Not scanned:** Curve crvUSD ETH markets, Liquity v2 and its forks other than the known Ebisu book, Aave v3 on Avalanche, Polygon and BNB, Kamino, and Venus.
- **Identity depth.** The 47 wallets above $20M were checked by hand: labels, Safe owners, funding chains, and flows in the 120 days to T, plus full history for quiet wallets. The other 115 accounts at or above $5M got the automated pass (labels, funding chain, 120-day flows) or, where ETH backs less than $1M of the debt, a code-type screen only. Arkham was not available.
