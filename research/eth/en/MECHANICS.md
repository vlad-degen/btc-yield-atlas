# Where ETH yield comes from and how carry works

Published 3 October 2026. The formulas below explain strategy economics; they are not promised returns. Contract values refer to T: 2 October 2026, 23:59:59 UTC. Documentation terms may describe the current product rather than its settings at T.

## Start with the currency investors receive

An ETH product's return measures ETH per share. A rise in ETH/USD is a gain in dollar value, not income earned by the strategy. For a dollar product, convert the return as follows:

`1 + R_ETH = (1 + R_USD) × P_ETH_start / P_ETH_end`.

If a dollar portfolio earns 5% while ETH appreciates 30%, its return measured in ETH is −19.23%. Comparing sUSDe with an ETH vault's dollar carry strategy on annual percentage yield (APY) alone misses this difference. The former holds dollar exposure. The latter can keep ETH collateral while investing borrowed dollars separately.

Published price per share (PPS) is also different from the proceeds of a withdrawal. Exit fees, slippage, debt repayment, bridge costs and waiting time can change the amount received. Rewards paid outside PPS need separate accounting. Unredeemed points contribute zero realized cash income.

## E1 and E2: staking and restaking

Staking income comes from Ethereum consensus issuance and from execution users through tips and maximal extractable value (MEV). Validator expenses, provider fees, downtime and penalties reduce the holder's return. These are the E1 economics.

