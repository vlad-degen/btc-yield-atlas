# ETH yield outside the on-chain count, and the small categories

Snapshot T = 2 October 2026 (ETH about $2,668). Collected 7 October 2026. Beacon-chain entity figures are from 7 October; fund figures from 5 and 6 October; treasury figures from their latest filing before T. Raw pulls: `raw/eth/gap-2026-10-07/outside/`.

## 1. Listed but not counted: off-chain ETH yield

Full rows with sources: [gap_outside_totals.csv](../../../../data/eth/gap_outside_totals.csv). It follows the BTC `outside_totals.csv` columns, adds `size_eth`, `size_date` and `overlap_note`.

**About 14.4M ETH of staked ETH can be attributed to custodial or institutional holders outside on-chain receipts, a third of the 43.7M ETH staked.** The layers overlap, so the parts below cannot all be added:

| Layer | ETH | Counts toward the 14.4M? |
|---|---:|---|
| Exchange tags net of their LSTs: Kraken 1.73M, Coinbase 1.09M (1.53M less cbETH 0.45M), Upbit 0.64M, OKX 0.61M, Revolut/CoinSpot/Bitstamp 0.47M, Bitget 0.03M | 4.57M | Yes |
| Institutional provider tags: Figment 1.31M, Blockdaemon 1.04M, Kiln 0.83M, Everstake 0.79M, Bitcoin Suisse 0.41M, P2P.org 0.35M | 4.73M | Yes |
| BitMine native stake (untagged on beaconcha.in) | 5.07M | Yes |
| US staking ETFs: ETHE 587k, Grayscale mini 747k, ETHB 337k, TETH 7k | 1.68M | No: staked through Coinbase custody and Figment/Galaxy/Attestant, inside the tags |
| EU ETP: 21Shares AETH | about 73k | No: inside provider tags |
| Treasuries: SharpLink native 593k, Ether Machine 497k, Bit Digital native 74k, BTCS 70k | 1.23M | No: run by tagged providers (SharpLink via Figment) or route unknown |

Findings:

- **BitMine is the largest single off-chain staker**: 5,067,309 of 6,001,302 ETH staked (84%, 27 September 8-K/press release), 2.62% 7-day yield. That is about 11.6% of all stake, and it shows under no beaconcha.in entity.
- **Binance has no measurable custodial stake beyond wBETH.** wBETH backs about 3.73M ETH (3,366,093 wBETH x 1.10796), more than the 3.29M ETH tagged to Binance. The tags undercount Binance; the custodial excess cannot be measured.
- **Coinbase custodial stake is about 1.09M ETH**: 1,534,779 tagged minus 449,301 ETH behind cbETH. Coinbase's Q2 10-Q gives 18.9M ETH on the platform, with no staked figure. The tag likely misses consolidated validators.
- **Kraken (1.73M) is the largest custodial staker without any on-chain receipt.** Upbit (639k) and OKX (609k) follow. Bybit's staking is a conversion into mETH, stETH or cmETH, all on-chain.
- **US ETFs staking at T hold about 1.68M ETH staked**, out of about 2.10M ETH in those four funds. ETHA (3.66M ETH, 5 October), ETHW and ETHV do not stake. Fidelity filed to stake FETH on 12 August; there is no evidence it was live by T. Grayscale nets 2.05% (ETHE, 2.50% fee) and 2.49% (mini). ETHB's 30-day rewards rate is 1.37%, after 18% of rewards go to the sponsor and Coinbase.
- **Treasuries mostly stake natively**, except where they hold LSTs. SharpLink held 163,083 LsETH and 66,267 weETH at 30 June; Bit Digital holds 66,192 LsETH; ETHZilla restakes via ether.fi and Puffer. Those are on-chain and are excluded here.
- **Not disclosed**: Coinbase Asset Management has no ETH yield fund (only the BTC one). Laser Digital, Arbelos and the Galaxy-SharpLink on-chain fund (about $125M of commitments) publish no ETH AUM. CeFi lenders (Nexo, YouHodler) publish no ETH balances.
- **Gaps**: The European ETPs (CoinShares about $308M, Bitwise ET32 $234M, WisdomTree $152M) have only USD figures from August and earlier. Canadian and Hong Kong staking ETFs, Franklin EZET and Invesco QETH were not retrieved. Hildobby's Dune dashboard needs a login. Beaconcha.in uses the same hildobby tags.

## 2. Small ETH yield categories

Sizes are ETH-family token units at 2 October 2026 from DefiLlama protocol token series (pulled 7 October), unless the row says otherwise. Full rows: [gap_small_categories.csv](../../../../data/eth/gap_small_categories.csv); month-ends October 2024 to September 2026: [gap_small_categories_monthly.csv](../../../../data/eth/gap_small_categories_monthly.csv).

**Options, ETH credit, ETH basis and fixed yield together hold about 6,500 ETH at T, excluding Kelp Gain (10,322 rsETH, a layer on rsETH) and exchange margin.** More than half is residual capital in retired products (Ribbon, Opyn, Manta) or expired Pendle markets. Only Rysk (1,182) and Panoptic (255) grew in 2026. Most categories peaked between October 2024 and early 2025 and are down 80% to 99%.

