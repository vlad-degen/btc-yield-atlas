# Maple "BTC Yield" (with Core Foundation): deep dive

Research date: 2026-09-21. Scope: Maple's institutional BTC Yield product, which used Core dual staking with a USDC loan, CORE purchases and CORE puts; the related lstBTC; syrupBTC; and the Core Foundation v Maple dispute.

**How to read this report**
- **DISCLOSED**: stated by Maple, Core or a court.
- **ON-CHAIN**: reconstructed by me from Core or Bitcoin chain data. The attribution method and confidence are in §0.3.
- **EST**: my estimate. The inputs are stated each time.
- **NOT FOUND**: I could not find the data. I say what would be needed to get it.

Companion files in this folder:
- `size_history.csv`
- `yield_history.csv`
- `events.csv`
- `scripts/`: every number here is reproducible.
- `raw/`: API dumps, court PDFs converted to text, and on-chain extracts.

---

## 0. Bottom line (the open question: current size and status)

**The product no longer exists as a live product. Its current size is 0 BTC.**

1. **Maple's API still has the record, but it is hidden.** Maple's public GraphQL API has a pool record `poolMeta(id: 67e542004191822941f9e703)` with `poolName: "BTC Yield"`, `state: "Hidden"`, and `withdrawalDays: 60`. Its highlights are frozen at "Next Maturity Date: 27 June 2025". The ObjectId timestamp shows the record was created on 2025-03-27. The public product page is 404. Protos reported that the BTC-yield section of the site was removed around 2025-11-20. Snapshot: `raw/maple_btc_yield_poolmeta.json`.
2. **Nothing is staked on Core any more.**
   - All CLTV stakes of the Maple-attributed addresses had expired by **2025-11-19**, and none have been made since.
   - The ~50.7M CORE leg was unstaked between **2026-03-29 and 2026-05-12**.
   - Core's own lstBTC system token (`0x…010001`, "Core BTC LST") has **totalSupply = 0**. The staking API returns `btc_lst_apr = 0`.
   - The lstBTC pages (Core blog, docs, lstbtc.coredao.org) are all 404.
3. **Lenders got 85% back in BTC.** On Bitcoin, the remaining **1,333.78 BTC** was swept on 2025-11-19 into one hub wallet (`bc1pm9v0y2…c0pc4`). **1,133.69 BTC (85.0%)** was paid to **66 addresses** between 2025-11-19 and 2025-12-22, with a small tail to 2026-08-10. **200.09 BTC (15.0%)** was set aside. This matches Maple's 2025-11-21 statement: "return 85% of BTC principal … remaining 15% retained … released upon the successful resolution of the legal proceedings".
4. **Where the withheld 15% went is not public.** On **2026-06-05**, 14 days after the 2026-05-22 settlement, the 200.0 BTC holdback left in **one transfer**, via a pre-existing intermediate address, to wallet `bc1q5zly2…` (≈2,263 BTC lifetime throughput). The owner is not public. The chain cannot show whether this was a release to lenders, a repayment of the USDC leg, or a settlement payment. The settlement terms are confidential.
5. **syrupBTC has not launched.** The settlement says "Maple will proceed with the launch of … syrupBTC in the ordinary course". As of 2026-09-21 I found **no syrupBTC**:
   - no token on Ethereum, Base or Arbitrum (Blockscout search);
   - no pool in Maple's API (`poolsMeta`, `syrupTokens` list only the Syrup token and syrupUSDC/USDT/USDG);
   - no mention in the 2026 memos, the Q2-2026 update or the 2026-09-02 "allocation strategies" post, which lists direct lending, ABS and a CME basis trade instead.

   **Status: not launched (NOT FOUND).**

### 0.1 What the product really was (new findings versus the repo's §4.12)

- **The CORE hedge counterparty was Core Foundation itself.**
  - The hedge was physically settled CORE put options under a **Master Trading Agreement dated 27 Feb 2025**. Core Foundation would "repurchase the CORE tokens under that Put Option" at the strike.
  - Core Foundation backed it with **US$5M cash collateral**.
  - In Core's words: "We honored every put expiry for months, paying out millions of dollars."
  - Core stopped paying after the puts that fell due on 30 Sep 2025.
- **This was wrong-way risk.** The hedge writer was the token issuer, and it was also the commercial partner in the dispute.
- **Staking rewards alone could not produce 5%+.**
  - ON-CHAIN, CORE rewards claimed by the Maple addresses were **4.66M CORE** over **848 BTC-years**. That is a **gross dual-staking yield of ≈1.9% per year in BTC terms** (at claim-date prices), and **≈2.7%** even at the BTC-weighted average CORE price ($0.527).
  - This is before the USDC borrow cost (EST ≈1.2–1.5% per year of BTC value).
  - The marketed 5.1–5.6% net therefore required roughly **3.5–4.5 pp per year from outside staking**. The most likely source is the put payouts / subsidy from Core Foundation (EST).
- **Lender economics.** The court record says lenders "loaned their Bitcoins" to the segregated portfolio under a master loan agreement. The loans auto-rolled unless a repayment demand was made.
- **Leverage.** Maple borrowed USDC against that BTC to buy the CORE leg:
  - 50.5M CORE at peak, which is 34,000 CORE/BTC × 1,485 BTC.
  - "Over 40 million CORE … purchased … for over US$20 million" (court record).
  - Implied LTV ≈ **13–16% (EST)**.
