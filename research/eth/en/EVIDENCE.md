# Evidence behind the findings

Evidence supports a specific conclusion. A contract balance can be verified even when its underlying backing or eventual payout is unknown. `data/eth/evidence_ledger.json` preserves hashes for the derived inputs and raw responses. Observations from product interfaces are labelled separately.

| ID | Finding | Date and what the evidence establishes | Main data file |
|---|---|---|---|
| C01 | 5,688 ETH-family pools / 57 chains / 197 projects | Current screen, not net total | [discovery_summary.json](../../../data/eth/discovery_summary.json) |
| C02 | 82 sources with token history; 24 months and 247 missing rows | Dated API | [protocol_source_coverage.json](../../../data/eth/protocol_source_coverage.json) |
| C03 | Liquid ETH book NAV 177,171.063302 ETH | T, book value | [etherfi_verified_metrics.json](../../../data/eth/etherfi_verified_metrics.json) |
| C04 | Partial balance $460.231M; residual $12.453M | T, marks + nested book claims; backing not audited | [etherfi_partial_balance_sheet.json](../../../data/eth/etherfi_partial_balance_sheet.json) |
| C05 | Aave loop 13.325×; HF 1.02708 | T oracle-valued account | [etherfi_verified_metrics.json](../../../data/eth/etherfi_verified_metrics.json) |
| C06 | Carry 64.66%; loops 21.65% in disclosed breakdown | 3 October UI, not fixed-block allocation | [etherfi_verified_metrics.json](../../../data/eth/etherfi_verified_metrics.json) |
| C07 | Liquid ETH +6.8501% / stETH +5.4875%, 730 days | Published PPS/conversion; external rewards/costs excluded | [etherfi_staking_comparison.json](../../../data/eth/etherfi_staking_comparison.json) |
| C08 | senRLUSD: kBTC 52.89%, weETH 24.09% book allocation | T, expected assets and raw supply shares | [carry_credit_lookthrough.json](../../../data/eth/carry_credit_lookthrough.json) |
| C09 | PRIME/PYUSD approximately 95.04% of carry-vault assets | T; credit economics from separate disclosure | [carry_credit_lookthrough.json](../../../data/eth/carry_credit_lookthrough.json) |
| C10 | Self-credit 8.709M RLUSD / 4.759M PYUSD | Overlap, not extra assets or measured income | [carry_credit_lookthrough.json](../../../data/eth/carry_credit_lookthrough.json) |
| C11 | Concrete vaults share one 3-of-5 Safe | T; exclusive backing allocation unknown | [concrete_lookthrough_T.json](../../../data/eth/concrete_lookthrough_T.json) |
| C12 | Delta sole holder; ctwst supply owned by Safe | T; genesis mint does not prove absent backing | [concrete_self_holdings_T.json](../../../data/eth/concrete_self_holdings_T.json) |
| C13 | Fluid Lite L=7.759×; 730-day ETH book return +8.8243% | T contract valuation; parity assumptions | [fluid_lite_balance_T.json](../../../data/eth/fluid_lite_balance_T.json) |
| C14 | Treehouse IAU historically wstETH-denominated; ETH +6.2761% | 730 days; independent backing unreconstructed | [treehouse_denomination_history.json](../../../data/eth/treehouse_denomination_history.json) |
| C15 | CIAN rsETH ETH book return +1.0854%, 730 days | Issuer oracle; rewards/recovery costs excluded | [rseth_benchmark_rpc.json](../../../data/eth/rseth_benchmark_rpc.json) |
| C16 | JustLend mapped ETH approximately 484K units; annual supply rate 0.0002899% | Current 3 October; Ethereum backing unverified | [justlend_eth_semantics.json](../../../data/eth/justlend_eth_semantics.json) |
| C17 | Ethena ETH basis approximately $374.44M | 3 October rounded UI, no custody audit | [ethena_ETH_basis_observation.json](../../../data/eth/ethena_ETH_basis_observation.json) |
| C18 | Pendle 626 listed / 126 ETH-family / 122 expired | four-chain current API; expiry evaluated against T | [pendle_source_coverage.json](../../../data/eth/pendle_source_coverage.json) |
| C19 | Monad claim approximately $21.687M; ETH/Monad rates differ | T; remote backing open | [mono_identity_T.json](../../../data/eth/mono_identity_T.json) |
| C20 | Main Aave debt 410,134 WETH; reserve cash 269,693 | T; cash does not guarantee flash-loan eligibility | [lending_reserve_T.json](../../../data/eth/lending_reserve_T.json) |
| C21 | Aave loop model: +44.3 bp in debt cost erases return | mixed trailing-30d staking proxy / T APR; no forecast | [loop_economics_T.json](../../../data/eth/loop_economics_T.json) |
| C22 | Global underlying and external-equity totals remain unmeasured | Overlap/consensus/custody/identity gaps | [market_summary.json](../../../data/eth/market_summary.json) |
| C23 | Five WETH markets: 2.881M claims / 2.388M debt | T; gross claims, not unique backing | [weth_lending_markets_T.json](../../../data/eth/weth_lending_markets_T.json) |
| C24 | WETH deficits: Ethereum 52,964 / Arbitrum 29,835 | T getter; no established final haircut | [weth_lending_markets_T.json](../../../data/eth/weth_lending_markets_T.json) |
| C25 | Liquid ETH main account: 23.28% variable WETH debt Aave ETH | T; selected borrower concentration | [weth_lending_summary_T.json](../../../data/eth/weth_lending_summary_T.json) |

## Primary links and reproducibility

An aggregator balance is not independent proof of reserves. Contract-call records retain the block, address, requested function and response. Verified interfaces, source code and identity getters are linked to the relevant contracts. [How the evidence was checked](AUDIT.md) explains the source layers.

A share price, debt balance, cash balance, oracle value and actual payout each establish a different fact. C22 leaves global totals unmeasured because the backing and ownership map is incomplete. Conflicting observations keep their dates and require an explanation; source errors never become zero balances.
