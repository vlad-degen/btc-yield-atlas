# CIAN rsETH Yield Layer

Срез: 2 октября 2026, 23:59:59 UTC. Ethereum vault `0xd87a19ff681ae98bf10d2220d1ae3fbd374ade4e`, подтверждён в [официальном contract registry CIAN](https://docs.cian.app/yieldlayer/for-builders-developer-documentation/yield-layer-contracts). Другие vaults и сети сохраняются отдельными products.

## Accounting и размер

На T `asset()` — rsETH; book assets около 1 416,5594 rsETH, supply 1 477,3937 shares, PPS около 0,958823231 rsETH/share. Доход в rsETH и ETH отличается. Исторический rsETH oracle через LRTConfig проверен на 33 точках; на T rsETHPrice около 1,081227340 ETH.

На последней dated adapter observation вся ETH-family часть CIAN около $6,718 млн. Aggregate protocol TVL значительно больше и содержит BTC/USD продукты. Токен `LFBTC-CIAN-ETH` — BTC product на Ethereum; наличие слова ETH в имени сети не делает его ETH underlying.

## Стратегия и доход

[Core concepts](https://docs.cian.app/yieldlayer/for-users-quick-start/core-concepts-and-yield-layer-page-overview) различают recursive staking и recursive restaking; для rsETH заявлена RR стратегия. Registry показывает Aave, Compound, converters и новые cross-chain components. Список текущих implementations не доказывает фактическую historical allocation.

За 365 дней rsETH assets/share уменьшились на 0,2105%; за 730 — на 4,1177%. После historically verified rsETH oracle conversion book return в ETH составляет 2,2455% и 1,0854%, соответственно. Это существенно слабее plain rsETH conversion growth за те же окна, но не полная investor P&L: points, distributions, migrations и fees необходимо сопоставить с соответствующими beneficiary addresses.

Нельзя приписывать разницу одному событию без position/event attribution. Срез включает 2026 rsETH bridge incident, но PPS/oracle history не измеряет secondary-market depeg и условия recovery на каждой сети.

## Fees, выход и риски

Текущая [fee documentation](https://docs.cian.app/yieldlayer/for-users-quick-start/fees) заявляет 8% performance fee и 0,02% exit fee, с net APY после performance fee. Это policy disclosure; полная историческая fee series этого vault не восстановлена.

Пользовательский exit включает CIAN withdrawal, unwind долгов и redemption rsETH. Liquidity или ограничения remote rsETH являются отдельным уровнем. Наличие положительного oracle rate не гарантирует возможность быстро получить ETH.

## Предел проверки

Есть verified identity, fixed-block book metrics и matched-window PPS. Нужны strategy allocations, independent assets/debts, rewards ownership, historical rates/roles и redemption simulation. Данные: `vault_registry_rpc_T.json`, `vault_history_rpc.json`, `rseth_benchmark_rpc.json`, `rseth_oracle_identity.json`, `vault_history_comparison.json`.