- **CORE fell ≈94% from the CORE-leg build-up to the unwind.** The CORE leg was worth ≈$28M at purchase (EST) and ≈$1.4–3.3M in Mar–May 2026. That loss is about 15% of BTC principal, which is the same size as the **15% holdback** (EST, a strong coincidence).

### 0.2 Size in one line

Timeline (ON-CHAIN unless marked):
- **2025-02-06**: first stake.
- **2025-04-30**: 1,600+ BTC (DISCLOSED).
- **2025-05-14**: peak **1,757.85 BTC** staked (≈$182M), ≈24% of all BTC staked on Core.
- **Jul–Sep 2025**: ≈1,485 BTC (≈$160–175M), 28–30% of Core BTC staking.
- **2025-10-15**: 757 BTC staked, but ≈1,341 BTC still in the program.
- **2025-11-19**: 0 staked; 1,333.78 BTC swept for wind-down.
- **2026-06-05**: holdback left.
- **Today**: 0.

Disclosed USD points: $140M (Jun 23 and Jul 7, 2025) and ">$180M" (Q2 2025). Core Foundation said ">$150m" (cumulative).

### 0.3 Attribution method and confidence (on-chain)

- **Seed address.** Core reward address `0x74bb2c9f…` has CLTV maturities of **584.047 BTC on 2025-10-15** and **756.983 BTC on 2025-11-19**. The Cayman judgment of 10 Oct 2025 cites "some 584 Bitcoins … due on 15 October 2025" and repayment obligations on "15 October and 19 November 2025".
- **Linked addresses.** Four more reward addresses stake BTC under the same four Bitcoin owner scripts (2 P2PKH and 2 P2WSH 2-of-3 multisig):
  - `0xadfaaa5f…`, first stake 2025-03-26;
  - `0xfd818e35…`, first stake 2025-02-06;
  - `0x87f34109…`;
  - `0x2ed725c8…`.

  The CORE funding wallet `0x34a8b81a…` also appears under one of those scripts. See `scripts/cluster_link.py`.
- **Bitcoin side.** The BTC staking transactions resolve on Bitcoin (mempool.space). Their final sweep lands in a single hub whose payouts are exactly 85%/15% of the swept amount.
- **Confidence.** High that this cluster is the BTC Yield program. Medium that it is *all* of it: early stakes by other wallets could be missed, and the disclosed 1,600+ BTC versus the on-chain 1,570–1,758 BTC around 1 May–14 May fits well.

---

## A. Passport

| Field | Value | Source / confidence |
|---|---|---|
| Name | "BTC Yield" (Maple). The "pilot"/"OTC version" of what "would ultimately become lstBTC" (Core) | Maple API; Core statement 2025-11-19 |
| Launch | **Feb 2025.** Maple: "launched … in February 2025". First on-chain stake 2025-02-06. CoinDesk 2025-02-17 describes an existing 90-day product. The pool record was created 2025-03-27, and the public push came in April 2025 (Core: revenue "from April 2025 onward") | Maple page snippet (now 404); ON-CHAIN; CoinDesk; Maple API |
| Status now | **Closed and wound down.** API `state: "Hidden"`; 0 BTC staked; 85% of principal returned Nov–Dec 2025; the 15% holdback left the program wallet 2026-06-05; hub emptied 2026-08-10. **syrupBTC not launched** | §0 |
| Peak size | 1,757.85 BTC on-chain (2025-05-14). Disclosed: 1,600+ BTC (Apr/May 2025), ">$180M AUM" (Q2 2025), $140M (Jun–Jul 2025) | `size_history.csv` |
| Size at wind-down | 1,333.78 BTC (2025-11-19, ≈$122M) | ON-CHAIN |
| Issuer / legal entity | **Maple International Operations SPC**, acting for its **BTC Staking Segregated Portfolio 1** (Cayman Islands SPC; George Town). The injunction also names affiliates **Maple Labs Pty Ltd** (Melbourne) and **Maple DAO**. Pool delegate / manager label: **"Maple Direct"** | Cayman judgments FSD 2025-0268; settlement release; Maple API |
| Sister portfolios | syrupUSDC = "Secured Loan Segregated Portfolio 1"; syrupUSDT = "Maple USDT SP 1"; syrupUSDG = "Maple USDG SP 1" | Maple docs |
| Jurisdiction / law | Cayman Islands. Disputes go to arbitration seated in Cayman, with a 30-day award timetable | Judgment [2025] CIGC (FSD) 105 |
| Contracts (Maple–Core) | Letter of intent; **Master Trading Agreement 27 Feb 2025** (CORE puts); **Commercial Agreement 28 May 2025** (confidentiality and a 24-month exclusivity per Core) | Judgment of 10 Oct 2025 (filed 2 Dec 2025) |
| Contract (lenders) | "Master loan agreement". Lenders "loaned their Bitcoins"; loans auto-roll unless a repayment demand is made | Same judgment ¶24.4, ¶30 |
| Eligibility | "Permissioned and open to BTC holders who are accredited investors and complete a KYC and AML onboarding process with Maple." Marketed to funds, family offices, HNWIs, treasuries and ETF issuers | Maple API `strategy`; Core blog |
| Minimum | **NOT FOUND.** Not in the API record or any article. Needs the offering memorandum or term sheet | — |
| Lock / redemption | 90-day lock at launch (CoinDesk, Feb 2025). Later "Bimonthly maturity, redemption notice required two weeks before next maturity date"; API `withdrawalDays: 60` | CoinDesk; Maple API |
| Fees | 0.40% per year management on BTC deposits, plus 20% performance fee on yield above 5% | OAK Research; bitcoin.com |
| Target / realised | Target "5%+" (Feb), "4–6%" (pool card), "3–5%" (OAK, Jun). Realised: 5.6% net (April), 5.6% since launch (May 2), 5.2% net (Q2), 5.13% (H1). **Final 2025 lender outcome: −15% principal withheld; post-settlement outcome not public** | `yield_history.csv` |
| Custody | BitGo and Copper (Maple and Core materials). Hex Trust was named as an lstBTC custodian only. On-chain: 4 owner scripts plus a taproot hub; I **cannot tie scripts to custodians (NOT FOUND)** | — |

