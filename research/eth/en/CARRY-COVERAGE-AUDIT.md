# Carry coverage and product decisions

Financial snapshot: **2 October 2026**. Later public discovery locates candidates; contract reads and financial histories use the fixed snapshot.

The saved DefiLlama screen contains 299 ETH-name pools above $5M. A match to an existing parent does not establish a reconstructed strategy or additive ETH capital.

| Product / family | Decision | Evidence |
| --- | --- | --- |
| YieldBasis WETH | Confirmed dollar-financed LP; moved from farming to carry | Actual frozen crvUSD loan, effective supply and fair ETH mark; 24 archive month ends |
| ZenSats wstETH / LlamaLend | Fixed-block dollar funding route confirmed; included in the examined product census. | The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category. |
| ZenSats wstETH / pmUSD | Fixed-block dollar funding route confirmed; included in the examined product census. | The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category. |
| Vesper ETH / stETH / msETH | Fixed-block dollar funding route confirmed; included in the examined product census. | vaETH reports 1,052 ETH. Its XY strategy supplies 57.35 WETH, owes 68,998 DAI and holds 60,034 vDAI shares. Other strategies in the same pool are lending or liquidity positions, so the whole pool cannot be labelled carry. |
| Makina DETH | Fixed-block dollar funding route confirmed; included in the examined product census. | DETH reports 2,499 ETH in a cached book. Its hub has 15,065 WETH of Aave debt against weETH, plus a Morpho USDT / wstETH carry route. Verified accounting instructions identify the credit receipts instead of relying on the vault name. |
| Avant savETH / avETHx | Fixed-block dollar funding route confirmed; included in the examined product census. | The published 29 September portfolio has a $33.18M net NAV and a $32.53M savUSD position. Ethereum reads at T confirm USDC, USDS and PYUSD borrowing against ETH collateral. The large own-credit destination makes this a concentrated issuer dependency. |
| yoETH | ETH pool allocator; dollar-carry allocation unverified | Published design is an ETH-pool basket with operator-reported balances and cash-dependent asynchronous redemptions. A receipt denomination does not prove dollar borrowing. |
| 9Summits Flagship ETH / Lagoon | Staking and DeFi mandate; dollar-carry allocation unverified | ETH denomination, curator and settlement model are documented; no frozen dollar-funded destination ledger is established. |
| Lido earnETH / GGV / stRATEGY | Fixed-block dollar funding route confirmed; included in the examined product census. | Earn ETH reports 83,309 ETH. Its main holding is stRATEGY, whose book must not be added again. The nested portfolio owes about 355,217 WETH in staking loops and 25.55M USDT in its main dollar-carry account. Those are gross loans, not the carry sleeve’s equity. |
| YieldNest ynETHx | Mixed MAX vault; dollar-loan allocation unverified | Restaking and multi-strategy vault design do not establish actual stablecoin debt. |
| Lucidly cyETH | Unverified product claim; excluded from measured carry | Search-indexed official pages claim an ETH carry product. Direct hosts failed DNS and no fixed-T deployed book was verified. Do not assign the sibling cyBTC route or marketing APR. |

| Examined book | Status | Capital convention / boundary |
| --- | --- | --- |
| Concrete Delta weETH | Declared arbitrage; shared custody | Dollar debt is observed in a shared Safe; assets and debt attributable to Delta are unresolved. |
| ether.fi Liquid ETH | Active hybrid | Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled. |
| Lido Earn ETH | Active hybrid | Earn ETH reports 83,309 ETH. Its main holding is stRATEGY, whose book must not be added again. The nested portfolio owes about 355,217 WETH in staking loops and 25.55M USDT in its main dollar-carry account. Those are gross loans, not the carry sleeve’s equity. |
| Avant avETH / savETH | Active hybrid | The published 29 September portfolio has a $33.18M net NAV and a $32.53M savUSD position. Ethereum reads at T confirm USDC, USDS and PYUSD borrowing against ETH collateral. The large own-credit destination makes this a concentrated issuer dependency. |
| YieldBasis WETH | Active dollar-financed LP | Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate. |
| Rocksolid rETH | Closing; nested carry | 728.48 ETH of Liquity shares is the evidenced nested carry claim; direct Aave debt is zero. |
| Liquity ETH Carry | Active minted-dollar LP | Ebisu collateral, ebUSD debt and dollar LP positions are measured; do not equate collateral with sleeve equity. |
| Makina DETH | Active hybrid | DETH reports 2,499 ETH in a cached book. Its hub has 15,065 WETH of Aave debt against weETH, plus a Morpho USDT / wstETH carry route. Verified accounting instructions identify the credit receipts instead of relying on the vault name. |
| Vesper vaETH | Active hybrid | vaETH reports 1,052 ETH. Its XY strategy supplies 57.35 WETH, owes 68,998 DAI and holds 60,034 vDAI shares. Other strategies in the same pool are lending or liquidity positions, so the whole pool cannot be labelled carry. |
| Royco ETH | Loan traced; parent marks stale | Morpho PYUSD debt and the senior credit receipt are traced; parent accounting and immediate exit remain restricted. |
| TAU InfiniFi ETH Carry | Historical; dust debt at T | Accrued debt is 0.022132 USDC at T; the old whole book is not current active carry equity. |
| Reservoir ETH Yield | Small current nested savings | Outer dollar borrowing and borrowing inside the savings destination are distinct liabilities. |
| ZenSats wstETH | Active micro-position | The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category. |

**YO ETH exclusion:** the saved API contains 606 daily TVL observations from February 2025 to T, with the last observation 87.9 seconds before T at 4,955.87 ETH. Archived Ethereum and Base positions show ETH lending / staking allocations, including IPOR and Morpho receipts. No own dollar loan is established in those inspected positions. The global API book and local oracle-valued share books are overlapping claims, not extra capital.

**ZenSats legacy:** the old vault has zero assets and share supply at T. The active deployment is a measured sub-one-ETH book, included as a micro-position.

[Final reconstruction](../../../data/eth/finalization_reconstruction.json), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv), [material-pool dispositions](../../../data/eth/carry-discovery-dispositions.csv).
