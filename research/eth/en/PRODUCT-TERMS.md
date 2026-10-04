# Withdrawals, fees and who controls the vault

An ETH yield product is easier to understand when we follow both the money and the exit. Where does income come from? What asset does the holder receive? Who can change the strategy, valuation or fees while the holder is waiting?

This review separates **contract settings at T, 2 October 2026 at 23:59:59 UTC**, from **published documentation checked on 4 October 2026**. The document review does not update the financial snapshot. An estimated processing time describes the expected route; it is not a guaranteed payout date.

## The five carry products

These are the main website's ranked carry chapters. Contract configuration, a published operating policy and an executed exit remain different evidence.

| Product | Configured fees at T | Exit and valuation evidence | Control evidence at T |
|---|---|---|---|
| Liquid ETH | 0.35% annual NAV fee on the checked Ethereum accountant | Published queue estimate up to 3 days; exit depends on destination redemption, funding and settlement | Authority owner has a 24-hour timelock; a separate role can update the management fee |
| Concrete Delta weETH | Wrapper settings 0% management / 0% performance; private investor fees remain unresolved | A book claim and a public Safe balance do not establish the investor's contractual withdrawal rights | Wrapper owner / VAULT_MANAGER is a 1-of-2 Safe; the shared execution Safe is 3-of-5 |
| Rocksolid rETH | 1% management / 10% performance | Book NAV is rETH-denominated. The executor also owns Liquity shares, adding a nested withdrawal route | Owner and execution address have no contract code at T; the documented 30-day fee-change policy is not a verified wrapper timelock |
| Liquity ETH Carry | 0.5% management / 10% performance | Fixed-block collateral is an Ebisu Trove, with 2.55% annual borrowing APR; liquidity and debt repayment govern an unwind | Ebisu and Uniswap V4 fuses, permitted substrates and governance actors are mapped in the chapter |
| Royco ETH | 0% management / 10% performance; later documentation says zero fees | All three recorded Caliber position categories are stale; wrapper, adapter and machine immediate maxWithdraw are zero. Published exit is a 30-day epoch plus roughly 2 processing days | Owner is a 3-of-4 Safe; fee manager is separate. Caliber instruction-root delay is 2 days, distinct from the documented 7-day allocation notice |

See [fixed-block source records and the complete product review](CARRY-PRODUCTS.md) for exact addresses, contract roles, dates, restrictions and the scope of every finding. Zero immediate maxWithdraw establishes the observed exit limit at that block; it does not prove permanent inability to exit or investor loss.

## Supporting ETH-loop and managed-product comparisons

The following earlier comparison provides additional ETH-loop and operational context. Its five products differ from the ranked carry set above.

| Product | Fees and their evidence | Published exit route, checked 4 October | Control and verification |
|---|---|---|---|
| [ether.fi Liquid ETH](dossiers/etherfi-liquid-eth.md) | Annual management fee was **0.35% at T**. The checked queue allowed a **0 to 10 bp discount** for weETH requests. | The help centre estimates **up to 3 days**, subject to liquidity, queue demand, strategy operations and settlement. The interface can offer a choice of output asset. | The authority owner has a **24-hour timelock**, but management-fee permission also belongs to a separate role holder. Operational permissions therefore need to be assessed individually. |
| [Fluid Lite ETH](dossiers/fluid-lite.md) | **0.05% exit fee**, verified at T and disclosed in the user guide. | The guide describes a direct ETH/stETH withdrawal. Documented pause rights and the liquidity needed to unwind still apply. | The publisher says DAO governance selects protocols and leverage limits; rebalancers operate within those limits. A team multisig can pause withdrawals and rebalancing. Exact deployed permissions remain incompletely mapped. |
| [Treehouse tETH](dossiers/treehouse-teth.md) | Published policy: **20% of positive Market Effective Yield**, **5 bp normal redemption**, **0.5% Fastlane**. | A Curve swap within the published band; normal redemption takes **about 7 days** and pays wstETH; Fastlane has limited capacity. | The publisher describes a **5-day governance timelock** and a governance-controlled redemption band. The actual actor set and emergency exceptions still need contract-level checks. |
| [CIAN rsETH Yield Layer](dossiers/cian-rseth.md) | Published policy: **8% of profits**, already included in Net APY, plus **0.02% exit fee** retained by the vault. The actual contract fee can have an override. | The general Yield Layer guide estimates **about 5 days** after a signed receipt-token withdrawal request. The subsequent rsETH-to-ETH route is separate. | The published architecture uses multisig allocation and batch withdrawal processing. Exact rsETH upgrade, pause, fee-setting and timelock permissions remain open. |
| [Concrete ETH products](dossiers/concrete-eth.md) | The reviewed permissioned products do not provide a public, complete investor fee schedule. | The earlier product-interface capture disclosed **7 days**. Current general terms defer to each product's agreement and allow withdrawal restrictions. | The two products share a Safe verified as **3 of 5 at T**. Holder rights, contractual payout terms and the complete upgrade/parameter authority require separate evidence. |

