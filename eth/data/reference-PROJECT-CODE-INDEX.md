# Индекс кода и данных BTC Yield Atlas

Статический индекс исходной версии `711a3935621cfd72da0b25ebcf5a6c173a10adbe`. Составлен 3 октября 2026 года до добавления заметок изучения.

Назначение скрипта извлечено из docstring, начального комментария или имён функций. Это навигация по коду; полная проверка финансового результата каждого вспомогательного скрипта не подразумевается.

Подробная методика, выводы и открытые вопросы: [PROJECT-KNOWLEDGE.md](PROJECT-KNOWLEDGE.md). Hashes, импорты, функции, строковые пути и публичные endpoints: [project-study-inventory.json](project-study-inventory.json).

## Python-скрипты

### tools — общие утилиты (3)

| Файл | Строк | Назначение |
|---|---:|---|
| [build_site.py](../tools/build_site.py) | 33 | Regenerate site/index.html (artifact format, no HTML skeleton) from index.html. index.html is the source of truth. Run after every edit: python3 tools/build_site.py |
| [monitor_carry.py](../tools/monitor_carry.py) | 79 | Weekly snapshot of the BTC carry products and the markets they borrow from. Appends one row per item to data/monitor.csv (timestamp, item, metric, value), so a spreadsheet or the site can chart borrow-rate spikes, full caps and share-price  |
| [site_data.py](../tools/site_data.py) | 201 | Build the chart data object embedded in index.html as const V3 = {...} (market map, category history, top-5 series). The page's switches are the categories themselves: each one takes its category out of every market number. Money markets (C |

### tools/marketmap/money_markets (17)

