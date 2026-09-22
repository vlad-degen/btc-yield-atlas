# BTC-yield market map: method, exclusions, gaps

Snapshot 2026-09-20; history 2024-09 to 2026-09 (month-end). Produced 2026-09-21 from APIs only (DefiLlama, Babylon, Core, Binance, mempool.space). Values marked ESTIMATE or flagged in `market_map_current.csv` are not measured on-chain.

## Files

- `market_map_current.csv`: one row per product (overlapping products split into a gross-only part and a net part); C0 context and excluded wrappers listed at the bottom.
- `market_map_history_monthly.csv`: month x product (same splits), plus an `include_net` column.
- `category_history_monthly.csv`: month x category: gross/net USD and BTC, net share.
- `category_flows_monthly.csv`: month x category: change in net USD split into net flow (BTC change at average price) and price effect (price change on average BTC).
- `c1_pending_proxy_history.csv`: DefiLlama proxies for the C1 products, for comparison with the merged on-chain histories.
- `jump_candidates.csv`: automatically detected step changes in DefiLlama series (persistent >35% one-day moves over $25M) for review.
- `overlap.md`: double-counting analysis, gross vs net.
- `scripts/`: re-runnable pipeline, see "Re-run" below.
- `raw/`: all API pulls.

## Conventions

- **Snapshot point:** DefiLlama daily point stamped 2026-09-20 00:00 UTC; USD from `tokensInUsd`, BTC = USD / $81,178 (Binance close 2026-09-20). Values supplied from on-chain work (Kraken 6,492.7 BTC; Yield Basis 1,326.2 BTC of depositor equity; Bitget 801.7 bgBTC; ether.fi Liquid BTC ~232 BTC; Maple 0) are BTC and are converted at $81,178. Their month-end histories are merged from inputs/c1_histories.csv (on-chain).
- **Month-end point:** DefiLlama point stamped 00:00 UTC on the 1st of the next month (= end of the last day), converted at the Binance close of the last day. The 2026-09 row is the 09-20 snapshot. Yields-pool series use the point stamped on the last day.
- **BTC part only:** sum of BTC-denominated symbols in the protocol-level (or chain-level) `tokensInUsd` breakdown (list in `scripts/lib.py`: BTC, WBTC, cbBTC, BTCB, BTC.b, kBTC, LBTC, tBTC, FBTC, SolvBTC and variants, xSolvBTC, uniBTC/brBTC, enzoBTC, stBTC, bgBTC, sBTC, UBTC, eBTC, LBTCv, pumpBTC, M-BTC/mBTC, YBTC, cirBTC, xBTC, zBTC, bfBTC, lfBTC-*, RBTC, avBTC, mHyperBTC, BTCOC, BTC-only Curve LPs, etc.). Mixed LP tokens (tricrypto, WBTC/WETH) count at an estimated BTC share (1/3 or 1/2); they are a few million USD in total. Protocols without a token breakdown that are BTC-only (Hermetica, Lorenzo stBTC, Chakra, alloBTC, pSTAKE, LISA) use total TVL (method `total`).
- **DefiLlama TVL convention:** idle balances; lent-out balances are excluded unless noted. For Accountable and Zest v2 (lending-type yield products) the `-borrowed` keys are added, so the row is total supplied BTC.
- **Flows vs price:** for months t-1 -> t, net flow = (B_t - B_{t-1}) x (P_{t-1} + P_t)/2 and price effect = (P_t - P_{t-1}) x (B_{t-1} + B_t)/2; the two add up to the USD change exactly.

## Universe