The fees have different bases. A percentage of profits, a percentage of total assets and a one-off exit charge cannot be compared by their number alone. The [mechanics guide](MECHANICS.md) explains the income sources; the [return history](HISTORY.md) compares wealth over matched periods rather than advertised APY.

## A withdrawal has several stages

Holding a vault share, submitting a withdrawal request and receiving ETH are three different states. A managed strategy may first need to recover assets from another vault, redeem an LST, repay ETH or stablecoin debt, and settle a bridge. If the holder receives weETH, wstETH or rsETH, conversion to native ETH adds another route, with its own timing and market price.

This is why the same product can have a share value, an estimated payout and a different executable sale value. A loan can also require repayment before the underlying collateral is released. Keep the requested output asset next to the exit estimate when comparing products.

## Liquid ETH: a queue estimate and several control layers

ether.fi's current help centre estimates up to three days for ETH Yield and explicitly qualifies the estimate. Its older withdrawal guide says processed proceeds arrive automatically and can offer wETH or weETH. That interface description does not establish that both assets are enabled in the exact queue inspected at T. The checked queue accepted weETH, while its one-hour maturity and minimum three-day request deadline were request settings, not promises of settlement. [Current timelines](https://help.ether.fi/en/articles/269720-typical-liquid-withdrawal-timelines), [withdrawal guide](https://help.ether.fi/en/articles/284654-how-to-withdraw-from-liquid).

Veda's framework uses a solver queue: shares enter the queue, wait for maturity, then a solver supplies the requested asset in exchange for shares. The framework also describes cancellation of unfulfilled requests. Whether that right applies to a particular deployed queue must be checked against its code and configuration. [Veda Core Components](https://docs.veda.tech/architecture-and-flow-of-funds/core-components).

The fixed-block permissions review makes the governance distinction concrete:

| Ethereum function at T | Authorised roles | What the finding means |
|---|---|---|
| Update management fee | Roles 8 and 55 | Role 8 belongs to the authority-owner timelock. Role 55 belongs to a separate address, so the owner's delay is not a universal fee-change delay. |
| Publish exchange rate | Role 11 | Rate publication is permissioned and is not a public function. |
| Pause the Accountant | Roles 5, 9 and 14 | Operational actors can pause; pause authority does not have to pass through the owner. |
| Unpause the Accountant | Roles 5 and 9 | The ability to pause and the ability to resume have different scopes. |
| Change rate-provider configuration | Role 8 | This checked capability belongs to the timelock role. |

The role 55 address at T is `0x607d0c7e3578802eb46d388cb86cfba8ff657306`. The owner timelock is `0xd829f278016b90fec735f9a12bf8b75e06102c89`. Address permissions do not identify their beneficial owners or prove how an external signer system operates. The review covers selected functions and Ethereum authority state; it is not a complete inventory of every strategy permission. [Fixed-block permission evidence](../../../data/eth/permissions_review_T.json).

The service adds a legal layer to these contract controls. ether.fi's terms incorporate Veda's separate terms and reserve changes to pricing. Points are not a contractual cash claim. The help centre also describes geographic access restrictions. These service conditions belong beside the product's technical mechanics, without replacing the on-chain evidence. [Terms of Use](https://www.ether.fi/legal/terms-of-use), [Liquid guide](https://help.ether.fi/en/articles/517109-how-liquid-works).

## Fluid Lite: direct exits depend on unwind conditions

Fluid's guide discloses the five-basis-point exit charge and describes returning ETH/stETH to the wallet after a withdrawal transaction. Its risk page explains how that route can become harder: automation may refinance or sell collateral to repay debt, and a forced deleverage can incur slippage losses. [User guide](https://lite.guides.instadapp.io/getting-started/getting-started-with-fluid-lite), [risk disclosure](https://lite.guides.instadapp.io/information/risks).

The same disclosure assigns protocol selection and leverage limits to DAO governance. Rebalancers work within those limits and are described as unable to withdraw funds. The team multisig, `0xa8c31E39e40E6765BEdBd83D92D6AA0B33f1CCC5`, can reduce a protocol ratio and pause withdrawals or rebalancing. Its current signer threshold, upgrade authority and exact deployed function permissions still need independent verification. Read the instant-exit description together with those conditions.

## Treehouse: the exit price can change during the wait

