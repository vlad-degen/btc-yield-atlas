# ETH carry products: snapshot evidence and product chapters

The final edition adds [capital, earned income and investor exit evidence](CAPITAL-INCOME-EXIT.md). Its fixed-block custody graph, common-window cash-flow ledgers and receipt-verified payout history extend the original scope of this chapter. Use that exhibit for the completed measured answer and its evidence boundaries.


Financial snapshot: **2 October 2026, 23:59:59 UTC**. Ethereum block **26,108,081**; Optimism block **157,693,411**. New contract and document observations were collected on **4 October 2026**. Earlier financial inputs retain their original capture dates.

These chapters follow the Bitcoin product format: capital and return, linked money flow, actor powers, income payers, capital history, funding cost, holder distribution, loan legs and dated events. The ordering uses whole-product book NAV. It does not rank verified carry-only equity, realized profit or investment quality. The books overlap and must not be added as independent net market capital. The current five largest are Concrete, Liquid, YieldBasis WETH, Rocksolid and Liquity; Royco remains an additional fully examined case.

The current renderer data is [reader_product_chapters.json](../../../data/eth/reader_product_chapters.json). The original five-case capture remains in [product_chapters.json](../../../data/eth/product_chapters.json). Published designs remain in the existing carry census; `liveRoute` in this file records what the fixed-block audit actually established.

## Comparable measurements

| Product | Book capital at T | 30-day ETH book return | First funded sampled date | Return from that sample to T | Positive share addresses at T | Configured fees at T |
| --- | ---: | ---: | --- | ---: | --- | --- |
| Concrete Delta weETH | 307,362.925 ETH / $820.029M | +0.1915% | 2025-12-31 | +1.8434% | 1 Ethereum | 0% / 0% configured vault fees; private fees unresolved |
| ether.fi Liquid ETH | 177,171.063 ETH / $472.684M | +0.2610% | 2024-09-30 | +6.8658% | 7,793 Ethereum, 1,511 Optimism | 0.35% management fee at T |
| YieldBasis WETH | 10,425.999 ETH / $27.816M | −0.1622% | 2026-05-31 in monthly samples | External gauge rewards excluded; see the matched 94-day comparison below | 332 direct LT addresses, including the gauge | 10% minimum admin parameter; variable fee allocation |
| Rocksolid rETH | 9,727.767 ETH / $25.953M | +0.2192% | 2025-08-31 | +4.6354% | 388 Ethereum | 1% management / 10% performance at T |
| Liquity ETH Carry | 6,014.002 ETH / $16.045M | +0.4597% | 2026-03-31 | +3.5159% | 130 Ethereum | 0.5% management / 10% performance at T; indexed UI zero defaults differ |
| Royco ETH | 116.052 ETH / $0.310M | +0.1849% | 2026-03-31 | +1.3494% | 8 Ethereum | 0% management / 10% performance at T; current documentation says 0% / 0% |

T capital uses the existing standardized ETH/USD quote of $2,667.9504418816 at T plus one second; loan collateral uses its own protocol oracle rather than that display quote. Completed-month USD values use dated Chainlink observations.

Returns are cumulative changes in recorded ETH share value. They are not annualized. Different inception samples make the full-period column unsuitable as a performance ranking. For weETH, rETH and wstETH products, historical exchange rates convert native vault assets to ETH. That conversion includes underlying staking growth. It does not isolate strategy profit. Separately distributed rewards are outside the share-price series.

The first funded sampled date is the earliest archived observation with positive share supply. It can include manager or seed capital before the public launch. January and February Liquity reads returned a default share price of 1 while supply and assets were zero, so those values are excluded as investor-return baselines. The capital chart correctly retains the deployed empty months as zero. Predeployment reads remain absent, rather than zero.

## 1. Concrete Delta weETH

