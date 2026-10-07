# Audit 4: research depth, ETH study vs BTC benchmark

Repo: `/Users/vladdegen/BTC Yield`, branch `codex/eth-research`. Read-only audit, 2026-10-07. Snapshot T = 2026-10-02 (block 26,108,081).

Legend: **=** same depth as BTC, **~** partly there, **x** missing. Hours assume the repo's existing archive RPC, month-end blocks and tools/eth scripts get reused.

---

## 1. Market

| BTC component | ETH equivalent | Verdict | What is missing / action |
|---|---|---|---|
| Category history, 24 month-ends | `data/eth/netmap/category_history_monthly.csv` (ETH units, eth_usd column), 236-row map, 6,219-row netting ledger | = | – |
| Flows vs price (`category_flows_monthly.csv`) | None. ETH units already strip price, but no USD bridge and no split between deposits and share-price accrual inside staking | ~ | Build `category_flows_monthly.csv` with the BTC formula from the existing csv: 1 h. Optional split of staking growth into new stake vs APR accrual: issuer exchange-rate series (stEthPerToken, weETH getRate) at month-end blocks, 3 h. Low impact. |
| Products that emptied | "Emptied since 2024" under each category on the site (e.g. Reservoir 4,137 → 24 ETH); outflow leaders for restaking (EigenLayer 1.13M, ether.fi 543k, Renzo 281k) | = | – |
| DefiLlama cross-check and re-check | `netmap/crosscheck.json`: 603 pools, not-in-map list, `recheck` block | = | – |
| Listed but not counted | OUTSIDE-AND-SMALL §1 + `gap_outside_totals.csv` (14.4M ETH off-chain: exchanges, providers, BitMine, ETFs, treasuries) | = (stronger than BTC) | Fill EU/CA/HK ETP ETH counts (CoinShares, Bitwise ET32, WisdomTree, CI, 3iQ, Purpose, HK ETFs) from issuer factsheets: 2 h. Low. |
| Money markets as optional segment, own pipeline, overlap groups A–D | 56 lending rows, 788k idle plain WETH, month-end history, off by default. Overlap handled by rule (plain WETH only), not by subtracting counted products' measured supply positions | ~ | Measure WETH supplied by counted products (Liquid, Lido Earn/Mellow, YO, Morpho ETH vaults, Fluid Lite) and subtract, as BTC did (7,324 BTC); write the A–D style overlap table: 4 h. Medium-low. |
| CDP segment | 9 rows, 657k ETH, history | = | – |
| Coinbase-type retail loans (BTC: ~37,900 cbBTC behind Coinbase loans on Morpho Base) | Not measured. Base has 70 sampled Morpho positions, no attribution | x | Morpho API: Base cbETH/WETH → USDC markets, classify Coinbase Smart Wallet borrowers as in BTC scan: 2–3 h. Medium (a large ETH-backed dollar borrower class that is not a product but sizes "retail ETH carry"). |
| Consistency | `dossiers/staking-restaking.md` still says no verified stake total at T; BRIEFING says 43,805,557 ETH measured from consensus state | bug | Fix the stale dossier line (editorial, 10 min). |

## 2. Top-5 selection: borrower scan

BTC: 319 positions ≥ $2M across Morpho (14 chains), Aave v3 (Eth Core/Prime/EtherFi, Base, Arbitrum) + Spark top-400 holders, Compound v3 Ethereum fully enumerated, Euler v2, Fluid every Ethereum position, Kamino, Aave v4 every spoke; all 27 wallets > $20M traced to an owner.

ETH:
- `research_borrowers.json`: top **10** positions in each of **25** Morpho markets (Ethereum 148, Base 70, Arbitrum 10, Optimism 9). Explicitly "not complete borrowers".
- `funding_atlas_borrowers.json` / `funding_borrower_deep_chapter.json`: Aave Ethereum + Spark debt-token holder discovery, 350 venue-account rows. Top-10 unique borrowers identified only by contract type; `named_legal_entities_verified: 0`.
- BORROWER-IDENTITIES: 23 Ethereum addresses > $5M traced (good: rSHARE private vaults, Fasanara, NEMO, Seamless). **Its seed list is the Morpho sample, not the Aave/Spark ranking.**
- CREDIT-EXPANSION: Compound v3 (11 deployments), Euler (1,321 proxies), Fluid (232 vaults), Silo v2 read **at market level**; no account enumeration.

