# ETH Yield Research

Public report: https://vlad-degen.github.io/btc-yield-atlas/eth/

Financial snapshot: **2 October 2026, 23:59:59 UTC**. Presentation simplified on 7 October following the reader’s comments. Financial observations are unchanged.

## Reading route

Answer → Market → Top 5 → Other carry → Data. Risks are available in a closed disclosure. Market includes the protocol map, 24 monthly category bars and category/protocol drilldowns. Top 5 includes the 24-month dollar-financing history, the common-window comparison and five detailed project chapters.

The main page omits the duplicate hero note, header date strip, second donut legend, “months in the lead” card, carry-calculation chapter, calculator, standalone financed-lot table, product-launch playbook and responsibilities block. Supporting calculations and research remain in `exhibits.html` and the library.

Charts retain their full hover and keyboard breakdown, filters, tables and CSV downloads. The main carry history measures direct ETH-backed dollar debt in verified product accounts. Its ten-product inventory is separate from whole-vault NAV, nested credit and unique investor capital. The five main projects are Liquid, YieldBasis, Lido, Avant and Liquity, ordered by measured dollar financing.

Protocol claims can overlap. Unknown global unique ETH capital, private-wallet positions and complete carry-sleeve profit remain explicitly unmeasured. Source observations, ownership exclusions, fees, controls, holders, launch history and unwind evidence remain available in the project chapters and supporting articles.

## Local preview

From the full project root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/eth/index.html. The main HTML embeds its CSS, JavaScript and dataset; accompanying folders provide article links and downloads.

## Sources and verification

Website source: `tools/eth/site/`. Frozen analytical inputs: `data/eth/`. Articles: `research/eth/en/`. Output: `eth/`, mirrored to `site/eth/`. The public website contains the reader and linked source ledgers, rather than the full working repository.

The 7 October update reran website integrity, reader structure and history/export checks and reviewed desktop/mobile behavior, risk expansion and carry hovers. It does not refresh the financial snapshot. Publication is confined to `/eth/`; the original BTC report is unchanged.
