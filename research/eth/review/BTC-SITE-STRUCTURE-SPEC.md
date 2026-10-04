# Bitcoin website structure to reproduce in the ETH study

Reviewed 4 October 2026. This specification describes the actual original Bitcoin webpage and its data builder. It is an implementation guide for the ETH rebuild, not a comparison of dossier lengths. Original BTC files are unchanged. Financial observations retain their original dates.

The central feature to reproduce is a linked market dashboard. A reader first sees how much capital is counted, where it sits, how that distribution changed, and which products make up each category. The page then explains carry economics and examines the products. Research logs, source inventories and unresolved questions support this reading path later in the page.

## 1. The actual page order

The sticky navigation has eight links, in this order:

| Label | Actual destination | Main purpose |
|---|---|---|
| Answer | `#top` | Four findings and three practical conclusions |
| Market | `#map` | Current composition, monthly history and searchable category products |
| Carry math | `#how` | Worked unit economics, destination yields, financing and calculator |
| Top 5 | `#top5` | Carry product history, comparison and individual product panels |
| Other carry | `#market` | Wider product landscape, borrower identities and realized returns |
| Risks | `#risks` | Observed failures and corresponding controls |
| Playbook | `#do` | Decisions derived from the product evidence |
| Data | `#data` | Counting rules, exclusions, checks and sources |

`#map` is the market overview. `#market` is a later section about other carry products. These IDs are easy to confuse and must retain distinct purposes if reused. The source page does not put a research journal, task checklist or evidence file browser between the headline and market composition.

Source: [header and introduction](</Users/vladdegen/BTC Yield/index.html:513>), [market](</Users/vladdegen/BTC Yield/index.html:543>), [other carry](</Users/vladdegen/BTC Yield/index.html:928>).

## 2. Exact market composition and DOM contract

The following is the order inside the first two sections. Reuse this order, with ETH data and copy.

| Position | Original element | Structure and behavior |
|---|---|---|
| Header | `#countmenu`; `[data-flagset]`; `[data-flag-all]` | A compact Counting menu contains the same category switches as the market panels. Reset restores the default category set. |
| Hero | `#top`; `.tiles.answers` | Four cards: counted capital in BTC/USD and product count; carry share; carry concentration; return without rewards. The first two depend on category selection. |
| Selection notice | `#hiddennote` | Appears after a category is removed or an optional category added. Names the changed categories and their amounts, and offers Reset. |
| Main conclusions | `.panel.bottomline` | Three numbered, complete conclusions supported by the research. This is a brief interpretation, not a methodology inventory. |
| Market heading | `#map`; `.shead` | Section number, title and one sentence explaining category switches. |
| Main switches | `.flagrow.flagbar[data-flagset]` | All eight categories, each with a color and on/off switch. |
| Composition panel | `.panel.mapgrid` | Left: title, one-line reading instruction, `#c-donut`. Right: `.mapnotes`, a heading and three or four implications of the composition. |
| History panel | `#hist` | Title, dated interpretation, repeated category switches, unit/mode controls, `#c-hist`, Table, then four findings. |
| Product drill-down | `#cats` | Title and snapshot note beside search `#pq`; category tabs `#cat-tabs`; selected category contents `#cat-body`. |
| Compatibility anchors | `#products`; `#kinds-panel` | Empty anchors inside `#cats`. `#kinds-panel` opens C6 through the hash handler. |

Original dynamic text uses `[data-num]`, including `total`, `usd`, `n`, `totlabel`, `leftout`, `c1share`, `c2share`, `countsum`, `histout`, `mmnote`, `c2lead`, `leadh3`, `leadnote2`, `xlead`, `xleadh3`, `xleadp`, `c6drop`, `c6peakm`, `c6text`, `c1hist`, `totdrop`, `toth3`, `totpeak`, `totpeakm`, `totnow` and `nohist`. Original conditional IDs are `#tile-c1`, `#f-c1`, `#f-c6` and `#hiddennote`.

The classes `.stk-in` and `.stk-x` select alternate interpretations when staking is included or excluded. CSS reads `html[data-staking="off"]`; this affects both composition notes and historical findings. Category selection does more than hide colored chart series.

Source: [market markup](</Users/vladdegen/BTC Yield/index.html:543>), [dynamic findings](</Users/vladdegen/BTC Yield/index.html:1159>), [conditional CSS](</Users/vladdegen/BTC Yield/index.html:392>).

## 3. Category switches are one global state

The original constants have these definitions:

