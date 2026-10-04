# ETH capital: what can be counted once

The market panel measures reported ETH-related exposure. It does not measure unique ETH capital. This closure adds a separate calculation anchored to actual native ETH and canonical WETH custody at the original snapshot, 2 October 2026 at 23:59:59 UTC. The Ethereum block is 26,108,081. New collection on 4 October reads that historical block; it does not move the financial snapshot forward.

The result is **457,182.304022 ETH of independently measured native ETH and WETH custody in the examined yield venues**. A further **25,175.548143 ETH** is locked for finalized Lido withdrawal claims and remains separate. These figures establish underlying custody. They do not establish that every unit is currently earning, is immediately withdrawable, or belongs to a particular investor.

An exact global total remains unavailable. The missing consensus balance and unexamined custody cannot be replaced by an arbitrary overlap discount. A bounded result is nevertheless possible for the stated liquid universe: examined yield-venue custody is at least 457,182.304022 ETH, while all canonical WETH together with the examined native ETH balances is 2,045,831.884961 ETH. That second number is a conservative ceiling only for this liquid scope. Native consensus ETH, other native custody and other chains sit outside it.

## Quantities suitable for the website

| Quantity | ETH | Meaning |
|---|---:|---|
| Native/WETH custody in examined yield venues | 457,182.304022 | Distinct physical balances at the same historical block; some reserve cash can be idle |
| Lido finalized withdrawal-claim custody | 25,175.548143 | Separate exit claims; not added to the main custody subset or issuer backing |
| Extended examined custody including finalized claims | 482,357.852165 | A custody total that includes the exit queue |
| Maximum liquid custody in the stated canonical WETH/native scope | 2,045,831.884961 | All canonical WETH, even unclassified balances, plus the named native balances |
| Unique global ETH earning capital | Not measured | Actual consensus balances, broader custody and claim links remain incomplete |
| Percentage of global market covered | Not measured | The overlapping adapter panel is not a valid denominator |

The two measured ledgers answer different questions. The existing panel shows the scale and distribution of reported exposure. The new custody subset proves where some underlying ETH sits. They should appear together with their definitions, without dividing one by the other or replacing the market headline with the small measured subset.

## The physical custody reconciliation

| Examined group | ETH |
|---|---:|
| Aave V3 and Spark Ethereum WETH reserve cash | 385,841.291121 |
| 21 canonical Uniswap V3 pools and seven Curve main-registry pools | 69,531.485331 |
| Lido buffer, execution rewards vault and consensus withdrawal vault | 1,809.527570 |
| Total before finalized withdrawal claims | 457,182.304022 |

There are 33 included address/asset nodes and one separately labelled withdrawal-queue node. Each native balance is counted at its own address. Each WETH balance is assigned once to the canonical WETH escrow, rather than added on top of the entire escrow.

At T, canonical WETH supply is **2,027,838.730723 WETH**, and the contract holds **2,027,838.730723 native ETH**. The reconciliation difference is exactly zero in wei. Of that supply, **439,189.149783 WETH** is held in the examined lending and LP nodes. **1,588,649.580939 WETH** remains outside those nodes. That remaining amount is measured, but its use is not classified. It cannot all be called productive capital.

The examined native ETH balances add **17,993.154239 ETH**. The bounded liquid ceiling is therefore:

`2,027,838.730723 canonical WETH + 17,993.154239 examined native ETH = 2,045,831.884961 ETH`

This ceiling bounds potential yield-venue custody within the stated canonical WETH and named-native universe. It does not include every ETH balance on Ethereum. It cannot cap the full yield market.

