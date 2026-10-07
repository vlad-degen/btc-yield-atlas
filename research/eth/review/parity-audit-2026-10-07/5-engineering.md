# 5. Engineering audit: ETH site (branch codex/eth-research @ 59501a0)

Method: read-only on the real repo. Builds ran in an APFS clone (`scratchpad/clone`, with raw/) and a fresh `git clone` of the branch (`scratchpad/fresh`, no raw/). Browser numbers come from headless Chrome via Playwright over a local http.server: V8 precise coverage, a Proxy on `R` that records every payload path read, and a pass that clicks every button, select and details element and scrolls the page.

## 1. Page weight and performance

| | BTC `index.html` | ETH `eth/index.html` (reader) | ETH `eth/exhibits.html` |
|---|---|---|---|
| Raw HTML | 315 KB | 12.99 MB | 13.04 MB |
| Live gzip transfer (Pages) | 102 KB | 1.88 MB | 1.89 MB |
| Inline JSON payload | inline | 12.52 MB (same in both pages) | 12.52 MB |
| JS (11 files concatenated) | | 362 KB | 362 KB |
| DOM nodes after load | 5,021 | 10,626 (2,556 inside `[hidden]`) | 20,238 |
| Visible text | | 28 KB | 114 KB |

Timings, local server, so network time is excluded:
- **Desktop (M-series):** load event at 383 ms; hero filled at 419 ms.
- **Mobile (390 px, 4x CPU throttle):** first contentful paint at 548 ms, but it paints "Loading" placeholders. DOMContentLoaded lands at 1.12 s and the hero fills at 1.23 s. JS heap is about 30 MB.
- **Real mid-range Android:** expect roughly 2-4 s of parse and script work, plus transfer time.
- **Transfer time for 1.88 MB:** about 9 s on Slow 4G (1.6 Mbps), about 1.7 s on 9 Mbps 4G.

Mobile data cost is about 1.9 MB per page, because Pages serves gzip and not brotli. Opening both pages costs 3.8 MB, since the identical payload is inlined twice and cannot be cached across them. Cache-control is 600 s.

**Payload keys the reader actually reads (runtime trace):**
- **Read:** 32 of 50 top-level keys.
- **Never touched (1.94 MB):** assets, balance, basisDisclosures, carryAssets, coverage, credit, economics, edges, etherfi, etherfiHistory, evidence, finalMeasurements, lending, marketPanel (1.55 MB), pendle, reportLibrary, stress, summary.
- **Bound to a const at load but never read into (2.27 MB):** fundingAtlas 755 KB, marketNetting 557 KB, creditExpansion 411 KB, borrowerDeep 253 KB, creditDeep 216 KB, borrowRateHistory 75 KB, managerCase. These are aliases in expansion.js, closure.js and strict.js used only by the exhibits edition.
- **pools (2.10 MB):** only `R.pools.length` is read, from app.js:21 and strict.js:80. One integer costs 2.1 MB.
- **carryAttribution (1.01 MB):** only `top5_coverage` is read (173 B).
- **strategyExpansion (189 KB) and strategyDeep (74 KB):** each reads under 250 B.
- **carryCoverage (103 KB):** 4 KB used. **economicAnswers:** 175 KB of 442 KB used.
- **marketChapter (2.0 MB):** 1.17 MB used. The bulk is `products[].history`, which feeds the per-product charts.
- **borrowersChapter (865 KB):** fully read, including `positions` (503 KB). Check whether `positions` is really needed.

**Minimal reader payload:** about 3.1 MB raw and 0.43 MB gzip, against 12.5 MB raw and 1.75 MB gzip today. This is an upper bound: the trace stops at depth 3 and keeps anything deeper whole. Lazy-loading `marketChapter.products[].history` and the borrower table (fetch when those sections open) would bring the first paint payload to about 1.5 MB raw and 0.2 MB gzip.

**Options:**
- **(a) Per-edition payload in site.py:** a whitelist of keys and fields; small change.
- **(b) Shared payload:** move it to `eth/data/site_payload.json` with `fetch`, so both pages share the browser cache. The cost is that file:// offline use from the zip breaks, so keep inline for the zip build only.
- **(c) Derived scalars:** replace `R.pools` with a `poolCount` scalar, and carryAttribution with `top5_coverage` only.

## 2. Dead code and layering