| Key / category | Label | Default |
|---|---|---|
| `carry` / C1 | Carry | On |
| `staking` / C2 | Staking | On |
| `basis` / C3 | Basis | On |
| `options` / C4 | Options | On |
| `credit` / C5 | Credit | On |
| `farming` / C6 | Farming and pools | On |
| `mm` / C7 | Money markets | Off |
| `cdp` / C8 | CDP collateral | Off |

`FLAGDEF` defines each switch and its category. `FLAGS[key].off` stores selection. `OFFCAT()` converts it to category exclusions. `FKEY()` is the eight-bit selection key used by the memoized calculations.

The change pipeline is exact:

```text
switch click or Reset
    -> setFlags(changes)
    -> update FLAGS
    -> persistFlags()
    -> markFlags()
    -> remove every open .tv table and reset Table aria-pressed
    -> render()
    -> renderV4()
    -> renderCats()
    -> fillNums()
    -> linkify(document.body)
```

`VMAP()` supplies the counted current rows, category totals, donut product groups and current denominator. `VHIST()` supplies the same categories in history, setting disabled category series to zero. `SEGNOW()` retains every category's full current amount for the selection notice. The selection affects the hero, composition, monthly totals, category shares and findings together.

Every switch appears three times: header menu, above composition, and inside history. `markFlags()` synchronizes all copies with `aria-checked`, and writes `data-carry`, `data-staking` and the other flags to the document root. Nondefault selection also sets `data-filtered` for the Counting menu styling. Switches use `role="switch"`.

If any recognized category query parameter is present, the URL defines the complete selection; omitted keys take their default. For example, `?staking=off&mm=on` removes staking and adds money markets. Without recognized query parameters, `flagFromPage()` reads `localStorage['atlas.' + key]`. `persistFlags()` stores every choice locally and writes only deviations from default into the URL with `history.replaceState`. Reset restores the default, rather than turning everything on. Escape closes the header menu and returns focus to its summary; a click outside closes it too.

For ETH, preserve this interaction model but use a separate storage namespace such as `eth-atlas.*`. BTC and ETH must not inherit each other's selections through shared keys. Put a single state update function behind every repeated switch.

Important boundary: BTC's detailed carry section and product histories remain visible when carry is switched off. They are independent research exhibits, not filtered market totals. `c-waves` reads `V3.c1hist`, not `VHIST()`. Reproduce that distinction, or deliberately add a clear separate filter. Do not accidentally erase the mechanism explanation when a reader excludes its capital from the map.

Source: [state and calculations](</Users/vladdegen/BTC Yield/index.html:1056>), [initialization](</Users/vladdegen/BTC Yield/index.html:1644>).

## 4. Current composition: nested donut, not a card grid

`renderV4()` calls `donut('c-donut', ...)` with `VMAP().cats`, counted total, counted USD value, selection notice and `onPick: c => pickCat(c, true)`.

The SVG is a 420 by 420 viewBox with two concentric rings. The inner ring uses category BTC as its angle. The outer ring uses product BTC within that category. Both tooltips show BTC and dollars. Category tooltip adds share and product count; product tooltip adds share of the whole map and its category. The center shows current counted capital and dollars. A smaller line names category exclusions or additions.

`VMAP()` sorts categories by capital and rows within each category. The original product grouping rule is:

1. Show a product individually if it is at least 1.2% of the counted map, or a C1 carry product with at least 100 BTC.
2. Keep at most six such products per category.
3. If one remaining product exists, show its name. Otherwise group remaining products into “N smaller products”.

Category and product slices both open the corresponding category, clear search and scroll to `#cats`. An outer-ring slice does not open an individual product dossier. Each slice has `tabindex=0` and Enter/Space activation. A clickable legend below the donut repeats category name, amount and share and opens the same drill-down.

The render also populates `REG['c-donut']` with Category, Product, BTC, US dollars and Share of all. The original markup has no donut Table button, even though that table record exists. Adding a visible Table or download for ETH is a useful adaptation rather than a copied BTC feature.

If all categories are off, the chart displays “Every category is switched off” and clears its table record. Retain this empty state and prevent any percentage from becoming NaN.

Source: [VMAP grouping](</Users/vladdegen/BTC Yield/index.html:1073>), [donut renderer](</Users/vladdegen/BTC Yield/index.html:1385>), [market render](</Users/vladdegen/BTC Yield/index.html:1452>).

## 5. Monthly category history and its four interpretations

`#hist-tools` contains four buttons:

