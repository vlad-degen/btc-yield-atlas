# Lending и LP: капитал, плательщики и ликвидность

Срез T — 2 октября 2026, 23:59:59 UTC. Материал соединяет широкий protocol screen и verified positions ether.fi; он не является полным account census всех сетей.

## Lending — крупный deployment layer

Датированные ETH-family observations: Aave V3 $9,835 млрд, SparkLend $4,161 млрд, Sky Lending $1,639 млрд, Morpho Blue $1,422 млрд, Compound V3 $724,582 млн, Fluid Lending $231,542 млн. Это underlying/receipt balances adapter, с разными учётными механиками. Их нельзя прибавить к staking issuers и managed vault NAV. Aave ETH-family subtotal — во многом weETH, wstETH и rsETH collateral, а не исключительно ETH, приносящий supply interest.

ETH lender получает платежи borrowers. Условно supply APR ≈ borrow APR × utilization × (1 − reserve factor), без rewards и compounding corrections. При большом idle cash supply yield может быть близок к нулю. [Aave liquidity pool](https://www.aave.com/docs/aave-v3/concepts/liquidity-pool) также связывает возможность withdrawal с unborrowed reserve liquidity. [Morpho interest accounting](https://docs.morpho.org/developers/borrow/concepts/interest-rates/) объясняет lazy accrual: stored market debt нужно доначислять при независимом NAV расчёте.

Fixed-block пять WETH markets Aave четырёх сетей и Spark дают 2,881m lender claims и 2,388m debt. Main Liquid ETH account составляет 23,28% variable WETH debt Aave Ethereum. Отдельные reserve deficit getters показывают около 52964 WETH Ethereum и 29835 WETH Arbitrum, без утверждения о final haircut. Полный selected-market balance analysis: [LENDING-MARKETS.md](../LENDING-MARKETS.md).

Нельзя считать income на весь ETH collateral как borrow interest. Для определения плательщика нужны конкретные loan asset, market, outstanding debt, rate, collateral и borrower purpose. ETH debt под LST часто связано с loops, но stable debt под ETH может финансировать carry, leveraged ETH long, business needs или вывод денег. Без проверки применения loan classification остаётся вероятностным.

## Borrower scan

Morpho API scan охватывает 25 выбранных ETH-collateral markets с WETH или stable loan assets, по десять крупных positions каждого. Получены 237 positions и 213 unique `(chain,address)` borrowers. Это current discovery после T и ограниченный top-N, без полного pagination всех borrowers. ETH-debt и stable-debt rows разделены; каждой позиции нельзя автоматически присвоить carry.

Крупный wstETH/USDT borrower `0x7ee293…` связан contract getters с общим Concrete Safe. Current его loan около $70,395 млн. Этот результат связывает протокольный demand с управляемым portfolio, но не распределяет все Safe assets между private vaults. Крупные positions Liquid ETH проверены на fixed block отдельно.

Aave account scan пока ограничен verified управляющими accounts пилота. Полный event/indexer census Aave, set исторических borrowers и repayment destinations ещё не восстановлены. Покрытие borrower screen нельзя выдавать за долю всех carry strategies.

## LP — доход за исполнение торговых потоков

LP получает fees и иногда incentives, одновременно меняя состав underlying. Для ETH/LST пары корреляция цен не устраняет depeg и adverse selection. Concentrated LP становится односторонним вне range и перестаёт получать swap fees, как описано в [Uniswap concentrated liquidity](https://developers.uniswap.org/docs/get-started/concepts/liquidity-providers/concentrated-liquidity). TVL pool не равен одновременно fee-earning active liquidity; virtual reserves не являются внешними активами.

В Liquid ETH проверены NFT 1363661 и 1363660: token0 WETH, token1 weETH, fee tiers 500 и 100. Principal по sqrtPrice/ticks и issuer conversion составляет 6 875,525431 ETH-equivalent, около $18,344 млн. Uncollected fee growth не включён; три старых NFT имеют liquidity=0. ERC20-only inventory пропустил бы весь этот капитал.

Fluid NFT 4241 / vault 74 использует smart collateral weETH/native ETH и долг wstETH. Его net equity около 3 073,874326 ETH-equivalent, $8,201 млн. Расчёт применяет pro-rata **real** reserves, supply shares из packed storage, сверенные через resolver, и subtracts debt. Суммирование imaginary reserves, gross smart collateral и vault book NAV дало бы повторный учёт.

Current UI относит к Uniswap LP 4,05% Liquid ETH и к Fluid LP 1,81%; эти веса после T не используются для восстановления fixed-block amounts. Их нельзя распространить на весь LP рынок.

## Что требуется для capacity и стрессов

Нужно измерять borrow reserve liquidity, DEX executable depth и issuer redemption throughput отдельно. Для unwind loop требуется сначала доступный debt asset и возможность снять collateral; LP exit может давать менее ликвидный receipt вместо ETH. Rate shock, collateral oracle shock и DEX discount — три разных сценария.

Raw NFT calls, pool identities и resolver state сохранены в `data/eth/pilot_more_T.json`, `etherfi_uniswap_positions.json`, `fluid_pilot_decoded.json`; borrower rows — `morpho_borrower_screen.json`. LP aggregate ETH-side principal всех major-chain pools пока не вычислен. Full mixed-pool TVL discovery не является этой величиной.
