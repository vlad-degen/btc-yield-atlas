# ETH market chapter: strategy groups and borrower table

Prepared 4 October 2026 from captured evidence. No financial data was refreshed. The original `market_panel.json`, its quantities and its source hashes remain unchanged. This work supplies data for the user's eight-chapter Bitcoin-style website; it does not edit the website or the existing research reports.

The deliverables are [research_market_chapter.json](../../../data/eth/research_market_chapter.json) and [research_borrowers.json](../../../data/eth/research_borrowers.json).

## The market dataset is compatible with the existing panel

`research_market_chapter.json` is a deep clone of `market_panel.json` with eight strategy-oriented groups. It retains all 85 protocol rows, their exact current/history records, 24 completed months, the original prices, the 64-protocol constant cohort, chain observations, excluded views, source inputs and the unresolved chain-to-aggregate difference. Only category assignments and category aggregates change. Additional product notes, yield observations and detailed product books are separate fields.

Its `current` remains the complete captured 85-row universe. The default selection is in `default_selection` and `default_current`; the existing UI should continue calculating active totals from selected product categories. Default switches include the first six groups and exclude Lending and CDP collateral. This default excludes contextual overlapping layers, not categories that necessarily pay zero. ETH lending can earn material interest.

| Category ID | Website label | Protocol rows | Observed now | Current USD exposure | ETH equivalent |
|---|---|---:|---:|---:|---:|
| staking | Staking / restaking | 19 | 19 | $54.598338B | 20,190,378.327413 |
| loops | ETH borrowing loops | 2 | 2 | $264.936331M | 97,973.033236 |
| carry | USD carry / hybrid parents | 2 | 2 | $1.355712B | 501,340.106744 |
| basis | Spot / short basis | 0 | 0 | Not measured at T | Not measured at T |
| fixed_yield | Fixed yield | 2 | 2 | $23.237645M | 8,593.243960 |
| farming | Liquidity / farming / other vaults | 38 | 34 | $971.614154M | 359,301.366392 |
| lending | Lending markets | 16 | 16 | $18.226437B | 6,740,107.294045 |
| cdp | CDP collateral | 6 | 6 | $2.064211B | 763,342.062714 |

The default subtotal is **21,157,586.077744 ETH equivalent / $57.213838B**, with 59 observed rows out of 63 expected rows. Enabling all categories restores **28,661,035.434503 ETH equivalent / $77.504486B**, with 81 observed rows out of 85. These are signed, overlapping protocol exposure sums. They are not unique ETH, investor equity or a net market capitalization.

“ETH equivalent” retains the canonical convention: adapter USD value divided by Lido's implied ETH price on the same adapter date. It is a value normalization, not proof of underlying ETH quantity. Staking receipts can appear again as restaking collateral, lending collateral or managed-vault assets.

The basis group contains no frozen ledger rows. Its category amount and constant-cohort amount remain null, with zero expected observations and an explicit unmeasured status. It must not be presented as an empty or zero-sized basis market. The separate Ethena disclosure remains in `post_snapshot_observations`: $374.440M of rounded ETH backing legs observed on 3 October, outside T totals.

## Mapping decisions

- Staking issuers and restaking layers join the first group, while `source_role_category` and subtypes preserve the distinction.
- Fluid Lite and Treehouse join ETH borrowing loops because their examined ETH products have E3 mechanisms. Their adapter exposures remain separate from product book NAV and executable exits.
- ether.fi Liquid and Concrete join **USD carry / hybrid parents**. Their reported protocol exposures are not converted into carry equity. Both retain null `allocated_carry_equity_ETH` and `allocated_carry_equity_USD` fields.
- Pendle and Spectra remain fixed-yield venues. Their adapter balances are not outstanding PT principal or complete SY backing.
- DEX, derivatives-liquidity and bridge-liquidity balances stay in liquidity/farming, with distinct subtypes and descriptions.
- Fusion, Yearn, Lagoon, Upshift and other ambiguous managed protocols stay in the `other_managed` subtype. They are not automatically carry because they host a carry vault or issue an ETH-denominated claim.
- CIAN remains other managed at protocol level. The examined rsETH product is E3, but that fact does not establish the whole CIAN protocol allocation.
- CDP and Synthetics rows, including the six captured stablecoin/collateral systems, move out of lending into CDP collateral. Coexisting ETH collateral and dollar debt do not prove reinvestment of the dollars.

This grouping is applied consistently to every historical record. It is a current product-family grouping, not reconstructed historical strategy weights. A category history should therefore be labelled as reported exposure of these product families. Liquid ETH's 64.66% post-T carry disclosure is never applied backward to parent NAV.

## Catalogue fields and additional product books

Every protocol row includes `how_earns`, `yield`, `yield_scope`, `operator`, `operator_scope`, `source_urls`, `official_url`, `classification_scope`, `classification_evidence`, `mechanism_status` and `subtype`. The official URL is retained from the captured protocol registry. An operator name that is only a protocol namespace is labelled accordingly; it is not a verified legal manager or key-holder identification.

