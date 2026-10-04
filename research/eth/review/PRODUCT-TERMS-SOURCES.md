# Product terms, withdrawals and control rights

Official sources reviewed on 4 October 2026, at approximately 10:30 UTC. The financial edition remains frozen at 2 October 2026, 23:59:59 UTC. These fresh observations explain the products; they do not update their balances, rates or returns at T.

The structured ledger is [presentation_terms_sources.json](../../../data/eth/presentation_terms_sources.json). Its TS identifiers record exact supported facts, scope, publication dates where available, short quotations and unresolved items. Publisher documentation is evidence of a disclosed policy, not independent proof that every deployed contract has that configuration.

## What this adds to the research

The existing dossiers explain how the capital works. They need a clearer description of what the holder can actually do, who can change the rules and what remains open. Three distinctions are especially useful for a colleague reading the site:

1. A displayed withdrawal estimate is different from a guaranteed payout date.
2. An upgrade delay is different from a restriction on already-authorised strategy actions.
3. A receipt-token return is different from points, separately distributed rewards, option premiums or the final amount received after exit.

## ether.fi Liquid ETH

The current help centre estimates up to three days for Liquid ETH withdrawals. It explicitly qualifies that estimate by cash availability, queue demand, strategy operations and settlement. It does not promise that a future request will match a past completion. This is stronger and more current evidence than repeating a queue maturity or request deadline as the user's settlement time. [Typical Liquid withdrawal timelines](https://help.ether.fi/en/articles/269720-typical-liquid-withdrawal-timelines), TS01.

The user guide describes selecting the vault, choosing a requested output asset such as wETH or weETH, entering the amount and submitting the request. Processed proceeds are sent automatically, without a separate manual claim in that interface. However, this April guide uses stronger deadline language than the current timelines page. Present the newer estimate, and retain the exact contract findings from T as a separate layer. The guide's wETH example does not prove that wETH is enabled in the particular weETH-only queue checked at T. [Withdrawal guide](https://help.ether.fi/en/articles/284654-how-to-withdraw-from-liquid), TS02.

Veda's architecture explains why an exit has several stages. The queue takes shares, waits for maturity and allows a solver to supply the requested underlying in exchange for them. Asset-specific maturity, solver deadline and discount are configurable. The framework also describes cancellation of an unfulfilled request, but that property must be checked against the exact Liquid ETH queue before the site offers it as a confirmed user right. [Veda Core Components](https://docs.veda.tech/architecture-and-flow-of-funds/core-components), TS05.

The same source explains the control structure. The Manager verifies permitted contracts, functions and parameters using per-strategist Merkle trees. The Accountant receives off-chain rates subject to frequency and deviation limits. This describes how execution is bounded, but does not identify every actor who can change the bounds, permissions or rates. The 24-hour timelock verified at T applies to the authority owner. It must not be presented as a universal delay on fee changes, price publication, pauses or already-authorised strategy execution. Those permissions need the separate fixed-block capability reconstruction, rather than a generic governance label.

