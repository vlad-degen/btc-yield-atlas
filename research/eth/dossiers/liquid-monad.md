# Liquid Monad ETH: вложенный receipt и разные книги сетей

Срез T — 2 октября 2026, 23:59:59 UTC. Этот claim входит в Liquid ETH; его отдельное прибавление к market NAV создаст double count.

На Ethereum BoringVault `0xa024063b630d554078bbf985718b22f3c6870ee0` называется Liquid Monad ETH. На T **весь Ethereum supply 8 085,725173 долей принадлежит Liquid ETH**. Это nested portfolio claim, не доказательство независимых внешних депозитов в оба продукта.

Цепочка getter identity: vault `hook()` → Teller `0x0698ba360468a8c3f62d6c57b01b874016c2b854` → `accountant()` `0x5ce04a3d8d5297a24bf752d0172064941d8d853b`. Teller `vault()` и Accountant `vault()` возвращают исходный vault. Accountant `base()` возвращает Ethereum WETH. Getter `getRate()` на T — **1,005322540540 ETH/share**; последнее update 2 октября 21:22:35 UTC. Его age 2 часа 37 минут. Fee fields platform/performance на T равны нулю; это не полная история комиссий.

Book claim Liquid ETH составляет 8 128,761773 ETH-equivalent, около **$21,687 млн**. Этот расчет уменьшает residual общего Liquid ETH с $34,140 млн до $12,453 млн, с 7,223% до 2,634%. Он опирается на собственную книгу nested vault, а не UI weight, и не доказывает remote physical backing.

На Monad chainId 143 тот же vault contract существует. Block 110 031 481 timestamp=T, следующий block timestamp=T+1: boundary проверен. Local share supply на T равен нулю, hook имеет тот же адрес. Same-address Accountant на Monad даёт `getRate()`=1.0, отличный от Ethereum. Это означает, что единую цену доли для всех сетей нельзя предполагать без проверки синхронизации. Нулевой local supply не доказывает отсутствие underlying portfolio в этой сети.

Teller verified source содержит burn/mint bridging shares. In-flight messages и весь circulating supply остальных сетей не восстановлены. Ethereum current token discovery показывает преимущественно WETH остаток, недостаточный для общей оценки: remote deployments нельзя выводить из одного execution wallet.

UI Liquid ETH 3 октября показывает Monad sleeve 6,28% около $29,7 млн при current total TVL. Он превышает восстановленный Ethereum nested book claim на T. Различия dates, rate refresh, состава или иных claims требуют reconcile; остаток не заполнен этой разницей и не назван дефицитом.

Первичные contracts: [vault verified source](https://eth.blockscout.com/address/0xa024063b630d554078bbf985718b22f3c6870ee0?tab=contract), [Teller](https://eth.blockscout.com/address/0x0698ba360468a8c3f62d6c57b01b874016c2b854?tab=contract), [Accountant](https://eth.blockscout.com/address/0x5ce04a3d8d5297a24bf752d0172064941d8d853b?tab=contract). Fixed-block evidence: `mono_identity_T.json`, `mono_hook_T.json`, `mono_accountant_T.json`, `mono_remote_T.json`. Предположенный GitBook URL возвращает HTTP 200 с «Page Not Found» и не используется как подтверждение продукта.

Следующая необходимая глубина — remote asset/loan inventory, asset bridges/custody, periodic PPS reconciliation и исполнимый exit. До неё nested book claim не равен independently verified underlying NAV.