## B. Mechanics, step by step (with parameters)

1. **Deposit / loan of BTC.**
   - The lender signs the master loan agreement and lends BTC to Maple International Operations SPC (BTC Staking SP 1).
   - The BTC sits at the custodian (BitGo or Copper) in wallets controlled for the SP.
   - Maple marketed this as "never lent, wrapped, or rehypothecated". Legally, though, the lender makes a BTC loan to the SP, and the SP then pledges that BTC for a USDC loan (see step 3).
2. **Bitcoin CLTV staking on Core.**
   - Each stake is a Bitcoin transaction paying to a P2WSH script `<locktime> OP_CLTV OP_DROP <custodian owner script>`, with an OP_RETURN naming the Core validator and the CORE reward address.
   - No bridge or wrap is involved. The BTC cannot move before the locktime.
   - ON-CHAIN: 221 stake transactions, 12,296 BTC gross (including re-stakes), across **33 validators**.
   - The locks were short and rolling. BTC-weighted: 65% of stakes locked ≤15 days, 24% for 36–65 days, 4% for 66–95 days.
   - Maturities were staggered, for example 1,000 BTC on 2025-05-15, 904 BTC on 08-20, 584 BTC on 10-15 and 757 BTC on 11-19.
3. **USDC borrowing against the BTC.**
   - "Maple uses the deposited BTC as collateral to borrow USDC through its internal infrastructure" (OAK).
   - The court record refers to obligations to "investors who loaned their Bitcoins" **or** "investors in another linked segregated portfolio". This strongly suggests the USDC came from another Maple-managed segregated portfolio or pool (inference).
   - **Lender identity: NOT FOUND. Rate: NOT FOUND.** Getting either needs the SP accounts or the loan confirmations. For context, Maple institutional loans price at about 6–12% (2026 memo), and the secured pool targets 9%.
   - **LTV ≈13–16% (EST)**, from USDC needed per BTC = tier ratio × CORE price. For example, 34,000 CORE/BTC × $0.50 = $17k per BTC against a $115k BTC price. It is consistent with the court's "584 Bitcoins, equivalent to roughly US$9 million" (= $15.4k per BTC), which I read as the USD needed to release those BTC.
4. **CORE purchase.**
   - ON-CHAIN, CORE flowed from a high-volume wallet (`0xe41bae1d…`, nonce > 109k, 44M CORE balance, likely an exchange; inference) → `0x9509e801…` → Maple funding wallet `0x34a8b81a…` → the reward addresses.
   - The staked CORE leg grew from 0.4M (Feb 6) to 39.6M (Apr 24), 45.5M (May 8) and **50.5M (Jul 10, 2025)**.
   - Court: Maple held ">40 million CORE tokens that they legitimately purchased themselves for over US$20 million". Core had also provided CORE "by way of collateral", and on Sept 26 Maple held "some US$27 million" of Core's assets.
   - EST cost basis of the leg: ≈$25–28M (average ≈$0.53–0.56).
5. **Protective puts (the hedge).**
   - Physically settled puts under the MTA of 27 Feb 2025. **Counterparty: Core Foundation** ("one of these third parties" per Core; Maple: "options supported by cash collateral provided by CORE Foundation under our agreement").
   - The collateral was US$5M cash.
   - Tenor: the expiries followed the BTC maturity schedule; puts "fell due on 30 September 2025, or will fall due on 15 October 2025".
   - Design: "structured protective put strategy at entry … to cover both principal and anticipated rewards"; "position sizing is capped based on hedge capacity" (OAK).
   - **Premium / cost: NOT FOUND.** Core calls its spending "subsidies of the product", which suggests the puts were free or cheap to Maple (inference). Getting the premium needs the MTA.
6. **Dual staking tier.** Maple kept the Satoshi (top) tier. The ON-CHAIN claim events show `dualStakingRate` 40000 → 60000/45000/32500 → 50000, which matches the Satoshi multipliers below. Core's thresholds, from BitcoinAgent governance events:

