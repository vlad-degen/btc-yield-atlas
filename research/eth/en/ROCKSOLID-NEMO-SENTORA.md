# Rocksolid rETH, NEMO ETH Prime, Sentora ETH: gap closure

Snapshot T: 2 October 2026 23:59:59 UTC. Ethereum block 26,108,081; Monad 110,031,481; Base 52,098,126; Avalanche 96,636,400. 30-day window starts at Ethereum block 25,893,051 (2 Sep 2026 23:59:59 UTC). Valuation uses ETH = $2,667.95 (the Rocksolid book USD/ETH from `data/eth/backing_exit_closure.json`) and fixed-block rates: rETH 1.172960, wstETH 1.245402 stETH, weETH 1.104943. All numbers are in [gap_rocksolid_upshift.json](../../../data/eth/gap_rocksolid_upshift.json). Raw responses are in `raw/eth/gap-2026-10-07/rocksolid-upshift/`.

## Summary

- **Rocksolid's backing is fully accounted for.** The missing $19.85M sits in four places: Monad loops, Ethereum Morpho positions, and a second strategy wallet (`0x80c9…e18c`) that holds a rETH-collateral USDC loan. Reconstructed backing is 9,731.40 ETH against a book of 9,727.77 ETH, a residual of −0.04%.
- **Dollar carry is a minority of Rocksolid.** One Morpho rETH/USDC loan of **$2,727,060** (4.61% APR at T) is 10.5% of book. It funds $2.73M of dollar vaults. About 64% of the book is ETH-denominated loops, ETH lending and LP. The rest is the rETH collateral behind the loan (28%) and the nested Liquity ETH Carry claim (7.5%).
- **The Closing state was reversed.** On 7 Oct the owner upgraded the implementation to add `cancelClosing()`, reopened the vault and resumed deposits. No public reason was found.
- **The NEMO and Sentora debts belong to their vaults.** In both, the borrowing account is funded by the vault and controlled by it, and the NAV reconciles only if the loan is inside the book.
- **Sentora has a second loan the repo missed:** $907,092 of Aave USDC at 13.93%. Sentora's total dollar debt is $1,163,317, not $256k.
- **Rocksolid's loan was not counted in the attributed total either.** The wallet was listed as "Unknown owner" in `data/eth/research_borrowers.json`.
- **Revised attributed total: $261,325,366**, up from $251,823,181. The four additions are listed in the attribution section below. Upshift additions alone give $258,598,306.

## A. Rocksolid rETH (`0x936facdf10c8c36294e7b9d28345255539d81bc7`)

### Where the backing sits at T

The vault's `safe()` is `0x9ca1d6e7…8f4d`, a Fordefi MPC EOA (`reth-mpc.vaults.rocksolidnetwork.eth`) with no contract code. Being an EOA, it uses the same address on every EVM chain. A second EOA, `0x80c9dc96…e18c`, was funded only from the safe: 2,319.64 rETH net, starting with tx `0x43294576…` (2,092 rETH, 27 Mar 2026). It carries the same spam-token airdrop profile as the safe.

| Line | Chain | Position at T | ETH | USD |
|---|---|---|---|---|
| Previously mapped | Ethereum | loose rETH/weETH, Liquity ETH Carry, Spark net, Balancer, YieldBasis, native | 2,286.9 | 6.101M |
| Morpho rETH/WETH (`0x251b7c…`) | Ethereum | 851.11 rETH collateral − 326.73 WETH debt | 671.6 | 1.792M |
| Morpho savETH/WETH (`0xd98cd8…`) | Ethereum | 563.57 WETH supplied to Avant savETH borrowers | 563.6 | 1.504M |
| Morpho wstETH/WETH (`0x8bdb7d…`) | Monad | 2,642.57 wstETH − 2,717.25 WETH | 573.8 | 1.531M |
| Euler sub-account `…8f4c` (ewstETH-2 / eWETH) | Monad | 1,967.48 wstETH − 2,152.87 WETH | 297.4 | 0.794M |
| Steakhouse Prime ETH (steakETH) | Monad | 2,554.52 shares × 1.00908 | 2,577.7 | 6.877M |
| Loose WETH | Monad | 1.20 WETH (551 MON not valued) | 1.2 | 0.003M |
| Wallet2: Morpho rETH/USDC (`0x0a1546…`) | Ethereum | 2,330.51 rETH (2,733.6 ETH) − $2,727,060 USDC | 1,711.4 | 4.566M |
| Wallet2: Gami USDC (`0x776f95…`) | Base | 1,953,554 shares = 76.9% of that vault | 756.6 | 2.019M |
| Wallet2: hyperUSDCa (Hyperithm Morpho) | Monad | 680,050 shares | 265.1 | 0.707M |
| Wallet2: loose | Ethereum | 20.98 rETH, 3,532 USDC | 26.0 | 0.069M |
| **Total** | | | **9,731.4** | **25.963M** |

