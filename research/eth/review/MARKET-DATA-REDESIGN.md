# ETH market panel: data design, findings and limits

The panel is ready for a market-first website. It contains 24 closed monthly observations, from October 2024 to September 2026, and a separate snapshot for 2 October 2026 at 23:59:59 UTC. It shows the ETH-related balances visible in captured protocol adapters, grouped by protocol role. It does not establish the size of a unique, fully reconciled ETH yield market.

The financial snapshot remains `1790985599`. The raw public API responses were captured on 3 October 2026. This work uses those saved responses and makes no new financial requests.

## Files and rebuild

- `data/eth/market_panel.json` is the isolated canonical panel dataset.
- `tools/eth/market_data_probe.py` rebuilds it offline.
- `data/eth/market_panel_monthly.csv` contains 150 category observations: six categories at 24 closed months and one snapshot.
- `data/eth/market_panel_protocols.csv` contains 85 protocol adapter rows.
- `data/eth/market_panel_chains.csv` contains 62 named-chain observations.
- `data/eth/market_panel_prices.csv` contains the 31 adapter-date ETH reference quotes used in the panel.
- `data/eth/market_pool_screen.json` and `.csv` provide a separate discovery screen for four missing liquidity adapters. Rebuild them with `tools/eth/market_pool_screen.py`.

The existing normalizer, original observations and canonical English research documents have not been changed. These artifacts give the site a consistent series without silently changing the earlier research's accounting.

## What the balance fields mean

`usd` is the signed sum of selected ETH-family token balances reported by an adapter. `gross_positive_usd` sums its positive selected balances. `negative_usd` sums its negative selected balances and therefore retains a negative sign. Their identity is:

`usd = gross_positive_usd + negative_usd`

At the snapshot, gross positive balances are **$77,544,140,706.6601** and reported negative balances are **-$39,654,780.37038**, giving signed balances of **$77,504,485,926.28972**. The negative balances come from the two ETH debt-token entries in the Treehouse adapter. Other protocols can have debt that is not represented as a negative ETH token in the selected fields. Dollar debt, off-chain hedges and liabilities outside this token screen are not deducted. The signed number is consequently not whole-product NAV or global net ETH capital.

The same underlying economic position can appear as staking issuer backing, restaking collateral, lending collateral and a managed vault position. Receipt tokens and bridge claims can add further layers. Summing the layers produces overlapping exposure. Neither the sum nor each category is a denominator for unique market share.

**Price normalization:** Each adapter USD balance is divided by Lido's same-date implied ETH price; this is a value equivalent, not a count of physically backed ETH.

The resulting `eth_ref` is useful for separating the common ETH/USD reference price from the reported USD balance. It does not convert every receipt into native ETH at an independently verified redemption rate. An ETH receipt's market discount, adapter valuation method, debt sign and claim hierarchy still affect this measure. The physical backing and executable redemption value of each claim have not been reconciled.

## Schema for the website

| Field | Meaning |
|---|---|
| `categories` | Six objects with `id`, `label`, `color`, `default` and `scope` |
| `months` | The 24 closed months, with period, target timestamp, signed USD and ETH reference values, positive and negative balances, coverage and `by_category` |
| `current` | The separate T snapshot with the same measurements |
| `chart_points` | The closed months followed by the explicitly labelled snapshot; 25 observations |
| `products` | 85 protocol adapters, each with current measurements, 24 monthly observations, a source URL and current discovery category |
| `chains` | Current named-chain balances with the same measurement fields, category breakdown, observation count and source dates |
| `chain_observations` | Protocol-level chain rows behind those aggregates |
| `prices` | Date, implied ETH quote, raw-response hash and cross-adapter dispersion checks |
| `comparisons` | Current versus first, current versus last, and first versus last, restricted to protocols observed at both endpoints |
| `constant_cohort_protocols` | 64 adapters with an eligible observation in every closed month |
| `inputs` and `chain_inputs` | Paths and SHA-256 hashes for the derived and raw sources |

Each product observation preserves `status`, source timestamp, source age, selected values and excluded token values. `status` is `observed`, `missing` or `stale`. A missing value is `null`. An eligible empty selected-token observation can be zero, and is identified by `observed_zero`. The dataset does not replace missing balances with zero.

Each category has coverage counts, missing and stale protocol names, source-date distribution, and `constant_cohort` values. Coverage describes this selected adapter universe. It does not measure coverage of all ETH products or all positions inside a protocol.

`products[].row_kind` is `protocol_adapter`. A protocol can offer many products, and multiple protocols can refer to the same underlying position. The site should call these rows protocols or adapters, not a count of distinct investment products.