stETH distributes income through a rebasing balance: the number of tokens grows. wstETH instead increases the amount of stETH represented by each share. Counting both rebase growth and wrapper conversion growth would count the same return twice. weETH uses the verified `getRate`; rewards paid separately need not appear in that rate. See the [Lido wstETH documentation](https://docs.lido.fi/contracts/wsteth/).

Restaking, classified as E2, adds obligations to secure external services. Additional economic income requires a payment from an actively validated service (AVS) or its customer. Recording the same ETH under EigenCloud and a liquid restaking token (LRT) provider creates neither new income nor new capital.

Analysis must establish slashing conditions, the recipients entitled to rewards and exit timing. Adding Lido, EigenCloud, Kelp, Aave and downstream vault balances can count the same underlying backing repeatedly.

## E3: borrowing ETH to amplify the staking spread

An ETH loop deposits a liquid staking token (LST), borrows ETH/WETH, buys or mints more LST, and adds it as collateral. A flash loan can complete several steps in one transaction without changing the final assets and debt.

In ETH units, define collateral C, debt D, equity E=C−D and leverage L=C/E. With staking rate s and ETH borrowing rate b:

`r_equity ≈ L × s − (L−1) × b − fees − execution costs`.

For example, L=5, s=2.5% and b=2% give 4.5% before costs. At b=3%, the return falls to 0.5%. Earning positive staking income does not guarantee a profitable loop. Without extra rewards, the break-even borrowing rate is `b* = (L × s − fees − costs)/(L−1)`.

Liquid ETH's main Aave account has L=13.3245 at T. A +1 pp increase in borrowing rates reduces annual return on that account's equity by approximately 12.3245 pp, with positions and other rates fixed. pp means percentage points. The isolated cost is approximately 2.3136 pp when measured against whole-vault net asset value (NAV).

Neither calculation forecasts portfolio performance. Supply rates, rewards and rebalancing can change alongside borrowing rates.

### What can force a loop to unwind

An ETH/USD decline usually reprices LST collateral and ETH debt together. The remaining risks include a fall in LST value relative to ETH, changes to the oracle or liquidation threshold (LT), growing debt interest, and insufficient ETH liquidity for repayment.

Health factor (HF) measures collateral coverage under the lending protocol's liquidation rules:

`HF = oracle_collateral × LT / oracle_debt`.

With debt and LT fixed, the collateral-oracle reduction that reaches liquidation is `1−1/HF`. This is an oracle threshold. A discount in a decentralized exchange (DEX) can first make an unwind more expensive while a redemption-rate oracle keeps HF unchanged. Verified deployed source shows that, at T, Aave's weETH oracle reads a capped `getRate`.

## E4: borrowing dollars against ETH and investing the spread

An ETH-collateral carry strategy deposits ETH or an LST, borrows USDC/RLUSD/PYUSD, invests in a dollar strategy, and converts net profit into ETH accounting. Final income payers can be traders, Morpho borrowers, Cap operators or borrowers outside DeFi.

Two conditions must hold. The dollar investment must earn more than the borrowing cost, and the ETH collateral must remain sufficient until the dollars return. A market-neutral dollar investment can sit inside an account whose collateral is still subject to liquidation.

For initial collateral C_ETH, ETH price P, dollar loan B_USD, destination yield y, borrowing rate b and deployed fraction u, additional ETH income is approximately:

`profit_ETH ≈ B_USD × (u × y − b − costs_USD_per_debt) / P_conversion`.

If the dollar investment still holds its principal, include that asset alongside the dollar debt. Collateral-account equity C×P−B differs from whole-strategy equity, which also owns the invested principal. Account leverage and product leverage therefore need separate reporting.

### A simple carry example

Take $100 of ETH collateral and $60 of dollar debt, fully invested. With y=6%, b=4% and costs=0.5% of debt, the strategy earns $0.90 annually. That is 0.9% of initial collateral if ETH's price is unchanged.

If only 60% of the borrowed funds is deployed, the spread turns negative: 0.6×6%−4%−0.5%=−0.9% of debt. Idle borrowed cash still incurs funding costs.

Capacity depends on the smallest of the collateral cap, available loans, destination limits, redemption liquidity and manager limits. Growth can raise borrowing rates and reduce destination yield. Today's APY cannot be scaled to unlimited capital.

### What is verified in Liquid ETH

Verified paths include weETH/RLUSD debt with senRLUSDv2 investments, and PRIME/PYUSD debt with senPYUSDPRIMEv2 investments. RLUSD allocates approximately 52.89% to kBTC/RLUSD and 24.09% to weETH/RLUSD. These positions add BTC and ETH collateral credit risk. They do not establish direct long BTC ownership by the ETH vault.

## E9: spot ETH plus a short derivative

Another use of the term carry is holding ETH or an LST while taking an equal-delta short derivative. Delta describes sensitivity to market price changes. The hedge mainly preserves dollar value rather than ETH upside. For a linear short perpetual, approximate economics are:

`r_USD ≈ staking_income + short_funding − financing − trading − custody − hedge_tracking_cost`.

Positive funding pays the short holder; negative funding requires the short holder to pay. A dated futures contract can capture the difference between spot and futures prices at entry if it is held and settled. Neither funding nor basis is a guaranteed fixed yield or simply a return on collateral.

[Ethena's basis mechanism](https://docs.ethena.fi/backing-assets/crypto-basis-trade) uses these hedges. Its [protocol revenue](https://docs.ethena.fi/backing-assets/protocol-revenue) also includes lending, real-world assets (RWA) and liquid-stablecoin income. All USDe cannot be assigned to the ETH basis strategy.

The 3 October dashboard shows approximately $374.44M in ETH positions within $928.89M of crypto basis. This is a disclosure after T, not a custody audit.

A delta-neutral position can still need margin at a trading venue. Spot gains and short losses may sit with different counterparties, and transfers can fail to arrive in time. Off-exchange custody adds settlement, legal, venue-liquidity and operational dependencies. [Funding risk documentation](https://docs.ethena.fi/protocol-overview/risks/funding-risk) covers negative funding and allocation changes. Historical averages are not forecasts.

## E5: lending

Lending earns borrower interest after protocol reserve or curator fees and credit losses. An ETH supplier and a borrower posting ETH collateral play different economic roles.

Compare lending returns with the same staking benchmark and in the same unit. Do not add staking income separately if it is already captured by the asset's denomination. Idle lending liquidity can earn almost nothing, as the JustLend figures illustrate.

## E6: fixed yield through principal tokens

A principal token (PT) is bought below the value of a specified redemption unit at maturity. With price p and d days remaining, `APY_implied ≈ (1/p)^(365/d)−1` applies only if the payout is one of that unit.

Pendle PT-wstETH uses stETH accounting. Substituting one wstETH or one ETH without conversion would change the claim. Standardized yield (SY), PT and yield tokens (YT) divide one underlying position rather than create separate deposits.

PT principal remains claimable after maturity, while YT stops accruing future yield. An early sale depends on market depth. See the [primary PT mechanics](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT).

## E7: liquidity provision

A liquidity provider (LP) earns trading fees and incentives while the position's token inventory changes. ETH/stablecoin pools retain directional exposure and impermanent loss, meaning performance can differ from simply holding the deposited tokens.

An LST/ETH pair reduces the currency mismatch but still carries the risk of a receipt-token discount and of leaving the active price range. Concentrated positions outside their range stop earning fees. Fluid's imaginary reserves support pricing; they do not represent additional assets. Principal, unclaimed fees and debt must be measured separately.

## E8: selling options

An option premium pays the seller for accepting a specified payoff. A covered call limits upside; a short put accepts downside. The premium alone is not risk-free yield.

An ETH return comparison needs the full payoff and the collateral consumed, rather than just the premium received. Aggregate market size remains unverified without a contract catalogue.

## Stress scenarios to apply to every product

| Shock | Recalculate | Why APY is insufficient |
|---|---|---|
| Rewards/points off | Base income − debt − fees | Subsidized spreads can vanish |
| Borrow rate +1/+3 pp | Debt service and supply-income response | Leverage amplifies small rate gaps |
| LST market discount 1/3/5% | Executable unwind NAV | Oracle and DEX can diverge |
| Oracle markdown/LT change | HF and liquidatable amount | Oracle price differs from DEX |
| ETH/USD −20/−40% | Stable-debt collateral HF | Dollar neutrality does not protect ETH collateral |
| Credit loss 1/5/10% | Underlying claim and equity | Dollar principal can be impaired |
| Negative funding 7/30/90 days | Margin, reserves and hedge carry | Annual averages hide cash gaps |
| Queue/bridge delay | Time to debt repayment and ETH payout | Solvency does not establish liquidity |
| Mass withdrawal | Liquidity by debt asset | Total dollar liquidity cannot replace required ETH/RLUSD |

Model sensitivities are retained in `data/eth/stress_scenarios.json`. Full executable DEX, liquidation and queue stress remains open. Arithmetic with fixed balances does not replace an execution simulation.
