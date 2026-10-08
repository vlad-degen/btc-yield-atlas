# Carry discovery sweep (T = 2 Oct 2026, block 26,108,081)

Data: [`data/eth/carry_discovery.csv`](../../../data/eth/carry_discovery.csv). Raw reads and scripts: `raw/eth/carry-sweep-2026-10-08/` (`main/`, `infraA/`, `infraB/`). ETH at $2,669.

## Result

Four open products borrow dollars against ETH and are not in the carry category. Together they hold about 7,000 ETH of collateral against $6.9M of dollar debt. That is roughly 2 to 3% of the dollar debt the atlas counts as carry (about $250M to $280M).

| Product | ETH collateral | Dollar debt | Where | Atlas today |
|---|---:|---:|---|---|
| YieldNest ynETHx | 3,744 (3,005.9 wstETH) | $3.09M USDe | Aave Core, Safe [0x24d2486f](https://etherscan.io/address/0x24d2486f5b2c2c225b6be8b4f72d46349cbf4458) | inside "YieldNest", restaking |
| 9Summits Flagship ETH (Lagoon) | 1,590 (1,423.8 weETH) | $1.50M USDS | Spark, Safe [0xc868bfb2](https://etherscan.io/address/0xc868bfb240ed207449afe71d2ecc781d5e10c85c) | inside "Lagoon vaults (other)", farming |
| Yearn yvWETH-2 | 976 (742 wstETH plus a second leg) | $1.58M USDS | Spark, strategy [0x41cfe42d](https://etherscan.io/address/0x41cfe42d221a591c6308dcea419015ba8570b380) | inside "Yearn", lending |
| DAMM Ethereum Fund (Lagoon) | 686 | $0.70M USDC+USDT | Spark, Safe [0xe39cd9b3](https://etherscan.io/address/0xe39cd9b36b9a86a8227ec3f5159b610bf2a30e69) | inside "Lagoon vaults (other)", farming |

All four products were open to deposits at T:
- **ynETHx:** `paused()` is false and `maxDeposit` is max.
- **9Summits and DAMM:** both are Lagoon async vaults. DAMM appears to be whitelisted.
- **yvWETH-2:** `maxDeposit` is 8,857 ETH.

**Notes:**
- **ynETHx.** The USDe goes to a YieldNest Safe and then into YieldNest's own dollar vault, ynRWAx. This is the same own-credit pattern as Avant. Its leverage strategy LVG1 reports 3,029.9 wstETH of assets. That is the gross collateral with no deduction for the USDe loan, so check its book before using it.
- **yvWETH-2.** The borrowed USDS goes into yvUSD. The closed yETH-Recovery vault holds 42.8% of the shares, so only about 57% belongs to open depositors.
- **9Summits** was marked "unverified" in CARRY-COVERAGE-AUDIT. It is now confirmed.

Smaller than 500 ETH, left out: Mt Pelerin ETH (Lagoon, $0.33M), Treehouse Growth v2 (Upshift, $0.20M), KPK LsETH (Upshift, $0.26M), Gami ETH, Ammalgam WETH.

Closed: TESS wstETH Debt Vault (IPOR, deposits closed).

## Earlier open cases now closed

- **Concrete wstETH Plus ($121M).** Its strategy multisig is the Concrete Delta Safe 0x7ee29373, and that Safe holds 100% of the shares. It is one principal's mandate, like Delta. Exclude it.
- **mRe7ETH (4,843 ETH).** Deposits go to Re7 EOA 0x462a336d, which has only ETH debt. This is an ETH loop, not carry.
- **yoETH.** The vault has no loan of its own. It only lends.
- **Not carry, ETH debt only:** Fluid Lite iETHv2, Treehouse tETH, Cian ylrsETH, Kelp Gain, hgETH (an rsETH loan book), and the IPOR stETH and cbETH loopers.
- **Unresolved:** Lucidly cyETH. No deployed address was found.

## How the sweep was done

1. **DefiLlama.**
   - Protocols: 501 protocols in the vault, curator, yield, CDP, basis and restaking categories with TVL above $1M. ETH-family tokens were measured from each protocol's latest token breakdown.
   - Pools: single-asset ETH pools above $1M. Every vault or curator project with more than about 500 ETH was checked, using the strategy description or on-chain debt.
2. **Vault infrastructures, read at T.**
   - Veda: all 196 BoringVaults with Enter events.
   - Lagoon: 65 vaults and their Safes.
   - IPOR: 496 vaults.
   - Upshift: registry, subaccounts and EOA operators.
   - Also: Mellow, Concrete, Midas, YO, Yearn v3 (ydaemon), Cian, Sommelier, Fluid Lite, Treehouse, Toros, Index Coop.
   - Minted-dollar venues: Liquity v2 troves above $0.3M, crvUSD and LlamaLend loans above $0.5M, and Sky CDPs above $0.9M. The only pooled borrower there is the counted Liquity ETH Carry.
   - HyperEVM ETH lending is below $2.5M in total.
3. **Reverse check from the borrower side.** The source is every account in the gap scan (`merged_addresses.json`) with at least $0.4M of ETH-backed dollar debt, 575 in all. It covers Aave Core, Prime and Spark, Morpho, Compound, Fluid, Euler and Aave v4 on Ethereum, plus Aave and Morpho on Base, Arbitrum and Katana.
   - Every contract account was named through Blockscout.
   - The 44 Safes under $5M were checked for owners, modules and token counterparties. Only the ynETHx and 9Summits Safes deal with a vault.
   - The other non-Safe contracts are per-user accounts (DeFi Saver, Summer.fi, Instadapp, Ambire, Avocado, Coinbase smart wallets) or leverage tokens. The one exception is the Yearn strategy.
4. **Web and curator search.** I searched for "ETH carry vault", borrowing stablecoins against ETH, and the curators named in the brief. Nothing new turned up beyond the products above. UltraYield's ETH product is hgETH, an rsETH loan book. Its other ETH vaults only lend.

## What the atlas may still miss

- **EOA-run products under $5M.** 273 EOAs carry $421M of ETH-backed dollar debt between about $0.4M and $5M, and none of them is identified. Counted products run from EOAs (NEMO, Sentora), so a product could hide here. Upshift's EOA operators were checked. The rest look like individuals, but this is not proven.
- **Venues not scanned.** About $350M of ETH is supplied on lending venues that were not scanned: Monad Euler and Morpho, Venus BSC, Aave Polygon, Gnosis, Optimism, X Layer, Ink Tydro, Katana Morpho (partly covered). No ETH vault product was found borrowing there.
- **Under the scan floor.** Products with less than about $0.9M of debt on a venue are found only through the infrastructure listings.

**Estimate.** Beyond the four rows above, uncovered pooled ETH carry is probably under $5M of dollar debt and under 5,000 ETH. The upper bound comes from the share of the $421M EOA bucket that is not individuals, and that share is unknown.
