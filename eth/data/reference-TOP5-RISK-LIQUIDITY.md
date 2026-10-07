# Top-5 ETH carry: risk history, liquidity ladder, reward payers

Snapshot **T = 2 Oct 2026 23:59:59 UTC**, Ethereum block **26,108,081**. Monthly samples are the last block of each month (Oct 2024–Sep 2026), the same blocks as `economic-dollar-loans.csv`. Pulled on 7 Oct 2026.

Data: [`gap_top5_risk_series.csv`](../../../../data/eth/gap_top5_risk_series.csv) (long format), [`gap_top5_liquidity_ladder.json`](../../../../data/eth/gap_top5_liquidity_ladder.json), [`gap_top5_rewards.json`](../../../../data/eth/gap_top5_rewards.json). Scripts: [`tools/eth/gap_top5_risk/`](../../../../tools/eth/gap_top5_risk/). Raw pulls: `raw/eth/gap-2026-10-07/top5-risk/`.

Scope: only dollar debt secured by ETH collateral. ETH-on-ETH loops and Liquid's PRIME→PYUSD loop are excluded from the totals (they are named where they matter).

## Findings

1. **The prior debt history was wrong for Lido Earn and Avant.** Per-reserve reads of every borrowed asset replace the earlier leg list.
   - **Lido Earn, Nov 2025–Mar 2026:** the 34.5–53.5M USDC on `0x9938a09f` is a **USDe/sUSDe e-mode loop**, not ETH-collateral carry (Aave e-mode 2, LT 92%, HF 1.03–1.13). The ETH-collateral debt in those months sits on `0x181cb55f` and was partly missed. It includes USDe borrowing: 8.2M in Dec, 20.0M in Jan, 19.2M in Jul and 16.3M in Aug.
   - **Corrected Lido Earn ETH-collateral debt by month:**

     | Nov | Dec | Jan | Feb | Mar | Jun | Jul | Aug |
     |---:|---:|---:|---:|---:|---:|---:|---:|
     | 8.0M | 27.2M | 27.3M | 5.8M | 19.8M | 20.3M | 20.4M | 20.5M |

     The prior figures were 34.5M, 42.8M, 43.2M, 47.3M, 64.5M, 10.0M, 1.2M and 4.2M.
   - **Avant had dollar debt in every month from Sep 2025.** The prior file shows zero for Nov 2025–Mar 2026 and Jul 2026. The real range is 2.4–11.3M, with Spark USDC/USDT and Aave USDT/USDe legs added.
   - **Liquity had small troves at the Mar–May 2026 month-ends** (0.01M, 0.04M and 0.41M ebUSD). The prior file shows zero.
2. **Liquid's dollar sleeve runs negative carry at T.**
   - **Cost:** 181.1M of debt costs about **$14.1M/yr**. Of that, **$9.0M/yr** is the 64.5M Aave USDC drone loan at **13.93%**. Aave Core USDC has been 12.6–14.1% at every month-end since Jun 2026.
   - **Income from measured claims:** **$7.3M/yr**, made up of
     - $4.7M/yr base yield (senRLUSDv2 2.80%, senPYUSDPRIMEv2 3.61% and stcUSD 5.64%, all 30-day);
     - $2.6M/yr Merkl rewards.
   - **Net:** about **−$6.8M/yr**. Debt-weighted borrow APR was 14.25% at the Sep month-end because the Morpho RLUSD and PYUSD rates spiked at that block. It was 7.79% at T.
3. **The other four have thin or structural spreads at T** (borrow vs 30-day parking APR):

   | Product | Borrow | Parking | Spread | Note |
   |---|---:|---:|---:|---|
   | Lido Earn | 4.33% | earnUSD 4.80% | +0.5 pp | |
   | Avant | 6.30% | savUSD 7.54% | +1.2 pp | |
   | YieldBasis | 10.00% (fixed AMM rate) | Curve WETH/crvUSD LP 9.19% | | LP fee accrual on 2× the debt, so fees cover interest |
   | Liquity ETH Carry | 2.55% (borrower-set) | Curve ebUSD/USDC 0.45% (fees only) | negative | The dollar leg does not pay for itself; the low rate also places the trove early in the Ebisu redemption order |

