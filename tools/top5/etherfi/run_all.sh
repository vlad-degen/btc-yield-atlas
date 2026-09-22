#!/bin/sh
# Order used to produce ../*.csv (raw data cached in ../raw). Network: publicnode/drpc (ETH archive), mainnet.optimism.io, rpc.scroll.io, Blockscout, DefiLlama.
set -e
python3 fetch_logs.py            # vault/accountant logs, vault ERC20 in/out
python3 tokens_seen.py           # token universe
python3 fetch_topic_logs.py      # every non-transfer log with the vault in a topic
python3 month_blocks.py          # month-end blocks (eth/op; scroll added in supply step)
python3 rate_series.py && python3 rate_monthly.py
python3 supply_monthly.py && python3 crosschain_holdings.py
python3 bridges.py && python3 owned_contracts.py && python3 morpho_events.py
python3 positions.py             # month-end vault balances, Morpho, Aave/Spark account data
python3 itb_tokens.py && python3 itb_positions.py   # IntoTheBlock position managers
python3 borrow_rates.py && python3 share_prices.py
python3 rewards.py && python3 reward_values.py && python3 governance.py && python3 lz_dst.py
python3 value_positions2.py      # full balance sheet vs accountant NAV
python3 holders_eth.py && python3 flows_monthly.py
python3 op_share_logs.py && python3 op_holders_rpc2.py
python3 classify_holders.py eth eth_bal_snap.json eth_holders_class.json
python3 classify_holders.py op op_bal_snap.json op_holders_class.json
python3 build_yield.py && python3 build_tables.py && python3 add_stress.py && python3 build_holders.py
python3 economics.py && python3 incentive_share.py
python3 liquidity_checks.py
