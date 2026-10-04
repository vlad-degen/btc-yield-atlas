# ETH website rebuild against the actual Bitcoin Research website

4 October 2026. The final deliverable is an English, presentation-ready research website. This plan governs the page rebuild, rather than another collection of research notes.

## Phase 1: reproduce the reading sequence

Use the original Bitcoin site's linked market dashboard as the contract: headline capital and findings, current category composition, two years of category history, category/product catalogue, carry composition and history, carry economics, product investigation, risks and implications, then sources. The BTC implementation is documented in BTC-SITE-STRUCTURE-SPEC.md. Preserve the original BTC files.

## Phase 2: construct one consistent market ledger

Use captured dated ETH-family token balances, with an explicit whitelist of ETH claims. Exclude Ethereum-prefixed stablecoins and BTC. Assign each protocol to a stable activity category and reconcile every category to its constituent rows. Convert each dated USD observation with its contemporaneous ETH reference. Keep actual token units separate from this market-value ETH equivalent. Preserve missing observations and source age. Show price normalization, coverage changes and common-cohort comparisons. This is a layered exposure market, not unique native ETH or externally deposited equity. Chain totals use ETH-family token exposure, not mixed-pool TVL.

## Phase 3: implement the integrated market exhibit

One category state updates headline totals, nested category/product donut, category shares, monthly stacked history, findings and tables. Provide ETH/USD and Amount/Share controls, current/monthly tables, category drill-down and search across all products. Empty selection, missing observations and small-product tails must behave correctly. Show 24 completed monthly observations, with the current snapshot separately dated. Explain the six categories through what they do, who pays and where products run.

## Phase 4: build the carry category before explaining products

Distinguish ETH collateral with dollar borrowing, ETH-debt staking loops and spot/short basis. Render the wider carry product catalogue, chain, collateral, loan, destination, dated size and evidence. Fetch fixed-block balances for additional products where primary identities are available. Show historical parent NAV separately from historical carry allocation. A current allocation must never be copied backward. Include all products with observations in carry history, including the small tail. Carry mechanics, financing, credit destinations and worked economics follow this category exhibit.

## Phase 5: retain the useful product investigation below the market

Keep detailed product tabs, capital reconciliation, fee chronology, control rights, comparable ETH-denominated returns, financing, borrower samples, risk scenarios and withdrawal costs. Move broad discovery tables, research plans and raw evidence inventories behind supporting details. Main copy should explain findings in readable English, with no long dashes or research-task language.

## Phase 6: verify and package

Check category reconciliation, month coverage, price normalization, excluded non-ETH tokens, current/history dating, chart/table consistency, complete carry tails and source provenance. Run existing financial and website audits, then browser checks for category changes, units/modes, search, tables, responsive layout and product controls. Rebuild both site copies and the shareable archive. Deliver the working local website and the archive, with the scope of any unresolved measurement stated plainly.

Acceptance: a colleague can answer how large the measured ETH yield market is, what categories it contains, how these changed in ETH and USD, which chains and protocols hold exposures, what the carry category contains, and how its economics and investor outcomes differ, directly from the primary page.
