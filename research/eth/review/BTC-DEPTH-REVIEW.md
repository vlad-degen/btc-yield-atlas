# BTC and ETH research: structure, depth and presentation review

Reviewed 4 October 2026. This is an internal comparison of the retained BTC project and the English ETH edition before the colleague-facing revision. Original BTC files are unchanged. The ETH snapshot remains 2 October 2026, 23:59:59 UTC; the review does not update financial observations.

## The conclusion

The ETH edition has the right analytical foundation, broad discovery and several strong findings. It distinguishes ETH borrowing loops from dollar carry and basis, verifies important contract relationships, compares investor returns in ETH, and exposes problems with nested capital and book valuation. It does not yet match the BTC project's product-level depth.

The most important difference is the evidence behind the story. BTC reconstructs how strategies changed, who deposited, who paid rewards, how the manager responded to stress, and how much the operator earned. ETH currently gives readers mostly a current balance sheet, selected share-price history and a clear account of what remains unknown. Extra pages alone do not close this gap.

For the colleague-facing revision, first make the existing findings easier to read. Then surface useful calculations already supported by the captured evidence. Keep genuinely unmeasured questions visible without repeating the same limitations in every paragraph. Do not turn missing measurements into confident narrative conclusions.

## What the BTC project actually contains

The original main page has eight sections: introduction, market, carry economics, the five products, the wider carry market, risks, product implications, and method. The introduction leads with three conclusions: dependence on subsidies, the importance of distribution, and dollar borrowing capacity. Each conclusion connects an observation to an implication.

The market section starts with a selected, netted product universe. Six categories are on by default; money markets and CDP collateral are optional and excluded from the default number. The reader can change categories, compare BTC and USD, inspect 25 dated history points, and drill into product descriptions and excluded products. Category changes are disclosed rather than mistaken for investor flows.

Carry starts with a worked example for one BTC. It shows posted collateral, borrowed dollars, deployment income, reward income, interest, the operator's fee and what the investor keeps. An interest-rate curve explains why the borrow rate changes. The calculator then lets the reader change assumptions. The sequence is example, explanation, model.

The five product panels repeat the same readable pattern: a small set of facts, a numbered deposit-to-exit flow, a control table, a payer table, size and yield history, holder concentration, a dated event strip, and a practical finding. The detailed source dossiers use a common A through K structure:

| Part | Question answered |
|---|---|
| Passport | Which product, share, issuer, chain, dates and investor terms are being studied? |
| Mechanics | What happens to the investor's asset from deposit to withdrawal? |
| Counterparties and control | Who owns each claim, holds keys and can change parameters? |
| Manager | Who runs it, with what authority and security coverage? |
| Yield | What was earned, what paid for it, and when did the spread become negative? |
| Risk management | What were the historical exposures, stress response and exit resources? |
| Depositors | Who owns the shares, with custody and collateral holders looked through? |
| Growth | How much change came from share flows, yield and the asset price? |
| Dated drivers | Which observed events coincide with growth, migration or withdrawal? |
| Operator economics | What did fees and incentives cost, and who received them? |
| Verdict | Which measured features inform product design? |

Baseline English dossier lengths are 9,331 words for Kraken, 7,165 for Yield Basis, 4,949 for Bitget, 4,951 for mHyperBTC, 5,555 for Liquid BTC and 5,915 for Maple. Liquid ETH starts at 1,894 words; Fluid Lite, Treehouse and CIAN start at 393, 383 and 331. Word count is not a quality target, but it confirms that the short ETH notes do not contain the same measured dimensions.

The BTC data reinforces the distinction. Kraken has 78 dated events, a replay of 111,832 share transfers, weekly debt/yield/flow histories, holder types and a liquidity ladder. Liquid BTC reconstructs 21 funded month-end portfolios to within 0.5% of book NAV, separates real Ethereum deposits from an all-chain net-flow measure, and tracks nine controlled position managers. Yield Basis tests book versus redemption value, reward cost, governance execution time and stress-era exit discounts. Maple follows a closed product through maturities, legal proceedings and a principal-return waterfall. These are analyses, rather than additional interface widgets.

