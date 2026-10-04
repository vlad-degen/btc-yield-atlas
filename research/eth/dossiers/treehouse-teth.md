# Treehouse tETH

Срез: 2 октября 2026, 23:59:59 UTC. Share token Ethereum: `0xd11c452fc99cf405034ee446803b6f6c1f6d5ed8`.

## Identity и баланс

На T `asset()` — `0x1b6238e95bbcabee58997c99badd4154ad68ba92`, InternalAccountingUnit_wstETH. Это виртуальная unit, не физический wstETH inventory. `getUnderlying()` у tETH и IAU возвращает wstETH; denomination исторически проверена на всех 33 выбранных archive points. Proxy implementation на T также сверена через EIP1967 slot.

Book totalAssets около 19 860,3799 IAU, supply 19 711,9957 tETH; PPS около 1,007527608 IAU/share. Независимое backing находится в strategy vault, lending positions, внешних receipts и withdrawal claims. Summing IAU balances с этими активами задваивает требования.

Adapter history содержит как collateral, так и отрицательный WETH debt. ETH-family selector также может пропустить неизвестный receipt KPKWSTETH: такое исключение сохраняется как coverage gap, а не как отсутствие актива. Full protocol TVL включает tAVAX/tHYPE и не равен tETH NAV.

## Механика и income

[Yield optimization](https://docs.treehouse.finance/protocol/tasset/architecture/yield-optimization) описывает LST collateral, ETH borrowing и reinvestment в LST, плюс incentives. Это ETH debt loop E3. Base staking и market-efficiency spread нужно считать отдельно; points не получают денежной оценки до реализации.

По опубликованному book PPS и wstETH conversion: 365 дней 2,7845% в ETH, 730 дней 6,2761%, annualized двухлетнее 3,0903%. Рост tETH/IAU без underlying staking за 730 дней всего 0,7475%. Excess к stETH — около 0,7885 п.п. за всё двухлетнее окно, до расходов выхода и внешних rewards.

## Fees и redemption

[Fee policy](https://docs.treehouse.finance/protocol/tasset/architecture/fees) указывает 20% performance fee на положительный market-effective yield, а не автоматически на всю staking доходность. Fastlane fee — 0,5%. Датированные параметры конкретного route ещё не сверены со всеми deployed contracts.

[Redemption process](https://docs.treehouse.finance/protocol/tasset/architecture/redemption-process) различает Curve swap в пределах governance band, normal redemption ориентировочно за семь дней и limited fast route. Normal route имеет 5 bps charge и формулу minimum rates между initiation и claim; итог может быть ниже front-end estimate. Документация содержит неоднозначные числа в worked example, поэтому они не скопированы в расчёт.

При двухлетнем excess yield около 0,79 п.п. fast exit fee 0,5% способен поглотить большую его часть. Реальная разница зависит от срока, route и слippage; это сопоставление масштаба расходов, не рекомендация продукта.

## Предел проверки

Book denomination доказана, физическое backing ещё не полностью reconciled. Нужны NAV registry/strategy graph, pending Lido requests, economic ownership external vaults, route simulation и исторический debt ledger. Данные: `treehouse_denomination_history.json`, `vault_history_comparison.json`, `vault_registry_rpc_T.json`, raw `tree_*`.
