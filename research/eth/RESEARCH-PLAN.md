# План глубокого исследования рынка доходности ETH

Дата плана: 3 октября 2026 года. Исследование запущено по указанию пользователя. Фактический прогресс отражён в [чеклисте](EXECUTION-CHECKLIST.md); рыночные итоги и рейтинги публикуются после проверки соответствующих данных.

Цель — исследовать рынок доходности ETH с глубиной BTC Yield Atlas: измерить капитал, стратегии, продукты и сети, восстановить реальную экономику крупнейших продуктов, выяснить источник дохода, распределение рисков и возможности выхода. Особый приоритет — carry trade, лупинг и гибридные волты. Первым пилотом станет ether.fi Liquid ETH, который пользователь привёл как пример.

Основной результат должен объяснять, сколько ETH работает в выбранном охвате, где и как, сколько дохода получено в ETH, какую прибавку продукт даёт к обычному стейкингу и какую цену вкладчик платит за неё плечом, ликвидностью, контрагентским риском и комиссиями. Гипотезы о механике и рекламу проверяем по позициям и событиям.

Основа: [BTC RESEARCH PLAN](../../RESEARCH-PLAN.md), [BTC REPORT](../../REPORT.md), [карта BTC проекта](../PROJECT-KNOWLEDGE.md), [индекс BTC кода](../PROJECT-CODE-INDEX.md). Сохраняем полезную структуру досье и ончейн-проверок, адаптируя определения и расчёты к ETH.

## Что должно стать известно

1. Размер измеримого рынка в ETH и USD; какие сегменты измерены точно, оценены или остаются неизвестными.
2. Как капитал распределён по продуктам, стратегиям, базовым ETH-активам, сетям и конечным площадкам размещения.
3. Сколько капитала находится в простом стейкинге, рестейкинге, лупинге, carry, кредитовании, PT, LP, опционах и других стратегиях.
4. Как рынок изменился за два года; что объясняют притоки, начисленный доход, цена ETH, кредитное плечо и смена классификации.
5. Какие продукты действительно используют ETH как залог для долларового carry, каковы их размеры и куда идут доллары.
6. Какие продукты усиливают доход стейкинга займами ETH, сколько у них плеча и как они переживают изменение ставок и LST-дисконт.
7. Как устроен ether.fi Liquid ETH: цепочки контрактов, распределение по рукавам, доходность, долг, ликвидность, ключи и история смены стратегии.
8. Кто оплачивает каждую составляющую дохода: Ethereum, пользователи сети, заёмщики, AVS, трейдеры, эмитенты, маркетинговые программы или сам оператор продукта.
9. Что получает вкладчик после всех комиссий и расходов; где рекламный APY отличается от фактического результата.
10. Кто вносит капитал и что удерживает его: стейкинг, дополнительный доход, интеграции, плечо, институциональные клиенты, биржевая дистрибуция или поинты.
11. Какие зависимости системные: концентрация в LST/LRT, одном кредитном рынке, oracle, мосте, кураторе и внешнем источнике стимулов.
12. Какие механики и условия имеют смысл для будущего ETH-yield продукта; какие выводы доказаны, а какие остаются гипотезами.

## Что меняется относительно BTC

