# ETH yield: market map, top five carry products, findings

**Snapshot:** 2 October 2026, 23:59:59 UTC (Ethereum block 26,108,081). ETH at $2,669.39. Built 7 October 2026 to the standard of the BTC study; categories redrawn 8 October 2026.

**Questions:**
1. How much ETH earns a yield in products, counted once, and how it splits by strategy.
2. Which categories grew or shrank over two years.
3. The five largest products that post ETH as collateral and borrow dollars (carry): how they work, what they pay against stETH, who controls them, who pays the yield, how they exit.
4. What failed, and what is common to all of them.

**Where things are:** site [`eth/index.html`](../../../eth/index.html); deep dives [`research/eth/top5/en/`](../top5/en/) (Russian in [`research/eth/top5/`](../top5/)); map data [`data/eth/netmap/`](../../../data/eth/netmap/) with decisions and reasons in [`tools/eth/netmap/decisions.py`](../../../tools/eth/netmap/decisions.py).

## 0. Short answers

1. **16,044,015 ETH ($42.83B) earns a yield in 133 products, each counted once.** Staking 12.00M (74.8%), leveraged staking 2.89M (18.0%), farming 528k (3.3%), restaking 419k (2.6%), carry 172k (1.1%), credit 27k, fixed yield 9k, options 2k. Money markets (3.23M ETH and staking tokens posted in lending markets outside loops and carry products) and CDPs (657k) are listed and off by default. About 14.4M ETH more is staked off-chain (exchanges, institutional providers, BitMine) and not counted.
2. **Two years: staking and loops grew, restaking and farming shrank.** Total 16.64M (Oct 2024), peak 17.45M (Jan 2026), low 15.30M (Jun 2026), 16.04M now. Staking +2.05M (9.95M to 12.00M). Leveraged staking 2.25M, peak 4.28M (Jan 2026), 2.59M after the April rsETH exploit (May 2026), 2.89M now. Restaking fell from 2.51M to 0.42M as weETH and rsETH moved into lending markets. Farming fell from 1.58M to 0.53M, fixed yield from 307k to 9k. Carry is the only new category: nearly zero until August 2025, 172k ETH now.
3. **Carry is small and concentrated.** 12 products owe $270.9M of dollars against 171,649 ETH, 1.1% of the map (BTC 9.9%, counted on whole books). Liquid ETH and YieldBasis hold 77% of the debt; Liquid ETH and Lido Earn hold 82% of the carry ETH.
4. **Carry barely beats staking.** The best product, Liquid ETH, beat stETH by 0.66 pp a year over two years, all of it in year two, and mostly from a fee cut. Its dollar leg loses about $6.8M a year at 2 October rates. YieldBasis is the only one whose fees cover its loan, and its depositors still trail stETH unless they take YB emissions.
5. **Rewards are a minority of the lead over stETH,** except at YieldBasis (all of it, for gauge stakers) and Liquity (99%). Liquid: 34%. Lido Earn: none in 90 days. Avant: 7%.
6. **Private mandates borrow as much as all carry products together.** Concrete Delta (307k ETH, one Bitfinex-linked wallet, $176.2M of debt) and three whitelist-only rSHARE vaults (about 83k WETH, $80.4M) are left out of the map, like Avalon in BTC.
7. **No large pooled product is missing.** A scan of every lending venue found 162 wallets with at least $5M of stablecoin debt against ETH. The 38 above $20M owe $2.28B; four are pooled products (Liquid ETH ×3, Lido Earn), the rest are private mandates, funds, desks and individuals. The only new product is Yearn's WETH-2 vault ($1.5M). Avant's debt was under-counted: $19.7M, not $10.0M ([SELECTION](SELECTION.md)).

## 1. The map now

| Category | ETH | Share | Note |
|---|---:|---:|---|
| Staking | 12,001,955 | 74.8% | Lido 6.59M, Binance 3.73M, Rocket Pool 0.46M, cbETH 0.36M (on-chain supply); staked and held only |
| Leveraged staking | 2,885,012 | 18.0% | Aave v3 and v2 2.07M, Spark 0.53M, Morpho, Fluid and others; equity about 307k ETH |
| Farming | 528,228 | 3.3% | points, pools (the ETH side no other row counts), vaults |
| Restaking | 419,194 | 2.6% | EigenLayer direct 0.21M, ether.fi Stake 0.07M, Renzo 0.04M; weETH 1.83M and rsETH 0.39M sit in lending markets |
| Carry | 171,649 | 1.1% | 12 products, $270.9M of dollar debt; only the ETH behind those loans |
| Credit, fixed yield, options, basis | about 38,000 | 0.2% | credit counts lent-out ETH too; basis is nearly empty |
| Money markets (off) | 3,231,215 | | ETH and staking tokens posted in lending markets outside loops and carry products |
| CDPs (off) | 657,327 | | |

