# ETH market: every product, counted once

Financial snapshot: **2 October 2026**. Month-ends October 2024 to September 2026.

| Category | ETH, 2 Oct 2026 | Share | Oct 2024 | Switch |
| --- | --- | --- | --- | --- |
| Staking | 15,016,520 | 81.0% | 12,463,594 | on |
| Restaking | 2,427,324 | 13.1% | 4,173,272 | on |
| Leveraged staking | 97,144 | 0.5% | 268,007 | on |
| Carry | 304,716 | 1.6% | 0 | on |
| Fixed yield | 9,315 | 0.1% | 307,484 | on |
| Basis | 372 | 0.0% | 25,423 | on |
| Options | 1,664 | 0.0% | 4,786 | on |
| Credit | 24,279 | 0.1% | 2,496 | on |
| Farming and pools | 661,258 | 3.6% | 1,918,811 | on |
| Money markets | 786,904 | off | 809,351 | off |
| CDP collateral | 657,327 | off | 1,277,081 | off |

Each product is counted once: a staking token held by another product leaves its issuer's row. Money markets count only idle plain WETH and are off by default, because lent ETH is staked again by its borrowers. Binance's wBETH grew by 2.19M ETH, the largest change on the map; restaking fell from 4.67M ETH (July 2025) and farming and pools from 2.09M (February 2025) as points programmes ended. [Method and every netting step](../../../data/eth/netmap/netting_ledger.csv).

Categories follow where the yield comes from, as in the BTC study. Restaking platforms count only what no restaking token on the map already counts (estimate). DEX projects without a token breakdown are their ETH pools above $1M, plain-ETH side only; their history covers pools that still exist. Off-chain staking, ETFs, treasuries and the rows left out are listed with reasons on the site (Data, Listed but not counted).

[Map CSV](../../../data/eth/netmap/market_map_current.csv), [month-ends](../../../data/eth/netmap/market_map_history_monthly.csv), [netting ledger](../../../data/eth/netmap/netting_ledger.csv), [product notes](../../../data/eth/netmap/product_notes.csv).


## Native stake: measured backing, not another wrapper

The archived consensus state at T has **43,805,557.723 actual active ETH**, **43,739,959 effective active ETH** and **874,362 active validators**. Actual balance and effective stake answer different questions. The active set includes 22,432 exiting validators. These balances are measured directly from validator objects, including compounding validators; they are not validator count multiplied by 32. Receipt claims are a separate, overlapping layer.

The archived slot is **15346798**, state root `0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282`. The public provider marks the response finalized and execution optimistic. The header state root agrees with the saved header; we do not claim an independent state-root recomputation from the validator JSON. Five successful monthly state reads cover May to September 2026. Earlier headers exist but their complete states are pruned at the tested public endpoints. Those missing balances remain absent.

[Archived state endpoint](http://testing.mainnet.beacon-api.nimbus.team/eth/v1/beacon/states/15346798/validators?status=active_ongoing,active_exiting,active_slashed), [monthly observations](../../../data/eth/native-staking-observations.csv), [normalised reconstruction and receipt hashes](../../../data/eth/finalization_reconstruction.json).