| Файл | Строк | Назначение |
|---|---:|---|
| [atoken_holders.py](../tools/marketmap/money_markets/scripts/atoken_holders.py) | 46 | Top holders of the main BTC aTokens (Aave v3 Ethereum/Base/Arbitrum, Spark) from Blockscout (no key), with contract name / implementation name, to find map products that supply BTC to these markets. Read 2026-09-23 (current balances). -> ra |
| [build.py](../tools/marketmap/money_markets/scripts/build.py) | 228 | Build the deliverable tables from out/mm_long.json (process.py) and the DefiLlama yields pools. Writes (scratch folder mm/): mm_monthly.csv segment, protocol, slug, month, btc_total, btc_plain, btc_yieldbearing, btc_borrowed, usd (+ source) |
| [fetch_pool_charts.py](../tools/marketmap/money_markets/scripts/fetch_pool_charts.py) | 35 | Fetch https://yields.llama.fi/chart/{pool} for BTC lending pools (tvlUsd >= MIN today) into raw/charts/ (cached). Pools: raw/btc_lending_pools.json (written by select_pools.py). Spaced requests, backoff on errors / Cloudflare pages. |
| [fetch_protocols.py](../tools/marketmap/money_markets/scripts/fetch_protocols.py) | 47 | Fetch https://api.llama.fi/protocol/{slug} for the screening list into raw/proto/{slug}.json (streamed by curl, cached). Usage: python3 fetch_protocols.py [slug ...] (default: raw/fetch_list.json 'fetch') |
| [make_fetch_list.py](../tools/marketmap/money_markets/scripts/make_fetch_list.py) | 18 | Screening list -> raw/fetch_list.json: DefiLlama Lending / Uncollateralized Lending / CDP protocols with TVL > $1M (raw/protocols.json, api.llama.fi/protocols read 2026-09-23) plus every C0 slug of tools/marketmap/scripts/products.py (cdp / |
| [mgql.py](../tools/marketmap/money_markets/scripts/mgql.py) | 17 | Retrying client for the Morpho API (blue-api.morpho.org/graphql). |
| [mmlib.py](../tools/marketmap/money_markets/scripts/mmlib.py) | 75 | Helpers for the money-market BTC data set. Same conventions as tools/marketmap/scripts/lib.py (DefiLlama daily points stamped 00:00 UTC; month-end = point stamped on the 1st of the next month; snapshot = 2026-09-20 point). |
| [morpho_holder_names.py](../tools/marketmap/money_markets/scripts/morpho_holder_names.py) | 28 | Names of Morpho BTC-collateral depositors with >= 3 BTC (Ethereum, Base, Arbitrum, Katana via Blockscout) -> raw/morpho/holder_names.json |
| [morpho_markets.py](../tools/marketmap/money_markets/scripts/morpho_markets.py) | 36 | Morpho Blue API (blue-api.morpho.org/graphql): all markets with state, saved to raw/morpho/markets.json. Read 2026-09-23 (current state). |
| [morpho_positions.py](../tools/marketmap/money_markets/scripts/morpho_positions.py) | 54 | Morpho API: top collateral positions in every BTC-collateral market with >= 5 BTC collateral (current state, read 2026-09-23), and all MetaMorpho (v1) and Vault V2 vaults whose asset is a BTC-family token. -> raw/morpho/positions.json, raw/ |
| [overlap.py](../tools/marketmap/money_markets/scripts/overlap.py) | 231 | Overlap of money-market / CDP / venue / curator BTC with products the map already counts -> mm_overlap.csv (+ out/overlap_summary.json). Groups (column 'group'): A yield-bearing BTC tokens (LBTC, SolvBTC LSTs, uniBTC, eBTC, bfBTC, mHyperBTC |
| [process.py](../tools/marketmap/money_markets/scripts/process.py) | 94 | Money-market / CDP / venue / curator BTC by protocol, chain and month from DefiLlama /protocol/{slug} token units. Month points (map convention): month-end = DefiLlama point stamped 00:00 UTC on the 1st of the next month (3 days back if mis |
| [reconcile.py](../tools/marketmap/money_markets/scripts/reconcile.py) | 95 | Reconcile the protocol-based snapshot with the page's C0 row (169,406 BTC = DefiLlama yields BTC lending pools on 09-20, $13.86B less Zest v2 and Accountable) and with its per-protocol $B split. -> out/reconcile.json, printed tables. |
| [rpc.py](../tools/marketmap/money_markets/scripts/rpc.py) | 30 | Minimal JSON-RPC eth_call helper over public RPC endpoints (no keys). |
| [scan_symbols.py](../tools/marketmap/money_markets/scripts/scan_symbols.py) | 37 | Scan every fetched protocol at the 2026-09-20 point (and the max over month-ends) for BTC-like token symbols. Output raw/symbol_scan.json: {slug: {chainkey: {SYM: [units, usd]}}} for symbols that are in the map's BTC list or contain 'BTC'. |
| [select_pools.py](../tools/marketmap/money_markets/scripts/select_pools.py) | 39 | Select BTC-family lending pools from DefiLlama yields /pools (read 2026-09-23) -> raw/btc_lending_pools.json. BTC family = the map's list (tools/marketmap/scripts/lib.py btc_weight == 1) plus a few symbols seen in lending pools that the lis |
| [tokens.py](../tools/marketmap/money_markets/scripts/tokens.py) | 50 | BTC token classification for the money-market data set. BTC family = the map's list (tools/marketmap/scripts/lib.py: BTC_FULL, BTC_PARTIAL, LFBTC-*) plus ALIASES (the same tokens under other DefiLlama keys; added because otherwise a DefiLla |

### tools/marketmap/scripts (16)

| Файл | Строк | Назначение |
|---|---:|---|
| [01_candidates.py](../tools/marketmap/scripts/01_candidates.py) | 34 | Build the candidate slug list from DefiLlama /protocols (raw/protocols.json). Categories per task + manual list. Output: raw/candidates.json |
| [02_fetch_protocols.py](../tools/marketmap/scripts/02_fetch_protocols.py) | 26 | Fetch https://api.llama.fi/protocol/{slug} for every candidate into raw/proto/ (cached; delete a file to refetch). Usage: python3 02_fetch_protocols.py [slug ...] (no args = all candidates) |
| [02b_fetch_parallel.py](../tools/marketmap/scripts/02b_fetch_parallel.py) | 35 | Parallel variant of 02_fetch_protocols.py (4 workers, backoff on 429). Usage: python3 02b_fetch_parallel.py slugs.json |
| [03_fetch_btc_price.py](../tools/marketmap/scripts/03_fetch_btc_price.py) | 12 | Binance BTCUSDT daily klines 2024-08-25 .. today -> raw/btc_daily.json {date: close} |
| [04_fetch_babylon.py](../tools/marketmap/scripts/04_fetch_babylon.py) | 29 | Babylon: stats + finality providers (staking-api) + all ACTIVE BTC delegations (Babylon LCD, publicnode). Output: raw/babylon_stats.json, raw/babylon_fps.json, raw/babylon_active_delegations.json (slim) |
| [05_screen.py](../tools/marketmap/scripts/05_screen.py) | 22 | Screen all candidates: BTC-token part at the 2026-09-20 point. Output raw/screen_0920.json + printed table. |
| [06_babylon_lst_fp_history.py](../tools/marketmap/scripts/06_babylon_lst_fp_history.py) | 97 | Babylon phase-2 delegations (all statuses) of finality providers operated by/for LST & BTC-yield products, reconstructed into month-end active stake. Heights->dates via mempool.space. Output: raw/babylon_lst_fp_delegations.json, raw/btc_hei |
| [06c_babylon_lst_staker_history.py](../tools/marketmap/scripts/06c_babylon_lst_staker_history.py) | 96 | Babylon stake of LST / BTC-yield products, month-end 2024-09..2026-09, by STAKER KEY (captures phase-1 and delegations to non-branded finality providers). 1) staker BTC keys = keys that ever delegated to a product-branded FP (Lombard*, Solv |
| [07_fetch_yield_pools.py](../tools/marketmap/scripts/07_fetch_yield_pools.py) | 28 | Selected DefiLlama yields pools (for products without a protocol-level token series) + their daily charts. Output: raw/yield_pools_selected.json, raw/pool_charts/{pool}.json |
| [08_history_screen.py](../tools/marketmap/scripts/08_history_screen.py) | 27 | Screen every fetched protocol for its BTC-token part at month-ends 2024-09..2026-09 (catches products that are small/dead today). Output: raw/history_screen.json {slug: {category, max_usd, max_month, cur_usd, months:{m: usd}}} |
| [10_build.py](../tools/marketmap/scripts/10_build.py) | 408 | Build the BTC-yield market map: current snapshot (2026-09-20), monthly history 2024-09..2026-09, category aggregates, overlap (double-count) splits, flow/price decomposition and sanity checks. Inputs: raw/proto/*.json (DefiLlama), raw/pool_ |
| [11_write_reports.py](../tools/marketmap/scripts/11_write_reports.py) | 328 | Write overlap.md, notes.md and jump_candidates.csv from the build outputs (run after 10_build.py). |
| [12_crosscheck_update.py](../tools/marketmap/scripts/12_crosscheck_update.py) | 268 | Post-build step: apply the 2026-09-23 cross-check against DefiLlama's BTC yields list to the map in data/. 1. Adds what the map missed and what has more than $1M of liquidity on https://defillama.com/yields?token=family:btc (read 2026-09-23 |
| [13_money_markets.py](../tools/marketmap/scripts/13_money_markets.py) | 94 | Post-build step: BTC in money markets and CDPs that the map does not count yet, for the site's two optional segments. Reads the money-market data set in tools/marketmap/money_markets/ (built 2026-09-23 from DefiLlama protocol and yields dat |
| [lib.py](../tools/marketmap/scripts/lib.py) | 97 | Shared helpers: DefiLlama protocol loading, BTC-token filtering, date points. |
| [products.py](../tools/marketmap/scripts/products.py) | 254 | Product universe: classification + data spec. Edit here, then re-run 10_build.py. Fields id, product, slug, cat (code or {month_from: code} for time-varying), sub, src: 'dl' DefiLlama /protocol/{slug}: BTC-symbol part of tokensInUsd (option |

### tools/top5/bitget (19)

| Файл | Строк | Назначение |
|---|---:|---|
| [abidec.py](../tools/top5/bitget/abidec.py) | 29 | Функции: evsig, build, dec_word, decode, t |
| [blocks.py](../tools/top5/bitget/blocks.py) | 21 | interpolation-ish bisection |
| [bs.py](../tools/top5/bitget/bs.py) | 51 | Функции: get, v2_all, getlogs, getlogs_w |
| [build_events.py](../tools/top5/bitget/build_events.py) | 37 | -> ../events.csv (dated timeline; 'onchain' rows come from raw/*.json produced by the other scripts) |
| [build_misc.py](../tools/top5/bitget/build_misc.py) | 55 | -> ../liquidity_ladder.csv, ../holders.csv, ../events.csv (values from raw/ files produced by the other scripts; see comments) |
| [build_tvl.py](../tools/top5/bitget/build_tvl.py) | 39 | -> ../tvl_weekly.csv (weekly TVL, bgBTC and USD; on-chain snapshots + ETH supply events + Chainlink PoR + DefiLlama) |
| [eth_supply.py](../tools/top5/bitget/eth_supply.py) | 33 | bgBTC on Ethereum: supply / CCIP-locked / Bitget-hot-wallet history from token transfers (eth.blockscout.com). |
| [fetch_all.py](../tools/top5/bitget/fetch_all.py) | 44 | Fetch raw on-chain data from Morph Blockscout (explorer-api.morphl2.io) used by the other scripts. Run order: fetch_all.py -> state_now.py > ../raw/state_now.json -> weekly.py -> yields.py -> swaps.py -> ltv_path.py -> por.py -> eth_supply. |
| [governance.py](../tools/top5/bitget/governance.py) | 27 | Read roles/keys/timelocks of the whole stack (Morph + Ethereum) -> ../raw/governance.json |
| [ltv_path.py](../tools/top5/bitget/ltv_path.py) | 33 | 6-hourly LTV / health path of the Aera vault position (Morph archive RPC) -> raw/ltv_path.json |
| [morphoev.py](../tools/top5/bitget/morphoev.py) | 32 | Функции: words, addr, decode |
| [pfc_decode.py](../tools/top5/bitget/pfc_decode.py) | 24 | daily last anchor |
| [por.py](../tools/top5/bitget/por.py) | 22 | Chainlink BGBTC PoR feed history on Ethereum (proxy getRoundData walk-back). |
| [rpc.py](../tools/top5/bitget/rpc.py) | 45 | Функции: k256, sel, post, call, batch, eth_call |
| [snap.py](../tools/top5/bitget/snap.py) | 74 | Snapshot of the whole bgBTC Earn stack at a Morph block (archive RPC reads). |
| [state_now.py](../tools/top5/bitget/state_now.py) | 86 | Morpho market |
| [swaps.py](../tools/top5/bitget/swaps.py) | 30 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [weekly.py](../tools/top5/bitget/weekly.py) | 15 | Weekly snapshots (Morph archive RPC) -> raw/weekly_snaps.json |
| [yields.py](../tools/top5/bitget/yields.py) | 71 | Weekly yield decomposition -> ../yield_weekly.csv (+ raw/yield_detail.json) Sources: raw/weekly_snaps.json (RPC), raw/morpho_market_decoded.json (Morpho events), raw/campaigns.json (reward distributor 0x53d2...), raw/aera_swaps_claims.json  |

### tools/top5/etherfi (39)

| Файл | Строк | Назначение |
|---|---:|---|
| [add_stress.py](../tools/top5/etherfi/add_stress.py) | 20 | adds month_min_btc_close / hf_at_month_low_est to positions_monthly.csv (run after build_tables.py) |
| [borrow_rates.py](../tools/top5/etherfi/borrow_rates.py) | 18 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [bridges.py](../tools/top5/etherfi/bridges.py) | 21 | Функции: ts |
| [bs_fetch.py](../tools/top5/etherfi/bs_fetch.py) | 20 | Blockscout v2 paginator: python3 bs_fetch.py <base> <path> <outname> [maxpages] |
| [build_holders.py](../tools/top5/etherfi/build_holders.py) | 65 | combined buckets (address-level; Aave v4 Hub counted as one address) |
| [build_tables.py](../tools/top5/etherfi/build_tables.py) | 77 | ---- positions_monthly ---- |
| [build_yield.py](../tools/top5/etherfi/build_yield.py) | 147 | Builds yield_monthly.csv (+ raw/yield_detail.json) |
| [classify_holders.py](../tools/top5/etherfi/classify_holders.py) | 23 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [crosschain_holdings.py](../tools/top5/etherfi/crosschain_holdings.py) | 22 | Scroll share supply + vault token holdings on Optimism and Scroll at month-ends (used by value_positions2.py) |
| [economics.py](../tools/top5/etherfi/economics.py) | 37 | yield to depositors |
| [fetch_logs.py](../tools/top5/etherfi/fetch_logs.py) | 15 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [fetch_topic_logs.py](../tools/top5/etherfi/fetch_topic_logs.py) | 14 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [flows.py](../tools/top5/etherfi/flows.py) | 17 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [flows_monthly.py](../tools/top5/etherfi/flows_monthly.py) | 37 | Функции: rate_at_block, month |
| [governance.py](../tools/top5/etherfi/governance.py) | 29 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [holders_eth.py](../tools/top5/etherfi/holders_eth.py) | 28 | Replay share Transfer logs on Ethereum -> balances at month-ends, holder counts, flows (mint/burn) |
| [incentive_share.py](../tools/top5/etherfi/incentive_share.py) | 14 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [itb_positions.py](../tools/top5/etherfi/itb_positions.py) | 45 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [itb_tokens.py](../tools/top5/etherfi/itb_tokens.py) | 19 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [keccak_lib.py](../tools/top5/etherfi/keccak_lib.py) | 63 | Функции: rol, f, keccak, sel, call, rpc |
| [lib.py](../tools/top5/etherfi/lib.py) | 111 | binary search |
| [liquidity_checks.py](../tools/top5/etherfi/liquidity_checks.py) | 23 | Snapshot liquidity checks behind liquidity_ladder.csv: Sentora/stcUSD redeem simulations from the vault, Cap burn capacity, queue terms, Spark oracle/config |
| [lz_dst.py](../tools/top5/etherfi/lz_dst.py) | 25 | version 1B, nonce 8B, srcEid 4B, sender 32B, dstEid 4B |
| [month_blocks.py](../tools/top5/etherfi/month_blocks.py) | 20 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [morpho_events.py](../tools/top5/etherfi/morpho_events.py) | 28 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [op_holders_rpc.py](../tools/top5/etherfi/op_holders_rpc.py) | 19 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [op_holders_rpc2.py](../tools/top5/etherfi/op_holders_rpc2.py) | 30 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [op_share_logs.py](../tools/top5/etherfi/op_share_logs.py) | 20 | Функции: fetch |
| [owned_contracts.py](../tools/top5/etherfi/owned_contracts.py) | 16 | contracts whose ownership was transferred to the vault (ITB position managers etc.) |
| [positions.py](../tools/top5/etherfi/positions.py) | 81 | Reconstruct vault positions at month-end blocks (Ethereum). Output raw/positions_raw.json |
| [rate_monthly.py](../tools/top5/etherfi/rate_monthly.py) | 24 | Функции: rate_at, apy |
| [rate_series.py](../tools/top5/etherfi/rate_series.py) | 20 | drops |
| [reward_values.py](../tools/top5/etherfi/reward_values.py) | 11 | USD value of reward tokens received (ETHFI, MORPHO, CRV, FXN) at receipt time via DefiLlama historical prices |
| [rewards.py](../tools/top5/etherfi/rewards.py) | 34 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [share_prices.py](../tools/top5/etherfi/share_prices.py) | 34 | month-end share prices of deployment vaults + borrow indices of every venue used |
| [supply_monthly.py](../tools/top5/etherfi/supply_monthly.py) | 10 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [tokens_seen.py](../tools/top5/etherfi/tokens_seen.py) | 15 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [value_positions.py](../tools/top5/etherfi/value_positions.py) | 59 | Функции: rate_at, btc_px |
| [value_positions2.py](../tools/top5/etherfi/value_positions2.py) | 89 | Full month-end balance sheet: Ethereum vault + ITB managers + Morpho + off-Ethereum (Berachain/Corn in-flight, Optimism vault) |

### tools/top5/kraken (21)

| Файл | Строк | Назначение |
|---|---:|---|
| [accountant_logs.py](../tools/top5/kraken/accountant_logs.py) | 30 | All event logs of the Ink accountant 0x4bb6...f1d6 and the fee PaymentSplitter 0x600d...0a4a via Blockscout v2 API. Output raw/accountant_logs.json, raw/splitter_logs.json |
| [accrue_fetch.py](../tools/top5/kraken/accrue_fetch.py) | 39 | Morpho Blue AccrueInterest events (id, prevBorrowRate per second, interest, feeShares) for the markets the vault borrows from / deploys into. prevBorrowRate is the average rate the IRM applied over the elapsed interval, so the event stream  |
| [analysis.py](../tools/top5/kraken/analysis.py) | 289 | Main analysis for the Kraken Bitcoin Vault deep dive (v3). Builds weekly/monthly yield, spread, negative-carry, LTV, TVL, holder and fee series from the raw data. Outputs: yield_weekly.csv, tvl_weekly.csv, ltv_weekly.csv, raw/analysis.json  |
| [analysis_carry.py](../tools/top5/kraken/analysis_carry.py) | 63 | Negative-carry episodes and carry P&L by leg (daily), plus the 21 Sep 2026 live day. Uses raw/daily_legs.json (analysis.py) and raw/accrue_events.json. Output raw/analysis_carry.json |
| [analysis_econ.py](../tools/top5/kraken/analysis_econ.py) | 102 | Operator economics (fees, Sentora downstream fees, issuer incentives) + cap-binding days + events.csv. Output raw/analysis_econ.json, events.csv |
| [analysis_growth.py](../tools/top5/kraken/analysis_growth.py) | 151 | TVL growth (weekly/monthly, BTC and USD, flows vs price vs yield decomposition), holder count over time, monthly net inflows, public-milestone cross-check, flow drivers, and operator fee economics. Outputs: tvl_weekly.csv, raw/analysis_grow |
| [analysis_risk.py](../tools/top5/kraken/analysis_risk.py) | 224 | Risk section: LTV per position over time (daily/weekly + intraday path from Chainlink rounds and position events), delever reaction lags (price-driven and rate-spike-driven), stress test at the snapshot, liquidity ladder. Outputs: ltv_weekl |
| [blocks.py](../tools/top5/kraken/blocks.py) | 34 | Daily 00:00 UTC block numbers. Ethereum: first block with timestamp >= 00:00 UTC, found by Newton iteration on RPC block timestamps and verified (block-1 < ts <= block). Ink: 1-second blocks, block = 56,407,189 + (ts - 1,789,905,600) (verif |
| [chainlink_btc.py](../tools/top5/kraken/chainlink_btc.py) | 24 | Chainlink BTC/USD (proxy 0xF403...E88c, aggregator 0x4a34...84f1, phase 7 unchanged over the window) AnswerUpdated rounds. Output raw/cl_btc_rounds.json rows [block, answer_usd, updatedAt] |
| [classify_unknown.py](../tools/top5/kraken/classify_unknown.py) | 25 | Classify snapshot holders that later exited (absent from the Blockscout holder list) via eth_getCode on Ink at the snapshot block. EIP-7702 delegated accounts have code 0xef0100 \|\| delegate(20 bytes). Output raw/unknown_type_codes.json |
| [daily_eth.py](../tools/top5/kraken/daily_eth.py) | 86 | Daily (00:00 UTC) + snapshot archive reads on Ethereum for the Kraken BTC vault's legs. Output raw/daily_eth.json {date: {...decoded values...}} |
| [dec.py](../tools/top5/kraken/dec.py) | 52 | Decoding helpers for raw/daily_eth.json rows. |
| [events_csv.py](../tools/top5/kraken/events_csv.py) | 66 | Assemble events.csv (date, event, type, source) from on-chain findings (this run), the web timeline research (raw/timeline_agent.tsv) and previously verified items (BTC-Carry-Vaults-Dossiers.md / dossier-kraken.md). |
| [holders_fetch.py](../tools/top5/kraken/holders_fetch.py) | 50 | Paginate Blockscout (Ink) token holders of the vault share token sentoraBTC. Output: raw/holders_ink.jsonl (one compact row per holder) + raw/holders_meta.json Run: python3 holders_fetch.py (resumable: continues from last saved next_page_pa |
| [ink_flows.py](../tools/top5/kraken/ink_flows.py) | 164 | Replay every sentoraBTC Transfer on Ink -> daily supply, holders, deposits, withdrawals (BTC at accountant rate), per-address balances at the snapshot, holder buckets/concentration, and address-type classification. Inputs: raw/share_transfe |
| [klib.py](../tools/top5/kraken/klib.py) | 193 | Minimal on-chain helper: pure-python keccak256, ABI encode/decode, JSON-RPC via curl. |
| [ladder_reads.py](../tools/top5/kraken/ladder_reads.py) | 40 | Archive reads at the snapshot block for the liquidity ladder: every Morpho market each Sentora V2 vault (that the Kraken vault holds) allocates to, the V2 adapter's supply position there, V2 idle, force-deallocate penalties, and the PRIME/P |
| [md_tables.py](../tools/top5/kraken/md_tables.py) | 31 | Print markdown tables used in deepdive.md from the computed outputs (avoids hand transcription). |
| [merkl_fetch.py](../tools/top5/kraken/merkl_fetch.py) | 43 | Merkl campaign history for the Sentora vaults the Kraken BTC vault deploys into. Output raw/merkl_campaigns.json : list of campaigns (opportunity, start, end, token, amount, maxApr, whitelist, creator). |
| [transfers_fetch.py](../tools/top5/kraken/transfers_fetch.py) | 34 | Fetch every Transfer event of the vault share token (sentoraBTC) on Ink. Primary: Ink RPC eth_getLogs in 10k-block windows (parallel). Output raw/share_transfers.json rows: [block, logIndex, from, to, value_raw, tx] |
| [v2_caps.py](../tools/top5/kraken/v2_caps.py) | 44 | Sentora V2 cap history (IncreaseAbsoluteCap / DecreaseAbsoluteCap) for RLUSD Main and Paypal USD Main, via eth_getLogs. Cap ids are keccak(idData); idData embeds market params, so kBTC-market caps are recognised by the kBTC address in idDat |

### tools/top5/maple (19)

| Файл | Строк | Назначение |
|---|---:|---|
| [btc_hub_trace.py](../tools/top5/maple/btc_hub_trace.py) | 30 | Trace the Bitcoin wind-down of the Maple BTC Yield program via mempool.space. Hub = bc1pm9v0y2...c0pc4: receives the 2025-11-19 sweep of all remaining CLTV outputs (from btc_outspends.py), then pays out to recipient addresses (each preceded |
| [btc_outspends.py](../tools/top5/maple/btc_outspends.py) | 37 | For each Core BTC stake of the Maple-attributed cluster, look up the Bitcoin staking tx on mempool.space (txid byte-reversed vs the Core event), identify the locked output (value == staked amount), and check whether/when it was spent and to |
| [build_csvs.py](../tools/top5/maple/build_csvs.py) | 58 | Assemble size_history.csv, yield_history.csv, events.csv from disclosed sources + on-chain reconstruction. |
| [build_events.py](../tools/top5/maple/build_events.py) | 57 | Write events.csv (date, event, type, source). |
| [cluster_link.py](../tools/top5/maple/cluster_link.py) | 30 | Attribute Core BTC-staking reward addresses to one owner by shared Bitcoin owner scripts. Each Core BTC stake script = <locktime> OP_CLTV OP_DROP <owner script>. Delegators (CORE reward addresses) whose stakes lock BTC under the same owner  |
| [core_block_at.py](../tools/top5/maple/core_block_at.py) | 19 | Binary-search the Core block number for a UTC date via rpc.coredao.org. |
| [core_btc_stakes.py](../tools/top5/maple/core_btc_stakes.py) | 39 | Decode Core BitcoinStake 'delegated' and 'btcExpired' events into a per-stake table (txid, block, approx UTC time, delegator = CORE reward address, candidate, BTC amount, CLTV locktime from script). Block->time via linear interpolation on b |
| [core_grades.py](../tools/top5/maple/core_grades.py) | 38 | Read Core dual-staking tier table (BitcoinAgent.getGrades / gradeActive) from Core RPC, at 'latest' and optionally at historical block numbers (needs archive support). BitcoinAgent system contract: 0x0000000000000000000000000000000000001013 |
| [core_logs.py](../tools/top5/maple/core_logs.py) | 28 | Pull logs from Core RPC in chunks. Usage: core_logs.py <address> <topic0> <fromBlock> <toBlock> <chunk> <out.jsonl> |
| [core_logs_by_addr.py](../tools/top5/maple/core_logs_by_addr.py) | 25 | Pull logs for a contract + topic0 filtered by indexed address in topic position N (1..3). Usage: core_logs_by_addr.py <contract> <topic0> <pos> <addr1,addr2,...> <from> <to> <chunk> <out.jsonl> |
| [decode_paramchange.py](../tools/top5/maple/decode_paramchange.py) | 19 | Decode Core paramChange(string key, bytes value) logs; for key 'grades' decode the tier table (value encoding per BitcoinAgent.updateParam: uint8 length followed by (uint32 stakeRate, uint32 percentage) pairs, per the contract source). Bloc |
| [fetch_text.py](../tools/top5/maple/fetch_text.py) | 25 | Fetch a URL with a browser UA and dump readable text (script/style stripped). |
| [maple_cluster_series.py](../tools/top5/maple/maple_cluster_series.py) | 35 | Reconstruct BTC staked on Core by the address cluster attributed (by shared BTC owner scripts and by the 584.047 BTC / 2025-10-15 and 756.983 BTC / 2025-11-19 CLTV maturities that match the Cayman judgment) to Maple's BTC Yield program. Act |
| [maple_core_leg.py](../tools/top5/maple/maple_core_leg.py) | 57 | Reconstruct the CORE leg (delegated CORE) and BTC/CORE reward claims of the Maple-attributed cluster on Core. Inputs: cl_*.jsonl from core_logs_by_addr.py. Block->date via block_calib.txt interpolation. Outputs maple_core_leg_daily.csv (COR |
| [maple_gql_probe.py](../tools/top5/maple/maple_gql_probe.py) | 34 | Probe Maple's public GraphQL API (api.maple.finance/v2/graphql) for the off-chain 'BTC Yield' pool metadata record (id 67e542004191822941f9e703, linked from Core's 2025-05-02 blog post). Introspection is disabled, so field names are discove |
| [maple_yield_model.py](../tools/top5/maple/maple_yield_model.py) | 37 | Estimate the gross staking yield earned on-chain by the Maple-attributed cluster, per month and overall. Gross yield (BTC terms) = sum(CORE rewards claimed * CORE/USD on claim date) / sum(BTC staked * BTC/USD per day) * 365. This EXCLUDES:  |
| [prices.py](../tools/top5/maple/prices.py) | 33 | Daily and monthly CORE/USDT and BTC/USDT closes from Bybit public spot klines (no key). Writes ../raw/prices_daily.csv and ../raw/prices_monthly.csv (UTC). |
| [rlp_grades.py](../tools/top5/maple/rlp_grades.py) | 22 | Decode RLP 'grades' values from agent_paramchange_decoded.txt into CORE-per-BTC thresholds and reward percentages. Grade = (stakeRate [CORE per BTC], percentage [/10000 of reference BTC reward rate]). |
| [scan_txs.py](../tools/top5/maple/scan_txs.py) | 21 | Pull all normal transactions for given Core addresses via scan.coredao.org's public web API (POST /api/chain/address_transaction) and summarise large CORE value transfers. |

### tools/top5/mhyperbtc (33)

| Файл | Строк | Назначение |
|---|---:|---|
| [aave_daily.py](../tools/top5/mhyperbtc/aave_daily.py) | 46 | Daily (00:00 UTC) Aave v3 Core / Prime / Horizon and Spark account data + per-asset balances of the strategy wallet (Ethereum archive) |
| [aave_rates_daily.py](../tools/top5/mhyperbtc/aave_rates_daily.py) | 22 | Daily variable borrow rates of Aave Core / Spark reserves used by the strategy (getReserveData at daily blocks, days with debt only) |
| [admin_events.py](../tools/top5/mhyperbtc/admin_events.py) | 26 | Upgrade / pause events on mHyperBTC Ethereum contracts (token, deposit vault, redemption vault, oracle) via getLogs (tenderly, 500k-block chunks, throttled) |
| [borrow_cost.py](../tools/top5/mhyperbtc/borrow_cost.py) | 46 | Daily borrow cost of the strategy's on-chain debt (Morpho per-market APY x debt; Aave/Spark per-reserve rate x debt), aggregated monthly |
| [bs_transfers.py](../tools/top5/mhyperbtc/bs_transfers.py) | 19 | Paginate Blockscout v2 token-transfers for an address (any Blockscout host) |
| [build_balance_sheet.py](../tools/top5/mhyperbtc/build_balance_sheet.py) | 99 | Daily identified balance sheet of the mHyperBTC strategy (on-chain venues + PoR CEX lines) vs NAV |
| [build_events.py](../tools/top5/mhyperbtc/build_events.py) | 52 | events.csv: dated timeline (legal, product, integration, flows, risk, strategy) with sources |
| [build_outputs.py](../tools/top5/mhyperbtc/build_outputs.py) | 77 | Build positions.csv, yield_monthly.csv, liquidity_ladder.csv from the raw datasets |
| [build_tvl_monthly.py](../tools/top5/mhyperbtc/build_tvl_monthly.py) | 30 | tvl_monthly.csv: month-end supply / NAV / TVL per chain (Midas tvl-snapshots-by-network), plus total with flows vs NAV effect |
| [eoa_profile.py](../tools/top5/mhyperbtc/eoa_profile.py) | 21 | Profile unknown counterparties: Blockscout tags + where they forward tokens (top outgoing counterparties) |
| [eth_daily_blocks.py](../tools/top5/mhyperbtc/eth_daily_blocks.py) | 27 | Ethereum last block at/before 00:00 UTC for each day 2025-10-14..2026-09-21 (batched RPC, iterative correction) |
| [fetch_por.py](../tools/top5/mhyperbtc/fetch_por.py) | 24 | Fetch all mHyperBTC PoR attestations (Midas Attestation Engine) from IPFS (pinata gateway, gzip) and tabulate |
| [flow_summary.py](../tools/top5/mhyperbtc/flow_summary.py) | 23 | Summarise ERC-20 flows of a wallet by token and counterparty; only whitelisted real tokens (spam/poisoning filtered) |
| [holder_history.py](../tools/top5/mhyperbtc/holder_history.py) | 36 | Month-end holdings of mHyperBTC by holder type (Ethereum + Monad logs): Morpho collateral, Pendle SY, EOAs; top-holder concentration |
| [holders_bs.py](../tools/top5/mhyperbtc/holders_bs.py) | 18 | Current token holders via Blockscout v2 (Ethereum, Rootstock) |
| [holders_buckets.py](../tools/top5/mhyperbtc/holders_buckets.py) | 57 | Current holders per chain, BTC-eq buckets, top-N concentration, contract vs EOA, collateral re-use (look-through) |
| [incentives.py](../tools/top5/mhyperbtc/incentives.py) | 59 | Incentives received by the strategy wallet, valued at claim-date prices (DefiLlama), monthly. Katana: Merkl totals allocated over the Katana-active period (estimate) |
| [monad_daily_balances.py](../tools/top5/mhyperbtc/monad_daily_balances.py) | 31 | Reconstruct daily (00:00 UTC) token balances of the strategy wallet on Monad from Transfer logs (no archive state on public Monad RPC) |
| [morpho_api.py](../tools/top5/mhyperbtc/morpho_api.py) | 12 | Функции: gql |
| [morpho_daily.py](../tools/top5/mhyperbtc/morpho_daily.py) | 38 | Build a daily table of Morpho positions of the strategy wallet: BTC collateral, dollar debt, vault holdings |
| [morpho_market_apy.py](../tools/top5/mhyperbtc/morpho_market_apy.py) | 19 | Daily borrow APY history of every Morpho market the strategy wallet touched (Morpho API) |
| [morpho_mhyper_markets.py](../tools/top5/mhyperbtc/morpho_mhyper_markets.py) | 27 | Morpho markets using mHyperBTC as collateral (Ethereum, Monad): state, borrowers, suppliers (vaults) |
| [morpho_pos_history.py](../tools/top5/mhyperbtc/morpho_pos_history.py) | 34 | Daily history of every Morpho market position and vault position of the mHyperBTC strategy wallet (Morpho API) |
| [morpho_txs.py](../tools/top5/mhyperbtc/morpho_txs.py) | 45 | All Morpho market + vault transactions of the mHyperBTC strategy wallet (Morpho API), Ethereum/Monad/Stable |
| [morpho_vaults.py](../tools/top5/mhyperbtc/morpho_vaults.py) | 24 | Morpho V2 vaults touched by the mHyperBTC strategy: fees, curator, allocation, positions (share of vault held by strategy) |
| [oracle_history.py](../tools/top5/mhyperbtc/oracle_history.py) | 32 | NAV oracle (MHyperBtcCustomAggregatorFeed proxy 0x3359...517C) AnswerUpdated history via Blockscout v2 |
| [read_views.py](../tools/top5/mhyperbtc/read_views.py) | 25 | Read all zero-arg view functions of a (proxy) contract using the implementation ABI from Blockscout |
| [rpc.py](../tools/top5/mhyperbtc/rpc.py) | 71 | Minimal JSON-RPC helpers for the mHyperBTC deep dive |
| [rpc_flow_summary.py](../tools/top5/mhyperbtc/rpc_flow_summary.py) | 25 | Summarise RPC Transfer logs of a wallet: resolve token symbols; group by token/direction/counterparty |
| [token_transfers_rpc.py](../tools/top5/mhyperbtc/token_transfers_rpc.py) | 24 | Pull all Transfer logs of a token via RPC in chunks; save json; reconcile balances vs totalSupply |
| [vault_income.py](../tools/top5/mhyperbtc/vault_income.py) | 45 | Income of the dollar (and BTC) vault positions: daily position assetsUsd x vault share-price growth (Morpho API), monthly |
| [wallet_logs_rpc.py](../tools/top5/mhyperbtc/wallet_logs_rpc.py) | 20 | All ERC-20 Transfer logs in/out of a wallet on an RPC chain (no explorer available: Monad, Stable) |
| [yield_monthly.py](../tools/top5/mhyperbtc/yield_monthly.py) | 49 | Monthly realized yield from the NAV oracle, vs on-chain borrow cost, dollar-vault income and incentives -> yield_monthly.csv |

### tools/top5/selection (67)

| Файл | Строк | Назначение |
|---|---:|---|
| [aave_deep_pages.py](../tools/top5/selection/aave_deep_pages.py) | 31 | Supplement: aEthWBTC / aEthcbBTC / spcbBTC / aBascbBTC holders ranks 101-400 (pages 3-8) -> getUserAccountData -> debt >= $2M |
| [aave_scan.py](../tools/top5/selection/aave_scan.py) | 61 | Aave v3 (Ethereum core/prime/etherfi, Base, Arbitrum) + Spark: top holders of BTC aTokens -> debt via getUserAccountData -> stable debt breakdown |
| [aave_v4_scan.py](../tools/top5/selection/aave_v4_scan.py) | 64 | Aave v4 (Ethereum): enumerate Spoke Borrow events (all spokes), per (spoke,user) getUserAccountData; for debt>=$2M, list BTC collateral reserves |
| [aave_v4_stage2.py](../tools/top5/selection/aave_v4_stage2.py) | 36 | Aave v4 stage 2: batch getUserAccountData for saved (spoke,user) pairs via publicnode; keep debt >= $2M; list BTC collateral + debts |
| [addrinfo.py](../tools/top5/selection/addrinfo.py) | 80 | Address classification helpers: eth_getCode (EOA / contract / EIP-7702 delegated), Blockscout names, Safe owners/threshold, EIP-1967 impl |
| [bitget_morph.py](../tools/top5/selection/bitget_morph.py) | 31 | Bitget bgBTC Onchain Earn: read Aera vault position in Morpho (Morph chain) via RPC |
| [blockat.py](../tools/top5/selection/blockat.py) | 13 | Функции: ts, block_at |
| [btc_addr_history.py](../tools/top5/selection/btc_addr_history.py) | 11 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [build_products_csv.py](../tools/top5/selection/build_products_csv.py) | 51 | carry_products_scan.csv: one row per product checked (qualifying and excluded) |
| [build_scan_csv.py](../tools/top5/selection/build_scan_csv.py) | 96 | Build scan_borrowers_all.csv: every BTC-collateral borrower with >= $2M dollar debt found in the scans, with EOA/contract class and identification |
| [classify_aave.py](../tools/top5/selection/classify_aave.py) | 21 | Функции: w |
| [classify_list.py](../tools/top5/selection/classify_list.py) | 10 | Функции: w |
| [classify_morpho.py](../tools/top5/selection/classify_morpho.py) | 19 | Функции: w |
| [compound_l2_scan.py](../tools/top5/selection/compound_l2_scan.py) | 24 | Compound v3 on Base/Arbitrum: SupplyCollateral logs via Blockscout (paged by block), current collateral/borrow via RPC |
| [compound_scan.py](../tools/top5/selection/compound_scan.py) | 38 | Compound v3: enumerate accounts that supplied BTC collateral (SupplyCollateral logs), read current collateral + borrow, keep debt >= $2M |
| [compound_totals.py](../tools/top5/selection/compound_totals.py) | 17 | Compound v3: BTC collateral totals per Comet |
| [core_btckey_cluster.py](../tools/top5/selection/core_btckey_cluster.py) | 32 | cluster Core BTC staking delegations by the Bitcoin key material in the CLTV redeem script |
| [core_btcstake_agg.py](../tools/top5/selection/core_btcstake_agg.py) | 28 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [core_btcstake_logs.py](../tools/top5/selection/core_btcstake_logs.py) | 29 | Scan Core BitcoinStake (0x...1014) delegated / btcExpired / undelegated events via public RPC |
| [core_btcstake_timeseries.py](../tools/top5/selection/core_btcstake_timeseries.py) | 20 | Функции: blk |
| [core_cluster_ts.py](../tools/top5/selection/core_cluster_ts.py) | 40 | Transitive cluster (Core delegator <-> BTC key) from a seed; then active-BTC time series for the cluster |
| [core_dele_detail.py](../tools/top5/selection/core_dele_detail.py) | 28 | Функции: bd, parse_script |
| [eoa_flows.py](../tools/top5/selection/eoa_flows.py) | 25 | Light check of large EOA borrowers: counterparties of recent stablecoin/BTC transfers (Blockscout names), to see if any is a product wallet |
| [etherfi_liquidbtc.py](../tools/top5/selection/etherfi_liquidbtc.py) | 15 | ether.fi Liquid BTC (Veda BoringVault 0x5f46...0726): Spark position + total shares (Ethereum + Optimism) x accountant rate, at 2026-09-20 12:00 UTC |
| [euler_scan.py](../tools/top5/selection/euler_scan.py) | 60 | Euler v2 (EVK) Ethereum/Base/Arbitrum: BTC-asset vaults -> top share holders -> EVC controllers -> debtOf -> keep debt >= $2M in stablecoins |
| [fluid_scan.py](../tools/top5/selection/fluid_scan.py) | 32 | Fluid vaults with BTC collateral (Ethereum/Base/Arbitrum): all positions via VaultPositionsResolver.getAllVaultPositions; keep debt >= $2M |
| [holdings.py](../tools/top5/selection/holdings.py) | 16 | Функции: holdings |
| [kamino_scan.py](../tools/top5/selection/kamino_scan.py) | 43 | Kamino (Solana) main market: obligations with BTC-wrapper deposits; parse owner, deposits/borrows market values (Sf = value * 2^60); keep borrowed >= $2M |
| [kraken_vault.py](../tools/top5/selection/kraken_vault.py) | 13 | Kraken Bitcoin Vault (Veda BoringVault "Advanced Strategies BTC", sentoraBTC) size on Ink at snapshot + Morpho loan-manager legs on Ethereum |
| [maple_text.py](../tools/top5/selection/maple_text.py) | 12 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechA_llama_tokens.py](../tools/top5/selection/mechA_llama_tokens.py) | 17 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechA_morpho_apex.py](../tools/top5/selection/mechA_morpho_apex.py) | 17 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechA_morpho_user.py](../tools/top5/selection/mechA_morpho_user.py) | 12 | Функции: user |
| [mechA_river_bob_logs.py](../tools/top5/selection/mechA_river_bob_logs.py) | 30 | Pull Transfer/Deposit logs for River vaults on BOB via RPC (mechA). Output raw/mechA/river_bob_logs.json |
| [mechA_river_bsc_logs.py](../tools/top5/selection/mechA_river_bsc_logs.py) | 36 | Find BSC block by timestamp and pull River bfBTC Prime Vault logs around given timestamps (mechA). |
| [mechA_river_holders.py](../tools/top5/selection/mechA_river_holders.py) | 41 | List holders of River SmartVault share tokens via Blockscout (Base, BOB, Ethereum, Hemi) and classify each holder (EOA/Safe/contract, name, creator, first funding). Output raw/mechA/river_holders.json |
| [mechA_river_identify.py](../tools/top5/selection/mechA_river_identify.py) | 46 | Identify River vault depositors: code type, Safe owners, where their BTC-wrapper came from (mechA). Base via Blockscout token-transfers; BOB via RPC getLogs on uniBTC Transfer(to=holder). Output raw/mechA/river_identify.json |
| [mechA_river_pps_history.py](../tools/top5/selection/mechA_river_pps_history.py) | 27 | Historical satUSD+ price-per-share and vault state on Base/BOB/BSC via archive eth_call where available (mechA). Output raw/mechA/river_pps_history.json |
| [mechA_river_selectors.py](../tools/top5/selection/mechA_river_selectors.py) | 30 | Compare function selectors of River SmartVault implementations across chains (mechA). |
| [mechA_river_staking.py](../tools/top5/selection/mechA_river_staking.py) | 25 | Read River satUSD+ staking vaults (mechA): share price, emission list, claimable rewards of SmartVaults, and the vaults' share of each pool. Output raw/mechA/river_staking.json |
| [mechA_river_vaults.py](../tools/top5/selection/mechA_river_vaults.py) | 83 | River Smart/Prime Vault on-chain reader (mechA). Reads every SmartVault listed in the DefiLlama satoshi-protocol adapter + any found via SmartVaultCreated logs, and dumps state to raw/mechA/river_vaults_state.json. Functions read (SmartVaul |
| [mechA_rpc.py](../tools/top5/selection/mechA_rpc.py) | 80 | Функции: rol, f, keccak, k256, sel, post |
| [mechA_upshift_subs.py](../tools/top5/selection/mechA_upshift_subs.py) | 19 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechB_addrinfo.py](../tools/top5/selection/mechB_addrinfo.py) | 23 | Функции: info |
| [mechB_bs_logs.py](../tools/top5/selection/mechB_bs_logs.py) | 15 | Функции: get |
| [mechB_hermetica.py](../tools/top5/selection/mechB_hermetica.py) | 33 | minimal clarity decode for uint/bool/ok wrappers |
| [mechB_holders.py](../tools/top5/selection/mechB_holders.py) | 14 | Функции: get |
| [mechB_ipor_btc.py](../tools/top5/selection/mechB_ipor_btc.py) | 17 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechB_keccak.py](../tools/top5/selection/mechB_keccak.py) | 31 | minimal pure-python keccak256 |
| [mechB_mezo_creator.py](../tools/top5/selection/mechB_mezo_creator.py) | 20 | Функции: get |
| [mechB_mezo_edm.py](../tools/top5/selection/mechB_mezo_edm.py) | 15 | Функции: c |
| [mechB_mezo_tt.py](../tools/top5/selection/mechB_mezo_tt.py) | 18 | Функции: get |
| [mechB_morpho.py](../tools/top5/selection/mechB_morpho.py) | 7 | Функции: gql |
| [mechB_morpho_borrowers.py](../tools/top5/selection/mechB_morpho_borrowers.py) | 20 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechB_morpho_btcmarkets.py](../tools/top5/selection/mechB_morpho_btcmarkets.py) | 18 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechB_morpho_v1btc.py](../tools/top5/selection/mechB_morpho_v1btc.py) | 17 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechB_morpho_v2btc.py](../tools/top5/selection/mechB_morpho_v2btc.py) | 22 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [mechB_rpc.py](../tools/top5/selection/mechB_rpc.py) | 25 | Функции: rpc, call, u, bal, s |
| [mechB_safe_usdt.py](../tools/top5/selection/mechB_safe_usdt.py) | 15 | Функции: get |
| [mechB_veda_tvl.py](../tools/top5/selection/mechB_veda_tvl.py) | 25 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [morpho.py](../tools/top5/selection/morpho.py) | 18 | Функции: gql |
| [morpho_btc_markets.py](../tools/top5/selection/morpho_btc_markets.py) | 20 | Fetch all Morpho Blue markets (all chains covered by blue-api) with BTC-like collateral and borrow >= $100k |
| [morpho_top_borrowers.py](../tools/top5/selection/morpho_top_borrowers.py) | 19 | For each Morpho BTC-collateral market with borrow >= $2M: list positions with debt >= $2M |
| [rpc.py](../tools/top5/selection/rpc.py) | 39 | Функции: k256, sel, post, call, batch, eth_call |
| [snapshot_0920.py](../tools/top5/selection/snapshot_0920.py) | 33 | Re-read Bitget (Morph), mHyperBTC (Morpho+Spark), Upshift Sentora BTC legs at 2026-09-20 12:00 UTC where archive RPC allows |
| [yb_value.py](../tools/top5/selection/yb_value.py) | 21 | Yield Basis BTC markets: depositor value in BTC via LT.pricePerShare()*totalSupply, and staked share |
| [yieldbasis.py](../tools/top5/selection/yieldbasis.py) | 54 | Yield Basis: per market BTC deposited (asset share of Curve pool owned by LEVAMM), crvUSD debt, allocation; crvUSD source |

### tools/top5/yieldbasis (23)

| Файл | Строк | Назначение |
|---|---:|---|
| [agg_events.py](../tools/top5/yieldbasis/agg_events.py) | 28 | Aggregate YB API event datasets (interest collected, LT/gauge flows) per market per month |
| [archive_monthend.py](../tools/top5/yieldbasis/archive_monthend.py) | 34 | Archive eth_call at month-end sample blocks (from API snapshot sampleBlockNumber) to verify PPS and read debt/rate/allocation/staked/watermark |
| [bs.py](../tools/top5/yieldbasis/bs.py) | 9 | Функции: get |
| [build_events.py](../tools/top5/yieldbasis/build_events.py) | 58 | events.csv: YB DAO proposals (execution dates from api.yieldbasis.com), Curve DAO votes (prices.curve.finance), |
| [build_monthly.py](../tools/top5/yieldbasis/build_monthly.py) | 93 | Build tvl_monthly.csv and yield_monthly.csv from YB API daily snapshots (verified vs archive eth_call), |
| [credit_line.py](../tools/top5/yieldbasis/credit_line.py) | 18 | Bisect the blocks where Curve DAO changed crvUSD debt_ceiling for the YB Factory (credit line) |
| [economics.py](../tools/top5/yieldbasis/economics.py) | 60 | Monthly protocol economics: admin-fee revenue, veYB distributions, YB emissions (units and USD), TVL, cost per $ TVL |
| [eth.py](../tools/top5/yieldbasis/eth.py) | 63 | Функции: rol, f, keccak, sel, call, rpc |
| [fetch_docs.py](../tools/top5/yieldbasis/fetch_docs.py) | 23 | Функции: txt |
| [holders.py](../tools/top5/yieldbasis/holders.py) | 21 | Fetch ERC-20 holders of LT (yb-LP) and gauge tokens from Blockscout |
| [holders_aggregate.py](../tools/top5/yieldbasis/holders_aggregate.py) | 25 | Aggregate per-address BTC-equivalent across all live BTC markets (v3 + deprecated v2 + v1) |
| [holders_analysis.py](../tools/top5/yieldbasis/holders_analysis.py) | 51 | Convert Blockscout holder balances to BTC-equivalent, bucket, concentration, holder type |
| [holding_period.py](../tools/top5/yieldbasis/holding_period.py) | 25 | Holding-period (cohort) returns in BTC terms: book PPS and redeemable value, per generation and chained across migrations |
| [liquidity_ladder.py](../tools/top5/yieldbasis/liquidity_ladder.py) | 26 | Exit liquidity ladder: LT.preview_withdraw(shares) vs pricePerShare at the current block, per market and size |
| [load.py](../tools/top5/yieldbasis/load.py) | 20 | Функции: day, snaps, series |
| [markets.py](../tools/top5/yieldbasis/markets.py) | 15 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [pager.py](../tools/top5/yieldbasis/pager.py) | 13 | Исследовательский скрипт; входы и импорты в JSON-инвентаре |
| [snap.py](../tools/top5/yieldbasis/snap.py) | 32 | Функции: snap |
| [staked_principal.py](../tools/top5/yieldbasis/staked_principal.py) | 19 | Staked-side principal in BTC per gauge share at month-end (archive eth_call): gauge.totalAssets()/totalSupply() * LT.pricePerShare() |
| [trd_stats.py](../tools/top5/yieldbasis/trd_stats.py) | 24 | Temporary Redemption Discount (TRD) statistics from daily snapshots |
| [ybapi.py](../tools/top5/yieldbasis/ybapi.py) | 13 | Функции: api |
| [ybrpc.py](../tools/top5/yieldbasis/ybrpc.py) | 48 | Функции: rpc, ec, u, words, addr, s |
| [yield_summary.py](../tools/top5/yieldbasis/yield_summary.py) | 52 | Protocol-level (TVL-weighted) monthly BTC yield series, organic vs incentive split, stability stats |

## CSV — все доступные таблицы

Число записей ниже соответствует обычному CSV-чтению. В таблицах с footer-комментариями оно включает комментарии; для анализа числовых наблюдений их нужно отфильтровать.

| Файл | Записей | Колонки |
|---|---:|---|
| [data/c1_histories.csv](../data/c1_histories.csv) | 70 | month, product_id, tvl_btc |
| [data/c1_pending_proxy_history.csv](../data/c1_pending_proxy_history.csv) | 25 | month, kraken_vault_proxy_veda_ink_kbtc_units, bitget_earn_proxy_aera_v3_bgbtc_units, etherfi_liquid_proxy_btc_units_all_vaults |
| [data/c6_groups.csv](../data/c6_groups.csv) | 85 | product, group, btc_tokens, label |
| [data/category_flows_monthly.csv](../data/category_flows_monthly.csv) | 168 | month, category_code, delta_usd_net, net_flow_btc, net_flow_usd, price_effect_usd, residual_usd |
| [data/category_history_monthly.csv](../data/category_history_monthly.csv) | 150 | month, category_code, tvl_usd_gross, tvl_btc_gross, tvl_usd_net, tvl_btc_net, share_net |
| [data/lending_products.csv](../data/lending_products.csv) | 16 | product, category_code, in_snapshot, reason |
| [data/market_map_current.csv](../data/market_map_current.csv) | 205 | product, slug, category_code, category_name, subcategory, tvl_usd, tvl_btc, source, method, offchain, double_count_note, include_net, justification |
| [data/market_map_history_monthly.csv](../data/market_map_history_monthly.csv) | 2899 | month, product, category_code, tvl_usd, tvl_btc, include_net |
| [data/money_markets.csv](../data/money_markets.csv) | 99 | segment, protocol, slug, btc_supplied, btc_plain, btc_yieldbearing, btc_lent_out, btc_in_counted_products, btc_counted, supply_apy, how, url |
| [data/money_markets_monthly.csv](../data/money_markets_monthly.csv) | 2475 | segment, protocol, slug, month, btc_counted, usd_counted |
| [data/outside_totals.csv](../data/outside_totals.csv) | 20 | kind, product, yield_btc, size, why_not_counted, url |
| [data/product_notes.csv](../data/product_notes.csv) | 113 | product, how, yield_btc, run_by, url |
| [data/top5/bitget/events.csv](../data/top5/bitget/events.csv) | 29 | date, event, type, source |
| [data/top5/bitget/holders.csv](../data/top5/bitget/holders.csv) | 17 | asset, chain, address, label, amount, share |
| [data/top5/bitget/liquidity_ladder.csv](../data/top5/bitget/liquidity_ladder.csv) | 12 | horizon, source, amount, unit, who_can_access, evidence |
| [data/top5/bitget/tvl_weekly.csv](../data/top5/bitget/tvl_weekly.csv) | 10 | date, morph_block, btc_usd_redstone, vault_collateral_bgbtc, vault_nav_bgbtc, vault_nav_usd, vault_debt_usdc, vault_ltv_pct, gtusdc_tvl_usd, gtusdc_owned_by_vault_usd, gtusdc_external_usd, gtusdc_idle_usd, market_supply_usd, market_borrow_usd, headline_tvl_usd, net_external_capital_usd, bgbtc_supply_morph, bgbtc_supply_ethereum, bgbtc_ccip_locked_eth, por_reserves_btc, defillama_bitget_bgbtc_usd |
| [data/top5/bitget/yield_weekly.csv](../data/top5/bitget/yield_weekly.csv) | 8 | week, days, vault_realized_apy, borrow_rate, gtusdc_apy_organic, incentives_apy, spread, notes |
| [data/top5/etherfi/events.csv](../data/top5/etherfi/events.csv) | 55 | date, event, type, source |
| [data/top5/etherfi/holders_buckets.csv](../data/top5/etherfi/holders_buckets.csv) | 49 | section, chain, label, holders, btc_eq, share_pct_or_value |
| [data/top5/etherfi/liquidity_ladder.csv](../data/top5/etherfi/liquidity_ladder.csv) | 10 | step, source, asset_out, amount_native, amount_usd, cumulative_usd, cumulative_pct_of_debt, time_to_cash, mechanism, evidence |
| [data/top5/etherfi/positions_monthly.csv](../data/top5/etherfi/positions_monthly.csv) | 23 | month, collateral_btc, debt_usd, ltv, holdings, btc_usd, nav_btc, min_health_factor, min_hf_account, liq_btc_price_est, btc_debt_btc, deployed_usd, debt_by_venue, reconstructed_net_btc, residual_vs_nav_btc, month_min_btc_close, month_min_date, hf_at_month_low_est |
| [data/top5/etherfi/tvl_monthly.csv](../data/top5/etherfi/tvl_monthly.csv) | 23 | month, month_end_utc, rate_btc_per_share, shares_ethereum, shares_optimism, shares_scroll, shares_total, nav_btc, btc_usd, tvl_usd, net_flow_all_chains_btc, yield_btc, tvl_change_usd, price_effect_usd, flow_effect_usd, yield_effect_usd, eth_deposits_btc, eth_withdrawals_btc, eth_net_real_flow_btc, n_deposits_eth, n_withdrawals_eth, deposits_by_asset_btc, bridge_out_from_eth_btc, bridge_in_to_eth_btc, holders_ethereum, holders_optimism |
| [data/top5/etherfi/yield_monthly.csv](../data/top5/etherfi/yield_monthly.csv) | 22 | month, realized_net_apy, borrow_pyusd, borrow_usdc, depl_stcusd, depl_paypal_main_total, depl_paypal_main_organic, spread, organic_spread, notes, actual_borrow_apy, actual_deploy_organic_apy, actual_deploy_reward_apy, avg_debt_usd, avg_deployed_usd, carry_contrib_to_nav_apy, vault_token_incentives_to_nav_apy, platform_fee_bps_avg, avg_nav_btc, hypo_current_structure_spread, hypo_current_structure_organic_spread |
| [data/top5/kraken/events.csv](../data/top5/kraken/events.csv) | 78 | date, event, type, source |
| [data/top5/kraken/holders_buckets.csv](../data/top5/kraken/holders_buckets.csv) | 21 | bucket_btc, holders, holders_pct, btc, btc_pct, avg_btc |
| [data/top5/kraken/holders_types.csv](../data/top5/kraken/holders_types.csv) | 7 | view, type, holders, holders_pct, shares_or_btc, balance_pct |
| [data/top5/kraken/liquidity_ladder.csv](../data/top5/kraken/liquidity_ladder.csv) | 11 | tier, usd_m, pct_of_debt, cum_pct, source |
| [data/top5/kraken/ltv_weekly.csv](../data/top5/kraken/ltv_weekly.csv) | 22 | date, btc_usd, RLUSD-1_coll_kbtc, RLUSD-1_debt_musd, RLUSD-1_ltv, RLUSD-1_hf, RLUSD-1_liq_px, RLUSD-1_drop_to_liq_pct, RLUSD-2_coll_kbtc, RLUSD-2_debt_musd, RLUSD-2_ltv, RLUSD-2_hf, RLUSD-2_liq_px, RLUSD-2_drop_to_liq_pct, PYUSD-1_coll_kbtc, PYUSD-1_debt_musd, PYUSD-1_ltv, PYUSD-1_hf, PYUSD-1_liq_px, PYUSD-1_drop_to_liq_pct, PYUSD-2_coll_kbtc, PYUSD-2_debt_musd, PYUSD-2_ltv, PYUSD-2_hf, PYUSD-2_liq_px, PYUSD-2_drop_to_liq_pct, kbtc_total_ltv, aave_wbtc, aave_usdt_debt_musd, aave_hf, aave_liq_px, morpho_wbtc_usdt_ltv, morpho_wbtc_usdt_debt_musd |
| [data/top5/kraken/tvl_weekly.csv](../data/top5/kraken/tvl_weekly.csv) | 28 | week, tvl_btc_end, btc_usd_end, tvl_usd_end_m, holders_end, new_depositors, deposit_txs, deposits_btc, withdrawals_btc, withdraw_requests_btc, net_flow_btc, yield_btc, d_tvl_usd_m, flow_effect_usd_m, price_effect_usd_m, yield_effect_usd_m, avg_deposit_btc |
| [data/top5/kraken/yield_weekly.csv](../data/top5/kraken/yield_weekly.csv) | 25 | week, realized_net_apy, borrow_rlusd, borrow_pyusd, depl_rlusd_total, depl_rlusd_organic, depl_pyusd_total, depl_pyusd_organic, prime, weighted_spread, organic_spread, borrow_aave_usdt, borrow_morpho_wbtc_usdt, depl_prime_main_total, depl_prime_main_organic, depl_pst_total, depl_pst_organic, debt_A_RLUSD_musd, debt_B_RLUSD_musd, debt_A_PYUSD_musd, debt_B_PYUSD_musd, debt_C_AAVE_musd, debt_D_WBTCUSDT_musd, debt_to_nav, model_gross_on_nav, model_net_on_nav, model_net_no_rewards |
| [data/top5/maple/events.csv](../data/top5/maple/events.csv) | 40 | date, event, type, source |
| [data/top5/maple/size_history.csv](../data/top5/maple/size_history.csv) | 38 | date, btc, usd, source |
| [data/top5/maple/yield_history.csv](../data/top5/maple/yield_history.csv) | 13 | period, realized_apy, core_staking_apr, core_price, notes, source |
| [data/top5/mhyperbtc/events.csv](../data/top5/mhyperbtc/events.csv) | 45 | date, event, type, source |
| [data/top5/mhyperbtc/holders_buckets.csv](../data/top5/mhyperbtc/holders_buckets.csv) | 35 | chain, bucket_btc_eq, holders, btc_eq, share, contracts, eoas, note |
| [data/top5/mhyperbtc/liquidity_ladder.csv](../data/top5/mhyperbtc/liquidity_ladder.csv) | 10 | tier, source, chain, amount_usd, amount_btc, time_to_cash, constraint, data_source |
| [data/top5/mhyperbtc/positions.csv](../data/top5/mhyperbtc/positions.csv) | 81 | date, venue, chain, role, collateral, collateral_amount, collateral_usd, debt_asset, debt_usd, ltv, lltv_or_lt, liq_price_usd, source, note |
| [data/top5/mhyperbtc/tvl_monthly.csv](../data/top5/mhyperbtc/tvl_monthly.csv) | 40 | month, chain, supply, nav, tvl_btc, tvl_usd, share_of_supply, net_flow_btc, nav_effect_btc, as_of |
| [data/top5/mhyperbtc/yield_monthly.csv](../data/top5/mhyperbtc/yield_monthly.csv) | 12 | month, realized_apy, borrow_cost, notes, nav_start, nav_end, days, realized_return, avg_supply, nav_gain_btc, nav_gain_usd, avg_usd_debt_onchain, borrow_interest_usd, stable_loop_interest_usd, usd_vault_income_usd, btc_vault_income_usd, incentives_usd, incentives_share_of_gain |
| [data/top5/selection/carry_products_scan.csv](../data/top5/selection/carry_products_scan.csv) | 26 | rank, product, chain, collateral_btc, debt_usd, borrowed_asset, venue, contract_addresses, fits_definition, notes, btc_deposits, as_of, evidence |
| [data/top5/selection/scan_borrowers_all.csv](../data/top5/selection/scan_borrowers_all.csv) | 319 | venue, chain, address, kind, btc_collateral, collateral_usd, debt_usd, borrowed, identified_as, fits_definition |
| [data/top5/yieldbasis/economics_monthly.csv](../data/top5/yieldbasis/economics_monthly.csv) | 13 | month, avg_tvl_usd_protocol_defillama, avg_tvl_usd_btc_markets, yb_emitted_btc_gauges, yb_emitted_eth_gauges, yb_emissions_usd_btc_gauges, yb_emissions_usd_all, avg_yb_price, admin_fee_accrued_usd_btc, admin_fee_accrued_usd_all, veyb_distributed_usd, emission_cost_pct_btc_tvl_ann, admin_rev_pct_btc_tvl_ann |
| [data/top5/yieldbasis/events.csv](../data/top5/yieldbasis/events.csv) | 110 | date, event, type, source, btc_tvl_d_minus1, btc_tvl_d_plus7 |
| [data/top5/yieldbasis/holders_buckets.csv](../data/top5/yieldbasis/holders_buckets.csv) | 66 | market, bucket_btc_equiv, holders, btc_equiv, share_of_market_pct |
| [data/top5/yieldbasis/liquidity_ladder.csv](../data/top5/yieldbasis/liquidity_ladder.csv) | 61 | block, time, market, shares, share_of_supply_pct, book_value_asset, redeem_asset, haircut_vs_book_pct, pps, pool_price_scale, pool_price_oracle, ps_lag_pct, pool_crvusd, pool_asset, pool_crvusd_share_pct, cap_usd, tvl_asset |
| [data/top5/yieldbasis/tvl_monthly.csv](../data/top5/yieldbasis/tvl_monthly.csv) | 127 | month, pool, asset, date, tvl_btc, tvl_usd, tvl_btc_redeemable, tvl_usd_redeemable, asset_price_usd, net_flow_asset, flow_method, cap_usd, debt_crvusd |
| [data/top5/yieldbasis/yield_monthly.csv](../data/top5/yieldbasis/yield_monthly.csv) | 101 | month, pool, unstaked_realized_apy, staked_reward_apy, crvusd_rate, rebalancing_loss_est, notes, period, days, unstaked_redeemable_apy, interest_paid_usd, interest_cost_pct_equity_ann, gross_pool_income_est, watermark_gap_end_pct, trd_end_pct, pps_start, pps_end, redeem_start, redeem_end |
| [data/top5/yieldbasis/yield_protocol_monthly.csv](../data/top5/yieldbasis/yield_protocol_monthly.csv) | 13 | month, unstaked_book_apy, unstaked_redeemable_apy, staked_token_apr, staked_frac, blended_lp_apy, organic_to_unstaked_usd, admin_fees_usd, incentive_yb_usd, organic_share_of_lp_income |
| [tools/marketmap/inputs/c1_histories.csv](../tools/marketmap/inputs/c1_histories.csv) | 70 | month, product_id, tvl_btc |
| [tools/marketmap/money_markets/mm_apy.csv](../tools/marketmap/money_markets/mm_apy.csv) | 84 | project, chain, symbol, pool_meta, btc_0923, tvl_usd_0923, btc_can_be_lent, supply_apy_base_pct, supply_apy_reward_pct, supply_apy_total_pct, supply_apy_mean30d_pct, btc_utilization, btc_borrow_apy_pct, dollar_loan_apy_pct, note |
| [tools/marketmap/money_markets/mm_monthly.csv](../tools/marketmap/money_markets/mm_monthly.csv) | 3150 | segment, protocol, slug, month, btc_total, btc_plain, btc_yieldbearing, btc_borrowed, usd, source |
| [tools/marketmap/money_markets/mm_overlap.csv](../tools/marketmap/money_markets/mm_overlap.csv) | 3259 | product_already_counted, protocol, btc, method, confidence, month, group, segment, slug, chain, in_column, note |
| [tools/marketmap/money_markets/mm_protocols.csv](../tools/marketmap/money_markets/mm_protocols.csv) | 126 | segment, protocol, slug, defillama_category, included_because, btc_total_0920, btc_borrowed_0920, btc_yieldbearing_0920, peak_month, peak_btc_supplied, btc_total_2024_09, yields_pools_0920_btc, yields_pools_n, chains_0920 |
| [tools/marketmap/money_markets/mm_tokens_snapshot.csv](../tools/marketmap/money_markets/mm_tokens_snapshot.csv) | 576 | segment, protocol, slug, chain, token, class, counted_at_map_product, btc_in_tvl, btc_borrowed, usd_in_tvl |

## Исследовательские документы исходной версии

| Файл | Строк | Ссылок HTTP(S) |
|---|---:|---:|
| [AUDIT.md](../AUDIT.md) | 207 | 0 |
| [BTC-Carry-Vaults-Dossiers.md](../BTC-Carry-Vaults-Dossiers.md) | 1302 | 60 |
| [BTC-Yield-Deep-Dive.md](../BTC-Yield-Deep-Dive.md) | 464 | 0 |
| [BTC-Yield-Market-Research.md](../BTC-Yield-Market-Research.md) | 651 | 41 |
| [BTC-Yield-Product-Catalog.md](../BTC-Yield-Product-Catalog.md) | 421 | 0 |
| [README.md](../README.md) | 90 | 1 |
| [REPORT.md](../REPORT.md) | 1372 | 1 |
| [RESEARCH-PLAN.md](../RESEARCH-PLAN.md) | 295 | 0 |
| [data/marketmap_notes.md](../data/marketmap_notes.md) | 209 | 1 |
| [data/marketmap_overlap.md](../data/marketmap_overlap.md) | 168 | 0 |
| [research/top5/00-selection.md](../research/top5/00-selection.md) | 202 | 0 |
| [research/top5/01-kraken.md](../research/top5/01-kraken.md) | 746 | 0 |
| [research/top5/02-yield-basis.md](../research/top5/02-yield-basis.md) | 532 | 0 |
| [research/top5/03-bitget.md](../research/top5/03-bitget.md) | 323 | 0 |
| [research/top5/04-mhyperbtc.md](../research/top5/04-mhyperbtc.md) | 422 | 1 |
| [research/top5/05-etherfi.md](../research/top5/05-etherfi.md) | 488 | 0 |
| [research/top5/06-maple.md](../research/top5/06-maple.md) | 442 | 20 |
| [research/top5/en/00-selection.md](../research/top5/en/00-selection.md) | 201 | 0 |
| [research/top5/en/01-kraken.md](../research/top5/en/01-kraken.md) | 745 | 0 |
| [research/top5/en/02-yield-basis.md](../research/top5/en/02-yield-basis.md) | 530 | 0 |
| [research/top5/en/03-bitget.md](../research/top5/en/03-bitget.md) | 321 | 0 |
| [research/top5/en/04-mhyperbtc.md](../research/top5/en/04-mhyperbtc.md) | 421 | 1 |
| [research/top5/en/05-etherfi.md](../research/top5/en/05-etherfi.md) | 487 | 0 |
| [research/top5/en/06-maple.md](../research/top5/en/06-maple.md) | 441 | 20 |
| [tools/marketmap/README.md](../tools/marketmap/README.md) | 13 | 0 |
| [tools/marketmap/money_markets/mm_notes.md](../tools/marketmap/money_markets/mm_notes.md) | 355 | 0 |

## Проверки сохранённых результатов

- Все 257 Python-файлов имеют корректный AST-синтаксис.
- В CSV-инвентаре 54 файлов; в исходном файловом инвентаре 384 файлов.
- V3, построенный из сохранённых CSV, совпадает с inline V3 в index.html.
- site/index.html соответствует текущему tools/build_site.py.
- Базовая сумма сайта: 94 361,21 BTC; 101 продукт с положительным размером.
- C2 лидирует в 25 из 25 исторических точек базового охвата.
- Шесть текущих продуктов без истории: 4 540,80 BTC.
- Полный повторный расчёт по chain/raw не выполнен: большие raw-папки и часть прежних входов отсутствуют.
