# BTC website design parity review

Review date: 4 October 2026.

This is a read-only comparison of the actual BTC website in `index.html` and the ETH template, renderers and styles in `tools/eth/site`. It covers the main exhibits, their defaults, interaction design and reading order. No website code or financial data was changed. Findings refer to the source baseline inspected for this review; work elsewhere in the shared workspace may subsequently resolve them. This is a source audit, not a claim that a browser rendering has passed visual QA.

## Main finding

The ETH page now has the same eight main chapters as BTC. The remaining mismatch is inside the chapters. BTC makes an argument through a small number of distinct exhibits: a current market map, monthly stacked bars, four numerical findings, category tables, carry economics, product histories, and observed events. ETH often presents the same evidence as filled areas, long tables and paragraphs about what the data cannot establish.

This is not a missing stylesheet problem. `tools/eth/site/base.css` is identical to the stylesheet extracted from BTC's `index.html`, after trimming whitespace. ETH's additional styles and chart renderers replace the most recognizable BTC patterns.

The first changes should be monthly bars, a properly styled Top 5 tab strip, four market finding cards with large numbers, and a complete carry-product history exhibit. These can use existing evidence.

## Prioritized changes

| Priority | Exact mismatch | Concrete fix | Evidence / target |
|---|---|---|---|
| P0 | Market monthly history is a filled stacked area. BTC uses individual stacked columns. | Render 24 equal month bands with narrow bars, 2 px gaps between stacked layers, rounded top segments, baseline, legend and a complete month tooltip. Preserve the ETH missing-observation policy. | BTC `stackCols`, `index.html:1407`; ETH `marketHistoryChart`, `tools/eth/site/market.js:13`; `#m-history-chart`. |
| P0 | Carry waves are also areas. The default shows only Liquid ETH and Concrete Delta. Rocksolid, now third in the Top 5, is absent from the overview even though its product chapter has 14 capital observations. | Use the same monthly column renderer. Include all ranked products visibly. Keep overlapping parent and nested product claims in separate labelled panels if they cannot form an additive total. Show the small dedicated products together rather than losing them under the large parent scale. | BTC `#c-waves`, `index.html:636`, `:1457`; ETH `market.js:77`, `:81`; `#c-history-chart`; `data/eth/product_chapters.json`. |
| P0 | Every Top 5 product capital history is a line. BTC renders all five capital histories as bars. | Replace the capital-history call with a one-series column chart. Keep return and borrowing histories as lines. | BTC `tvl` helper, `index.html:1460`; ETH `strict.js:111`. |
| P0 | The Top 5 tab container has `class="product-tabs"`, without BTC's `.tabs`. Its desktop CSS only sets a grid column count, so it does not receive the BTC grid or button-card styling. | Add the shared `.tabs` presentation and use six columns for five products plus Closed. Keep the separate five-product managed comparison's grid override scoped to its own container. | ETH `index.html:36`, `strict.js:94`; shared `.tabs`, `base.css:347`. |
| P1 | The market history findings are prose-only blocks, with no large numerical anchors. Extra scope paragraphs are appended on each market render. | Reuse BTC's `.findings.f4`, `.f`, `.big` structure. Each card should lead with one number, one plain-language result and one explanation grounded in a date or product. Put detailed coverage notes in the existing disclosure. | BTC `index.html:566`; ETH `market.js:63`, `strict.js:17`; `#m-history-findings`. |
| P1 | ETH uses `var(--head)` in font shorthands and the donut centre, but no `--head` token is defined. | Use the existing `--display` token, or define a consistent alias once. Invalid font declarations should be resolved before visual QA. | ETH `eth.css:42`, `:44`, `:56`; `market.js:26`; token definition in `base.css`. |
| P1 | ETH's current donut renders every positive protocol as an outer segment, without grouping the tail. It has native SVG titles and no BTC-style ring legend. | Reuse BTC's grouped outer ring, floating tooltip and clickable category legend. Limit individual visible products within a category and retain a named smaller-products segment. Keep every original protocol in the catalogue. | BTC `VMAP`, `index.html:1073`, and `donut`, `:1385`; ETH `marketDonut`, `market.js:22`; `#m-donut`. |
| P1 | Top 5 comparison rows are products and columns are broad topics. BTC places products across columns and compares eight specific dimensions. | Use a dimension-by-product matrix: capital, collateral/debt, destination, measured investor return, reward share, operator/control, holders, and the principal risk. Unmeasured dimensions should remain explicitly unmeasured. | BTC `#t-top5`, `index.html:646`, `TOP5`, `:1441`; ETH `strict.js:125`; `#strict-top5-comparison`. |
| P1 | Product money-flow diagrams are sequences of generic cards. They do not show the return path, collateral lock, debt edge, reward payer or self-credit loop. | Adapt BTC's linked SVG graph: asset-coloured edges, contract nodes, numbered operations, forward and return paths, actor zones and a legend. Use the captured product account identities and mark unresolved edges. | BTC `flowSVG`, `index.html:1369`, product `fd-*` exhibits; ETH `strict.js:120`, `.flowline`, `eth.css:13`. |
| P1 | Dollar funding and investment bars have no common numeric axis; borrowing rows precede investment rows rather than comparing matching legs. | Use BTC-style horizontal bars with an axis and end labels. Make base income the solid segment and rewards a lighter segment. Show the relevant borrowing cost beside its destination. Preserve dates and rate-window differences in a compact caption and table. | BTC `barH`, `index.html:1302`, `#c-venues`, `#c-legs`; ETH `strict.js:85`; `#strict-venue-chart`. |
| P2 | Category tables show 15 products by default, eight columns and subtype details after the main table. BTC shows eight rows, or five within meaningful subtype chapters. | Reuse compact category headers and facts, then subtype sections where economically useful. Show eight primary rows or five per subtype, with Show all. Keep the current searchable full catalogue. | BTC `renderCats`, `index.html:1136`; ETH `marketCatalogue`, `market.js:47`; `#m-category-body`. |
| P2 | The category table's Share column uses the selected whole-market denominator even while inspecting one category. BTC uses category share in category mode and market share for global search. | Match the BTC denominator behaviour and name it explicitly. An excluded category should remain inspectable with valid within-category shares. | BTC `cxTable`, `index.html:1130`, `:1147`; ETH `market.js:53`; `#m-product-table`. |
| P2 | ETH appends an empty-products section even when no empty product is established. This repeats an evidence caveat in every category. | Display an emptied-products note only when there are measured examples. Keep the general missing-versus-closed rule in Data. | BTC `cxEnded`, `index.html:1134`; ETH `market.js:53`. |
| P2 | ETH forces all SVGs inside `.chart-scroll` to at least 550 px; its newly added tables range from 980 to 1,450 px. | Test at phone and laptop widths. Use responsive chart labels and a deliberate compact comparison layout. Keep horizontal scrolling for genuinely wide evidence tables, not every chart by default. | ETH `eth.css:17`, `:44`, `:56`, `:63`. |