The share contract was deployed on **12 December 2025 at 10:48:23 UTC**. Its book holds **278,170.834213 weETH**, equal to **307,362.925 ETH** at T. One address holds the entire share supply. This establishes a large manager-issued accounting book, not a broad investor base. [Share contract](https://etherscan.io/address/0xb9dc54c8261745cb97070cefbe3d3d815aee8f20#code), [reconciled holder ledger](../../../raw/eth/2026-10-04/strict-products/concrete_holder_distribution_T.json).

The linked strategy is [MultisigStrategy](https://etherscan.io/address/0xc8ea269d4dba296f7fbba812905c1b2efe5dbe1c#code). It reports assets to the share contract and identifies the [shared execution Safe](https://etherscan.io/address/0x7ee29373f075ee1d83b1b93b4fe94ae242df5178). That Safe is 3-of-5 at T. Its Aave account contains **$503,452,604.19 collateral** and **$105,736,216.10 debt**, with **21.0022% actual loan-to-value** and **3.82219 health factor**. The account is shared with another Concrete product. Its balances cannot be assigned entirely to Delta or split proportionally using the share books. [Original fixed-block lookthrough](../../../data/eth/concrete_lookthrough_T.json).

The advertised dollar strategy deploys stable borrowing into neutral arbitrage. The available private-strategy documentation does not independently identify the trading venues, hedge counterparties, funding income or investor payout terms. Ethereum issuance and transaction-related income fund the underlying weETH staking return, distributed through the staking issuer. Arbitrage counterparties would fund the dollar strategy margin, but no product-specific realized profit series was established. The initial share mint itself did not transfer underlying ERC20 assets.

The [vault owner Safe](https://etherscan.io/address/0x8f5f1d40243b259ceb7ab44ba421ff191bcd3381) is **1-of-2**, distinct from custody. It also holds the active `VAULT_MANAGER` role. Verified fee-update functions require that role. Both management and performance fees are zero in the share contract at T; private commercial fees remain outside the verified configuration. No product-specific enforced fee timelock was established. [Controls capture](../../../raw/eth/2026-10-04/strict-products/controls_rpc.json), [role history and active membership](../../../raw/eth/2026-10-04/strict-products/concrete_roles_rpc.json).

Every archived funded observation has a native share price of **1 weETH**. The ten completed-month observations from December 2025 through September 2026 retain the same native book assets. The **+1.8434% ETH book change** since the December sample therefore reflects the changing weETH exchange rate. It must not be presented as independently measured arbitrage profit, organic carry yield or a realized payout.

## 2. ether.fi Liquid ETH

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

The capital panel retains 24 completed month ends, October 2024 through September 2026. A separate dated current UI observation labels 64.66% carry and 21.65% looping on 3 October. Those labels cannot reconstruct historical allocation. The existing independent partial reconstruction leaves **$12,452,629.59**, or **2.6345% of book NAV**, unresolved; the difference is not labelled yield. [Partial balance sheet](../../../data/eth/etherfi_partial_balance_sheet.json).

## 3. YieldBasis WETH

The WETH LT pool has **10,425.999 ETH / $27.816M** of net oracle book at T. Its actual liability is **27,814,855.84 crvUSD**, approximately 99.996% of net equity at a nominal $1 debt mark. The **64.14M crvUSD allocation limit** is capacity, not debt. This liability finances WETH/crvUSD liquidity, which places the pool in the same carry family as BTC YieldBasis. [Pool contract](https://etherscan.io/address/0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea#code), [official design](https://docs.yieldbasis.com/).

WETH deposits create LT claims on the net book. The AMM borrows crvUSD, supplies liquidity and adjusts leverage as prices move. Traders pay swap fees; borrowing, rebalancing and administration consume part of that income. Staking LT in the gauge adds distinct fee and incentive rights. **5,875 ETH** of book is staked and **4,551 ETH** unstaked. Both claims belong to the same pool and must not be added as new capital. The minimum admin parameter is 10%; actual allocation follows the contract mechanism rather than a flat 10% deduction from every investor gain.

All 24 selected month-end blocks were read. Code is absent through April 2026; the first funded monthly observation is May, at **641 ETH**. Net book reaches **12,512 ETH** in August and **10,616 ETH** in September. Updated effective supply and fair value per LT unit provide the book measure. Missing predeployment months remain null. [Reader observations](../../../data/eth/reader_carry_category.json).

The unstaked fair ETH mark fell **0.6926%** over the matched 94-day window while stETH gained **0.5741%**, a **−1.2668 percentage-point** excess. External gauge rewards are excluded; this does not establish the complete return of a staked investor. Realized funding cash flow has not been isolated. [Fixed-block capital and return ledger](../../../data/eth/strategy_universe_deep.json).

Complete LT Transfer discovery identifies 524 touched addresses. Archived balances reconcile exactly to **10,364.971982645044 effective LT shares**, held by **332 positive addresses**. The largest address is the gauge, with **56.35%** of supply. Direct addresses include contracts; they do not count gauge beneficiaries or unique investors. [Reconciled holder ledger](../../../data/eth/yb_LT_holders_T.json).

The configured admin at T is `0x370a449febb9411c95bf897021377fe0b7d100c0`. Snapshot withdrawal previews for 1%, 10% and 30% of raw supply quote approximately **104, 1,043 and 3,128 WETH**. A preview establishes an output calculation, not an executed or paid withdrawal. An actual unwind must remove liquidity, settle crvUSD debt and release WETH. The main product chapter displays the eight operational steps, control actors, income payers, actual loan, monthly capital, ETH return and holder distribution together. [Current product chapter dataset](../../../data/eth/reader_product_chapters.json).

## 4. Rocksolid rETH

The share contract was deployed on **28 August 2025 at 04:55:35 UTC**. The [public launch announcement](https://blog.rocksolid.network/introducing-rocksolid-liquid-vaults/) followed on **25 September 2025**. At T, the book contains **8,293.351834 rETH**, equal to **9,727.767 ETH / $25.953M**. Fourteen completed-month observations run from August 2025 through September 2026. Cumulative ETH book change since the first funded August sample is **+4.6354%**. It includes rETH staking growth and recognized strategy accounting; separately distributed incentives are not included. [Vault](https://etherscan.io/address/0x936facdf10c8c36294e7b9d28345255539d81bc7#code).

Published roles separate Tulipa’s management and valuation proposals from Rocksolid’s co-signing and distribution, using Fordefi policy controls. The configured valuation manager is `0x5856fcbe7b15a5a2cdccff5051b59bb8bdd54204`. At T, both the vault owner and the execution address have **no contract code**. Therefore the documented 30-day fee-change policy cannot be described as an independently verified 30-day onchain wrapper timelock. Fees are **1% management / 10% performance** in the vault at T. [Architecture](https://docs.rocksolid.network/architecture), [reward policy](https://docs.rocksolid.network/for-depositors/rewards), [code and role capture](../../../raw/eth/2026-10-04/strict-products/extra_controls_rpc.json).

The report for **17 to 24 August 2026** labels **28.54% stable carry** and **9.07% looping**. Its carry example posts rETH on Aave, borrows USDC at 50% LTV and deploys dollars to Spectra and a Hyperithm Morpho strategy. Those numbers belong to that report vintage. Direct Aave collateral and debt in the configured execution account are both zero at T. [Dated report page](https://app.rocksolid.network/vaults/0x936facdf10c8c36294e7b9d28345255539d81bc7), [fixed-block account capture](../../../raw/eth/2026-10-04/strict-products/controls_rpc.json).

The snapshot nevertheless proves nested carry-product exposure. The execution account holds **748.638010 Liquity ETH Carry shares**, with a whole-product book value of **728.484 ETH / $1.944M**. That is **7.4887%** of Rocksolid’s own whole book, but not a pure carry-allocation estimate. It also overlaps the underlying Liquity NAV. Adding both products as disjoint market capital would count that claim twice. [Underlying holder ledger](../../../raw/eth/2026-10-04/strict-products/liquity_holder_distribution_T.json).

At T, **388 positive share-holding addresses** reconcile exactly to supply. The largest holds **40.9678%**. The issuer’s [one-month retrospective](https://blog.rocksolid.network/a-rocksolid-retrospective-one-month-post-launch/) reports more than 220 historical depositors and an initial **0.3173 rETH/day** incentive programme. Those are historical issuer claims. They are neither the T holder census nor independently measured organic returns. Validator rewards, external borrower payments, trading fees and issuer-funded incentives have different payers and must remain distinct.

## 5. Liquity ETH Carry

The contract was deployed on **30 January 2026 at 14:23:47 UTC**. The published product name and earlier description point to Liquity/BOLD and Curve. The fixed-block audit instead identifies an **Ebisu wstETH Trove** and an active **Uniswap V4** fuse. Granted stablecoin substrates include **ebUSD and USDC**. The live route must therefore use the onchain finding rather than silently preserving the earlier BOLD/Curve design. [Share contract](https://etherscan.io/address/0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c#code), [Ebisu create fuse](https://etherscan.io/address/0x864d303d4d161209b406eb3d4c43759231a73a07#code), [Uniswap V4 fuse](https://etherscan.io/address/0x1a2d2f51d1874bdc89f6e78feb99b8b7967d16da#code).

The active Trove holds **4,585.482153 wstETH** against **6,752,064.750858 ebUSD accrued debt**. Its borrower-set annual rate is **2.55%**. At the branch oracle price, collateral is **$15,232,433.83**. Treating ebUSD debt as a nominal dollar unit gives **44.3269% actual LTV**. Branch minimum collateralization is **120%**, equivalent to an **83.3333% liquidation LTV**. The derived collateral ratio divided by that minimum is **1.87997**; this is not an Aave health-factor getter. Market ebUSD peg deviation and loan upfront fees are separate from those nominal calculations. [Active Trove getters](../../../raw/eth/2026-10-04/strict-products/trove_final_rpc.json), [oracle read](../../../raw/eth/2026-10-04/strict-products/loan_prices_rpc.json), [Ebisu loan mechanics](https://ebisu.gitbook.io/ebisu-money/managing-your-ebusd-loan).

Nine captured Ebisu enter/exit events establish actual strategy changes. The first rETH Trove opens on **5 March 2026** and closes on **9 March**. The vault then uses the wstETH branch, with further closes and opens in March and April. The currently open Trove was created on **6 June 2026 at 22:07:23 UTC**. Thus a single static borrowing route cannot describe the entire product history. [First enter transaction](https://etherscan.io/tx/0x8f4183c38c56ffd02e711245f2e6a6b46d5c1b0decd1889eba5337ea0c3ea2cc), [current Trove opening](https://etherscan.io/tx/0x076e6b9213e496ffec45190370bbf1ba95a81d8d8712271660fb52b6300795ba), [full captured events](../../../raw/eth/2026-10-04/strict-products/deep_positions_rpc.json).

The vault has **20-decimal shares** and **18-decimal WETH assets**. T book NAV is **6,014.002 ETH / $16.045M**. January and February assets and supply are zero. The funded return series begins at the 31 March sampled observation: cumulative WETH book change is **+3.5159%** through T, and the 30-day change is **+0.4597%**. A default empty-vault price of 1 would give a misleading return baseline. [Historical getters](../../../raw/eth/2026-10-04/strict-products/history_rpc.json).

The market accounting fields are explicitly stored book values: market 29 records **3,265.353049 ETH**, market 53 **59.732893 ETH**, market 16 a negligible balance and market 12 zero. They are not a newly refreshed independent mark of every asset. The captured idle wallet holds **300.678433 WETH** and **1.907947 ebUSD**, with no wstETH, rETH or USDC idle balances in the tested tokens. These observations do not complete a fresh LP and vault asset reconciliation. [Market substrates and books](../../../raw/eth/2026-10-04/strict-products/market_controls_rpc.json), [idle token balances](../../../raw/eth/2026-10-04/strict-products/liquity_wallet_T.json).

Fees at T are **0.5% management / 10% performance**, rather than the indexed zero defaults. The owner, guardian, Atomist and fuse-manager memberships include `0x32787cd59244581a358a068d52e460eb00df6543`. Alpha execution role 200 has two active addresses. The full historical role-grant set was checked through `getAccess` at T: all active memberships have **zero current and pending execution delays**. Per-function permissions still constrain actions. No address is equated to the Sentinel brand without separate identity evidence. The 1-second redemption parameter is a deposit lock; it does not promise a one-second strategy unwind. [Role membership capture](../../../raw/eth/2026-10-04/strict-products/deep_positions_rpc.json), [access-manager source](https://etherscan.io/address/0xcee55bd8ce0361a67f9a48888a2b519c9d207a97#code).

The exact supply reconstruction gives **130 positive share addresses**, including Rocksolid’s execution account. The largest holder owns **36.8805%** of supply. Income comes from retained wstETH staking and the strategy’s recognized stablecoin or liquidity-position returns; the vault pays debt interest and protocol loan fees. No independently isolated organic carry return is claimed.

## 6. Royco ETH

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

The additional [fixed-block withdrawal getters](../../../raw/eth/2026-10-04/strict-products/exit_getters_T.json) query each product’s largest holder. Royco and Rocksolid return zero `maxWithdraw` and `maxRedeem`. Concrete and Liquity return nominal holder balances. The final exit exhibit adds separate read-only request and withdrawal tests at 1%, 10% and 30% of book, plus receipt-verified historical cash payments. Nominal getters alone still do not establish cash delivery or a full strategy unwind.

## Deprecated and closed examples

Rocksolid entered Closing through an owner initiateClosing transaction on 29 September 2026 at 02:39:23 UTC. Its verified implementation rejects new requests in that state. The review does not establish the economic reason, completed closure, investor loss or permanent future deprecation. The Closed tab states this transition and keeps adjacent official E3 deprecations outside the E4 failure census.

[Origami wOETH 5x](https://docs.origami.finance/the-second-fold-v2/deprecated-vaults/woeth-5x/token-flow) appears in the issuer’s Deprecated Vaults collection and explicitly borrows WETH to buy wOETH. That is E3, not dollar carry. [Origami wstETH 11x](https://docs.origami.finance/the-second-fold-v2/deprecated-vaults/wsteth-11x/token-flow) is another deprecated ETH staking-loop precedent. The documentation establishes deprecated placement. It does not establish a failure, investor loss, closing date or reason. Both examples retain null values for those unsupported claims.

## Reproduction and schema

Run `python3 tools/eth/build_product_chapters.py` from the repository root. This is an offline build using the captured files and the editorial template, not a new live query. It rebuilds share-price, funding, capital and holder panels and combines them with source-checked product descriptions and fixed-block control reads. The editorial template holds curated English text and the review’s disclosure decisions; it is not an extra financial data feed.

- [Offline builder](../../../tools/eth/build_product_chapters.py)
- [Editorial input template](../../../raw/eth/2026-10-04/strict-products/product_chapter_editorial_template.json)
- [Snapshot getters and creation transactions](../../../raw/eth/2026-10-04/strict-products/snapshot_rpc.json)
- [Historical book/rETH-rate getters](../../../raw/eth/2026-10-04/strict-products/history_rpc.json)
- [Historical funding getters](../../../raw/eth/2026-10-04/strict-products/funding_history_rpc.json)
- [Ethereum transfer manifest](../../../raw/eth/2026-10-04/strict-products/transfer_manifest_tenderly.json) and [completed retry manifest](../../../raw/eth/2026-10-04/strict-products/transfer_manifest_retry.json)
- [Optimism transfer manifest](../../../raw/eth/2026-10-04/strict-products/transfer_manifest_op.json)
- [Primary HTTP source manifest](../../../raw/eth/2026-10-04/strict-products/http_manifest.json)
- [Final raw-file hash manifest](../../../raw/eth/2026-10-04/strict-products/all_captures_manifest.json)

Each product provides `keyMetrics`, `moneyFlow`, `actors`, `incomePayers`, `timeline`, `sources`, `limitations` and the `liveRoute` overlay. Chart keys are `capitalHistory`, `returnVsBorrow`, `walletDistribution` and `loanLegs`. Dated return rows use `ethBookPrice`, `cumulativeReturnPct`, `borrowAPR_pct` and `borrowScope`. Separate `windowReturns` are end-at-T intervals, so they are never used as dates on a time-series axis. Wallet bins include `chain`, `holders`, `shares`, `capitalETH` and `shareOfSupplyPct`; named `topHolders` retain exact address links. Loan rows explicitly identify whether values are protocol oracle balances, nominal dollar units, shared custody or cached position accounting.

Raw historical strategy-allocation percentages remain null. Whole managed books are not all carry. The canonical financial census and original input hashes have not been rewritten by these chapters.


## Additional carry books: fixed-block reconstruction

The final census includes **13 carry-linked books**, of which **10 have current traced routes**. Lido Earn and Avant enter the five largest examined books. Makina DETH, Vesper and ZenSats add distinct smaller routes. Whole books, dollar loans, investment claims and carry equity are kept separate.

## Lido Earn ETH

Earn ETH reports 83,309 ETH. Its main holding is stRATEGY, whose book must not be added again. The nested portfolio owes about 355,217 WETH in staking loops and 25.55M USDT in its main dollar-carry account. Those are gross loans, not the carry sleeve’s equity.

**Separate the WETH loop from the USDT investment before judging income or liquidation risk.**

### Buy the outer ETH claim

Deposits enter the outer queue. Oracle processing allocates shares, which can remain unclaimed. Total shares, rather than minted supply alone, form the reported book.

### Follow the nested holding

The main subvault holds 79,267 strETH shares. stRATEGY reports 84,664 ETH, but almost all its shares are already represented inside Earn ETH. Count the outer book once.

### Keep ETH loops separate

Aave and Spark WETH borrowing totals about 355,217 ETH. Health factors are 1.035 to 1.039. These loops depend on collateral conversion and funding; they are not dollar carry.

### Borrow dollars in the carry account

The separate account owes 22.240M USDT on Aave and 3.313M USDT on Spark. Their health factors are 2.124 and 2.488. Loan cost accrues in USDT even when the investor holds an ETH claim.

### Invest in the dollar vault

That account holds 24.726M earnUSD shares. The oracle reports shares per asset: invert its six-decimal USDT price to value the claim. Share growth and changing deposits must be separated.

### Apply the fee layers once

The outer fee settings are 15% of performance and 0.20% annually. stRATEGY and earnUSD settings are zero at T. Fees already recognised in the reported share price are not deducted again.

### Exit through two liquidity decisions

EarnUSD must provide dollar liquidity so the carry account can repay USDT; the outer vault must then settle the investor’s ETH redemption. Oracle pricing and liquidity settlement are separate steps. A quoted NAV is not immediate cash.

| Borrowing venue | Debt currency | Actual / stored debt units | Health factor | Scope |
| --- | --- | --- | --- | --- |
| Aave V3 | WETH | 80,273.396053 | 1.037610 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Aave V3 | WETH | 112,309.585558 | 1.035453 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Spark V3 | WETH | 162,634.511886 | 1.039044 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Aave V3 | USDT | 22,239,666.457473 | 2.124397 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Spark V3 | USDT | 3,313,137.709644 | 2.487729 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Aave V3 | USDC | 2,356.026137 | 1.028057 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |

**Holder distribution:** 2,500 on Ethereum. All Transfer events from block 0 through T reconcile exactly to archived issued totalSupply. Contracts count as addresses, not people. The outer book additionally includes 788.324 allocated, unclaimed shares; these are outside the issued-token distribution.

**Size convention:** Oracle-valued ETH claim; includes allocated, unclaimed shares. **Matched claim return:** +0.2513% from 2 September to 2 October 2026.

**Fee and exit detail:** 15% performance + 0.20% annual outer fee; nested stRATEGY and earnUSD settings are zero.

| Actor | Control |
| --- | --- |
| Outer fee owner | Controls the outer fee-manager settings; owner and fee recipient are distinct |
| Carry account | Executes the separately traced Aave / Spark USDT position |
| Oracle and curators | Authorised reports price claims; curators arrange swaps and queue liquidity |

**Evidence limits:** The outer ETH oracle mark is about 17 hours old at T; this is a reported claim, not an independently recomputed exit NAV. Loop loan balances are gross and cannot be used as carry-equity weights. The earning period, borrower mix and incentive sponsor inside earnUSD require further look-through before calling all share growth organic income.

[Official deployments and strategy documentation](https://docs.lido.fi/earn/deployment-contracts/), [Fixed-block share contract](https://etherscan.io/address/0xBBFC8683C8fE8cF73777feDE7ab9574935fea0A4), [Reconstruction, timestamps and source hashes](../../../data/eth/finalization_reconstruction.json), [Launch, ownership and economics reconstruction](../../../data/eth/parity_depth_measurements.json), [Product development and measured findings](PRODUCT-EVOLUTION.md).

## Avant avETH / savETH

The published 29 September portfolio has a $33.18M net NAV and a $32.53M savUSD position. Ethereum reads at T confirm USDC, USDS and PYUSD borrowing against ETH collateral. The large own-credit destination makes this a concentrated issuer dependency.

**A second product from the same issuer does not create independent credit diversification.**

### Distinguish the token claims

avETH is the issuer’s nominal ETH liability. savETH is a senior staking claim on avETH. The book-size row uses avETH supply; the return row uses savETH conversion. They do not describe the same investor right.

### Post ETH collateral

A listed strategy wallet has WETH, wstETH and weETH supplied on Ethereum. At T its Aave health factor is 1.382 and Spark health factor 1.370.

### Borrow several dollar currencies

The traced wallet owes 2.211M USDC on Aave, plus 7.322M USDS and 0.502M PYUSD on Spark. Repayment requires those specific tokens, not merely any dollar balance.

### Follow the published investments

The latest saved allocation is dated 29 September, three days before T. It includes 32.535M dollars of savUSD plus avUSD, credit receipts and stablecoin liquidity. This disclosure is dated separately from the fixed-block debt.

### Look through the issuer relationship

savUSD and avUSD are Avant claims. The dollar portfolio’s borrower credit, reserve backing and valuation affect the ETH product through this link. The roughly 98% savUSD / net-NAV ratio is a concentration indicator, not a carry-allocation percentage.

### Assign income to the tranche

Senior savETH receives income under its distribution and vesting rules. Issuer NAV growth, junior income and a senior conversion return cannot be substituted for one another.

### Complete the redemption chain

savETH has a one-day cooldown at T. Converting it to avETH is one step; receiving final ETH still depends on avETH redemption, reserve liquidity and strategy unwinds. The cooldown does not guarantee the whole exit.

| Borrowing venue | Debt currency | Actual / stored debt units | Health factor | Scope |
| --- | --- | --- | --- | --- |
| Aave V3 | USDC | 2,211,129.911781 | 1.381984 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Spark V3 | USDS | 7,322,116.673908 | 1.369821 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Spark V3 | PYUSD | 501,530.013453 | 1.369821 | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |

**Holder distribution:** 37 on Ethereum. All Transfer events from block 0 through T reconcile exactly to archived issued totalSupply. Contracts count as addresses, not people. Issuer face-token ownership is different from savETH senior-tranche ownership.

**Size convention:** avETH face supply; returns belong to the senior savETH claim. **Matched claim return:** +0.3385% from 2 September to 2 October 2026.

**Fee and exit detail:** Senior savETH conversion measured; fee rights depend on the mint, redemption and tranche contracts.

| Actor | Control |
| --- | --- |
| Issuer and NAV process | Publishes portfolio NAV and distributes income; disclosure is dated |
| Traced Ethereum strategy wallet | Holds collateral and debt on Aave and Spark |
| savETH contract | Controls senior conversion, vesting and cooldown state |

**Evidence limits:** avETH face supply is not an independently verified reserve NAV. The fixed-block Ethereum loans do not reconstruct all cross-chain weights at T. The common 30-day return belongs to savETH’s senior claim; it is not whole-issuer or organic carry profit.

[Official deployments and strategy documentation](https://docs.avantprotocol.com/security/contract-addresses), [Fixed-block share contract](https://etherscan.io/address/0x9469470C9878bf3d6d0604831d9A3A366156f7EE), [Reconstruction, timestamps and source hashes](../../../data/eth/finalization_reconstruction.json), [Launch, ownership and economics reconstruction](../../../data/eth/parity_depth_measurements.json), [Product development and measured findings](PRODUCT-EVOLUTION.md).

## Makina DETH

DETH reports 2,499 ETH in a cached book. Its hub has 15,065 WETH of Aave debt against weETH, plus a Morpho USDT / wstETH carry route. Verified accounting instructions identify the credit receipts instead of relying on the vault name.

**The biggest gross position is an ETH loop; the USDT route has separate currency and exit risk.**

### Start with the machine book

DETH shares reference a WETH-accounted machine. The last reported AUM is 2,499 ETH. Its accounting timestamp is about 14.5 hours before T.

### Inspect the actual accounting instructions

The saved accounting transaction decodes 15 positions, their debt flags, commands and affected tokens. This identifies what the machine values and prevents classifying every position as carry.

### Separate the dominant loop

The hub owes 15,065 WETH on Aave and supplies 15,110 weETH units. The gross borrowed ETH is leveraged restaking exposure; it is not new investor capital or a dollar loan.

### Trace the dollar route

A Morpho wstETH / USDT market has 279.57 wstETH collateral and about 384,701 USDT of stored indexed debt before pending interest. The small USDC loan is a different position.

### Identify the investment claim

Accounting includes senPYUSDmain and nested DQAeETH / DCM shares. USDT funding and a PYUSD destination introduce currency sourcing and borrower credit. The whole receipt cannot be assigned to a single loan without transaction allocation.

### Respect stale and cross-chain state

The fresh accounting getter rejects stale positions. Cached AUM is retained as a book observation. Configured spokes do not prove substantial deployments: the reported spoke balances at T are negligible.

### Use the redemption module

Selling a DETH share and redeeming through the machine are different routes. A complete unwind needs updated accounting, the configured redeemer and sufficient hub liquidity, including repayment of both WETH and dollar debts.

| Borrowing venue | Debt currency | Actual / stored debt units | Health factor | Scope |
| --- | --- | --- | --- | --- |
| Aave V3 | WETH | 15,064.646059 | Different model / not independently measured | Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry. |
| Morpho USDT / wstETH | USDT | 384,701.113736 | Different model / not independently measured | Stored indexed debt before pending interest. This is a distinct dollar route from the larger Aave WETH loop. |

**Holder distribution:** Not independently replayed. A complete all-transfer holder replay at T is not included for this additional product; the report does not replace it with a current holder count.

**Size convention:** Cached reported ETH book; accounting timestamp retained. **Matched claim return:** +0.3468% from 2 September to 2 October 2026.

**Fee and exit detail:** Machine fee manager and redemption module identified; quoted book is a cached accounting value.

| Actor | Control |
| --- | --- |
| Machine | Sets the reported share book and connects fees, depositor and redeemer modules |
| Hub Caliber | Executes and accounts for permitted investment positions |

**Evidence limits:** A cached book is not an executable fresh NAV. Morpho stored debt requires pending-interest treatment before final repayment sizing. Nested receipts and debt do not establish a uniquely attributed carry-equity amount.

[Official deployments and strategy documentation](https://docs.makina.finance/strategies/deployments), [Fixed-block share contract](https://etherscan.io/address/0x871aB8E36CaE9AF35c6A3488B049965233DeB7ed), [Reconstruction, timestamps and source hashes](../../../data/eth/finalization_reconstruction.json).

## Vesper vaETH

vaETH reports 1,052 ETH. Its XY strategy supplies 57.35 WETH, owes 68,998 DAI and holds 60,034 vDAI shares. Other strategies in the same pool are lending or liquidity positions, so the whole pool cannot be labelled carry.

**The strategy’s actual dollar loan is different from its pool-accounting allocation.**

### Hold a share of the ETH pool

vaETH shares represent the combined pool book. The eight registered strategies include lending, nested pools, liquidity and a dollar-carry route.

### Select the funded XY strategy

The funded AaveV3_Vesper_Xy_ETH_DAI strategy posts WETH. Another registered ETH / DAI strategy has zero actual debt at T; an active flag alone does not establish deployment.

### Read the lender liability

The XY account’s variable DAI debt is 68,998 DAI. The pool accountant’s totalDebtOf is the allocation owed to the ETH pool, not the DAI loan amount.

### Value the dollar investment

The account holds 60,034 vDAI shares. The archived share price is 1.148609 DAI per share. Multiply to value the destination; keep VSP and other externally paid rewards separate.

### Account for flows before income

During the matched 30 days both the loan and vDAI share balance fell materially. A simple end-minus-start balance would confuse withdrawals with losses.

### Return income to the ETH book

Dollar yield after DAI interest and strategy costs supports the ETH pool. The pool’s observed 30-day ETH share gain is a different measure from carry-only profit.

### Unwind the lending route

Redeem vDAI, source and repay DAI, withdraw WETH collateral and provide ETH-pool liquidity. A destination share price does not guarantee redemption at the required size.

| Borrowing venue | Debt currency | Actual / stored debt units | Health factor | Scope |
| --- | --- | --- | --- | --- |
| Aave V3 → Vesper vDAI | DAI | 68,998.302816 | Different model / not independently measured | Actual variable DAI loan. PoolAccountant strategy allocation is a different quantity. |

**Holder distribution:** Not independently replayed. A complete all-transfer holder replay at T is not included for this additional product; the report does not replace it with a current holder count.

**Size convention:** Reported ETH pool book; carry is one strategy. **Matched claim return:** +0.0698% from 2 September to 2 October 2026.

**Fee and exit detail:** Pool universalFee is 100 bps at T; strategy and realised profit fees require the pool’s fee formula.

| Actor | Control |
| --- | --- |
| ETH pool | Issues shares and combines strategy accounting |
| Funded XY strategy | Manages WETH collateral, DAI debt and vDAI shares |

**Evidence limits:** Carry is one strategy in a mixed pool. Dollar share growth excludes unassigned external reward cash. Pool-reported NAV, loan interest and investor exit cash answer different questions.

[Official deployments and strategy documentation](https://docs.vesper.finance), [Fixed-block share contract](https://etherscan.io/address/0xd1C117319B3595fbc39b471AB1fd485629eb05F2), [Reconstruction, timestamps and source hashes](../../../data/eth/finalization_reconstruction.json).

## ZenSats wstETH

The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category.

**Use frozen balances to distinguish a live micro-position from an empty legacy design.**

### Use the active deployment

The active vault differs from the withdraw-only legacy deployment. Archived supply and assets establish which book is funded.

### Post staking collateral

The loan manager supplies wstETH. Staking income remains on the collateral while the loan is denominated in crvUSD.

### Borrow with soft liquidation

LlamaLend converts collateral exposure across price bands during soft liquidation. Its risk cannot be expressed as an Aave health factor.

### Supply dollar liquidity

The strategy invests crvUSD in the crvUSD / USDT pool and StakeDAO route. Trading fees, inventory changes and incentives contribute differently to its result.

### Compare the dollar claim with debt

The saved strategy value is about 951 crvUSD against 953 crvUSD of debt. This snapshot comparison does not by itself establish full realised profit, including collateral staking and rewards.

### Keep the legacy product separate

The old Aave / RAAC route is withdraw-only in documentation and has zero share supply / assets at T. Do not add its historical design as current funded capital.

### Exit in the debt currency

Withdraw or rebalance the liquidity position, source crvUSD, repay the controller and release wstETH. Soft-liquidation inventory and pool liquidity determine actual proceeds.

| Borrowing venue | Debt currency | Actual / stored debt units | Health factor | Scope |
| --- | --- | --- | --- | --- |
| Curve LlamaLend | crvUSD | 952.791888 | Different model / not independently measured | LlamaLend soft-liquidation mechanics differ from Aave health factor. |

**Holder distribution:** Not independently replayed. A complete all-transfer holder replay at T is not included for this additional product; the report does not replace it with a current holder count.

**Size convention:** Reported wstETH managed assets converted to ETH; not independently netted carry equity. **Matched claim return:** +0.2480% from 2 September to 2 October 2026.

**Fee and exit detail:** Configured vault fee settings are zero at T.

| Actor | Control |
| --- | --- |
| Active vault | Issues the current wstETH-accounted claim |
| Loan manager | Manages the LlamaLend collateral and crvUSD debt |
| Yield strategy | Holds the dollar investment claim |

**Evidence limits:** This micro-position is included for route completeness, not evidence of large carry-market capital. Reported managed assets are not independently netted carry equity. No complete reward-adjusted investor cash return is claimed.

[Official deployments and strategy documentation](https://www.zensats.app/llms-full.txt), [Fixed-block share contract](https://etherscan.io/address/0x23F189dE34EED95f6303CfF1C77f7676F211Dd2c), [Reconstruction, timestamps and source hashes](../../../data/eth/finalization_reconstruction.json).


<!-- substantive-parity -->

## Product history behind the snapshot

Liquid’s stablecoin borrowing predates its current Morpho routes: Aave USDC financing is observed in August 2025. Its 18M PYUSD cohort is negative after funding under three explicit withdrawal conventions, before rewards and other costs. Cash Hub ownership now resolves to 7,012 positive account positions. Lido’s current wrapper follows its November 2025 underlying strategy; its April crisis required a 27-day pause and DAO loss absorption. YieldBasis’s present LT history starts after an earlier WETH pool, and gauge investors have different income rights from unstaked holders. Avant’s senior holder analysis traces Gearbox and Morpho custody instead of treating their contracts as single investors.

[Full product development, accounting assumptions and source evidence](PRODUCT-EVOLUTION.md).

<!-- economic-answers -->
## Current financing comparison

| Product | Direct dollar debt at T | Debt-weighted quoted APR | Whole book ETH | Scope |
| --- | --- | --- | --- | --- |
| ether.fi Liquid ETH | $181,084,944 | 7.79% | 177,171 | attributed product account / direct loan |
| YieldBasis WETH | $27,814,856 | 10.00% | 10,426 | attributed product account / direct loan |
| Lido Earn ETH | $25,555,160 | 4.33% | 83,309 | attributed product account / direct loan |
| Avant avETH / savETH | $10,034,777 | 6.30% | 12,583 | attributed product account / direct loan |
| Liquity ETH Carry | $6,752,065 | 2.55% | 6,014 | attributed product account / direct loan |
| NEMO ETH Prime | $5,611,801 | 4.75% | Not reconstructed | attributed product account / direct loan (vault book reconciles with the loan) |
| Rocksolid rETH | $2,727,060 | 4.61% | 9,728 | attributed product account / direct loan (second strategy wallet) |
| Sentora ETH | $1,163,324 | 11.79% | Not reconstructed | attributed product account / direct loan (vault book reconciles with the loan) |
| Makina DETH | $384,701 | 3.21% | 2,499 | attributed product account / direct loan |
| Royco ETH | $90,891 | 30.24% | 116 | attributed product account / direct loan |
| Vesper vaETH | $68,998 | 5.00% | 1,052 | attributed product account / direct loan |
| Reservoir ETH Yield | $36,790 | 13.93% | Not reconstructed | attributed product account / direct loan |
| TAU InfiniFi ETH Carry | $0 | Unavailable | Not reconstructed | attributed product account / direct loan |


The principal five are ordered by attributed direct dollar financing. Monthly quotes and whole-book ETH returns measure different units. Concrete is an unresolved case, not a verified member of the five. [Economic answers and historical debt](ECONOMIC-ANSWERS.md).