Sources: MPC Ethereum Morpho (`raw/eth/gap-2026-10-07/rocksolid-upshift/rocksolid_mpc_morpho_eth_positions_T-0d132822df1853b3.json`), Monad positions (`raw/eth/gap-2026-10-07/rocksolid-upshift/rocksolid_mpc_monad_positions_T-b528ba927aec40e0.json`), Monad Euler sub-accounts (`raw/eth/gap-2026-10-07/rocksolid-upshift/rocksolid_mpc_monad_euler_subaccounts_T-e6b144e1dc6b20d9.json`), wallet2 Morpho (`raw/eth/gap-2026-10-07/rocksolid-upshift/wallet2_morpho_position_T-fffe73a01da0e7de.json`), wallet2 Gami (`raw/eth/gap-2026-10-07/rocksolid-upshift/wallet2_base_gami_usdc_T-bb8708777996a11a.json`), wallet2 hyperUSDCa (`raw/eth/gap-2026-10-07/rocksolid-upshift/wallet2_monad_hyperUSDCa_T-2ab0ccd9f72bb25a.json`), rates and residual claims (`raw/eth/gap-2026-10-07/rocksolid-upshift/rocksolid_rates_and_misc_T-493faba30ba50e2d.json`).

Searched and found nothing material at T:
- Tulipa ETH+: no balance and no pending redeem.
- ether.fi withdrawal NFT 76680: already burned.
- Lido unstETH and Makina redeem NFTs: none held.
- Katana: exited 7 Feb 2026.
- Base csETH: redeemed 6 Aug 2026, with 384.64 WETH sent back through Relay.
- Unichain, Linea and Ink: active nonces but no balances checked. With a −0.04% residual they are immaterial.

### Monad route

Rocksolid ran a cross-chain loop on Monad, largest in May and June 2026:
1. On Ethereum, mint wstETH (4,759 wstETH through the Lido referral staker).
2. Bridge the wstETH to Monad through Chainlink CCIP (pool `0xa586a732`, selector 8481857512324358265). 5,183 wstETH went out in total.
3. Post it as collateral on Morpho and Euler and borrow WETH.
4. Bridge the WETH back to Ethereum through the Wormhole NTT (`0xfea937f7` on Monad, 7,975.6 WETH in total).
5. Stake again.

Separately, 5,048.6 WETH was bridged to Monad through the NTT (`0x03db430d`, chain 48) and mostly placed in steakETH. Merkl paid 5.43M WMON in rewards, sold for 59.8 WETH plus $1.5k. Mainnet Merkl paid 14,417 RPL; that matches the Rocket Pool IMC incentive of 200 RPL per fortnight, and 3,151 RPL came in the last 30 days. Monthly flows are in the JSON (`monadBridgeFlowsByMonth`). Decoded example: tx `0x3e979c27…` (1,400.04 WETH, `TransferSent` toChain 48).

### Dollar carry

- **Funding path:** wallet2 borrowed $2.5M of Aave USDC against rETH on 27 Mar 2026. It refinanced into Morpho rETH/USDC on 14 Apr and added $0.5M on 25 Sep (tx `0x2b60f1ee…`).
- **Where the dollars went:**
  - $2.0M by CCTP to Base (domain 6, tx `0xa799cf78…`), into Gami USDC.
  - $0.5M plus $0.502M by CCTP to Monad (domain 15), into hyperUSDCa. $0.3M came back on 5 Jun.
  - Avalanche (domain 1) is used only to claim and sell Merkl/Spectra rewards.
