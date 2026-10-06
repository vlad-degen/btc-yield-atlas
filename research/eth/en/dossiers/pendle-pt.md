# ETH fixed yield and Pendle PT

Catalogue captured 3 October 2026. Expiry is checked against T: 2 October, 23:59:59 UTC. Liquidity and annual percentage yield (APY) are current API observations after T.

## What a principal token represents

A principal token (PT) is a claim redeemable at maturity in a specified accounting unit. Buying it below its redemption value creates an implied yield, provided the units and payout rules are verified. The yield-bearing asset is wrapped as standardized yield (SY); a yield token (YT) receives the associated future yield and rewards. PT+YT divides one underlying position rather than doubling deposits.

[Pendle PT mechanics](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT) explain this construction. PT-wstETH redeems in stETH units and PT-weETH in eETH units. Each has a separate conversion rate from its receipt token to ETH.

Every market requires checks of the SY `exchangeRate`, redemption token and PT accounting unit. One PT does not automatically represent one liquid staking token (LST) or one ETH. An API's implied yield cannot replace contract conversion and an executable redemption route.

## Catalogue coverage

The fully paginated official API contains 494 Ethereum markets, 92 Arbitrum, 38 Base and 2 Optimism: 626 unique markets. ETH-family selection uses `accountingAsset.symbol`, rather than finding an arbitrary ETH substring in an underlying description.

There are 126 ETH accounting markets. At T, 122 are expired and four remain unexpired.

| PT | Maturity | Approximate current AMM liquidity | Implied APY |
|---|---|---:|---:|
| superWETH | 26 November 2026 | $373.9K | 4.92% |
| stETH | 30 December 2027 | $5,500.9K | 2.13% |
| SYpufETH | 26 November 2026 | $314.9K | 3.94% |
| mixWETH | 29 October 2026 | $73.9K | 2.02% |

All four are on Ethereum in this catalogue. Their approximately $6.264M combined liquidity is an automated market maker (AMM) pool figure. It is not outstanding PT principal, SY backing or the size of the entire fixed-yield ETH market. Spectra and other venues remain in discovery and require their own contract catalogues.

## Who pays and what changes the result

A PT investor buys the maturity claim at a discount from a seller. Future yield is separated into the YT claim, so the PT holder's return depends on the entry price and final redemption value, rather than a promise of the underlying asset's floating yield. The underlying asset and SY wrapper still determine redemption risk.

Fees, slippage on an early sale, liquidity-provider (LP) inventory and rewards affect investor profit and loss. There is no single verified fee or exit price for every market in the catalogue.

## Expiry does not erase the claim

Expired PT principal is not assigned zero value. Holders can retain unredeemed claims after active AMM yield trading ends. YT, PT and LP positions have different cash flows. Moving to a new maturity is not automatically a net withdrawal from ETH yield.

Most discovered markets are expired. Reconstructing historical market size requires token supply and redeemed principal, not simply the number of active rows in an interface. Comparing a long-duration stETH PT with staking also requires the same ETH unit and holding period.

## What is verified and what remains open

API pagination and expiry coverage are verified. Completeness of the whole ETH fixed-yield market is not. PT and YT supply at T, SY backing, owners and market-wide redemption paths have not been reconstructed.

Data: `pendle_source_coverage.json`, `pendle_eth_market_screen.json`, raw `pendle_markets_*`.


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).
