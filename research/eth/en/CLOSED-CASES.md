# Closed and stressed ETH cases

Snapshot T: 2 October 2026 23:59:59 UTC, Ethereum block 26,108,081. Month-end reads use the study's 24 verified month-end blocks. Every row is in [gap_closed_cases.csv](../../../data/eth/gap_closed_cases.csv). Raw reads and source notes are in `raw/eth/gap-2026-10-07/cases/`.

## Findings

- **No ETH depositor in a covered product lost principal from the Kelp exploit, but three products froze or marked down.** Lido Earn froze for 27 days and the DAO absorbed 144.77 ETH. CIAN rsETH fell 2.6% in a month, then recovered. hgETH (Kelp Gain) froze for seven weeks and then wrote down 500 rsETH of its loan book on 5 June.
- **The cost of the exploit sat with lenders' treasuries and their allies, not with depositors.** About 107k of 112k unbacked rsETH came back through Aave and Compound liquidations. DeFi United, a group of DAOs and firms, covered the rest. Aave Umbrella stakers were not slashed because the module was paused.
- **Aave still carries the accounting hole at T: 52,964 WETH on Ethereum and 29,835 WETH on Arbitrum** (`getReserveDeficit`). Recovery funds exist, but nothing public reconciles them to this deficit.
- **The real damage was the exit, not the loss.** Lido Earn ETH went from 111k ETH to 58k ETH after reopening. Aave Ethereum WETH ended April at 99.2% utilization. ETH loopers paid an April average of 3.53% against 2.49% from stETH.
- **The two small IPOR carry vaults shut down quietly, with no exploit.** Reservoir ETH Yield earned +0.29% over 13 months, against +2.72% for stETH over the same blocks. TAU lost 0.33% in wstETH terms. Both lost 96% to 99% of their peak books within three months.
- **Restaking-token outflows were large and mostly ended programs, not losses.** Eigenpie, Puffer, Mellow LRT and Renzo lost 88% to 99% of their ETH. Most of it left when points and airdrop programs ended, before slashing went live, or after the Kelp exploit.

## 1. Lido Earn ETH, April 2026

