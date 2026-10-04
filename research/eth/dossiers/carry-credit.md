# Dollar credit legs внутри ETH vault

Исследование на 3 октября 2026; контрактные balances — на T 2 октября, 23:59:59 UTC. Это look-through рукавов Liquid ETH, а не отдельный рейтинг всех USD продуктов.

## Проверенные claims

| Контракт | Book assets | Claim Liquid ETH | Доля book assets |
|---|---:|---:|---:|
| senRLUSDv2 `0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf` | 444,242 млн RLUSD | 55,105 млн RLUSD | 12,40% |
| senPYUSDPRIMEv2 `0xc21b08c16458202593d4d9b26b9984ee67b38bbd` | 219,084 млн PYUSD | 49,605 млн PYUSD | 22,64% |

В обоих используется Morpho Vault V2 с одним MorphoMarketV1AdapterV2. `parentVault`, market IDs, supply shares и market parameters проверены на T. RLUSD имеет 18 decimals, PYUSD — 6; shares обоих vaults имеют 18. Доля senPYUSDPRIMEv2 представляет около 2,02486 PYUSD. One-share=$1 здесь неверно.

## Где работают доллары

| Рынок senRLUSDv2 | Доля всего book assets, приблизительно |
|---|---:|
| kBTC/RLUSD | 52,89% |
| weETH/RLUSD | 24,09% |
| USDe/RLUSD | 7,23% |
| cbBTC/RLUSD | 2,99% |
| FXRP/RLUSD | 1,92% |
| syrupUSDC/RLUSD | 1,11% |
| wstETH/RLUSD | 0,31% |

Оставшаяся доля включает idle/unallocated и другие малые positions; это не доказанный полностью liquid buffer. Metadata всех collateral tokens подтверждена адресными calls. Особенно важно не перепутать kBTC `0x73e0…` с syrupUSDC `0x80ac…`.

У senPYUSDPRIMEv2 около 95,04% book assets выделено в PRIME/PYUSD. Stored market utilization около 91,80%; у weETH/RLUSD — около 88,34%, у kBTC/RLUSD — около 90,32%. Вытянуть весь supply одновременно без repayments при таких utilization нельзя предполагать.

Источник supply income — процент borrowers, за вычетом curator fee и потенциальных losses. PRIME добавляет credit economics: [Sentora](https://sentora.com/case-studies/sentora-s-prime-main-vault-reaches-200m-in-pyusd-deposits-in-under-100-days) описывает финансирование originators между выдачей home-equity loans и securitization. Stable lenders несут collateral/liquidation risk PRIME, а PRIME holder — underlying credit и extension risk. Это связанные, но разные требования.

Performance fee на T: 10% у RLUSD-vault, 15% у PRIME-vault; management fee обоих равна нулю. Это комиссии вложенных vaults, поверх которых ETH wrapper имеет свою fee economics. Нельзя вычитать их ещё раз, если используемый net PPS уже их учитывает.

## Взаимное кредитование

Liquid ETH инвестирует через supply vaults и одновременно его главный account/LoanManager занимают в части тех же markets. На T adapter supply shares покрывают практически весь supply weETH/RLUSD и PRIME/PYUSD. Через долю Liquid ETH во внешних vaults получаются около 8,709 млн RLUSD и 4,759 млн PYUSD look-through self-credit notional.

Расчёт использует доли vault, доли adapter в market supply shares и controlled borrower debt из stored market ratio. Последующее interest accrual не добавлено; это diagnostic principal estimate, не месячный revenue ledger. Независимый income нужно получить как проценты от внешних borrowers плюс кредитный доход за вычетом долга, fees и losses. Internal interest transfer не создаёт новый экономический доход сам по себе.

## Cap и пределы анализа

Отдельный STCUSD claim Liquid ETH представляет 24,626 млн cUSD. [Механика Cap](https://docs.cap.app/overview/protocol-overview/stcusd-mechanics) связывает income с borrower payments, idle reserve yield и underwriter security. Заявленное coverage нужно проверить по available collateral, slashing/realization procedure и priority claims; token conversion не заменяет этот анализ.

UI также называет Yuzu. Его конкретный claim и конечные позиции в этом выпуске не восстановлены. Поэтому UI Stable Carry нельзя полностью отождествить с суммой уже прочитанных ERC20 receipts.

Ключевой insight: ETH unit of account не означает, что конечный плательщик и collateral всех loan legs связаны только с Ethereum. Risk graph пересекает BTC, XRP, stablecoins и residential credit, сохраняя ETH-залог и условия repayment на другом уровне.

Данные: `carry_vaults_T.json`, `carry_market_allocations_T.json`, `carry_collateral_assets_T.json`, `carry_credit_lookthrough.json`, `pilot_details_T.json`. Полный независимый underlying-credit audit и юридическая enforceability PRIME/Cap claims остаются за пределом доказанного balance sheet.