## Actionable depth matrix

“Presentation” means existing evidence can be explained or exposed now. “Derivation” means a transparent calculation can be made from captured files. “Measurement” means new collection or reconciliation is needed. Rows describe the starting ETH edition; the main task may close some gaps during this revision.

| Dimension | BTC depth | ETH starting coverage | Action and evidence boundary | Type |
|---|---|---|---|---|
| Executive findings | Three measured conclusions before the market | Four statistical cards and a technical description | Add three or four complete, plain-English takeaways with one supporting number and one implication each. Use existing matched returns, leverage, carry allocation and Concrete ownership. | Presentation |
| Market definition | Selected netted categories, optional C7/C8 and excluded products | 5,688 candidate pools, 87 selected protocol sources, explicit unknown global net total | Keep the screening sum separate from market size. Add a coverage table explaining the size of each verified segment and why those segments cannot be summed. No global net pie chart until the graph is complete. | Presentation + measurement |
| Product selection | Ranked scan with a definition, threshold and documented exclusions | Five comparison products with different mechanisms and verification depth | Explain why these five were chosen. Call it a research sample rather than a verified top five by external equity. Add notable excluded, private or unmeasured product classes. | Presentation |
| Major chains | Broad market coverage plus venue-specific borrower follow-up | Ten focus chains in discovery; most deep fixed-block work is Ethereum, Optimism, Base and Arbitrum | Separate “included in discovery” from “reconstructed at a fixed block.” Add chain-specific measurement notes. BNB, Tron, Linea and smaller material sleeves still need exact root-backing and borrower work. | Presentation + measurement |
| Strategy map | Market categories and dated reclassification | Nine mechanics with payers, formulas and risks | Preserve E1 through E9. Add an everyday example before equations and define ETH loop, dollar carry and dollar basis in one paragraph. Mechanism TVL remains unmeasured, so do not turn category hints into a strategy-capital total. | Presentation |
| Worked unit economics | One-BTC Kraken example with reward and fee split | Generic calculators plus real account sensitivities | Add a 100-ETH worked loop example and a clearly illustrative dollar-carry example. Distinguish account equity from whole-product NAV. Use the verified Aave parameters for the loop; do not label an unmeasured carry split as actual Liquid ETH P&L. | Presentation + derivation |
| Portfolio reconciliation | Liquid BTC covers complete funded monthly portfolios within 0.5% | Liquid ETH partial reconstruction has a 2.634% residual; nested claims remain book-valued | Show a balance-sheet waterfall and explain what is included in each line. Group accounts, carry claims, LP and nested vaults without double counting. Keep “97.37% explained by selected claim valuation” distinct from “97.37% physically audited.” | Presentation |
| Historical composition | Dated regime tables, debt venues and controlled managers | Current strategy details and matched PPS; historical portfolio composition open | Add only dated regime events established by logs or disclosures. A current 64.66% carry UI allocation cannot explain the full two-year return. Reconstruct month-end positions and debt before attributing excess to carry or looping. | Measurement |
| Return attribution | Debt-weighted interest, rewards, fees and net PPS compared over time | PPS and issuer conversion returns; no complete portfolio P&L | Add return stability, benchmark excess and share-rate contribution from captured series. Complete interest indices, reward beneficiaries and claim-time prices are needed for organic/reward attribution. | Derivation + measurement |
| Flows and growth | Deposits, withdrawals, yield and price decomposed; concentrated flow drivers identified | Liquid ETH supplies and rates at 33 points; protocol USD observations | Derive the exact share-supply and accounting-rate decomposition of book NAV. Name the first component “share-supply effect,” not real cash inflow. Preserve bridge and in-flight boundaries. Protocol USD growth alone is not a flow series. | Derivation |
| Depositors and distribution | Holder buckets, top-N shares, wallet types, look-through and cohorts | Concrete concentrated holdings; no comparable Liquid ETH/Fluid/Treehouse/CIAN holder census | Complete Transfer replay or paginated holders with balances at T; unwrap lending/queue/bridge custody; separate addresses from people. A borrower scan is not a depositor census. | Measurement |
| Dated chronology | 29 to 110 events per flagship, connected to exposure and growth | 66 Liquid ETH non-rate Accountant events, plus incident sources | Expose fee and payout changes as a chronology now. Keep operational/configuration events separate from deposits and causal growth claims. Collect deployment, withdrawal, market-cap and strategy events for full product timelines. | Presentation + derivation |
| Controls | Specific roles, signers, key powers, timelocks and bypasses | Specific owned managers; a 24-hour authority timelock; Concrete 3-of-5 Safe | Present a “who can change what” table with verified and unresolved columns. Read RolesAuthority capabilities and historical role events; getMinDelay alone does not establish a delay on ordinary authorized strategy calls. | Presentation + measurement |
| Security and incidents | Audit scope, bounty, pauses, liquidation records and executed response | rsETH incident explanation, reserve deficits and selected oracle verification | Map audit reports to the actual implementation/modules. Add observed pause/withdrawal incidents and fund recovery by product. Do not infer no exploit or no liquidation from absence of a searched event set. | Measurement |
| Exit value | Published versus executable NAV, withdrawal quotes and dated gates | Documented exit fees, queue state, reserve cash; simulations open | Add a one-fee return illustration to comparison. Label it a cost model. Build repayment and redemption ladders in the required asset, with competing-withdrawal assumptions. Cash and documentation do not establish successful execution. | Derivation + measurement |
| Risk response | Intraday LTV, negative-carry duration, repayment lag and realized exits | Fixed-state account shocks and model break-even | Keep snapshots as sensitivities. Reconstruct account histories and transactions to measure manager response. Do not borrow Kraken's 40 to 48-hour lag or BTC liquidation formula for an ETH-debt loop. | Measurement |
| Borrower concentration | 319 positions, multiple venues and subsequent identification | 237 top-N positions across 25 selected Morpho markets; pilot Aave accounts | Aggregate the existing selected positions by chain/address and measure top borrower shares within that sample. State its coverage and timing. Full Aave, Spark, Fluid and other-chain enumeration remains needed for a carry census. | Derivation + measurement |
| Operator economics | Fee claims, splitters, downstream fees and subsidy budget | Liquid ETH fee state and 26 captured fee claims; carry-curator fees | Add asset-separated fee totals and dated changes. Current fee × current NAV gives a hypothetical run-rate, not earned revenue. Claim balances need issuer conversion at claim time before summing assets; recipient identity and intercompany splits remain unknown. | Derivation + measurement |
| Restaking, fixed yield and options | Explicit lifecycle, emissions and excluded segments | General staking/LRT note, Pendle catalogue, brief options mechanic | Expand issuer/payer/fee/redemption differences and identify genuinely unmeasured AVS reward income. Measure PT outstanding supply and SY backing, rather than AMM liquidity. Build an options product catalogue before assigning a segment total. | Presentation + measurement |
| Legal claims and credit recovery | Midas/Maple passports distinguish ownership, unsecured/subordinated claims and settlement | PRIME credit disclosure and explicit verification limits | Add holder rights only where current primary terms support them. On-chain collateral and a case study do not establish lender enforcement or beneficial ownership. Keep documented rights distinct from inference. | Measurement |
| Closed products and lifecycle | Maple, Hermetica, Acre, migrations and ceased yield displayed separately | Expired PT and legacy contracts distinguished; no broad shutdown catalogue | Add a lifecycle table for captured expired/legacy products. Track residual principal separately from active strategy size. Do not assume 122 expired PT markets hold zero capital. | Presentation + measurement |
| Final implications | Each operational rule is connected to a measured failure or constraint | Six strong general product insights | State a few decisions plainly: benchmark after exit, publish a readable balance sheet, budget rate headroom, separate credit and liquidity, disclose fee changes. Keep numeric operating limits illustrative unless the capacity analysis supports them. | Presentation |

