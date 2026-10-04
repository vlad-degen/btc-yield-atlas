# What happened after the borrowed dollars entered yield vaults

Financial snapshot: **2 October 2026, 23:59:59 UTC**. Ethereum state is read at block **26,108,081**. The lifecycle transactions occurred in September. Their receipts, block timestamps, state calls, request parameters and source hashes are preserved under `raw/eth/credit-expansion-2026-10-04/deep/`. Source discovery occurred on 4 October; it does not move the financial snapshot.

The three observed lending-to-yield sequences establish a mechanism, not a profitable whole-wallet strategy. The USDC lots earn an allocated **91.840383 USDC** in their destination but incur **239.889887 USDC** of borrowing cost by redemption. The PYUSD vault returns **1.948867 PYUSD** above principal, while repayment and the remaining liability imply **2.347298 PYUSD** of borrowing cost. Neither result includes gas, collateral yield or other positions. Neither borrower's beneficial owner is verified.

## The USDC borrower: a full redemption followed by a confidential wrap

Wallet `0xa122687285dc5012141055a801045f069112e7c6` borrows USDC against OETH in Morpho market `0xb8fef900b383db2dbbf4458c7f46acf5b140f26d603a6d1829963f241b82510e`. The destination is **RockawayX f(x) Protocol Ecosystem USDC**, vault `0x2ca22cb25558fa2018ecb1ce4ed8af92ee7ea423`.

| UTC time | Measured action | Currency or receipt |
|---|---|---:|
| 11 Sep, 15:31:23 | Earlier deposit, before either examined loan | 1,000,000 USDC |
| 14 Sep, 13:42:11 | Morpho loan | 350,000 USDC |
| 14 Sep, 13:43:47 | Deposit, 96 seconds later | 350,000.000100 USDC |
| 15 Sep, 07:49:23 | Second Morpho loan | 350,000 USDC |
| 15 Sep, 07:51:59 | Deposit, 156 seconds later | 350,000 USDC |
| 16 Sep, 13:27:23 | Redeem all shares from the three deposits | 1,700,553.396390 USDC |
| 16 Sep, 13:35:59 | Wrap the full redemption for the same wallet | 1,700,553.396390 USDC |

The deposits use intermediary `0x4a6c312ec70e8747a587ee860a0353cd42be0ae0`. Each receipt shows the same underlying amount moving from the wallet to this intermediary and then to the vault. The vault's Deposit event names the borrower as the share recipient. This proves the deposit route even though the wallet does not transfer the assets directly to the vault.

The receipt also proves the destination mechanism. Adapter `0x516ecd770f9b6420e77cedd80ea7052ae65bf835` supplies the deposited USDC to Morpho lending market `0x17f7ae1b52670010976b3fe41324cbb2b1eb7dd8f492e51764b2828371b86b84`. Its collateral token is `fxSAVE`, named f(x) USD Saving at T, at `0x7743e50f534a7f9f1791dde7dcd89f7783eefc39`. The depositor owns yield-vault shares with loan-supplier exposure. The product name does not establish direct ownership of fxSAVE by this wallet.

