# ETH yield market coverage tables

Published 3 October 2026; protocol table corrected 4 October. Snapshot T: 2 October 2026, 23:59:59 UTC.

The chain table uses discovery data captured after T. It shows the full TVL of candidate pools, including non-ETH assets in mixed pools, repeated receipt deposits and borrowing. It does not measure net capital or a verified upper or lower bound on unique ETH.

| Chain | Candidate pools | Full-pool TVL, $M | Pools ≥$5M | Selected for deeper study |
|---|---:|---:|---:|---|
| Ethereum | 2472 | 66,462.260 | 184 | yes |
| Base | 2121 | 1,319.010 | 32 | yes |
| Tron | 1 | 1,288.655 | 1 | yes |
| BNB Chain | 46 | 637.576 | 5 | yes |
| Arbitrum | 433 | 568.131 | 17 | yes |
| Linea | 32 | 208.053 | 1 | yes |
| Monad | 20 | 127.920 | 5 | yes |
| Optimism | 185 | 96.490 | 4 | yes |
| Polygon | 132 | 62.127 | 2 | yes |
| Gnosis | 9 | 39.790 | 1 | yes |
| Katana | 9 | 21.413 | 3 | screen |
| Avalanche | 23 | 20.040 | 1 | screen |
| Ink | 9 | 17.989 | 1 | screen |
| Cronos | 8 | 14.707 | 1 | screen |
| Starknet | 27 | 11.012 | 0 | screen |
| Solana | 13 | 5.931 | 0 | screen |
| Fraxtal | 12 | 5.794 | 0 | screen |
| Mantle | 5 | 5.615 | 1 | screen |
| Polkadot | 2 | 4.858 | 0 | screen |
| Fantom | 1 | 3.142 | 0 | screen |
| Unichain | 7 | 2.841 | 0 | screen |
| Berachain | 7 | 2.415 | 0 | screen |
| Celo | 4 | 2.066 | 0 | screen |
| Flare | 9 | 1.708 | 0 | screen |
| Rootstock | 1 | 1.047 | 0 | screen |
| Native Core | 1 | 0.997 | 0 | screen |
| Robinhood Chain | 17 | 0.960 | 0 | screen |
| Sui | 4 | 0.740 | 0 | screen |
| Osmosis | 8 | 0.683 | 0 | screen |
| Sonic | 15 | 0.663 | 0 | screen |
| MegaETH | 3 | 0.640 | 0 | screen |
| Scroll | 3 | 0.601 | 0 | screen |
| ZKsync Era | 8 | 0.595 | 0 | screen |
| Plasma | 4 | 0.580 | 0 | screen |
| Bifrost Network | 1 | 0.507 | 0 | screen |
| MultiversX | 3 | 0.438 | 0 | screen |
| Defichain | 1 | 0.200 | 0 | screen |
| Flow | 1 | 0.180 | 0 | screen |
| Bob | 3 | 0.160 | 0 | screen |
| Heco | 5 | 0.147 | 0 | screen |
| Metis | 4 | 0.111 | 0 | screen |
| Hemi | 2 | 0.096 | 0 | screen |
| HyperEVM | 1 | 0.063 | 0 | screen |
| Shape | 1 | 0.053 | 0 | screen |
| Move | 3 | 0.053 | 0 | screen |
| Abstract | 1 | 0.050 | 0 | screen |
| Thorchain | 1 | 0.036 | 0 | screen |
| Manta | 1 | 0.029 | 0 | screen |
| Neo | 1 | 0.029 | 0 | screen |
| Opbnb | 1 | 0.025 | 0 | screen |
| Taiko | 1 | 0.022 | 0 | screen |
| Moonbeam | 1 | 0.021 | 0 | screen |
| Soneium | 1 | 0.020 | 0 | screen |
| Mode | 1 | 0.013 | 0 | screen |
| Cronos zkEVM | 1 | 0.012 | 0 | screen |
| Neutron | 1 | 0.010 | 0 | screen |
| Algorand | 1 | 0.004 | 0 | screen |

