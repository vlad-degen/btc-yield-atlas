# Экономика, предельная ёмкость и стрессы

Срез T — 2 октября 2026, 23:59:59 UTC. Здесь отделены contract state, model sensitivity и ещё не выполненная execution simulation.

## ETH loops: небольшой spread усилен большим плечом

Для модели берём trailing-30d staking log return, annualized в APR, плюс текущий collateral supply APR. WETH debt использует instantaneous variable borrow APR на T. Это смешанное proxy-окно для разбора экономики, без claims о будущей или исторически реализованной прибыли. Rewards, management/performance fees и execution costs исключены.

| Account | L | Staking + supply APR proxy | WETH borrow APR на T | Модель return на equity | Borrow uplift до zero return | Uplift до исчезновения loop excess |
|---|---:|---:|---:|---:|---:|---:|
| aave | 13.325 | 2.328% | 2.074% | 5.455% | 44.3 bp | 25.4 bp |
| spark | 9.762 | 2.248% | 1.907% | 5.232% | 59.7 bp | 34.1 bp |

Даже при positive staking APR усиленная стратегия теряет привлекательность при десятках basis points дополнительного debt cost. Эти thresholds относятся к выбранной модели. Variable rate может изменяться вместе с supply yield, staking yield, utilization и размером позиции.

## Rate shocks на фиксированном equity

| Account | +25 bp | +50 bp | +100 bp | +300 bp |
|---|---:|---:|---:|---:|
| aave | 2.374% | -0.707% | -6.870% | -31.519% |
| spark | 3.042% | 0.852% | -3.529% | -21.052% |

Main Aave +100 bp даёт −12,3245 п.п. годового дохода на account equity и около −2,3136 п.п. на Liquid ETH book NAV до возможных offsets. Изолированный shock нельзя складывать с изменённой lender income, не выполнив полный asset/debt look-through.

## Доступный debt asset и закрытие

| Account | Main WETH debt | WETH reserve cash | Cash / debt |
|---|---:|---:|---:|
| aave | 410,134.20 | 269,693.45 | 65.76% |
| spark | 31,042.02 | 116,147.84 | 374.16% |

Aave reserve cash меньше WETH долга main loop. Одновременный полный repayment через один flash loan только этого резерва ограничен наблюдаемым cash. Это не доказательство невозможности выхода: возможны другие lenders, собственная ликвидность, collateral redemption и поэтапные операции. Spark cash больше долга этого account, но eligibility, caps и route не симулированы.

Ставки прочитаны через 15-word legacy getReserveData layout. WETH cash измерен `balanceOf(aTokenAddress)` на том же fixed block, а debt — balance соответствующего variableDebt token. Max withdraw/flashloan зависит также от paused state, reserve rules и исполнения.

## Oracle, market discount и stable debt

| Account | HF на T | Изолированный oracle markdown до HF=1 | Borrow +100bp: изменение return equity |
|---|---:|---:|---:|
| main_aave | 1.02708 | 2.637% | -12.325 п.п. |
| main_spark | 1.03615 | 3.488% | -8.762 п.п. |
| drone_aave | 1.39045 | 28.081% | -1.355 п.п. |
| drone_spark | 1.87192 | 46.579% | -0.814 п.п. |

Для ETH debt LST/ETH oracle markdown важнее ETH/USD direction. У stable debt падение ETH/USD действует на HF через collateral value, если stable loan и LT фиксированы. Drone Aave при −20% ETH collateral shock сохраняет HF около 1,112; при −40% HF около 0,834. Это arithmetic sensitivity, без фактического liquidation quote и rebalancing.

DEX discount отдельно меняет исполнимую стоимость выхода. В Aave weETH CAPO source не обязан отслеживать DEX discount. Для principal-only estimate 1% markdown всего collateral уменьшает account equity примерно на L%; точные smart collateral/LP изменения требуют пересчитать pool reserves и liquidity ranges.

## Carry: риск кредита и связанных денежных потоков

Dollar-leg loss проходит в ETH book NAV через долю инвестора и ETH conversion. Self-credit diagnostics 8,709 млн RLUSD и 4,759 млн PYUSD показывают связанность borrower и lender потоков; они не являются доступной кассой и не удваивают активы. Curator fees 10%/15% на конкретных carry vaults могут удерживаться даже когда часть borrower payments возвращается собственному инвестору.

Для PRIME/PYUSD проверенное market utilization около 91,8%, для weETH/RLUSD около 88,3%. Current outstanding loan и наличная supply liquidity различаются. Recovery collateral с внебиржевой кредитной зависимостью нельзя считать мгновенной ликвидностью ETH.

## Capacity: чего пока нельзя утверждать

Предельная ёмкость не равна protocol TVL. Для E3 минимум определяется LST liquidity/redemption, ETH borrow liquidity, caps, HF и допустимым drawdown. Для E4 добавляются USD borrow capacity, destination yield cap, credit terms и redemption duration. Для E9 — hedge open interest, funding curve, venue margin и custody limits.

Полная stress execution пока открыта: архивные executable DEX quotes, flash-loan eligibility, redemption queue throughput, liquidation transactions, bridge settlement delay и rates/funding paths на 7/30/90 дней. Таблицы выше сохраняют model assumptions и не подменяют эту проверку. Данные: `loop_economics_T.json`, `lending_reserve_T.json`, `stress_scenarios.json`.
