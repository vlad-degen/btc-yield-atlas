# Product development, ownership and carry economics

Financial snapshot: **2 October 2026, 23:59:59 UTC**. Public documents reviewed on 6 October. The main report retains the BTC eight-chapter route. This supporting chapter explains the history behind the five largest examined books.

## ether.fi Liquid ETH

The present contract was used in June 2024. ETH loops came first; Aave dollar borrowing appeared in August 2025. Morpho financing followed through the LoanManager in June 2026 and the main vault in July.

| Date | Change | Economic significance |
| --- | --- | --- |
| 2024-06-11T02:15:35+00:00 | First observed share issuance | A 0.24446-share mint establishes use of the present contract. Deployment was 3 June; neither timestamp alone establishes the public launch. [Primary evidence](https://etherscan.io/tx/0x1221b300eb5ee3ef6ec3b94b16dc888a68293e49b84b3a5d7418be126ff19070) |
| 2024-06-25 | The Aave ETH loop begins | The main vault first borrows WETH. This increases staking exposure; it does not create dollar investment capital. [Primary evidence](https://etherscan.io/tx/0x744955da54daf75b9d30f6c648f685e3921e45f6cdc17aa695d1314aaf0f6cfd) |
| 2025-08-18 | Dollar financing appears in the managed account | The controlled account 0x0a42…c02c first borrows USDC on Aave. It already owes 47.07M USDC at the August month end. [Primary evidence](https://etherscan.io/tx/0x4e906fd4127e61b3360c3bf1d1953366ca49246a67cec545c033c4f46e63ebfb) |
| 2025-11-26 | Cap becomes an investment destination | The captured stcUSD deposit history begins. Its receipt earns through Cap’s credit machinery; this is a new destination, not extra underlying ETH. [Primary evidence](https://etherscan.io/tx/0x9b217842406c49d31c2dc5e32d0d8bc3cee67cf2aeb18c2bae3ef033dd64bc88) |
| 2026-03-24 | Spark adds a second ETH loop | The first main-vault Spark WETH borrowing is observed. The main Aave and Spark accounts have different liquidations and funding costs. [Primary evidence](https://etherscan.io/tx/0x8fd92c153ccdf45c864f79b4b7fd288f430e40aa017d4f56338cb35abb5a3442) |
| 2026-06-23 | Morpho dollar routes expand beyond the main vault | The controlled LoanManager begins RLUSD borrowing in June. The main vault adds weETH/RLUSD and weETH/PYUSD in July; Sentora RLUSD V2 deposits begin on 7 August. [Primary evidence](https://etherscan.io/tx/0x2ad45b7723fbbfb5b6c36ce035167a0c7bfc825b6ad36573a4d9e4fed2d0cb08) |
| 2026-08-09T11:00:21+00:00 | Cash shares move into pooled custody | The captured Cash spoke history begins. By T, the Hub holds 20.53% of the whole Liquid book on behalf of 7,012 positive account positions. [Primary evidence](https://optimistic.etherscan.io/address/0xdffcc3536d932eb51df51a7f5fa407c4270d5308) |
| 2026-09-25 | PRIME-backed financing enters the credit vault | An 18M PYUSD loan against PRIME is deposited into a PYUSD credit vault. Its claim and financing are measured through T. [Primary evidence](https://etherscan.io/tx/0xb12b59b3177d97b6f2118b14b6712c09558c75c977fa78c5ef3eb1d4d2fbc176) |
| 2026-09-25 | Kyber adds a distribution channel | Kyber announces Liquid ETH on KyberEarn. This establishes an integration announcement, not how many new deposits it generated. [Primary evidence](https://blog.kyberswap.com/ether-fi-liquid-vaults-are-live-on-kyberearn/) |

### What the investor owns and earns

For the 18M PYUSD investment originated on 25 September, FIFO, LIFO and proportional withdrawal allocation all give a negative claim-minus-funding result: -5,360 to -4,584 PYUSD through T. Rewards, collateral income, gas and outer fees are separate.

The two largest Ethereum wallets together hold about 37% of the whole book. The Optimism Hub holds another 20.53% across 7,012 positive Cash account positions. Its single address conceals a distribution of claims; these accounts are not necessarily different people.

Between September 2024 and September 2026, the ETH book grew by 30,053 ETH. Share-supply changes account for 19,717 ETH of that change; the share-price effect accounts for 10,336 ETH. This is an accounting bridge, not a cash-flow or carry-profit estimate.

The Ethereum management fee changed repeatedly: 1.50% in January 2025, zero in July, and 0.35% at T. Nineteen claimed payments total 2,130.60 ETH after converting each weETH payment at its own block. This is platform cash received, not operator profit.

The May 2025 Member Rewards proposal budgets 7.5M ETHFI across ether.fi for June to August and assigns Liquid ETH nine points per ETH per day, versus three for staking. This explains the distribution incentive; the ecosystem budget is not a measured payment to this vault or organic carry income.

At T, Aave USDC funding is 13.93% APR, versus 4.38% for Aave USDT and 4.39% for Spark PYUSD. Funding cost depends on the actual loan currency and venue; a low quote on one route does not describe the whole carry book.

[Distribution proposal](https://governance.ether.fi/t/ether-fi-member-rewards/2974).

| Named owner / account | Share of stated claim | Denominator |
| --- | --- | --- |
| [0x6794662db6a212b607ecfc07360941b5ddfd4b6b](https://optimistic.etherscan.io/address/0x6794662db6a212b607ecfc07360941b5ddfd4b6b) | 33.3449% | Share of Cash Hub |
| [0xc93c35246652b40f3f090bd180b58322679b9f1b](https://optimistic.etherscan.io/address/0xc93c35246652b40f3f090bd180b58322679b9f1b) | 9.1729% | Share of Cash Hub |
| [0x463ff502f702a306f2c5850a0562fb47b8e4acea](https://optimistic.etherscan.io/address/0x463ff502f702a306f2c5850a0562fb47b8e4acea) | 3.0972% | Share of Cash Hub |
| [0x72cbd2c5e6cfe895224af00c039c7d2b3b11a9b5](https://optimistic.etherscan.io/address/0x72cbd2c5e6cfe895224af00c039c7d2b3b11a9b5) | 2.0542% | Share of Cash Hub |
| [0x0cb7977b907782ca1038ba68699263c9eecaf879](https://optimistic.etherscan.io/address/0x0cb7977b907782ca1038ba68699263c9eecaf879) | 1.7065% | Share of Cash Hub |
| [0xf387f8058e00fe37d5c11a205ee0bad9774ac4df](https://optimistic.etherscan.io/address/0xf387f8058e00fe37d5c11a205ee0bad9774ac4df) | 1.5225% | Share of Cash Hub |
| [0x428167a972786b7f924af2f2ecf6680aa8b5243e](https://optimistic.etherscan.io/address/0x428167a972786b7f924af2f2ecf6680aa8b5243e) | 1.4596% | Share of Cash Hub |
| [0x559e319c3710c2370ed1b18878ee10a2ff1f9339](https://optimistic.etherscan.io/address/0x559e319c3710c2370ed1b18878ee10a2ff1f9339) | 1.4378% | Share of Cash Hub |
| [0x1c0a6763a251be74ef56c1919b1184f94f93a70d](https://optimistic.etherscan.io/address/0x1c0a6763a251be74ef56c1919b1184f94f93a70d) | 1.4326% | Share of Cash Hub |
| [0xed0e0f34671338fd51c90cad6b5eabc239ac4f6e](https://optimistic.etherscan.io/address/0xed0e0f34671338fd51c90cad6b5eabc239ac4f6e) | 1.2906% | Share of Cash Hub |

[Reproducible measurement ledger](../../../data/eth/parity_depth_measurements.json).

## YieldBasis WETH

WETH liquidity existed by January 2026. The chart follows the current LT contract from May and does not splice the old Curve pool into its return series.

| Date | Change | Economic significance |
| --- | --- | --- |
| 2026-01-23 | An earlier WETH pool is already operating | The parameter proposal identifies Curve pool 0x6e54…A9C2 and discusses dynamic swap fees, financing and temporary redemption discounts. Its history must not be confused with the current LT receipt. [Primary evidence](https://forum.yieldbasis.com/t/tweak-weth-pool-parameters/25) |
| 2026-05 | The measured current WETH LT book appears | The present LT contract is absent at the sampled April end and funded at May end. Its AMM at T is 0x5f8d…233c, distinct from the January pool. [Primary evidence](https://etherscan.io/address/0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea) |
| 2026-05 to 2026-06 | V3 changes the liquidity architecture | Curve’s dated recap describes FXSwap upgrades and personal HybridVaults combining crypto exposure with crvUSD allocation. It reports an allocation adjustment from 55% to 45%; this is not an investor yield promise. [Primary evidence](https://news.curve.finance/curve-monthly-recap-may-june-2026/) |
| 2026-10-02 | Staking changes the economic claim | The gauge holds 56.35% of direct LT supply for 155 receipt holders. Unstaked LT marks and gauge fee/reward rights are different investor outcomes. [Primary evidence](https://etherscan.io/address/0xd829456fd63ada7de0657714a3a7a26de403e3d8) |

### What the investor owns and earns

Traders pay Curve swap fees. Those fees must fund rebalancing and crvUSD financing before the ETH holder earns a spread. A staked gauge receipt has additional fee and YB reward rights; the unstaked LT return chart excludes those cash flows.

Of 332 direct LT addresses, the largest is a gauge with 56.35% of supply. Its 155 holders own the gauge claim. After replacing that custody balance and mapping four personal HybridVaults to their owners, the largest named-owner claim is 21.77% of LT supply. Other contracts remain identified as custody.

| Named owner / account | Share of stated claim | Denominator |
| --- | --- | --- |
| [0x0b077c44454fdfb799e303a0fd43f278fd1ae081](https://etherscan.io/address/0x0b077c44454fdfb799e303a0fd43f278fd1ae081) | 21.7721% | Share of LT supply |
| [0xb016f77cdc7874da1cddf28605010fd2d19b55a8](https://etherscan.io/address/0xb016f77cdc7874da1cddf28605010fd2d19b55a8) | 9.5236% | Share of LT supply |
| [0x9e406b2c2021966f3983e899643609c45e3bbffe](https://etherscan.io/address/0x9e406b2c2021966f3983e899643609c45e3bbffe) | 7.2044% | Share of LT supply |
| [0x3da232a0c0a5c59918d7b5ff77bf1c8fc93aee1b](https://etherscan.io/address/0x3da232a0c0a5c59918d7b5ff77bf1c8fc93aee1b) | 6.1207% | Share of LT supply |
| [0x2cc4e9d6d5656205f9b3206287945c3ca97dc6ce](https://etherscan.io/address/0x2cc4e9d6d5656205f9b3206287945c3ca97dc6ce) | 6.1188% | Share of LT supply |
| [0xf791da446d04282f921f38fbf954ad5caee899a3](https://etherscan.io/address/0xf791da446d04282f921f38fbf954ad5caee899a3) | 5.7027% | Share of LT supply |
| [0xb24d671f0c7bef757412897ef60013040185c6fa](https://etherscan.io/address/0xb24d671f0c7bef757412897ef60013040185c6fa) | 4.5105% | Share of LT supply |
| [0x8e8745acd6fbe3e70afc96042c7f3ec84b1f0e9f](https://etherscan.io/address/0x8e8745acd6fbe3e70afc96042c7f3ec84b1f0e9f) | 4.0442% | Share of LT supply |
| [0xdfbe92a83a3c17c69acca978b0ba23fdcca286f4](https://etherscan.io/address/0xdfbe92a83a3c17c69acca978b0ba23fdcca286f4) | 3.0556% | Share of LT supply |
| [0x27a6df167b15450f6653e5314988f281d65631d1](https://etherscan.io/address/0x27a6df167b15450f6653e5314988f281d65631d1) | 2.6138% | Share of LT supply |

[Reproducible measurement ledger](../../../data/eth/parity_depth_measurements.json).

## Lido Earn ETH

The underlying strategy launched in November 2025; the present outer EarnETH book is measured from March 2026. Its April crisis and May recovery belong in the investment history.

| Date | Change | Economic significance |
| --- | --- | --- |
| 2025-11-06 | stRATEGY launches before the current outer vault | Lido introduces the underlying strETH strategy with Aave, Ethena and Uniswap routes. Its announced 1% annual and 10% performance fees describe that launch, not the zero nested settings observed at T. [Primary evidence](https://blog.lido.fi/introducing-the-lido-strategy-vault/) |
| 2026-02-19 | DAO proposes a first-loss treasury allocation | The proposal assigns $3M in wstETH to EarnETH and $2M in USDC to EarnUSD. DAO shares can absorb losses by being burned; the budget is not a yield reward. [Primary evidence](https://research.lido.fi/t/lido-earn-competing-on-trust-5m-treasury-allocation/11228) |
| 2026-03 | Current EarnETH outer vault becomes materially funded | The first >1 ETH month-end book in the sampled outer-vault history is March. Earlier strETH capital belongs to its predecessor and is not backfilled into this chart. [Primary evidence](https://docs.lido.fi/earn/deployment-contracts/) |
| 2026-04-18 | Kelp-related market stress freezes the exit | The review reports roughly 113.2k rsETH collateral and 111.1k WETH debt in the affected strategy. Deposits and withdrawals pause for 27 days; funding costs become an actual loss. [Primary evidence](https://research.lido.fi/t/kelp-incident-review-earneth-exposure-response-and-risk-framework-changes/11579) |
| 2026-05-15 | Operations resume after DAO loss absorption | The executed transaction burns 143.9766 earnETH shares. The later treasury report values the cover at 144.77 ETH. User protection came from reserve capital as well as recovery of the affected markets. [Primary evidence](https://etherscan.io/tx/0xdfca0390d39299ec88e6be26f5254d873b9a1098f71591c42f357412d60e71c7) |
| 2026-09-29 | A directly financed USDT investment is measurable | A 5M USDT borrowing and new earnUSD claim in the same transaction gain 1,400.57 USDT after allocated interest through T, before gas and outer fees. Existing allocated shares are excluded. [Primary evidence](https://etherscan.io/tx/0x48c24a9436a519bd778454ff6946404afa79f943afc1952e36c08d69949adbc1) |

### What the investor owns and earns

The USDT-funded earnUSD claim earns a different spread from the leveraged ETH staking positions. The 5M USDT lot adds 1,400.57 USDT before gas and outer fees over 3.75 days; its mark remains an investment claim rather than redeemed cash.

The outer token has 2,500 positive holder addresses, including managed accounts. Allocated but unclaimed shares sit outside that issued-token census. The DAO’s first-loss reserve is risk-bearing seed capital, not a deposit guarantee.

The Kelp review reports 143.98 ETH of operational loss from elevated funding costs. The treasury’s later account specifies 143.98 earnETH shares burned, worth 144.77 ETH. The executed burn confirms the share units. These disclosures use different measures and must not be added together.

[Reproducible measurement ledger](../../../data/eth/parity_depth_measurements.json).

## Avant avETH / savETH

avETH and senior savETH have a measured September 2025 origin in this study. Later issuer disclosures show a multi-chain, leveraged book; the measured Ethereum face supply is not that global NAV.

| Date | Change | Economic significance |
| --- | --- | --- |
| 2025-09 | The measured avETH book becomes material | September is the first >1 ETH month-end issuer face supply in the captured history. The official yield series begins with the week ending 25 September; neither observation establishes an exact public launch date. [Primary evidence](https://app.avantprotocol.com/api/metrics/aveth) |
| 2026-09-29 | Issuer discloses a leveraged multi-chain portfolio | The dated disclosure reports $72.65M assets and $39.47M liabilities, with $33.18M net NAV. A $32.53M savUSD position makes own-issuer credit economically important. These are reported portfolio figures, not a T backing audit. [Primary evidence](https://app.avantprotocol.com/api/metrics/aveth) |
| 2026-10-02 | The senior claim and holder intermediaries are traced | savETH owns 88.08% of Ethereum avETH face supply. Its 83 direct holders include a Gearbox credit account, Morpho collateral custody and a CCIP bridge pool. [Primary evidence](https://etherscan.io/address/0xda06ee2dacf9245aa80072a4407debdea0d7e341) |

### What the investor owns and earns

Senior savETH earns from the avETH issuer structure. ETH collateral generates staking income while dollar loans finance credit claims, including the issuer’s own savUSD product. A senior return series does not disclose the complete strategy P&L or the junior loss waterfall.

The 37 direct avETH holders do not describe senior investor ownership: savETH holds 88.08% of avETH and has 83 direct receipt holders. After tracing Gearbox and Morpho custody and combining each named owner’s claims, the largest holds 42.90% of senior shares. The CCIP bridge still represents remote claims.

| Named owner / account | Share of stated claim | Denominator |
| --- | --- | --- |
| [0x3d461625dc02f1d4c8b14601439357be2ec07904](https://etherscan.io/address/0x3d461625dc02f1d4c8b14601439357be2ec07904) | 42.9036% | Share of senior savETH |
| [0x43f47a434dadd5a122c42e49378365cca949fa54](https://etherscan.io/address/0x43f47a434dadd5a122c42e49378365cca949fa54) | 16.2694% | Share of senior savETH |
| [0x66b206c91374453cda591e84287eefef7a3d4f21](https://etherscan.io/address/0x66b206c91374453cda591e84287eefef7a3d4f21) | 11.7224% | Share of senior savETH |
| [0xe29bb87d5a3a8ef6b24edb35d0d8ef0241cb39d1](https://etherscan.io/address/0xe29bb87d5a3a8ef6b24edb35d0d8ef0241cb39d1) | 8.4669% | Share of senior savETH |
| [0x8c2527051d0e98ad09211749fafbe1aa590c01b3](https://etherscan.io/address/0x8c2527051d0e98ad09211749fafbe1aa590c01b3) | 3.7896% | Share of senior savETH |
| [0xcf7e7c56614b6e22b0043895a37e3858971ec904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) | 3.0212% | Share of senior savETH |
| [0x55c4a5eb2b5323a7ddf97c6870f4794cd19a3ed1](https://etherscan.io/address/0x55c4a5eb2b5323a7ddf97c6870f4794cd19a3ed1) | 2.1837% | Share of senior savETH |
| [0x96977d15ee849bcbb23ea88f0517e1e4faad81d4](https://etherscan.io/address/0x96977d15ee849bcbb23ea88f0517e1e4faad81d4) | 2.0794% | Share of senior savETH |
| [0x1cde180fd33935c744623d655696eb3a77e5d891](https://etherscan.io/address/0x1cde180fd33935c744623d655696eb3a77e5d891) | 1.9118% | Share of senior savETH |
| [0x6f593a98f9fd364027cd053bdee1fa97f9826a45](https://etherscan.io/address/0x6f593a98f9fd364027cd053bdee1fa97f9826a45) | 1.1368% | Share of senior savETH |

[Reproducible measurement ledger](../../../data/eth/parity_depth_measurements.json).

## Concrete Delta weETH

The share contract was deployed in December 2025. Its first completed-month weETH book is already large, but the native share price stays flat through T. The resulting ETH mark largely follows weETH staking conversion.

| Date | Change | Economic significance |
| --- | --- | --- |
| 2025-12-12T10:48:23Z | Share contract deployed | The contract creation transaction establishes the first possible onchain history. Public launch can occur later. [Primary evidence](https://etherscan.io/address/0xb9dc54c8261745cb97070cefbe3d3d815aee8f20#code) |
| 2025-12-31 | First completed-month book observation | 278,170.834213 weETH book assets. Subsequent captured month ends retain the same native asset book and unit share price. [Primary evidence](https://etherscan.io/address/0xb9dc54c8261745cb97070cefbe3d3d815aee8f20#code) |
| 2026-10-02T23:59:59Z | Owner, fee role and private-account scope verified | Configured vault management and performance fees are both zero; private service fees and arbitrage payout terms are not established. [Primary evidence](https://etherscan.io/address/0xb9dc54c8261745cb97070cefbe3d3d815aee8f20#code) |

### What the investor owns and earns

The stated mandate includes neutral arbitrage and staking collateral financed with dollars. The shared account has observable loans, but Delta-specific investment principal, revenue and private fees are not publicly assigned. Its place at the top of the book-size table is therefore not evidence of dominance in verified carry capital.

One externally owned address holds all issued Delta shares at T. That establishes concentration in this claim, while the shared custody Safe holds the actual strategy assets. It does not identify outside investor capital or assign the Safe’s dollar arbitrage profit to Delta.

[Reproducible measurement ledger](../../../data/eth/parity_depth_measurements.json).

## Liquid: the same invested dollars under three withdrawal conventions

Replay every actual destination mint and burn from inception. Assign withdrawals with FIFO, LIFO and proportional share conventions. Value remaining lots against the observed ending claim. Allocate deposit earnings to borrowed cash in proportion to loan cash/deposit cash, then subtract the exact debt-share cohort interest.

| Convention | Borrowed PYUSD | Allocated claim growth | Exact debt interest | Claim less financing |
| --- | --- | --- | --- | --- |
| FIFO | 18,000,000 | 13,408.744077 | 17,992.579637 | -4,583.835560 |
| LIFO | 18,000,000 | 12,632.455047 | 17,992.579637 | -5,360.124590 |
| Pro rata | 18,000,000 | 13,124.436200 | 17,992.579637 | -4,868.143437 |

Sensitivity scenarios, not rigorous economic bounds or observed unique provenance. The same whole-account gain reconciles under all conventions. Rewards, gas, outer fees, collateral earnings and private PRIME backing are excluded. The final 108-second lot is an accounting diagnostic, not a representative annual return.

[Loan and investment transaction](https://etherscan.io/tx/0xb12b59b3177d97b6f2118b14b6712c09558c75c977fa78c5ef3eb1d4d2fbc176), [cohort CSV](../../../data/eth/parity-Liquid-cohort-sensitivity.csv).

## Liquid: actual funding history

| Venue | Account | Currency | First borrowing | Borrow / repay events |
| --- | --- | --- | --- | --- |
| Aave | 0xf0bb20865277abd641a307ece5ee04e79073416c | WETH | [2024-06-25T04:50:35+00:00](https://etherscan.io/tx/0x744955da54daf75b9d30f6c648f685e3921e45f6cdc17aa695d1314aaf0f6cfd) | 113 / 64 |
| Aave | 0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c | USDC | [2025-08-18T17:31:47+00:00](https://etherscan.io/tx/0x4e906fd4127e61b3360c3bf1d1953366ca49246a67cec545c033c4f46e63ebfb) | 19 / 5 |
| Spark | 0xf0bb20865277abd641a307ece5ee04e79073416c | WETH | [2026-03-24T21:21:47+00:00](https://etherscan.io/tx/0x8fd92c153ccdf45c864f79b4b7fd288f430e40aa017d4f56338cb35abb5a3442) | 18 / 0 |
| Aave | 0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c | USDT | [2026-08-21T15:49:11+00:00](https://etherscan.io/tx/0xf20da2f2279b5e508fb49fedda1ffb46d20a1838d72b23f134f276e10fe3d695) | 2 / 0 |
| Spark | 0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c | PYUSD | [2026-10-02T23:58:11+00:00](https://etherscan.io/tx/0x3e66faeae23a347b524536ae17291e0f7c9d89c39bbba2e711cae76afd21e12d) | 1 / 0 |

Indexed account debt on current identified reserve debt tokens at verified month-end blocks. Earlier token absence remains null. This supplements the dated Morpho ledgers and does not reconstruct a complete historical asset allocation.

[Indexed monthly debt CSV](../../../data/eth/parity-Liquid-monthly-debt.csv), [Cash accounts CSV](../../../data/eth/parity-Liquid-Cash-beneficiaries.csv), [senior savETH CSV](../../../data/eth/parity-savETH-holders.csv), [YieldBasis gauge CSV](../../../data/eth/parity-ybGauge-holders.csv).

## Reproduce the measurements

The input ledgers below retain the captured request, response, block and source fingerprint where available. The measurement file records SHA-256 hashes of every input. Receipt look-through changes ownership attribution, not capital.

- [parity_depth_extra_sources.json](../../../data/eth/parity_depth_extra_sources.json)
- [parity_depth_fee_receipts.json](../../../data/eth/parity_depth_fee_receipts.json)
- [parity_depth_fees_owners.json](../../../data/eth/parity_depth_fees_owners.json)
- [parity_depth_holder_bindings.json](../../../data/eth/parity_depth_holder_bindings.json)
- [parity_depth_holder_checks.json](../../../data/eth/parity_depth_holder_checks.json)
- [parity_depth_holder_transfers.json](../../../data/eth/parity_depth_holder_transfers.json)
- [parity_depth_lending_events.json](../../../data/eth/parity_depth_lending_events.json)
- [parity_depth_monthly_debt.json](../../../data/eth/parity_depth_monthly_debt.json)
- [parity_depth_op_and_seed_sources.json](../../../data/eth/parity_depth_op_and_seed_sources.json)
- [parity_depth_op_asset.json](../../../data/eth/parity_depth_op_asset.json)
- [parity_depth_op_beneficiary_events.json](../../../data/eth/parity_depth_op_beneficiary_events.json)
- [parity_depth_op_hub.json](../../../data/eth/parity_depth_op_hub.json)
- [parity_depth_op_interface.json](../../../data/eth/parity_depth_op_interface.json)
- [parity_depth_op_liquidations.json](../../../data/eth/parity_depth_op_liquidations.json)
- [parity_depth_op_reserves.json](../../../data/eth/parity_depth_op_reserves.json)
- [parity_depth_op_spoke_interfaces.json](../../../data/eth/parity_depth_op_spoke_interfaces.json)
- [parity_depth_op_spokes.json](../../../data/eth/parity_depth_op_spokes.json)
- [parity_depth_op_user_balances.json](../../../data/eth/parity_depth_op_user_balances.json)
- [parity_depth_prime_rate.json](../../../data/eth/parity_depth_prime_rate.json)
- [parity_depth_reserve_tokens.json](../../../data/eth/parity_depth_reserve_tokens.json)
- [parity_depth_sav_gearbox_owner.json](../../../data/eth/parity_depth_sav_gearbox_owner.json)
- [parity_depth_sav_holder_bindings.json](../../../data/eth/parity_depth_sav_holder_bindings.json)
- [parity_depth_sav_holders.json](../../../data/eth/parity_depth_sav_holders.json)
- [parity_depth_sav_morpho_events.json](../../../data/eth/parity_depth_sav_morpho_events.json)
- [parity_depth_sav_morpho_markets.json](../../../data/eth/parity_depth_sav_morpho_markets.json)
- [parity_depth_sav_morpho_positions.json](../../../data/eth/parity_depth_sav_morpho_positions.json)
- [parity_depth_sav_routes.json](../../../data/eth/parity_depth_sav_routes.json)
- [parity_depth_sources.json](../../../data/eth/parity_depth_sources.json)
- [parity_depth_spark_debt.json](../../../data/eth/parity_depth_spark_debt.json)
- [parity_depth_yb_v3_source.json](../../../data/eth/parity_depth_yb_v3_source.json)
- [carry_attribution_ledger.json](../../../data/eth/carry_attribution_ledger.json)
- [carry_attribution_tranches.json](../../../data/eth/carry_attribution_tranches.json)
- [presentation_analysis.json](../../../data/eth/presentation_analysis.json)
- [etherfi_parameter_events.json](../../../data/eth/etherfi_parameter_events.json)
- [etherfi_verified_metrics.json](../../../data/eth/etherfi_verified_metrics.json)
- [yb_LT_holders_T.json](../../../data/eth/yb_LT_holders_T.json)
- [carry_attribution_states.json](../../../data/eth/carry_attribution_states.json)
- [pilot_details_T.json](../../../data/eth/pilot_details_T.json)
- [carry_economics_chapter.json](../../../data/eth/carry_economics_chapter.json)
