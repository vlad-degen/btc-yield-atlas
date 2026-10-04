# ETH market composition and history

The final edition adds [capital, earned income and investor exit evidence](CAPITAL-INCOME-EXIT.md). Its fixed-block custody graph, common-window cash-flow ledgers and receipt-verified payout history extend the original scope of this chapter. Use that exhibit for the completed measured answer and its evidence boundaries.


Financial snapshot: 2 October 2026, 23:59:59 UTC. Monthly window: October 2024 through September 2026. Document review: 4 October 2026.

## How large is the measured market?

The default selection contains **21.158 million ETH equivalents / $57.214 billion**, with 59 fresh protocol observations across six included strategy groups. The reader ledger has 84 selected rows and eight groups; 80 rows are observed at T. The original 85-row capture retains JustLend’s Tron mapped-ETH observation outside the primary counts. Lending and CDP are optional financing layers. Including them raises reported exposure to 28.177 million ETH equivalents / $76.195 billion.

These figures describe overlapping ETH-related claims. An LST issuer, a restaking layer, a lender and a vault can all report claims supported by the same ETH. The total is not unique physical ETH, independently reconciled market equity or external deposits. The switches are a transparent way to inspect those layers.

## Eight strategies, one consistent monthly classification

| Strategy | Observed protocols at T | ETH equivalents at T | Oct 2024 to Sep 2026 change | Default |
|---|---:|---:|---:|---|
| Staking / restaking | 19 | 20,190,378 | -4.30% | Included |
| ETH borrowing loops | 2 | 97,973 | +7.57% | Included |
| USD carry / hybrid parents | 2 | 501,340 | +53.88% | Included |
| Spot / short basis | 0 | Not measured | Not measured | Included; no T observation |
| Fixed yield | 2 | 8,593 | -96.74% | Included |
| Liquidity / farming / other vaults | 34 | 359,301 | -31.32% | Included |
| Lending markets | 15 | 6,255,733 | +37.94% | Optional |
| CDP collateral | 6 | 763,342 | -51.17% | Optional |

The default changing set declines 5.13% in ETH equivalents and 5.03% in dollars between the first and last completed month. This is a change in observed exposure. New claims, receipt conversion, missing coverage and internal movements affect the series; it is not a deposit-flow ledger.

The Constant cohort control retains the 63 protocols observed in all 24 months and at T, then applies the chosen categories. It keeps membership fixed. The common end-point comparison requires observations only at the first and last month and therefore can contain more protocols.

## What each category means

Staking includes issuer and restaking layers. ETH loops contain examined products that borrow ETH to enlarge staked exposure. Dollar carry contains examined hybrid protocol parents, whose total balances also include non-carry assets. Basis holds hedged ETH backing, but no frozen-ledger row is measured at T. Fixed yield measures selected yield-market balances, not all outstanding PT principal. Farming includes trading and bridge liquidity plus managed protocols whose full allocation is unverified. Lending and CDP add optional financing and collateral context.

The catalogue keeps protocol names, selected tokens, mechanism, advertised yield, operator, subtype, baseline, separate ETH/USD peaks and monthly coverage. Search spans included and excluded groups. Operator labels identify the protocol namespace; the product chapters separately verify actual addresses and control.

## Why carry needs a separate book

[The carry census](CARRY-CATEGORY.md) keeps dedicated vaults and mixed parents separate. The Top 5 ranks Concrete Delta, Liquid ETH, Rocksolid, Liquity and Royco by measured whole-product book NAV at T. A published carry design is not proof of a live route at that block. Current sleeve percentages are not applied backward to historical NAV.

## Prices, coverage and chains

The main chart divides adapter-date signed ETH-family USD balances by the contemporaneous ETH reference. Product histories instead use fixed-block receipt conversions and dated oracle prices. They are different conventions. Neither converts a receipt into independently verified executable ETH.

Four major liquidity adapters lack usable token histories: Uniswap V3/V4, Balancer V2 and Sushi. LP positions or wrappers can also be absent from token fields. Missing observations stay missing, while records older than 72 hours are excluded from fresh sums. A later discovery screen provides candidate pools without filling the historical gap with full mixed-pool TVL.

The named-chain ledger retains the long tail and shows the largest ten. Aggregate and chain views differ by $2.580 million after alias reconciliation. Validator location, token circulation and strategy deployment are different geographies.

## Evidence

[Eight-category ledger](../../../data/eth/research_market_chapter.json), [original market panel](../../../data/eth/market_panel.json), [borrower discovery](../../../data/eth/research_borrowers.json).