**Verdict: selection is not complete to BTC standard.** Concrete gaps:

| Gap | Why it matters | How | Hours |
|---|---|---|---|
| The ten largest Aave/Spark ETH-collateral dollar borrowers are untraced: `0xd848…f452` DSProxy $212.4M, `0x9992…f242` 1-of-1 Safe $205.9M, `0x741a…31f3` $126.1M, `0xed0c…4312` $125.3M, `0x28a5…a6b0` $112.2M, `0x3a0d…97d9` InstaDapp $79.4M (plus `0xb99a` Abraxas, `0x2835` Binance whale, `0xe40d` treasury, already named in the BTC re-check). Debt is "partly or wholly" ETH-backed, so the ETH share is unknown too. | These are 5–10× the #2 product's debt; the "no pooled product missed" claim rests only on the Morpho sample | Per address: Aave `getUserAccountData` + per-reserve collateral split at T; Etherscan funding labels, Safe owners, DSProxy owner; vault shares minted (Blockscout token transfers); reuse BTC re-check notes for b99a/2835/e40d | 6–8 |
| All Aave/Spark addresses > $20M ETH-backed dollar debt, not only top-10 | BTC traced every > $20M wallet | Extend holder pages of variableDebt USDC/USDT/USDS/PYUSD/RLUSD/GHO/USDe to rank 400; filter by collateral bitmap | 4 |
| Morpho complete, not top-10 × 25 markets | Misses mid-size product wallets (BTC found Kraken LoanManagers, Bitget this way) | Morpho GraphQL `marketPositions` for every market with ETH-family collateral and ≥ $100k borrow, all API chains (Eth, Base, Arb, OP, Unichain, Katana, Hyperliquid/HyperEVM, Monad, Plasma, Linea where listed) | 3 |
| Aave v3 on Base, Arbitrum, Optimism, Linea, Plasma; Aave v4 spokes | BTC scanned Aave v4 every spoke; Aave v4 ETH TVL is $233M and v4 is Babylon's route | Holder discovery as above per chain; v4: `Borrow` events per spoke since launch, as BTC did (3,549 pairs) | 4 |
| Compound v3 accounts (Eth USDC 346.8M, USDT 145.9M; Base, Arb, OP) | Only market totals today | Enumerate `SupplyCollateral` logs → `borrowBalanceOf` at T, BTC method | 2 |
| Fluid positions (ETH/USDC 32.6M, ETH/USDT 34.8M) | BTC enumerated every Fluid Ethereum position | Fluid resolver `positionsByUser`/NFT positions for vaults 11, 12, 14, 15, 19, 20 | 2 |
| Euler account allocation (79 vaults accept ETH) | Unallocated | Euler accounts lens / `Borrow` events on the dollar vaults with ETH collateral | 2 |
| Other chains: Monad (0.13B ETH-family pools; Rocksolid already lives there), HyperEVM (HyperLend, Hypurrfi, Felix), Linea, BNB (Venus/Lista ETH), Tron JustLend | BTC listed un-scanned venues explicitly | Screen top borrowers on each; at minimum list them as "not scanned" in a Selection doc | 3 (screen) |
| No single "00-selection" equivalent | PRODUCT-SELECTION.md is 14 lines; scan coverage is spread over 5 docs | Write one selection page: ranked list, excluded with reasons, scan coverage table, not-scanned list | 2 |

Total to close selection: about 25–30 h. **Highest impact gap in the study.**

## 3. Per product vs the Kraken template

Kraken template items: A scope, B legs, C positions, D governance, E yield monthly/weekly + carry P&L by leg + negative-carry periods, F LTV weekly + delever reaction lag + ladder + stress, G holders buckets/types/over time, H TVL growth, I growth drivers (78 events), J operator economics, K verdict.