4. **Liquidation distance at T** (worst leg per product):

   | Product | Worst leg | HF | ETH move to liquidation |
   |---|---|---:|---:|
   | Liquid | Morpho weETH/RLUSD (main vault), LLTV 86% | **1.268** | **−21%** |
   | Avant | Spark / Aave | 1.37 / 1.38 | −27% |
   | Liquity | Ebisu trove | 1.88 | −47% |
   | Lido Earn | Aave | 2.12 | −53% |

   - **Lowest month-end HF in the sample:**
     - Liquid 1.23 (Jun 2026, LoanManager RLUSD leg);
     - Avant 1.32 (Sep 2025);
     - Lido 1.49 (Dec 2025).
   - **YieldBasis has no liquidation engine.** Its LEVAMM holds debt/value at 50% (range 49.8–50.2% at every month-end). The critical ratio is 56.25%, which gives an HF-equivalent of 1.12.
5. **Same-block repayability.** "Same-block repayable" means the strategist can repay that share from destination liquidity readable at T.

   | Product | Same block | ~1 day | Slower | No destination claim found |
   |---|---:|---:|---:|---:|
   | Liquid | 35.8% currency-matched (64.8M), +13.4% with a PYUSD→USDC swap | 0 | 25.1% | **25.6% (46.4M)** |
   | YieldBasis | 99.6% (+0.4% swapped in the same pool) | | | |
   | Liquity | 97.5% via Curve one-coin exit (+2.5% from idle WETH) | | | |
   | Lido Earn | 0% | 100% (earnUSD redeem queue) | | |
   | Avant | 2.4% (Ethereum wallet) | | 97.6% (savUSD on Avalanche) | |

   - **Liquid's "no claim found" share** is debt with no dollar claim on Liquid's three accounts.
   - **Lido Earn's queue settles at the next oracle report**, which comes about every 24h. Lido's carry account owns **48.5% of all earnUSD**.
   - **Avant's slower share** needs the 24h savUSD→avUSD cooldown, then a bridge, then avUSD redemption of up to 7 days.
6. **Issuer-side wallets fund Liquid's rewards; Sentora only creates the campaigns.**
   - **RLUSD campaigns:** created by Safe `0xCc6d…e000` (Merkl tag "sentora"). The tokens trace back through five unlabelled EOAs to `0xFbcA8B5f…` "MultiSign", which receives RLUSD directly from mint.
   - **PYUSD campaigns:** created by Safe `0x4307…1609` (tag "sentora-pyusd"). The tokens trace to `0x264bd829…`, an EOA that receives PYUSD directly from mint.
   - **Reward rate at T:**
     - Liquid: **$2.60M/yr**, which is 2.0% on its 129.3M of Sentora/Cap claims and **1.4% of its ETH-collateral debt**.
     - **stcUSD and earnUSD:** no Merkl program.
7. **Liquid partly borrows from itself.**
   - **RLUSD:** Sentora RLUSD Main has 107.0M (24%) of its assets in the weETH/RLUSD market that Liquid borrows 70.2M from. Liquid holds 12.4% of that vault.
   - **PYUSD:** Sentora PRIME Main's only market is PRIME/PYUSD. Liquid holds 22.6% of that vault and also borrows 21.0M PYUSD in that market against 24.8M PRIME (LTV 79.7%, LLTV 86%, HF 1.08).
   - **Effect on exit:** 21.7M of Liquid's 49.6M senPYUSDPRIMEv2 claim cannot leave in the same block.

## Monthly series (product aggregate, ETH-collateral dollar legs only)

Collateral is the dollar-debt share of each account's collateral. The liquidation threshold is collateral-weighted, and HF is Σ(collateral×LT)/debt. Parking APR is the simple annualized change in destination share price since the previous month-end; T uses the 30-day window from 2 Sep. Months with no debt are omitted; all months are in the CSV.

**ether.fi Liquid ETH.** Accounts:
- `0x0a42b2f3` (drone): Aave USDC/USDT against weETH; Spark PYUSD against wstETH.
- `0xf0bb2086` (main vault): Morpho weETH/RLUSD and weETH/USDC.
- `0xc936e848` (LoanManager): Morpho weETH/RLUSD.