The Lido queue's `getLockedEtherAmount()` equals its native balance exactly: 25,175.548143 ETH. These are finalized claim funds at a distinct address. The separately captured 149,994.440130 unfinalized stETH requests remain claims on the issuer and add no new ETH. Lido's [withdrawal contract documentation](https://docs.lido.fi/contracts/withdrawal-queue-erc721/) describes the separation between request, finalization and claim.

## Lido accounting is reconciled, but is not the T consensus census

Lido's `getTotalPooledEther()` returns **9,841,288.206626 ETH** at T. The following components reconcile exactly in wei:

| Pool accounting component | ETH |
|---|---:|
| Active CL balance at last oracle report | 9,516,117.556528 |
| Pending CL deposits at last oracle report | 317,438.000000 |
| Deposited since the last report | 1,472.000000 |
| Buffered ETH | 1,725.562173 |
| External stVault backing | 4,535.087925 |
| Total pooled accounting | 9,841,288.206626 |

The last processed oracle reference is slot **15,343,199**, or **2 October 2026 at 12:00:11 UTC**. It precedes T by **43,188 seconds**, almost 12 hours. Reading the accounting contract at T does not make the CL report a direct observation of every validator's actual balance at T. None of this reported CL accounting is added to the physical custody floor. The [Lido balance model](https://docs.lido.fi/contracts/lido/) distinguishes active, pending, post-report deposits and external backing.

`getBeaconStat()` returns 501,047 for both validator counters. The captured documentation says those deprecated compatibility counters do not represent the actual active validator set. Multiplying either counter by 32 would be wrong. More generally, EIP-7251 permits compounding validator effective balances up to 2,048 ETH; effective balance is consensus weight, not the full actual balance. [Ethereum EIP-7251](https://eips.ethereum.org/EIPS/eip-7251)

## Lending adds claims, not a second ETH reserve

The same-block reserve reconciliation is:

| Ethereum market | WETH lender claims | WETH debt | WETH reserve cash |
|---|---:|---:|---:|
| Aave V3 | 2,084,173.402169 | 1,761,598.486675 | 269,693.451502 |
| Spark | 608,325.686676 | 492,183.597439 | 116,147.839618 |
| Total | 2,692,499.088844 | 2,253,782.084114 | 385,841.291121 |

The lender claims exceed current reserve cash by **2,306,657.797724 WETH**. Most of that difference is a claim on borrowers. It is not additional ETH sitting in those reserve contracts. The WETH can also be spent, staked or supplied elsewhere after borrowing, so subtracting all debt from all market rows would not create a reliable global root census either.

The accounting remainder is retained. Aave's lender claims minus cash and debt is 52,881.463992 WETH, while its separately reported reserve deficit is 52,964.453913 WETH. Spark's remainder is negative 5.750382 WETH. These distinct getters and rounding/accounting differences are not renamed as independent capital or treated as exact losses.

The most direct staking overlap is wstETH. Aave and Spark together report **2,350,079.425692 ETH-equivalent of wstETH lender claims** at the T conversion rate. Those claims reuse Lido backing and add zero new ETH on top of the issuer root. Adding them to Lido's book would produce 12,191,367.632318 ETH-equivalent. Removing the repeated lender layer returns the same 9,841,288.206626 ETH issuer accounting. That is a closed accounting example, not independent proof of actual consensus custody at T. The same calculation separately retains wstETH cash and debt, instead of adding all three balances. The [wstETH contract](https://docs.lido.fi/contracts/wsteth/) wraps stETH; wrapping changes the receipt format rather than creating a new validator deposit.

Equivalent lender-claim edges are captured for weETH and rETH. Each points back to ether.fi staking or Rocket Pool backing. Conversion into ETH equivalent is an accounting transformation, not independent proof that every issuer's consensus backing has been reconciled.

## The measured Kelp to EigenLayer to Lido chain

The official EigenLayer stETH strategy at `0x93c4b944d05dfe6df7645a86cd2206016c51564d` holds **233,604.391119 stETH** at T. Its underlying-token getter returns canonical stETH, it is allowed for deposits, and its total-share conversion reconciles with token custody to within 104 wei. The deployed strategy identity is recorded in [EigenLayer's official contract repository](https://github.com/Layr-Labs/eigenlayer-contracts#deployments).

Kelp's seven node delegators have active deposit shares worth **199,118.512331 stETH** inside that strategy. This is **85.2375%** of the strategy's stETH custody. The path is:

`Lido underlying staking → 233,604.391119 stETH in EigenLayer strategy → 199,118.512331 stETH attributed to Kelp node deposit shares`

These amounts are nested. They cannot be added together as unique ETH. Counting the same stake once as Lido, again as EigenLayer and again as Kelp would repeat its backing across three product layers.

Kelp's total stETH accounting exposure is **217,203.622575 stETH**. Direct node custody adds 0.060633 stETH, and the deposit pool itself holds **2,999.828662 stETH**. The remaining **15,085.220948 stETH** is not allocated by these active-node and direct-custody reads. Queued withdrawals and other accounting locations need their own reconciliation. This remainder is an unallocated accounting amount, not a measured loss or deficit.

Native restaking remains a separate unknown. The captured current [Eigen measurement adapter](https://github.com/DefiLlama/DefiLlama-Adapters/blob/main/projects/eigenlayer/index.js) has `timetravel: false`, queries native validator balances with a three-day offset, and retrieves a cached external query. That current source explains why its WETH-labelled aggregate is not evidence of physical liquid WETH. Its source version at T was not independently reproduced, so the frozen daily API date alone cannot date the native component precisely. The [Kelp adapter](https://github.com/DefiLlama/DefiLlama-Adapters/blob/main/projects/kelp-dao/index.js) also identifies its exposure as including deposits made through node delegators into EigenLayer.

## LP principal and history added in this closure

The canonical Uniswap V3 factory was queried at T for six WETH pairs, USDC, USDT, DAI, wstETH, weETH and rETH, across four fee tiers. **21 of 24 pair/fee combinations have a pool**. Each pool's token identities and WETH custody were read at the historical block. Factory [pool discovery](https://docs.uniswap.org/contracts/v3/reference/core/interfaces/IUniswapV3Factory) provides a contract-based identity check.

Curve's main-registry directory contains 49 pools at the separately dated collection. Seven list native ETH or WETH. Their contract existence, selected coin identity and cash were verified at T. The directory was used to find addresses; its current balances and yields were not imported into the financial snapshot. Factory pools, crypto factories and other venues remain outside this bounded sample.

The 28 addresses have **700 successful cash observations across 25 monthly points**, from the September 2024 baseline through September 2026. Missing data was not interpolated. Their aggregate custody is **133,133.569574 ETH** at the baseline and **67,988.170807 ETH** at September 2026. This history follows the same bounded address census. It is not the history of all LP capital, deposit flows or LP investor returns. Current discovery still creates a survivorship limitation.

The existing Liquid ETH NFTs separately quantify investor principal. At T, their active positions contain **6,585.543561 WETH** plus **289.981870 ETH-equivalent of weETH**, for **6,875.525431 ETH-equivalent total principal**. The two pools' WETH custody is **6,590.131118 WETH**. NFT principal sits inside pool custody, while the weETH side points back to staking backing. Neither is added again to the custody floor. Uncollected fees are not assumed to equal the difference between pool cash and NFT principal.

## Quantified reuse in the daily market panel

The frozen adapter panel contains **51 protocols with selected stETH or wstETH exposure**. In the default category selection, those receipt balances account for **$1.846478 billion**, or **682,824.439875 ETH at the relevant adapter-date reference prices**. Enabling the lending and CDP groups raises this recorded receipt exposure to **$10.145314 billion**, or **3,751,720.908317 ETH-reference**.

This is a measured set of repeated receipt exposure against Lido's issuer layer. It is not a complete overlap adjustment. Receipt marks differ from ETH principal, lender claims can include loaned units, some intermediate layers are nested, and the daily observations are not the exact-T RPC records. No subtraction has been applied to the canonical panel, and no claimed global net figure is produced from this table.

## Why native consensus remains open

The original collection captured a canonical finalized beacon header for slot **15,346,798**, including state root `0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282`. The new collection tried historical validator balances or validators by slot, epoch-boundary slot, state root and block root through public providers. Responses included unavailable states, forbidden endpoints and service errors.

Beaconcha.in's correctly formed historical epoch and ETH.STORE requests return **401 Unauthorized** without an API key. MigaLabs' daily effective-balance endpoint also requires a key. No credential request or paid purchase was made. ETH.STORE's [published methodology](https://www.beaconcha.in/ethstore) selects validators active throughout a reward day. Its effective/start/end balance fields would still need to be matched to their exact period and population before being used as a capital census.

The previously captured Ethereum.org widget shows 43,869,560 ETH staked, but has no usable timestamp for T. It remains context. The deposit contract's execution balance, validator count multiplied by 32, a current widget and an issuer's last oracle report are all different quantities from actual active-validator balances at T.

The unresolved native quantity therefore remains null. A complete global calculation still needs actual balances and statuses at T, validator ownership and withdrawal credentials, issuer-to-restaking links, all relevant liquid custody, and bridge escrow versus remote claims. The measured subset and its explicit liquid ceiling are usable now; the unexamined part has no numeric upper bound established by the available evidence.

## Reproduction and presentation rules

The website should consume [market_netting_closure.json](../../../data/eth/market_netting_closure.json). [market_netting_build.py](../../../tools/eth/market_netting_build.py) rebuilds it offline. Root nodes, LP monthly totals and per-pool history also have CSV exports. Every new capture records its URL, UTC collection time, response hash and immutable raw path in [the capture manifest](../../../raw/eth/research-closure-2026-10-04/market/requests.jsonl).

The presentation should retain five distinctions:

1. Reported adapter exposure is useful for distribution, but is not unique ETH.
2. Exact physical custody proves underlying backing in a bounded subset; idle balances remain possible.
3. Issuer oracle accounting is measured at T but can describe an earlier CL state.
4. Claims inside another measured balance are shown as links, never added as new roots.
5. The liquid ceiling excludes native consensus and broader custody. It is never presented as a global market bound.