The currently opened documentation defines the Curve redemption band as zero to 50 wstETH. Larger normal redemptions burn tETH, wait approximately seven days and lead to a wstETH claim. The payout uses rates from both initiation and finalisation, plus a five-basis-point charge. The estimate can therefore fall before the claim is ready. Fastlane costs 0.5% and has limited capacity. [Redemption process](https://docs.treehouse.finance/protocol/tasset/architecture/redemption-process).

The performance fee applies to positive Market Effective Yield. The fee page also says Pendle YT-tETH and LP-tETH redemptions use Fastlane. Search snippets with a 2% Fastlane fee are older than the current opened pages. The redemption page's worked example contains inconsistent inputs, so this research uses the stated formula rather than copying its numerical result. [Fee policy](https://docs.treehouse.finance/protocol/tasset/architecture/fees).

The published five-day timelock is shorter than the approximate seven-day normal exit. That comparison does not prove a harmful change, but it shows why notice alone cannot guarantee a completed exit before execution. The described insurance fund can support selected shortfalls and peg operations; risk-event compensation remains conditional. [Timelock](https://docs.treehouse.finance/protocol/tasset/security/timelock), [support mechanisms](https://docs.treehouse.finance/protocol/tasset/architecture/safety-mechanisms).

## CIAN: distinguish policy fees, overrides and points

CIAN's general guide estimates five days after a withdrawal request. Its published performance fee is already reflected in Net APY, so subtracting the same 8% again would understate a displayed net rate. The one-off exit policy is 0.02% of NAV, retained by the vault. [Withdrawal overview](https://docs.cian.app/yieldlayer/for-users-quick-start/core-concepts-and-yield-layer-page-overview), [fees](https://docs.cian.app/yieldlayer/for-users-quick-start/fees).

The API documentation provides an important qualification: `fee_info.exit_override` is the actual contract fee, while `fee_info.exit` is the initial policy rate. A generic fee page is therefore insufficient to establish the deployed rsETH exit fee at every date. The schema also separates leveraged TVL from user-deposited TVL, and receipt-price income from estimated points and ecosystem income. These differences matter when reconciling a headline APY with the historical share-price return. [API definitions](https://docs.cian.app/yieldlayer/for-builders-developer-documentation/cian-yield-layer-tech-docs).

The disclosed architecture uses multisig allocation and a RedeemOperator for batch exits. Its examples mainly describe stETH. The rsETH product still needs its own complete control map and reward-ownership reconciliation. [Architecture](https://docs.cian.app/yieldlayer/for-users-quick-start/yield-layer-value-proposition).

## Concrete: product agreements are part of the evidence

Concrete's WeETH product is permissioned and its APY is private. Current general terms incorporate product-specific agreements, including possible lockups, cooldowns and gates. They also describe vault deprecation with a designated withdrawal period. An executed agreement or product-specific disclosure takes precedence over conflicting website information. [Catalogue](https://app.concrete.xyz/earn), [terms](https://concrete.xyz/terms), [disclosures](https://concrete.xyz/disclaimers).

For these products, the remaining question is who holds the economic claim and what agreement governs its payout. The public Safe threshold answers a control question; it does not answer the contractual one. A seven-day interface description alone cannot resolve fee terms, priority of payment or beneficial ownership. Generic Concrete queue audits also cannot establish the behaviour of the two AsyncVault implementations without matching the reviewed code to them.

## Historical example: selling ETH calls

ETH yield also includes payment for taking option risk. Ribbon's documented ETH Theta strategy posts ETH collateral, sells calls to option buyers and receives ETH premiums. If a call finishes in the money, settlement returns less ETH collateral. The holder receives a premium while giving up part of the ETH upside and bearing the option obligation. [Ribbon architecture](https://docs.ribbon.finance/theta-vault/ribbon-v2).

Ribbon's documented projected APY excludes in-the-money weeks. It is therefore not a full realised-return measure. The strategy is also explicitly described as non-neutral to market direction. Queued exits remain exposed to that week's outcome, and LST vaults return their collateral token. [APY and settlement definitions](https://docs.ribbon.finance/faq/dov-trading-and-options), [withdrawal process](https://docs.ribbon.finance/theta-vault/user-guides/how-to-withdraw).

This is a historical strategy example. Current operational status, T capital and deployed fees were not verified, so it contributes no amount to the market totals. Its role here is to show why option premiums should be assessed through total ETH wealth, settlement losses and exit conditions rather than premium APY alone. The [benchmark methodology](HISTORY.md) and [economics guide](ECONOMICS.md) apply the same measurement principle to the other strategies.

## What remains to verify

The next evidence that would change the comparison is specific: executed exit routes under material withdrawal sizes, actual fee overrides, complete signer and upgrade permissions, definitive Concrete holder agreements, and the ownership of separately distributed rewards. Until those are available, published policies and contract observations retain their own labels.

The 22-source supporting terms review, its dates and limitations are recorded in the [source ledger](../../../data/eth/presentation_terms_sources.json). Primary sources for the ranked carry products are linked separately in the [five carry-product review](CARRY-PRODUCTS.md).
