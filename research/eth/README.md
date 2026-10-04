# ETH yield research

Первый подробный исследовательский выпуск на 3 октября 2026. Основной срез T — 2 октября, 23:59:59 UTC. Историческое окно — 24 месяца. Исследование уже содержит данные, contract checks и выводы; полный market-wide net sizing ещё открыт.

Начать с [основного отчёта](MARKET-RESEARCH.md). Он объясняет структуру рынка, carry/loop mechanics и главные findings, с явным различием book NAV, gross deployments и unique underlying.

| Материал | Содержание |
|---|---|
| [Market tables](MARKET-TABLES.md) | все 57 candidate chains, 82 dated protocol observations и return comparison |
| [WETH lending markets](LENDING-MARKETS.md) | fixed-block claims, debt, cash, deficit и borrower concentration на главных сетях |
| [History](HISTORY.md) | сопоставимый ETH wealth chart, два года returns и protocol trends |
| [Mechanics](MECHANICS.md) | staking, restaking, ETH loops, USD carry, basis, PT, LP и options |
| [Economics](ECONOMICS.md) | break-even, rate/HF shocks и debt liquidity |
| [Dependencies](DEPENDENCIES.md) | nested receipts, общий custody, carry credit и self-credit |
| [Evidence](EVIDENCE.md) | claim ledger и семантика подтверждений |
| [Audit](AUDIT.md) | source limitations, checks и local reproduction |
| [Execution status](EXECUTION-CHECKLIST.md) | выполненные и открытые пункты фаз |
| [Research plan](RESEARCH-PLAN.md) | полный исходный phased scope |

## Досье

| Продукт / сегмент | Глубина этого выпуска |
|---|---|
| [ether.fi Liquid ETH](dossiers/etherfi-liquid-eth.md) | fixed-block shares, accounts, partial balance sheet, carry, LP, history, fees/governance |
| [Concrete ETH](dossiers/concrete-eth.md) | mint/holder provenance, общий Safe, private accounting и overlaps |
| [Fluid Lite](dossiers/fluid-lite.md) | gross/debt/net, fees и исторический ETH book return |
| [Treehouse tETH](dossiers/treehouse-teth.md) | IAU denomination, historical conversion и exit terms |
| [CIAN rsETH](dossiers/cian-rseth.md) | receipt vs ETH returns, historical oracle, rewards/recovery gaps |
| [Carry credit](dossiers/carry-credit.md) | RLUSD/PRIME allocations, borrowers, fees и связанные lender/borrower потоки |
| [Liquid Monad](dossiers/liquid-monad.md) | nested Accountant, sole holder, разные книги сетей и remote gap |
| [Staking/restaking](dossiers/staking-restaking.md) | native root, overlap, receipt accounting и rsETH incident |
| [Lending/LP](dossiers/lending-lp.md) | плательщики income, selected borrower scan, NFT principal и debt |
| [JustLend Tron](dossiers/justlend-tron.md) | mapped ETH address identity, utilization и public API reconciliation |
| [Ethena basis](dossiers/ethena-basis.md) | конкретный ETH leg, hedge/custody mechanics и disclosure boundaries |
| [Pendle PT](dossiers/pendle-pt.md) | expiry cohorts, redemption unit и отличия liquidity от principal |

Semantic data находятся в `data/eth`, collectors/build tools — в `tools/eth`, raw evidence — в `raw/eth/2026-10-02`. Original BTC project outputs не изменены. Воспроизводимость: `python3 tools/eth/rebuild.py` из корня проекта; см. Audit для runtime и raw handoff.
