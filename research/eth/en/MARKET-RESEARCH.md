# The ETH yield market: research edition

The integrated market ledger, corrected ETH-token selection, category history and chain view are presented in [ETH market composition and history](MARKET-STRUCTURE.md). The discovery screens below retain their original scope and dates; full mixed-pool TVL is not the measured ETH principal.


The original data capture was completed on 3 October 2026. The financial snapshot T is 2 October 2026, 23:59:59 UTC. History covers 24 completed months, October 2024 to September 2026, and return windows end at T. The presentation review adds documentation checked on 4 October 2026 without changing those financial dates. This edition brings together the market data, contract checks and product findings. Global net size and complete portfolio reconciliation remain open.

## Main finding

ETH yield is built from several claims on the same underlying ETH. A staking receipt can become restaking collateral, enter a lending market or be held by a managed vault. Borrowing against it creates another deployment. Principal tokens (PT) and liquidity-provider positions (LP) add further claims. To understand the market, we need to separate the ETH backing those claims, external investors' equity after debt, and gross assets deployed across protocols. A conventional total value locked (TVL) sum can mix all three.

Screening 16,992 yield pools identified 5,688 ETH-family candidates across 57 chains and 197 projects represented in the feed. Of 87 protocols selected for deeper collection, 82 have token history. There are 259 pools with full TVL ≥$5M. The candidates' full-pool TVL adds up to $70.939B, including non-ETH assets in mixed pools and repeated claims on the same capital. **This measures the discovery screen, not the net capital in the ETH yield market.** Net totals that have not been established remain `null` in the data.

The strongest product findings come from narrower questions that we can verify. These include Liquid ETH's share supply and price per share (PPS) on Ethereum and Optimism, its debt accounts and most identified assets; Concrete's custody and original share issuance; historical returns for Fluid Lite, Treehouse and CIAN; the credit behind carry strategies; Tron ETH contract identities; and Ethena's currently disclosed ETH basis positions.

The edition contains 12 dossiers, 25 evidence claims and 31 selected ownership, claim and debt relationships. Start with the [research guide](README.md), then explore [return history](HISTORY.md), [economics and stresses](ECONOMICS.md) and [dependencies](DEPENDENCIES.md). The [return-driver review](RETURN-DRIVERS.md) explains what the observed returns can tell us, and [product terms](PRODUCT-TERMS.md) compares fees, exits and control rights.

## Where the market sits

The original core coverage includes Ethereum, Base, Arbitrum and Optimism. The expanded fixed-block dollar-reserve atlas also measures Avalanche, BNB Chain, Linea, Mantle, Monad, Polygon, Scroll and Sonic. The screen also highlights Tron, BNB Chain, Linea, Monad, Polygon and Gnosis. The other 47 chains remain in the tables; a chain without a deep dossier may still contain a market. Mantle/mETH and chains where rsETH operations are being wound down remain relevant dependencies despite their smaller local TVL.

| Chain | Current candidate full-pool TVL | Role and limitation |
|---|---:|---|
| Ethereum | $66.462B | Staking issuers, lending, carry and core infrastructure; substantial overlap |
| Base | $1.319B | Lending and LP; many small pools |
| Tron | $1.289B | One large mapped-ETH pool; backing and income require separate analysis |
| BNB Chain | $637.576M | ETH representations and DeFi; token chain differs from validator geography |
| Arbitrum | $568.131M | Lending, LP and historical PT/strategies |
| Linea | $208.053M | Concentrated in relatively few large exposures |
| Monad | $127.920M | Cross-chain strategies/claims, including Liquid ETH's sleeve |
| Optimism | $96.490M | Distinguish deployment from share circulation |
| Polygon | $62.127M | Lending/LP and bridged-asset dependencies |
| Gnosis | $39.790M | Local deployments and wrapped ETH |

These are post-T discovery observations without a common valuation timestamp. All 57 chains and 82 dated protocols appear in the [market tables](MARKET-TABLES.md). Ethereum accounts for 93.69% of screened TVL, but that does not establish its share of unique ETH backing or investor equity. Backing can remain on Ethereum while its receipts circulate on another chain.

The chain map therefore has three layers: where the backing sits, where a strategy operates and where its shares circulate. Liquid ETH shares exist on Ethereum and Optimism at T, while its allocation interface shows Ethereum and Monad. The same product has different share-circulation and strategy-deployment maps.

