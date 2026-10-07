# 1 · Structure parity audit: ETH site vs BTC site

Read-only audit. BTC = `index.html` (snapshot 20 Sep 2026). ETH = `eth/index.html`, built from `tools/eth/site/*` (snapshot 2 Oct 2026).
Inputs: `dumps/btc_rendered.txt`, `dumps/eth_rendered.txt`, plus the sources (`index.html`, `tools/eth/site/index.html`, `strict.js`, `reader.js`, `closure.js`, CSS).
Scope the owner set: ETH drops **Carry math** (`#how`) and **Playbook** (`#do`). Everything else should match BTC.

Status check: both sections are already `hidden` in the ETH reader edition (`<section id="how" hidden>`, `<section id="do" hidden>`, `eth.css:144`), and the ETH nav leaves them out. That part is done.

Dump caveats:
- The ETH dump opened every disclosure, including the `Table: chart data` blocks. The BTC dump shows only the word "Table", because BTC's table toggles swap the chart for a table. ETH word counts are therefore inflated against the default view, but the default ETH view is still 2–3x longer than BTC.
- The BTC category dumps C2–C8 all repeat the Carry panel (a capture artefact), so BTC's non-carry category panels were checked in the source, not the dump.

---

## 0. Word counts (rendered text, whitespace tokens; "prose" = lines of 6+ words)

| Section | BTC words (prose) | ETH words (prose) | Ratio |
|---|---|---|---|
| Hero tiles | 72 (47) | 98 (71) | 1.4x |
| What it means for us | 113 (108), 3 points | 194 (189), 4 points | 1.7x |
| Market header + switches | 46 | 93 (switches print "On/Off") | 2x |
| Donut + What stands out | 121 | 163 + category table | 1.3x |
| Two years + findings | 194 | 220 + 114 ("Change by category" table) | 1.7x |
| Who is in each category (default tab) | 514 | 631 | 1.2x |
| By chain | — | 474 (52-row table) | ETH only |
| Carry math | 677 | hidden | owner decision |
| Top 5 intro + waves + findings | 276 | 354 | 1.3x |
| Side by side | 37 header + 8 rows | 336, 11 rows | — |
| Product #1 block | Kraken 1,233 (860) | Liquid ETH **4,921 (4,145)** | **4.0x** |
| Product #2 | Yield Basis 841 | YieldBasis WETH 2,134 | 2.5x |
| Product #3 | Bitget 795 | Lido Earn 2,200 | 2.8x |
| Product #4 | mHyperBTC 806 | Avant 2,115 | 2.6x |
| Product #5 | ether.fi 758 | Liquity 2,472 | 3.3x |
| Closed tab | 338 (Maple, Hermetica, Acre) | 227 (Origami ×2, Rocksolid note) | weaker |
| Other carry table + sweep | 1,204 | 587 | 0.5x (sweep paragraph missing) |
| Awaiting dollar-carry verification | — | 187 | ETH only |
| Largest borrowers | 593 (29 rows) | **8,377 (237 rows)** | **14x** |
| Share prices | 106 | 494 (+252 protocol capital) | 7x |
| Risks | 300 (10 rows) | 357 (8 rows) | 1.2x |
| Playbook | 559 | hidden | owner decision |
| Data: method | 455 | 443 (+ coverage table) | 1x |
| Listed, not counted | 797 (21 rows) | 1,023 (33 rows) | 1.3x |
| Rows left out (DefiLlama) | (in method, 1 paragraph) | 1,280 (100 rows) | ETH only |
| DefiLlama check | 369 | 129 | 0.35x |
| Re-check | 374 (28 rows, source column) | 108 (15 rows, no source) | 0.3x |
| Sources | 349 (~80 named links) | 139 (6 library cards + buttons) | — |
| **Main page total** | **8,845** (7,609 without carry math and playbook) | **20,980** | **2.8x** |

---

## 1. Global chrome

