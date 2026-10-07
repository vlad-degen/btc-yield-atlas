# ETH dollar carry: financing, ownership and economics

Financial snapshot: 2 October 2026, 23:59:59 UTC. Ethereum block 26,108,081. Later discovery documents are dated separately.

## What the category actually contains

The attributed product accounts owe **$261,325,366** of direct ETH-backed dollar debt at the snapshot. This measures financing, not carry equity. Whole hybrid vault books contain other strategies, while outstanding debt includes accrued interest and can differ from dollars invested. The top two account for **79.94%** of this measured financing sample, not the global ETH yield market.

| Product | Direct dollar debt at T | Debt-weighted quoted APR | Whole book ETH | Scope |
| --- | --- | --- | --- | --- |
| ether.fi Liquid ETH | $181,084,944 | 7.79% | 177,171 | attributed product account / direct loan |
| YieldBasis WETH | $27,814,856 | 10.00% | 10,426 | attributed product account / direct loan |
| Lido Earn ETH | $25,555,160 | 4.33% | 83,309 | attributed product account / direct loan |
| Avant avETH / savETH | $10,034,777 | 6.30% | 12,583 | attributed product account / direct loan |
| Liquity ETH Carry | $6,752,065 | 2.55% | 6,014 | attributed product account / direct loan |
| NEMO ETH Prime | $5,611,801 | 4.75% | Not reconstructed | attributed product account / direct loan (vault book reconciles with the loan) |
| Rocksolid rETH | $2,727,060 | 4.61% | 9,728 | attributed product account / direct loan (second strategy wallet) |
| Sentora ETH | $1,163,324 | 11.79% | Not reconstructed | attributed product account / direct loan (vault book reconciles with the loan) |
| Makina DETH | $384,701 | 3.21% | 2,499 | attributed product account / direct loan |
| Royco ETH | $90,891 | 30.24% | 116 | attributed product account / direct loan |
| Vesper vaETH | $68,998 | 5.00% | 1,052 | attributed product account / direct loan |
| Reservoir ETH Yield | $36,790 | 13.93% | Not reconstructed | attributed product account / direct loan |
| TAU InfiniFi ETH Carry | $0 | Unavailable | Not reconstructed | attributed product account / direct loan |


## The corrected historical comparison

Twenty-four month-end samples now reconstruct actual dollar liabilities and funded financing quotes. The series excludes ETH-debt loops, duplicate nested product claims and unassigned Concrete debt. Inner savings loans remain in the full loan ledger with `outer=false`; they do not inflate the direct ETH-backed chart. The inventory follows markets identified by the present and historical research, so earlier alternate or retired markets can remain missing. An empty call is not a measured zero. Rates are debt-weighted month-end model quotes, not paid monthly average costs.

[Monthly loan observations](../../../data/eth/economic-dollar-loans.csv) and [product financing bars](../../../data/eth/economic-carry-history.csv) contain the account, currency, block and source labels. The existing whole-book histories remain in product chapters. They are not relabelled as carry allocation history.

## Why Concrete is outside the verified five

Its 307,363 ETH book is a manager-issued claim. The shared strategy Safe has dollar loans, but the records do not assign its backing or debt wholly to Delta. The initial mint is not an underlying deposit transfer. Counting the entire claim as measured carry would conflate issuance with beneficial ownership. The case and its full evidence remain accessible.

## Funding is a separate unit from ETH return

A cumulative ETH book return cannot be reduced by an annual dollar loan quote. A cash spread needs identical dollar principal, dates, investment income, interest and costs. The matched cash ledgers include four financed lots and two flow-adjusted claim/funding records. Lido's 5M USDT lot earns a positive recognised margin over 29 September to the snapshot, before gas and outer fees. Vesper's vDAI accrual falls short of its DAI cost. These narrow results are not whole-product organic annual yields.

For Liquid, the larger controlled Aave USDC debt matters alongside the lower-rate RLUSD markets. Its weighted dollar funding cost differs materially from quoting the RLUSD route alone. Destinations, rewards and fees must be assigned per loan before estimating the whole carry sleeve's income. [Source-calculated ledger](../../../data/eth/economic_questions.json).

## Additional manager routes

The full official Upshift registry was examined after finding Sentora ETH's documented weETH/RLUSD route. Archive calls also establish NEMO-associated wstETH/USDC debt. Vault permissions and manager-associated accounts are disclosed separately; permission to use an account is not a complete beneficial-ownership reconciliation. These loans are shown as associated candidates and excluded from the attributed aggregate. API NAV and APR fetched on 6 October are discovery data and never substituted for the frozen financial balances.

## Market accounting

The default protocol panel contains 175 observed parents and 18,542,591 ETH equivalents of reported exposure. The headline, donut, category table and two-year bars all use that same selection. Issuer, restaking, lending and vault claims overlap; this is a protocol-exposure market map. Exact-block Lido, Aave and Spark reconciliation demonstrates the duplication numerically. Public inputs do not establish a complete global net yield-capital total or carry-equity share, and neither number is manufactured from the panel.

## Sources and reproduction

[Canonical answers](../../../data/eth/economic_questions.json), [loan CSV](../../../data/eth/economic-dollar-loans.csv), [financing history CSV](../../../data/eth/economic-carry-history.csv), [product mechanics](CARRY-PRODUCTS.md), [ownership reconciliation](CAPITAL-INCOME-EXIT.md), [product evolution](PRODUCT-EVOLUTION.md).
