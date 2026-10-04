# Staking and restaking

Snapshot T: 2 October 2026, 23:59:59 UTC. Staking and restaking sit beneath many lending, principal-token (PT) and managed-vault positions. Their capital overlaps with those downstream products.

## Where the income comes from

Native staking earns Ethereum protocol issuance, execution tips and maximal extractable value (MEV), after operating costs, commissions and penalties. A liquid staking token (LST) changes how an investor holds a claim on validator backing. It does not create a second, independent source of staking income. [Ethereum staking](https://ethereum.org/staking/) explains the mechanism.

The balance of the execution-layer deposit contract is not a substitute for the active balance recorded by the consensus layer. The Ethereum.org page captured on 3 October displays 43,869,560 ETH staked. Its widget does not provide a usable timestamp for the state at T, and another web cache shows a different current value. This is a reference for market scale, **not a verified total at T**.

Finalized header slot 15,346,798 was obtained, but public endpoints did not restore the full historical state by slot or root. Multiplying validator count×32 is unsuitable when balances compound and validators exit.

## What restaking adds

Restaking commits collateral to external services in addition to staking. Service rewards, validator income and token incentives need separate accounting. One ETH securing several services is counted once as unique underlying capital. It is counted repeatedly only when describing the separate obligations it secures.

The [EigenLayer whitepaper](https://docs.eigencloud.xyz/assets/files/EigenLayer_WhitePaper-88c47923ca0319870c611decd6e562ad.pdf) describes native and LST architecture. It does not establish current revenue from actively validated services (AVS), payable rewards, or the slashing rules permitted for individual services.

## Largest dated observations

These API token-history observations are predominantly dated 2 October, 00:00 UTC. The rows overlap and are not summed.

| Protocol | ETH-family USD, billions | Interpretation |
|---|---:|---|
| Lido | 26.677 | Backing accounting; downstream receipt deployment repeats this capital |
| Binance Staked ETH | 10.081 | Issuer disclosure and adapter data, not an independent custody audit |
| EigenCloud | 7.075 | Native restaking and LST claims overlap with staking |
| ether.fi Stake | 5.188 | Staking and restaking layer, separate from Liquid ETH |
| Rocket Pool | 1.409 | Staking backing and receipt-token economy |
| Kelp | 1.130 | Material stETH/ETHx backing; overlaps with Lido/Stader |
| StakeWise V3 | 1.017 | Staking vaults and osETH collateralization need separate accounting |
| mETH Protocol | 0.637 | Ethereum validators and Mantle token circulation describe different locations |
| Coinbase cbETH | 0.517 | Receipt backing; cbETH does not include all Coinbase staking products |
| Stader | 0.233 | ETHx underlying used by downstream products |

EigenCloud's adapter uses virtual WETH to represent native stake. This is not liquid WETH held in an execution wallet. Kelp's stETH/ETHx holdings cannot be added again to the underlying capital attributed to Lido/Stader.

Dated rows and hashes: `data/eth/protocol_eth_observations.json`.

## Receipt conversion and return benchmarks

stETH rebases: the number of units grows. wstETH units stay fixed while the amount of stETH represented by each token grows. The [wstETH contract](https://docs.lido.fi/contracts/wsteth/) defines the conversion; this comparison uses historical `stEthPerToken` calls. weETH conversion comes directly from fixed-block `getRate()`.

Over 730 days, stETH-equivalent growth is 5.4875% and weETH growth is 5.2947%, excluding separately distributed rewards. A conversion quote does not prove that the token can be sold or withdrawn at that price.

## How investors exit

Investors may use protocol withdrawal queues, secondary markets or, after an incident, recovery procedures. [Ethereum withdrawals](https://ethereum.org/staking/withdrawals/) distinguish legacy and compounding validators. Receipt-token queues can add further waiting time.

Liquid ETH's finalized but unclaimed Lido withdrawal NFT 122235 represents 25.069520 ETH. It is a withdrawal claim, not an additional active staking position. Fees, control rights and exit conditions vary by issuer; the aggregate observations do not verify them for every product.

## rsETH shows why chain-specific redemption matters

The 18 April 2026 incident involved 116,500 rsETH, approximately $292M in the party's published estimate. [LayerZero's 20 May report](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report) attributes the forged message to compromised RPC infrastructure and a single-DVN configuration. A DVN is a decentralized verifier network used in bridge-message verification. This is the report author's attribution, not an independent determination of responsibility.

[Kernel's 19 June publication](https://blogs.kerneldao.com/blog/recovering-rseth-from-sunset-networks) describes the end of bridging from 15 June on 20 chains, including Optimism and Monad. Quarterly recovery continues to June 2027, with a 100 USDC fee per address. The author's statement that Ethereum L1 backing remains intact was not independently verified.

Historical `rsETHPrice()` or `paused=false` on L1 does not prove that holders on another chain can withdraw promptly. A common ETH accounting asset still requires a separate redemption analysis for each chain. No recovery transactions, burns or payments are executed in this research.

## What remains open

Remaining checks include historical consensus state, issuer reserve reconciliation, AVS reward events, reward recipients, realized slashing or credit losses, and complete bridge inventory. Current total value locked (TVL) does not establish AVS revenue. Points enter verified income only when realized as cash.
