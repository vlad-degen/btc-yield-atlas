# Carry sweep from the borrower side (T = 2 Oct 2026, block 26,108,081)

Data: [`data/eth/carry_sweep.csv`](../../../data/eth/carry_sweep.csv), one row per position where ETH-family collateral backs dollar debt (at least 100 ETH). Scripts: `tools/eth/carry_sweep/`. Raw reads: `raw/eth/carry-sweep-2026-10-08/`.

## Result

Open products that borrow dollars against ETH and are not counted as carry hold **12,134 ETH against $14.0M of dollar debt**. Without the NEMO USDC operator (a dollar vault) and the closed TESS vault, the figure is 9,281 ETH. Three of them are pooled ETH products with more than 100 holders: ynETHx, 9Summits and yvWETH-2, together 6,258 ETH.

| Product | Chain, venue | Account | ETH backing dollar debt | Dollar debt | Share holders | Atlas row now |
|---|---|---|---:|---:|---:|---|
| YieldNest ynETHx (Flex Strategy LVG1) | Ethereum, Aave Core | Safe [0x24d2486f](https://etherscan.io/address/0x24d2486f5b2c2c225b6be8b4f72d46349cbf4458) | 3,744 | $3.09M | 1,102 | yieldnest (restaking) |
| NEMO USDC Prime, operator | Arbitrum, Aave | EOA [0xfb1898bb](https://arbiscan.io/address/0xfb1898bb5955fdd11704e397104c6a0e0725eb17) | 2,725 | $4.86M | n/a | none (dollar vault) |
| Lagoon 9Summits Flagship ETH | Ethereum, Spark | Safe [0xc868bfb2](https://etherscan.io/address/0xc868bfb240ed207449afe71d2ecc781d5e10c85c) | 1,590 | $1.50M | 121 | lagoon (farming) |
| Yearn yvWETH-2, Spark lender-borrower | Ethereum, Spark | strategy [0x41cfe42d](https://etherscan.io/address/0x41cfe42d221a591c6308dcea419015ba8570b380) | 924 | $1.49M | 131 | yearn-finance (lending) |
| Enzyme funds, 3 vaults of one manager | Ethereum, Aave Core | external positions 0x3a6be494, 0x934ae3e3, 0x7546cfc0 | 878 | $0.63M | 4 to 8 each | enzyme-finance (farming) |
| Lagoon DAMM Ethereum Fund | Ethereum, Spark | Safe [0xe39cd9b3](https://etherscan.io/address/0xe39cd9b36b9a86a8227ec3f5159b610bf2a30e69) | 686 | $0.70M | 8 | lagoon (farming) |
| Upshift Treehouse Growth v2 | Ethereum, Aave Core | subaccount 0xeb72e4df | 251 | $0.20M | n/a | upshift (farming) |
| Lagoon Mt Pelerin ETH pool | Ethereum, Morpho | Safe 0xee6b63e2 | 237 | $0.33M | 3 | lagoon (farming) |
| Lagoon Ammalgam WETH | Ethereum, Morpho | Safe 0x90deceec | 185 | $0.02M | n/a | lagoon (farming) |
| Upshift KPK LsETH | Ethereum, Morpho | subaccount 0x15d869a5 | 131 | $0.26M | n/a | upshift (farming) |
| IPOR TESS wstETH Debt Vault (closed) | Ethereum, Morpho | vault 0x378d18ec | 128 | $0.16M | 4 | fusion-by-ipor (farming) |
| Lagoon Gami ETH | Ethereum, Morpho | Safe 0x4ea9c877 | 105 | $0.15M | n/a | lagoon (farming) |

- **NEMO USDC operator.** The EOA runs a dollar vault. Its wstETH on Aave Arbitrum backs $4.86M USDC, and the same wallet trades on Derive. The ETH is the vault's trading book, not an ETH product.
- **Ammalgam.** Nearly all of its 185 ETH sits on Morpho against $21k of debt, so the whole collateral lands in the dollar cell.
- **Leverage tokens, not carry.** Index Coop ETH2X has 2,517 ETH. Toros ETHBULL3X on Arbitrum has 244 ETH and Index Coop ETH2x on Arbitrum has 104 ETH.

## Not products: private books borrowing dollars against ETH

| Owner | ETH | Dollar debt | Why it is not a product |
|---|---:|---:|---|
| Concrete Delta weETH Safe | 307,208 | $176.1M | One principal holds 100% of shares (already excluded) |
| rSHARE vault managers #1 to #3 | 59,686 | $87.6M | Private vaults (already excluded) |
| Dolomite Safe 0x5be9a495 | 19,285 | $205.0M | 3-of-5 Safe; USD1, USDC and WLFI collateral beside ETH; treasury book |
| Aave wrapper on Base 0xd1895f20 | 13,620 | $7.56M | Single-owner contract (owner Safe 0x6b27512a), whitelist, no shares |
| MakinaX account 0xd164a2e9 | 7,885 | $9.33M | 1-of-2 client Safe run through a MakinaX module; no share token |
| Aave wrapper on Optimism 0xb32cb14f | 713 | $0.39M | Same code as the Base wrapper; owner is an EOA |

## Who holds the A2/B2 cells

Lending split accounts with at least 100 ETH in A2+B2: 1,688 positions, 4,543,315 ETH.

| Owner | Positions | ETH | Share |
|---|---:|---:|---:|
| EOAs and EIP-7702 accounts, no product link | 1,321 | 2,667,954 | 58.7% |
| Safes, no product link | 159 | 763,923 | 16.8% |
| Per-user smart accounts | 169 | 549,024 | 12.1% |
| Private mandates and treasuries (table above) | 13 | 388,399 | 8.5% |
| Counted carry products | 14 | 160,219 | 3.5% |
| Open products not counted | 10 | 11,035 | 0.2% |
| Leverage tokens | 2 | 2,761 | 0.1% |

- **Per-user smart accounts:** DSProxy 230,698 ETH, Instadapp DSA 182,905, Summer.fi DPM 92,816, Coinbase Smart Wallet 32,183, Avocado, Ambire, Argent and Kernel about 10,000.
- **Wallets without a product link (3,431,877 ETH).** The gap scan already names part of them:
  - individuals: 1,681,487 ETH
  - funds, exchanges and market makers: 381,112 ETH
  - unknown after checks: 190,762 ETH
  - never identity-checked: 1,178,516 ETH
- **Unknown.** "No product link" means no registry match and no vault among the wallet's recent token counterparties. It does not prove the wallet is personal: Avant, NEMO and Sentora each run carry from a plain EOA.

**Other venues (step 2).** 1,323 more positions hold 909,462 ETH:

| Venue | ETH |
|---|---:|
| Sky/Maker | 591,008 |
| Accounts of 100 to 187 ETH on the split venues | 133,076 |
| Liquity v1 and v2 | 108,016 |
| Curve crvUSD and LlamaLend | 28,876 |
| Aave on Gnosis, Optimism, Avalanche, Plasma, Linea, Sonic and Scroll | 22,886 |
| Dolomite | 19,285 |
| Fluid on Base and Arbitrum | 4,268 |
| Euler | 1,681 |
| Compound on Optimism | 365 |

Per-user smart accounts hold 70.6% of that, mostly Maker DSProxies. Wallets without a product link hold 26.5%. The only products found there:
- counted: Liquity ETH Carry, Sentora and Royco
- not counted: KPK LsETH, TESS, Ammalgam and Gami (under 200 ETH each)
- leverage: ETH2x on Arbitrum

No other pooled borrower turned up in Curve, Liquity, Maker, Euler, Silo, Gearbox, Dolomite or the other Aave deployments.

## Method

1. **Lending split accounts.** Every account in `lending_split_accounts.csv` with A2+B2 of at least 100 ETH was read at the snapshot block (`classify.py`):
   - code type (EOA, EIP-7702, contract), EIP-1167 and EIP-1967 implementations
   - about 30 view functions: Safe owners and threshold, DSProxy cache, ERC-4626 `asset`, BoringVault `hook`, Mellow `vault`
   - Blockscout and Etherscan names
   - Safe modules (`classify2.py`)
   - contract owners of DSProxies and DPMs
   - the latest ERC-20 counterparties of every Ethereum EOA and Safe (`counterparties.py`)
   - Lagoon `safe()` and Upshift subaccounts, operators and strategists from the two public registries (`registries.py`)
2. **Other venues.**
   - Curve, all Liquity v1/v2 forks in the DefiLlama registry, Sky/Maker CDPs: 100% of debt read.
   - Euler v2 on 15 chains: 100% of debt read. Silo v1/v2, Gearbox v3 and Dolomite: no position of 100 ETH except the Dolomite Safe.
   - Aave v3 on Optimism, Avalanche, Gnosis, Linea, Plasma, Sonic, Scroll, Mantle, Celo, zkSync and Metis.
   - Compound and Fluid on L2s, and the 100 to 187 ETH band of the split venues.
   - Owners classified the same way (`classify_venues.py`). Assembly: `build.py`.
3. **Counted** means listed in `data/eth/netmap/carry_lending_snapshot.json`, plus Liquity ETH Carry and Rocksolid.

## Gaps

- **L2 split venues are only partly read.** The 100 ETH accounts read cover only part of the collateral that backs dollar debt on these venues; the rest is the split's estimate for accounts it did not read:

  | Venue | Share read |
  |---|---:|
  | Aave Arbitrum | 46% |
  | Aave Base | 57% |
  | Morpho Base | 50% |
  | Compound Arbitrum | 61% |
  | Aave Core | 91% |
  | Spark, Morpho Ethereum, Compound Ethereum, Aave Prime | 96 to 99% |

  A small L2 product could sit in the unread part.
- **Not read:**
  - Aave Polygon and BNB, and Compound Base: log limits and rate limits.
  - HyperLend: its whole UETH supply was about 3,035 ETH, so at most a few positions are missed.
  - Dolomite Botanix.
- **Counterparty check is partial.** It covers only the last 150 or so ERC-20 transfers, on Ethereum only. L2 EOAs had only the registry check.
- **Dollar debt includes EURe on Gnosis.** It is a fiat stablecoin; 9,952 ETH on one EOA backs EURe.
- **Agreement with CARRY-DISCOVERY.md.** The top-down sweep found ynETHx, 9Summits, yvWETH-2, DAMM, Mt Pelerin, Treehouse, KPK and Gami, and this sweep agrees. It adds the NEMO USDC operator, the Enzyme funds, the MakinaX account and the two private Aave wrappers.
