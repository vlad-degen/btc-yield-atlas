# Market-map pipeline

Scripts that build the BTC-yield market map (`data/market_map_current.csv`, the monthly history files and the notes).

Layout: `scripts/` holds the code, `inputs/c1_histories.csv` the on-chain month-end histories of the carry products (merged by `10_build.py`), and `raw/` the API pulls (not in the repository, about 2 GB).

Re-run from this folder in the order given in `data/marketmap_notes.md`, section "Re-run" (fetch scripts `01`–`08`, then `10_build.py` and `11_write_reports.py`). `10_build.py` writes the CSVs into this folder.

Then copy the outputs into `data/`, renaming `notes.md` to `marketmap_notes.md` and `overlap.md` to `marketmap_overlap.md`. The product list and classification decisions live in `scripts/products.py`.

After copying, run `python3 scripts/12_crosscheck_update.py`. It applies the 2026-09-23 check against DefiLlama's BTC pool list to the files in `data/`: it adds missed pools holding more than $1M (DEX pools included), writes `data/lending_products.csv` (the products the site's lending switch hides) and recomputes the category history and flows. `data/c6_groups.csv` (the kind and BTC tokens of each farming-and-pools product, for the site's switches) is kept by hand: `tools/site_data.py` stops with an error if a C6 product has no kind. It caches pool charts in `raw/pool_charts/` and can be re-run safely.

Then run `python3 scripts/13_money_markets.py`. It reads the money-market data set in `money_markets/` (BTC in money markets, lending venues, CDPs and curated vaults by protocol and month, with the overlap with map products; the fetch and build scripts are in `money_markets/scripts/`, method in `money_markets/mm_notes.md`, raw pulls not in the repository) and writes `data/money_markets.csv` and `data/money_markets_monthly.csv`, the BTC that no product on the map counts. Finally rebuild the site data: `python3 tools/site_data.py . tools/v3data.json --inject` and `python3 tools/build_site.py` from the repo root.
