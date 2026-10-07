# Top-5 ETH carry: how much of the yield is paid by rewards

Snapshot **T = 2 Oct 2026 23:59:59 UTC**, Ethereum block **26,108,081**. Windows end at T: **90 days** (from block 25,462,598, 4 Jul 2026) and **365 days** (from block 23,493,531, 2 Oct 2025). For products launched later, the long window is **since inception**. Pulled on 7 Oct 2026.

Data: [`rewards_split.csv`](../../../data/eth/top5/rewards_split.csv) (product, window, component, ETH, share of return, source; 90d, 365d or inception, and every month), [`incentive_cost.csv`](../../../data/eth/top5/incentive_cost.csv). Raw pulls and scripts: `raw/eth/gap-2026-10-07/rewards-split/` (`scripts/build.py` rebuilds both CSVs offline from the raw files).

## Findings

1. **Rewards are a minority of the yield in every product, far below Kraken's ~82%.**

   | Product | Window | Actual APY | APY without rewards | stETH APY | Rewards share of excess over stETH |
   |---|---|---:|---:|---:|---:|
   | ether.fi Liquid ETH | 90d | 3.32% | 2.94% | 2.25% | **35%** |
   | | 365d | 3.87% | 3.39% | 2.48% | **34%** |
   | Lido Earn ETH | 90d | 3.14% | 3.14% | 2.25% | **0%** |
   | | since 28 Feb 2026 | 3.14% | 2.63% | 2.39% | **67%** |
   | Avant savETH | 90d | 4.74% | 4.55% | 2.25% | **7%** (priced rewards only) |
   | | 365d | 5.47% | 5.42% | 2.48% | **2%** (priced rewards only) |
   | Liquity ETH Carry | 90d | 3.84% | 2.26% | 2.25% | **~99%** |
   | | since 31 Mar 2026 | 7.06% | 5.34% | 2.36% | **36%** |
   | YieldBasis WETH, unstaked LT | 90d | **−2.96%** | −2.96% | 2.25% | no excess |
   | | since 31 May 2026 | 2.10% | 2.10% | 2.30% | no excess |
   | YieldBasis WETH, staked in gauge | 90d | 1.69% | **−2.96%** | 2.25% | no excess |
   | | since 31 May 2026 | 6.13% | **−2.29%** | 2.30% | **>100%** |

   "Without rewards" removes every priced reward that reached the vault or the holder. AvantPoints and IPOR Fusion points have no realized price and are not in these numbers.

2. **Liquid: about a third of the excess is rewards, and the source changed during the year.**
   - **Oct 2025 to Jan 2026:** the vault received **3,410 KING (LRT²)** in 16 weekly drops from ether.fi's CumulativeMerkleDrop `0x6db24ee6`. That is **$2.36M**, or 0.38 pp of the 365d return. The vault redeemed KING into EIGEN, ETHFI, KERNEL, MNT, SWELL and WETH. The last drop was on **23 Jan 2026**.
   - **Since Aug 2026:** the vault has received Merkl **RLUSD and PYUSD** on its Sentora claims, $361k to date. At T the run-rate is **$2.73M/yr**, or **0.58% of Liquid's $474M TVL**. These are the issuer-funded campaigns described in TOP5-RISK-LIQUIDITY.
   - **90d split, annualized:**
     - staking 2.38 pp;
     - ETH loop spread +0.75 pp;
     - dollar leg organic **−0.63 pp**;
     - rewards +0.37 pp;
     - fees −0.52 pp;
     - residual +0.92 pp.
   - **The dollar sleeve loses money even with rewards.** Rewards cover about 60% of its organic loss.
   - **The residual is large (+1.0 pp over 365d).** It holds the unmeasured books: Uniswap and Fluid LPs, Pendle, Optimism and Monad books, PRIME yield, and the ETH-price effect on dollars that have no measured claim (46M at T).
3. **Lido Earn: the last 90 days are organic.** Over 90d the 3.14% splits into staking 2.23 pp, wstETH/WETH loops +0.80 pp and the USDT→earnUSD leg +0.26 pp. Fees and timing take −0.24 pp.
   - **Rewards were earlier and one-off.**
     - **Ethena paid 449k aEthUSDe** ($449k) to stRATEGY's USDe/sUSDe loop subvault `0x9938a09f` from Oct 2025 to Apr 2026, plus a 214,767 sENA drop.
     - **Resolv paid 228,713 wstUSR** ($258k at receipt) through Merkl to subvault `0xecf3bde9` from Dec 2025 to Feb 2026. USR depegged on 23 Mar 2026.
     - **The Lido DAO burned 143.98 of its earnETH shares** (144.77 ETH, $330k) on 15 May 2026 to cover the Kelp-incident loss.
   - **The May 2026 month shows the cover and the loss together.** The DAO cover added +0.20 pp, the residual was −0.30 pp and the outer layer −0.15 pp, which left a −0.71% APY without rewards for that month.
