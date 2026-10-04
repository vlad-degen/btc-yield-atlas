# Dollar funding across chains

Dollar carry starts with a financing choice. The same ETH collateral can support different dollar currencies and venues, with different interest, caps, oracles and repayment requirements. This atlas expands the selected Aave and Morpho analysis to additional dollar reserves and Spark. Every balance and stored rate below is read at the existing 2 October 2026, 23:59:59 UTC snapshot. Later holder discovery is labelled separately.

## What the expanded funding evidence shows

### Debt currency matters within the same chain

At T, Aave Ethereum USDC costs 13.93% APR while USDT costs 4.38%. The 9.55 percentage-point funding difference is larger than the measured USDC differences among several chains. The tokens have different credit, liquidity and conversion dependencies.

### A low displayed rate can belong to a closed route

Frozen reserves, disabled borrowing and caps below existing debt remain in the atlas. They describe debt already outstanding, rather than a new financing opportunity. Bridged and native versions of the same dollar token remain separate.

### Liquidity and rates constrain the same trade

Ethereum Aave USDC holds about $6.33M physical underlying at its reserve while USDT holds $183.29M. These balances do not guarantee a permitted loan, flash loan or simultaneous investor exit.

### Reserve debt is not ETH carry

Dollar reserve debt spans all collateral types. The borrower screen separately verifies enabled ETH-family collateral and dollar debt at T, then leaves use of loan proceeds unclassified until traced.

## Dollar reserves at the snapshot

The atlas measures 60 dollar reserves and 57 ETH-family reserves across 15 measured pool instances on 12 chains. 39 dollar reserves each have at least $1 million of observed variable debt across all collateral types. These are financing venues, not a sum of ETH carry capital.

| Pool | Chain | Dollar token | Borrow APR | Physical cash USD | Base rules |
|---|---|---|---:|---:|---|
| Aave V3 | ethereum | USDC | 13.934% | $6.325M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | DAI | 5.000% | $10.407M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | USDT | 4.382% | $183.294M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | LUSD | 2.065% | $1.278M | Restricted by the observed base rules |
| Aave V3 | ethereum | GHO | 4.250% | $19.355M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | crvUSD | 2.827% | $0.109M | Restricted by the observed base rules |
| Aave V3 | ethereum | PYUSD | 4.995% | $0.765M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | USDe | 6.608% | $533.888M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | USDS | 5.939% | $4.060M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | RLUSD | 4.633% | $1.036M | Allow a new loan subject to account checks |
| Aave V3 | ethereum | USDG | 3.908% | $2.382M | Allow a new loan subject to account checks |
| Aave V3 | base | USDbC | 8.085% | $0.042M | Restricted by the observed base rules |
| Aave V3 | base | USDC | 4.648% | $19.966M | Allow a new loan subject to account checks |
| Aave V3 | base | GHO | 4.497% | $0.144M | Allow a new loan subject to account checks |
| Aave V3 | arbitrum | DAI | 3.923% | $0.967M | Restricted by the observed base rules |
| Aave V3 | arbitrum | USDC | 23.314% | $0.069M | Restricted by the observed base rules |
| Aave V3 | arbitrum | USDT | 4.251% | $5.950M | Allow a new loan subject to account checks |
| Aave V3 | arbitrum | LUSD | 5.121% | $0.118M | Restricted by the observed base rules |
| Aave V3 | arbitrum | USDCn | 3.940% | $20.260M | Allow a new loan subject to account checks |
| Aave V3 | arbitrum | GHO | 4.117% | $0.143M | Allow a new loan subject to account checks |
| Aave V3 | optimism | DAI | 4.807% | $0.077M | Restricted by the observed base rules |
| Aave V3 | optimism | USDC | 2.918% | $0.818M | Restricted by the observed base rules |
| Aave V3 | optimism | USDT | 4.054% | $0.696M | Allow a new loan subject to account checks |
| Aave V3 | optimism | sUSD | 3.132% | $0.000M | Restricted by the observed base rules |
| Aave V3 | optimism | LUSD | 7.127% | $0.006M | Restricted by the observed base rules |
| Aave V3 | optimism | USDCn | 3.827% | $1.501M | Allow a new loan subject to account checks |
| Aave V3 Lido instance | ethereum | USDS | 5.353% | $0.012M | Restricted by the observed base rules |
| Aave V3 Lido instance | ethereum | USDC | 4.393% | $1.490M | Allow a new loan subject to account checks |
| Aave V3 Lido instance | ethereum | GHO | 3.923% | $7.426M | Allow a new loan subject to account checks |
| Aave V3 ether.fi instance | ethereum | USDC | 1.811% | $0.006M | Restricted by the observed base rules |
| Aave V3 ether.fi instance | ethereum | PYUSD | 0.000% | $0.000M | Allow a new loan subject to account checks |
| Aave V3 | bsc | USDC | 4.249% | $1.678M | Allow a new loan subject to account checks |
| Aave V3 | bsc | USDT | 3.925% | $13.060M | Allow a new loan subject to account checks |
| Aave V3 | polygon | DAI | 7.894% | $0.712M | Allow a new loan subject to account checks |
| Aave V3 | polygon | USDC | 9.595% | $0.456M | Restricted by the observed base rules |
| Aave V3 | polygon | USDT0 | 6.440% | $11.178M | Allow a new loan subject to account checks |
| Aave V3 | polygon | USDCn | 5.936% | $11.704M | Allow a new loan subject to account checks |
| Aave V3 | avalanche | USDC | 7.912% | $4.583M | Allow a new loan subject to account checks |
| Aave V3 | avalanche | USDt | 4.907% | $2.549M | Allow a new loan subject to account checks |
| Aave V3 | avalanche | GHO | 9.101% | $0.091M | Allow a new loan subject to account checks |
| Aave V3 | avalanche | USDe | 6.640% | $0.026M | Allow a new loan subject to account checks |
| Aave V3 | mantle | USDT0 | 4.000% | $16.290M | Allow a new loan subject to account checks |
| Aave V3 | mantle | USDC | 12.651% | $0.035M | Allow a new loan subject to account checks |
| Aave V3 | mantle | USDe | 6.600% | $33.118M | Allow a new loan subject to account checks |
| Aave V3 | mantle | GHO | 3.030% | $1.046M | Allow a new loan subject to account checks |
| Aave V3 | sonic | USDC | 9.025% | $1.062M | Restricted by the observed base rules |
| Aave V3 | linea | USDC | 4.255% | $0.167M | Allow a new loan subject to account checks |
| Aave V3 | linea | USDT | 4.316% | $0.049M | Allow a new loan subject to account checks |
| Aave V3 | scroll | USDC | 8.280% | $0.064M | Restricted by the observed base rules |
| Aave V3 | monad | USDT0 | 4.910% | $5.666M | Allow a new loan subject to account checks |
| Aave V3 | monad | USDC | 4.999% | $13.583M | Allow a new loan subject to account checks |
| Aave V3 | monad | USDe | 6.601% | $69.634M | Allow a new loan subject to account checks |
| Aave V3 | monad | GHO | 22.141% | $0.220M | Allow a new loan subject to account checks |
| SparkLend | ethereum | DAI | 4.243% | $76.385M | Allow a new loan subject to account checks |
| SparkLend | ethereum | USDC | 4.176% | $4.096M | Allow a new loan subject to account checks |
| SparkLend | ethereum | USDT | 3.966% | $15.949M | Allow a new loan subject to account checks |
| SparkLend | ethereum | USDS | 4.126% | $435.481M | Allow a new loan subject to account checks |
| SparkLend | ethereum | PYUSD | 4.388% | $85.935M | Allow a new loan subject to account checks |
| SparkLend | ethereum | USDG | 3.537% | $0.000M | Allow a new loan subject to account checks |
| SparkLend | ethereum | RLUSD | 3.788% | $2.041M | Allow a new loan subject to account checks |