| Item | Liquid ETH | YieldBasis WETH | Lido Earn ETH | Avant | Liquity ETH Carry |
|---|---|---|---|---|---|
| Realized return monthly | = 24 m PPS, 730-day vs stETH/weETH | ~ 5 m (from May 2026) | ~ 7 m reported book | ~ 14 m reported book | ~ 7 m |
| Carry P&L by leg (Kraken E.4) | ~ snapshot only (−$6.8M/yr dollar leg); no monthly leg P&L; ETH loop P&L not separated | ~ fees vs interest at T | ~ 5M USDT lot only | x | ~ spread at T |
| Rewards share of carry | ~ at T ($2.6M/yr Merkl, payer chain traced); no history although weekly campaigns since July are in Merkl API | x gauge/YB emissions excluded | = none at T | ~ small Merkl | ~ $15k/yr |
| Organic vs rewards decomposition | x (explicitly "not stripped") | x | x | x | x |
| Negative-carry periods | x (Aave USDC 12.6–14.1% since Jun 2026 noted, not dated as periods) | x | ~ April freeze | x | x |
| LTV/HF history | ~ monthly, dollar legs only; **ETH loop (HF 1.027, $1.09B WETH debt, 23% of Aave WETH debt) excluded** | = LEVAMM 49.8–50.2% | ~ monthly | ~ monthly | ~ monthly |
| Target LTV and reaction lag to breaches | x | n/a | x | x | x |
| Liquidity ladder | = | = | = | = | = |
| Stress test (price shocks) | ~ distance to liquidation only | ~ | ~ | ~ | ~ |
| Admin keys / timelock / roles | ~ 24h timelock, 147 role events mapped (`permissions_review_T.json`) | x | x (Mellow roles not mapped) | x | ~ fuses and role members |
| Fees history | = 12 dated changes, 19 claims (2,130.6 ETH) | x | x (config only) | x | x (config only) |
| Holders: count, buckets, concentration, growth vs APY | ~ top owners + Cash Hub 7,012 accounts; no buckets, no history | ~ 332 addresses, gauge look-through | ~ 2,500 count | ~ 83 senior holders, look-through | ~ top holder 36.9% (`0x1676` Safe) |
| TVL growth drivers / distribution channel | ~ supply vs price bridge, ETHFI points, Kyber | x | x | x | x |
| Events timeline | ~ 9 events (Kraken: 78) | ~ 4 | ~ 6 | ~ 3 | ~ 4 |
| Legal / issuer terms, loss allocation | x | x | ~ DAO first-loss reserve, loss absorbed | x (own-credit issuer) | x |
| Incidents | x (April 2026 rsETH/Aave WETH stress not analysed for Liquid's loop) | x | = Kelp freeze, 27-day pause | x | x |
| Counterparty chain | = (Sentora, Cap, Hastra, self-credit) | = | ~ earnUSD | ~ savUSD on Avalanche | ~ Ebisu |

### Per-product work list

**Liquid ETH (largest gap is the ETH loop, not the dollar leg).** 
1. Weekly HF/LTV and WETH borrow rate for the main Aave/Spark loop, Oct 2024–T, plus event list of every deleverage (Aave `Repay`/`Withdraw` logs on account `0xf0bb…416c`) with lag from rate/HF breach: 6 h. Sources: Aave Pool events, `getUserAccountData` at weekly blocks.
2. April 2026 rsETH/Aave WETH stress: Liquid's HF, WETH rate and flows 15 Apr–31 May: 3 h.
3. Monthly P&L by leg (staking on collateral, WETH interest, dollar interest, destination yield, Merkl/ETHFI rewards, fees) reconciled to PPS: 8 h. Uses existing `carry_attribution_*`, `etherfi_*` files.
4. Holder buckets and holder count monthly (Ethereum + Optimism Cash Hub), flows vs APY: 4 h. Blockscout token holders, Transfer logs replay.
5. Liquid Terms of Service / Veda loss allocation: 1 h (ether.fi docs, Veda docs).

**YieldBasis WETH.** Gauge emissions to the WETH pool by month (YB `GaugeController`, emissions per gauge) and share of LP return; admin/emergency roles (YB factory, `set_*` owners); holder buckets: 5 h. Reuse BTC `yield_protocol_monthly.csv` method.

**Lido Earn ETH.** Mellow/stRATEGY role map (curator, oracle, pause); fee schedule; the April loss: amount, who bore it, pause timeline as a case box; holders buckets and monthly count; what distribution (Lido UI) did to inflows: 6 h. Sources: research.lido.fi incident review, Mellow docs, vault Deposit/Withdraw logs.

**Avant.** Issuer terms of avETH/savETH and savUSD (who absorbs losses, senior/junior), Avalanche savUSD cooldown in practice, admin keys; history of savUSD own-credit share: 5 h. Sources: Avant docs, published portfolio PDFs, Avalanche contract reads.

**Liquity ETH Carry (IPOR Fusion).** Fee history, atomist/alpha roles, Ebisu redemption-order risk history (how often low-rate troves got redeemed), holder history: 4 h.

Per-product total about 45 h. Priority: Liquid 1–3 first (largest book; the loop decides the return).

## 4. Closed and wound-down cases

| BTC case | ETH equivalent | Status |
|---|---|---|
| Maple (mechanism, partner subsidy, cause, payout to 66 addresses) | Lido Earn April freeze | ~ facts present (113k rsETH collateral, 27-day pause, DAO loss absorption); no case box with loss size, depositor outcome, lessons |
| Hermetica, Acre (small, closed with loss) | TAU InfiniFi ETH Carry (peak $854k Jan 2026, dust debt at T), Reservoir ETH Yield (peak 4,137 ETH / $15.9M, now $63k) | ~ state at checkpoints and fees measured; **why they shrank and what depositors got** (share price path from peak to exit, outflow dates, InfiniFi/Reservoir srUSD events) not researched. 3 h each |
| — | Rocksolid closing 29 Sep → reopen 7 Oct | = (logs, upgrade, verdict) |
| — | Kelp rsETH bridge exploit Apr 2026 | ~ in staking dossier + LENDING-MARKETS (Aave WETH deficit 52,964 Eth / 29,835 Arb). Missing: who among ETH yield products took losses (Lido Earn, CIAN rsETH, Liquid, Fluid Lite, Kelp Gain) in one table. 4 h |
| — | Ribbon Theta / Earn residual | = enough (residual 522/372 ETH). Do not expand |
| — | Eigenpie, Renzo, Puffer, Swell, Mantle outflows | ~ numbers only. One paragraph "why restaking halved" (points ended, EIGEN/AVS rewards small) is enough: 2 h, ties to §6 |
| — | Origami deprecated vaults | listed; fine, do not expand |

## 5. Playbook-type material: keep as findings or drop

| BTC item | Belongs in ETH? | Notes / action |
|---|---|---|
| Incentive cost per $ of TVL | **Yes, as a finding** | Pieces exist: Merkl RLUSD/PYUSD 2.2–3.0% APR on Sentora vaults, $2.6M/yr = 1.4% of Liquid's ETH-backed debt; ETHFI Member Rewards 7.5M ETHFI Jun–Aug 2025 (9 pts/ETH/day for Liquid); YB emissions; Lido DAO first-loss; Liquity BOLD campaign. Build one table by payer: 4 h |
| Curator / platform landscape | **Yes, short** | Veda (Liquid), Mellow (Lido Earn), IPOR Fusion (Liquity carry, TAU, Reservoir), Upshift (NEMO, Sentora), Lagoon (Rocksolid), Makina, Concrete; curators Sentora, Nonce, Steakhouse, Gauntlet, Re7, Hyperithm. 3 h, mostly reuse BTC 7.11 |
| Regulation | No | Only ETF-staking status, already in OUTSIDE §1 |
| Partners / who to talk to | No | Playbook-only |
| CARRY-MATH "seven-input calculator, four Playbook tables (Scenarios, Who pays, Limits, Partner roles)" | No | The ETH site has no playbook; see cut list |

## 6. ETH-specific topics an expert reader expects

| Topic | Present | Gap / action | Hours |
|---|---|---|---|
| Native staking: total, entities | = 43.81M ETH from consensus state; 14.4M off-chain by entity | – | – |
| Staking yield composition (issuance vs priority fees vs MEV) and its 24-month path | x | Month-end CL rewards (beacon API or rated/ultrasound), EL tips + MEV relay data; show why stETH fell from 2.94% to 2.48% | 4 |
| LST/LRT fee take and validator/operator share | x | Table: Lido 10% (5/5), Rocket Pool node commission, ether.fi, cbETH 25%, wBETH 10%, mETH, StakeWise; gross vs net APR per issuer at T | 3 |
| Restaking rewards reality | x (only "TVL does not establish AVS revenue") | EigenLayer `RewardsCoordinator` submissions/claims by token and month; slashing events; compare weETH vs stETH (already shows weETH 5.29% < stETH 5.49% over 730 days, so restaking added nothing net, a strong headline not stated as such) | 6 |
| Ethena / basis as a dollar product | ~ dossier (51 lines); ETH basis 372 ETH | Enough. One line on ETH perp share of USDe backing and funding history is sufficient | 1 |
| Pendle PT | ~ dossier; 122 of 126 markets expired | Enough; add PT-weETH/PT-rsETH loop sizes only if cheap | 0–2 |
| Aave/Spark WETH borrow-rate regime driving loops | ~ T snapshot for 5 markets, Liquid's own monthly WETH rate, `loop_economics_T.json` | Monthly market series: WETH borrow APR, utilization, stETH APR, spread, E3 loop TVL (97k ETH now, 122k Oct 2024); mark April 2026 spike and e-mode changes. `getReserveData` at existing month-end blocks | 4 |

## 7. Ranked gaps (impact first)

1. Trace the top Aave/Spark ETH-backed dollar borrowers and complete the scan (Morpho full, Aave other chains + v4, Compound/Fluid/Euler accounts), then one selection page. High. 25–30 h.
2. Liquid ETH loop risk and P&L: weekly HF, delever lag, April 2026 stress, monthly P&L by leg reconciled to PPS. High. 17 h.
3. Organic vs rewards decomposition for all five (rewards history from Merkl API, YB gauge emissions, ETHFI points). High. 8 h beyond item 2.
4. Aave WETH borrow-rate regime and staking-yield composition (why loops paid, then stopped). Medium-high. 8 h.
5. Holders (buckets, monthly count, flows vs APY) for the five. Medium. 10 h.
6. Admin/role maps and fee histories for YB, Lido Earn, Avant, Liquity; issuer terms and loss allocation. Medium. 12 h.
7. Closed cases written as cases (Lido Earn freeze, Reservoir, TAU) + Kelp-loss table. Medium. 13 h.
8. Incentive-cost table + curator/platform table. Medium. 7 h.
9. Restaking rewards reality + LST fee table. Medium. 9 h.
10. Coinbase-style ETH-backed retail loans on Base; money-market overlap table; category flows csv. Low-medium. 8 h.

Total ≈ 115–125 h.

## 8. Researched but noise (cut or collapse)

- Micro-books given full reconstruction chapters: ZenSats (< 1 ETH, 953 crvUSD), Vesper ($69k debt; −439 DAI ledger), Royco ($91k), TAU dust, Reservoir $37k current. Keep one line each in a table.
- The 350k USDC ×2 and 1M PYUSD "financed lots" (results −86, −62, −0.40) and the 3.75-day 5M USDT lot (+1,400): anecdotes, not carry economics. Keep the 5M lot as a footnote at most.
- Section "Two additional dollar investment and funding ledgers" is copied into BRIEFING, CAPITAL-INCOME-EXIT, CARRY-MATH, CARRY-LIFECYCLES; "Native stake" into 4 docs; "Product history behind the snapshot" into 4 docs. Keep one copy each.
- CARRY-MATH calculator and "Four Playbook tables": no playbook on the ETH site.
- Compound Arbitrum archive repair, Silo legacy markets, Midas mark ages (12.95 ETH mHyperETH), Yearn 2020 yETH precedent, Origami deprecated vaults, JustLend Tron dossier: process notes or out of scope.
- Methodology hedging prose ("does not establish", "is not a…") dominates CARRY-MATH, PRODUCT-TERMS, CARRY-PRODUCTS (10–12 instances each); move limits to one method section, per the "no Captain Obvious" rule.
- ~150 `finalization_*`, `parity_*`, `*_verification`, `presentation_*`, `site_*_qa` data files: build plumbing; fine in repo, should not surface in reader docs.
- Supporting comparison of Fluid Lite / Treehouse / CIAN terms in PRODUCT-TERMS duplicates the dossiers.