**Override map.** Function declarations hoist, so the last file in the concatenation wins for both editions:
- market.js `marketRender`, `marketCatalogue`, `marketPersist` and `marketFindings` are replaced by atlas.js.
- strict.js `stRisks`, `stMarketMechanism` and `stMarketOperator` are replaced by atlas.js.
- reader.js `readerCarryWaves` is replaced by atlas.js.
- `readerAnswer` has **7 definitions**: reader.js:185, economic.js:8 and atlas.js lines 123, 143, 264, 273 and 326. The atlas line 123 version is a full replacement, so the reader.js and economic.js bodies are dead. The later four wrap it.
- `readerLandscape` has 3 definitions; reader.js and economic.js are dead.
- `atlasFinal` has 2 definitions, `stRenderProduct` has 2, and reader.js `readerComparison` and `readerPlaybook` are reassigned by economic.js.

**Coverage, as the share of each file's bytes never executed in either edition after full interaction:**

| File | Never executed |
|---|---|
| market.js | 55% |
| reader.js | 50% |
| charts.js | 35% |
| presentation.js | 29% |
| app.js | 20% (renderCian, renderConcrete, renderFluid, renderTreehouse) |
| economic.js | 20% |
| strict.js | 12% |
| atlas.js | 5% (its own `stMarketMechanism`/`stMarketOperator` are never called; `atShareOf` is unused) |
| **Total** | **75 KB of 362 KB (21%)** |

**Reader edition alone:** only 50% of the JS executes. expansion.js runs 1.4%, closure.js 19%, compare.js 20% and app.js 32%.

**Risks of the layering approach:**
1. **Hoisting bleeds across editions.** atlas.js declarations replace market.js functions in the exhibits page too; the last commit, "restore hero after the atlas market override", is exactly this bug. The economic.js:6 line `const previousMarketRender=marketRender` already captures the atlas version, not market.js, so the wrap order differs from the file order.
2. **Every market filter change re-runs the whole answer chain** through `marketRender → readerAnswer`: 5 wrappers, plus `stRisks` and DOM rebuilds.
3. **Old output is rendered and then hidden.** `atHideOld` leaves 2,556 hidden nodes in the reader.
4. **Behaviour depends on file order** in a site.py string, with no tests.

**Proposal:** an explicit `reader.js` entry module with one definition per function, built from atlas.js plus the live parts of strict.js, economic.js, charts.js and reader.js. Keep exhibits on the old stack, minus the dead declarations. Concatenate per edition: the reader drops expansion, closure, compare and presentation. Add a CI check that fails on a duplicate top-level `function` name.
- **Effort:** 2-3 days, including the browser parity check against the current DOM; `qa/reader-btc-parity-dom.json` already exists as a harness.
- **Removing only the duplicate declarations:** about 0.5 day.

## 3. Reproducibility

**Fresh checkout, no raw/:** `rebuild.py` fails at its first step, `netmap/02_screen`, and prints nothing. It uses `capture_output=True, check=True`, so stderr is swallowed.

Run step by step, **43 of 60 steps need raw/eth**:
- **netmap:** 02_screen, 03_build, 04_chapter, 06_crosscheck.
- **Builders:** discover, normalize, pilot_analyze, catalog, pilot_balance, package_metrics, evidence, market_data_probe, carry_economics_build, carry_borrow_history, market_netting_build, carry_attribution_build, carry_attribution_organic, carry_attribution_tranches, backing_exit_build, basis_closure_build, build_product_chapters, strategy_universe_expansion_build, carry_variants_expansion_build, credit_expansion_build, credit_expansion_deep_build, strategy_universe_deep_build, funding_borrower_deep_build, manager_case_build.
- **site.py itself:** its sub-builder reader_carry_build reads `raw/eth/parity-sweep-2026-10-05/yb_monthly_frozen.json`.
- **All verifiers and audits except site_audit and report_contract_verify.**

As a result, nobody can rebuild the page from git alone. site.py is also not just a packager: it runs about 10 data builders and rewrites `research/eth/en/*.md` and data/eth.

**With raw/ (clone):** `rebuild.py` exits 0 in 76 s, including figures; 965 backing checks pass. site.py is **deterministic**: two runs give byte-identical index, exhibits and payload, matching the committed sha 7d1c90f1. Figures are also unchanged. The only diffs are `created_at` timestamps in 8 audit JSONs.

