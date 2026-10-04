# Этапы исследования ETH: фактический статус

Обновлено 3 октября 2026 после первого исследовательского выпуска. `[x]` означает выполненный конкретный пункт, а не завершённую целиком фазу. Полный дизайн: [RESEARCH-PLAN.md](RESEARCH-PLAN.md).

## Подготовка и фаза 0 — методология

- [x] Изучен BTC проект, сохранены inventory и code/research index.
- [x] Зафиксированы ETH-long и USD-neutral segments, E1–E9 taxonomy.
- [x] Определены unique underlying, external equity и gross deployment; составлены шесть net-accounting examples.
- [x] Выбран T, 24 месяца, benchmarks и правила fees/rewards/points.
- [x] Проверены block boundaries Ethereum, Base, Arbitrum, Optimism; дополнительно Monad для nested sleeve.
- [x] Созданы config/schema и read-only raw collector с URL/time/request/hash.
- [ ] Восстановлен полный native consensus balance на T. Header finalized получен, historical state недоступен использованным public endpoints.

## Фаза 1 — ether.fi Liquid ETH: значительная часть пилота выполнена

- [x] Проверены vault/Accountant/Teller identities, Ethereum/Optimism supply и burn/mint source.
- [x] Проверены controlled managers, Drone и current governance timelock 24h.
- [x] Восстановлены main/Drone Aave/Spark accounts, Morpho markets, carry receipts, LP NFTs, withdrawal claim.
- [x] Собран partial balance sheet $460,231m против book NAV $472,684m; residual $12,453m явно сохранён.
- [x] Найдены собственный Accountant и ETH denomination Liquid Monad; разные rates Ethereum/Monad проверены.
- [x] Восстановлены 719 Accountant events, historical PPS, own Optimism rates и 24 monthly points.
- [x] Разделены published return, UI estimate, fees и external rewards.
- [ ] Полностью восстановлены remote Monad backing и in-flight bridge messages.
- [ ] Замкнуты remaining assets/reward ownership/fee growth/Morpho interest и независимый NAV без residual.
- [ ] Проверены actual redeem/repay paths execution simulation и все historical role changes.

## Фаза 2 — широкий universe готов, исчерпывающий product catalog открыт

- [x] Screen: 5 688 ETH-family pools / 197 feed projects / 57 chains.
- [x] Deep shortlist: 87 protocol sources; 259 material pools ≥ $5m.
- [x] Основные четыре сети включены; десять крупных candidate chains и critical dependencies выделены.
- [x] Созданы selected asset/product registries; BTC/USD negative controls сохранены отдельно.
- [x] Полностью paginated Pendle listing выбранных четырёх сетей: 626 markets, ETH subset 126.
- [x] Опубликованы source coverage, missing observations, dated/current boundary и adapter caveats.
- [ ] Полностью reconciled address-based ETH capital каждого крупного protocol/chain.
- [ ] Полный исторический universe закрытых/мигрировавших продуктов и E8 options catalog.

## Фаза 3 — выбранный look-through готов, market-wide netting открыт

- [x] Проверены 31 selected ownership/control/claim/debt relationship.
- [x] Раскрыты carry collateral portfolios, supply shares и self-credit diagnostics.
- [x] Concrete sole holders/common Safe подтверждены на T; external provenance не подменён TVL.
- [x] Выполнен ограниченный Morpho screen: 25 markets, 237 positions, 213 unique borrowers.
- [x] Fixed-block WETH lending claims/debt/cash получены для Aave четырёх сетей и Spark.
- [x] Вычислена концентрация Liquid ETH main borrower в Aave WETH variable debt: 23,28%.
- [ ] Полные Aave/Morpho borrower censuses, цели каждого займа и ultimate holders.
- [ ] Замкнуты issuer/bridge/receipt edges и additive unique-underlying/external-equity totals.

## Фаза 4 — history dataset и сравнение дохода готовы, attribution открыт

- [x] Восстановлены 2 088 protocol-month rows, включая 247 missing, для 24 месяцев.
- [x] Сопоставлены шесть ETH book return series на 365/730-дневных окнах.
- [x] Проверены historical Treehouse denomination и CIAN rsETH oracle identity.
- [x] Отдельно показаны первый/второй годы, fee changes и Pendle maturity cohorts.
- [ ] Полные historical holdings/debt/rewards/migrations всех выбранных продуктов.
- [ ] Декомпозиция flows vs income vs price vs adapter changes по всему рынку.

## Фаза 5 — 12 досье опубликованы с разной глубиной подтверждения

- [x] Liquid ETH, Concrete, Fluid Lite, Treehouse, CIAN rsETH.
- [x] Carry credit, Liquid Monad, staking/restaking, lending/LP.
- [x] JustLend Tron, Ethena basis и Pendle PT.
- [x] Основные риски, fees/redemption conditions и limitations явно описаны.
- [ ] Все досье имеют independent backing reconciliation и полный realized cash P&L.
- [ ] Все yield paths подтверждены до конечного плательщика onchain/offchain credit ledger.

## Фаза 6 — economics и contract-state стресс готов, execution стресс открыт

- [x] Разделены ETH loop, ETH collateral/USD carry и spot/short basis.
- [x] Построены frozen-position rate shocks, break-even и oracle HF thresholds.
- [x] Измерены debt-asset cash и существующие Aave WETH reserve deficits на T.
- [x] Выход Aave main loop сопоставлен с cash резерва; cash не назван guaranteed flashloan capacity.
- [x] Выделены credit loss, funding, depeg, queue/bridge и связанность cash flows.
- [ ] Полные DEX/liquidation/redemption/debt-repayment simulations и historical funding/rate paths.
- [ ] Предельная ёмкость и общие counterparties всего рынка количественно reconciled.

## Фазы 7–8 — первый синтез и integrity проверка выполнены

- [x] Report, market tables, history chart, mechanics, economics и dependencies опубликованы.
- [x] Claim ledger связывает выводы с semantic inputs и raw responses.
- [x] Сохранён raw manifest; local rebuild прошёл без network refresh.
- [x] Проверены единицы, timestamps, supply/NAV арифметика, token order, source hashes и ссылки.
- [x] Все 384 original BTC files проверены как неизменённые.
- [x] Unknown totals и gaps опубликованы в [AUDIT.md](AUDIT.md).
- [ ] Итоговый полный net market sizing и execution audit завершены.

Следующие обязательные work packages: native/issuer backing census → address graph крупнейших lending/bridge/receipt слоёв → полный borrowers/holders scan → remote/private residuals → execution stress и cash-flow attribution. Это продолжение уже собранных данных, а не повторение первоначального плана.
