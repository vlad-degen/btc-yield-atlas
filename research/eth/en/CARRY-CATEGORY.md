# ETH dollar carry: products, positions and history

Financial snapshot: **2 October 2026**. Eight examined books have current, historical or declared carry links. A carry route retains ETH-family exposure, incurs dollar debt and deploys the financing to income-generating assets. Dollar-financed ETH liquidity is shown as its own subtype. An ETH loan used to buy more staking exposure is a loop; an offsetting ETH short is basis. Debt with no evidenced income destination is financing, not confirmed carry.

## Status and attributable capital

| Product | Whole book ETH | Status | What is established |
| --- | --- | --- | --- |
| Concrete Delta weETH | 307,363 | Declared arbitrage; shared custody | Dollar debt is observed in a shared Safe; assets and debt attributable to Delta are unresolved. |
| ether.fi Liquid ETH | 177,171 | Active hybrid | Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled. |
| Lido Earn ETH | 83,309 | Active hybrid | Earn ETH reports 83,309 ETH. Its main holding is stRATEGY, whose book must not be added again. The nested portfolio owes about 355,217 WETH in staking loops and 25.55M USDT in its main dollar-carry account. Those are gross loans, not the carry sleeve’s equity. |
| Avant avETH / savETH | 12,583 | Active hybrid | The published 29 September portfolio has a $33.18M net NAV and a $32.53M savUSD position. Ethereum reads at T confirm USDC, USDS and PYUSD borrowing against ETH collateral. The large own-credit destination makes this a concentrated issuer dependency. |
| YieldBasis WETH | 10,426 | Active dollar-financed LP | Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate. |
| Rocksolid rETH | 9,728 | Closing; nested carry | 728.48 ETH of Liquity shares is the evidenced nested carry claim; direct Aave debt is zero. |
| Liquity ETH Carry | 6,014 | Active minted-dollar LP | Ebisu collateral, ebUSD debt and dollar LP positions are measured; do not equate collateral with sleeve equity. |
| Makina DETH | 2,499 | Active hybrid | DETH reports 2,499 ETH in a cached book. Its hub has 15,065 WETH of Aave debt against weETH, plus a Morpho USDT / wstETH carry route. Verified accounting instructions identify the credit receipts instead of relying on the vault name. |
| Vesper vaETH | 1,052 | Active hybrid | vaETH reports 1,052 ETH. Its XY strategy supplies 57.35 WETH, owes 68,998 DAI and holds 60,034 vDAI shares. Other strategies in the same pool are lending or liquidity positions, so the whole pool cannot be labelled carry. |
| Royco ETH | 116 | Loan traced; parent marks stale | Morpho PYUSD debt and the senior credit receipt are traced; parent accounting and immediate exit remain restricted. |
| TAU InfiniFi ETH Carry | 82 | Historical; dust debt at T | Accrued debt is 0.022132 USDC at T; the old whole book is not current active carry equity. |
| Reservoir ETH Yield | 24 | Small current nested savings | Outer dollar borrowing and borrowing inside the savings destination are distinct liabilities. |
| ZenSats wstETH | 1 | Active micro-position | The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category. |

The gross sum is **610,368 ETH** of overlapping sample book claims. Concrete and Liquid represent **79.38%** of that sample. These are not market size or concentration. Concrete's shared borrowing account cannot be assigned to Delta; Rocksolid's 728.48 ETH Liquity claim overlaps the underlying Liquity book. Current TAU debt is dust. YieldBasis net equity, actual crvUSD debt and staked gauge rights are different measurements.

## Two years of product development

The stacked bars show 24 month-end observations for all thirteen books; a small-book zoom uses the same records. Missing observations remain absent. Current labels are not historical allocation weights. Share issuance, staking conversion, portfolio movements and discovery coverage can change book NAV without outside deposits or new carry capital.

Liquid is the early large hybrid. Rocksolid and Reservoir acquire material books in September 2025, and Concrete's issued claim appears in December. Liquity becomes funded in March 2026; YieldBasis WETH is funded by May. TAU reduces its dollar liability and Rocksolid enters Closing on 29 September. These dates describe observed books and route changes.

## Carry variants

The examined routes include dollar lending, nested savings borrowing, senior credit, minted-dollar stablecoin LP, dollar-financed ETH LP and a manager's declared neutral arbitrage. Fixed-maturity and cross-chain destinations need separately verified loans and positions. ZenSats documents an active wstETH / LlamaLend / Curve / StakeDAO route and a legacy withdraw-only Aave / RAAC route; the active book is a measured micro-position and the legacy book has zero assets and share supply at T. Lido Earn, Avant, Makina DETH and Vesper are included after tracing dollar loans and investments. Their large ETH loops and nested books remain separate from dollar carry. YO ETH lends and allocates ETH receipts without a traced own dollar loan, so it stays outside the carry census. [Route decisions](CARRY-COVERAGE-AUDIT.md).

## Return and profit

The main comparison uses one 30-day ETH book window. Historical carry-only profit is not independently isolated for the whole sample. Four financed investment lots and two flow-adjusted dollar claim / funding ledgers provide measured economics; their results cannot be scaled into market-wide carry returns. [Common returns and funded results](BRIEFING.md).

## Sources

[Status and capital CSV](../../../data/eth/carry-status-and-capital.csv), [24-month product ledger](../../../data/eth/reader_analysis.json), [deep product evidence](CARRY-PRODUCTS.md), [nested routes](CARRY-VARIANTS-EXPANSION.md), [capital and exits](CAPITAL-INCOME-EXIT.md).
