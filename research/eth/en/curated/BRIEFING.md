# ETH yield research: team briefing

Financial snapshot: **2 October 2026**. Same data as the main page.

## Answer

**15,924,980 ETH earns a yield** in 133 products counted once ($42.51B on 2 October 2026): 74.8% staking, 18.1% leveraged staking, 3.3% farming and pools, 2.6% restaking. About 14.4M ETH more is staked off-chain with exchanges, institutional providers and BitMine; it is listed, not counted.

**Carry is 1.1%**: 178,579 ETH, the part of 16 products open for deposits where ETH is collateral for a dollar loan. They owe $277.7M; Liquid ETH and Lido Earn hold 79% of the carry ETH. In BTC carry is 9.8%, but the BTC map counts the whole book of each carry product, so the two shares are not on the same basis.

**Carry barely beats staking.** Liquid ETH beat stETH by 0.66 pp a year over two years (3.37% against 2.71%). Its ETH loop added +0.02 pp a year and its dollar leg -0.13 pp; the rest is income our model cannot assign. At 2 October rates the dollar leg loses about $6.8M a year ($9.0M of interest on one 13.93% Aave USDC loan). YieldBasis is the only top-five product whose fees cover its loan.

## Market and two years of history

| Category | ETH, 2 Oct 2026 | Share | Oct 2024 | Switch |
| --- | --- | --- | --- | --- |
| Staking | 11,900,735 | 74.7% | 9,589,367 | on |
| Restaking | 411,377 | 2.6% | 2,513,366 | on |
| Leveraged staking | 2,885,012 | 18.1% | 2,247,038 | on |
| Carry | 178,579 | 1.1% | 0 | on |
| Fixed yield | 9,203 | 0.1% | 307,465 | on |
| Basis | 372 | 0.0% | 25,423 | on |
| Options | 1,664 | 0.0% | 4,786 | on |
| Credit | 26,682 | 0.2% | 5,051 | on |
| Farming and pools | 511,356 | 3.2% | 1,583,227 | on |
| Money markets | 3,223,361 | off | 2,743,062 | off |
| CDP collateral | 765,192 | off | 1,637,787 | off |

Each product is counted once, where the ETH is used. Staking and restaking are staked and held, not used anywhere else: staking tokens posted in lending markets (5.48M ETH) or held by other products leave their issuers. Leveraged staking is every loop of staked ETH against borrowed ETH on lending markets, private and product (equity about 313k ETH; month-ends estimated from ETH debt). Carry is only the dollar-loan part of products open for deposits; their loops count as leveraged staking. Money markets (ETH and staking tokens posted outside loops and carry products, mostly collateral for dollar loans by unknown wallets) and CDPs are off by default, as in BTC. Binance's wBETH grew by 2.18M ETH, the largest change on the map; restaking fell from 2.51M ETH (October 2024) as weETH and rsETH moved into lending markets, and farming and pools from 1.58M ETH (October 2024) as points programmes ended. [Method and every netting step](../../../data/eth/netmap/netting_ledger.csv).

The beacon chain holds **43.81M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: 11.90M ETH staked and held and 0.42M restaked and held; 5.48M ETH of staking tokens sit in lending markets and are counted there (leveraged staking, carry, money markets). About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. The remaining 11.50M ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. [Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).

## Top five carry products

Ranked by dollars borrowed against ETH. Concrete Delta weETH (307,363 ETH, $176.15M of stablecoin debt) is left out of the map and the ranking: its whole supply was minted to one address after a Bitfinex-linked wallet moved its own Aave position into the vault's Safe; there are no outside depositors ([evidence](CONCRETE-DELTA.md)).

| Product | Dollars borrowed | Loan rate | Whole book, ETH | Carry, ETH |
| --- | --- | --- | --- | --- |
| ether.fi Liquid ETH | $181.1M | 7.79% | 177,171 | 115,864 |
| YieldBasis WETH | $27.8M | 10.00% | 10,426 | 10,426 |
| Lido Earn ETH | $25.6M | 4.33% | 83,309 | 25,029 |
| Avant avETH / savETH | $19.7M | 6.30% | 12,583 | 7,493 |
| Liquity ETH Carry | $6.8M | 2.55% | 6,014 | 6,014 |

Other carry: NEMO ETH Prime ($5.6M), Rocksolid rETH ($2.7M), Sentora ETH ($1.2M), Makina DETH ($385k), Royco ETH ($91k), Vesper vaETH ($69k), Reservoir ETH Yield ($37k), TAU InfiniFi ETH Carry (dust). Rocksolid closed on 29 September and reopened on 7 October. ZenSats wstETH is a micro-position. [All carry products](CARRY-CATEGORY.md), [risk, repayment ladder and reward payers](TOP5-RISK-LIQUIDITY.md).

## 30-day returns

All products below use **2 September to 2 October 2026**: ETH book marks, before external payouts and exit costs. YieldBasis is the unstaked LT fair value. Fees already in the share price are not deducted again.

| Product | 30-day ETH book return | Excess vs stETH, pp |
| --- | --- | --- |
| ether.fi Liquid ETH | 0.2610% | +0.0761 |
| YieldBasis WETH | -0.1622% | -0.3471 |
| Lido Earn ETH | 0.2513% | +0.0664 |
| Avant avETH / savETH | 0.3385% | +0.1536 |
| Liquity ETH Carry | 0.4597% | +0.2748 |
| Concrete Delta weETH (excluded, reference only) | 0.1915% | +0.0066 |
| Rocksolid rETH | 0.2192% | +0.0343 |
| Makina DETH | 0.3468% | +0.1619 |
| Vesper vaETH | 0.0698% | -0.1151 |
| Royco ETH | 0.1849% | +0.0000 |
| ZenSats wstETH | 0.2480% | +0.0630 |

stETH returned **0.1849%** over the same days. Concrete's share price is flat in weETH, so its row is weETH staking and nothing else.

## Financed lots

Four loans traced from borrowing to the investment and back to repayment (or to T for the open Lido lot). Selected cases, not a market average; gas and collateral income excluded.

| Borrowed amount | Investment income | Funding cost | Result before gas |
| --- | --- | --- | --- |
| 350,000 USDC | 59.633841 | 146.057155 | -86.423314 USDC |
| 350,000 USDC | 32.206543 | 93.832732 | -61.626189 USDC |
| 1,000,000 PYUSD | 1.948867 | 2.347298 | -0.398431 PYUSD |
| 5,000,000 USDT | 3651.565058 | 2250.992481 | 1400.572577 USDT |

[Financed lots and the two flow-adjusted ledgers](CARRY-LIFECYCLES.md), [Liquid income ledger](CAPITAL-INCOME-EXIT.md), [rewards split](REWARDS-SPLIT.md).

## Coverage

DefiLlama lists 299 ETH-name pools above $5M; 224 belong to a product already on the map and the other 75 have a written decision ([CARRY-COVERAGE-AUDIT](CARRY-COVERAGE-AUDIT.md)). What the map counts, lists and leaves out: [coverage](MARKET-COVERAGE.md).

## Reproduce the answers

[Canonical data](../../../data/eth/report_contract.json), [common return CSV](../../../data/eth/carry-common-30d.csv), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv), [market map CSV](../../../data/eth/netmap/market_map_current.csv).
