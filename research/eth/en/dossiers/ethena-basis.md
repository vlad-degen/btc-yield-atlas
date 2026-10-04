# Ethena's ETH basis strategy

Reviewed 4 October 2026. Financial snapshot: 2 October, 23:59:59 UTC. The venue table is a separately dated 3 October observation. In this strategy, ETH backs a dollar product. The E9 mechanism is analysed separately from products whose investors retain exposure to the price of ETH.

## What investors own and who pays the yield

USDe and sUSDe primarily preserve dollar exposure. Holding spot ETH together with a short derivative reduces the combined sensitivity to ETH/USD price changes, often called delta. The strategy can earn derivative funding payments or the difference between spot and futures prices, known as basis. Staking income is added only when the ETH backing is actually staked. Hedge and custody costs reduce the result.

Current [protocol revenue documentation](https://docs.ethena.fi/backing-assets/protocol-revenue) also includes lending, real-world assets (RWA) and rewards on liquid stablecoins. Total sUSDe return therefore differs from the return on Ethena's ETH basis strategy.

## Current public disclosure

The [backing-assets dashboard](https://app.ethena.fi/dashboards/backing-assets) was labelled updated 3 Oct 26 11:00, without an explicit timezone.

| Venue / custody | Rounded ETH-leg USD | Displayed APY |
|---|---:|---:|
| Binance / Ceffu | $202.12M | 6.0% |
| Bybit / Copper | $81.62M | 4.8% |
| OKX / Copper | $90.70M | 4.4% |

APY means annual percentage yield. The combined ETH rows total $374.44M. No ETH rows appeared for the other disclosed basis venues, Deribit and Coinbase Derivatives Exchanges.

The entire crypto basis allocation was $928.89M, approximately 19.1% of backing. Other categories included approximately $1.7B DeFi lending, $621.43M institutional lending, $1.34B liquid stablecoins and $283.55M RWA. These rounded figures come from the current interface. They are not a custody audit at T.

The global menu showed a different supply from the transparency table. This conflict was recorded, and the figures were excluded from headline totals. Even an exact USDe supply could not be assigned entirely to ETH.

## How the allocation has changed

The [May 2026 risk-committee update](https://gov.ethenafoundation.com/t/ethenas-may-2026-governance-update/796) disclosed $94M ETH basis, $297M BTC basis and approximately 89% liquid cash backing. This is a historical disclosure, not an allocation verified at T. Comparing it with the current interface shows why the source of “Ethena yield” depends on the portfolio allocation at the time.

The [June governance report](https://gov.ethenafoundation.com/t/ethena-s-june-2026-governance-update/808) reproduces a 3 July dashboard observation of about **$39M across all crypto basis**, approximately 1.0% of backing, with a reported -0.1% APY. ETH is not separated. The allocation can change enough that neither this rounded historical figure nor the later venue table can fill the missing T observation.

## What the last reserve disclosure before T establishes

The [weekly reserve feed](https://data.ht.digital/por/ethena) reports **$4,905.76M of backing**, **$4,903.84M of token supply** and **$4,967.84M including the reserve fund** at 00:08 UTC on 2 October. This precedes T by almost 24 hours. It covers the whole dollar portfolio and does not disclose ETH notional. The publisher distinguishes weekly automated output from its separately scoped assurance engagements.

The public sources therefore establish dated reserve context and changes in allocation. They do not support an exact-T ETH basis amount. That amount stays unavailable in the market chart. Resolving it requires dated ETH spot and hedge positions, custody ownership, margin balances and valuations, with ETH separated from the other strategies. The captured sources and typed observations are in [basis_closure_disclosures.json](../../../../data/eth/basis_closure_disclosures.json).

## Funding, custody and exit risk

A short derivative can require funding payments rather than receive them. It can also require additional margin as ETH rises and depend on settlement between the custodian and trading venue. The [funding risk documentation](https://docs.ethena.fi/protocol-overview/risks/funding-risk) describes dynamic allocation and reserves. Historical average rates in documentation are not current expected returns.

Custodial omnibus balances combine assets from multiple clients. They are not necessarily identical to Ethena-owned assets, as the [official dashboard explanation](https://docs.ethena.fi/backing-custody-and-security/real-time-dashboards) warns. Independent reconstruction requires dated attestations, derivative positions, margin and valuation deductions, and the legal claims attached to those assets. Token transfers into deposit wallets do not supply all of this evidence.

Executable institutional redemption and the allocation of trading or custody costs to investors have not been reconstructed. The displayed conversion or yield alone does not establish the outcome of an exit.

## What is verified and what remains open

Current ETH-only disclosure and the yield mechanism are documented. ETH notional at T, complete funding history over matching periods, realized trading and custody costs, investor allocation to this strategy, and executable institutional redemption remain open. Current sUSDe interface APY is not used as realized ETH return.

Data: `ethena_ETH_basis_observation.json`; raw `ethena_ui_observation.json`, `ethena_revenue`, `ethena_basis`, `ethena_funding_risks`, `ethena_may2026`, `ethena_dashboard_doc`.
