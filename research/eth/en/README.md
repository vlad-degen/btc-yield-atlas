# ETH yield research

Expanded public-record edition, reviewed 4 October 2026. Snapshot T: 2 October, 23:59:59 UTC. History: 24 months. Captured data, contract checks and findings are available; complete net market sizing remains open.

Start with the [team briefing](BRIEFING.md), the [market composition and history](MARKET-STRUCTURE.md), and the [five carry-product chapters](CARRY-PRODUCTS.md). The original [market report](MARKET-RESEARCH.md) remains available as supporting research. It explains where ETH earns income, how carry and borrowing loops work, and what the evidence says about capital, returns and withdrawals.

| Material | Contents |
|---|---|
| [Capital, earned income and exits](CAPITAL-INCOME-EXIT.md) | Fixed-block custody, repeated receipts, historical income/cost ledgers and verified investor cash payouts |
| [Market coverage](MARKET-COVERAGE.md) | Main economic mechanisms, measured scope and remaining public omissions |
| [Dollar funding atlas](DOLLAR-FUNDING-ATLAS.md) | Sixty reserves across twelve chains, dated APRs, cash and restrictions |
| [Strategy universe](STRATEGY-UNIVERSE-EXPANSION.md) | Ten additional families and twenty-five selected product cases |
| [Product financial histories](PRODUCT-FINANCIAL-HISTORY.md) | Capital, matched ETH share benchmarks, fees and withdrawal simulations |
| [Nested carry](CARRY-VARIANTS-EXPANSION.md) | Historical outer/inner loans and manager accounting |
| [Financed lifecycles](CARRY-LIFECYCLES.md) | Exact loan, deposit, redemption and residual-liability results |
| [Borrower use](BORROWER-USE.md) | Contract identities, rankings, refinancing and actual currency conversions |
| [hgETH loan book](HGETH-LOAN-BOOK.md) | Loan/cash/adapter reconciliation, historical share marks and control |
| [Market tables](MARKET-TABLES.md) | 57 discovery chains, the 85-row protocol ledger and comparable returns |
| [WETH lending](LENDING-MARKETS.md) | Fixed-block claims, debt, cash, deficits and borrower concentration |
| [History](HISTORY.md) | ETH wealth, two-year returns and protocol trends |
| [Mechanics](MECHANICS.md) | Staking, restaking, ETH loops, dollar carry, basis, PT, LP and options |
| [Carry calculations](CARRY-MATH.md) | Dollar financing, destination income, rewards and the seven-input model |
| [Archived financing](BORROW-HISTORY.md) | 24 month ends, verified account funding and separate E3/E4 rates |
| [Economics](ECONOMICS.md) | Break-even rates, liquidation headroom and cash for debt repayment |
| [Dependencies](DEPENDENCIES.md) | Nested claims, shared custody and overlapping lending and borrowing |
| [Evidence](EVIDENCE.md) | What each conclusion establishes and where its evidence stops |
| [Audit](AUDIT.md) | Source limits, checks and local reproduction |
| [Execution status](EXECUTION-CHECKLIST.md) | Completed analyses and specific public-record limits |
| [Research plan](RESEARCH-PLAN.md) | Full phased target scope |

## Dossiers

| Product / segment | Evidence depth in this edition |
|---|---|
| [ether.fi Liquid ETH](dossiers/etherfi-liquid-eth.md) | Shares and positions at T, partial balance sheet, carry, LP, history, fees and control |
| [Concrete ETH](dossiers/concrete-eth.md) | Share genesis/ownership, shared Safe, private accounting and overlap |
| [Fluid Lite](dossiers/fluid-lite.md) | Gross/debt/net, fees and historical ETH returns |
| [Treehouse tETH](dossiers/treehouse-teth.md) | Accounting unit, ETH conversion and withdrawal terms |
| [CIAN rsETH](dossiers/cian-rseth.md) | Returns in rsETH and ETH, historical conversion and recovery limits |
| [Carry credit](dossiers/carry-credit.md) | RLUSD/PRIME, borrowers, fees and linked flows |
| [Liquid Monad](dossiers/liquid-monad.md) | Its own accounting rate, sole holder and unresolved remote backing |
| [Staking/restaking](dossiers/staking-restaking.md) | Native root, overlap, receipt accounting and rsETH incident |
| [Lending/LP](dossiers/lending-lp.md) | Payers, selected borrowers, NFT principal and debt |
| [JustLend Tron](dossiers/justlend-tron.md) | Mapped-token identities, utilization and API reconciliation |
| [Ethena basis](dossiers/ethena-basis.md) | ETH leg, hedges/custody and disclosure boundaries |
| [Pendle PT](dossiers/pendle-pt.md) | Expiry, redemption units and liquidity versus principal |

Semantic data: data/eth; tools: tools/eth; raw: raw/eth/2026-10-02. Original BTC outputs remain unchanged. Reproduce from the root with python3 tools/eth/rebuild.py; Audit explains runtime/raw handoff.