| Element | BTC | ETH | Verdict |
|---|---|---|---|
| `<title>` / brand | "BTC Yield Atlas" / brand "BTC Yield Atlas" | "ETH Yield Research · The Ether yield market" / "ETH Yield Research" with a diamond icon | **DIFFERENT**: rename to "ETH Yield Atlas" in both places |
| Nav | Answer, Market, Carry math, Top 5, Other carry, Risks, Playbook, Data | Answer, Market, Top 5, Other carry, Risks, Data | **SAME** (minus the two owner-dropped items) |
| Counting menu | `Counting **all yield categories**`; popup "Categories every market number counts", chips, "Reset to default" | Same summary text; popup adds a note ("Filters change the Market charts… saved in this browser and URL") | **DIFFERENT (minor)**: drop the note |
| Header stamp | "snapshot 20 Sep 2026 · BTC $81,178" | none | **ETH MISSING**: add "snapshot 2 Oct 2026 · ETH $2,6xx" |
| Theme button | none | ◐ theme button | **ETH EXTRA** (harmless; BTC follows the system theme). Keep or drop, but be consistent |
| Back to top | "Top ↑" at the top level | "↑ Back to top" after the footer | **DIFFERENT (minor)**: same label and position |
| Footer | "BTC Yield Atlas · research for the Babylon team · snapshot 20 September 2026, updated 24 September. Data, scripts, the Russian report and the dossiers are in the repository." | "ETH Yield Research · financial snapshot 2 October 2026 · reviewed 6 October 2026. Current team briefing · Coverage and measurement boundaries." | **REWRITE**: "ETH Yield Atlas · research for the Babylon team · snapshot 2 October 2026, updated 7 October. …" |
| Meta description | Concrete numbers ("94,361 BTC across 101 products…") | Generic ("Deep research into the ETH yield market…") | **REWRITE** with numbers |
| OG / Twitter | og:title, og:description, og:url, og:image 1200×630, twitter:card large | none | **ETH MISSING**: add the full set and an `og.png` |
| Favicon | `assets/favicon.svg` | none | **ETH MISSING** |
| theme-color | `#0f1216` | none | **ETH MISSING** |
| Print | no print CSS, no button | `@media print` rules and a "Print / PDF" button in Data | **ETH EXTRA**: keep the CSS, drop the button |
| Link to the other site | none | "Original BTC Research →" button | **ETH EXTRA**: a footer link is enough |
| Section numbering | "1 · MARKET" … "7 · DATA" | "01 · MARKET" … "05 · DATA" | **DIFFERENT**: use "1 ·" (renumbering after the dropped sections is fine) |

---

## 2. Hero / Answer

| Element | BTC | ETH | Verdict |
|---|---|---|---|
| Eyebrow | "SNAPSHOT: 20 SEPTEMBER 2026" | "SNAPSHOT · 2 OCTOBER 2026" | SAME |
| H1 | "Where Bitcoin earns a yield, and what carry really pays" | "Where ETH earns a yield, / and what carry really pays" (forced `<br>`) | SAME (drop the `<br>`) |
| Tile 1 | 94,361 BTC earn a yield ($7.7B); "Across 101 products. 62% is staking." | 18,349,193 ETH ($49.0B); "Across 170 products, each counted once; 81% is staking." | SAME (show "18.35M"; drop "each counted once") |
| Tile 2 | 9.9% is carry; "Zero two years ago." | 1.7% is carry; 306k ETH, 14 products, $261M debt, 147k two years ago | SAME |
| Tile 3 | 70% of carry is Kraken's vault | 85% of carry is in two products | SAME |
| Tile 4 | 0.1–0.6% without rewards | +0.7 pp over staking | SAME in spirit (ETH-specific framing is right) |
| What it means for us | 3 numbered points, bold lead, 113 words | 4 points, 194 words; point 3 (private mandates) runs 3 sentences | **REWRITE**: 3 points of at most 2 sentences. Merge point 4 (loan currency) into point 1, or fold the private-mandate point into the Other carry lede |

---

## 3. Market

