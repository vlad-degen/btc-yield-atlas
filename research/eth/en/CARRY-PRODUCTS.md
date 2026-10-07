# ETH carry products: evidence per product

Financial snapshot: **2 October 2026, 23:59:59 UTC**, Ethereum block **26,108,081**, Optimism block **157,693,411**. Contract reads collected 4 to 7 October 2026.

## Ranking

The top five are ranked by dollars borrowed against ETH: **Liquid ETH, YieldBasis WETH, Lido Earn, Avant, Liquity**. Together the 12 carry products on the map hold 305,908 ETH and owe $270.9M ([all products and status](CARRY-CATEGORY.md)). Books overlap with other map rows; do not add them.

| Product | Dollars borrowed | Loan rate | Whole book, ETH | 30-day ETH book return | Excess vs stETH, pp |
| --- | --- | --- | --- | --- | --- |
| ether.fi Liquid ETH | $181.1M | 7.79% | 177,171 | 0.2610% | +0.0761 |
| YieldBasis WETH | $27.8M | 10.00% | 10,426 | -0.1622% | -0.3471 |
| Lido Earn ETH | $25.6M | 4.33% | 83,309 | 0.2513% | +0.0664 |
| Avant avETH / savETH | $10.0M | 6.30% | 12,583 | 0.3385% | +0.1536 |
| Liquity ETH Carry | $6.8M | 2.55% | 6,014 | 0.4597% | +0.2748 |
| Rocksolid rETH | $2.7M | 4.61% | 9,728 | 0.2192% | +0.0343 |
| Makina DETH | $385k | 3.21% | 2,499 | 0.3468% | +0.1619 |
| Royco ETH | $91k | 30.24% | 116 | 0.1849% | +0.0000 |
| Vesper vaETH | $69k | 5.00% | 1,052 | 0.0698% | -0.1151 |

Returns are 2 September to 2 October 2026, not annualised; stETH returned 0.1849%. NEMO ETH Prime ($5.6M) and Sentora ETH ($1.2M) are in [ROCKSOLID-NEMO-SENTORA](ROCKSOLID-NEMO-SENTORA.md).

**Concrete Delta weETH is excluded.** Its 307,363 ETH is one Bitfinex-linked wallet's own Aave position moved into the vault's Safe; one address holds all shares and the Safe borrows $176.15M of stablecoins. It is not a pooled product ([CONCRETE-DELTA](CONCRETE-DELTA.md)).

## Book history

| Product | Book capital at T | 30-day ETH book return | First funded sampled date | Return from that sample to T | Positive share addresses at T | Configured fees at T |
| --- | ---: | ---: | --- | ---: | --- | --- |
| ether.fi Liquid ETH | 177,171.063 ETH / $472.684M | +0.2610% | 2024-09-30 | +6.8658% | 7,793 Ethereum, 1,511 Optimism | 0.35% management fee at T |
| YieldBasis WETH | 10,425.999 ETH / $27.816M | −0.1622% | 2026-05-31 in monthly samples | External gauge rewards excluded; see the matched 94-day comparison below | 332 direct LT addresses, including the gauge | 10% minimum admin parameter; variable fee allocation |
| Rocksolid rETH | 9,727.767 ETH / $25.953M | +0.2192% | 2025-08-31 | +4.6354% | 388 Ethereum | 1% management / 10% performance at T |
| Liquity ETH Carry | 6,014.002 ETH / $16.045M | +0.4597% | 2026-03-31 | +3.5159% | 130 Ethereum | 0.5% management / 10% performance at T; indexed UI zero defaults differ |
| Royco ETH | 116.052 ETH / $0.310M | +0.1849% | 2026-03-31 | +1.3494% | 8 Ethereum | 0% management / 10% performance at T; current documentation says 0% / 0% |

Since-first-sample returns start on different dates, so they do not rank products. Returns are cumulative changes in recorded ETH share value and include the underlying staking conversion; separately distributed rewards are outside the series. Pre-deployment months stay empty, not zero.

## ether.fi Liquid ETH (#1, $181.1M borrowed)

**Finding:** Liquid beat stETH by 0.66 pp a year over two years (3.37% against 2.71%). The ETH loop added +0.02 pp a year and the dollar leg -0.13 pp; the rest is income our model cannot assign ([LIQUID-LOOP](LIQUID-LOOP.md)). At 2 October rates the dollar leg loses about $6.8M a year. Dossier: [Liquid ETH](dossiers/etherfi-liquid-eth.md).

