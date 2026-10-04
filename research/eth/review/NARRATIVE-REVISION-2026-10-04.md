# ETH presentation: narrative revision, 4 October 2026

This is an editorial proposal based on existing captured evidence. It changes no financial input, date, market classification or accounting result. The contract snapshot remains 2 October 2026, 23:59:59 UTC. Adapter observations and later interface or document captures retain their own dates. All suggested reader copy is in English.

## The editorial conclusion

The ETH research has enough substantive findings to support a presentation at the BTC site's level. The main weakness is the order in which the reader encounters them. New verified findings sit below repeated descriptions of coverage, product classification and incomplete reconstruction. Several older explanatory blocks repeat the same mechanisms or retain routes superseded by the fixed-block product investigation.

The presentation should develop one argument:

> ETH already earns staking income. Borrowing and dollar credit can add income, but the extra return must survive funding costs, fees and the exit. The market history shows where these claims sit. The product evidence shows what investors actually hold. Those findings determine how a new product should be designed.

The BTC site succeeds because each chapter advances its argument with new evidence. Its funding example leads to the product findings; each product supplies a different lesson; observed risks turn into design requirements. Preserve that explanatory structure. The BTC claims about subsidy dependence, distribution, campaign funding and the completeness of its carry census do not automatically apply to ETH.

Reviewed BTC sources: the eight sections in [the actual BTC presentation](../../../site/index.html), including `#top`, `#map`, `#how`, `#top5`, `#market`, `#risks`, `#do` and `#data`, plus its dynamic `RISKS` records. Reviewed ETH sources: [the ETH HTML source](../../../tools/eth/site/index.html), [strict chapter renderer](../../../tools/eth/site/strict.js), [market renderer](../../../tools/eth/site/market.js), [market chapter data](../../../data/eth/research_market_chapter.json), [product chapter data](../../../data/eth/product_chapters.json), [carry economics](../../../data/eth/carry_economics_chapter.json), [monthly funding history](../../../data/eth/carry_borrow_rate_history.json), and the English reports cited below.

## Opening and four headline measures

Suggested title:

> ETH yield: what earns the extra return?

Suggested opening:

> Staking is the starting point for ETH yield. Products then add borrowing, dollar lending, liquidity provision or other claims to earn more. We follow the capital, compare the extra income with its funding cost, and examine what a holder can withdraw.

Suggested hero measures:

| Number | Label | Required adjacent context | Evidence |
|---|---|---|---|
| 21.16M ETH equivalent | Selected yield exposure | $57.21B across the default selected categories. Layered claims can overlap. This is observed exposure, not unique ETH deposited. | `research_market_chapter.json`: `default_current.eth_ref`, `default_current.usd`, `default_selection` |
| 95.4% | Staking and restaking share | Share of the selected default exposure. Issuer and restaking layers can contain claims on the same underlying ETH. | `current.by_category.staking.eth_ref / default_current.eth_ref` |
| -7.11% | Two-year change in the same protocol set | Oct 2024 to Sep 2026, holding 47 default-category protocols fixed. | `chart_points[0]` and `chart_points[23]`, sum of each selected category's `constant_cohort.eth_ref` |
| -0.84 pp | Carry contribution without rewards | Annual scenario per ETH of equity, before the outer management fee. Uses the observed RLUSD loan and a separately dated destination quote. | `carry_economics_chapter.json`: `worked_example.modeled_income`, `playbook.scenarios[0].result.no_reward_carry_uplift_before_outer_fee` |

The fourth measure deliberately isolates the extra carry contribution. The existing +1.09% scenario includes a staking baseline and a 0.35% annual NAV fee. If the existing tile is retained, label it **Total modeled income without destination rewards**, with **Includes staking** beside the number. Do not call it reward-free carry yield.

Keep one compact scope line beneath the hero:

> Financial snapshot: 2 October 2026. Market history covers 24 completed months. The market measure contains overlapping claims; product returns measure ETH-denominated book value. Later quotes and published terms are dated separately.

