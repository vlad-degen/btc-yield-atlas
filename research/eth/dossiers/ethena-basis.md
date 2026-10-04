# ETH basis leg Ethena

Дата: 3 октября 2026. ETH используется в backing dollar продукта; этот leg относится к E9 и учитывается отдельно от ETH-long yield products.

## Что получает инвестор

USDe/sUSDe сохраняют преимущественно USD exposure. Spot ETH и short derivative уменьшают совокупную ETH/USD delta. Source of yield — staking, когда backing действительно staked, и funding/basis после hedging/custody costs. Current [Protocol Revenue](https://docs.ethena.fi/backing-assets/protocol-revenue) включает также lending, RWA и rewards liquid stables. Поэтому доход всего sUSDe не равен доходу ETH basis leg.

## Проверенный public disclosure

В раскрытой [таблице backing assets](https://app.ethena.fi/dashboards/backing-assets), помеченной updated 3 Oct 26 11:00 без явно указанного timezone:

| Venue / custody | ETH leg, rounded USD | Display APY |
|---|---:|---:|
| Binance / Ceffu | $202,12 млн | 6,0% |
| Bybit / Copper | $81,62 млн | 4,8% |
| OKX / Copper | $90,70 млн | 4,4% |

Сумма $374,44 млн. На остальных раскрытых basis venues Deribit и Coinbase Derivatives Exchanges ETH rows не показаны. Whole crypto basis — $928,89 млн, около 19,1% backing; остальные categories включают около $1,7 млрд DeFi lending, $621,43 млн institutional lending, $1,34 млрд liquid stables и $283,55 млн RWA. Это rounded current UI values, не fixed-T custody audit.

Неиспользованный как headline global menu показывал supply, отличающийся от таблицы transparency. Этот конфликт записан в observation. Совокупный USDe TVL нельзя присвоить ETH рынку даже при точном supply.

## История стратегии и риски

В [отчёте risk committee за май 2026](https://gov.ethenafoundation.com/t/ethenas-may-2026-governance-update/796) ETH basis был $94 млн, BTC $297 млн, liquid cash около 89% backing. Это историческое раскрытие, не allocation на T. Сопоставление с current UI показывает, что смысл общего «Ethena yield» меняется вместе с allocation.

Короткий derivative может получать отрицательный funding, требовать margin при росте ETH и зависеть от settlement custodian→venue. [Funding Risk](https://docs.ethena.fi/protocol-overview/risks/funding-risk) описывает dynamic allocation и reserve fund. Historical averages из документации не используются как current expected return.

Custodial omnibus address balance не равен принадлежащему Ethena портфелю: [официальное dashboard explanation](https://docs.ethena.fi/backing-custody-and-security/real-time-dashboards) прямо предупреждает о co-mingled solutions. Для independent reconstruction нужны dated attestations, позиции derivatives, haircut/margin и legal claims, а не сумма token transfers на deposit wallets.

## Предел проверки

Получены current ETH-only disclosure и механика дохода. Не восстановлены ETH notional на T, полного matched funding history, реализованные trading/custody costs, investor share этого leg и исполнимый institutional redemption. sUSDe current APY из UI не используется как фактический ETH-return.

Данные: `ethena_ETH_basis_observation.json`; raw `ethena_ui_observation.json`, `ethena_revenue`, `ethena_basis`, `ethena_funding_risks`, `ethena_may2026`, `ethena_dashboard_doc`.
