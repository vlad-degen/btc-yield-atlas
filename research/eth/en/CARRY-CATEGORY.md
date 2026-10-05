# ETH carry: category composition and capital history

Document review: 5 October 2026. Financial snapshot: 2 October 2026, 23:59:59 UTC. Original interface and discovery captures: 3 October. The new archive reads in this review use the original snapshot and completed-month blocks. Current documentation is not treated as proof of every historical strategy allocation.

The carry section should follow the overall ETH market map and answer four questions: which products use ETH to finance dollar investments, how much capital each reports, where the borrowing and investment happen, and how those products have grown. Product mechanics and risk analysis then explain that map. A category composed only of five managed vaults misses documented carry products and includes products whose main mechanism is different.

Machine-ready product rows and monthly histories are in [carry_category_candidates.json](../../../data/eth/carry_category_candidates.json). The [source ledger](../../../data/eth/carry_category_sources.json) contains 20 scoped primary-source and discovery records. It distinguishes financial evidence at T, document observations, and current borrower screening.

## What belongs in this category

Here, **ETH-collateral dollar carry, E4**, means retaining ETH-family exposure as collateral, borrowing or minting a dollar liability, and deploying the dollars into an income-producing strategy. ETH collateral can be ETH, an LST or an LRT. The dollar investment can be lending, a stablecoin LP, a credit vault, a Senior tranche or a hedged arbitrage portfolio. A manager, a curator and a lending protocol are different roles in that route.

| Mechanism | Collateral and debt | Reinvestment | Category treatment |
|---|---|---|---|
| ETH-collateral dollar carry, E4 | ETH-family collateral; dollar debt | Dollar lending, credit, LP or neutral strategy | Include the verified carry sleeve or the product with a confirmed carry mandate |
| ETH debt loop, E3 | LST/LRT collateral; ETH or WETH debt | Buy more LST/LRT | Separate category; funding is ETH rather than dollars |
| Spot/short basis, E9 | Long ETH spot plus offsetting ETH short | Earn basis and funding | Separate category; ETH market exposure is hedged |
| Dollar loop | Stablecoin or dollar-yield collateral; dollar debt | More dollar-yield exposure | Exclude unless it is demonstrably a destination inside an ETH-collateral carry route |
| USD-funded directional ETH leverage | ETH collateral; dollar debt | Buy more ETH/LST | Separate leveraged ETH exposure, not the dollar-income reinvestment defined here |
| Unclassified ETH-denominated product | Denomination known; debt and hedges unknown | Broad or undisclosed strategies | Keep in the product universe with a pending mechanism label |

The word “carry” is used more broadly in finance and in some protocol descriptions. Consistent categories need the actual collateral, debt currency, reinvestment and hedge. Fusion's official examples make the distinction concrete: cbETH collateral with ETH borrowing is a staking loop, while rETH collateral with BOLD borrowing and a Curve investment is dollar carry. [Fusion strategy examples](https://www.ipor.io/institutional-vaults/).

An ETH-denominated share does not establish ETH-long dollar carry. An Ethereum contract address does not establish ETH exposure. A “market-neutral” description does not reveal which exposure has been hedged. The destination of borrowed funds must be established before an unidentified lending account enters a measured carry total.

## Products and sleeves identified

The [five product chapters](CARRY-PRODUCTS.md) extend the original published-design census with archived live positions, controls, share-holder ledgers and funded return histories. The website uses those findings for its current route table. Historical strategy weights remain unknown.

The table reports **whole-product book NAV at T**, where available. It does not claim that every dollar in a mixed vault is allocated to carry, or that book NAV has been independently reconciled to reserves. USD snapshot marks use the same $2,667.9504418816 ETH quote disclosed in the existing research, timestamped T+1 second. This is a valuation convention, not an execution price.