- **Position at T:**
  - Debt: $2,727,060 at a 4.61% APR (IRM `borrowRateView` at T).
  - Dollar assets: $2,729,465.
  - Collateral: 2,330.51 rETH, worth 2,733.6 ETH or 28.1% of book.
- **Income:** the USDC that wallet2 received from yield and reward routes, mostly swapped into rETH, was $97,998 gross from 27 Mar to T. The last 30 days brought $13,379. Against roughly $8 to 9k of interest a month, the net dollar-carry contribution is about $4 to 5k per 30 days, or about 0.02% of book.
- **Share of the book:** the direct dollar loan is 10.5% of book. The nested Liquity ETH Carry claim adds $1.94M (7.5%); that claim is itself dollar carry. Everything else is ETH-denominated loops, ETH lending, or LP positions:

| Bucket | Share of book ETH |
|---|---|
| Monad ETH loops and steakETH | 35.5% |
| Ethereum Morpho rETH/WETH loop and savETH WETH lending | 12.7% |
| Spark loop, Balancer, YieldBasis, loose | ~16% |

Monthly USDC debt is in the history table below.

### Why Closing, and what followed

| UTC | Block | Event | Tx |
|---|---|---|---|
| 2026-09-29 02:39:23 | 26,080,189 | Owner `0x3d4366ce…` calls `initiateClosing()` → state 1 | `0xb3ed2719618ec664e52d904c4f65eb9dcbbddd7ff1ae5c5599148bbadf23b70a` |
| 2026-09-29 to 10-05 |, | Existing claimable `redeem` calls keep paying; a new `claimSharesAndRequestRedeem` reverts (`0xee57ac6b…`) |, |
| 2026-10-07 00:02:47 | 26,136,796 | ProxyAdmin `0x5c6c0e4f…` `upgradeAndCall` → implementation `0x8a051dd8…`, replacing `0xe50554ec…` | `0x137aade1a7d7c45cb5f81bc166a749f644fd5c2e0304bab9fc70d69fe9fc53f0` |
| 2026-10-07 | 26,136,838 | Owner calls `cancelClosing()` → state 0 (Open) | `0xb87bfc604a9d05824f2158e4160fcff2ee40b2b583df8b743199a3cf6ea946e1` |
| 2026-10-07 | 26,136,887 to 26,136,899 | `settleDeposit` (totalAssets 8,296.086 rETH), then a new `syncDeposit` | `0x620af0e3…`, `0xe516835b…` |

The old implementation had no `cancelClosing()`, so the upgrade was needed to undo the closing. Rocksolid's blog and RSS feed (last post 1 May 2026), its docs, its app page and the Rocket Pool forum give no stated reason, and X was not reachable. **Verdict: this was a temporary closure and the vault reopened 8 days later, not a wind-down. The reason is not public. Treat the "Closed" tab entry as reversed after T.** Sources: vault logs (`raw/eth/gap-2026-10-07/rocksolid-upshift/rocksolid_vault_logs_latest-7ac4a49a3c000881.json`), upgrade tx (`raw/eth/gap-2026-10-07/rocksolid-upshift/tx_upgrade_20261007-ad3fc65e1116f6da.json`), new implementation (`raw/eth/gap-2026-10-07/rocksolid-upshift/new_impl_contract-2eba22c4a7945932.json`).

### Monthly book (Lagoon `totalAssets`/`totalSupply` and rETH rate at the repo's month-end blocks)

