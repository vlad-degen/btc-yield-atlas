# BTC Yield Atlas

A market study of products that pay a Bitcoin holder in Bitcoin. It maps the whole BTC-yield market and its history. It then takes apart the five largest products that post BTC as collateral, borrow dollars against it and put the dollars to work (the "carry" trade), and ends with a playbook for building one.

**Live site:** https://vlad-degen.github.io/btc-yield-atlas/

## Start here

- `REPORT.md` (Russian): the main report. It covers:
  - the current market map, with 95,825 BTC in yield products and the split by strategy;
  - two years of history by category;
  - the top-5 carry products, with a comparison matrix and a full breakdown of each;
  - the closed cases (Maple, Hermetica, Acre);
  - conclusions: mechanics, a numeric risk policy, partners, how to grow TVL, a one-page target product, scenarios and the cost of incentives.
- `index.html`: the site, in English, published at the link above. It is a single file with no build step and all data inline, and it is the source of truth for the page. Sections:
  - the answer and a five-minute reading route;
  - market map (radial chart, category history, carry waves);
  - how carry works (with a calculator);
  - the five biggest: a comparison table and a tab per product;
  - the wider field: every product that borrows against BTC;
  - risks;
  - playbook (including who runs these products);
  - data and method.
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
  - `marketmap_notes.md` and `marketmap_overlap.md`: method, classification decisions and double counting;
  - `top5/<product>/`: TVL, yield, depositor buckets, liquidity ladder and dated events per product (Maple: size, yield and events only); `top5/selection/`: the borrower scan behind the top-5 choice.
- `tools/`:
  - `marketmap/`: the market-map pipeline. See `tools/marketmap/README.md` for the run order. The raw API pulls (about 2 GB) are not in the repository; the fetch scripts recreate them.
  - `top5/<product>/`: the scripts behind each deep dive, for reference. They expect a local `raw/` folder.
  - `monitor_carry.py`: a weekly snapshot of borrow markets and share prices, written to `data/monitor.csv`.
  - `site_data.py`: rebuilds the chart data object embedded in `index.html` (`const V3 = {...}`) from `data/`. It writes `tools/v3data.json`, which you paste over that object.
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

Every product is counted once, net of staking tokens held inside other products. Wrappers and plain loan collateral are excluded.

**On-chain:**
- Ethereum, Ink, Base, Optimism, Morph, Monad, HyperEVM, Stacks, Core and Bitcoin, including archive calls at the snapshot block;
- Blockscout;
- Morpho GraphQL;
- Merkl;
- the Midas transparency API;
- mempool.space.

**Documents:** project docs and legal pages, court filings, SEC/EDGAR filings and MiCA white papers.

Where something could not be verified, the documents say so.
