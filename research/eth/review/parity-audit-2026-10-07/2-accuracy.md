# ETH page accuracy audit (read-only), snapshot T = 2026-10-02, block 26,108,081

Sources checked: rendered dump, atlas.js, data/eth/netmap/*, economic_questions.json, report_contract.json, gap_* files, research/eth/en (CONCRETE-DELTA, TOP5-RISK-LIQUIDITY, ROCKSOLID-NEMO-SENTORA, BORROWER-IDENTITIES, OUTSIDE-AND-SMALL), tools/eth/netmap/*.py, raw/eth/netmap-2026-10-07/proto and raw/eth/gap-2026-10-07/outside.

## 1. Numbers: what reconciles

These tie to their sources: 18,349,193 ETH / $49.0B (ETH price $2,669.39); category table; 170 products (23+14+14+6+4+2+8+2+97); carry 305,991 ETH and 1.7%; top two products 85.1% (260,480/305,991); debt $261.33M (economic_questions.attributedDollarDebtUSD; the top five sum to $251.24M, and the other $10.08M is Rocksolid 2.73 + NEMO 5.61 + Sentora 1.16 + Makina 0.385 + Royco 0.091 + Vesper 0.069 + Reservoir 0.037); Liquid $181.085M (excludes the $21.02M PRIME/PYUSD leg); 7.79% weighted APR; $14.1M interest, $9.0M of it on the Aave USDC leg; $7.3M = $4.7M + $2.6M income; −$6.8M; ladder 36/13/0/25/26%; health factors and liquidation distances for Avant, Lido Earn and Liquity; stETH 30-day benchmark 2.25% (consistent across every "vs stETH" cell); holder buckets (7,793 / 1,511; 37%; 20.53%); 730-day table (6.8501% vs 5.4875%, i.e. 3.368% vs 2.707% a year); off-chain total 14.4M (4.55 + 4.73 + 5.07); coverage table; −8% from the peak; −48% restaking; +2.19M wBETH; Lido +622k; restaking and farming movers; senRLUSD 52.89% kBTC; Concrete $176.15M at 21.5% LTV; Morpho USDT 3.21% (Concrete's leg).

## 2. Mismatches and contradictions (ranked)

### HIGH
1. **Hero tile "+0.7 pp, what carry adds over staking" (atlas.js atHero, hardcoded).** The 0.66 pp is the excess of Liquid ETH's whole share price over two years. The page itself says that book is mostly a WETH loop, that dollar borrowing only existed in Aug–Sep 2025 and from Jun 2026, and that "the loop is what pays". The tile also says "rewards included", but the comparison section says the published PPS "excludes external rewards". Fix: relabel it as "Liquid ETH vs stETH, whole book, 2 years", drop "rewards included", or use a carry-only figure.
2. **Carry history counts whole books with no dollar debt.** "Two years ago: 147k ETH" and "Carry +104.9%" rest on 146k of Liquid ETH in Oct 2024. Liquid had $0 of dollar debt Oct 2024–Jul 2025 and Oct 2025–May 2026 (economic_questions history). Lido Earn enters in Mar 2026 (0 → 86k) because its predecessor strETH book (in mellow-core, farming) was not backfilled, which adds +127k to carry from Feb to Mar 2026. Fix: present the carry history as a dollar-debt series, or mark the whole-book months without dollar debt as loops.
3. **cbETH counted two ways.** The off-chain table subtracts cbETH = 393,750.6 × 1.14108 = **449,301 ETH** (on-chain totalSupply, raw/…/outside/cbeth_totalsupply_eth.json). The map's Coinbase cbETH row is **188,701 ETH gross / 183,393 net** (DefiLlama adapter, Ethereum only). One is wrong by about 261k ETH: either the map undercounts staking by 1.4%, or Coinbase custodial stake is 1.35M, not 1.09M. Fix: use the on-chain supply for the map row (as already done for wBETH, which ties out at 3.73M) or explain the gap.

### MEDIUM
4. Liquid tab: "beat stETH by 1.36 pp (3.37% vs 2.71% a year)". 1.36 pp is the cumulative two-year gap; the annual gap is 0.66 pp. The heading "0.7 pp a year", the top-five cell "+0.93 pp" (September 30-day) and the hero's 0.66 sit side by side without their windows named.
5. Hero: "306k ETH in 14 products post ETH against dollar loans". Most of the 306k is ETH-on-ETH loops. $261M of debt is about 98k ETH, and TAU (debt $0.02) and ZenSats are in the 14.
6. "Private mandates … owe $263M against ETH". The rSHARE $87.1M includes about $10.8M borrowed against Huma PST (0x4f87). The pooled $261M excludes Liquid's PRIME-backed $21M, so the two sides use different bases. On the same basis it is about $252M vs $261M. economic_questions.excluded also says the Concrete Aave debt ($105.7M) "cannot be assigned to Delta", while the census attributes all $176M to it.
7. Liquid product note (carry table): "a Drone account borrowing $80M". Total dollar debt is $181M; the $101M of Morpho RLUSD/USDC legs is missing.
8. mETH counted twice: mantle-restaking (cmETH, 14.7k mETH) is in ISSUER_SLUGS but not LRT_ISSUERS, so its mETH is never netted from mETH Protocol (234.6k). No mantle-restaking→meth-protocol ledger line exists. About 16k ETH counted twice.
9. Swell L2 Farm (31,989 ETH, rank 26) is 28,973 egETH flat for 18 months. Eigenpie (the egETH issuer) holds only 1,683 ETH. Hemi Staking was excluded on exactly this ground (stale egETH, no issuer row) while Swell L2 Farm is kept.
10. History artefacts (month-over-month moves >30%):
    - The EigenLayer residual swings 493k→809k→1.15M→1.34M→…→204k. This is arithmetic (gross minus gross LRT TVL), yet the restaking card names it as a 1.13M "outflow".
    - Royco V1 jumps from 17k to 306k in Feb 2025, then has no observations for May–Jul 2025. These are Boyco deposits that also show up in Kodiak V3 (167–177k), Veda (+135k) and Dolomite (+72k) in Feb–Apr 2025. The farming peak of 2.09M and the "Points money left" card are probably overstated, and the drop is partly a data gap.
    - StakeStone is floored to 0 in Feb–Apr 2025 (ledger 'floored').
    - Jan 2026 peak: Lido +530k, Kelp +229k and ether.fi +178k all in one month. Worth checking for an adapter change.
    - Liquid Collective 107k→363k in May–Jul 2025: check this.
    - Lido Earn 110.6k→44.3k→90.4k in Apr–Jun 2026, while the text says "May recovery".
    - Rocksolid: 728.48 ETH of Liquity shares is deducted from June 2026 onward, but Liquity's whole book was 641 ETH in June (decisions._rocksolid_liquity is a constant).
11. Money-market rationale: the map counts **idle** WETH (DefiLlama supply minus borrow) but keeps it off by default because "lent ETH is staked again by its borrowers". That reason applies to the borrowed part, not the idle part. Fix the wording or the default.
12. 32 flagged dead, static or leftover rows (54k ETH; GETH 7.7k, StaFi, creth2, Ribbon, Opyn, Belt, Blast and others) are still counted and inflate "170 products". Meta Pool and Hemi were excluded for the same reason.

### LOW
- Risk table: "dollar legs at 1.27 to 1.39". The actual range is 1.27 to 1.87 (Spark PYUSD 1.872, Morpho USDC 1.645, LoanManager 1.408).
- "In BTC it is 9.9%" is hardcoded. data/market_map_current.csv gives 9.78% (C1 9,316 of 95,235 BTC); the Sep 2026 month-end is 10.2%.
- "ETH collateral already earns about 2.7% staked" is the two-year average. Current figures are 2.2 (Lido note) and 2.25 (30-day).
- "Without rewards its RLUSD leg loses 0.84 pp" uses dated quotes (loan 4.30%, rewards 2.59%). At T, Morpho RLUSD is 4.21% and the Merkl APR is 2.72%.
- "Shown by DefiLlama as an $820M product": the DefiLlama Concrete row is 352,622 ETH, about $941M. $820M is Delta's own book.
- The Concrete exclusion text cites research/eth/en/gaps/CONCRETE-DELTA.md; the file is research/eth/en/CONCRETE-DELTA.md.
- midas-rwa: a $12.9M "ETH" pool is labelled "under 100 ETH today". The status comes from candidates.json, not from a measurement.
- Royco ETH "2.25%, +0.00 pp" equals the stETH benchmark exactly because the book mark is stale. It is not a measured return.
- TAU collateral is "wstETH" in product_notes but "cbETH" in the Other-carry table, the IPOR note and decisions (issuer_mix coinbase).
- Upshift note still says the row includes NEMO ETH Prime; the nemo-trading exclusion says "counted in the Upshift row". NEMO is a separate carry row.
- Kelp note says "50k ETHx"; the ledger shows 55,058.
- Liquity note says "manager not identified"; the tab names Sentinel as curator.
- Closed tab: "Completion of closure … unestablished" is stale, since Rocksolid reopened on 7 Oct.
- TOP5-RISK-LIQUIDITY.md: "Avant had dollar debt in every month from Sep 2025 (2.4–11.3M)". Its own series shows $0.08M (Apr 2026) and $0 (May 2026).
- "Dollar debt ×15 in five months from $18M in May" starts from the trough. April was $68.6M.
- Carry chart: "twelve products", but ZenSats has no history column, so 11 have history.
- The re-check table labels EigenLayer "direct restaking 2,626,338". That is the gross figure; the map row is 204,200.
- Lido "gross" is 9,866,628 in the re-check table but 9,829,968 as map row plus ledger.
- Canopy is listed twice (Move 210 / Movement 210 in the chain table).
- Borrower table values tokens at 3 October API prices (about $2,720/ETH) while the rest of the page uses $2,669.

## 3. Counted-once map: method and top 40

- Top 40 rows: categories look right. Two points to argue: Jupiter JLP (27k bridged whETH, flagged "not an ETH product"), and Enzyme (contains treasuries and steakETH Morpho shares).
- Issuer netting: for carry rows, issuer_mix nets whole books from a single issuer.
  - Rocksolid is netted 100% from rETH, although about 64% of its book is wstETH/WETH loops.
  - Liquid is netted 100% from weETH, although it also holds wstETH.
  - Avant uses issuer_mix {}, so its wstETH/weETH collateral is not netted from Lido or ether.fi. That is a small double count.
  - The total changes only through Avant.
- Restaking platforms: EigenLayer net = gross minus the gross TVL of every LRT issuer. This assumes all LRT ETH sits in EigenLayer; it is an estimate and volatile (see item 10).
- Floored rows: only stakestone-stone (2025-02/03/04).
- DEX method: an equal share per leg; plain ETH/WETH legs count and staking-token legs stay with their issuer. This is reasonable. History covers only pools still above $1M (survivorship), which the page discloses.
- Independent checks: wBETH on-chain 3.73M = map ✓; Lido gross 9.83M (plausible); EigenLayer gross 2.63M; Pendle ETH 8.9k (Pendle API: 4 active ETH markets, $6.3M liquidity, so consistent); cbETH ✗ (item 3).

## 4. The 96 product_notes flags against decisions.py

**Resolved:** inceptionlrt slug; curve/vesper msETH and alETH (lib excludes them); fusion-by-ipor nesting (carry replaces); Lagoon/Liquity; tETH and STONE now issuers (treehouse, upshift, balancer-v3, kodiak, tranchess, stakestone-bera, zircuit STONE); Nucleus, Puffer and Swell duplicates; Mitosis/Theo; origami and index-coop SCALE; Cap weETH (SYMBIOTIC_ALSO); all rows now in EXCLUDE.

**Unresolved:**
- Symbiotic Vesper-wstETH vault vs Vesper row (about 6k ETH)
- Cap's 11.5k wstETH, possibly also inside Symbiotic/EigenLayer
- Swell L2 Farm egETH (item 9)
- Jupiter as a non-ETH product
- Zircuit weETHs (779)
- Enzyme steakETH and treasuries
- Treehouse gross vs equity
- GETH and StaFi static rows
- VVS jump (cdcETH)
- Theo category (options vs basis)
- Canopy and DODO chain duplicates
- 32 dead or leftover rows (item 12)
- Mixed carry books (Liquid, Lido Earn, Makina, Vesper, Avant): by design, but feeds items 1, 2 and 5

## 5. Product notes spot check (66 rows: every carry row, every row >10k ETH, 15 random)

No wrong operators found. Errors:
- Liquid: "$80M" (item 7)
- TAU: wstETH vs cbETH
- Upshift and nemo-trading: stale "includes NEMO"
- Kelp: 50k vs 55k ETHx
- Swell L2 Farm: "pre-launch deposits for Swell L2" is stale (Swellchain has launched)
- Treehouse: yield "0.5" is DefiLlama's pool field; the measured two-year rate is 3.09%
- Liquity: manager not identified vs Sentinel
- PancakeSwap: example yield "WETH-GFC, Arbitrum 0.0" is an odd sample
- Royco: stale return shown as 2.25%
- Liquid: "+6.87% since 30 Sep 2024" vs the page's "6.85% / 730 days" (different start dates; pick one)