| Month-end | Block | totalAssets rETH | Supply | PPS (rETH) | Book ETH | USDC debt (wallet2) |
|---|---|---|---|---|---|---|
| 2025-09 | 23,479,243 | 1,609.52 | 1,592.61 | 1.01062 | 1,846.1 | 0 |
| 2025-10 | 23,700,766 | 5,321.24 | 5,255.77 | 1.01246 | 6,116.4 | 0 |
| 2025-11 | 23,914,920 | 5,751.77 | 5,676.10 | 1.01333 | 6,624.2 | 0 |
| 2025-12 | 24,136,052 | 6,631.64 | 6,536.72 | 1.01452 | 7,652.4 | 0 |
| 2026-01 | 24,358,292 | 8,244.67 | 8,118.06 | 1.01560 | 9,534.9 | 0 |
| 2026-02 | 24,558,867 | 8,334.98 | 8,204.18 | 1.01594 | 9,655.7 | 0 |
| 2026-03 | 24,781,026 | 8,173.38 | 8,039.12 | 1.01670 | 9,485.1 | $2,501,096 (Aave) |
| 2026-04 | 24,996,367 | 8,311.92 | 8,170.98 | 1.01725 | 9,662.5 | $2,507,519 |
| 2026-05 | 25,218,797 | 8,362.76 | 8,218.22 | 1.01759 | 9,738.3 | $2,507,796 |
| 2026-06 | 25,433,938 | 8,059.14 | 7,910.69 | 1.01877 | 9,400.1 | $2,207,032 |
| 2026-07 | 25,656,292 | 8,181.19 | 8,020.62 | 1.02002 | 9,560.3 | $2,215,018 |
| 2026-08 | 25,878,704 | 8,164.35 | 7,998.55 | 1.02073 | 9,558.3 | $2,217,643 |
| 2026-09 | 26,093,737 | 8,293.35 | 8,121.35 | 1.02118 | 9,726.6 | $2,726,021 |
| T | 26,108,081 | 8,293.35 | 8,121.35 | 1.02118 | 9,727.8 | $2,727,060 |

30-day ETH return: **+0.2192%**, against stETH at +0.1849%. Of that, share price in rETH terms added only **+0.0417%**; rETH staking growth supplied the rest. After fees (1% management, 10% performance), the strategy layer, dollar carry included, added about 0.5% a year to rETH.

**Verdict A.** Rocksolid was mostly an ETH-denominated incentive and loop book:
- Monad CCIP/NTT wstETH-WETH loops and steakETH deposits, farming Monad and Merkl rewards.
- Morpho and Spark rETH/WETH loops, plus WETH lending to Avant savETH loopers.

Dollar carry was one $2.73M USDC loan (10.5% of book) placed in Gami USDC on Base and Hyperithm USDC on Monad, plus a 7.5% nested Liquity ETH Carry claim. Net dollar-carry income was small: about $4 to 5k per 30 days after interest.

## B. NEMO ETH Prime and Sentora ETH (Upshift TokenizedVault)

In both vaults, `getTotalAssets` = in-vault assets + `externalAssets`. The owner or operator reports `externalAssets` through `updateTotalAssets`, which can change by at most `maxChangePercent` = 20 per day. `depositToSubaccount` moves vault assets to a whitelisted sub-account (type 1) or wallet (type 2) and increases `externalAssets`.

### State at T (block 26,108,081)

| | NEMO ETH Prime | Sentora ETH |
|---|---|---|
| Vault / LP token | `0xa422c301…c91b` / `0xd211f28f…` | `0xd0271e19…1e9d` / `0x18039d7d…` (sentETH) |
| Asset | WETH | WETH |
| Share supply | 2,891.219 | 665.343 (19.930 held by vault for pending redeems) |
| PPS (WETH) | 1.050653 | 1.017026 |
| Total assets | 3,037.67 WETH ($8.104M) | 676.67 WETH ($1.805M) |
| externalAssets / last update | 2,965.74 WETH, 2026-10-02 16:16 UTC | 671.32 WETH, 2026-09-22 16:21 UTC (10.3 days stale) |
| Holders (positive balances) | 55 | 26 (25 excluding the vault) |
| Top holders | `0x5d97c2a6…` 73.14%, `0x6de1d632…` 10.51%, `0x95470d01…` 6.73% (all EOAs) | `0xb7b9fad3…` 71.66%, `0xb12a9d1b…` 19.63%, `0xec105f29…` 3.71% (all EOAs) |
| Fees | 1% management; 0 performance; 0 withdrawal; 2% instant redemption. Collectors: `0x3e11d59f…` 82.5%, `0xf87d27d3…` 17.5% | 0 / 0 / 0; 0.2% instant redemption |
| Redemption lag | 30 days | 3 days |
| Owner | Safe `0x9328b0bb…` (3-of-4) | Sub-account `0x9aa69b81…`; its `owner()` is the vault |
| Proxy admin | `0xd3a67c75…`, owned by Safe `0xfc76bbc4…` (3-of-4, same signers) | `0xa5d3e7b5…`, owned by Safe `0xbfbc2596…` (1-of-2; both signers are also NEMO Safe signers `0x4ea49872…`, `0x5524ebe3…`) |
| Operator | `0x8baf70cb…` (EOA) | `0xe0b7deab…` (EOA) |
| Timelock | 1 day, only on `acceptOwnership`, management-fee change, max-change change and lag change. Upgrades, sub-account whitelisting and fund moves have no delay | Same |