`global_unique_ETH`, `global_net_market_NAV` and `market_share_denominator` are deliberately `null`.

## Category definitions

| ID | Label | Eligible adapters | Boundary |
|---|---|---:|---|
| `staking` | Staking issuers | 12 | ETH-related balances reported by issuers; can include receipts issued elsewhere |
| `restaking` | Restaking layers | 7 | Restaking and liquid-restaking collateral claims, overlapping the staking layer |
| `lending` | Lending and collateral | 22 | Loan assets and collateral selected by token; collateral need not earn lender interest |
| `liquidity` | Liquidity and trading pools | 23 | ETH token balances in trading, DEX and bridge-liquidity adapters, not every active LP position |
| `fixed_yield` | Fixed-yield pools | 2 | Pendle and Spectra token balances visible to the adapters, not all outstanding principal and redemption claims |
| `managed` | Managed and yield vaults | 19 | Selected assets and reported ETH debts in managed/yield protocols, not complete product NAV |

This is a consistent protocol-role grouping, derived from the current discovery category and applied to the entire historical window. It is not a reconstruction of each protocol's strategy mix at each historical date. ETH carry trades inside a managed vault do not become a separate, independently additive market category. Yield-source and strategy allocation data belong in the mechanism and product dossiers.

The underlying discovery universe has 87 protocols. Ethena USDe is excluded because dollar basis exposure needs a separate accounting scope. Midas RWA is excluded because the capture does not establish a verified ETH product identity or ETH token history. An empty ETH token field is not proof that either protocol has no ETH-related strategy.

## Category endpoints

USD values below are millions. ETH reference values are units of ETH valued at the relevant adapter-date quote. Values are rounded here; JSON and CSV retain the underlying precision.

| Observed category | October 2024 USD m | September 2026 USD m | T snapshot USD m | October 2024 ETH ref | September 2026 ETH ref | T snapshot ETH ref |
|---|---:|---:|---:|---:|---:|---:|
| Staking issuers | 41,217.806 | 45,483.236 | 46,017.647 | 15,444,958.330 | 17,024,637.200 | 17,017,252.383 |
| Restaking layers | 15,108.156 | 8,481.464 | 8,580.691 | 5,661,262.874 | 3,174,660.907 | 3,173,125.944 |
| Lending and collateral | 16,415.483 | 20,169.671 | 20,290.648 | 6,151,138.844 | 7,549,624.206 | 7,503,449.357 |
| Liquidity and trading pools | 1,098.355 | 665.958 | 666.977 | 411,570.905 | 249,271.813 | 246,647.138 |
| Fixed-yield pools | 705.050 | 22.988 | 23.238 | 264,193.342 | 8,604.572 | 8,593.244 |
| Managed and yield vaults | 1,422.961 | 1,904.478 | 1,925.285 | 533,205.704 | 712,856.992 | 711,967.368 |

The snapshot's managed category has positive selected assets of **$1,964,939,893.5041**, reported negative ETH balances of **-$39,654,780.37038**, and signed selected balances of **$1,925,285,113.13372**.

| Category | Observed at first / last / current | USD change, first to current | ETH ref change, first to current | Always-observed cohort count | Cohort USD change, first to current | Cohort ETH ref change, first to current |
|---|---|---:|---:|---:|---:|---:|
| Staking | 12 / 12 / 12 | +11.6451% | +10.1800% | 12 | +11.6451% | +10.1800% |
| Restaking | 7 / 7 / 7 | -43.2049% | -43.9502% | 7 | -43.2049% | -43.9502% |
| Lending | 17 / 22 / 22 | +23.6068% | +21.9847% | 17 | +21.1369% | +19.5473% |
| Liquidity | 15 / 19 / 19 | -39.2749% | -40.0718% | 13 | -52.4167% | -53.0411% |
| Fixed yield | 2 / 2 / 2 | -96.7041% | -96.7474% | 2 | -96.7041% | -96.7474% |
| Managed | 14 / 19 / 19 | +35.3014% | +33.5258% | 13 | -39.4164% | -40.2114% |

These are changes in observed signed balances. They are not net deposits, investment returns, changes in total economic backing or a measurement of capital moving between categories.

The fixed-yield decline requires particular care. Maturing pools, redeemed positions, unobserved wrapper tokens and outstanding claims can disappear from the selected token view. The separate captured Pendle discovery includes a large expired-market population. This table does not establish a 96.7% collapse of the entire fixed-yield market or explain the decline's causes.

## What the common cohorts reveal

