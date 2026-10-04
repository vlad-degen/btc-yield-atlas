# Independent review of presentation additions

Reviewed on 4 October 2026. This review is read-only for calculation inputs, outputs, source tools and public reports. The financial snapshot remains 2 October 2026, 23:59:59 UTC.

## Result

No arithmetic discrepancy remains in the reviewed additions. An independent checker passed 120 numerical and provenance checks. Additional manual checks covered raw rate events, the fee setter's source code, the Ethereum-only fee scenario and selected current publisher documents.

Two presentation issues were reported to the project lead and corrected before this record was saved:

- The exchange-rate permission row counted three addresses but described four. It now consistently says three.
- The fee-history and fee-payment descriptions were too broad for Ethereum-only source events. They now identify the Ethereum Accountant. The consolidated-NAV fee scenario explicitly assumes a common fee, while the separate Ethereum-circulating-share scenario avoids that assumption. Neither is described as realized revenue.

## Monthly capital reconciliation

Recomputed every one of the 24 completed months from October 2024 through September 2026. The calculation uses each chain's own shares and accounting rate:

`change in NAV = opening shares × change in rate + change in shares × closing rate`.

Ethereum and Optimism are calculated separately before their effects are added. Ethereum supplies were decoded from captured archive RPC responses. Ethereum rates were selected from the latest eligible rate event at each endpoint. Optimism rates were independently decoded from `op_history_rates_rpc.json`.

All monthly opening and closing values, rate effects, share-supply effects and summary totals agree with `presentation_analysis.json`. With the serialized input values, Decimal arithmetic reconciles the identity exactly. With the full raw Ethereum event-rate integers instead, the largest NAV difference is below 0.000000000044 ETH. This is harmless serialization rounding, far below the displayed precision.

The summary is verified: total NAV change of 30,053.392820230 ETH, accounting-rate effect of 10,336.365389111 ETH, and share-supply effect of 19,717.027431119 ETH.

The labels are appropriately limited. Share-supply changes are not a measured external-deposit ledger. Rate effects explain accounting marks, not which strategy produced the income. The analysis does not treat bridge issuance, migrations or fee shares as independently proven investor flows.

## Fee chronology and payment window

Recomputed the fee integral over the exact 730-day interval from timestamp 1727913599 to 1790985599. The starting Ethereum fee is 100 basis points, determined from the last eligible pre-window update. The calendar-time weighted fee is 68.605628805175 basis points, or 0.686056288052% annually.

This is time weighting, not capital weighting. It does not establish the fee rate realized by an investor, actual fees charged to both chains or operator profit. The July 2024 update is correctly retained as pre-window context rather than counted as time inside the two-year interval.

Ethereum fee-claim events within the interval sum to:

- 121.699458818694102698 weETH, paid in three distinct transactions.
- 1,996.421850969645189349 WETH, paid in sixteen distinct transactions.

Checked the event payloads and block numbers against the captured raw Ethereum Accountant logs. The full raw collection contains 719 unique logs. Its 653 rate events also match the derived rate-event records, with a maximum rate serialization difference of 0.000000000000000244.

Payment timing is correctly distinguished from accrual timing. WETH and weETH are kept separate; the weETH payments are not silently treated as the same number of ETH. Downstream charges, operating costs and revenue sharing remain outside the operator-profit calculation.

The simple flat-balance scenarios are correct:

- Applying the Ethereum 0.35% rate to consolidated snapshot NAV gives 620.098721556 ETH annually. The report labels the equal-fee assumption and does not claim a reconstruction of both chains' accrual.
- Applying that rate only to Ethereum-circulating shares gives 486.321019084 ETH annually.

## Exit-fee illustrations

All eight product, route and period calculations agree with their source book returns and matched stETH benchmark:

`after-exit return = (1 + book return) × (1 - one-off exit fee) - 1`.

The fee is applied to final proceeds, rather than simply subtracting the fee from the return percentage. Management fees are not deducted again. Treehouse Fastlane's one-year illustration is below the matched stETH book return; the statement is supported by the calculation.

The scope labels remain necessary and are present: Fluid's fee uses the getter checked at T; Treehouse uses current published terms and does not simulate its minimum-rate settlement; CIAN uses the published policy and does not verify a deployment-specific override. None of the rows is described as an executed historical return. Slippage, waiting time, market discounts, benchmark exit costs and external rewards are excluded explicitly.

## Borrower sample and concentration

Independently normalized addresses to lowercase and counted both network/address pairs and addresses across networks. The captured sample contains 25 markets, 237 positions, 213 network/address pairs and 207 unique addresses. There are no duplicate network/market/address position records. Each market has at most ten sampled positions, sorted by reported dollar debt, and 21 markets have additional unsampled positions.

