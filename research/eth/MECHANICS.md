# Откуда берётся доход ETH и как устроен carry trade

Дата исследования: 3 октября 2026. Формулы ниже — модели для анализа, а не обещания дохода. Числа из контрактов относятся к T = 2 октября 2026, 23:59:59 UTC; условия из документации могут быть текущими.

## Сначала валюта результата

Доходность ETH-продукта измеряется количеством ETH, которое приходится на долю. Рост ETH/USD не является доходом стратегии. Для долларового продукта пересчёт иной:

`1 + R_ETH = (1 + R_USD) × P_ETH_start / P_ETH_end`.

Если долларовый портфель заработал 5%, а ETH подорожал на 30%, его результат в ETH равен −19,23%. Поэтому sUSDe и ETH vault с долларовым carry-рукавом нельзя сравнивать только по цифре APY. В первом случае инвестор держит USD exposure; во втором ETH-залог может сохранять ETH exposure, пока заёмные доллары работают отдельно.

Опубликованный PPS также отличается от реализованного вывода. Из него нужно вычесть applicable exit fees, slippage, стоимость погашения долга, bridge и время без дохода. Rewards вне PPS учитываются отдельно; непогашенные points имеют нулевой реализованный денежный доход.

## Staking и restaking

В staking плательщики — Ethereum consensus issuance и пользователи execution layer через tips/MEV. Validator expenses, provider fees, downtime и penalties уменьшают результат владельца. Это базовая экономика E1.

