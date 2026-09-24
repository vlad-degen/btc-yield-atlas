# BTC-yield market map: method, exclusions, gaps

Snapshot 2026-09-20; history 2024-09 to 2026-09 (month-end). Produced 2026-09-21 from APIs only (DefiLlama, Babylon, Core, Binance, mempool.space). Values marked ESTIMATE or flagged in `market_map_current.csv` are not measured on-chain.

## Update 2026-09-23: DefiLlama cross-check, lending flagged

The map was checked against DefiLlama's list of BTC yield pools (https://defillama.com/yields?apyComponents=base&token=family:btc, 425 pools, 155 of them lending markets) and changed by `tools/marketmap/scripts/12_crosscheck_update.py`, which runs on the files in this folder:

- **Added (C6 unless noted), when the pool holds more than $1M:** BTC-pair DEX pools on Uniswap v3 (529 BTC) and v4 (438), Fluid (252), Curve (166), Bancor v3 (66), Chainflip (65; was excluded with all DEX LPs), Orca (53), Ekubo (52), Hydration (30), Aerodrome (27) and BeraPaw (7); GMX v2's BTC-only GM pool (131); Across's WBTC pool (115); Multipli xWBTC (47, C3); Wildcat's uncollateralized loans to market makers (161, C5, lending). 2,139 BTC in all. Only the part not counted elsewhere is added: the LBTC, eBTC, uniBTC, pumpBTC or stBTC side of a pair, LP staked through Convex, Stake DAO, Beefy or Troves, and the Kraken vault's own 268 BTC WBTC/kBTC position are left out. Pool values are each pool's DefiLlama series: the 2026-09-20 point for the snapshot and the last-day point for month-ends; history exists only for pools above $1M today. Wildcat is snapshot only (total supplied on the 2026-09-23 page at that day's BTC price; DefiLlama's own series counts only undrawn BTC, so its old history rows were dropped).
- **Lending is flagged, not removed:** `lending_products.csv` lists the 15 products whose BTC is lent out (3,153 BTC): Xapo Byzantine credit fund (1,232), Zest v2 sBTC supply (677), Accountable (589), Wildcat (161), Two Prime Axiom (150), Yearn BTC vaults (123), Solv RWA (102), Native Credit Pool (45), and Harvest, Moonwell vaults, Radpie, Superform, DeltaPrime, Extra Finance and Vesper (74 together); plus Seamless vaults in the history. The site's lending switch takes them out of every total, share and month. Money markets stay C0 context as before.
- **Seen, not added:** pools of $1M or less (Makina Dialectic BTC and others); Pendle markets on mHyperBTC (already counted); Solv's base SolvBTC reserves ($523M at 0%, listed under Solv Basis Trading; a wrapper); Concrete's Berachain vaults ($38M at 0%, see Gaps); a Bluefin SVBTC/WBTC pool that opened on 2026-09-22.
- **Farming and pools split into kinds:** `c6_groups.csv` gives every C6 product (today's and the history's) a kind and the BTC tokens it holds: points farming (BTC parked for points, airdrops or a protocol's own token: L2 campaigns, pre-deposits, lock-and-vote; 4,334 BTC in 6 products today), strategy vaults (managed vaults that lend, loop or provide liquidity; 3,615 BTC in 22), liquidity pools (DEX, perp and bridge pools over $1M and the vaults that stake their LP; 2,554 BTC in 22) and lending (vaults that only lend, from `lending_products.csv`; 875 BTC in 9). The line between points farming and strategy vaults follows the product's form, not its source of yield: most strategy vaults also farmed points in 2024-25, and they account for most of the fall of C6 (32,513 BTC in 2025-04 to 3,615). Tokens come from DefiLlama's protocol token breakdowns and the pool pairs (2026-09-20 to 23). The site has a switch for each kind.
- **Result:** net 95,825 → 97,964 BTC ($7.95B), 112 products holding BTC, plus Maple BTC Yield at zero (94,811 BTC and 97 products without lending); gross 105,139 → 107,278 BTC ($8.71B). Aggregator vaults whose use of BTC we could not check (Belt, Autofarm, Yield Yak, Reaper, YO, Mellow Core, Volo, Ember, UltraYield, OmniYield) are not flagged as lending.

## Update 2026-09-23 (later): money markets and CDP collateral, as optional segments

The C0 context rows (money markets, CDP collateral, lending venues, curated BTC vaults) were rebuilt protocol by protocol with month-end history, so the site can add them to the map with two switches that are off by default. Data set and method: `tools/marketmap/money_markets/` (`mm_notes.md`); step `scripts/13_money_markets.py` writes `money_markets.csv` (snapshot, one row per protocol) and `money_markets_monthly.csv`.

- **Money markets (C7 on the site):** 173,891 BTC in DefiLlama TVL on 2026-09-20 (collateral plus unlent supply, BTC units; 68 protocols), of which 158,935 BTC is not counted anywhere on the map, plus 498 BTC in eight small lending venues: 159,433 BTC. Taken out: staking tokens counted at their issuer (6,989 BTC, 5,695 of it LBTC), positions of counted products measured on-chain (7,324 BTC: Kraken vault 5,833 on Morpho and Aave, Bitget 802, mHyperBTC 241, ether.fi 208, Upshift 88, IPOR vaults 61, Yearn 53, Concrete 29, lend-only vaults 10) and the lending products that are map rows themselves (Zest v2, Accountable, Wildcat, Native: 644 BTC). Strategy vaults whose venues were not traced (Veda's other vaults, Solv Strategies and others) may overlap by up to ~3,720 BTC more. About 37,900 BTC is the cbBTC behind Coinbase's BTC-backed loans on Morpho (Base). The BTC earns about 0.03% a year (TVL-weighted supply rate).
- **CDP collateral (C8):** 5,239 BTC in 27 CDPs, of which 4,242 BTC is plain wrappers not counted elsewhere (the rest is River's bfBTC and uniBTC, counted at the issuers).
- **Curated BTC lending vaults** are not added: their BTC sits inside Morpho and Euler (counted by the money-market segment) or in map rows; the C0 curator list also counts 139 BTC twice (Tulipa = 9Summits, Anthias = Block Analitica).
- **History:** money markets peaked at 173,891 BTC now (low 107,840 in 2024-10, after one JustLend holder withdrew ~80,000 Tron BTC); the April 2026 KelpDAO exploit cut Aave by ~24,000 BTC in a week. Overlaps measured only at the snapshot (mHyperBTC, Upshift, Concrete, Yearn, small vaults) are subtracted from the snapshot only, so earlier months are an upper bound.
- **Reconciliation with the old C0 row (169,406 BTC, DefiLlama yields pools):** same convention (supply minus borrow); the difference is coverage (Lista Lending, Morpho chains missing from yields, lenders without a BTC yields pool) and the CDP and venue projects the old row included; see `mm_notes.md`.

Known issues found on the way, not changed in the totals: the Yearn row counts about 47 BTC twice (DefiLlama adds the v2 WBTC yVault and the v3 vault it deposits into); mHyperBTC moved its collateral after the snapshot (220 cirBTC on Morpho on Arc on 09-23), which does not affect the 09-20 figures.

## Files

- `market_map_current.csv`: one row per product (overlapping products split into a gross-only part and a net part); C0 context and excluded wrappers listed at the bottom.
- `market_map_history_monthly.csv`: month x product (same splits), plus an `include_net` column.
- `category_history_monthly.csv`: month x category: gross/net USD and BTC, net share.
- `category_flows_monthly.csv`: month x category: change in net USD split into net flow (BTC change at average price) and price effect (price change on average BTC).
- `lending_products.csv`: the products whose BTC is lent out (the site's lending switch); written by step 12.
- `c6_groups.csv`: kind (points, vaults, pools, lending), BTC tokens and an optional table label for every C6 product (the site's farming-and-pools switches); kept by hand.
- `product_notes.csv`: one row per product in today's map: what it does, its yield where known, who runs it and a link (the site's product table); kept by hand, and `tools/site_data.py` stops if a product has no row.
- `outside_totals.csv`: products listed on the site but not counted (CeFi, funds, ETFs, unconfirmed or unmeasurable ones) and why; kept by hand.
- `money_markets.csv` and `money_markets_monthly.csv`: BTC in money markets, lending venues and CDPs that no product on the map counts, by protocol (the site's two optional segments); written by step 13.
- `c1_pending_proxy_history.csv`: DefiLlama proxies for the C1 products, for comparison with the merged on-chain histories.
- `jump_candidates.csv`: automatically detected step changes in DefiLlama series (persistent >35% one-day moves over $25M) for review.
- `overlap.md`: double-counting analysis, gross vs net.
- `scripts/`: re-runnable pipeline, see "Re-run" below.
- `raw/`: all API pulls.

## Conventions

- **Snapshot point:** DefiLlama daily point stamped 2026-09-20 00:00 UTC; USD from `tokensInUsd`, BTC = USD / $81,178 (Binance close 2026-09-20). Values supplied from on-chain work (Kraken 6,492.7 BTC; Yield Basis 1,326.2 BTC of depositor equity; Bitget 801.7 bgBTC; ether.fi Liquid BTC ~232 BTC; Maple 0) are BTC and are converted at $81,178. Their month-end histories are merged from inputs/c1_histories.csv (on-chain).
- **Month-end point:** DefiLlama point stamped 00:00 UTC on the 1st of the next month (= end of the last day), converted at the Binance close of the last day. The 2026-09 row is the 09-20 snapshot. Yields-pool series use the point stamped on the last day.
- **BTC part only:** sum of BTC-denominated symbols in the protocol-level (or chain-level) `tokensInUsd` breakdown (list in `scripts/lib.py`: BTC, WBTC, cbBTC, BTCB, BTC.b, kBTC, LBTC, tBTC, FBTC, SolvBTC and variants, xSolvBTC, uniBTC/brBTC, enzoBTC, stBTC, bgBTC, sBTC, UBTC, eBTC, LBTCv, pumpBTC, M-BTC/mBTC, YBTC, cirBTC, xBTC, zBTC, bfBTC, lfBTC-*, RBTC, avBTC, mHyperBTC, BTCOC, BTC-only Curve LPs, etc.). Mixed LP tokens (tricrypto, WBTC/WETH) count at an estimated BTC share (1/3 or 1/2); they are a few million USD in total. Protocols without a token breakdown that are BTC-only (Hermetica, Lorenzo stBTC, Chakra, alloBTC, pSTAKE, LISA) use total TVL (method `total`).
- **DefiLlama TVL convention:** idle balances; lent-out balances are excluded unless noted. For Accountable and Zest v2 (lending-type yield products, flagged as lending since 2026-09-23) the `-borrowed` keys are added, so the row is total supplied BTC.
- **Flows vs price:** for months t-1 -> t, net flow = (B_t - B_{t-1}) x (P_{t-1} + P_t)/2 and price effect = (P_t - P_{t-1}) x (B_{t-1} + B_t)/2; the two add up to the USD change exactly.

## Universe

1. DefiLlama `/protocols` (8,317 protocols): every protocol in Restaked BTC, Anchor BTC, Basis Trading, Leveraged Farming, Onchain Capital Allocator, Yield, Staking Pool, Restaking, CDP, Yield Aggregator, Governance Incentives, Risk Curators (plus Farm, Options, Options Vault, CeDeFi, Uncollateralized Lending, Liquid Restaking, Dual-Token Stablecoin and BTC-named Bridge/Liquid Staking entries) was pulled via `/protocol/{slug}` (1994 files). Lending-category protocols were pulled only where they are yield products (Maple, Zest, Accountable, Native Credit Pool, BTC lending venues); plain money markets are C0 context.
2. Kept: protocols whose BTC-token part is >= ~$0.25M today or reached >= $3M at any month-end since 2024-09 (history screen catches dead products such as Corn, Royco, DeSyn, Pell, Kernel).
3. Added from the catalog/dossiers: Kraken Bitcoin Vault, Bitget bgBTC Earn, ether.fi Liquid BTC, Maple BTC Yield (on-chain history), Core staking (Core API), Midas mHyperBTC/mRe7BTC/mBTC, Tesseract and BTCD carry vaults, ether.fi eBTC (DefiLlama yields pools), off-chain funds.
4. Classified into C1-C6 by the plan's taxonomy; any product with a dollar loan against BTC is C1. 111 C1-C6 rows on 2026-09-21 (98 in the net).
5. 2026-09-23: DefiLlama's BTC yields pool list checked pool by pool; missed pools above $1M added (DEX, perp and bridge pools included) and lending products flagged (see the update section above). 112 products hold BTC in the net (113 rows with Maple BTC Yield at zero), 97 without lending.

## Key classification decisions

- **Lombard LBTC** switches category: C2 (Babylon LST) through 2026-07, C4 (Bitwise covered call, live 13.08.2026) from 2026-08. Lombard staker keys still had ~10.1k BTC in Babylon at end-June 2026 (all of LBTC) and ~130 BTC at end-July.
- **Lombard Vaults (LBTCv/BTCe)**: C6 (DeFi money-market/points vault) through 2026-06; C5 from 2026-07 (BTCe credit leg since 23.07.2026: LBTC as slashable cover for a loan on Cap).
- **Yield Basis** is C1 (hybrid: user BTC plus borrowed crvUSD into a 2x LP), per the plan rule "dollar debt under BTC -> C1".
- **Avalon CeDeFi** (USDT debt against lfBTC) is C0, not C1: it is a pool for four institutional Safes, the USDT went to Binance deposit addresses, DefiLlama says it is 100% team-deposited and it has been static since 11-2024. It is not a product with outside depositors (top-5 check).
- **Hermetica hBTC** stays C1 although the strategy was wound down 18.06.2026 (46.9 BTC left).
- **River Omni-CDP** is C0, not a yield product: users post bfBTC/uniBTC/UBTC to mint satUSD. The BTC holder earns nothing from River (only the LST's own yield), so it is borrowing context; counting it would double count bfBTC and uniBTC.
- **Mezo Earn** (veBTC) is C6 per the plan. Mezo Borrow (MUSD CDP) is C0.
- **Lending is flagged (since 2026-09-23):** products whose BTC is lent out stay in their category and are listed in `lending_products.csv` (credit funds, uncollateralized loans, Zest's lending market, vaults that only lend), so the site can show the market with or without them. Money markets and curated lending vaults remain C0 context.
- **Zest v2** sBTC supply is C6 (incentive-driven) per the plan, flagged as lending. Zest's "STBTC" ($10.9M) is excluded: the yields API lists it as stSTXbtc (an STX token) while the protocol breakdown prices it as BTC.
- **Accountable** (cbBTC/wcBTC) is C5 (uncollateralized credit), flagged as lending. Its largest vault lends to Hyperithm, the manager behind Midas mHyperBTC.
- **Curator BTC vaults** (Gauntlet, Steakhouse, Re7, Sentora WBTC, Hyperithm cbBTC on Monad, etc.) are C0: BTC lending at ~0% (plan: "BTC-vaults Morpho under ~0%"). Sentora's and Veda's kBTC on Ink are the Kraken vault and are counted only in the Kraken row.
- **BitFi** bfBTC: both DefiLlama slugs (EVM chains; AILayer) are C3 (BitFi CeDeFi basis/staking; mechanism not verified). AILayer farm (84.6M on Bitcoin) is treated as the same BTC as bfBTC on AILayer and kept out of the net.
- **Vishwa** (865 BTC) and **ObeliskBTC** are placed in C2 with a flag: yield mechanism not disclosed.
- **Midas mHyperBTC** is C1 (its strategy wallet posts cbBTC on Morpho/Spark and borrows USDT/USDS; Midas transparency API) and is measured from the Midas oracle NAV (354.1 BTC, $28.7M at $81,178); its history (from 2025-11) is rebuilt on-chain (top5/mhyperbtc/tvl_monthly.csv) and merged through inputs/c1_histories.csv.
- **Two Prime Axiom** is on-chain (Pareto) but not tracked by DefiLlama; recorded from the dossier (150 WBTC) with offchain=1.
- **Xapo Byzantine** (ESTIMATE): $100M phase-1 allocation used = 1,231.9 BTC at $81,178. The 3,000 BTC "seed" (2024) is the upper bound. Reason: the $100M is the fund-level allocation tied to the current mandate; the 2024 seed has no later confirmation and the fund page (launch 15.09.2024, net yield 2.94%) publishes no AUM.
- **Starboard Sygnum BTC Alpha**: 750 BTC (disclosed "750+", a lower bound).
- **Coinbase CBYF**: size not disclosed; blank, not in totals. **Maple BTC Yield**: 0 today; its 2025 history (up to 1,758 BTC) is reconstructed on-chain from Core CLTV stakes and merged.

## Exclusions

- Bare wrappers and bridges: WBTC, cbBTC, BTCB, kBTC, FBTC, enzoBTC, base SolvBTC, tBTC, BTC.b, bgBTC, sBTC, UBTC (Unit), xBTC (OKX), cirBTC, Nexus BTC, YBTC (Bitlayer), Merlin's Seal (M-BTC bridge custody), Katana vault bridge, bridge entries for Core/Echo/Mezo/exSat/BOB.
- Yield-tokenization venues (Pendle, Spectra, RateX, Nemo): their BTC is the LSTs already counted.
- USD-denominated products backed partly by BTC (Ethena, Falcon), DEX, perp and bridge pools of $1M or less (larger ones are in C6 since 2026-09-23), StackingDAO (STX staking), BTCST (hashrate).
- **C0 context (not yield):** money-market BTC collateral $13.75B (169,406 BTC; DefiLlama yields pools 09-20: $13.86B less Zest v2 and Accountable). Separately listed and not additive with it: curator BTC lending vaults 1,589 BTC, CDP collateral 5,240 BTC (includes River 1,244 BTC), BTC lending venues 495 BTC.

## History results

| Month | C1 net BTC (share) | C2 net BTC (share) | C3 net BTC (share) | C4 net BTC (share) | C5 net BTC (share) | C6 net BTC (share) | Net BTC | Net USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-09 | 0 (0.0%) | 11,518 (35.8%) | 8,882 (27.6%) | 109 (0.3%) | 3 (0.0%) | 11,649 (36.2%) | 32,162 | $2.04B |
| 2024-10 | 0 (0.0%) | 35,908 (51.0%) | 12,786 (18.2%) | 108 (0.1%) | 3 (0.0%) | 21,616 (30.7%) | 70,422 | $4.95B |
| 2024-11 | 0 (0.0%) | 48,339 (49.7%) | 10,266 (10.6%) | 107 (0.1%) | 1 (0.0%) | 38,490 (39.6%) | 97,202 | $9.37B |
| 2024-12 | 0 (0.0%) | 78,786 (67.8%) | 2,666 (2.3%) | 106 (0.1%) | 21 (0.0%) | 34,662 (29.8%) | 116,241 | $10.88B |
| 2025-01 | 214 (0.2%) | 83,007 (69.2%) | 2,543 (2.1%) | 113 (0.1%) | 21 (0.0%) | 34,144 (28.4%) | 120,041 | $12.30B |
| 2025-02 | 764 (0.6%) | 80,713 (66.0%) | 2,631 (2.1%) | 113 (0.1%) | 20 (0.0%) | 38,014 (31.1%) | 122,255 | $10.31B |
| 2025-03 | 1,101 (0.9%) | 83,068 (64.3%) | 3,647 (2.8%) | 78 (0.1%) | 2 (0.0%) | 41,238 (31.9%) | 129,134 | $10.66B |
| 2025-04 | 2,208 (1.8%) | 74,179 (60.5%) | 4,126 (3.4%) | 76 (0.1%) | 2 (0.0%) | 42,113 (34.3%) | 122,705 | $11.56B |
| 2025-05 | 2,132 (1.8%) | 69,743 (58.6%) | 4,232 (3.5%) | 80 (0.1%) | 2 (0.0%) | 42,857 (36.0%) | 119,046 | $12.45B |
| 2025-06 | 1,533 (1.5%) | 62,098 (58.5%) | 4,301 (4.0%) | 83 (0.1%) | 2 (0.0%) | 38,079 (35.9%) | 106,097 | $11.37B |
| 2025-07 | 1,485 (1.4%) | 60,570 (58.6%) | 4,373 (4.2%) | 59 (0.1%) | 17 (0.0%) | 36,821 (35.6%) | 103,325 | $11.96B |
| 2025-08 | 1,938 (1.7%) | 74,178 (63.3%) | 6,229 (5.3%) | 58 (0.1%) | 0 (0.0%) | 34,749 (29.7%) | 117,151 | $12.68B |
| 2025-09 | 1,843 (1.6%) | 76,346 (66.2%) | 7,614 (6.6%) | 57 (0.1%) | 5 (0.0%) | 29,370 (25.5%) | 115,235 | $13.14B |
| 2025-10 | 3,109 (2.7%) | 76,324 (65.7%) | 7,206 (6.2%) | 67 (0.1%) | 1 (0.0%) | 29,448 (25.4%) | 116,155 | $12.73B |
| 2025-11 | 2,001 (2.1%) | 69,735 (72.6%) | 7,305 (7.6%) | 76 (0.1%) | 2 (0.0%) | 16,974 (17.7%) | 96,092 | $8.68B |
| 2025-12 | 2,914 (2.8%) | 77,857 (75.4%) | 7,556 (7.3%) | 98 (0.1%) | 34 (0.0%) | 14,762 (14.3%) | 103,220 | $9.05B |
| 2026-01 | 3,263 (3.3%) | 73,814 (75.5%) | 7,014 (7.2%) | 97 (0.1%) | 42 (0.0%) | 13,584 (13.9%) | 97,812 | $7.70B |
| 2026-02 | 3,339 (3.8%) | 63,509 (71.7%) | 7,565 (8.5%) | 108 (0.1%) | 114 (0.1%) | 13,959 (15.8%) | 88,594 | $5.93B |
| 2026-03 | 3,318 (3.6%) | 66,619 (73.0%) | 7,122 (7.8%) | 139 (0.1%) | 199 (0.2%) | 13,866 (15.2%) | 91,263 | $6.23B |
| 2026-04 | 2,408 (2.6%) | 66,627 (73.3%) | 7,267 (8.0%) | 115 (0.1%) | 167 (0.2%) | 14,266 (15.7%) | 90,850 | $6.94B |
| 2026-05 | 3,647 (4.0%) | 65,852 (72.5%) | 7,218 (7.9%) | 125 (0.1%) | 327 (0.4%) | 13,724 (15.1%) | 90,893 | $6.70B |
| 2026-06 | 6,588 (7.1%) | 65,665 (70.9%) | 7,098 (7.7%) | 115 (0.1%) | 262 (0.3%) | 12,846 (13.9%) | 92,573 | $5.43B |
| 2026-07 | 8,236 (8.9%) | 64,976 (70.2%) | 6,604 (7.1%) | 122 (0.1%) | 676 (0.7%) | 11,974 (12.9%) | 92,588 | $5.82B |
| 2026-08 | 9,001 (9.9%) | 54,525 (59.8%) | 6,736 (7.4%) | 8,159 (8.9%) | 1,296 (1.4%) | 11,404 (12.5%) | 91,121 | $7.16B |
| 2026-09 | 9,278 (9.9%) | 56,549 (60.5%) | 6,610 (7.1%) | 7,992 (8.6%) | 1,655 (1.8%) | 11,378 (12.2%) | 93,463 | $7.59B |

- **Leading category:** C2 (staking & restaking) leads the net in every month from 2024-10 to 2026-09. In 2024-09 C6 edges it out (11,649 vs 11,518 BTC), a month when DefiLlama did not yet list Babylon, so C2 is incomplete. C2's net share went from 51% (2024-10) to a peak of 75% and 61% now; the drop in 2026-08 is LBTC moving to C4. Without the lending products C2 leads every month. (Figures after the 2026-09-23 update.)
- **Second place:** C6 in every month that C2 leads. Third place: C1, C3. C4 appears only from 2026-08 (LBTC reclassified); C1 reached 9.9% of the net in 2026-08 and 2026-09 (10.0% and 10.1% without lending), with the on-chain histories of Kraken, Yield Basis, Bitget, mHyperBTC, ether.fi and Maple merged.
- 2024-09 is incomplete for C2: DefiLlama lists Babylon only from 2024-10-22.

"Net flow" is the change in BTC units, so it also contains DefiLlama listing/delisting effects: Babylon listed 2024-10-22 (+~23k BTC in 2024-10), GTBTC listed 2025-11 (+~3k), Mezo Earn 2026-05, Vishwa 2025-09; DeSyn delisted 2025-11-28 (-~10k BTC in C6); Solv Basis re-scoped 2024-12 (-~7k BTC in C3). Read the category flows with these in mind.

Flows vs price, net basis, 2024-09 -> 2026-09 (USD change = net flow + price effect):

| Category | USD change | Net flow BTC | Net flow USD | Price effect USD |
|---|---:|---:|---:|---:|
| C1 | $753.2M | 9,278 | $705.4M | $47.8M |
| C2 | $3,861.2M | 45,032 | $4,008.5M | $-147.3M |
| C3 | $-25.9M | -2,272 | $-240.3M | $214.5M |
| C4 | $641.9M | 7,883 | $555.8M | $86.0M |
| C5 | $134.2M | 1,652 | $117.7M | $16.5M |
| C6 | $185.9M | -271 | $-713.9M | $899.8M |
| ALL | $5,550.4M | 61,301 | $4,433.2M | $1,117.3M |

Same from 2024-10 (first month with Babylon on DefiLlama):

| Category | USD change | Net flow BTC | Net flow USD | Price effect USD |
|---|---:|---:|---:|---:|
| C1 | $753.2M | 9,278 | $705.4M | $47.8M |
| C2 | $2,066.5M | 20,641 | $2,378.9M | $-312.4M |
| C3 | $-362.2M | -6,176 | $-501.2M | $139.0M |
| C4 | $641.2M | 7,884 | $555.9M | $85.2M |
| C5 | $134.2M | 1,652 | $117.7M | $16.5M |
| C6 | $-595.8M | -10,238 | $-1,379.7M | $783.9M |
| ALL | $2,637.1M | 23,041 | $1,877.0M | $760.0M |

## Sanity checks

- Category sums = total and product rows sum to category totals, every month: pass. Net <= gross every month: pass.
- 2026-09 history row vs current snapshot, like for like (products with a history): equal (gross and net).
- Current rows without history (not in the monthly files): Core BTC staking (Satoshi Plus) 2,210 BTC; Starboard Sygnum BTC Alpha Fund 750 BTC; Hilbert Xapo Byzantine BTC Credit Fund 1,232 BTC; Wildcat (BTC) 161 BTC (23 Sep value); Two Prime Axiom WBTC Vault (Pareto) 150 BTC. Total 4,503 BTC. Current gross = 2026-09 history gross + these rows.
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
- Veda "other BTC vaults" (1,350 BTC today after taking out ether.fi Liquid BTC's 232 BTC, up to ~10.8k BTC in 2025) are not identified by vault; placed in C6.
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
# after copying the outputs into data/:
python3 scripts/12_crosscheck_update.py      # 2026-09-23 cross-check: pools over $1M in, lending flagged; recomputes the category files
```
Product list and classification live in `scripts/products.py`; the BTC symbol list in `scripts/lib.py`.

## Update 2026-09-24: LBTCv netted out of Veda, sizes re-checked, borrowers traced

- **Veda double count fixed.** DefiLlama's Veda adapter (`projects/veda/ethereum_constants.js`) values every BTC BoringVault in WBTC, so the "Veda (other BTC vaults)" row contained Lombard's LBTCv (`0x5401…D57c`, 863 shares, about 885 BTC on 2026-09-20), which the "Lombard Vaults (LBTCv / BTCe)" row already counts. The snapshot row is cut by 885 BTC (1,349 → 464 BTC: ether.fi's eBTC vault ~262, a PumpBTC vault ~150, small vaults); in the history the smaller of the Veda and Lombard Vaults rows is subtracted from Veda each month (249 to 1,525 BTC). Net map: 97,090 → 96,205 BTC ($7.81B), 103 products; farming and pools 10,503 → 9,618 BTC. Still inside the Veda row and not checked against their issuers: Lombard Loop BTC, Bedrock Uni BTC-Fi and Pump BTC-Fi.
- **Vaults that only lend, and Zest's sBTC market** (874 BTC, 9 products; `c6_groups.csv` kind `lending`) count as money markets on the site, not as farming and pools.
- **Products listed but not counted** (`outside_totals.csv`) re-checked: Ledn's BTC Growth Account (retired 1 July 2025), Botanix stBTC (network shut down June 2026) and Core lstBTC (site gone; Maple's product wound down) are zero; BounceBit's $289M is its total AUM with no BTC split; exchange programs publish reserves, not Earn balances; the covered-call ETFs are BTCC $17M, BTCI $1,377M, BITA $93M, BTCY C$158M. Two measurable BTC-paying products are new and not yet in the map: Stacks Bitcoin Staking (about 250 BTC bonded since 10 September) and Stacking DAO stBTC (153 sBTC; may overlap Zest's 133 STBTC).
- **The 27 BTC-collateral borrowers with over $20M of debt** in `data/top5/selection/scan_borrowers_all.csv` were traced through funding and outflows: all single-owner books (an unidentified institutional cluster with ~9,900 cbBTC against $364M USDC on Aave and Morpho; Galaxy Digital desks; Abraxas Capital's Heka funds; a Binance-funded whale cluster; Nexo's operational wallet with 1,031 cbBTC against $40M USDS on Spark). No pooled carry product is missing (`research/top5/en/00-selection.md`).
- **BTC lending pays about nothing:** DefiLlama's single-asset BTC pools with a base APY over 0.5% held $25M in all on 24 September (the largest: a Morpho market on Monad $7.8M at 2.2%, Benqi BTC.b $5.7M at 1.2%), so no lending segment with a yield is added. BTC-pair DEX pools outside DefiLlama's BTC family (WHYPE/UBTC on Hyperliquid, about $13M; BTC.b/WAVAX on Avalanche $3.6M) stay out: their BTC halves are near or below the $1M threshold.
- **eBTC's LBTC netted too (24 September, later).** ether.fi's eBTC vault (`0x657e…C642`, a Veda BoringVault inside the Veda row) holds LBTC: 247 BTC at the snapshot block and 715 to 2,997 BTC at month-ends from September 2024 to April 2025 (archive `balanceOf` reads on eth.drpc.org at month-end blocks estimated from the snapshot block at 12.05 s per block). That LBTC is already in the "Lombard LBTC - direct / other holders" row (C2 until July 2026, C4 since August), so the Veda row is cut by it month by month, a lower bound: LBTC the vault restaked or lent elsewhere is not measured. Pump BTC-Fi (150 pumpBTC in the same row) does not overlap the pumpBTC row, whose DefiLlama total is smaller than pumpBTC supply; Lombard Loop BTC, Bedrock Uni BTC-Fi, Hourglass and tacBTC are empty.
- **Three rows excluded and four cut (24 September, later).** Their own product notes said so: BitFi bfBTC on AILayer (1,017 BTC; 3,052 in September 2024) is, in BitFi's words, "solely a 1:1 wrapped Bitcoin with no yield mechanisms"; Proxy (261 BTC) is the supply of BTCpx, a wrapped BTC on Polygon with the project offline; Hope (20 BTC) is the reserve behind the HOPE token with no trade. All three are wrappers or non-products and move to `outside_totals.csv` (include_net 0 in the snapshot and the history). Ember (190 → 3 BTC) held the Syntetika/Hilbert vault already counted in the Syntetika row; Belt (46 → 23) was double counted by DefiLlama's own adapter; Convex (−65) and Badger (−61) held old renBTC/sBTC pool tokens with almost no BTC behind them. Net map: 95,958 → 94,324 BTC ($7.66B), 100 products; C3 7,360 → 6,322; C6 9,371 → 8,774.
- **Venue sweep beyond Ethereum (24 September).** Tydro (Ink), Aave v3 (Avalanche, Polygon), Frankencoin, crvUSD BTC markets, Takara (Sei), Vesu (Starknet) and Zest (Stacks) were checked for BTC-collateral dollar borrowers with outside depositors. One found and added as C1: Vesu's Noon WBTC vault (37.66 WBTC on 24 September, at the snapshot price; no history). Tydro's largest position (913 kBTC against $45M USDC) is a Kraken-linked book (kBTC from Kraken's Ink hot wallet, dollars swept back to Kraken), not a product. Not completed: Venus, Aave and Lista on BNB, JustLend on Tron, Morpho on Pharos and Citrea, Dolomite, NAVI and Suilend, Kamino's other markets, Jupiter Lend (`research/top5/en/00-selection.md`).