ETH имеет собственный базовый доход стейкинга. Для исследования важна прибавка сверх него, а не только положительная абсолютная доходность. На Ethereum rewards поступают через consensus и execution layers; ликвидные токены представляют требования к стейкинг-продукту, а выход через погашение и продажу на рынке имеет разные условия. [Ethereum staking](https://ethereum.org/staking/), [pooled staking](https://ethereum.org/staking/pools/).

ETH lending нельзя автоматически отправить в исключённый «нулевой контекст», как часть BTC-залога. Поставщик ETH может получать значимый процент, а заёмщик использовать ETH для лупинга. Измеряем supply yield и источники спроса на долг отдельно.

Один ETH может обеспечивать staking token, restaking claim, lending position и vault share. Возникает граф требований и долгов, а не простая сумма TVL. В частности, wstETH представляет долю stETH и меняет стоимость относительно stETH; его баланс не является количеством ETH 1 к 1. [Lido wstETH](https://docs.lido.fi/contracts/wsteth/).

Коррелированный лупинг LST против ETH и carry с долгом в USD имеют разные риски. В первом случае критичны относительная цена LST/ETH, ставка займа ETH и ликвидность выхода; во втором — также цена ETH/USD, стоимость долларового финансирования и долларовые активы размещения. Параметры eMode задаются конкретной категорией рынка и должны читаться на выбранном блоке. [Aave eMode](https://aave.com/help/borrowing/e-mode).

Нативную эмиссию ETH, execution rewards/MEV, реальную выручку AVS и внешние токеновые кампании показываем раздельно. Сценарий «внешние награды выключены» сохраняет базовый Ethereum staking; иначе сравнение экономик потеряет смысл.

## Фаза 0 Методология и границы

### Охват продуктов

Основная вселенная — продукты и позиции, куда держатель вносит ETH или требование на ETH и получает ETH-номинированный результат либо сохраняет существенную экспозицию к ETH. Включаем native staking как базовый слой, LST/LRT, ETH lending, управляемые волты и доступные сторонним вкладчикам стратегии.

При каждом продукте сохраняем: актив депозита, актив NAV, актив выплаты, ETH-delta, наличие хеджа и изменение экспозиции в процессе стратегии. Продукт с ETH-депозитом, но результатом в USD и закрытой ETH-delta, показываем отдельным сегментом. Возврат выплаты в ETH не делает долларовую дельта-нейтральную стратегию эквивалентом держанию ETH со стейкингом.

В расширенном каталоге сохраняем биржевое staking/earn, институциональные фонды, staking ETF, собственные treasury positions, закрытые продукты и неизвестные размеры. Они получают причины включения/исключения и не добавляются механически к прозрачному onchain итогу. Native stake через биржу и отдельный биржевой сертификат могут представлять один капитал.

Голый WETH, plain bridge receipt и ETH, не приносящий дохода, учитываются как инфраструктура/контекст. ETH-выплаты по airdrop не превращают несвязанный продукт в ETH-yield продукт. Нативные AVAX, BNB, SOL и другие активы не входят только потому, что сеть имеет staking.

### Дата и временной ряд

Предлагаемый базовый снимок — 2 октября 2026, 23:59:59 UTC, последний полный UTC-день перед составлением плана. До массового сбора проверяем доступность archive и исторических API. Если выбирается иной T, он меняется во всём manifest и всех выходах одновременно.

Базовая история — 24 завершённых месяца, октябрь 2024 — сентябрь 2026, плюс отдельная точка текущего снимка. Досье восстанавливают весь срок жизни продукта, если данные доступны. У событий высокой частоты используем дневные и внутридневные точки. Partial month не выдаём за полное месячное наблюдение.

Для каждой сети выбираем блок не позднее T, сохраняем timestamp и finality. Для native staking сохраняем соответствующие consensus slot/epoch и execution block. Цена, exchange rate, oracle и долг должны соответствовать своей точке. Позднее уточнение получает собственную дату вместо скрытой подстановки в снимок.

### Три разные величины капитала

| Представление | На какой вопрос отвечает | Что допускается складывать |
|---|---|---|
| Уникальный базовый ETH | Сколько исходного ETH лежит за цепочками требований | Только устранённые пересечения backing, bridge escrow, receipts и переиспользования |
| Внешний капитал вкладчиков | Сколько собственного капитала инвестировано в продукты | Остаточные внешние требования после look-through; активы минус обязательства на каждом уровне |
| Валовые позиции и зависимости | Где размещены активы и долги, насколько велика экспозиция | Gross assets/exposures в отдельном представлении, с указанием повторного использования |

Эти суммы не обязаны совпадать. При ETH borrowing и покупке LST нельзя вычитать backing как «дубль» и терять внешнего кредитора; при учёте vault share нельзя добавлять целиком его underlying issuer ещё раз. Для каждой корректировки строим баланс и объясняем, какое требование осталось у внешнего владельца.

Headline рынка строится после согласования представления и проверок графа. Сохраняем gross, net и диапазон неопределённости. Coverage означает долю обнаруженной измеримой вселенной, а не доказанную долю всего мирового рынка.

### География капитала

Отвечаем «на каких чейнах» четырьмя полями: origin/backing chain, сеть обращения receipt/share, сеть collateral/debt и сеть конечного размещения. Например, LST на L2 может иметь validator backing на Ethereum. Это одновременно разные места риска, но не два отдельных ETH.

Аддитивная таблица по сетям распределяет выбранный net capital один раз по правилу attribution. Если у multi-chain продукта нельзя достоверно разделить equity рукавов, он получает `multi-chain/unallocated` вместо условных процентов. Отдельная gross dependency matrix может суммироваться больше 100%.

### Критерий завершения

Должны быть готовы `scope.md`, taxonomy, schema, snapshot manifest и worked examples: обычный LST, LST → restaking, LST → WETH-loop, ETH → USD-carry, PT/YT, multi-chain vault. Для каждого примера баланс сходится; добавление wrapper не увеличивает net market. На этой базе начинаются массовые расчёты.

## Предлагаемая таксономия

Код обозначает механизм и не наследует числовое значение BTC-категории. Категории для аддитивного графика взаимоисключающие; mechanism tags и карты источников дохода допускают несколько признаков. Гибридный продукт с недостаточной разбивкой сохраняется как hybrid/unallocated.

| Код | Стратегия | Основной источник дохода | Что различать |
|---|---|---|---|
| E1 | Простой native/liquid staking | Consensus rewards, execution rewards/MEV за вычетом расходов | Native self-stake, pooled/LST, CEX staking, валидаторные версии |
| E2 | Restaking и LRT | Базовый staking плюс AVS/security доход и отдельные кампании | Реальная allocation/slashing, оплаченные AVS rewards, points, native/LST restake |
| E3 | Лупинг и leveraged staking/restaking | Усиленный доход ETH-актива минус ETH borrowing | LST/ETH loops, LRT/ETH loops, PT/ETH loops, mixed debt |
| E4 | ETH collateral и долларовый carry | Доход USD-размещения минус стоимость USD-долга, плюс доход залога | Валюта долга, размещения, source of rewards, валютный хедж |
| E5 | Прямое кредитование | Проценты заёмщиков ETH/ETH-family активов | Pool lending, curated lender vault, институциональный кредит |
| E6 | Фиксированный доход и PT | Дисконт к accounting asset при погашении | PT denomination, maturity, mark-to-market, базовый актив, PT-loops |
| E7 | LP и управление ликвидностью | Trading fees, emissions и доход underlying | ETH/LST, ETH/stable, concentrated LP, perp inventory, hedged LP |
| E8 | Опционы и структурные продукты | Option premiums и структурный payoff | Сохранение ETH-delta, проданный upside, фактическая выплата |
| E9 | Basis/funding и хеджированные стратегии | Фандинг, basis, staking leg | ETH/USD nomination, collateral margin, CEX exposure, delta neutrality |
| E10 | Прочие стратегии и поинтовый капитал | Несколько источников или будущие награды | Idle, pending yield, модельная стоимость points, недостаточное раскрытие |
| EH | Гибридные управляемые продукты | Измеренная комбинация E1–E10 | Equity по рукавам, blended return, общие позиции/долги |
| E0 | Контекст | Доход не подтверждён или не относится к основному охвату | Голые wrappers, CDP collateral, treasury, USD-only products, неизвестный AUM |

Лупинг не определяется одним фактом займа. Классификация прослеживает использование долга:

- LST → WETH debt → покупка/стейкинг нового ETH → LST: коррелированный loop.
- ETH/LST → USD debt → USD-yield assets: долларовый carry.
- ETH/LST → USD debt → новый ETH/LST: leveraged long; отдельная подкатегория E3 и иной риск.
- ETH/LST → долг → LP/PT/CEX: классификация по фактической позиции и хеджу, а не по названию «yield vault».

Для mixed products сохраняем два ранжирования: полный NAV продукта и капитал/долг, относящийся к конкретному механизму. Наличие небольшого carry-рукава не делает весь NAV размером carry-рынка.

Термин carry используется в разных смыслах. Помимо E4 отдельно исследуем E9: spot/staking ETH плюс short futures/perpetuals с доходом от basis/funding. Сохраняем связь между семействами, но разделяем источник прибыли, ETH-delta, валюту результата и риски маржи. Положительный funding сегодня не доказывает устойчивую доходность за весь период.

## Фаза 1 Пилот ether.fi Liquid ETH

### Почему начинаем с него

Пилот проверит методику на важном для задачи гибридном продукте до масштабирования. Официальная документация на дату плана идентифицирует Liquid ETH Vault как Veda vault с базовым ETH на Ethereum и Optimism. Адрес BoringVault: `0xf0bb20865277aBd641a307eCe5Ee04E79073416C`; Accountant: `0x0d05D94a5F1E76C18fbeB7A13d17C8a314088198`. Эти адреса — отправная точка документации; deployed code и актуальные роли проверяем onchain. [Liquid ETH Vault](https://etherfi.gitbook.io/etherfi/products/liquid/live-vaults/liquid-eth-vault).

Документация Liquid описывает blended APY и views Position/Protocol/Network; protocol exposures могут перекрываться. Это задаёт полезную проверку: интерфейс, positions и восстановленный баланс должны объяснять один результат, даже когда exposures превышают 100%. Текущие доли loop/carry пока остаются проверяемой гипотезой пользователя. [How Liquid works](https://help.ether.fi/en/articles/517109-how-liquid-works).

### Порядок разбора

1. Установить product identity: user-facing ETH Yield/Liquid ETH, receipt token, версии, deployed chains, start of funded operations. Не смешать с eETH/weETH issuance, ether.fi Borrow/Cash и lender vaults других кураторов.
2. Проверить BoringVault, Accountant, Teller, Manager, roles authority, очередь и используемые мосты; найти все стратегические кошельки и sub-vaults.
3. Восстановить assets, liabilities и shares по всем сетям; отдельно escrow/in-transit и claims на мостах. Сверить `supply × share rate` с независимым balance sheet.
4. Разложить текущие рукава: unlevered LST/LRT, ETH-debt loops, USD carry, lending, PT, LP, CEX, idle и неизвестные позиции. Проверить конечное использование каждой валюты займа.
5. Восстановить PPS/NAV и fees; отдельно market/exit value, внешние rewards и их попадание в NAV.
6. Выбрать 6–10 исторических дат с изменениями стратегии или стрессом и проверить, что классификация работает во времени. Далее расширить до месячной/дневной истории.
7. Сопоставить base staking, loop uplift, carry PnL, incentives, fees, gas/slippage и остаток необъяснённого PnL.
8. Посчитать liquidity ladder для каждой валюты долга и отдельно маршрут выдачи ETH вкладчику. Проверить queue parameters и исторические фактические исполнения.
9. Изучить ключи, timelocks, смену modules/Merkle roots, accountant restrictions, executor paths и действия в стрессовые даты.
10. Определить holders с look-through и интеграциями; установить, какие наблюдения можно повторить для других продуктов.

Архитектурные описания Veda служат списком проверяемых компонентов, а не доказательством безопасности конкретного deployment. Возможность администратора сменить модуль нужно оценивать отдельно от неизменяемости ядра. [Veda architecture](https://etherfi.gitbook.io/etherfi/products/liquid/veda-vault).

### Выход и критерий завершения

Пилотное досье и таблицы positions, debts, PPS, fees, strategy classification, liquidity, roles и unresolved gaps. Цель — баланс с объяснённой разницей в пределах 1% NAV; любой больший остаток разобран либо явно ограничивает выводы. Минимум одна дата перепроверена другим независимым источником/методом. После пилота уточняем schema и реальные затраты сбора.

## Фаза 2 Вселенная продуктов и основных сетей

### Широкий поиск

Используем protocol registry, token/chain breakdowns, yields pools, официальные контрактные реестры, lending markets, staking/restaking сведения, DEX/PT data и каталоги управляющих. Категория DefiLlama — вспомогательный фильтр; ETH-продукт может находиться внутри протокола с общей категорией «Yield» или «Lending».

Token registry содержит `(chain_id, address)`, canonical asset, type, issuer, backing, conversion method, reward mechanics и bridge relationship. Symbol/подстрока ETH не считается достаточной идентификацией. Добавляем native ETH, WETH, LST/LRT, aTokens/cTokens, vault shares, PT/YT/SY, LP и debt tokens. Конверсии делают ETH-эквивалент и market value раздельно.

Порог детальной карточки для первоначального screening: текущий капитал продукта ≥$5 млн либо исторический peak ≥$20 млн. Для carry/loop допускаем меньший размер — текущий equity/выделенный рукав от $1 млн, уникальная механика, важный инцидент или критичная зависимость. Эти пороги — предложенные настройки discovery, а не оценки размера рынка. Небольшие продукты могут оставаться агрегированным long tail с измеримым итогом.

Историческая universe включает закрытые, переименованные и мигрировавшие продукты. Выбор только сегодняшних крупных строк привёл бы к survivorship bias и потерянным историям аирдропов/инцидентов.

### Сети

Обязательный первый круг: Ethereum execution и consensus layers, Base, Arbitrum, Optimism. Для остальных делаем широкий лёгкий screening ETH-family капитала, затем фиксируем глубокий список по данным.

Кандидаты следующего круга: BNB Chain, Polygon, Avalanche, Linea, Scroll, zkSync Era, Mantle, Unichain, Sonic, HyperEVM, Monad, Berachain, Katana, Ink, Blast, Fraxtal и другие сети с найденным значимым ETH-yield. Это список проверки наличия, а не утверждение, что все они входят в лидеры. На Solana/Sui/Tron и других не-EVM сетях ищем подтверждённые ETH-family assets и существенные площадки; их собственные нативные токены исключаются.

Предлагаемая политика включения сети: ≥1% обнаруженного gross ETH-yield deployment либо ≥$25 млн соответствующего капитала, либо продукт/кредитный рукав ≥$5 млн, либо значимая системная зависимость. Обязательные сети остаются независимо от порога. Меньшие сети можно объединить, сохранив измеренный размер и причины исключения из deep dives.

Цель покрытия — 95–98% обнаруженного измеримого deployment в выбранной вселенной. Полноту показываем отдельно для staking и DeFi: огромный native staking denominator не должен скрыть плохо покрытый DeFi long tail.

### Кандидаты по областям

| Область | Начальный список для проверки статуса и размера |
|---|---|
| Staking и LST | Native Ethereum, Lido, Rocket Pool, Coinbase/cbETH, Binance staking, Frax, StakeWise, Mantle staking и иные обнаруженные эмитенты |
| Restaking и LRT | EigenLayer, Symbiotic и другие security layers; ether.fi, Renzo, Kelp, Puffer, Swell, Mellow и иные продукты из токенового реестра |
| Managed vaults и automation | ether.fi Liquid ETH, CIAN, Instadapp/Fluid/Instadapp Lite, Summer.fi, Gearbox, Yearn, Enzyme, Lagoon, Upshift, Veda deployments и обнаруженные аналоги |
| Credit venues | Aave, Morpho, Spark, Euler, Fluid, Compound, Silo, Gearbox, Venus, Moonwell, Radiant и другие рынки с соответствующими активами |
| Fixed yield | Pendle, Spectra и аналогичные рынки ETH-family PT; lender vaults с PT-collateral |
| LP и structured | Curve, Uniswap, Balancer, Aerodrome, Tokemak, Beefy, Convex, perp/option venues и их управляемые ETH-волты |
| Offchain и USD context | CEX earn/staking, ETH funds/treasuries/ETF, Ethena и другие USD-продукты с ETH в стратегии |

В таблице нет предварительного рейтинга, подтверждения живого продукта или инвестиционной рекомендации. Название протокола может включать несколько разных продуктов и версии, которые потребуется разделить. В частности, CIAN прямо различает recursive staking и recursive restaking; конкретные deployment и доли проверяем отдельно. [CIAN concepts](https://docs.cian.app/yieldlayer/for-users-quick-start/core-concepts-and-yield-layer-page-overview).

### Выход и критерий завершения

`product_registry`, `asset_registry`, `chain_coverage`, `contracts`, `exclusions`, `source_registry`, `raw_manifest`. Для каждой крупной строки есть источник, адрес/issuer, дата, механизм и confidence. Неизмеримый размер хранится как unknown, не как ноль. По каждому пропуску виден возможный порядок величины или отсутствие обоснованной оценки.

## Фаза 3 Net market map и поиск carry и looping продуктов

### Карта капитала

Собираем product × asset × chain × strategy: net external equity, ETH units, USD, gross assets, ETH/USD debt, pledged collateral, stake backing и claims. Баланс работает на одинаковых ценах/блоках. Для LST/LRT используем share exchange rates и actual backing, сохраняя market discount.

Для native staking считаем действующие остатки и reward flows по данным consensus, withdrawal credentials и operator/issuer attribution. Число валидаторов ×32 не используется как универсальная оценка после изменений effective balance/compounding. Сервисные депозиты, buffer и pending exits учитываются с их реальным состоянием.

Отдельно строим граф: ETH backing → issuer → restaking/security allocation → receipt holder → lending collateral → debt-funded asset → vault → external owner. Циклы borrowing не разворачиваем бесконечно; решаем связанную систему активов и обязательств с контролем внешних требований. Неподтверждённые ребра сохраняют диапазон overlap, а не точную поправку.

После reconciliation создаём additive market-by-product/category/chain и non-additive dependency-by-issuer/protocol/chain. Пара «количество продуктов и общий TVL» всегда сопровождается определением denominator.

### Поиск скрытых стратегий

1. Перечислить ETH/LST/LRT/PT-collateral рынки и ETH/stable borrowable assets на выбранных сетях.
2. Выгрузить borrower positions и определить smart account, vault, sub-vault, Safe, EOA, CEX/institutional desk.
3. Проверить use of proceeds: WETH → LST, USD → USD yield, USD → ETH, PT, LP, bridge, CEX и неизвестные направления.
4. Связать кошелёк с user-facing продуктом через share supply, manager permissions, документы, deposit flows и NAV. Один известный адрес недостаточен для идентификации полного продукта.
5. Собственные EOA/treasury позиции оставить в отдельной таблице спроса на заём и systemic dependencies. Product top-5 содержит доказанные внешние investor claims.
6. Проверить lender vaults: supply-side ETH yield и borrower-side loop нельзя смешивать под общим названием куратора.
7. Сопоставить identity и ranking по full NAV, carry/loop allocated equity и соответствующему debt. Unknown allocation не автоматически равен всему NAV.

Первоначальный scan threshold: долг ≥$1 млн эквивалента; глубоко идентифицируем всех найденных ≥$5 млн и особо проверяем крупнейших неизвестных. Для продуктовых рукавов используем также долю NAV, чтобы не потерять небольшой carry в большом hybrid vault. Порог и неполнота API остаются в отчёте.

### Отбор глубоких досье

Обязательный ether.fi pilot независимо от места в рейтинге. Далее — пять крупнейших доказанных carry-продуктов/существенных carry-рукавов, три–пять крупнейших или механически различных loop/hybrid продуктов и два–три базовых staking/restaking benchmarks. Один продукт может закрывать несколько групп. Плановый набор 8–12 уникальных глубоких досье, расширяемый при выявлении важной механики или зависимости.

Если живых carry-продуктов окажется меньше пяти, показываем фактическое число и исторические кейсы. Не заполняем top-5 институциональными EOA ради количества. Досье базового issuer также может иметь иной уровень подробности, чем trading vault.

Дополняем набор репрезентативными разборами крупных ETH lending, PT/fixed-yield, LP и basis/funding продуктов, если эти механики не покрыты выбранными волтами. Число 8–12 — первоначальное ядро, а не предел глубины: у каждой значимой категории должен быть проверенный пример экономики, риска и выхода.

### Выход и критерий завершения

Current map, overlap graph/table, borrower scan, ranked candidates и `selection.md`. Суммы category/chain/product сходятся в выбранном additive view. Все крупные поправки имеют доказательство. Выбранные продукты покрывают большую часть обнаруженного carry/loop капитала; фактический процент вычисляется после отбора.

## Фаза 4 История рынка и изменения механизмов

По каждой включённой позиции строим месячный ETH и USD ряд. Обновляем exchange rates, backing, debt и классификацию по каждой исторической дате. Не распространяем сегодняшний portfolio mix или overlap на два года без маркировки оценки.

Для рынков сохраняем supply, borrow, idle/utilization и ликвидность, а не только nominal TVL. Для managed products — supply shares, book PPS, independent NAV и actual assets. Для PT — конкретную maturity/version и accounting asset; текущий PT нельзя подставить в ранний рынок. По документации Pendle это именно accounting asset, который определяет погашение, а не простое равенство «1 PT =1 LST». [Pendle PT](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT).

Включаем закрытые продукты и стратегии, закончившие rewards. Маркируем миграции, bridge changes, мердж версий, переход от points к монетизированному доходу и моменты изменения полномочий/комиссий.

Разлагаем рост:

- внешние deposits/withdrawals;
- базовые staking rewards;
- incremental strategy PnL;
- incentives и их realized conversion;
- цена ETH/USD и относительная цена ETH-family активов;
- изменение плеча и финансирования;
- методологические/coverage/classification changes.

Midpoint-разложение ETH-value и ETH/USD price полезно как идентичность, но не заменяет события cash flow. Для ключевых продуктов делаем TWR по NAV/PPS и, где доступны investor flows, money-weighted return. Результат в ETH сравниваем с пассивным ETH и выбранным unlevered LST benchmark на том же окне.

Выход: market/category/chain histories, product lifetimes, event timeline и coverage matrix. Исторический охват и current-only rows показаны отдельно; разрыв последней исторической точки с current map полностью объяснён либо имеет ограниченный остаток.

## Фаза 5 Досье продуктов и контрагентов

Шаблон наследует BTC-разборы, дополняясь ETH-бенчмарком, типом долга и вложенным staking.

### Паспорт и механизм

Issuer, operator/curator, people/entities при подтверждении, launch/deploy/funded start, chains, token, deposited assets, NAV denomination, redemption asset, current/peak equity, status и стратегия по версиям. Схема от депозита до последнего источника дохода и выдачи пользователю.

Collateral/debt/deployment — по каждому рукаву. Фиксируем gross ETH exposure, debt currency, leverage, LTV, thresholds, eMode, borrowing permissions, hedge/delta, caps и взаимные зависимости. Не переносим threshold одной позиции на весь портфель.

### Источник и распределение дохода

Реализованный return в ETH, APR/APY и cumulative return по одинаковым окнам. Base staking, loop uplift, carry, lending, PT discount, LP fees/IL, funding, option payoff, AVS revenue, emissions, points и неизвестный остаток — отдельными строками.

Сверяем marketing APY, API estimate, accrued rewards, claimed rewards, проданные rewards и PPS/NAV gain. Различаем rewards inside NAV и выплаты держателям снаружи; не учитываем один токен одновременно в обоих местах. Points сохраняются как немонетизированное право, стоимость в базовом realized yield равна нулю до подтверждённой реализации.

### Отрицательная доходность и сравнительный результат

Проверяем периоды, когда cost of debt превышает доход funded leg, цена share падает или продукт зарабатывает меньше unlevered staking. Показываем длительность, величину убытка, реакцию оператора, скорость уменьшения долга и последующий recovery. Managed PPS может сглаживать потери; его отсутствие просадок не заменяет независимый MTM.

### Ликвидность и выход

Две отдельные лестницы: погашение долга в нужной валюте и получение ETH/актива выплаты вкладчиком. Same-block, минуты, день, 1–7 дней, дольше и unknown. При repay/recycle учитываем исполнение полного пути, flash loan availability, authorizations и competing withdrawals.

Withdrawal queue, staking exits, restaking deallocation/slashing window, PT maturity, bridge settlement, CEX withdrawals и institutional redemption имеют собственные сроки. «Можно продать receipt» оценивается по объёму/цене, а не только по существованию DEX-пары. Для размеров 1%, 10% и 30% NAV измеряем выход/дисконт и bottleneck.

### Ключи и правила

Token issuer, staking operator, restaking operator, bridge, oracle, accountant, vault admin, strategy executor, lending market, lender vault и fee recipient. По каждому — адрес, authority, threshold, timelock, возможность pause/mint/change oracle/withdraw/module/root и route обхода. Проверяем заявления документами и live deployment отдельно.

Для restaking фиксируем действующий механизм slashing, delegated/allocated stake, operator sets и получателя rewards; исторические airdrop points не являются подтверждением оплаты текущего security service.

### Вкладчики и рост

Address counts, unique economic owners где доказуемо, buckets, top-1/10/100, HHI, retail/institutional/contract/omnibus/CEX, cross-chain shares, bridge escrow и internal holders. Не считать lending hub одним вкладчиком, если claims принадлежат его заёмщикам; не пытаться реконструировать частных клиентов omnibus из одного адреса.

TVL growth, events, caps, incentives, integrations, collateral acceptance, distribution и повторный спрос. Статистическое совпадение с APY не выдаём за причинность. Оцениваем, насколько рост обусловлен issuer/curator self-deposits или recursive integration loops.

### Экономика оператора и вывод

Все уровни fees, revenue recipients, actual claimed/owed fees, gas/keepers, issuer reward budget, extra yield на единицу внешнего капитала. Кто заработал при одинаковом периоде: вкладчик, issuer, lender, curator, validator/operator и плательщик rewards. Финальный вывод содержит измеренные tradeoffs и ограничения, без универсального рейтинга «самый безопасный» по одному показателю.

## Фаза 6 Экономика carry и looping и системные стрессы

### Формулы и бенчмарк

Формулы ниже — приближённые локальные модели. Фактический PnL подтверждается balance sheet и cash flows с изменением цен/позиций.

Долларовый carry при единых текущих ценах:

`APR_equity ≈ annual_collateral_income_USD / equity_USD + (USD deployment APR − USD borrow APR) × USD debt / equity_USD − annual_costs_USD / equity_USD`.

Если залог — доходный LST, его baseline contribution сохраняется. Для incremental carry отдельно вычитаем unlevered benchmark и учитываем posted/idle share. Реальную прибыль в USD конвертируем в ETH по датам получения/компаундинга; изменение ETH/USD и депеги не скрываются в одной постоянной ставке.

Коррелированный ETH-loop:

`APR_equity ≈ L × ETH-asset APR − (L − 1) × ETH borrow APR + external incentives − costs`.

`L = gross ETH-valued assets / ETH-valued equity` при сопоставимых оценках. Теоретический `1/(1−LTV)` действует только в идеализированной полной рекурсии; фактическое плечо определяется состоянием портфеля, ограничениями, ценой обмена и finite loops.

Для mixed vault рассчитываем equity, PnL и costs по рукавам без повторного отнесения shared collateral/debt. Если shared finance не позволяет точную аллокацию, показываем диапазоны/sensitivity и отдельный unallocated остаток.

Для basis/funding carry раскладываем доход на staking leg, изменение basis, funding cash flows и расходы на hedge/margin. Отдельно считаем потерю ETH-экспозиции, риск ликвидации short leg, доступность collateral transfer и контрагентский риск площадки. Проверяем доходность при смене знака funding и расхождении spot и derivative prices; номинальную delta neutrality подтверждаем позициями во времени.

Главные сравнения: ETH held; unlevered staking benchmark net of its fee; unlevered lending; конкретная стратегия; та же стратегия без external rewards; стратегия при стрессовой ставке и ликвидности. Все окна и denomination совпадают.

### Сценарии

| Сценарий | Для кого критичен | Что измеряем |
|---|---|---|
| ETH/USD −10%, −20%, −35% | USD-debt carry и leveraged long | HF/LTV, repay need, ликвидация, потеря и путь восстановления |
| LST/LRT discount 1%, 3%, 5% к ETH | Коррелированные loops и LST collateral | Oracle valuation, market exit, relative HF, haircut и collateral seized |
| ETH borrow rate скачком и на 7/30 дней | Loops | Negative carry, break-even, накопленный убыток и deleverage cost |
| Stable borrow rate скачком | Carry | Margin, отрицательный spread, компенсация base staking и unwind |
| Funding меняет знак, basis расходится, margin requirements растут | Basis/funding carry | Фактический cash flow, margin shortfall, стоимость закрытия и риск площадки |
| Lending utilization 95–100% | Borrowers и suppliers | Ставки, доступный cash, flash capacity, withdrawals и очереди |
| External rewards =0 | Reward-dependent products | Net return и alpha к baseline staking без дополнительных субсидий |
| Withdrawal requests 10%/30% NAV | Все managed products | Доля долга погашаема и доля ETH выдана по срокам и цене |
| Exit queue 7/21/60 дней как сценарий | Staking/LRT-dependent positions | Funding cost за время выхода, forced DEX sales и liquidity reserve |
| Slashing/haircut и oracle задержка | Staking/restaking/lending | NAV loss, haircut propagation, кто несёт первую потерю |
| Bridge/chain/keeper outage | Cross-chain vaults | Возможность repay без перемещения активов, длительность блокировки |
| Параллельные выводы связанных vaults | Shared lender/liquidation ecosystem | Конкуренция за один liquidity buffer и круговые зависимости |

Указанные shocks — проектные сценарии, не утверждения о текущих параметрах или вероятностях. На коррелированный LST/ETH-loop не накладываем автоматически обычную формулу USD liquidation price: проверяем обе валюты и фактический oracle. Изменение governance parameters, caps и eMode также может вызвать deleverage без движения ETH/USD.

Восстанавливаем крупнейшие исторические стрессовые окна и сравниваем заявленную политику с фактическими transactions. Для event-driven выводов сохраняем timestamp, block, before/after positions и интервал реакции.

### Системные зависимости и ёмкость

Issuer/curator/market concentration, доля продукта в liquidity pool, доля собственного займа в lender vault, общие rewards payers, круговые ownership links, overlap LST collateral и restaking exposure. Estimation of capacity учитывает borrow utilization/rate curve, caps, buy/sell liquidity LST, staking exits, reward budget и предельную доходность при росте AUM.

Выход: сравнительная экономика, break-even surfaces, stress tables, debt/exit ladders, concentration graph и risk matrix. Для каждого сценария отделяем подтверждённые параметры от предположений.

## Фаза 7 Синтез и исследовательские инсайты

Сформулируем выводы после расчётов, проверяя следующие гипотезы:

1. Насколько значим чистый incremental ETH yield сверх простого стейкинга после fees и borrowing cost?
2. Где добавленный APY оплачивается реальными участниками рынка, а где token emissions/маркетинговым бюджетом?
3. Усиливает ли лупинг базовый staking эффективно, или почти весь uplift съедают debt costs, execution и liquidation risk?
4. Даёт ли USD carry преимущества против ETH loops при сопоставимом риске и ликвидности?
5. Насколько поинтовые циклы и collateral integrations искусственно увеличивают reported TVL?
6. Может ли несколько ETH-yield продуктов на разных сетях иметь фактически один источник дохода и один liquidity bottleneck?
7. Где book NAV скрывает стоимость выхода, depeg или CEX/credit exposure?
8. Какие продукты выдерживают rewards-off и массовый redemption; кому хватает долга/выходной ликвидности?
9. Кто выигрывает от fee stacking: пользователь, LST issuer, curator, vault platform, lender или reward sponsor?
10. Какие конкретные distribution routes объясняют рост капитала; что меняется для retail и институтов?
11. Как изменились стратегии по фазам рынка, ставкам и очередям; какие механики исчезли?
12. Где есть ёмкость для нового продукта и каким параметрам риска она соответствует?

Результат: русский отчёт уровня BTC REPORT, английское резюме/atlas при необходимости, market and chain charts, полные досье, source ledger, limitations и playbook. Playbook содержит допустимые условия, economic sensitivities и измеримые risk limits; партнёры/кураторы сравниваются по подтверждённым deployment, conflicts, track record и полномочиям.

Число «всего ETH в рынке» сопровождается разрезом scope и uncertainty. Вывод «не найдено» относится к проверенной universe и порогам; он не означает доказанное отсутствие во всём рынке.

## Фаза 8 Проверка и воспроизводимая сборка

1. Заново собрать главные таблицы из сохранённого raw/manifest на выбранном T без ручной подмены сумм.
2. Перепроверить все headline numbers, top rankings, category/chain totals и исторические точки по одной версии классификации.
3. Сделать independent method reconciliation крупных продуктов: share supply × exchange rate против assets minus liabilities.
4. Проверить dimension/currency/unit, rebasing, decimal conversion, quote orientation, stale oracle, addresses и version ranges.
5. Проверить market/exit price против book value и benchmark alignment на одинаковых окнах.
6. Проверить supply/borrow и wrapper/bridge/issuer/vault overlap; отдельно показать unknown edges.
7. Все published facts связать с source, date/block, transformation и confidence. Обновлённый источник не должен бесшумно заменять старый снимок.
8. Текстовые итоги и графики генерировать из того же semantic dataset; fixed hand-written numbers сверять автоматически. Калькуляторы получают явные assumptions.
9. Сравнить current и last-history coverage и объяснить differences. Нулевой capital, unknown capital и закрытый product — разные состояния.
10. Подготовить audit findings и unresolved issues. Незакрытые пробелы не маскируются красивым графиком или точным округлением.

Вычислительная база: публичные источники, archive RPC, protocol APIs/indexers, contract logs, опубликованные отчёты. Доступность consensus history, старых events и historical APIs проверяем заранее; paid-only endpoint требует alternative source или обозначенного gap. Длительность всего исследования оцениваем после пилота и проверки данных, а не по числу страниц.

Критерий завершения: получены воспроизводимые ключевые выводы, объяснены существенные расхождения, раскрыты границы покрытия. Невозможность доказать точное значение сохраняется диапазоном/unknown с объяснением влияния.

## Данные и структура материалов

Предлагаемые отдельные namespaces сохраняют BTC snapshot и его инструменты. Этот план не требует немедленно создавать все файлы.

```text
research/eth/
  RESEARCH-PLAN.md
  EXECUTION-CHECKLIST.md
  scope.md
  methodology.md
  selection.md
  report.md
  audit.md
  dossiers/
data/eth/
  product_registry.csv
  asset_registry.csv
  chain_coverage.csv
  contracts.csv
  sources.csv
  snapshot_manifest.json
  market_current.csv
  positions_current.csv
  debts_current.csv
  ownership_edges.csv
  overlap_adjustments.csv
  product_strategy_allocations.csv
  market_history_monthly.csv
  category_history_monthly.csv
  chain_history_monthly.csv
  cashflows_monthly.csv
  benchmark_yields.csv
  carry_loop_candidates.csv
  exclusions.csv
  events.csv
  claims.csv
  products/<product_id>/
    positions.csv
    debts.csv
    nav_series.csv
    returns.csv
    pnl_components.csv
    fees.csv
    rewards.csv
    liquidity_ladder.csv
    roles.csv
    holders.csv
    events.csv
tools/eth/
  README.md
  config/
  fetch/
  normalize/
  classify/
  netting/
  history/
  products/
  validation/
  build/
raw/eth/<snapshot_id>/
```

### Обязательные поля

| Набор | Ключевые поля |
|---|---|
| Registry | product_id, name, protocol, type, status, start/end, chain_ids, issuer, deposit/NAV/redemption assets, exposure/delta tag |
| Asset | chain_id, address, canonical_id, issuer, decimals, token_type, backing, exchange_rate_method, market_price_method, bridge_origin |
| Snapshot | T, chain, block/slot/epoch, timestamp, finality, price_source/time, retrieval_time, source_version/hash |
| Position | owner/sub-vault, product_id, chain, contract/market, asset, units, claim/backing ETH, book/market USD, strategy, confidence |
| Debt | borrower, product_id, chain, market, currency, principal/accrual, USD/ETH quote, borrow APR, oracle, LTV/LT/eMode, liquidity |
| Allocation | product_id, date, sleeve/mechanism, allocated_equity, gross assets, debt, shared/unallocated flag, attribution_method |
| Overlap | source_node, target_node, type, amount/unit, timestamp, method, adjustment, confidence, uncertainty |
| Return | window, funded_start, denomination, cumulative_return, APR/APY, TWR/MWR where applicable, gross/net, benchmark, MTM/exit adjustment |
| PnL | staking_consensus, execution/MEV, restaking_fees, carry/loop/lending/PT/LP/options/funding, incentives, costs, residual |
| Evidence | claim_id, statement, value/unit, date/block, primary URL/file/hash, transform/script, confidence, caveat |

Confidence: high — direct state/logs/documented amount reconciled; medium — dated API/disclosure with partial reconciliation; low — stated strategy, proxy or model. Inferred identities и source-of-funds relations получают собственную confidence, независимую от точности суммы.

Raw responses, параметры запросов, pagination, ошибки и время retrieval сохраняются с hash. Config включает chain scope, snapshot, thresholds, token mapping, category rules и historical version rules. Сбор должен возобновляться с checkpoints и не изменять предыдущий raw snapshot.

## Что переиспользуем из BTC проекта

| BTC элемент | Для ETH |
|---|---|
| Досье с fund flows, roles, yield, liquidity, holders и events | Основной шаблон с добавлением staking benchmark, peg риска и типа долга |
| Borrower scan и идентификация внешнего продукта | Две ветки поиска: ETH debt loops и stable debt carry |
| Archive calls, rate history, event replay | Общие приёмы с новым token registry и источниками consensus |
| Share/accountant/NAV reconstruction | С поддержкой rebases, exchange-rate tokens и разных версий |
| Overlap tables | Более полный ownership/backing/debt graph и separate net/gross views |
| Market history и price/flow attribution | Плюс staking accrual, leverage, cash events и classifications во времени |
| Liquidity ladder и intraday reactions | Две лестницы: repay и ETH redemption, относительный LST shock |
| Site/report outputs | Та же форма объяснения, общий semantic dataset, контроль текстовых чисел |

Жёстко заданные BTC addresses/blocks/categories, частные пути raw и ручные corrections не переносятся автоматически. Новые adapters/config живут в ETH namespace, чтобы baseline BTC оставался проверяемым.

## Порядок работы и промежуточные результаты

| Этап | Что можно обсуждать после него |
|---|---|
| Фаза 0 | Согласованные определения, датировка и пример net accounting |
| Фаза 1 | Полный pilot ether.fi и проверка, какие данные реально доступны |
| Фаза 2 | Большой каталог продуктов и обоснованный список основных сетей |
| Фаза 3 | Первая карта рынка, overlap и подтверждённые carry/loop rankings |
| Фаза 4 | История рынка и событий, текущий размер на сопоставимом охвате |
| Фаза 5 | Глубокие досье выбранных лидеров и benchmarks |
| Фаза 6 | Сравнение реального дохода, break-even, stress и системных зависимостей |
| Фаза 7 | Инсайты и playbook, привязанные к результатам |
| Фаза 8 | Проверенный отчёт и воспроизводимый набор данных/графиков |

Пилот предшествует массовой реконструкции. После первичного каталога устранение пересечений и поиск заёмщиков могут идти параллельно восстановлению части истории; финальное ранжирование требует одинаковой базы собственного капитала. История и досье уточняют каталог, поэтому исправления оформляются версионно с повторной сборкой итогов.

Первый конкретный пакет исполнения — scope/schema/snapshot manifest и независимый balance sheet ether.fi Liquid ETH с разметкой loop/carry. Он проверит главный пример задачи и снимет неопределённости методики до большого сбора. Точные рыночные числа, current APY, доли стратегий и список лидеров появятся после соответствующих фаз.
