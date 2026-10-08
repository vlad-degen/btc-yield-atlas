# What is borrowed against ETH and BTC in lending markets

ETH: 2 October 2026, 23:59:59 UTC (Ethereum block 26,108,081), ETH $2,669.39. BTC: 20 September 2026, 12:00 UTC (Ethereum block 26,018,583), BTC $81,178. L2s: last block at or before each time. Data: `data/eth/lending_split.json`, `data/eth/lending_split_accounts.csv`.

Form A = staking or yield tokens (wstETH, weETH, rsETH, osETH; LBTC, SolvBTC.BBN, eBTC). Form B = plain WETH or plain BTC wrappers (WBTC, cbBTC, tBTC, kBTC). Each holding is counted once. WETH that a pool has lent out is shown as a memo line, not as a second holding.

## ETH, 6.30M ETH ($16.8B)

| | 1 ETH borrowed (loops) | 2 Stablecoins borrowed | 3 Other borrowed | 4 Nothing borrowed | Total |
|---|---:|---:|---:|---:|---:|
| A Staking tokens | 2,907k ETH, $7.76B | 2,503k ETH, $6.68B | 23k, $0.06B | 76k, $0.20B | 5,509k, $14.71B |
| B Plain ETH/WETH | 6k, $0.02B | 661k, $1.76B | 4k, $0.01B | 117k, $0.31B | 789k, $2.11B |
| Total | 2,914k, $7.78B | 3,164k, $8.45B | 27k, $0.07B | 193k, $0.52B | 6,298k, $16.81B |

Memo: 2.65M WETH lent out. This is the other side of column 1. The loops owe 2.63M ETH against 2.94M ETH of collateral, so their ETH equity is 0.31M ETH ($0.84B), about 9.4x leverage. Stablecoin debt in column 2 is $5.07B against $13.8B of collateral claims, an LTV of 37%.

## BTC, 173.7k BTC ($14.1B)

| | 1 BTC borrowed | 2 Stablecoins borrowed | 3 ETH or other borrowed | 4 Nothing borrowed | Total |
|---|---:|---:|---:|---:|---:|
| A Staking / yield tokens | 88 BTC, $0.01B | 6,780, $0.55B | 39, $0.00B | 82, $0.01B | 6,989, $0.57B |
| B Plain wrappers | 863, $0.07B | 161,953, $13.15B | 932, $0.08B | 3,008, $0.24B | 166,756, $13.54B |
| Total | 951, $0.08B | 168,733, $13.70B | 971, $0.08B | 3,090, $0.25B | 173,745, $14.10B |

Memo: 1.5k BTC lent out. Stablecoin debt in column 2 is $5.24B against $11.6B of collateral, an LTV of 45% (venues read account by account).

Both tables include an estimated long tail: 0.10M ETH and 28.2k BTC. This is the gap between DefiLlama's lending total and what was read. It is spread using the mix that was read.

## Findings

1. **Only half of ETH in lending backs dollar loans. Almost all lending BTC does.** Column 2 holds 3.16M ETH (50%) and 168.7k BTC (97%). The other 46% of ETH is loop collateral. BTC loops are under 1k BTC.
2. **Dollar debt against ETH and against BTC is about the same.** Across the same venues, $5.07B of stablecoins is borrowed against ETH and $5.24B against BTC. The ETH pool is larger, $16.8B against $14.1B, so ETH holders borrow fewer dollars per unit of collateral. LTV is 37% on ETH and 45% on BTC.
3. **Loops are large but hold little equity.** 2.94M ETH of loop collateral carries 2.63M ETH of debt, leaving 0.31M ETH of equity. The top 20 loop accounts hold 69% of loop collateral. ether.fi Liquid ETH alone holds 443k ETH on Aave.
4. **Most WETH supplied to Aave and Spark is dollar borrowers' collateral, not idle lender money.** Of 3.37M plain WETH supplied, 2.68M sits in accounts that borrow stablecoins. Only 0.63M sits in accounts with no debt. Yet 2.65M WETH is lent out. So the WETH that loopers borrow is mostly WETH that dollar borrowers posted. Counted once, plain WETH backing stablecoins falls from 2.68M to 0.66M.
5. **ETH dollar loans are concentrated. BTC dollar loans are spread out.** The 38 borrowers with more than $20M of ETH-backed stablecoin debt (gap_borrower_scan.csv) hold 2.37M ETH of collateral claims (46%) and owe $2.29B (45%). Pooled carry products (Liquid ETH, Lido Earn and the others flagged pooled) owe only $0.24B (4.7%). On the BTC side the top 20 accounts hold 26% of plain BTC backing stablecoins. Coinbase's cbBTC/USDC market on Base is 37.0k BTC (22% of column 2), spread across about 43k positions.
6. **Staking tokens dominate ETH collateral. Plain wrappers dominate BTC collateral.** Staking tokens are 87% of ETH in lending, and 2.50M ETH of them ($6.68B) back dollar loans. On BTC, yield tokens are 4% (mostly LBTC on Aave and Spark), and almost all of that is also borrowed against in dollars.
7. **Little low-LTV noise.** In column 2, only 5% of ETH collateral (1% of BTC) sits in accounts whose dollar debt is below 10% of it. The pro-rata rule does not inflate the dollar-loan cell.

