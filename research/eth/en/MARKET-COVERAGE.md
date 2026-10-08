# Coverage of the ETH yield market

Financial snapshot: **2 October 2026**. What the counted-once map includes, what it lists without counting, and what it leaves out. Map total: **15,920,754 ETH** in 133 products (products holding at least $50k at the snapshot, the BTC map's listing threshold; 64 ETH in smaller rows stays in the total).

## By category

| Category | ETH counted | How it is counted | Not counted |
| --- | --- | --- | --- |
| Staking | 11,901,177 | Staked and held, not used anywhere else: issuer backing (DefiLlama token breakdown; cbETH from on-chain supply) less every staking token posted in a lending market (5.48M ETH) or held by another counted product | About 14.4M ETH staked off-chain (listed); beacon chain 43.81M ETH active is the ceiling |
| Restaking | 411,377 | Restaking-token issuers on the same rule (weETH 1.83M and rsETH 0.39M sit in lending markets); EigenLayer and Symbiotic only for what no restaking token or other product (Cap, Vesper) counts (estimate) | Points and AVS rewards are not in the size |
| Leveraged staking | 2,885,012 | Staked ETH looped against borrowed ETH on lending markets, private and product: cells A1+B1 of the lending split (2,913,878 ETH, collateral counted once, lent-out WETH not added) less 28,866 ETH of product shares (tETH, savETH, weETHs) that their products count. Equity about 313k ETH. Split by venue ETH debt | Loop vaults (Fluid Lite, Treehouse, CIAN, Origami, Index Coop) count 0: their positions are inside this total |
| Carry | 171,649 | Only the part of products open for deposits where ETH is collateral for a dollar loan, read account by account at block 26,108,081: 12 products, $270.9M of dollar debt. YieldBasis and Liquity ETH Carry whole books | Loops, idle tokens and other strategies of the same products (see the table below); Concrete Delta (313k ETH) and three rSHARE vaults (about 83k WETH): private mandates, not products |
| Fixed yield | 9,203 | ETH-family assets held by Pendle, Tranchess and other yield-splitting protocols (behind both principal and yield tokens); the staking tokens leave their issuers | Expired markets count only their residual; tETH inside Pendle is counted in leveraged staking |
| Basis, options, credit | 28,718 | Protocol token series; credit counts what is supplied, lent-out ETH included (Wildcat, Native, Maple), as in the BTC map. Cap is slashable cover for loans to named market makers (like Lombard's LBTC cover on Cap in BTC): its 22,679 ETH sits in Symbiotic vaults filled by Vesper, ether.fi weETHs, StakeStone and Mellow, so it is counted once, in Cap, and taken out of those rows. All four checked on-chain at the snapshot ([CREDIT-CHECK](CREDIT-CHECK.md)) | Exchange margin and CeFi lenders (no ETH balances published) |
| Farming and pools | 513,618 | DEX, perp and bridge pools: the ETH side no other row counts (staking and product tokens in a pool stay with their issuer); DEX token breakdowns, or pools above $1M where a DEX has none. Managed vaults and points programmes | Vaults that only lend WETH (in money markets) and vaults that hold DEX positions (Beefy, AUTOfinance, Convex and others; counted in the pools). History of the above-$1M pool sets covers only pools that still exist |
| Money markets (off) | 3,231,215 | ETH and staking tokens posted in lending markets outside loops and carry products (cells A2 to A4 and B2 to B4 of the lending split, 3,384,075 ETH, less 155,293 ETH of the carry products' own positions, plus 2,688 ETH in Seamless outside the split's basis, less 257 ETH of Superform shares that Pendle counts): mostly collateral for dollar loans by unknown wallets, and plain WETH not lent out. Off by default, as in the BTC map | Lent-out WETH (2.69M ETH) is not added: it is the other side of the loops. spETH (WETH lent into SparkLend) is not added again |
| CDP collateral (off) | 765,192 | ETH posted to mint stablecoins | Off by default. Staking tokens posted in a CDP count here and leave their issuer, like those in lending markets |

Before 8 October the map counted staking tokens in lending markets at their issuers (staking 15,093,012, restaking 2,435,229), only loop vaults as leveraged staking (97,793), whole carry books (305,908) and only plain WETH as money markets (812,124); the total was 18,499,055 ETH in 131 products.

## Staking: on-chain, off-chain and the beacon chain

The beacon chain holds **43.81M ETH** of active stake at T (slot 15,346,798). The map counts the on-chain part once: 11.90M ETH staked and held and 0.42M restaked and held; 5.48M ETH of staking tokens sit in lending markets and are counted there (leveraged staking, carry, money markets). About 14.4M ETH is staked off-chain (exchanges 4.6M, institutional providers 4.7M, BitMine 5.1M) and is listed but not counted. The remaining 11.50M ETH (solo and untagged validators, and staking tokens held inside other map rows) is not split further. [Off-chain stake](OUTSIDE-AND-SMALL.md), [staking and restaking](dossiers/staking-restaking.md).

## Lending markets: one split, three categories

| Cell (lending split, counted once, long tail included) | ETH | Goes to |
| --- | --- | --- |
| A1 + B1: staking tokens or ETH against borrowed ETH | 2,913,878 | Leveraged staking (less 28,866 of product shares) |
| A2 + B2: against dollars | 3,164,169 | Carry for the 12 products' own accounts (155,209), money markets for the rest |
| A3 + B3: against other assets | 26,755 | Money markets |
| A4 + B4: no debt, or supply not lent out | 193,151 | Money markets (TAU InfiniFi's 82 ETH: farming, outside carry) |

Staking tokens leave their issuers wherever they sit in a lending market: Lido 2.97M ETH, ether.fi 1.83M, Kelp 0.39M, StakeWise 0.13M, Coinbase 0.09M, Rocket Pool 0.05M.

## Two years of history

The same rules apply at every month-end from October 2024; what is measured and what is estimated:

- **Staking tokens and plain ETH in lending markets**: DefiLlama token breakdowns of the lending rows each month (the lending split's basis at the snapshot).
- **Leveraged staking**: estimate. Month-end ETH debt (Aave Core, Prime and Spark on-chain; every other market and chain from DefiLlama's borrowed WETH) times the snapshot ratio of loop collateral to ETH debt (1.070; the measured loop accounts hold 1.119 ETH of collateral per ETH of debt, the rest of the ETH debt is not loops). From 2.25M ETH in October 2024 to a peak of 4.28M in January 2026, 2.88M at the snapshot.
- **Carry**: measured. Collateral and dollar debt of each product's accounts at each month-end block (archive reads: ether.fi Liquid, Lido Earn, Avant on Aave v3, Spark, Aave v4 and Morpho, NEMO, Sentora, Makina, Royco, TAU, Vesper, Reservoir, Rocksolid's second wallet); WETH collateral counts less the part its market lends out. Estimates: Rocksolid in March 2026 (loan on Aave, collateral at the snapshot loan-to-value) and Avant's WETH share (snapshot ratio). A product counts only in months it owes at least $10k. Peak 168,609 ETH in September 2026; 26,933 in August 2025 when Liquid ETH first borrowed dollars.
- **Money markets**: lending-market ETH less loops less the carry products' positions. In nine months from May 2025 to April 2026 DefiLlama shows more staking tokens in lending markets than their issuer backs (ether.fi up to 371k ETH, Kelp up to 73k); the excess (at most 227k ETH, December 2025) is taken out of money markets so nothing is counted twice. Range 2.31M (April 2026, a DefiLlama dip in plain WETH) to 3.65M (November 2025).
- **Staking** rose from 9.59M to 11.90M ETH; **restaking** fell from 2.51M to 0.42M as weETH and rsETH moved into lending markets.

## Left out with a reason (largest)

| Row | ETH | Why |
| --- | --- | --- |
| SSV Network | 5,252,428 | Validator infrastructure (distributed validators). The ETH belongs to the staking providers that run on it, counted at their issuers. |
| JustLend V1 | 485,732 | ETH token on Tron. Ethereum backing and redemption not verified. |
| Concrete | 352,622 | Concrete Delta weETH (313k ETH) is one principal's own position, not a pooled product: a Bitfinex-linked wallet moved its Aave position into the vault's Safe on 10 Dec 2025 and holds 100% of the shares; it borrows $176M of stablecoins against it. ctwstETH+ (45k ETH) is that Safe's own circular holding. Excluded like Avalon in the BTC map; its weETH collateral is counted in money markets. |
| Obol | 326,760 | Validator infrastructure (distributed validators); the ETH is counted at the staking providers. |
| Nonce Capital | 177,171 | Curator of ether.fi Liquid ETH; counted once as Liquid ETH. |
| ether.fi Liquid | 148,834 | Same ether.fi Liquid vaults as the Veda row; counted once there (Liquid ETH on-chain, the rest as Veda). |

Full list: Data, Listed but not counted, on the site; [netting ledger](../../../data/eth/netmap/netting_ledger.csv).

## Counting rules

The same rules apply at the snapshot and at every month-end from October 2024.

- **Once, where it is used.** A staking token, or the token of another product on the map (egETH, weETHs, Mellow LRTs, ETH+, agETH and others), held by a counted product or posted in a lending market leaves the row that issued it. Tokens of the carry products and of loop vaults (tETH) held elsewhere are not counted again.
- **Lending markets.** Loops (staking tokens or ETH against borrowed ETH) are leveraged staking; the carry products' collateral against dollar loans is carry; everything else is money markets. Collateral counts once and lent-out WETH is not added, as in the lending split.
- **Carry** is only the part of a product's book that is ETH collateral for a dollar loan, in months with at least $10k of dollar debt. Its loops are leveraged staking, staking tokens it just holds stay with their issuer, lending collateral that backs no loan goes to its base category; the whole book still replaces the DefiLlama row that lists the product.
- **Pools count only what no other row counts.** The staking-token side of an ETH/LST pool stays with the issuer, as in the BTC map; the WETH in YieldBasis' Curve pool stays with YieldBasis.
- **Vaults booked in their base asset.** The Veda adapter books ether.fi Liquid vaults as WETH; the eETH inside them (less the Liquid ETH book) leaves ether.fi Stake, as the BTC map cut Veda by Lombard's LBTCv.
- **Restaking platforms** count only what no restaking-token issuer or other product counts; positions of Cap and Vesper in Symbiotic vaults are the smaller of the two balances each month.
- **Leftovers.** Rows on a reviewed list whose own balance is flat (under 0.5% change) for three month-ends count as zero from the start of the run, and take nothing from the issuers of the tokens they hold.
- **Prices.** USD values are DefiLlama's at each point (the 3 October 00:00 UTC point for the snapshot, 00:00 UTC on the 1st for month-ends), converted at the ETH price of the same point; staking tokens count at their ETH value.

Known gap: map products other than the carry and loop products (vaults in farming, credit) may post some of the staking tokens they hold in lending markets; those positions are not separated from the lending cells.

## Nothing large missed

DefiLlama's yields page lists 603 ETH pools above $1M. 97.1% of their TVL belongs to products on the map and 2.9% to rows left out for a stated reason; the rest ($27M) is pools under 100 ETH. The 299 ETH-name pools above $5M in the carry screen: 224 belong to a product already counted, the other 75 have a written decision ([CARRY-COVERAGE-AUDIT](CARRY-COVERAGE-AUDIT.md)).

## Carry products and status

| Product | Dollars borrowed | Loan rate | Whole book, ETH | Carry, ETH | Rest of the book | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ether.fi Liquid ETH | $181.1M | 7.79% | 177,171 | 115,864 | weETH loop on Aave, Spark and Fluid (481,697 ETH collateral, 441,802 WETH debt) in leveraged staking; about 21k held | Top five |
| YieldBasis WETH | $27.8M | 10.00% | 10,426 | 10,426 | none | Top five |
| Lido Earn ETH | $25.6M | 4.33% | 83,309 | 25,029 | stRATEGY loops (391,734 ETH collateral, 355,164 WETH debt) in leveraged staking; about 21k held | Top five |
| Avant avETH / savETH | $19.7M | 6.30% | 12,583 | 7,493 | 4,747 ETH of its WETH collateral is lent out by the markets (counted with the borrowers) | Top five |
| Liquity ETH Carry | $6.8M | 2.55% | 6,014 | 6,014 | none | Top five |
| NEMO ETH Prime | $5.6M | 4.75% | 3,038 | 2,965 | 72 WETH idle in the vault | Live; vault book reconciles with the loan |
| Rocksolid rETH | $2.7M | 4.61% | 9,728 | 2,728 | ETH loops on Ethereum, Monad and Spark (6,950 ETH collateral) in leveraged staking; Steakhouse Prime ETH and Liquity ETH Carry shares counted in those products | Closed 29 Sep, reopened 7 Oct |
| Sentora ETH | $1.2M | 11.79% | 677 | 655 | 22 idle | Live; vault book reconciles with the loans |
| Makina DETH | $385k | 3.21% | 2,499 | 348 | weETH loop on Aave (16,695 ETH collateral, 15,065 WETH debt) in leveraged staking | Live; mostly a weETH loop |
| Royco ETH | $91k | 30.24% | 116 | 116 | none | Live; parent marks stale, no immediate exit |
| Vesper vaETH | $69k | 5.00% | 1,052 | 9 | 57 WETH on Aave, 48 of it lent out by Aave; other strategies where they sit | Live; dollar leg trails its loan |
| Reservoir ETH Yield | $37k | 13.93% | 24 | 3 | 21 WETH on Aave, 18 of it lent out by Aave | Emptied after a 2025 peak |
| TAU InfiniFi ETH Carry | dust | - | 82 | 0 | 82 ETH of wstETH on Morpho without a loan (farming) | Unwound; 0.02 USDC of debt at T |

Avant's monthly debt history in the economic census covers Aave v3 and Spark; the map also reads its Aave v4 and Morpho loans each month (Morpho from May 2026, Aave v4 from September 2026).

## Supporting research

[Team briefing](BRIEFING.md), [market structure](MARKET-STRUCTURE.md), [carry category](CARRY-CATEGORY.md), [lending split](LENDING-SPLIT.md), [off-chain and small categories](OUTSIDE-AND-SMALL.md), [Concrete Delta](CONCRETE-DELTA.md), [private mandates](BORROWER-IDENTITIES.md).