## Useful calculations hidden in the captured data

1. **Liquid ETH book growth can be decomposed exactly.** For total circulating shares `S` and the Ethereum accounting rate `P`, `NAV = S × P`. Between two observations, `ΔNAV = ΔS × midpoint(P) + ΔP × midpoint(S)`. Summing all 32 captured intervals from 30 September 2024 to T gives +19,898.580780 ETH from share-supply change and +10,363.444646 ETH from accounting-rate change, for +30,262.025494 ETH book change. This is a book decomposition, not verified cash flows or portfolio income attribution. Historical Optimism rate discrepancies and pending bridge shares remain relevant. Source: `data/eth/etherfi_history_points.json`.
2. **The current asset-fee burden is more concrete than “fees can matter.”** The 12 `ManagementFeeUpdated` events range from 200 bp before July 2024 to 35 bp at T. There are 26 `FeesClaimed` events. Native token totals are 2,595.644762 WETH and 121.699459 weETH; these units must not be summed as ETH without conversion at each claim. For 2026 captured claims alone, the amounts are 87.856326 WETH and 121.699459 weETH. Claims do not independently reconcile accrual, payment beneficiaries or a full operator P&L. Source: `data/eth/etherfi_parameter_events.json`.
3. **Fluid has its own measured leverage sensitivity.** Its resolver net equity is 77,359.338125 normalized ETH against 522,808.544153 debt and 600,256.387051 gross assets. A uniform +100 bp annual cost on that debt reduces fixed-state annual return by 6.758183 percentage points of this net equity. A uniform 1% gross-asset markdown reduces that equity by 7.759327%, assuming debt and other terms stay fixed. Neither is a forecast or a complete liquidation test. Source: `data/eth/fluid_lite_balance_T.json`.
4. **Treehouse's current fast-exit fee changes the one-year comparison.** Its 365-day ETH book return is 2.784529%, versus stETH at 2.478539%. Applying one 0.5% fee to ending proceeds yields 2.270607%, or 0.207932 pp below the benchmark. For 730 days, 6.276056% becomes 5.744675%, leaving 0.257157 pp above stETH. This illustration ignores waits, slippage and benchmark exit costs and does not assume the route can fill. Sources: `data/eth/vault_history_comparison.json`, `etherfi_staking_comparison.json`; fee from the captured official Treehouse terms.
5. **Positive CIAN ETH return does not mean outperformance.** Its matched benchmark excess is −0.233013 pp over 365 days and −4.402087 pp over 730 days, excluding external rewards and exit costs. The rsETH units/share loss and issuer-rate increase must be shown separately. Source: `data/eth/vault_history_comparison.json` and `etherfi_staking_comparison.json`.
6. **A small Fluid balance gap can be described precisely.** Book totalAssets exceeds resolver net by 4.692453 stETH, 0.006065% of book or about 0.61 bp. Its size is small, but a separate fee/queue reconciliation is needed to explain it. The table should not silently force agreement. Sources: `data/eth/fluid_lite_balance_T.json`, `vault_registry_rpc_T.json`.

