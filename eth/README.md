# ETH Yield Research

An English research website using the visual system and reading structure of the original BTC Yield Atlas. Start with `index.html`; use `exhibits.html` for the complete interactive investigations. Detailed mechanics, product dossiers, analytical reports and source records are linked throughout.

## Open the website

Public website: https://vlad-degen.github.io/btc-yield-atlas/eth/

Original BTC Research: https://vlad-degen.github.io/btc-yield-atlas/

Local preview: http://127.0.0.1:8765/eth/index.html

To start the preview from the project root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

The main HTML also opens directly from disk: CSS, JavaScript and the research dataset are embedded. Keep the accompanying folders beside it for article navigation and downloads. Optional Google Fonts have system fallbacks. The ZIP includes the BTC reference page, so its navigation link remains usable after extraction.

## Present to colleagues

This edition is ready for an internal presentation of the measured market and product findings. It does not claim an exhaustive global product census. Open `library/BRIEFING.html` for the 15-minute route and five likely questions, or `qa/colleague-readiness.md` for the review verdict and remaining evidence limits.

To share the portable package, extract the entire ZIP and open **eth/index.html**. The root index.html is the BTC reference. The localhost address works only on the presenting machine.

## Contents

- Eight chapters matching the supplied Bitcoin Research structure: Answer, Market, Carry math, Top 5, Other carry, Risks, Playbook and Data.
- 5,688 discovered ETH-family pools across 57 chains, with search, category filters, sorting and pagination. The reader ledger has 84 protocol rows and 80 current observations; the original 85-row source ledger is preserved, eight strategy groups and 24 monthly points. The measured market is overlapping ETH-family exposure; missing and stale observations remain explicit.
- Linked market category switches, a nested category/product donut with a grouped tail, monthly stacked columns, ETH/USD and Amount/Share views, a full-window fixed cohort, endpoint common-cohort comparison and category-change tables. Chain views use selected ETH token balances rather than full mixed-pool TVL.
- A 14-product carry census, seven products with published carry evidence, and an exported 192-row monthly product grid. Monthly columns show the large hybrid parents; Rocksolid and four smaller carry products have separate panels and ETH/USD views. Rocksolid’s nested Liquity claim is not added as independent capital. Historical strategy allocations remain unverified where null.
- A fixed-block RLUSD worked loan ledger, 22 dollar borrowing markets, seven verified rate-model curves, six investment destinations, a seven-input carry calculator and four presets. Playbook tables cover economics, reward payers, operating rules and partner criteria.
- Nine supporting mechanics and three additional interactive models: ETH staking loops, ETH-collateral dollar carry and spot/short basis. Borrowing, management, performance and hedge costs are explicit inputs. Worked cash-flow examples update with those inputs.
- Five ranked carry-product chapters (Concrete Delta, Liquid ETH, Rocksolid, Liquity and Royco), a side-by-side comparison and reconciled snapshot share-holder distributions. Supporting ETH-loop cases remain available. The library has 12 detailed dossiers and 46 articles in total.
- Six comparable ETH book-wealth series, selectable chart/table views and 30/90/365/730-day return windows. Liquid ETH has a separate 24-month NAV and monthly-return panel.
- Five fixed-block WETH lending-market balance sheets, liquidation stresses, dollar carry credit destinations, a dependency map and 25 source-backed claims.
- A team briefing, product-selection rationale, primary-source fee/control/exit review and explicit comparison with the BTC study.
- Liquid ETH's 24-month capital reconciliation, Ethereum fee changes and claim payments, selected fixed-block permissions, a borrower sample and single-exit-fee return illustrations.
- Ordinary CSV files for all 256 market selections in both cohort modes, the borrower table, selected wealth series, Liquid ETH and each selected protocol; the complete pool catalogue is downloadable. Arbitrary filtered pool results can be viewed and copied as CSV. Null values stay blank.
- Light/dark themes, keyboard-accessible tabs and chart inspection, responsive chart labels, mobile layouts and print support. Archived loan-rate curves separate dollar borrowing from the ETH-debt benchmark; the Closed tab distinguishes verified deprecation from unverified failure claims.

## Final capital, income and exit exhibits

- Fixed-block custody and repeated receipt ownership, including a 457,182 ETH examined native/WETH custody floor and a separate finalized withdrawal queue. The floor can contain idle reserve cash and is not global earning capital.
- Three destination cash-flow ledgers, six borrowing ledgers, paid reward receipts and a 56.29-day matched window. Claim growth, financing cost, incentives, own-credit overlap and whole-share returns are separated.
- Public backing reconstruction for five products, read-only 1/10/30% exit-demand scenarios, historical cash transfers and deployed control/state verification.
- A new findings article, full JSON/CSV downloads, evidence hashes and integrated consistency checks.

Open library/CAPITAL-INCOME-EXIT.html for these results. Public records do not establish global unique earning capital, a complete product carry P&L or fully allocated private backing. Those boundaries are stated beside the measured answer.

## Broader market and financing investigation

