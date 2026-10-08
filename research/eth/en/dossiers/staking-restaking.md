# Staking and restaking

Snapshot T: 2 October 2026, 23:59:59 UTC. Map figures are counted once ([MARKET-STRUCTURE](../MARKET-STRUCTURE.md)).

## How much ETH is staked, and how much the map counts

| Layer | ETH at T | In the map? |
| --- | ---: | --- |
| Beacon chain, active stake (slot 15,346,798) | 43,805,558 | Ceiling, not a row |
| Staking tokens and pools, staked and held (net of tokens in lending markets and other products) | 11,901,177 | Yes (Staking) |
| Restaking tokens held; EigenLayer and Symbiotic only where no token or product counts | 411,377 | Yes (Restaking) |
| Staking and restaking tokens posted in lending markets | about 5.48M | Yes (leveraged staking, carry, money markets) |
| Off-chain: exchanges 4.57M, institutional providers 4.73M, BitMine 5.07M | about 14.4M | Listed, not counted ([OUTSIDE-AND-SMALL](../OUTSIDE-AND-SMALL.md)) |
| Rest: solo and untagged validators, staking tokens held inside other map rows | about 11.5M | Not split further |

Largest staking rows: Lido 6.59M, Binance wBETH 3.73M, Rocket Pool 0.46M, cbETH 0.36M, Liquid Collective 0.27M, StakeWise 0.24M. Largest restaking rows: EigenLayer direct 0.21M, ether.fi 0.07M, Renzo 0.04M. In lending markets sit Lido 2.97M, ether.fi 1.83M, Kelp 0.39M, StakeWise 0.13M, Coinbase 0.09M, Rocket Pool 0.05M.

### Native stake: measured backing

The archived consensus state at T has **43,805,557.723 actual active ETH**, **43,739,959 effective active ETH** and **874,362 active validators** (22,432 of them exiting), read from the validator objects, not validator count times 32. Slot **15346798**, state root `0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282`; the provider marks it finalized. Monthly state reads cover May to September 2026; earlier states are pruned at the tested public endpoints. [Archived state endpoint](http://testing.mainnet.beacon-api.nimbus.team/eth/v1/beacon/states/15346798/validators?status=active_ongoing,active_exiting,active_slashed), [monthly observations](../../../../data/eth/native-staking-observations.csv), [reconstruction](../../../../data/eth/finalization_reconstruction.json).

## Findings

- **Staking pays less every year.** Lido's oracle reports show consensus rewards falling from 2.78% to 2.38% gross and priority fees plus MEV from 0.55% to 0.09% between October 2024 and September 2026. Issuers keep 5 to 15% (Lido 10%, Renzo 15%, Kelp and Puffer 5%).
- **Staking grew, restaking shrank.** Staked and held rose from 9.59M ETH (October 2024) to 11.90M; Binance's wBETH added 2.18M. Restaked and held fell from 2.51M ETH to 0.42M as weETH and rsETH moved into lending markets.
- **Restaking paid in its own token, and less each year.** EigenLayer distributed $137M in its first year and $36M in its second, 99.6% of it EIGEN; services paid $0.75M in two years. ETH and LST restakers got 0.78% and then 0.18% a year, and nothing programmatic since 30 July 2026. The 13 real slashes (32.4k ETH equivalent) all came from one operator's redistributable sets.
- **weETH trailed stETH by 0.19 pp over two years** (5.2947% against 5.4875% cumulative conversion growth to T).

## rsETH shows why chain-specific redemption matters

The 18 April 2026 incident involved 116,500 rsETH, approximately $292M in the party's published estimate. [LayerZero's 20 May report](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report) attributes the forged message to compromised RPC infrastructure and a single-DVN configuration. This is the report author's attribution, not an independent determination of responsibility.

[Kernel's 19 June publication](https://blogs.kerneldao.com/blog/recovering-rseth-from-sunset-networks) describes the end of bridging from 15 June on 20 chains, including Optimism and Monad. Quarterly recovery continues to June 2027, with a 100 USDC fee per address. The author's statement that Ethereum L1 backing remains intact was not independently verified.

Historical `rsETHPrice()` or `paused=false` on L1 does not prove that holders on another chain can withdraw promptly. A common ETH accounting asset still requires a separate redemption analysis for each chain. No recovery transactions, burns or payments are executed in this research.