Best placement: show the book-growth decomposition under Liquid ETH history; fee chronology and fee claims inside the same dossier; exit-cost illustrations directly below the matched-return table; Fluid sensitivities inside its product panel; and a compact sample-coverage and concentration table in the lending section. Put the detailed methodology in linked articles.

## Readability patterns to reuse

- Lead with a complete conclusion. A sentence such as “The payout fell because borrowing became more expensive” is easier to understand than an abstract phrase about spread compression.
- Give each section a task. A reader should know whether it answers size, payer, mechanics, return, control or exit.
- Use one numbered path from deposit to payout. Link the detailed contract proof from the relevant step.
- Separate three parallel questions: what investors earn, who pays it, and who can change the rules.
- Define NAV, PPS, LST/LRT, HF, percentage points and basis points at first use. Keep raw ABI, hashes and accounting formulas in expandable evidence unless they explain a concrete decision.
- Replace long-dash interruptions with two sentences, commas, parentheses or a colon. Use “to” for prose ranges. A missing numeric value should read “Not measured” or “Unavailable,” as applicable.
- Reduce repeated caveats through a short measurement label on each table: fixed-block state, dated adapter balance, disclosed terms, published book return, or scenario. Give the complete limitations once beneath the exhibit.
- Preserve readable source labels. A colleague should see “Liquid ETH contract” or “Treehouse redemption policy” before a URL path or machine artifact.
- Use the same product dossier outline consistently. Unknown sections can be short, but should say what was searched and which evidence is needed.
- Close each product with a measured implication, not a general list of every possible DeFi risk.