`baseline` retains the first completed month's complete observation. `peak.eth_ref` and `peak.usd` give independent completed-month maxima and their dates. `history_coverage` gives observed/missing/stale months, first/last available observation and `no_history`. Four liquidity adapters have no captured history: Balancer V2, SushiSwap, Uniswap V3 and Uniswap V4. This is not evidence that those products are absent from the market.

Where pool discovery provides APYs, `yield_discovery` retains advertised range, full-pool-weighted APY and largest-pool details with the 3 October capture date and explicit post-T status. The weights can include non-ETH sides of pools. These numbers are neither protocol realized returns nor frozen T portfolio yields. A single-pool APY can be shown only with its dated discovery label; multi-pool protocols have no single comparable realized APY.

`detailed_products` contains the 14 carry/adjacent product records from `carry_category_candidates.json`, with native book size, ETH/USD conversion, primary-source URLs, mechanism status and all available histories. Those include Liquid ETH, Concrete Delta and wstETH Plus, Liquity ETH Carry, TAU, Reservoir, Royco, Rocksolid, Fluid Lite, Treehouse, CIAN and the unclassified Midas products. The Ethena candidate remains a separate basis observation.

Detailed product books have `included_in_adapter_totals=false` and explicit parent overlap lists. They must not be added on top of their Fusion, Concrete, ether.fi or other protocol adapter balances. Their USD histories use the candidate dataset's dated Chainlink references; those prices are not substituted into the canonical adapter ledger.

The lifecycle output is deliberately conservative. Convex and Spark Savings have observed zero selected-ETH balances, but no positive-to-zero histories establish an emptied product here. `emptied_products` and `closed_products` are empty. Missing data, absent selected symbols and zero ETH inventory do not prove shutdown or principal recovery. A fabricated “Closed” roster would weaken the research.

## Actual borrower identities and loan units

`research_borrowers.json` includes all **237 positions**, all **25 selected market records**, and **213 borrower identities keyed by chain and address**. There are 207 distinct address strings. It also includes the top 20 identities and exact identified economic groups.

The borrower requests ran from **3 October 2026, 15:00:22.662928 to 15:00:43.135021 UTC**. Market aggregate state came from an earlier independent request. Neither layer is fixed-block T. The sampled positions total **$465.256994M of debt**, versus **$593.751263M** reported by the selected market-state records. The 78.3589% ratio is a diagnostic of the top-ten sample and asynchronous calls, not an exact reconciliation or a market-wide coverage percentage.

Each position preserves raw collateral, raw borrow assets, raw borrow shares, token addresses and decimals. Native units use the exact token precision. Collateral/debt USD values are the original API values. Implied USD-per-token quotes divide each API USD value by that position's native units. They are request-specific marks, not independent oracle prices; stablecoins are not forcibly priced at $1 and no T ETH quote is imposed.

The Who and Evidence columns name only exact identities established in captured contract evidence:

| Chain/address identity | Name | Sampled debt | Identity evidence |
|---|---|---:|---|
| Ethereum `0x7ee29373f075ee1d83b1b93b4fe94ae242df5178` | Concrete shared Safe | $70.395564M | Same Safe linked to examined Concrete strategies; 3-of-5 controls captured at T. Product backing and beneficial ownership remain unresolved. |
| Ethereum `0xf0bb20865277abd641a307ece5ee04e79073416c` | ether.fi Liquid ETH vault | $66.596699M | Known vault identity from the fixed-block pilot; API debt is later. |
| Ethereum `0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3` | Liquid ETH controlled position manager | $34.293233M | `owner()` returns the Liquid ETH vault at T. |

All other 210 chain/address identities are **Unknown owner**. Their evidence describes the observed collateral/debt and the unverified funding destination, outside investors and strategy purpose. ETH collateral with stablecoin debt is a screening hint, not a carry classification. ETH debt is similarly a potential loop hint until the borrowed asset's destination is verified.

The two identified Liquid ETH addresses consolidate to **$100.889932M of sampled debt**. That is not complete product debt or investor capital. Other unidentified addresses could share managers; the dataset does not invent those relationships.

The top five chain/address identities hold **50.596398%** of sampled debt. The earlier presentation analysis reported 51.020269% after combining identical address strings across chains. Both describe the same captured positions with different grouping. This new table uses the chain/address definition consistently; it does not treat identical bytes on different chains as proven common ownership.

## Verification and integration

The derivation checked all **256 category masks**, every completed month and the current snapshot. Selected category sums equal selected protocol rows in both USD and ETH-equivalent units. All original product current/history records, original prices, constant-cohort membership and chain reconciliation fields are unchanged. The canonical market panel's hash was checked before and after derivation.

The borrower extraction preserves native raw quantities and reconciles all chain/address totals to the 237 positions. No unverified wallet receives an owner name. Tables retain source request metadata, source paths and hashes.

The site can now use `research_market_chapter.json` in place of `market_panel.json`, update its eight category descriptions, and build the catalogue from the added fields. The separate detailed carry histories continue to support the carry chapter. The borrower table can use `top_borrowers` or all `borrowers`, with Wallet, Venue, Collateral, Debt, Who and Evidence columns. Show native token units and captured USD marks without labelling them fixed-block T.

The result supplies the requested strategy dashboard and comparable product catalogue while keeping the unmeasured net-capital and strategy-allocation questions explicit.
