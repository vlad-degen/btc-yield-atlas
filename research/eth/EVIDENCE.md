# Evidence ledger: что именно подтверждает каждый вывод

Это claim ledger исследовательского выпуска. Confidence относится к конкретной части вывода: fixed-block state может быть надёжен, тогда как independent backing и cash realization той же позиции неизвестны. Hashes semantic inputs и raw source responses сохранены в `data/eth/evidence_ledger.json`. Manual public UI observations отмечены отдельно.

| ID | Проверенный результат / исследовательское ограничение | Время и предел вывода | Основной data artifact |
|---|---|---|---|
| C01 | 5 688 ETH-family pools / 57 chains / 197 feed projects | current screen, не net total | [discovery_summary.json](../../data/eth/discovery_summary.json) |
| C02 | 82 protocol sources с token history; 24 месяца и 247 missing rows | dated API observations | [protocol_source_coverage.json](../../data/eth/protocol_source_coverage.json) |
| C03 | Liquid ETH book NAV 177 171,063302 ETH | T, book value | [etherfi_verified_metrics.json](../../data/eth/etherfi_verified_metrics.json) |
| C04 | Частичный баланс $460,231 млн; residual $12,453 млн | T, marks + nested book claims, backing не audited | [etherfi_partial_balance_sheet.json](../../data/eth/etherfi_partial_balance_sheet.json) |
| C05 | Loop Aave 13,325× и HF 1,02708 | T oracle-valued account | [etherfi_verified_metrics.json](../../data/eth/etherfi_verified_metrics.json) |
| C06 | Carry 64,66% и loops 21,65% в опубликованном breakdown | 3 октября UI, не fixed-block allocation | [etherfi_verified_metrics.json](../../data/eth/etherfi_verified_metrics.json) |
| C07 | Liquid ETH +6,8501% / stETH +5,4875% за 730 дней | Published PPS/conversion; external rewards и costs excluded | [etherfi_staking_comparison.json](../../data/eth/etherfi_staking_comparison.json) |
| C08 | senRLUSD: kBTC 52,89%, weETH 24,09% book allocation | T, expected assets and raw supply shares | [carry_credit_lookthrough.json](../../data/eth/carry_credit_lookthrough.json) |
| C09 | PRIME/PYUSD около 95,04% carry vault assets | T, credit economics via separate disclosure | [carry_credit_lookthrough.json](../../data/eth/carry_credit_lookthrough.json) |
| C10 | Self-credit notional 8,709m RLUSD и 4,759m PYUSD | economic overlap, не added asset или measured income | [carry_credit_lookthrough.json](../../data/eth/carry_credit_lookthrough.json) |
| C11 | Concrete vaults имеют общий 3-of-5 Safe | T; exclusive backing allocation неизвестна | [concrete_lookthrough_T.json](../../data/eth/concrete_lookthrough_T.json) |
| C12 | Concrete Delta supply целиком у sole holder; ctwst supply у Safe | T; genesis mint не доказывает отсутствия backing | [concrete_self_holdings_T.json](../../data/eth/concrete_self_holdings_T.json) |
| C13 | Fluid Lite L=7,759×; 730-day ETH book return +8,8243% | T contract valuation; parity assumptions | [fluid_lite_balance_T.json](../../data/eth/fluid_lite_balance_T.json) |
| C14 | Treehouse IAU исторически wstETH-denominated; ETH return +6,2761% | 730 дней; independent backing не reconstructed | [treehouse_denomination_history.json](../../data/eth/treehouse_denomination_history.json) |
| C15 | CIAN rsETH ETH book return +1,0854% за 730 дней | issuer oracle conversion; rewards/recovery costs excluded | [rseth_benchmark_rpc.json](../../data/eth/rseth_benchmark_rpc.json) |
| C16 | JustLend mapped ETH около 484k units, APY 0,0002899% | current 3 октября; Ethereum backing не verified | [justlend_eth_semantics.json](../../data/eth/justlend_eth_semantics.json) |
| C17 | Ethena ETH basis legs около $374,44m | 3 октября rounded UI disclosure; no custodial audit | [ethena_ETH_basis_observation.json](../../data/eth/ethena_ETH_basis_observation.json) |
| C18 | Pendle 626 listed / 126 ETH-family / 122 expired | four-chain current API; expiry evaluated against T | [pendle_source_coverage.json](../../data/eth/pendle_source_coverage.json) |
| C19 | Nested Monad claim около $21,687m; rates ETH/Monad различаются | T; remote backing open | [mono_identity_T.json](../../data/eth/mono_identity_T.json) |
| C20 | Main Aave debt 410134 WETH; reserve cash 269693 WETH | T, reserve cash не guarantee flashloan eligibility | [lending_reserve_T.json](../../data/eth/lending_reserve_T.json) |
| C21 | Model zero-return borrow uplift Aave 44,3bp | mixed trailing-30d staking proxy / T APR; no forecast | [loop_economics_T.json](../../data/eth/loop_economics_T.json) |
| C22 | Unique underlying и external equity market totals остаются null | overlap / consensus / custody / identity gaps | [market_summary.json](../../data/eth/market_summary.json) |
| C23 | Пять выбранных WETH markets: 2,881m lender claims / 2,388m debt | T; gross lending claims, не unique underlying | [weth_lending_markets_T.json](../../data/eth/weth_lending_markets_T.json) |
| C24 | Aave WETH reserve deficit: ETH 52964 / Arbitrum 29835 WETH | T contract getter; не established final investor haircut | [weth_lending_markets_T.json](../../data/eth/weth_lending_markets_T.json) |
| C25 | Liquid ETH main account: 23,28% variable WETH debt Aave ETH | T; selected borrower concentration | [weth_lending_summary_T.json](../../data/eth/weth_lending_summary_T.json) |

## Первичные связи и воспроизводимость

Claim ledger не превращает secondary adapters в первичное доказательство reserves. Для RPC claims полные request payloads содержат block tags, addresses, selectors и результаты; verified source/ABI и identity getters привязаны к relevant contracts. [AUDIT.md](AUDIT.md) описывает уровни источников.

Цена доли, размер кредита, cash balance, oracle mark и исполненная выплата — разные факты. Row C22 преднамеренно оставляет неизвестные totals открытыми. Если появятся данные, противоречащие книгам или disclosures, нужно сохранить обе vintage и объяснить reconciliation. Ошибки источников не заменяются нулём.
