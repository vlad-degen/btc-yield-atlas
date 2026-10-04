# Concrete ETH vaults

Срез 2 октября 2026, 23:59:59 UTC; публичные интерфейсы прочитаны 3 октября. Главная находка — различие между опубликованной AUM, выпуском учётных долей и доказанными внешними депозитами. Два ETH-продукта ведут стратегии через один Safe. Полная оценка активов Safe и экономических прав держателей пока не восстановлена.

## Продукты и заявленная стратегия

| Продукт | Vault | Book assets на T |
|---|---|---:|
| ctDeltaWeETH | `0xb9dc54c8261745cb97070cefbe3d3d815aee8f20` | 278 170,834213 weETH |
| ctwstETH Plus | `0xd57588c73715b65e0ead36ae06c15644169501b7` | 36 439,686407 wstETH |

В [публичном каталоге Concrete](https://app.concrete.xyz/earn) WeETH Vault показывает около $823 млн, permissioned access и скрытый APY. Его обзор описывает заём стейблкоинов под weETH с вложением заёмных средств в delta-neutral arbitrage. Указаны задержка withdrawal 7 дней и 30 дней до получения yield. Это заявленные условия; их исполнение и полный набор venues не подтверждены этим обзором.

Публичный API сообщает для двух продуктов около $823,925 млн и $121,685 млн на время сбора. Это текущие API estimates, не цена на T. В обоих vault convertToAssets(1e18) на T равен 1e18 соответствующего LST. Flat share rate не доказывает нулевую доходность инвестора: сам LST накапливает staking, а внешние выплаты и договорные права неизвестны.

## Onchain архитектура

Реализации прокси на T проверены через EIP1967 implementation slot. Для ctDeltaWeETH это ConcreteInitMintableAsyncVaultImpl, для ctwstETH Plus — ConcreteAsyncVaultImpl. У каждого getDeallocationOrder возвращает одну MultisigStrategy:

| Vault | Strategy |
|---|---|
| ctDeltaWeETH | `0xc8ea269d4dba296f7fbba812905c1b2efe5dbe1c` |
| ctwstETH Plus | `0x50a7510e73d79d60823dcac50e6b2c62e89ed82b` |

Обе getMultiSig возвращают `0x7ee29373f075ee1d83b1b93b4fe94ae242df5178`. Safe на T имеет threshold 3 и 5 owners. Адрес также найден независимым borrower scan: он крупнейший среди просмотренных заёмщиков Morpho wstETH/USDT, с текущим API-долгом около $70,4 млн. Это подтверждает наличие разных кредитных позиций у одной общей точки управления. Данные текущего API не считаются фиксированным debt на T.

В Aave этот Safe на T имеет около $503,453 млн collateral, $105,736 млн debt, $397,716 млн account equity и HF 3,82219. В Spark данных о действующей позиции нет. Эти значения нельзя распределить между двумя vault по долям или автоматически использовать как их общий NAV: Safe держит другие активы и claims и может обслуживать другие продукты.

MultisigStrategy использует totalAllocatedValue и функции adjustment учётной стоимости. На T getLastUpdatedTimestamp у weETH strategy относится к 16 декабря 2025, у wstETH strategy — к 9 февраля 2026. Accounting validity period настроен на 300 дней и примерно 83,3 года соответственно. Это фактические параметры текущего контракта, а не заявленная периодичность независимых проверок. Движение средств и обновление allocated balance могут происходить отдельно от accounting timestamp. Свежая USD-котировка LST не делает такую исходную учётную оценку свежей. Полное totalAssets не является автоматически суммой исполнимых рыночных активов за вычетом всех долгов.

## Выпуск долей ctDeltaWeETH

Полная доступная страница из 47 logs содержит событие UnbackedMint на 278 170,834213 долей 16 декабря 2025. Это ровно весь supply на T. В [транзакции выпуска](https://etherscan.io/tx/0xce658f57edc490798ddc55e3f67169e3190fe23afe50a4ce4ca411d0714edada) доли сначала выпущены управляющему адресу, затем переданы `0x5bab73f561a5365c9e4bbc7c52fe0fa384fcf324`. Текущий holder list показывает этого одного держателя на весь supply.

В проверенном коде unbackedMint разрешён VAULT_MANAGER только при нулевом supply и нулевом deposit limit. Он выпускает shares без вызова transfer underlying. Поэтому событие не является подтверждением внесения 278 тысяч weETH в этой транзакции. Оно может представлять существующий или перенесённый портфель; экономическое основание первоначальной оценки требует отдельной реконструкции. Название функции и отсутствие transfer в ней сами по себе не устанавливают необеспеченность всего продукта.

Нельзя назвать $823 млн новыми внешними ETH-депозитами только по TVL или totalSupply. Нужны активы исходного портфеля, liabilities, права единственного держателя и условия внешней стратегии. Сначала этот продукт сохраняется в reported managed AUM view с открытой backing verification.

## Круговая связь ctwstETH Plus

На T общий Safe владеет 36 439,686407 долей ctwstETH Plus — 100% supply. Deposit events февраля 2026 показывают тот же Safe и как sender, и как owner. Vault передаёт allocated value в MultisigStrategy, которая возвращает тот же Safe как управляющий адрес.

Это реальная внутренняя связь, требующая look-through. Добавление стоимости долей ctwstETH Plus к активам Safe, которые обеспечивают эти доли, создало бы двойной счёт. Нельзя также маркировать эти доли как отдельные внешние вклады без подтверждения внешних beneficial claims. Это не доказывает отсутствие внешних экономических владельцев по договорам: таких прав публичный holder list не показывает.

## Что следует из проверки

1. Два продукта с разными underlying share tokens имеют общую точку custody и исполнения. Они не дают независимую диверсификацию по управляющему только благодаря разным именам.
2. Book AUM, внешние депозиты и unique underlying — разные показатели. Первоначальный mint ctDeltaWeETH особенно ясно показывает это различие.
3. Наличие нейтральной dollar strategy не устраняет падение ETH-залога, stable borrow cost и задержку возврата средств.
4. Сравнение по public APY невозможно. Для доходности нужны договорные выплаты и NAV history; 1:1 LST share conversion не заменяет их.
5. Safe-level net assets нельзя произвольно распределять на vaults. Требуются отдельные sub-ledgers и проверка debt ownership.

## Открытые проверки

Нужны полный Safe balance sheet на всех существенных сетях, Morpho liabilities на T, внешние deployments долларовых средств, происхождение первоначальных активов ctDeltaWeETH, identity и права holder, все claims других vault в Safe, historical accounting adjustments и фактическое исполнение exits. Holders на T должны быть подтверждены отдельно для ctDeltaWeETH; для ctwstETH Plus 100% self holding уже подтверждён eth_call.

Артефакты: `data/eth/vault_registry_rpc_T.json`, `governance_T.json`, `concrete_lookthrough_T.json`, `concrete_self_holdings_T.json`; raw ключи `concrete_holders`, `concrete_logs`, `concrete_multisig_strategy_abi`, `concrete_vault_api`, `concrete_ui_observation.json`. Прокси labels текущего explorer не использованы как единственное доказательство версии на T.
