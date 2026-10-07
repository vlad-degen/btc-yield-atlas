# ETH Yield Research

Public report: https://vlad-degen.github.io/btc-yield-atlas/eth/

Financial snapshot: **2 October 2026, 23:59:59 UTC** (Ethereum block 26,108,081). Rebuilt on 7 October 2026 to match the BTC study: the market is now a product map with every product counted once, and the five carry chapters gain risk, repayment and reward-payer evidence.

## What the page says

- **18.35M ETH earns a yield** in 170 products, each counted once ($49.0B): 81% staking, 13% restaking. About 14.4M ETH more is staked off-chain with exchanges, institutional providers and BitMine.
- **Carry is 1.7%**: 306k ETH in 14 products that borrow $261M of dollars against ETH (BTC: 9.9%). Liquid ETH and Lido Earn hold 85%.
- **Carry barely beats staking.** Liquid ETH beat stETH by 0.66 pp a year over two years; its dollar leg loses about $6.8M a year at 2 October rates. YieldBasis is the only top-five product whose fees cover its loan.
- **Concrete Delta (307k ETH) is not a product**: one Bitfinex-linked wallet's own position, left out of the map.

## Reading route

Answer, Market (counted-once map, two years by category, every product by category), Top 5 (carry history, side-by-side matrix, one chapter per product with a risk and exit panel), Other carry, Risks (disclosure), Data (method, listed but not counted, DefiLlama cross-check, re-check, sources).

## Build

From the repository root, on branch `codex/eth-research` (inputs in `data/eth`, raw captures in `raw/eth`):

```sh
python3 tools/eth/rebuild.py
python3 tools/eth/package_site.py
```

The counted-once map is `tools/eth/netmap/` (fetch: `01_fetch.py`, `02b_pool_charts.py`, `02c_yields.py`; offline: `02_screen.py` to `06_crosscheck.py`); decisions with reasons are in `tools/eth/netmap/decisions.py`. The reader's text and charts for the new findings are in `tools/eth/site/atlas.js`. Output: `eth/`, mirrored to `site/eth/`.

## Local preview

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/eth/index.html. Publication is confined to `/eth/`; the BTC report is unchanged.