| Product | Classification | Chain and route | Whole-product book NAV at T | Carry allocation evidence |
|---|---|---|---:|---|
| ether.fi Liquid ETH | Mixed portfolio with confirmed E4 sleeve | Ethereum borrowing and dollar destinations; Optimism share circulation; nested Monad exposure | 177,171.063302 ETH / $472.684M | UI capture on 3 October: 64.66% labelled carry, 21.65% explicit ETH loops; not weights at T |
| Concrete Delta weETH | Disclosed E4 design | weETH collateral, stablecoin borrowing and dollar-neutral arbitrage; shared Ethereum Safe | 278,170.834213 weETH = 307,362.925489 ETH / $820.029M | No product-specific verified allocation; initial issuance, shared backing and external-equity attribution remain unresolved |
| Concrete wstETH Plus | Candidate, not established E4 | Ethereum product shares and shared Safe with dollar debt | 36,439.686407 wstETH = 45,382.053910 ETH / $121.077M | Shared debt does not prove this product's mandate or allocation |
| Liquity ETH Carry, Fusion / Sentinel | Confirmed E4 design | Ethereum at T: wstETH → Ebisu ebUSD debt; an active Uniswap V4 fuse | 6,014.001735 ETH / $16.045M | Fixed-block active Ebisu Trove: 44.3269% LTV, 2.55% borrower-set APR; full destination attribution remains incomplete |
| Reservoir ETH Yield, Fusion / Reservoir | Confirmed E4 design | Ethereum; WETH collateral → USDC → leveraged srUSD strategy | 23.594840 ETH / $62.950K | At T: 36,789.61 USDC outer debt and 11,021.11 USDC in the main wsrUSD-backed inner loan; October 2025 historical inner debt 90.26M USDC before pending accrual |
| Royco ETH | Confirmed E4 design | Ethereum; wstETH collateral → PYUSD loan → verified senior receipt; srRoyUSDC is the wrapper label | 93.184064 wstETH = 116.051608 ETH / $309.620K | Makina/Caliber route verified; three position categories are stale and immediate maxWithdraw is zero at T |
| TAU InfiniFi ETH Carry, Fusion | Historical nested E4; dust debt at T | Ethereum; wstETH → USDC → siUSD, with a second siUSD/USDC loan | 66.029974 wstETH = 82.233854 ETH / $219.396K | Exact T accrued debt 0.022132 USDC; January 2026 stored debt about 3.04M USDC before pending accrual |
| Rocksolid rETH | Mixed portfolio with dated E4 sleeve | Ethereum rETH collateral on Aave → USDC → Spectra / Hyperithm Morpho; other sleeves include Monad lending and loops | 8,293.351834 rETH = 9,727.767354 ETH / $25.953M | 17-24 August report: 28.54% stablecoin carry. At T, the executor holds a roughly 728.48 ETH book claim in Liquity; direct Aave debt is zero |
| Midas mRe7ETH | Mechanism pending | Optimism product; ETH-denominated neutral Re7 strategy | Not reconstructed at T | Launch description does not establish ETH-collateral dollar borrowing |
| Midas mHyperETH | Mechanism pending | ETH-denominated stablecoin strategy; precise chain and route need verification | Not reconstructed at T | Legal terms cover lending, arbitrage, derivatives and rewards, without establishing an E4 loan route |

