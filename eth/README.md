# ETH Yield Research

Public report: https://vlad-degen.github.io/btc-yield-atlas/eth/

Financial snapshot: **2 October 2026, 23:59:59 UTC** (Ethereum block 26,108,081). Rebuilt on 7 October 2026 to match the BTC study: the market is now a product map with every product counted once, and the five carry chapters gain risk, repayment and reward-payer evidence. Categories redrawn on 8 October 2026: staking is staked and held only, every loop is leveraged staking, carry is only the dollar-loan part of products open for deposits, and money markets (off) hold the rest of lending collateral.

## What the page says

- **15.94M ETH earns a yield** in 133 products, each counted once ($42.51B): 74.8% staking, 18.1% leveraged staking, 3.3% farming, 2.6% restaking. About 14.4M ETH more is staked off-chain with exchanges, institutional providers and BitMine.
- **Carry is 1.1%**: 179k ETH, the part of 16 products where ETH backs $278M of dollar loans (BTC: 9.8%, counted on whole books). Liquid ETH and Lido Earn hold 79%. Rewards are a minority of the lead over stETH except at YieldBasis and Liquity.
- **Carry barely beats staking.** Liquid ETH beat stETH by 0.66 pp a year over two years; its dollar leg loses about $6.8M a year at 2 October rates. YieldBasis is the only top-five product whose fees cover its loan.
- **Concrete Delta (313k ETH) is not a product**: one Bitfinex-linked wallet's own position, left out of the map.
- **Lending collateral**: $5.07B of stablecoins is borrowed against ETH and $5.24B against BTC; half of ETH collateral backs dollar loans, 46% backs loops.

## Reading route

Answer, Market (counted-once map, two years by category, every product by category), Top 5 (carry history, side-by-side matrix, one chapter per product with a risk and exit panel), Other carry, Risks (disclosure), Data (method, listed but not counted, DefiLlama cross-check, re-check, sources).

## Build

From the repository root, on branch `codex/eth-research` (inputs in `data/eth`, raw captures in `raw/eth`):

```sh
python3 tools/eth/rebuild.py
python3 tools/eth/package_site.py
```

The counted-once map is `tools/eth/netmap/` (fetch: `01_fetch.py`, `02b_pool_charts.py`, `02c_yields.py`; offline: `02_screen.py` to `06_crosscheck.py`); decisions with reasons are in `tools/eth/netmap/decisions.py`. The reader's text and charts for the new findings are in `tools/eth/site/atlas.js`. Output: `eth/`.

## Local preview

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/eth/index.html. Publication is confined to `/eth/`; the BTC report is unchanged.