| Effective | Base | Boost | Super | Satoshi (CORE per BTC → multiplier) |
|---|---|---|---|---|
| 2024-11-20 | 0 → 20% | 1,000 → 35% | 3,000 → 85% | **8,000 → 1000%** (then 800/600/500/400%) |
| 2025-02-27 | 0 → 20% | 2,000 | 6,000 | **16,000 → 400%** (625% on 03-05, 230% on 03-25) |
| 2025-04-03 | 0 → 20% | 3,000 | 9,000 | **24,000 → 230%** |
| 2025-04-08 | 0 → 10% | 3,000 → 20% | 9,000 → 30% | **24,000 → 400%** (250% on 06-03) |
| 2025-06-13 | 0 → 10% | 3,625 | 10,875 | **29,000 → 600%** (450% 06-17, 325% 06-25) |
| 2025-07-15 | 0 → 10% | 4,250 | 12,750 | **34,000 → 500%** |
| 2025-11-11 | 0 → 10% | 8,500 | 25,500 | **68,000 → 500%** (current) |

   The required CORE per BTC rose **8.5×** in 12 months. Maple's CORE leg tracked it: 50.5M = 1,485 × 34,000.
7. **Rewards.**
   - Rewards arrive as CORE on the BTC leg and the CORE leg (4.66M CORE in total).
   - They were periodically sent to `0xc027ac0b…` and then on to the exchange-like wallet (7.4M CORE moved). This is consistent with "rewards converted back to BTC".
   - BTC yield was paid out from the hub. One identifiable lender address received 0.3077 BTC (Aug), 0.0662 BTC (Sep) and 0.045 BTC (Oct 2025) on an implied ~25 BTC principal. **Monthly per-lender distributions: NOT FOUND** beyond this one address.
8. **Redemption.**
   - Give notice 2 weeks before a bimonthly maturity.
   - At maturity, the SP must (a) let the CLTV expire, and (b) repay the USDC attached to that BTC by selling CORE or exercising the puts.
   - Then the BTC returns from the custodian wallet to the lender.
   - CORE can be unstaked at any time with no bonding period (Core docs). The binding constraints are the CORE sale / put settlement and the CLTV date.

## C. Counterparty chain and who owns the liquidity at each step

```
Lender BTC ──loan (MLA, auto-roll)──► Maple Int'l Ops SPC – BTC Staking SP 1  (owns BTC claim; lender = unsecured? creditor of the SP)
    │                                          │
    │  custody: BitGo / Copper wallets (4 owner scripts + taproot hub)  ◄── custodian holds keys; SP is beneficial owner
    │                                          │
    ├─► Bitcoin CLTV P2WSH outputs (locked until maturity; no third party can move them, custodian can't either before locktime)
    │                                          │
    ├─► pledged as collateral for USDC loan ◄── USDC lender (likely "another linked segregated portfolio" of Maple – inference)
    │                                          │
    ├─► USDC → CORE bought on market/OTC (≈50.5M CORE, owned by SP) + CORE posted by Core Foundation as collateral
    │                                          │
    ├─► CORE put options (physically settled) ◄── writer: Core Foundation (+US$5M cash collateral)   ← wrong-way risk
    │                                          │
    └─► Core validators (33 used; e.g., DAO pools, Solv, stc Bahrain, BTCS…) – no custody, only reward attribution
```

- **Liquidity ownership.**
  - BTC: the custodian (keys) and the SP (legal owner). The lender has a contractual claim on the SP.
  - CORE: the SP's reward addresses.
  - The hedge value depends on Core Foundation's willingness and ability to pay (it stopped).
  - The USDC lender has a security interest in the BTC.
- **What changed in the crisis.** When Core stopped honouring puts and obtained an injunction freezing all CORE dealing, the SP could not turn CORE into USDC. It therefore could not release the BTC that secured the USDC. That produced the "impairment", the 85/15 split and the holdback.

## D. Who manages it (people, risk, audits, dispute)

- **Maple.**
  - **Sidney (Sid) Powell**, co-founder and CEO: the public face, with quotes on BTC yield (Feb 2025).
  - **Joe (Joseph) Flanagan**, co-founder and Executive Chairman: swore the defendants' affidavits of 7 Oct 2025.
  - 2026 hires (not tied to BTC Yield): Conor O'Hanlon (General Counsel), Tarek Court (Head of Trading), Natalie Williams (Head of Marketing).
  - A Maple "Risk Committee" approves collateral (per the 2026 rsETH post). **A named risk team for BTC Yield: NOT FOUND.**
- **Core side.**
  - **Richard (Rich) Rines**, Core Foundation "operational lead" and affiant.
  - **Hong Sun**, institutional contributor at Core DAO (lstBTC PR).
- **Counsel.** Conyers Dill & Pearman (Core Foundation); Travers Thorp Alberga (Maple).
- **Judge.** Hon. Justice Jalil Asif KC, Grand Court of the Cayman Islands (FSD).
- **Audits and attestation.**
  - BTC Yield had **no Maple smart contracts**. Its security rested on the custodians, Bitcoin CLTV scripts and the SPC ring-fence.
  - Core's staking contracts are open-source genesis contracts.
  - Promised "monthly transparency reports" and "wallet-level attestations" (Core blog): **not public (NOT FOUND)**.
  - Maple's audits (Trail of Bits, Spearbit, Three Sigma and others) cover the Maple v2 / Syrup contracts, not this product.
