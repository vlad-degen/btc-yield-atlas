# ETH carry economics: evidence, calculations and review

Prepared 4 October 2026. Financial state remains frozen at T, 2 October 2026, 23:59:59 UTC (Unix 1790985599). The additional RPC requests were captured on 4 October and queried the original verified blocks. Destination reward screens were captured on 3 October and remain separately dated.

The principal finding is that the observed RLUSD loan has a positive spread only when the captured rewards are included. Organic destination yield is 2.9988%, while the annual borrowing-cost equivalent is 4.299900%. The full-parking illustration earns 2.754570% total ETH income after a 0.35% annual NAV fee, or 1.085808% when rewards are removed. Those figures include the historical staking baseline and allocation assumptions. They are not measured Ether.fi returns or a whole-product carry attribution.

## Artifacts and verification

- Machine data: [carry_economics_chapter.json](../../../data/eth/carry_economics_chapter.json).
- Capture script: [carry_economics_collect.py](../../../tools/eth/carry_economics_collect.py). It writes only into the separate [capture manifest](../../../raw/eth/carry-economics-2026-10-04/requests.jsonl).
- Offline builder: [carry_economics_build.py](../../../tools/eth/carry_economics_build.py).
- Independent check script: [carry_economics_verify.py](../../../tools/eth/carry_economics_verify.py), with [machine review](../../../data/eth/carry_economics_review.json).

The independent check passed 914 assertions. These cover token and model bindings, chain blocks, oracle-unit calculations, account debt and health factors, all 60 primary Morpho curve points, all 80 Aave analytical curve points, seven deployed rate-model bytecodes, 68 raw manifest hashes, destination fee getters, four calculator scenarios and every component decomposition. Rebuilding the dataset offline produced identical bytes.

Dataset SHA-256: `eca038f400d12e550b284f6242f5d0ecec21180c8b0ea8ddf13cbf6c397ddfe0`.

The review found and corrected the Ethereum Aave reserve link. It also found that native Optimism USDC has no matched reward-feed observation. That reward value is now null. Its bar contains only the observed organic supply-rate equivalent; unobserved rewards are not represented as an established zero.

## Frozen blocks and source dates

| Chain | Fixed block | Block timestamp | Next block timestamp |
|---|---:|---:|---:|
| ethereum | 26,108,081 | 1790985599 | 1790985611 |
| optimism | 157,693,411 | 1790985599 | 1790985601 |
| base | 52,098,126 | 1790985599 | 1790985601 |
| arbitrum | 511,139,919 | 1790985599 | 1790985600 |

Each retained block is verified as the last block at or before T. The Morpho and Aave captures bind their response sets to these block numbers and hashes. The Arbitrum Morpho deployment is `0x6c247b1f6182318877311737bac0844baa518f5e`; using the Ethereum/Base address on Arbitrum would query the wrong identity.

The original destination screen came from `https://yields.llama.fi/pools`, retrieved at `2026-10-03T13:40:39.080809+00:00`, with SHA-256 `65cd13598ec237eefc25461937e26df5fda1b1791cf1f7bbea8eeccb59caceda`. It is archived in [yield_pools-65cd13598ec237ee.json](../../../raw/eth/2026-10-02/yield_pools-65cd13598ec237ee.json). This feed is a separately dated observation. Its folder name does not turn it into a T-block state.

## Selected borrowing venues

The new panel includes 18 fixed-block Morpho markets: 13 on Ethereum, four on Base and one on Arbitrum. Selection begins with the existing discovery screen, then verifies market parameters, token symbols and decimals, oracle price, IRM, borrow rate and the two tracked Ether.fi accounts at T. It is an observed subset, not an exhaustive universe of ETH-backed dollar borrowing.

Each Morpho market has one specified collateral and one loan asset. Its market-wide debt is therefore linked to that collateral. The reconstructed collateral, LTV and health-factor fields cover only the tracked main Ether.fi vault and LoanManager. An empty tracked-account field means the named accounts had no captured position in that market. It does not mean the market has no borrowers.

The table also includes four Aave V3 USDC reserves. Their variable debt spans every supported collateral. The wstETH settings describe the base collateral configuration, not the share of reserve debt financed by ETH or the terms of every eMode account. Morpho market debt and Aave reserve debt must not be added into an ETH-only debt total.

Annual cost equivalent means `exp(APR) - 1` for a frozen continuously compounded rate. It makes the cost input comparable to the displayed annual destination yield. It does not predict a year of realized borrowing costs.

### Morpho markets at T

