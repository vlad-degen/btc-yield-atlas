# ether.fi Liquid ETH

The [final capital, income and exit findings](../CAPITAL-INCOME-EXIT.md) extend this original reconstruction with dated cash flows, public backing and investor payout evidence. Original partial-reconstruction figures retain their original scope.


Published 3 October 2026; expanded and reviewed 4 October. Snapshot T: 2 October 2026, 23:59:59 UTC. This dossier verifies share accounting, material positions and return history. An unexplained difference remains between reconstructed positions and published net asset value (NAV), so the independent reconciliation is incomplete.

## What the product is and where income comes from

Liquid ETH is a managed portfolio whose value is reported in ETH. It earns income through staking, ETH borrowing and reinvestment, dollar investments funded by borrowing against ETH collateral, liquidity-provider (LP) positions, and investments in other vaults.

Staking ultimately earns validator income. Lending spreads depend on reinvestment returns exceeding borrowing costs. Dollar lending is paid by external borrowers, while LP positions earn trading fees and incentives. These sources have different payers and risks even when the investor's account is denominated in ETH.

The [official Liquid ETH description](https://etherfi.gitbook.io/etherfi/products/liquid/live-vaults/liquid-eth-vault) provides the product identity and addresses. The [product interface](https://www.ether.fi/app/cash/earn/liquid/eth-yield?tab=breakdown), captured on 3 October, names Nonce as strategy provider and Veda as infrastructure.

The interface displayed approximately $475M total value locked (TVL) and 3.23% 14-day annual percentage yield (APY). This observation is after T. Positions were labelled as updated one day earlier, without an exact timestamp. These figures do not replace evidence from fixed blocks.

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

## Disclosed portfolio composition

These weights were captured on 3 October and are not asserted to describe the portfolio exactly at T. A sleeve is an allocation within the larger portfolio.

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

## How the ETH loops work

An ETH loop deposits a liquid staking token (LST) as collateral, borrows ETH, buys more staking exposure and repeats the cycle. It increases both the staking exposure and the debt that must be repaid.

| Account at T | Collateral USD | Debt USD | Equity after debt | Collateral leverage | HF |
|---|---:|---:|---:|---:|---:|
| Main vault / Aave | $1,182.315M | $1,093.583M | $88.732M | 13.325× | 1.02708 |
| Main vault / Spark | $92.243M | $82.794M | $9.450M | 9.762× | 1.03615 |
| Drone / Aave | $133.116M | $76.589M | $56.527M | 2.355× | 1.39045 |
| Drone / Spark | $8.048M | $3.612M | $4.437M | 1.814× | 1.87192 |

HF means health factor, the lending protocol's measure of collateral coverage before liquidation. These accounts use oracle valuations, not a common set of executable market prices. Main Aave holds weETH against WETH debt, and main Spark holds wstETH against WETH debt.

With debt and liquidation thresholds fixed, Aave reaches HF=1 after an approximately 2.637% reduction in the collateral oracle value; Spark does so after approximately 3.488%. These are not ETH/USD drawdown thresholds. They also need not equal the discount that triggers stress in a decentralized exchange (DEX).

At T, Aave prices weETH through WeETHPriceCapAdapter. Verified `getRatio` code reads `weETH.getRate` and caps rate growth. A DEX discount therefore need not reduce HF immediately. It may first make an exit expensive, leave insufficient ETH to repay debt, or create a gap between book NAV and the value obtainable in the market. Oracle reductions and market discounts are modelled separately.

The Drone borrows stablecoins, so its collateral remains sensitive to ETH/USD. Even if its dollar investment is market-neutral, the ETH collateral can be liquidated before that investment returns cash. A strategy's stated arbitrage neutrality does not remove this timing risk.

## Dollar carry and the claims actually held

Carry invests borrowed funds where the expected return exceeds the funding cost. In Liquid ETH, this includes borrowing dollars against ETH-related collateral and buying dollar vault shares.

| Main-vault ERC4626 claim at T | Assets returned by convertToAssets |
|---|---:|
| STCUSD | 24,625,816.339387 cUSD |
| senRLUSDv2 | 55,104,709.535318 RLUSD |
| senPYUSDPRIMEv2 | 49,605,232.777562 PYUSD |
| kpdWETH | 2,500 WETH |

ERC4626 is a vault-share interface that allows a contract to quote the assets represented by its shares. One senPYUSDPRIMEv2 share represents approximately 2.02486 PYUSD; valuing it at one dollar is incorrect. PYUSD has 6 decimals, while RLUSD and cUSD have 18. Unit errors or incorrectly decoded dynamic ABI responses can create false unexplained balances worth tens of millions.

LoanManager holds 19,063.547023 weETH and approximately 34.289M RLUSD debt, with HF 1.40806. PositionManager holds 32,272,324.083318 PRIME, valued through a separate PRIME/PYUSD oracle rather than assuming PRIME=$1.

The main vault also holds weETH/USDC, weETH/RLUSD and PRIME/PYUSD Morpho positions. The partial reconciliation uses stored market borrow assets and borrow shares. It does not separately accrue interest since `lastUpdate`.

The cUSD allocation earns from borrower payments and Underwriter security. Current [stcUSD mechanics](https://docs.cap.app/overview/protocol-overview/stcusd-mechanics) describe borrower interest, idle reserve income and collateral realization under stress. Collateral does not eliminate correlated losses, delays in realization or insufficient liquidity. The interface's Yuzu connection has not been traced to a separate position or its final payers.

## LP positions and assets missed by ERC20 balances

Two active Uniswap V3 NFTs contain approximately 6,875.525431 ETH of principal after converting the receipt backing, or $18.344M. Both have token0=WETH and token1=weETH; weETH conversion is applied only to token1. Uncollected fee growth is excluded, and three older NFTs have zero liquidity.

Fluid NFT 4241 belongs to vault 74. It holds smart collateral in the weETH/native-ETH DEX and wstETH debt. The position's share of real DEX reserves minus current debt gives approximately 3,073.874326 ETH net, or $8.201M. Packed supply shares were decoded from primary source and checked against `DexResolver.getDexState`. Imaginary reserves are not counted as capital.

A finalized but unclaimed Lido withdrawal NFT 122235 was separately verified for 25.069520 ETH. Final payout was not simulated. A claim remains an asset after the related ERC20 token has been burned.

## How much of the published value is explained

Reconstructed positions, ERC4626 assets, liquid tokens, NFT principal and the nested Monad book claim total $460.231M, compared with $472.684M book NAV. The unexplained $12.453M, or 2.634%, remains unresolved. It is not an established deficit.

The Accountant for 8,085.725173 Liquid Monad ETH shares was located through its own Teller. At T, it reports 1.005322540540 ETH/share, valuing the claim at $21.687M. Main Liquid ETH owns the entire Ethereum supply.

The Accountant at the same address on Monad reports 1.0, with zero local share supply. Each chain's accounts are checked separately, and remote backing remains unreconstructed. The post-T 6.28% interface weight still needs reconciliation and is not inserted into the balance sheet. See the [Liquid Monad dossier](liquid-monad.md).

The reconciliation has several limits. Current token and NFT discovery can miss assets sold after T. Reward or royalty rights and entitlement to retained ETHFI remain unverified. Uncollected Uniswap fee growth is unvalued, some stablecoins are marked at $1, and oracle and date conventions differ.

Accordingly, 97.37% is the fraction of book NAV explained by these valued positions and nested book claims. It is not an audit confirmation that 97.37% of physical backing has been independently verified.

## What the return history shows

Price per share (PPS) measures the published value of one vault share.

| Window ending T | Liquid ETH | stETH through wstETH | weETH through getRate | Liquid ETH minus stETH |
|---|---:|---:|---:|---:|
| 30 days | 0.2610% | 0.1849% | 0.1915% | +0.0761 pp |
| 90 days | 0.8094% | 0.5490% | 0.5875% | +0.2604 pp |
| 180 days | 1.5917% | 1.1580% | 1.1887% | +0.4336 pp |
| 365 days | 3.8700% | 2.4785% | 2.4830% | +1.3914 pp |
| 730 days | 6.8501% | 5.4875% | 5.2947% | +1.3626 pp |

pp means percentage points. The 730-day annualized returns are 3.3683% for Liquid ETH and 2.7071% for stETH. The comparison uses published PPS and conversion rates. External points and separately distributed rewards are excluded.

PPS changes in discrete updates. The endpoint rate is 17.55 hours older than T, while staking conversions use archive execution blocks no later than each endpoint. The age of the rate is retained for every period.

The dataset contains 719 Accountant events: 653 rate changes and 66 other events. It includes 24 completed monthly observations, from October 2024 to September 2026. These describe share supply and book NAV, not the composition of each historical portfolio.

The second year was stronger relative to staking. Excess return over the last 365 days nearly equals the excess over the full 730 days. This shows that relative performance changed over time. It does not establish which strategy change caused the difference.

## Why the published capital balance changed

Over the 24 completed months, October 2024 to September 2026, book capital increased from 146,909.038 ETH to 176,962.431 ETH. Changes in the accounting rate contributed 10,336.365 ETH; changes in share supply, valued at each month's closing rate, contributed 19,717.027 ETH. Together they explain the 30,053.393 ETH change.

The calculation uses each chain's own rate and share supply. It distinguishes capital growth from return on an existing share. Share changes can include issuance, redemptions and cross-chain movements; they are not a verified ledger of external deposits. The rate effect explains the published marks without identifying which historical strategies earned the income. [Monthly calculation and limits](../RETURN-DRIVERS.md).

## Fees and governance

At T, the management fee is 35 bp, or 0.35% annually. bp means basis points. Ethereum and Optimism Accountants have different state structures. Optimism also stores `highwaterMark` and `performanceFee`, with the latter set to zero. Using one ABI layout for both would decode them incorrectly. Accrued fees and their allocation across chains still need final reconciliation.

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

## The economic finding

Liquid ETH has verified excess return over staking, but it is much smaller than the gross leverage: +1.36 pp over two years alongside a 13.3× allocation. With positions fixed, a +1 pp rise in borrowing rates reduces the isolated Aave loop's annual return on equity by approximately 12.32 pp.

This is a sensitivity calculation, not a forecast or a whole-vault loss estimate. The consolidated impact depends on how much equity belongs to that allocation.

The two loops and the carry investments respond differently to stress. Shared ETH collateral, weETH exposure, dollar credit, managers and withdrawal liquidity connect them. Different protocol names do not establish independent risks.

## Evidence and remaining work

Calculations: `data/eth/etherfi_verified_metrics.json`, `etherfi_partial_balance_sheet.json`, `etherfi_staking_comparison.json`, `etherfi_history_monthly.json`, `fluid_pilot_decoded.json`, `governance_T.json`. Raw requests and responses: `raw/eth/2026-10-02/requests.jsonl` and content-addressed files.

Remaining work includes Liquid Monad assets and liabilities, pending bridge messages, complete strategy and timelock permissions, economic reward rights, complete fee ledgers on both chains, Morpho interest accrual, Uniswap fee growth, historical asset inventory at T, and simulations of redemption and debt repayment. Until those checks are complete, the dossier cannot be described as fully reconciled.

<!-- substantive-parity -->
## ether.fi Liquid ETH

The present contract was used in June 2024. ETH loops came first; Aave dollar borrowing appeared in August 2025. Morpho financing followed through the LoanManager in June 2026 and the main vault in July.

| Date | Change | Economic significance |
| --- | --- | --- |
| 2024-06-11T02:15:35+00:00 | First observed share issuance | A 0.24446-share mint establishes use of the present contract. Deployment was 3 June; neither timestamp alone establishes the public launch. [Primary evidence](https://etherscan.io/tx/0x1221b300eb5ee3ef6ec3b94b16dc888a68293e49b84b3a5d7418be126ff19070) |
| 2024-06-25 | The Aave ETH loop begins | The main vault first borrows WETH. This increases staking exposure; it does not create dollar investment capital. [Primary evidence](https://etherscan.io/tx/0x744955da54daf75b9d30f6c648f685e3921e45f6cdc17aa695d1314aaf0f6cfd) |
| 2025-08-18 | Dollar financing appears in the managed account | The controlled account 0x0a42…c02c first borrows USDC on Aave. It already owes 47.07M USDC at the August month end. [Primary evidence](https://etherscan.io/tx/0x4e906fd4127e61b3360c3bf1d1953366ca49246a67cec545c033c4f46e63ebfb) |
| 2025-11-26 | Cap becomes an investment destination | The captured stcUSD deposit history begins. Its receipt earns through Cap’s credit machinery; this is a new destination, not extra underlying ETH. [Primary evidence](https://etherscan.io/tx/0x9b217842406c49d31c2dc5e32d0d8bc3cee67cf2aeb18c2bae3ef033dd64bc88) |
| 2026-03-24 | Spark adds a second ETH loop | The first main-vault Spark WETH borrowing is observed. The main Aave and Spark accounts have different liquidations and funding costs. [Primary evidence](https://etherscan.io/tx/0x8fd92c153ccdf45c864f79b4b7fd288f430e40aa017d4f56338cb35abb5a3442) |
| 2026-06-23 | Morpho dollar routes expand beyond the main vault | The controlled LoanManager begins RLUSD borrowing in June. The main vault adds weETH/RLUSD and weETH/PYUSD in July; Sentora RLUSD V2 deposits begin on 7 August. [Primary evidence](https://etherscan.io/tx/0x2ad45b7723fbbfb5b6c36ce035167a0c7bfc825b6ad36573a4d9e4fed2d0cb08) |
| 2026-08-09T11:00:21+00:00 | Cash shares move into pooled custody | The captured Cash spoke history begins. By T, the Hub holds 20.53% of the whole Liquid book on behalf of 7,012 positive account positions. [Primary evidence](https://optimistic.etherscan.io/address/0xdffcc3536d932eb51df51a7f5fa407c4270d5308) |
| 2026-09-25 | PRIME-backed financing enters the credit vault | An 18M PYUSD loan against PRIME is deposited into a PYUSD credit vault. Its claim and financing are measured through T. [Primary evidence](https://etherscan.io/tx/0xb12b59b3177d97b6f2118b14b6712c09558c75c977fa78c5ef3eb1d4d2fbc176) |
| 2026-09-25 | Kyber adds a distribution channel | Kyber announces Liquid ETH on KyberEarn. This establishes an integration announcement, not how many new deposits it generated. [Primary evidence](https://blog.kyberswap.com/ether-fi-liquid-vaults-are-live-on-kyberearn/) |

### What the investor owns and earns

For the 18M PYUSD investment originated on 25 September, FIFO, LIFO and proportional withdrawal allocation all give a negative claim-minus-funding result: -5,360 to -4,584 PYUSD through T. Rewards, collateral income, gas and outer fees are separate.

The two largest Ethereum wallets together hold about 37% of the whole book. The Optimism Hub holds another 20.53% across 7,012 positive Cash account positions. Its single address conceals a distribution of claims; these accounts are not necessarily different people.

Between September 2024 and September 2026, the ETH book grew by 30,053 ETH. Share-supply changes account for 19,717 ETH of that change; the share-price effect accounts for 10,336 ETH. This is an accounting bridge, not a cash-flow or carry-profit estimate.

The Ethereum management fee changed repeatedly: 1.50% in January 2025, zero in July, and 0.35% at T. Nineteen claimed payments total 2,130.60 ETH after converting each weETH payment at its own block. This is platform cash received, not operator profit.

The May 2025 Member Rewards proposal budgets 7.5M ETHFI across ether.fi for June to August and assigns Liquid ETH nine points per ETH per day, versus three for staking. This explains the distribution incentive; the ecosystem budget is not a measured payment to this vault or organic carry income.

At T, Aave USDC funding is 13.93% APR, versus 4.38% for Aave USDT and 4.39% for Spark PYUSD. Funding cost depends on the actual loan currency and venue; a low quote on one route does not describe the whole carry book.

[Distribution proposal](https://governance.ether.fi/t/ether-fi-member-rewards/2974).

| Named owner / account | Share of stated claim | Denominator |
| --- | --- | --- |
| [0x6794662db6a212b607ecfc07360941b5ddfd4b6b](https://optimistic.etherscan.io/address/0x6794662db6a212b607ecfc07360941b5ddfd4b6b) | 33.3449% | Share of Cash Hub |
| [0xc93c35246652b40f3f090bd180b58322679b9f1b](https://optimistic.etherscan.io/address/0xc93c35246652b40f3f090bd180b58322679b9f1b) | 9.1729% | Share of Cash Hub |
| [0x463ff502f702a306f2c5850a0562fb47b8e4acea](https://optimistic.etherscan.io/address/0x463ff502f702a306f2c5850a0562fb47b8e4acea) | 3.0972% | Share of Cash Hub |
| [0x72cbd2c5e6cfe895224af00c039c7d2b3b11a9b5](https://optimistic.etherscan.io/address/0x72cbd2c5e6cfe895224af00c039c7d2b3b11a9b5) | 2.0542% | Share of Cash Hub |
| [0x0cb7977b907782ca1038ba68699263c9eecaf879](https://optimistic.etherscan.io/address/0x0cb7977b907782ca1038ba68699263c9eecaf879) | 1.7065% | Share of Cash Hub |
| [0xf387f8058e00fe37d5c11a205ee0bad9774ac4df](https://optimistic.etherscan.io/address/0xf387f8058e00fe37d5c11a205ee0bad9774ac4df) | 1.5225% | Share of Cash Hub |
| [0x428167a972786b7f924af2f2ecf6680aa8b5243e](https://optimistic.etherscan.io/address/0x428167a972786b7f924af2f2ecf6680aa8b5243e) | 1.4596% | Share of Cash Hub |
| [0x559e319c3710c2370ed1b18878ee10a2ff1f9339](https://optimistic.etherscan.io/address/0x559e319c3710c2370ed1b18878ee10a2ff1f9339) | 1.4378% | Share of Cash Hub |
| [0x1c0a6763a251be74ef56c1919b1184f94f93a70d](https://optimistic.etherscan.io/address/0x1c0a6763a251be74ef56c1919b1184f94f93a70d) | 1.4326% | Share of Cash Hub |
| [0xed0e0f34671338fd51c90cad6b5eabc239ac4f6e](https://optimistic.etherscan.io/address/0xed0e0f34671338fd51c90cad6b5eabc239ac4f6e) | 1.2906% | Share of Cash Hub |

[Reproducible measurement ledger](../../../../data/eth/parity_depth_measurements.json).

