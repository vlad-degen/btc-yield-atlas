# Audit 3: ETH library, exhibits, deep dives and published files

Branch `codex/eth-research`, checked 7 Oct 2026. Read-only. The reference throughout is the main page `eth/index.html` as rendered:
- 18,349,193 ETH in 170 products, each counted once.
- Carry is 306k ETH in 14 products, with $261M of debt.
- The top five are ranked by **dollars borrowed** (Liquid, YieldBasis, Lido Earn, Avant, Liquity).
- Concrete Delta is left out as one wallet's own position.
- Rocksolid closed on 29 Sep and reopened on 7 Oct.
- Liquid beat stETH by **+0.66 pp a year** (3.37% vs 2.71%).

Method:
- Grepped all 54 `research/eth/en` sources (ARTICLES in `tools/eth/site.py`) for stale markers.
- Compared paragraphs across all article pairs (shared paragraphs over 150 chars).
- Rendered `eth/exhibits.html` locally and searched each section's text.

Status codes:
- **A**: consistent with the main page.
- **B**: stale or contradicts the main page.
- **C**: internal process note, not meant for readers.
- **D**: duplicate of another article.

## 0. Headline facts

- **CARRY-CATEGORY.md and ECONOMIC-ANSWERS.md are byte-identical** (diff is empty, and they have the same title). The main page links ECONOMIC-ANSWERS twice.
- **The library is the size of a book and points readers to stale material.** It has 54 articles and about 85k words. The library index sends readers to BRIEFING, MARKET-STRUCTURE, CARRY-CATEGORY and MARKET-COVERAGE. MARKET-COVERAGE and CARRY-CATEGORY are partly stale. The build stamps a "Current report · 6 October" banner on CARRY-PRODUCTS, and that article still ranks Concrete #1.
- **Heavy overlap between articles:**
  - MARKET-STRUCTURE repeats 78% of its paragraphs in BRIEFING.
  - BRIEFING shares 35% with CAPITAL-INCOME-EXIT.
  - CARRY-CATEGORY shares 27% each with BRIEFING and CARRY-PRODUCTS.
  - pendle-pt shares 23% each with MARKET-COVERAGE and STRATEGY-UNIVERSE.
  - etherfi-liquid-eth shares 26% with PRODUCT-EVOLUTION.
  - The block "Native stake: measured backing" is pasted into 4 articles.
  - The block "Two additional dollar investment and funding ledgers" is pasted into 4 articles.
- **The ETH study has no Russian report.** `research/eth/*.md` (16 Russian files) is the 3 October first edition. Nothing in it reflects the netmap, the Concrete exclusion or the debt-ranked top five. None of it is in ARTICLES.

## 1. The 54 articles

### Dossiers (12, `eth/dossiers/`)

| Article | Status | Contradicting text / note | Recommendation |
|---|---|---|---|
| etherfi-liquid-eth | B, D (26% with PRODUCT-EVOLUTION) | "+1.36 pp over two years alongside a 13.3× allocation" (main: +0.66 pp/yr); "The unexplained $12.453M, or 2.634%, remains unresolved." | MERGE into the new Liquid deep dive (top5/01) |
| carry-credit | B (3 Oct) | "## Cap and the unresolved Yuzu allocation"; Liquid sleeve look-through superseded by TOP5-RISK ladder | MERGE into Liquid deep dive §C |
| liquid-monad | A (Liquid sub-sleeve) | -- | MERGE into Liquid deep dive §C |
| concrete-eth | B | "Beneficial ownership, investor agreements and attributable custody backing remain unresolved."; "## Findings for colleagues"; "$823M cannot be described as new external ETH deposits" (answered by CONCRETE-DELTA) | REMOVE; move the ctwstETH Plus paragraph into CONCRETE-DELTA |
| fluid-lite | A | Leveraged-staking case | MERGE into "Other ETH strategies" annex |
| treehouse-teth | A | same | MERGE into annex |
| cian-rseth | A | same | MERGE into annex |
| staking-restaking | A | Category background | MERGE into annex (staking/restaking) |
| lending-lp | A | -- | MERGE into annex (money markets / LP) |
| pendle-pt | A, D (23% with MARKET-COVERAGE and STRATEGY-UNIVERSE) | -- | MERGE into annex (fixed yield) |
| ethena-basis | A | Basis is 372 ETH on the map | MERGE into OUTSIDE-AND-SMALL (small categories) |
| justlend-tron | A | Niche | MERGE into OUTSIDE-AND-SMALL |

### Library (42, `eth/library/`)

