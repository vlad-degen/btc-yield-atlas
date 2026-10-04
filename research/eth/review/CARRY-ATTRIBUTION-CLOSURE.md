# Historical carry-income attribution

Frozen financial snapshot: **2026-10-02 23:59:59 UTC**, Ethereum block **26,108,081**. New public captures were collected on 2026-10-04. They use historical state and logs through T, rather than current yield quotes applied to past positions.

The research now measures actual destination-claim growth, accrued borrowing costs, reward cash receipts and selected funding paths for Liquid ETH. It does not establish complete carry sleeve profit or explain the whole product's return. The distinction matters: a destination claim, a paid reward and an outstanding interest liability are different accounting components.

The final presentation input is `data/eth/carry_attribution_closure.json`. Detailed ledgers, raw captures, CSV exports and an independent verifier accompany it.

## A common period for the primary comparison

Every row below covers **2026-08-07 17:04:59 UTC to 2026-10-02 23:59:59 UTC**, or **56.2881944444 days**. The opening block, 25,704,466, is immediately before the first tracked RLUSD V2 deposit. Existing PYUSD claims and debt are marked at the same opening block. The comparison therefore preserves opening balances instead of assuming that every strategy began when the RLUSD position began.

Amounts stay in their native assets. RLUSD, PYUSD, USDC, cUSD, wYLDS, WETH and weETH are not summed as dollars or ETH. No one-dollar peg or historical conversion rate is invented.

| Measured component | RLUSD | PYUSD |
|---|---:|---:|
| Opening destination claim | 0.00 | 21,163,838.92 |
| Actual destination deposits | 57,027,780.85 | 58,698,538.46 |
| Cash withdrawn from destination | 2,068,990.75 | 30,421,967.97 |
| Ending destination claim | 55,104,709.54 | 49,605,232.78 |
| Net destination claim growth | **145,919.43** | **164,823.37** |
| Paid Merkl rewards to tracked accounts | **172,802.40** | **150,678.52** |
| Accrued ETH-collateral financing cost | 218,778.53 | 208,331.44 |
| Additional tracked financing cost | 186,738.39, LoanManager | 17,993.33, PRIME-backed |
| Opening tracked accrued debt | 26,857,219.04 | 15,606,464.21 |
| Ending tracked accrued debt | 70,211,978.15 | 21,017,993.33 |

The claim calculation is ending claim minus opening claim, plus withdrawals, minus deposits. It includes fees recognized in the destination's share value. It is not the sum of cash withdrawals and is not isolated gross organic interest.

Borrowing cost is ending accrued debt minus opening accrued debt, plus actual repayments, minus actual borrowed cash. Morpho debt shares reconcile to the exact contract positions. Pending interest is projected using the historical market state and the market's bound AdaptiveCurveIRM average-rate view, with Morpho's actual compounding and rounding rules. A current APR is never multiplied by the historical principal.

**These bars form a partial component comparison, not complete sleeve profit.** Loan and destination principal differ, earlier destinations are outside the selected ledgers, a cash reward can pay for an earlier earning period, own-credit interest has not been assigned to net destination income, and outer fees remain unallocated. In addition, measured USDC debt accrued **15,559.44 USDC** in this window. Some of that debt funds RLUSD or PYUSD deposits; it is shown separately rather than converted or silently charged to a same-currency bar.

The arithmetic component balances in the JSON are deliberately labelled partial. They must not appear as realized carry profit, total organic carry profit or the product's net return.

Sources: [captured opening state](../../../data/eth/carry_attribution_window_states.json), [captured T state](../../../data/eth/carry_attribution_states.json), [full income ledger](../../../data/eth/carry_attribution_ledger.json), [common-window claims CSV](../../../data/eth/carry_attribution_common_window_claims.csv), [common-window debt CSV](../../../data/eth/carry_attribution_common_window_debt.csv).

## What was actually paid

There are **43 RLUSD transfers** and **43 PYUSD transfers** from the documented Merkl distributor to the four tracked accounts during the common window. They total 172,802.40147222954 RLUSD and 150,678.520904 PYUSD. One ETHFI transfer in the window paid 54.25261576354828 ETHFI. These are observed token receipts, rather than advertised rewards or unclaimed estimates.

