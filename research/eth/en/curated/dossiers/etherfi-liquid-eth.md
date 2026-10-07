# ether.fi Liquid ETH

Snapshot T: 2 October 2026, 23:59:59 UTC. Published 3 October; findings updated 7 October 2026. Rank #1 of the ETH carry products by dollars borrowed ($181.1M at a 7.79% debt-weighted rate). Strategy provider Nonce, infrastructure Veda ([product page](https://etherfi.gitbook.io/etherfi/products/liquid/live-vaults/liquid-eth-vault)).

## Findings

- **Liquid beat stETH by 0.66 pp a year over two years** (3.37% against 2.71%, share price against wstETH conversion).
- **The loop did not earn it.** Over two years the Aave and Spark ETH loop added +68 ETH over holding the same equity unlevered (+0.02 pp a year); two rate spikes (July 2025, April 2026) wiped out its carry. The dollar leg cost about 0.13 pp a year. The lead sits in income our model cannot assign (+1.5 pp a year before fees), and the share price did not show the loop's April loss when it happened ([LIQUID-LOOP](../LIQUID-LOOP.md)).
- **The dollar leg loses about $6.8M a year at 2 October rates.** Interest is about $14.1M a year, $9.0M of it on the $64.5M Aave USDC loan at 13.93%; the parked dollars earn about $7.3M ($4.7M base yield, $2.6M Merkl rewards). A quarter of the debt ($46M) has no dollar asset behind it that we could find.
- **Rewards are 34% of the lead over stETH** ([REWARDS-SPLIT](../REWARDS-SPLIT.md)). The RLUSD and PYUSD campaigns trace to the issuers' side; Sentora creates them but does not fund them.
- **Shared dollar vaults.** $55M sits in Sentora's RLUSD vault (53% lent to Kraken's kBTC loop) and $50M in the PYUSD vault (95% PRIME home-equity credit); a loss there hits BTC and ETH carry at once.
- **Thin liquidation buffer.** The main Aave loop runs at health factor 1.027; the dollar legs at 1.27 to 1.87. Breaches below 1.03 were self-inflicted (collateral sent to redemption queues), repaid after a median 13.5 hours.
- **Exit:** queue paid in 12.6 hours at the median and 12.3 days at worst. The 24-hour timelock does not cover the role that can change the fee.

## Contracts and the accounts being consolidated

| Component | Ethereum address |
|---|---|
| BoringVault / LiquidETH share token | `0xf0bb20865277abd641a307ece5ee04e79073416c` |
| Accountant | `0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198` |
| Teller | `0x9aa79c84b79816ab920bbce20f8f74557b514734` |
| Authority | `0x485bde66bb668a51f2372e34e45b1c6226798122` |
| Withdrawal queue | `0x0d2df071207e18ca8638b4f04e98c53155ec2ce0` |
| BoringDrone | `0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c` |
| PositionManager | `0x528353aea55dbbbf18be26d5726afe6585898dc5` |
| LoanManager | `0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3` |

Both managers belong to the main vault at T. Verified Drone source restricts its management methods to the main vault. These control relationships justify consolidating their positions.

