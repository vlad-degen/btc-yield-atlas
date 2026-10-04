# Таблицы охвата рынка ETH yield

Дата: 3 октября 2026. T: 2026-10-02T23:59:59+00:00.

Таблица сетей — current discovery feed после T. Это сумма полных TVL выбранных пулов, включая не-ETH стороны mixed pools, повторные LST deposits и leverage. Она не является ни net market capital, ни доказанной верхней/нижней границей unique ETH.

| Сеть | Пулы-кандидаты | Full-pool TVL, $млн | Пулы ≥$5млн | Углублённый отбор |
|---|---:|---:|---:|---|
| Ethereum | 2472 | 66 462.260 | 184 | да |
| Base | 2121 | 1 319.010 | 32 | да |
| Tron | 1 | 1 288.655 | 1 | да |
| BNB Chain | 46 | 637.576 | 5 | да |
| Arbitrum | 433 | 568.131 | 17 | да |
| Linea | 32 | 208.053 | 1 | да |
| Monad | 20 | 127.920 | 5 | да |
| Optimism | 185 | 96.490 | 4 | да |
| Polygon | 132 | 62.127 | 2 | да |
| Gnosis | 9 | 39.790 | 1 | да |
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

## Датированные наблюдения по протоколам

Последняя доступная token observation не позднее T. В таблице только выбранная ETH-family часть adapter accounting. Она не равна всему protocol TVL, external investor equity или уникальному underlying. Строки с отрицательными balances сохраняют знак. Неизвестные обёртки остаются ограничением охвата. Текущая category — подсказка для классификации, не доказательство исторической стратегии.