stETH отражает доход через rebasing balance; wstETH — через изменение количества stETH на одну долю. При расчёте нельзя одновременно прибавлять rebase stETH и рост wstETH/stETH. Для weETH применяется проверенный `getRate()`; дополнительные распределяемые rewards не обязательно входят в этот курс. [Lido wstETH](https://docs.lido.fi/contracts/wsteth/) описывает устройство обёртки.

Restaking E2 добавляет услуги безопасности другим системам. Экономически новый доход появляется, когда AVS или другой заказчик платит за услугу. Повторная запись того же ETH в EigenCloud и LRT-provider сама по себе дохода и нового капитала не создаёт. Здесь отдельно проверяются slashing conditions, economic beneficiaries rewards и срок выхода. Суммирование Lido, EigenCloud, Kelp, Aave и vault поверх этих активов даёт несколько записей одной цепочки backing.

## ETH debt loop: усиление staking spread

Последовательность E3: внести LST → занять ETH/WETH → купить или выпустить LST → добавить его в залог. Flashloan может выполнить несколько шагов одним действием; он не меняет конечную экономику.

В единицах ETH обозначим залог `C`, долг `D`, equity `E=C−D`, плечо `L=C/E`. При staking rate `s` и ETH borrow rate `b`:

`r_equity ≈ L × s − (L−1) × b − fees − execution costs`.

Пример: L=5, s=2,5%, b=2%. До расходов получается 4,5%; при b=3% — всего 0,5%. Положительная staking ставка не гарантирует положительный loop. Без дополнительных rewards break-even равен `b* = (L × s − fees − costs)/(L−1)`.

У Liquid ETH основной Aave-account на T имеет L=13,3245. Рост ETH borrow rate на 1 п.п. даёт около −12,3245 п.п. годового результата на equity этого account при фиксированных балансе и остальных ставках. На общий book NAV vault тот же изолированный расход составляет около −2,3136 п.п.; это не прогноз всего портфеля. Supply rates, rewards, rebalancing и иные доходы способны измениться вместе с borrow rate.

ETH/USD падение само по себе обычно не ухудшает отношение LST-залога к ETH-долгу пропорционально такому падению: обе стороны переоцениваются. Риск возникает при относительном LST/ETH markdown, изменении oracle/LT, процентах на долге и нехватке ликвидности ETH для погашения.

`HF = oracle_collateral × LT / oracle_debt`. При фиксированных debt и LT запас относительного markdown равен `1−1/HF`. Это oracle threshold. Рыночный discount может первым проявиться через unwind cost, даже если oracle использует redemption rate и HF пока не меняется. В Liquid ETH Aave weETH oracle на T читает capped `weETH.getRate()`, что проверено по deployed source.

## Carry под ETH-залог со стабильным долгом

Последовательность E4: внести ETH/LST → занять USDC/RLUSD/PYUSD → вложить заём в долларовую стратегию → направлять net profit на ETH-учёт продукта. Конечные плательщики могут быть трейдерами, заёмщиками Morpho, операторами Cap или заемщиками вне крипторынка.

У такого рукава две разные задачи. Долларовая инвестиция должна заработать больше стоимости USD займа; ETH-залог должен пережить падение ETH/USD до момента возврата долларовых средств. Dollar strategy может быть нейтральна к рынку, а collateral account всё равно ликвидируем.

При исходном ETH-залоге `C_ETH`, цене `P`, займе `B_USD`, dollar yield `y`, borrow rate `b` и доле использованных средств `u` дополнительный income в ETH примерно:

`profit_ETH ≈ B_USD × (u × y − b − costs_USD_per_debt) / P_conversion`.

Если dollar assets сохраняют principal, их следует включать в баланс вместе с USD liability. Equity отдельного collateral account `C×P−B` не равно equity всего carry-портфеля, куда входит и вложенный USD principal. Именно поэтому account leverage и product leverage показываются раздельно.

Пример модели: ETH-залог $100, USD debt $60, все заёмные средства инвестированы. y=6%, b=4%, costs=0,5% на debt дают $0,90 годового дополнительного дохода, или 0,9% первоначального ETH collateral value при постоянной цене. Если utilization инвестиций лишь 60%, net spread становится отрицательным: 0,6×6%−4%−0,5%=−0,9% на debt.

Capacity определяется минимумом: collateral cap, доступный USD loan, yield deployment cap, redemption liquidity и лимиты управляющего. Рост TVL может уменьшать spread: borrow demand повышает b, а приток supply снижает y. Нельзя масштабировать текущий APY на неограниченный капитал.

Проверенный путь Liquid ETH включает weETH/RLUSD debt и senRLUSDv2, а также PRIME/PYUSD debt и senPYUSDPRIMEv2. RLUSD-vault на T размещает около 52,89% book assets в kBTC/RLUSD market и 24,09% в weETH/RLUSD. Это кредитный collateral risk BTC и ETH внутри продукта с ETH-учётом, без утверждения о прямой длинной позиции vault в BTC.

## Spot + short futures: dollar basis trade

Другой смысл carry — купить ETH/LST и открыть short ETH derivative равного delta notional. Он сохраняет преимущественно USD value, а не ETH upside. Для линейного short perp приблизительная экономика:

`r_USD ≈ staking_income + short_funding − financing − trading − custody − hedge_tracking_cost`.

При положительном funding платят longs; при отрицательном short платит. Для dated futures доход — зафиксированный basis между entry spot и futures settlement, если hedge удержан до settlement. Funding не является гарантированным fixed yield и не равен collateral return.

[Текущая модель Ethena](https://docs.ethena.fi/backing-assets/crypto-basis-trade) использует такие hedges. [Protocol Revenue](https://docs.ethena.fi/backing-assets/protocol-revenue) также включает lending, RWA и liquid stablecoin income. Размер USDe нельзя целиком приписывать ETH basis. В публичной таблице 3 октября ETH legs составили около $374,44 млн из crypto basis $928,89 млн; это post-T UI observation, а не независимая custody сверка.

Нейтральность совокупного delta не устраняет требования к margin на конкретной venue. При росте ETH spot-side gains и short-side losses могут находиться у разных counterparties и не успеть переместиться. Off-exchange custody уменьшает один вид риска, но оставляет settlement, legal claim, venue liquidity и операционную зависимость. [Ethena Funding Risk](https://docs.ethena.fi/protocol-overview/risks/funding-risk) описывает отрицательный funding и изменение allocation; прошлые средние не используются как current forecast.

## Lending, PT, LP и options

В E5 источник дохода — borrower interest за вычетом reserve/curator fees и кредитных потерь. ETH supplier и ETH collateral borrower — разные экономические роли. Lending yield сравнивается с тем же staking benchmark, а не прибавляется к staking независимо от underlying. Unutilized liquidity может иметь почти нулевой base income; JustLend ETH на Tron — количественный пример.

В E6 PT покупает определённый redemption unit со скидкой к maturity claim. Для цены p в той же unit и d дней до expiry: `APY_implied ≈ (1/p)^(365/d)−1`, если maturity payout действительно равен единице этой unit. PT-wstETH у Pendle обещает stETH accounting unit: нельзя подставлять «1 wstETH» или «1 ETH» без conversion rules. SY, PT и YT — decomposition одного underlying; PT+YT нельзя считать двумя новыми депозитами. После maturity principal claim не исчезает, а YT обычно прекращает будущие accruals. Early exit зависит от AMM depth. [Pendle PT mechanics](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT) — первичная механика; наш отдельный каталог сохраняет expiry и accounting asset.

В E7 LP получает trading fees и, иногда, incentives. Для ETH/stable pool доход включает изменение directional exposure и impermanent loss. LST/ETH pair уменьшает валютный разрыв, но несёт depeg и range risk. Concentrated position может выйти из range и перестать получать fees. Imaginary reserves в Fluid — расчётный инструмент ценообразования, не реальные активы. Liquidity principal, unclaimed fees и debt учитываются отдельно.

В E8 option premiums оплачиваются контрагентом за передачу ему payoff. Covered call ограничивает upside; short put принимает downside. Premium не равен risk-free yield. Для ETH-return comparison нужно оценивать весь payoff и collateral consumption, а не только поступившую премию. Размер E8 в этом выпуске ещё не подтверждён контрактным каталогом.

## Что стрессуется в любом продукте

| Шок | Что пересчитывать | Почему одного APY недостаточно |
|---|---|---|
| Rewards/points выключены | base income − debt − fees | incentivized spread может исчезнуть |
| Borrow rate +1/+3 п.п. | debt service, supply income response | плечо усиливает небольшой rate gap |
| LST market discount 1/3/5% | исполнимый unwind NAV | oracle и DEX могут расходиться |
| Oracle markdown/LT change | HF и liquidatable amount | действует другая цена, чем на DEX |
| ETH/USD −20/−40% | stable-debt collateral HF | neutral USD sleeve не спасает ETH collateral |
| Credit loss 1/5/10% | underlying claim и equity | dollar strategies могут не вернуть principal |
| Funding отрицателен 7/30/90 дней | margin, reserve depletion, hedge carry | среднегодовое значение скрывает кассовый разрыв |
| Queue/bridge задержка | время до debt repayment и ETH payout | capital solvent может быть illiquid |
| Массовый withdrawal | ликвидность по каждому debt asset | суммарная USD ликвидность не заменяет нужный ETH/RLUSD |

Model sensitivities сохранены в `data/eth/stress_scenarios.json`. Полный исполнимый стресс с DEX quotes, liquidation paths и очередями пока не построен; его нельзя подменять арифметикой фиксированных балансов.