Native staking provides a separate scale reference. The captured [Ethereum.org page](https://ethereum.org/staking/) shows approximately 43.87M ETH staked, without a usable state timestamp at T. That number cannot be reconstructed simply by adding liquid staking token (LST) TVL or multiplying validator count×32. Restaking is another use of the same stake, so it cannot be added as new underlying ETH. See the [staking and restaking dossier](dossiers/staking-restaking.md).

## Measured WETH lending and concentrated demand

At the fixed T blocks, Aave V3 on Ethereum, Base, Arbitrum and Optimism, together with Spark on Ethereum, contains **2.881M WETH lender claims**, **2.388M WETH debt** and **410,491 WETH cash**. The market identities and chain-specific blocks are verified. This is a selected lending segment: its claims overlap with other backing and deployments, so it is not unique market capital.

The main Liquid ETH vault accounts for **23.28% of Aave Ethereum variable WETH debt**. Managed staking loops are therefore a material source of ETH borrowing demand. Some ETH lender income comes from borrowers trying to earn a staking spread on leveraged LST holdings. Those two yield sources are connected.

Independent contract getters report approximately **52,964 ETH reserve deficit on Ethereum and 29,835 on Arbitrum** at T. These values do not establish a loss charged to investors. That conclusion would require recovery assets, treasury accounting and settlement/burn events. [Aave's deficit mechanics](https://github.com/aave-dao/aave-v3-origin/blob/main/docs/3.3/Aave-v3.3-features.md) explain why this ledger differs from ordinary reserve balances.

APY and available cash do not describe the full quality of a lending claim. Claims, performing debt, cash, deficits and recovery must be assessed together. See the [five-market evidence](LENDING-MARKETS.md). We do not use a reserve deficit to explain Liquid ETH's unexplained balance without evidence linking that particular claim to the deficit ledger.

## Protocols and strategies

Dated ETH-family observations include Lido $26.677B, Binance Staked ETH $10.081B, Aave V3 $9.835B, EigenCloud $7.075B, ether.fi Stake $5.188B, SparkLend $4.161B, Sky Lending $1.639B, Morpho Blue $1.422B, Rocket Pool $1.409B, JustLend $1.310B, Kelp $1.130B, StakeWise V3 $1.017B and Concrete $953.047M. These amounts overlap and should not be added. Most observations are dated 2 October, 00:00 UTC, rather than the end-of-day contract state.

| Class | Income source | Separate accounting |
|---|---|---|
| E1 staking | Issuance, tips and MEV after expenses | Backing, receipts and external rewards |
| E2 restaking | Security-service payments | Stake overlap, AVS rewards, slashing and points |
| E3 ETH debt loop | Staking spread on amplified collateral | ETH debt, rates, oracles and unwind liquidity |
| E4 ETH collateral / USD carry | Dollar deployment yield minus dollar debt cost | Invested principal, collateral HF and credit losses |
| E5 lending | Borrower interest | Utilized debt, idle liquidity and bad debt |
| E6 PT/fixed yield | discounted maturity claim | redemption unit, expiry, SY/PT/YT overlap |
| E7 LP | trading fees/incentives | principal, range, depeg, debt, fee growth |
| E8 options | Transferred counterparty payoff | Directional exposure and obligation losses |
| E9 spot/short basis | Funding or dated-futures basis | Dollar exposure, margin, custody and ETH-only leg |
| EH hybrid | Combination of the above | Sleeve equity and shared counterparties |

The [mechanics guide](MECHANICS.md) explains who pays for each strategy, its formula, break-even point and stress path. E8 has mechanics and discovery coverage without a verified aggregate size. The [product-terms review](PRODUCT-TERMS.md) includes Ribbon's documented historical ETH-call example. Its dated historical/deprecation status is separated from current Thetanuts candidates in the strategy atlas, and it contributes no amount to the fixed-T market totals.

## Ether.fi: carry and looping together

Liquid ETH's published net asset value (NAV) at T is 177,171.063302 ETH, approximately $472.684M using the disclosed T+1-second quote. The partial balance reconstruction totals $460.231M, including the Monad claim valued at its own Accountant rate. The remaining $12.453M, or 2.634%, is unresolved. That difference neither establishes a deficit nor independently verifies the backing of the other claims.

The 3 October interface assigns 64.66% to two carry allocations and 21.65% to explicitly labelled loops. These weights were observed after T and are not verified fixed-block allocations. The main Aave position has $1.182B weETH collateral, $1.094B ETH debt and $88.732M equity, giving 13.325× leverage and a health factor (HF) of 1.02708. Spark has 9.762× leverage and HF 1.03615. A health factor reaching 1 makes the lending position eligible for liquidation.

Aave's HF uses the capped conversion oracle, so it need not move with every decentralised exchange (DEX) price. The approximately 2.64% headroom is a collateral-oracle markdown with debt and the liquidation threshold (LT) fixed. A market discount can separately make repayment and exit more expensive. The Drone's stablecoin debt has a different exposure: an ETH/USD decline can weaken its HF even if the strategy holding the borrowed dollars is market-neutral.

The frozen model combines trailing-30-day staking annual percentage rate (APR) with WETH borrow APR at T. The main Aave loop reaches zero model return after approximately **44 bp** of additional borrowing cost, before fees and rewards. Its 410,134 WETH debt exceeds the reserve's 269,693 WETH cash, limiting an unwind funded by one flash loan from that reserve. Other liquidity sources and staged repayments remain possible. This measures a capacity constraint; it does not forecast an exit failure.

Liquid ETH's published PPS gains 6.8501% over 730 days, compared with stETH's 5.4875%, an excess of 1.3626 percentage points (pp). Annualized returns are 3.3683% and 2.7071%. The observed excess is measurable but modest relative to the product's complexity. Its last year is stronger, although the current portfolio composition cannot by itself explain the historical result. See the [return-driver analysis](RETURN-DRIVERS.md).

The [Liquid ETH dossier](dossiers/etherfi-liquid-eth.md) covers fees, governance, LP positions, the queue and the remaining limitations. The owner has a 24-hour timelock, but management-fee permission also belongs to role 55 at a separate address. The owner's delay therefore cannot be treated as a universal delay on every fee or operational change. The [product-terms review](PRODUCT-TERMS.md) links the fixed-block capability evidence.

## Carry reaches BTC collateral and real credit

Address-level evidence shows that senRLUSDv2 earns from dollar lending. Its borrowers are not limited to ETH holders. Book assets at T are 444.242M RLUSD: approximately 52.89% in kBTC/RLUSD, 24.09% in weETH/RLUSD and 7.23% in USDe/RLUSD, plus cbBTC, syrupUSDC, FXRP and other markets. Liquid ETH holds a 55.105M RLUSD claim, approximately 12.40% of book assets.

senPYUSDPRIMEv2 has approximately 219.084M PYUSD book assets, with 95.04% supplied to PRIME/PYUSD. Liquid ETH's claim is 49.605M PYUSD, or 22.64%. [Sentora's case study](https://sentora.com/case-studies/sentora-s-prime-main-vault-reaches-200m-in-pyusd-deposits-in-under-100-days) links PRIME income to home-equity financing. The quality of those loans, redemption terms and collateral liquidity matter more to this income than demand for Ethereum transactions.

The main Liquid ETH vault and LoanManager also borrow in the weETH/RLUSD and PRIME/PYUSD markets. Their ownership and supply/borrow shares imply approximately 8.709M RLUSD and 4.759M PYUSD of self-credit notional. This is the amount of lending exposure linked back to the same group's borrowing, not additional NAV or measured interest income. Part of the borrower's interest can return through its owned supply portfolio. The relevant income is what remains from external payers after curator fees and debt costs.

BTC collateral and real-world assets (RWA) are material dependencies of these ETH products' dollar strategies. They belong in the ETH analysis as sources of income and risk. The scope remains the ETH product rather than a new BTC market census. See the [carry-credit dossier](dossiers/carry-credit.md).

## Concrete changes TVL interpretation

Two ETH vaults use the same 3-of-5 Safe, a wallet requiring three of its five owners to authorise a transaction. All 278,170.834213 ctDeltaWeETH shares originated in one UnbackedMint on 16 December 2025 and are held by one address at T. The shared custody Safe holds all ctwstETH Plus supply.

These relationships may reflect a migrated portfolio and internal ownership. The events alone do not prove that backing is absent. They also do not establish that the approximately $953M published ETH-family NAV represents new external deposits. Adding that NAV to all assets in the Safe would risk counting the same capital twice. A flat PPS cannot establish zero investor income when private payouts have not been disclosed.

The remaining work is to establish the original portfolio, holders' economic rights and each vault's allocation of assets and liabilities. See the [Concrete dossier](dossiers/concrete-eth.md) and [product terms](PRODUCT-TERMS.md).

## Returns and exits change product rankings

Over the same 730-day window, ETH book returns are Fluid Lite 8.8243%, Liquid ETH 6.8501%, Treehouse 6.2761%, stETH 5.4875%, weETH 5.2947% and CIAN rsETH 1.0854%. These exclude external rewards, exit costs and the outcome of executing a complete withdrawal. Over 365 days, Liquid ETH leads Fluid Lite, 3.8700% versus 3.5096%. The ranking changes with the horizon.

Fluid Lite has approximately 600,256 ETH-equivalent gross assets, 522,809 debt and 77,359 net after revenue at T, with 7.759× leverage. Its contract assumes stETH/eETH/WETH parity, so this is a contract valuation rather than a market NAV that reflects trading discounts. WithdrawFee for 1 stETH is 0.0005 stETH, or 5 bp.

Treehouse uses IAU_wstETH, an internal accounting unit, as its asset rather than physical token inventory. Historical getUnderlying checks verify that denomination. Two-year IAU growth is approximately 0.7475%; adding the verified wstETH conversion gives a 6.2761% ETH return. The [redemption terms](https://docs.treehouse.finance/protocol/tasset/architecture/redemption-process) describe approximately seven-day standard redemption, a 5 bp charge and a minimum-rate formula. Fast redemption costs 0.5% and has capacity limits. That exit cost is material relative to the measured excess over staking.

CIAN's rsETH units per share declined 4.1177% over two years. Growth in the underlying issuer-oracle conversion offsets part of that decline, leaving a 1.0854% ETH book return. A complete investor profit and loss calculation still needs external rewards and event attribution. Returns must use the correct units and compounding; multiplying today's APY by the holding period does not reconstruct them.

## Tron: a large balance with almost no yield

The [JustLend contract directory](https://docs.justlend.org/developers/deployed_contracts/) identifies ETH and ETHB by different addresses and explains their renaming. Current ETH `THb4…` was ETHOLD; ETHB `TRFe…` represents another mapped token. The 2023 offboarding announcement does not describe the current directory, which lists both as active.

The current ETH API reports approximately 484,122 cash units, 87.51 borrowed, a 0.0002899% annual base supply rate and zero mining rewards. Utilization is approximately 0.0181%, so the large nominal balance generates very little borrower income. Physical backing remains unverified. This mapped-token segment is kept separate from verified native ETH. The [Tron dossier](dossiers/justlend-tron.md) reconciles cash+borrows−reserves with share claims.

## Ethena and PT: leg size and lifecycle matter

The 3 October [Ethena backing dashboard](https://app.ethena.fi/dashboards/backing-assets) shows approximately $374.44M of ETH basis positions across Binance/Ceffu, Bybit/Copper and OKX/Copper. Total crypto basis is $928.89M; other backing includes DeFi and institutional lending, liquid stablecoins and RWA. USDe supply therefore cannot be used as the size of ETH carry. These are rounded post-T disclosures, without independently reconstructed custody books.

The fully paginated Pendle API covers four chains and 626 markets, with 126 selected ETH accounting assets. At T, 122 are expired and four remain unexpired. Their current automated market-maker (AMM) liquidity is approximately $6.264M. That is pool liquidity, not PT principal or the size of the whole fixed-yield market. Expired markets can still contain redemption claims, and other venues exist. A wave of maturities should not be read as a wave of investor exits. See the [PT dossier](dossiers/pendle-pt.md) and [basis dossier](dossiers/ethena-basis.md).

## The broader financing and product investigation

The [funding atlas](DOLLAR-FUNDING-ATLAS.md) measures 60 dollar reserves across 12 chains and 320 archived rate observations. The [credit expansion](CREDIT-EXPANSION.md) adds Compound, Euler, Fluid and separately bounded Silo deployments. These are financing evidence; all-collateral reserve debt is not ETH carry capital.

The [additional product histories](PRODUCT-FINANCIAL-HISTORY.md) measure six product claims at T, matched stETH share benchmarks, loan states and selected withdrawal demand. Yearn's fourth strategy is a material Spark ETH loop absent from its default withdrawal queue. YieldBasis debt differs from allocated crvUSD. The [hgETH study](HGETH-LOAN-BOOK.md) reconciles a seventh material loan-pool book with physical rsETH and an adapter reserve.

The [nested carry investigation](CARRY-VARIANTS-EXPANSION.md) follows historical TAU and Reservoir financing and manager mark ages. The [financed lifecycles](CARRY-LIFECYCLES.md) calculate actual paid destination proceeds against allocated loan cost and residual debt. The [large-borrower study](BORROWER-USE.md) traces refinancing and dollar conversion rather than assigning every dollar loan to yield investment.

These exhibits deepen the report without changing T or silently merging post-T discovery with financial balances. The [coverage assessment](MARKET-COVERAGE.md) gives the mechanism-wide evidence and remaining public measurement gaps.

## What is established and what remains open

Confidence is high for the fixed-block states we read, contract identities and return arithmetic. It is medium for adapter history and currently disclosed allocations, and low or unknown for the origin of external deposits, private distributions, shared-custody backing and global net totals. These evidence types retain their different limits even when they appear in the same comparison table.

The priorities are native staking at T, a market-wide ownership and backing graph, a complete Aave/Morpho borrower census, the Monad allocation and Liquid ETH's unexplained balance, historical asset universes and strategies, investor rewards, executable redemption and repayment, unmeasured venue/loan histories beyond the archived observations, and concentration among the final payers of income.

The existing data and tools provide the starting point for that work. The [execution checklist](EXECUTION-CHECKLIST.md) records phase status, the [audit guide](AUDIT.md) explains evidence and reproduction, and the [research plan](RESEARCH-PLAN.md) preserves the full target scope.
