# WETH lending: claims, debt and available cash

Snapshot T: 2 October 2026, 23:59:59 UTC. This study covers Aave V3 on Ethereum, Base, Arbitrum and Optimism, plus Spark on Ethereum. Contract addresses were checked against official address books and `getReserveData` calls. Within each market, WETH cash, lender claims and debt-token supply were read at the same block.

## Claims and outstanding debt

| Protocol / chain | Lender claims, WETH | Outstanding debt, WETH | Reserve cash, WETH | Supply APR at T | Borrow APR at T |
|---|---:|---:|---:|---:|---:|
| aave / ethereum | 2,084,173.40 | 1,761,598.49 | 269,693.45 | 1.490% | 2.074% |
| spark / ethereum | 608,325.69 | 492,183.60 | 116,147.84 | 1.466% | 1.907% |
| aave / optimism | 8,517.63 | 6,274.08 | 2,243.49 | 1.127% | 1.801% |
| aave / base | 85,371.09 | 70,588.44 | 14,783.07 | 1.453% | 2.067% |
| aave / arbitrum | 95,030.48 | 57,608.71 | 7,623.32 | 1.088% | 2.112% |

Across these five markets, lenders hold **2,881,418.29 WETH in claims**, borrowers owe **2,388,253.31 WETH**, and reserves hold 410,491.18 WETH in cash. These measure different parts of lending. Borrowed ETH can be staked and appear again as LST backing, so adding the two would count the same deployment twice.

Liquid ETH's main account owes **23.28%** of Aave Ethereum's variable WETH debt and **6.31%** of Spark's. The calculation includes this verified account, not every potentially linked borrower. It shows that a managed ETH yield product is a material source of demand for ETH loans.

## Why lender claims exceed cash plus debt

| Aave chain | getReserveDeficit(WETH), WETH | Deficit / lender claims | Claims − cash − debt, WETH |
|---|---:|---:|---:|
| ethereum | 52,964.453913 | 2.5413% | 52,881.463992 |
| optimism | 0.076433 | 0.0009% | 0.050285 |
| base | 0.001238 | 0.0000% | -0.412268 |
| arbitrum | 29,835.199567 | 31.3954% | 29,798.450998 |

At T, Aave's `getReserveDeficit(WETH)` reports 52,964.453913 WETH on Ethereum and 29,835.199567 WETH on Arbitrum. These come from the contract getter, rather than a subtraction alone. The Optimism and Base values are small. Spark's equivalent getters were unavailable in the checked responses, so its deficit remains unknown.

[Aave v3.3's definition](https://github.com/aave-dao/aave-v3-origin/blob/main/docs/3.3/Aave-v3.3-features.md) explains reserve deficit and its permissioned reduction through aToken burns. Claims−cash−debt need not exactly equal stored deficit because of treasury accounting, accrued indexes, virtual balances and rounding. The getter gap is preserved rather than forced to zero.

The deficit as a share of lender claims describes reserve accounting. It **does not establish the final loss to aToken holders**. Recovery assets, outside compensation and settlement require a separate reconciliation. A normal interest rate or available withdrawal cash does not show that the recorded deficit has been cleared.

## Incident attribution and conclusion limits

The [20 April Aave provider report](https://governance.aave.com/t/rseth-incident-report-april-20-2026/24580) describes rsETH bridge risk becoming WETH borrowing exposure on Ethereum/Arbitrum and possible coverage. [Aave Labs' May update](https://governance.aave.com/t/al-development-update-may-2026/25013) discusses liquidations, recovery guardian and ETH liquidity restoration. These disclosures provide context; each outstanding deficit at T is not yet reconciled to a complete event-level recovery waterfall.

A WETH lending reserve can be affected by the quality of the bridged or staked tokens borrowers post as collateral. To assess it, examine interest income, cash for withdrawals, collectible debt and recovery rights separately. The snapshot is not a loss forecast or a complete financial audit of Aave.

Full request/response evidence: `weth_lending_markets_T.json`; summary: `weth_lending_summary_T.json`. Each getter uses its chain's fixed block; current UI does not substitute for historical borrowing state.