4. **Avant: the carry is organic on paper, but it is own-issuer.**
   - **365d split:** staking (LST plus WETH lending) 2.32 pp, dollar leg **+1.99 pp**, residual +1.11 pp.
   - **The dollar leg earns the savUSD rate against Aave/Spark borrow.** savUSD is Avant's own product.
   - **Priced rewards are small:** CRV $10.4k and Merkl $0.4k on the strategy wallet.
   - **AvantPoints are unpriced.** They ran from 13 Nov 2025 to 15 May 2026 on savETH, avETH, avETHx, Morpho collateral, Pendle and Curve.
   - **Only part of the book is measured.** The Ethereum wallet covers 40 to 90% of the avETH book, depending on the month. The other chains (Monad, Sei, Berachain) sit in the residual.
5. **Liquity ETH Carry: the dollar leg runs negative and rewards make up the gap.**
   - **Over 90d:** the trove pays 2.55 to 6.35% on ebUSD, while the measured Curve LP fees are about 0.4%. That gives dollar leg organic −2.03 pp/yr.
   - **BOLD from the Curve BOLD/USDC gauge** adds +1.54 pp/yr ($23k in 90d; run-rate $153k/yr, 0.95% of TVL).
   - **Without rewards, the 90d APY of 2.26% equals stETH.** IPOR Fusion points on depositors run to 30 Nov 2026 and are unpriced.
   - **The residual (+3.3 pp/yr) is unmeasured.** It is Uniswap V4 BOLD/USDC fees and keeper-reported market books.
   - **The since-inception figure is distorted** by a +2.15% month when the vault held about 280 ETH.
6. **YieldBasis: the LT does not beat stETH, and staked holders live on YB emissions.**
   - **Since 31 May:**
     - LP fees on the 2× position minus the 10% crvUSD rate give **+8.97 pp/yr**;
     - rebalancing and tracking losses (residual) take **−6.88 pp/yr**;
     - the admin fee was zero.
   - **Jul to Sep were negative every month.**
   - **Staked LT gives up fee income** (the gauge share fell from 0.99995 to 0.98514 LT). It earns **1.85M YB** ($152k realized) instead.
   - **The YB run-rate at T is $504k/yr**, which is **3.16% of staked TVL**. That emission is the whole of the staked holder's return.

## Decomposition, by window

Components are shares of the start capital in percentage points over the window (not annualized). They are:
- **a:** staking yield on ETH equity;
- **b:** LST growth minus WETH borrow cost on borrowed ETH;
- **c:** destination growth on measured claims minus dollar borrow cost;
- **d:** rewards that reach the share price;
- **e:** fees;
- **f:** residual.

| Product | Window | Return | a | b | c | d | e | f |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Liquid | 90d | 0.809 | 0.588 | 0.186 | −0.154 | 0.092 | −0.127 | 0.226 |
| Liquid | 365d | 3.870 | 2.503 | 0.285 | −0.114 | 0.477 | −0.286 | 1.005 |
| Lido Earn | 90d | 0.766 | 0.549 | 0.196 | 0.064 | 0.000 | −0.060 | 0.016 |
| Lido Earn | since 28 Feb | 1.848 | 1.409 | 0.300 | 0.187 | 0.297 | −0.170 | −0.175 |
| Avant savETH | 90d | 1.148 | 0.489 | 0.000 | 0.403 | 0.044 | n/a | 0.212 |
| Avant savETH | 365d | 5.473 | 2.321 | 0.000 | 1.988 | 0.056 | n/a | 1.108 |
| Liquity | 90d | 0.934 | 0.484 | 0.000 | −0.499 | 0.382 | −0.241 | 0.808 |
| Liquity | since 31 Mar | 3.516 | 1.003 | 0.000 | −0.595 | 0.844 | −0.679 | 2.943 |
| YieldBasis LT | 90d | −0.737 | 0 | 0 | 1.360 | 0 | 0 | −2.097 |
| YieldBasis LT | since 31 May | 0.710 | 0 | 0 | 3.048 | 0 | 0 | −2.338 |

