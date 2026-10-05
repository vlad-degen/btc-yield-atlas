# BTC reader parity: audit and completed implementation

Reference: the actual BTC website, not its source notebook. Reviewed 6 October 2026. ETH financial observations remain fixed at 2 October, 23:59:59 UTC.

## Plan and completion

1. Compare the eight visible BTC chapters, their questions, default disclosures and product chapter order. Completed against the rendered website.
2. Retain one reading sequence: Answer → Market → Carry math → Top 5 → Other carry → Risks → Playbook → Data. Completed.
3. Reduce the visible Market to composition, category history and category participants. Place chain detail, counting rules and cohort checks in contextual disclosures. Completed.
4. Reduce Carry math to the worked balance sheet, funding/investment comparison, lending and rate model, and calculator. Preserve assumptions and source ledgers. Completed.
5. Keep carry development inside Top 5, with 24 month-end bars, product-level hover, ETH/USD, small-book zoom, table, matched CSVs and three dated development phases. Completed.
6. Follow BTC's product questions: money flow, control, payers, debt, capital and returns, holders, events and exit. Show eight or nine operational steps; keep large ledgers behind contextual links. Completed for six examined products, with the five largest in the main tabs.
7. Re-audit ETH carry coverage and reconcile classification changes. Completed: 299 material ETH-keyword DefiLlama pools across 86 projects have explicit dispositions; YieldBasis WETH is measured and reclassified; two ZenSats routes are documented without invented T capital.
8. Check desktop and narrow phones, browser errors, financial conservation, exports, sources and BTC preservation. Completed locally. Public deployment verification is recorded separately after publication.

## Editorial choices

The primary page answers the BTC report's same questions. ETH mechanisms require ETH-specific findings: staking conversion, ETH-debt loops, dollar-financed liquidity and dollar debt are distinct. The structure matches; copying BTC conclusions would be misleading.

A single wider carry census replaces multiple competing product tables. Unknown allocator books, detailed borrower tracing, discovery logs, source inventories, common-cohort tables and nested financing evidence sit in disclosures or the full exhibits. Full research remains available through a grouped source library.

Two observed capital lenses remain clear: adapter parent exposure in Market and whole-product claims in carry history. They use different marks and overlap; neither is global unique carry equity. YieldBasis moves between existing categories without increasing total market capital. Direct LT holders include the gauge, not its beneficial investors.

## Rendered comparison

| Chapter | BTC visible words | ETH visible words | BTC panels | ETH panels |
|---|---:|---:|---:|---:|
| top | 185 | 181 | 1 | 1 |
| map | 875 | 795 | 3 | 3 |
| how | 677 | 708 | 4 | 4 |
| top5 | 1930 | 1732 | 11 | 9 |
| market | 1222 | 444 | 1 | 1 |
| risks | 300 | 316 | 1 | 1 |
| do | 559 | 532 | 5 | 5 |
| data | 37 | 45 | 0 | 0 |

At 1440 px, the selected ETH reader has 4,753 visible words versus 5,785 in BTC. Measured section height is 17,908 px versus 17,540 px. Height depends on the selected product, filters, text and chart shape; it is a diagnostic, not a pixel-identical claim. The ETH default includes staking receipts; the recorded comparison preserves the user’s selected five categories.

## Publication completed

Published through [PR 5](https://github.com/vlad-degen/btc-yield-atlas/pull/5), website commit `5d15b8a`, merge `86f51d2`. The matching Pages workflow completed successfully. All 24 public HTML, evidence and CSV responses match the verified local bytes; the BTC root matches its original checksum. All 345 non-ETH Git blobs are unchanged. Public browser verification confirms the eight-book hover, YieldBasis’s eight operational steps and holder scope, and no JavaScript errors. [Verification ledger](../../data/eth/publication_verification_btc_parity.json), [public browser check](../../data/eth/public_browser_parity.json).