| Article | Status | Contradicting text / note | Recommendation |
|---|---|---|---|
| README | A | Index | REWRITE as the index of the new structure |
| BRIEFING | top A; tail B | Top matches the main page. Appended tail: "All eleven detailed products have the same 2 September to 2 October..."; "Concrete is an unresolved case, not a verified member of the five." (l.149); pasted native-stake / ledgers / product-history blocks | REWRITE: becomes the skeleton of the Russian REPORT (cut everything after "Reproduce the answers") |
| MARKET-STRUCTURE | A, D (78% in BRIEFING) | -- | MERGE into REPORT §Market |
| MARKET-RESEARCH | B (first edition, 3 Oct) | "## Concrete changes TVL interpretation … The remaining work is to establish the original portfolio, holders' economic rights…"; "$70.939B" candidate TVL; "12 dossiers, 25 evidence claims" | REMOVE (git history keeps it) |
| MARKET-TABLES | B (protocol-panel era) | DefiLlama protocol rows "USD carry / hybrid parents" (Concrete 953.047, Liquid 402.665); "Concrete's flat share price … private payouts … remain unresolved" | REMOVE (netmap CSVs replace it) |
| MARKET-COVERAGE | B | "Thirteen examined books; ten current traced routes"; "Rocksolid is Closing, TAU's current debt is dust…"; "Native consensus balances are outside the protocol panel." | REWRITE into METHOD §coverage (keep the family × evidence matrix) |
| CAPITAL-INCOME-EXIT | B | "The default market chart measures 21.158M ETH equivalents across dated protocol layers."; Concrete Delta "$339.412M" unmapped (CONCRETE-DELTA: Safe covers 99.96%); Rocksolid "$19.852M" of $25.953M unmapped (= the 76%); "The T contract state is Closing."; "Final public-record edition, reviewed 4 October" | REWRITE: move the earned-income ledger to Liquid §E and exits to each deep dive §F; drop "Unique capital" |
| PRODUCT-SELECTION | A, but one stale reason | "Concrete is excluded until shared-wallet ownership is reconciled" (it is reconciled: one wallet's position) | REWRITE as `00-selection` in BTC form |
| CARRY-CATEGORY | B (partly) | "The default protocol panel contains 178 observed parents…"; "## Why Concrete is outside the verified five … the records do not assign its backing or debt wholly to Delta"; table lists 13 products (main: 14); "top two account for 79.94%" (main: 85% of book) | REWRITE as REPORT §Carry, or MERGE into 00-selection |
| ECONOMIC-ANSWERS | D (identical to CARRY-CATEGORY) | same | REMOVE; repoint the 2 main-page links |
| CARRY-PRODUCTS | B | "The current five largest are Concrete, Liquid, YieldBasis WETH, Rocksolid and Liquity"; "The ordering uses whole-product book NAV"; "## 1. Concrete Delta weETH"; Liquity "published as Liquity/BOLD" (now Ebisu/ebUSD); stamped "Current report" by the builder | SPLIT: per-product parts into deep dives; Makina/Vesper/ZenSats/Royco into the "Other carry" annex; then REMOVE |
| PRODUCT-EVOLUTION | B | "explains the history behind the five largest examined books" (includes Concrete, omits Liquity); "Its place at the top of the book-size table…"; "The main report retains the BTC eight-chapter route" | SPLIT the timelines into deep dives §I; REMOVE |
| TOP5-RISK-LIQUIDITY | A | -- | SPLIT into deep dives §F (HF series, ladder) and §J (rewards) |
| CARRY-MATH | partly B (4 Oct; carry math was dropped from the main page) | RLUSD worked leg, calculator, "Four Playbook tables" | MERGE the RLUSD leg into Liquid §E; rate models into METHOD; drop the playbook |
| BORROW-HISTORY | A | Liquid rate history | MERGE into Liquid §E/§F |
| ECONOMICS | A (3–4 Oct) | Liquid loop stress, +100 bp shock | MERGE into Liquid §F.4 (stress) |
| RETURN-DRIVERS | partly B | Liquid capital-growth split (useful); "Sampled position debt totals $465.257M…" (old borrower sample) | MERGE the Liquid parts into §H/§J; REMOVE the rest |
| PRODUCT-TERMS | B | "## The five carry products … the main website's ranked carry chapters" table = Liquid, Concrete Delta, Rocksolid…; "private investor fees remain unresolved" | SPLIT the fees/exit/control into deep dives §D; REMOVE |
| HISTORY | partly B | "## History of the 25 largest observed protocols" (protocol API panel); comparable book-return table is fine | REWRITE: keep the return table in REPORT; drop the protocol history |
| MECHANICS | A (3 Oct, generic E1–E9) | Explains generic DeFi to Babylon readers | REMOVE, or reduce to one METHOD paragraph |
| LENDING-MARKETS | A | WETH lending, Liquid = 23.28% of Aave WETH debt | MERGE into REPORT §Market (money markets) |
| DEPENDENCIES | A (3 Oct diagrams) | -- | MERGE the shared-dollar-vault contagion into REPORT §Risks; REMOVE |
| DOLLAR-FUNDING-ATLAS | A | 13.93% USDC / 4.38% USDT | KEEP as an annex, or MERGE into REPORT §Carry |
| STRATEGY-UNIVERSE-EXPANSION | partly B | Banner "Earlier discovery-only decisions below describe the prior screen" | MERGE into the "Other ETH strategies" annex |
| CARRY-VARIANTS-EXPANSION | partly B | Same banner; "## Concrete's book identifies a manager claim, not a loan attribution" (superseded) | MERGE Reservoir/TAU/Midas into the "Other carry" annex |
| PRODUCT-FINANCIAL-HISTORY | partly B | Same banner | MERGE the YieldBasis denominator into YB §A; the rest into the strategies annex |
| CARRY-LIFECYCLES | A, D (12% with BRIEFING/CAPITAL/CARRY-MATH) | -- | MERGE the Lido 5M lot into Lido §E; the 3 lots into the "Other carry" annex |
| CREDIT-EXPANSION | A (partly superseded) | -- | MERGE into the BORROWER-IDENTITIES annex |
| BORROWER-USE | A, superseded | "authorized users unresolved" | MERGE into BORROWER-IDENTITIES |
| HGETH-LOAN-BOOK | A, niche | -- | MERGE into the strategies annex |
| CARRY-COVERAGE-AUDIT | A (updated 7 Oct) | -- | MERGE into 00-selection (candidate dispositions) |
| CONCRETE-DELTA | A | -- | KEEP (annex: excluded mandates) |
| ROCKSOLID-NEMO-SENTORA | A | Title "gap closure" is internal wording | KEEP; retitle |
| BORROWER-IDENTITIES | A | -- | KEEP (with CONCRETE-DELTA: "private mandates") |
| OUTSIDE-AND-SMALL | A | -- | KEEP |
| AUDIT | A, meta (3 Oct numbers: "Of 87 selected protocols…") | -- | REWRITE as the ETH `AUDIT.md` (netmap checks, re-check 7 Oct) |
| EVIDENCE | C/meta | "C22 leaves global totals unmeasured…" | MERGE into AUDIT |
| methodology | partly B (pre-netmap three-layer accounting) | -- | REWRITE into METHOD with the netmap counting rules |
| scope | A, dated 3 Oct | -- | MERGE into METHOD |
| RESEARCH-PLAN | C | "Research is underway… rankings and market totals require verification before publication"; links BTC PROJECT-KNOWLEDGE | REMOVE from public |
| EXECUTION-CHECKLIST | C | "- [x] Rocksolid Closing state…", "colleague briefing edited" | REMOVE |
| SITE-PARITY | C, B | "The presentation follows the eight chapters"; "all seven products"; "adapter" | REMOVE |

**Tally:** 9 KEEP or REWRITE as core; about 30 MERGE or SPLIT into deep dives and annexes; 9 REMOVE outright (MARKET-RESEARCH, MARKET-TABLES, ECONOMIC-ANSWERS, concrete-eth, RESEARCH-PLAN, EXECUTION-CHECKLIST, SITE-PARITY, MECHANICS, DEPENDENCIES).

### `eth/exhibits.html` sections (rendered)

This page is the old 8-chapter "complete" edition with the netmap hero restored. It is titled "Supporting exhibits", and the main page links to it 9 times.

| Section | Status | Contradicting text | Recommendation |
|---|---|---|---|
| top | B | "Review · 4 Oct 2026"; "Liquid ETH's book share return exceeded stETH by 1.36 percentage points over two years" (main +0.66 pp/yr); "-2.23% two-year change, 102 selected protocols held fixed" (main: -8% from peak, netmap) | REMOVE |
| map | mixed | The top matches the main page. Below that come the protocol-panel exhibits: market-net-capital (457k ETH custody floor), strategy-atlas, additional-product-history, hgeth-loan-book, market-method ("ETH equivalents are reported USD divided by … Lido balance") | REMOVE; strategy-atlas/hgETH become an annex if wanted |
| how | partly B/C | carry-earned-income, dollar-funding-atlas, carry-variants, worked RLUSD example, calculator. These were dropped from the main page on purpose | MOVE carry-earned-income to Liquid §E; drop the rest |
| top5 | B | "Five product books. Five investor questions."; matrix "#7 Concrete Delta weETH, #12 Rocksolid rETH…"; "Rocksolid is in Closing and rejects new requests"; "beat stETH by 1.36 pp (3.37% vs 2.71% a year)" (internally inconsistent: 3.37-2.71=0.66) | REMOVE; investor-exits table moves to deep dives |
| market | B | Product table column "MAIN UNRESOLVED RISK"; "Concrete wstETH Plus: Material funded product; carry route unresolved"; "Closing at T." | REMOVE (main §Other carry replaces it) |
| risks | A | -- | Already on the main page |
| do ("06 · PLAYBOOK") | C/legacy | Playbook deliberately removed from the main page (colleague-readiness.md) | REMOVE |
| data ("07 · DATA") | B | "The original 85 adapter rows, 5,688 symbol candidates and five deep carry chapters…" | REMOVE |

## 2. Is there an ETH REPORT.md and research/top5?

**There is no Russian full report** (BTC `REPORT.md` is 178 KB, 1,372 lines). The closest things are BRIEFING.md (English, about 2k words, with a stale tail) and the main page itself. The Russian `research/eth/*.md` files are the 3 Oct first edition and contradict everything after the netmap.

**There is no per-product deep-dive set.** Per-product content is scattered across:
- CARRY-PRODUCTS (short chapters, ranked by book with Concrete #1)
- PRODUCT-EVOLUTION (Liquid, YB, Lido, Avant, Concrete; no Liquity)
- TOP5-RISK-LIQUIDITY
- PRODUCT-TERMS
- CAPITAL-INCOME-EXIT
- dossiers/etherfi-liquid-eth (Liquid only)
- `data/eth/reader_product_chapters.json` (the main page's tabs)

There is no `data/eth/top5/<product>/` folder. The BTC equivalent is `data/top5/kraken/{events,holders_buckets,holders_types,liquidity_ladder,ltv_weekly,tvl_weekly,yield_weekly}.csv`.

**The ranking metric differs.** BTC `00-selection` ranks by BTC deposits and has an explicit definition, exclusions and reserves (#6–7). ETH ranks by dollar debt. That is fine, but the choice has to be stated as such.

### Gaps against the Kraken template

Kraken template sections:
- Summary (12 findings)
- A Scope
- B Structure/legs
- C Positions
- D Governance
- E Yield history: E.1 monthly, E.2 weekly, E.3 stability, E.4 carry P&L by leg, E.5 negative-carry periods
- F Risk: F.1 LTV over time, F.2 delever events and lag, F.3 liquidity ladder, F.4 stress test
- G Depositors: G.1 buckets, G.2 address types, G.3 holders over time
- H TVL growth
- I Growth drivers (events.csv)
- J Operator economics
- K Verdict: copy/avoid
- Method

Present for all five:
- A to D, in short form (CARRY-PRODUCTS, PRODUCT-TERMS, main page tabs)
- F.1 monthly health factor (TOP5 series)
- F.3 ladder (TOP5)
- Rewards / payers (TOP5)
- 30-day return and monthly book (main page)

Missing for **all five**:
- A numbered findings summary
- E.2 weekly yield; E.3 stability stats; E.5 negative-carry periods as a section (only line items in TOP5)
- F.2 delever events with reaction lag
- G.2 address types; G.3 holders over time
- H weekly TVL with inflow/outflow attribution
- I a dated events.csv per product
- J operator economics (fee revenue vs costs)
- K copy/avoid verdict
- A per-product Method / reproducibility block
- A Russian translation

Per product:
- **ether.fi Liquid ETH** (richest). Has: dossier, rate history (BORROW-HISTORY), stress (ECONOMICS), earned-income ledger, capital-growth decomposition (RETURN-DRIVERS), timeline (PRODUCT-EVOLUTION), holders at T. Lacks: E.4 P&L by leg as one table (loop vs RLUSD/PYUSD/USDC legs), F.2 delevers, G buckets/types, I events.csv, J (fee revenue vs 0.35% NAV fee), K. The 1.36 vs 0.66 pp conflict has to be resolved first.
- **YieldBasis WETH.** Has: a 14-line chapter, PRODUCT-EVOLUTION timeline, denominator note (PRODUCT-FINANCIAL-HISTORY), ybGauge holders CSV. Lacks: E.1/E.2 history beyond monthly since May 2026, E.4 (fees vs 10% crvUSD loan, which is the headline claim), F.4 stress (no-liquidation design vs critical 56.25%), G, H, I, J (admin fee 10%), K.
- **Lido Earn ETH.** Has: CARRY-PRODUCTS fixed-block chapter, timeline, the 5M USDT matched lot. Lacks: E.4 by leg (the wstETH loop at HF 1.035 vs the earnUSD leg), F.2, F.4 for the loop, G (no holder file found), H, I, J, K.
- **Avant avETH/savETH.** Has: CARRY-PRODUCTS chapter, timeline, savETH holders CSV. Lacks: E.1/E.2 history, E.4, F.2, F.4, G.2/G.3, H, I, J (issuer relationship economics), K. Its exit path (savUSD cooldown, bridge, 7 days) appears only in the TOP5 ladder.
- **Liquity ETH Carry** (thinnest). Has: a 16-line CARRY-PRODUCTS chapter (still framed as "Liquity/BOLD"; the route is Ebisu ebUSD), holder distribution at T, TOP5 rows. **No timeline** (PRODUCT-EVOLUTION skips it). It lacks everything in E to K.

## 3. What should not be public

GitHub Pages builds the repo root from `main` (source `main /`, public). Today `main` holds only `eth/` (148.7 MB, 884 data files, 27 qa files). **The branch also tracks four directories outside `eth/`:**
- `data/eth/` (397 files, about 271 MB)
- `research/eth/` (with `review/` 38 files and `finalization/` 23 files)
- `site/eth/` (616 files, about 261 MB, a mirror of `eth/`)
- `tools/eth/`

Every one of them becomes publicly served on merge, not just `/eth/`. Exclude them, or accept that the repo is public anyway; at minimum, don't merge `site/eth`.

Other points:
- `raw/eth` is untracked.
- The ZIP is git-ignored (`eth/.gitignore`), so it is not published, but it is 139 MB, contains 4,936 `raw/eth` files and `eth/qa`, and the README advertises it.

Do not publish:
- **`eth/qa/` (58 files, 2.9 MB).**
  - Screenshots: desktop/mobile png/jpg, `reader-carry-*-oct5/6`, `browser-checks-before-axis-fix.json`.
  - Verification JSONs.
  - `colleague-readiness.md`. It is stale ("thirteen examined products", "the protocol panel is gross reported exposure") and internal ("simplified on 7 October at the user's request").
  - Recommendation: drop the whole folder from `eth/`, or keep only one `audit_results.json` that AUDIT links to.
- **`research/eth/review/*` (35 md plus 7 json) and `research/eth/finalization/*`.** These are plans, parity audits, handoffs, branch-consolidation and publication-verification JSONs, and raw txt captures (avant_addresses.txt etc.). They are not for readers and should not be public: move them to an untracked folder or a private branch.
- **Library articles that are internal notes:** RESEARCH-PLAN, EXECUTION-CHECKLIST, SITE-PARITY (see §1).
- **`eth/data/reference-*` (53 files, 20 MB).** `site.py:92` copies these automatically whenever an article links outside `data/eth`. They include:
  - internal BTC project notes: `reference-PROJECT-KNOWLEDGE.md`, `reference-PROJECT-CODE-INDEX.md`, `reference-RESEARCH-PLAN.md`
  - a copy of BTC `reference-REPORT.md` (178 KB)
  - duplicates of library md: `reference-CONCRETE-DELTA.md`, `reference-TOP5-RISK-LIQUIDITY.md`
  - 9 `.py` build scripts
  - RPC dumps: `reference-yield_pools-…json` is 11 MB
  - Recommendation: stop the copy (link to GitHub instead) and delete them.

**`eth/data` size:** 497 files, 246 MB, of which 223 MB duplicates `data/eth` by name.
- By path strings in the pages: index.html references 139 files, exhibits 149, library and dossiers 180. The union is 267 files (205 MB).
- 230 files (42 MB) are referenced by nothing, for example:
  - `carry_variants_expansion_follow.json` (10.8 MB)
  - `yield_pool_candidates.json` (7 MB)
  - `carry_variants_expansion_bootstrap.json` (4 MB)
  - `funding_borrower_deep_*` (about 6.6 MB)
  - `*_retry_*.json`
  - `research_closure_audit.json`
- Most of the "referenced" volume comes from `sources[].path` hashes embedded in the JSON, not reader links. Examples: `carry_attribution_organic_rpc.json` (19 MB), `parity_depth_op_user_balances.json` (21 MB), `carry_attribution_rpc.json` (16 MB).
- The page runs on its embedded packed data; it does not `fetch()` these files.
- Realistic public data set: netmap CSVs, the product CSVs linked under Data, the gap_* files and a manifest. That is probably under 15 MB.
- If exhibits.html and the library are cut back, about 200 MB of raw RPC JSON can leave `eth/data` and stay in `data/eth` (or in the ZIP).
