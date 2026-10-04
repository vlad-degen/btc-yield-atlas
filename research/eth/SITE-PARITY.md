# Как ETH Research использует структуру BTC Research

Изучены основной `index.html`, generated `site/index.html`, `tools/site_data.py`, `tools/build_site.py`, chart functions, category switches, carry calculator, six top-product tabs, source/data sections и исходные deep dives. Проверен работающий BTC сайт в браузере. Главный файл BTC — автономный HTML; второе представление генерируется из него. Нативный результат ETH — такой же статический сайт, с отдельными HTML страницами для всех подробных материалов.

| BTC Research | ETH Research | Статус и существенное отличие |
|---|---|---|
| Итоговые ответы на первом экране | 57 сетей, 82 dated protocols, Liquid ETH excess и loop leverage | Есть; global net capital не придуман |
| Market map, категории и product table | География, three-view accounting, protocol/pool filters и полный каталог | Есть; ETH-family screen не подменяет net census |
| Carry mechanics и calculator | E1–E9 flows; ETH loop, USD carry и basis calculators | Есть; ETH-long и USD-neutral exposure разделены |
| Flow of funds каждого крупного продукта | 5 managed products, Etherfi contract stack, 3 exit routes, carry markets | Есть; выборка не названа точным top-5 external equity |
| Кто держит ключи и кто платит доход | Authority / Accountant / Timelock / Safe / loan dependencies | Проверенные relationships показаны; полный role/holder census остаётся открытым |
| TVL и yield history, события | 24 protocol month-ends, 6 comparable ETH PPS series, fee timeline | Есть; historical portfolio attribution и flow/price decomposition не закрыты |
| Depositor distribution | Concrete sole-holder/custody proof, Liquid ETH circulation по сетям | Частично; полный wallet-bucket анализ Liquid ETH ещё не выполнен |
| Yield/rewards decomposition | Staking benchmarks, interest models, carry collateral/self-credit | Есть selected analyses; полного realized rewards/fees ledger нет |
| Liquidity ladder и intraday stress | Cash/debt capacity, oracle markdown, debt-rate sensitivity, exit waterfalls | Есть contract-state/models; full executable simulations остаются открытыми |
| Risks / product playbook | Rate/oracle/credit/keys/bridge/exit risks и выводы для ETH продукта | Есть |
| Sources и воспроизводимая база | 25 claims, linked evidence, 26 standalone pages, CSV/JSON downloads | Есть |

Эта таблица не объявляет исследование завершённым по глубине BTC. Она сохраняет разницу между уже работающей презентацией, измеренными результатами и оставшимися доказательствами. Сайт позволяет презентовать текущее исследование без сокрытия этих границ.