**Stale QA in HEAD:**
- The committed `eth/qa/*` and `data/eth/*audit*` record `site_sha256 587df051…`, not the committed page `7d1c90f1…`. The last commit rebuilt the HTML without re-running the audits or `package_site.py`.
- `package_site.py` would refuse the current tree (`Stale or failed checks`).
- The clone rebuild shows the current page passes; only the records are stale.

**Hardcoded path and dependencies:**
- `rebuild.py:16` defaults `ETH_FIGURE_PYTHON` to `/Users/vladdegen/.cache/codex-runtimes/.../python3`. It skips gracefully elsewhere.
- Third-party Python deps are only PIL and reportlab, in figures.py; everything else is stdlib.
- There is no requirements file, and the Python version is not pinned (tested on 3.14).
- Headless QA relies on the Codex runtime's playwright, which is also not declared.

## 4. Publication hygiene

**Pages setup:** legacy Jekyll build from `main` root, with no `.nojekyll` (`/AUDIT.md` is served as rendered `/AUDIT.html`).

The HEAD working tree is **817 MB**. On merge, everything is publishable:

| Path | Size | Note |
|---|---|---|
| data/eth | 276 MB | |
| eth | 266 MB | eth/data alone is 236 MB |
| site/eth | 266 MB | byte-copy mirror written by site.py; served at `/site/eth/` after merge |
| tools, research | | |

That is about 82% of the 1 GB Pages site limit, with three copies of the evidence. main today is 153 MB. No single file is over the limit (largest 21.6 MB, `parity_depth_op_user_balances.json`). The 146 MB zip is ignored correctly in eth/ and site/eth/.

**Should not be public:**
- **eth/qa (2.9 MB, 58 files):** 25 screenshots (2.4 MB) and `colleague-readiness.md`, an internal review note mentioning "at the user's request". It is rendered by Jekyll and already live at `/eth/qa/`.
- **eth/data/reference-\* (53 files, 19 MB):** copies of research inputs.
- **302 of 497 eth/data files (150 MB):** never linked from any page, mostly `*_rpc.json` RPC dumps of 20, 16 and 11 MB.
- **`site/index.html`:** a stale BTC copy dated 24 Sep, live at `/site/`.

**Git history:**
- **Locally:** 26 versions of eth/index.html plus 25 of exhibits.html add about 386 MB of blobs. The local .git is 621 MB of loose objects that have never been gc'd.
- **On GitHub:** the remote repo is 41.7 MB, because the HTML versions delta-compress well. Growth is roughly 1-2 MB per build and not urgent, but every data change still rewrites two 13 MB files.

**Recommended publish set (eth/):**
- index.html and exhibits.html with trimmed payloads.
- site.css, figures, library, dossiers, and README if wanted.
- eth/data restricted to the about 195 files that pages link (CSV exports plus cited evidence; at most 97 MB, likely about 60 MB).
- Drop qa/ and reference-\*. Stop writing `site/eth` (the zip already covers offline use). Add `.nojekyll`, or `_config.yml` excludes for data/, raw/, tools/, research/ and qa/.
- Better: publish from a GitHub Actions artifact or a `gh-pages` branch built from an allowlist. That keeps the evidence in the repo but off the site; result about 30-110 MB.

## 5. Accessibility and SEO parity with BTC

| Item | BTC | ETH index / exhibits | ETH library and dossiers (55 pages) |
|---|---|---|---|
| lang | en | en | en |
| title | yes | yes | yes |
| description | yes | yes (generic, no numbers) | **missing** |
| og:title/description/url/image, twitter:card | yes | **missing** | **missing** |
| favicon | assets/favicon.svg | **missing** | **missing** |
| theme-color | #0f1216 | **missing** | **missing** |
| viewport-fit=cover | yes | no | no |
| print styles | none | yes (2 blocks) | yes |
| h1 | 1 | 1 | **0 on 54 of 55** (markdown `#` becomes `<h2>`) |
| skip link / `<main>` | no / no | no / yes | no / yes |
| Web fonts | ok | ok | **broken URL**: `12..96.500;12..96.700` returns HTTP 400 (needs commas), so system fonts on every article |
| SVG charts named | 28/28 | 13/13 | |

**Fixes:**
- Copy BTC's og, twitter, favicon and theme-color block into `tools/eth/site/{index,exhibits,article}.html`, with an ETH og.png (about 0.5 day including the image).
- Fix the font URL in article.html (1 line).
- Emit h1 for the first heading in site.py `markdown()` (about 1 hour).
