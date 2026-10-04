# Concrete ETH vaults

The [final capital, income and exit findings](../CAPITAL-INCOME-EXIT.md) add a conditional shared-custody attribution range, eliminate the internal sibling receipt and test epoch requests against snapshot demand. Original figures below retain their original reconstruction scope.


Snapshot: 2 October 2026, 23:59:59 UTC. Public interfaces were captured on 3 October. The main finding is that reported assets under management (AUM), issued accounting shares and verified external deposits are different measures. Two ETH products execute through one Safe wallet. Its complete value and the holders' economic rights have not been reconstructed.

## Products and how they aim to earn income

| Product | Vault | Book assets at T |
|---|---|---:|
| ctDeltaWeETH | `0xb9dc54c8261745cb97070cefbe3d3d815aee8f20` | 278,170.834213 weETH |
| ctwstETH Plus | `0xd57588c73715b65e0ead36ae06c15644169501b7` | 36,439.686407 wstETH |

The [public Concrete catalogue](https://app.concrete.xyz/earn) displays approximately $823M for WeETH Vault, with permissioned access and a private annual percentage yield (APY). Its overview describes borrowing stablecoins against weETH and investing the proceeds in delta-neutral arbitrage. Delta-neutral means the trading position aims to limit its sensitivity to market prices. It does not remove the liquidation risk of the ETH collateral.

The captured interface disclosed a seven-day withdrawal delay and yield eligibility after 30 days. These are dated interface observations. The overview does not verify execution or the complete list of trading venues. Final income payers, realized strategy returns and investor fee allocation remain unverified.

At capture time, the public API estimates approximately $823.925M and $121.685M for the two products. These are current estimates, not valuations at T. Both vaults return 1e18 underlying liquid staking tokens (LSTs) from `convertToAssets(1e18)` at T. A flat share conversion does not prove zero investor yield: the LST itself accrues staking income, while external payouts and contractual rights remain unknown.

## Shared custody and control

Proxy implementations at T were checked through EIP1967 implementation slots. They are ConcreteInitMintableAsyncVaultImpl for ctDeltaWeETH and ConcreteAsyncVaultImpl for ctwstETH Plus. Each `getDeallocationOrder` returns one MultisigStrategy.

| Vault | Strategy |
|---|---|
| ctDeltaWeETH | `0xc8ea269d4dba296f7fbba812905c1b2efe5dbe1c` |
| ctwstETH Plus | `0x50a7510e73d79d60823dcac50e6b2c62e89ed82b` |

Both `getMultiSig` calls return `0x7ee29373f075ee1d83b1b93b4fe94ae242df5178`. At T, this Safe has five owners and requires three signatures. An independent borrower scan also identifies it as the largest examined Morpho wstETH/USDT borrower, with approximately $70.4M debt in the current API. This corroborates multiple credit positions under one control point. It does not restore that debt at T.

At T, its Aave position has approximately $503.453M collateral, $105.736M debt, $397.716M equity and a health factor (HF) of 3.82219. No active Spark position was found. These values cannot be allocated proportionally between the vaults or treated as their combined net asset value (NAV). The Safe holds other assets and claims and may serve other products.

## How the reported asset value is maintained

MultisigStrategy uses `totalAllocatedValue` and methods that adjust accounting value. At T, `getLastUpdatedTimestamp` is 16 December 2025 for the weETH strategy and 9 February 2026 for wstETH. Their accounting-validity periods are 300 days and approximately 83.3 years, respectively.

These periods are contract settings, not the frequency of independent verification. Funds can move and allocated balances can change separately from the accounting timestamp. A fresh dollar quote for an LST does not refresh the original accounting mark. `totalAssets` does not automatically equal assets that can be sold at market prices minus all debt.

## What the ctDeltaWeETH issuance establishes

The complete available 47-log page contains an UnbackedMint event for 278,170.834213 shares on 16 December 2025. This equals the entire supply at T. In the [issuance transaction](https://etherscan.io/tx/0xce658f57edc490798ddc55e3f67169e3190fe23afe50a4ce4ca411d0714edada), the shares first go to the manager and then to `0x5bab73f561a5365c9e4bbc7c52fe0fa384fcf324`. The reconstructed share ledger confirms that this single holder owns the entire supply at T.

Verified `unbackedMint` code allows VAULT_MANAGER to mint only when supply and the deposit limit are zero, without transferring underlying assets. The event therefore does not prove that 278,000 weETH was deposited in that transaction. It could represent an existing or migrated portfolio. Establishing the economic basis of the initial accounting value requires further reconstruction.

The function name and lack of a transfer do not, by themselves, prove that the product has no backing. Equally, the reported $823M cannot be described as new external ETH deposits solely from total value locked (TVL) or share supply. The original portfolio's assets, liabilities, sole holder's rights and external strategy terms must be established. For now, the product is reported managed AUM with backing verification open.

## Why ctwstETH Plus must be consolidated with the Safe

At T, the shared Safe owns all 36,439.686407 ctwstETH Plus shares. February 2026 Deposit events identify the Safe as both sender and owner. The vault allocates value to MultisigStrategy, which names the same Safe as manager.

Adding these shares to the Safe assets that back them would count the same value twice. The shares are not separately verified external deposits without evidence of beneficial claims. Public holder lists also cannot rule out external investors who hold contractual economic rights.

## Findings for colleagues

1. Different underlying and share tokens share custody and execution. Product names alone do not establish diversification between managers.
2. Book AUM, external deposits and unique underlying capital measure different things. The initial ctDeltaWeETH mint makes the distinction clear.
3. A dollar-neutral investment does not remove ETH collateral drawdown, stablecoin borrowing costs or delays in recovering cash.
4. Public APY comparison is unavailable. Return analysis needs contractual payouts and NAV history; a 1:1 LST conversion is insufficient.
5. Safe-level net assets cannot be allocated arbitrarily to individual vaults. Separate accounting records and debt ownership are needed.

## Exit and remaining evidence

The captured withdrawal delay is a policy observation, not an independently tested exit. Current permissioned-product guidance assigns lockups, cooldowns, gates and fees to each investor's specific agreement. A shared 3-of-5 Safe describes technical control; it does not establish the investor's legal claim or withdrawal right. [Current guidance and evidence boundary](../PRODUCT-TERMS.md). Remaining checks include the Safe balance sheet across material chains, Morpho liabilities at T, external dollar investments, the source of the original ctDeltaWeETH assets, holder identity and rights, other vault claims held by the Safe, historical accounting adjustments, and executed exits.

The T ledger confirms one positive ctDeltaWeETH share holder and reconciles to supply. Beneficial ownership, investor agreements and attributable custody backing remain unresolved. ctwstETH Plus 100% self-holding is independently verified through `eth_call`. See the [ranked carry-product review](../CARRY-PRODUCTS.md) for the updated holder evidence.

Artifacts: `data/eth/vault_registry_rpc_T.json`, `governance_T.json`, `concrete_lookthrough_T.json`, `concrete_self_holdings_T.json`; raw keys `concrete_holders`, `concrete_logs`, `concrete_multisig_strategy_abi`, `concrete_vault_api`, `concrete_ui_observation.json`. Current explorer labels were not the sole evidence of the implementation at T.
