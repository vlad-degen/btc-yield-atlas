# Market-map pipeline

Scripts that build the BTC-yield market map (`data/market_map_current.csv`, the monthly history files and the notes).

Layout: `scripts/` holds the code, `inputs/c1_histories.csv` the on-chain month-end histories of the carry products (merged by `10_build.py`), and `raw/` the API pulls (not in the repository, about 2 GB).

Re-run from this folder in the order given in `data/marketmap_notes.md`, section "Re-run" (fetch scripts `01`–`08`, then `10_build.py` and `11_write_reports.py`). `10_build.py` writes the CSVs into this folder.

Then copy the outputs into `data/`, renaming `notes.md` to `marketmap_notes.md` and `overlap.md` to `marketmap_overlap.md`. The product list and classification decisions live in `scripts/products.py`.