Rewards inside d:

| Product | Window | Reward lines (pp of start capital) |
|---|---|---|
| Liquid | 365d | KING drops 0.379, Merkl RLUSD 0.051, Merkl PYUSD 0.044, Merkl ETHFI (Aave weETH lending) 0.004 |
| Liquid | 90d | Merkl RLUSD 0.049, Merkl PYUSD 0.042 |
| Lido Earn | since 28 Feb | DAO first-loss cover 0.188, Ethena aEthUSDe 0.093, sENA 0.012, aEthrsETH 0.004 |
| Avant | 365d | CRV 0.051, Merkl MORPHO/USDS/USDC/WFRAX 0.005 |
| Liquity | 90d | BOLD from Curve gauge 0.380, Merkl BOLD 0.002 |

Monthly rows for every product are in the CSV (`month YYYY-MM`). Liquid's rewards share of the monthly excess was 75% in Oct 2025, then fell to 0 from Feb to Jun 2026. It rose back to 57% in Aug and Sep 2026 once the RLUSD/PYUSD campaigns started.

## Incentive cost table (last 365 days to T)

| Product | Program | Payer | Receiver | Realized | $/yr | $ per $ TVL per yr | Run-rate at T | Run-rate per $ TVL | End |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| Liquid | KING (LRT²) drops | ether.fi (KING distributor `0x6db24ee6`) | vault | $2.36M | $2.36M | 0.65% | 0 | 0 | last drop 23 Jan 2026 |
| Liquid | Merkl RLUSD, Sentora RLUSD Main V2 | RLUSD issuer-side treasury via Sentora Safe `0xCc6d` | vault | $194k | $194k | 0.05% | $1.40M | 0.30% | weekly, renewed (current to 8 Oct) |
| Liquid | Merkl PYUSD, Sentora PRIME and Paypal USD Main V2 | PYUSD issuer-side wallets via Sentora Safe `0x4307` | vault | $167k | $167k | 0.05% | $1.33M | 0.28% | weekly, renewed |
| Liquid | Merkl ETHFI, Aave weETH lending | ETHFI via Aave Merkl Safe `0xdef1` | vault | $19k | $19k | 0.005% | 0 | 0 | 15 Jan 2026 |
| Lido Earn (stRATEGY) | Merkl aEthUSDe, USDe loop | Ethena (`0x8353D558`, tag ethena-aci) | vault (subvault) | $449k | $449k | 0.35% | ~0 | 0 | loop closed Apr 2026 |
| Lido Earn (stRATEGY) | Merkl wstUSR, Resolv leg | Resolv via Merkl | vault (subvault) | $258k | $258k | 0.20% | 0 | 0 | Feb 2026 |
| Lido Earn (stRATEGY) | sENA drop | Ethena | vault (subvault) | $22k | one-off | 0.02% | 0 | 0 | Apr 2026 |
| Lido Earn | DAO first-loss cover | Lido DAO treasury (share burn) | depositors via share price | $330k | one-off | 0.21% of avg TVL | 0 | 0 | 15 May 2026 |
| YieldBasis | YB gauge emissions | YieldBasis GaugeController `0x1be14811` | depositors who stake LT | $152k (since 31 May) | $358k | 4.8% of staked TVL | $504k | 3.16% of staked TVL | ongoing |
| Avant | CRV receipts | Curve emissions via Accountant `0x93b4b9bd` | vault (strategy wallet) | $10k | $10k | 0.08% | $37k | 0.11% | ongoing |
| Avant | Merkl MORPHO/USDS/USDC/WFRAX | Morpho, Sky-related, Frax creators | vault | $0.4k | $0.4k | ~0 | 0 | 0 | Jul 2026 |
| Avant | AvantPoints | Avant (`0xc22b79e6`) | depositors | unpriced | | | | | 13 Nov 2025 to 15 May 2026 |
| Liquity | BOLD from Curve BOLD/USDC gauge | BOLD deposited into the gauge (reward depositor not traced) | vault | $26k | $44k | 1.50% | $153k | 0.95% | ongoing |
| Liquity | Merkl BOLD, Uniswap V4 BOLD/USDC | Liquity (`0xB4244885`) | vault | $0.2k | $0.4k | 0.01% | $2.6k | 0.02% | weekly |
| Liquity | IPOR Fusion points | IPOR (`0x1384Fa51`) | depositors | unpriced | | | | | to 30 Nov 2026 |

