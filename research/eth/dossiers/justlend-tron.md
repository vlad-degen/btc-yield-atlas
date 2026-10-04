# ETH representations в JustLend на Tron

Дата наблюдения public API: 3 октября 2026. Это current disclosure, не historical TRON block на T. Последняя dated DefiLlama observation на 2 октября показывает около $1,310 млрд cash ETH и отдельно около $236,5 тыс. borrowed ETH.

## Identity важнее символа

| Рынок | Underlying TRC20 | Delegator | Current directory |
|---|---|---|---|
| jETH | `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF` | `TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV` | active |
| jETHB | `TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh` | `TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6` | active |

[Deployed contracts](https://docs.justlend.org/developers/deployed_contracts/) объясняет смену названий: нынешний ETH прежде назывался ETHOLD, нынешний ETHB — ETH. Адреса не менялись. Статья 2023 об offboarding старого ETH описывает тогдашнее решение; current directory и API свидетельствуют о другом актуальном отображении и статусе. Текущий статус не доказывает восстановленное issuer backing.

[Официальное объявление 2023](https://support.justlend.org/hc/en-us/articles/20625315184793-Announcement-on-Enabling-Supply-and-Borrowing-of-ETH-New-and-Offboarding-ETHOLD) различает старую centralized representation и новый BTTC bridge token. Эти разные риски нельзя убрать переименованием.

## Баланс и yield

По [публичному API](https://docs.justlend.org/developers/apis/), current jETH cash около 484 121,559906 units, totalBorrows 87,513298, reserves 4,694534. jToken supply умножен на human exchange rate и независимо сопоставлен с `cash+borrows−reserves`. Числа API уже de-scaled, их нельзя повторно делить на 1e18. jToken имеет 8 decimals, underlying 18.

Borrow utilization около 0,0181%. Base annual supply rate — 0,0002899115%, active USDD mining reward — 0. Borrow rate около 2,0054%; низкая utilization означает, что даже этот interest приносит очень мало дохода относительно supply.

У jETHB cash около 472,99 token units, долг около 0,00904 units, reserve factor 100%, base supply rate и mining reward равны нулю. Это существенно меньший и экономически иной рынок.

## Вывод и пределы

Большой dollar TVL не гарантирует значительного доходного рынка. Здесь headline объём отражает преимущественно остатки ETH representation, а не активный ETH credit demand. Capital provenance, issuer reserves и доступное redemption Ethereum ETH не восстановлены. Нельзя маркировать этот cash как verified native ETH или исключить representation risk, основываясь на цена-oracle=$ETH.

Contract withdrawal/borrow controls, holder concentration и historical yield требуют отдельного TRON archive анализа. Данные: `justlend_eth_semantics.json`, raw `justlend_markets_current`, `justlend_rewards_current`, `justlend_contracts`; сохранены текущие статусы и точные addresses.
