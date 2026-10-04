# Capital, earned income and investor exits

Final public-record edition, reviewed 4 October 2026. All contract balances and tests retain the financial snapshot of **2 October 2026, 23:59:59 UTC**. Later capture dates do not refresh the snapshot.

The research separates three quantities that a yield dashboard often puts together: the capital represented by a claim, income earned over a dated period, and proceeds available through an investor exit. Each now has a reproducible ledger. Full-market ownership and private trading records remain outside the measured scope.

## Unique capital

The default market chart measures 21.158M ETH equivalents across dated protocol layers. The new Ethereum custody graph identifies **457,182.304 ETH** in distinct native-ETH holdings and canonical WETH backed by matching native escrow. This is a restricted custody floor in examined yield venues; reserve cash can be idle. It is not a floor for all assets currently earning yield.

| Examined custody group | Physical native ETH / escrow-backed WETH |
|---|---:|
| Issuer cash | 1,809.528 |
| Aave and Spark reserve cash | 385,841.291 |
| Twenty-eight examined liquidity pools | 69,531.485 |

Finalized withdrawal-queue custody of **25,175.548 ETH** is separate. Including it gives 482,357.852 ETH in the examined custody graph. The queue balance equals locked ETH at the same block. Unfinalized stETH remains a claim rather than an additional physical ETH balance.

Canonical WETH supply and native escrow agree at **2,027,838.731 ETH**. All canonical WETH plus the named native-ETH holdings defines a scoped ceiling of 2,045,831.885 ETH. This scope excludes actual consensus balances, other native custody and other chains. It gives no global market ceiling or coverage percentage.

The largest directly measured receipt repetition is **2,350,079.426 ETH equivalent** in Aave and Spark wstETH lender claims. Lido already accounts for the backing. Restaking has another nested path: Kelp node claims sit inside EigenLayer’s stETH strategy, which refers to Lido stake. The ownership edges overlap; adding or subtracting all of them indiscriminately would create a new counting error.

Lido’s book reconciles to **9,841,288.207 ETH**. Its consensus fields refer to the oracle slot at 2026-10-02T12:00:11Z, about twelve hours before T. Tested public historical consensus endpoints did not supply the actual state at T. Validator count times 32 ETH is not used as a substitute.

The pool extension follows the same 21 Uniswap V3 and seven Curve addresses through 25 monthly observations, including the September 2024 baseline. All 700 pool/month cash reads succeeded. The main exhibit uses the 24 completed months from October 2024 to September 2026. This is a history of physical ETH-side custody in a bounded current address census. It does not establish a market-wide historical pool universe, active trading liquidity or LP profit. V4, Balancer, Sushi and the broader pool universe remain outside this reconstruction.

**Conclusion:** repeated ownership is quantified, a restricted physical custody floor is established, and the global unique earning-capital total remains unavailable. A global number needs actual consensus state, remaining custody and bridge backing, and ownership allocation across all included layers. A blanket percentage haircut would not resolve those records.

Evidence: [market netting ledger](../../../data/eth/market_netting_closure.json), [custody CSV](../../../data/eth/market_netting_roots.csv), [pool history CSV](../../../data/eth/market_netting_lp_monthly.csv).

## Earned income

Common window: **2026-08-07T17:04:59+00:00 to 2026-10-02T23:59:59+00:00**, 56.288 days. The window starts at the last block before the first tracked RLUSD V2 deposit. All included claims, loans and cash reward payments use the same endpoints.

| Destination / asset | Net claim growth | Cash rewards received | Accrued tracked loan cost | Ending claim | Ending tracked debt |
|---|---:|---:|---:|---:|---:|
| RLUSD | 145,919.43 | 172,802.40 | 405,516.92 | 55,104,709.54 | 70,211,978.15 |
| PYUSD | 164,823.37 | 150,678.52 | 226,324.77 | 49,605,232.78 | 21,017,993.33 |
| cUSD | 247,384.00 | Not established | Not established | 24,625,816.34 | Not established |

