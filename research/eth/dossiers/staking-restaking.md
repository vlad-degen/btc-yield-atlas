# Staking и restaking: underlying, дополнительный доход и redemption

Срез T — 2 октября 2026, 23:59:59 UTC. Это досье базовых слоёв рынка; их капиталы пересекаются с lending, PT и managed vaults.

## Кто платит

Native staking даёт protocol issuance, execution tips и MEV, с вычетом operating costs, commissions и penalties. Новый депозит в LST не создаёт отдельный источник дохода: это способ владеть тем же validator backing. [Ethereum staking](https://ethereum.org/staking/) описывает этот базовый механизм; execution deposit-contract balance не заменяет active consensus balance.

В сохранённой public Ethereum.org странице 3 октября отображается 43 869 560 total ETH staked. У widget нет пригодного для T времени состояния; веб-кэш того же сайта показывает иной current показатель. Поэтому эта цифра — ориентир масштаба, **не установленный total на T**. Finalized header slot 15 346 798 получен, но полный historical state по slot/root публичными endpoints не восстановлен. Количество валидаторов × 32 не подходит при compounding balances и exits.

Restaking добавляет обязательства обеспечения внешних сервисов. Вознаграждение сервисов, validator staking income и token incentives нужно различать. Один ETH, обеспечивающий несколько сервисов, считается один раз в unique underlying и несколько раз только в карте обеспечиваемых обязательств. Общая архитектура native/LST restaking изложена в [EigenLayer whitepaper](https://docs.eigencloud.xyz/assets/files/EigenLayer_WhitePaper-88c47923ca0319870c611decd6e562ad.pdf). Этот документ сам по себе не доказывает current AVS revenue, payable rewards или разрешённые параметры slashing каждого конкретного сервиса.

## Крупнейшие датированные observations

Из API token history, преимущественно 2 октября 00:00 UTC:

| Протокол | ETH-family USD, млрд | Как читать |
|---|---:|---|
| Lido | 26,677 | backing accounting; receipt deployments повторяют этот капитал |
| Binance Staked ETH | 10,081 | issuer disclosure/adapter, не независимый custody audit |
| EigenCloud | 7,075 | native restaking и LST claims пересекаются с staking |
| ether.fi Stake | 5,188 | staking/restaking layer, не Liquid ETH vault |
| Rocket Pool | 1,409 | staking backing и receipt economy |
| Kelp | 1,130 | значимая доля backing в stETH/ETHx, overlap с Lido/Stader |
| StakeWise V3 | 1,017 | staking vaults и osETH collateralization требуют раздельного учёта |
| mETH Protocol | 0,637 | Ethereum validators и обращение на Mantle — разные сети учёта |
| Coinbase cbETH | 0,517 | receipt backing; не все Coinbase staking products входят в cbETH |
| Stader | 0,233 | ETHx underlying, используется и вышележащими products |

Строки не складываются. EigenCloud adapter использует virtual WETH representation native stake: её нельзя интерпретировать как ликвидный WETH balance execution wallet. Kelp stETH/ETHx backing нельзя добавить второй раз к Lido/Stader underlying. Датированные строки и source hashes: `data/eth/protocol_eth_observations.json`.

## Receipt accounting и benchmark

stETH rebases: число units растёт. wstETH сохраняет units, растёт stETH-per-token. [Lido wstETH contract](https://docs.lido.fi/contracts/wsteth/) определяет conversion; сравнение использует archive stEthPerToken. weETH exchange rate читается непосредственно из fixed-block `getRate()`. За 730 дней stETH-equivalent рост составляет 5,4875%, weETH — 5,2947%; без отдельно выплаченных rewards. Изменение quote не доказывает продажу/withdrawal по этому quote.

Redemption может проходить через protocol queue, secondary market или recovery process. [Ethereum withdrawals](https://ethereum.org/staking/withdrawals/) различает legacy и compounding validators; конкретная receipt queue может добавлять собственные сроки. Liquid ETH Lido NFT 122235 уже finalized, unclaimed: это требование на 25,069520 ETH, а не дополнительный продолжающий доход staking.

## rsETH: реализовавшийся bridge risk

18 апреля 2026 bridge incident затронул 116 500 rsETH, около $292 млн по сообщению стороны. [Отчёт LayerZero от 20 мая](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report) связывает forged message с компрометацией RPC environment и конфигурацией одного DVN. Это атрибуция автора отчёта, а не независимое установление ответственности.

[Сообщение Kernel от 19 июня](https://blogs.kerneldao.com/blog/recovering-rseth-from-sunset-networks) описывает прекращение bridging с 15 июня на 20 сетях, включая Optimism, Monad и ряд меньших сетей. Предложен quarterly recovery до июня 2027 с отдельной платой 100 USDC за адрес. Claim автора о сохранении L1 backing независимо не проверен. Исторический `rsETHPrice()` или `paused=false` на L1 не доказывает своевременный выход remote holder.

Эта история объясняет необходимость chain-specific redemption analysis даже при едином ETH accounting asset. В данном исследовании не выполняются recovery transactions, burns или платежи.

## Предел глубины

Нужны historical consensus state, issuer-by-issuer reserve reconciliation, AVS reward events, recipient ownership, realized slashing/credit losses и полный bridge inventory. Current TVL не заменяет выручку AVS; points до cash realization не добавляются к подтверждённому доходу.