## Exact chart replacement map

BTC's capital-bar component has `viewBox="0 0 640 300"` by default. The main market uses height 320; product capital uses 240. Its margins are top 14, right 12, bottom 30, left 54. Each month receives an equal categorical band. Bar width is `max(3, min(26, band - 3))`. The top of each complete stack has a radius of up to 4. Share mode is 0 to 100%, with ticks at 0, 25, 50, 75 and 100. Amount mode uses the shared nice-number tick function. Month labels use readable abbreviated month names.

ETH currently uses a 1040 by 375 area renderer with time-scaled x coordinates, five arithmetic y ticks, hard-coded x indices `[0, 4, 9, 14, 19, 23]`, and ISO month labels. Individual points are keyboard-focusable, but the value is written into a text box below the chart. This differs from the BTC full-month floating tooltip, which also shows the total, coloured series keys and each category's share.

| ETH exhibit | Current renderer | Correct BTC pattern | Retain or adapt |
|---|---|---|---|
| `#m-history-chart` | `marketHistoryChart`, filled areas | `stackCols`, stacked monthly columns | ETH equivalent / USD, Amount / Share, selected categories, all-observation / constant cohort, table and CSV. |
| `#c-history-chart` | Same area renderer | `stackCols`, product monthly columns | Separate parent and dedicated claims when overlap prevents an additive total; include Rocksolid through the available product history source. |
| Top 5 `capitalHistory` | `lineChart` | One-series `stackCols`, height 240 | Native unit, ETH equivalent, USD and observation status in the table; no predeployment zero observations. |
| `#etherfi-chart`, Published capital | `lineChart` | One-series `stackCols` | Existing metric and chart/table controls. |
| `#protocol-history-chart` | `lineChart` | One-series monthly columns | Protocol selection, dated USD amount, native-unit table and missing records. |
| `#strict-venue-chart` | CSS tracks with segmented spans | `barH`, base plus lighter rewards | Distinguish funding cost from investment income; include a common numeric annual-rate axis. |
| Product wallet distribution | CSS percentage tracks | `barH`, wallet-size buckets | Keep chain/date and verified share-supply denominator. Addresses do not equal people. |
| `#m-chain-bars` | CSS bars | `barH`, common scale and end values | This is a useful ETH-specific addition; retain the separate chain-versus-aggregate explanation. |
| Top 5 investor return | Cumulative book-value line | `lineChart` | Lines remain appropriate. Add a same-date ETH staking benchmark where captured, a clear legend and floating tooltip. |
| Top 5 financing history | APR lines or single quotes | `lineChart` | Keep missing points absent. Do not subtract a cumulative share return from an annual loan-principal APR. |
| `#wealth-chart` | Multi-series wealth lines | BTC `lineChart` ergonomics | Keep normalized 100 ETH, window controls and selectable series; improve nice ticks, full-date tooltips and mobile sizing. |
| `#strict-curve-chart` | Single selected IRM line | BTC `#c-irm` line comparison | Keep lines. Optional comparison of several verified curves would expose the funding alternatives that a single selector hides. |

