# Economics, capacity and stress tests

Financial snapshot T: 2 October 2026, 23:59:59 UTC. The original data capture was completed on 3 October 2026; the presentation review includes documentation checked on 4 October 2026. The tables below distinguish verified contract state from modelled sensitivities. Full exit execution has not yet been simulated.

## ETH loops: a small spread amplified by leverage

The model annualizes trailing-30-day staking log return as an annual percentage rate (APR), then adds the supply interest earned on collateral. For WETH debt, it uses the variable borrow APR at T. These inputs cover different windows, so the result explains the position's economics rather than forecasting a return or measuring its realised historical profit. Rewards, management and performance fees, and execution costs are excluded. In the table, L means gross collateral divided by investor equity after debt.

| Account | L | Staking + supply APR proxy | WETH borrow APR at T | Model return on equity | Borrow uplift to zero return | Uplift eliminating loop excess |
|---|---:|---:|---:|---:|---:|---:|
| aave | 13.325 | 2.328% | 2.074% | 5.455% | 44.3 bp | 25.4 bp |
| spark | 9.762 | 2.248% | 1.907% | 5.232% | 59.7 bp | 34.1 bp |

Positive staking income is not enough to make a loop profitable. A small increase in borrowing cost can erase the spread that leverage amplifies. These thresholds apply to the stated inputs. In practice, staking returns, supply interest, market utilization and position size can also change. A basis point (bp) is one hundredth of a percentage point.

## A worked example with 100 ETH

Using the main Aave account's captured parameters, 100 ETH of net equity supports approximately 1,332.453 ETH of gross collateral and 1,232.453 ETH of WETH debt. At the displayed proxy rates, annual asset income is about 31.014 ETH and debt interest about 25.559 ETH. The difference is 5.455 ETH, before management fees, rewards and execution costs. This scales the isolated account model; it does not estimate Liquid ETH's whole-portfolio return.

For a hypothetical dollar-carry example, post 100 ETH, borrow dollars worth 50 ETH and keep the ETH price constant. Staking at 2.3% earns 2.3 ETH. A 5% destination return earns 2.5 ETH equivalent while a 4% borrowing rate costs 2 ETH equivalent. The gross result is 2.8 ETH. A 10% performance fee on that positive result costs 0.28 ETH; a 0.35% equity-based management cost takes another 0.35 ETH, leaving 2.17 ETH. These are illustrative assumptions, not a reconstruction of the product's realized carry income or fee convention.

The website lets readers change each input and see the corresponding cash-flow example. Dollar-neutral spot/short basis is shown separately in dollars because its exposure differs from an ETH-long investor's.

## Rate shocks with fixed equity

| Account | +25 bp | +50 bp | +100 bp | +300 bp |
|---|---:|---:|---:|---:|
| aave | 2.374% | -0.707% | -6.870% | -31.519% |
| spark | 3.042% | 0.852% | -3.529% | -21.052% |

For the main Aave account, a +100 bp borrowing-rate shock produces a −12.3245 pp change in annual return on its equity. The corresponding change is approximately −2.3136 pp on Liquid ETH's book net asset value (NAV), before offsets elsewhere in the portfolio. This is an isolated debt-cost shock. Combining it with changes in lending income requires a complete view of which assets and liabilities belong to the same investor.

## Available debt asset and unwind

| Account | Main WETH debt | WETH reserve cash | Cash / debt |
|---|---:|---:|---:|
| aave | 410,134.20 | 269,693.45 | 65.76% |
| spark | 31,042.02 | 116,147.84 | 374.16% |

The Aave reserve has less cash than the main loop owes in WETH. Its observed cash therefore limits a single flash loan from that reserve funding the entire repayment. It does not prove that the position cannot exit: other lenders, the vault's own liquidity, collateral redemption and staged repayments remain possible. Spark cash exceeds this account's debt, although eligibility, caps and the actual route have not been simulated.

The rate decoder uses the 15-word legacy getReserveData layout. Cash is measured with WETH `balanceOf(aTokenAddress)` at the same fixed block, and debt comes from the corresponding variableDebt token. Cash alone is not the maximum executable withdrawal or flash loan: pause status, reserve rules and the transaction route also matter.

## Oracle, market discounts and stablecoin debt

| Account | HF at T | Isolated oracle markdown to HF=1 | Borrow +100 bp: equity-return change |
|---|---:|---:|---:|
| main_aave | 1.02708 | 2.637% | -12.325 pp |
| main_spark | 1.03615 | 3.488% | -8.762 pp |
| drone_aave | 1.39045 | 28.081% | -1.355 pp |
| drone_spark | 1.87192 | 46.579% | -0.814 pp |

Health factor (HF) measures collateral value relative to the liquidation boundary. With ETH-denominated debt, an oracle markdown of the liquid staking token (LST) relative to ETH matters more than ETH/USD direction alone. With stablecoin debt, an ETH/USD decline reduces collateral value against dollar debt. Holding debt and the liquidation threshold (LT) fixed, Drone Aave retains HF approximately 1.112 after a −20% collateral shock; at −40%, HF is approximately 0.834. These are arithmetic sensitivities, without liquidation quotes or rebalancing.

A decentralised exchange (DEX) discount can lower the amount recovered during an exit even when the lending oracle does not move. Aave's weETH CAPO, a capped conversion-price oracle, need not follow that discount. In a principal-only estimate, a 1% markdown of all collateral reduces account equity by approximately L%. Smart collateral and liquidity-provider (LP) positions need a separate recalculation of reserves and active price ranges.

## Carry: credit risk and linked cash flows

Losses in a dollar strategy affect an ETH product through the claim it owns and the conversion back to ETH. The 8.709M RLUSD and 4.759M PYUSD self-credit diagnostics show where a group's borrowing is linked to its owned lending portfolio. These amounts are neither available cash nor extra assets. Nested curator fees of 10%/15% can still apply when part of the borrower's interest returns to the same investor.

Verified PRIME/PYUSD utilization is approximately 91.8%, and weETH/RLUSD utilization is approximately 88.3%. Much of the supplied capital is therefore lent out rather than immediately available for withdrawal. Recovering collateral linked to off-chain credit is another process and does not provide instant ETH liquidity.

## Capacity: what remains unestablished

Protocol TVL does not measure how much additional capital a strategy can absorb. An ETH loop (E3) depends on LST trading and redemption liquidity, ETH borrowing liquidity, protocol caps, HF and the drawdown the investor can tolerate. Dollar carry against ETH collateral (E4) also depends on dollar borrowing capacity, destination limits, credit terms and redemption time. Spot/short basis (E9) adds the available hedge positions, funding behaviour, venue margin and custody limits. The [mechanics guide](MECHANICS.md) explains these income sources, and [product terms](PRODUCT-TERMS.md) shows the corresponding exit conditions.

Full stress execution remains open. The missing evidence includes executable DEX quotes at archive blocks, flash-loan eligibility, redemption throughput, liquidation transactions, bridge settlement and 7/30/90-day interest-rate and funding paths. These tables keep the model assumptions visible; they do not replace transaction checks. The [return-driver review](RETURN-DRIVERS.md) separates these current sensitivities from historical returns. Data: `loop_economics_T.json`, `lending_reserve_T.json`, `stress_scenarios.json`.
