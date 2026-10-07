# Staking and restaking

Snapshot T: 2 October 2026, 23:59:59 UTC. Map figures are counted once ([MARKET-STRUCTURE](../MARKET-STRUCTURE.md)).

## How much ETH is staked, and how much the map counts

| Layer | ETH at T | In the map? |
| --- | ---: | --- |
| Beacon chain, active stake (slot 15,346,798) | 43,805,558 | Ceiling, not a row |
| Staking tokens and pools, net of tokens held by other products | 15,016,520 | Yes (Staking) |
| Restaking tokens; EigenLayer and Symbiotic only where no token counts | 2,427,324 | Yes (Restaking) |
| Off-chain: exchanges 4.57M, institutional providers 4.73M, BitMine 5.07M | about 14.4M | Listed, not counted ([OUTSIDE-AND-SMALL](../OUTSIDE-AND-SMALL.md)) |
| Rest: solo and untagged validators, staking tokens held inside other map rows | about 12.0M | Not split further |

Largest staking rows: Lido 9.33M, Binance wBETH 3.74M, Rocket Pool 0.50M, cbETH 0.44M, StakeWise 0.37M. Largest restaking rows: ether.fi 1.69M, Kelp 0.40M, EigenLayer direct 0.20M.

### Native stake: measured backing

The archived consensus state at T has **43,805,557.723 actual active ETH**, **43,739,959 effective active ETH** and **874,362 active validators** (22,432 of them exiting), read from the validator objects, not validator count times 32. Slot **15346798**, state root `0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282`; the provider marks it finalized. Monthly state reads cover May to September 2026; earlier states are pruned at the tested public endpoints. [Archived state endpoint](http://testing.mainnet.beacon-api.nimbus.team/eth/v1/beacon/states/15346798/validators?status=active_ongoing,active_exiting,active_slashed), [monthly observations](../../../../data/eth/native-staking-observations.csv), [reconstruction](../../../../data/eth/finalization_reconstruction.json).

## Findings

- **Staking pays less every year.** Lido's oracle reports show consensus rewards falling from 2.78% to 2.38% gross and priority fees plus MEV from 0.55% to 0.09% between October 2024 and September 2026. Issuers keep 5 to 15% (Lido 10%, Renzo 15%, Kelp and Puffer 5%).
- **Staking grew, restaking shrank.** The staking row rose from 12.58M ETH (October 2024) to 15.09M; Binance's wBETH added 2.19M. Restaking fell from 4.67M ETH (July 2025) to 2.43M.
- **Restaking paid in its own token, and less each year.** EigenLayer distributed $137M in its first year and $36M in its second, 99.6% of it EIGEN; services paid $0.75M in two years. ETH and LST restakers got 0.78% and then 0.18% a year, and nothing programmatic since 30 July 2026. The 13 real slashes (32.4k ETH equivalent) all came from one operator's redistributable sets.
- **weETH trailed stETH by 0.19 pp over two years** (5.2947% against 5.4875% cumulative conversion growth to T).

## rsETH shows why chain-specific redemption matters

The 18 April 2026 incident involved 116,500 rsETH, approximately $292M in the party's published estimate. [LayerZero's 20 May report](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report) attributes the forged message to compromised RPC infrastructure and a single-DVN configuration. This is the report author's attribution, not an independent determination of responsibility.

[Kernel's 19 June publication](https://blogs.kerneldao.com/blog/recovering-rseth-from-sunset-networks) describes the end of bridging from 15 June on 20 chains, including Optimism and Monad. Quarterly recovery continues to June 2027, with a 100 USDC fee per address. The author's statement that Ethereum L1 backing remains intact was not independently verified.

Historical `rsETHPrice()` or `paused=false` on L1 does not prove that holders on another chain can withdraw promptly. A common ETH accounting asset still requires a separate redemption analysis for each chain. No recovery transactions, burns or payments are executed in this research.
