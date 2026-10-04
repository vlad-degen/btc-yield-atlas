# ETH credit expansion: actual markets and borrower destinations

Financial snapshot: 2 October 2026, 23:59:59 UTC. Discovery and source capture took place on 4 October. Contract balances use the frozen blocks; the older borrower ranking is explicitly a 3 October API sample.

This expansion adds 131 credit-market rows beyond the selected Aave/Morpho economics screen. It identifies real deployed routes and three historical credit-to-yield sequences. It does not establish a complete global carry market or resolve the beneficial owners of the large unknown addresses.

## What was measured

| Protocol | Registry coverage | ETH/USD route result | Capital interpretation |
|---|---|---|---|
| Compound V3 | 11 official dollar-base deployments on Ethereum, Base, Arbitrum and Optimism | All 11 read at the frozen block, including the three repaired Arbitrum archive reads; collateral deposits, caps and rates measured | Total base debt includes non-ETH collateral |
| Euler | 889 Ethereum and 432 Base factory proxies; every underlying asset read | 213 Ethereum and 123 Base canonical-dollar vaults screened; 79 have ETH collateral in their lists | Whole loan-vault debt is not allocated to ETH borrowers |
| Fluid | All 182 Ethereum and 50 Base registered vaults decoded | 41 routes include ETH and dollar assets; 31 have simple dollar debt and exclusively ETH-family collateral | Pair-specific debt can be measured; smart debt shares cannot be called dollars |
| Silo V2 | Current Ethereum factory: 37 configs and 74 assets; Base/Optimism current factories: no existing configs in the examined range | No canonical ETH/USD pair in this factory generation | Legacy V1 and historical Arbitrum state remain outside coverage |

The Euler list is permissionless. Of the 79 loan vaults with an ETH collateral entry, 69 have at least one positive ETH borrowing LTV; ten retain ETH entries with borrowing disabled. A factory entry, a familiar symbol or an accepted collateral address does not establish frontend inclusion, manager reputation or a funded strategy. LTVs, rates and decoded caps are included in the JSON so empty and disabled routes can be separated.

## Fluid: a material missing borrowing venue

The 31 simple routes have 76.703 million nominal dollar-token units of debt at T. Ethereum contributes 73.475 million and Base 3.228 million. This subtotal is explicitly denominated in nominal stablecoin units. It is neither a peg-adjusted dollar valuation nor proof that the loans finance carry.

| Chain | Vault ID | Collateral | Dollar debt | Outstanding units | Borrow APR | Borrowable units |
|---|---:|---|---|---:|---:|---:|
| Ethereum | 12 | ETH | USDT | 34,776,740.42 | 6.06% | 17,388,348.40 |
| Ethereum | 11 | ETH | USDC | 32,642,115.27 | 6.20% | 16,321,040.70 |
| Ethereum | 14 | wstETH | USDC | 2,894,431.72 | 6.20% | 6,106,962.71 |
| Ethereum | 15 | wstETH | USDT | 1,753,431.38 | 6.06% | 7,209,822.68 |
| Base | 2 | wstETH | USDC | 1,570,913.23 | 4.25% | 4,651,684.41 |
| Base | 1 | ETH | USDC | 1,502,619.33 | 4.25% | 4,651,684.41 |
| Ethereum | 20 | weETH | USDT | 649,957.85 | 6.06% | 1,888,239.80 |
| Ethereum | 19 | weETH | USDC | 525,896.93 | 6.20% | 2,014,649.56 |
| Ethereum | 54 | ETH | GHO | 208,544.68 | 7.49% | 4,278,511.50 |
| Base | 25 | ETH | GHO | 94,968.54 | 5.86% | 105,002.32 |

The large Ethereum ETH/USDC and ETH/USDT routes account for 32.642 million and 34.777 million units respectively. Older vault generations remain in the factory with small residual balances and restricted borrowing. A protocol count alone would miss the difference between active scale and deployed leftovers.

Fluid rate figures are instantaneous annual borrowing rates. Smart collateral represents LP shares and inventory; smart debt represents debt shares in a DEX. Those rows remain separate from the simple-debt subtotal. Resolver borrowability is a contract limit, not a guarantee of executable liquidity after another transaction.

## Compound and Euler: borrowing routes, not an ETH-only debt total

Compound Ethereum USDC has 346.834 million USDC of total debt, and its USDT market has 145.948 million USDT. These markets accept several collateral assets. Their debt totals must not be added to ETH-only carry capital. The dataset instead lists each ETH-family collateral deposit, oracle value, supply cap, borrowing factor and liquidation factor, alongside the base-market rate.

Euler similarly exposes an ETH borrowing route through a collateral vault accepted by a dollar loan vault. Other accepted collateral can fund the same debt total. The expansion reads each relevant ETH borrowing and liquidation LTV, cash, debt, rate and compressed cap at T. Cap zero means no configured limit; it does not mean a zero borrowing cap. Account-level debt allocation, hooks and other dollar synthetics still require work.

## Seven large unknown dollar borrowers

The original screen used a dollar valuation for every debt currency. That was mistakenly described as dollar borrowing. The largest unknown address, 0x462a, has about $40.585 million of sampled WETH debt valuation against wstETH/weETH. It belongs in the ETH-debt discussion.

