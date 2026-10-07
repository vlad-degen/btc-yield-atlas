# ETH market structure and two years of history

Financial snapshot: **2 October 2026**. Monthly window: October 2024 to September 2026.

## A layered market

Staking is the base income source. Receipts move into lending, restaking and managed products; the same underlying ETH can support claims in multiple layers. The protocol panel groups full parent exposure by family. It does not measure unique ETH, investor equity or precise strategy weights. Native validator balances are outside the panel.

| Protocol family | Observed parents at T | ETH-equivalent exposure | Oct 2024 to Sep 2026 change | Chart scope |
| --- | --- | --- | --- | --- |
| Staking | 23 | 14,786,203 | +20.83% | Default |
| Restaking | 15 | 2,428,297 | -41.84% | Default |
| Leveraged staking | 6 | 97,015 | -20.44% | Default |
| Carry | 12 | 302,276 | +104.88% | Default |
| Fixed yield | 5 | 9,315 | -96.95% | Default |
| Basis | 3 | 372 | -98.54% | Default |
| Options | 8 | 3,182 | -41.78% | Default |
| Credit | 2 | 24,279 | +879.49% | Default |
| Farming and pools | 101 | 686,955 | -64.26% | Default |
| Money markets | 55 | 764,223 | -4.09% | Optional financing layer |
| CDP collateral | 10 | 657,327 | -48.40% | Optional financing layer |

## How to interpret history

The stacked bars retain a stable protocol-family mapping through 24 monthly snapshots. A mixed parent's entire book stays in its family. Changes reflect reported claims, conversion, membership and coverage; they are neither historical carry allocations nor external deposit flows. Constant cohort fixes the protocols observed at every date, while current discovery can still omit dead products. ETH equivalents use the dated ETH reference price; dollar values use reported token balances and marks. Missing and stale observations remain absent.

## Carry-linked parents versus product books

Concrete, ether.fi Liquid and YieldBasis form the three carry-linked protocol parents. Their adapter histories use different asset scopes and valuation dates from the eight contract-level product books. The latter include nested Liquity claims, historical carry and a declared arbitrage book. Neither series establishes global carry equity. The five largest examined books are Concrete Delta, Liquid, YieldBasis WETH, Rocksolid and Liquity. [Product status and attribution](CARRY-CATEGORY.md).

## Chains and missing liquidity history

The chain chart reports where adapters place balances, rather than validator geography or every strategy destination. Product chapters identify actual loan and investment chains. Unverified Tron mapped ETH stays excluded. Four major liquidity adapters lack token history at T; the separate 28-pool custody subset does not fill the whole DEX market. [Coverage by mechanism](MARKET-COVERAGE.md).

## Sources

[Reader ledger](../../../data/eth/market_reader_chapter.json), [original captured grouping](../../../data/eth/research_market_chapter.json), [custody and overlap evidence](CAPITAL-INCOME-EXIT.md), [current briefing](BRIEFING.md).


## Native stake: measured backing, not another wrapper

The archived consensus state at T has **43,805,557.723 actual active ETH**, **43,739,959 effective active ETH** and **874,362 active validators**. Actual balance and effective stake answer different questions. The active set includes 22,432 exiting validators. These balances are measured directly from validator objects, including compounding validators; they are not validator count multiplied by 32. Receipt claims are a separate, overlapping layer.

The archived slot is **15346798**, state root `0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282`. The public provider marks the response finalized and execution optimistic. The header state root agrees with the saved header; we do not claim an independent state-root recomputation from the validator JSON. Five successful monthly state reads cover May to September 2026. Earlier headers exist but their complete states are pruned at the tested public endpoints. Those missing balances remain absent.

[Archived state endpoint](http://testing.mainnet.beacon-api.nimbus.team/eth/v1/beacon/states/15346798/validators?status=active_ongoing,active_exiting,active_slashed), [monthly observations](../../../data/eth/native-staking-observations.csv), [normalised reconstruction and receipt hashes](../../../data/eth/finalization_reconstruction.json).