| Attribute | Choices | Original default |
|---|---|---|
| `[data-hu]` | `btc`, `usd` | BTC |
| `[data-hm]` | `abs`, `share` | Amount |

`HIST = {u:'btc', m:'abs'}` stores unit and mode. `drawHist()` reads `VHIST()[HIST.u]`, builds category series in `CATORDER`, removes all-zero series and calls `stackCols('c-hist', ...)` at height 320.

There are 25 observations from September 2024 through September 2026. Each month is a stacked column. The sum of the visible segments is the counted monthly total; there is no separate total line or total/category chart toggle. “Amount” uses capital units. “Share” normalizes each month to 100%. The unit toggle changes both displayed amounts and the underlying date-matched USD series. It does not reprice historical BTC at today's price.

Pointer movement highlights a month and shows its total, followed by category amounts and percentages. Keyboard focus shows the latest month. The legend is informational. Category selection happens through the switches, not by clicking the chart legend.

The Table button uses `data-table="c-hist"`. `tableToggle()` appends `.tblwrap.tv` beside the chart using `REG['c-hist']`: Month, category columns and Total when more than one category exists. Unit changes remove an open history table so it cannot retain the old unit. Amount/Share changes redraw the chart but do not remove the table. In the BTC renderer, the table retains absolute amounts even in Share mode. An ETH copy should either clearly label that table as absolute values or make table and CSV obey the selected mode. Do not silently present an ETH amount table as the values of a percentage chart.

Below the chart, `.findings.f4` presents four substantive facts:

1. Which category led and in how many months. An alternate finding appears when staking is off.
2. The farming/pools decline from its peak, with strategy-vault and points components.
3. Carry's growth from zero to its current historical share.
4. Total decline from its selected historical peak and the number of current products without history.

`fillNums()` recalculates leaders and peak/drop under category selection. These findings should become ETH-specific observations derived from the selected cohort. Do not copy BTC's points boom, LBTC reclassification, carry waves or subsidies into ETH prose.

The main ETH market history should occupy this position before detailed product histories. A wealth/PPS comparison is a different exhibit and does not replace it.

Source: [history markup](</Users/vladdegen/BTC Yield/index.html:559>), [stacked columns and table record](</Users/vladdegen/BTC Yield/index.html:1407>), [history handlers](</Users/vladdegen/BTC Yield/index.html:1470>).

## 6. Category drill-downs are miniature market chapters

`CX = {cat:'C1', open:{}}` starts on Carry. `renderCats()` creates eight tabs, with IDs `ctab-C1` through `ctab-C8`, `data-cat`, `aria-controls="cat-body"`, `aria-selected` and roving tab focus. Each tab displays the category's full current capital and its share of the counted map, or “not counted” when disabled.

The selected category contains, in order:

1. Full category name, colored marker, current amount, share of map and product count.
2. A short description explaining how investors earn income in it.
3. Typical yield, month-end peak when its guard allows it, amount two years earlier, and products without history.
4. Product table or subcategory tables.
5. An “Emptied or closed” note for products present in history but not current capital.

The product table columns are Product, BTC at snapshot, Share, How it earns, Yield per year and Run by. Source URLs link the product names. BTC token details appear below mechanism text. Within a normal category the Share denominator is the full category amount. Search results instead use the counted map as denominator and add a Category column. Keep these denominators explicit in ETH.

Ordinary category tables initially show eight products. `data-more` and `data-mk` control “Show all N” / “Show fewer”, with `aria-expanded`; hidden rows use `.more` and become visible through `.showall`. C6 subdivides into Points farming, Strategy vaults and Liquidity pools. C7 subdivides into Lending markets and Vaults that only lend. Each subtype shows five rows initially and uses the full category denominator. Its headline separately gives the subtype's share of its category.

Search `#pq` spans every category, including disabled ones. It matches product/internal name, display name, mechanics, manager, token and category text. It shows every matching row, with disabled rows dimmed and labelled “not counted”; those rows do not gain a percentage of the counted map. Search does not modify market switches. Selecting a category clears search. Left/Right arrows cycle category tabs. `[data-cat-open]` links elsewhere open a category and scroll to it.

Turning a category off does not delete its catalogue. The tab and table stay browsable, with `.cx.off`, `.offtag` and reduced opacity. Its current amount remains visible, but its historical facts come from the filtered `VHIST()` and therefore disappear. For ETH, retaining the full category's own dated history in a disabled category detail is a reasonable improvement; label it as excluded from the market selection.