| Chain and collateral/loan | Stored market loan units | Borrow APR | Annual cost equivalent | LLTV | Tracked product accrued loan units | Minimum tracked account HF |
|---|---:|---:|---:|---:|---:|---:|
| [ethereum: wstETH/USDT](https://app.morpho.org/ethereum/market/0xe7e9694b754c4d4f7e21faf7223f6fa71abaeb10296a4c43a54a7977149687d2) | 118,984,950.717657 | 3.210803% | 3.262906% | 86.00% | No tracked position | n/a |
| [ethereum: weETH/RLUSD](https://app.morpho.org/ethereum/market/0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4) | 94,535,772.319920 | 4.210021% | 4.299900% | 86.00% | 70,211,978.147154 | 1.267795 |
| [base: WETH/USDC](https://app.morpho.org/base/market/0x8793cf302b8ffd655ab97bd1c695dbd967807e8367a65cb2f4edaf1380ba1bda) | 92,538,071.336872 | 4.722727% | 4.836024% | 86.00% | No tracked position | n/a |
| [ethereum: weETH/USDC](https://app.morpho.org/ethereum/market/0x85252bb8485c99bba46fe149c7dd2aad83672640f53c630890673cf1848ba16e) | 32,028,872.927892 | 4.762917% | 4.878167% | 86.00% | 30,667,083.612682 | 1.644979 |
| [ethereum: weETH/PYUSD](https://app.morpho.org/ethereum/market/0x85d59152eeeab7ca024804895b358868d8dd1e134171be400d7792d5604a212c) | 29,276,681.392138 | 5.828901% | 6.002131% | 86.00% | 0.001636 | 1387.175623 |
| [ethereum: wstETH/USDC](https://app.morpho.org/ethereum/market/0xb323495f7e4148be5643a4ea4a8221eef163e4bccfdedc2a6f4696baacbc86cc) | 29,064,019.008887 | 4.881741% | 5.002861% | 86.00% | No tracked position | n/a |
| [base: cbETH/USDC](https://app.morpho.org/base/market/0x0ca10126f6c94cbd9cf0a48cc9516ae5e3dec5aa68303e6d988ee37c5149bf0d) | 14,004,549.989622 | 4.770084% | 4.885683% | 77.00% | No tracked position | n/a |
| [ethereum: wstETH/USDC](https://app.morpho.org/ethereum/market/0x7e585a933ffe8443c371b4f8cfeb4430f5f6a14c2f32a898c26662c67a1cb8b8) | 11,351,607.988135 | 4.750790% | 4.865449% | 86.00% | No tracked position | n/a |
| [ethereum: OETH/USDC](https://app.morpho.org/ethereum/market/0xb8fef900b383db2dbbf4458c7f46acf5b140f26d603a6d1829963f241b82510e) | 9,481,389.861378 | 7.640608% | 7.940081% | 86.00% | No tracked position | n/a |
| [ethereum: WETH/USDC](https://app.morpho.org/ethereum/market/0x94b823e6bd8ea533b4e33fbc307faea0b307301bc48763acc4d4aa4def7636cd) | 8,454,046.799640 | 4.556565% | 4.661972% | 86.00% | No tracked position | n/a |
| [ethereum: weETH/USDT](https://app.morpho.org/ethereum/market/0xa6a4c1f15490a1ff39d9de3a366b408dd5647a436d8b179726d3e0562aff1292) | 4,293,069.569354 | 3.254999% | 3.308554% | 86.00% | No tracked position | n/a |
| [ethereum: rETH/USDC](https://app.morpho.org/ethereum/market/0x0a15460ad263c2186fe0b5df20a8cf71d55f3cfa06de15edcf6138f6b8edd8bf) | 2,815,543.873939 | 4.612469% | 4.720498% | 86.00% | No tracked position | n/a |
| [ethereum: wstETH/USDT](https://app.morpho.org/ethereum/market/0x6a57d77b9a173c5ed10d432e7009dd1ee9a97fac62a7bc970b4bd715e2fff5c8) | 2,522,766.907049 | 3.219118% | 3.271492% | 86.00% | No tracked position | n/a |
| [base: wstETH/USDC](https://app.morpho.org/base/market/0x13c42741a359ac4a8aa8287d2be109dcf28344484f91185f9a79bd5a805a55ae) | 2,107,196.208578 | 4.769152% | 4.884705% | 86.00% | No tracked position | n/a |
| [ethereum: weETH/USDT](https://app.morpho.org/ethereum/market/0xc2c53d2b868e163da71de14a5113cc2743fc9b5ad7488334720ed2846566a8f6) | 1,879,203.240783 | 3.328230% | 3.384236% | 86.00% | No tracked position | n/a |
| [base: cbETH/USDC](https://app.morpho.org/base/market/0x1c21c59df9db44bf6f645d854ee710a8ca17b479451447e9f56758aee10a2fad) | 1,516,335.820469 | 3.390609% | 3.448745% | 86.00% | No tracked position | n/a |
| [ethereum: wstETH/RLUSD](https://app.morpho.org/ethereum/market/0x88abdf8693e663144c3544b9442e9b04520016d6ebc57aa76424c00ab1683c9d) | 1,266,285.391712 | 6.606318% | 6.829421% | 86.00% | No tracked position | n/a |
| [arbitrum: wstETH/USDC](https://app.morpho.org/arbitrum/market/0x33e0c8ab132390822b07e5dc95033cf250c963153320b7ffca73220664da2ea0) | 1,010,896.357415 | 2.927233% | 2.970497% | 86.00% | No tracked position | n/a |

LLTV means the liquidation loan-to-value threshold. Health factor (HF) is threshold-adjusted oracle collateral divided by debt. A value below 1 makes an account eligible for liquidation. The Morpho market debt and utilization columns reflect stored balances before the pending interest interval is projected. Tracked product debt and HF project interest to the T block using the primary model quote. The weETH/PYUSD position is a tiny residual, about 0.001636 PYUSD, rather than evidence of a material active carry allocation.

### Aave USDC reserves at T

| Chain | Variable USDC debt | Physical USDC cash | Virtual USDC cash | Borrow APR | Annual cost equivalent | Supply APR | Base wstETH LTV / threshold | Base bonus |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| [ethereum](https://app.aave.com/reserve-overview/?underlyingAsset=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&marketName=proto_mainnet_v3) | 2,246,615,640.292179 | 6,325,453.553238 | 6,293,707.259601 | 13.934401% | 14.951948% | 12.505927% | 78.50% / 81.00% | 6.00% |
| [base](https://app.aave.com/reserve-overview/?underlyingAsset=0x833589fcd6edb6e08f4c7c32d4f71b54bda02913&marketName=proto_base_v3) | 161,645,492.952729 | 19,967,099.209728 | 19,966,818.013945 | 4.648081% | 4.757797% | 3.723355% | 75.00% / 79.00% | 6.00% |
| [arbitrum](https://app.aave.com/reserve-overview/?underlyingAsset=0xaf88d065e77c8cc2239327c5edb3a432268e5831&marketName=proto_arbitrum_v3) | 158,341,978.474191 | 20,260,421.290913 | 20,260,380.344298 | 3.940273% | 4.018932% | 3.143957% | 75.00% / 79.00% | 7.20% |
| [optimism](https://app.aave.com/reserve-overview/?underlyingAsset=0x0b2c639c533813f4aa9d7837caf62653d097ff85&marketName=proto_optimism_v3) | 9,295,304.707132 | 1,500,931.905257 | 1,500,930.569408 | 3.826562% | 3.900718% | 2.964933% | 75.00% / 79.00% | 7.20% |

Ethereum USDC is the clear high-cost case in this snapshot: 13.934401% variable APR and about 6.325m USDC of physical reserve cash against 2.2466bn USDC of variable debt. Large lender claims do not establish cash for a deleveraging batch. Physical cash is a balance diagnostic, not a guaranteed borrow or exit capacity. Virtual cash is separately captured because the verified Aave strategy can use it in rate calculations. Debt, cash and the stored rate do not have to reconstruct exactly the same instantaneous utilization after every accrued operation.

Aave base wstETH thresholds and bonuses are measured at T. Account-specific eMode, collateral flags, caps, borrowing eligibility and actual liquidation close-factor policy are not reconstructed for a proposed new account. The calculator therefore labels its 50% close factor and 5% bonus as illustrative. They are not asserted as Aave V4 policy, Aave V3 policy or Morpho execution rules.

## Rate models and utilization curves

IRM means interest-rate model. Every market is bound to its actual rate-model address. All seven deployed model bytecodes match the verified source bytecode exactly at the original block. This proves the code identity used for the rate calculations. It does not prove whole-vault solvency, a future rate or an executable withdrawal.

| Chain | Model | Address |
|---|---|---|
| ethereum | AdaptiveCurveIrm | `0x870ac11d48b15db9a138cf899d20f13f79ba00bc` |
| ethereum | DefaultReserveInterestRateStrategyV2 | `0x9ec6f08190dea04a54f8afc53db96134e5e3fdfb` |
| base | AdaptiveCurveIrm | `0x46415998764c29ab2a25cbea6254146d50d22687` |
| base | DefaultReserveInterestRateStrategyV2 | `0x86ab1c62a8bf868e1b3e1ab87d587aba6fbcbdc5` |
| arbitrum | AdaptiveCurveIrm | `0x66f30587fb8d4206918deb78eca7d5ebbafd06da` |
| arbitrum | DefaultReserveInterestRateStrategyV2 | `0x429f16dba3b9e1900087cbaa7b50d38bc60fb73f` |
| optimism | DefaultReserveInterestRateStrategyV2 | `0x9359282735496463131139875849d5302fb4bed1` |

### Morpho AdaptiveCurveIrm

The verified model targets 90% utilization and has curve steepness 4. At a frozen learned target rate, zero utilization produces one quarter of that target rate, 90% produces the target rate and full utilization produces four times the target rate. The learned target rate is stored separately for every market. It adapts over elapsed time rather than remaining a fixed governance-selected slope.

The panel contains primary `borrowRateView` calls at 20 utilization points for three Ethereum markets: wstETH/USDT, weETH/RLUSD and weETH/USDC. For these hypothetical curve calls, `lastUpdate` is set to the T block timestamp. This freezes pending adaptation and isolates the utilization curve around the stored target rate. These curve points are not the actual borrower quotes for an untouched interval.

| Curve market | Stored target APR at T | Primary points |
|---|---:|---:|
| [wstETH/USDT](https://app.morpho.org/ethereum/market/0xe7e9694b754c4d4f7e21faf7223f6fa71abaeb10296a4c43a54a7977149687d2) | 3.603336% | 20 |
| [weETH/RLUSD](https://app.morpho.org/ethereum/market/0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4) | 4.270212% | 20 |
| [weETH/USDC](https://app.morpho.org/ethereum/market/0x85252bb8485c99bba46fe149c7dd2aad83672640f53c630890673cf1848ba16e) | 4.769216% | 20 |

The actual market `borrowRateView` quote has another important meaning: the verified implementation returns an average over the pending interest-accrual interval, including model adaptation. The quoted weETH/RLUSD interval is 21,120 seconds. The 4.299900% annual cost equivalent is therefore a conversion of that fixed-block average quote. It is not an independently measured instantaneous forward funding offer. All 60 curve calls were independently recomputed using the signed integer arithmetic and matched exactly.

Source: [Morpho IRM documentation](https://docs.morpho.org/developers/contracts/irm/) and the archived deployed contract sources identified in the JSON. The code constants, average-rate calculation and immutable MORPHO binding were checked rather than inferred from protocol branding.

### Aave DefaultReserveInterestRateStrategyV2

The four USDC reserves use the verified two-segment model. Below optimal utilization, APR is `base + slope1 × utilization / optimal`. Above it, APR is `base + slope1 + slope2 × (utilization - optimal) / (1 - optimal)`. The optimal point and slopes were called at T for the actual USDC token in each pool. Independent base/slope getters agree with the packed parameter getter.

| Chain | Optimal utilization | Base APR | Slope 1 | Slope 2 |
|---|---:|---:|---:|---:|
| ethereum | 94.00% | 0.00% | 4.40% | 10.00% |
| base | 90.00% | 0.00% | 4.70% | 10.00% |
| arbitrum | 90.00% | 0.00% | 4.00% | 10.00% |
| optimism | 90.00% | 0.00% | 4.00% | 10.00% |

The 20 plotted points for each Aave reserve are analytical calculations from the verified T parameters. They are not fabricated historical observations or claims that governance will preserve those slopes. All 80 APR and annual-equivalent points passed independent arithmetic checks.

## Destination yields, rewards and fees

The destination comparison separates organic income from external incentives. Organic means the reported base yield from lending or the stored Aave supply rate. It is not a guarantee that every borrower or underlying credit layer has been independently reconciled. A reward token identifies the payout currency. It does not establish who financed the campaign.

| Destination | Organic annual yield | Reported reward annual yield | Observed total before outer NAV fee | Destination performance fee at T | Evidence boundary |
|---|---:|---:|---:|---:|---|
| [Aave V3 USDC (Ethereum)](https://app.aave.com/reserve-overview/?underlyingAsset=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&marketName=proto_mainnet_v3) | 13.321561% | 0.000000% | 13.321561% | Reserve economics in supply quote | T organic quote; 3 Oct feed reports no reward component |
| [Aave V3 USDC (Base)](https://app.aave.com/reserve-overview/?underlyingAsset=0x833589fcd6edb6e08f4c7c32d4f71b54bda02913&marketName=proto_base_v3) | 3.793540% | 0.000000% | 3.793540% | Reserve economics in supply quote | T organic quote; 3 Oct feed reports no reward component |
| [Aave V3 USDC (Arbitrum)](https://app.aave.com/reserve-overview/?underlyingAsset=0xaf88d065e77c8cc2239327c5edb3a432268e5831&marketName=proto_arbitrum_v3) | 3.193901% | 0.000000% | 3.193901% | Reserve economics in supply quote | T organic quote; 3 Oct feed reports no reward component |
| [Aave V3 USDC (Optimism)](https://app.aave.com/reserve-overview/?underlyingAsset=0x0b2c639c533813f4aa9d7837caf62653d097ff85&marketName=proto_optimism_v3) | 3.009325% | Unknown, no matched feed | 3.009325% | Reserve economics in supply quote | T organic quote only; reward coverage missing |
| [Sentora RLUSD Main V2](https://app.morpho.org/ethereum/vault/0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf) | 2.998800% | 2.592980% | 5.591780% | 10.00% | 3 Oct captured base/reward split |
| [Sentora PRIME Main V2](https://app.morpho.org/ethereum/vault/0xc21b08c16458202593d4d9b26b9984ee67b38bbd) | 4.487680% | 2.211940% | 6.699620% | 15.00% | 3 Oct captured base/reward split |

The RLUSD and PRIME/PYUSD performance-fee getters are 10% and 15%, respectively, with zero destination management fees at T. They are different contracts and must not be collapsed into a single 10% assumption. The displayed base yield uses the captured published figure. The calculator does not apply another performance-fee haircut to that same figure. A reconstruction of gross borrower interest, fees accrued in the destination and net realized distributions would require its own accounting.

The separate Ethereum ETH-vault management fee is 0.35% per year of NAV at T. The calculator charges 0.0035 of starting NAV in its frozen annual illustration. It is not 0.35% of profit. Fee rates on another chain, historical fees and fee compounding are separate questions.

RLUSD reward asset: `0x8292bb45bf1ee4d140127049757c2e0ff06317ed`. PYUSD reward asset: `0x6c3ea9036406852006290770bedfcaba0e23a0e8`. Neither token address proves that Ripple, PayPal or Paxos funded the captured program. Funding wallet, program creator, budget, expiry, renewal and whether rewards economically belong to Liquid ETH holders remain open. [Morpho rewards documentation](https://docs.morpho.org/learn/concepts/rewards/) describes the distribution mechanism but does not resolve these particular campaigns.

## Worked RLUSD leg: what is measured

Observed product: Ether.fi Liquid ETH. Main vault: `0xf0bb20865277abd641a307ece5ee04e79073416c`. Controlled LoanManager: `0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3`. The specific weETH/RLUSD market is `0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4`. Destination: `0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf`.

| Measured or derived item | Value | Basis |
|---|---:|---|
| Combined collateral | 37,046.188203 weETH | Primary account positions |
| Oracle collateral value | 109,097,756.801714 RLUSD units | Collateral amount × market oracle |
| Stored combined debt | 70,209,998.550567 RLUSD | Shares converted with stored debt and virtual assets/shares |
| Accrued combined debt at T | 70,211,978.147154 RLUSD | Verified Taylor interest and shares conversion |
| RLUSD destination book claim | 55,104,709.535318 RLUSD | Fixed-block ERC4626 convertToAssets |
| Maximum arithmetic matched notional | 55,104,709.535318 RLUSD | Minimum of held claim and combined loan; not traced funds |

The held claim and the debt coexist at T. That does not trace the dollars from these loans into the destination. Other loan balances and other dollar assets are outside this worked income example. The claim is valued in its own RLUSD asset units; the partial dollar balance sheet assumes $1 per RLUSD. Collateral is valued by the actual Morpho oracle in loan units. Neither convention establishes an executable spot sale or redemption price.

### Accounts liquidate separately

| Account | weETH collateral | Oracle RLUSD collateral | Accrued RLUSD debt | LTV | HF | Oracle collateral markdown to threshold |
|---|---:|---:|---:|---:|---:|---:|
| Liquid ETH main vault | 17,982.641180 | 52,957,292.214026 | 35,923,215.502664 | 67.834313% | 1.267794953 | 21.122892% |
| Controlled LoanManager | 19,063.547023 | 56,140,464.587688 | 34,288,762.644490 | 61.076735% | 1.408064795 | 28.980541% |

The combined accounting LTV is 64.356940%. Applying an 86% threshold to that combined value gives a hypothetical single-account HF of 1.336297. The weaker actual account is the main vault at HF 1.267795. It cannot use the LoanManager's surplus collateral automatically merely because the same product controls both accounts. The market table consequently reports minimum account HF, retaining the aggregate value/loan ratio separately.

The markdown calculation holds debt, threshold and every other collateral price constant. It is an oracle collateral shock bound in the one-account model. It is not a forecast of the ETH spot drop that will trigger liquidation after evolving interest, issuer conversion and oracle changes.

### Accrued debt agrees with the original primary getter

Stored market balances can lag the current block. The exact debt projection follows the verified Morpho implementation:

```text
elapsed = T_block_timestamp - market.lastUpdate
first = ratePerSecondWAD × elapsed
second = floor(first² / (2 × 10^18))
third = floor(second × first / (3 × 10^18))
interest = floor(totalBorrowAssets × (first + second + third) / 10^18)
accountDebtUp = ceil(borrowShares × (totalBorrowAssets + interest + 1)
                     / (totalBorrowShares + 10^6))
```

The exact LoanManager result is `34288762644489622798767210` smallest RLUSD units, or 34,288,762.644489622798767210 RLUSD. It matches the original fixed-block `getBorrow()` result exactly, and the independently calculated HF matches `getHealthFactor()`. The old partial portfolio balance sheet was not overwritten; its stored main-Morpho debt convention remains disclosed there.

For LLTV 86%, the verified Morpho liquidation incentive factor is `min(1.15, 1 / (1 - 0.3 × (1 - 0.86)))`, giving a 4.384134% bonus. Morpho's actual seize/repay arithmetic is separate from the calculator's 50% close and 5% bonus illustration.

### Matched-notional income is still a scenario

Applying the captured spread to the maximum matched notional gives about 711,886.911 RLUSD per year including rewards, or -716,967.187 RLUSD without them. These are annual arithmetic illustrations. They are not paid income, whole-vault income, or an allocation of every loan dollar. The JSON marks `not_measured_income=true`, `source_of_parked_funds_traced=false` and `whole_product_carry_return=null`.

The earlier allocation analysis identifies approximately 8.709m RLUSD of indirect self-credit notional. This is a diagnostic of the product holding a vault claim that helps fund its own debt, not an asset or income to add again. Recovering some interest paid by the same product is a recycling effect rather than independent external demand.

The full product publishes approximately $472.684m of book NAV under the disclosed nearest-quote convention. Its partial balance reconstruction has approximately $12.453m unresolved residual. Mixed oracle and market marks, incomplete positions and nested claims keep this from proving either a deficit or complete backing. The worked leg does not resolve that residual.

## Seven-input calculator and four presets

The annual staking baseline is the 30-day historical stETH conversion return annualized at T: 2.273156%. It uses the interval from 1788393599 to 1790985599. The comparison weETH baseline is 2.354830%. The calculator uses stETH as a clear benchmark, not a promised future return or a direct assertion that all product collateral earns that exact rate.

Inputs are fractions in JSON. The operator fee is an annual fee on starting NAV. The model uses constant ETH/USD and stablecoin value, assigns the staking baseline to all initial ETH, and assumes all modeled debt is parked at the destination rate. Changes in prices, variable rates, eligibility, swaps, queue settlement, taxes, execution costs and fee compounding are outside this one-period illustration.

```text
modeledDebt / initialNAV = collateral_share × LTV
annualETHIncome = stakingBaseline
                + collateral_share × LTV × (parkingYield - borrowingCost)
                - annualNAVFee
annualETHIncomeWithoutRewards = stakingBaseline
                + collateral_share × LTV
                  × (parkingYield × (1 - rewardShare) - borrowingCost)
                - annualNAVFee
hypotheticalAccountHF = collateralThreshold / LTV
collateralMarkdownToLiquidation = 1 - LTV / collateralThreshold
```

| Preset | LTV | Collateral share | Threshold | Borrow annual cost | Parking annual yield | Reward share of parking yield | Annual NAV fee | Total ETH income | Without rewards |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Observed RLUSD loan, full parking scenario | 64.356940% | 100.000000% | 86.000000% | 4.299900% | 5.591780% | 46.371281% | 0.350000% | 2.754570% | 1.085808% |
| Ethereum USDC reserve, 65% LTV scenario | 65.000000% | 100.000000% | 81.000000% | 14.951948% | 13.321561% | 0.000000% | 0.350000% | 0.863404% | 0.863404% |
| RLUSD leg with rewards removed | 64.356940% | 100.000000% | 86.000000% | 4.299900% | 2.998800% | 0.000000% | 0.350000% | 1.085808% | 1.085808% |
| RLUSD loan cost increases 3 percentage points | 64.356940% | 100.000000% | 86.000000% | 7.299900% | 5.591780% | 46.371281% | 0.350000% | 0.823862% | -0.844900% |

The first preset measures aggregated LTV, LLTV, borrowing quote, current Ethereum fee and the separately dated parking/reward split. Its 100% collateral share and full-debt parking are assumptions. Its HF is a hypothetical single account at that LTV. Actual measured account HFs remain in the worked ledger.

The Ethereum USDC preset uses actual T borrow and supply quotes and the base wstETH threshold. Its 65% LTV is illustrative, as are the collateral allocation and ability to borrow and deposit at the proposed size. It is a same-reserve parking comparison, not a recommended trade. Organic borrowing cost exceeds organic supply yield in that example.

The third preset removes all observed RLUSD rewards. The fourth adds exactly 3 percentage points to annual borrowing cost; it is a 300 bp stress, not a forecast or captured future quote. Removing rewards as well in the fourth preset gives -0.844900% total ETH income after the NAV fee at constant prices.

For the first preset, the carry uplift before the outer fee is +0.831415 percentage points including rewards, or -0.837348 percentage points without them. The staking baseline explains why the no-reward total remains positive. Showing a positive total without this split would conceal negative marginal carry economics.

## Four Playbook tables

The arrays are populated in `playbook.scenarios`, `playbook.reward_payers`, `playbook.rules` and `playbook.partners`. They contain four, six, seven and six rows, respectively. They are product-design and diligence choices tied to observed evidence. They do not establish financing offers, committed subsidy budgets or final partner selection.

### Scenarios

The four presets above preserve which fields are measured and which are illustrative. Their JSON contains `observed_fields`, `illustrative_fields`, `basis`, the seven `inputs` and complete `result` values. This lets the presentation explain the scenario rather than presenting a simulated return as a protocol quote.

### Who pays

| Income source | Payer or evidence boundary |
|---|---|
| Staking baseline | Ethereum issuance and block execution income allocated by the staking issuer; historical conversion is measured, future rate is unknown. |
| RLUSD organic lending | Borrowers in the destination allocation markets; some linked borrowing belongs to the same product, so recovered own-loan interest is recycling. |
| RLUSD incentives | Campaign funder unknown; RLUSD reward-token identity does not establish Ripple financing. |
| PYUSD incentives | Campaign funder unknown; PYUSD identity does not establish PayPal/Paxos financing. |
| Aave organic supply income | Reserve borrowers pay interest after reserve-factor economics; rates depend on demand and liquidity. |
| PRIME underlying credit | Disclosed home-equity credit cash flows; underlying loans, recovery rights and complete cash-flow accounting are not reconstructed here. |

Primary context: [Morpho's Sentora case study](https://morpho.org/stories/sentora), [Hastra PRIME disclosure](https://help.hastra.io/24d233935654815fb088ffef227d7f5a) and [Morpho rewards](https://docs.morpho.org/learn/concepts/rewards/). The case study establishes an integration and curation context, not the funding wallet or economic owner of these captured rewards. Current case-study financial figures are not substituted into T.

### Limits and observed risks

| Proposed rule | What is observed or still needs proof |
|---|---|
| Require a positive organic marginal spread before scaling unfunded carry: Parking yield without subsidies must exceed borrowing cost and the marginal execution/manager charge. A renewal budget is a separate decision. | RLUSD base APY 2.9988% versus borrowing annual equivalent 4.2999%; removing rewards makes the modeled carry uplift negative. Status: Product-design rule, not an observed contractual limit. |
| Use each borrowing account health factor: Illustrative operating floor HF 1.25 with additional collateral/oracle stress tests; liquidation remains the venue threshold. | The observed main RLUSD account HF is 1.267795 and its LoanManager HF is 1.408065. The Liquid ETH Aave ETH loop has HF 1.027082, a different same-asset risk. Aggregating account headroom conceals the weaker account. Status: Illustrative operating proposal, not a protocol requirement or calibrated loss guarantee. |
| Test borrowing-cost and reward-budget shocks together: Remove 100% of captured external rewards and add 300 bp to the borrowing annual-cost input. Preserve a separate unstressed benchmark. | With both changes, the RLUSD full-parking illustration has negative total ETH income after the outer NAV fee even at constant ETH/USD. Status: Explicit scenario inputs, not predicted market moves. |
| Match withdrawal promises to repayable liquidity: Budget reserve cash, destination redemption capacity and collateral exit separately. No fixed universal exit SLA is asserted. | Ethereum Aave USDC has $6.325m physical cash against $2.2466bn variable debt at T. Higher total deposits do not prove enough dollars for a deleveraging batch. Status: Operational funding requirement; capacities and account eligibility need execution testing. |
| Expose recycled self-credit: Count a held vault claim once, and show own-borrower interest recovery separately from external interest and subsidy income. | Liquid ETH holds 55.105m RLUSD in the vault that supplies its weETH/RLUSD borrowing market. The earlier fixed-block allocation diagnostic identifies about 8.709m RLUSD of indirect self-credit notional. Status: Accounting rule, not a proven safe concentration cap. |
| Apply fees at the correct layer: Use 0.35% annual outer Ethereum NAV fee for this scenario. Do not apply destination performance fees twice to a reported net destination base yield. | RLUSD destination performanceFee is 10%; the PRIME/PYUSD destination is 15%. These are different from the ETH manager NAV fee. Status: Observed Ethereum fee policy at T plus an annual fee scenario; other chains can differ. |
| Treat price, bridge and oracle marks as separate risks: Stress stablecoin exchange value and collateral-oracle discounts separately; preserve actual oracle units beside dollar assumptions. | The same market can have a $1 loan-unit convention, a collateral oracle and an ETH quote with a different timestamp. A positive modeled spread does not cover a depeg or recovery loss. Status: Scenario accounting requirement; no stablecoin parity or reserve audit claimed. |

The proposed HF 1.25 floor is an illustrative operational choice requiring calibration. It is not a protocol limit, risk-free point or statistical loss guarantee. The same-asset Aave loop HF 1.027082 refers to another measured strategy, not the stablecoin carry loan. That distinction stays explicit.

### Partner roles

| Role | Initial diligence candidate | Basis and remaining question |
|---|---|
| Stablecoin funding and any subsidy budget | RLUSD and PYUSD issuer/ecosystem teams, with Sentora as an existing integration lead | Measured matching-currency loan and destination legs and documented issuer-vault relationships. Verify: Committed liquidity, budget funding address, duration, renewal rights, eligible holder, redemption and stablecoin conversion route. Primary case study links Sentora with both stablecoin ecosystems. It does not establish a funded offer for our product or identify the captured campaigns funders. |
| Market and vault curation | Sentora; compare alternatives against the same risk and reporting requirements | Observed RLUSD and PRIME vault allocations and documented curation role. Verify: Market caps, collateral concentration, reallocators, fee rights, oracle policy, withdrawal priority and who bears losses. The observed destination vaults give a concrete diligence starting point, not proof that their present allocation is suitable. |
| ETH vault infrastructure | Veda as the observed Ether.fi implementation reference | Existing BoringVault, Accountant, Manager, Teller and queue contracts in the ETH product. Verify: Exact selectors/roles, fee permissions, rate publishing, cross-chain accounting, solver routes and change delays. The existing deployment is measurable. Its selected permissions are verified, but economic backing and every exit path are not fully reconciled. |
| Strategy operation and monitoring | Nonce as the observed Liquid ETH strategy-provider reference | Captured product interface identifies the provider; measured account and portfolio mechanics supply diligence cases. Verify: Debt hedge, keeper uptime, authority limits, withdrawal rehearsals, oracle/bridge incident response, reporting of self-credit and realized rewards. Provider identification is a separately dated UI statement, not a complete fixed-block map of every operator permission. |
| Distribution | Ether.fi ETH-holder interface; evaluate exchange/broker channels with an ETH-specific business case | An existing ETH yield product distributes staking, looping and carry strategies through one interface. Verify: Deposit ownership, rewards ownership, exit communications, custody terms, commercial economics and support responsibility. BTC distribution success cannot be assumed to transfer to ETH. The present dataset does not measure acquisition costs or prove a channel wins on net yield. |
| Independent verification and liquidity counterparties | Separate contract/accounting reviewer and repay-liquidity providers selected against the actual contracts and asset routes | The incomplete portfolio reconciliation and variable reserve cash create distinct review and execution tasks. Verify: Independent claim-graph reconciliation, simulation at the proposed size, price-impact bounds, executable repayment and queue settlement. Seven rate-model bytecodes match verified source at T. That proves model identity, not whole-product solvency or an executable exit. |

Veda and Nonce identification uses the observed deployment and separately dated Ether.fi interface. It is not a complete T map of operator permissions. Stablecoin teams and Sentora are concrete diligence starting points because the relevant assets and integrations are observed. A partner relationship, funded offer and return premium for our own proposed product have not been established.

## Remaining evidence boundaries

- No global ETH-carry capital total is inferred from all protocol borrowing. Selected debt may fund leverage, hedging, liquidity or unrelated spending.
- Aave reserve debt is not ETH-specific. Morpho selected-market debt is ETH-collateral-linked, but its market-wide collateral quantities and every borrower strategy are not reconstructed.
- The worked RLUSD destination balance is a book claim. The source of its dollars is not traced to the particular debt accounts.
- Captured APY components are rate observations, not realized reward receipts. Campaign funders, budgets, expiry, renewal, claim eligibility and holder ownership remain unresolved.
- Rate-model identity is verified. Variable quotes, governance changes, future demand and adaptive target rates remain uncertain.
- Contract oracle value, nominal $1 loan currency, market value and executable recovery are separate marks. Constant prices are a scenario assumption.
- Destination cash and Aave physical/virtual cash are not guaranteed withdrawal or deposit capacity at a proposed trade size. No exit was executed and no wallet transaction was submitted.
- Main vault and LoanManager liquidate separately. Combined LTV is useful for accounting but cannot transfer collateral headroom between them.
- The illustration does not allocate all Ether.fi fees, credit exposure, other carry legs, ETH loops, LP claims, cross-chain balances or realized income. The original financial snapshot and partial-balance accounting were preserved.
