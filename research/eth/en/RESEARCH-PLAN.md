# Deep ETH yield market research plan

Plan date: 3 October 2026. Research is underway. The [execution checklist](EXECUTION-CHECKLIST.md) records completed work; rankings and market totals require verification before publication. This is the complete target design, not a claim that every phase is finished.

The goal is to study ETH yield as closely as the Bitcoin research studied BTC. We will measure capital by product, strategy and chain, reconstruct major products, and explain who pays the income, who controls the assets and how investors can withdraw. Carry, ETH borrowing loops and products that combine several strategies receive priority. The first detailed case is ether.fi Liquid ETH. The final result is an English research website with product dossiers, mechanisms, history, calculators and linked evidence.

The study must answer three questions: how much ETH is in the measured market, what investors earn beyond simple staking, and what they give up in fees, liquidity and risk to earn that excess. Contract positions and dated events will test the products' public claims.

References: [BTC plan](../../../RESEARCH-PLAN.md), [BTC report](../../../REPORT.md), [BTC project knowledge](../../PROJECT-KNOWLEDGE.md), [BTC code index](../../PROJECT-CODE-INDEX.md). Reuse the dossier and verification structure while adapting accounting to ETH.

## Questions the finished study must answer

1. Measurable size in ETH and dollars, separating verified, estimated and unknown segments.
2. Capital by product, mechanism, root ETH asset, chain and final deployment venue.
3. Capital in native staking, restaking, loops, carry, lending, PT, LP, options and other strategies.
4. Two-year changes attributable to flows, accrued income, ETH prices, leverage and classification.
5. Which ETH-collateral dollar-carry products exist, their equity/debt and where dollars go.
6. Which products borrow ETH to amplify staking, their leverage and response to rates/depegs.
7. Liquid ETH contracts, sleeves, returns, debt, cash, keys and historical strategy changes.
8. Each payer: issuance, network users, borrowers, AVS, traders, issuers, incentives or operators.
9. Investor outcome after fees/execution and discrepancies with advertised APY.
10. Capital owners and retention drivers: staking, excess, integrations, leverage, institutions, exchanges or points.
11. Shared LST/LRT, credit, oracle, bridge, curator and incentive dependencies.
12. Defensible product-design opportunities, separating findings from hypotheses.

## What changes relative to BTC