Seven unidentified addresses have at least $5 million of sampled stablecoin debt, totaling $85.049 million in the 3 October discovery sample. Their Ethereum Morpho positions were reread at the frozen block. These fixed-T amounts are native debt units derived from stored market debt and shares, rounded up; they exclude interest accruing after each market’s last update. The sample valuation and the fixed-T native amounts remain separate.

| Borrower | Sampled stablecoin debt valuation | Debt assets | Historical credit-to-yield sequences |
|---|---:|---|---:|
| [0xa122687285dc5012141055a801045f069112e7c6](https://eth.blockscout.com/address/0xa122687285dc5012141055a801045f069112e7c6) | $23,532,601.34 | PYUSD, RLUSD, USDC | 2 |
| [0x1778767436111ec0adb10f9ba4f51a329d0e7770](https://eth.blockscout.com/address/0x1778767436111ec0adb10f9ba4f51a329d0e7770) | $17,877,268.00 | USDT | 0 |
| [0xa56da9bb528fedf8379b02e95fbbdad34d45846f](https://eth.blockscout.com/address/0xa56da9bb528fedf8379b02e95fbbdad34d45846f) | $15,571,395.91 | PYUSD, RLUSD | 0 |
| [0x4f87de7d21aef48090958f7342e1f69dff790545](https://eth.blockscout.com/address/0x4f87de7d21aef48090958f7342e1f69dff790545) | $11,337,832.74 | RLUSD, USDT | 1 |
| [0x90882e7c28ddf0ac1177033a310aeed8eff25e90](https://eth.blockscout.com/address/0x90882e7c28ddf0ac1177033a310aeed8eff25e90) | $5,612,115.07 | USDC | 0 |
| [0xaa34d20be3f9623ccf5bff53ef4dfa765c3f5dd5](https://eth.blockscout.com/address/0xaa34d20be3f9623ccf5bff53ef4dfa765c3f5dd5) | $5,599,226.02 | PYUSD, RLUSD, USDT | 0 |
| [0x20f6c325df578a11209817a30ebb2f0d5454176d](https://eth.blockscout.com/address/0x20f6c325df578a11209817a30ebb2f0d5454176d) | $5,518,716.78 | USDC | 0 |

The first four dollar borrowers have up to 250 captured token transfers each. The next three have a first-page discovery sample. Zero-value transfers and unsolicited tokens were excluded from economic inference. An address, its funding counterparty or its use of the same adapter does not identify its owner.

## Two visible credit-to-yield deployment patterns

A122 borrowed 350,000 USDC on 14 September and again on 15 September. Approximately two minutes after each loan, it deposited about 350,000 USDC into **RockawayX f(x) Protocol Ecosystem USDC**, contract `0x2ca22cb25558fa2018ecb1ce4ed8af92ee7ea423`. The receipts record ERC4626 deposits, share issuance directly to A122 and the underlying USDC supplied into Morpho through adapter `0x516ecd770f9b6420e77cedd80ea7052ae65bf835`.

4f87 borrowed 1,000,000 PYUSD on 17 September and deposited 1,000,000 PYUSD into **Sentora Huma PST Main**, contract `0x8381a156958711e230f325428b5eb4b6555c75d9`. The destination minted shares to the same borrower and supplied PYUSD into Morpho through adapter `0x39ad1c6152c09de4598a4f39c7b0a85f7b03326b`. A later same-token transfer repaid another Morpho debt and withdrew collateral, showing that the address also refinances positions.

These are strong historical credit-to-yield sequences. Fungible cash prevents claiming that a specific loan was the exclusive funding source. The beneficial owners remain unknown. More importantly, **both borrowers hold zero direct shares in these destination vaults at T**. The sequences must not be presented as their current carry allocation or as evidence that their whole stablecoin debt is invested in these two vaults.

Morpho’s [official address registry](https://docs.morpho.org/developers/contracts/addresses/) identifies `0x4a6c312ec70e8747a587ee860a0353cd42be0ae0` as EthereumGeneralAdapter1. This identifies execution infrastructure, not the address owner. Event interpretation uses the captured [official EventsLib](https://github.com/morpho-org/morpho-blue/blob/main/src/libraries/EventsLib.sol), including which fields are indexed.

## What remains unresolved

The three Compound Arbitrum archive reads were repaired through a public Blast endpoint at the same frozen block. The follow-up in `CREDIT-EXPANSION-DEEP.md` measures destination redemptions, borrowing cost and residual debt for the three observed lending-to-yield sequences, plus selected Silo V1 routes. Other Silo generations, other dollar synthetics, Euler account allocation and a complete lender/borrower census remain open. Whole-wallet profit and current carry allocation remain unknown. No global ETH-collateral dollar-debt total or coverage percentage is assigned.

## Reproduce and inspect

- [Structured integration dataset](../../../data/eth/credit_expansion.json): markets, borrowers, flow receipts, findings, coverage boundaries and source URLs/hashes.
- [Offline builder](../../../tools/eth/credit_expansion_build.py): rebuilds from retained captures.
- [Read-only collector](../../../tools/eth/credit_expansion_capture.py): explicit historical blocks, immutable response files and a request manifest.
- [Raw capture manifest](../../../raw/eth/credit-expansion-2026-10-04/requests.jsonl): URL, request parameters, capture time, HTTP status, response path and SHA-256.

The frozen market datasets and website were not edited by this expansion.
