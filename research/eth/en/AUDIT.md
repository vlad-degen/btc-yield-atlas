# How the evidence was checked

Published 3 October 2026. The checks below verify dates, source files, units and arithmetic. Assessing product solvency, investor rights and successful withdrawal requires additional evidence.

## The fixed snapshot

T = **1790985599**, 2 October 2026, 23:59:59 UTC.

| Chain | Chain ID | Last block ≤ T | Next block timestamp |
|---|---:|---:|---:|
| Ethereum | 1 | 26 108 081 | T+12 s |
| Optimism | 10 | 157 693 411 | T+2 s |
| Base | 8453 | 52 098 126 | T+2 s |
| Arbitrum | 42161 | 511 139 919 | T+1 s |
| Monad: nested sleeve check | 143 | 110 031 481 | T+1 s |

Block headers and hashes are retained in `snapshot_manifest.json` and `mono_remote_T.json`. The 66 Ethereum and Optimism historical benchmark reads were checked against their target timestamps. They cover 24 month ends, the starting point and additional dates needed for return comparisons. Balances are never filled from a later block.

The nearest ETH quote is $2,667.9504418816, timestamped one second after T, with source confidence 0.99. It is a reference for conversion; no trade at that price is assumed. Protocol API observations are usually 86,399 seconds old at T because their data represents the start of the day.

## Source layers

1. **Contract calls at a fixed block:** share supply, `convertToAssets`, collateral, debt, ownership, cash, rates, NFT positions and proxy implementation. These establish the reported contract state. Oracle and book values can still differ from the proceeds of a sale or withdrawal.
2. **Verified source code and official documentation:** interfaces, accounting rules, burn/mint bridges, withdrawal queues, fees and risks. A contract's current code only establishes historical behavior if its implementation and settings were also checked at T.
3. **Dated aggregator APIs:** balances and history for 87 selected protocol sources. The analysis preserves observation age, negative balances and the source's `misrepresentedTokens` warning.
4. **Current discovery/public UI:** pools, Pendle, Morpho top borrowers, Ether.fi allocations, Ethena backing and JustLend APIs. Captured after T and separately labelled.
5. **Calculations and scenarios:** receipt conversion, overlapping lending and borrowing, break-even rates and stress. Derived JSON files record the units and assumptions.

A successful HTTP response can still contain no usable evidence. One guessed Monad GitBook URL returned “Page Not Found”; an empty HTTP 202 response supplied no data. A batch of contract calls can also contain individual errors. The dataset retains these responses, and an error never becomes a zero balance.

## Actual coverage

Current feed: 16,992 pools → 5,688 ETH-family candidates, 197 projects, 57 chains; 259 full-pool TVLs ≥$5M. Another 206 symbol-only candidates remain separate. Of 87 selected protocols, 82 have aggregate token history. The 2,088 protocol-month rows include 247 missing observations.

Balancer V2, Midas RWA, SushiSwap, Uniswap V3 and V4 lack aggregate token history. This particularly affects LP: absence does not mean zero ETH principal. Current mixed-pool listings cannot fill historical ETH-side inventory.

Some adapters flag misrepresentedTokens, including ether.fi Liquid/Stake, Gearbox and some DEX/aggregators. Treat these as reported accounting rather than physical reserves. Current category is a hint, not historical mechanism proof.

The vault registry is a selected sample. It also includes BTC and dollar products to test that the ETH filter excludes unrelated assets. The 12 dossiers vary in depth: some reconstruct contract positions, while others document a mechanism or public terms. Their underlying backing has not all been independently reconciled.

Morpho coverage consists of 25 selected markets and up to ten large positions per market: 237 positions belonging to 213 unique `(chain, address)` borrowers. The same address string on two chains counts as two chain-specific identities; there are 207 distinct address strings. This is a sample, not a complete borrower census. Pendle's listing was fully paginated across four chains: 626 unique markets, including 126 with ETH accounting units and 122 that were expired. Complete pagination verifies that API listing, not the entire fixed-yield market.

## Integrity and numerical checks

`tools/eth/audit.py` checks:

- Raw-response SHA256 and file existence, including a separate UI-observation manifest.
- All 384 original BTC files against the baseline inventory.
- Block boundaries and absence of future benchmark/history observations.
- Liquid ETH supply×rate NAV, partial balance rows and explicit residual.
- Uniswap token ordering/principal and Fluid gross/debt/net leverage.
- Historical Treehouse denomination and rsETH oracle identity.
- Matched 730-day windows across six series; missing intermediate points are not zero.
- Unique protocol-month rows and preserved missing observations.
- Carry supply-share fractions and kBTC/syrupUSDC identity distinction.
- Monad internal supply, Concrete ownership, Pendle expiry and listing coverage.
- Null market net totals, gross-screen reconciliation and local links.
- Five-market fixed-block totals, reserve-deficit getters and evidence-input hashes.

Results are in `data/eth/audit_results.json`; the raw-file manifest is `data/eth/raw_manifest.json`. The [evidence ledger](EVIDENCE.md) links individual conclusions to their inputs. These checks do not establish every asset's origin, custody rights, reward beneficiary, private valuation or withdrawal outcome.

## Reproduction without refreshing sources

The derived results rebuild from **captured raw data**. Git excludes the raw-data folder, so a reproducible handoff must include it separately. The manifest checks that the copied files match their recorded hashes. Replacing a captured response with a live API response creates a new dated dataset.

From the project root:

```sh
python3 tools/eth/rebuild.py
```

Rebuild runs deterministic local derivations without API/RPC requests or edits to original BTC outputs. Figures use bundled Python with ReportLab/Pillow; override with ETH_FIGURE_PYTHON. The audit runs after figures/site generation. English reports preserve the same numerical tables and evidence boundaries.

## New source collection

For a **new dated edition**, choose a new T and a separate raw-data folder, verify block boundaries and update the source records. `collect.py` currently uses this edition's T. Rerunning live requests without changing the collection setup can mix observations from different dates.

Collection is read-only. Public GET/POST and eth_call do not transact. Entry points include collect.py bootstrap/protocols/consensus/pilot/balances/ratelogs, benchmark.py, op_history_rates.py, vaults.py, vault_history.py, rseth_benchmark.py, carry_lookthrough.py, mono_lookthrough.py and lending_liquidity.py. The URL/payload/time/hash log is raw/eth/2026-10-02/requests.jsonl. Manual UI observations are explicitly labelled.

## Conclusions this edition cannot establish

The dataset cannot yet establish a global total for unique underlying ETH or external investor equity. That requires a complete record of native staking, issuer backing, bridges, debt, internal shares and custody. The $70.939B screening sum is neither a net total nor a verified upper or lower bound.

Liquid ETH's $12.453M residual is not called a deficit. Explained 97.37% book value does not establish independently audited backing. Monad assets, reward ownership, fee growth and accrued Morpho interest remain open.

History drawn from today's protocol list can miss closed products. Share-price returns exclude some distributions and trading or withdrawal costs. Stress scenarios hold positions and rates fixed; full trading, withdrawal and funding simulations remain open. Each conclusion states its evidence boundary so later work can extend the dataset without silently changing what the current edition proves.