| Month | Collateral $M | Dollar debt $M | LTV | LT | HF | Borrow APR | senRLUSDv2 / senPYUSDPRIMEv2 / stcUSD |
|---|---:|---:|---:|---:|---:|---:|---|
| 2025-08 | 117.9 | 47.07 | 39.9% | 80.0% | 2.00 | 5.61% | – / – / 12.61% |
| 2025-09 | 111.7 | 52.31 | 46.8% | 80.0% | 1.71 | 5.58% | – / – / 11.61% |
| 2026-06 | 17.2 | 11.99 | 69.7% | 86.0% | 1.23 | 3.02% | 1.76% / 3.24% / 5.05% |
| 2026-07 | 74.3 | 42.64 | 57.4% | 83.8% | 1.46 | 7.03% | 2.52% / 3.46% / 5.15% |
| 2026-08 | 268.6 | 165.83 | 61.7% | 83.5% | 1.35 | 7.29% | 2.77% / 3.88% / 5.06% |
| 2026-09 | 303.6 | 183.37 | 60.4% | 83.3% | 1.38 | 14.25% | 2.71% / 3.56% / 5.54% |
| T | 308.9 | 181.08 | 58.6% | 83.4% | 1.42 | 7.79% | 2.80% / 3.61% / 5.64% (30d) |

**YieldBasis WETH.** LEVAMM `0x5f8d24f3`, LT `0x2b9c9f3b`. Collateral is Curve WETH/crvUSD LP at the LP oracle. "LT" is the 56.25% critical ratio. Parking is the LP virtual-price APR, i.e. fee accrual, not a dollar destination.

| Month | Collateral $M | Debt $M | LTV | LT | HF-eq. | Borrow | LP APR |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05 | 2.6 | 1.29 | 49.9% | 56.25% | 1.13 | 10.00% | – |
| 2026-06 | 15.8 | 7.95 | 50.2% | 56.25% | 1.12 | 10.00% | 15.79% |
| 2026-07 | 28.2 | 14.12 | 50.1% | 56.25% | 1.12 | 10.00% | 7.42% |
| 2026-08 | 61.2 | 30.48 | 49.8% | 56.25% | 1.13 | 10.00% | 6.82% |
| 2026-09 | 56.2 | 28.06 | 49.9% | 56.25% | 1.13 | 10.00% | 9.18% |
| T | 55.6 | 27.81 | 50.0% | 56.25% | 1.12 | 10.00% | 9.19% (30d) |

**Lido Earn ETH.** `0x181cb55f`, Aave and Spark, against wstETH. The USDe-loop account `0x9938a09f` is excluded from these totals but kept in the CSV with a flag.

| Month | Collateral $M | Debt $M | LTV | LT | HF | Borrow | earnUSD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025-11 | 15.6 | 8.01 | 51.5% | 81.0% | 1.57 | 4.78% | – |
| 2025-12 | 50.0 | 27.20 | 54.4% | 81.0% | 1.49 | 4.40% | – |
| 2026-01 | 50.2 | 27.28 | 54.3% | 81.0% | 1.49 | 3.58% | – |
| 2026-02 | 15.5 | 5.83 | 37.5% | 81.0% | 2.16 | 2.56% | – |
| 2026-03 | 56.1 | 19.84 | 35.4% | 81.0% | 2.29 | 2.97% | – |
| 2026-04 | 191.3 | 65.65 | 34.3% | 84.0% | 2.45 | 3.42% | 4.92% |
| 2026-05 | 34.5 | 12.46 | 36.2% | 84.0% | 2.32 | 3.40% | 4.77% |
| 2026-06 | 47.6 | 20.26 | 42.5% | 81.6% | 1.92 | 2.97% | 7.05% |
| 2026-07 | 54.4 | 20.39 | 37.5% | 81.0% | 2.16 | 3.18% | 6.02% |
| 2026-08 | 72.1 | 20.47 | 28.4% | 81.2% | 2.86 | 3.79% | 6.85% |
| 2026-09 | 68.7 | 25.54 | 37.2% | 81.4% | 2.19 | 4.31% | 4.92% |
| T | 68.1 | 25.55 | 37.5% | 81.4% | 2.17 | 4.33% | 4.80% (30d) |

**Avant avETH/savETH.** Strategy wallet `0x6cc60a0b`, Aave and Spark, against WETH/weETH/wstETH. savUSD yield comes from the Chainlink SAVUSD/AVUSD feed `0x9fbb7d07`, which has existed since Dec 2025.