The general legal terms incorporate Veda's separate terms and reserve price-plan changes. They also disclaim fiduciary obligations. Points are a licence rather than a contractual currency claim. These facts support keeping points separate from cash returns and avoiding a claim that the ether.fi interface itself guarantees redemption. This is a summary of the publisher's terms, not a legal opinion on their enforceability. [Terms of Use](https://www.ether.fi/legal/terms-of-use), TS04.

The help guide says Liquid is unavailable to users in the United States, Canada and the United Kingdom. This is an access condition, not a reason to exclude the product's assets from a market map. [How Liquid works](https://help.ether.fi/en/articles/517109-how-liquid-works), TS03.

## Fluid Lite ETH

The official user guide describes a direct withdrawal through the deposited vault, in ETH/stETH, and discloses a 0.05% exit fee paid to the DAO. That matches the five-basis-point contract observation at T. The guide's instant language needs to sit beside its documented pause and unwind conditions. [Getting started](https://lite.guides.instadapp.io/getting-started/getting-started-with-fluid-lite), TS06.

The risk page makes the operator hierarchy unusually clear. DAO governance sets leverage ranges and decides which protocols the vault can use. Governance appoints rebalancers to leverage or refinance within those limits. The page says rebalancers cannot withdraw vault funds. The team multisig can reduce protocol ratios, temporarily pause withdrawals and pause rebalancing; the disclosed address is `0xa8c31E39e40E6765BEdBd83D92D6AA0B33f1CCC5`. The publisher says this multisig cannot withdraw or move vault funds. [Risks](https://lite.guides.instadapp.io/information/risks), TS07.

Those are useful disclosed permissions, but they are not a completed access-control audit. The current Safe owners and threshold, governance timelock, module-upgrade authority and fee-setting functions still need independent mapping. The page also explains that automation can refinance or sell collateral to repay debt, with slippage losses. That is the practical link between an apparently smooth share-price series and an expensive stress exit.

## Treehouse tETH

The currently opened redemption page defines the Curve band as zero to 50 wstETH. Within it, the dApp can use the tETH/wstETH pool. Above it, normal redemption burns tETH and leads to a wstETH claim after approximately seven days. It charges five basis points and adjusts the payout using the lower share exchange rate and a minimum/maximum underlying conversion ratio at initiation and finalisation. The front-end amount is an estimate. The process may require LST redemption and debt repayment before the claim is funded. [Redemption Process](https://docs.treehouse.finance/protocol/tasset/architecture/redemption-process), TS08.

The current fee and redemption pages agree on a 0.5% Fastlane fee. Fastlane is capacity limited. The fee page says Pendle YT-tETH and LP-tETH redemptions are automatically routed through this service. The performance policy is 20% of positive Market Effective Yield, collected before the profit/loss rebase; it is not automatically 20% of all staking income. [Fees](https://docs.treehouse.finance/protocol/tasset/architecture/fees), TS09.

Search results still contain older versions with a 200 wstETH band and 2% Fastlane fee. Use the opened current pages, not the search snippets. The numerical redemption example also mixes 200 tETH in the narrative with 50 in the formula and inconsistent subtraction. Retain the symbolic formula and do not reproduce its worked result.

Treehouse describes a five-day timelock for critical governance changes, including upgrades and fee changes. Actual proposer, executor, canceller, proxy-admin and pause permissions remain unverified here. A useful analytical observation is that the advertised five-day notice is shorter than the approximate seven-day normal exit. A notice window alone does not guarantee that redemption completes before a change. [Timelock](https://docs.treehouse.finance/protocol/tasset/security/timelock), TS10.

The insurance-fund description is also worth clarifying. It describes support for peg operations and some rebalancing shortfalls, while risk-event coverage is potential and subject to protocol decisions. Treat it as a support mechanism whose assets and rules need checking, not a blanket insurance promise. [Safety Mechanisms](https://docs.treehouse.finance/protocol/tasset/architecture/safety-mechanisms), TS11.

## CIAN rsETH Yield Layer

The general guide describes a signed withdrawal request that transfers receipt tokens, followed by an estimated payout in about five days. It also links recursive restaking to the exact Ethereum rsETH vault used in our dossier. The estimate is general Yield Layer policy; it does not establish an unconditional five-day rsETH-to-ETH exit. [Core Concepts](https://docs.cian.app/yieldlayer/for-users-quick-start/core-concepts-and-yield-layer-page-overview), TS12.

The fee policy is 8% of profits, already included in displayed Net APY, plus a one-off 0.02% exit fee retained by the vault. Keep it described as policy. The API schema distinguishes the initial exit fee from `fee_info.exit_override`, documented as the actual contract fee. A product-specific getter or current configuration is needed before presenting 0.02% as an independently verified deployed rate. [Fees](https://docs.cian.app/yieldlayer/for-users-quick-start/fees), TS13; [Tech Docs](https://docs.cian.app/yieldlayer/for-builders-developer-documentation/cian-yield-layer-tech-docs), TS14.

The API documentation provides another useful accounting distinction: `tvl_usd` includes leverage, while `net_tvl_usd` represents user-deposited TVL. APY separates receipt-price income, estimated points and ecosystem income; its documented breakdown excludes CIAN points. This explains why a headline yield or gross TVL can differ from our matched-window PPS return and net capital. The documentation's sample balances are examples, so none were imported into T.

CIAN describes multisig allocation, time-locked allocation parameters and a RedeemOperator that processes requests in batches. Its examples mainly describe the stETH deployment. Do not transfer that complete control model to rsETH without checking its implementation and roles. The linked GitHub technical document returned 404. Exact rsETH upgrade, pause and fee-setting actors, threshold and delay remain open. [Architecture](https://docs.cian.app/yieldlayer/for-users-quick-start/yield-layer-value-proposition), TS15.

## Concrete ETH products

Concrete's current catalogue still identifies the WeETH Vault as permissioned, with private APY and Concrete as curator. It defines total volume as deposits, transfers and withdrawals, which reinforces why cumulative volume cannot be called current capital. No current dollar values were used to update the frozen edition. [Earn catalogue](https://app.concrete.xyz/earn), TS18.

The general terms, effective 29 September 2026, identify Concrete Network Services Ltd in the British Virgin Islands as the entity for app, vault and strategy services. They incorporate product-specific vault terms, including potential locks, unbonding, cooldowns and gates. Concrete can deprecate a vault and set a claim window; a missed window can lead to migration, reward forfeiture and costs. [Terms of Use](https://concrete.xyz/terms), TS16.

The separate disclosure says executed agreements or product-specific disclosures control over conflicting website statements. For these permissioned products, the definitive agreement and beneficial-holder rights are therefore material evidence, not optional background. Publicly available documents did not establish the exact fee schedule or contractual redemption rights of ctDeltaWeETH and ctwstETH Plus. Keep those gaps visible beside the seven-day UI observation already captured in the original research. [Disclaimers](https://concrete.xyz/disclaimers), TS17.

Concrete hosts a Halborn assessment of a multisig and queued ERC4626 system. It explains that a queue-mode maximum redemption can burn the user's full shares while payment remains queued and subject to fees. However, the two dossier products execute different AsyncVault implementations; equivalence to the audited ConcreteMultiStrategyVault was not established. Use this assessment only as contextual code evidence, not proof of an active bug or exact withdrawal behaviour in either ETH product. [Assessment](https://docs.concrete.xyz/assets/files/Upgradable-Multisig-and-Queue-Changes-140d08a81b2b4164f47d38a3227ebae9.pdf/), TS19.

## A missing strategy family: selling ETH options

Ribbon's ETH Theta documentation supplies a clear historical example. The vault posts ETH collateral, sells calls to option buyers and collects ETH premiums. When a call finishes in the money, settlement returns less ETH collateral. The premium is payment for bearing the option obligation, rather than staking income or a risk-free lending spread. [Theta architecture](https://docs.ribbon.finance/theta-vault/ribbon-v2), TS20.

This example has a particularly useful measurement lesson. Ribbon's documented projected APY averages four annualised weekly observations but excludes in-the-money weeks. That statistic cannot replace full realised ETH wealth across a matched window. The FAQ also says the strategy is not delta neutral. [Trading and options](https://docs.ribbon.finance/faq/dov-trading-and-options), TS21.

The withdrawal guide describes weekly queued exits, continued exposure to that week's gain or loss and no cancellation of a queued request. LST vaults return their collateral token rather than native ETH. Current activity, deployed fees and T capital were not verified, so this should be presented as a documented strategy example with no market-size contribution. [Withdrawal guide](https://docs.ribbon.finance/theta-vault/user-guides/how-to-withdraw), TS22.

## Integration guidance

Add an exit-and-control comparison alongside the existing product comparison, using plain labels such as requested asset, estimated wait, exit fee, manager powers and verification status. Link each row to the relevant primary source and dossier. Put the date of these document observations in the table caption.

Keep the financial chart dated at T. Mark governance descriptions as published policy unless the corresponding deployed state has been checked. Explain that a receipt, a queue request and ETH in the holder's wallet are different stages of the same exit. This gives colleagues a usable comparison without obscuring the unfinished work.
