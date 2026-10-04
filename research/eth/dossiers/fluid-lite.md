# Fluid Lite ETH

Срез: 2 октября 2026, 23:59:59 UTC. Продукт V2: `0xa0d3707c569ff8c87fa923d3823ec5d81c98be78`, Ethereum. V1 `0xc383…` хранится отдельно как legacy, а USD vault исключён из ETH product NAV.

## Identity и accounting

`asset()` на T возвращает stETH. Shares имеют 18 decimals; `totalAssets()` — около 77 364,030578 stETH, supply 63 315,850950 shares, `convertToAssets(1e18)` — около 1,2218746083 stETH. StETH rebases: assets/share уже отражает увеличение количества stETH. Второе умножение этого ряда на staking APR задвоило бы income.

Proxy маршрутизирует function selectors к модулям. На T `getSigsImplementation(getNetAssets.selector)` указывает на ViewModule `0x9fb2fdc9f64c1fd7aabede5d3f0a5bca9402451f`; его verified source прочитан. ABI DummyImplementation используется только как интерфейс, не как доказательство исполнения методов.

## Баланс и источник дохода

`getNetAssets()` возвращает 600 256,387051 gross assets и 522 808,544153 debt в приведённых ETH/stETH единицах. Net после revenue — 77 359,338125; revenue — 88,504772. Равенство `gross−debt−revenue=net` проверено. Contract valuation предполагает parity stETH/eETH/WETH и применяет LST conversion; market discount здесь не отражён.

Collateral/net leverage около 7,7593×, aggregate debt ratio 87,1103%, настроенный aggregate maximum 92%. Это не HF и не обещанный liquidation threshold. Состав resolver включает Aave V3, Spark, Fluid и Lido-market accounts; часть legacy components имеет лишь dust. В наиболее крупном Aave component присутствуют weETH и wstETH против WETH debt. Разные площадки используют общие LST backing и ETH liquidity.

Продукт усиливает staking/lending spread и использует LP components. Текущие [официальные риски](https://lite.guides.instadapp.io/information/risks) описывают refinancing, deleveraging и losses при slippage. Исторические статьи про V1 или запуск V2 не считаются доказательством текущих fee/strategy settings.

## Доход и выход

По archive PPS: 365 дней 3,5096% в ETH, 730 дней 8,8243%, двухлетний годовой эквивалент 4,3189%. Это +3,3368 п.п. к stETH за 730 дней. Liquid ETH сильнее на последнем году, Fluid Lite — на полном двухлетнем окне. Внешние KING/points и withdrawal costs в comparison не включены.

На T `getWithdrawFee(1 stETH)` равен 0,0005 stETH: 0,05%, или 5 bps. `allocationToTeamMultisig()` и maximum allocation возвращают 0. Другие governance permissions из этого не следуют. Для большого выхода нужны available ETH liquidity, корректное deleveraging, Lido redemption и проверка route-specific fees.

## Предел проверки

Разница book totalAssets и resolver net около 4,6925 stETH ещё не объяснена отдельным fee/queue ledger. История состава, executed withdrawal и полный governance role history не восстановлены. GetNetAssets — сильнее маркетингового TVL, но не независимая рыночная NAV сверка.

Данные: `fluid_lite_balance_T.json`, `segment_checks_T.json`, `vault_history_comparison.json`, `vault_history_rpc.json`, raw `fluid_net_module_abi`. Скрипты: `segment_checks.py`, `package_metrics.py`, `vault_history_analyze.py` в `tools/eth/`.
