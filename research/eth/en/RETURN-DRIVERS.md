# Where returns and capital growth come from

This report adds calculations to the captured research edition. The financial snapshot remains 2 October 2026, 23:59:59 UTC. Current document terms used in exit illustrations are labelled separately.

## The practical findings

- Liquid ETH's capital changed by 30,053.393 ETH over the 24 completed months. The accounting-rate effect contributed 10,336.365 ETH; changes in share supply contributed 19,717.027 ETH at month-end marks.
- Capital growth is therefore different from investor return. New shares, withdrawals, internal transfers and other issuance events can change capital without changing return per share.
- Exit costs can reverse a close ranking. A single 0.5% Treehouse fast exit applied to the one-year book return leaves less than the matched stETH book return. This is an illustration using current terms, not a historical execution result.
- Liquid ETH management fees changed several times. Applying today's fee to the whole two-year history would misstate past terms.
- A 24-hour owner timelock is not a universal delay: a separate measured role can change Liquid ETH's management fee.

## Capital growth: a reconciliation, not a deposit ledger

The published capital value is the share supply multiplied by the accounting rate on each chain. For each month, we separate the change into two terms. The first measures the effect of the rate change on the opening share balance. The second values changes in shares at the closing rate.

`NAV change = old shares × (new rate - old rate) + (new shares - old shares) × new rate`

The calculation is performed separately for Ethereum and Optimism, using each chain's own rate. Every monthly row reconciles to the captured published NAV change. The share-supply term is not measured external deposits: a transaction-level ledger is still required to distinguish investor flows, migrations, fee shares and messages in flight. The rate term explains accounting marks, not the strategy positions that earned them.

| Month | Opening capital, ETH | Closing capital, ETH | Capital change, ETH | Rate effect, ETH | Share-supply effect, ETH |
|---|---:|---:|---:|---:|---:|
| 2024-10 | 146,909.038 | 146,203.011 | -706.027 | 357.505 | -1,063.532 |
| 2024-11 | 146,203.011 | 150,259.353 | 4,056.343 | 408.132 | 3,648.211 |
| 2024-12 | 150,259.353 | 152,716.552 | 2,457.198 | 348.445 | 2,108.754 |
| 2025-01 | 152,716.552 | 153,364.319 | 647.767 | 358.805 | 288.962 |
| 2025-02 | 153,364.319 | 159,201.605 | 5,837.286 | 296.115 | 5,541.171 |
| 2025-03 | 159,201.605 | 161,418.292 | 2,216.687 | 197.827 | 2,018.859 |
| 2025-04 | 161,418.292 | 176,931.275 | 15,512.984 | 595.328 | 14,917.655 |
| 2025-05 | 176,931.275 | 194,955.502 | 18,024.227 | 254.980 | 17,769.247 |
| 2025-06 | 194,955.502 | 191,748.420 | -3,207.082 | 173.106 | -3,380.188 |
| 2025-07 | 191,748.420 | 200,467.344 | 8,718.924 | 173.406 | 8,545.518 |
| 2025-08 | 200,467.344 | 203,044.519 | 2,577.175 | 908.140 | 1,669.035 |
| 2025-09 | 203,044.519 | 192,310.393 | -10,734.126 | 768.665 | -11,502.792 |
| 2025-10 | 192,310.393 | 177,463.784 | -14,846.609 | 902.870 | -15,749.479 |
| 2025-11 | 177,463.784 | 147,816.663 | -29,647.120 | 724.078 | -30,371.198 |
| 2025-12 | 147,816.663 | 147,083.058 | -733.605 | 653.525 | -1,387.130 |
| 2026-01 | 147,083.058 | 154,309.518 | 7,226.460 | 591.487 | 6,634.973 |
| 2026-02 | 154,309.518 | 108,292.173 | -46,017.345 | 295.463 | -46,312.809 |
| 2026-03 | 108,292.173 | 147,239.056 | 38,946.883 | 301.170 | 38,645.714 |
| 2026-04 | 147,239.056 | 124,604.898 | -22,634.158 | 363.671 | -22,997.829 |
| 2026-05 | 124,604.898 | 108,176.240 | -16,428.658 | 307.946 | -16,736.604 |
| 2026-06 | 108,176.240 | 88,680.876 | -19,495.364 | 321.060 | -19,816.424 |
| 2026-07 | 88,680.876 | 122,177.115 | 33,496.238 | 273.990 | 33,222.248 |
| 2026-08 | 122,177.115 | 173,879.679 | 51,702.564 | 308.211 | 51,394.353 |
| 2026-09 | 173,879.679 | 176,962.431 | 3,082.751 | 452.441 | 2,630.310 |

