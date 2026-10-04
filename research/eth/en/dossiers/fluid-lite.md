# Fluid Lite ETH

Snapshot: 2 October 2026, 23:59:59 UTC. This dossier covers the V2 Ethereum product `0xa0d3707c569ff8c87fa923d3823ec5d81c98be78`. The legacy V1 vault `0xc383…` is a separate product. The dollar vault is excluded from ETH product net asset value (NAV).

## What the product is and how it earns income

Fluid Lite combines staking, leveraged lending spreads and liquidity-provider (LP) positions. It can borrow ETH against liquid staking tokens (LSTs), reinvest the borrowed funds and repeat the process. Returns depend on whether reinvestment income exceeds borrowing costs, fees and any losses during an exit.

Current [official risk documentation](https://lite.guides.instadapp.io/information/risks) covers refinancing, forced reductions in leverage and losses from slippage. Historical V1 or V2 launch articles do not establish current fees or strategy settings.

## Identity and share accounting

At T, `asset()` returns stETH. Shares have 18 decimals. `totalAssets()` is approximately 77,364.030578 stETH, supply is 63,315.850950 shares, and `convertToAssets(1e18)` returns approximately 1.2218746083 stETH.

stETH rebases, meaning its token balance increases as staking income accrues. The measured assets-per-share series already includes this growth. Adding staking income to it again would double count the return.

The proxy sends each function call to a module according to the function selector. At T, `getSigsImplementation(getNetAssets.selector)` points to ViewModule `0x9fb2fdc9f64c1fd7aabede5d3f0a5bca9402451f`, whose verified source was reviewed. The DummyImplementation ABI describes the interface; it does not prove which code executes.

## Assets, debt and leverage

`getNetAssets()` reports 600,256.387051 gross assets and 522,808.544153 debt in normalized ETH/stETH units. Net assets after revenue are 77,359.338125, and revenue is 88.504772. The accounting identity `gross−debt−revenue=net` was verified. Contract valuation assumes parity between stETH, eETH and WETH and uses LST conversion rates. It does not capture discounts in secondary markets.

Collateral divided by net equity is approximately 7.7593×. Aggregate debt is 87.1103% of collateral, against a configured maximum of 92%. Neither figure is a health factor (HF) or a promised liquidation threshold.

The resolver reports positions in Aave V3, Spark, Fluid and Lido markets. Some legacy components contain small residual balances. The largest Aave component holds weETH and wstETH collateral against WETH debt. Using several venues still leaves shared exposure to LST backing and ETH liquidity.

## How sensitive the leverage is

With the captured balances held fixed, a one-percentage-point rise in debt APR reduces annual return on net equity by approximately 6.7582 percentage points. A uniform 1% markdown of gross assets reduces resolver net equity by approximately 7.7593%. These isolated scenarios exclude lender-income offsets, rebalancing and transaction costs. They explain why a small change in the spread or asset value can matter at this leverage. [Calculation and assumptions](../RETURN-DRIVERS.md).

## What the return history shows

Historical price per share (PPS) gives a 365-day ETH return of 3.5096% and a 730-day return of 8.8243%. The two-year annualized equivalent is 4.3189%. Excess return over stETH is +3.3368 pp over 730 days, where pp means percentage points.

Liquid ETH leads over the last year; Fluid Lite leads over two years. External KING rewards, points and withdrawal costs are excluded from this comparison.

## Fees, control and how investors exit

At T, `getWithdrawFee(1 stETH)` returns 0.0005 stETH: 0.05%, or 5 bp. Here bp means basis points. `allocationToTeamMultisig()` and maximum allocation both return zero. These results do not establish the scope of other governance permissions.

Current official documentation says the DAO chooses protocols and leverage. Permissioned rebalancers can adjust positions but cannot withdraw user assets. A disclosed team multisig can pause rebalancing and withdrawals. The exact deployed permissions and signing threshold still need a separate contract review. [Control and exit sources](../PRODUCT-TERMS.md).

Applying the checked 5 bp withdrawal fee once to the 365-day book result gives an illustrative return of 3.4578%, before slippage, waiting time and any other route costs. Historical book return already reflects its embedded accounting treatment; the model does not deduct management or performance fees again.

A large withdrawal depends on available ETH liquidity, a successful reduction in leverage, Lido redemption and the fees charged by the chosen route. The published share value alone does not establish how much can be withdrawn immediately.

## What is verified and what remains open

The approximately 4.6925 stETH gap between book `totalAssets` and resolver net assets has not been explained through a separate fee or withdrawal-queue ledger. Historical portfolio composition, an executed withdrawal and complete governance history remain unreconstructed. `getNetAssets` provides stronger evidence than marketing TVL, but still does not independently reconcile NAV at market prices.

Data: `fluid_lite_balance_T.json`, `segment_checks_T.json`, `vault_history_comparison.json`, `vault_history_rpc.json`, raw `fluid_net_module_abi`. Scripts in `tools/eth/`: `segment_checks.py`, `package_metrics.py`, `vault_history_analyze.py`.