The user's request for BTC-style bars should be applied to capital and composition histories. BTC itself uses lines for rates, share values, price and collateral time series. Turning every rate curve into bars would not mirror the reference.

BTC's horizontal-bar component uses a 640 px viewBox, a 150 px label region by default, a 70 px right margin and 26 px rows. It can render a numeric axis, per-row floating tooltips, extra table columns and a solid subsegment within a lighter total. Its line component uses nice ticks, a crosshair, a full-date multi-series tooltip, null-segment breaks, optional end labels and event markers. All three components share a data-table registry.

The ETH implementation should preserve its stronger missing-data handling rather than copying BTC's `value || 0` treatment. An absent basis series is unmeasured, not a row of zero market observations. A missing month must not become an interpolated bar or line segment.

## Eight chapters: present structure and remaining gap

| Chapter | BTC main exhibits | ETH status | Best next change |
|---|---|---|---|
| Answer | Four headline cards, followed directly by three numbered implications. | Four cards and three implications are present, but a lede, three snapshot labels and a long scope paragraph separate the framing. The accent card has moved from carry to the overall market. | Keep one short date/scope line. Make headline card labels concise, with their denominator in the detail. Use one accent consistently. Lead implications with findings rather than instructions for reading. |
| Market | Current donut plus four observations; category bars; four numerical cards; category catalogue. | Core exhibits exist, plus a valuable chain exhibit. The main map notes are longer accounting explanations, with a wide summary table, and history findings have no large numbers. | Mirror the BTC exhibit sequence and dimensions. Keep chains as the ETH-specific final exhibit. Move the full accounting table into Data or a disclosure under the market. |
| Carry math | One BTC worked ledger; destination bars; borrowing markets; utilization curves; one calculator. | All required elements are present. The ledger has four dense columns, and the bars lack an axis. A second mechanics/calculator system sits in a supporting disclosure. | Make the primary one-ETH worked ledger readable in two columns, with evidence/status in the disclosure. Use paired financing/income bars. Leave general mechanism models in the optional detail. |
| Top 5 | Product-by-month carry bars and three historical waves; dimension matrix; product tabs; detailed product exhibits. | Product chapters, loan tables, holder distributions and events now exist. Capital charts and flows are visually different; overview omits one ranked product. | Fix the four P0 items, transpose the matrix and build linked money-flow graphs. Give each product one clear historical event and one numerical result before its long evidence table. |
| Other carry | Full landscape table; sampled borrower disclosure; share-price chart and realized-return table. | Landscape and borrower tables exist. Share prices, wealth comparison, exit costs and a second product catalogue are under supporting disclosures. | Keep one concise visible return exhibit after the landscape, with the larger managed-product comparison in optional depth. This makes investor outcomes visible without requiring a disclosure to find them. |
| Risks | One compact table: risk, observed example, acceptable operating response. | Matching compact table is present. Detailed account stress and incident timelines are available below it. | This chapter has strong structural parity. Prefer specific dates, accounts and thresholds in each row over generic risk language. Promote only the one or two most material measured stress numbers. |
| Playbook | Three recommendations; payout, reward-payer, rule and partner tables. | Matching recommendations and four tables are present. | Shorten headers, make numbers easy to scan and distinguish proposed limits from observed terms. No additional chart is required. |
| Data | Five disclosures for method, exclusions, cross-check, re-check and sources. | The five disclosures are present, followed by extensive library and evidence navigation. | Keep this depth. Simplify the top-level labels and make sources identifiable by descriptive names rather than repeated Source 1 / Source 2 links. |