| Протокол | ETH-family, $млн | Категория источника сейчас | Дата token observation UTC | Возраст на T, часов |
|---|---:|---|---|---:|
| [Lido](https://api.llama.fi/protocol/lido) | 26 677.058 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Binance staked ETH](https://api.llama.fi/protocol/binance-staked-eth) | 10 081.459 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Aave V3](https://api.llama.fi/protocol/aave-v3) | 9 835.182 | Lending | 2026-10-02 00:00 | 24.00 |
| [EigenCloud](https://api.llama.fi/protocol/eigencloud) | 7 075.345 | Restaking | 2026-10-02 00:00 | 24.00 |
| [ether.fi Stake](https://api.llama.fi/protocol/ether.fi-stake) | 5 188.347 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [SparkLend](https://api.llama.fi/protocol/sparklend) | 4 160.791 | Lending | 2026-10-02 00:00 | 24.00 |
| [Sky Lending](https://api.llama.fi/protocol/sky-lending) | 1 639.333 | CDP | 2026-10-02 00:00 | 24.00 |
| [Morpho Blue](https://api.llama.fi/protocol/morpho-blue) | 1 421.869 | Lending | 2026-10-02 00:00 | 24.00 |
| [Rocket Pool](https://api.llama.fi/protocol/rocket-pool) | 1 409.233 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [JustLend V1](https://api.llama.fi/protocol/justlend-v1) | 1 309.833 | Lending | 2026-10-02 00:00 | 24.00 |
| [Kelp](https://api.llama.fi/protocol/kelp) | 1 130.443 | Liquid Restaking | 2026-10-02 00:00 | 24.00 |
| [StakeWise V3](https://api.llama.fi/protocol/stakewise-v3) | 1 016.917 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Concrete](https://api.llama.fi/protocol/concrete) | 953.047 | Onchain Capital Allocator | 2026-10-02 00:00 | 24.00 |
| [Compound V3](https://api.llama.fi/protocol/compound-v3) | 724.582 | Lending | 2026-10-02 00:00 | 24.00 |
| [mETH Protocol](https://api.llama.fi/protocol/meth-protocol) | 637.236 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Coinbase Wrapped Staked ETH](https://api.llama.fi/protocol/coinbase-wrapped-staked-eth) | 516.968 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [ether.fi Liquid](https://api.llama.fi/protocol/ether.fi-liquid) | 402.665 | Onchain Capital Allocator | 2026-10-02 00:00 | 24.00 |
| [Curve DEX](https://api.llama.fi/protocol/curve-dex) | 269.230 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Aave V4](https://api.llama.fi/protocol/aave-v4) | 240.385 | Lending | 2026-10-02 00:00 | 24.00 |
| [Stader](https://api.llama.fi/protocol/stader) | 233.251 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Fluid Lending](https://api.llama.fi/protocol/fluid-lending) | 231.542 | Lending | 2026-10-02 00:00 | 24.00 |
| [Fluid Lite](https://api.llama.fi/protocol/fluid-lite) | 208.926 | Yield Aggregator | 2026-10-02 00:00 | 24.00 |
| [Liquity V1](https://api.llama.fi/protocol/liquity-v1) | 195.871 | CDP | 2026-10-02 00:00 | 24.00 |
| [Symbiotic](https://api.llama.fi/protocol/symbiotic) | 165.706 | Collateral Markets | 2026-10-02 00:00 | 24.00 |
| [Frax Ether](https://api.llama.fi/protocol/frax-ether) | 137.015 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Renzo](https://api.llama.fi/protocol/renzo) | 117.732 | Liquid Restaking | 2026-10-02 00:00 | 24.00 |
| [Liquity V2](https://api.llama.fi/protocol/liquity-v2) | 107.835 | CDP | 2026-10-02 00:00 | 24.00 |
| [Euler V2](https://api.llama.fi/protocol/euler-v2) | 100.026 | Lending | 2026-10-02 00:00 | 24.00 |
| [Fluid DEX](https://api.llama.fi/protocol/fluid-dex) | 96.106 | Dexs | 2026-10-02 00:00 | 24.00 |
| [crvUSD](https://api.llama.fi/protocol/crvusd) | 79.608 | CDP | 2026-10-02 00:00 | 24.00 |
| [Origin Ether](https://api.llama.fi/protocol/origin-ether) | 64.586 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Aerodrome V1](https://api.llama.fi/protocol/aerodrome-v1) | 62.542 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Dolomite](https://api.llama.fi/protocol/dolomite) | 60.028 | Lending | 2026-10-02 00:00 | 24.00 |
| [Compound V2](https://api.llama.fi/protocol/compound-v2) | 58.579 | Lending | 2026-10-02 00:00 | 24.00 |
| [GMX V2 Perps](https://api.llama.fi/protocol/gmx-v2-perps) | 56.520 | Derivatives | 2026-10-02 00:00 | 24.00 |
| [Treehouse Protocol](https://api.llama.fi/protocol/treehouse-protocol) | 56.010 | DOR | 2026-10-02 00:00 | 24.00 |
| [Fusion by IPOR](https://api.llama.fi/protocol/fusion-by-ipor) | 54.942 | Onchain Capital Allocator | 2026-10-02 00:00 | 24.00 |
| [Aerodrome Slipstream](https://api.llama.fi/protocol/aerodrome-slipstream) | 50.137 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Venus Core Pool](https://api.llama.fi/protocol/venus-core-pool) | 46.227 | Lending | 2026-10-02 00:00 | 24.00 |
| [Yearn Finance](https://api.llama.fi/protocol/yearn-finance) | 42.852 | Yield Aggregator | 2026-10-02 00:00 | 24.00 |
| [Lagoon](https://api.llama.fi/protocol/lagoon) | 42.849 | Onchain Capital Allocator | 2026-10-02 00:00 | 24.00 |
| [Upshift](https://api.llama.fi/protocol/upshift) | 42.306 | Onchain Capital Allocator | 2026-10-02 00:00 | 24.00 |
| [Swell Liquid Staking](https://api.llama.fi/protocol/swell-liquid-staking) | 32.948 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Alchemix V3](https://api.llama.fi/protocol/alchemix-v3) | 32.925 | Synthetics | 2026-10-02 00:00 | 24.00 |
| [Swell Liquid Restaking](https://api.llama.fi/protocol/swell-liquid-restaking) | 32.332 | Liquid Restaking | 2026-10-02 00:00 | 24.00 |
| [Puffer Stake](https://api.llama.fi/protocol/puffer-stake) | 31.366 | Liquid Restaking | 2026-10-02 00:00 | 24.00 |
| [Yield Basis](https://api.llama.fi/protocol/yield-basis) | 28.468 | Leveraged Farming | 2026-10-02 00:00 | 24.00 |
| [AUTOfinance](https://api.llama.fi/protocol/autofinance) | 28.193 | Yield | 2026-10-02 00:00 | 24.00 |
| [Bedrock uniETH](https://api.llama.fi/protocol/bedrock-unieth) | 27.767 | Liquid Restaking | 2026-10-02 00:00 | 24.00 |
| [Vesper](https://api.llama.fi/protocol/vesper) | 23.603 | Yield Aggregator | 2026-10-02 00:00 | 24.00 |
| [Pendle V2](https://api.llama.fi/protocol/pendle-v2) | 22.982 | Yield | 2026-10-02 00:00 | 24.00 |
| [Ankr](https://api.llama.fi/protocol/ankr) | 22.630 | Liquid Staking | 2026-10-02 00:00 | 24.00 |
| [Reserve Protocol](https://api.llama.fi/protocol/reserve-protocol) | 20.472 | Indexes | 2026-10-02 00:00 | 24.00 |
| [Uniswap V2](https://api.llama.fi/protocol/uniswap-v2) | 18.011 | Dexs | 2026-10-02 00:00 | 24.00 |
| [PancakeSwap AMM](https://api.llama.fi/protocol/pancakeswap-amm) | 15.943 | Dexs | 2026-10-02 00:00 | 24.00 |
| [SushiSwap V3](https://api.llama.fi/protocol/sushiswap-v3) | 15.024 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Tydro](https://api.llama.fi/protocol/tydro) | 14.200 | Lending | 2026-10-02 00:00 | 24.00 |
| [Harvest Finance](https://api.llama.fi/protocol/harvest-finance) | 14.187 | Yield Aggregator | 2026-10-02 00:00 | 24.00 |
| [Origin ARM](https://api.llama.fi/protocol/origin-arm) | 14.153 | Yield | 2026-10-02 00:00 | 24.00 |
| [YO Protocol](https://api.llama.fi/protocol/yo-protocol) | 13.406 | Yield Aggregator | 2026-10-02 00:00 | 24.00 |
| [Lista Lending](https://api.llama.fi/protocol/lista-lending) | 10.091 | Lending | 2026-10-02 00:00 | 24.00 |
| [VVS Standard](https://api.llama.fi/protocol/vvs-standard) | 10.057 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Frankencoin](https://api.llama.fi/protocol/frankencoin) | 8.638 | CDP | 2026-10-02 00:00 | 24.00 |
| [Beefy](https://api.llama.fi/protocol/beefy) | 8.619 | Yield Aggregator | 2026-10-02 00:00 | 24.00 |
| [Balancer V3](https://api.llama.fi/protocol/balancer-v3) | 7.621 | Dexs | 2026-10-02 00:00 | 24.00 |
| [CIAN Yield Layer](https://api.llama.fi/protocol/cian-yield-layer) | 6.718 | Yield Aggregator | 2026-10-02 00:00 | 24.00 |
| [Camelot V2](https://api.llama.fi/protocol/camelot-v2) | 6.656 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Native Credit Pool](https://api.llama.fi/protocol/native-credit-pool) | 6.587 | Lending | 2026-10-02 00:00 | 24.00 |
| [Across](https://api.llama.fi/protocol/across) | 6.335 | Cross Chain Bridge | 2026-10-02 00:00 | 24.00 |
| [Gearbox](https://api.llama.fi/protocol/gearbox) | 5.123 | Lending | 2026-10-02 00:00 | 24.00 |
| [Ekubo](https://api.llama.fi/protocol/ekubo) | 4.904 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Velodrome V3](https://api.llama.fi/protocol/velodrome-v3) | 4.749 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Velodrome V2](https://api.llama.fi/protocol/velodrome-v2) | 4.316 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Quickswap Dex](https://api.llama.fi/protocol/quickswap-dex) | 4.226 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Bancor V3](https://api.llama.fi/protocol/bancor-v3) | 3.922 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Fluxion Network](https://api.llama.fi/protocol/fluxion-network) | 2.209 | Dexs | 2026-10-02 00:00 | 24.00 |
| [Exactly](https://api.llama.fi/protocol/exactly) | 1.391 | Lending | 2026-10-02 00:00 | 24.00 |
| [Stake DAO Yield](https://api.llama.fi/protocol/stake-dao-yield) | 0.604 | Yield | 2026-10-02 00:00 | 24.00 |
| [Spectra V2](https://api.llama.fi/protocol/spectra-v2) | 0.256 | Yield | 2026-10-02 00:00 | 24.00 |
| [Convex Finance](https://api.llama.fi/protocol/convex-finance) | 0.000 | Yield | 2026-10-02 00:00 | 24.00 |
| [Ethena USDe](https://api.llama.fi/protocol/ethena-usde) | 0.000 | Basis Trading | 2026-10-02 00:00 | 24.00 |
| [Spark Savings](https://api.llama.fi/protocol/spark-savings) | 0.000 | Yield | 2026-10-02 00:00 | 24.00 |

## Сопоставимый результат в ETH по цене доли

Окна до T: 365 и 730 дней. Доход по published PPS/contract conversion, без внешних rewards, комиссии выхода и market depeg. Это не доказательство реализуемого cash payout.

| Продукт или benchmark | 365 дней | 730 дней | Годовой эквивалент 730 дней |
|---|---:|---:|---:|
| Liquid ETH | 3.8700% | 6.8501% | 3.3683% |
| stETH/wstETH benchmark | 2.4785% | 5.4875% | 2.7071% |
| weETH benchmark | 2.4830% | 5.2947% | 2.6132% |
| Fluid Lite ETH | 3.5096% | 8.8243% | 4.3189% |
| Treehouse tETH | 2.7845% | 6.2761% | 3.0903% |
| CIAN rsETH | 2.2455% | 1.0854% | 0.5413% |

Treehouse: исторически подтверждена wstETH denomination внутренней IAU; она не является физическим запасом wstETH. CIAN: rsETH conversion использует исторически проверенный oracle и не включает рыночный bridge/depeg loss. Concrete не получает нулевой APR из плоского PPS: private distributions и более короткая история остаются неизвестными.

Источники таблиц: `market_summary.json`, `chain_screen.json`, `protocol_eth_observations.json`, `etherfi_staking_comparison.json`, `vault_history_comparison.json`. Все пути данных относительно `data/eth/`.