Do not copy every BTC statement uncritically. The original mixes a few daily, snapshot and live vintages; some broad legal/identity passages rely on disclosed terms or explicitly labelled inference. The ETH edition should preserve its stronger source-vintage and unknown-value controls while adopting the clearer narrative.

## Exact BTC carry-total discrepancy

Two real totals exist in the original files:

| View | Source and filter | Exact BTC | Rounded display |
|---|---|---:|---:|
| Current C1 category | `data/market_map_current.csv`, C1, include_net=1 | 9,315.590 | 9,316 |
| September historical endpoint | `data/market_map_history_monthly.csv`, 2026-09, C1, include_net=1 | 9,277.942 | 9,278 |

The current map includes Vesu Noon WBTC vault at 37.660 BTC. The history does not contain this product. The other difference is small retained precision: Hermetica is 46.950 in current versus 46.952 in history, TESS is 14.490 versus 14.495, and BTCD/TAU is 6.580 versus 6.585. These account for −0.012 BTC. Consequently, `9,315.590 − 9,277.942 = 37.660 − 0.012 = 37.648 BTC`.

`tools/site_data.py` reads the current map and historical map separately and declares snapshot products without history in `nohist`. `REPORT.md` line 107 uses the rounded current total correctly, while its summary and line 138 retain 9,278 as though it were the current category total. This is a prose inconsistency. The source data provides an exact explanation; it is not a disagreement about the definition of dollar carry.

For ETH, every sum and chart must identify its cohort, units, date and coverage. A history endpoint cannot silently replace a current total when the product sets differ. The original BTC files were preserved, including this discrepancy.

## Evidence inspected

BTC: `index.html`, `tools/site_data.py`, `README.md`, selected `REPORT.md` passages, `data/market_map_current.csv`, `market_map_history_monthly.csv`, `product_notes.csv`, `outside_totals.csv`, `c6_groups.csv`, all seven `research/top5/en/` documents, the product CSV inventories, `research/PROJECT-KNOWLEDGE.md` and `PROJECT-CODE-INDEX.md`.

ETH: `tools/eth/site/index.html`, `app.js`, `compare.js`, English library headings and all 12 dossiers; `product_registry.json`, `market_summary.json`, `chain_screen.json`, `protocol_trend_screen.json`, `morpho_borrower_screen.json`, `etherfi_history_points.json`, `etherfi_history_monthly.json`, `etherfi_parameter_events.json`, `etherfi_verified_metrics.json`, `etherfi_partial_balance_sheet.json`, `fluid_lite_balance_T.json`, `vault_history_comparison.json`, `etherfi_staking_comparison.json`, `governance_T.json`, `dependency_graph.json`, `loop_economics_T.json`, `stress_scenarios.json`, `snapshot_manifest.json` and `audit_results.json`.

This review checks the retained project structure and captured evidence. It does not independently re-collect all BTC raw data or perform a complete financial audit of either asset class.