ETH has native staking income. Excess over that baseline matters alongside absolute yield. Consensus rewards and execution tips/MEV differ; receipts represent staking claims, with distinct market-sale and redemption routes. See [staking](https://ethereum.org/staking/) and [pooled staking](https://ethereum.org/staking/pools/).

ETH lending is a yield-producing deployment layer. Suppliers can earn interest while borrowers use ETH for loops. Measure supply economics and debt demand separately.

One ETH can support a staking token, restaking receipt, collateral position and vault share. This creates a claims/debt graph rather than additive TVL. wstETH represents stETH at a changing rate rather than ETH 1:1; see [contract conversion](https://docs.lido.fi/contracts/wsteth/).

LST/ETH loops and dollar-debt carry have different stress. The former needs relative LST/ETH, ETH rates and exit liquidity; the latter also needs ETH/USD, dollar funding and destination assets. Read each market's eMode at the chosen block rather than assuming a common category; see [Aave eMode](https://aave.com/help/borrowing/e-mode).

Keep consensus issuance, tips and MEV, paid revenue from additional security services, and token campaigns separate. In a scenario without external incentives, retain native staking income. This keeps the comparison with simple staking meaningful.

## Phase 0: scope, taxonomy and accounting

### Product universe

Core products accept ETH or an ETH claim and preserve material ETH exposure or deliver ETH-denominated results: native staking, LST/LRT, lending, managed vaults and depositor-accessible strategies. Record deposit asset, NAV asset, payout asset, ETH delta, hedge and exposure changes. ETH deposits followed by dollar-neutral deployment form a separate segment; converting payout back to ETH does not make it ETH-long staking.

The extended catalogue retains CEX staking/earn, institutional funds, staking ETFs, proprietary treasuries, closed products and unknown AUM, with inclusion/exclusion reasons. They are not mechanically added to transparent on-chain totals. Exchange staking and an exchange certificate can represent the same capital.

Plain WETH, bridge receipts and idle ETH are infrastructure/context. ETH airdrop payouts do not turn unrelated products into ETH yield. Native AVAX, BNB, SOL and other assets are excluded merely because their chains support staking.

### Time and geography

T is 2 October 2026, 23:59:59 UTC. Verify archive availability before bulk collection. Any changed T must update the whole manifest/output set. History covers 24 completed months, October 2024 to September 2026, plus snapshot T. Dossiers cover full funded lifetimes where available; daily/intraday events supplement monthly points. Partial months remain labelled.

For every chain retain last block ≤T, timestamp, successor and finality. Native staking additionally needs consensus slot/epoch and execution block. Prices, rates, oracles and debt match their observation times; later corrections retain dates.

Four geographic fields distinguish origin/backing, share circulation, collateral/debt and final deployment. L2 LSTs can still have Ethereum validator backing. Additive equity attribution counts capital once. Unproven multi-chain splits remain multi-chain/unallocated; gross dependency percentages may exceed 100%.

### Three capital views

| View | Question | Additive accounting |
|---|---|---|
| Unique underlying ETH | Original ETH behind claims | Net backing, bridge escrow, receipts and reuse |
| External investor equity | Investor-owned capital in products | External residual claims after look-through |
| Gross deployment/dependencies | Asset/debt exposure by venue | Separate gross positions, with reuse disclosed |

These totals need not coincide. An ETH lender remains an external claim when a borrower buys an LST; eliminating overlap must not erase that lender. Conversely, a vault share does not add the issuer's whole NAV again. Every adjustment needs a worked balance sheet identifying surviving external rights.

Each headline total must say what it counts. Reconcile shared backing and claims before presenting a net number, and show uncertainty where evidence is incomplete. Coverage means the measurable products found by this study, not a proven census of the entire world market.

Completion gate: scope, taxonomy, schema, manifest and reconciled examples for LST, LST→restaking, LST→WETH loop, ETH→dollar carry, PT/YT and cross-chain shares. Wrapping alone must never increase net capital.

### Mechanism taxonomy

Use ETH-specific mechanism codes. For any table that sums capital, assign each unit once. A product can still carry several mechanism tags when it combines strategies. Leave mixed products unallocated where the evidence cannot support a reliable split.

| Code | Strategy | Income source | Required distinctions |
|---|---|---|---|
| E1 | Native/liquid staking | Consensus, tips/MEV after expenses | Self-stake, pooled/LST, CEX and validator versions |
| E2 | Restaking/LRT | Staking, paid security and campaigns | Allocation/slashing, paid rewards, points, native/LST |
| E3 | Leveraged staking/restaking | ETH asset income less ETH borrowing | LST/LRT/PT loops and mixed debt |
| E4 | ETH collateral / dollar carry | Dollar deployment minus dollar funding | Debt currency, destination, incentives and hedge |
| E5 | Lending | Borrower interest | Pool, curated vault and institutional lending |
| E6 | PT/fixed yield | Discount to maturity accounting unit | Units, maturity, marks, underlying and PT loops |
| E7 | LP | Fees, incentives and underlying income | LST/stable pairs, ranges, perp inventory and hedges |
| E8 | Options/structured | Premium and complete payoff | Delta, sold upside and settlement |
| E9 | Basis/funding | Funding, futures basis, staking leg | Currency, margin, venue and delta neutrality |
| E10 | Other/points | Mixed or prospective rewards | Idle/pending, modelled points and disclosure gaps |
| EH | Hybrid | Measured E1 through E10 combination | Sleeve equity, blended return and shared financing |
| E0 | Context | Unverified or outside scope | Plain wrappers, CDP collateral, treasury and dollar-only |

Classify loan use, not borrowing alone: LST→WETH→LST is correlated looping; ETH→USD→USD yield is carry; ETH→USD→ETH is leveraged long; LP/PT/CEX deployment depends on actual positions/hedges. Maintain full-product NAV and mechanism equity/debt rankings separately. A small carry sleeve does not make all hybrid NAV carry capital.

Carry also includes E9 spot/staking plus short futures/perpetuals. Keep its relationship to E4 while distinguishing payer, ETH delta, return currency and margin risk. Current positive funding does not prove durable return.

## Phase 1: ether.fi Liquid ETH pilot

The hybrid pilot tests accounting, nested claims and multiple loan currencies. Official starting identities are BoringVault `0xf0bb20865277aBd641a307eCe5Ee04E79073416C` and Accountant `0x0d05D94a5F1E76C18fbeB7A13d17C8a314088198`, on Ethereum/Optimism. Verify deployed code/roles independently of [documentation](https://etherfi.gitbook.io/etherfi/products/liquid/live-vaults/liquid-eth-vault).

[How Liquid works](https://help.ether.fi/en/articles/517109-how-liquid-works) describes blended APY and Position/Protocol/Network views with overlapping exposure. UI and reconstructed balances should explain the same economics even when protocol exposure exceeds 100%.

1. Establish identity, versions, deployed chains and funded start. Separate staking issuance, Borrow/Cash and other curators' lending vaults.
2. Verify Vault, Accountant, Teller, Manager, Authority, queue, bridges and all strategy wallets/sub-vaults.
3. Reconstruct assets, liabilities and shares across chains, including escrow/in-transit claims. Compare supply×rate with independent balance sheets.
4. Classify unlevered LST/LRT, ETH loops, dollar carry, lending, PT, LP, CEX, idle and unknown sleeves; trace each loan currency.
5. Reconstruct PPS/NAV and fees; separately value market exit and external reward rights.
6. Examine 6 to 10 strategy/stress dates, then extend to monthly/daily history.
7. Attribute staking, loop uplift, carry, incentives, fees, execution and unexplained P&L.
8. Build debt-currency liquidity ladders and investor ETH exit routes; compare queue settings with actual fulfillment.
9. Review keys, timelocks, modules/Merkle roots, Accountant restrictions and stress actions.
10. Look through holders/integrations and identify reusable checks for other products.

[Veda architecture](https://etherfi.gitbook.io/etherfi/products/liquid/veda-vault) identifies components to investigate rather than proving deployment safety. Administrator module replacement differs from immutable-core behaviour.

Completion gate: positions, debt, PPS, fees, strategy, liquidity, roles and gaps; explain NAV differences within 1%, or explicitly limit conclusions for larger residuals. Independently recheck at least one date. The actual pilot still has an explicit residual; see its dossier/status rather than assuming this gate passed.

## Phase 2: products and major chains

Use registries, token/chain breakdowns, pool feeds, contract directories, lending, staking/restaking, DEX/PT and manager catalogues. Aggregator category is a discovery hint.

Asset identity uses `(chain_id,address)`, canonical asset, type, issuer, backing, conversion, rewards and bridges. Include native ETH, WETH, LST/LRT, a/cTokens, vault shares, PT/YT/SY, LP and debt tokens. Symbols/substrings alone do not establish identity. Compute backing-equivalent and market value separately.

Initial thresholds: detailed product ≥$5M current capital or ≥$20M historical peak; carry/loop sleeve ≥$1M equity or a material mechanism/incident/dependency. Preserve the measured long tail. Include closed, renamed and migrated products to reduce survivorship bias.

Required first circle: Ethereum execution/consensus, Base, Arbitrum and Optimism. Screen others broadly. Candidates include BNB, Polygon, Avalanche, Linea, Scroll, zkSync Era, Mantle, Unichain, Sonic, HyperEVM, Monad, Berachain, Katana, Ink, Blast and Fraxtal; these are search candidates, not asserted leaders. On non-EVM Solana/Sui/Tron, verify material ETH representations rather than including native assets.

Deep-chain trigger: ≥1% discovered gross deployment, ≥$25M relevant capital, ≥$5M product/credit sleeve or critical dependency. Required chains remain regardless. Target 95 to 98% of discovered measurable deployment, reporting staking and DeFi coverage separately so native staking does not hide DeFi gaps.

| Area | Initial candidates to verify |
|---|---|
| Staking | Native, Lido, Rocket Pool, cbETH, Binance, Frax, StakeWise, Mantle and discovered issuers |
| Restaking | EigenLayer, Symbiotic, ether.fi, Renzo, Kelp, Puffer, Swell, Mellow |
| Managed/automation | Liquid ETH, CIAN, Fluid/Instadapp Lite, Summer.fi, Gearbox, Yearn, Enzyme, Lagoon, Upshift, Veda |
| Credit | Aave, Morpho, Spark, Euler, Fluid, Compound, Silo, Gearbox, Venus, Moonwell, Radiant |
| Fixed | Pendle, Spectra, ETH PT and PT-collateral lender vaults |
| LP/structured | Curve, Uniswap, Balancer, Aerodrome, Tokemak, Beefy, Convex, perp/options |
| Off-chain/context | CEX, funds/treasuries/ETF, Ethena and other dollar strategies |

Candidates are not live-status confirmations, rankings or recommendations. Split versions/products; [CIAN concepts](https://docs.cian.app/yieldlayer/for-users-quick-start/core-concepts-and-yield-layer-page-overview) illustrate separate recursive staking/restaking.

Completion gate: product/asset/chain/contract/exclusion/source registries and raw manifest. Every major row needs source, identity, date, mechanism and confidence. Missing size remains unknown, with estimated order of magnitude only where defensible.

## Phase 3: net market map and hidden carry/loops

Build product×asset×chain×strategy balances: external equity, ETH/USD, gross assets, ETH/dollar debt, collateral, stake backing and claims, using aligned blocks/prices. LST/LRT conversion and actual backing remain separate from market discounts.

Native staking uses consensus balances, withdrawal credentials and operator/issuer attribution, including buffers/pending exits. Validator count×32 is not universal after effective-balance/compounding changes.

Graph: backing→issuer→security allocation→receipt holder→collateral→debt-funded asset→vault→external owner. Solve linked assets/liabilities rather than expanding recursive loops indefinitely. Unknown edges retain overlap ranges. Publish additive product/category/chain views alongside non-additive dependency matrices, with denominator definitions.

Borrower discovery: enumerate ETH/LST/LRT/PT collateral markets and ETH/stable loans; collect borrower accounts; classify vault/Safe/EOA/CEX; trace WETH→LST, USD→yield, USD→ETH, PT, LP, bridges and unknown destinations; connect wallets to user-facing products through supply, permissions, documents and flows. One known address is insufficient. Proprietary EOA/treasury positions remain a separate debt-demand table.

Separate supply-side lending from borrower-side looping. Rank full NAV, carry/loop equity and debt independently. Begin at ≥$1M debt; identify ≥$5M positions and major unknowns. Use sleeve shares to retain small carry in large hybrids; disclose thresholds/pagination.

Mandatory pilot plus five largest verified carry products/sleeves, three to five material or distinct loop/hybrids and two to three staking/restaking benchmarks form an initial 8 to 12 unique-dossier core. Fewer genuine carry products means publish fewer, with historical cases; do not fill ranks with proprietary desks. Add representative lending, PT, LP and basis cases wherever mechanics are otherwise uncovered.

Completion gate: current map, overlap graph, borrower scan and selection rationale. Additive sums reconcile; material adjustments have evidence. Compute actual share of discovered carry/loop capital covered by chosen dossiers.

## Phase 4: history and mechanism changes

Build monthly ETH/USD for each included position, updating rates, backing, debt and classification by date. Do not backfill current mix/overlap without an estimate label. Lending retains supply, debt, cash and utilization; vaults retain shares, book PPS, independent NAV and assets; PT retains maturity/version/accounting asset. See [PT mechanics](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT).

Retain closed products, exhausted rewards, migrations, bridge/version changes, monetized points and authority/fee changes. Attribute growth to deposits/withdrawals, staking, incremental P&L, realized incentives, ETH/USD and receipt prices, leverage and methodology. Midpoint price/value identities do not replace cash-flow events. Use TWR and MWR where flows permit, against ETH holding and unlevered LST on matched windows.

Completion gate: histories, lifetimes, events and coverage matrix. Explain the gap between last historical observation and current map, retaining any bounded residual.

## Phase 5: dossier specification

Each dossier follows BTC depth with ETH benchmarks, loan currencies and nested staking:

1. **Identity:** issuer/operator/curator, verified people/entities, deploy/launch/funded dates, chains, versions, assets, current/peak equity and status; flow from deposit through payer to payout.
2. **Positions:** collateral, debt and destination by sleeve; gross exposure, leverage/LTV/LT/eMode, permissions, delta/hedge, caps and shared finance. No account threshold is generalized to the whole vault.
3. **Income:** matched cumulative ETH/APR/APY; staking, loops, carry, lending, PT, LP/IL, funding, options, AVS, incentives and residual. Compare marketing, API, accrued/claimed/sold rewards and PPS. Avoid rewards inside/outside NAV duplication.
4. **Negative windows:** duration, losses, debt costs above destination income, underperformance versus staking, operator response, deleverage and recovery. Smooth managed PPS does not replace independent MTM.
5. **Liquidity:** separate repayment and investor-payout ladders: same block, minutes, day, 1 to 7 days, longer, unknown. Simulate authorization, flash liquidity and competing withdrawal. Include staking/restaking, PT, bridges, CEX/institutional routes. Price exits of 1%, 10% and 30% NAV.
6. **Control:** issuer, operators, bridge, oracle, Accountant, admin, executor, market, curator and fee recipient; address, threshold, timelock, pause/mint/withdraw/upgrade/root and bypass powers. Verify deployed versus documented terms. Restaking needs actual allocation/slashing/reward beneficiaries.
7. **Owners/growth:** addresses versus proven economic owners; top-1/10/100, HHI, retail/institutional/contract/omnibus/CEX, escrow and internal shares. Do not invent private omnibus clients. Analyse caps, incentives, integrations/distribution and self-deposits; APY correlation is not causation.
8. **Operator economics:** fees at every layer, claimed/owed revenue, gas/keepers and subsidy budget; gains to investors, issuer, lenders, curators, validators and sponsors. Conclusions quantify tradeoffs rather than universal safety rankings.

## Phase 6: carry economics, stress and capacity

Local approximations require actual balances/cash flows for realized P&L.

`APR_equity ≈ collateral_income_USD / equity_USD + (destination_APR − borrow_APR) × USD_debt / equity_USD − annual_costs_USD / equity_USD`

Preserve income-bearing collateral, subtract unlevered benchmark for incremental carry, account for idle funds and convert realized dollars at cash-flow dates. Constant rates must not hide ETH price or depeg effects.

`APR_equity ≈ L × ETH_asset_APR − (L−1) × ETH_borrow_APR + external_incentives − costs`

L uses comparable gross/equity marks. `1/(1−LTV)` applies only to idealized complete recursion; actual leverage depends on finite loops, caps and exchange execution. Allocate shared debt/equity once; use ranges and unallocated balances where exact allocation is impossible.

Basis decomposes staking, basis change, funding and hedge/margin costs. Measure lost ETH exposure, short liquidation, collateral transfer and counterparties. Verify delta neutrality over time and funding-sign changes.

Compare ETH holding, staking net of issuer fees, unlevered lending, strategy, rewards-off strategy and stressed strategy on identical windows/units.

| Scenario | Exposed strategies | Measure |
|---|---|---|
| ETH/USD −10/−20/−35% | Stable-debt carry / leveraged long | HF/LTV, repay need, liquidation, loss/recovery |
| LST/LRT discount 1/3/5% | Loops/collateral | Oracle versus exit, haircut and collateral seizure |
| ETH rate jumps and 7/30-day persistence | Loops | Break-even, negative carry and deleverage cost |
| Stable rate jumps | Carry | Negative spread, staking offsets and unwind |
| Funding reverses / basis diverges / margin rises | Basis | Cash flow, shortfall, close cost and venue risk |
| Utilization 95 to 100% | Suppliers/borrowers | Rates, cash, flash capacity and queues |
| External rewards zero | Incentivized products | Net yield/excess retaining native staking |
| Withdrawals 10/30% NAV | Managed products | Debt repaid and ETH delivered by size/time/price |
| Queue 7/21/60 days | Staking/LRT | Funding costs, forced sales and buffers |
| Slashing/haircut and delayed oracle | Staking/restaking/lending | NAV propagation and first-loss bearer |
| Chain/bridge/keeper outage | Cross-chain | Repayment without asset movement and duration |
| Concurrent related-vault exits | Shared ecosystems | Competition for buffers and circular dependencies |

These are designed shocks rather than asserted probabilities/current settings. Do not apply dollar liquidation formulas automatically to LST/ETH loops. Governance/caps/eMode changes can force deleveraging without ETH/USD movement. Historical stress studies retain blocks, before/after positions and response times.

Capacity includes issuer/curator/market concentration, product shares of pools, self-credit, shared payers and collateral/restaking overlap. Model utilization/rate curves, caps, LST depth, staking exits, budgets and marginal yield with AUM growth. Output break-even surfaces, stress tables, two liquidity ladders and a dependency/risk matrix, separating verified parameters from assumptions.

## Phase 7: synthesis and website

Test net excess, independent payers versus subsidies, debt-cost consumption of loop uplift, carry versus looping, points-driven TVL, shared cross-chain bottlenecks, book versus exit value, rewards-off/mass-exit resilience, fee stacking, distribution/owner differences, changing strategy regimes and viable new-product capacity.

Deliver an English report and interactive atlas with market/chain views, comparable history, product comparisons, flows, controls, sources and calculators. Each chart has inspectable data; dossiers carry full evidence and limitations. A playbook ties permitted economics/risk limits to results. Compare curators by verified deployments, conflicts, history and powers.

Every total retains scope/uncertainty. “Not found” means not found in the checked universe at disclosed thresholds.

## Phase 8: verification and reproducibility

Rebuild from captured raw; independently reconcile shares×rates against assets−debt; check headlines/ranks/totals/history against one classification; verify units, rebases, decimals, quote direction, stale marks, versions and addresses; align market/exit benchmarks; net borrowing, wrappers, bridges and issuers; retain unknown edges; tie every fact to date/block, source, transform and confidence; generate graphs/text from common semantic data; check fixed text and calculator assumptions; explain current/history coverage; publish unresolved issues.

Use public archive RPC/APIs/indexers, logs and reports. Test historical availability early; paid-only data requires alternatives or explicit gaps. Completion requires reproducible findings, explanations for material discrepancies and a clear statement of coverage. Unprovable exact values remain ranges/unknown with stated impact.

## Data specification and reuse

Keep ETH namespaces separate from original BTC outputs. Registries, snapshots, current/history positions/debt, ownership/netting, sleeve allocation, cash flows, benchmarks, exclusions, events and evidence live under data/eth. Each product can retain positions, debts, NAV, returns, P&L, fees, rewards, liquidity, roles, holders and events. Raw is content-addressed under raw/eth/<snapshot_id>; tools/config/collectors/normalizers/history/validation/build remain tools/eth.

| Dataset | Required fields |
|---|---|
| Registry | product_id, name, protocol, type/status, funded_start/end, chains, issuer, deposit/NAV/payout assets, exposure |
| Asset | chain/address, canonical ID, issuer, decimals/type, backing, conversion, market marks and bridge origin |
| Snapshot | T, block/slot/epoch, time/finality, price source/time, retrieval and version/hash |
| Position | owner/sub-vault, product, chain/market, units, claim/backing ETH, book/market USD, strategy/confidence |
| Debt | borrower/product, chain/market/currency, principal/accrual, quote/APR/oracle, LTV/LT/eMode and liquidity |
| Allocation | product/date/sleeve, equity/gross/debt, shared/unallocated and attribution method |
| Overlap | source/target/type, amount/unit/time, method/adjustment, confidence/uncertainty |
| Return | window/funded start, denomination, cumulative/APR/APY, TWR/MWR, gross/net, benchmark and exit adjustment |
| P&L | Staking, tips/MEV, AVS, carry/loop/lending/PT/LP/options/funding, incentives, costs and residual |
| Evidence | Claim, value/unit/date/block, primary URL/file/hash, transform, confidence and caveat |

Confidence: high for reconciled direct state/logs; medium for dated disclosure with partial reconciliation; low for claimed strategy, proxies/models. Identity and source-of-funds confidence are independent of amount precision. Preserve requests, pagination, errors and capture time. Resume collection with checkpoints without overwriting prior snapshots.

Reuse BTC's flow/roles/return/liquidity/holder/event dossiers, borrower discovery, archive/event methods, share/NAV reconstruction, overlap/history and presentation. Extend for staking benchmarks, rebases, relative depegs, consensus, shared debt and separate repayment/redemption ladders. Do not copy hardcoded BTC addresses/blocks/categories, private raw paths or manual corrections.

The pilot precedes bulk reconstruction. Catalogue, netting, borrower identification and some history can progress concurrently, but final ranking requires comparable equity. Version corrections and rebuild outputs when dossiers refine classification. The first edition's actual completion and open work remain in the checklist.