All amounts stay in the named asset. Dollar parity is a valuation assumption, not a verified redemption price. These components are not combined into a product carry ROI. In RLUSD, accrued loan costs exceed the captured claim growth and reward receipts; tracked loan principal also exceeds the destination claim. That makes financing coverage essential to interpretation.

Claim growth is ending claim less opening claim, plus actual withdrawals, less deposits. Destination fees already recognized in the share value are included. The result can contain lending income, donations or other recognized asset changes; it does not independently classify every dollar as organic interest. Cash withdrawals contain returned principal. The gain on redeemed shares uses the disclosed weighted-average acquisition-cost convention.

Borrowing cost is ending accrued debt less opening debt, plus actual repayments, less new borrowed cash. It includes interest still owed at T. Borrow/repay share ledgers reconcile to historical contract state, and pending interest uses the verified deployed model. Monthly APR quotes are not interpolated into paid cost.

Reward cash is measured from actual token transfers from the distributor to controlled accounts. Campaign sponsor, entitlement periods and destination allocation remain separate. Receiving a reward inside the window does not establish that the entire reward was earned inside it.

| Financing coverage | Direct same-token borrow/deposit amount | Deposit principal without that transaction link |
|---|---:|---:|
| RLUSD | 36,000,000.00 | 21,027,780.85 |
| PYUSD | 39,400,000.00 | 19,298,538.46 |
| cUSD | 0.00 | 11,099,060.00 |

Receipt log order is part of the funding test. A deposit made before the loan arrives is not assigned to that loan, even if both events share one transaction. Four additional currency-changing receipts trace USDC loans into RLUSD/PYUSD deposits. The borrowed and invested asset amounts remain separate; no peg conversion or common-dollar profit is assumed.