The all-observed signed series rises from **$75,967,810,204.9291** in October 2024 to **$77,504,485,926.28972** at T, an increase of **2.0228%**. Its ETH reference increase is **0.6840%**. Observation availability also expands from 67 to 81 protocols. Comparing those changing populations as though they were the same set would hide the coverage effect.

The 64 adapters observed in every closed month have **$75,938,913,030.54683** at the start, **$75,125,463,095.58415** at the last closed month, and **$75,877,202,409.47238** at T. Their first-to-current change is **-0.0813% in USD** and **-1.3925% in ETH reference value**. Their first-to-last-closed-month change is **-1.0712% in USD** and **-1.1794% in ETH reference value**.

The managed category is the clearest example: the changing observed subset increases 35.3014% in USD, while the 13 adapters eligible throughout the closed-month window decline 39.4164%. That difference is a measurement of different included populations. It is not evidence that the omitted early balances were zero, that newly observed protocols were newly launched, or that one specific strategy caused the change.

Endpoint-only comparisons preserve more coverage than requiring every intermediate month:

| Common endpoint set | Protocols | USD change | ETH ref change |
|---|---:|---:|---:|
| First closed month to current | 67 | -0.0721% | -1.3834% |
| First to last closed month | 67 | -1.0616% | -1.1698% |
| Last closed month to current | 81 | +1.0123% | -0.2041% |

The last comparison also shows why both units should be available: reported USD exposure increases from September to T while ETH reference exposure declines. This does not, by itself, identify deposits, withdrawals, strategy P&L or an exact price contribution. Adapter composition and valuations can also change.

The always-observed cohort controls observation availability. It does not remove survivorship bias. The universe was selected from captured current discovery plus historical seeds; closed or missing products can still be absent.

## Observation coverage and dates

The 85-protocol core has 2,040 monthly protocol observations: **1,813 observed**, **223 missing** and **four stale** under the panel's freshness rule. Monthly eligible counts range from 67 to 81. This differs from the original 2,088 rows because this panel excludes two protocols and does not promote stale observations into the main series.

At T, 81 of the 85 eligible adapters are observed and four are missing. All 81 eligible current adapter observations are dated **2 October 2026 at 00:00:00 UTC**, so they are **86,399 seconds** behind T. The snapshot is a partial October observation, not an October month-end close. Two observed rows, Convex Finance and Spark Savings, have zero selected ETH token balances; this is not proof of zero ETH exposure across their products.

Primary sums include observations no more than **72 hours** old. Older observations retain their original values, dates and `stale` status in product rows, and appear in `including_stale_usd` and `including_stale_eth_ref`. They are excluded from the main chart totals and from the constant cohort.

| Adapter and period | Preserved stale USD | Age behind target |
|---|---:|---:|
| Sushi V3, May 2025 | 4,496,980.38433 | 950,399 seconds |
| Sushi V3, June 2025 | 4,496,980.38433 | 3,542,399 seconds |
| Camelot V2, February 2026 | 5,115,175.00063 | 777,599 seconds |
| Origin ARM, June 2026 | 4,385,007.07201 | 1,123,199 seconds |

Missing rows preserve missingness even when an adapter has whole-protocol TVL elsewhere. An observation's absence can reflect an unavailable token series, launch timing, deprecation or adapter coverage. The panel does not choose among those explanations without evidence.

## Liquidity: more than four missing rows

The category must be labelled **observed ETH token balances in liquidity and trading protocols**. Its current **$666,977,287.42145** covers 19 of 23 selected adapters. Uniswap V3, Uniswap V4, Balancer V2 and Sushi have no eligible aggregate ETH token observations, and their captured protocol chain views do not supply the missing ETH token amounts either.

Those four missing adapters are identifiable gaps, not the full size of the gap. Even an observed adapter can omit concentrated-liquidity NFT holdings, wrapper or LP tokens that do not have recognized ETH symbols, assets in a pool's custody contracts, or unobserved chains. The universe itself is a screen, not an exhaustive protocol registry. Some included ETH balances belong to bridge liquidity or trading collateral and are not demonstrated to be active fee-earning LP capital. Fixed-yield and managed receipt layers can also hold LP claims. There is no supported numeric estimate of all omitted liquidity.

The captured yield feed supplies pool symbols, underlying token addresses, full-pool USD TVL and headline APYs. It does **not** supply token reserves or quantities, concentrated-liquidity ranges and positions, or pool weights. It therefore cannot establish the ETH side of a mixed pool. A 50% split would be an unsupported assumption, especially for concentrated or weighted pools.

The separate latest discovery screen can still help readers find the missing venues:

| Captured protocol | ETH-related symbol pools | Full-pool USD TVL | All components are ETH-family symbols | Full-pool USD TVL in that symbol subset |
|---|---:|---:|---:|---:|
| Uniswap V3 | 1,030 | 1,012,621,186 | 26 | 33,181,997 |
| Uniswap V4 | 972 | 460,107,201 | 27 | 5,364,673 |
| Balancer V2 | 65 | 16,939,922 | 1 | 23,080 |
| Sushi | 174 | 34,388,460 | 1 | 68,999 |
| Screen total | 2,241 | 1,524,056,769 | 55 | 38,638,749 |

The feed was captured at **2026-10-03T13:40:39.080809+00:00**, after T. Its response date is 3 October 2026 at 13:40:39 GMT, and its SHA-256 is `65cd13598ec237eefc25461937e26df5fda1b1791cf1f7bbea8eeccb59caceda`. It is a latest captured discovery screen, not a verified T balance.

The all-ETH-family subset has 38 pools on Ethereum, eight on Base, four on Arbitrum, three on Optimism, one on Gnosis and one on Polygon. Its **$38,638,749** is still a full-pool, symbol-based candidate value. Address identity, issuer conversion, claim hierarchy and backing are not verified uniformly across these chains. It can guide pool-level follow-up, but is not a verified ETH principal total. The mixed-pool ETH-side fields remain `null`.

These pool rows must remain separate from the historical chart, aggregate exposures and chain totals. Their APYs are discovery fields, not measured investor returns, and full-pool TVL is not evidence that all of the value earns the stated return.

## ETH reference quote and heterogeneous valuations

The captured Lido response contains 2,114 daily observations with WETH token units and WETH USD value. The probe derives a quote by dividing USD by units on each adapter's own source date. All 31 unique dates used by eligible or preserved stale observations have a quote. The raw source is `raw/eth/2026-10-02/protocol_lido-2f33d38b9f47e245.json`, SHA-256 `2f33d38b9f47e245b0b2acbb6f81e9764d3d6f198f896f56ccdb2aa74398fe9f`.

| Adapter source date, 00:00 UTC | Lido implied ETH/USD | Native ETH/WETH comparisons of at least $10,000 | Minimum relative deviation | Median relative deviation | Maximum relative deviation |
|---|---:|---:|---:|---:|---:|
| 31 October 2024 | 2,668.690000 | 64 | -5.827578% | -0.002784% | +0.007494% |
| 30 September 2026 | 2,671.612637 | 79 | -0.151247% | approximately 0% | +2.141064% |
| 2 October 2026 | 2,704.176062 | 79 | -0.289378% | -0.000001% | +0.344940% |

These are cross-adapter unit-price comparisons, not independent exchange quotes. Their daily timestamps do not establish atomic observations at one common block or price. Intraday capture conventions, oracle choices and representation of token units can differ. The JSON preserves outliers above 1% for follow-up. It does not silently replace their USD valuations or claim to identify the cause of each deviation.

The nearest captured ETH price quote is **$2,667.9504418816** at timestamp **1790985600**, which is T plus one second. It is retained separately and is not used to reprice the monthly adapter USD balances. Applying that current quote to the whole historical USD series would introduce an avoidable ETH-price distortion.

The original monthly observations also retain reported token units for many adapters. Those units cannot be summed across receipts as native ETH. Captured Ethereum archive histories contain 33 endpoints for wstETH and weETH conversion, and the separate verified rsETH oracle history has 33 endpoints. Selected endpoint histories are not complete conversion histories for every token, adapter date and bridge chain. Receipt redemption book value and executable ETH value need separate treatment, especially after bridge or recovery events.

## Token selection correction

The original selector admitted symbols beginning with `AETH` when their names contained `ETH`. The network prefix appears in stablecoin and BTC receipt symbols as well as ETH receipts. This probe uses an explicit family whitelist and four explicit ETH receipt/debt symbols: `AETHWSTETH`, `AETHLIDOWSTETH`, `VARIABLEDEBTETHWETH` and `VARIABLEDEBTWETH`.

It excludes `AETHUSDC`, `AETHRLUSD`, `AETHPYUSD`, `AETHUSDT`, `AETHUSDG` and `AETHWBTC`. At the current snapshot those excluded legacy selector entries total **$8,269,003.42214**, including **$8,267,080.39237 of AETHUSDC**. Their presence in the original selected fields was not evidence of ETH principal. The new dataset preserves them in `excluded_tokens_usd`, preserves `legacy_selector_usd`, and leaves the old raw and normalized research files untouched.

