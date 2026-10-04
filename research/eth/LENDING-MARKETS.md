# WETH lending: размер выбранного сегмента и проверка баланса

Срез T: 2 октября 2026, 23:59:59 UTC. Охват: Aave V3 Ethereum, Base, Arbitrum, Optimism и Spark Ethereum. Addresses получены из primary address book и сверены `getReserveData` на fixed block; WETH cash, aToken claims и debt token supply прочитаны на том же блоке.

## Сколько требований и долга

| Протокол / сеть | Lender claims, WETH | Outstanding debt, WETH | Reserve cash, WETH | Supply APR на T | Borrow APR на T |
|---|---:|---:|---:|---:|---:|
| aave / ethereum | 2,084,173.40 | 1,761,598.49 | 269,693.45 | 1.490% | 2.074% |
| spark / ethereum | 608,325.69 | 492,183.60 | 116,147.84 | 1.466% | 1.907% |
| aave / optimism | 8,517.63 | 6,274.08 | 2,243.49 | 1.127% | 1.801% |
| aave / base | 85,371.09 | 70,588.44 | 14,783.07 | 1.453% | 2.067% |
| aave / arbitrum | 95,030.48 | 57,608.71 | 7,623.32 | 1.088% | 2.112% |

Выбранные пять markets имеют **2,881,418.29 WETH lender claims** и **2,388,253.31 WETH outstanding debt**. Cash — 410,491.18 WETH. Это gross lending-claim segment: его нельзя складывать с LST backing или выдавать за уникальный ETH yield капитал.

Main Liquid ETH account создаёт **23.28%** variable WETH debt Aave Ethereum и **6.31%** variable WETH debt Spark. Доли относятся к одному проверенному borrower account, без добавления всех потенциально связанных borrowers. Это прямая связь demand for ETH loans с managed yield loop.

## Reserve deficit и claims не равны cash + обслуживаемый debt

| Сеть Aave | getReserveDeficit(WETH), WETH | Deficit / lender claims | Claims − cash − debt, WETH |
|---|---:|---:|---:|
| ethereum | 52,964.453913 | 2.5413% | 52,881.463992 |
| optimism | 0.076433 | 0.0009% | 0.050285 |
| base | 0.001238 | 0.0000% | -0.412268 |
| arbitrum | 29,835.199567 | 31.3954% | 29,798.450998 |

Aave Ethereum показывает 52 964,453913 WETH reserve deficit; Arbitrum 29 835,199567 WETH. Это значения контрактного getter на T, а не цифры, выведенные только из расхождения двух subtotal. В Optimism/Base значения малы. Spark аналогичные getters в проверенных RPC responses недоступны; ему не присвоен нулевой deficit.

[Определение Aave v3.3](https://github.com/aave-dao/aave-v3-origin/blob/main/docs/3.3/Aave-v3.3-features.md) описывает reserve deficit и permissioned механизм его уменьшения с burn aTokens. Сравнение claims−cash−debt не обязано точно равняться stored deficit: присутствуют treasury accounting, accrued indexes, виртуальные balances и rounding. Здесь разница с getter сохранена, не насильно сведена к нулю.

Deficit / claims — показатель состояния reserve accounting, **не доказанный haircut держателя aToken**. Recovery assets, внешние компенсации и механика дальнейшего погашения должны быть учтены отдельно. Наличие normal APR или восстановление операционной ликвидности не доказывает, что deficit ledger уже очищен.

## Incident attribution и предел вывода

[Aave service-provider report от 20 апреля](https://governance.aave.com/t/rseth-incident-report-april-20-2026/24580) описывает переход bridge incident rsETH в WETH borrowing exposure на Ethereum/Arbitrum и сценарии покрытия. [Майский update Aave Labs](https://governance.aave.com/t/al-development-update-may-2026/25013) сообщает о ликвидациях, recovery guardian и восстановлении ETH liquidity. Эти disclosures дают контекст; каждый outstanding deficit на T ещё не привязан здесь к полному event-level recovery waterfall.

Поэтому исследования только staking APY или isolated smart-contract risk недостаточно: качество receipt/bridge collateral способно повлиять на reserve, где lender держит WETH. Отдельно нужно анализировать доход, cash для withdrawals, debt collectability и право на recovery. Не следует интерпретировать указанные текущие состояния как прогноз потерь или как законченный аудит Aave.

Данные и полные request/response pairs: `weth_lending_markets_T.json`; итоговые числа — `weth_lending_summary_T.json`. Getters проверяются на fixed block каждой сети; historical borrowed state не заменён current UI.