## Corrected dated protocol observations

This table uses the same corrected 85-row ledger as the Market chapter. There are 81 observed rows across all groups, and 59 in the default six-group selection. Lending and CDP are off by default. Each observed row selects dated ETH-family token balances within the disclosed freshness window; daily adapter measurements are separate from fixed-block product books.

Reserve Protocol excludes dollar claims such as AETHUSDC from the ETH subtotal. The four major missing liquidity adapters stay unmeasured. Basis has no measured frozen observation; an absent ETH token field does not establish zero basis capital. Signed debt stays signed. These are overlapping exposure layers, not unique ETH or verified outside investor equity.

| Protocol | ETH-family exposure, $M | Research group | Token date UTC | Status |
|---|---:|---|---|---|
| [Lido](https://api.llama.fi/protocol/lido) | 26,677.058 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Binance staked ETH](https://api.llama.fi/protocol/binance-staked-eth) | 10,081.459 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Aave V3](https://api.llama.fi/protocol/aave-v3) | 9,835.182 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [EigenCloud](https://api.llama.fi/protocol/eigencloud) | 7,075.345 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [ether.fi Stake](https://api.llama.fi/protocol/ether.fi-stake) | 5,188.347 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [SparkLend](https://api.llama.fi/protocol/sparklend) | 4,160.791 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Sky Lending](https://api.llama.fi/protocol/sky-lending) | 1,639.333 | CDP collateral | 02 Oct 2026, 00:00 | observed |
| [Morpho Blue](https://api.llama.fi/protocol/morpho-blue) | 1,421.869 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Rocket Pool](https://api.llama.fi/protocol/rocket-pool) | 1,409.233 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [JustLend V1](https://api.llama.fi/protocol/justlend-v1) | 1,309.833 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Kelp](https://api.llama.fi/protocol/kelp) | 1,130.443 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [StakeWise V3](https://api.llama.fi/protocol/stakewise-v3) | 1,016.917 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Concrete](https://api.llama.fi/protocol/concrete) | 953.047 | USD carry / hybrid parents | 02 Oct 2026, 00:00 | observed |
| [Compound V3](https://api.llama.fi/protocol/compound-v3) | 724.582 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [mETH Protocol](https://api.llama.fi/protocol/meth-protocol) | 637.236 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Coinbase Wrapped Staked ETH](https://api.llama.fi/protocol/coinbase-wrapped-staked-eth) | 516.968 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [ether.fi Liquid](https://api.llama.fi/protocol/ether.fi-liquid) | 402.665 | USD carry / hybrid parents | 02 Oct 2026, 00:00 | observed |
| [Curve DEX](https://api.llama.fi/protocol/curve-dex) | 269.230 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Aave V4](https://api.llama.fi/protocol/aave-v4) | 240.385 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Stader](https://api.llama.fi/protocol/stader) | 233.251 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Fluid Lending](https://api.llama.fi/protocol/fluid-lending) | 231.542 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Fluid Lite](https://api.llama.fi/protocol/fluid-lite) | 208.926 | ETH borrowing loops | 02 Oct 2026, 00:00 | observed |
| [Liquity V1](https://api.llama.fi/protocol/liquity-v1) | 195.871 | CDP collateral | 02 Oct 2026, 00:00 | observed |
| [Symbiotic](https://api.llama.fi/protocol/symbiotic) | 165.706 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Frax Ether](https://api.llama.fi/protocol/frax-ether) | 137.015 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Renzo](https://api.llama.fi/protocol/renzo) | 117.732 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Liquity V2](https://api.llama.fi/protocol/liquity-v2) | 107.835 | CDP collateral | 02 Oct 2026, 00:00 | observed |
| [Euler V2](https://api.llama.fi/protocol/euler-v2) | 100.026 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Fluid DEX](https://api.llama.fi/protocol/fluid-dex) | 96.106 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [crvUSD](https://api.llama.fi/protocol/crvusd) | 79.608 | CDP collateral | 02 Oct 2026, 00:00 | observed |
| [Origin Ether](https://api.llama.fi/protocol/origin-ether) | 64.586 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Aerodrome V1](https://api.llama.fi/protocol/aerodrome-v1) | 62.542 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Dolomite](https://api.llama.fi/protocol/dolomite) | 60.028 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Compound V2](https://api.llama.fi/protocol/compound-v2) | 58.579 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [GMX V2 Perps](https://api.llama.fi/protocol/gmx-v2-perps) | 56.520 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Treehouse Protocol](https://api.llama.fi/protocol/treehouse-protocol) | 56.010 | ETH borrowing loops | 02 Oct 2026, 00:00 | observed |
| [Fusion by IPOR](https://api.llama.fi/protocol/fusion-by-ipor) | 54.942 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Aerodrome Slipstream](https://api.llama.fi/protocol/aerodrome-slipstream) | 50.137 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Venus Core Pool](https://api.llama.fi/protocol/venus-core-pool) | 46.227 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Yearn Finance](https://api.llama.fi/protocol/yearn-finance) | 42.852 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Lagoon](https://api.llama.fi/protocol/lagoon) | 42.849 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Upshift](https://api.llama.fi/protocol/upshift) | 42.306 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Swell Liquid Staking](https://api.llama.fi/protocol/swell-liquid-staking) | 32.948 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Alchemix V3](https://api.llama.fi/protocol/alchemix-v3) | 32.925 | CDP collateral | 02 Oct 2026, 00:00 | observed |
| [Swell Liquid Restaking](https://api.llama.fi/protocol/swell-liquid-restaking) | 32.332 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Puffer Stake](https://api.llama.fi/protocol/puffer-stake) | 31.366 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Yield Basis](https://api.llama.fi/protocol/yield-basis) | 28.468 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [AUTOfinance](https://api.llama.fi/protocol/autofinance) | 28.193 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Bedrock uniETH](https://api.llama.fi/protocol/bedrock-unieth) | 27.767 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Vesper](https://api.llama.fi/protocol/vesper) | 23.603 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Pendle V2](https://api.llama.fi/protocol/pendle-v2) | 22.981 | Fixed yield | 02 Oct 2026, 00:00 | observed |
| [Ankr](https://api.llama.fi/protocol/ankr) | 22.630 | Staking / restaking | 02 Oct 2026, 00:00 | observed |
| [Uniswap V2](https://api.llama.fi/protocol/uniswap-v2) | 18.011 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [PancakeSwap AMM](https://api.llama.fi/protocol/pancakeswap-amm) | 15.943 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [SushiSwap V3](https://api.llama.fi/protocol/sushiswap-v3) | 15.024 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Tydro](https://api.llama.fi/protocol/tydro) | 14.200 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Harvest Finance](https://api.llama.fi/protocol/harvest-finance) | 14.187 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Origin ARM](https://api.llama.fi/protocol/origin-arm) | 14.153 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [YO Protocol](https://api.llama.fi/protocol/yo-protocol) | 13.406 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Reserve Protocol](https://api.llama.fi/protocol/reserve-protocol) | 12.204 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Lista Lending](https://api.llama.fi/protocol/lista-lending) | 10.091 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [VVS Standard](https://api.llama.fi/protocol/vvs-standard) | 10.057 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Frankencoin](https://api.llama.fi/protocol/frankencoin) | 8.638 | CDP collateral | 02 Oct 2026, 00:00 | observed |
| [Beefy](https://api.llama.fi/protocol/beefy) | 8.619 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Balancer V3](https://api.llama.fi/protocol/balancer-v3) | 7.621 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [CIAN Yield Layer](https://api.llama.fi/protocol/cian-yield-layer) | 6.718 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Camelot V2](https://api.llama.fi/protocol/camelot-v2) | 6.656 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Native Credit Pool](https://api.llama.fi/protocol/native-credit-pool) | 6.587 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Across](https://api.llama.fi/protocol/across) | 6.335 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Gearbox](https://api.llama.fi/protocol/gearbox) | 5.123 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Ekubo](https://api.llama.fi/protocol/ekubo) | 4.904 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Velodrome V3](https://api.llama.fi/protocol/velodrome-v3) | 4.749 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Velodrome V2](https://api.llama.fi/protocol/velodrome-v2) | 4.316 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Quickswap Dex](https://api.llama.fi/protocol/quickswap-dex) | 4.226 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Bancor V3](https://api.llama.fi/protocol/bancor-v3) | 3.922 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Fluxion Network](https://api.llama.fi/protocol/fluxion-network) | 2.209 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Exactly](https://api.llama.fi/protocol/exactly) | 1.391 | Lending markets | 02 Oct 2026, 00:00 | observed |
| [Stake DAO Yield](https://api.llama.fi/protocol/stake-dao-yield) | 0.604 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Spectra V2](https://api.llama.fi/protocol/spectra-v2) | 0.256 | Fixed yield | 02 Oct 2026, 00:00 | observed |
| [Convex Finance](https://api.llama.fi/protocol/convex-finance) | 0.000 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Spark Savings](https://api.llama.fi/protocol/spark-savings) | 0.000 | Liquidity / farming / other vaults | 02 Oct 2026, 00:00 | observed |
| [Balancer V2](https://api.llama.fi/protocol/balancer-v2) | Not measured | Liquidity / farming / other vaults | No usable observation | missing |
| [SushiSwap](https://api.llama.fi/protocol/sushiswap) | Not measured | Liquidity / farming / other vaults | No usable observation | missing |
| [Uniswap V3](https://api.llama.fi/protocol/uniswap-v3) | Not measured | Liquidity / farming / other vaults | No usable observation | missing |
| [Uniswap V4](https://api.llama.fi/protocol/uniswap-v4) | Not measured | Liquidity / farming / other vaults | No usable observation | missing |

[Market findings and accounting method](MARKET-STRUCTURE.md) · [Corrected exposure ledger](../../../data/eth/research_market_chapter.json) · [Protocol CSV](../../../data/eth/market_panel_protocols.csv)

## Comparable ETH share-price returns

The return table compares 365-day and 730-day windows ending at T. It uses published share prices and verified receipt conversions. External rewards, withdrawal fees and market discounts are excluded, so these are book returns rather than measured withdrawal proceeds.

| Product / benchmark | 365 days | 730 days | 730-day return, annualized |
|---|---:|---:|---:|
| Liquid ETH | 3.8700% | 6.8501% | 3.3683% |
| stETH/wstETH benchmark | 2.4785% | 5.4875% | 2.7071% |
| weETH benchmark | 2.4830% | 5.2947% | 2.6132% |
| Fluid Lite ETH | 3.5096% | 8.8243% | 4.3189% |
| Treehouse tETH | 2.7845% | 6.2761% | 3.0903% |
| CIAN rsETH | 2.2455% | 1.0854% | 0.5413% |

Treehouse's internal accounting unit was verified as wstETH-denominated throughout the measured history; it does not represent physical inventory. CIAN's ETH conversion uses a verified historical oracle and does not measure market discounts or product-specific bridge recovery. Concrete's flat share price is not treated as zero investor income: private payouts and the shorter history remain unresolved.

Sources under data/eth: chain_screen.json for discovery, research_market_chapter.json and market_panel_protocols.csv for corrected exposure, etherfi_staking_comparison.json and vault_history_comparison.json for returns. Original adapter responses and token exclusions remain in the evidence ledger.