1. DefiLlama `/protocols` (8,317 protocols): every protocol in Restaked BTC, Anchor BTC, Basis Trading, Leveraged Farming, Onchain Capital Allocator, Yield, Staking Pool, Restaking, CDP, Yield Aggregator, Governance Incentives, Risk Curators (plus Farm, Options, Options Vault, CeDeFi, Uncollateralized Lending, Liquid Restaking, Dual-Token Stablecoin and BTC-named Bridge/Liquid Staking entries) was pulled via `/protocol/{slug}` (1994 files). Lending-category protocols were pulled only where they are yield products (Maple, Zest, Accountable, Native Credit Pool, BTC lending venues); plain money markets are C0 context.
2. Kept: protocols whose BTC-token part is >= ~$0.25M today or reached >= $3M at any month-end since 2024-09 (history screen catches dead products such as Corn, Royco, DeSyn, Pell, Kernel).
3. Added from the catalog/dossiers: Kraken Bitcoin Vault, Bitget bgBTC Earn, ether.fi Liquid BTC, Maple BTC Yield (on-chain history), Core staking (Core API), Midas mHyperBTC/mRe7BTC/mBTC, Tesseract and BTCD carry vaults, ether.fi eBTC (DefiLlama yields pools), off-chain funds.
4. Classified into C1-C6 by the plan's taxonomy; any product with a dollar loan against BTC is C1. 111 C1-C6 rows today (98 in the net).

## Key classification decisions

