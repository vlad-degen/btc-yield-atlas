# ETH market: every product, counted once

Financial snapshot: **2 October 2026**. Month-ends October 2024 to September 2026.

| Category | ETH, 2 Oct 2026 | Share | Oct 2024 | Switch |
| --- | --- | --- | --- | --- |
| Staking | 15,016,520 | 81.0% | 12,463,594 | on |
| Restaking | 2,427,324 | 13.1% | 4,173,272 | on |
| Leveraged staking | 97,144 | 0.5% | 268,007 | on |
| Carry | 305,908 | 1.6% | 0 | on |
| Fixed yield | 9,315 | 0.1% | 307,484 | on |
| Basis | 372 | 0.0% | 25,423 | on |
| Options | 1,664 | 0.0% | 4,786 | on |
| Credit | 24,279 | 0.1% | 2,496 | on |
| Farming and pools | 660,066 | 3.6% | 1,918,811 | on |
| Money markets | 786,904 | off | 809,351 | off |
| CDP collateral | 657,327 | off | 1,277,081 | off |

Each product is counted once: a staking token held by another product leaves its issuer's row. Money markets count only idle plain WETH and are off by default, because lent ETH is staked again by its borrowers. Binance's wBETH grew by 2.19M ETH, the largest change on the map; restaking fell from 4.67M ETH (July 2025) and farming and pools from 1.92M ETH (October 2024) as points programmes ended. [Method and every netting step](../../../data/eth/netmap/netting_ledger.csv).

## Staking: on-chain, off-chain and the beacon chain

The beacon chain holds **43.81M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: 15.02M ETH of staking and 2.43M ETH of restaking, after removing staking tokens held by other products. About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. The remaining 11.96M ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. [Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).

## Method

Categories follow where the yield comes from, as in the BTC study. Restaking platforms count only what no restaking token on the map already counts (estimate). DEX projects without a token breakdown are their ETH pools above $1M, plain-ETH side only; their history covers pools that still exist. Off-chain staking, ETFs, treasuries and the rows left out are listed with reasons on the site (Data, Listed but not counted) and in [coverage](MARKET-COVERAGE.md).

[Map CSV](../../../data/eth/netmap/market_map_current.csv), [month-ends](../../../data/eth/netmap/market_map_history_monthly.csv), [netting ledger](../../../data/eth/netmap/netting_ledger.csv), [product notes](../../../data/eth/netmap/product_notes.csv).