The distributor is `0x3ef3d8ba38ebe18db133cec108f4d14ce00dd9ae`. Its role is supported by [Morpho's primary reward-claim documentation](https://docs.morpho.org/developers/rewards/tutorials/claim-rewards/). A distributor payment alone does not identify the campaign sponsor, destination or earning period. Other distributors, redirected beneficiaries, unclaimed rewards and private payments are outside this capture.

The vault withdrawal ledger also distinguishes redeemed-share gain from retained claim gain using an explicit weighted-average purchase basis. During the common period, assigned redeemed-share gains are 350.48 RLUSD, 37,274.22 PYUSD and 49,792.72 cUSD. Most of the corresponding destination income remains in claims. This basis convention separates proceeds from returned principal; it does not prove a separately earmarked interest payment.

Sources: [actual reward receipts and dates](../../../data/eth/carry_attribution_cash_rewards.csv), [successful transaction receipts](../../../data/eth/carry_attribution_flows.json).

## Proven funding paths, with ordering enforced

The funding test follows exact loan-token receipts from Morpho through controlled-wallet transfers to destination payment. It processes events in receipt log order. A deposit before a loan receipt receives zero coverage, and cash consumed by an earlier transfer cannot be used again.

| Destination | Ordered same-token deposit links | Same-token loan cash coverage | Deposits alongside a different-token loan | Deposit cash still without same-transaction coverage |
|---|---:|---:|---:|---:|
| RLUSD V2 | 6 | 36,000,000.00 RLUSD | 18,672,780.85 RLUSD, 3 transactions | 2,355,000.00 RLUSD |
| PYUSD PRIME V2 | 6 | 39,400,000.00 PYUSD | 1,993,422.62 PYUSD, 1 transaction | 17,305,115.84 PYUSD |

The three RLUSD deposits co-occur with 18,681,524.170147 USDC borrowed. The PYUSD deposit co-occurs with 1,970,000 USDC borrowed. Loan receipts and destination payments are verified in their respective native assets. The cash graph does not turn them into an assumed one-for-one dollar conversion or assign every later earning to those loans.

The final count is **12 ordered same-token deposit links**, with **36.0 million RLUSD and 39.4 million PYUSD** covered. A receipt-level audit corrected an earlier 13-link, 42.4-million-PYUSD co-occurrence screen: a 3,611,570 PYUSD deposit at log 180 preceded the 3 million PYUSD loan at log 183 and cash receipt at log 184. The actual loan-funded payment occurs at log 187, followed by the 3 million PYUSD deposit at log 189. The earlier deposit remains unmatched.

Transaction: [2 October ordering example](https://etherscan.io/tx/0x3e66faeae23a347b524536ae17291e0f7c9d89c39bbba2e711cae76afd21e12d).

Unmatched cash is not assumed to be unborrowed. Opening claims, inventory, earlier loans, other lenders and transfers between transactions can contribute. Proving every funding path would require a wider inventory and transaction ledger.

Sources: [ordered funding links](../../../data/eth/carry_attribution_funding_links.csv), [cross-currency links](../../../data/eth/carry_attribution_cross_currency_funding_links.csv).

## Retained deposit cohorts provide a narrower check

For loans with no repayment, each actual minted debt-share cohort can be marked at T. A destination cohort is assigned an exact T claim only when no outgoing destination shares follow its deposit. This avoids an invented rule for choosing which purchased shares a later withdrawal redeemed.

Three USDC-financed RLUSD cohorts satisfy that retention test:

| Borrow/deposit date, UTC | USDC loan principal | RLUSD deposit | RLUSD claim growth to T | USDC accrued cost to T |
|---|---:|---:|---:|---:|
| 2026-09-22 22:42:35 | 2,903,973.87 | 2,902,064.71 | 2,596.64 | 4,043.46 |
| 2026-09-29 22:52:47 | 12,277,550.30 | 12,270,716.14 | 3,642.55 | 5,334.42 |
| 2026-10-02 18:48:23 | 3,500,000.00 | 3,500,000.00 | 60.13 | 103.42 |

The costs and income are different assets. No common-currency profit is reported.

The final 3 million PYUSD borrow/deposit pair is retained for **108 seconds**, from 2026-10-02 23:58:11 UTC to T. Exact historical calls value its destination claim at **3,000,000.557687 PYUSD** and debt at **3,000,000.751967 PYUSD**. Their lending-minus-financing component is **-0.194280 PYUSD**, before reward, own-credit and outer-fee allocation. This is a verification example, too short to establish strategy economics. No destination income was withdrawn and no loan interest was repaid on this cohort.

The larger 18 million PYUSD loan originated on 25 September has later destination withdrawals on 1 October. Its debt cost is measured, but its remaining destination cohort basis is not uniquely assigned. It must not be presented as a closed retained pair.

Source: [debt and retained destination cohorts](../../../data/eth/carry_attribution_tranches.json). Each retained claim comes from an exact `convertToAssets` call at block 26,108,081, rather than a price at an earlier block on 2 October.

## Interest can circulate through the product's own credit

Two selected destination markets lend to the same product accounts that also borrow from them. Historical reconstruction follows every relevant supply, withdrawal, borrow, repayment, market-interest event and destination-share transfer during the common window. It reconciles market assets and shares, adapter shares, borrower shares and product destination shares to T.

At actual accrual events, the gross interest overlap attributable to the product's contemporaneous borrower and lender ownership is **38,912.20 RLUSD** and **4,049.74 PYUSD**. The calculation uses 323 RLUSD and 647 PRIME/PYUSD interest events. It does not apply the T ownership share backward.

These figures are an economic overlap diagnostic. They are before destination fees, rate caps and pending fee dilution. They use ownership at recognition events, rather than an exact integration of ownership at each earning instant between events, and exclude pending interest after the last market update. They are neither extra income nor proof that a particular interest amount returned as cash. Net own-credit income and settlement stay null.

Source: [historical own-credit reconstruction](../../../data/eth/carry_attribution_recycling.json), [event-level CSV](../../../data/eth/carry_attribution_recycling_events.csv).

## Lending income, fees and staking stay separate

Every captured RLUSD and PYUSD deposit matches the corresponding non-adapter, non-self underlying-token receipts. Historical adapter returns and self transfers are separate categories. There is no unexplained external receipt into either destination during the common window. One separate 1-RLUSD receipt predates both the window and the tracked RLUSD position.

This narrows the income-source uncertainty, but it does not isolate pure gross lending interest. Morpho V2 book recognition can differ from underlying interest because of rate caps, fees and other asset changes. Current recognized destination claim growth is the measured quantity.

Two actual Ethereum fee payments during the common window transfer **71.18634344326532 weETH** from Liquid custody to `0xf6bd950c66869a32170bf26a38c8b7c6d6eca863`. Both fee events match successful transaction receipts and token transfers. Their earning periods and allocation to carry are unknown. They are not deducted again from the already reported Ethereum share return. The Ethereum management fee's calendar-time-weighted setting was 38.27520819196842 basis points over this period; this is not the fee actually charged to carry capital.

Over the same exact blocks, the observed whole Ethereum Liquid share return is **0.47502005%**, compared with **0.34293472%** for stETH's issuer conversion and **0.36123033%** for weETH's conversion. This is a whole-share comparison in ETH. Its excess is not assigned causally to carry, rewards, leverage or a particular destination.

The stcUSD claim separately grew by **247,384.00 cUSD** in the common window, after deposits and withdrawals. The share/cash-flow ledger closes, but gross economic sources do not. PRIME's underlying is verified as **wYLDS with 6 decimals**. Its custody-share acquisition basis and shares moved into collateral are not fully reconstructed; 26,191,000 deposited wYLDS and the custody claim must not be subtracted to invent income.

Source: [receipt-source review, fees and matched benchmarks](../../../data/eth/carry_attribution_organic.json).

## What remains open across the Top 5

| Product | Attribution achieved | Remaining income boundary |
|---|---|---|
| Concrete Delta weETH | Native share history separates issuer conversion from a flat weETH book | Private payouts and realized strategy income are unverified |
| ether.fi Liquid ETH | Selected destination claims, six account/market debt ledgers, paid rewards, ordered funding and own-credit overlap | Complete portfolio financing, campaign periods, former destinations, net own-credit income and carry fee allocation |
| Rocksolid rETH | Nested claim and active route evidence | Realized strategy cash-flow and income-source attribution |
| Liquity ETH Carry | Active borrower/destination route evidence | Historical income and funding attribution across the route |
| Royco ETH | Funding/controller route evidence | Realized destination payouts and complete strategy income |

Complete organic carry-income attribution remains open for all five products. That does not mean the measured returns are zero. It means their economic components have not all been independently assigned.

The 12,452,629.59 USD residual retained in `whole_product_boundary` belongs to the **original partial T balance-sheet reconstruction**. It is an asset-reconciliation gap, not unexplained historical profit or an established deficit. The site's newer backing and exit closure is a separate exhibit and may cover additional assets. This dataset does not overwrite either reconstruction.

## Rebuild and verification

The build is offline once the captured inputs exist:

```sh
python3 tools/eth/carry_attribution_build.py
python3 tools/eth/carry_attribution_recycling.py
python3 tools/eth/carry_attribution_organic.py
python3 tools/eth/carry_attribution_tranches.py
python3 tools/eth/carry_attribution_close.py
python3 tools/eth/carry_attribution_verify.py
```

The independent verifier recomputes native endpoint residuals without importing the accounting helpers. It checks fixed T, opening balances, debt shares, contract-bound models, exact reward transfers, cash coverage and ordering, retained claims, fees, source hashes and scope boundaries. Final result: **162 checks passed, 0 failed**. It verifies **85 preserved public capture hashes**; one failed capture attempt remains recorded, with successful individual requests supplying the missing code observations. Builder checks also pass: 38 leg-ledger checks, 24 own-credit state checks, 10,784 deposit-receipt checks and 13 tranche/fee checks.

Raw captures and the request manifest live in `raw/eth/research-closure-2026-10-04/income`. Mutable derived source inputs are preserved there as content-addressed copies. The main final dataset exposes the immutable source paths and hashes, so later editorial rebuilds cannot silently change its accounting inputs.

Source: [independent verification report](../../../data/eth/carry_attribution_verification.json).
