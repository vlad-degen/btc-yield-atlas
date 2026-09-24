# BTC Yield Atlas

A market study of products that pay a Bitcoin holder in Bitcoin. It maps the whole BTC-yield market and its history. It then takes apart the five largest products that post BTC as collateral, borrow dollars against it and put the dollars to work (the "carry" trade), and ends with a playbook for building one on Babylon's Trustless Bitcoin Vaults and Aave v4.

**Live site:** https://vlad-degen.github.io/btc-yield-atlas/

## Start here

- `REPORT.md` (Russian): the main report. It covers:
  - the current market map and the split by strategy: 97,964 BTC in 112 products after the 23 September check against DefiLlama; since 24 September the site counts vaults that only lend and Zest's market (874 BTC in 9 products) as money markets and nets Lombard's LBTCv (885 BTC) and the LBTC held by ether.fi's eBTC vault (247 BTC) out of the Veda row, which leaves 94,361 BTC in 101 products; the kinds of farming and pools, the products listed but not counted, and money markets and CDPs as optional segments;
  - two years of history by category;
  - the top-5 carry products, with a comparison matrix and a full breakdown of each;
  - the closed cases (Maple, Hermetica, Acre);
  - conclusions and the playbook for our product on Babylon's Trustless Bitcoin Vaults and Aave v4: design, economics, risk limits, partners, how to grow TVL. It follows the site and was brought in line with it on 23 September.
- `index.html`: the site, in English, published at the link above. It is a single file with no build step and all data inline, and it is the source of truth for the page. Sections:
  - the answer: four numbers and three conclusions;
  - market: the radial chart, then two years of history by category, then who is in each category: one tab per category with every product, what it does, what it pays and who runs it (farming and pools split into points farming, strategy vaults and liquidity pools; money markets into lending markets and vaults that only lend; products that emptied since 2024 listed under each). Every category has a switch (in the top menu and above the charts) that takes it out of every market number, in any mix; money markets and CDP collateral earn about 0% and are off by default. The whole choice is kept in the browser and in the link (`?carry=off`, `?staking=off`, `?basis=off`, `?options=off`, `?credit=off`, `?farming=off`, `?mm=on`, `?cdp=on`);
  - carry math: a worked example on Kraken's vault, parking rates against the loan, the borrow markets and their rate curves, and a calculator in Aave v4 terms (LTV, collateral factor, loan rate, parking yield and the share of it that is third-party rewards; health factor and what a liquidation to the target health factor sells);
  - the five biggest: carry waves, a comparison table and one sequential block per product: a numbered flow-of-funds diagram with links to the contracts and markets, who is in the chain and what each can change, who pays the yield, charts and events;
  - other carry: every product that borrows against BTC, live, small and closed (checked for missing ones on 24 September);
  - risks: one table;
  - playbook: what the top five imply for a product on Babylon vaults and Aave v4: what it would pay, who pays for rewards, rules and partners;
  - data: method, products listed but not counted (sizes re-checked on 24 September), the DefiLlama check, the 24 September re-check of the snapshot against the same sources, and sources.
- `site/index.html`: the same page in the claude.ai artifact format. It is generated, so do not edit it by hand. Regenerate it after every edit of `index.html`:

  ```
  python3 tools/build_site.py
  ```

## Deep dives and data

- `research/top5/` (Russian, with addresses, blocks and method; the English originals are in `research/top5/en/`):
  - `00-selection.md`: how the top-5 was chosen, the borrower scan and the exclusions;
  - `01-kraken.md`: Kraken Bitcoin Vault;
  - `02-yield-basis.md`: Yield Basis;
  - `03-bitget.md`: Bitget bgBTC Onchain Earn;
  - `04-mhyperbtc.md`: Midas mHyperBTC;
  - `05-etherfi.md`: ether.fi Liquid BTC;
  - `06-maple.md`: Maple BTC Yield, wound down.