Suggested three opening conclusions:

> **Staking supplies the baseline.** Staking and restaking account for 95.4% of the default selected exposure. The same 47-protocol set falls 7.11% over the two-year window. Changes in coverage and claims affect the apparent market trend.

> **The extra spread can disappear.** The measured RLUSD loan costs more than the destination's reported organic yield. Rewards make the illustrated spread positive, while a fully utilized funding market can raise the cost sharply.

> **A share price is only part of the product.** Liquid adds 1.36 percentage points over stETH in two years. Other products introduce shared custody, nested vault claims or stale position marks. Fees, control and the exit route determine what that return means to a holder.

## Eight chapters and exact reader copy

### 1. Answer: establish the question

Use the opening and three conclusions above. The opening should answer what the research found before describing how much work was done. Keep the full research scope and audit record in Data.

Transition:

> First, locate the exposure. Then separate the staking income from the strategies built around it.

### 2. Market: show scale, then explain the change

Suggested chapter title:

> Staking dominates the observed market. Coverage changes its apparent growth.

Suggested lede:

> The default market view contains 21.16M ETH equivalent of observed exposure, worth $57.21B at the adapter reference quote. Staking and restaking dominate this view. Lending markets and collateralized debt positions are available as separate layers because they can reuse claims already counted elsewhere.

Place the default category chart and the two-year history next to these findings:

> **The changing set falls 5.13%.** From October 2024 to September 2026, default selected exposure moves from 22.32M to 21.17M ETH equivalent. Holding the same 47 protocols fixed produces a larger decline of 7.11%, from 22.30M to 20.72M. The difference shows why new coverage and new claims need to be distinguished from growth in the same products.

> **The carry-parent trend changes with the comparison.** The two-parent hybrid category rises 53.88% across the completed-month window. The one parent with continuous observations falls 54.29%. The rising category total therefore does not establish inflows into existing carry strategies. It also measures whole protocol parents, whose books include other strategies.

> **Lending grows while some product claims shrink.** The observed lending category rises 48.47% over the same window. The selected fixed-yield balances fall 96.74%. These are movements in the measured claim categories. They do not establish that every fixed-yield position redeemed, or that new lending exposure represents new ETH entering the system.

Required short chart caption:

> ETH equivalents are the selected ETH-family dollar balances divided by the same-date ETH reference quote. They express market value, not independently verified physical ETH backing. Signed debt remains visible. Missing observations remain missing.

All three findings come from [market chapter data](../../../data/eth/research_market_chapter.json), `chart_points[0]`, `chart_points[23]`, `by_category` and each category's `constant_cohort`. Default categories are `staking`, `loops`, `carry`, `basis`, `fixed_yield` and `farming`. The staking share uses the current default denominator. The fixed cohort contains 47 protocols across those categories. These measures must not be replaced by the broader 64-protocol cohort or the endpoint-common 67-protocol comparisons, which include optional layers or different inclusion rules.

Put the protocol search and chain view after the two main charts. Explain large chain rows through the same selected token-exposure data. Keep mixed full-pool TVL screens inside a separate discovery drawer. The 93.69% Ethereum figure from a mixed-pool screen is not the chain distribution of unique ETH or of this canonical market measure.

Fold issuer context, overlap examples, adapter lifecycle, dated native staking context and the pool catalogue into expandable evidence. The unmeasured basis category should say **Capital at the snapshot is not measured**, rather than displaying a zero allocation.

Transition:

> A market label does not identify the income source. ETH loops and dollar carry borrow different assets and respond to different risks.

### 3. Carry math: explain two balance sheets, then one actual loan

Suggested title:

> ETH loops amplify staking. Dollar carry adds a separate credit spread.

Suggested opening mechanism copy:

> **An ETH loop** deposits a staking token, borrows ETH, and stakes or deposits that ETH again. The extra income depends on the staking return exceeding the ETH borrowing cost. Both sides are linked to ETH, but collateral-token discounts, rate changes and a forced unwind can still hurt the holder.

> **Dollar carry** deposits ETH collateral, borrows a dollar token, and invests the borrowed dollars. The holder keeps ETH exposure and adds the investment yield minus the dollar borrowing cost. A fall in the collateral price can trigger liquidation even when the dollar investment keeps its book value.

Use one pair of simple flows, one worked RLUSD ledger, the funding-versus-investment bars, the actual curve selector and one seven-input calculator. The later 100-ETH toy example and second carry calculator repeat this explanation and should move to the mechanism library.

Suggested lead to the measured example:

> Liquid ETH's main account and LoanManager hold 37,046.19 weETH in the examined RLUSD market and owe 70.21M RLUSD at the snapshot. The product also holds a 55.10M RLUSD book claim in the destination vault. Those observations establish the loan and investment balances. A transfer ledger is still needed to show how much of that borrowing funded the destination.

Suggested rate interpretation:

> The loan quote is 4.21% APR, or 4.30% on the annual cost convention used here. The 3 October destination feed reports 3.00% organic APY and 2.59% reward APY. Organic yield alone falls below the funding cost. With all borrowed dollars invested at that rate, the carry contribution is -0.84 percentage points per year per ETH of equity before the outer fee. Including the staking baseline and the 0.35% annual NAV fee gives 1.09% total modeled income without destination rewards, versus 2.75% with them.

Suggested historical funding takeaway:

> **A snapshot hides the funding path.** The main RLUSD account is funded in the July, August and September month-end samples. Its quoted APR is 3.60%, 3.76% and 16.68%, respectively. September utilization reaches 100%. The October snapshot rate is lower. These are point-in-time costs on the loan principal, rather than monthly average costs or whole-product returns.

Suggested curve caption:

> The curves use the verified interest-rate models and parameters of the selected markets. They show how quoted funding responds to utilization. A current quote does not reserve financing at that rate or guarantee cash for a later repayment.

Evidence: [carry economics](../../../data/eth/carry_economics_chapter.json), `worked_example.measured_leg`, `worked_example.modeled_income`, `destinations`, `borrow_markets` and `calculator`; [monthly loan quotes](../../../data/eth/carry_borrow_rate_history.json), `rows` for `Morpho Blue` in `2026-07`, `2026-08` and `2026-09`; [English carry math](../en/CARRY-MATH.md); [independent funding review](CARRY-BORROW-HISTORY.md). Keep the null pre-funding observations in charts. The separate Aave WETH series is an ETH-loop funding benchmark, not a dollar-carry history.

Transition:

> The worked loan explains the economics of one sleeve. Whole products combine several sleeves, fee layers and withdrawal paths. The five largest measured books show how different those combinations can be.

### 4. Top 5: give every product a distinct finding

Suggested chapter title:

> Five product books, five different investor questions.

Suggested lede:

> We rank these products by whole-product ETH book NAV at the snapshot. The ranking includes hybrid strategies, shared custody and claims on other vaults. It describes the size of the published books; it does not measure five independent pools of carry equity.

The comparison table belongs at the start. Product details should then open with a finding, followed by the capital flow, who earns or pays, the return and funding history, holders, controls, exits and dated events. Put shared accounting definitions once above the table. Product-specific unresolved issues remain beside the affected claim.

#### Concrete Delta weETH: a large book claim needs a custody and payout reconciliation

Suggested product opening:

> Concrete Delta publishes the largest book in this group: 307,362.93 ETH, or $820.03M. One address holds the entire share supply at the snapshot. The initial share issuance does not contain an underlying-token transfer, and the weETH book price stays at 1 across the captured history. Its measured ETH book growth therefore follows weETH's staking conversion. Private arbitrage income and payouts need separate evidence.