- **Lombard LBTC** switches category: C2 (Babylon LST) through 2026-07, C4 (Bitwise covered call, live 13.08.2026) from 2026-08. Lombard staker keys still had ~10.1k BTC in Babylon at end-June 2026 (all of LBTC) and ~130 BTC at end-July.
- **Lombard Vaults (LBTCv/BTCe)**: C6 (DeFi money-market/points vault) through 2026-06; C5 from 2026-07 (BTCe credit leg since 23.07.2026: LBTC as slashable cover for a loan on Cap).
- **Yield Basis** is C1 (hybrid: user BTC plus borrowed crvUSD into a 2x LP), per the plan rule "dollar debt under BTC -> C1".
- **Avalon CeDeFi** (USDT debt against lfBTC) is C0, not C1: it is a pool for four institutional Safes, the USDT went to Binance deposit addresses, DefiLlama says it is 100% team-deposited and it has been static since 11-2024. It is not a product with outside depositors (top-5 check).
- **Hermetica hBTC** stays C1 although the strategy was wound down 18.06.2026 (46.9 BTC left).
- **River Omni-CDP** is C0, not a yield product: users post bfBTC/uniBTC/UBTC to mint satUSD. The BTC holder earns nothing from River (only the LST's own yield), so it is borrowing context; counting it would double count bfBTC and uniBTC.
- **Mezo Earn** (veBTC) is C6 per the plan. Mezo Borrow (MUSD CDP) is C0.
- **Zest v2** sBTC supply is C6 (incentive-driven), per the plan; it is removed from the C0 money-market number to avoid counting it twice. Zest's "STBTC" ($10.9M) is excluded: the yields API lists it as stSTXbtc (an STX token) while the protocol breakdown prices it as BTC.
- **Accountable** (cbBTC/wcBTC) is C5 (uncollateralized credit); also removed from the C0 number.
- **Curator BTC vaults** (Gauntlet, Steakhouse, Re7, Sentora WBTC, Hyperithm cbBTC on Monad, etc.) are C0: BTC lending at ~0% (plan: "BTC-vaults Morpho under ~0%"). Sentora's and Veda's kBTC on Ink are the Kraken vault and are counted only in the Kraken row.
- **BitFi** bfBTC: both DefiLlama slugs (EVM chains; AILayer) are C3 (BitFi CeDeFi basis/staking; mechanism not verified). AILayer farm (84.6M on Bitcoin) is treated as the same BTC as bfBTC on AILayer and kept out of the net.
- **Vishwa** (865 BTC) and **ObeliskBTC** are placed in C2 with a flag: yield mechanism not disclosed.
- **Midas mHyperBTC** is C1 (its strategy wallet posts cbBTC on Morpho/Spark and borrows USDT/USDS; Midas transparency API) and uses the three DefiLlama yields pools ($30.5M in total; the Hyperithm curator entry shows only the Ethereum part). Pool histories start 06-2026, so earlier months are missing.
- **Two Prime Axiom** is on-chain (Pareto) but not tracked by DefiLlama; recorded from the dossier (150 WBTC) with offchain=1.
- **Xapo Byzantine** (ESTIMATE): $100M phase-1 allocation used = 1,231.9 BTC at $81,178. The 3,000 BTC "seed" (2024) is the upper bound. Reason: the $100M is the fund-level allocation tied to the current mandate; the 2024 seed has no later confirmation and the fund page (launch 15.09.2024, net yield 2.94%) publishes no AUM.
- **Starboard Sygnum BTC Alpha**: 750 BTC (disclosed "750+", a lower bound).
- **Coinbase CBYF**: size not disclosed; blank, not in totals. **Maple BTC Yield**: 0 today; its 2025 history (up to 1,758 BTC) is reconstructed on-chain from Core CLTV stakes and merged.

## Exclusions

- Bare wrappers and bridges: WBTC, cbBTC, BTCB, kBTC, FBTC, enzoBTC, base SolvBTC, tBTC, BTC.b, bgBTC, sBTC, UBTC (Unit), xBTC (OKX), cirBTC, Nexus BTC, YBTC (Bitlayer), Merlin's Seal (M-BTC bridge custody), Katana vault bridge, bridge entries for Core/Echo/Mezo/exSat/BOB.
- Yield-tokenization venues (Pendle, Spectra, RateX, Nemo): their BTC is the LSTs already counted.
- USD-denominated products backed partly by BTC (Ethena, Falcon), DEX LPs (out of scope; Chainflip AMM listed as excluded), StackingDAO (STX staking), BTCST (hashrate).
- **C0 context (not yield):** money-market BTC collateral $13.75B (169,406 BTC; DefiLlama yields pools 09-20: $13.86B less Zest v2 and Accountable). Separately listed and not additive with it: curator BTC lending vaults 1,589 BTC, CDP collateral 5,240 BTC (includes River 1,244 BTC), BTC lending venues 495 BTC.

## History results

| Month | C1 net BTC (share) | C2 net BTC (share) | C3 net BTC (share) | C4 net BTC (share) | C5 net BTC (share) | C6 net BTC (share) | Net BTC | Net USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-09 | 0 (0.0%) | 11,518 (37.6%) | 8,882 (29.0%) | 109 (0.4%) | 3 (0.0%) | 10,122 (33.0%) | 30,634 | $1.94B |
| 2024-10 | 0 (0.0%) | 35,908 (52.3%) | 12,786 (18.6%) | 108 (0.2%) | 3 (0.0%) | 19,814 (28.9%) | 68,619 | $4.82B |
| 2024-11 | 0 (0.0%) | 48,339 (50.8%) | 10,266 (10.8%) | 107 (0.1%) | 1 (0.0%) | 36,372 (38.2%) | 95,084 | $9.17B |
| 2024-12 | 0 (0.0%) | 78,786 (69.1%) | 2,666 (2.3%) | 106 (0.1%) | 21 (0.0%) | 32,507 (28.5%) | 114,086 | $10.68B |
| 2025-01 | 214 (0.2%) | 83,007 (70.2%) | 2,543 (2.1%) | 113 (0.1%) | 21 (0.0%) | 32,294 (27.3%) | 118,191 | $12.11B |
| 2025-02 | 764 (0.6%) | 80,713 (67.0%) | 2,631 (2.2%) | 113 (0.1%) | 20 (0.0%) | 36,317 (30.1%) | 120,558 | $10.17B |
| 2025-03 | 1,101 (0.9%) | 83,068 (65.2%) | 3,647 (2.9%) | 78 (0.1%) | 2 (0.0%) | 39,461 (31.0%) | 127,356 | $10.51B |
| 2025-04 | 2,208 (1.8%) | 74,179 (61.3%) | 4,126 (3.4%) | 76 (0.1%) | 2 (0.0%) | 40,395 (33.4%) | 120,987 | $11.39B |
| 2025-05 | 2,132 (1.8%) | 69,743 (59.5%) | 4,207 (3.6%) | 80 (0.1%) | 3 (0.0%) | 41,002 (35.0%) | 117,166 | $12.25B |
| 2025-06 | 1,533 (1.5%) | 62,098 (60.0%) | 4,258 (4.1%) | 83 (0.1%) | 2 (0.0%) | 35,580 (34.4%) | 103,555 | $11.10B |
| 2025-07 | 1,485 (1.5%) | 60,570 (60.4%) | 4,330 (4.3%) | 59 (0.1%) | 18 (0.0%) | 33,842 (33.7%) | 100,304 | $11.61B |
| 2025-08 | 1,938 (1.7%) | 74,178 (64.9%) | 6,190 (5.4%) | 58 (0.1%) | 0 (0.0%) | 31,952 (28.0%) | 114,315 | $12.37B |
| 2025-09 | 1,843 (1.6%) | 76,346 (67.8%) | 7,575 (6.7%) | 57 (0.1%) | 5 (0.0%) | 26,709 (23.7%) | 112,535 | $12.83B |
| 2025-10 | 3,109 (2.7%) | 76,324 (67.4%) | 7,206 (6.4%) | 67 (0.1%) | 6 (0.0%) | 26,563 (23.4%) | 113,275 | $12.42B |
| 2025-11 | 2,001 (2.1%) | 69,735 (74.7%) | 7,305 (7.8%) | 76 (0.1%) | 2 (0.0%) | 14,201 (15.2%) | 93,320 | $8.43B |
| 2025-12 | 2,914 (2.9%) | 77,857 (77.6%) | 7,472 (7.4%) | 98 (0.1%) | 36 (0.0%) | 11,905 (11.9%) | 100,281 | $8.79B |
| 2026-01 | 3,263 (3.4%) | 73,814 (77.6%) | 6,928 (7.3%) | 97 (0.1%) | 43 (0.0%) | 10,913 (11.5%) | 95,057 | $7.48B |
| 2026-02 | 3,339 (3.9%) | 63,509 (74.2%) | 7,502 (8.8%) | 108 (0.1%) | 114 (0.1%) | 10,962 (12.8%) | 85,535 | $5.73B |
| 2026-03 | 3,318 (3.8%) | 66,619 (75.2%) | 7,060 (8.0%) | 139 (0.2%) | 199 (0.2%) | 11,244 (12.7%) | 88,579 | $6.05B |
| 2026-04 | 2,408 (2.7%) | 66,627 (75.3%) | 7,211 (8.2%) | 115 (0.1%) | 168 (0.2%) | 11,924 (13.5%) | 88,453 | $6.75B |
| 2026-05 | 3,647 (4.1%) | 65,852 (74.3%) | 7,162 (8.1%) | 125 (0.1%) | 327 (0.4%) | 11,473 (13.0%) | 88,587 | $6.53B |
| 2026-06 | 6,588 (7.3%) | 65,665 (72.6%) | 7,042 (7.8%) | 115 (0.1%) | 318 (0.4%) | 10,716 (11.8%) | 90,443 | $5.30B |
| 2026-07 | 8,236 (9.1%) | 64,976 (71.7%) | 6,547 (7.2%) | 122 (0.1%) | 679 (0.8%) | 10,104 (11.1%) | 90,665 | $5.70B |
| 2026-08 | 9,001 (10.1%) | 54,525 (61.2%) | 6,682 (7.5%) | 8,159 (9.2%) | 1,296 (1.5%) | 9,441 (10.6%) | 89,104 | $7.00B |
| 2026-09 | 9,278 (10.1%) | 56,549 (61.8%) | 6,563 (7.2%) | 7,992 (8.7%) | 1,656 (1.8%) | 9,447 (10.3%) | 91,486 | $7.43B |

- **Leading category:** C2 (staking & restaking) leads the net in every month from 2024-09 to 2026-09, so the leader never changed (gross gives the same answer). Its net share went from 52% (2024-10) to a peak of 78% and 62% now; the drop in 2026-08 is LBTC moving to C4.
- **Second place:** C6 in every month. Third place: C1, C3. C4 appears only from 2026-08 (LBTC reclassified); C1 reached 10.1% of the net in 2026-08 and 2026-09, with the on-chain histories of Kraken, Yield Basis, Bitget, mHyperBTC, ether.fi and Maple merged.
- 2024-09 is incomplete for C2: DefiLlama lists Babylon only from 2024-10-22.

"Net flow" is the change in BTC units, so it also contains DefiLlama listing/delisting effects: Babylon listed 2024-10-22 (+~23k BTC in 2024-10), GTBTC listed 2025-11 (+~3k), Mezo Earn 2026-05, Vishwa 2025-09; DeSyn delisted 2025-11-28 (-~10k BTC in C6); Solv Basis re-scoped 2024-12 (-~7k BTC in C3). Read the category flows with these in mind.

Flows vs price, net basis, 2024-09 -> 2026-09 (USD change = net flow + price effect):

| Category | USD change | Net flow BTC | Net flow USD | Price effect USD |
|---|---:|---:|---:|---:|
| C1 | $753.2M | 9,278 | $705.4M | $47.8M |
| C2 | $3,861.2M | 45,032 | $4,008.5M | $-147.3M |
| C3 | $-29.7M | -2,319 | $-244.7M | $215.0M |
| C4 | $641.9M | 7,883 | $555.8M | $86.0M |
| C5 | $134.2M | 1,653 | $118.1M | $16.1M |
| C6 | $125.9M | -674 | $-776.5M | $902.4M |
| ALL | $5,486.6M | 60,852 | $4,366.6M | $1,120.0M |

Same from 2024-10 (first month with Babylon on DefiLlama):

| Category | USD change | Net flow BTC | Net flow USD | Price effect USD |
|---|---:|---:|---:|---:|
| C1 | $753.2M | 9,278 | $705.4M | $47.8M |
| C2 | $2,066.5M | 20,641 | $2,378.9M | $-312.4M |
| C3 | $-366.0M | -6,224 | $-505.6M | $139.5M |
| C4 | $641.2M | 7,884 | $555.9M | $85.2M |
| C5 | $134.2M | 1,653 | $118.1M | $16.1M |
| C6 | $-625.8M | -10,366 | $-1,424.0M | $798.2M |
| ALL | $2,603.2M | 22,866 | $1,828.8M | $774.4M |

## Sanity checks

- Category sums = total and product rows sum to category totals, every month: pass. Net <= gross every month: pass.
- 2026-09 history row vs current snapshot, like for like (products with a history): $8.18B vs $7.44B (gross) - equal.
- Current rows without history (not in the monthly files): Core BTC staking (Satoshi Plus) 2,210 BTC; Starboard Sygnum BTC Alpha Fund 750 BTC; Hilbert Xapo Byzantine BTC Credit Fund 1,232 BTC; Two Prime Axiom WBTC Vault (Pareto) 150 BTC. Total 13,548 BTC. Current gross = 2026-09 history gross + these rows.
- **On-chain C1 histories:** `inputs/c1_histories.csv` (columns month, product_id, tvl_btc) is merged by `10_build.py`; the rows enter history, category totals, shares and flows. DefiLlama proxies for comparison are in `c1_pending_proxy_history.csv`.

## DefiLlama methodology jumps and data breaks (review before charting)

- Solv Basis Trading: $735M at end-11-2024 -> $28M at end-12-2024 (one-day drop 2024-12-26, $689M -> $2M) and several flips in 2024-09 and 2025-05: the adapter was re-scoped; C3 in 2024-09..11 is inflated relative to later months.
- Royco v1: +$1.25B on 2025-02-03 (Boyco) and -> 0 on 2025-05-08. Gross only (see overlap.md).
- DeSyn Liquid Strategy: $1.07B -> 0 on 2025-11-28 (delisting/re-scope); DeSyn Safe -> 0 on 2025-08-08; DeSyn Basis -> 0 on 2024-11-09. C6 falls by ~10k BTC at end-11-2025 for this reason, not flows.
- Lombard LBTC: one-day dip 2026-07-15 ($591M -> $251M) and recovery 2026-07-17; month-ends unaffected. Methodology now caps Bitcoin-address BTC at the Lombard ledger balance and adds LFBTC.
- Babylon: -48% on 2026-03-12 then back by 2026-03-25 (data gap; month-ends unaffected); +36% on 2024-12-11 (cap-3) and +41% on 2025-04-26 (phase-2 registration) are real flows.
- Abrupt drops to ~0 that look like delistings or shutdowns: Kernel (2025-07-11), Pell (2025-12-30), CoinWind (2025-10-04), Flamincome (2025-07-17), Hemi staking (2025-12-02), Chakra (2025-09-03), Solv Others (2025-11-18).
- Zircuit staking flips between ~$1M and ~$55M many times (data glitch); month-end values for 2025-06..11 are unreliable (< 700 BTC either way).
- Full list: `jump_candidates.csv` (186 candidate step changes; many are real flows).

## Gaps and unverifiable items

- Coinbase CBYF AUM not disclosed (blank). Maple BTC Yield history is an on-chain attribution (medium-high confidence).
- Kraken Bitcoin Vault, Yield Basis, Bitget bgBTC Earn, Midas mHyperBTC, ether.fi Liquid BTC and Maple BTC Yield: current values and month-end histories from the on-chain deep dives (`inputs/c1_histories.csv`, merged).
- Core BTC staking: current value only (Core staking API, read 2026-09-21: 2,210.3 BTC, 1,814 stakers); no history endpoint found. Possible overlap with b14g and Maple.
- Stacks Dual Stacking: no public enrollment figure found; sBTC is excluded as a wrapper and Dual Stacking is not in the totals.
- Midas pools (mHyperBTC, mRe7BTC) and Tesseract pools: DefiLlama yields history starts mid-2026; earlier months are missing. Tesseract pools stopped updating 2026-09-16 (value carried to 09-20).
- Veda "other BTC vaults" (1,581 BTC today, up to ~10.8k BTC in 2025) are not identified by vault; placed in C6.
- Concrete: DefiLlama yields lists ~$38M of Berachain BTC vaults (APY 0) that are not in Concrete's protocol TVL; not counted.
- Babylon attribution is by finality-provider name; stake that LSTs delegate to generic operators without a product-linked key is not attributed (upper-bound case in overlap.md).
- Mechanisms not verified: Vishwa, ObeliskBTC, BitFi bfBTC, Solv RWA (constant $8.32M in DefiLlama), D2 Finance, DeSyn, CoinWind.
- Small protocols (< $0.25M BTC today and < $3M at every month-end) are not listed.

## Re-run

```
cd tools/marketmap
python3 scripts/01_candidates.py            # candidate slugs from raw/protocols.json
python3 scripts/02_fetch_protocols.py        # DefiLlama /protocol/{slug} (cached in raw/proto; delete to refresh)
python3 scripts/02b_fetch_parallel.py raw/extra_small_slugs.json   # small/dead protocols for the history screen
python3 scripts/03_fetch_btc_price.py        # Binance daily closes
python3 scripts/04_fetch_babylon.py          # Babylon stats, FPs, active delegations
python3 scripts/06_babylon_lst_fp_history.py # Babylon stake by product-branded FP, month-end (fallback)
python3 scripts/06c_babylon_lst_staker_history.py  # Babylon stake by product-linked staker keys (phase 1 + 2)
python3 scripts/07_fetch_yield_pools.py      # Midas / Tesseract / eBTC pools + charts
python3 scripts/08_history_screen.py         # BTC part at every month-end for every fetched protocol
python3 scripts/10_build.py                  # all CSVs
python3 scripts/11_write_reports.py          # overlap.md, notes.md, jump_candidates.csv
```
Product list and classification live in `scripts/products.py`; the BTC symbol list in `scripts/lib.py`.
