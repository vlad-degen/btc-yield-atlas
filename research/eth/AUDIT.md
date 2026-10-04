# Источники, границы проверки и воспроизведение

Исследовательский выпуск на 3 октября 2026. Integrity validation и экономический аудит — разные уровни: прошедшая арифметическая проверка не подтверждает solvency, legal rights или исполнимый withdrawal.

## Зафиксированный срез

T = **1790985599**, 2 октября 2026, 23:59:59 UTC.

| Сеть | Chain ID | Последний block ≤ T | Timestamp следующего block |
|---|---:|---:|---:|
| Ethereum | 1 | 26 108 081 | T+12 s |
| Optimism | 10 | 157 693 411 | T+2 s |
| Base | 8453 | 52 098 126 | T+2 s |
| Arbitrum | 42161 | 511 139 919 | T+1 s |
| Monad — nested sleeve check | 143 | 110 031 481 | T+1 s |

Headers и hashes сохранены в `snapshot_manifest.json` и `mono_remote_T.json`. 66 archive benchmark block reads по Ethereum/Optimism проверяются на timestamp ≤ target. Historical points включают 24 month ends, начало окна и дополнительные return endpoints. Нет интерполяции balances с будущего блока.

ETH quote — $2 667,9504418816 с timestamp T+1, confidence 0,99. Это раскрытый ближайший reference quote. USD mark не является ценой исполнения позиции. Source ages API protocol points обычно 86 399 секунд: datapoint приходится на начало последнего дня, тогда как fixed execution snapshot — на его конец.

## Слои источников

1. **Fixed-block RPC:** supply, convertToAssets, account collateral/debt, ownership, reserve cash/rates, NFT data, proxy slots. Наиболее сильный источник contract state, но oracle/book value ещё не равна executable market NAV.
2. **Verified source и первичная документация:** ABI, accounting, bridge burn/mint, queue, fee mechanics, risk disclosures. Current verified implementation не считается historical implementation без storage/getter proof на T.
3. **Датированные aggregator API:** token observations 87 отобранных протоколов и history. ETH-family filters сохраняют source age, signs и `misrepresentedTokens`.
4. **Current discovery и public UI:** yield pools, Pendle listings, Morpho top borrowers, Ether.fi allocation, Ethena backing, JustLend public API. Они собраны после T и всегда помечены отдельно.
5. **Аналитические модели:** return conversion, self-credit, break-even и stresses. Все исходные единицы и assumptions сохраняются в semantic JSON.

HTTP 200 не доказывает содержательную корректность ответа. Например guessed Monad GitBook URL возвращает «Page Not Found»; он не подтверждает identity. Пустой HTTP 202 не считается данными. RPC response может содержать individual errors внутри HTTP 200. Ошибки и excerpt error bodies сохранены, не преобразованы в нулевые balances.

## Реальный объём покрытия

В current screen: 16 992 feed pools → 5 688 ETH-family candidates, 197 feed projects, 57 chains; 259 pools ≥ $5 млн full-pool TVL. 206 symbol-only candidates отделены от основного поиска. Выбранный набор для token history — 87 протоколов, 82 с aggregate token history. 2 088 protocol-month rows включают 247 missing observations.

Aggregate token history отсутствует у Balancer V2, Midas RWA, SushiSwap, Uniswap V3 и Uniswap V4. Это особенно существенно для LP: отсутствие token history не означает нулевой ETH principal. Current mixed-pool listings не исправляют такой пробел исторического ETH-side inventory.

`misrepresentedTokens=true` у ряда adapters, включая ether.fi Liquid/Stake, Gearbox, некоторые DEX/aggregators. Эти data points используются как reported accounting, не как прямое доказательство native wallet reserves. Current category — hint, не доказанная historical mechanism.

Vault registry содержит выбранные contract candidates, включая BTC/USD negative controls. Он не объявлен исчерпывающим ETH product inventory. 12 досье имеют разную глубину: fixed-block reconciliation, borrower look-through, первичные disclosures или segment mechanics. Они не все независимо reconciled до конечного backing.