The full redemption burns exactly `1,697,605,793,085,194,127,605,948` raw shares, the sum minted by those three deposits. The realised cash income is **553.396290 USDC**, but this includes the earlier 1,000,000 USDC deposit. Treating all of that income as a return on the two loans would overstate the observed carry result. The [redemption receipt](https://etherscan.io/tx/0x324c54a149f5fcdcd2cf22bf1dd338decfb06d767cedb5b5117758f7221430aa) establishes the cash paid.

We allocate the common redemption to the two borrowed lots in proportion to the exact shares each deposit minted. This is an analytical allocation, not two separately observed cash payments. We value each lot's debt shares at the redemption block, including 6,732 seconds of pending interest using the historical interest-rate model and Morpho's rounding rules. The [Morpho borrowing source](https://github.com/morpho-org/morpho-blue/blob/main/src/Morpho.sol) and [interest expansion](https://github.com/morpho-org/morpho-blue/blob/main/src/libraries/MathLib.sol) define that calculation.

| Borrowed lot | Allocated vault income, USDC | Borrowing cost at exit, USDC | Allocated funded result before gas, USDC |
|---|---:|---:|---:|
| 14 September | 59.633841 | 146.057155 | -86.423314 |
| 15 September | 32.206543 | 93.832732 | -61.626189 |
| Combined | 91.840383 | 239.889887 | -148.049504 |

**This is not measured repayment or whole-wallet cash profit.** The loan's borrow shares do not change in the sampled redemption and wrap blocks. At T, the wallet still has `6,090,499,603,936,801,111` debt shares in this loan market. Its stored-market debt value is 6,386,173.443556 USDC, accrued only through the market's last update, 9,432 seconds before T. That loan-market balance is not an allocation of current carry capital.

The [next transaction](https://etherscan.io/tx/0x0bea263b3cee1f5d58d96a5ee5b25d830c8959d01123d58d497ee40b41889328) calls `wrap(address,uint256)` on `0xe978f22157048e5db8e5d07971376e86671672b2`, with the same wallet as receiver and the full redemption as amount. Zama's [official registry and explanation](https://www.zama.org/confidential-tokens) identify this contract as cUSDC and describe encrypted balances and transfer amounts. The underlying read at T is USDC, with a 1:1 wrapper rate. The implementation at T is `0x2abad2203eba104b52cf040cccfa100df15687f8`.

The public trace therefore reaches a measured wrap amount and recipient. A subsequent event census covers this wallet's cUSDC incoming and outgoing transfer events, wraps and receiver-filtered unwraps from that block through T, plus public amount disclosures in the wrapper. All stated queries completed. They find two outgoing encrypted-transfer events, eight incoming events and two public wraps. The second wrap adds **2,002,038.655059 USDC** on 17 September at 12:31:35 UTC. These later flows prevent exclusive attribution of a confidential balance to the original redemption.

Both outgoing events reach `0x11c6acfd368ddfab97d15649eb8043c0197fac4c`, whose verified historical code is a `VaultBatcherConfidentialRouter`. Their receipts show Joined events naming this wallet in batches 3 and 4 across three batcher addresses. The verified `DepositVaultBatcherConfidential` at `0x2deafb36f3b118d434cde4708e8350eae918724d` later emits Quit events for this wallet, with encrypted cUSDC returned from that batcher. Its source and runtime are preserved. The other two batchers' individual roles are not independently verified here.

This is more specific than an unexplained off-wallet transfer: it is visible confidential batch routing with return events. It does not establish a successful yield-share issuance, the amount refunded or the return of every unit from the original wrap. Encrypted handles can represent zero and must not be read as positive token amounts. The census observes no `UnwrapFinalized` event with this wallet as receiver and no `AmountDisclosed` event in this wrapper/window. It does not cover every possible unwrap receiver or disclose confidential balances. Exact allocations still require authorised decryption or a disclosed accounting statement.

At T, the wrapper is unpaused, its pauser address is zero and its global observer list is empty. Its owner is `0xb6d69d5f334d8b97b194617b53c6ab62f8681ef3`. The [control source](https://github.com/zama-ai/protocol-apps/blob/main/contracts/confidential-wrapper/contracts/ConfidentialWrapper.sol) gives the owner powers to configure observers and a pauser, block users and authorise upgrades. An empty observer list is a dated setting, not proof that all decryption access has been audited. The historical implementation bytecode exactly matches the captured explorer-verified runtime.

## The PYUSD borrower: cash returned, but the loan was not fully cleared

Wallet `0x4f87de7d21aef48090958f7342e1f69dff790545` uses weETH collateral in Morpho market `0x85d59152eeeab7ca024804895b358868d8dd1e134171be400d7792d5604a212c`. Its destination is **Sentora Huma PST Main**, vault `0x8381a156958711e230f325428b5eb4b6555c75d9`.

Its deposit receipt supplies PYUSD through adapter `0x39ad1c6152c09de4598a4f39c7b0a85f7b03326b` to Morpho lending market `0xb4977179610abfecfc8b76255a002c16b33f46d077beb86e5911e1fe9ee6e512`. The collateral at T is the PayFi Strategy Token, symbol PST, contract `0x22ae3d9a738471f405169af055d31c687087d4c7`. The observed destination earns through lending PYUSD against this collateral. This borrower receives vault shares, rather than a directly measured PST position.

| 17 September, UTC | Measured action | Amount |
|---|---|---:|
| 13:50:23 | Supply collateral and borrow | 700 weETH; 1,000,000 PYUSD |
| 13:52:11 | Deposit through the same intermediary | 1,000,000 PYUSD |
| 14:16:59 | Redeem every minted vault share | 1,000,001.948867 PYUSD |
| 14:18:11 | Repay and withdraw collateral | 1,000,001 PYUSD; 699.994930347918797441 weETH |

The vault burns all `995,928,814,821,987,126,598,511` raw shares from the deposit. The [repayment receipt](https://etherscan.io/tx/0x1dc143ab1082e0ab4c2e5f94515a6c0ea9e9182c66606ebb8db21c16e7ecfe13) repays fewer debt shares than were created by the loan. In the repayment-block state, `1,323,255,899,504` raw debt shares remain. Their exact upward-rounded value is **1.347298 PYUSD**. The market is accrued through that block's timestamp. Archive calls return end-of-block state; these figures are not claimed to be an intra-transaction trace.

The accounting is:

| Component | PYUSD |
|---|---:|
| Vault income above the deposit | 1.948867 |
| Cash repayment above borrowed principal | 1.000000 |
| Remaining loan liability in the repayment-block state | 1.347298 |
| Total borrowing cost | 2.347298 |
| Cash remaining after repayment | 0.948867 |
| Cash remaining minus the loan liability, before gas | -0.398431 |

The four transactions cost **0.001004596384898971 ETH** in gas, paid by the borrower. We do not convert this to dollars using a different date's ETH price. The position also retains **0.005069652081202559 weETH**. Those collateral units and debt shares persist at T. The stored debt value has grown to 1.350615 PYUSD, with another 5,052 seconds of interest not yet included in the stored market. The direct yield-vault share balance is zero at T.

This is a negative funded result for the observed brief sequence before gas. It is not a whole-wallet profit calculation: collateral income, other positions, rewards and outside costs are not measured here.

## Fees are already inside the observed redemption

Historical getters show a **10% performance fee** for the RockawayX USDC vault and **15%** for the Sentora PYUSD vault, both at exit and T. Both have a zero management fee in those observations. The exact historical runtime bytecode of each vault matches its captured verified source.

[Vault V2's redemption mechanics](https://github.com/morpho-org/vault-v2/blob/main/src/VaultV2.sol) accrue fees by minting shares and use a fee-aware share conversion. In both receipts, actual assets paid equal the conversion and redemption preview in the post-exit block. The measured cash income already reflects the destination's fee treatment. Subtracting 10% or 15% from that income again would double charge it in the analysis. Standard redemption has no additional cash deduction in the verified path; the separately implemented forced-deallocation penalty is a different operation. Vault-wide fee-share mint events are preserved but are not represented as fees attributable solely to these borrowers.

## Selected Silo legacy markets

The official [Silo V1 repository](https://github.com/silo-finance/silo-core-v1) provides an Ethereum repository and lens. Five selected assets were queried at T. Three have a Silo entry; the queried stETH and WETH entries return the zero address.

| Ethereum Silo V1 | XAI bridge debt, XAI units | WETH bridge debt, WETH units |
|---|---:|---:|
| wstETH, `0x4f5717f1efdec78a960f08871903b394e7ea95ed` | 1.796022450478200188 | 0.06157620157332653 |
| rETH, `0xb1590d554dc7d66f710369983b46a5905ad34c8c` | 0 | 0 |
| weETH, `0xcd7ae3373f7e76a817238261b8303fa17d2af585` | 0.000000010000002971 | 0.008411728696407859 |

These are the entire bridge-asset loan balances in the three selected Silos. They are not account-level debt allocated exclusively to ETH collateral. XAI is kept in its own units; no verified peg or oracle dollar conversion is supplied.

The earlier Arbitrum archive errors were repaired using a public Blast endpoint at block 511,139,919. The already identified official V1 repository and lens are deployed and return valid historical state. Four ETH-family assets found in the official Compound Arbitrum collateral routes were queried. The repository returns two nonzero entries, wstETH and ezETH; the queried WETH and tETH entries are zero.

| Arbitrum Silo V1 | Bridged USDC debt, USDC.e units | WETH bridge debt, WETH units |
|---|---:|---:|
| wstETH, `0xa8897b4552c075e884bdb8e7b704eb10db29bf0d` | 60.707049 | 3.1878236824107287 |
| ezETH, `0x4a2bd8dcc2539e19cb97df98ef5afc4d069d9e4c` | 151.627391 | 2.5849533169729755 |
| Selected total | 212.334440 | 5.772776999383704 |

The Arbitrum bridge dollar token is `0xff970a61a04b1ca14834a43f5de4533ebddb5cc8`, with six decimals. Its onchain symbol is USDC; the table labels it USDC.e to distinguish the bridged token from native USDC. These units are not a separately verified dollar-market price.

The previously queried current factory at `0xAFd8F792cb025A76C4916652CfC8e20eee3b6fe2` is also deployed. At T, its next ID is 3014. IDs 3001 through 3013 resolve to 13 configurations and 26 silo assets; ID 3000 is empty. Four configurations pair canonical WETH with native USDC. Their loan state is measured, rather than inferred from the registration count.

| Arbitrum current-factory config | WETH maximum LTV | Liquidation threshold | USDC debt with interest at T | WETH deposits, borrowable plus protected |
|---|---:|---:|---:|---:|
| 3001 | 85% | 90% | 0 | 0.000500 |
| 3003 | 85% | 90% | 0.088410 | 0.000500 |
| 3012 | 80% | 90% | 0 | 0 |
| 3013 | 79% | 80% | 0 | 0 |

The debt getter includes accrued interest; the raw storage value for config 3003 is lower, 0.087751 USDC. The [official Silo interface](https://github.com/silo-finance/silo-contracts-v2/blob/master/silo-core/contracts/interfaces/ISilo.sol) defines the difference, and the [configuration interface](https://github.com/silo-finance/silo-contracts-v2/blob/master/silo-core/contracts/interfaces/ISiloConfig.sol) defines the LTV and threshold fields. Each configuration has a hook receiver, preserved in the structured result; its trust and behaviour are not independently audited here. The other pairs include GM pools, gold, PUSD and test tokens. Their registration does not make them canonical ETH/USD loans.

The selected legacy markets and this current generation therefore have little measured dollar-token debt. This is a scoped observation. Previous factories, other assets, GM pool exposures and account-level allocation remain outside this pass, so it does not establish that Silo's entire market is small.

## Compound archive repair

All three previously failed Compound Arbitrum reads now succeed at the same frozen block. The Ethereum, Base and Optimism chain objects were preserved. The repair supplies the accepted collateral, caps, oracle values, utilisation and rates missing from the original provider responses.

| Compound Arbitrum Comet | Entire base-token debt, token units | Borrow APR at T | Accepted ETH-family collateral, oracle USD value |
|---|---:|---:|---:|
| Bridged USDC | 207,242.256558 | 2.9676% | 60,886.98 |
| Native USDC | 12,413,935.272952 | 3.8407% | 15,139,419.17 |
| USDT | 10,085,436.593709 | 3.3920% | 11,666,219.54 |

The debt columns include borrowers using non-ETH collateral and are not ETH-only borrowing totals. The collateral column measures accepted ETH-family assets deposited in each Comet, valued using that Comet's captured oracle. It does not identify which dollars were borrowed against them or whether their owners used carry. The original missing-trie-node errors were evidence of a provider limitation, not proof that a market was absent. The base expansion now has 131 measured rows at T, including all 11 Compound deployments.

## Reproduction and limits

`data/eth/credit_expansion_deep.json` is the structured result. `tools/eth/credit_expansion_deep_build.py` builds it offline from captures. `tools/eth/credit_expansion_deep_validate.py` verifies source hashes, receipt cash paths, full share burns, historical runtime code, exact debt liability, gas and the accounting distinctions. Its dated output is `data/eth/credit_expansion_deep_validation.json`.

The evidence covers **11 distinct original lifecycle transactions and five additional post-wrap receipts**, three verified historical loan-to-vault sequences, two borrowers, two destination vaults, five selected Silo V1 markets across Ethereum and Arbitrum, and four canonical WETH/USDC routes in the examined current Arbitrum factory. The Compound archive repair also closes three previously unavailable deployments. It establishes useful mechanisms and measured results. It does not establish either borrower's owner, current whole-book carry allocation, whole-wallet profit, a complete confidential flow history or a market-wide carry census. Those values remain unknown in the dataset.
