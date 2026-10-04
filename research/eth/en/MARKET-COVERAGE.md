# ETH yield market: coverage and what the numbers mean

The report follows the Bitcoin Research sequence: market size and history, category composition, carry mechanics, large products, wider borrowing, risks, product implications and evidence. This edition broadens the ETH investigation with actual lending deployments, historical nested financing and traced credit-to-yield transactions.

Financial balances remain fixed at 2 October 2026, 23:59:59 UTC. Registry discovery and source review are dated separately. A later product catalogue or yield quote does not replace a fixed-block balance.

## The economically meaningful strategy set

ETH yield begins with validator revenue. Lending, dollar credit, liquidity provision, option premiums and hedge funding add other payers. Restaking adds security-service claims and possible rewards. Points require a separate valuation assumption. A custody wrapper or aggregator can package an existing source without creating a new payer.

The research distinguishes eight broad mechanism groups below. A product can combine several, so a product name is not an exclusive category and its whole book cannot be assigned to one sleeve without position evidence.

| Mechanism group | Evidence in this report | Remaining measurement limits |
|---|---|---|
| Staking and restaking | 24-month adapter balances, issuer conversions, validator/restaking payer and dependency maps; selected additional issuer contracts at T. | Full native consensus state, issuer consolidation, every AVS payment and liquid exit depth. |
| ETH lending and debt loops | Fixed-block reserve economics, major product account leverage, matched share-return benchmarks, StakeWise Boost mechanism and additional automated vaults. | Complete borrower population and realized spread for every major automated account. |
| ETH collateral to dollar carry | 60 Aave/Spark dollar reserves on 12 chains, 131 additional credit rows, five deep carry books, five extra product cases and historical loan layers. | Account-level allocation across all venues, Concrete private/shared custody, confidential ownership and complete product-specific external cash flows. |
| Fixed maturity and yield trading | Official Ethereum Pendle registry: 494 markets, 117 ETH-tagged, 4 active/unexpired at dated discovery; accounting units and overlap checked. | Cross-chain historical pool consolidation, expired instruments, all early-exit execution costs, and exact Spectra sleeve identity. |
| Liquidity provision | Broad chain/pool discovery, bounded ETH-side history, ETH/ETH and ETH/USD mechanics, GMX trader-P&L payer, YieldBasis and automated LP receipt overlap. | Full token-side LP capital, 24-month direct protocol reconciliation and total investor returns after inventory changes. |
| Options and structured products | Historical Ribbon capacity, current Thetanuts contracts, call/put mechanics, premium payer, settlement currency and capped upside. | Materiality at T for every active options vault, completed premium/expiry ledgers and payout histories. |
| Basis and market-neutral managers | Ethena ETH hedge mechanism, mixed USD revenue, margin/custody dependencies, Midas token supply, issuer marks, contracts and stale-price ages at T. | ETH-only hedge/notional and yield attribution, off-chain manager inventory, complete fees and realized payouts. |
| Rewards, recovery and custody wrappers | Paid incentives separated from points; paused Yearn yETH/Resolv cases separated from active products; exchange/fund wrappers mapped to existing validator backing. | Complete paid reward histories, recovery outcomes, private custody balances and all institutional wrappers. |

## What now changes the carry conclusion

The funding atlas has 60 dollar reserves and 57 ETH-family reserve views across 15 measured Aave/Spark instances on 12 chains. It records 320 successful dated annual-rate observations. These observations are instantaneous APR, not monthly average borrowing costs.

At the snapshot, Aave Ethereum USDC costs 13.93% APR and USDT 4.38%. Their physical reserve cash is about $6.33 million and $183.29 million. A carry comparison that considers only the chain or only USDC misses a material financing decision. Restrictions, conversion costs, issuer risks and account eligibility still determine whether a cheaper route can actually be used.

The Compound/Euler/Fluid expansion adds 131 deployed market rows. The 31 simple Fluid ETH-only collateral pairs hold 76.703 million nominal dollar-token units of debt. Compound and Euler loan-vault totals accept other collateral, so those totals cannot be added to an ETH-only debt subtotal.

Reservoir proves why nested funding needs two separate loan tests. At the October 2025 checkpoint, its book was about $15.91 million, its outer Aave account owed about $10.35 million and its srUSD-collateralized Morpho position owed about 90.26 million USDC before pending accrual. Those are gross financing layers, not extra investor equity. At T, the outer USDC borrowing quote exceeds the configured savings APY, while the selected inner loan has a small positive frozen-rate difference before other costs.

