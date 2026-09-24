# BTC in money markets, CDPs, lending venues and curated vaults: data set for the map extension

Snapshot 2026-09-20 (DefiLlama point stamped 00:00 UTC; BTC $81,178), month-ends 2024-09 to 2026-08 (point stamped 00:00 UTC on the 1st of the next month). Built 2026-09-23 from public APIs only: DefiLlama `/protocols`, `/protocol/{slug}` (259 protocols), yields `/pools`, `/lendBorrow`, `/chart/{pool}` (215 BTC lending pools); Morpho API (blue-api.morpho.org); IPOR Fusion API; Blockscout (aToken holders, contract names); public RPC reads; and the repo's own on-chain deep dives (`data/top5/*`). Nothing in the repo was changed.

## Files

| File | What it holds |
|---|---|
| `mm_monthly.csv` | segment, protocol, slug, month, btc_total, btc_plain, btc_yieldbearing, btc_borrowed, usd, source. One row per protocol and month (126 protocols x 25 months). |
| `mm_monthly_by_chain.csv` | the same per chain. |
| `mm_overlap.csv` | product_already_counted, protocol, btc, method, confidence, then month, group (A/B/C/D, see below), segment, slug, chain, in_column (which mm_monthly column the BTC sits in), note. Snapshot rows for everything, month rows where a history exists. |
| `mm_tokens_snapshot.csv` | 2026-09-20 BTC per protocol x chain x token, class (plain / yb) and the map product a yield-bearing token is counted at. |
| `mm_protocols.csv` | the protocol list: slug, DefiLlama category, segment, why included, 09-20 values, peak month, 2024-09 value, the protocol's BTC in DefiLlama yields on 09-20, chains. |
| `mm_apy.csv` | supply APY (DefiLlama yields, read 2026-09-23) of every BTC lending / CDP pool over $5M, with utilisation and borrow rates. |
| `scripts/` | the pipeline (see "Re-run"); `raw/` the API pulls (about 450 MB). |

## Column definitions (mm_monthly.csv)

- **btc_total**: BTC-family tokens in the protocol's DefiLlama TVL, in token units, summed over chains. DefiLlama's lending convention: collateral plus supplied BTC that is not lent out (supply minus borrow). It is the same convention as the yields `tvlUsd` behind the page's 169,406 BTC (checked: Aave WBTC tvlUsd = totalSupplyUsd - totalBorrowUsd; Morpho collateral pools = collateral).
- **btc_plain / btc_yieldbearing**: the split of btc_total by token class (below). btc_plain + btc_yieldbearing = btc_total.
- **btc_borrowed**: BTC lent out, from the `{chain}-borrowed` keys. Supplied BTC = btc_total + btc_borrowed. Kept separate because lent BTC leaves the protocol and can reappear elsewhere (a DEX pool, another lender, an LST), so adding it risks double counting.
- **usd**: DefiLlama's own valuation (`tokensInUsd`) of the tokens in btc_total at the same point. At the snapshot usd / (btc_total x 81,178) = 1.0006 for money markets; small gaps come from yield-bearing tokens priced off BTC.
- **source**: `defillama-protocol (token units)` except two protocols built from yields pools (TownSquare Lending; Takara Lend from 2026-02), see "Exceptions".

## Method

