# Double counting: Babylon, LSTs and nested vaults (snapshot 2026-09-20)

BTC price for conversion: $81,178 (Binance BTCUSDT close 2026-09-20). "Gross" = every product row in C1-C6; "net" = each BTC counted once, at the outermost product the holder owns (the rule in plan 0.3: count where the BTC earns, at the top level).

## 1. Totals

| Measure | USD | BTC |
|---|---:|---:|
| Gross, on-chain rows | $8.36B | 103,007 |
| Net, on-chain rows | $7.61B | 93,693 |
| Gross incl. disclosed off-chain AUM | $8.54B | 105,139 |
| **Net incl. disclosed off-chain AUM (central)** | **$7.78B** | **95,825** |
| Net, low end of range (see section 5) | $7.43B | 91,528 |
| Gross minus net (removed overlap) | $0.76B | 9,314 |

Not in these totals: C0 context (money-market collateral, curator BTC lending vaults, CDPs), excluded wrappers, Coinbase CBYF (size unknown, left blank). Maple BTC Yield is 0 today (wound down 11-2025) with an on-chain history.

By category (current):

| Category | Gross BTC | Net BTC | Net USD | Net share |
|---|---:|---:|---:|---:|
| C1 Carry (BTC collateral + USD loan) | 9,278 | 9,278 | $753.2M | 9.7% |
| C2 Staking & restaking | 66,358 | 58,759 | $4,769.9M | 61.3% |
| C3 Basis & delta-neutral | 7,312 | 7,312 | $593.6M | 7.6% |
| C4 Options selling | 8,654 | 7,992 | $648.8M | 8.3% |
| C5 Credit to institutions | 3,037 | 3,037 | $246.6M | 3.2% |
| C6 LP / emissions / farming / DeFi vaults | 10,499 | 9,446 | $766.9M | 9.9% |
| **Total** | **105,139** | **95,825** | **$7,778.9M** | 100% |

## 2. Babylon vs LSTs

Babylon TVL on DefiLlama at 2026-09-20: 41,329 BTC (equals the sum of active delegations to *active* finality providers: 41,288 BTC in the Babylon LCD `btc_delegations/ACTIVE` list, 1,398 delegations, 217 staker keys).

**Method.** Babylon exposes no per-product breakdown, so stake is attributed through finality providers (FPs) whose operator names a product (Lombard*, Solv*, RockX-Bedrock, PumpBTC, lorenzo, Chakra, Allo, BSquared*, Gate Earn). Sources: `staking-api.babylonlabs.io/v2/stats`, `/v2/finality-providers`; `babylon-rest.publicnode.com/babylon/btcstaking/v1/btc_delegations/ACTIVE`. Delegations to *inactive* FPs are not in Babylon's active TVL (and not in DefiLlama), so they are not an overlap.

Composition of active Babylon stake by finality provider (BTC):

| Finality provider | BTC | Share | Maps to listed product? |
|---|---:|---:|---|
| Kraken02 | 18,305 | 44.3% | no: Kraken exchange staking (custodial) |
| Kraken | 14,627 | 35.4% | no: Kraken exchange staking (custodial) |
| Gate Earn | 3,455 | 8.4% | GTBTC (Gate) |
| Figment | 2,087 | 5.1% | unattributed institutional (upper-bound case) |
| Binance Finality Provider | 1,301 | 3.1% | no: Binance |
| OKX Earn | 1,126 | 2.7% | no: OKX Earn (CeFi) |
| RockX-Bedrock | 153 | 0.4% | Bedrock uniBTC |
| Lombard Finance | 42 | 0.1% | Lombard LBTC |
| Stakecito | 33 | 0.1% | no |
| Keplr | 33 | 0.1% | no |
| Solv Protocol | 31 | 0.1% | SolvBTC LSTs |
| Blockdaemon | 30 | 0.1% | no |
| other 23 FPs | 65 | 0.2% | no |

Overlap table (current):

| Listed product | Product BTC (gross) | BTC it stakes in Babylon (active) | Treatment |
|---|---:|---:|---|
| Gate GTBTC | 3,468 | 3,455 | removed from the Babylon row, counted in the product |
| Bedrock uniBTC | 4,595 | 153 | removed from the Babylon row, counted in the product |
| Lombard LBTC | 8,499 | 42 | removed from the Babylon row, counted in the product |
| SolvBTC LSTs | 970 | 31 | removed from the Babylon row, counted in the product |
| PumpBTC | 342 | 0 | no active stake today |
| Lorenzo stBTC | 0 | 0 | no active stake today |
| B2 Buzz Farming | 3,222 | 0 | no active stake today |
| **Total removed from Babylon** | | **3,681** | Babylon net = 37,606 BTC |

