# ETH yield research scope

Research began on 3 October 2026. The core market consists of products that accept ETH or a claim on ETH and preserve ETH exposure or deliver returns measured in ETH. Hedged dollar products are studied separately because their exposure differs. Every amount has a date; unmeasured amounts remain unavailable.

## Snapshot and history

Target snapshot: 2 October 2026, 23:59:59 UTC. On-chain observations use the last block no later than T, checking the next block. History covers 24 completed months, October 2024 to September 2026, plus a separate snapshot. Later APIs/interfaces belong to discovery and do not replace T.

## Capital and products

A product is a claim available to outside investors, with an identifiable issuer, mechanism and contract addresses. A protocol, token, lending market and portfolio component can each describe a different part of the same product. Private wallets and treasury trades are tracked separately from products accepting investor deposits.

Publish three measures: unique underlying ETH, external investor equity and gross deployment. A total of protocol or pool TVL is not market size. The ownership and debt map removes repeated internal claims while retaining the claims of outside lenders.

## Chains

The required first group is Ethereum, including its validator state, Base, Arbitrum and Optimism. Other chains are screened for ETH-related capital. A chain merits deeper work if it accounts for at least 1% of discovered gross deployment, has $25M in relevant capital, contains a $5M product or credit position, or is a critical dependency. These are selection rules, not claims that every selected chain has been fully reconstructed.

Track four locations separately: where ETH is backed, where shares circulate, where collateral and debt sit, and where strategy assets are deployed. Count equity once in any table that adds capital. Leave unsupported geographic splits unallocated.

## Discovery thresholds

The plan calls for detailed product work at $5M of current capital or a $20M historical peak. A carry or loop component qualifies at $1M, or when it introduces an important mechanism, incident or dependency. Borrower discovery starts at $1M debt, with identification priority at $5M. The thresholds determine research depth; smaller observations remain in the catalogue.

## Returns and comparison

The main investor result is ETH after fees. Also show dollar value, ETH price exposure, and gross and net returns where evidence allows. Compare each strategy with holding ETH and simple staking over the same dates. Separate staking, tips and MEV, paid security services, strategy income, debt interest, incentives and costs. Points count as realized income only after verified receipt of their value.

## Sources and limits

Primary contracts/events, official registries and published reports establish identity and mechanics. Aggregators support discovery and scale checks. Preserve raw URL, capture time, parameters and SHA256. Every amount has a date and verification status. Coverage refers to the discovered measurable universe.