The BTC peak guard is `historicalPeak >= currentCategoryAmount * 0.98`, and no-history count is displayed separately. This is not proof that every current product has a complete history. ETH should use an explicit coverage flag rather than interpreting the 98% numerical guard as historical completeness.

### Actual C1 current contents

The current BTC carry category has ten products and sums to 9,315.590 BTC. The initial category table shows eight, with the last two behind Show all:

| Product | Current BTC |
|---|---:|
| Kraken Bitcoin Vault | 6,492.700 |
| Yield Basis | 1,326.200 |
| Bitget bgBTC Earn | 801.700 |
| Midas mHyperBTC | 354.120 |
| ether.fi Liquid BTC | 231.560 |
| Hermetica hBTC | 46.950 |
| Vesu Noon WBTC vault | 37.660 |
| Tesseract TESS debt-loop vaults | 14.490 |
| BTCD Labs / TAU dollar-carry vaults | 6.580 |
| Acre acreBTC | 3.630 |

C1's short description explains BTC collateral, a dollar loan and reinvestment, then links to `#top5`. This description and catalogue connect the market composition to the next analytical sections. For ETH, the equivalent carry chapter should distinguish dollar debt against ETH claims, ETH borrowing loops, and dollar-neutral basis rather than placing all three into one capital category.

Source: [category render and search](</Users/vladdegen/BTC Yield/index.html:1114>), [data generator](</Users/vladdegen/BTC Yield/tools/site_data.py:68>).

## 7. Transition from market to economics to products

After `#cats`, the original page immediately enters `#how`. Its sequence is:

| Exhibit | Actual DOM | Connection to preceding market |
|---|---|---|
| One-BTC worked example | `.cols` and `table.ledger` | Shows deposited BTC, collateral fraction, dollars borrowed, gross destination income, rewards, debt interest, operator fee and investor return. |
| Destination-yield comparison | `#c-venues`; `[data-table="c-venues"]` | Explains which destinations clear financing costs and which depend on rewards. |
| Borrowing venues | `#t-markets` | Market, chain, collateral, debt, current LTV and rate. Names link to the relevant markets. |
| Rate curve | `#c-irm`; `[data-table="c-irm"]` | Shows how utilization changes borrowing costs. |
| Preset model | `#presets`; `.calc`; `.out` | Lets the reader reproduce a product example or change loan economics. |

Calculator inputs are `i-ltv`, `i-post`, `i-cf`, `i-br`, `i-dy`, `i-rs`, `i-fee`. Visible values use corresponding `v-*` IDs. Outputs are `o-net`, `o-org`, `o-gross`, `o-spread`, `o-hf`, `o-buf`, `o-liq`. `CALC_IDS` wires live inputs; `PRESETS` supplies named scenarios. Changing an input clears preset selection. Profit fees apply only to positive carry.

The BTC formula and liquidation assumptions are specific to dollar debt against BTC, and the liquidation model uses Babylon/Aave v4 testnet target HF 1.24 and maximum bonus 10%. Reuse the control layout, not those assumptions. ETH needs separate models for an ETH-debt loop, ETH collateral with dollar debt, and basis. Income-bearing ETH collateral also needs its baseline income retained. A generic ETH price drop does not describe relative LST/ETH liquidation risk.

Then `#top5` begins with product composition over time, before presenting individual deep dives:

1. `#c-waves`: stacked carry capital by product, with a Table button.
2. Three short dated “wave” stories, followed by a note about a hybrid changing category when its debt disappeared.
3. `#t-top5`: a side-by-side table of investor capital, collateral/debt, dollar deployment, realized yield, reward dependence, operator, depositors and main concern.
4. `#top5-tabs`: five current product tabs plus Closed.
5. Panels `tp-kraken`, `tp-yb`, `tp-bitget`, `tp-mhyper`, `tp-etherfi`, `tp-closed`.

`#c-waves` uses carry product history from January 2025 onward. Six named products have `WAVECOL` colors; remaining included series are grouped as Others. Closed Maple remains in history despite zero current capital. Each product panel includes a linked flow diagram, numbered mechanics, control and payer tables, current facts, histories, events and interpretation. Product tabs support arrow keys, `data-open` links and hash-driven opening of hidden panels/details.

For ETH, keep the chart-before-comparison-before-product-tabs sequence. Use a verified product sample until a size ranking is established, and say what capital measure selects it. Liquid ETH's whole NAV is a hybrid product, not a measured dollar-carry sleeve. Its current disclosed percentage is not a two-year carry allocation history.