- Kraken (FPs "Kraken" + "Kraken02") is 32,932 BTC, 80% of Babylon. It is custodial exchange staking; it stays in the Babylon row. Whether any of it is the kBTC reserve behind the Kraken Bitcoin Vault (6,492.7 BTC) cannot be checked from public data; no overlap is assumed.
- Lombard: only 42 BTC remain on an active Lombard FP. A further 2,500 BTC sit on the *inactive* "Lombard x P2P.org" FP; this stake is outside Babylon's active TVL and outside DefiLlama's Babylon number, so it is not double counted.
- Figment (2,087 BTC) is an institutional operator; Lombard used separate "Lombard x Figment" FPs, so plain Figment stake is not attributed. It is the upper-bound case in section 5.

## 3. Nested holdings (LST held inside another listed product)

Each yield-bearing BTC token held by another listed product is counted once, at the holder (outer product), and removed from the issuer row. Holdings come from the holders' DefiLlama token breakdowns (symbols LBTC, BTCOC, UNIBTC/BRBTC, PUMPBTC, SOLVBTC.BBN/XSOLVBTC, SOLVBTC.TRADING, BFBTC, GTBTC, MHYPERBTC, EBTC, AVBTC, STBTC, ASBTC).

| Issuer (removed from) | Holder (counted in) | USD | BTC |
|---|---|---:|---:|
| Bedrock uniBTC | Symbiotic (BTC vaults) | $211.9M | 2,610 |
| Lombard LBTC | Lombard Vaults (LBTCv / BTCe) | $53.2M | 656 |
| PumpBTC | CIAN Yield Layer (BTC vaults) | $24.6M | 304 |
| Bedrock uniBTC | Mellow restaking (uniBTC) | $8.7M | 107 |
| Symbiotic (removed from) | Lombard Vaults (BTCe credit leg) | $47.4M | 584 |
| (holders under $0.5M omitted from this table; included in the numbers) | | | |

