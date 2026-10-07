# Coverage of the ETH yield market

Financial snapshot: **2 October 2026**. What the counted-once map includes, what it lists without counting, and what it leaves out. Map total: **18,542,591 ETH** in 144 products.

## By category

| Category | ETH counted | How it is counted | Not counted |
| --- | --- | --- | --- |
| Staking | 15,016,520 | Issuer backing (DefiLlama token breakdown), net of staking tokens held by other products | About 14.4M ETH staked off-chain (listed); beacon chain 43.81M ETH active is the ceiling |
| Restaking | 2,427,324 | Restaking-token issuers; EigenLayer and Symbiotic only for what no restaking token counts (estimate) | Points and AVS rewards are not in the size |
| Leveraged staking | 97,144 | Loop vaults (Fluid Lite, Treehouse, CIAN and others) | Loops inside Liquid ETH, Lido Earn and Makina stay in those products |
| Carry | 305,908 | On-chain books and loans at block 26,108,081: 12 products, $261.3M of dollar debt | Concrete Delta (307k ETH) and three rSHARE vaults (about 83k WETH): private mandates, not products |
| Fixed yield | 9,315 | Pendle and Spectra principal tokens on ETH-family assets | Expired markets count only their residual |
| Basis, options, credit | 26,315 | Protocol token series | Exchange margin and CeFi lenders (no ETH balances published) |
| Farming and pools | 660,066 | DEX ETH pools above $1M (plain-ETH side), managed vaults, points programmes | History covers only pools that still exist |
| Money markets (off) | 786,904 | Idle WETH no product counts | Off by default: lent ETH is staked again by borrowers |
| CDP collateral (off) | 657,327 | ETH posted to mint stablecoins | Off by default: the collateral earns nothing |

## Staking: on-chain, off-chain and the beacon chain

The beacon chain holds **43.81M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: 15.02M ETH of staking and 2.43M ETH of restaking, after removing staking tokens held by other products. About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. The remaining 11.96M ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. [Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).

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

## Nothing large missed

DefiLlama's yields page lists 603 ETH pools above $1M. 97.3% of their TVL belongs to products on the map and 2.7% to rows left out for a stated reason; the rest ($27M) is pools under 100 ETH. The 299 ETH-name pools above $5M in the carry screen: 224 belong to a product already counted, the other 75 have a written decision ([CARRY-COVERAGE-AUDIT](CARRY-COVERAGE-AUDIT.md)).

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
