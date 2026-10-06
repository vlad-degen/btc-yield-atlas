# ETH Yield Research

English research website using BTC Research's eight chapters: Answer, Market, Carry math, Top 5, Other carry, Risks, Playbook and Data. The main reader presents the conclusions; disclosures and linked exhibits retain the detailed evidence.

Public ETH report: https://vlad-degen.github.io/btc-yield-atlas/eth/

BTC reference: https://vlad-degen.github.io/btc-yield-atlas/

Financial snapshot: **2 October 2026, 23:59:59 UTC**. Presentation and definitions revised on 6 October. This revision does not refresh the financial snapshot.

## Read and present

Start with `index.html`. Use `library/BRIEFING.html` for the presentation route, `library/MARKET-COVERAGE.html` for what is measured, and `exhibits.html` for the full investigations. Older library notes retain their own dates and scopes; they are identified as supporting evidence or earlier research notes.

The report distinguishes staking/restaking receipt claims, protocol-family exposure, whole-product book values and verified financing positions. These are overlapping layers, not an additive unique-ETH market total. Native validator balances and several other market families remain outside the aggregate panel.

Eight examined books appear in the carry history, including five products with current traced financing routes, one Closing product, one historical route and one product with unverified carry attribution. The history has 24 monthly stacked bars, ETH/USD views, a small-book zoom and a tooltip showing each product's amount and share. Historical whole-book changes are not reconstructed historical carry allocations or deposit flows.

The six deep product chapters use a common 30-day window ending at the snapshot and the same stETH benchmark. Whole-book returns are separate from organic carry profit. Three traced financed lots have explicit investment income, funding cost and measured results; they do not establish complete product P&L.

The coverage matrix distinguishes ten significant mechanism families. The discovery screen resolves 299 material ETH-keyword pool candidates across 86 projects, with 287 parent joins. This is a discovery disposition screen, not 299 individually reconstructed strategies or an exhaustive global census.

The four main answers and product conclusions have a fixed scope. Market filters affect the market panels and exports. The Briefing, status table, headline definitions and common-window returns are generated from the same canonical dataset, `data/report_contract.json`.

## Local preview and offline handoff

From the full project root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/eth/index.html. This address works only on the presenting machine.

The main HTML embeds its CSS, JavaScript and dataset. Keep the accompanying folders for article links and downloads. To use the portable ZIP, extract the entire archive and open `eth/index.html`. The root `index.html` is the unchanged BTC reference. Optional Google Fonts have system fallbacks. The portable archive stays local and is excluded from public Git publication.

## Build and verify

In the full research checkout:

```sh
python3 tools/eth/rebuild.py
python3 tools/eth/report_contract_verify.py
python3 tools/eth/package_site.py
```

Website source: `tools/eth/site/`. Analytical inputs: `data/eth/`. Research articles: `research/eth/en/`. Output: `eth/`, mirrored to `site/eth/`. Rebuild requires the original captured-response collection; the public website is a presentation, not the full working repository.

The checks verify source integrity, arithmetic, matched returns, financial definitions, exports, navigation and interface behavior. They do not certify global market completeness, private backing or complete carry profitability. The public ETH edition is confined to `/eth/`. Original BTC files remain unchanged.