This review does not recommend deleting the supporting research. The BTC pattern is a clear main argument with deeper source material available when needed. ETH already uses disclosures for much of its prior material; their placement can be improved without losing evidence.

## Numerical findings available without new research

The current `research_market_chapter.json` can already produce four BTC-style market cards. The following numbers were computed read-only from its six default strategy groups and 24 completed monthly points:

| Proposed large number | Plain-language finding | Exact observed basis |
|---|---|---|
| 24 / 24 months | Staking and restaking lead the covered exposure in every month. | Largest measured default category in all 24 monthly observations. This is issuer and security-layer exposure, not unique native validator stake. |
| -13.6% from peak | The selected market is below its January high in ETH equivalents. | 24,501,261.6 ETH equivalent in January 2026; 21,170,031.5 in September 2026. |
| -50.5% from peak | The examined ETH-loop parents are much smaller than at their peak. | 200,222.3 ETH equivalent in June 2025; 99,160.9 in September 2026. |
| -40.5% from peak | The covered farming and managed claims have contracted. | 607,925.4 ETH equivalent in May 2025; 361,915.0 in September 2026. Four major liquidity adapters remain missing. |

These describe reported layered exposure. They do not establish withdrawals, strategy losses, unique capital or historical portfolio weights. The constant-cohort switch should recalculate the cards from that same cohort, and category selection should update all four cards consistently.

The fixed-yield subset also declines 96.7% from its first-point peak. That is a large observation, but it needs coverage and product-level explanation before being used as a headline about the whole fixed-yield market. A numerical card should be a supported insight, not simply the largest percentage available.

Product insight density can also improve from captured evidence. Liquid's fee-change and share-supply reconciliation explain why capital growth differs from investor return. Concrete's genesis mint and concentrated holder ledger explain why a large claim is not automatically a new deposit. Rocksolid's indirect vault exposure explains why no direct Aave loan is not the same as no carry. Liquity has an active Trove and distinct dollar debt, wstETH collateral and oracle valuation. Royco's Caliber accounting does not identify the full downstream lending venue. These belong beside each product's flow and capital exhibit, before the generic limitation list.

## Typography, hierarchy and defaults

BTC uses an 1120 px wrapper, 15 px body text at 1.55 line height, Bricolage Grotesque display headings, IBM Plex Sans body text and IBM Plex Mono ticks. Its main h3 is 18 px, its h1 tops out at 60 px, and its history cards use a 34 px numerical anchor. The ETH override increases the wrapper to 1200 px, h1 to 64 px, several panel headings to 23 or 24 px, and several analytical paragraphs to 1.75 or 1.8 line height. At the same time, it reduces headline numbers from BTC's 42 px to 36 px. These changes give section labels more emphasis and findings less emphasis.

Use the shared BTC spacing and type tokens as the default. Keep purple as an ETH identity choice if desired; a colour change is not the main parity problem. Resolve `--head`, restore prominent finding numbers, use concise h3 labels and constrain long prose to a comfortable reading width. Preserve monospace only for numbers, addresses, dates and chart labels, rather than full analytical paragraphs.