Sampled position debt is $465,256,993.956185. Separately captured market debt sums to $593,751,262.924202. Their ratio is 78.358905994543%, and the five largest sampled addresses account for 51.020268953270% of sampled debt.

These are sample diagnostics. The report correctly states that requests are asynchronous, the sample deliberately selects large positions, gross debt differs from depositor equity, addresses do not identify beneficial owners, and borrowing against ETH does not by itself establish a carry strategy. It does not present these ratios as exact market reconciliation or market-wide concentration.

## Historical permissions

Decoded raw RPC masks independently and resolved each tested function against active roles at Ethereum block 26,108,081. The raw request journal confirms the historical block and Authority target for every RPC call; content hashes agree with all captured responses.

The paginated logs produce 147 eligible role events and 36 addresses ever assigned a role. Fixed-block responses identify 22 addresses with at least one active role. These are addresses, including contracts, not counts of people or organizations.

Role 11 has exactly three eligible addresses for exchange-rate publication. Management-fee permission accepts roles 8 and 55. The role 55 holder is `0x607d0c7e3578802eb46d388cb86cfba8ff657306`. The tested functions' public-capability flags are all false.

The captured Accountant source confirms that `updateManagementFee(uint16)` uses `requiresAuth` and rejects values above `0.2e4`, equivalent to a 20% ceiling in basis-point units. A separate direct role explains why the owner timelock does not provide a universal notice period. The ceiling is correctly distinguished from the actual 0.35% fee.

Coverage is still selected-function coverage. The review does not close every strategy Merkle permission, actor's beneficial identity, upgrade path or timelock proposer/executor.

## Current document spot checks

Independently opened selected primary pages. Their descriptions agree with the corresponding report labels:

- ether.fi estimates up to three days for ETH Yield and qualifies the time by liquidity, queues, strategy operations and settlement. [Withdrawal timelines](https://help.ether.fi/en/articles/269720-typical-liquid-withdrawal-timelines).
- Fluid discloses a 0.05% exit fee and describes a direct withdrawal workflow. Its risk page separately describes emergency pause rights and losses during deleveraging. The report appropriately reads those disclosures together rather than guaranteeing instant exit. [User guide](https://lite.guides.instadapp.io/getting-started/getting-started-with-fluid-lite), [risk disclosure](https://lite.guides.instadapp.io/information/risks).
- Treehouse's opened pages state a zero-to-50-wstETH redemption band, approximately seven-day normal redemption, a five-basis-point charge and a capacity-limited 0.5% Fastlane. They disclose a 20% fee on positive Market Effective Yield and a five-day timelock. The report does not treat these current policies as fixed-block permission proofs, and excludes the inconsistent numerical redemption example. [Redemption process](https://docs.treehouse.finance/protocol/tasset/architecture/redemption-process), [fees](https://docs.treehouse.finance/protocol/tasset/architecture/fees), [timelock](https://docs.treehouse.finance/protocol/tasset/security/timelock).
- CIAN discloses an 8% performance fee included in Net APY and a 0.02% one-off exit policy. Its API documentation distinguishes policy `fee_info.exit` from contract-applied `fee_info.exit_override`, and leveraged TVL from user-deposited TVL. The report preserves those distinctions. [Fees](https://docs.cian.app/yieldlayer/for-users-quick-start/fees), [API definitions](https://docs.cian.app/yieldlayer/for-builders-developer-documentation/cian-yield-layer-tech-docs).

This is an independent spot check, not a second complete review of all 22 source-ledger entries. Enforceability of legal terms, product-specific Concrete agreements and actual executed exits remain outside this verification.

## Reviewed file identities

SHA-256 hashes at this review point:

| File | SHA-256 |
|---|---|
| `tools/eth/presentation_analysis.py` | `f22809709fc40cbf3095949157f4a43d5c9814764649d840fc875e66824079e4` |
| `data/eth/presentation_analysis.json` | `2d1a213ad3e7a92ff2c5f397d46b3c29c03c1747897b309f566c9c51794dfc0c` |
| `research/eth/en/RETURN-DRIVERS.md` | `4b466bdde142c3a418defaad6374c722f37d8ae6d4133f9e0da6965bbe873bc4` |
| `research/eth/en/PRODUCT-TERMS.md` | `964f7377c76640352f2b0c8da18d8d8747fa79f3df5b38bcd8e01952f95a00ad` |
| `data/eth/permissions_review_T.json` | `cc8213d7181f5594b3a5fe5c6d349ed78b802210be38b2aafa5fbe48fca5aa8a` |

No financial input or derived output was changed by this reviewer. Final site build, link checks, mobile review and archive validation remain the project lead's release checks.