Exact symbols reduce one known classification error but do not independently authenticate every token address. Different assets can share a symbol; bridged and internal accounting units can use familiar labels. Ten current adapters carry the source's `misrepresentedTokens` flag. The panel preserves that flag and makes no physical reserve or redemption guarantee.

## Chain view and reconciliation

Chain rows use the same selected symbols, same-date reference price and freshness threshold as the aggregate series. They include only named chains found in the captured chain registry. Auxiliary `borrowed`, `staking`, `pool2` and other API views are not added as though they were new chains. This avoids adding borrowed assets a second time to supplied assets.

Chain aliases are explicit in `chain_name_aliases`, including OP Mainnet to Optimism, Binance/BSC to BNB Chain, xDai to Gnosis and Hyperliquid L1 to HyperEVM. The ambiguous Beefy `Oasis` view is not mapped to either Emerald or Sapphire without evidence.

| Largest observed chain | Signed selected USD | ETH reference units |
|---|---:|---:|
| Ethereum | 73,894,789,939.15396 | 27,326,175.608538 |
| Tron | 1,309,833,259.46700 | 484,374.252847 |
| Base | 825,385,422.50714 | 305,226.214443 |
| BNB Chain | 645,195,070.29763 | 238,592.109230 |
| Arbitrum | 390,961,229.04357 | 144,576.839717 |
| Monad | 132,264,355.97829 | 48,911.148150 |
| Optimism | 56,831,397.16444 | 21,016.160142 |
| Polygon | 47,724,255.32863 | 17,648.353598 |
| Gnosis | 40,932,897.03553 | 15,136.920120 |
| Linea | 28,739,668.60388 | 10,627.883669 |

The 62 chain rows exceed the aggregate protocol series by **$2,580,052.319244**. Morpho Blue's chain views exceed its aggregate by **$2,580,355.547980**. The excluded ambiguous Beefy Oasis view leaves about **$303.22864** outside the named-chain sum; small residual differences are rounding. The source captures do not resolve the Morpho discrepancy. `chain_reconciliation_complete` remains `false`, and no residual is assigned to an invented chain or silently forced into balance.

The rows describe the observed location of reported token balances. They are not complete economic backing by chain, and do not prove the backing quality or ETH redemption route of a bridged claim. Chain percentages, if shown, must use the observed chain sum and explicitly say that the view is incomplete and does not fully reconcile to the aggregate.

## Suggested site copy and behavior

Use the title **Observed ETH exposures by protocol role**. A short description can read: **Reported ETH-related token balances across protocol layers. The same underlying ETH can appear in several layers. Coverage and missing observations are shown for every date.**

Label the headline amount **Signed reported exposure**. Place positive assets and negative reported balances beside it, and make the overlapping scope clear. Do not title the number total ETH market, unique yield capital or net deposits.

Use **USD** and **ETH at the adapter-date price** for the unit switch. Keep the one-sentence normalization explanation visible. The ETH reference view is a valuation normalization, while the product return charts elsewhere use historical issuer/share conversions with a different accounting purpose.

Keep **2 Oct 2026 snapshot** distinct from **Sep 2026 close**. Show date-specific coverage beside the chart and retain missing/stale states in protocol details. Offer the always-observed cohort as a separate comparison and show matched-endpoint change counts with the comparisons.

For liquidity, display **Observed subset: 19 of 23 selected adapters; token and position coverage is incomplete.** Link to the separate latest discovery screen for the four missing adapters. Label its amounts **Full-pool USD TVL**, preserve unknown ETH-side amounts, and show its 3 October capture date.

## Validation performed

The builder checks 24 closed months, 85 core adapters and complete reference-quote availability for every preserved source date. It verifies signed balance identities across current and historical product observations and verifies the six-category sums for every panel date.

The independent final review passed **16,800 checks**. It recomputed all **1,898 preserved current and historical observations** directly from raw protocol responses, and independently recomputed **341 protocol-chain observations** and the 62 named-chain aggregates. It also checked raw-response hashes, CSV row counts, category coverage totals, common endpoint sets, the always-observed cohort, price reconstruction and separation of pool discovery from canonical history. Missing rows were checked against the absence of eligible raw token observations. A fresh offline rebuild produced a byte-for-byte identical canonical file, SHA-256 `384461b5d6e6fb0e3fa4d42cc2d8ebc851923f71ada54b54341f1acd80f01808`.

The panel is suitable for presenting observed market structure and its documented gaps. Completing a unique market estimate would require per-asset addresses, dated issuer conversions, pool token quantities, loan/debt reconciliation, bridge and backing relations, and a claim graph that removes duplication across layers. These are further research inputs, not quantities inferred by this dataset.