## What a one-off exit fee does to the comparison

The table applies a single fee to the final proceeds: `(1 + book return) × (1 - exit fee) - 1`. It does not deduct management fees again. It excludes slippage, waits, market discounts, benchmark exit costs and external rewards. Fees could have differed during the historical window.

| Product / route | Days | Book return | One exit fee | Illustrative return after exit | Excess vs stETH book return, pp |
|---|---:|---:|---:|---:|---:|
| Fluid Lite ETH / Checked withdrawal | 365 | 3.5096% | 0.05% | 3.4578% | 0.9793 |
| Treehouse tETH / Standard | 365 | 2.7845% | 0.05% | 2.7331% | 0.2546 |
| Treehouse tETH / Fastlane | 365 | 2.7845% | 0.50% | 2.2706% | -0.2079 |
| CIAN rsETH / Published policy | 365 | 2.2455% | 0.02% | 2.2251% | -0.2535 |
| Fluid Lite ETH / Checked withdrawal | 730 | 8.8243% | 0.05% | 8.7699% | 3.2824 |
| Treehouse tETH / Standard | 730 | 6.2761% | 0.05% | 6.2229% | 0.7354 |
| Treehouse tETH / Fastlane | 730 | 6.2761% | 0.50% | 5.7447% | 0.2572 |
| CIAN rsETH / Published policy | 730 | 1.0854% | 0.02% | 1.0652% | -4.4223 |

Fluid uses the checked 5 bp getter at T. Treehouse uses current published terms and still depends on route capacity and settlement rules. CIAN's 0.02% is the published policy; an actual contract override has not been verified here. Liquid ETH is omitted because a single verified cost for every exit route is unavailable. Concrete private distributions and settlement terms do not support a matched numerical return. See [product terms and exit routes](PRODUCT-TERMS.md).

## Ethereum fee changes and operator revenue

The two-year calendar-time weighted Ethereum Accountant management fee is 0.6861%. This weights time, not capital, and must not be read as the investor's realized fee rate.