Product sources: [Liquid ETH](https://etherfi.gitbook.io/etherfi/products/liquid/live-vaults/liquid-eth-vault), [Concrete catalogue](https://app.concrete.xyz/earn), [Liquity ETH Carry](https://app.ipor.io/fusion/ethereum/0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c/vault-info), [Reservoir ETH Yield](https://app.ipor.io/fusion/ethereum/0xf6cd9e8415162c8fb3c52676c7ca68812a34f76e/vault-info), [Royco Dawn](https://royco.gitbook.io/royco-dawn), [TAU product](https://app.ipor.io/fusion/ethereum/0xc50b2d51fd1e2ac67a9c09eaf63c24ea2465c64b), [Rocksolid dated report](https://app.rocksolid.network/vaults/0x936facdf10c8c36294e7b9d28345255539d81bc7).

The new products matter for different reasons. Liquity provides a substantial, explicit carry product outside the existing five-vault comparison. Reservoir shows a second layer of dollar leverage inside an ETH-funded carry route. Royco adds a tranched credit destination. Rocksolid provides a rare dated allocation report for a mixed ETH portfolio. TAU is a verified historical nested route that is almost fully unwound at T. The supplemental carry chapter measures its earlier loans and current dust debt.

The latest retrieved documentation establishes each product's current published design. The financial state is read at T. Without a contemporaneous mandate or historical position reconstruction, the two facts should not be collapsed into a claim that every historical asset followed today's route.

### Managed ETH vaults that belong in another mechanism

| Examined product | Verified mechanism | Whole-product book NAV at T | Why it is outside E4 |
|---|---|---:|---|
| Fluid Lite ETH V2 | E3 ETH-debt leveraged staking | 77,364.030578 ETH / $206.403M | Borrowed ETH finances additional staking exposure |
| Treehouse tETH | E3 ETH-debt leveraged staking | 24,734.154440 ETH equivalent / $65.989M | Official mechanism borrows ETH and converts it into LST |
| CIAN rsETH | E3 examined rsETH loop | ETH conversion not included in this isolated category table | The examined strategy increases restaked ETH exposure through ETH debt |
| Ethena ETH backing leg | E9 spot/short basis | T figure not reconstructed here | The ETH short hedge changes its economic exposure; whole USDe backing is not ETH-long carry |

These are product-specific classifications. They do not classify every product built by Fluid, Treehouse or CIAN. [Fluid Lite documentation](https://lite.guides.instadapp.io/getting-started/getting-started-with-fluid-lite), [Treehouse yield mechanism](https://docs.treehouse.finance/protocol/tasset/architecture/yield-optimization), [CIAN product documentation](https://docs.cian.app/yieldlayer/for-users-quick-start/core-concepts-and-yield-layer-page-overview).

### Midas needs a separate classification check

mRe7ETH is a material ETH product candidate. The existing discovery capture reports a $13.000M full pool on Optimism, but that is neither NAV at T nor an E4 allocation. The issuer documents an April 2026 launch, ETH-denominated market-neutral returns, Re7 Labs as manager and Optimism Foundation seed capital. It does not explain an ETH-collateral dollar-debt route. [Midas April recap](https://blog.midas.app/midas-in-april-2026-recap/).

mHyperETH's Final Terms specify an ETH base currency and a crypto-denominated stablecoin strategy covering spot, lending, arbitrage, derivatives and token rewards. Its initial issue date is 25 November 2025. This deserves investigation as an ETH yield product, but the legal description does not prove E4. [Issuer Final Terms, pages 0-1](https://www.mfsa.mt/wp-content/uploads/2026/01/Midas-Software-GmbH-Final-Terms-Document-dated-25-November-2025-mHyperETH.pdf).

Midas' general architecture describes onchain NAV and portfolio reporting. A historical token-supply and issuer-NAV series is therefore a concrete next step. Its underlying debt, hedges and wallet allocations need a separate reconstruction. Do not assign the entire Midas protocol, mHYPER, mROX or mBASIS to ETH carry because they can appear on the same chain or in the same investment platform. [Midas product structure](https://docs.midas.app/).

## The size measures must stay separate

For each carry product or sleeve, retain four balance measures:

1. Investor equity attributed to carry, shown in ETH and USD.
2. Gross ETH-family collateral, shown in native tokens, ETH equivalent and USD.
3. Dollar debt, shown by debt currency and USD mark.
4. Dollar destination assets or claims, shown by asset, book value and backing status.

A lending account's collateral minus debt is not the equity of the whole carry strategy. The borrowed dollars may appear in an external investment. That investment must be included when reconciling the strategy balance sheet.

For example, $100 of ETH collateral, $60 of dollar debt and $60 invested in a dollar vault leaves $100 of equity before gains, costs and losses: $100 + $60 − $60 = $100. The $40 reported as net equity inside the borrowing account is only one part of the portfolio. Counting collateral, debt-funded investments and investor shares as three independent capital amounts would overstate the market.

Liquid ETH's senRLUSDv2 and senPYUSDPRIMEv2 holdings are dollar destinations inside its carry route. Their whole-vault assets cannot be added to Liquid ETH investor capital. They include other depositors and exposures to BTC, ETH-related borrowers and credit assets. The lookthrough belongs in the destination-composition view, with the parent's claim and ownership fraction shown. The original [carry credit dossier](../en/dossiers/carry-credit.md) establishes the relevant book claims and concentration limits.

Likewise, Royco ETH and srRoyUSDC are two layers of the same route. The Senior vault's total AUM is not all funded by ETH borrowing. Concrete's shares and the shared Safe's underlying assets cannot be added together. Rocksolid's whole NAV cannot be multiplied by an August allocation and labelled an October measurement.

A single verified global E4 capital total is not yet available. The category page can still show measured product book sizes, current or dated disclosed sleeve weights, and a clear list of unresolved amounts. Its headline should state the measurement actually completed rather than publish a sum with an inconsistent denominator.

## Capital history now available

The main page starts with all seven measured books on one 24-month stacked bar chart, followed by three dated development stories, the comparison matrix and five product tabs plus closed cases. The small-book zoom retains all five smaller products. ETH/USD, table and view-matched CSV controls use the same normalized observations. A separate **Market category** view reproduces the two adapter parents used in the category chart. The [normalized reader dataset](../../../data/eth/reader_analysis.json) preserves every missing state and the two measurement lenses.

Liquid’s contract whole-book series rises from 146,203.01 ETH in October 2024 to 176,962.43 ETH in September 2026, a **21.04%** change. This is distinct from the adapter category’s **53.88%** growth and its continuously observed parent’s **54.29% decline**. The adapter ledger selects different token balances and ETH reference prices; new Concrete membership also changes its denominator. None of these is a measured deposit-flow series.


The [archived borrowing-rate review](BORROW-HISTORY.md) separately follows Liquid's actual main-account RLUSD loan and its Aave WETH debt. The specific RLUSD main account is funded from July 2026 in the month-end sample. Its September quote is 16.6774% APR, independently verified at 100% utilization; this is a point sample rather than the month's average cost.

The isolated dataset contains primary archive histories at all 24 completed-month blocks, October 2024 through September 2026. Each successful observation retains native book assets, ETH conversion, a same-block Chainlink ETH/USD answer and its update timestamp. Predeployment getter absences were checked against empty code and are null, not zero.

| Product | Available completed-month observations | First to last available month | What the curve establishes |
|---|---:|---|---|
| Liquid ETH | 24 | October 2024 to September 2026 | Total product book NAV from archived share supply and published ETH share rate |
| Concrete Delta weETH | 10 | December 2025 to September 2026 | Vault book assets; flat at 278,170.834213 weETH throughout available months |
| Concrete wstETH Plus | 8 | February 2026 to September 2026 | Vault book assets; flat at 36,439.686407 wstETH throughout available months |
| Liquity ETH Carry | 9 | January 2026 to September 2026 | Vault totalAssets in WETH at dated blocks |
| TAU InfiniFi ETH Carry | 12 | October 2025 to September 2026 | Vault totalAssets in wstETH at dated blocks |
| Reservoir ETH Yield | 14 | August 2025 to September 2026 | Vault totalAssets in WETH at dated blocks |
| Royco ETH | 7 | March 2026 to September 2026 | Vault totalAssets in wstETH at dated blocks |
| Rocksolid rETH | 14 in the expanded product chapter | August 2025 to September 2026 | Archived rETH book assets, converted at the dated rETH/ETH rate |
| Midas ETH products | Not reconstructed | Launch and issue dates documented | Supply and issuer NAV feeds must be identified before plotting capital |

These are the first successful month-end reads in the selected window, not exact creation dates. Earlier product histories may exist. The complete getter requests, responses and absence checks are preserved in [the candidate dataset](../../../data/eth/carry_category_candidates.json).

Historical USD marks use the Ethereum Chainlink ETH/USD proxy. Its description and 8-decimal precision were verified at the examined blocks. The maximum answer age in the collected month-end and T references is 3,420 seconds. These oracle marks are dated valuation references, not executable market prices. Snapshot USD product sizes continue to use the existing nearest ETH quote rather than silently changing the report's T convention. [Chainlink historical data](https://docs.chain.link/docs/historical-price-data), [timestamp checks](https://docs.chain.link/data-feeds/overview).

The native and dollar curves answer different questions. Concrete's native book assets are flat, while their ETH equivalent increases with LST conversion and their USD value changes with ETH/USD. Neither change alone establishes external inflows or realized arbitrage income. The documented genesis issuance and self-held share findings remain necessary context.

The page presents **capital history of products with current, historical or declared carry evidence**, with the whole-product scope visible. It cannot present a verified two-year carry allocation series. In particular, multiplying Liquid ETH's historical NAV by the current 64.66% weight would invent a historical strategy allocation. The same applies to Rocksolid's August weight or a currently described Fusion mandate.

To complete category evolution, retain a dated strategy-weight ledger or reconstruct historical collateral, debts and dollar destinations. Existing product NAV can then be split only for months where that split has evidence. A missing strategy weight should create a gap in the carry-allocation series, even if total product NAV is known.

## Borrowing venues and the unmeasured part of the market

Public managed products are only one distribution layer. Direct wallets and private mandates can execute the same ETH-collateral dollar carry without issuing a named vault token. A market-wide census therefore needs borrowers on Aave, Morpho, Spark, Liquity, Sky, Euler, Silo and Fluid where ETH-family collateral and dollar debt coexist. That coexistence alone is not enough: borrowed dollars may be spent, held, used to buy more ETH or deployed to yield.

Ethereum is the confirmed execution chain for the additional explicit carry designs documented here. Optimism is a receipt-token chain for Liquid ETH and the product chain for mRe7ETH, whose mechanism is pending. Monad is a disclosed destination in mixed ETH portfolios, not proof that every nested allocation there is E4. Mainstream chains such as Base and Arbitrum should remain in the borrower and vault screens, but confirmed ETH carry must be separated from the large ETH-debt loop products already found there.

The largest material gaps should be prioritized by observable size, without classifying unknown loans as investments:

| Unresolved item | Observable evidence | What it does not establish |
|---|---|---|
| Concrete Delta and shared Safe | $820.029M Delta book NAV at T; shared Safe's current Morpho wstETH/USDT loan around $70.396M | External equity, exclusive product backing, carry allocation or debt at T |
| Liquid ETH stable carry sleeve | 64.66% post-T labelled carry; material dollar claims and stablecoin liabilities reconstructed | Exact carry investor equity at T or all historical allocations |
| Rocksolid mixed portfolio | $25.953M whole-product book NAV at T; dated 28.54% carry weight | Carry weight at T or a continuous allocation history |
| Midas mRe7ETH | $13.000M captured aggregator pool; official Optimism ETH strategy identity | E4 mechanism or product NAV at T |
| Unidentified Morpho borrower `0xa122687285dc5012141055a801045f069112e7c6` | Current sampled dollar debt $23.533M; weETH/RLUSD, weETH/PYUSD and OETH/USDC | Owner, funding destination, net investor equity or E4 classification |
| Unidentified Morpho borrower `0x1778767436111ec0adb10f9ba4f51a329d0e7770` | Current sampled wstETH/USDT debt $17.877M | Yield reinvestment rather than another use of dollars |
| Unidentified Morpho borrower `0xa56da9bb528fedf8379b02e95fbbdad34d45846f` | Current sampled weETH/PYUSD and weETH/RLUSD debt $15.571M | Owner, overlap with an existing product or use of proceeds |

The borrower numbers come from the existing [Morpho screen](../../../data/eth/morpho_borrower_screen.json), not fixed-block T reads. The screen covers 25 selected markets and mixes mechanisms. Its total debt cannot be used as the ETH carry denominator. Liquid ETH and its confirmed controlled accounts should be consolidated before comparing unidentified borrowers; named and unnamed accounts may share a manager or destination.


## Broader financing and traced carry cases

The [dollar funding atlas](DOLLAR-FUNDING-ATLAS.md) measures 60 dollar reserves in 15 Aave/Spark instances across 12 chains. The [credit expansion](CREDIT-EXPANSION.md) adds actual Compound, Euler and Fluid routes. The [nested funding study](CARRY-VARIANTS-EXPANSION.md) distinguishes historical gross loans from current NAV, and the [coverage assessment](MARKET-COVERAGE.md) states which public measurements remain incomplete.