| Category | Product | ETH at T | Peak since Oct 2024 | Note |
|---|---|---:|---:|---|
| Options | Rysk v12 covered calls | 1,182 | 3,031 (28 Aug 2026) | Only growing options product. Premium is paid in USDT/USDC, so it is dollar income on ETH collateral |
| Options | Ribbon Theta ETH (residual) | 522 | 2,123 | No option since 12 Dec 2025; already in our options row (712.655 ETH by our read) |
| Options | Ribbon Earn stETH | 372 | 436 | Legacy, no new rounds |
| Options | Opyn Gamma + Squeeth | 644 | 4,114 | Legacy collateral; Gamma partly old Ribbon positions |
| Options | Panoptic v2 | 255 | 327 | New in September 2026 |
| Options | Premia, Sofa, Tymio, Siren | 167 | 830 | |
| Options | Derive vaults (weETH basis, covered call, spreads) | 72 (+38 stale rsETH/rswETH) | n/a | Derive API, 6 Oct |
| Options | Hegic, Stryke, Cega, Thetanuts | 82 | 3,448 combined | Thetanuts from 1,208 to 3.5 |
| Basis / delta-neutral in ETH | Theo straddle vaults | 244 | 6,338 (21 Feb 2025) | |
| Basis / delta-neutral in ETH | Derive weETH Basis Trade | 42 | n/a | Inside the Derive row |
| Basis / delta-neutral in ETH | Manta CeDeFi ETH | 354 | 18,154 (Oct 2024) | Off-chain strategy |
| Credit | Kelp Gain (hgETH, agETH) | 10,322 rsETH | 62,399 (28 Feb 2025) | Holds rsETH: same ETH as Kelp's 411k rsETH-family, strategy layer only |
| Credit | Wildcat Wintermute WETH | 49 | 1,068 (10 May 2026) | 3.75% fixed, uncollateralised |
| Credit | Maple, Clearpool, TrueFi, 3Jane, Accountable | 10 | 1,923 (Maple, Apr 2025) | All live credit pools are dollar pools |
| Fixed yield | Pendle ETH (all markets incl. expired) | 7,669 | 246,249 (Oct 2024 month-end) | Only 4 active ETH markets, all on Ethereum: $6.12M liquidity (2,268 ETH), 588 ETH PT face |
| Fixed yield | Spectra v2 + MetaVault WETH | 182 | 26,393 | |
| Fixed yield | Term Finance, TermMax, Notional, Napier, IPOR | 151 | 10,033 (Term), 4,033 (TermMax) | |

Exchange collateral is listed for context and is not a yield product: Derive v2 holds 22,184 ETH-family tokens of trader margin (doubled in September 2026), Aevo 759.

Euler WETH vaults (K3 Monad Earn WETH $59.76M, about 22,000 ETH) are lending and already in the strategy-universe review.

Overlap: almost all of these products hold an LST or LRT (wstETH, weETH, rsETH, pufETH, ezETH). Their ETH is already counted by the staking and restaking issuers. They add a strategy layer, not new ETH.

## Sources

- Beacon-chain entities (hildobby tags): https://beaconcha.in/entities, entity pages for Coinbase, Binance, Kraken, Upbit, OKX, Figment, Kiln (captured 7 October, `browser_captures_2026-10-07.txt`)
- cbETH and wBETH supply and exchange rates: Ethereum and BSC RPC `eth_call` (`cbeth_*.json`, `wbeth_*.json`)
- Coinbase Q2 2026 10-Q (`coin_10q_2026q2.htm`)
- iShares ETHA and ETHB holdings CSVs, 5 October (`etha_latest_holdings.csv`, `ethb_latest_holdings.csv`)
- Grayscale ETHE and ETH fund pages, 6 October: https://etfs.grayscale.com/ethe, https://etfs.grayscale.com/eth
- 21Shares TETH and AETH pages; ethwetf.com; vaneck.com ETHV
- BitMine press release, 27 September 2026 (`bmnr_pr_2026-09-28.html`)
- SharpLink Q2 2026 10-Q (`sbet_10q_2026q2.htm`) and ETH dashboard (`sbet_dashboard.html`)
- Bit Digital July and August 2026 monthly metrics (`btbt_*.html`)
- Secondary trackers for Ether Machine, BTCS, GameSquare, FG Nexus and EU ETP sizes: https://www.strategicethreserve.xyz, The Block treasuries, trackinsight
- DefiLlama: https://api.llama.fi/protocols, https://api.llama.fi/protocol/{slug} (`llama_protocol/`), https://yields.llama.fi/pools (`pools.json`), Wildcat pool chart (`wildcat_wmtweth_chart.json`), ETH prices from coins.llama.fi
- Derive vault statistics: https://api.lyra.finance/public/get_vault_statistics (`derive_vault_statistics.json`)
- Pendle active markets by chain: https://api-v2.pendle.finance/core/v1/{chainId}/markets/active (`pendle/`)
- PT face supplies and the Ribbon residual: [MARKET-COVERAGE.md](../MARKET-COVERAGE.md)

The series are rebuilt with `python3 build_small_series.py`, run from the raw folder. ETH-family means a fixed list of ETH, WETH, LST and LRT symbols. LP tokens such as GMX GM `WETH-USDC` are excluded.