| Month | Collateral $M | Debt $M | LTV | LT | HF | Borrow | savUSD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025-09 | 3.4 | 2.04 | 60.7% | 80.2% | 1.32 | 2.39% | – |
| 2025-10 | 8.2 | 4.33 | 52.7% | 81.1% | 1.54 | 4.43% | – |
| 2025-11 | 5.6 | 3.10 | 55.3% | 80.5% | 1.46 | 5.00% | – |
| 2025-12 | 7.8 | 2.89 | 36.9% | 80.0% | 2.17 | 4.65% | – |
| 2026-01 | 6.3 | 2.36 | 37.4% | 80.7% | 2.16 | 4.41% | 12.50% |
| 2026-02 | 7.4 | 4.30 | 58.3% | 81.7% | 1.40 | 3.38% | 7.95% |
| 2026-03 | 7.4 | 4.38 | 59.1% | 81.0% | 1.37 | 3.09% | 7.50% |
| 2026-06 | 6.2 | 3.71 | 60.0% | 82.1% | 1.37 | 5.72% | 7.82% |
| 2026-07 | 14.3 | 8.67 | 60.5% | 81.4% | 1.35 | 3.21% | 8.09% |
| 2026-08 | 19.4 | 11.28 | 58.2% | 82.4% | 1.42 | 3.79% | 8.57% |
| 2026-09 | 16.2 | 10.03 | 62.1% | 84.3% | 1.36 | 6.34% | 7.70% |
| T | 16.3 | 10.03 | 61.5% | 84.3% | 1.37 | 6.30% | 7.54% (30d) |

In Apr–May 2026 Avant borrowed WETH (an E3 loop), with dollar debt below $0.1M.

**Liquity ETH Carry.** Vault `0xb9e806e8`, Ebisu wstETH branch. Troves `0xcc51…` (March), `0xa7f1…` (April–May) and `0x17fd…` (June onward). LT is 1/MCR (MCR 120%); HF is ICR/MCR. The borrow rate is the trove's own annual rate.

| Month | Collateral $M | Debt $M | LTV | LT | HF | Borrow | Curve ebUSD/USDC |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-03 | 0.02 | 0.01 | 39.1% | 83.3% | 2.13 | 1.41% | 0.56% |
| 2026-04 | 0.07 | 0.04 | 53.1% | 83.3% | 1.57 | 0.88% | 0.60% |
| 2026-05 | 0.94 | 0.41 | 43.6% | 83.3% | 1.91 | 0.88% | 0.45% |
| 2026-06 | 0.8 | 0.47 | 55.9% | 83.3% | 1.49 | 3.27% | 0.91% |
| 2026-07 | 2.4 | 1.22 | 50.9% | 83.3% | 1.64 | 5.55% | 0.49% |
| 2026-08 | 6.1 | 3.28 | 53.7% | 83.3% | 1.55 | 6.35% | 0.50% |
| 2026-09 | 15.3 | 6.75 | 44.0% | 83.3% | 1.89 | 2.55% | 0.43% |
| T | 15.2 | 6.75 | 44.3% | 83.3% | 1.88 | 2.55% | 0.45% (30d) |

## Liquidity ladder at T

ETH released assumes each repaid leg keeps its LTV, and is converted at Chainlink ETH/USD $2,667.15. The ladder is the strategist's capacity, not an investor's exit right. For example, Liquity's 10% and 30% holder withdrawals revert at T.

| Product | Dollar debt | Same block | ~1 day | Slower | Not matched | ETH collateral if all repaid |
|---|---:|---|---|---|---:|---:|
| Liquid | 181.08M | 64.82M matched (35.8%, 39.0k ETH released) + 24.32M with swap (13.4%, 15.8k ETH) | 0 | 45.53M (25.1%) | 46.40M (25.6%) | 115.8k ETH-eq |
| YieldBasis | 27.81M | 27.70M (99.6%) + 0.11M in-pool swap | – | – | 0 | 10,469 WETH in the LP share; 99% preview 10,200.9 WETH |
| Lido Earn | 25.55M | 0 | 25.55M (earnUSD queue; claim 25.57M) | – | 0 | 25.5k ETH-eq wstETH |
| Avant | 10.03M | 0.08M eUSDC + 0.16M sdBOLD LP | – | 9.79M (savUSD, 1–7 days) | 0 | 6.1k ETH-eq |
| Liquity | 6.75M | 6.58M Curve one-coin + 0.17M idle WETH/V4 | – | – | 0 | 4,585.5 wstETH |

**Liquid's tiers in detail:**

- **Matched currency, same block:**
  - **senRLUSDv2:** Liquid's 55.10M RLUSD claim is fully withdrawable. The vault has 42.03M idle, plus 42.12M that can be force-deallocated at a 1 bp penalty; 12.47M of that sits in Liquid's own weETH/RLUSD market.
  - **senPYUSDPRIMEv2:** 3.61M PYUSD repays the Spark leg.
  - **stcUSD:** unstakes to cUSD in full (maxWithdraw = 24.63M). Cap holds only 6.11M of available USDC (61.44M supplied, 55.34M lent to agents), so 6.11M repays the Morpho USDC leg.