- **Dispute timeline** (full detail in `events.csv`):

| Date | Event |
|---|---|
| mid-2025 | Core alleges Maple began building syrupBTC with Core's confidential information in breach of the 24-month exclusivity |
| Sep 2025 | Arbitration commenced |
| 26 Sep 2025 | **Ex parte** injunction. Bars syrupBTC ("or any … variant") and **any dealing in CORE, including staking, unstaking, options and hedges**. The judge relied partly on Maple holding ~US$27M of Core's assets as security for Core's cross-undertaking |
| 30 Sep 2025 | Puts due. Core stops paying ("as we considered we were directly subsidizing a competitive product") and terminates the agreements |
| 10 Oct 2025 | Maple's urgent application to exercise the puts and sell CORE is **refused**: the evidence of lender repayment demands was incomplete, and some pages of a Flanagan exhibit "appeared to have been changed or substituted" after it was sworn. Maple offered TWAP selling and said it held >40M CORE. Core said it would consent to trades if Maple proved identified lender repayment calls |
| 19–21 Nov 2025 | Public fight. Core: "unclear why Maple maintains that they are unable to return the Bitcoin … or if they have the right to impair them". Rines: lenders should take legal advice before signing any waiver. Maple: program ring-fenced; unwind began because of the CORE decline; "return 85% … 15% retained" |
| 22 May 2026 | **Full and final settlement.** Mutual release; arbitration and FSD 268 of 2025 discontinued on consent; terms confidential; no admission. Maple "will proceed with the launch of … syrupBTC". **Terms (who paid whom, the puts, the holdback): NOT FOUND.** Getting them needs the settlement deed or a lender notice |

## E. Yield

**Disclosed history (net to lenders, BTC-denominated).**

| Point | Figure |
|---|---|
| Launch target (Feb 2025) | 5%+ |
| Pool card (Mar 2025) | 4–6% |
| April 2025 | 5.6% net |
| Since launch (as of May 2) | 5.6% |
| OAK (Jun 23) | 5.1–5.6% (5.3% since launch) |
| Q2 2025 | 5.2% net |
| H1 2025 (Jul 7) | 5.13% |

After July 2025 nothing was disclosed. **Monthly realised APY is NOT FOUND after Q2 2025.** Getting it needs the monthly transparency reports.

**On-chain components** (`yield_history.csv`, `raw/core/maple_yield_model.csv`): gross dual-staking yield in BTC terms (CORE rewards × CORE/USD at claim ÷ BTC staked × BTC/USD). The claims are lumpy, so single months are noisy.

| Month | Avg BTC staked | CORE rewards (BTC leg + CORE leg) | Avg CORE $ | Implied gross % p.a. |
|---|---|---|---|---|
| 2025-04 | 1,016 | 167.7k | 0.589 | 1.6 |
| 2025-05 | 1,564 | 678.0k | 0.793 | 3.9 |
| 2025-06 | 1,322 | 403.9k | 0.585 | 2.0 |
| 2025-07 | 1,439 | 423.9k | 0.540 | 1.6 |
| 2025-08 | 1,482 | 180.9k | 0.479 | 0.6 |
| 2025-09 | 1,480 | 480.4k | 0.430 | 1.5 |
| 2025-10 | 1,021 | 939.2k | 0.286 | 2.2 |
| 2025-11 | 454 | 345.3k | 0.176 | 2.0 |
| **Program (Feb–Nov 2025)** | 848 BTC-yr | **4.66M** | 0.527 (BTC-weighted) | **1.9 (range 1.9–2.7)** |

**CORE price** (Bybit close):

| Date | CORE price |
|---|---|
| 2025-02-06 | $0.52 |
| May 2025 | $0.79–0.90 |
| 2025-07-15 | $0.55 |
| 2025-09-26 | $0.39 |
| 2025-11-19 | $0.16 |
| 2026-03-28 → 2026-03-31 | $0.066 → $0.028 (−58%) |
| 2026-09-21 | $0.022 (market cap ≈$33M) |

- **Effect on the carry.** The BTC-leg reward per BTC is paid in CORE, so its USD value falls one-for-one with CORE. The Satoshi-tier requirement moved from 16k to 68k CORE/BTC, which forced more CORE per BTC (more USDC, higher LTV) to hold the tier.
- **Current reference rates (2026-09-21, stake.coredao.org API).** Validator `btcStakeApr` 0.39–0.56%; CORE-staking APR 2.4–4.8%; total BTC staked on Core **2,210 BTC** (versus ≈5,000–7,000 in 2025); 300M CORE staked.

**How the 5%+ was met (EST, per BTC per year at July 2025 parameters).**

| Component | Value |
|---|---|
| BTC-leg rewards | ≈3,600 CORE × $0.50 ≈ $1.8k (1.6%) |
| CORE-leg rewards | ≈3% × $17k ≈ $0.5k (0.4%) |
| USDC cost | ≈9% × $17k ≈ −$1.5k (−1.3%) |
| **Net staking carry** | **≈ +0.7%** |