| UTC | Event |
|---|---|
| 18 Apr 17:35 | rsETH bridge exploit starts. Lido detects it at 18:53. |
| 18 Apr 20:29 / 20:33 | UI deposits are switched off, then the SyncDepositQueues are paused. |
| 18 Apr | Exposure: about 113.2k rsETH collateral against 111.1k WETH debt in the underlying loop. Net exposure through strETH is about 9k ETH (about $21M). |
| Late Apr | The projected loss is 400 to 600 ETH. |
| 15 May 17:15 | Deposits and withdrawals resume after 27 days. The DAO burns 143.9766 earnETH ([tx](https://etherscan.io/tx/0xdfca0390d39299ec88e6be26f5254d873b9a1098f71591c42f357412d60e71c7)), worth 144.77 ETH. |

- **Loss:** 143.98 ETH, about 0.13% of the 111k ETH book.
  - It came from WETH borrow cost during the freeze and from slow unwinds, not from rsETH principal.
  - It was below the reserve's 1% trigger, so the DAO approved a one-off cover.
- **Depositors:** 0% loss. The modelled worst case was about 12%. Their cost was that they could not exit for 27 days.
- **First-loss reserve:**
  - Approved 9 March 2026: $3M wstETH for EarnETH, plus $2M USDC for EarnUSD.
  - About $0.33M of it was used. The remaining balance is not published.
- **Separate DAO cost:** 2,500 stETH (about $5.7M) to DeFi United.
- **After reopening:** TVL went from 111,000 ETH to 58,000 ETH.
- **Lido's framework changes** include:
  - Caps on exposure to external protocols.
  - A review of looping strategies before deployment.
  - Exit-under-stress scoring, kept separate from yield.

Sources: [Lido incident review](https://research.lido.fi/t/kelp-incident-review-earneth-exposure-response-and-risk-framework-changes/11579), [May tokenholder update](https://blog.lido.fi/lido-poolside-recap-tokenholder-update-may-2026/), [first-loss proposal](https://research.lido.fi/t/lido-earn-competing-on-trust-5m-treasury-allocation/11228).

**Lesson:** First-loss capital covered the loss easily. The freeze still cost the product half its deposits.

## 2. Kelp rsETH bridge exploit, 18 April 2026: who lost what

116,500 rsETH (about $292M) was released from the LayerZero adapter. The attacker posted 89,567 rsETH on Aave (53,400 on Ethereum, 36,167 on Arbitrum) and borrowed WETH against it.

| Product / protocol | What happened | Amount | Who bore it | Status at T |
|---|---|---|---|---|
| Aave v3 (Ethereum, Arbitrum) | Attacker WETH debt against unbacked rsETH. The collateral was liquidated to the Recovery Guardian. | Deficits at T: 52,964 WETH (Ethereum) and 29,835 WETH (Arbitrum) | DeFi United and Aave DAO (25k ETH pledged) | Accounting deficit still open. Funding not reconciled. |
| Aave Umbrella WETH | 23,508 WETH stake at risk | 0 slashed | n/a. The module was paused on 20 Apr to block slashing. | Paused |
| Aave WETH suppliers and loopers | Utilization reached 99.2% (30 Apr). The April average borrow APR was 3.53%. | Rate cost, no principal loss | Borrowers. Suppliers could not withdraw. | WETH LTVs restored by 18 May |
| Compound v3 | Attacker debt | 17,426 rsETH recovered. 1,900 to 3,000 ETH pledged. | Compound DAO | Recovered |
| Lido Earn ETH | 27-day freeze plus funding loss | 144.77 ETH | Lido DAO first-loss shares | Closed 15 May |
| CIAN rsETH | Share price fell from 0.95449 to 0.92949 rsETH (17 Apr to 16 May) | -2.62% | Holders who exited in the window | Recovered to 0.95882 at T |
| hgETH (Kelp Gain) | Supply and price frozen from 19 Apr to 5 Jun. On 5 Jun a Safe called `liquidate()` on loan `0xd08e3ec3…` and totalAssets fell by 500 rsETH. | -4.09% from 31 May to 30 Jun (about 626 rsETH) | hgETH holders | 0.99874 rsETH at T. Link to the exploit not established. |
| rsETH holders | Backing restored to 100.01% on 25 May | 0 haircut | Kelp and DeFi United | Closed |
| Euler, Morpho, Spark, Fluid | Froze rsETH | No depositor loss found. Euler attacker debt is reported at about $0.84M, unverified. | n/a | n/a |

DeFi United pledges:

| Contributor | Pledge |
|---|---|
| Consensys/Lubin | 30k ETH |
| Mantle | 30k ETH (loan) |
| Arbitrum DAO | 30k ETH (from 30,766 ETH it froze) |
| Aave DAO | 25k ETH |
| Kulechov | 5k ETH |
| ether.fi | 5k ETH |
| Lido | 2.5k stETH |

Sources: [Aave incident report](https://governance.aave.com/t/rseth-incident-report-april-20-2026/24580), [Umbrella pause](https://governance.aave.com/t/direct-to-aip-pause-stkwaweth-umbrella-staked-token-on-ethereum-v3/24595), [Aave Labs May update](https://governance.aave.com/t/al-development-update-may-2026/25013), [CoinDesk 18 May](https://www.coindesk.com/markets/2026/05/18/aave-restores-weth-collateral-limits-as-rseth-crisis-enters-recovery-phase), [backing restored](https://ambcrypto.com/kelpdao-says-rseth-recovery-completed-as-backing-returns-above-100/), [DeFi United list](https://news.bitcoin.com/compound-dao-defi-united-rseth-recovery-proposal/). The CIAN and hgETH figures are our own fixed-block reads (`raw/eth/gap-2026-10-07/cases/vaults/kelp_exposed_vaults.json`, `hg_block_25253082*.json`).

**Lesson:** A bridge bug at one restaking-token issuer froze the main ETH borrow market. The loss was socialised by the protocol's allies, which is a political backstop, not a contractual one.

## 3. Reservoir ETH Yield (IPOR Fusion, `0xf6cd…f76e`)

| Month end | Book (WETH) | Share price |
|---|---|---|
| Sep 2025 | 2,428.8 | 1.01138 |
| Oct 2025 (peak) | 4,136.9 | 1.01914 |
| Nov 2025 | 1,620.2 | 1.01008 |
| Jan 2026 | 153.0 | 0.99965 |
| Feb 2026 (low) | 310.3 | 0.98706 |
| Jun 2026 | 162.5 | 1.00190 |
| T | 23.6 (about $63k) | 1.00288 |

- **The design:** the vault borrows USDC on Aave against WETH and holds Reservoir dollar savings (srUSD). It charges a 1% management fee and a 10% performance fee.
- **Peak to low:** the share price fell 3.15% from Oct 2025 to Feb 2026.
- **No liquidations:** we found no Aave or Morpho liquidation of the vault.
- **No public cause:** we found no Reservoir depeg or incident. Reservoir's own TVL fell from $289M to $18M in November 2025.
- **What depositors got:**
  - Leavers in November and December left near 1.010 to 1.012.
  - Late entrants who bought below 1.0 in Feb and Mar 2026 are about +1.6% at T.
  - Holders since launch have +0.29% in 13 months, against +2.72% for stETH over the same blocks.

**Lesson:** An ETH vault that funds a dollar savings product can lose ETH with no exploit at all. The fee and the funding cost alone exceeded what stETH paid.

## 4. TAU InfiniFi ETH Carry (IPOR Fusion, `0xc50b…c64b`)

| Month end | Book (wstETH) | Share price |
|---|---|---|
| Dec 2025 | 33.5 | 1.00091 |
| Jan 2026 (peak, about $854k) | 285.2 | 1.00104 |
| Mar 2026 | 36.3 | 1.00010 |
| Apr 2026 | 1.9 | 0.99979 |
| Jun 2026 | 142.0 | 0.99897 |
| T | 66.0 | 0.99673 |

- **The design:** the vault borrows USDC on Morpho against wstETH into infiniFi siUSD. It charges a 0.8% management fee and a 10% performance fee.
- **The unwind:** by T the dollar debt is 0.022 USDC, so what remains is a wstETH wallet paying a management fee. The share price has drifted at about 0.9% a year since June.
- **No public cause:** we found no infiniFi incident. infiniFi's TVL fell from $179M in January to $45M in October, and its points season ended without a token launch.
- **Depositors:** -0.33% in wstETH terms since launch, which means they underperformed plain wstETH.

**Lesson:** When the dollar leg stops paying, the product keeps charging fees on idle collateral. Watch the debt, not the label.

## 5. Rocksolid rETH: Closing on 29 Sep, reopened 7 Oct

- **29 Sep 02:39 UTC:** the owner called `initiateClosing()`.
- **During Closing:** redemptions already claimable kept paying, and new redeem requests reverted.
- **7 Oct:** the owner upgraded the implementation to add `cancelClosing()` and reopened the vault, with 8,296 rETH in assets.
- **Outcome:** no loss, and no public reason given.

Detail: [ROCKSOLID-NEMO-SENTORA.md](ROCKSOLID-NEMO-SENTORA.md).

**Lesson:** A vault's state can be changed by an owner upgrade within days. "Closed" on a dashboard is an owner decision that can be reversed.

## 6. Restaking-token outflows

These are ETH balances in the netted market map ([market_map_history_monthly.csv](../../../data/eth/netmap/market_map_history_monthly.csv)). Where the peak is shown as Oct 2024, that is the first month of the series.

| Product | Peak (ETH, month) | T (ETH) | Change | Main step | Stated or likely reason |
|---|---|---|---|---|---|
| Eigenpie | 434,227 (Oct 2024) | 1,683 | -99.6% | Jul 2025: 213k to 6k | No sunset notice found. Falls in the wave after EigenLayer slashing went live (17 Apr 2025). |
| Puffer | 289,102 (Oct 2024) | 8,956 | -96.9% | Oct to Dec 2024: 289k to 71k | Withdrawals opened and the PUFFER airdrop came on 14 Oct 2024. The EigenLayer season 2 stakedrop had ended. |
| Mellow LRT vaults | 230,577 (Oct 2024) | 5,643 | -97.6% | Dec 2025 to Jan 2026: 88k to 22k | LRT vaults deprecated. Lido stRATEGY moved to Lido Earn (Mar 2026). |
| Renzo | 421,989 (Nov 2024) | 40,897 | -90.3% | Apr to May 2026: 148k to 70k | Points era over. A second leg of outflows came after the Kelp exploit. |
| Swell restaking | 50,261 (Oct 2024) | 10,599 | -78.9% | Aug 2025 | Airdrop programs ended. No dated trigger found. |
| Mantle restaking (cmETH) | 195,579 (Mar 2025) | 16,046 | -91.8% | Aug 2025, May 2026 | No dated trigger found. |
| Kelp | 641,768 (Apr 2026) | 403,271 | -37.2% | May to Sep 2026 | Exploit |
| ether.fi | 2,627,213 (Jan 2026) | 1,689,026 | -35.7% | Mar to May 2026 | Exploit-period deleveraging of weETH loops |
| Symbiotic (direct) | 333,865 (Oct 2024) | 31,033 | -90.7% | 2025 | The netted row is noisy. USD TVL went from $2.13B (Jan 2025) to $478M. |

- **No loss caused these outflows.** Holders left when points and airdrop programs ended.
- **The rewards that replaced points are small.** See [RESTAKING-AND-LOOPS.md](RESTAKING-AND-LOOPS.md) for actual EigenLayer reward payments.

Sources: [Aave pufETH thread](https://governance.aave.com/t/temp-check-onboard-pufeth-to-aave-v3-core-instance/20770/10), [slashing go-live outflows](https://99bitcoins.com/news/eigenlayer-liquidity-restaking-protocols-lose-over-1-billion-in-tvl-ahead-of-key-update/), [Mellow LRT deprecated](https://docs.mellow.finance/resources/mellow-lrt-depreciated/vault), [Lido stRATEGY to Earn](https://help.lido.fi/en/articles/12761642-vault-overview-strategy). DefiLlama USD series are in `raw/eth/gap-2026-10-07/cases/defillama_*.json`.

**Lesson:** Restaking demand was rented with points. Once the points ended, 88% to 99% of the deposits left, without any loss event.

## Open items

- **Remaining first-loss reserve:** what Lido's reserve holds after the burn is not published.
- **Aave deficit:** the 82.8k WETH deficit at T is not reconciled to DeFi United funds.
- **hgETH loan:** who borrowed on loan `0xd08e3ec3…`, and whether it is linked to the exploit.
- **Reservoir and TAU:** no issuer statement says why either vault was unwound.