| Element | BTC | ETH | Verdict |
|---|---|---|---|
| Section head | "1 · MARKET / All the BTC that earns a yield" + 1-sentence lede | Same head; lede is 2 sentences ("each counted once: a staking token held inside a vault counts in the vault…") | **REWRITE** the lede to 1 sentence; the counting rule belongs in Data |
| Switches | One chip row (8 chips), no On/Off text | Chip row with "On"/"Off" under each, "Reset", and the sentence "Counting: Staking, Restaking, …" | **DIFFERENT**: show BTC-style chips; drop the On/Off text and the Counting sentence (the header menu already says it) |
| Switch duplicate | Switches only at the top (owner rule) | **A second full switch set + Reset inside "Two years, by category"** | **ETH EXTRA → REMOVE** (breaks the "switches only at the top" rule) |
| Donut | "Where the money is"; inner = categories, outer = products; **legend list beside the donut** (category, size, %) | Same donut; center "18.35M ETH $49.0B counted once"; **no legend in the rendered text** | **ETH MISSING**: add the BTC legend (6 rows) |
| What stands out | 3 one-sentence findings, 59 words | 4 findings, 137 words, **plus a CATEGORY/ETH/USD/SHARE table** | **REWRITE** to 3 findings; **REMOVE** the table (the legend replaces it) |
| Two years, by category | Stacked chart; BTC/US dollars and Amount/Share toggles; Table toggle; 4 findings (big number, label, 1–2 sentences) | Same chart and toggles + "Selected data CSV" + "Hover a month…" hint; 4 findings in the same format | **SAME** core. **REMOVE** the CSV button and hover hint |
| Change by category | — | Table (9 categories × 6 columns) with All observations / Constant cohort toggle + footnote | **ETH EXTRA → MOVE to exhibits** |
| Who is in each category: tabs | 8 tabs, each with size · share | 11 tabs (adds Leveraged staking, Fixed yield) | SAME (ETH-specific categories are legitimate) |
| Category panel header | Title, size, "% of the map · N products", 1–2 sentence description, then "Pays 1 to 3% a year / Month-end peak / Two years ago / N of N products have no history" | Same, but the pay line is "Paid by …" (who pays) and there is no "N products have no history" line | **DIFFERENT**: add BTC's "Pays X to Y% a year" range and the no-history count; "Paid by" can stay as the description's second sentence |
| Category table | 6 columns: PRODUCTS · BTC, 20 SEP · SHARE · HOW IT EARNS · YIELD, % A YEAR · RUN BY; plain names; "Show all N" | 6 columns, but every ETH cell carries a second $ line, names carry ↗, the pay column reads "2.2, 2 Oct pool APY (STETH, Ethereum)" | **REWRITE** the cells: plain "2.2" (source in the method); drop the $ line or move it to a tooltip |
| Emptied line | "Emptied or closed since September 2024 (month-end peak): Maple BTC Yield 1,643 BTC." | "Emptied since 2024: Reservoir ETH Yield (4,137 ETH in Oct 2025, 24 now)." | SAME |
| By chain | — | Bar chart (10 chains) + 52-row chain table + "Map CSV" + "What was netted, and why" + "Strategy deep dives →" | **ETH EXTRA → MOVE to exhibits** (BTC has no chain view) |

---

## 4. Top 5

### 4a. Section frame

| Element | BTC | ETH | Verdict |
|---|---|---|---|
| Head | "3 · TOP 5 / The five largest carry products"; lede "Ranked by BTC deposited… flow of funds with links to the contracts and markets, who holds the keys, who pays the yield, the charts and the events." | "02 · TOP 5 / The five largest carry products"; "Ranked by **dollars borrowed** against ETH… how fast the debt can be repaid." | **DIFFERENT**: the ranking basis differs. By dollars borrowed, YieldBasis (10k ETH) ranks #2 ahead of Lido Earn (83k ETH). Either rank by ETH deposited like BTC (Liquid, Lido Earn, Avant, YieldBasis, Rocksolid/Liquity) or say why in one clause |
| Waves chart | "Carry came in three waves": stacked month-end BTC by product, 7 series, Table | "Two years of carry, by product": stacked, 12 series, All/Smaller toggle, ETH/USD toggle, Table, CSV, hover hint, 2 notes (Concrete left out; mixed vaults) | **DIFFERENT**: name it as a finding ("ETH carry is one product, then a debt jump"); **REMOVE** CSV, the hover hint and the "Product balances, conversions and counting →" link; keep one note |
| Wave findings | 3 headed paragraphs + 1 aside, no links | 3 headed paragraphs, each followed by "Evidence →" | **REMOVE** the 3 "Evidence →" links |
| Side by side | Caption + 8 rows: Depositors own · Collateral and loan · Where the dollars go · Paid, in BTC · Share from rewards · Run by · Depositors · Biggest red flag | 11 rows: Book · Dollars borrowed · Loan rate · Where the dollars go · Parked dollars earn · Dollar spread · Paid in ETH (vs stETH) · Lowest HF · Debt repayable · Who can change it · Main risk; then "Complete product evidence…" and "Backing and withdrawal stress…" buttons | **ETH MISSING**: "Share from rewards", "Run by", "Depositors" (holder count and concentration). **ETH EXTRA**: Loan rate, Parked dollars earn and Dollar spread (fold into one "Dollar leg" row), Lowest HF, Debt repayable. **REMOVE** both buttons |
| Closing line | "Maple BTC Yield, the 2025 leader, is under Closed." | — | ETH MISSING (point to Reservoir/Rocksolid under Closed) |
| Product tabs | "Kraken / 6,493 BTC · 1.41%" (size · yield) | "ether.fi Liquid ETH / #1 · $181.085m debt" | **REWRITE**: "Liquid ETH / 177k ETH · 3.2%" |
| Label above the chapter | — | "What the evidence supports" | **REMOVE** |

### 4b. Product block, element by element (BTC Kraken vs ETH Liquid; the same holds for #2–#5)