> The strategy leads to a shared 3-of-5 Safe with verified borrowing. The Safe also serves another product, so its entire collateral and debt cannot be assigned to Delta. To understand the investor claim, the book needs to be matched to attributable custody assets and the governing payout agreement.

Product lesson:

> Before treating a large book as new investor capital, reconcile issuance, attributable assets and the rights attached to the shares.

Evidence: [Concrete dossier](../en/dossiers/concrete-eth.md); [product data](../../../data/eth/product_chapters.json), product `concrete`, `limitations`, `liveRoute`, `snapshotEvidence`; share contract [verified source](https://etherscan.io/address/0xb9dc54c8261745cb97070cefbe3d3d815aee8f20#code). Avoid implying that an issuance without the underlying transfer proves absent assets, fraud or insolvency.

#### Liquid ETH: a modest two-year excess sits beside substantial borrowing

Suggested product opening:

> Liquid ETH combines ETH staking loops with dollar borrowing and lending. Its ETH book value rises 6.85% over two years, compared with 5.49% for stETH, an excess of 1.36 percentage points. At the snapshot, its main Aave ETH loop holds $1.18B of collateral against $1.09B of debt. Gross collateral is 13.3 times that account's equity, and its health factor is 1.027.

> The two-year return and the current account leverage answer different questions. Current positions do not explain every historical return. They do show why a small change in funding can matter: with balances fixed, a one-percentage-point rise in the ETH borrowing rate reduces the isolated account's annual equity return by about 12.32 percentage points before offsets.

Follow with the strongest funding and credit evidence:

> The dollar destinations add other credit exposures. The examined RLUSD lender supplies 52.89% of its book to a kBTC market and 24.09% to weETH. The PYUSD lender supplies 95.04% to PRIME, whose disclosed underlying business includes home-equity financing. These sources of income extend well beyond demand for Ethereum staking.

Product lesson:

> Judge the incremental ETH return together with each borrowing account, the destination's borrowers and the cash needed for an unwind.

Evidence: [Liquid dossier](../en/dossiers/etherfi-liquid-eth.md), positions, destination books and benchmark table; [market research](../en/MARKET-RESEARCH.md); [return drivers](../en/RETURN-DRIVERS.md); product `liquid` in [product data](../../../data/eth/product_chapters.json). Annual ETH-loop rate stress is an isolated sensitivity, not an observed loss or a dollar-carry liquidation estimate. The 13.3x ratio belongs to the main Aave account, not the whole vault.

#### Rocksolid rETH: carry can sit inside another carry product

Suggested product opening:

> Rocksolid holds 748.64 shares of Liquity ETH Carry, with a book value of 728.48 ETH. That claim represents 7.49% of Rocksolid's book at the snapshot. Its captured direct Aave account has no debt. The verified carry exposure is therefore partly nested inside another product, whose underlying Ebisu loan belongs to that product.

> An August report describes a different combination of carry and looping. That dated allocation helps explain the strategy's history, but it does not replace the snapshot position. Returns measured in rETH also need the rETH-to-ETH staking conversion to become comparable with an ETH benchmark.

Product lesson:

> Look through nested vault shares. Count the outer claim and the underlying book as separate layers of the same exposure.

Evidence: product `rocksolid`, `nestedCarryClaim` and `liveRoute` in [product data](../../../data/eth/product_chapters.json); verified [underlying share contract](https://etherscan.io/address/0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c#code). The 7.49% is a share of the outer book, not a verified pure carry allocation.

#### Liquity ETH Carry: the active loan matters more than the product name

Suggested product opening:

> At the snapshot, Liquity ETH Carry uses an Ebisu loan and an active Uniswap V4 configuration. Its Trove holds 4,585.48 wstETH and owes 6.75M ebUSD at a 2.55% borrower-set annual rate. The earlier BOLD and Curve description does not describe this active route. Upfront or rate-adjustment charges remain additional to the quoted annual rate.

> The book first has funded observations in March. January and February return an initialized share price of 1 with no supply, so those empty observations are not an investor return baseline. The one-second redemption delay is a deposit lock; it does not promise a one-second collateral unwind or withdrawal.

Product lesson:

> Verify the current collateral, loan token and investment route, then start the return series when the product is funded.

Evidence: product `liquity`, `liveRoute`, `marketBooks`, `idleBalances`, `limitations` and `snapshotEvidence` in [product data](../../../data/eth/product_chapters.json); the [Ebisu Trove manager](https://etherscan.io/address/0xa2895d6a3bf110561dfe4b71ca539d84e1928b22#code) and [vault source](https://etherscan.io/address/0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c#code). Active V4 fuse and substrate permissions establish configuration, while its complete LP value remains a separate valuation question.

#### Royco ETH: fresh position marks and book value can diverge

Suggested product opening:

> Royco ETH publishes a 116.05 ETH book held by eight addresses at the snapshot. Its wrapper leads through a Concrete adapter to a Makina machine and executor. All three recorded executor positions are marked stale, and calculating fresh net assets reverts. Immediate maxWithdraw returns zero at the examined layers.

> The documented withdrawal process is asynchronous. Zero immediate capacity does not establish a loss or permanent inability to withdraw. It does show why a published book price needs to be presented alongside the age of its position marks and the route to actual proceeds. The cached debt category does not identify the borrowing venue.

Product lesson:

> Publish the accounting timestamp and the withdrawal state next to the share price.

Evidence: product `royco`, `positionBook`, `cachedAccounting`, `exitGetters`, `liveRoute` and `limitations` in [product data](../../../data/eth/product_chapters.json); [Caliber source](https://etherscan.io/address/0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0#code). The current documentation's fee and service terms are reviewed on 4 October, separately from the T configuration.

Transition:

> These large books do not exhaust ETH yield. The wider comparison shows how the holding period and the exit can change the result.

### 5. Other carry: compare alternatives without flattening their mechanisms

Suggested title:

> The benchmark and the exit change the comparison.

Suggested opening:

> Over the matched two-year window, Fluid Lite's ETH book return is 8.82%, Liquid's is 6.85%, Treehouse's is 6.28%, stETH's is 5.49%, and CIAN rsETH's is 1.09%. Over one year, Liquid leads Fluid. The ranking depends on the holding period, and these book returns exclude separately distributed rewards and the cost of executing a complete exit.

Suggested exit-chart takeaway:

> **A small advantage can be spent on the exit.** Treehouse's one-year book return is 2.78%, against 2.48% for stETH. Applying one current 0.5% Fastlane charge to the final proceeds gives an illustrative 2.27% return. The standard 5-basis-point route gives 2.73%, with a published wait of about seven days. Capacity, payout rules and slippage still affect the executable outcome.

Keep the wealth chart and one exit illustration prominent. Move the repeated protocol-month history into Market. Keep ETH-loop products in a clearly named comparator group, rather than labeling every yield strategy dollar carry. Explain spot/short basis here with its own money flow; retain its unmeasured snapshot capital and any later quote date.

Suggested borrower-census caption:

> We sampled the largest borrowing positions in 25 Morpho markets. The sample contains 213 chain/address groups and 207 distinct addresses across chains. Borrowing dollars against ETH identifies a financing leg. It does not reveal the destination of those dollars or prove a public carry product.

Evidence: [market research](../en/MARKET-RESEARCH.md), return comparison; [return drivers](../en/RETURN-DRIVERS.md), exit-cost comparison and borrower boundaries; [product terms](../en/PRODUCT-TERMS.md), dated routes. Do not compare the product's historical net book return with a current gross rate as if they were the same period and measure.

Transition:

> The differences between these products become clearer when we ask what can interrupt the income or prevent its conversion into ETH.

### 6. Risks: organize concrete evidence around three investor outcomes

Suggested title:

> Funding, valuation and the exit are the three pressure points.

Suggested opening:

> The risks are visible in the measured positions and permissions. Funding can outgrow income. A book mark can be older than the assets it describes. A withdrawal can depend on another vault, a debt repayment or an operator action. Each needs a different control.

Suggested compact table:

| Pressure point | What the research observed | What the product needs to show |
|---|---|---|
| Funding and repayment | The RLUSD market reaches 100% utilization and 16.68% APR in the September sample. Liquid's main Aave ETH-loop debt exceeds that reserve's measured WETH cash. | Funding sensitivity, account-level headroom and a repayment route that fits available liquidity. |
| Marks and investor claims | Royco's three executor positions are stale. Concrete's large share book leads to shared custody with incomplete product attribution. Rocksolid holds another carry product's shares. | The mark timestamp, attributable assets, claim seniority and the handling of nested exposures. |
| Controls and withdrawal | Liquid's fee setter accepts both a timelock role and a separate operator role. Treehouse's normal exit is about seven days; its fast route costs 0.5%. | Function-level permissions, notice and emergency exceptions, plus a costed withdrawal path at material size. |

Evidence: [funding history](../../../data/eth/carry_borrow_rate_history.json); [Liquid dossier](../en/dossiers/etherfi-liquid-eth.md); [product data](../../../data/eth/product_chapters.json); [historical permission review](../../../data/eth/permissions_review_T.json); [product terms](../en/PRODUCT-TERMS.md). The debt-versus-cash comparison is a capacity constraint on a particular unwind source, not a forecast of exit failure.

Keep issuer or token incidents in a dated evidence drawer with their affected claims and status. An incident provides context for a risk; it is not automatically the cause of a product's historical loss. Avoid a second generic six-card risk inventory after the observed table.

Transition:

> A new product can use these observations as acceptance criteria before choosing its financing, investment and withdrawal partners.

### 7. Playbook: make design choices follow from the evidence

Suggested title:

> Design around the extra return and the path back to ETH.

Suggested opening:

> Start with the ETH staking benchmark. Then test whether the proposed borrowing and investment add enough income after funding, fees and a complete exit. A reward-funded spread needs a named budget and an expiry. Every debt account needs its own repayment plan. Every investor share needs an attributable claim and a settlement route.

The four existing tables should form a sequence: economics, payers, operating limits and partner roles. Suggested introductions:

| Table | Reader introduction |
|---|---|
| Scenarios | Start with the measured RLUSD leg. Remove destination rewards, raise funding costs, then compare an alternative reserve. The outputs are scenarios with explicit assumptions, not product forecasts. |
| Income and reward payers | Separate staking income, borrower interest and campaign rewards. An RLUSD or PYUSD reward token identifies the payment asset; it does not identify the sponsor or guarantee renewal. |
| Operating limits | Set limits per account and calibrate them to rates, collateral discounts and liquidity. A combined health factor can conceal the weakest account. The illustrative HF 1.25 floor requires calibration. |
| Partner roles | Assign a lender, investment manager, accountant, controller and exit provider to specific obligations. Current venue balances and quotes are evidence for diligence, rather than committed financing or a completed partner choice. |

Suggested closing design test:

> A product is ready to present when it can show the return above staking, the source and duration of that income, the assets attributable to its shares, and the sequence that turns those shares back into ETH. The research identifies where each of those claims is measured and where another piece of evidence is still needed.

Evidence: [carry economics](../../../data/eth/carry_economics_chapter.json), `playbook.scenarios`, `playbook.reward_payers`, `playbook.rules` and `playbook.partners`; [English carry math](../en/CARRY-MATH.md), Playbook section. Do not copy BTC's illustrative utilization or LTV limits into ETH as calibrated requirements. The seven-input calculator's liquidation module remains a simplified scenario, not Aave or Ebisu policy.

Transition:

> The final chapter records the definitions, dates and evidence behind those decisions.

### 8. Data: make the methods available without restarting the presentation

Suggested title:

> Definitions, dates and evidence.

Suggested opening:

> The financial snapshot is 2 October 2026, 23:59:59 UTC. Market adapters, contract states, issuer conversion rates and later published terms are different evidence types. Each keeps its source timestamp. Missing capital, rewards or permissions remain unmeasured.

Suggested three definitions:

> **Market exposure** is the signed value of selected ETH-family token balances across observed protocol layers. ETH equivalents use a same-date ETH reference quote. Parent and underlying claims can overlap, so this is not a unique-ETH total.

> **Book return** is the change in ETH-denominated value per share over matched timestamps. It includes income and fees recognized in the published accounting rate. Separately paid rewards, execution costs and realizable exit proceeds require their own records.

> **Carry scenario** combines a measured loan quote with a measured or separately dated destination rate and explicit allocation assumptions. It explains funding economics without attributing the whole product's return to that leg.

Organize downloads into four reader questions: market size and history; product positions and returns; funding and income sources; controls and exits. The detailed capture manifests, reconciliation checks and editorial records can sit beneath those groups. Avoid repeating the full source catalogue in earlier chapters.

Evidence: [market structure](../en/MARKET-STRUCTURE.md), [history method](../en/HISTORY.md), [carry math](../en/CARRY-MATH.md), [product terms](../en/PRODUCT-TERMS.md), and the structured datasets above.

## Copy to remove, replace or relocate

| Current pattern | Why it weakens the presentation | Specific treatment |
|---|---|---|
| Hero says to start with the market and follow ETH into products | Describes the page order without delivering a finding. | Replace with the staking-baseline opening and three evidence-backed conclusions. |
| Hero tile says carry scenario without rewards beside +1.09% | The result includes staking, so readers can infer a positive organic carry contribution. | Use -0.84 pp incremental contribution, or label the existing number total modeled income including staking. |
| Share in the two largest carry products | The denominator can be read as the carry market or unique investor capital. | Move into Top 5 and name the denominator: these five whole-product book NAVs. If using the seven-product census, label that separately. |
| Repeated product subtitle says E4 design confirmed, positions not fully reconstructed | Hides the new active-route evidence and makes five different products sound identical. | Use the five finding-led product openings above, followed by precise route status. Keep the classification badge in the comparison table. |
| Four identical limitations at the end of every product | The same accounting explanation becomes a wall of defensive copy. | State shared book-return and ranking definitions once. Keep Concrete custody, Rocksolid nesting, Liquity empty baseline and Royco stale marks beside their claims. |
| Earlier Liquity BOLD/Curve route and Rocksolid direct Aave carry route | They can contradict the newly measured T route. | Retain as dated historical descriptions within the timeline. Lead with Ebisu/V4 and the nested Liquity share claim. |
| Second What carry pays block and second calculator | Competing examples make the reader work out which one is the main model. | Keep one verified RLUSD example and one seven-input model. Place the older educational examples in the mechanism drawer. |
| Borrower sample, protocol histories and several similar vault tables in Other carry | Repeats Market and Top 5 without a new conclusion. | Lead with matched returns and the exit-cost ranking change. Keep the borrower census as a bounded discovery result. |
| Generic risk cards after the observed risk table | Repeats risk names without deepening the evidence. | Use the three pressure points and link their measured examples to the Playbook. |
| Generic Playbook bullets after four detailed tables | Restates the answer and dilutes the evidence-based design choices. | Replace with the short readiness test above. |
| Large source and audit catalogues distributed across chapters | Breaks the argument before the reader reaches its conclusion. | Keep a small source link near each main claim and group full records in Data. |

Location references: [HTML source](../../../tools/eth/site/index.html), sections `#top`, `#map`, `#how`, `#top5`, `#market`, `#risks`, `#do` and `#data`; [strict renderer](../../../tools/eth/site/strict.js), `strict-worked-example`, `strict-top5-comparison` and product-detail generation; [market renderer](../../../tools/eth/site/market.js), history findings and category controls.

## Comparisons and claims that must remain bounded

1. **A market measure is not a deposit census.** The default 21.16M ETH-equivalent measure contains issuer, restaking and product layers. The larger all-category total includes lending and CDP layers. Neither is global unique ETH or global net market NAV.
2. **A protocol-parent history is not a historical carry allocation.** The 501,340 ETH-equivalent adapter category uses two hybrid parents. The five-product ranking uses separately reconstructed product books and another ETH quote. Do not reconcile them as identical quantities.
3. **Concentration needs a named denominator.** The two largest products account for approximately 96.83% of the five listed books. The seven-product census produces approximately 96.81%. Neither is a measured global market share, and nested product claims overlap.
4. **Same-asset loop leverage is not dollar-carry LTV.** Liquid's Aave health factor 1.027 belongs to the ETH borrowing loop. Its main RLUSD and LoanManager health factors are separately measured. An aggregate scenario HF is not the minimum health factor of a product.
5. **APR and APY require an explicit convention.** The 4.21% loan APR is 4.30% on the annual cost convention used in the scenario. Compare it with destination APY on that convention, preserving the later destination date. Do not subtract one current rate from a two-year cumulative return.
6. **Positive total income does not establish positive carry.** The no-reward scenario retains staking and gives 1.09% total income. Its carry contribution is negative before the annual NAV fee.
7. **Growth in NAV does not establish outside deposits.** Liquid's monthly reconciliation separates the accounting-rate effect from the share-supply effect. Neither term by itself identifies investor flows or strategy attribution.
8. **Historical book marks are not cash exits.** A cached share-price series does not independently prove realization at that price. Royco's stale marks and zero immediate capacity require their own labels, without implying bankruptcy.
9. **Policy and function permissions are separate.** Liquid's owner has a 24-hour timelock; role 55 can also set its fee. Current terms, signer policies and code delays need exact function scope. Avoid a universal delay claim.
10. **Reward tokens do not identify campaign sponsors.** The captured fields do not prove that Ripple finances RLUSD incentives or that PayPal or Paxos finances PYUSD incentives. Funding wallet, budget, expiry and holder eligibility remain open.
11. **Liquidity coverage remains incomplete.** Four expected adapters lack usable current ETH-side observations, and the selected LP inventory is narrower than the whole liquidity market. A separate latest-pool screen is useful, but mixed pool TVL must not fill the historical token ledger.
12. **Lifecycle categories require event evidence.** Zero, missing or falling selected balances do not prove closure. An incident does not by itself explain an entire product return. The currently selected protocol history can miss products that disappeared before selection.
13. **BTC's conclusions require ETH evidence.** Do not import “carry is a subsidy,” “distribution wins,” a complete carry census, or calibrated BTC risk limits as ETH results. The ETH evidence supports a negative organic spread in the examined scenario and several concrete account, claim and exit constraints.

## Integration priorities

1. Replace the hero and market-history findings first. These establish the argument and correct the no-reward metric's interpretation.
2. Promote the five distinct product findings above each diagram. Remove identical limitation blocks and historical route conflicts from the main flow.
3. Keep one measured funding example, one curve panel and one calculator. Place extra mechanisms in an expandable library.
4. Make the exit-cost illustration the main comparison in Other carry and the three measured pressure points the main Risks view.
5. Connect each Playbook requirement to a measured observation, with an explicit status for proposals, later terms and unmeasured rights.
6. Retain all eight BTC-style chapters and every substantive dataset. Reduce repeated visible prose through evidence drawers, rather than discarding detail.

Editorial verification: proposed numeric copy was checked against the listed frozen structured inputs and English reports. The 47-protocol decline, category endpoint changes and concentration denominator are simple arithmetic on those captured values, not newly researched financial observations. No site, financial dataset or canonical report was changed by this audit. The suggested reader copy contains no em dash or en dash.