The marketed 5.1–5.6% net means ≈5.5–6.2% gross, so a gap of about **4.5–5.5 pp**, or ≈$7–8M per year on ≈1,485 BTC. That is consistent with Core's "we honored every put expiry for months, paying out millions of dollars", and with strikes set to protect "principal and anticipated rewards". **Conclusion (EST): most of the lender yield was a Core-Foundation-funded subsidy delivered through the puts, not staking income.**

**Negative-APR scenarios and whether they happened.**

| Scenario (per BTC, 1 year, LTV 15%) | Carry (EST) |
|---|---|
| Base (CORE flat, puts honoured) | +0.5–1.5% before subsidy; 5%+ with subsidy |
| USDC cost > rewards (e.g., CORE at −40% for the year with rewards falling in step) | ≈ −0.5% before hedge |
| CORE −50%, hedge fails | ≈ −7% |
| **CORE −94% (actual Sep 2025 → Mar 2026), hedge fails** | **≈ −14 to −15% of principal** → matches the 15% holdback |
| Tier doubling (Nov 11, 2025) without buying more CORE | Drop from Satoshi (500%) to Super (30%): BTC-leg rewards −94% |

**Did it happen?** Yes. From Sept 2025 the hedge stopped working. Core stopped paying, and the injunction froze exercise and sales, so the lenders' result for 2025 was **−15% of BTC principal withheld**, pending the outcome. The staking rewards themselves stayed positive. The final lender recovery after the June 2026 transfer of the 200 BTC is **NOT FOUND**.

**The "impairments" Core alleged.**
- Core said Maple told it that it "need[s] to declare an impairment to the value of millions of dollars against Bitcoin lenders".
- Mechanically, the SP owed USDC secured on lenders' BTC. Its CORE had lost most of its value, and its put claims were contested and frozen. So part of the BTC had to be kept back to cover the USDC shortfall.
- That shortfall is 15% ≈ 200 BTC ≈ $17M at the time, which is close to the EST CORE-leg loss.
- **Stability: poor.** Returns were stable only while the subsidy lasted (~Feb–Aug 2025).

## F. Risk management

- **Margin on the USDC loan.** At LTV ~15%, BTC price risk was small: it would take a ~80–85% BTC fall to breach typical thresholds. **Margin terms: NOT FOUND.** The real risk sat in the collateral the USDC bought (CORE), not in BTC.
- **CORE price risk.**
  - Hedged only through the partner's puts: a single counterparty that was also the issuer, with $5M cash collateral against a ~$25M+ CORE position (≈20% coverage, EST).
  - The hedge failed exactly when it was needed: CORE fell with Core's own fortunes (Core chain DeFi TVL went from $877M in Feb 2025 to $47M in Dec 2025 and $5M in 2026, per DefiLlama).
  - Liquidity was also a risk. 50.5M CORE is ≈3.4% of circulating supply, and the court was told daily volume was around 66M CORE at $0.40.
- **Liquidity and redemption.** BTC is locked until each CLTV date. The lender's liquidity also depends on the USDC being repaid, which requires CORE liquidity or put settlement. The 60-day/bimonthly cycle with 2-week notice does not provide liquidity on demand. Loans auto-roll unless a lender demands repayment.
- **Custody risk.** Qualified custodians (BitGo, Copper). The CLTV scripts mean even the custodian cannot move BTC before maturity. I saw no custody incident. All 221 staked outputs were spent only after maturity, into re-stakes, the hub wallet or other wallets that look like the program's own (I did not verify every destination).
- **Legal / partner risk (it materialised).**
  - The exclusivity dispute let the partner (a) stop hedge payments and (b) obtain an ex parte freeze of every CORE action, including unstaking and hedging.
  - The segregated-portfolio ring-fence protected Maple's other products (syrupUSDC and syrupUSDT were unaffected), but *not* this product's lenders.
- **Protocol-parameter risk.** Core governance can change tier thresholds and multipliers at any time. It did so 16 times, including 8,000 → 68,000 CORE/BTC.

## G. Depositors

- **Named clients: NOT FOUND.** Maple and Core named only target segments.
- **ON-CHAIN proxy from the Nov 2025 wind-down.** 66 payout addresses received 85% of principal.
  - The payouts look like 85% of round principals: 8.5 = 85% × 10, 21.25 = × 25, 42.5 = × 50.
  - Implied principal per address: **median ≈10.3 BTC, mean ≈20.2 BTC**.
  - 49 addresses ≥5 BTC; 37 ≥10; 17 ≥25; 5 ≥50; 2 ≥100.
  - **Largest ≈131 BTC (≈9.8%)**; top-5 ≈33% of principal.
- **Caveat.** An address is not a client. One lender may use several addresses, and a custodian omnibus address may cover several lenders. EST client count: **~50–66**.
- **Other on-chain signs.** A few lenders redeemed at earlier maturities: Sep 2025 outflows of 61, 25, 15 and 12 BTC to external addresses. Payouts were preceded by 0.0001 BTC test transfers, which is institutional whitelisting behaviour.

## H. Size growth by month

On-chain staked BTC is the 1st of each month unless noted. The full series (with the 15th of each month) is in `size_history.csv` and `raw/core/maple_cluster_daily.csv`.