The [officially linked DeBank bundle](https://debank.com/bundles/222822/accounts) contains 13 addresses. Inclusion in that bundle alone does not prove control; the remaining relationships still need verification.

## Shares and published value

| Metric at T | Value |
|---|---:|
| Ethereum shares | 125,538.573238 |
| Optimism shares | 34,533.284066 |
| Published share rate | 1.106822062823 ETH |
| Consolidated book NAV | 177,171.063302 ETH |
| USD book NAV at nearest ETH quote | $472.684M |
| Last rate update | 2 October 2026, 06:26:47 UTC |
| Rate age at T | 17 hours 33 minutes |

Ethereum block 26,108,081 and Optimism block 157,693,411 were verified as the last blocks no later than T. The $2,667.9504418816 ETH quote is timestamped T+1 second. It is the disclosed nearest quote, not an execution price at T.

Ethereum and Optimism share supply can be added because the verified Teller bridge burns shares on sending and mints them on receipt. A lock-and-mint bridge would require different accounting. Messages still in transit remain an audit item.

The chains on which shares circulate differ from those on which strategies operate. The interface shows portfolio allocation of Ethereum 93.72% and Monad 6.28%. Book NAV uses the Accountant's rate; it is not an independent market valuation of every asset and liability.

## How the ETH loops work

| Account at T | Collateral USD | Debt USD | Equity after debt | Collateral leverage | HF |
|---|---:|---:|---:|---:|---:|
| Main vault / Aave | $1,182.315M | $1,093.583M | $88.732M | 13.325× | 1.02708 |
| Main vault / Spark | $92.243M | $82.794M | $9.450M | 9.762× | 1.03615 |
| Drone / Aave | $133.116M | $76.589M | $56.527M | 2.355× | 1.39045 |
| Drone / Spark | $8.048M | $3.612M | $4.437M | 1.814× | 1.87192 |

These accounts use oracle valuations, not a common set of executable market prices. Main Aave holds weETH against WETH debt, and main Spark holds wstETH against WETH debt.

With debt and liquidation thresholds fixed, Aave reaches HF=1 after an approximately 2.637% reduction in the collateral oracle value; Spark does so after approximately 3.488%. These are not ETH/USD drawdown thresholds. They also need not equal the discount that triggers stress in a decentralized exchange (DEX).

At T, Aave prices weETH through WeETHPriceCapAdapter. Verified `getRatio` code reads `weETH.getRate` and caps rate growth. A DEX discount therefore need not reduce HF immediately. It may first make an exit expensive, leave insufficient ETH to repay debt, or create a gap between book NAV and the value obtainable in the market. Oracle reductions and market discounts are modelled separately.

The Drone borrows stablecoins, so its collateral remains sensitive to ETH/USD. Even if its dollar investment is market-neutral, the ETH collateral can be liquidated before that investment returns cash. A strategy's stated arbitrage neutrality does not remove this timing risk.

## Dollar carry and the claims actually held

| Main-vault ERC4626 claim at T | Assets returned by convertToAssets |
|---|---:|
| STCUSD | 24,625,816.339387 cUSD |
| senRLUSDv2 | 55,104,709.535318 RLUSD |
| senPYUSDPRIMEv2 | 49,605,232.777562 PYUSD |
| kpdWETH | 2,500 WETH |

One senPYUSDPRIMEv2 share represents approximately 2.02486 PYUSD; valuing it at one dollar is incorrect. PYUSD has 6 decimals, while RLUSD and cUSD have 18. Unit errors or incorrectly decoded dynamic ABI responses can create false unexplained balances worth tens of millions.

LoanManager holds 19,063.547023 weETH and approximately 34.289M RLUSD debt, with HF 1.40806. PositionManager holds 32,272,324.083318 PRIME, valued through a separate PRIME/PYUSD oracle rather than assuming PRIME=$1.

The main vault also holds weETH/USDC, weETH/RLUSD and PRIME/PYUSD Morpho positions. The partial reconciliation uses stored market borrow assets and borrow shares. It does not separately accrue interest since `lastUpdate`.

The cUSD allocation earns from borrower payments and Underwriter security. Current [stcUSD mechanics](https://docs.cap.app/overview/protocol-overview/stcusd-mechanics) describe borrower interest, idle reserve income and collateral realization under stress. Collateral does not eliminate correlated losses, delays in realization or insufficient liquidity.

## LP positions and assets missed by ERC20 balances

Two active Uniswap V3 NFTs contain approximately 6,875.525431 ETH of principal after converting the receipt backing, or $18.344M. Both have token0=WETH and token1=weETH; weETH conversion is applied only to token1. Uncollected fee growth is excluded, and three older NFTs have zero liquidity.

Fluid NFT 4241 belongs to vault 74. It holds smart collateral in the weETH/native-ETH DEX and wstETH debt. The position's share of real DEX reserves minus current debt gives approximately 3,073.874326 ETH net, or $8.201M. Packed supply shares were decoded from primary source and checked against `DexResolver.getDexState`. Imaginary reserves are not counted as capital.

A finalized but unclaimed Lido withdrawal NFT 122235 was separately verified for 25.069520 ETH. Final payout was not simulated. A claim remains an asset after the related ERC20 token has been burned.

## What the return history shows

| Window ending T | Liquid ETH | stETH through wstETH | weETH through getRate | Liquid ETH minus stETH |
|---|---:|---:|---:|---:|
| 30 days | 0.2610% | 0.1849% | 0.1915% | +0.0761 pp |
| 90 days | 0.8094% | 0.5490% | 0.5875% | +0.2604 pp |
| 180 days | 1.5917% | 1.1580% | 1.1887% | +0.4336 pp |
| 365 days | 3.8700% | 2.4785% | 2.4830% | +1.3914 pp |
| 730 days | 6.8501% | 5.4875% | 5.2947% | +1.3626 pp |

The 730-day row is cumulative: annualised, Liquid earned **3.37%** a year against **2.71%** for stETH, a lead of **0.66 pp a year** (the 1.36 pp quoted on 4 October is the two-year cumulative gap). The comparison uses published PPS and conversion rates. External points and separately distributed rewards are excluded.

The share price changes in discrete updates. The endpoint rate is 17.55 hours older than T, while staking conversions use archive execution blocks no later than each endpoint. The age of the rate is retained for every period.

The dataset contains 719 Accountant events: 653 rate changes and 66 other events. It includes 24 completed monthly observations, from October 2024 to September 2026. These describe share supply and book NAV, not the composition of each historical portfolio.

The second year was stronger relative to staking. Excess return over the last 365 days nearly equals the excess over the full 730 days. This shows that relative performance changed over time. It does not establish which strategy change caused the difference.

## Why the published capital balance changed

Over the 24 completed months, October 2024 to September 2026, book capital increased from 146,909.038 ETH to 176,962.431 ETH. Changes in the accounting rate contributed 10,336.365 ETH; changes in share supply, valued at each month's closing rate, contributed 19,717.027 ETH. Together they explain the 30,053.393 ETH change.

The calculation uses each chain's own rate and share supply. It distinguishes capital growth from return on an existing share. Share changes can include issuance, redemptions and cross-chain movements; they are not a verified ledger of external deposits. The rate effect explains the published marks without identifying which historical strategies earned the income. [Monthly calculation and limits](../RETURN-DRIVERS.md).

## Fees and governance

At T, the management fee is 35 bp, or 0.35% annually. Ethereum and Optimism Accountants have different state structures. Optimism also stores `highwaterMark` and `performanceFee`, with the latter set to zero. Using one ABI layout for both would decode them incorrectly. Accrued fees and their allocation across chains still need final reconciliation.

Fees changed in June 2026, 25→50→65 bp; July, 65→80; August, 80→70→10→35. The current 35 bp cannot be applied to the entire history. Fee claims are retained as separate events. The Ethereum Accountant's calendar-time average annual fee over the 730-day window was 0.6861%. It weights time rather than invested capital, so it is not an investor's realized fee rate.

During that window, its claim events paid 121.699459 weETH across three transactions and 1,996.421851 WETH across 16 transactions. These token amounts are kept separate. Payments can settle fees accrued earlier; they do not measure strategy income or operator profit. Revenue sharing, downstream charges, operating costs and Optimism's fee ledger remain open. At fixed Ethereum-circulating shares and the captured rate, a 0.35% annual fee would represent approximately 486.321 ETH. This is a flat-balance scenario, not recorded revenue. [Fee chronology and claim transactions](../RETURN-DRIVERS.md).

Authority is owned by TimelockController `0xd829f278016b90fec735f9a12bf8b75e06102c89`. At T, `getMinDelay` returns 86,400 seconds. A zero owner on the vault or Accountant does not make the system immutable.

The historical Authority scan found 36 addresses ever assigned roles and 22 with active roles at T. Three role-11 addresses could update the accounting rate. Two addresses could change the management fee: the owner timelock through role 8, and `0x607d0c7e3578802eb46d388cb86cfba8ff657306` through role 55. The owner delay therefore does not guarantee a 24-hour notice period before every fee change. The captured Accountant code caps this setter at 20%; this is a code limit, not the actual fee.

The selected-function review also distinguishes vault management, deposits, withdrawals, pauses, restarts and changes to rate providers. It does not establish beneficial identities, every strategy permission, or all Timelock proposer and executor rights. [Exact permission table and exit terms](../PRODUCT-TERMS.md).

## How investors withdraw

At T, the queue accepts weETH. Its request settings are maturity 1 hour, minimum deadline 3 days and discount range 0-10 bp. These settings govern requests and solver operations. They do not promise payment in an hour or three days.

The checked queue disables WETH. Teller allows WETH deposits but no direct WETH withdrawals; weETH is enabled in both directions.

The help centre's current estimate of up to three days depends on liquidity, strategy operations and settlement. It is separate from the fixed-block queue settings and does not guarantee that ETH will arrive within that period. [Current guidance and source dates](../PRODUCT-TERMS.md).

There are three different processes: selling LiquidETH shares, having a withdrawal request fulfilled, and unwinding the underlying portfolio. The last requires repayment of ETH and dollar debt, recovery of external investments, redemption of underlying assets, and bridge settlement where relevant. Selling LP inventory does not guarantee enough of the currency needed to repay debt.

## Interface allocation, 3 October

Captured on 3 October, after T; not the portfolio at T.

| Sleeve | Weight | Estimated UI APY | Linked venues |
|---|---:|---:|---|
| Stable Carry | 52.27% | 2.37% | Cap, ether.fi, Morpho, Yuzu |
| weETH Looping | 19.57% | 6.02% | ether.fi, Aave |
| Sentora weETH/RLUSD or Hastra PRIME Carry Trade | 12.39% | 3.54% | ether.fi, Morpho |
| Liquid Monad ETH | 6.28% | 1.92% | Nested BoringVault |
| Uniswap LP | 4.05% | 0.81% | Uniswap |
| Spark wstETH/WETH Loop | 2.08% | 5.06% | Spark |
| weETH/ETH or stETH LP | 1.81% | 4.81% | Fluid |
| Withdrawal Liquidity | 1.55% | 0% | Exit liquidity |

Carry allocations total 64.66%; the two explicitly named loop allocations total 21.65%. The weights sum to 100%, and their weighted estimated APY is 3.201209%.

The difference from the displayed 14-day APY is not fully explained. Allocation estimates and retrospective returns use different periods and may update at different times. Fees should not be deducted again without checking whether each estimate already includes them.

## As of 4 October (superseded)

- *Return:* "+1.36 pp over two years alongside a 13.3x allocation" was the cumulative gap; the annual figure is 0.66 pp.
- *Reconciliation:* reconstructed positions, ERC4626 assets, liquid tokens, NFT principal and the nested Monad claim totalled $460.231M against a $472.684M book, leaving $12.453M (2.634%) unexplained. The expanded look-through ([CAPITAL-INCOME-EXIT](../CAPITAL-INCOME-EXIT.md)) gives $458.586M reconstructed and $14.098M unmapped; not a proven shortfall. Liquid Monad: 8,085.725 shares at 1.00532 ETH ($21.687M), see [Liquid Monad](liquid-monad.md).
- *Rate sensitivity (still valid):* with positions fixed, +1 pp on the WETH borrow rate cuts the isolated Aave loop's return on equity by about 12.3 pp a year.

Product history and owners: [PRODUCT-EVOLUTION](../PRODUCT-EVOLUTION.md). Calculations: `data/eth/etherfi_verified_metrics.json`, `etherfi_partial_balance_sheet.json`, `etherfi_staking_comparison.json`, `etherfi_history_monthly.json`; loop ledger `data/eth/top5/liquid/`.