| Currency-changing deposit | Borrowed cash | Verified transaction |
|---|---:|---|
| 2,902,064.71 RLUSD | 2,903,973.87 USDC | [Transfer receipt](https://etherscan.io/tx/0x3271597261ff099d80b3c097aa60ec15b7dc1c3908f130dc81f815c4619c6ffc) |
| 12,270,716.14 RLUSD | 12,277,550.30 USDC | [Transfer receipt](https://etherscan.io/tx/0x6f35ce22c709d955741a7cd70808c7a81b1d38932c4ff7cca46d4e11a529954e) |
| 3,500,000.00 RLUSD | 3,500,000.00 USDC | [Transfer receipt](https://etherscan.io/tx/0xa88ac6fc36efe5821426b99b27dc62463aa83c0a60dc8f319c99a3a8362aafa7) |
| 1,993,422.62 PYUSD | 1,970,000.00 USDC | [Transfer receipt](https://etherscan.io/tx/0x66a0fb9f9b6d836e613bd7723cbf8e3e05e537e0984f5f92ef5b64ccc0a0a7a3) |

The other tracked USDC loan accrues 15,559.44 USDC of cost in this window. It is not included in either same-currency chart. PRIME’s underlying is wYLDS with six decimals; transferred PRIME share basis and its full collateral financing remain unallocated.

| Own-credit diagnostic | Accrual events | Gross recognition-time overlap | Net destination allocation / paid own-interest |
|---|---:|---:|---|
| RLUSD | 323 | 38,912.20 RLUSD | Not established |
| PYUSD | 647 | 4,049.74 PYUSD | Not established |

The common window contains 2 Ethereum fee-claim payments totaling 71.18634 weETH. Payment dates do not assign the earning period or carry strategy. The Ethereum net share return already reflects recognized fees; these payments are not deducted a second time.

| Whole Ethereum share / issuer conversion | ETH book return in the common window |
|---|---:|
| stETH | 0.3429% |
| weETH | 0.3612% |
| LiquidETH Ethereum | 0.4750% |

These whole-share outcomes use identical endpoint blocks. They include every strategy and do not identify the causal carry contribution.

One exact retained pair matches 3,000,000 PYUSD of borrowing and destination deposits. It exists for only 108 seconds before T: destination claim growth is 0.557687 PYUSD and accrued loan cost is 0.751967 PYUSD. Their -0.194280 PYUSD component is before rewards, outer fees and own-credit allocation. Neither claim income nor loan interest was paid as cash in this interval. This tiny exact-state diagnostic is too short to establish strategy economics and is not annualized. The older 18M PYUSD pair has subsequent withdrawals, so its retained acquisition basis cannot be uniquely assigned.

A same-transaction transfer establishes a financing link. It does not identify unique fungible dollars or allocate later profit. Unmatched principal is not assumed unborrowed. Own-credit can recycle a borrower’s interest through a destination it owns; gross recognition-time overlap, where reconstructed, remains a diagnostic rather than additional income. Net own-interest after fees and actual cash distribution remain unallocated.

**Conclusion:** historical claim growth, loan expense and paid incentives are measured. Staking, other destinations, historical self-credit, outer fees and private payouts are not fully allocated to each carry sleeve or whole product. Complete sleeve net income stays unavailable. The fixed-rate calculator remains a separately labelled scenario.

Evidence: [income components](../../../data/eth/carry_attribution_closure.json), [historical event ledger](../../../data/eth/carry_attribution_ledger.json), [financing transactions](../../../data/eth/carry_attribution_funding_links.csv).

## Investor exits

Demand is tested at 1%, 10% and 30% of each whole accounting book. Calls use the examined Ethereum holder and configured route; Liquid’s book denominator includes Ethereum and Optimism shares. Requests, immediate withdrawals and full portfolio unwinds are separate. Read-only calls persist no state and send no transaction.

| Product | Book, USD | Examined positions / conditional claims, USD | Book less examined reconstruction, USD | Verified historical cash payout records |
|---|---:|---:|---:|---:|
| Concrete Delta weETH | $820.029M | $480.617M | $339.412M | 0 |
| ether.fi Liquid ETH | $472.684M | $458.586M | $14.098M | 2,822 |
| Rocksolid rETH | $25.953M | $6.101M | $19.852M | 428 |
| Liquity ETH Carry | $16.045M | $16.030M | $0.015M | 93 |
| Royco ETH | $0.310M | $0.309M | $0.000M | 0 |

The reconstruction column includes the stated oracle marks and conditional nested claims. Coverage differs by product. Book less examined reconstruction is an unmapped amount; it is not a proven deficit or loss. Shared custody does not establish beneficial assignment to one share book.

### Concrete Delta weETH

Visible shared Safe assets and nested book claims. Beneficial assignment to Delta is not independently established.

Successful eth_call enters active epoch queue and transfers vault shares into escrow. It does not transfer weETH to the receiver.

Granting Delta every captured visible shared asset gives a conditional attributable ceiling of $480.617M and still leaves $339.412M of its book unmapped to this set. Its captured attributable range starts at zero because beneficial assignment is not established. The sibling internal receipt is eliminated. This makes private asset statements and allocation agreements necessary to reconcile the whole claim.

Ethereum vault logs, blocks 23996053 through 26108081 (T); every requested interval returned successfully.

### ether.fi Liquid ETH

Existing mixed-price position reconstruction, including nested book claims. This is not independently audited physical backing.

Ordinary holder direct exit is unauthorized. Queue request requires share allowance; aggregate demand exceeds individual holder capacity at larger sizes and was not simulated as a portfolio unwind.

The original mixed-price reconstruction was $460.231M with a $12.453M scope residual. The expanded look-through replaces the nested Monad book receipt with captured claims rather than adding them on top: $458.586M reconstructed and $14.098M unmapped. It includes 7,427.621860 SteakETH shares converting to 7,495.062795 WETH in that receipt book, plus known loose balances. SteakETH backing itself is a nested credit claim, not independently reconciled physical assets.

maxWithdraw reports zero while a one-WETH withdraw eth_call returns successfully. No simulated transfer trace or T implementation binding is available for this nested receipt, so a successful return is not promoted to proven cash liquidity.

Ethereum BoringOnChainQueue, blocks 20000000 through T; every requested interval returned successfully. Optimism and older predecessor queues are outside this census.

Completed request-to-cash observations have a median of 12.56 hours, p90 56.39 hours and maximum 12.26 days. The wait can include investor collection delay. Cancelled and pending requests are excluded; these figures do not forecast a new request.

### Rocksolid rETH

Known Ethereum execution-wallet cash, Spark net equity, Balancer principal and YieldBasis/nested-vault book claims. Remaining book value has no attributable position in this bounded public inventory; this is not a proven shortfall.

New request simulation reverts NotOpen(Closing). Holder has no claimable redemption assets at T.

The T contract state is Closing. Verified source distinguishes initiateClosing from ordinary redemption settlement; new redemption requests are rejected in that state. The owner transition is dated in the exit ledger. This is evidence of an initiated closure process, not proof of a loss, completed closure or permanent future deprecation. Historical payout records remain relevant to existing claims.

Ethereum vault logs, blocks 23000000 through 26108081 (T); every requested interval returned successfully.

Completed request-to-cash observations have a median of 40.30 hours, p90 160.27 hours and maximum 134.97 days. The wait can include investor collection delay. Cancelled and pending requests are excluded; these figures do not forecast a new request.

### Liquity ETH Carry

Ebisu collateral less debt, loose cash, Curve ebUSD/USDC principal and the stored Uniswap V4 market book. Different protocol/book prices and uncollected fees remain unreconciled. Fresh accounting update simulations from holder and atomist both lack permission, so stored market marks were not promoted to refreshed values.

The 1% holder withdrawal succeeds. The 10% and 30% calls revert on the configured withdrawal path despite sufficient holder shares.

Ethereum vault logs, blocks 24000000 through 26108081 (T); every requested interval returned successfully.

### Royco ETH

Fresh Morpho collateral/debt and an identified senior receipt replace stale Caliber position values. Standardized asset quotes and nominal-dollar assumptions can differ from the parent cached AUM. Senior vault book value remains a nested credit claim.

ERC4626 withdrawal simulation reverts because maximum immediate withdrawal is zero.

Machine and Caliber beacon implementations at T match the examined verified bytecode. The instruction-root delay is two days. Duration changes use an active AccessManager role held by a 3-of-4 Safe with a three-day execution delay; an unscheduled execute call reverts. The controls apply to different actions. They do not establish an immutable or universally additive five-day notice, and every other admin/module path is outside this particular proof.

Ethereum vault logs, blocks 24585152 through 26108081 (T); every requested interval returned successfully.

**Conclusion:** historical token payouts and snapshot execution constraints are documented. Concrete queues requests, Liquid has a measured payout history but no tested aggregate unwind, Rocksolid rejects new requests in Closing, Liquity succeeds at the tested 1% withdrawal size while larger calls revert, and Royco’s examined immediate route is unavailable at T. Public backing and private ownership boundaries remain product-specific.

Evidence: [backing and exits](../../../data/eth/backing_exit_closure.json), [all demand scenarios](../../../data/eth/backing_exit_demands.csv), [source manifest](../../../data/eth/backing_exit_manifest.json).

## What this edition supports

The completed website supports a colleague presentation of the market’s reported layers, two-year category changes, financing mechanics, measured income components and investor exit constraints. It preserves the original Bitcoin chapter structure and uses bars for capital exhibits. Every numerical answer keeps its measurement date, unit, denominator and evidence boundary.

Private custody allocation, full actual consensus state and a complete strategy-attributed investor P&L cannot be created from public share prices or sampled rates. They remain precise evidence limits, not silently filled estimates. The record needed to improve each answer is stated in its ledger.
