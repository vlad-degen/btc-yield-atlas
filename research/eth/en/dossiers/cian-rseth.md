# CIAN rsETH Yield Layer

Snapshot: 2 October 2026, 23:59:59 UTC. This dossier covers the Ethereum vault `0xd87a19ff681ae98bf10d2220d1ae3fbd374ade4e`, verified against the [official CIAN contract registry](https://docs.cian.app/yieldlayer/for-builders-developer-documentation/yield-layer-contracts). CIAN's other vaults and chains are separate products.

## What the product is

The vault accepts rsETH, a liquid restaking token, and aims to increase returns by borrowing and reinvesting against staking or restaking collateral. CIAN calls this recursive restaking, or RR. The [core concepts](https://docs.cian.app/yieldlayer/for-users-quick-start/core-concepts-and-yield-layer-page-overview) distinguish it from recursive staking. Both involve repeating a collateral, borrowing and reinvestment cycle.

The contract registry includes Aave, Compound, converters and newer components that operate across chains. This shows which integrations exist today. It does not establish how the portfolio was allocated in the past. Income can include the underlying staking return and the spread between reinvestment income and borrowing costs. The amount attributable to each source remains unverified.

## Size and share accounting

At T, `asset()` returns rsETH. Book assets are approximately 1,416.5594 rsETH, with 1,477.3937 shares outstanding. Price per share (PPS) is approximately 0.958823231 rsETH/share. A return measured in rsETH can differ from the return measured in ETH because rsETH's ETH conversion rate also changes.

The historical rsETH oracle accessed through LRTConfig was checked at 33 points. At T, `rsETHPrice` is approximately 1.081227340 ETH.

The latest dated adapter observation reports approximately $6.718M of CIAN ETH-family exposure. Protocol-wide total value locked (TVL) is substantially larger and includes BTC and dollar products. For example, `LFBTC-CIAN-ETH` is a BTC product deployed on Ethereum. ETH in a network label does not make ETH the underlying asset.

## What the return history shows

Assets per share fell 0.2105% over 365 days and 4.1177% over 730 days when measured in rsETH. Applying the historically verified rsETH-to-ETH conversion produces ETH book returns of 2.2455% and 1.0854%, respectively. These returns are materially below the growth in plain rsETH conversion over the same periods.

This comparison does not capture complete investor profit and loss. Points, distributions, migrations and fees still need to be reconciled with the addresses entitled to receive them. The shortfall cannot be attributed to a single event without evidence of the relevant positions and transactions.

The period includes the 2026 rsETH bridge incident. PPS and oracle history do not measure discounts in secondary markets or the recovery terms available to holders on each chain.

## Fees and how investors exit

Current [fee documentation](https://docs.cian.app/yieldlayer/for-users-quick-start/fees) discloses an 8% performance fee and a 0.02% exit fee. Displayed annual percentage yield (APY) is net of performance fees. These are the published current terms; the complete historical fee series has not been reconstructed. The API distinguishes the published exit-fee policy from an actual contract override through `fee_info.exit_override`. That override has not been verified for this rsETH vault, so 0.02% is a policy assumption in the illustration.

The general guide estimates about five days for a receipt-token withdrawal. Conversion of the resulting rsETH into ETH is a separate step. Published architecture uses multisig allocation and batch withdrawal processing; exact pause, upgrade, fee-setting and timelock rights still need contract-level checks. [Terms, control and primary sources](../PRODUCT-TERMS.md).

An investor's exit may require a CIAN withdrawal, repayment of portfolio debt and redemption of rsETH. Liquidity or restrictions on another chain can add a further delay. A positive oracle conversion rate does not guarantee prompt recovery of ETH.

## What is verified and what remains open

Vault identity, book metrics at fixed blocks and PPS returns over matching periods are verified. Strategy allocation, an independent asset-and-debt balance sheet, reward ownership, historical rates and permissions, and a simulated redemption remain open.

Data: `vault_registry_rpc_T.json`, `vault_history_rpc.json`, `rseth_benchmark_rpc.json`, `rseth_oracle_identity.json`, `vault_history_comparison.json`.
