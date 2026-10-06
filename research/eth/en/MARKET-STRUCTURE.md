# ETH market structure and two years of history

Financial snapshot: **2 October 2026**. Monthly window: October 2024 to September 2026.

## A layered market

Staking is the base income source. Receipts move into lending, restaking and managed products; the same underlying ETH can support claims in multiple layers. The protocol panel groups full parent exposure by family. It does not measure unique ETH, investor equity or precise strategy weights. Native validator balances are outside the panel.

| Protocol family | Observed parents at T | ETH-equivalent exposure | Oct 2024 to Sep 2026 change | Chart scope |
| --- | --- | --- | --- | --- |
| Staking / restaking claims | 19 | 20,190,378 | -4.30% | Default |
| Loop-focused vaults | 2 | 97,973 | +7.57% | Default |
| Carry-linked parents | 3 | 511,868 | +57.16% | Default |
| Basis / hedged ETH | 0 | Not measured | Not measured | Default |
| Fixed-yield venues | 2 | 8,593 | -96.74% | Default |
| Liquidity / mixed vaults | 33 | 348,774 | -33.35% | Default |
| Lending infrastructure | 15 | 6,255,733 | +37.94% | Optional financing layer |
| CDP collateral | 6 | 763,342 | -51.17% | Optional financing layer |

## How to interpret history

The stacked bars retain a stable protocol-family mapping through 24 monthly snapshots. A mixed parent's entire book stays in its family. Changes reflect reported claims, conversion, membership and coverage; they are neither historical carry allocations nor external deposit flows. Constant cohort fixes the protocols observed at every date, while current discovery can still omit dead products. ETH equivalents use the dated ETH reference price; dollar values use reported token balances and marks. Missing and stale observations remain absent.

## Carry-linked parents versus product books

Concrete, ether.fi Liquid and YieldBasis form the three carry-linked protocol parents. Their adapter histories use different asset scopes and valuation dates from the eight contract-level product books. The latter include nested Liquity claims, historical carry and a declared arbitrage book. Neither series establishes global carry equity. The five largest examined books are Concrete Delta, Liquid, YieldBasis WETH, Rocksolid and Liquity. [Product status and attribution](CARRY-CATEGORY.md).

## Chains and missing liquidity history

The chain chart reports where adapters place balances, rather than validator geography or every strategy destination. Product chapters identify actual loan and investment chains. Unverified Tron mapped ETH stays excluded. Four major liquidity adapters lack token history at T; the separate 28-pool custody subset does not fill the whole DEX market. [Coverage by mechanism](MARKET-COVERAGE.md).

## Sources

[Reader ledger](../../../data/eth/market_reader_chapter.json), [original captured grouping](../../../data/eth/research_market_chapter.json), [custody and overlap evidence](CAPITAL-INCOME-EXIT.md), [current briefing](BRIEFING.md).