Sources: NEMO state (`raw/eth/gap-2026-10-07/rocksolid-upshift/upshift_nemo_vault_state_26108081-d6aad922b37fdbfe.json`), Sentora state (`raw/eth/gap-2026-10-07/rocksolid-upshift/upshift_sentora_vault_state_26108081-22267ba4ecbdea80.json`), holder logs NEMO (`raw/eth/gap-2026-10-07/rocksolid-upshift/nemo_lp_transfers-c2f9e3923afdc01d.json`), holder logs Sentora (`raw/eth/gap-2026-10-07/rocksolid-upshift/sentora_lp_transfers-da6209b371905d85.json`), roles (`raw/eth/gap-2026-10-07/rocksolid-upshift/upshift_admin_roles_T-27d80ef81ab3e562.json`), proxy admins (`raw/eth/gap-2026-10-07/rocksolid-upshift/upshift_proxyadmin_owners_T-e9ce53678a0f6c47.json`).

### NEMO: where the borrowed dollars go

`0x90882e7c…5e90` is NEMO's type-2 whitelisted wallet (`whitelistedSubAccounts` = 2). It received 2,820.65 WETH net from the vault and staked it into 2,381.09 wstETH, which is posted on Morpho wstETH/USDC (`0x7e585a…`, 86% LLTV). It borrowed **$5,611,790** of USDC and deposited it into **NEMO USDC Yield**, a sibling Upshift vault (`0x955256b3…`, LP `0xee012ec1…`). The wallet holds 5,265,419 nUSDC (43.4% of supply), worth **$5,611,170** at PPS 1.065665.

nUSDC terms: $12.92M total assets, of which $12.40M is external; 2% management, 20% performance, 30-day lag. It pays USDC to EOA `0xfb1898bb…`, which has burned $19.44M through CCTP and has 5,371 Arbitrum, 33,390 Base and 9,846 HyperEVM transactions. That EOA also deposits to Derive (Lyra). In short, the borrowed dollars fund an active trading book.

NAV check at T:

| Component | WETH |
|---|---|
| wstETH collateral | 2,965.42 |
| Vault WETH | 71.93 |
| nUSDC − debt | −0.23 |
| **Sum** | **3,037.12** |
| Reported total assets | 3,037.67 |

The reported NAV equals the collateral, which means the debt is netted inside the book.

30-day return (2 Sep → T): **+1.0348%** in ETH, against stETH at +0.1849%. Most of the excess comes from nUSDC, whose PPS rose 1.755% over the same window.

### Sentora: where the borrowed dollars go

Chain of custody: vault → sub-account `0x9aa69b81` (664.29 WETH, converted to weETH) → supervised loan and position managers. Every manager reports `owner()` = `0x9aa69b81`.

| Leg | Manager | Venue | Collateral | Debt at T | APR at T | Destination |
|---|---|---|---|---|---|---|
| RLUSD | `0xfb9776de…` (contract) | Morpho weETH/RLUSD `0xea4bfb18…` | 121.016 weETH | $256,225 | 4.21% | 252,892 senRLUSDv2 (Morpho VaultV2 `0x6dc58a0f…`) = $256,236 |
| USDC (**new**) | `0x38752981…` | Aave v3 Core | $1,389,513 (~471.6 weETH) | **$907,092** | 13.93% | 905,873 USDC swapped through 1inch into 798,110 PST (Huma PayFi Strategy Token), held by `0x58dc5ce5…`. Cost basis $1.1348 per PST; no on-chain price |
| PYUSD | `0x9e1e5829…` | Morpho |, | 0 (closed) |, |, |

NAV check:

| Component | ETH |
|---|---|
| Morpho weETH | 133.72 |
| Aave weETH | 520.82 |
| Sub-account weETH | 16.47 |
| Vault WETH | 5.36 |
| Dollar legs | ≈ 0 |
| **Sum** | **676.36** |
| Reported total assets | 676.67 |

Dollar debt was $201k at end-July, $325k at end-August, $1.205M at end-September and $1.163M at T. Debt-weighted APR at T is 11.8%.