| # | BTC block (order) | ETH chapter (order) | Verdict |
|---|---|---|---|
| 1 | — | Eyebrow "#1 by dollars borrowed against ETH", H3 name, one-line verdict, "Product data" download button | ETH EXTRA: the eyebrow and verdict line are fine; **REMOVE** the "Product data" button |
| 2 | — | "Product finding" paragraph (90–120 words) + bold lesson | **DIFFERENT**: BTC has no intro paragraph; its steps carry the story. Keep at most 2 sentences or cut |
| 3 | **6 KPI tiles**: Depositors own (BTC, $) · Public since (+ chain, builders) · Paid (since launch; this month) · Without rewards (est.) · Depositors (count) · LTV (+ liquidation LTV) | 6 tiles: Whole-product capital at T · Holder addresses at snapshot · Fees · Contract deployment ("not public launch") · Observed 30-day ETH book return · 30-day excess vs stETH; each with a caveat sub-label | **REWRITE**: Depositors own (ETH, $) · Live since · Paid (ETH a year, vs stETH) · Without rewards · Depositors · LTV/HF (+ liquidation line). Drop the caveat sub-labels |
| 4 | **How the money moves**: 1-sentence caption ("Out along the top, back along the bottom. The loop: …"); legend by asset (BTC/kBTC, dollars, PRIME, rewards); **SVG flow, 7–9 boxes on two rows** with real names, sizes, contract addresses, numbered circles 1–9 and a labelled loop arrow; boxes link to contracts/markets | Generic **4-box strip** (`strict.js` `routes[...]`): "LiquidETH shares / Staking collateral / Dollar loans / Dollar vault claims", edge labels "Collateral / book · Borrowing leg · Investment route", one dashed loop on Liquid only; caveat note ("Twelve ordered same-token borrow/deposit links are verified…"); no legend; no return path | **ETH MISSING (largest visual gap)**: build BTC-style flows: two rows (out/back), legend, 7–9 named boxes with amounts and addresses, numbered circles matching the steps, loop arrows (Liquid→Sentora vaults that lend back; Avant→own savUSD; YieldBasis→own pool) |
| 5 | **Numbered steps** 1–9 under the flow: each 1–2 sentences with numbers and addresses; last step = exit time | "The route back to the investor" box (generic 5-step sentence + "This is the sequence to verify…"), then 8–9 numbered steps written as instructions ("Receive LiquidETH.", "Pay for the funding."), each ending in "Contract / source → ↗" | **REWRITE** the steps BTC-style: declarative, with numbers, contract links inline. **REMOVE** the "route back to the investor" box; the last step covers the exit |
| 6 | **Who is in the chain, and what each can change**: WHO · ROLE · CAN CHANGE · DELAY, 6–8 rows covering token issuer, vault admin, strategist, withdrawal keys, lender vaults, issuer of parked asset, oracle, venue; caption with read date; 1 note (SEC memo) | "People, contracts and control": ACTOR · CONTROL · DELAY (renderer has 4 columns; Liquid shows 3 rows: "Veda RolesAuthority", "Owner role 8", "Role 55 fee updater") | **ETH MISSING**: rows for the token issuers (ether.fi weETH, Lido wstETH), the strategist (Nonce), Sentora's lender-vault owners, the PRIME issuer (Hastra), the oracle, the venues (Aave/Spark/Morpho). **REWRITE** role names into plain words |
| 7 | — | "Fee changes and actual platform payments" (Liquid) | ETH EXTRA → fold one sentence into a "What moved it" event |
| 8 | **Who pays the yield**: 5–6 label/value rows with $ (Rewards $1.54M of $1.89M, 82%; loop legs −$0.25M; PRIME legs +$0.60M; Who keeps what; Depositors got) | "Who pays the income?": INCOME SOURCE table with 3 generic rows and no $; FIFO/LIFO paragraph; plus "Distribution incentives and reward budgets" | **REWRITE** as BTC rows with $: Merkl rewards $2.6M/yr (issuer side); base yield $4.7M; interest −$14.1M; ETH loop (staking spread) +$X; fees; depositors got 3.2% (+0.7 pp vs stETH). **MERGE** "Who pays the rewards" (Merkl table, currently further down) into this block |
| 9 | **By loan leg** bar chart (Kraken): normal interest / rewards / loan cost per leg, gap labels | "Collateral and borrowing legs" **table** (9 legs, debt, HF, APR) | **DIFFERENT**: replace the table with the BTC bar chart (per leg: earn vs loan cost, rewards split); the table goes behind "Table" |
| 10 | — | "Withdrawal evidence" (2,822 payouts; 1/10/30% table of "Aggregate request untested / Not established") | **ETH EXTRA → REMOVE** (the table says nothing was established) |
| 11 | — | "Risk and exit" paragraph | KEEP the paragraph (good, findings-only) but move it up as the chapter lede, replacing #2 |
| 12 | — | Health factor, month-end chart | DIFFERENT: BTC shows LTV in a tile and a stress chart. Keep as the BTC-style **stress chart** only where an event exists |
| 13 | **Yield vs loan cost** chart: paid to depositors, same without rewards (model), borrow rate; 1-sentence finding as caption | "Loan rate against what the dollars earn" chart (no finding caption) | **SAME** chart; **ADD** a finding caption and a "without rewards" line |
| 14 | — | "How much of the dollar debt can be repaid, and how fast" bars + "Repayment ladder" 5-row table + footnote | **ETH EXTRA**: strong finding (26% unmatched). Keep one sentence and the bar chart; table behind "Table" |
| 15 | — | "Who pays the rewards" Merkl table | MERGE into #8 |
| 16 | — | "Dollar funding history" chart (7 series) + 24-row monthly table + long caption | **ETH EXTRA → MOVE to exhibits** (merge its point into #13) |
| 17 | **BTC in the vault, month-end** chart + decomposition caption ("83% new deposits, 17% BTC price, 0.3% yield") | "Capital and investor outcomes / Whole-product capital history" chart + 24-row table + accounting-bridge paragraph | **SAME** chart; **REWRITE** the caption BTC-style ("Growth: 66% new shares, 34% share price"); table behind "Table" |
| 18 | (inside the Yield chart) | "Book share return in ETH" chart + 30-row table with a repeated "E3 funding reference" column; "Matched return windows" table | **MERGE** into #13 (yield chart in % a year vs stETH); the windows go to the Other carry share-price table |
| 19 | — | "What supports the book value?" (3 boxes, Monad note, 5-row Monad table, **60-row valuation table**) | **ETH EXTRA → MOVE to exhibits** (Liquid only; 1,000+ words) |
| 20 | — | "Dollar borrowing before the current Morpho routes" chart | **ETH EXTRA → REMOVE** (covered by the waves chart and the events) |
| 21 | **Share of BTC by wallet size**: one bar chart (7 buckets) + 1–2 sentence finding | "Who holds the shares?" paragraph + 10 bars split by chain + distribution table + top-20 holder table + custody look-through table + caveats | **REWRITE**: one chart, one finding sentence ("11 wallets hold 70%; one Cash hub holds 21% for 7,012 accounts"). Holder tables → exhibits |
| 22 | **What moved it**: 5 dated events, each with a title and an **outcome line about deposits/flows** | "What changed, and when?" 4 events + "Additional dated strategy and distribution events" (5 more), each ending "Primary evidence → ↗"; events are contract milestones, not deposit drivers | **REWRITE**: at most 5 events, each with its effect on deposits or yield (e.g. "Aug 2025: first Aave USDC loan, $47M" → "book −10k ETH by Nov"); link the date, drop "Primary evidence →" |
| 23 | **Stress chart** (Kraken June fall): market collateral + BTC price, ▲ repay days, finding headline | — | **ETH MISSING**: add for Lido Earn (rsETH freeze, 27 days) or Liquid (HF 1.027 loop in an ETH drawdown) |
| 24 | — | "Read the complete product evidence" links | **REMOVE** (one link in Data is enough) |

Per-product charts: **BTC** has 3–5 per product (month-end size, yield vs loan, wallet sizes; plus loan legs and stress for Kraken). **ETH** has 6–8 per product (HF, rate vs earn, repayment ladder, funding history, capital, share return, wallets, plus Liquid's extra borrowing chart) and 6–9 data tables per product, several with 24–60 rows.

### 4c. Closed tab

| BTC | ETH | Verdict |
|---|---|---|
| 3 cards (Maple, Hermetica, Acre): size now and peak, status/date, 1-line mechanism, Promised · Really earned/Paid · What broke · Outcome, **Lesson.** | Intro paragraph (Rocksolid "Closing… remain unestablished") + 2 Origami cards ("E3 · adjacent precedent… Deprecation alone is not evidence of failure"), closing caveat | **REWRITE**: Reservoir ETH Yield (peak 4,137 ETH Oct 2025 → 24), TAU InfiniFi (wound down), Rocksolid (closed 29 Sep, reopened 7 Oct) in BTC card format with a lesson each. **REMOVE** Origami (not carry) |

---

## 5. Other carry

| Element | BTC | ETH | Verdict |
|---|---|---|---|
| Head | "4 · OTHER CARRY / Every product that borrows against BTC"; "Live, small and closed, with what each really paid." | "03 · OTHER CARRY / Every other product that borrows against ETH"; lede about private mandates | SAME (ETH lede fine) |
| Table | 23 rows **including the top 5**; PRODUCT · STATUS · WHAT IT DOES · REAL YIELD (BTC) · SIZE · BIGGEST RISK | 9 rows **excluding the top 5**; PAID, A YEAR (30 DAYS) with "vs stETH" · SIZE · **WHAT TO TAKE FROM IT**; footnote + "Status and size CSV" | **DIFFERENT**: include the top 5 so the table is the full census; rename the last column "Biggest risk"; **REMOVE** CSV |
| Coverage sweep | Long "Checked on 24 September: no large live carry product is missing…" paragraph (venues swept, 27 wallets over $20M traced, unfinished chains) | Missing; replaced by "Borrowing against ETH establishes financing. Carry also needs an evidenced investment leg. Discovery boundary and remaining gaps →" | **ETH MISSING**: add the sweep paragraph (venues, threshold, what was found, what is unfinished) |
| Products awaiting dollar-carry verification | — | An empty table ("No verified observation.") + 4 classification rows (yoETH, 9Summits, ynETHx, Lucidly) + 3 links | **ETH EXTRA → REMOVE**; one sentence in the sweep paragraph covers it |
| Largest borrowers | "The largest BTC-collateral borrowers on Ethereum: who they are"; 1-paragraph lede; **29 rows, all >$20M stablecoin debt**; WALLET · VENUE · BTC COLLATERAL · DEBT · WHO · EVIDENCE; one-line evidence | "The largest ETH-collateral borrowers in the captured sample"; 2 stat tiles (237 positions, 213 groups), 3 caveat paragraphs, CSV button, **237 rows**, WETH-loop wallets mixed with dollar borrowers, **189 rows saying "Only the sampled chain/address… have not been verified."**, 24 "Full trace in Borrower identities." | **REWRITE**: BTC format, **dollar debt >$20M only** (about 6–10 wallets: Concrete Delta, Liquid ×2, rSHARE managers ×3, Fasanara, …), 1-line evidence each. Drop the tiles, the caveats, the WETH loopers and the unknown rows. Full sample → exhibits |
| Share prices | "Share prices since launch: what the vaults actually paid"; 1 line chart (3 carry vaults) + table VAULT · 30 D · 90 D · 1 Y · ADVERTISED | "Compare returns in ETH": "What happened to 100 ETH?" chart with **Liquid vs stETH, weETH, Fluid Lite, Treehouse, CIAN** (mostly leveraged staking, not carry), Chart/Table/CSV/JSON/SVG, window selector + table, 3 findings, **exit-fee table** | **REWRITE**: chart the carry products (Liquid, Lido Earn, Avant savETH, Liquity, YieldBasis) against a stETH benchmark line; table 30d · 90d · 1y · advertised. **REMOVE** the exit-fee panel, the 3 findings and the export buttons |
| Protocol capital over 24 months | — | Protocol selector (Lido, Binance, Aave V3, EigenCloud, …) + $ chart + 3 links | **ETH EXTRA → REMOVE** (duplicates the market history; includes money markets) |
| Transition line | — | "Across these products, the recurring problems are… Those become the risk checklist." + "Risks and unwind checks" disclosure | **REMOVE** |

---

## 6. Risks

| Element | BTC | ETH | Verdict |
|---|---|---|---|
| Head | "5 · RISKS / What breaks carry products"; lede is a **finding**: "In 2025 and 2026 the losses came from the parked dollars and from keys, not from Bitcoin's price." | Same H2; lede "Measured examples and the conditions that affect collateral, repayment and withdrawals." (a description) | **REWRITE** the lede as a finding (e.g. "In ETH carry the cost comes from the loan currency and the restaking token, not from ETH's price.") |
| Table | 10 rows; RISK · SEEN · WHAT GOOD LOOKS LIKE | 8 rows; RISK · WHAT WE SAW · RULE FOR A PRODUCT | SAME format. **ETH MISSING rows**: "The borrow market fills up" (Aave USDC 13.93% is exactly this), "A price feed blind to the token" (weETH/rsETH exchange-rate oracles), "A slow exit" (Avant 7 days + bridge, Royco epochs, Lido queue), "A thin legal wrapper". Rename the last column "What good looks like" |

---

## 7. Data

| Element | BTC | ETH | Verdict |
|---|---|---|---|
| Head | "7 · DATA / Method and sources"; "Figures as of 20 September 2026 unless marked." | Same | SAME |
| Coverage table | — | "Coverage by mechanism" 7×5 table | **ETH EXTRA → MOVE** into the method text or exhibits |
| Method | Bold-lead paragraphs: **Counting · Left out · Categories and switches · Money markets and CDPs · Judgement calls · Not verified** | **What is counted · Counted once · On-chain books · What was cut**; 5 download buttons (Map, month-ends ×2, netting ledger, product notes) | **ETH MISSING**: "Judgement calls" (Concrete Delta excluded, rSHARE private, Rocksolid/Liquity overlap, YieldBasis counts depositor equity, Liquid's ETH loop counted as carry) and **"Not verified"** (who funds the RLUSD/PYUSD Merkl budgets, rSHARE principal, Fasanara link, …). Downloads → one repository link |
| Listed, not counted | 1 lede + 21 rows: PRODUCT · TYPE · YIELD · SIZE · WHY | Long lede + 33 rows with KIND, date and overlap notes | SAME format; **TRIM** the overlap notes to one clause |
| DefiLlama rows left out | 1 "Left out" paragraph in the method | **100-row table** "DefiLlama rows the map leaves out" | **ETH EXTRA → MOVE to exhibits**; keep a 2-sentence "Left out" paragraph |
| DefiLlama check | "The DefiLlama check, 23 September": ADDED · CATEGORY · BTC · WHY (+2,139 BTC) + "Seen but not added" | "The DefiLlama cross-check": 97.3% coverage, 4 left-out pools | SAME purpose; ETH lacks the "what we added because of the check" list. Fine if nothing was added: say so in one line |
| Re-check | 28 rows with a SOURCE AND NOTE column; on-chain carry rows re-read; rows that moved >10% | 15 rows, no source column, DefiLlama gross only; carry products not re-read | **ETH MISSING**: re-read the 5 carry products on-chain, add a source column and the rows that moved most |
| Sources | ~80 named links (product docs, explorers, governance, filings) | 6 "library" cards (Team briefing, Interactive research exhibits, Yield strategy universe, Carry product evidence, Coverage and remaining gaps, Data and collection method) + 5 buttons (Market ledger, Carry census, Evidence ledger, Print / PDF, Original BTC Research) | **ETH MISSING**: a plain list of named source links (ether.fi Liquid docs, Lido Earn/Mellow, Avant, YieldBasis, Liquity/Ebisu, Sentora/Merkl, Aave/Spark/Morpho markets, Hastra PRIME, rsETH incident, etc.). **REWRITE** the library cards as one line of links, as in BTC ("Dossiers… · Audit… · Main report…") |

---

## 8. Elements on ETH with no BTC counterpart (remove or move to exhibits)

| ETH element | Where | Words | Action |
|---|---|---|---|
| Category table under the donut | Market | ~60 | Remove (replace with the donut legend) |
| Second switch set in the history panel | Market | ~30 | Remove |
| "Change by category" + cohort toggle | Market | 114 | Exhibits |
| By chain (chart + 52-row table + buttons) | Market | 474 | Exhibits |
| "What the evidence supports" label, "Product data" buttons | Top 5 | — | Remove |
| "The route back to the investor" box + 8 instruction steps | each product | ~250 each | Rewrite as BTC numbered steps |
| Withdrawal evidence (1/10/30% "untested" table) | Liquid, Liquity | ~80 | Remove |
| Dollar funding history + 24-row table | each product | ~300 each | Exhibits |
| Book share return 30-row table | each product | ~600 each | Behind "Table" or exhibits |
| What supports the book value + 60-row valuation | Liquid, Liquity | ~1,200 | Exhibits |
| Dollar borrowing before Morpho chart | Liquid | ~60 | Remove |
| Holder top-20 and custody look-through tables | each product | ~250 each | Exhibits |
| "Additional dated strategy and distribution events" | Liquid, Lido | ~200 | Cut to 5 events total |
| Products awaiting dollar-carry verification | Other carry | 187 | Remove |
| Borrower sample tiles + 237 rows | Other carry | 8,377 | Cut to the >$20M dollar-debt rows |
| Exit-fee panel + 3 findings + 100 ETH extras | Other carry | ~350 | Remove |
| Protocol capital over 24 months | Other carry | 252 | Remove |
| Coverage by mechanism table | Data | ~120 | Fold into the method |
| DefiLlama rows left out (100 rows) | Data | 1,280 | Exhibits |
| Library cards, ledgers, Print, Original BTC buttons | Data | ~140 | One line of links |
| CSV/JSON/SVG export buttons (×10+) | throughout | — | Remove (BTC has none) |
| "Hover a month… / Focus or hover…" hints (×13) | throughout | — | Remove |
| ↗ markers (910 in the dump) | throughout | — | Remove the glyph; BTC links are plain |

## 9. Elements on BTC missing from ETH (add)

1. BTC-style SVG money-flow diagram per product (two rows, legend, 7–9 named boxes with amounts and addresses, numbered circles, loop arrows, linked boxes).
2. KPI tiles in BTC's set: Depositors own · Live since · Paid · **Without rewards** · Depositors · LTV.
3. "Who is in the chain" rows for the token issuer, strategist, lender vaults, issuer of the parked asset, oracle and venue, in plain words.
4. "Who pays the yield" with dollar amounts and the reward share.
5. A "By loan leg" bar chart (earn vs loan cost per leg, rewards split) for Liquid.
6. Finding captions on every chart (BTC: "The payout fell because the loan got dearer…").
7. "What moved it" events with deposit or yield outcomes.
8. One stress-event chart (rsETH freeze at Lido Earn, or Liquid's HF in a drawdown).
9. Closed tab as BTC cards with a **Lesson.** each.
10. The Other carry table including the top 5, with a "Biggest risk" column.
11. A "Checked on …: no large live carry product is missing" sweep paragraph.
12. Risk rows: borrow market fills up, price feed blind to the token, slow exit, thin legal wrapper.
13. Method paragraphs: Judgement calls; Not verified.
14. Re-check with on-chain carry rows and a source column.
15. A named Sources list.
16. Donut legend; header stamp with the ETH price; OG/Twitter meta, og.png, favicon, theme-color; "Atlas" naming; BTC-style footer.

---

## 10. Tone

**BTC**: short declarative findings with numbers; no caveats on the page (they sit in the method's "Not verified" paragraph); every chart caption is a finding; one hedge word ("est.", "about") at most. Example captions: "Every week the USDC earns less than the loan costs." / "Deposits came when BTC fell, whatever the vault paid."

**ETH**: audit-report register. Measurement jargon ("at T" ×35, "E3 funding reference", "book NAV", "nested book claim", "promoted to proven cash liquidity"), instructions to the reader ("Do not assign…", "must not be confused…", "This is the sequence to verify"), and a caveat attached to most numbers. The ETH product verdicts and the "Risk and exit" paragraphs are already in BTC tone; the surrounding scaffolding is not.

### The 20 worst ETH hedge/caveat sentences (verbatim)

1. "Only the sampled chain/address, collateral and debt are established. Funding destination, outside depositors and strategy purpose have not been verified." (repeated **189** times in the borrower table)
2. "No simulated transfer trace or T implementation binding is available for this nested receipt, so a successful return is not promoted to proven cash liquidity." (Liquid, backing)
3. "The sample represents about 78.36% of the markets' asynchronously reported debt; it is a coverage diagnostic, not an exact reconciliation or a whole-market concentration measure." (borrowers)
4. "Borrowing against ETH-family collateral does not by itself establish reinvestment, beneficial ownership or a carry trade." (borrowers)
5. "Twelve ordered same-token borrow/deposit links are verified in the common income window; other financing remains unassigned." (Liquid flow note)
6. "Owner delay does not prove this route has a delay" (Liquid, control table)
7. "This explains the distribution incentive; the ecosystem budget is not a measured payment to this vault or organic carry income." (Liquid)
8. "Funding cost depends on the actual loan currency and venue; a low quote on one route does not describe the whole carry book." (Liquid)
9. "Net fair value and withdrawal previews are not executable cash; staked gauge returns are separate." (YieldBasis flow note)
10. "Actual fee allocation varies through the contract mechanism; it is not a flat 10% deduction from every holder's gain." (YieldBasis)
11. "Its single address conceals a distribution of claims; these accounts are not necessarily different people." (Liquid holders)
12. "Omitted positions, accrued costs and ownership rights stay explicit; no balancing entry is invented." (Liquid backing)
13. "An unmapped amount, not an established deficit or investment loss." (Liquid backing)
14. "These are alternative scopes, not positions to add together." (Liquid backing)
15. "This is an accounting bridge, not a cash-flow or carry-profit estimate." (Liquid capital)
16. "Portfolio size alone does not establish how much can be redeemed immediately." (Withdrawal evidence)
17. "Completion of closure, its reason and the complete investor outcome remain unestablished." (Closed tab)
18. "Closure date, cause and investor loss are not established by the documentation. Deprecation alone is not evidence of failure." (Closed tab, twice)
19. "The table uses checked or current published terms; it illustrates their effect on old book returns. It does not show a realised historical withdrawal." (exit-fee panel)
20. "Its history must not be confused with the current LT receipt." / "It reports an allocation adjustment from 55% to 45%; this is not an investor yield promise." (YieldBasis events)

Also recurring: "Same dates; whole book, not carry profit" (KPI sub-label on every product), "Deployment, not public launch", "Missing and unfunded periods stay absent", "Unfunded / unavailable" (78 table cells), "dated aggregator price; timestamp and source in raw pilot_prices_T; reward ownership requires checking" (41 cells), "Primary evidence → ↗" (22), "Contract / source → ↗" (30).