**LBTC -> LBTCv -> BTCe (counted once).** LBTC supply is backed by 8,499 BTC at the 09-20 point. Lombard Vaults (LBTCv; BTCe is a wrapper over LBTCv) hold 71 LBTC, 580 BTCOC (the LBTC-backed token of the BTCe credit strategy), 188 cbBTC and 75 BTC.b. The 580 BTCOC is the same LBTC that Symbiotic reports as 583 LBTC in the "Lombard-Flow Traders" vault (slashable cover for Flow Traders' loan on Cap). Treatment: 651 LBTC-equivalent removed from LBTC; the Symbiotic LBTC removed from Symbiotic; the whole Lombard Vaults balance (919 BTC) counted once in C5. LBTC's own covered-call program is counted in the LBTC row (C4); the off-chain memo row is not added.

**SolvBTC LSTs vs Solv Basis.** No overlap in the net: the two rows count different token supplies (SolvBTC.BBN backing: locked FBTC + native BTC; SolvBTC.TRADING supply for the basis fund). The base SolvBTC wrapper, which backs both, is excluded as a wrapper. Solv Strategies (SolvBTC in LP/farming) and Solv RWA are separate supplies too. Only 31 BTC of Solv stake is active in Babylon (removed from Babylon).

**uniBTC vs Babylon.** 153 BTC is staked in Babylon via the RockX-Bedrock FP (removed from Babylon). Most uniBTC sits in Symbiotic (2,624 uniBTC) and Mellow (107): counted at those holders and removed from the uniBTC row.

**Other rows kept out of the net** (gross only):

- ether.fi eBTC: 277 BTC. gross only: eBTC is a Veda BoringVault, presumed inside the Veda (other BTC vaults) balance; yields-pool history starts 2026-01
- Endur (Starknet BTC LSTs): 32 BTC. Endur LSTs delegate into Starknet BTC Staking: counted there.
- AILayer farm (AINN): 1,042 BTC. Presumed same BTC as bfBTC on AILayer.; presumed same BTC as BitFi bfBTC on AILayer (84.6 vs 82.6 $M, co-moving)
- Hyperbeat Earn (hbBTC): 11 BTC. Same hbBTC balance as the UBTC in Upshift: counted in Upshift.
- Syntetika hBTC disclosed AUM (~$16.1M) and the Lombard covered call are memo rows: the same money is already in the on-chain Syntetika and LBTC rows.

## 4. Overlap over time

Babylon history source: `raw/babylon_lst_staker_monthly.json` (stake of product-linked staker keys / FPs, rebuilt from phase-1 (v1) and phase-2 (v2) delegations; stake end = block height of the transaction spending the staking output, from mempool.space, for stakes >= 2 BTC). Attributed stake is capped at the product's own DefiLlama BTC and at Babylon's total. Excludes the products whose history is pending (Kraken vault, Bitget, ether.fi Liquid BTC), Core and off-chain rows.

| Month | Gross BTC | Net BTC | Babylon stake removed (LSTs) | Nested LST removed | Other gross-only rows |
|---|---:|---:|---:|---:|---:|
| 2024-09 | 34,550 | 30,634 | 0 | 1,740 | 2,176 |
| 2024-10 | 93,248 | 68,619 | 14,134 | 8,749 | 1,746 |
| 2024-11 | 124,060 | 95,084 | 14,865 | 12,660 | 1,450 |
| 2024-12 | 157,553 | 114,086 | 31,122 | 11,001 | 1,344 |
| 2025-01 | 164,975 | 118,191 | 31,305 | 12,800 | 2,679 |
| 2025-02 | 188,254 | 120,558 | 31,352 | 19,811 | 16,533 |
| 2025-03 | 197,646 | 127,356 | 30,126 | 22,902 | 17,261 |
| 2025-04 | 191,548 | 120,987 | 33,688 | 19,696 | 17,176 |
| 2025-05 | 163,519 | 117,166 | 28,169 | 16,031 | 2,153 |
| 2025-06 | 144,996 | 103,555 | 24,636 | 14,674 | 2,131 |
| 2025-07 | 138,942 | 100,304 | 23,708 | 13,743 | 1,187 |
| 2025-08 | 144,853 | 114,315 | 19,961 | 9,402 | 1,174 |
| 2025-09 | 138,132 | 112,535 | 17,489 | 6,908 | 1,200 |
| 2025-10 | 135,677 | 113,275 | 14,964 | 5,994 | 1,444 |
| 2025-11 | 113,247 | 93,320 | 16,434 | 2,132 | 1,361 |
| 2025-12 | 119,996 | 100,281 | 15,354 | 2,992 | 1,369 |
| 2026-01 | 115,363 | 95,057 | 15,276 | 2,662 | 2,368 |
| 2026-02 | 105,839 | 85,535 | 15,039 | 3,087 | 2,178 |
| 2026-03 | 109,498 | 88,579 | 14,615 | 4,101 | 2,202 |
| 2026-04 | 108,593 | 88,453 | 13,741 | 4,219 | 2,180 |
| 2026-05 | 107,843 | 88,587 | 13,111 | 4,187 | 1,959 |
| 2026-06 | 108,320 | 90,443 | 13,039 | 3,446 | 1,392 |
| 2026-07 | 99,058 | 90,665 | 3,879 | 3,160 | 1,354 |
| 2026-08 | 98,032 | 89,104 | 3,782 | 3,798 | 1,348 |
| 2026-09 | 100,800 | 91,486 | 3,681 | 4,272 | 1,362 |

Babylon stake attributed to listed products, by product (BTC, month-end):

| Month | alloBTC | Bedrock uniBTC | B2 Buzz Farming | Chakra | Gate GTBTC | Lombard LBTC | Lorenzo stBTC | PumpBTC | SolvBTC LSTs (SolvBTC.BBN etc.) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-09 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2024-10 | 527 | 671 | 300 | 0 | 0 | 7,354 | 131 | 38 | 5,112 |
| 2024-11 | 527 | 671 | 300 | 732 | 0 | 7,354 | 131 | 38 | 5,112 |
| 2024-12 | 527 | 914 | 300 | 1,143 | 0 | 15,550 | 134 | 6,294 | 6,259 |
| 2025-01 | 528 | 884 | 300 | 1,140 | 0 | 15,550 | 134 | 6,509 | 6,259 |
| 2025-02 | 529 | 884 | 300 | 1,142 | 0 | 15,550 | 134 | 6,699 | 6,113 |
| 2025-03 | 528 | 884 | 300 | 740 | 0 | 15,550 | 55 | 6,502 | 5,566 |
| 2025-04 | 529 | 893 | 300 | 705 | 0 | 20,475 | 55 | 6,385 | 4,346 |
| 2025-05 | 528 | 849 | 300 | 703 | 0 | 17,879 | 54 | 4,886 | 2,970 |
| 2025-06 | 473 | 1,419 | 300 | 705 | 0 | 15,223 | 54 | 3,316 | 3,145 |
| 2025-07 | 470 | 1,863 | 300 | 704 | 0 | 13,948 | 54 | 3,222 | 3,148 |
| 2025-08 | 0 | 1,844 | 300 | 501 | 0 | 13,681 | 54 | 997 | 2,584 |
| 2025-09 | 0 | 1,870 | 300 | 152 | 0 | 12,581 | 54 | 947 | 1,584 |
| 2025-10 | 0 | 1,260 | 100 | 152 | 0 | 12,081 | 54 | 941 | 375 |
| 2025-11 | 0 | 1,029 | 100 | 51 | 2,961 | 10,971 | 3 | 863 | 455 |
| 2025-12 | 0 | 234 | 100 | 51 | 2,998 | 10,895 | 3 | 860 | 212 |
| 2026-01 | 0 | 313 | 100 | 51 | 2,998 | 10,771 | 3 | 799 | 241 |
| 2026-02 | 0 | 312 | 100 | 51 | 2,998 | 10,534 | 2 | 805 | 236 |
| 2026-03 | 0 | 252 | 100 | 50 | 2,998 | 10,573 | 0 | 404 | 237 |
| 2026-04 | 0 | 252 | 0 | 0 | 2,998 | 10,049 | 0 | 404 | 37 |
| 2026-05 | 0 | 232 | 0 | 0 | 2,998 | 9,439 | 0 | 404 | 37 |
| 2026-06 | 0 | 232 | 0 | 0 | 3,427 | 8,938 | 0 | 404 | 37 |
| 2026-07 | 0 | 262 | 0 | 0 | 3,449 | 134 | 0 | 2 | 32 |
| 2026-08 | 0 | 260 | 0 | 0 | 3,449 | 40 | 0 | 2 | 31 |
| 2026-09 | 0 | 153 | 0 | 0 | 3,455 | 42 | 0 | 0 | 31 |

## 5. Range and unresolved overlaps

- **Central net: 95,825 BTC ($7.78B).**
- **Low net: 91,528 BTC.** Subtracts (a) all plain-Figment Babylon stake (2,087 BTC) as if it belonged to listed LSTs, and (b) all Core staking (2,210 BTC) as if it were b14g's BTC (b14g reports 3,181 BTC on Bitcoin, more than Core's whole staked BTC, so b14g cannot be entirely Core stake; the true overlap is somewhere in 0-2,210).
- **Not netted, no evidence either way:** Kraken exchange staking in Babylon (32,932 BTC) vs the Kraken Bitcoin Vault (6,492.7 BTC, kBTC-based); Maple BTC Yield vs Core staking (Maple staked on Core in 2025; Core rows are current only); Yearn/Beefy/Stake DAO Curve-LP vaults that may sit inside Convex (a few million USD); ether.fi eBTC (276 BTC, yields pool) vs Veda "other BTC vaults" (eBTC is a Veda BoringVault, but Veda's Ethereum WBTC balance, 1,449 BTC, is much larger than eBTC).
- **Historical months:** the Babylon attribution follows the staker keys that ever delegated to a product-branded FP (321 keys, top keys per product covering ~99% of their branded stake), including their phase-1 stakes (v1 API). Keys a product never used with a branded FP are missed, so the historical LST overlap is a lower bound and the historical net an upper bound. Stakes under 2 BTC that ended early use an approximate end height.
- **Campaign wrappers:** Royco v1 (up to 15,177 BTC in 2025-04, mostly LBTC/WBTC/xSolvBTC/uniBTC) and YieldNest (nested in Kernel) are gross-only. If Royco's deposits had not been counted anywhere else, the 2025-02..04 net would be 11-15k BTC higher.
