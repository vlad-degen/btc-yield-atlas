# BTC Yield Atlas

A market study of products that pay a Bitcoin holder in Bitcoin, with a focus on the vaults that post BTC as collateral, borrow stablecoins against it and park the dollars somewhere that pays.

**Live site:** https://vlad-degen.github.io/btc-yield-atlas/

## What is in here

- `index.html` — the site. Single file, no build step, all data inline.
- `BTC-Yield-Market-Research.md` — the written report: taxonomy, unit economics, market sizing, conclusions.
- `BTC-Yield-Deep-Dive.md` — the on-chain trace of Kraken Bitcoin Vault, rate curves, stress timeline, incident register.
- `BTC-Yield-Product-Catalog.md` — a registry of about 230 BTC yield products across DeFi, CeFi, funds and ETFs.
- `site/index.html` — the same page in the format used by the claude.ai artifact (no HTML skeleton).

## Method

On-chain: Ethereum and Ink RPC, Blockscout API (verified contract names, balances, transfers, decoded accountant events), Morpho GraphQL, Spark pool data. Market data: DefiLlama, Binance daily candles. Snapshot date 2026-09-20. Every figure on the site links to its source.
