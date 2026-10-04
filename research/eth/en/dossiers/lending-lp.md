# Lending and liquidity provision

Snapshot T: 2 October 2026, 23:59:59 UTC. This dossier connects the broad protocol screen with verified ether.fi positions. It is not a complete borrower census across all chains.

## Lending capital and who pays the yield

Dated ETH-family observations are Aave V3 $9.835B, SparkLend $4.161B, Sky Lending $1.639B, Morpho Blue $1.422B, Compound V3 $724.582M and Fluid Lending $231.542M. These adapter balances mix underlying assets and receipt tokens. They cannot be added to staking issuers or managed-vault net asset value (NAV) without counting some capital twice.

Aave's subtotal includes substantial weETH, wstETH and rsETH collateral. It does not measure only ETH supplied to earn loan interest.

ETH lenders receive interest paid by borrowers. A useful approximation is `supply APR ≈ borrow APR × utilization × (1−reserve factor)`, excluding rewards and corrections for compounding. APR means annual percentage rate; utilization is the share of supplied capital borrowed, and the reserve factor is the share of interest retained by the protocol. Large idle cash balances can produce a near-zero supply yield.

[Aave's liquidity-pool documentation](https://www.aave.com/docs/aave-v3/concepts/liquidity-pool) connects withdrawals with unborrowed reserve liquidity. [Morpho interest accounting](https://docs.morpho.org/developers/borrow/concepts/interest-rates/) explains that interest is accrued when the market is updated. An independent NAV calculation must include accrued debt, rather than simply reading the last stored amount.

## Verified markets and borrower concentration

The five fixed-block WETH markets across four Aave chains and Spark contain 2.881M lender claims and 2.388M debt. Main Liquid ETH represents 23.28% of Aave Ethereum variable WETH debt. Reserve getters report approximately 52,964 WETH deficit on Ethereum and 29,835 on Arbitrum. These values do not establish final losses to depositors. See the [selected-market balance analysis](../LENDING-MARKETS.md).

Not all income on ETH collateral is loan interest. Analysis needs the loan asset, market, debt, rate, collateral and purpose of borrowing. ETH debt against liquid staking tokens (LSTs) often supports looping. Stablecoin debt against ETH can fund carry, leveraged ETH purchases, business needs or a cash withdrawal. Without verifying the destination of borrowed funds, strategy classification remains an inference.

## What the borrower scan covers

The current, post-T Morpho API scan covers 25 selected ETH-collateral markets with WETH or stablecoin loans. It examines ten large positions per market and returns 237 positions and 213 unique `(chain,address)` borrowers. This is a limited scan of the largest positions, without complete borrower pagination. ETH and stablecoin debt are separated; not every position is classified as carry.

The large wstETH/USDT borrower `0x7ee293…` is contract-linked to Concrete's shared Safe. Its current loan is approximately $70.395M. This connects borrowing demand to a managed portfolio, but does not allocate all Safe assets among its private vaults. Liquid ETH's material positions are independently checked at fixed blocks.

The Aave account scan covers only verified pilot manager accounts. A complete census using events or indexers, historical borrowers and repayment destinations has not been reconstructed. Coverage of the borrower scan is not a measure of the share of all carry strategies.

## Liquidity-provider income and changing inventory

Liquidity providers (LPs) earn trading fees and incentives while the tokens in their positions change. Correlated ETH and LST prices do not remove the risk of a receipt-token discount or trades against a mispriced pool.

Concentrated liquidity can become entirely one token when price moves outside its range, at which point it stops earning swap fees. [Uniswap's documentation](https://developers.uniswap.org/docs/get-started/concepts/liquidity-providers/concentrated-liquidity) explains this mechanism. Pool total value locked (TVL) differs from liquidity actively earning fees, and virtual reserves are not external assets.

Liquid ETH NFTs 1363661 and 1363660 have token0=WETH, token1=weETH and fee tiers 500/100. Principal calculated from `sqrtPrice`, ticks and issuer conversion is 6,875.525431 ETH-equivalent, approximately $18.344M. Uncollected fee growth is excluded. Three older NFTs have zero liquidity. An inventory of ERC20 balances alone would miss this capital.

Fluid NFT 4241 / vault 74 holds smart collateral in weETH/native ETH and wstETH debt. Net equity is approximately 3,073.874326 ETH-equivalent, or $8.201M. The calculation uses the position's proportional share of **real** reserves, checks packed supply shares through the resolver and subtracts debt. Adding imaginary reserves, gross smart collateral and book NAV would count the same exposure more than once.

Current interface weights are 4.05% Uniswap LP and 1.81% Fluid LP. These observations are after T. They do not reconstruct amounts at fixed blocks or represent the whole LP market.

## Fees, controls and exit capacity

Net lending and LP returns depend on protocol reserves or curator fees, trading costs, incentives and losses. This screen does not provide a complete historical fee or governance ledger for every venue.

Available borrowing cash, executable decentralized-exchange (DEX) depth and issuer redemption throughput need separate measurement. A loop must obtain the debt asset before collateral can be released. An LP exit may return a less-liquid receipt token rather than ETH. Borrow-rate increases, collateral-oracle reductions and DEX discounts therefore require separate stress scenarios.

## What remains open

NFT calls, pool identities and resolver state: `data/eth/pilot_more_T.json`, `etherfi_uniswap_positions.json`, `fluid_pilot_decoded.json`. Borrowers: `morpho_borrower_screen.json`.

Aggregate ETH-side LP principal across major chains remains uncomputed. The discovery total for mixed-asset pools does not measure it. A full borrower census and market-wide exit simulation also remain open.