- **Same block with a swap:** 24.32M more PYUSD is reachable — 10.86M idle plus 17.07M that can be force-deallocated at a **1% penalty**. It must be swapped into USDC/USDT for the Aave drone; DEX depth was not checked.
- **Slower (45.53M):**
  - 21.68M of senPYUSDPRIMEv2 is locked in PRIME/PYUSD at 91.8% utilization;
  - 18.52M of cUSD waits on Cap agents repaying;
  - 5.34M of PRIME net of Liquid's own PYUSD loan, redeemed through Hastra in 1–2 business days.
- **No claim found (46.4M):** debt that exceeds the dollar destinations on Liquid's three accounts.

## Rewards at T

| Payer chain | Campaign / opportunity | Weekly amount at T | Annualized | APR on vault at T | Liquid's claim | Liquid $/yr |
|---|---|---:|---:|---:|---:|---:|
| RLUSD mint → `0xFbcA8B5f` MultiSign → 4 EOAs → Safe `0xCc6d…e000` (tag "sentora") → Merkl `0x3ef3d8ba` | Sentora RLUSD Main V2 (`2433802672589613459`) | 231,475 RLUSD | $12.07M | 2.72% | 55.10M | **$1.50M** |
| PYUSD mint → `0x264bd829` → EOAs → Safe `0x4307…1609` (tag "sentora-pyusd") → Merkl | Sentora PRIME Main V2 (`16103329905303288034`) | 93,575 PYUSD | $4.88M | 2.23% | 49.61M | **$1.10M** |
| same PYUSD creator | Paypal USD Main V2 (`18030207387280065324`) | 221,625 PYUSD | $11.56M | 2.98% | 0 (Liquid exited) | 0 |

- **Claimed by Liquid's main vault to date:**
  - RLUSD 192.4k;
  - PYUSD 133.6k from PRIME Main and 32.1k from PYUSD Main;
  - plus ETHFI 22.2k and rEUL 1.1k. These were paid on the E3 weETH/WETH legs by Safes tagged "aave" and "euler"; none were active at T.
- **No rewards on the other Liquid accounts:** the LoanManager and the drone have no Merkl rewards.
- **Campaign cadence:** weekly campaigns have run without gaps since July. The RLUSD budget rose from 193k to 246k per week, then fell to 231k in the T week.
- **Other products:**
  - **Liquity:** Uniswap V4 BOLD-USDC campaign from a creator tagged "liquity", about 200k BOLD/yr in total. That is roughly **$15k/yr** on the vault's 0.16M V4 book.
  - **Lido carry account and YieldBasis LT:** no Merkl rewards.
  - **Avant:** small Merkl claims (USDS, MORPHO, USDC, WFRAX), not tied to its debt.

## Method notes and limits

- **Collateral, debt and HF for Aave/Spark** come from `getUserAccountData` at each block.
  - **Per-asset legs:** the user-configuration bitmap gives the borrowed and collateral reserves. Debt is the variableDebtToken balance times the pool oracle price, with the reserve `currentVariableBorrowRate`.
- **Morpho:** `position`, `market` and oracle `price()`. Debt uses the stored share index (pending interest excluded).
- **YieldBasis:** `get_state`, `value_oracle` and `rate()`.
- **Ebisu:** `getLatestTroveData` with `lastGoodPrice`.
- **Borrow rates are instantaneous quotes at each sample block**, not realized cost. Month-end spikes (Liquid Sep: RLUSD 16.7%, PYUSD 20.1%) are real reads but not monthly averages.
- **Parking yields come from share-price changes.** The T row's "month" figure covers only two days (2026-09-30→T), so use the 30-day figure. Liquid's historical destination weights are not reconstructed; the per-destination series are shown side by side.
- **earnUSD price** is the inverse of oracle `0x82704473…getReport(USDT)`. **savUSD** is in avUSD and assumes avUSD at $1.
- **Ladder figures are fixed-block capacity.** They assume no competing withdrawals by other vault depositors in the same block, $1 stablecoins, and swap depth that was not checked.
- **Reward funder identities are unlabelled on-chain.** The trace ends at the address that receives tokens directly from the stablecoin's mint. Naming Ripple or PayPal/Paxos would need an off-chain source.