Base rules combine active, frozen, paused and borrowing flags with nominal variable-debt cap headroom. They are not an execution test. Some issuer-funded currencies need separate facilitator rules; discounts or borrower-specific arrangements can change effective cost.

## Financing history

The historical sample contains 325 market and date observations, including 320 successful stored-rate reads. Each bar represents the quoted annual rate at one dated block. The sample does not measure how long that rate prevailed or the cost paid by a borrower over the month.

## Look through the borrowers

Current debt-token holder pages lead to 350 examined accounts with at least $1 million of dollar debt and enabled ETH-family collateral at T. Account health factors and collateral-use flags are read independently. Other collateral and debt can coexist in the account. The dollars may be invested, spent, idle or used to buy more ETH; this screen alone does not establish carry.

## Read the limits with the numbers

The official address-book asset set is a dated discovery universe, not a full historical delisting registry. Pools and asset views are verified at T.

History is a sample of instantaneous reserve APR, not time-weighted or realized financing.

Current indexed holder discovery can miss an account that exited after T. A four-page limit remains explicit.

The base collateral configuration does not replace eMode, isolation or user configuration. Dollar debt cannot be attributed proportionally to ETH without tracing account funding.

Oracle marks can differ from stablecoin spot prices. No dollar token is assumed exactly one USD.

Physical reserve cash and nominal cap headroom are necessary diagnostics, not verified executable capacity.

## Data and primary references

[Reserve measurements](../../../data/eth/funding_atlas_chapter.json), [reserve CSV](../../../data/eth/funding_atlas_reserves.csv), [monthly rate CSV](../../../data/eth/funding_atlas_history.csv).

[Aave pool configuration](https://aave.com/docs/aave-v3/smart-contracts/pool), [Aave reserve mechanics](https://www.aave.com/docs/aave-v3/concepts/reserve), [official Aave address book](https://github.com/bgd-labs/aave-address-book), [Spark contract documentation](https://docs.spark.fi/dev/deployments/mainnet).