Morpho borrower screen — 25 selected markets, top 10 positions каждого, 237 positions/213 unique chain-address borrowers. Полного account census нет. Pendle four-chain listing paginated полностью: 626 listed unique markets; ETH accounting subset 126. Из них 122 expired. Это полнота API listings выбранных четырёх сетей, не полнота всей fixed-yield экономики.

## Integrity и numerical checks

`tools/eth/audit.py` сверяет:

- SHA256 всех сохранённых API response files и наличие файлов, включая UI observations в отдельном manifest.
- Неизменность 384 оригинальных BTC файлов относительно исходного inventory.
- Fixed-block boundaries и отсутствие будущих benchmark/history points.
- Supply × rate Liquid ETH NAV, строки частичного баланса и явно сохранённый residual.
- Uniswap token order и ETH-equivalent principal; Fluid gross/debt/net leverage.
- Историческую identity Treehouse denomination и rsETH oracle.
- Единое 730-дневное окно шести return series; missing intermediate point не заменяется нулём.
- Уникальность protocol-month rows и сохранённые missing.
- Корректные carry supply-share fractions и различие kBTC/syrupUSDC.
- Nested Monad internal supply, Concrete sole holders, Pendle expiry и listing coverage.
- `null` неизвестных market net totals, reconcile gross screen и local artifact links.
- Fixed-block totals пяти WETH lending markets, отдельные reserve deficit getters и claim-ledger input hashes.

Результат — `data/eth/audit_results.json`; raw file manifest — `data/eth/raw_manifest.json`; claim ledger — [EVIDENCE.md](EVIDENCE.md). Проверка не подтверждает полный portfolio provenance, custody rights, AVS reward entitlement, fresh private NAV или execution paths.

## Воспроизведение без сетевых обновлений

Все semantic outputs восстанавливаются из **уже сохранённого raw**. Raw namespace игнорируется Git; для передачи исследования его нужно включить в data handoff отдельно. Manifest позволяет проверять bytes/hash после копирования. Замена raw свежим API создаёт другую research vintage.

Из корня проекта:

```sh
python3 tools/eth/rebuild.py
```

Rebuild последовательно выполняет deterministic local derivations, не делает API/RPC requests и не трогает original BTC outputs. График использует bundled Python с ReportLab/Pillow, путь можно переопределить переменной `ETH_FIGURE_PYTHON`. После charts запускается audit.

## Повторный сбор источников

Для **нового vintage** следует выбрать новый T и raw namespace, проверить все chain boundaries и обновить provenance. `collect.py` сейчас зафиксирован на T этого исследования; простое повторение current API requests может смешать сборы внутри одного raw directory. Не обновляйте current sources и не представляйте их как frozen T.

Сбор в этом выпуске выполнен read-only через публичные источники. Public API GET/POST и eth_call не отправляют transactions. Основные entrypoints: `collect.py bootstrap/protocols/consensus/pilot/balances/ratelogs`, `benchmark.py`, `op_history_rates.py`, `vaults.py`, `vault_history.py`, `rseth_benchmark.py`, `carry_lookthrough.py`, `mono_lookthrough.py`, `lending_liquidity.py`, address-specific getters. Полный invocation log с URL/payload/time/hash — `raw/eth/2026-10-02/requests.jsonl`. Public UI observations записаны вручную и обозначены как такие.

## Что нельзя вывести из этого выпуска

Нет защищаемого unique-underlying total или external-depositor-equity total всего рынка. Причины — неполный historical native consensus state, overlapping issuers/receipts, bridges, gross leverage, internal shares и custody disclosures. Full-pool screening sum $70,939 млрд не является ни точным total, ни доказанной границей net рынка.

Liquid ETH residual $12,453 млн после nested book valuation не назван дефицитом. 97,37% book NAV, объяснённые выбранными marks/claims, не означают 97,37% independently audited backing. Monad remote assets, rewards ownership, fee growth и Morpho accrued interest остаются открытыми.

Historic current-universe selection имеет survivorship bias. Price/PPS returns не учитывают все external distributions и user execution costs. Stresses держат позиции/rates условно фиксированными; DEX/withdrawal/funding simulations ещё не выполнены. Послойная карта и опубликованные gaps позволяют продолжить исследование без ложной точности.
