# hgETH: an rsETH loan book, not an unexplained yield label

Financial state is measured at 2 October 2026, 23:59:59 UTC, Ethereum block 26,108,081. The implementation runtime at that block exactly matches the captured verified source.

## What the holder owns

The hgETH share is a claim on an rsETH-denominated loan pool. Its fixed-T book is 4,687.524488 rsETH, equivalent to 5,068.279633 ETH or $13,521,919 under the stated rsETH conversion and ETH quote. This nested claim must not be added to rsETH issuer backing as new physical ETH.

The implementation accounts for active loan exposure, underlying tokens held by the pool, collectable fees and reserved ETH in a configured adapter. Interest and loan repayments are possible payers. The public loan-book getter does not establish each borrower rate or identify a dollar reinvestment route.

## Reconcile the book before quoting yield

| Component | rsETH |
|---|---:|
| Active-loan accounting exposure | 4,670.949018699 |
| Physical rsETH in the pool | 7.359391105 |
| Reserved adapter claim, converted to rsETH | 9.216078397 |
| Collectable fees, deducted | 0.000000000 |
| Reconstructed total | 4,687.524488202 |
| Difference from totalAssets | 0.000000000000 |

The 173 deployed-loan registry entries are an all-time registry at T. Closed entries can remain present; the count is not active loan count, borrower count or current investment count. The aggregate loan exposure is a book accounting quantity rather than immediately available rsETH.

## The share mark can fall

| Date | Product book, ETH | rsETH per share | ETH per share | ETH share-value change from first endpoint |
|---|---:|---:|---:|---:|
| 2026-04 | 16,359.196 | 1.036767595 | 1.108937362 | 0.000% |
| 2026-06 | 10,435.086 | 0.994327561 | 1.068798081 | -3.620% |
| 2026-09 | 5,067.347 | 0.998634898 | 1.079663150 | -2.640% |
| snapshot_T | 5,068.280 | 0.998737186 | 1.079861951 | -2.622% |

These are four sampled endpoints. The share-value decline is not a continuous maximum drawdown, a proven realized investor loss or evidence of its cause. The measure excludes separately paid rewards, sale discounts and execution costs. The rsETH conversion itself is an issuer accounting mark.

## Fees, authority and exit

The measured management and withdrawal fee getters are zero at T. The owner and settlement account are the same Safe, with a measured 3-of-5 owner threshold. The loans operator is a separate address. Signer names, Safe modules, full authorization history and loan-level charges are not assigned.

Deposits paused: False. Withdrawals paused: False. The pool holds only 7.359391 physical rsETH against 4,687.524488 rsETH of book value. The queried owner's maxWithdraw and maxRedeem both return zero. That is a caller-specific result, not a statement that all holders can withdraw zero.

Request, processing and claim paths depend on the configured loan and withdrawal machinery. No investor payout receipt is claimed here. Loan repayments, adapter settlement and share redemption must be tested separately before estimating executable exit capacity.

## Carry classification and remaining work

This contract adds a material, publicly measured rsETH lending wrapper to the market investigation. It does not prove ETH-collateral dollar carry. Individual loans still require borrower identity, collateral, rate and repayment evidence before their economic route or realized income can be classified.

[Structured case](../../../data/eth/manager_case_chapter.json), [captured fixed-block calls](../../../data/eth/manager_case_capture.json).

[Pool](https://etherscan.io/address/0xc824a08db624942c5e5f330d56530cd1598859fd) and [fixed-T-bound implementation source](https://eth.blockscout.com/api/v2/smart-contracts/0x4ffe25598489c7259dc9686a2cba0507177bcf7f).