| Date | BTC staked on Core | ≈USD | Share of Core BTC staking | Disclosed |
|---|---|---|---|---|
| 2025-02-15 | 82 | $8M | 1.4% | launch |
| 2025-03-01 | 156 | $13M | 2.9% | |
| 2025-04-01 | 476 | $41M | 8.8% | |
| 2025-05-01 | 1,570 | $151M | 24.5% | 1,600+ BTC (Apr 30 / May 2) |
| 2025-05-14 (peak) | 1,758 | $182M | ~24% | |
| 2025-06-01 | 1,211 (maturity roll) | $128M | 28.7% | $140M (Jun 23); ">$180M" (Q2) |
| 2025-07-01 | 1,396 | $148M | 27.5% | ">1,500 BTC", $140M (Jul 7) |
| 2025-08-01 | 1,485 | $168M | 28.9% | |
| 2025-09-01 | 1,485 | $162M | 30.1% | |
| 2025-10-01 | 1,341 | $159M | 28.7% | |
| 2025-11-01 | 757 (program BTC ≈1,341) | $83M | 18.0% | |
| 2025-12-01 | 0 (holdback 200 BTC off-Core) | — | 0% | Core: ">$150m" cumulative |
| 2026 (all months) | 0 | 0 | 0% | — |

- Why the size stopped growing: there were **no new net inflows after mid-2025**. Maple's hub wallet shows external inflows of 1,615 BTC (Jun 2025), 464 (Jul), 71 (Aug), 344 (Sep) and 23 (Oct), which were most likely consolidations of matured stakes rather than new deposits (inference).
- Maple's year-end target of $1.5B (bitcoin.com / OAK) was never approached.

## I. Growth drivers and what stalled it

- **Drivers.**
  1. Core's co-marketing and "subsidies": the Consensus HK launch, the Core blog, and puts that underwrote a 5%+ BTC yield.
  2. Native custody with no wrapping, through BitGo and Copper, which suited institutions.
  3. It was one of the few ~5% "native BTC" yields in H1 2025.
  4. Maple's institutional distribution. Core claims the BTC product "helped to kick-start explosive growth for Maple" (Maple under $500M AUM at the partnership; DefiLlama Maple TVL went from $298M in Mar 2025 to $3.1B in Nov 2025).
- **What stalled it.** Growth stopped at ~1.5–1.76k BTC by June 2025, before the dispute. Reasons:
  1. **Hedge capacity**: "position sizing is capped based on hedge capacity", and Core was the hedge writer.
  2. The tier ratio went from 24k to 34k CORE/BTC (Apr–Jul 2025), requiring more CORE per BTC.
  3. CORE's steady decline from its May 2025 high.
  4. Maple pivoted to syrupBTC (Core alleges from mid-2025). lstBTC never launched.
- **Then the dispute ended it.** Sep–Nov 2025: puts unpaid, injunction, wind-down, 85/15.
- **Custodian integrations.** BitGo and Copper held the product's BTC. Hex Trust was only in the lstBTC announcement. **lstBTC mint or holders: none found** (Core system lstBTC supply = 0; no ERC-20 found; the pages were removed).
- **Maple's broader growth** (syrupUSDC/USDT; $4.6B AUM at end of H1 2026, $4.8B in Aug 2026) was not driven by BTC Yield after Q3 2025. Maple's 2026 materials do not mention the product.

## J. Economics

**Maple fee revenue (EST).**

| Item | Estimate |
|---|---|
| Management fee | 0.40% × ~$150M average × ~0.75 yr ≈ **$0.45M** |
| Performance fee | 20% × (≈5.5% gross − 5%) × ~$150M × ~0.5 yr ≈ **$0.1M** |
| **Lifetime fees** | **≈$0.5–0.6M** |
| Annualised at peak | ≈$0.8M |

For comparison, Maple's ARR was $15M in Q2 2025. Legal costs of the dispute (both sides "fully funding") probably exceeded these fees (inference).