The new chapters add 60 Aave/Spark dollar reserves on 12 chains, 320 archived annual-rate observations, 131 additional Compound/Euler/Fluid market rows and complete selected fixed-T views for 350 ETH-collateral dollar borrowers. Reserve debt spans all collateral types; the 76.703 million Fluid subtotal is nominal dollar-token debt across 31 simple ETH-only collateral pairs.

Nine carry mechanisms distinguish documented design, historical use and actual T positions. Reservoir and TAU have independently read historical nested loans. Three traced borrower lifecycles separate investment income, debt interest, residual liabilities and confidential onward transfers. The largest Aave/Spark addresses have separate pool and unique-address rankings; seven cash loans and 19 CoW trades establish sampled refinancing and conversion routes. Loan proceeds are not automatically yield investment.

A 25-case strategy/product atlas is supported by additional fixed-T capital, fee, withdrawal and funded-history measurements for osETH, mETH, cmETH, Yearn WETH, autoETH and YieldBasis WETH. Four additional products have matched 732-day stETH book benchmarks. Yearn’s actual Spark loan, YieldBasis crvUSD debt and autoETH sized exit constraints are measured separately. An hgETH loan-book reconstruction adds a seventh material contract case. Product books and wrappers overlap; none of these values is added as new unique market capital.

Start with library/MARKET-COVERAGE.html for the mechanism map and remaining public measurement gaps, library/CARRY-LIFECYCLES.html for actual financed outcomes, and library/PRODUCT-FINANCIAL-HISTORY.html for the additional financial histories. The expanded raw-response collections are included in the package alongside derived datasets and matching verification.

## Dates and accounting boundaries

Snapshot T: **2 October 2026, 23:59:59 UTC**. Financial sources were captured for the 3 October research edition. Primary product documentation and English presentation were reviewed on 4 October. New permission, custody, income and exit measurements use the original historical Ethereum block, with receipts collected on 4 October. Additional completed-month carry balances use archive blocks and dated Chainlink marks. Their requests and responses are included in carry_category_candidates.json. Current documentation, UI/feed observations and daily API measurements carry separate time labels; this review does not refresh the financial snapshot.

The integrated ledger measures signed, layered ETH-family exposure, normalized by an adapter-date ETH reference. A global unique-underlying ETH total and verified external-investor equity total remain unresolved. Liquidity is incomplete, including four major missing aggregate histories and possible omitted LP/wrapper tokens. Full mixed-pool TVL, nested claims and published book values are not added into a net capital total. Book marks are distinguished from independently verified backing and executable withdrawal value. See the research status and methodology pages for the remaining evidence gaps.

The ZIP contains the presentation and evidence handoff. The rebuild commands below require the full project checkout, including the original financial-response collection.

## Build and verify

```sh
python3 tools/eth/market_netting_build.py
python3 tools/eth/market_netting_validate.py
python3 tools/eth/carry_attribution_build.py
python3 tools/eth/carry_attribution_recycling.py
python3 tools/eth/carry_attribution_organic.py
python3 tools/eth/carry_attribution_tranches.py
python3 tools/eth/carry_attribution_close.py
python3 tools/eth/backing_exit_build.py
python3 tools/eth/basis_closure_build.py
python3 tools/eth/build_product_chapters.py
python3 tools/eth/closure_reports.py
python3 tools/eth/carry_borrow_history.py
python3 tools/eth/carry_borrow_history.py --verify
python3 tools/eth/carry_economics_build.py
python3 tools/eth/carry_economics_verify.py
python3 tools/eth/presentation_analysis.py
python3 tools/eth/market_data_probe.py
python3 tools/eth/site.py
python3 tools/eth/site_audit.py
python3 tools/eth/market_audit.py
python3 tools/eth/strict_audit.py
python3 tools/eth/audit.py
python3 tools/eth/research_closure_audit.py
```

Complete offline rebuild of derived research outputs and the website:

```sh
python3 tools/eth/rebuild.py
```

Website source: `tools/eth/site/`. Analytical inputs: `data/eth/`. Original research: `research/eth/`. English article sources: `research/eth/en/`. Build: `eth/`; mirrored delivery: `site/eth/`.

Reviewed English articles are canonical. The translation utility seeds missing English files and preserves subsequent edits. Its explicit `--refresh-translations` option replaces the initial translated reports and should only be used when deliberately restarting that editorial work. `RETURN-DRIVERS.md` is generated from the frozen calculation inputs. New public permission responses and their request/hash journal are retained separately in `raw/eth/presentation-review/`.

The archive contains the English presentation, derived evidence, public historical-permission responses, the new financing captures, monthly loan-rate captures the original 203-file product evidence collection, and the new custody, historical-income and 838-file exit/backing captures. Original BTC working notes retain their source language. The full original raw financial-response collection remains in the project. The captured third-party application bundle in `carry_variants_expansion_follow.json` also stays local; it is not required to read or use the website.

All 384 original BTC files are preserved. Automated checks verify evidence integrity, arithmetic and site consistency; browser QA verifies interaction and layout. These checks do not establish a complete financial audit of the entire market. The ETH edition is published as a separate `/eth/` path on the existing GitHub Pages site. The original BTC pages are preserved byte for byte. The portable ZIP stays local and is excluded from Git because it exceeds GitHub’s individual-file limit.
