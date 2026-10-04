# Treehouse tETH

Snapshot: 2 October 2026, 23:59:59 UTC. Ethereum share token: `0xd11c452fc99cf405034ee446803b6f6c1f6d5ed8`.

## What the product is and how it earns income

tETH uses liquid staking tokens (LSTs) as collateral, borrows ETH and reinvests in LSTs. Repeating this cycle increases exposure to the spread between staking income and borrowing costs. The [yield optimization documentation](https://docs.treehouse.finance/protocol/tasset/architecture/yield-optimization) also describes incentives. This is the ETH debt loop classified as E3 in the research.

Underlying staking income and the additional borrowing spread need separate measurement. Points are given no cash value until they are realized.

## What the shares represent

At T, `asset()` returns `0x1b6238e95bbcabee58997c99badd4154ad68ba92`, named InternalAccountingUnit_wstETH. This internal accounting unit (IAU) is a virtual measure of value, not a physical wstETH balance.

`getUnderlying()` on both tETH and the IAU returns wstETH. This denomination was verified at all 33 selected archive points. The proxy implementation at T was checked through its EIP1967 slot.

Book `totalAssets` is approximately 19,860.3799 IAU, supply is 19,711.9957 tETH, and price per share (PPS) is approximately 1.007527608 IAU/share. The assets backing those shares sit in strategy vaults, lending positions, external receipts and withdrawal claims. Adding IAU balances to these assets would count the same value again.

Adapter history includes collateral and negative WETH debt. The ETH-family selector can miss an unidentified KPKWSTETH receipt. This is a coverage gap, not evidence that assets are absent. Protocol-wide total value locked (TVL) also includes tAVAX and tHYPE, so it differs from tETH net asset value (NAV).

## What the return history shows

Published PPS combined with wstETH conversion gives a 365-day ETH return of 2.7845%, a 730-day return of 6.2761%, and a two-year annualized return of 3.0903%. Without the underlying staking conversion, tETH/IAU growth is only 0.7475% over 730 days.

Excess return over stETH is approximately 0.7885 pp over two years, where pp means percentage points. This comparison excludes withdrawal costs and external rewards.

## Fees and how investors exit

The [fee policy](https://docs.treehouse.finance/protocol/tasset/architecture/fees) charges 20% of positive market-effective yield. It does not automatically charge the fee on all staking income. The Fastlane fee is 0.5%. Dated route settings have not been reconciled against every deployed contract.

The [redemption terms](https://docs.treehouse.finance/protocol/tasset/architecture/redemption-process) describe three routes: a Curve swap within a governance-set band, normal redemption taking approximately seven days, and a fast route with limited capacity. Normal redemption charges 5 bp, meaning basis points. Its payout uses the minimum-rate formula between initiation and claim, so the final amount can fall below the front-end estimate.

The documentation's worked example contains inconsistent numbers and was excluded from the calculation. A 0.5% fast-exit fee can consume much of the approximately 0.79 pp excess earned over two years. The actual result depends on the holding period, exit route and slippage. This compares the size of the cost with the return; it is not a product recommendation.

## Why the exit route changes the comparison

Applying the current 0.5% Fastlane fee once to the 365-day book return produces an illustrative return of 2.2706%, below stETH's 2.4785% over the same dates. Over 730 days, the corresponding result is 5.7447%, still 0.2572 percentage points above stETH. The calculation compounds the fee with the closing balance rather than simply subtracting it from the return. Capacity, execution prices, waiting time and the benchmark's own exit costs are excluded. [Side-by-side exit illustration](../RETURN-DRIVERS.md).

The current published Curve routing band is zero to 50 wstETH. Governance can change it. The published governance timelock is five days, shorter than the approximate seven-day normal redemption. Notice alone therefore does not guarantee that an investor can complete the standard exit before a change takes effect. This is a comparison of documented timings, not a claim that a harmful change occurred. [Routing, governance and source dates](../PRODUCT-TERMS.md).

## What is verified and what remains open

The book denomination is verified. The physical assets backing the shares are not fully reconciled. Remaining work includes tracing the NAV registry and strategy relationships, pending Lido requests, economic ownership of external vaults, exit-route simulation and historical debt.

Data: `treehouse_denomination_history.json`, `vault_history_comparison.json`, `vault_registry_rpc_T.json`, raw `tree_*`.