**CORE incentive economics (Core Foundation's side, EST).**
- Core paid "millions" in put settlements (Mar–Aug 2025), posted $5M cash collateral and supplied CORE as collateral.
- In return Core got:
  - ~1.5–1.76k BTC of staked BTC (≈24–30% of all BTC staked on Core);
  - ~50M CORE of demand (≈3.4% of circulating supply);
  - validator decentralisation (Maple spread its stakes over 33 validators);
  - the headline "institutional BTC yield".
- Implied subsidy cost ≈ $0.6M per month ≈ 4–5 pp per year on ~$160M of BTC (EST).
- **The CORE leg itself (EST).** Bought for ≈$25–28M; worth ≈$8.3M at 2025-11-19 and ≈$1.4–3.3M when unstaked in Mar–May 2026.
- **Loss ≈$22–26M.** It was absorbed by some mix of the SP/lenders (the 15% ≈ $17M at the time), the USDC lender, Maple, and Core (via the settlement). **Allocation: NOT FOUND (confidential).**
- **Timing of the CORE exit (on-chain, not a causal claim).**
  - 25.9M CORE was unstaked and moved on 2026-03-29 to 04-02, through intermediates to low-nonce forwarding addresses.
  - CORE fell ~49% on 2026-03-29. Core DAO attributed the fall to "a series of large sell orders" and a Colend liquidation cascade.
  - The injunction was still in force then, so these moves presumably had Core's consent. **Consent: NOT FOUND.**

## K. Verdict for our product design

**Copy:**
- **Native custody with a CLTV time-lock and no wrap.** The custodian keeps the keys, and the CLTV means no one can move the BTC before maturity.
- **Staggered short locks.** They matched the maturities to the lender calendar.
- **A segregated-portfolio (SPC) wrapper per product.** It contained the damage to this product; syrupUSDC and syrupUSDT were untouched.
- **Institutional hygiene.** Test transfers and bimonthly maturities with notice.
- **Spreading stakes across many validators.**

**Avoid:**
- **A yield engine made of a small-cap token's emissions.** Real staking income was ≈1.9–2.7% gross, versus 5%+ promised.
- **Hedging that token with puts written by its issuer / partner.** That concentrates wrong-way risk: the counterparty weakens exactly when the hedge pays. It was also under-collateralised ($5M cash against ~$25M+ notional).
- **Marketing "no lending risk" when lenders' BTC secures a USDC loan.** Disclose the LTV, the USDC lender and the impairment waterfall upfront.
- **Depending on a partner who can freeze your hedge and inventory through exclusivity terms.** Keep contracts with no-freeze and step-in rights.
- **Building to a governance parameter that can double overnight** (the tier ratio went 8k → 68k CORE/BTC).
- **Holding 3–4% of a token's float with no exit capacity.**
- **Stopping disclosure after the good months.** No monthly performance data was published after Q2 2025.

**Our rule.** If we pair "BTC collateral + dollar loan → strategy", the strategy leg must:
- be liquid enough to repay the loan within one maturity cycle;
- be hedged with independent, well-collateralised counterparties;
- earn its target *without* partner subsidies, so we stress-test with the subsidy set to zero;
- come with a published per-lender waterfall for shortfalls.

---

## Sources (primary first)

- **Cayman Grand Court.**
  - [2025] CIGC (FSD) 105 (ex parte injunction, 26 Sep 2025, published 30 Oct 2025): https://judicial.ky/n0c-storage/judgments-repository/2025_cigc_fsd_105__core_foundation_v_maple_international_operations_spc.pdf
  - Judgment of 10 Oct 2025 (filed 2 Dec 2025): https://judicial.ky/n0c-storage/judgments-repository2/FSD0268202512022025COREFOUNDATIONMAPLE.pdf
  - Text copies: `raw/jud_105.txt`, `raw/jud_1202.txt`.
- **Settlement (Maple, 2026-05-22).** https://maple.finance/insights/core-foundation-and-maple-international-operations-spc-reach-full-and-final-settlement
- **Maple statement (2025-11-21, X article).** https://x.com/maplefinance/status/1991886803092091268. Also https://x.com/maplefinance/status/1991214703725735961 and https://x.com/maplefinance/status/1917628219223859367 (read via api.fxtwitter.com).
- **Core Foundation statement (2025-11-19).** https://x.com/Coredao_Org/status/1991171121534636264. Rich Rines: https://x.com/richrines/status/1991195611446518267
- **Maple GraphQL.** https://api.maple.finance/v2/graphql: `poolMeta(id:"67e542004191822941f9e703")`, `poolsMeta`, `syrupTokens`, `assets`.
- **Maple site.**
  - https://maple.finance/insights/q2-2025-maple-market-update
  - https://maple.finance/insights/one-maple
  - https://maple.finance/insights/maple-memo-september-2026
  - https://maple.finance/insights/maple-q2-2026-ecosystem-update
  - https://maple.finance/insights/allocation-strategies
  - Maple docs (legal structure of the SPs): https://docs.maple.finance/llms-full.txt
- **Core.**
  - Blog: https://coredao.org/blog/maple-core-bitcoin-yield-product
  - Docs: dual staking, tier adjustment, CORE staking.
  - Staking API: https://stake.coredao.org/api/staking/* (candidate list, btc_lst_apr, market price).
  - RPC: https://rpc.coredao.org (BitcoinStake 0x…1014, BitcoinAgent 0x…1013, CoreAgent 0x…1011, StakeHub 0x…1010, lstBTC 0x…010001).
  - Explorer API: https://scan.coredao.org/api/chain/address_transaction
- **Bitcoin.** https://mempool.space/api (staking transactions, outspends, hub `bc1pm9v0y2gjh4hjm6wp7vsaqwzf96ugsrtzs9ujcawdm880fveuzrcs3c0pc4`, holdback path `bc1pdcj7…` → `bc1pyed82…` → `bc1q9tfmg8…` → `bc1q5zly2ljxhtm3gycyum93czupz9k04gcse6emg6`).
- **Market data.** Bybit spot klines (CORE, BTC). CoinGecko simple price (CORE $0.0222, market cap $33.3M on 2026-09-21). DefiLlama (`maple` TVL; CORE chain TVL).
- **Secondary.**
  - CoinDesk 2025-02-17 and 2025-11-20
  - GlobeNewswire 2025-02-20 (lstBTC)
  - OAK Research 2025-06-23
  - bitcoin.com 2025-07-07
  - The Block 379601
  - DL News
  - Protos
  - Coinpedia (CORE crash, Mar 2026)
  - @catwychan thread 2025-11-22 (independent explanation of the USDC leg)