Source: [carry economics markup](</Users/vladdegen/BTC Yield/index.html:582>), [calculator logic](</Users/vladdegen/BTC Yield/index.html:1351>), [products markup](</Users/vladdegen/BTC Yield/index.html:634>), [product interaction](</Users/vladdegen/BTC Yield/index.html:1474>).

## 8. Data dependencies behind the page

`tools/site_data.py` emits the embedded `const V3` object. The page renders market capital from `V3.rows`, rather than from its stale fallback text. The current embedded default is 94,361.210 BTC / $7,660.0618M across 101 positive rows. The HTML fallback product count says 103, but runtime replaces it with 101. The last default historical sum is 89,788 BTC. These are separate cohorts/vintages.

| Embedded field | Builder input | Used by |
|---|---|---|
| `rows` | `market_map_current.csv` filtered to `include_net=1`, positive capital and known categories; optional net `money_markets.csv` rows | Hero, VMAP, switches, donut, categories, search |
| `cats` | Eight fixed code/name/color definitions | Switches, donut and category headings |
| `info` | `product_notes.csv`, supplemented by money-market descriptions | Product mechanics, yield, manager, URL |
| `names`, `tokens` | Display-name normalization and `c6_groups.csv` | Category catalogue and search |
| `hist.x`, `hist.btc`, `hist.usd` | Months from `category_history_monthly.csv`; amounts from product history and `money_markets_monthly.csv` | Monthly category chart and findings |
| `kinds` | C6 product-history amounts grouped as points/vaults/pools | Historical farming findings |
| `nohist` | Current positive products absent from product history | Coverage warnings |
| `ended` | Historical positive products absent from current live names | Closed/emptied category notes |
| `c1hist` | C1 product history, retaining series with historical maximum at least 40 BTC | Carry waves |
| `top` | `data/top5/*` CSVs and optional `site_series.json` | Product size/yield/holder charts |
| `outside` | `outside_totals.csv` | `#t-out` under Data |
| `mmgross` | Money-market gross supplied BTC | Retained supporting context; not VMAP's net amount |

Pure lending vaults are reclassified from C6 to C7 using `c6_groups.csv`, both now and historically. Money-market/CDP rows count only residual BTC after overlap adjustments. The table is therefore not a sum of raw DefiLlama categories. All current positive map rows must have product notes; the builder asserts coverage. Short-name collisions also raise an assertion.

`ended` joins holder-suffix aliases, excludes products still live, requires a peak of at least 20 BTC, and defines last material month at 2% of peak or one BTC. Its small category note is not a complete legal closure determination.

The carry-waves endpoint sums to 9,258 BTC, while category history displays 9,278 BTC. The builder drops C1 histories that never reached 40 BTC, so the “Others” series only aggregates retained histories. At the September endpoint this excludes TESS at 14.495 BTC and BTCD/TAU at 6.585 BTC, a 21.080 BTC tail. Rounding individual retained series leaves a 20 BTC difference between the displayed totals. The BTC page does not explain this tail. The current map has an additional 37.660 BTC Vesu product with no history, plus precision differences. ETH should disclose and reconcile omitted tails and current-only rows rather than reproducing these inconsistencies.

Source details belong in the final Data section: counting, exclusions, category selection, overlap judgments, unverified claims, `#t-out`, `#crosscheck`, `#recheck` / `#t-recheck`, and source links in `#srcs`. Market panels carry brief date/coverage notes and relevant links; they do not repeat the entire audit report.

## 9. What to reuse literally and what to adapt

| Component | Reuse literally | Adapt for ETH |
|---|---|---|
| Reading sequence | Answer -> Market -> Economics -> Products -> Landscape -> Risks -> Playbook -> Data | English titles and ETH findings; retain market before deep dives |
| Layout | `.wrap`, `.panel`, `.mapgrid`, `.cols`, `.tiles.answers`, `.findings.f4`, `.tabs`, `.tblwrap` | ETH visual identity; preserve chart density and responsive hierarchy |
| Category interaction | One global state, repeated switches, Reset, URL persistence, synchronized ARIA | E-series taxonomy, selected accounting basis and ETH-specific defaults/storage keys |
| Donut interaction | Inner categories, outer products, click-to-category, accessible tooltips and legend | ETH units, product grouping thresholds and a defensible additive cohort |
| Monthly history | Stacked categories, unit and amount/share controls, Table, derived findings | 24 completed ETH months; explicit null/coverage behavior; same date-matched prices and categories |
| Catalogue | Category tabs, mechanism/yield/manager table, search, Show all, excluded rows still browsable | Product identities, chain and capital basis; distinguish product NAV from strategy allocations |
| Carry economics | Worked ledger -> destination comparison -> debt markets/rate curve -> calculator | Separate ETH debt, dollar debt and basis, with verified collateral income and parameters |
| Product introduction | Composition history -> side-by-side -> current/closed product tabs | Measured sample and product histories; no invented carry ranking or allocation history |
| Evidence placement | Brief panel labels and links; fuller method/source section at the end | ETH capture dates, measurement coverage and reproducibility files |
| Renderer mechanics | SVG helpers, chart tooltips, table registry, tab semantics, hashes | ETH names/formatters, safe null handling and table/CSV consistency |

