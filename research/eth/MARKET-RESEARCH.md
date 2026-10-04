# Рынок доходности ETH: первый исследовательский выпуск

Исследование на 3 октября 2026. Основной срез T — 2 октября 2026, 23:59:59 UTC. Историческое окно — 24 закрытых месяца, октябрь 2024–сентябрь 2026; сравнительные окна дохода заканчиваются на T. Этот выпуск содержит реальный сбор данных, проверки контрактов и выводы. Net размер всего рынка и полная сверка каждого портфеля ещё не завершены.

## Главный результат

Рынок ETH yield устроен как несколько слоёв требований на один underlying ETH. Staking receipts попадают в restaking, lending, PT, LP и управляемые vaults; заёмные средства создают новые deployments. Для понимания рынка нужны одновременно unique underlying, external investor equity и gross deployment. Привычная сумма TVL смешивает эти три величины.

Скрининг 16 992 yield pools выделил 5 688 ETH-family кандидатов в 57 сетях и 197 feed projects. Из них 87 протоколов отобраны для более глубокого сбора, 82 имеют token history. 259 пулов показывают full TVL не менее $5 млн. Сумма full-pool TVL кандидатов — $70,939 млрд. Это размер экрана поиска, включая mixed assets и повторный учёт; **он не является net размером ETH yield рынка**. В semantic data неизвестные net totals оставлены `null`.

На уровне отдельных продуктов удалось получить более сильные результаты: восстановлены supply и PPS Liquid ETH на Ethereum/Optimism, долговые accounts и большая часть активов; проверены Concrete custody и создание долей; получены исторические returns Fluid Lite, Treehouse и CIAN; раскрыты кредитные связи carry-рукавов; проверен адресный состав ETH-пулов Tron и актуальный ETH basis leg Ethena.

Выпуск включает 12 досье, 25 claims в evidence ledger и 31 выбранную проверенную связь ownership/claim/debt. Навигация по материалам: [README.md](README.md). [График двухлетнего дохода](HISTORY.md), [экономика и стрессы](ECONOMICS.md), [карта зависимостей](DEPENDENCIES.md) дают отдельные углублённые разрезы.

## Где находится рынок

Обязательный охват — Ethereum, Base, Arbitrum, Optimism. Скрининг также выделил Tron, BNB Chain, Linea, Monad, Polygon и Gnosis. Остальные 47 сетей сохранены в таблице; отсутствие углублённого досье не означает нулевого рынка. Mantle/mETH и sunset networks rsETH учитываются как зависимости даже при небольшом локальном TVL.

| Сеть | Current full-pool TVL выбранных кандидатов | Роль и ограничение |
|---|---:|---|
| Ethereum | $66,462 млрд | staking issuers, lending, carry, основная инфраструктура; сильный overlap |
| Base | $1,319 млрд | lending и LP, большое число малых пулов |
| Tron | $1,289 млрд | один большой пул mapped ETH; backing и доход требуют отдельного анализа |
| BNB Chain | $637,576 млн | ETH representations и DeFi; сеть токена не равна сети валидаторов |
| Arbitrum | $568,131 млн | lending, LP и исторические PT/strategies |
| Linea | $208,053 млн | концентрация в небольшом числе крупных ETH exposures |
| Monad | $127,920 млн | отдельные стратегии и cross-chain claims, в том числе sleeve Liquid ETH |
| Optimism | $96,490 млн | deployment и share circulation нужно различать |
| Polygon | $62,127 млн | lending/LP и bridged asset dependencies |
| Gnosis | $39,790 млн | локальные deployments и wrapped ETH |

Это current discovery после T, без утверждения об одинаковом времени оценки. Все 57 сетей и 82 датированных protocol observations представлены в [таблицах рынка](MARKET-TABLES.md). 93,69% screening sum приходятся на Ethereum, но эту долю нельзя переносить на unique underlying или external equity: staking backing учитывается на Ethereum даже при обращении receipt в другой сети.

Сети различаются по трём признакам: где физически работает backing, где размещена стратегия и где обращается доля. Liquid ETH на T имеет доли на Ethereum и Optimism, а UI размещения показывает Ethereum и Monad. Это один логический продукт с разными картами circulation и deployment.