Both pages default to asset units, absolute amounts and lending/CDP off. ETH additionally defaults to the all-observation cohort and a two-parent carry history. Those should remain visibly labelled. The default product selection is Concrete because it is first in the ranked Top 5. That follows BTC's rank-first interaction pattern, but the comparison needs a useful narrative result immediately after the tab so the first encounter is more than a private-custody caveat.

Category tabs should use BTC's four-column card layout with amounts and market shares underneath the names. ETH currently uses a wrapping strip of small buttons. Product tabs should use the six-card layout including Closed. At narrow widths, use the existing horizontal tab-strip behaviour. Treat the chain exhibit, constant-cohort option and normalized staking benchmarks as useful ETH adaptations, not reasons to redesign the whole visual system.

## Required evidence versus display work

The following are presentation gaps that can be fixed now: bars; market findings; grouped donut tail; complete ranked-product history; card tabs; font token; transposed comparison; linked flow graph; compact category facts; numeric axes; floating tooltips; legends; chart tables; source labels; and a visible common-window return comparison.

The following cannot be created by visual imitation: an exact unique global ETH total; historical carry-sleeve weights for hybrid parents; a time-weighted realized financing bill from month-end rate quotes; verified realized reward allocations to holders; a fully executed withdrawal-price series; product-specific allocation of Concrete's shared custody; or a verified closed dollar-carry case with a documented investor outcome. Where these are absent, retain the concise measurement limit and do not invent an equivalent BTC exhibit.

ETH now has wallet distribution rows for all five ranked products: Concrete 5, Liquid 10, Rocksolid 5, Liquity 5 and Royco 5. Holder distributions are therefore a rendering opportunity, not a missing-data excuse. Its product capital archives have 10, 24, 14, 9 and 7 monthly rows respectively. These are sufficient for actual product capital bars, with absent predeployment months left empty.

## Visual acceptance checks after implementation

1. At the default URL, market history, carry history and each product capital history visibly consist of bars, not area paths or connected capital lines.
2. Every multi-series capital chart has a visible colour legend and a floating tooltip with date, selected total, component amounts and shares. Table and CSV retain missing statuses and correct units.
3. Amount / Share, ETH equivalent / USD, category switches and cohort controls update chart, findings, table and export together. A category with no observations is described as unmeasured.
4. The ranked carry products are all represented in the carry-history overview. Parent/child overlap never creates an unexplained grand total.
5. The Top 5 has six styled tab cards on desktop, a visible selected border, keyboard focus and an accessible mobile strip. Opening a product presents capital, return, holders and loan scope coherently.
6. The market chapter has four numerical findings and compact category facts. Their source dates and denominators agree with the active chart.
7. At phone widths, ticks and month labels remain legible, tooltips fit the viewport and wide evidence tables scroll inside their own container. At laptop widths, the main argument does not require opening a research library to understand it.
8. BTC remains unchanged. Recheck the generated ETH site against the source, because the source fixes must survive the build.

## Source baseline

| File | SHA256 at inspection |
|---|---|
| `index.html` | `ee05709e085406a6b0da19717e974834c6ae48cea54f34840c830fbc9eaf1222` |
| `tools/eth/site/index.html` | `b12c7ff3d79ff4755b70bcba203a934d92eb02638897b3304c432c479069e98e` |
| `tools/eth/site/app.js` | `12b17f121674917a8c0d874c082fc9efde7aa7ccfa49ce9ef98e034754579684` |
| `tools/eth/site/market.js` | `6d8924bb56dc56bf923229ed36a3fccf027a25a19204230aa3b157f5470c8bcf` |
| `tools/eth/site/strict.js` | `5443f7ef326011ade486fd34950c3af5129d5d8d6a44d473ccfc90930c7eaacc` |
| `tools/eth/site/base.css` | `19cd2f1e8b3915fe669e21bcc5fb09da8ba14092a697cf3bc8e1ae544a5e8bf4` |
| `tools/eth/site/eth.css` | `943f86b3f74923e797aa3e038cc187a0ea70697f95281f556d3888819eb89dff` |

Other inspected sources: `tools/eth/site/compare.js`, `presentation.js`, `tools/eth/site.py`, `data/eth/research_market_chapter.json`, `data/eth/carry_economics_chapter.json`, `data/eth/carry_category_candidates.json`, `data/eth/product_chapters.json`, and `data/eth/carry_borrow_rate_history.json`.