ETH lending should not inherit BTC's “about 0%, off by default” argument. ETH supply interest is a genuine strategy and financing ETH also supports staking loops. Native staking needs a visible baseline; restaking and looping do not each create a new underlying ETH. Dollar-neutral basis requires an explicit exposure and return-currency label.

Use original visual dimensions: `.wrap` max-width 1,120 px; market columns 1.05fr/1fr with a 28 px gap, stacking below 860 px; four finding cards, two below 900 px and one below 560 px; category tabs four columns, two below 900 px, scrolling buttons below 560 px. All grid children need `min-width:0`, and tables should scroll within `.tblwrap`, not widen the page. Header Counting hides below 760 px, leaving the visible market switch rows available.

## 10. Concrete ETH build contract

Keep a market object separate from a research-status object. The minimum normalized market shape is:

```text
market = {
  edition, snapshot, basis, unit, cohort_description,
  categories: [{id, label, color, income_explanation, default_on}],
  rows: [{product_id, category_id, chain, capital_eth, capital_usd,
          capital_basis, as_of, how, yield, yield_basis, operator,
          source, counted, overlap_adjustments, history_status}],
  history: {months, eth_by_category, usd_by_category, coverage_by_month},
  product_history, excluded_products, unresolved_segments
}
state = {categories_on, unit, mode, category_open, query, expanded_tables}
```

Every market view must derive from the same `market` and `state`. Category amount, product amount and market total must share one accounting basis. Current product capital and historical protocol adapter balances are not interchangeable. NULL means unavailable and must survive into tables/downloads. A known prelaunch zero is different from missing history.

Existing ETH evidence can populate a large catalogue and selected dated exhibits, but does not currently establish a globally netted mechanism market. `market_summary.json` leaves unique underlying ETH and external depositor equity null. Its $70.939B screening sum is full mixed-pool TVL, which is neither ETH capital nor a bound on unique ETH. `chain_screen.json` ranks that screening measure. `protocol_trend_screen.json` contains overlapping protocol observations. Those sources cannot directly fill an additive ETH donut or stacked mechanism chart.

The implementation choices are therefore:

1. Build a reconciled, explicitly scoped capital cohort with mutually exclusive rows and date-specific overlap adjustments. Use the BTC dashboard directly for that cohort and name it consistently in the hero, chart and table.
2. Present non-additive protocol observations as a distinct protocol comparison, with their own denominator and no all-market sum. A protocol ranking can complement the market page but cannot stand in for a reconciled category map.
3. Keep discovery counts and coverage controls below the main market exhibits or in Data. Do not make source counts and open tasks the headline story.
4. Add chain geography in the market section after composition/history, with backing, circulation and deployment distinguished. A chain filter must update the entire selected market cohort, or explicitly remain a separate geography exhibit.
5. Put existing wealth benchmarks and Liquid ETH history after the market overview, then connect them to mechanics and products. They answer investor performance, not total market size.

Acceptance checks for the rebuild:

- The opening screen communicates capital scope, largest categories and main economic findings.
- A category switch updates headline amount, donut, monthly series, product shares and interpretation together.
- A donut slice opens the relevant category catalogue; search finds products from all categories without changing the total.
- ETH/USD and Amount/Share work, and visible tables/downloads state the selected units and denominator.
- Current and last-historical totals identify different cohorts when they differ; omitted products and missing histories are visible.
- Carry has an actual category chapter before worked economics and detailed product panels.
- Each prominent panel explains a market fact. Research execution status remains supporting material.
- Mobile keeps controls and tables usable; switches, tabs, slices and hidden-panel links work with a keyboard.

Only this implementation specification was written for this task. The site, existing reports, source data and original BTC project were not edited.