## Method

- Pooled venues are Aave v3 (Core, Prime, EtherFi; Base, Arbitrum, Optimism, Linea, Polygon, Gnosis), Spark and Aave v4. Each account's family collateral is split across its debts in proportion to their USD value. Supply not enabled as collateral, and supply of accounts with no debt, goes to column 4.
- Counted once: each holding is cut by its reserve's utilization, which is the part the pool has lent out. The gross claims are 8.87M ETH and 147.1k BTC. The cut is applied pro rata because pool WETH is fungible.
- Pair venues are Morpho Blue (all API chains), Compound v3 and Fluid vaults. Each position goes to its loan asset. A position with collateral and no debt goes to column 4. Lender supply of the family asset goes to column 4, less the part that is lent out.
- Accounts were enumerated from Blockscout holders on Ethereum, Etherscan-family holder pages on L2s, aToken senders after the snapshot, Morpho API positions plus collateral withdrawals and liquidations after the snapshot, Compound SupplyCollateral logs, and Fluid's position resolver. Each account was then read on chain at the snapshot block through Multicall3.
- Stablecoin debt in column 2 is each account's stablecoin debt times its family share of enabled collateral. Loop ETH debt is attributed the same way.

## Coverage and limits

| Venue | ETH-family in venue (gross) | Read account by account | Held by accounts with at least $500k |
|---|---:|---:|---:|
| Aave v3 Ethereum | 5.23M | 97% | 92% |
| Spark | 2.01M | 100% | 99% |
| Morpho Ethereum / L2s | 0.45M / 0.17M | 100% (pair exact) | 94% / 48% |
| Aave v3 L2s | 0.42M | 71% (Base, Arbitrum read; Optimism, Linea, Polygon, Gnosis estimated) | 51% |
| Compound v3 Ethereum / L2s | 0.27M / 0.02M | 100% / 52% | 93% / 26% |
| Aave v4 | 0.12M | 100% | 83% |
| Fluid Ethereum / L2s | 0.16M / 0.02M | 100% / estimated | 93% / n/a |

BTC: Aave Ethereum 99% read (88% in large accounts), Morpho Base and Ethereum 100% (62% and 95%), Spark 100% (97%), Compound Ethereum 100% (93%), Aave Base and Arbitrum 77%.

- Estimates are labelled in the JSON. Unread small holders are spread by the mix of the small accounts that were read. Aave pools on Optimism, Linea, Polygon and Gnosis use the Base and Arbitrum mix, because explorer holder pages were unavailable. Compound Base and Optimism use the Ethereum split between collateral with and without debt. Fluid on Arbitrum and Base uses vault totals from the API on the scan day.
- Estimated parts are 3% of measured ETH and 2% of measured BTC. The long tail is 1.6% of ETH and 16% of BTC. On the BTC side this is mostly Venus, JustLend, Lista and Aave on Avalanche, BNB and Polygon. Euler is not read on either side; it is in the long tail.
- Morpho collateral is valued at today's API price ratios to ETH or BTC. Rates move little in a week. 1.2M "BTC" of unpriced look-alike collateral (wsBTCD) and 0.1M "ETH" on Monad were dropped, along with a fake-IRM cbBTC loan market.
- Aave v4 collateral flags were not read. Supplied family assets of an account with debt are treated as collateral.
- The BTC snapshot is 12 days earlier than the ETH snapshot. Both use their own study prices.
