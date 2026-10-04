# ETH fixed yield и Pendle PT

Каталог прочитан 3 октября 2026. Expiry проверен относительно T 2 октября, 23:59:59 UTC. Показатели liquidity/APY — current API после T.

## Охват и жизненный цикл

Полностью paginated official API: Ethereum 494 listed markets, Arbitrum 92, Base 38, Optimism 2; всего 626 уникальных markets. ETH-family отбор производится по `accountingAsset.symbol`, а не произвольному ETH substring в описании underlying.

Выделены 126 ETH accounting markets. 122 expired не позднее T, четыре ещё unexpired:

| PT | Maturity | Current AMM liquidity, приблизительно | Implied APY |
|---|---|---:|---:|
| superWETH | 26 ноября 2026 | $373,9 тыс. | 4,92% |
| stETH | 30 декабря 2027 | $5 500,9 тыс. | 2,13% |
| SYpufETH | 26 ноября 2026 | $314,9 тыс. | 3,94% |
| mixWETH | 29 октября 2026 | $73,9 тыс. | 2,02% |

Все четыре находятся на Ethereum в этом каталоге. Общая liquidity около $6,264 млн — AMM pool figure, а не total outstanding PT principal, SY backing или весь рынок fixed ETH yield. Spectra и другие площадки остаются в discovery screen и требуют собственного contract catalog.

## Механика дохода

PT представляет maturity claim в определённой accounting unit. Покупка со скидкой задаёт implied yield при погашении, если unit и payout rules подтверждены. SY оборачивает yield asset; YT отделяет будущие yield/rewards. Сумма PT и YT отражает разложение одного underlying, а не удвоенный вклад. [Pendle PT mechanics](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT) описывает эти конструкции. В частности PT-wstETH redeemable в stETH accounting units, а PT-weETH — в eETH units, с отдельными exchange rates receipts.

Каждый рынок требует проверки SY exchangeRate, redemption tokens и PT unit. Например, «один PT» не всегда следует оценивать как один LST или один ETH. Implied yield из API не заменяет own contract conversion и route execution. Fees, early-exit slippage, LP inventory и rewards меняют investor P&L.

## Закрытые рынки остаются требованиями

Expired PT principal не получает нулевую стоимость. Его владелец может иметь непогашенный claim даже после прекращения активной AMM yield торговли. YT, PT и LP имеют разные cash-flow paths. Maturity migration нельзя автоматически интерпретировать как net withdrawals из ETH yield экономики.

Основная часть найденных markets уже expired; для historical market size нужна supply и redeemed principal, а не число активных UI rows. Для long-duration stETH PT сравнение требует той же ETH unit и горизонта staking benchmark.

## Предел проверки

Доказана pagination/expiry coverage этого API, не completeness всего ETH fixed-yield рынка. PT/YT supply на T, SY backing, владельцы и все market-wide redemption paths ещё не восстановлены. Данные: `pendle_source_coverage.json`, `pendle_eth_market_screen.json`, raw `pendle_markets_*`.