| UTC date | Previous annual fee | New annual fee | Ethereum transaction |
|---|---:|---:|---|
| 2024-07-30 | 2.00% | 1.00% | [Transaction](https://etherscan.io/tx/0xe6ee85080f58036f22331a69f3b4f8ebd0688b4f89556469073ce55695fc3862) |
| 2025-01-01 | 1.00% | 1.50% | [Transaction](https://etherscan.io/tx/0xfcdf2463cb31deacb75e241a3111b056ff9eb944671b5f9ff4c03cdbbfd486cd) |
| 2025-07-26 | 1.50% | 0.00% | [Transaction](https://etherscan.io/tx/0x5a4d7253f0ac585c26ab7cd2f09be79a657a9cd77d9c15b5e1fc4c76fe0fcaa7) |
| 2025-10-25 | 0.00% | 0.50% | [Transaction](https://etherscan.io/tx/0x080e49d0cb6bee1f81e63bc87329bd5ddd2c4bb01cdcb3c5320ce7b90c21fd93) |
| 2025-12-29 | 0.50% | 0.00% | [Transaction](https://etherscan.io/tx/0xbb9a2cae9ca58ffda753f8d5478f3565f189028d858aa10655291ff8d1f0d9b4) |
| 2026-05-14 | 0.00% | 0.25% | [Transaction](https://etherscan.io/tx/0x4f6274c5a7262b74a2774c3a0fd5a415031b08b8bdc18cc5c3580e4a13767db0) |
| 2026-06-08 | 0.25% | 0.50% | [Transaction](https://etherscan.io/tx/0xbf1f51f73ea5bf5bef8c3df0df1baf9a60e58f3bd312774142d3dc8d9d025ef5) |
| 2026-06-11 | 0.50% | 0.65% | [Transaction](https://etherscan.io/tx/0xcc9f9c36cbe6b005f4212af0ce9db49de4ea78519e6ffc2b9274f7a1b8b73c0f) |
| 2026-07-16 | 0.65% | 0.80% | [Transaction](https://etherscan.io/tx/0xe96a2bc387572c0f94b55d5fe1c2b9af5f628fc5b0d7f8e9e74555a219deb0c3) |
| 2026-08-04 | 0.80% | 0.70% | [Transaction](https://etherscan.io/tx/0xf047c068b4d7311344adfb02fc56310d7200d12799a9894675b3b66ff5f2b431) |
| 2026-08-20 | 0.70% | 0.10% | [Transaction](https://etherscan.io/tx/0x76938146a7c176075c979c8b0ac206faa1a5e77e351bedcfa983a391575c3b3f) |
| 2026-08-31 | 0.10% | 0.35% | [Transaction](https://etherscan.io/tx/0x4aa5efd4417e8c3eef32362a2165f9f64e454808cf0b19ad7a5ebddd1683f7c4) |

Applying the Ethereum 0.35% annual fee to unchanged consolidated snapshot NAV gives an illustrative gross fee run rate of 620.099 ETH, or $1,654,393 at the research quote. This scenario assumes the same fee across all circulating shares. It is not a reconstruction of both chains’ actual fee accrual, annual revenue already earned or operator profit.

Using only Ethereum-circulating shares and the same flat-balance assumption gives 486.321 ETH per year. Optimism has its own Accountant and its fee history has not been reconstructed here.

Within the matched 730-day window, captured Ethereum Accountant fee-claim events paid:
- 121.699459 weETH across 3 claim transactions.
- 1,996.421851 WETH across 16 claim transactions.

WETH and weETH amounts are kept separate. Claim payments can settle fees accrued earlier, so payment timing does not equal fee-earning timing. Costs, revenue sharing and downstream curator charges are needed to calculate operator net profit.

## Who can change Liquid ETH's book and fee

The historical role audit paginated the Authority's logs to creation and read permissions at Ethereum block 26,108,081. It found 36 addresses ever assigned roles and 22 addresses with at least one active role at T. These counts include contracts and do not identify 22 people or organizations.

| Function | Active role IDs | Eligible addresses at T | What this means |
|---|---|---:|---|
| `manage(address,bytes,uint256)` | 1 | 1 | Manager can instruct the vault; its Merkle permission tree is another control layer. |
| `enter(address,address,uint256,address,uint256)` | 2 | 1 | The Teller can mint shares through the deposit path. |
| `exit(address,address,uint256,address,uint256)` | 3 | 1 | The Teller can burn shares through the withdrawal path. |
| `updateExchangeRate(uint96)` | 11 | 3 | Three addresses can publish the accounting rate. |
| `updateManagementFee(uint16)` | 8, 55 | 2 | Both the timelock role and a separate operator role can set the fee. |
| `pause()` | 5, 9, 14 | 11 | Emergency pause permission is broader than unpause permission. |
| `unpause()` | 5, 9 | 2 | Restarting the Accountant is restricted to a smaller set. |
| `setRateProviderData(address,bool,address)` | 8 | 1 | Changing asset-rate provider data uses the owner role. |

The owner timelock's minimum delay is 24 hours. The management-fee selector also accepts role 55, held at T by `0x607d0c7e3578802eb46d388cb86cfba8ff657306`. That direct role permission means the owner delay does not guarantee a 24-hour notice period for every fee change. The Accountant source limits this setter to a maximum management fee of 20%; a code ceiling is not the current fee or a commitment to keep it unchanged.

All tested selectors were non-public. The complete list of active role addresses and RPC responses is in the [historical permission record](../../../data/eth/permissions_review_T.json). Beneficial identities, every strategy leaf and every timelock proposer/executor remain separate checks.

## Borrower concentration: what the sample can tell us

The captured Morpho sample contains 25 markets and 237 positions. There are 213 network/address pairs and 207 unique addresses across networks. An address operating on two chains creates two network/address pairs.

It selects at most ten largest positions per market; 21 markets have more positions. The five largest sampled addresses account for 51.02% of sampled dollar debt. This is concentration inside a deliberately top-heavy sample, not a market-wide concentration statistic.

Sampled position debt totals $465.257M, versus $593.751M in the separately captured market states. The ratio is 78.36%. Requests are asynchronous, so the gap is not a proved error, deficit or exact missing-debt amount.

| Address | Sampled gross debt, USD millions | Sampled positions | Chain IDs |
|---|---:|---:|---|
| [0x7ee29373f075ee1d83b1b93b4fe94ae242df5178](https://etherscan.io/address/0x7ee29373f075ee1d83b1b93b4fe94ae242df5178) | 70.396 | 1 | 1 |
| [0xf0bb20865277abd641a307ece5ee04e79073416c](https://etherscan.io/address/0xf0bb20865277abd641a307ece5ee04e79073416c) | 66.597 | 2 | 1 |
| [0x462a336dcac6eaf544106266914caa5a18b831d0](https://etherscan.io/address/0x462a336dcac6eaf544106266914caa5a18b831d0) | 42.557 | 4 | 1, 10 |
| [0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3](https://etherscan.io/address/0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3) | 34.293 | 1 | 1 |
| [0xa122687285dc5012141055a801045f069112e7c6](https://etherscan.io/address/0xa122687285dc5012141055a801045f069112e7c6) | 23.533 | 3 | 1 |
| [0x1778767436111ec0adb10f9ba4f51a329d0e7770](https://etherscan.io/address/0x1778767436111ec0adb10f9ba4f51a329d0e7770) | 17.877 | 1 | 1 |
| [0xa56da9bb528fedf8379b02e95fbbdad34d45846f](https://etherscan.io/address/0xa56da9bb528fedf8379b02e95fbbdad34d45846f) | 15.571 | 2 | 1 |
| [0x4f87de7d21aef48090958f7342e1f69dff790545](https://etherscan.io/address/0x4f87de7d21aef48090958f7342e1f69dff790545) | 11.338 | 2 | 1 |
| [0x9a3569c7053f9fb5abeb7ccb1678bd33c47ad278](https://etherscan.io/address/0x9a3569c7053f9fb5abeb7ccb1678bd33c47ad278) | 11.002 | 1 | 1 |
| [0x5cede91b3c5783d093b2f6c29cb2571a11204b27](https://etherscan.io/address/0x5cede91b3c5783d093b2f6c29cb2571a11204b27) | 9.264 | 3 | 1 |

Addresses are not labelled carry traders solely because they borrow stablecoins against ETH. Known vaults can be traced through their contracts, but unknown borrower purpose and beneficial ownership are unresolved. The sample cannot replace a full holder or borrower census.

## Fluid: leverage outside Liquid ETH

Using Fluid's captured resolver balance, a one-percentage-point increase in debt APR reduces annual equity return by approximately 6.7582 percentage points if balances and asset income stay fixed. A uniform 1% markdown in gross assets reduces resolver net equity by approximately 7.7593%. These isolated illustrations exclude lender-income offsets, rebalancing and transaction execution.

## Evidence and remaining work

Inputs and their SHA-256 hashes are recorded in the [calculation dataset](../../../data/eth/presentation_analysis.json). New historical permission reads retain their request URL, payload, block and response hashes. The frozen financial series have not been refreshed.

The additions explain growth arithmetic, fee history and selected permissions. They do not close independent portfolio backing, transaction-level investor flows, a full holder census, realized fee-adjusted investor cash P&L, or executable liquidation and exit simulation.
