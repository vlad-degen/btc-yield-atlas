# ETH market: every product, counted once

Financial snapshot: **2 October 2026**. Month-ends October 2024 to September 2026.

| Category | ETH, 2 Oct 2026 | Share | Oct 2024 | Switch |
| --- | --- | --- | --- | --- |
| Staking | 15,093,012 | 81.6% | 12,579,566 | on |
| Restaking | 2,435,229 | 13.2% | 3,777,013 | on |
| Leveraged staking | 97,793 | 0.5% | 270,032 | on |
| Carry | 305,908 | 1.7% | 0 | on |
| Fixed yield | 9,287 | 0.1% | 307,465 | on |
| Basis | 372 | 0.0% | 25,423 | on |
| Options | 1,664 | 0.0% | 4,786 | on |
| Credit | 26,738 | 0.1% | 5,116 | on |
| Farming and pools | 529,052 | 2.9% | 1,584,333 | on |
| Money markets | 812,124 | off | 837,001 | off |
| CDP collateral | 657,327 | off | 1,277,081 | off |

Each product is counted once: a staking token held by another product leaves its issuer's row. Money markets count plain WETH in lending markets (collateral and supply not lent out) and are off by default, because lent ETH is staked again by its borrowers. Binance's wBETH grew by 2.19M ETH, the largest change on the map; restaking fell from 4.63M ETH (July 2025) and farming and pools from 1.58M ETH (October 2024) as points programmes ended. [Method and every netting step](../../../data/eth/netmap/netting_ledger.csv).

## Staking: on-chain, off-chain and the beacon chain

The beacon chain holds **43.81M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: 15.09M ETH of staking and 2.43M ETH of restaking, after removing staking tokens held by other products. About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. The remaining 11.96M ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. [Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).

## Method

Categories follow where the yield comes from, as in the BTC study. Restaking platforms count only what no restaking token on the map already counts (estimate). DEX projects without a token breakdown are their ETH pools above $1M, plain-ETH side only; their history covers pools that still exist. Off-chain staking, ETFs, treasuries and the rows left out are listed with reasons on the site (Data, Listed but not counted) and in [coverage](MARKET-COVERAGE.md).

[Map CSV](../../../data/eth/netmap/market_map_current.csv), [month-ends](../../../data/eth/netmap/market_map_history_monthly.csv), [netting ledger](../../../data/eth/netmap/netting_ledger.csv), [product notes](../../../data/eth/netmap/product_notes.csv).
