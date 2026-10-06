# Coverage of the ETH yield market

Financial snapshot: **2 October 2026**. This is a family-by-family map of measured evidence, not a claim that every wallet, private strategy or protocol is fully reconstructed.

## Capital, history and investor returns

| Family | Income mechanism | Capital evidence | History evidence | Return evidence |
| --- | --- | --- | --- | --- |
| Native validator staking | Consensus issuance, tips and MEV | No exact all-validator balance at T | No full market history | Issuer benchmarks only |
| Liquid staking / restaking | Validator income; additional service rewards where realised | Issuer and security-layer claims; overlapping | 24-month protocol observations | Matched share conversions for selected issuers |
| ETH lending | Borrower interest | Lending claims, cash and debt measured separately | Protocol histories; selected reserve histories | Selected rates and share returns |
| ETH-debt loops | Leveraged staking-minus-ETH-funding spread | Fluid / Treehouse parents; Liquid, CIAN and Yearn positions | Selected product books, not monthly loop weights | Selected matched ETH book returns |
| Dollar carry | Dollar investment income minus dollar funding | Eight examined books; five have current traced routes; unassigned sleeves retained | 24 monthly whole-book observations; allocation weights incomplete | Matched 30-day books; three financed investment lots |
| Spot / short basis | Funding or dated-futures premium | Frozen ETH slice unmeasured; later Ethena disclosure separate | No complete frozen ETH-slice history | No matched ETH-long strategy comparison |
| Fixed maturity | Underlying income or principal-claim discount | Pendle / Spectra parent claims; market registries screened | Parent histories; maturity-level coverage partial | Payoff denomination checked; no full investor-return panel |
| DEX / trading liquidity | Swap fees; inventory and trader P&L | 28 verified ETH-custody pools; broader adapters incomplete | 24 month ends for that same pool subset | Custody is not LP profit; selected positions traced |
| Options / structured yield | Option premiums in exchange for contingent payoff | Materiality and funded capacity not established at T | Historical / retired product screens | No full premium, settlement and cash-return ledger |
| Mixed allocators / tranches | A blend of the mechanisms above | Parent books and selected sleeves; never add both as unique capital | Parent NAV; changing allocation weights incomplete | Selected share marks; strategy attribution incomplete |

## Discovery is not strategy attribution

The saved DefiLlama screen contains **299** ETH-name pools above $5M from **86** projects. **287** are joined to an existing parent; the other **12** receive separate dispositions. These are discovery decisions, not 299 independently reconstructed strategies or additive ETH capital. [Individual decisions](CARRY-COVERAGE-AUDIT.md).

## Three boundaries that affect the answer

1. **Capital:** receipt claims, lending collateral, managed shares and underlying custody overlap. Global unique ETH and global carry equity are not measured. Native consensus balances are outside the protocol panel. Four major liquidity adapters lack usable token history at T; the 28-pool custody reconstruction is a separate bounded subset.
2. **History:** categories group protocol families consistently. Their monthly NAV is not a history of strategy allocations or external deposits. A constant cohort controls observation availability, while current discovery can omit dead products.
3. **Income:** matched book returns, financed investment-lot results and complete strategy profit answer different questions. Reward sponsor, earning period, own-credit flows, outer fees and exit cash must be assigned before stating organic carry profit.

## Carry routes and current status

| Product | Status | Attribution boundary |
| --- | --- | --- |
| Concrete Delta weETH | Declared arbitrage; shared custody | Dollar debt is observed in a shared Safe; assets and debt attributable to Delta are unresolved. |
| ether.fi Liquid ETH | Active hybrid | Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled. |
| YieldBasis WETH | Active dollar-financed LP | Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate. |
| Rocksolid rETH | Closing; nested carry | 728.48 ETH of Liquity shares is the evidenced nested carry claim; direct Aave debt is zero. |
| Liquity ETH Carry | Active minted-dollar LP | Ebisu collateral, ebUSD debt and dollar LP positions are measured; do not equate collateral with sleeve equity. |
| Royco ETH | Loan traced; parent marks stale | Morpho PYUSD debt and the senior credit receipt are traced; parent accounting and immediate exit remain restricted. |
| TAU InfiniFi ETH Carry | Historical; dust debt at T | Accrued debt is 0.022132 USDC at T; the old whole book is not current active carry equity. |
| Reservoir ETH Yield | Small current nested savings | Outer dollar borrowing and borrowing inside the savings destination are distinct liabilities. |

Five examined products have current traced routes, including the small Reservoir position and stale-mark Royco. Rocksolid is Closing, TAU's current debt is dust, and Concrete's published arbitrage mandate does not establish a product-attributed sleeve. ZenSats documents active LlamaLend / Curve / StakeDAO and legacy withdraw-only Aave / RAAC designs, with frozen capital unmeasured. [Official strategy documentation](https://www.zensats.app/docs/strategy).

## How to read TVL

DefiLlama separates borrowed balances and flags reused receipt assets. Native validator staking also has a different scope from chain DeFi TVL. Our token panel is a custom ETH-family exposure view, so it must not be labelled as their global TVL or unique market capital. [DefiLlama definitions](https://docs.llama.fi/analysts/data-definitions).

## Supporting research

[Team briefing](BRIEFING.md), [market structure](MARKET-STRUCTURE.md), [carry product evidence](CARRY-PRODUCTS.md), [custody and exits](CAPITAL-INCOME-EXIT.md), [additional product histories](PRODUCT-FINANCIAL-HISTORY.md), [strategy families](STRATEGY-UNIVERSE-EXPANSION.md). Financial observations retain their dates; later documentation does not fill missing values at T.
