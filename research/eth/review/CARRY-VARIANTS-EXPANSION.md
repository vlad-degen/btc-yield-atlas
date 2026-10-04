# The extra funding layer inside ETH carry

Financial snapshot: 2 October 2026, 23:59:59 UTC. Public discovery and contract-source review: 4 October 2026. This article supplements the five deep product chapters. It does not present a complete market census.

## Follow the liabilities as well as the investment

ETH collateral can fund a dollar lending share, a savings asset, a senior tranche or a stable pool. The difference matters because each destination has a different payer and exit. A second loan against the dollar investment adds another liability and another liquidation test. Minting BOLD through a collateralized debt position also has different mechanics from borrowing USDC from a lender.

The strongest comparison follows actual collateral, debt, destination and cash flows. A product name or permitted strategy is useful discovery evidence, but neither establishes current capital deployed in carry.

## Reservoir shows two separate funding layers

The Reservoir ETH Yield vault at `0xf6cd9e8415162c8fb3c52676c7ca68812a34f76e` holds **21.220601 WETH** as Aave collateral and has **36,789.61 USDC** of variable debt at T. Its Aave account health factor is **1.2766**. This ratio belongs to that account, not to a consolidated portfolio buffer.

Separately, its main Morpho wsrUSD/USDC position pledges **41,588.673512 wsrUSD** and owes **11,021.11 USDC** after pending interest accrual. The dollar savings share is collateral for this second loan. The two observed loan positions establish the nested structure; they do not by themselves match every borrowed dollar to its historical deposit transaction.

The wsrUSD contract returns an annual growth factor close to 1.06. Subtracting initial principal gives a configured APY of **6.00%**. The source code returns this factor even though a nearby comment calls it APY. Treating the raw value as a 106% yield would be an accounting error.

At T, the outer Aave USDC borrowing quote is **13.93% APR**. The examined inner Morpho loan quote is **5.54% APR**. A frozen-rate comparison between the savings APY and the corresponding compounded loan cost gives **-8.95%** for the outer layer and **0.31%** for the inner layer. These are conditional rate differences, not realized profit or whole-product APY. They omit rewards, manager charges, ETH collateral income, swaps and imperfect funding linkage.

The product's book NAV is **$62,949.86** at T. Its largest measured completed-month endpoint is **$15,910,980.19** in **2025-10**. That endpoint is not an all-time peak. Current capital is small, but a selected historical loan checkpoint shows that the route once financed a material investment.

At the **31 October 2025** checkpoint, the Aave account reports **$10,347,894.69** of debt against about **$15.751 million** of collateral. The separate Morpho srUSD/USDC position has **$90,262,051.67** of stored USDC debt against **91.0179 million srUSD**. The product book at that date is about **$15.911 million**. The much larger nested loan balances are gross financing, not additional investor equity. Morpho values exclude pending interest since the market's last update; Aave uses its account base currency. This is a dated position comparison, not a continuous allocation history or a realized-income ledger.

## TAU's carry route was almost fully unwound at T

TAU InfiniFi ETH Carry at `0xc50b2d51fd1e2ac67a9c09eaf63c24ea2465c64b` has a funded wstETH vault and two examined Morpho routes: wstETH/USDC and siUSD/USDC. Together their accrued USDC debt is **0.022132 USDC** at T. The product therefore has a carry design, but no material dollar loan in these observed positions at that date.

Its **$219,395.85** book NAV should not be counted as active carry allocation. The largest sampled monthly endpoint is **$853,559.56** in **2026-01**.

At the **31 January 2026** checkpoint, the outer Morpho position pledges **284.995723 wstETH** and has **505,581.226013 USDC** of stored debt. The inner position pledges **2,885,323.356786 siUSD** and has **2,531,950.176256 USDC** of stored debt. These actual balances establish a materially funded nested route at that date. Both loans were already dust at the **30 September 2026** checkpoint. Stored debt excludes pending market accrual, and historical financing is not the same as historical profit.

## Fees and exits are part of the funding structure

At T, TAU configures a **0.8% annual management rate** and **10% performance rate**. Reservoir configures **1% annual management** and **10% performance**. Both withdrawal managers report zero request and withdrawal fee rates. These configured rates have different bases and should not be deducted again from returns already measured through net share value.

Neither vault has instant market-withdrawal fuses configured at T. Their request windows are **1 day for TAU** and **8 days for Reservoir**. These windows describe request expiry. A qualifying release must occur after a request, and the withdrawal must remain inside its window. They are not fixed waiting periods or promised payout deadlines. Unallocated wallet liquidity is a separate withdrawal path.

## Concrete's book identifies a manager claim, not a loan attribution

