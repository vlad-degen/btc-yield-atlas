# Dollar lending inside an ETH vault

The [final capital, income and exit findings](../CAPITAL-INCOME-EXIT.md) extend this original reconstruction with dated cash flows, public backing and investor payout evidence. Original partial-reconstruction figures retain their original scope.


Published 3 October 2026. Contract balances are measured at T, 2 October, 23:59:59 UTC. This dossier examines the dollar investments inside Liquid ETH, rather than ranking the entire dollar-product market.

## What Liquid ETH owns

Liquid ETH borrows dollars against ETH-related collateral and invests in dollar products as part of its carry strategy. A carry strategy earns the spread between the return on the investment and the cost of the borrowing. To understand that spread, the analysis must trace the external vaults to their final borrowers and collateral.

| Contract | Book assets | Liquid ETH claim | Share of book assets |
|---|---:|---:|---:|
| senRLUSDv2 `0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf` | 444.242M RLUSD | 55.105M RLUSD | 12.40% |
| senPYUSDPRIMEv2 `0xc21b08c16458202593d4d9b26b9984ee67b38bbd` | 219.084M PYUSD | 49.605M PYUSD | 22.64% |

Both use Morpho Vault V2 with one MorphoMarketV1AdapterV2. The adapter connects the vault to its lending markets. `parentVault`, market IDs, supply shares and market parameters were checked at T.

RLUSD has 18 decimals and PYUSD has 6; both vault shares have 18. One senPYUSDPRIMEv2 share represents approximately 2.02486 PYUSD. Assuming one share=$1 would understate its value.

## Where the dollars are lent

| senRLUSDv2 market | Approximate share of total book assets |
|---|---:|
| kBTC/RLUSD | 52.89% |
| weETH/RLUSD | 24.09% |
| USDe/RLUSD | 7.23% |
| cbBTC/RLUSD | 2.99% |
| FXRP/RLUSD | 1.92% |
| syrupUSDC/RLUSD | 1.11% |
| wstETH/RLUSD | 0.31% |

The remainder includes idle or unallocated assets and smaller positions. It has not been verified as a fully liquid withdrawal buffer. Collateral metadata was checked with calls to the specific contracts. kBTC `0x73e0…` and syrupUSDC `0x80ac…` are different collateral assets.

Approximately 95.04% of senPYUSDPRIMEv2 book assets is allocated to PRIME/PYUSD. Stored utilization, the share of supplied capital borrowed, is approximately 91.80%. It is approximately 88.34% in weETH/RLUSD and 90.32% in kBTC/RLUSD. At these levels, all lenders cannot be assumed to withdraw at once without borrower repayment.

## Who pays the income and bears the risk

Lending income comes from borrower interest after curator fees and any losses. PRIME adds exposure to real-world credit. [Sentora's case study](https://sentora.com/case-studies/sentora-s-prime-main-vault-reaches-200m-in-pyusd-deposits-in-under-100-days) describes financing loan originators between the issuance of home-equity loans and securitization.

Stablecoin lenders bear the risk of the PRIME collateral and its liquidation. PRIME holders bear the underlying credit risk and the risk that repayment takes longer than expected. These exposures are connected, but they are different claims.

At T, performance fees are 10% for RLUSD and 15% for PRIME. Management fees are zero for both. These fees are charged within the external vaults, below the ETH wrapper. Do not subtract them again if net price per share (PPS) already reflects them.

## When the portfolio lends back to itself

Liquid ETH invests through supply vaults while its main account and LoanManager borrow in some of the same markets. At T, adapter supply shares represent almost all supply in weETH/RLUSD and PRIME/PYUSD.

Applying Liquid ETH's ownership fraction in the external vaults gives approximately 8.709M RLUSD and 4.759M PYUSD of indirect self-credit. This is the portion of lending principal economically attributable to a portfolio that also controls the borrower.

The calculation combines vault ownership, the adapter's share of market supply and controlled borrower debt, using stored market ratios. Later interest accrual is excluded. It measures principal relationships, not monthly revenue. Interest transferred within the consolidated portfolio does not create new economic income. Independent income must come from external borrowers or credit investments, after debt costs, fees and losses.

## Cap and the unresolved Yuzu allocation

Liquid ETH's separate STCUSD claim represents 24.626M cUSD. [Cap mechanics](https://docs.cap.app/overview/protocol-overview/stcusd-mechanics) connect its income to borrower payments, yield on idle reserves and Underwriter security. Assessing coverage requires available collateral, the procedures for slashing or realizing it, and claims that rank ahead of the investor. A token conversion rate does not verify that coverage.

The interface also names Yuzu. Its specific claim and final positions have not been reconstructed. The displayed Stable Carry allocation therefore cannot be equated in full with the ERC20 receipts already examined.

## Finding and exit limits

An ETH unit of account does not mean every final payer or collateral asset belongs to Ethereum's staking economy. These investments connect ETH collateral and repayment requirements with BTC, XRP, stablecoins and residential credit.

Exit depends on external lending liquidity, repayment, collateral realization and the ETH portfolio's own debt unwind. The recorded utilization rates do not establish a complete executable exit route.

Data: `carry_vaults_T.json`, `carry_market_allocations_T.json`, `carry_collateral_assets_T.json`, `carry_credit_lookthrough.json`, `pilot_details_T.json`. An independent audit of the underlying credit and legal enforceability of PRIME and Cap claims remains outside the verified balance sheet.
