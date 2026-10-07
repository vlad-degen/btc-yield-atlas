# ETH yield: market map, top five carry products, findings

**Snapshot:** 2 October 2026, 23:59:59 UTC (Ethereum block 26,108,081). ETH at $2,669.39. Built 7 October 2026 to the standard of the BTC study.

**Questions:**
1. How much ETH earns a yield in products, counted once, and how it splits by strategy.
2. Which categories grew or shrank over two years.
3. The five largest products that post ETH as collateral and borrow dollars (carry): how they work, what they pay against stETH, who controls them, who pays the yield, how they exit.
4. What failed, and what is common to all of them.

**Where things are:** site [`eth/index.html`](../../../eth/index.html); deep dives [`research/eth/top5/en/`](../top5/en/) (Russian in [`research/eth/top5/`](../top5/)); map data [`data/eth/netmap/`](../../../data/eth/netmap/) with decisions and reasons in [`tools/eth/netmap/decisions.py`](../../../tools/eth/netmap/decisions.py).

## 0. Short answers

1. **18,499,055 ETH ($49.38B) earns a yield in 131 products, each counted once.** Staking 15.09M (82%), restaking 2.44M (13%), farming 529k, carry 306k (1.7%), leveraged staking 98k, credit 27k, fixed yield 9k, options 2k. WETH in money markets and lending-only vaults (812k) and CDPs (657k) is listed and off by default. About 14.4M ETH more is staked off-chain (exchanges, institutional providers, BitMine) and not counted.
2. **Two years: staking grew, everything around it shrank.** Total 18.55M (Oct 2024), peak 20.00M (Jan 2026), 18.50M now. Staking +2.51M. Restaking peaked at 4.63M (Jul 2025) and lost half. Farming fell from 1.58M to 0.53M, fixed yield from 307k to 9k, leveraged staking from a 415k peak (May 2025) to 98k. Carry is the only new category: from nothing to 306k ETH in a year.
3. **Carry is small and concentrated.** 12 products owe $270.9M of dollars against ETH (BTC: 9.9% of its market is carry, ETH 1.7%). Liquid ETH and YieldBasis hold 77% of the debt; Liquid ETH and Lido Earn hold 85% of the ETH.
4. **Carry barely beats staking.** The best product, Liquid ETH, beat stETH by 0.66 pp a year over two years, all of it in year two, and mostly from a fee cut. Its dollar leg loses about $6.8M a year at 2 October rates. YieldBasis is the only one whose fees cover its loan, and its depositors still trail stETH unless they take YB emissions.
5. **Rewards are a minority of the lead over stETH,** except at YieldBasis (all of it, for gauge stakers) and Liquity (99%). Liquid: 34%. Lido Earn: none in 90 days. Avant: 7%.
6. **Private mandates borrow as much as all carry products together.** Concrete Delta (307k ETH, one Bitfinex-linked wallet, $176.2M of debt) and three whitelist-only rSHARE vaults (about 83k WETH, $80.4M) are left out of the map, like Avalon in BTC.
7. **No large pooled product is missing.** A scan of every lending venue found 162 wallets with at least $5M of stablecoin debt against ETH. The 38 above $20M owe $2.28B; four are pooled products (Liquid ETH ×3, Lido Earn), the rest are private mandates, funds, desks and individuals. The only new product is Yearn's WETH-2 vault ($1.5M). Avant's debt was under-counted: $19.7M, not $10.0M ([SELECTION](SELECTION.md)).

## 1. The map now