1. **Universe.** Every DefiLlama protocol in the categories Lending, Uncollateralized Lending and CDP with TVL over $1M (186), plus every C0 slug in `tools/marketmap/scripts/products.py` (27 CDP, 8 lending venues, 23 curators), plus Accountable (TVL $0.5M because DefiLlama books its loans as borrowed) and TownSquare Lending (see below). The yields pool list was used as a cross-check, not as the universe: 157 BTC lending pools over $1M (the site's earlier check found ~155) map to 50 protocols, all of which are covered; the protocol screen finds more (Lista Lending, Aave v2, Suilend, Alpaca, AlphaFi ...).
2. **Per protocol:** `api.llama.fi/protocol/{slug}`, `chainTvls[chain].tokens` (units) and `tokensInUsd`. Keys `borrowed`, `staking`, `pool2`, `vesting`, `offers`, `treasury`, `doublecounted`, `liquidstaking`, `dcAndLsOverlap` and the `-staking/-pool2/-vesting/-offers/-treasury` suffixes are skipped (same list as `10_build.py`); `{chain}-borrowed` keys give btc_borrowed. Point picking follows `lib.py`: the 00:00 UTC point of the date (3 days back if missing; 1 day at the snapshot). Token-breakdown coverage was checked: for the 30 largest protocols the token breakdown equals DefiLlama TVL within 5% at every month-end. On-chain spot check (2026-09-23, same-day DefiLlama point): Aave v3 aEthWBTC totalSupply 34,488.6 vs DefiLlama idle + borrowed 34,467.5 (-0.06%); aEthcbBTC 18,248.1 vs 18,233.2; Spark spcbBTC 6,117.9 vs 6,227.2 (+1.8%, intraday timing).
3. **Segment and selection.** C0 slugs keep their products.py segment (cdp / venue / curator), whatever their size. Other Lending / Uncollateralized Lending protocols are `money_market`; they are kept if they held more than $1M of BTC (12.3 BTC, supplied basis) on 09-20 (56 protocols) or at least 100 BTC at any month-end since 2024-09 (12 more, kept so the history is not biased by survivorship, e.g. Avalon Finance, LayerBank, ZeroLend, Ionic). No CDP outside the products.py list reaches $1M today or 100 BTC at a month-end (largest: QiDAO 6.8, Arkadiko 2.7 BTC).
4. **Excluded:** Cap (DefiLlama "Lending"): its 3,273 BTC is LBTC / uniBTC / SolvBTC restaked through Symbiotic and EigenLayer and delegated to Cap (its methodology counts "total delegated assets on networks"); the map already counts that BTC in Symbiotic (C2) and Lombard Vaults (C5), and it is not lent. Symbiotic ("Collateral Markets", in yields as lending-like pools) is a C2 product of the map. Leveraged-farming lenders (Extra Finance, DeltaPrime, Yield Basis) are map products, not money markets.
5. **Curator exclusions** (as in the map's C0 row): Sentora's kBTC on Ink (6,484.6) is the Kraken Bitcoin Vault itself and Hyperithm's mHyperBTC (284.1) is the Midas token; both are C1 products, so they are left out of the curator rows.

## Token classification

- **BTC family = the map's list** (`lib.py` BTC_FULL, BTC_PARTIAL with its LP weights, `LFBTC-*`), plus **aliases** for the same tokens under other DefiLlama keys, because a rename otherwise shows up as a flow: `BTCT`->BTC (JustLend's Tron BTC is keyed BTCT until 2025-06 and BTC from 2025-07; without the alias JustLend is 0 until 2025-06), `TBTCV2`->tBTC (Aave, Compound, Spark, crvUSD... until the rename), `SOLVBTC.M` / `SOLVBTC.B`->SolvBTC, coingecko-keyed cbBTC / LBTC / xBTC / SolvBTC.BBN, `BRIDGED MBTC`->M-BTC. The aliases add 0 BTC at the snapshot; they matter only for history.
- **Not BTC:** `STBTC` on Stacks (it is stSTXbtc, an STX token; the map drops it from Zest v2 for the same reason).
- **Yield-bearing (btc_yieldbearing)** = tokens whose backing the map already counts at an issuer row: LBTC and BTCOC (Lombard LBTC), LBTCv (Lombard Vaults), uniBTC / brBTC (Bedrock), pumpBTC, SolvBTC.BBN / SolvBTC.CORE / xSolvBTC (SolvBTC LSTs), SolvBTC.TRADING / .ENA / .JUP (Solv Basis Trading, whose DefiLlama token list holds .ENA and .JUP), bfBTC (BitFi), GTBTC, mHyperBTC, mRe7BTC, aHyperBTC (share of Accountable's Hyperithm vault, counted in the Accountable row), eBTC, avBTC / savBTC, stBTC (Lorenzo; its issuer row is ~0 today, flagged), asBTC, yoBTC, wfragBTC, scBTC and the small vault tokens in the list. This is `ISSUER` in `10_build.py` extended with the issuer rows whose own DefiLlama token list contains the token.
- **Plain (btc_plain)** = everything else in the list: WBTC, cbBTC, BTCB, BTC.b, tBTC, kBTC, FBTC, xBTC, cirBTC, enzoBTC, UBTC, sBTC, bgBTC, base SolvBTC, M-BTC, MBTC, native BTC on Tron / Bitcoin-side venues, WBTC.e, vbWBTC, wcBTC, rBTC ... The map excludes these as bare wrappers, so their BTC is counted nowhere unless a map product holds the position (group B of the overlap).
- **Seen but outside the list (not in any total):** BTCVC (Morpho on Pharos 253, AlphaFi 55), SVBTC (Current, Sui, 195), liquidBTC (ether.fi Liquid BTC shares used as collateral in ether.fi's borrowing market, 89.5: already counted in the map's C1 row), aEthWBTC used as collateral (61; the WBTC is already in Aave), CDCBTC (Tectonic 26), Pendle PTs on LBTC / eBTC / SolvBTC.BBN (up to ~1,150 in early 2025, 0 today) and a few dust tokens. About 680 BTC at the snapshot.

## Exceptions (DefiLlama protocol data vs yields pools)

- **TownSquare Lending (Monad):** the protocol adapter shows ~0 BTC; its yields pool shows 951.7 enzoBTC ($77.3M on 09-20, pool since 2026-04-16). Total enzoBTC supply on Monad is 983.06 (RPC `totalSupply`, 2026-09-23), so the pool is plausible. Series built from the yields chart (last-day point / map BTC price). Medium confidence.
- **Takara Lend (Sei):** protocol and yields data match month by month until 2026-01 (UBTC 250, enzoBTC 270, M-BTC 170), then the protocol data drops to 0 while the yields pools keep reporting ~545 BTC with unchanged balances. Filled from yields from 2026-02 (source column says so). Medium-low confidence: the balances have not moved for months.
- **Dolomite (Berachain) stBTC:** a constant 247.2 stBTC in the protocol data until 2026-07, gone from 2026-08, still in yields. Not filled (yield-bearing token whose issuer row is ~0; no effect on the "not yet counted" figure).

## Snapshot 2026-09-20

| Segment | Protocols | BTC in TVL | plain | yield-bearing | BTC lent out | USD (DefiLlama) |
|---|---:|---:|---:|---:|---:|---:|
| money_market | 68 (56 over $1M today + 12 kept for history) | 173,890.7 | 166,901.8 | 6,988.9 | 4,904.1 | $14.13B |
| cdp (products.py C0 list) | 27 | 5,239.3 | 4,242.4 | 996.9 | 0 | $0.43B |
| venue (products.py C0 list) | 8 | 498.1 | 498.1 | 0 | 13.7 | $0.04B |
| curator (products.py C0 list, kBTC / mHyperBTC excluded) | 23 | 1,585.1 | 1,475.3 | 109.8 | 0 | $0.13B |

The cdp, venue and curator totals match the map's C0 rows (5,240 / 495 / 1,589 BTC); the small gaps are units vs USD / $81,178 (e.g. Echo's aBTC trades below BTC).

Largest money markets (BTC in TVL; yield-bearing; lent out): Aave v3 65,620 (LBTC 2,708 and eBTC 83 yield-bearing; WBTC 37,378, cbBTC 21,141, tBTC 1,741, BTC.b 1,181, BTCB 984; 1,327 lent), Morpho Blue 62,505 (cbBTC 48,653 of which 37,887 on Base = Coinbase's BTC-backed loans; kBTC 6,335; WBTC 5,823; bgBTC 802 on Morph; yield-bearing 319: mHyperBTC 127, aHyperBTC 98, LBTC 77, uniBTC 16), SparkLend 10,637 (LBTC 2,741 yield-bearing), Venus Core 7,998 (BTCB 4,625, base SolvBTC 2,568, xSolvBTC 792 yield-bearing; 1,342 lent), Compound v3 7,663, JustLend 6,650 (Tron BTC), Lista Lending 3,076 (BTCB), Aave v4 1,164, Tydro 1,150 (kBTC 1,074), Kamino 1,071, TownSquare 952 (enzoBTC), NAVI 843, Fluid 813, Zest v2 598 (+73 lent), Takara 545. By chain: Ethereum 99,450, Base 41,005, BNB 12,184, Tron 6,650, Arbitrum 3,445, Avalanche 1,482, Solana 1,443, Monad 1,244, Ink 1,150, Sui 1,136 (60 chains).

By token (money markets, in TVL): cbBTC 77,889, WBTC 54,757, BTCB 8,831, kBTC 7,409, Tron/native BTC 6,691, LBTC 5,695 (67% of all LBTC), base SolvBTC 2,697, tBTC 1,959, enzoBTC 1,656, BTC.b 1,327, bgBTC 824, SolvBTC.BBN/xSolvBTC 795.

## Overlap with products the map already counts (mm_overlap.csv)

Groups: **A** yield-bearing tokens in the venue (exact, every month); **B** plain-wrapper positions held by counted products (on-chain); **C** venues that are themselves map products; **D** curator vaults.

Money markets, 2026-09-20:

| Group | Product already counted | BTC in TVL | BTC lent out | How measured | Confidence |
|---|---|---:|---:|---|---|
| A | Lombard LBTC (Aave 2,708, Spark 2,741, Morpho 77, NAVI 34, ...) | 5,694.6 | 2.3 | DefiLlama token units | high |
| A | SolvBTC LSTs (xSolvBTC on Venus 792) | 795.7 | 0.8 | same | high |
| A | Accountable (aHyperBTC collateral on Euler 107 / Morpho 98, Monad) | 204.7 | | same | high |
| A | Midas mHyperBTC token as collateral (Morpho Ethereum 70, Monad 57) | 127.3 | | same | high |
| A | ether.fi eBTC (Aave 83, Fluid 27, ether.fi market 15) | 125.9 | | same | high |
| A | Avant savBTC 20.4, uniBTC 16.0, others 4.3 | 40.6 | 0.1 | same | high |
| B | Kraken Bitcoin Vault: Morpho Ethereum kBTC/RLUSD + kBTC/PYUSD (4 loan managers) 5,395.41; Morpho WBTC/USDT 90.01; Aave v3 WBTC 347.10 | 5,832.5 | | on-chain position() / aToken at ETH block 26018582 (09-20 12:00) | high |
| B | Bitget bgBTC Earn: Morpho on Morph, bgBTC/USDC | 801.6 | | DefiLlama Morph = on-chain 801.58 | high |
| B | Midas mHyperBTC: Morpho ETH cbBTC/USDT 126.0, Spark cbBTC 113.4, Aave 1.4; lent on Monad via Euler 69.4 and Morpho V2 Apex 35.1 | 240.8 | 104.5 | Midas transparency API + RPC | high / medium (Monad) |
| B | ether.fi Liquid BTC: Spark spWBTC 153.1 + spcbBTC 54.8 | 207.9 | | on-chain at ETH block 26018582 (positions_monthly.csv); Blockscout 09-23 shows spWBTC 153.1, spcbBTC 67.3 after a later deposit | high |
| B | Upshift: Sentora BTC WBTC on Morpho 46.7; Gamma BTC on Aave v4 41.0 | 87.7 | | on-chain (carry scan 09-21, Morpho API 09-23) | high / medium |
| B | IPOR Fusion vaults (Tesseract TESS, BTCD / TAU carry, Reservoir): Aave v3 34.3, Spark 12.0, Morpho 16.2 | 60.5 | 1.9 | IPOR API market balances, 09-20 23:29 UTC | high |
| B | Yearn: WBTC MetaMorpho (Yearn v3 vault is its depositor) 47.5; Katana yVault vbWBTC collateral 14.2 | 53.1 | 8.6 | Morpho API + ydaemon + RPC | medium |
| B | Concrete ctWBTC v2 on Aave v3 | 29.3 | | on-chain | high |
| B | Moonwell vaults (Morpho Base) 13.9; Harvest 14.1, Superform 11.6, Vesper 4.9 (assumed fully lent) | 10.3 | 34.3 | Morpho API; ASSUMED for the last three | medium / low |
| C | Zest v2 sBTC (C6), Accountable (C5), Wildcat (C5, snapshot row only), Native Credit Pool idle BTC (C5) | 643.5 | 815.9 | DefiLlama token units | high |
| | **Total** | **14,956.1** | **968.4** | | |

**Not yet counted (money markets):** 173,890.7 - 14,956.1 = **158,934.6 BTC in TVL** ($12.9B at $81,178); on the supplied basis (adding lent BTC) 178,794.8 - 15,924.5 = 162,870.3 BTC.

Other segments: CDP 5,239.3 of which 996.9 yield-bearing (River: bfBTC 655.0, uniBTC 341.4) → 4,242.4 not counted; venues 498.1 → 498.1 (no counted product found); curator vaults (group D) 1,585.1 of which about 646.7 sits inside the Morpho / Euler money-market totals (supply of Gauntlet's vaults 224.0 incl. Katana's Vault Bridge WBTC 183.7, Hyperithm's Monad vaults ~256, Yearn WBTC 47.5, Sentora's (= Upshift Sentora BTC) 47.2, Moonwell Frontier 13.9, small Euler / Morpho vaults) and about 895 is counted in map products (Accountable's Hyperithm vault 505.7; Lagoon Flagship cbBTC 125.1, listed under both Tulipa and 9Summits; Odyssey on Lagoon 8.6; UltraYield 54.7; Moonwell 13.9 listed under both Anthias and Block Analitica; TAU 1.1). Only ~119 BTC of curator BTC is in neither (Telos WBTC in Euler vaults DefiLlama's euler-v2 does not show 63.2, Yearn-curated WBTC not located 33.7, DAMM funds 11.3, Gami on Robinhood chain 7.4, MEV Capital Sui 1.9, rounding). **All four segments together: ~163,794 BTC not yet counted (in TVL), ~167,744 on the supplied basis.**

**Possible further overlap, not measured (upper bound ~3,720 BTC, probably much less):** strategy vaults whose venues were not traced: Veda other BTC vaults 1,349 (no BoringVault other than ether.fi Liquid BTC's appears among the top-100 holders of aEthWBTC / aEthcbBTC / aEthtBTC / spWBTC / spcbBTC / aBascbBTC / aArbWBTC or among Morpho's top-200 BTC-collateral depositors, which argues against a large overlap), Solv Strategies 864 (SolvBTC on BNB / Avalanche / Ethereum; Venus holds 2,568 base SolvBTC, depositors not traced), Lombard Vaults' cbBTC / BTC.b 263, Lagoon 220 (incl. the Flagship cbBTC above), Ember 190, Mellow Core 164, Volo 110, YO 109, Avant 102, t3tris 84, Yield Yak 63, Belt 46, UltraYield 44, Tranchess 44, YieldFi 16, Upshift rest 15, Autofarm 14, OmniYield 10, Reaper 7, Yearn Katana rest 6, Trevee 2, Echo 1. No overlap for Radpie (Radiant is below $1M of BTC and not in the set), DeltaPrime and Extra Finance (own pools, not in the set). So the money-market "not yet counted" lies between ~155,200 and 158,935 BTC.

Checks behind group B: Morpho API top-200 collateral positions of all 48 BTC-collateral markets with 5+ BTC (576 depositors with 3+ BTC named via Blockscout): the only product contracts found are Kraken's 5 loan managers, Upshift's 2 loan contracts, IPOR PlasmaVaults (TESS, wBTC Dollar Carry, Debt Vault Loop), an Aera MultiDepositorVault (5.5 cbBTC, not a map product) and a StrategyMorphoV1 (5.4). The rest are EOAs (13.3k BTC), Coinbase Smart Wallets (8.0k, retail loans), Safes, EIP-7702 wallets and Instadapp / DeFi Saver / Summer.fi accounts. Aave / Spark top-100 aToken holders: Kraken, ether.fi Liquid BTC, TESS WBTC Lending Vault, Flying Tulip's Aave strategy (60.7 WBTC, not a map product), otherwise individual accounts and treasuries.

## History (month-ends, BTC in TVL)

| Month | Money markets: BTC in TVL | of which yield-bearing | BTC lent out (borrowed) | Overlap with the map (in TVL) | Not yet counted (in TVL) | USD, money markets | CDP | Venues | Curator vaults |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-09 | 147,011 | 2,546 | 10,089 | 2,549 | 144,462 | $9.35B | 10,547 | 4 | 854 |
| 2024-10 | 107,840 | 1,925 | 10,606 | 1,927 | 105,913 | $7.58B | 10,342 | 2,008 | 873 |
| 2024-11 | 112,880 | 3,806 | 11,065 | 3,807 | 109,073 | $10.87B | 13,626 | 2,427 | 1,280 |
| 2024-12 | 110,935 | 4,542 | 11,810 | 4,564 | 106,372 | $10.35B | 13,688 | 2,814 | 2,765 |
| 2025-01 | 109,139 | 4,868 | 12,487 | 4,959 | 104,180 | $11.16B | 13,910 | 2,819 | 4,144 |
| 2025-02 | 118,072 | 9,079 | 9,810 | 9,296 | 108,776 | $9.94B | 14,972 | 2,887 | 3,217 |
| 2025-03 | 125,878 | 11,388 | 10,545 | 11,510 | 114,368 | $10.37B | 13,611 | 2,892 | 4,125 |
| 2025-04 | 132,940 | 11,597 | 10,088 | 11,979 | 120,960 | $12.51B | 14,222 | 2,871 | 3,752 |
| 2025-05 | 136,830 | 9,929 | 9,532 | 10,303 | 126,527 | $14.29B | 14,847 | 2,996 | 3,840 |
| 2025-06 | 135,998 | 9,330 | 8,592 | 9,665 | 126,333 | $14.57B | 14,760 | 3,203 | 4,014 |
| 2025-07 | 150,930 | 8,775 | 9,235 | 9,043 | 141,887 | $17.47B | 14,906 | 2,983 | 3,610 |
| 2025-08 | 150,949 | 9,729 | 10,986 | 9,983 | 140,966 | $16.34B | 17,896 | 2,898 | 3,871 |
| 2025-09 | 161,475 | 9,122 | 9,065 | 9,330 | 152,144 | $18.44B | 17,532 | 2,926 | 2,970 |
| 2025-10 | 166,821 | 10,194 | 8,225 | 10,366 | 156,455 | $18.25B | 16,990 | 2,989 | 3,548 |
| 2025-11 | 157,748 | 8,533 | 6,842 | 8,642 | 149,105 | $14.14B | 12,448 | 3,165 | 2,361 |
| 2025-12 | 162,612 | 8,812 | 6,545 | 8,949 | 153,663 | $14.23B | 12,306 | 3,062 | 2,004 |
| 2026-01 | 162,476 | 9,836 | 6,814 | 10,023 | 152,453 | $12.83B | 10,919 | 3,002 | 2,060 |
| 2026-02 | 168,852 | 9,163 | 6,259 | 9,922 | 158,930 | $11.29B | 10,994 | 2,548 | 1,896 |
| 2026-03 | 164,350 | 8,870 | 5,965 | 9,851 | 154,499 | $11.19B | 10,423 | 2,467 | 2,822 |
| 2026-04 | 138,639 | 7,541 | 5,658 | 8,453 | 130,185 | $10.58B | 10,621 | 2,413 | 1,796 |
| 2026-05 | 150,992 | 7,360 | 5,156 | 9,320 | 141,671 | $11.12B | 10,728 | 2,422 | 1,585 |
| 2026-06 | 162,874 | 7,993 | 5,335 | 12,685 | 150,189 | $9.58B | 8,207 | 1,444 | 1,501 |
| 2026-07 | 167,418 | 7,888 | 5,188 | 13,781 | 153,636 | $10.53B | 4,879 | 546 | 1,653 |
| 2026-08 | 171,075 | 7,210 | 4,730 | 14,174 | 156,901 | $13.45B | 5,152 | 488 | 1,244 |
| 2026-09 | 173,891 | 6,989 | 4,904 | 14,956 | 158,935 | $14.13B | 5,239 | 498 | 1,585 |

- **Peak = now.** Money-market BTC is at its high of the series on 2026-09-20 (173,891). In USD the peak was 2025-09 ($18.4B at $114k BTC); now $14.1B.
- **Low = 2024-10 (107,840)** after one JustLend holder withdrew ~80,000 Tron BTC in 10,000-BTC steps between 2024-09-20 and 2024-10-28 (JustLend 87,950 → 7,406 BTC; 42,992 still in at the 2024-09 point). 2024-09 (147,011) is therefore inflated by one account.
- **Trend:** +61% from 2024-10 to now, almost all Morpho: 2,178 BTC (2024-09) → 62,505, of which Base 0 → 37,916 (Coinbase BTC-backed loans on Morpho, launched 16.01.2025) and Ethereum 2,147 → 22,739 (incl. the Kraken vault's 5,395 kBTC since 06-2026). Aave v3 45,764 → 81,317 (2026-03) → 65,620; SparkLend 2,359 → 10,637; Compound v3 9,746 → 7,663; Venus 9,948 → 7,998; JustLend 42,992 → 6,650; BTCfi-era lenders faded: Avalon Finance up to 11.4k (2024-12) → 0, LayerBank 10.2k (2024-09) → 25.
- **April 2026 drop (-25,711 BTC, -16%)**: the KelpDAO rsETH / LayerZero exploit of 18.04.2026 left Aave with bad debt; Aave v3 Ethereum lost ~12,100 WBTC and ~11,600 cbBTC between 04-18 and 04-24, part of it moved to SparkLend (2,189 → 7,851 BTC between 04-19 and 04-22). The total was back above its March level by 2026-07 thanks to Morpho and Spark; Aave v3 has not recovered (81,317 → 65,620).
- **Lent-out BTC fell** from 10-12.5k (2024-09 to 2025-04) to 4.9k: BTC borrowing demand has dried up (utilisation of the big pools 0.3-5.5%; Venus BTCB, 22.5%, is the exception).
- **Yield-bearing BTC in money markets** peaked at 11,597 (2025-04, LBTC / SolvBTC.BBN / pumpBTC looping era) and is 6,989 now.
- **Overlap history** is complete only for groups A and C and for Kraken (weekly on-chain reads, interpolated), Bitget, ether.fi, Moonwell / Seamless; IPOR vaults are estimated (map history x the 09-20 money-market share); mHyperBTC, Upshift, Concrete, Yearn, Harvest, Superform and Vesper are snapshot-only. In 2025 the unmeasured strategy vaults were much larger (the map's C6 vaults peaked at 32.5k BTC in 2025-04), so the historical "not yet counted" series is an upper bound.
- **CDP** 10.5k (2024-09) → peak 17.9k (2025-08) → 5.2k (Sky's WBTC vaults -1.6k on 2025-03-25 and -0.7k on 2025-09-30, Avalon USDa, River, Yala, Beraborrow). **Venues** 2.0-3.2k from 2024-10 to 2026-05 (Echo Lending on Aptos up to 2.7k) → 0.5k. **Curator vaults** up to 4.1k (2025-01) → 1.6k.

Step changes in the DefiLlama series worth knowing before charting (daily data, persistent moves >20% and >700 BTC): JustLend 2024-09/10 (real withdrawals); LayerBank 5,000 "BTC" on zkLink Nova in 2024-09 only (round number, priced as BTC, gone next month); Avalon Finance 1,724 → 99 on 2025-07-17 (likely re-scope / delisting); sumer.money 945 → 0 on 2025-06-15; Dolomite Berachain +4k in 2025-02 and out in 2025-05 (Boyco); Kamino and NAVI swings in 2025-10/11; Sky WBTC exits (real); the Kelp exit (real); Takara (protocol data 0 from 2026-02, yields-filled); Morpho on Morph tracked only from 2026-08-19 (Bitget's July collateral is not in the totals).

## Reconciliation with the page (169,406 BTC and the $B split)

The page's C0 row is DefiLlama **yields** pools on 09-20 (23:00 UTC points) for all projects in the categories Lending, CDP and Uncollateralized Lending whose pool symbol is a BTC-family token (62 projects), $13.86B, less Zest v2 and Accountable, / $81,178. Reproduced from `/pools` + `/chart/{pool}`: $13.863B (169,491 BTC after the two deductions; the 85 BTC gap is pools without a 09-20 point and the 09-23 pool list).

| BTC | Step |
|---:|---|
| 169,406.0 | page C0 row (yields pools, Lending+CDP+Uncollateralized, 09-20, less Zest v2 and Accountable) |
| 85.0 | reconstruction difference (pool set read 09-23; Jupiter Lend pools without a 09-20 point) |
| 1,282.2 | + Zest v2 and Accountable (yields) |
| -1,747.9 | - CDP projects in the yields set (my cdp segment) |
| -154.8 | - lending-venue projects in the yields set (my venue segment) |
| -67.6 | - yields projects below the $1M protocol threshold (not selected) |
| 168,802.8 | = yields BTC of the money-market projects |
| -582.8 | - yields symbols outside the map BTC list (vault shares, SVBTC, CDCBTC, stSTXbtc ...) |
| 3,074.1 | Lista Lending: 3,075 BTCB in protocol TVL, one small yields pool |
| 1,512.7 | Morpho Blue: protocol covers more chains / idle loan supply (Morph bgBTC 802, Citrea 100, Tempo 146, Arc 204, ...) |
| -584.2 | Accountable: yields shows supplied BTC, protocol TVL excludes the lent BTC (587 BTC in btc_borrowed) |
| 263.9 | Jupiter Lend: yields pools have no 09-20 point |
| -223.4 | Dolomite: stBTC on Berachain (247) dropped from the protocol data in 2026-08, still in yields |
| 139.6 | Compound v3: more markets/chains in protocol TVL |
| 118.1 | Euler v2: yields lists a few EVK vaults only (aHyperBTC collateral vault 107 etc. missing) |
| -67.9 | Zest v2: yields shows supply (idle + lent); protocol TVL is idle only |
| -0.0 | Takara Lend: protocol data 0 from 2026-02, filled from its yields pools (so no difference) |
| 330.3 | other coverage / timing differences (00:00 vs 23:00 UTC points), 40 projects |
| 1,107.5 | + money-market protocols with BTC but no BTC yields pool (Aave v2 420, Suilend 163, Alpaca 120, AlphaFi 104, ...) |
| 173,890.7 | = this data set: money_market btc_total (DefiLlama protocol TVL, token units) |

Key points: (1) the conventions are the same (yields `tvlUsd` of a lending pool = supply - borrow; Morpho / Compound v3 collateral pools = collateral), so neither figure includes the 4,904 BTC lent out, except that yields shows Accountable and Zest v2 at full supply; (2) the page's figure includes CDP (1,748 BTC) and venue (155 BTC) projects that also appear as separate C0 rows, so the C0 rows are indeed not additive; (3) the yields view misses Lista Lending (3,076 BTCB), Morpho's Morph / Citrea / Arc / Sei / World Chain markets (1,225) and most of Euler, Jupiter Lend and a dozen smaller lenders, and it contains vault-share tokens (vbgtWBTC, hyperCBBTCa, gtWBTCc ...) whose BTC the protocol data counts as plain supply; (4) both figures include 6,989 BTC of LST / yield-bearing collateral and 7,324 BTC of positions of products the map already counts, which is why they cannot be added to the map as they stand.

Per-protocol split ($B on 09-20):

| Protocol | Page | Yields 09-20 (reproduced) | Protocol TVL, DefiLlama USD | Protocol BTC x $81,178 | BTC in TVL | BTC lent out |
|---|---:|---:|---:|---:|---:|---:|
| Aave v3 | 5.32 | 5.324 | 5.335 | 5.327 | 65,620.1 | 1,327.0 |
| Morpho Blue | 4.98 | 4.978 | 5.077 | 5.074 | 62,505.4 | 109.0 |
| SparkLend | 0.86 | 0.862 | 0.864 | 0.863 | 10,637.1 | 169.4 |
| Venus | 0.64 | 0.643 | 0.648 | 0.649 | 7,998.4 | 1,341.9 |
| Compound v3 | 0.61 | 0.611 | 0.622 | 0.622 | 7,663.4 | 2.9 |
| JustLend | 0.54 | 0.543 | 0.539 | 0.540 | 6,650.3 | 18.8 |
| Tydro (Ink) | 0.09 | 0.093 | 0.093 | 0.093 | 1,150.2 | 3.8 |
| Aave v4 | 0.09 | 0.092 | 0.095 | 0.094 | 1,164.1 | 3.1 |
| Kamino | 0.09 | 0.087 | 0.087 | 0.087 | 1,070.7 | 26.1 |
| Others | 0.62 | 0.63 (incl. Zest v2 0.057 and Accountable 0.047; CDP and venue projects 0.155) | see mm_protocols.csv | | | |

## What the BTC earns (mm_apy.csv, DefiLlama yields read 2026-09-23; APY in % a year)

- TVL-weighted over all BTC lending pools ($14.4B): **0.030%** (0.026% base + 0.004% rewards). Pools where BTC can be lent ($8.6B): 0.049%, or **0.022%** without the uncollateralized credit vaults. Collateral pools of Morpho and Compound v3 ($5.8B) pay 0 by design. At ~0.03% the 174k BTC earn about 50 BTC a year in total.
- Largest pools: Aave v3 Ethereum WBTC 0.0034% (2.1% of the WBTC lent, borrow rate 0.32%), cbBTC 0.0011%; SparkLend cbBTC 0.0010%, WBTC 0.00001%; JustLend BTC 0.0054%; Aave Base cbBTC 0.0088%, Arbitrum WBTC 0.021%, Avalanche BTC.b 0.0075%, BNB BTCB 0.0074%; Tydro kBTC 0.0084%; Kamino cbBTC 0.0036%; Venus BTCB 0.17% (22.5% lent); Fluid WBTC 0.10% base (0.13% with rewards); Zest v2 sBTC 0.12% (30-day mean 0.025%); LBTC / xSolvBTC / SolvBTC collateral 0.
- Exceptions: Accountable's uncollateralized cbBTC vault 4.70% + 0.34% rewards; Wildcat's market-maker loans ~4-4.5% (page, 09-23); TownSquare enzoBTC 0.0033%.
- What the collateral pays for: the dollar loans against it cost 3.5-5.1% on Morpho (Base cbBTC/USDC 5.06%, Ethereum cbBTC/USDC 5.00%, kBTC/RLUSD 3.53%, kBTC/PYUSD 3.63%) and 3.6% on crvUSD.

## Findings for the map itself (outside this task, flagged for review)

1. **Yearn row double counts ~47.5 BTC.** DefiLlama's yearn-finance Ethereum WBTC (95.07) adds the v2 WBTC yVault (0xA696..6C7E, 47.46 WBTC) and the v3 vault it routes into (single strategy StrategyRouterV3-WBTC, 47.45 WBTC debt); the v3 vault's WBTC sits in the Yearn WBTC MetaMorpho (47.51). The map's Yearn row (122.77) is therefore ~47 BTC too high.
2. **The C0 curator row (1,589) lists 139 BTC twice** (Tulipa = 9Summits: one Lagoon Flagship cbBTC vault, 125.1; Anthias = Block Analitica: Moonwell Frontier cbBTC, 13.85), and ~900 BTC of it is also counted in map rows (Accountable 505.7, Lagoon, UltraYield, Upshift, Moonwell).
3. **mHyperBTC is moving venues:** at the 09-20 snapshot its BTC collateral was 126.0 cbBTC on Morpho Ethereum and 113.4 cbBTC on Spark (repo deep dive); on 09-23 Midas' transparency API lists Morpho on Arc (equity $7.5M; the strategy wallet 0x933a..2833 posts 220.0 cirBTC there, Morpho API) and no Spark line. The overlap uses the 09-20 positions; re-read the mHyperBTC row and its overlap before the next update. (A different wallet, 0x1778..7770, now holds 126.1 cbBTC in the same Ethereum market and 241 cirBTC on Arc; it is not in Midas' wallet list.)
4. **ether.fi Liquid BTC shares are recycled:** 89.5 liquidBTC (of ~224 shares) are posted as collateral in ether.fi's own borrowing market on Optimism.
5. DefiLlama tracks Morpho on Morph only from 2026-08-19, so Bitget's July collateral is missing from every DefiLlama-based total.

## Caveats

- **Source:** DefiLlama protocol adapters and prices; their errors pass through. Token breakdowns cover TVL at every month-end for the 30 largest protocols; step changes are listed above and not adjusted (except Takara).
- **Units:** token units, except LP tokens (the map's BTC share of USD value), depegged wrappers valued at market (Kava's Huobi HBTC 650 units ≈ 50 BTC; Solend / Larix "BTC" on Solana; renBTC) and unpriced tokens skipped (not in DefiLlama TVL either). Aliases fix renames. BTC-family symbols outside the map's list (~680 BTC now) are not included.
- **Timing:** protocol points are 00:00 UTC; yields points 23:00 UTC; on-chain overlap reads 09-20 12:00 UTC (Kraken, Bitget, ether.fi, mHyperBTC), 09-20 23:29 (IPOR) and 09-21..23 (Upshift, Concrete, Yearn, Moonwell, Monad vaults): a few BTC of timing noise per item.
- **Yield-bearing = counted:** assumes the issuer row counts the token's backing. True for LBTC, SolvBTC LSTs, bfBTC, uniBTC, mHyperBTC, aHyperBTC (Accountable), eBTC (gross; the net assumes it is inside the Veda row). Lorenzo stBTC's issuer row is ~0 today, so stBTC in venues (1.3 BTC now; up to ~800 in 2025 on NAVI and Dolomite) is not really counted anywhere.
- **Borrowed BTC** is reported, not netted: where the borrowed BTC went is not traced; it may be counted in other rows (DEX pools, LSTs) or leave DeFi.
- **Classification choices for the map:** 38k of the "not yet counted" BTC are Coinbase retail loans on Base and 6.6k are JustLend's Tron BTC; money-market collateral earns ~0%, so including this BTC in a yield map is a scope decision (plan 0.1 kept it as C0 context).
- **Curator attribution** of venues uses the DefiLlama curator registry, the Morpho vault list and Euler's chain totals; Hyperithm's split (inside ~256, Accountable 505.7) is approximate.
- **Not verified on-chain:** TownSquare's 952 enzoBTC (supply check only), Takara's 545 BTC after 2026-02, Harvest / Superform / Vesper venues, the unmeasured strategy vaults above.

## Protocol list

| Segment | Protocol | Slug | DefiLlama category | BTC in TVL 09-20 | of which yield-bearing | BTC borrowed 09-20 | Peak supplied (month) | Chains 09-20 |
|---|---|---|---|---:|---:|---:|---:|---|
| money_market | Aave V3 | `aave-v3` | Lending | 65,620.1 | 2,790.9 | 1,327.0 | 83,396 (2025-12) | Arbitrum Avalanche Base Binance Ethereum Linea Mantle MegaETH Monad... |
| money_market | Morpho Blue | `morpho-blue` | Lending | 62,505.4 | 318.6 | 109.0 | 62,614 (2026-09) | Arbitrum Arc Base Citrea Ethereum Hyperliquid L1 Katana Monad Morph... |
| money_market | SparkLend | `sparklend` | Lending | 10,637.1 | 2,740.8 | 169.4 | 12,041 (2025-10) | Ethereum |
| money_market | Venus Core Pool | `venus-core-pool` | Lending | 7,998.4 | 792.5 | 1,341.9 | 11,217 (2025-10) | Arbitrum Base Binance Ethereum zkSync Era |
| money_market | Compound V3 | `compound-v3` | Lending | 7,663.4 | 0.0 | 2.9 | 9,868 (2025-04) | Arbitrum Base Ethereum Linea Mantle Optimism Polygon |
| money_market | JustLend V1 | `justlend-v1` | Lending | 6,650.3 | 0.0 | 18.8 | 42,999 (2024-09) | Tron |
| money_market | Lista Lending | `lista-lending` | Lending | 3,075.6 | 0.0 | 0.0 | 5,429 (2025-10) | Binance |
| money_market | Aave V4 | `aave-v4` | Lending | 1,164.1 | 0.1 | 3.0 | 1,167 (2026-09) | Arc Avalanche Ethereum |
| money_market | Tydro | `tydro` | Lending | 1,150.2 | 0.0 | 3.8 | 2,250 (2026-01) | Ink |
| money_market | Kamino Lend | `kamino-lend` | Lending | 1,070.8 | 1.4 | 26.1 | 3,736 (2025-09) | Solana |
| money_market | Fluid Lending | `fluid-lending` | Lending | 813.0 | 36.7 | 175.6 | 2,633 (2025-07) | Arbitrum Base Ethereum Polygon |
| money_market | NAVI Lending | `navi-lending` | Lending | 843.4 | 34.9 | 130.0 | 2,782 (2025-09) | Sui |
| money_market | TownSquare Lending | `townsquare-lending` | Lending | 951.7 | 0.0 | 0.0 | 953 (2026-07) | Monad |
| money_market | Zest V2 | `zest-v2` | Lending | 597.9 | 0.0 | 73.4 | 831 (2026-05) | Stacks |
| money_market | Accountable | `accountable` | Uncollateralized Lending | 0.2 | 0.0 | 587.3 | 587 (2026-09) | Citrea Ethereum Monad |
| money_market | Takara Lend | `takara-lend` | Lending | 544.6 | 0.0 | 0.0 | 721 (2025-09) | Sei |
| money_market | Aave V2 | `aave-v2` | Lending | 420.1 | 0.0 | 3.0 | 6,014 (2024-09) | Avalanche Ethereum Polygon |
| money_market | Compound V2 | `compound-v2` | Lending | 290.0 | 0.0 | 0.8 | 4,509 (2024-09) | Ethereum |
| money_market | Jupiter Lend | `jupiter-lend` | Lending | 274.1 | 36.8 | 7.6 | 1,589 (2026-01) | Solana |
| money_market | Benqi Lending | `benqi-lending` | Lending | 85.8 | 0.0 | 170.8 | 1,932 (2024-12) | Avalanche |
| money_market | Euler V2 | `euler-v2` | Lending | 141.8 | 108.4 | 83.2 | 1,532 (2025-03) | Arbitrum Avalanche BOB Base Binance Ethereum Hyperliquid L1 Monad U... |
| money_market | AlphaFi Lending | `alphafi-lending` | Lending | 104.2 | 1.8 | 98.3 | 252 (2026-06) | Sui |
| money_market | Suilend | `suilend` | Lending | 162.8 | 40.1 | 24.3 | 1,337 (2025-08) | Sui |
| money_market | HyperLend Pooled | `hyperlend-pooled` | Lending | 137.6 | 0.0 | 28.7 | 568 (2025-09) | Hyperliquid L1 |
| money_market | Wildcat Protocol | `wildcat-protocol` | Uncollateralized Lending | 0.5 | 0.0 | 155.3 | 213 (2026-06) | Ethereum |
| money_market | Moonwell Lending | `moonwell-lending` | Lending | 63.2 | 43.1 | 60.7 | 882 (2024-11) | Base Ethereum |
| money_market | Alpaca Finance 2.0 | `alpaca-finance-2.0` | Lending | 120.2 | 0.0 | 0.0 | 243 (2024-09) | Binance |
| money_market | Native Credit Pool | `native-credit-pool` | Lending | 44.9 | 0.0 | 53.4 | 224 (2026-05) | Arbitrum Base Ethereum Morph |
| money_market | Dolomite | `dolomite` | Lending | 57.7 | 0.2 | 40.5 | 4,987 (2025-02) | Arbitrum Berachain Ethereum Mantle |
| money_market | Tectonic | `tectonic` | Lending | 93.0 | 0.0 | 0.0 | 306 (2024-11) | Cronos |
| money_market | TermMax | `termmax` | Lending | 0.0 | 0.0 | 80.9 | 224 (2026-03) | BSquared |
| money_market | Vires Finance | `vires-finance` | Lending | 72.9 | 0.0 | 0.1 | 75 (2025-07) | Waves |
| money_market | MetalX Lending | `metalx-lending` | Lending | 56.8 | 0.0 | 14.6 | 74 (2026-08) | Proton |
| money_market | Curve LlamaLend | `curve-llamalend` | Lending | 66.9 | 0.0 | 0.0 | 146 (2025-05) | Arbitrum Ethereum |
| money_market | Hydration Lending | `hydration-lending` | Lending | 35.4 | 0.0 | 1.1 | 54 (2025-12) | HydraDX |
| money_market | Fraxlend | `fraxlend` | Lending | 35.3 | 0.0 | 0.0 | 125 (2024-09) | Arbitrum Ethereum |
| money_market | Morpho Midnight | `morpho-midnight` | Lending | 34.7 | 0.0 | 0.0 | 35 (2026-09) | Base |
| money_market | Project 0 | `project-0` | Lending | 29.9 | 0.0 | 2.9 | 307 (2026-05) | Solana |
| money_market | Curvance | `curvance` | Lending | 0.1 | 0.0 | 32.5 | 33 (2026-06) | Monad |
| money_market | Save | `save` | Lending | 28.8 | 0.0 | 3.8 | 72 (2025-05) | Solana |
| money_market | LayerBank | `layerbank` | Lending | 24.9 | 0.0 | 6.0 | 10,223 (2024-09) | Hemi Move RSK |
| money_market | marginfi Lending | `marginfi-lending` | Lending | 27.1 | 0.0 | 2.9 | 53 (2025-10) | Solana |
| money_market | Current | `current` | Lending | 11.7 | 0.0 | 13.8 | 25 (2026-09) | Sui |
| money_market | Silo V2 | `silo-v2` | Lending | 21.3 | 20.6 | 0.2 | 596 (2025-10) | Avalanche Sonic |
| money_market | Flying Tulip Lend | `flying-tulip-lend` | Lending | 0.1 | 0.0 | 19.8 | 20 (2026-08) | Ethereum Sonic |
| money_market | Avalon Finance | `avalon-finance` | Lending | 5.9 | 3.7 | 10.7 | 14,434 (2024-12) | Arbitrum BOB Base Binance Bitlayer Ethereum Goat Klaytn Merlin Soni... |
| money_market | Folks Finance xChain | `folks-finance-xchain` | Lending | 16.1 | 0.0 | 0.2 | 96 (2025-12) | Arbitrum Avalanche Base Binance Ethereum Monad Polygon Sei |
| money_market | Loopscale | `loopscale` | Lending | 12.8 | 3.0 | 3.5 | 55 (2025-09) | Solana |
| money_market | Gearbox | `gearbox` | Lending | 13.0 | 0.0 | 2.5 | 113 (2025-03) | Ethereum Hemi |
| money_market | BEND | `bend` | Lending | 15.4 | 0.0 | 0.0 | 15 (2026-09) | Berachain |
| money_market | EtherFi Borrowing Market | `etherfi-borrowing-market` | Lending | 14.7 | 14.7 | 0.0 | 15 (2026-09) | Optimism |
| money_market | Scallop Lend | `scallop-lend` | Lending | 13.7 | 0.0 | 0.6 | 35 (2025-12) | Sui |
| money_market | Rhea Lend | `rhea-lend` | Lending | 8.6 | 0.0 | 5.2 | 35 (2024-10) | Near |
| money_market | Kava Lend | `kava-lend` | Lending | 12.4 | 0.0 | 0.2 | 51 (2025-02) | Kava |
| money_market | Hatom Lending | `hatom-lending` | Lending | 10.2 | 0.0 | 2.4 | 38 (2024-09) | Elrond |
| money_market | Capyfi | `capyfi` | Lending | 10.7 | 0.0 | 1.8 | 446 (2026-02) | Base Ethereum LaChain Network |
| money_market | Kinza Finance | `kinza-finance` | Lending | 10.5 | 0.0 | 0.3 | 276 (2024-09) | Binance Ethereum |
| money_market | Echelon Market | `echelon-market` | Lending | 6.6 | 0.0 | 0.0 | 696 (2025-04) | Aptos Move |
| money_market | Venus Flux | `venus-flux` | Lending | 5.3 | 0.0 | 0.1 | 521 (2026-02) | Binance |
| money_market | YeiLend | `yeilend` | Lending | 2.1 | 0.5 | 2.3 | 2,681 (2025-06) | Sei |
| money_market | ZeroLend Lending | `zerolend-lending` | Lending | 1.7 | 0.0 | 0.0 | 2,697 (2024-12) | X Layer zkSync Era |
| money_market | HypurrFi Pooled | `hypurrfi-pooled` | Lending | 0.8 | 0.0 | 0.7 | 149 (2025-08) | Hyperliquid L1 |
| money_market | TermFinance Lend | `termfinance-lend` | Lending | 1.0 | 0.0 | 0.0 | 274 (2025-01) | Ethereum |
| money_market | INIT Capital | `init-capital` | Lending | 0.8 | 0.0 | 0.0 | 113 (2025-02) | Mantle |
| money_market | Mendi Finance | `mendi-finance` | Lending | 0.1 | 0.0 | 0.3 | 108 (2024-09) | Linea |
| money_market | Sumer.money | `sumer.money` | Lending | 0.1 | 0.0 | 0.2 | 1,181 (2025-02) | Arbitrum Berachain CORE Goat |
| money_market | Venus Isolated Pools | `venus-isolated-pools` | Lending | 0.1 | 0.0 | 0.0 | 173 (2024-09) | Binance |
| money_market | Ionic Protocol | `ionic-protocol` | Lending | 0.0 | 0.0 | 0.0 | 2,417 (2024-09) |  |
| cdp | f(x) Protocol | `fx-protocol` | Dual-Token Stablecoin | 1,287.6 | 0.0 | 0.0 | 1,288 (2026-09) | Ethereum |
| cdp | River Omni-CDP (satUSD) | `river-omni-cdp` | CeDeFi | 1,245.4 | 996.8 | 0.0 | 5,223 (2025-09) | BOB BSquared Base Binance Bitlayer Ethereum Hemi |
| cdp | crvUSD / LlamaLend | `crvusd` | CDP | 929.9 | 0.0 | 0.0 | 1,633 (2025-04) | Ethereum |
| cdp | Frankencoin | `frankencoin` | CDP | 360.3 | 0.0 | 0.0 | 360 (2026-09) | Ethereum |
| cdp | Sky (Maker) | `sky-lending` | CDP | 339.3 | 0.0 | 0.0 | 6,256 (2024-09) | Ethereum |
| cdp | Money on Chain | `moneyonchain` | Dual-Token Stablecoin | 271.8 | 0.0 | 0.0 | 1,237 (2025-01) | RSK |
| cdp | Sovryn Zero | `sovryn-zero` | CDP | 249.6 | 0.0 | 0.0 | 540 (2024-09) | RSK |
| cdp | BIMA CDP | `bima-cdp` | CDP | 125.8 | 0.0 | 0.0 | 126 (2026-09) | Bitcoin Ethereum Hemi |
| cdp | BTCFi CDP | `btcfi-cdp` | CDP | 92.3 | 0.0 | 0.0 | 245 (2025-02) | Base Bifrost Network Bitcoin |
| cdp | Kava Mint | `kava-mint` | CDP | 62.4 | 0.0 | 0.0 | 206 (2025-02) | Kava |
| cdp | Bucket | `bucket-cdp` | CDP | 57.6 | 0.0 | 0.0 | 136 (2025-08) | Sui |
| cdp | Mezo Borrow | `mezo-borrow` | CDP | 36.4 | 0.0 | 0.0 | 314 (2026-01) | Mezo |
| cdp | Hylo | `hylo-protocol` | Dual-Token Stablecoin | 34.4 | 0.0 | 0.0 | 34 (2026-09) | Solana |
| cdp | Yala | `yala` | CDP | 29.0 | 0.0 | 0.0 | 2,171 (2025-10) | Bitcoin |
| cdp | Threshold thUSD | `threshold-thusd` | CDP | 26.8 | 0.0 | 0.0 | 117 (2024-09) | Ethereum |
| cdp | Lista CDP | `lista-cdp` | CDP | 25.8 | 0.0 | 0.0 | 344 (2024-10) | Binance |
| cdp | Felix CDP | `felix-cdp` | CDP | 23.1 | 0.0 | 0.0 | 232 (2025-08) | Hyperliquid L1 |
| cdp | Abracadabra | `abracadabra-spell` | CDP | 21.1 | 0.0 | 0.0 | 75 (2024-11) | Arbitrum Ethereum |
| cdp | Inverse FiRM | `inverse-finance-firm` | CDP | 9.1 | 0.0 | 0.0 | 73 (2024-10) | Ethereum |
| cdp | Angle | `angle` | CDP | 5.8 | 0.0 | 0.0 | 54 (2024-09) | Arbitrum Ethereum Polygon |
| cdp | Bucket v2 | `bucket-protocol-v2` | CDP | 5.7 | 0.0 | 0.0 | 69 (2025-10) | Sui |
| cdp | Beraborrow | `beraborrow` | CDP | 0.2 | 0.1 | 0.0 | 2,056 (2025-04) | Berachain |
| cdp | bitSmiley | `bitsmiley` | CDP | 0.1 | 0.0 | 0.0 | 313 (2024-09) | Bitlayer |
| cdp | Nerite | `nerite` | CDP | 0.0 | 0.0 | 0.0 | 30 (2025-09) | Arbitrum |
| cdp | Bitzap yUSD | `bitzap-yusd` | CDP | 0.0 | 0.0 | 0.0 | 638 (2025-05) |  |
| cdp | Avalon USDa CDP | `avalon-usda` | CDP | 0.0 | 0.0 | 0.0 | 5,712 (2025-03) |  |
| cdp | BitU | `bitu-protocol` | CDP | 0.0 | 0.0 | 0.0 | 251 (2024-10) |  |
| venue | Templar | `templar-protocol` | Lending | 201.2 | 0.0 | 0.0 | 230 (2026-06) | Bitcoin Ethereum |
| venue | Vesu | `vesu` | Lending | 82.8 | 0.0 | 6.6 | 164 (2025-12) | Starknet |
| venue | Echo Lending | `echo-lending` | Lending | 72.8 | 0.0 | 0.0 | 2,667 (2025-06) | Aptos |
| venue | Chainflip Lending | `chainflip-lending` | Lending | 53.1 | 0.0 | 6.3 | 65 (2026-08) | Chainflip |
| venue | Granite | `granite` | Lending | 38.8 | 0.0 | 0.0 | 192 (2026-02) | Stacks |
| venue | Zest v1 | `zest-v1` | Lending | 17.9 | 0.0 | 0.0 | 711 (2026-01) | Stacks |
| venue | Liquidium | `liquidium` | Lending | 15.6 | 0.0 | 0.8 | 16 (2026-09) | ICP |
| venue | Surge Credit | `surge-credit` | Lending | 15.9 | 0.0 | 0.0 | 16 (2026-09) | Bitcoin |
| curator | Hyperithm (curated cbBTC vaults) | `hyperithm` | Risk Curators | 761.9 | 106.9 | 0.0 | 762 (2026-09) | Ethereum Monad |
| curator | Gauntlet | `gauntlet` | Risk Curators | 224.0 | 1.1 | 0.0 | 2,358 (2025-01) | Base Ethereum |
| curator | Tulipa Capital | `tulipa-capital` | Risk Curators | 125.8 | 0.2 | 0.0 | 1,445 (2025-06) | Avalanche BOB Ethereum |
| curator | 9Summits | `9summits` | Risk Curators | 125.1 | 0.0 | 0.0 | 127 (2025-06) | Ethereum |
| curator | Yearn curating | `yearn-curating` | Risk Curators | 81.2 | 0.0 | 0.0 | 182 (2025-06) | Ethereum |
| curator | Telos Consilium | `telos-consilium` | Risk Curators | 71.1 | 0.0 | 0.0 | 81 (2025-10) | Ethereum |
| curator | UltraYield curator | `ultrayield-curator` | Risk Curators | 54.6 | 0.0 | 0.0 | 208 (2025-10) | Ethereum Hyperliquid L1 |
| curator | Sentora (WBTC vault) | `sentora-curator` | Risk Curators | 47.2 | 0.0 | 0.0 | 452 (2026-06) | Ethereum |
| curator | Gami Labs | `gami-labs` | Risk Curators | 17.3 | 0.0 | 0.0 | 114 (2026-05) | Ethereum Robinhood Chain |
| curator | Anthias | `anthias-labs` | Risk Curators | 13.8 | 0.0 | 0.0 | 33 (2026-07) | Base |
| curator | Block Analitica | `block-analitica` | Risk Curators | 13.8 | 0.0 | 0.0 | 304 (2024-12) | Base |
| curator | DAMM | `damm-capital` | Risk Curators | 11.3 | 0.0 | 0.0 | 11 (2026-09) | Ethereum |
| curator | Odyssey | `odyssey-digital-am` | Risk Curators | 8.6 | 0.0 | 0.0 | 9 (2026-09) | Ethereum |
| curator | K3 Capital | `k3-capital` | Risk Curators | 8.1 | 0.1 | 0.0 | 304 (2025-10) | Arbitrum Ethereum |
| curator | Clearstar | `clearstar` | Risk Curators | 8.0 | 0.0 | 0.0 | 38 (2026-04) | Base Hyperliquid L1 |
| curator | AlphaGrowth | `alphagrowth` | Risk Curators | 5.0 | 1.4 | 0.0 | 8 (2026-06) | Base Unichain |
| curator | Steakhouse | `steakhouse-financial` | Risk Curators | 3.1 | 0.0 | 0.0 | 66 (2025-03) | Ethereum |
| curator | Re7 Labs | `re7-labs` | Risk Curators | 1.9 | 0.0 | 0.0 | 114 (2025-04) | BOB Binance Ethereum World Chain |
| curator | MEV Capital | `mev-capital` | Risk Curators | 1.9 | 0.1 | 0.0 | 800 (2025-10) | Ethereum Sui |
| curator | Tau Labs | `tau-labs` | Risk Curators | 1.1 | 0.0 | 0.0 | 81 (2026-02) | Ethereum |
| curator | Apostro | `apostro` | Risk Curators | 0.0 | 0.0 | 0.0 | 57 (2025-01) |  |
| curator | B.Protocol | `b.protocol-curator` | Risk Curators | 0.0 | 0.0 | 0.0 | 322 (2024-12) |  |
| curator | Euler DAO | `euler-dao` | Risk Curators | 0.0 | 0.0 | 0.0 | 1,074 (2025-04) |  |

## Re-run

```
cd mm                                   # this folder
python3 scripts/make_fetch_list.py      # raw/protocols.json (api.llama.fi/protocols) -> raw/fetch_list.json
python3 scripts/fetch_protocols.py      # api.llama.fi/protocol/{slug} -> raw/proto/ (cached; retries a cached 502 with case variants of the slug)
python3 scripts/fetch_protocols.py accountable townsquare-lending   # below the TVL screen
python3 scripts/select_pools.py         # raw/pools.json + raw/lendborrow.json (yields.llama.fi) -> raw/btc_lending_pools.json
python3 scripts/fetch_pool_charts.py 300000                          # yields.llama.fi/chart/{pool} -> raw/charts/
python3 scripts/scan_symbols.py         # BTC-like symbols per protocol (checks for aliases / unlisted tokens)
python3 scripts/process.py              # -> out/mm_long.json, out/screen_results.json, out/unit_adjustments.json
python3 scripts/build.py                # -> mm_monthly.csv, mm_monthly_by_chain.csv, mm_tokens_snapshot.csv, mm_protocols.csv, mm_apy.csv
python3 scripts/morpho_markets.py; python3 scripts/morpho_positions.py; python3 scripts/morpho_holder_names.py   # Morpho API checks
python3 scripts/atoken_holders.py       # Blockscout aToken holders
python3 scripts/overlap.py              # -> mm_overlap.csv
python3 scripts/reconcile.py            # -> out/reconcile.json
```
Manual inputs used by `overlap.py` (read once, 2026-09-23): `api.ipor.io/fusion/vaults` (raw/ipor_vaults.json), the DefiLlama curator registry (`registries/curators.js`, evaluated with node into raw/curators_registry.json), ydaemon / RPC reads of the Yearn vaults, and the repo files data/top5/kraken/ltv_weekly.csv, data/top5/etherfi/positions_monthly.csv, data/top5/mhyperbtc/positions.csv, data/top5/selection/carry_products_scan.csv and scan_borrowers_all.csv.