The Ethereum share contract was deployed on **3 June 2024 at 23:23:59 UTC**. The T book covers Ethereum and Optimism share circulation and totals **177,171.063 ETH / $472.684M**. The first funded observation used here is 30 September 2024. Its cumulative ETH book change to T is **+6.8658%**; the exactly 730-day comparison in the existing benchmark uses a different start date and remains **+6.8501%**. These figures are compatible and should keep their explicit window labels. [Share contract](https://etherscan.io/address/0xf0bb20865277abd641a307ece5ee04e79073416c#code), [existing benchmark](../../../data/eth/etherfi_staking_comparison.json).

The product mixes at least two financing mechanisms. The main Aave and Spark accounts borrow WETH against staking collateral, so those legs are E3 staking loops. The controlled Drone account borrows stablecoins, so those legs are E4 dollar carry. Dollar destination claims include cUSD, senRLUSDv2 and senPYUSDPRIMEv2. Borrowing-account collateral less debt is only one part of carry equity; separately held dollar investments must also be counted. [Drone](https://etherscan.io/address/0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c), [loan manager](https://etherscan.io/address/0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3), [existing account metrics](../../../data/eth/etherfi_verified_metrics.json).

| Account | Mechanism | Collateral, protocol oracle USD | Debt, protocol oracle USD | Actual LTV | Weighted liquidation threshold | Health factor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0xf0bb20... / Aave V3 | E3 | $1,182,315,320.23 | $1,093,583,118.47 | 92.4950% | 95.00% | 1.027082 |
| 0xf0bb20... / Spark | E3 | $92,243,395.58 | $82,793,741.88 | 89.7557% | 93.00% | 1.036145 |
| 0x0a42b2... / Aave V3 | E4 | $133,115,759.35 | $76,588,521.61 | 57.5353% | 80.00% | 1.390451 |
| 0x0a42b2... / Spark | E4 | $8,048,315.74 | $3,611,570.54 | 44.8736% | 84.00% | 1.871924 |

The main WETH borrowing APR at T is **2.0738% on Aave** and **1.9070% on Spark**. The new dated funding series shows archived Aave WETH variable APR alongside ETH book share value. This is an E3 financing reference inside a mixed portfolio, not the carry sleeve’s blended dollar funding cost. Instantaneous APR and cumulative product return use different measures and must keep separate units. [Funding captures](../../../raw/eth/2026-10-04/strict-products/funding_history_rpc.json).

Income comes from validator staking rewards and payments by destination borrowers. Some destination credit flows back to the same consolidated borrower: the captured proportional overlap is **8,708,987.1107 RLUSD** and **4,758,914.1594 PYUSD**. Those amounts diagnose concentration and recycling of credit, not additional assets or extra income. [Credit lookthrough](../../../data/eth/carry_credit_lookthrough.json).

The authority is a per-function role system. Owner role 8 uses a 24-hour timelock, but management-fee updates also admit role 55, whose active address is `0x607d0c7e3578802eb46d388cb86cfba8ff657306`. The owner delay does not establish that every fee change is delayed. Rate updates, pausing, unpausing and rate-provider changes have their own selectors and roles. The T management fee is **0.35%**. [Exact permission review](../../../data/eth/permissions_review_T.json).

The transfer audit covers every Ethereum and Optimism share-transfer interval through T. Both reconstructed ledgers match each chain’s archived supply exactly. There are **7,793 Ethereum holders** and **1,511 Optimism holders**. Twenty-two addresses occur on both chains, producing **9,282 distinct address strings**. These are positive share balances, including contracts, not identifiable people or original depositors. The largest Ethereum holder owns **25.4187% of Ethereum supply**; that is not 25.4187% of consolidated cross-chain supply. [Ethereum ledger](../../../raw/eth/2026-10-04/strict-products/liquid_holder_distribution_T.json), [Optimism ledger](../../../raw/eth/2026-10-04/strict-products/liquid_op_holder_distribution_T.json).

The capital panel retains 24 completed month ends, October 2024 through September 2026. A separate dated current UI observation labels 64.66% carry and 21.65% looping on 3 October. Those labels cannot reconstruct historical allocation.

## YieldBasis WETH (#2, $27.8M borrowed)

**Finding:** the only top-five product whose fees cover its loan: Curve fee growth 9.19% a year on twice the debt against a fixed 10% crvUSD rate. Unstaked LP holders still trailed stETH because gauge rewards in YB go to stakers.

The WETH LT pool has **10,425.999 ETH / $27.816M** of net oracle book at T. Its actual liability is **27,814,855.84 crvUSD**, approximately 99.996% of net equity at a nominal $1 debt mark. The **64.14M crvUSD allocation limit** is capacity, not debt. This liability finances WETH/crvUSD liquidity, which places the pool in the same carry family as BTC YieldBasis. [Pool contract](https://etherscan.io/address/0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea#code), [official design](https://docs.yieldbasis.com/).

WETH deposits create LT claims on the net book. The AMM borrows crvUSD, supplies liquidity and adjusts leverage as prices move. Traders pay swap fees; borrowing, rebalancing and administration consume part of that income. Staking LT in the gauge adds distinct fee and incentive rights. **5,875 ETH** of book is staked and **4,551 ETH** unstaked. Both claims belong to the same pool and must not be added as new capital. The minimum admin parameter is 10%; actual allocation follows the contract mechanism rather than a flat 10% deduction from every investor gain.

All 24 selected month-end blocks were read. Code is absent through April 2026; the first funded monthly observation is May, at **641 ETH**. Net book reaches **12,512 ETH** in August and **10,616 ETH** in September. Updated effective supply and fair value per LT unit provide the book measure. Missing predeployment months remain null. [Reader observations](../../../data/eth/reader_carry_category.json).

The unstaked fair ETH mark fell **0.6926%** over the matched 94-day window while stETH gained **0.5741%**, a **−1.2668 percentage-point** excess. External gauge rewards are excluded; this does not establish the complete return of a staked investor. Realized funding cash flow has not been isolated. [Fixed-block capital and return ledger](../../../data/eth/strategy_universe_deep.json).

Complete LT Transfer discovery identifies 524 touched addresses. Archived balances reconcile exactly to **10,364.971982645044 effective LT shares**, held by **332 positive addresses**. The largest address is the gauge, with **56.35%** of supply. Direct addresses include contracts; they do not count gauge beneficiaries or unique investors. [Reconciled holder ledger](../../../data/eth/yb_LT_holders_T.json).

The configured admin at T is `0x370a449febb9411c95bf897021377fe0b7d100c0`. Snapshot withdrawal previews for 1%, 10% and 30% of raw supply quote approximately **104, 1,043 and 3,128 WETH**. A preview establishes an output calculation, not an executed or paid withdrawal. An actual unwind must remove liquidity, settle crvUSD debt and release WETH. The main product chapter displays the eight operational steps, control actors, income payers, actual loan, monthly capital, ETH return and holder distribution together. [Current product chapter dataset](../../../data/eth/reader_product_chapters.json).

## Liquity ETH Carry (#5, $6.8M borrowed)

**Finding:** the route is an Ebisu wstETH trove borrowing ebUSD at a 2.55% rate the product sets itself, into ebUSD/USDC liquidity that earned 0.45% in fees; the dollar side does not pay for itself, and its lead over stETH is 99% rewards ([REWARDS-SPLIT](REWARDS-SPLIT.md)).

The contract was deployed on **30 January 2026 at 14:23:47 UTC**. The published product name and earlier description point to Liquity/BOLD and Curve. The fixed-block audit instead identifies an **Ebisu wstETH Trove** and an active **Uniswap V4** fuse. Granted stablecoin substrates include **ebUSD and USDC**. The live route must therefore use the onchain finding rather than silently preserving the earlier BOLD/Curve design. [Share contract](https://etherscan.io/address/0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c#code), [Ebisu create fuse](https://etherscan.io/address/0x864d303d4d161209b406eb3d4c43759231a73a07#code), [Uniswap V4 fuse](https://etherscan.io/address/0x1a2d2f51d1874bdc89f6e78feb99b8b7967d16da#code).

The active Trove holds **4,585.482153 wstETH** against **6,752,064.750858 ebUSD accrued debt**. Its borrower-set annual rate is **2.55%**. At the branch oracle price, collateral is **$15,232,433.83**. Treating ebUSD debt as a nominal dollar unit gives **44.3269% actual LTV**. Branch minimum collateralization is **120%**, equivalent to an **83.3333% liquidation LTV**. The derived collateral ratio divided by that minimum is **1.87997**; this is not an Aave health-factor getter. Market ebUSD peg deviation and loan upfront fees are separate from those nominal calculations. [Active Trove getters](../../../raw/eth/2026-10-04/strict-products/trove_final_rpc.json), [oracle read](../../../raw/eth/2026-10-04/strict-products/loan_prices_rpc.json), [Ebisu loan mechanics](https://ebisu.gitbook.io/ebisu-money/managing-your-ebusd-loan).

Nine captured Ebisu enter/exit events establish actual strategy changes. The first rETH Trove opens on **5 March 2026** and closes on **9 March**. The vault then uses the wstETH branch, with further closes and opens in March and April. The currently open Trove was created on **6 June 2026 at 22:07:23 UTC**. Thus a single static borrowing route cannot describe the entire product history. [First enter transaction](https://etherscan.io/tx/0x8f4183c38c56ffd02e711245f2e6a6b46d5c1b0decd1889eba5337ea0c3ea2cc), [current Trove opening](https://etherscan.io/tx/0x076e6b9213e496ffec45190370bbf1ba95a81d8d8712271660fb52b6300795ba), [full captured events](../../../raw/eth/2026-10-04/strict-products/deep_positions_rpc.json).

The vault has **20-decimal shares** and **18-decimal WETH assets**. T book NAV is **6,014.002 ETH / $16.045M**. January and February assets and supply are zero. The funded return series begins at the 31 March sampled observation: cumulative WETH book change is **+3.5159%** through T, and the 30-day change is **+0.4597%**. A default empty-vault price of 1 would give a misleading return baseline. [Historical getters](../../../raw/eth/2026-10-04/strict-products/history_rpc.json).

The market accounting fields are explicitly stored book values: market 29 records **3,265.353049 ETH**, market 53 **59.732893 ETH**, market 16 a negligible balance and market 12 zero. They are not a newly refreshed independent mark of every asset. The captured idle wallet holds **300.678433 WETH** and **1.907947 ebUSD**, with no wstETH, rETH or USDC idle balances in the tested tokens. These observations do not complete a fresh LP and vault asset reconciliation. [Market substrates and books](../../../raw/eth/2026-10-04/strict-products/market_controls_rpc.json), [idle token balances](../../../raw/eth/2026-10-04/strict-products/liquity_wallet_T.json).

Fees at T are **0.5% management / 10% performance**, rather than the indexed zero defaults. The owner, guardian, Atomist and fuse-manager memberships include `0x32787cd59244581a358a068d52e460eb00df6543`. Alpha execution role 200 has two active addresses. The full historical role-grant set was checked through `getAccess` at T: all active memberships have **zero current and pending execution delays**. Per-function permissions still constrain actions. No address is equated to the Sentinel brand without separate identity evidence. The 1-second redemption parameter is a deposit lock; it does not promise a one-second strategy unwind. [Role membership capture](../../../raw/eth/2026-10-04/strict-products/deep_positions_rpc.json), [access-manager source](https://etherscan.io/address/0xcee55bd8ce0361a67f9a48888a2b519c9d207a97#code).

The exact supply reconstruction gives **130 positive share addresses**, including Rocksolid’s execution account. The largest holder owns **36.8805%** of supply. Income comes from retained wstETH staking and the strategy’s recognized stablecoin or liquidity-position returns; the vault pays debt interest and protocol loan fees. No independently isolated organic carry return is claimed.

## Rocksolid rETH ($2.7M borrowed)

**Finding:** dollar carry is 10.5% of the book: a second strategy wallet borrows $2.73M USDC against rETH on Morpho. The book reconciles to within 0.04% across Monad, Ethereum and that wallet ([ROCKSOLID-NEMO-SENTORA](ROCKSOLID-NEMO-SENTORA.md)). The owner closed the vault on 29 September and reopened it with a contract upgrade on 7 October.

The share contract was deployed on **28 August 2025 at 04:55:35 UTC**. The [public launch announcement](https://blog.rocksolid.network/introducing-rocksolid-liquid-vaults/) followed on **25 September 2025**. At T, the book contains **8,293.351834 rETH**, equal to **9,727.767 ETH / $25.953M**. Fourteen completed-month observations run from August 2025 through September 2026. Cumulative ETH book change since the first funded August sample is **+4.6354%**. It includes rETH staking growth and recognized strategy accounting; separately distributed incentives are not included. [Vault](https://etherscan.io/address/0x936facdf10c8c36294e7b9d28345255539d81bc7#code).

Published roles separate Tulipa’s management and valuation proposals from Rocksolid’s co-signing and distribution, using Fordefi policy controls. The configured valuation manager is `0x5856fcbe7b15a5a2cdccff5051b59bb8bdd54204`. At T, both the vault owner and the execution address have **no contract code**. Therefore the documented 30-day fee-change policy cannot be described as an independently verified 30-day onchain wrapper timelock. Fees are **1% management / 10% performance** in the vault at T. [Architecture](https://docs.rocksolid.network/architecture), [reward policy](https://docs.rocksolid.network/for-depositors/rewards), [code and role capture](../../../raw/eth/2026-10-04/strict-products/extra_controls_rpc.json).

The report for **17 to 24 August 2026** labels **28.54% stable carry** and **9.07% looping**. Its carry example posts rETH on Aave, borrows USDC at 50% LTV and deploys dollars to Spectra and a Hyperithm Morpho strategy. Those numbers belong to that report vintage. Direct Aave collateral and debt in the configured execution account are both zero at T; the dollar loan sits in the second wallet. [Dated report page](https://app.rocksolid.network/vaults/0x936facdf10c8c36294e7b9d28345255539d81bc7), [fixed-block account capture](../../../raw/eth/2026-10-04/strict-products/controls_rpc.json).

The snapshot nevertheless proves nested carry-product exposure. The execution account holds **748.638010 Liquity ETH Carry shares**, with a whole-product book value of **728.484 ETH / $1.944M**. That is **7.4887%** of Rocksolid’s own whole book, but not a pure carry-allocation estimate. It also overlaps the underlying Liquity NAV. Adding both products as disjoint market capital would count that claim twice. [Underlying holder ledger](../../../raw/eth/2026-10-04/strict-products/liquity_holder_distribution_T.json).

At T, **388 positive share-holding addresses** reconcile exactly to supply. The largest holds **40.9678%**. The issuer’s [one-month retrospective](https://blog.rocksolid.network/a-rocksolid-retrospective-one-month-post-launch/) reports more than 220 historical depositors and an initial **0.3173 rETH/day** incentive programme. Those are historical issuer claims. They are neither the T holder census nor independently measured organic returns. Validator rewards, external borrower payments, trading fees and issuer-funded incentives have different payers and must remain distinct.

## Royco ETH ($91k borrowed)

The roywstETH wrapper was deployed on **4 March 2026 at 16:00:47 UTC**. It reports **93.184064 wstETH**, equal to **116.052 ETH / $309,619.94** at T. Its funded monthly samples begin in March. ETH book change since 31 March is **+1.3494%**, and the 30-day change is **+0.1849%**. These are recorded book returns with explicit accounting freshness limits. [Share wrapper](https://etherscan.io/address/0x41ce72e04d349eb957bdc373baa9c69207032c56#code).

The actual contract path is **Concrete share wrapper → RoycoVaultMakinaStrategy → Makina Machine → Caliber**. The machine is `0x0fdf9f1920e160ea8ae267bde13e725def81e5ee`; the executor is `0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0`. The public design borrows dollars against wstETH to invest in srRoyUSDC Senior tranches; actual debt at T is PYUSD, while the senior receipt is USDC-denominated. A srRoyUSDC share balance is directly verified at Caliber. Actual Caliber accounting instructions identify a Morpho wstETH/PYUSD market. A fresh T read establishes 93.075979 wstETH of collateral, 90,890.891657 PYUSD of accrued debt and a 30.24% annual borrowing quote. The quote is a fixed-block model output, not realized financing cost. Funding conversion into the USDC receipt and its underlying senior-credit backing remain separate evidence. [Adapter](https://etherscan.io/address/0x185313dbb1f3aa2b3fcc603f0ee4cba753ef1dd7#code), [machine](https://etherscan.io/address/0x0fdf9f1920e160ea8ae267bde13e725def81e5ee#code), [executor](https://etherscan.io/address/0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0#code), [published vault design](https://royco.gitbook.io/royco-dawn/royco-dawn/3.-vault-products).

| Recorded category | Value in wstETH accounting units | Fresh at T? |
| --- | ---: | --- |
| Positive position | 93.075979 | No |
| Debt position | 26.981276 | No |
| Destination position | 26.923846 | No |

All three recorded positions are stale under Caliber’s own flag. `isAccountingFresh` is false and `getNetAum` reverts with `PositionAccountingStale`. Wrapper, adapter and machine return **zero immediate maxWithdraw**. This does not prove a loss or permanent inability to exit. It establishes that cached book NAV is not an immediately redeemable, independently current asset valuation. The documented vault process is asynchronous. Direct Aave and Spark accounts at Caliber have zero collateral and debt. [Recorded positions, freshness and destination balance](../../../raw/eth/2026-10-04/strict-products/loan_prices_rpc.json), [Caliber accounting controls](../../../raw/eth/2026-10-04/strict-products/trove_final_rpc.json).

The owner Safe is **3-of-4**, but the active wrapper `VAULT_MANAGER` is a separate address, `0x82eece4a736db0767370d2dffde9bdf6e38aaeb8`. Verified wrapper fee-update functions admit that role. The configured operator and mechanic are `0x425bbc2cff0c7e7960baa9bac2f0cb67b41d3bef`. Caliber’s instruction-root timelock is **172,800 seconds, or 2 days**, at T. That applies to the instruction-root control and is distinct from the current documentation’s minimum **7-day allocation notice**. It is not a universal delay on every wrapper or fee action. [Wrapper role capture](../../../raw/eth/2026-10-04/strict-products/concrete_roles_rpc.json), [machine control reads](../../../raw/eth/2026-10-04/strict-products/deep_positions2_rpc.json).

The final control check binds both beacon implementations to verified bytecode at T. Changing the configured duration uses an active AccessManager role held by a 3-of-4 Safe, with a three-day execution delay. An unscheduled duration-change execution reverts. The two-day instruction-root delay and the three-day role delay govern different actions; they do not establish an immutable or universally additive five-day notice. Other admin and module paths remain outside this specific proof. [Backing, exit and control ledger](../../../data/eth/backing_exit_closure.json).

The T wrapper has **zero management / 10% performance fee**. Current documentation reviewed on 4 October says zero fees. It also describes a **30-day vault withdrawal epoch** and approximately **2 additional processing days**, with KYC/KYB before withdrawal and US-person restrictions. Published policy and fixed-block implementation are shown separately. [Governance and fees](https://royco.gitbook.io/royco-dawn/royco-dawn/4.-governance-and-fees), [withdrawals](https://royco.gitbook.io/royco-dawn/royco-dawn/5.-deposits-and-withdrawals).

The share ledger contains **8 positive holders** at T and reconciles exactly to supply. The largest address holds **90.6311%**. Ethereum issuance and transaction-related income fund wstETH staking income through the staking issuer; borrowers in the underlying Senior allocations fund credit returns. Junior capital provides finite first-loss coverage, not guaranteed yield or principal protection. Neither the cached position book nor the public mandate isolates an organic carry result.

The additional [fixed-block withdrawal getters](../../../raw/eth/2026-10-04/strict-products/exit_getters_T.json) query each product’s largest holder. Royco and Rocksolid (then Closing) return zero `maxWithdraw` and `maxRedeem`; Liquity returns nominal holder balances. The final exit exhibit adds separate read-only request and withdrawal tests at 1%, 10% and 30% of book, plus receipt-verified historical cash payments. Nominal getters alone still do not establish cash delivery or a full strategy unwind.

## Deprecated and closed examples

Rocksolid's owner called initiateClosing on 29 September 2026 at 02:39:23 UTC; new requests were rejected while Closing. On 7 October the owner upgraded the implementation to add `cancelClosing()`, reopened the vault and resumed deposits. No public reason was given for either step. Reservoir and TAU InfiniFi ETH Carry unwound without an incident.

[Origami wOETH 5x](https://docs.origami.finance/the-second-fold-v2/deprecated-vaults/woeth-5x/token-flow) appears in the issuer’s Deprecated Vaults collection and explicitly borrows WETH to buy wOETH. That is E3, not dollar carry. [Origami wstETH 11x](https://docs.origami.finance/the-second-fold-v2/deprecated-vaults/wsteth-11x/token-flow) is another deprecated ETH staking-loop precedent. The documentation establishes deprecated placement. It does not establish a failure, investor loss, closing date or reason. Both examples retain null values for those unsupported claims.

## Reproduction

`python3 tools/eth/build_product_chapters.py` rebuilds the share-price, funding, capital and holder panels offline from the captures. Renderer data: [reader_product_chapters.json](../../../data/eth/reader_product_chapters.json). Raw captures: `raw/eth/2026-10-04/strict-products/` ([hash manifest](../../../raw/eth/2026-10-04/strict-products/all_captures_manifest.json)).