| Category | ETH | Share | Note |
|---|---:|---:|---|
| Staking | 15,093,012 | 81.6% | Lido 9.39M, Binance 3.74M, Rocket Pool 0.50M, cbETH 0.45M (on-chain supply) |
| Restaking | 2,435,229 | 13.2% | ether.fi Stake 1.70M, Kelp 0.41M; EigenLayer and Symbiotic only where no issuer or other product counted it |
| Farming | 529,000 | 2.9% | points, pools (the ETH side no other row counts), vaults |
| Carry | 305,908 | 1.7% | 12 products, $270.9M of dollar debt |
| Leveraged staking | 98,000 | 0.5% | |
| Credit, fixed yield, options, basis | about 38,000 | 0.2% | credit counts lent-out ETH too; basis is nearly empty |
| Money markets (off) | 812,000 | | plain WETH in lending markets and lending-only vaults |
| CDPs (off) | 657,000 | | |

Counting rules, the same at every month-end: a staking token, or another product's token, held inside a counted product leaves the row that issued it; a DEX pool counts only its ETH side that no other row counts; products count depositor equity (Treehouse is still at gross collateral); restaking platforms count only what token issuers and other products did not; vaults that only lend WETH go with money markets and vaults holding DEX positions are counted in the pools; credit counts lent-out ETH; a reviewed leftover row flat for three month-ends counts as zero and keeps no tokens from issuers; carry counts only in months with at least $10k of dollar debt; products under $50k at the snapshot stay in the totals but are not listed. Details: [MARKET-COVERAGE](MARKET-COVERAGE.md). DefiLlama cross-check: 97.2% of the TVL of 603 ETH pools is on the map.

## 2. Two years

| Category | Oct 2024 | Peak | 2 Oct 2026 |
|---|---:|---|---:|
| Staking | 12.58M | now | 15.09M |
| Restaking | 3.78M | 4.63M, Jul 2025 | 2.44M |
| Farming | 1.58M | Oct 2024 | 0.53M |
| Leveraged staking | 270k | 415k, May 2025 | 98k |
| Fixed yield | 307k | Oct 2024 | 9k |
| Carry | 0 | now | 306k |
| Total | 18.55M | 20.00M, Jan 2026 | 18.50M |

Restaking paid nothing extra: weETH earned 5.29% against stETH's 5.49% over two years in total, and EIGEN fell from about $3.4 to $0.20. Points programmes ended and farming left with them. Leveraged staking shrank because stETH beat the Aave WETH borrow rate by only 0.15 pp a year on average in year one and 0.10 pp in year two ([RESTAKING-AND-LOOPS](RESTAKING-AND-LOOPS.md)).

## 3. Top five carry products

| # | Product | ETH | Dollar debt | Paid vs stETH | Without rewards | Control |
|---|---|---:|---:|---|---|---|
| 1 | ether.fi Liquid ETH | 177,171 | $181.1M | 3.37% vs 2.71%, two years | 3.39% vs 3.87%, a year | Veda vault run by Nonce |
| 2 | YieldBasis WETH | 10,426 | $27.8M | unstaked −2.96%, staked +1.69%, 90 days | −2.96% | admin fee 40.5% on 2 October |
| 3 | Lido Earn ETH | 83,309 | $25.6M | 3.14%, 90 days | 3.14% | 5-of-8 Safe, no timelock |
| 4 | Avant savETH | 12,583 | $19.7M with Aave v4 and Morpho | 4.74%, 90 days | 4.55% | one EOA |
| 5 | Liquity ETH Carry | 6,014 | $6.75M | 3.84%, 90 days | 2.26% | 2-of-3 Safe, no delay |

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

Method, decisions and the re-check: [MARKET-COVERAGE](MARKET-COVERAGE.md), [BRIEFING](BRIEFING.md), and the Data section of the site. Not verified: Liquid's residual income, Lido Earn's launch-month yield, Avant's books on other chains, Liquity's keeper-stored balances, and the identity of large wallets. Map limits: money markets are not netted for positions of other map products (the BTC map is), so that off-by-default segment is an upper bound; Treehouse is counted at gross collateral; whether Cap's wstETH and ether.fi's weETHs vault also sit in EigenLayer or Symbiotic is not checked; YieldBasis' pool counts in Curve before its on-chain book starts (May 2026).