Four rules decide where ETH in and around lending markets goes (8 October 2026). **Staking** and **restaking** are staked and held, not used anywhere else: issuer TVL less every staking token posted in a lending market, looped or held inside another product or pool (5.48M ETH of staking tokens sit in lending markets). **Leveraged staking** is every loop of staked ETH, or ETH, against borrowed ETH on lending markets, private and product; month-ends before the snapshot are estimated from ETH debt. **Carry** is only products open for deposits, and only the part of each book where ETH is collateral for a dollar loan; the rest of the book follows the same rules (Liquid ETH's weETH loop is leveraged staking). **Money markets** are everything else posted in lending markets, mostly collateral for dollar loans by unknown wallets, off by default as in BTC; CDPs stay separate and off. ETH carry is 1.1% against 9.9% in BTC, but the BTC map counts the whole book of each carry product as carry, so the two are not on the same basis.

In lending markets, $5.07B of stablecoins is borrowed against ETH and $5.24B against BTC. Half of ETH collateral (3.16M of 6.30M ETH) backs dollar loans and 46% backs loops; for BTC, 97% backs dollar loans ([LENDING-SPLIT](LENDING-SPLIT.md)).

Counting rules, the same at every month-end: a staking token, or another product's token, held inside a counted product or posted in a lending market leaves the row that issued it; lending collateral counts once and lent-out WETH is not added; a DEX pool counts only its ETH side that no other row counts; loop vaults count zero, their positions are inside leveraged staking; restaking platforms count only what token issuers and other products did not; vaults that only lend WETH go with money markets and vaults holding DEX positions are counted in the pools; credit counts lent-out ETH; a reviewed leftover row flat for three month-ends counts as zero and keeps no tokens from issuers; carry counts only in months with at least $10k of dollar debt; products under $50k at the snapshot stay in the totals but are not listed. Details: [MARKET-COVERAGE](MARKET-COVERAGE.md). DefiLlama cross-check: 97.1% of the TVL of 603 ETH pools is on the map.

## 2. Two years

| Category | Oct 2024 | Peak | 2 Oct 2026 |
|---|---:|---|---:|
| Staking | 9.95M | now | 12.00M |
| Leveraged staking | 2.25M | 4.28M, Jan 2026 | 2.89M |
| Restaking | 2.51M | Oct 2024 | 0.42M |
| Farming | 1.58M | Oct 2024 | 0.53M |
| Fixed yield | 307k | Oct 2024 | 9k |
| Carry | 0 | now | 172k |
| Total | 16.64M | 17.45M, Jan 2026 | 16.04M |

Restaking paid nothing extra: weETH earned 5.29% against stETH's 5.49% over two years in total, and EIGEN fell from about $3.4 to $0.20. Points programmes ended and farming left with them. Leveraged staking stays large on a thin spread: stETH beat the Aave WETH borrow rate by only 0.15 pp a year on average in year one and 0.10 pp in year two ([RESTAKING-AND-LOOPS](RESTAKING-AND-LOOPS.md)). It fell from 4.28M in January 2026 to 2.59M in May, after the April rsETH exploit. Its history is an estimate (month-end ETH debt times the snapshot ratio of loop collateral to debt); carry history is measured account by account.

## 3. Top five carry products

| # | Product | Book, ETH | Carry, ETH | Dollar debt | Paid vs stETH | Without rewards | Control |
|---|---|---:|---:|---:|---|---|---|
| 1 | ether.fi Liquid ETH | 177,171 | 115,864 | $181.1M | 3.37% vs 2.71%, two years | 3.39% vs 3.87%, a year | Veda vault run by Nonce |
| 2 | YieldBasis WETH | 10,426 | 10,426 | $27.8M | unstaked −2.96%, staked +1.69%, 90 days | −2.96% | admin fee 40.5% on 2 October |
| 3 | Lido Earn ETH | 83,309 | 25,029 | $25.6M | 3.14%, 90 days | 3.14% | 5-of-8 Safe, no timelock |
| 4 | Avant savETH | 12,583 | 7,493 | $19.7M with Aave v4 and Morpho | 4.74%, 90 days | 4.55% | one EOA |
| 5 | Liquity ETH Carry | 6,014 | 6,014 | $6.75M | 3.84%, 90 days | 2.26% | 2-of-3 Safe, no delay |

## 4. Findings by product

**Liquid ETH** ([deep dive](../top5/en/01-liquid.md)). Year one trailed stETH (2.86% vs 2.93%); year two led (3.86% vs 2.47%). The management fee fell from 1.10 to 0.26 pp of NAV, most of the turn. The share price is posted (at most ±0.5% per update, 6 hours apart) and did not show the April loop loss. Two wallets left and returned twice, moving the book 32 to 40% within a week. 26% of the debt has no same-currency source in the repayment ladder.

**YieldBasis** ([deep dive](../top5/en/02-yieldbasis.md)). The pool loses when ETH rallies: since 12 June the share is −0.89% while ETH is +60%. Depositors as a group lost about 50 ETH since 31 May. Staked holders take the losses but none of the gains; YB emissions ($504k a year) are their whole return. Exit is close to book (−1.17% for a 99% exit).

**Lido Earn** ([deep dive](../top5/en/03-lido-earn.md)). The rsETH loop that froze the vault in April is still open: 113,216 rsETH against 112,310 WETH at health factor 1.035, 12% of the book, standing only through Aave's rsETH e-mode. A 3.4% fall in rsETH liquidates it. The loop was built up in the three weeks before the exploit; half the book queued to leave in three days and waited 27. The DAO's first-loss shares were minted 20 days after the loss. Since June the yield is organic: 3.40% vs 2.31%.

**Avant** ([deep dive](../top5/en/04-avant.md)). Beat stETH in all 54 weeks with no negative week, because one address pushes the rate daily rather than marking the strategy. The dollar spread is at its thinnest on 2 October (+1.24 pp, from +4.8 pp in August). Half of savETH is itself collateral elsewhere. Only about half the book is visible on Ethereum.

**Liquity ETH Carry** ([deep dive](../top5/en/05-liquity.md)). The share price never recovered its March test loss (−6%) and sits on its high-water mark. The measured legs lose −1.0% a year; an unexplained +3.3 pp carries the rest. BOLD rewards ($153k a year) roughly equal the curator and IPOR fees. Two holders own 49%.

## 5. What failed

- **Kelp rsETH exploit, 18 April 2026:** 112k unbacked rsETH. Lido Earn froze 27 days; Kelp Gain froze to 5 June and wrote down 500 rsETH; Aave was left short 52,964 WETH on Ethereum and 29,835 on Arbitrum.
- **Rocksolid rETH:** closed 29 September, reopened 7 October.
- **Reservoir and TAU:** emptied quietly with debt left near zero; check the debt, not the name.

Details: [CLOSED-CASES](CLOSED-CASES.md).

## 6. Common to all five

1. Carry has to beat staking, not zero. Over two years only Liquid did, by 0.66 pp, and not because of its dollar leg.
2. The loan currency decides the spread: on 2 October Aave charged 13.93% for USDC and 4.38% for USDT.
3. Share prices are posted or pushed, not marked, so losses show late or never.
4. Keys: no timelock at Lido Earn, one EOA at Avant, a 2-of-3 Safe with no delay at Liquity.
5. A few wallets own each book and leave together.
6. The same dollar vaults fund BTC and ETH carry: Liquid parks $55M in Sentora's RLUSD vault, 53% of which is lent to Kraken's kBTC loop.

## Method and limits

Method, decisions and the re-check: [MARKET-COVERAGE](MARKET-COVERAGE.md), [BRIEFING](BRIEFING.md), and the Data section of the site. Not verified: Liquid's residual income, Lido Earn's launch-month yield, Avant's books on other chains, Liquity's keeper-stored balances, and the identity of large wallets. Map limits: lending positions of map products other than the carry and loop products (farming vaults, credit) are not separated from the lending cells, so money markets, off by default, is an upper bound; leveraged staking history is an estimate from ETH debt; whether Cap's wstETH and ether.fi's weETHs vault also sit in EigenLayer or Symbiotic is not checked; YieldBasis' pool counts in Curve before its on-chain book starts (May 2026).