The TVL denominator is the product book in ETH × ETH/USD, averaged over the product's life in the window. For the Lido stRATEGY lines it is the stRATEGY book, for the DAO cover the Earn ETH book, and for YB the staked share of the LT pool. The run-rate covers 31 Aug to T, annualized.

**At T, the only material live programs are Liquid's issuer-funded RLUSD/PYUSD ($2.73M/yr, 0.58% of TVL) and YB emissions ($0.5M/yr).** The KING, Ethena and Resolv flows and the Lido cover have all ended.

## Method

- **Share price.** These are archive `eth_call`s at every month-end, at T−90 and at T−365:
  - Liquid: Accountant `getRate`.
  - Lido Earn: oracle `getReport(WETH)`, with stRATEGY on its own oracle.
  - Avant: savETH `convertToAssets`.
  - YieldBasis: LT `pricePerShare`, and the staked view is gauge `convertToAssets` × `pricePerShare`.
  - Liquity: vault `convertToAssets`.

  Windows chain the segment returns; the residual absorbs compounding.
- **a, staking.** For Liquid, Lido and Avant this is LST rate growth × ETH equity:
  - Liquid uses weETH `getRate`.
  - Lido uses wstETH `stEthPerToken` on the stRATEGY book.
  - Avant uses its measured wallet mix of weETH, wstETH and WETH. Aave WETH supply income counts as WETH yield.

  Liquity uses wstETH trove collateral. YieldBasis holds WETH, so its a is 0.
- **b, loops.** (LST growth − realized WETH borrow cost) × average WETH debt per account. The borrow cost is the growth of `getReserveNormalizedVariableDebt` on Aave Core, Aave Prime and Spark, or the borrow-share price on Morpho. Lido's rsETH/WETH subvault uses the rsETH rate.
- **c, dollar leg.**
  - **Liquid:** the growth of measured claim balances × `convertToAssets` (senRLUSDv2, senPYUSDPRIMEv2, stcUSD, Paypal USD Main V2), less index-based interest on every dollar loan (Aave, Spark, Morpho, including PRIME/PYUSD).
  - **Lido, Avant and Liquity:** the claim is set equal to the debt (assumption), and earns earnUSD, savUSD or the Curve ebUSD/USDC virtual price respectively. Lido before March uses the sUSDe rate as a proxy, and the Lido USDe/sUSDe loop is measured directly.
  - **YieldBasis:** Curve WETH/crvUSD virtual-price growth on the LP value, less AMM `rate_mul` growth on the crvUSD debt.

  USD amounts convert at the segment's average Chainlink ETH/USD.
- **d, rewards.**
  - **Merkl:** the v4 per-recipient ledgers, with each campaign accrued linearly over its dates and valued at the DefiLlama daily average.
  - **Non-Merkl flows:** every ERC-20 transfer into the product accounts over 365 days, found by `eth_getLogs`, scanned for distributors. This turned up KING, wstUSR, sENA, CRV and the BOLD gauge.
  - **Valuation:** at the price on the day of receipt.
- **e, fees.**
  - Liquid: the on-chain Accountant fee schedule, time-weighted.
  - Lido: the Earn return minus the stRATEGY return, less the DAO cover.
  - Liquity: 0.5% plus 10% on gains (estimate).
  - YieldBasis: the change in `liquidity.admin`, which was zero.
  - Avant: not separable.
- **RPC.** Public Tenderly archive. When Tenderly hit its rate limit, `mainnet.gateway.tenderly.co`, mevblocker and Blast served as fallbacks. Every call is logged in `rpc_log.jsonl`.

## Limits

- **Residuals are not organic yield.** For Liquid, Avant and Liquity they are unmeasured books: LPs, other chains, keeper marks and unhedged dollar exposure. Read "without rewards" as an upper bound on organic yield only where the residual is small (Lido 90d).
- **Points are not priced.** AvantPoints and IPOR Fusion points are depositor incentives with no realized value, so Avant's and Liquity's reward shares are lower bounds.
- **Only cash-like rewards are counted.** No ether.fi Member Rewards or Lido or Mellow points programs on these products' tokens were active in the window, in Merkl or on-chain. ether.fi's 7.5M ETHFI Member Rewards ran Jun to Aug 2025, before the window.
- **KING value depends on the DefiLlama LRT² price.** That price fell from about $1,060 to $260 over the year.
- **Avant's issuer book is only partly measured.** The Ethereum strategy wallet is the only measured part, and the senior/junior tranche split is not modeled.