TAU had about 3.04 million USDC of stored nested debt at the January 2026 checkpoint, but only 0.022132 USDC of accrued debt across the examined positions at T. Its carry history is real; its entire current book is not active carry capital.

Three historical loan-to-yield lifecycles now follow share minting, exact share burns and paid redemption. Allocating the USDC income to only the two borrowed lots gives a financed result of -148.049504 USDC before gas at redemption. The measured PYUSD lot ends at -0.398431 PYUSD before gas after repayment and residual debt. These are bounded financed-leg results, not whole-wallet profit. The USDC redemption enters a verified confidential wrapper, where subsequent holder-level allocation requires authorized decryption.

Concrete wstETH Plus and Midas show another boundary. A manager valuation or ETH-denominated security establishes a book claim. It does not establish attributable dollar financing, fresh portfolio backing or a payout. The report places the age of the accounting mark, fee denominator and withdrawal state beside the capital figure.

The large-borrower investigation binds technical identities and traces seven cash loans. The largest two unique measured addresses owe $212.36 million and $205.88 million across Aave and Spark, but their sampled cash is used for refinancing or dollar-token conversion. Their full debt is not classified as carry. A shared Concrete Safe is an exact known match; product allocation remains unresolved.

Six additional product records have capital, fees, historical share marks and selected exit evidence. Four share histories have a matched 732-day stETH benchmark; the comparison is book-only and excludes external rewards. Yearn has a material Spark ETH-debt loop absent from its default withdrawal queue. YieldBasis actual crvUSD debt is distinct from its larger allocated funding amount. A seventh case, hgETH, reconciles its loan book with physical rsETH and reserved adapter assets; individual loan income and dollar-carry use remain unclassified.

## What counts as a material case

The selection prioritizes products with at least $5 million of current observed value, $20 million at a sampled historical endpoint, or a distinct $1 million sleeve. Unknown borrowers with at least $5 million of sampled dollar debt receive priority. Smaller cases remain when they expose a distinct funding mechanism, closure, recovery problem or accounting dependency. These are selection rules for research depth, not proof that no unobserved material product exists.

Every additional case should answer the same questions: what asset the holder owns, who pays the income, which loan funds it, what the debt costs, which currency measures the return, who controls the assets, how the holder exits, and which dated values support the conclusion. Product permission, current positions, historical use and realized income have different evidence requirements.

## Read each capital measure in its own unit

The market chart measures linked ETH-related exposure across selected adapters. Product book NAV measures a holder claim at an accounting mark. Gross debt measures financing. A Fluid pair subtotal uses nominal stablecoin units. A later pool quote measures discovered TVL. None of those can be added together as a global net total.

An ETH-equivalent dollar value is not a native coin balance. A WETH loan valued in dollars remains ETH debt. Dollar carry retains the collateral exposure unless separately hedged, while a spot/short basis trade has a different payoff. An ETH-denominated manager token does not by itself prove ETH-long exposure.

## What remains incomplete

The report covers the main economic mechanism families and substantially expands their public evidence. It does not establish an exhaustive global product census or unique physical ETH. Public measurement gaps remain in full LP history, active options materiality and other lending generations or borrower populations outside the measured registries. Arbitrum archive access was repaired: all three selected Compound markets and four canonical WETH/USDC routes in the examined current Silo factory have fixed-T measurements. Its four routes hold only 0.088410 USDC debt; two examined legacy Arbitrum routes hold 212.334440 bridged-USDC debt units. These small amounts establish deployed routes, not material carry allocation. Confidential ownership, shared custody and off-chain inventory create additional attribution limits. These limits remain visible and are not replaced by estimates labelled as facts.

The five large carry books remain a ranked examined sample. Their combined books and top-two concentration are not the market-wide amount of deployed carry. The newly added products and borrower cases do not supply a denominator for a global coverage percentage.

## Read the supporting exhibits

[Dollar funding atlas](DOLLAR-FUNDING-ATLAS.md), [strategy and product universe](STRATEGY-UNIVERSE-EXPANSION.md), [nested carry and manager controls](CARRY-VARIANTS-EXPANSION.md), [credit venues and borrower receipts](CREDIT-EXPANSION.md), [capital, income and exits](CAPITAL-INCOME-EXIT.md).

[Carry lifecycles](CARRY-LIFECYCLES.md), [matched product histories](PRODUCT-FINANCIAL-HISTORY.md), [large-borrower use](BORROWER-USE.md) and [hgETH loan book](HGETH-LOAN-BOOK.md).

[Coverage dataset](../../../data/eth/research_expansion_coverage.json).