Concrete wstETH Plus at `0xd57588c73715b65e0ead36ae06c15644169501b7` has **$121,077,070.78** of book NAV. Essentially its full allocation is assigned to MultisigStrategy `0x50a7510e73d79d60823dcac50e6b2c62e89ed82b`. The verified implementation exposes allocated-value accounting, an accounting-validity period, a cooldown and accounting-change limits.

This gives a concrete product control and accounting map. It does not show which dollar loan finances this product, what investment rights its shared Safe controls, or what arbitrage profit it has actually paid. Debt shared with another Concrete product cannot be allocated using relative book NAV. The product remains an E4 candidate, with carry capital and realized carry income left unmeasured.

The strategy's last accounting update at T is **2026-02-09T15:03:59Z**, about **235.37 days** earlier. Its configured validity period is **2,628,000,000 seconds**, about **83.3 years**. The update cooldown is **3,600 seconds**, and the maximum accounting-change threshold is **100 basis points**. The two proxy implementation addresses were also checked at T. A long validity setting and a permissive accounting withdrawal allowance do not establish fresh valuation or payout inventory.

## The two Midas cases need visible mark ages

The official registry identifies mRe7ETH on Optimism and mHyperETH on Ethereum, including token, issuance, redemption and ETH NAV oracle addresses. At T, token supply multiplied by the published mark gives **4,843.30 ETH** for mRe7ETH and **12.95 ETH** for mHyperETH. These are published-mark book amounts.

The marks were **8.28 days** and **67.59 days** old at T, respectively. Oracle decimals were read at the same fixed block and agree with the redemption feed conversion. Fresh token supply does not make a stale portfolio mark current. The 4 October catalogue is separately dated discovery and should not replace the frozen amounts.

mRe7ETH's configured instant redemption fee is **0.5%** at T, using the verified 10,000-point denominator. mHyperETH's configured instant fee is **0%**. These fields do not establish available instant liquidity or the complete investor charge: token-specific fees, exemptions, slippage and external legal manager charges remain separate.

Both are ETH-denominated market-neutral manager products. Neither denomination nor market neutrality proves an ETH collateral loan invested in dollars. Their actual collateral, dollar debt, portfolio wallets and realized funding economics remain unclassified. The catalogue's `maxUsd` and `maxNative` fields are not treated as historical peaks because their meaning is unverified.

## Keep fixed maturity and external arbitrage claims bounded

Rocksolid's dated 17-24 August report discloses a $2m Spectra allocation. It does not establish a particular principal token, maturity or T position. The presentation can explain maturity mismatch, but should not manufacture a verified fixed-rate sleeve from a venue name.

Concrete Delta weETH discloses dollar-neutral arbitrage. Public shared-wallet positions do not close product-level funding or actual external payout attribution. A basis trade, exchange funding trade and private arbitrage claim should not be merged simply because each is described as market neutral.

The official Yearn forum documents the original yETH route through Maker-created DAI deployed as working capital in September 2020. It does not identify the existing investment instrument. It is a historical precedent, not current market capital. Proposed UNI, COMP or other future strategies in the forum are excluded from deployed route examples.

## Presentation-ready conclusions

1. Split direct credit carry, nested savings leverage, senior tranches, minted-stablecoin LP carry and external arbitrage by their actual payer and exit.
2. Label design separately from current use. TAU is the clearest example of why that distinction matters.
3. Compare every loan layer with its own destination, collateral buffer and funding cost. Reservoir is the clearest observed nested example.
4. Display stale issuer mark ages next to manager-product capital. Keep unproved routes outside confirmed E4.
5. Never turn product book NAV, a protocol label or a shared account into measured strategy capital or realized profit.

## Reproduce and inspect

The offline builder is `python3 tools/eth/carry_variants_expansion_build.py`. The presentation dataset is `data/eth/carry_variants_expansion.json`. Its `products`, `variants`, `destinations` and `findings` contain the ready-to-use exhibits. Raw primary responses, request timestamps, exact blocks and SHA256 hashes live under `raw/eth/carry-variants-expansion-2026-10-04/`. Every failed or reverted probe remains explicit. The export records **137 passing checks** and **0 failures**.

Key primary links: [Reservoir vault](https://app.ipor.io/fusion/ethereum/0xf6cd9e8415162c8fb3c52676c7ca68812a34f76e/vault-info), [TAU vault](https://app.ipor.io/fusion/ethereum/0xc50b2d51fd1e2ac67a9c09eaf63c24ea2465c64b/vault-info), [Midas contract registry](https://docs.midas.app/resources/smart-contracts-registry), [wsrUSD verified source](https://etherscan.io/address/0xd3fd63209fa2d55b07a0f6db36c2f43900be3094#code), [historical Yearn route](https://gov.yearn.fi/t/yeth-vault-strategy-w-uni-mining/5930).