Native staking имеет другой масштаб и coverage: сохранённая current [страница Ethereum.org](https://ethereum.org/staking/) показывает около 43,87 млн total ETH staked. У показателя не раскрыт пригодный timestamp T, поэтому он служит ориентиром масштаба. Его нельзя заменить суммой LST TVL, validator count × 32 или добавить поверх всех restaking deployments. [Staking/restaking dossier](dossiers/staking-restaking.md) сохраняет границы этой проверки.

## Измеренный WETH lending segment и концентрация спроса

Fixed-block Aave V3 Ethereum, Base, Arbitrum, Optimism и Spark Ethereum содержат **2,881 млн WETH lender claims**, **2,388 млн WETH debt** и **410 491 WETH cash**. Это размер выбранного gross lending-claim segment, с точной contract identity и T каждой сети. Он не является unique ETH market capital: borrowing/deployment создаёт overlap с другими слоями.

Main Liquid ETH account составляет **23,28% variable WETH debt Aave Ethereum**. Следовательно, managed staking loops — материальный конечный источник спроса на ETH loans. Проценты ETH lenders здесь частично оплачены экономикой LST carry; источники yield связаны друг с другом, а не независимы.

Независимая сверка также выявила stored `getReserveDeficit(WETH)` около **52 964 ETH на Ethereum и 29 835 ETH на Arbitrum**. Эти значения относятся к contract state на T. Они не равны установленному haircut инвесторов: нужны recovery assets, treasury accounting и дальнейшие settlement/burn events. [Первичная механика Aave deficit](https://github.com/aave-dao/aave-v3-origin/blob/main/docs/3.3/Aave-v3.3-features.md) отделяет этот ledger от обычных reserve balances.

Операционный APY и cash liquidity не описывают качество всего backing. Точный размер claims, servicing debt, cash, deficit и recovery нужно видеть одновременно. Полные пять markets, source proofs и оговорки — [LENDING-MARKETS.md](LENDING-MARKETS.md). Reserve deficits не используются как объяснение residual Liquid ETH без отдельной связи его claims с этим ledger.

## В каких протоколах и стратегиях

Датированные adapter observations выделяют Lido ($26,677 млрд ETH-family), Binance Staked ETH ($10,081 млрд), Aave V3 ($9,835 млрд), EigenCloud ($7,075 млрд), ether.fi Stake ($5,188 млрд), SparkLend ($4,161 млрд), Sky Lending ($1,639 млрд), Morpho Blue ($1,422 млрд), Rocket Pool ($1,409 млрд), JustLend ($1,310 млрд), Kelp ($1,130 млрд), StakeWise V3 ($1,017 млрд) и Concrete ($953,047 млн). Их нельзя складывать. Это преимущественно наблюдения 2 октября, 00:00 UTC, а не состояния execution block в конце суток.

| Класс | Что создаёт income | Что считать отдельно |
|---|---|---|
| E1 staking | issuance, tips, MEV после расходов | backing ETH, receipt, external rewards |
| E2 restaking | оплата услуг безопасности | stake overlap, AVS rewards, slashing и points |
| E3 ETH debt loop | staking spread на усиленном collateral | ETH debt, rates, oracle и unwind liquidity |
| E4 ETH collateral / USD carry | dollar deployment yield минус USD debt | вложенный USD principal, collateral HF, credit losses |
| E5 lending | проценты заёмщиков | utilized debt, idle liquidity, bad debt |
| E6 PT/fixed yield | discounted maturity claim | redemption unit, expiry, SY/PT/YT overlap |
| E7 LP | trading fees/incentives | principal, range, depeg, debt, fee growth |
| E8 options | передача контрагенту payoff | directional exposure и потери по обязательству |
| E9 spot/short basis | funding или dated futures basis | USD exposure, margin, custody и ETH-only leg |
| EH hybrid | комбинация вышеперечисленного | капитал каждого sleeve и общие counterparties |

Подробные формулы, источники платежей, break-even и stress paths: [MECHANICS.md](MECHANICS.md). E8 пока покрыт механикой и discovery, без доказанного aggregate size.

## Ether.fi: carry и looping работают вместе

На T совокупная published book NAV Liquid ETH равна 177 171,063302 ETH, около $472,684 млн по раскрытой nearest quote T+1 секунда. Восстановленный частичный balance sheet, включая оценку nested Monad claim по его собственному Accountant, даёт $460,231 млн. Остаток $12,453 млн, или 2,634%, сохранён как unresolved; это не установленный дефицит и не доказательство полного backing остальных claims.

UI 3 октября относит 64,66% портфеля к двум carry рукавам и 21,65% к двум явно названным loops. Это post-T веса, не доказанная allocation фиксированного блока. Main Aave account содержит $1,182 млрд weETH collateral и $1,094 млрд ETH debt: net account equity $88,732 млн, плечо 13,325×, HF 1,02708. Spark-loop имеет плечо 9,762× и HF 1,03615.

У Aave HF чувствителен к capped conversion oracle, а не автоматически к каждому движению DEX weETH/ETH. Поэтому «запас 2,64%» относится к oracle markdown при неизменных долге и LT. Рыночный discount отдельно увеличивает стоимость unwind. Stable-debt Drone accounts имеют иной стресс: падение ETH/USD может ухудшить HF, даже когда dollar leg рыночно нейтрален.

В frozen-position модели, использующей trailing-30d staking APR proxy и actual WETH borrow APR на T, main Aave loop достигает zero return уже при росте borrow rate примерно на **44 bp**, до fees/rewards/costs. Его WETH debt 410 134 units превышает cash Aave WETH reserve 269 693 units. Поэтому полный выход одним flash loan только из этого резерва ограничен наблюдаемым cash; другие источники и поэтапный unwind остаются возможны. Это quantified capacity constraint, не прогноз дохода и не доказательство невозможности выхода.

За 730 дней published PPS Liquid ETH вырос на 6,8501%, stETH benchmark — на 5,4875%. Преимущество составляет 1,3626 п.п. за всё окно; annualized rates — 3,3683% и 2,7071%. Значительная техническая сложность даёт измеримый, но сравнительно небольшой excess return. Последний год сильнее первого; current состав сам по себе не объясняет историческую разницу.

Полное досье с fee changes, governance, LP, withdrawal queue и ограничениями: [etherfi-liquid-eth.md](dossiers/etherfi-liquid-eth.md).

## Carry оказался связан с BTC collateral и реальным кредитом

По адресным контрактным проверкам senRLUSDv2 — USD lending portfolio, а не ETH-only источник процентов. На T его book assets около 444,242 млн RLUSD. Около 52,89% размещены в kBTC/RLUSD, 24,09% в weETH/RLUSD, 7,23% в USDe/RLUSD. Есть cbBTC, syrupUSDC, FXRP и другие markets. У Liquid ETH claim на 55,105 млн RLUSD, около 12,40% book assets этого vault.

senPYUSDPRIMEv2 имеет book assets около 219,084 млн PYUSD, из которых около 95,04% — supply PRIME/PYUSD. Liquid ETH владеет claim на 49,605 млн PYUSD, около 22,64%. PRIME связывает этот источник дохода с финансированием home-equity credit, описанным в [первичном case study Sentora](https://sentora.com/case-studies/sentora-s-prime-main-vault-reaches-200m-in-pyusd-deposits-in-under-100-days). Credit underwriting, redemption и ликвидность collateral здесь важнее Ethereum blockspace demand.

Одновременно главный vault и его LoanManager занимают в тех же weETH/RLUSD и PRIME/PYUSD markets. Look-through через владение долями и supply/borrow shares даёт экономическое self-credit notional около 8,709 млн RLUSD и 4,759 млн PYUSD. Эти величины не добавляются в NAV и не являются измеренным interest income. Они показывают, почему часть потоков borrower interest возвращается инвестору через принадлежащий ему supply portfolio. Это снижает независимость cash flows и требует считать внешний net income после curator fees и debt costs.

Мы исследуем ETH yield продукты; BTC и RWA здесь остаются необходимыми риск-зависимостями их dollar legs. Отдельного нового исследования BTC рынка этот выпуск не делает. Подробнее: [carry-credit.md](dossiers/carry-credit.md).

## Concrete меняет интерпретацию TVL

Два ETH vault связаны с одним 3-of-5 Safe. У ctDeltaWeETH весь supply 278 170,834213 долей создан одним первоначальным `UnbackedMint` 16 декабря 2025; на T он полностью находится у одного адреса. Весь supply ctwstETH Plus на T принадлежит общему Safe, который управляет и backing portfolios.

Это может отражать миграцию существующего портфеля и внутреннюю структуру владения. Сами события не доказывают отсутствие экономического backing. Однако приблизительно $953 млн опубликованной ETH-family NAV нельзя считать доказательством новых внешних депозитов и складывать со всеми assets управляющего Safe. Flat PPS также не доказывает нулевой пользовательский yield, поскольку private terms/distributions не раскрыты.

Верный следующий шаг — восстановить происхождение портфеля, права владельцев и долю backing, относящуюся к каждому vault. Проверенный анализ: [concrete-eth.md](dossiers/concrete-eth.md).

## Доход и условия выхода меняют рейтинг продуктов

На одинаковом 730-дневном окне Fluid Lite ETH показывает 8,8243% ETH book return, Liquid ETH 6,8501%, Treehouse tETH 6,2761%, stETH 5,4875%, weETH 5,2947%, CIAN rsETH 1,0854%. Это сравнение цены доли, без внешних rewards, exit costs и доказательства исполнения полного withdrawal. За последние 365 дней Liquid ETH опережает Fluid Lite: 3,8700% против 3,5096%. Рейтинг зависит от окна.

Fluid Lite имеет на T около 600 256 ETH-equivalent gross assets и 522 809 debt; net после revenue около 77 359 ETH-equivalent, плечо 7,759×. Источники используют parity assumptions stETH/eETH/WETH, поэтому это contract valuation, не market NAV. GetWithdrawFee для 1 stETH возвращает 0,0005 stETH, то есть 5 bps.

У Treehouse внутренний `asset()` — IAU_wstETH, а не физический wstETH. Исторический `getUnderlying()` подтверждает wstETH denomination. Рост tETH/IAU за два года всего около 0,7475%; вместе с wstETH/ETH это 6,2761%. По [условиям redemption](https://docs.treehouse.finance/protocol/tasset/architecture/redemption-process) standard route занимает ориентировочно семь дней и имеет 5 bps charge с дополнительной формулой minimum rates; fast route стоит 0,5% при доступном лимите. Такой разовый fee материален относительно excess yield.

У CIAN rsETH количество rsETH на долю за два года уменьшилось на 4,1177%; рост underlying oracle компенсирует часть, давая 1,0854% в ETH. Это не полная investor P&L: отдельно нужны external rewards и event attribution. Оно показывает необходимость считать compound return в правильных единицах вместо умножения current APY на прошлое окно.

## Tron: большой остаток с почти нулевым yield

Официальная [таблица контрактов JustLend](https://docs.justlend.org/developers/deployed_contracts/) различает ETH и ETHB по адресам и объясняет изменение UI-названий. Current ETH underlying `THb4…` раньше назывался ETHOLD; ETHB `TRFe…` связан с другим mapped token. В 2023 protocol объявлял offboarding старого ETH, тогда как current directory называет оба рынка active. Старую статью нельзя использовать как актуальный статус.

Current public API показывает у ETH рынка около 484 122 token units cash, 87,51 units borrowed и base supply APY около 0,0002899%; mining reward — 0. Utilization около 0,0181%. Значительный номинальный TVL здесь почти не генерирует текущего borrower interest. Физический Ethereum backing mapped tokens не восстановлен, поэтому это отдельный representation segment, без автоматического включения в verified native ETH. [Досье Tron](dossiers/justlend-tron.md) сохраняет адреса и reconcile cash+borrow−reserves с share claim.

## Ethena и PT: важны размер конкретного leg и жизненный цикл

В current [публичном backing UI Ethena](https://app.ethena.fi/dashboards/backing-assets) 3 октября ETH basis legs на Binance/Ceffu, Bybit/Copper и OKX/Copper суммарно составили около $374,44 млн. Весь crypto basis — $928,89 млн; остальная backing включает DeFi lending, institutional lending, liquid stables и RWA. Полный USDe supply не является ETH carry market size. Это rounded UI disclosure после T, без независимого восстановления custodial books.

Pendle API по четырём обязательным сетям полностью paginated: 626 listed markets, из них 126 имеют выбранный ETH-family accounting asset. На T 122 уже expired, четыре ещё unexpired. Current AMM liquidity этих четырёх около $6,264 млн. Это не total PT principal и не весь fixed-yield рынок: после expiry остаются redemption claims, а вне Pendle существуют другие площадки. Исторические maturity waves нужно отделять от исхода инвесторов из всей ETH экономики. [PT dossier](dossiers/pendle-pt.md), [basis dossier](dossiers/ethena-basis.md).

## Что уже можно утверждать и что остаётся открытым

Высокая уверенность относится к прочитанным fixed-block states, проверенной identity контрактов и арифметике returns. Средняя — к adapter history и current публичным allocations. Низкая или неизвестная — к external depositor provenance, private distributions, omnibus custody backing и market-wide net total. Цифры разных уровней не становятся взаимозаменяемыми после объединения в таблицу.

Наиболее важные незавершённые проверки: global native staking state на T; ownership/backing graph всего рынка; полный borrower scan Aave и Morpho; Liquid Monad sleeve и остаток Liquid ETH; historic asset universes и strategies; investor rewards; полноценные redemption/debt-repayment simulations; rates/funding history по venues и концентрация конечных плательщиков.

Это последовательность следующей глубины исследования, а не предложение заново начать работу. Данные и инструменты уже созданы. Текущее состояние фаз и критерии завершения — [EXECUTION-CHECKLIST.md](EXECUTION-CHECKLIST.md); источники и воспроизведение — [AUDIT.md](AUDIT.md). Полный [план исследования](RESEARCH-PLAN.md) сохраняет исходный объём задачи.
