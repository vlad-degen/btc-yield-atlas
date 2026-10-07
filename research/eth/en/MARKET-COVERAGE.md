# Coverage of the ETH yield market

Financial snapshot: **2 October 2026**. What the counted-once map includes, what it lists without counting, and what it leaves out. Map total: **18,499,055 ETH** in 131 products (products holding at least $50k at the snapshot, the BTC map's listing threshold; 61 ETH in smaller rows stays in the total).

## By category

| Category | ETH counted | How it is counted | Not counted |
| --- | --- | --- | --- |
| Staking | 15,093,012 | Issuer backing (DefiLlama token breakdown; cbETH from on-chain supply), net of staking tokens held by other products | About 14.4M ETH staked off-chain (listed); beacon chain 43.81M ETH active is the ceiling |
| Restaking | 2,435,229 | Restaking-token issuers; EigenLayer and Symbiotic only for what no restaking token or other product (Cap, Vesper) counts (estimate) | Points and AVS rewards are not in the size |
| Leveraged staking | 97,793 | Loop vaults (Fluid Lite, Treehouse, CIAN and others) at depositor equity; Treehouse at gross collateral, Origami and Index Coop scaled by their equity share at T | Loops inside Liquid ETH, Lido Earn and Makina stay in those products |
| Carry | 305,908 | On-chain books and loans at block 26,108,081: 12 products, $270.9M of dollar debt | Concrete Delta (307k ETH) and three rSHARE vaults (about 83k WETH): private mandates, not products |
| Fixed yield | 9,287 | ETH-family assets held by Pendle, Tranchess and other yield-splitting protocols (behind both principal and yield tokens); the staking tokens leave their issuers | Expired markets count only their residual |
| Basis, options, credit | 28,773 | Protocol token series; credit counts what is supplied, lent-out ETH included (Wildcat, Native, Maple), as in the BTC map | Exchange margin and CeFi lenders (no ETH balances published) |
| Farming and pools | 529,052 | DEX, perp and bridge pools: the ETH side no other row counts (staking and product tokens in a pool stay with their issuer); DEX token breakdowns, or pools above $1M where a DEX has none. Managed vaults and points programmes | Vaults that only lend WETH (in money markets) and vaults that hold DEX positions (Beefy, AUTOfinance, Convex and others; counted in the pools). History of the above-$1M pool sets covers only pools that still exist |
| Money markets (off) | 812,124 | Plain WETH in lending markets (collateral and supply not lent out) and vaults that only lend WETH (Yearn, Harvest, YO, Superform, Spark Savings) | Off by default: lent ETH is staked again by borrowers. Positions of other map products inside the markets are not taken out (the BTC map does), so this is an upper bound |
| CDP collateral (off) | 657,327 | ETH posted to mint stablecoins | Off by default: the collateral earns nothing |

## Staking: on-chain, off-chain and the beacon chain

The beacon chain holds **43.81M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: 15.09M ETH of staking and 2.44M ETH of restaking, after removing staking tokens held by other products. About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. The remaining 11.88M ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. [Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).

## Left out with a reason (largest)

| Row | ETH | Why |
| --- | --- | --- |
| SSV Network | 5,252,428 | Validator infrastructure (distributed validators). The ETH belongs to the staking providers that run on it, counted at their issuers. |
| JustLend V1 | 485,732 | ETH token on Tron. Ethereum backing and redemption not verified. |
| Concrete | 352,622 | Concrete Delta weETH (307k ETH) is one principal's own position, not a pooled product: a Bitfinex-linked wallet moved its Aave position into the vault's Safe on 10 Dec 2025 and holds 100% of the shares; it borrows $176M of stablecoins against it. ctwstETH+ (45k ETH) is that Safe's own circular holding. Excluded like Avalon in the BTC map; the weETH stays counted at ether.fi. |
| Obol | 326,760 | Validator infrastructure (distributed validators); the ETH is counted at the staking providers. |
| Nonce Capital | 177,171 | Curator of ether.fi Liquid ETH; counted once as Liquid ETH. |
| ether.fi Liquid | 148,834 | Same ether.fi Liquid vaults as the Veda row; counted once there (Liquid ETH on-chain, the rest as Veda). |

Full list: Data, Listed but not counted, on the site; [netting ledger](../../../data/eth/netmap/netting_ledger.csv).

## Counting rules

The same rules apply at the snapshot and at every month-end from October 2024.

- **Once, at the outermost product.** A staking token, or the token of another product on the map (egETH, weETHs, Mellow LRTs, ETH+, agETH and others), held by a counted product leaves the row that issued it. Tokens of the on-chain carry books stay in the book.
- **Pools count only what no other row counts.** The staking-token side of an ETH/LST pool stays with the issuer, as in the BTC map; the WETH in YieldBasis' Curve pool stays with YieldBasis.
- **Vaults booked in their base asset.** The Veda adapter books ether.fi Liquid vaults as WETH; the eETH inside them (less the Liquid ETH book) leaves ether.fi Stake, as the BTC map cut Veda by Lombard's LBTCv.
- **Restaking platforms** count only what no restaking-token issuer or other product counts; positions of Cap and Vesper in Symbiotic vaults are the smaller of the two balances each month.
- **Leftovers.** Rows on a reviewed list whose own balance is flat (under 0.5% change) for three month-ends count as zero from the start of the run, and take nothing from the issuers of the tokens they hold.
- **Equity, not gross.** Products count what their depositors own; on-chain books replace DefiLlama rows for the carry products.
- **Carry** counts only in months with at least $10k of dollar debt; other months go to the category the product worked in.
- **Prices.** USD values are DefiLlama's at each point (the 3 October 00:00 UTC point for the snapshot, 00:00 UTC on the 1st for month-ends), converted at the ETH price of the same point; staking tokens count at their ETH value.

## Nothing large missed

DefiLlama's yields page lists 603 ETH pools above $1M. 97.2% of their TVL belongs to products on the map and 2.8% to rows left out for a stated reason; the rest ($27M) is pools under 100 ETH. The 299 ETH-name pools above $5M in the carry screen: 224 belong to a product already counted, the other 75 have a written decision ([CARRY-COVERAGE-AUDIT](CARRY-COVERAGE-AUDIT.md)).

## Carry products and status

| Product | Dollars borrowed | Loan rate | Whole book, ETH | Status |
| --- | --- | --- | --- | --- |
| ether.fi Liquid ETH | $181.1M | 7.79% | 177,171 | Top five |
| YieldBasis WETH | $27.8M | 10.00% | 10,426 | Top five |
| Lido Earn ETH | $25.6M | 4.33% | 83,309 | Top five |
| Avant avETH / savETH | $10.0M | 6.30% | 12,583 | Top five |
| Liquity ETH Carry | $6.8M | 2.55% | 6,014 | Top five |
| NEMO ETH Prime | $5.6M | 4.75% | 3,038 | Live; vault book reconciles with the loan |
| Rocksolid rETH | $2.7M | 4.61% | 9,728 | Closed 29 Sep, reopened 7 Oct |
| Sentora ETH | $1.2M | 11.79% | 677 | Live; vault book reconciles with the loans |
| Makina DETH | $385k | 3.21% | 2,499 | Live; mostly a weETH loop |
| Royco ETH | $91k | 30.24% | 116 | Live; parent marks stale, no immediate exit |
| Vesper vaETH | $69k | 5.00% | 1,052 | Live; dollar leg trails its loan |
| Reservoir ETH Yield | $37k | 13.93% | 24 | Emptied after a 2025 peak |
| TAU InfiniFi ETH Carry | dust | - | - | Unwound; 0.02 USDC of debt at T |

## Supporting research

[Team briefing](BRIEFING.md), [market structure](MARKET-STRUCTURE.md), [carry category](CARRY-CATEGORY.md), [off-chain and small categories](OUTSIDE-AND-SMALL.md), [Concrete Delta](CONCRETE-DELTA.md), [private mandates](BORROWER-IDENTITIES.md).