- `data/`:
  - `market_map_current.csv`: one row per product with category, BTC and USD, source and double-count notes;
  - `market_map_history_monthly.csv` and `category_history_monthly.csv`: month-end history, 2024-09 to 2026-09;
  - `category_flows_monthly.csv`: USD change split into flows and price;
  - `c1_histories.csv`: on-chain month-end histories of the carry products; `c1_pending_proxy_history.csv`: DefiLlama proxies for the same products, for comparison;
  - `lending_products.csv`: the products whose BTC is lent out (used by the market-map pipeline);
  - `c6_groups.csv`: the kind (points farming, strategy vault, liquidity pool, lending) and BTC tokens of every farming-and-pools product; on the site the lending kind counts as money markets;
  - `product_notes.csv`: what each product in the map does, its yield where known and who runs it (the site's product table);
  - `outside_totals.csv`: products that pay a yield on BTC but are not counted (CeFi, funds, ETFs, unconfirmed or unmeasurable ones) and why;
  - `money_markets.csv` and `money_markets_monthly.csv`: BTC in money markets, lending venues and CDPs that no product on the map counts, by protocol and month (the site's optional segments);
  - `marketmap_notes.md` and `marketmap_overlap.md`: method, classification decisions and double counting;
  - `top5/<product>/`: TVL, yield, depositor buckets, liquidity ladder and dated events per product (Maple: size, yield and events only); `top5/selection/`: the borrower scan behind the top-5 choice.
- `tools/`:
  - `marketmap/`: the market-map pipeline. See `tools/marketmap/README.md` for the run order. The raw API pulls (about 2 GB) are not in the repository; the fetch scripts recreate them. `scripts/12_crosscheck_update.py` applies the 23 September DefiLlama check to the files in `data/` and writes the lending list; `scripts/13_money_markets.py` turns the money-market data set in `marketmap/money_markets/` (method in its `mm_notes.md`) into the two money-market files.
  - `top5/<product>/`: the scripts behind each deep dive, for reference. They expect a local `raw/` folder.
  - `monitor_carry.py`: a weekly snapshot of borrow markets and share prices, written to `data/monitor.csv`.
  - `site_data.py`: rebuilds the chart data object embedded in `index.html` (`const V3 = {...}`) from `data/`: every product in today's map with its category and kind, and the month-end history by category (money markets and CDPs from `data/money_markets*.csv`), with each product's notes, so the page can add up any mix of the category switches. It writes `tools/v3data.json`; with `--inject` it also writes the object into `index.html` (then run `build_site.py`); with `--check=<file>` it writes the default map and history to test the page's sums against.
  - `build_site.py`: regenerates `site/index.html`.

## Earlier documents (Russian)

- `BTC-Carry-Vaults-Dossiers.md`: dossiers on every carry vault. People, companies, keys, audits, realized versus advertised yield, incidents and a due-diligence checklist.
- `BTC-Yield-Market-Research.md`: the market report. Taxonomy, unit economics, competitors and regulation.
- `BTC-Yield-Deep-Dive.md`: the first on-chain trace of the Kraken vault.
- `BTC-Yield-Product-Catalog.md`: a registry of about 230 BTC yield products.
- `AUDIT.md`: the audit of the earlier versions: what was wrong, what it was corrected to, what is still unverified, and the corrections from the on-chain deep dives (section F).
- `RESEARCH-PLAN.md`: the plan for this version.

## Method

**Snapshot:** 2026-09-20, 12:00 UTC (Ethereum block 26,018,583; Ink block 56,407,189). Re-checked 2026-09-21.

**Market map:**
- DefiLlama protocol token breakdowns, using the BTC part only;
- the Babylon and Core staking APIs;
- on-chain values for the carry products;
- Binance prices.

Every product is counted once, net of staking tokens held inside other products. Wrappers are excluded; plain loan collateral in money markets and CDPs is shown as two optional segments, net of what the map already counts. On 23 September the map was checked pool by pool against DefiLlama's BTC yields list; pools above $1M that were missing were added, with each pool's own DefiLlama series for the history (Wildcat's value is from 23 September, at that day's price).

**On-chain:**
- Ethereum, Ink, Base, Optimism, Morph, Monad, HyperEVM, Stacks, Core, Rootstock, Mezo and Bitcoin, including archive calls at the snapshot block;
- Blockscout;
- Morpho GraphQL;
- Merkl;
- the Midas transparency API;
- mempool.space.

**Documents:** project docs and legal pages, court filings, SEC/EDGAR filings and MiCA white papers.

Where something could not be verified, the documents say so.
