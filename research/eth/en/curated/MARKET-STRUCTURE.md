# ETH market: every product, counted once

Financial snapshot: **2 October 2026**. Month-ends October 2024 to September 2026.

| Category | ETH, 2 Oct 2026 | Share | Oct 2024 | Switch |
| --- | --- | --- | --- | --- |
| Staking | 11,896,566 | 74.7% | 9,589,367 | on |
| Restaking | 416,743 | 2.6% | 2,513,366 | on |
| Leveraged staking | 2,885,012 | 18.1% | 2,247,038 | on |
| Carry | 171,649 | 1.1% | 0 | on |
| Fixed yield | 9,203 | 0.1% | 307,465 | on |
| Basis | 372 | 0.0% | 25,423 | on |
| Options | 1,664 | 0.0% | 4,786 | on |
| Credit | 26,738 | 0.2% | 5,116 | on |
| Farming and pools | 528,228 | 3.3% | 1,583,227 | on |
| Money markets | 3,231,215 | off | 2,743,062 | off |
| CDP collateral | 765,192 | off | 1,637,787 | off |

Each product is counted once, where the ETH is used. Staking and restaking are staked and held, not used anywhere else: staking tokens posted in lending markets (5.48M ETH) or held by other products leave their issuers. Leveraged staking is every loop of staked ETH against borrowed ETH on lending markets, private and product (equity about 313k ETH; month-ends estimated from ETH debt). Carry is only the dollar-loan part of products open for deposits; their loops count as leveraged staking. Money markets (ETH and staking tokens posted outside loops and carry products, mostly collateral for dollar loans by unknown wallets) and CDPs are off by default, as in BTC. Binance's wBETH grew by 2.18M ETH, the largest change on the map; restaking fell from 2.51M ETH (October 2024) as weETH and rsETH moved into lending markets, and farming and pools from 1.58M ETH (October 2024) as points programmes ended. [Method and every netting step](../../../data/eth/netmap/netting_ledger.csv).

## Staking: on-chain, off-chain and the beacon chain

The beacon chain holds **43.81M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: 11.90M ETH staked and held and 0.42M restaked and held; 5.48M ETH of staking tokens sit in lending markets and are counted there (leveraged staking, carry, money markets). About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. The remaining 11.50M ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. [Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).

## Method

Categories follow where the yield comes from, as in the BTC study. Lending markets are split account by account at the snapshot ([lending split](LENDING-SPLIT.md)): loops to leveraged staking, the carry products' dollar loans to carry, the rest to money markets; collateral counts once and lent-out WETH is not added. Restaking platforms count only what no restaking token on the map already counts (estimate). DEX projects without a token breakdown are their ETH pools above $1M, plain-ETH side only; their history covers pools that still exist. Off-chain staking, ETFs, treasuries and the rows left out are listed with reasons on the site (Data, Listed but not counted) and in [coverage](MARKET-COVERAGE.md).

[Map CSV](../../../data/eth/netmap/market_map_current.csv), [month-ends](../../../data/eth/netmap/market_map_history_monthly.csv), [netting ledger](../../../data/eth/netmap/netting_ledger.csv), [product notes](../../../data/eth/netmap/product_notes.csv).