30-day return: **+0.1654%** in ETH, against stETH at +0.1849%. PPS has not moved since the NAV update on 22 Sep.

Sources: Morpho positions (`raw/eth/gap-2026-10-07/rocksolid-upshift/upshift_morpho_positions_T-05a81602093f254f.json`), Aave accounts (`raw/eth/gap-2026-10-07/rocksolid-upshift/upshift_aave_spark_accounts_T-88b6252dafdc90f3.json`), Sentora dollar legs (`raw/eth/gap-2026-10-07/rocksolid-upshift/sentora_dollar_sleeves_T-f55ff17f7a969cec.json`), manager owners (`raw/eth/gap-2026-10-07/rocksolid-upshift/sentora_loanmgr_owners_T-0e7847a308f2570b.json`), NEMO wallet balances (`raw/eth/gap-2026-10-07/rocksolid-upshift/nemo_wallet_balances_T-69b79829d5efb029.json`), nUSDC state (`raw/eth/gap-2026-10-07/rocksolid-upshift/nemo_usdc_vault_state_T-9c9e47f9d597c1cb.json`), Aave rate (`raw/eth/gap-2026-10-07/rocksolid-upshift/borrow_rates_T_a-f86db766ecd1bee6.json`).

### Monthly history (vault getters at month-end blocks)

| Month-end | Block | NEMO supply | NEMO PPS | NEMO assets WETH | NEMO USDC debt | Sentora supply | Sentora PPS | Sentora assets WETH | Sentora $ debt |
|---|---|---|---|---|---|---|---|---|---|
| 2026-03 | 24,781,026 | 1,761.79 | 1.00223 | 1,765.72 | $0 | 0.01 | 1.00000 | 0.01 | $0 |
| 2026-04 | 24,996,367 | 2,218.58 | 1.00114 | 2,221.10 | $0 | 17.10 | 1.00179 | 17.13 | $0 |
| 2026-05 | 25,218,797 | 2,219.64 | 1.00531 | 2,231.44 | $0 | 520.98 | 1.00620 | 524.21 | $0 |
| 2026-06 | 25,433,938 | 2,416.07 | 1.01082 | 2,442.21 | $0 | 521.15 | 1.00959 | 526.14 | $0 |
| 2026-07 | 25,656,292 | 2,721.13 | 1.02378 | 2,785.84 | $2,613,670 | 653.57 | 1.01206 | 661.46 | $201,437 |
| 2026-08 | 25,878,704 | 2,839.71 | 1.03957 | 2,952.07 | $5,118,847 | 665.25 | 1.01514 | 675.32 | $325,406 |
| 2 Sep (30d start) | 25,893,051 | 2,845.12 | 1.03989 | 2,958.62 | $4,881,451 | 665.21 | 1.01535 | 675.41 | $325,455 |
| 2026-09 | 26,093,737 | 2,880.10 | 1.04951 | 3,022.69 | $5,731,955 | 665.34 | 1.01703 | 676.67 | $1,204,894 |
| T | 26,108,081 | 2,891.22 | 1.05065 | 3,037.67 | $5,611,790 | 665.34 | 1.01703 | 676.67 | $1,163,317 |

NEMO's first share transfer is at block 24,629,280 and Sentora's at 24,241,726.

### Attribution decision

**Both vaults' debt should be added to the attributed total.** The test applied to each:
- The borrowing account is funded by `depositToSubaccount` from the vault.
- That account is whitelisted by the vault (NEMO) or owned by the vault's sub-account (Sentora).
- The vault's reported NAV reconciles to collateral net of debt, with the dollar assets inside the book.

| Item | USD |
|---|---|
| Repo attributed total | 251,823,181 |
| + NEMO Morpho USDC | 5,611,801 |
| + Sentora Morpho RLUSD | 256,232 |
| + Sentora Aave USDC (new) | 907,092 |
| + Rocksolid wallet2 Morpho USDC (new; previously "Unknown owner") | 2,727,060 |
| **Revised total** | **261,325,366** |

Caveats:
- Sentora's NAV was 10 days stale at T.
- The PST leg has no on-chain price.
- NEMO's dollar leg sits in a sibling vault from the same operator group, so it is a nested claim, not a cash balance.
