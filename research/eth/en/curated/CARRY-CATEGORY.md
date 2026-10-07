# ETH dollar carry: products, debt and history

Financial snapshot: **2 October 2026**, Ethereum block 26,108,081.

## Findings

- **Carry is 1.7% of ETH that earns a yield**: 305,908 ETH in 12 products, owing **$270.9M** of dollar debt (BTC: 9.9%).
- **Two products dominate.** Liquid ETH and YieldBasis hold 80% of the debt; Liquid ETH and Lido Earn hold 85% of the books.
- **Private mandates borrow as much as all the products.** Concrete Delta ($176.15M, one Bitfinex-linked wallet) and three whitelist-only rSHARE vaults run by one operator owe about $252M between them; both are left out of the map.
- **The spread is thin.** Liquid ETH beat stETH by 0.66 pp a year over two years; its loop added +0.02 pp and its dollar leg -0.13 pp. Only YieldBasis covers its loan from fees.
- **The book is new.** Carry debt was under $1M until August 2025 and grew from $17.5M in May 2026 to $270.9M at T.

## Products

Ranked by dollars borrowed against ETH. Whole book includes ETH loops and other sleeves; Rocksolid's 728 ETH of Liquity shares are counted once, in Liquity.

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

## Left out

- **Concrete Delta weETH** (307,363 ETH, $176.15M of USDT, USDC and PYUSD at 21.5% LTV): one principal's own position, minted to one address; ctwstETH+ (45,382 ETH) is the same Safe's circular holding. [CONCRETE-DELTA](CONCRETE-DELTA.md).
- **Three rSHARE vaults** (about 83k WETH): whitelist-only, one operator, NAV set off-chain. [BORROWER-IDENTITIES](BORROWER-IDENTITIES.md).
- **ETH-debt loops** (WETH borrowed to stake again) are leveraged staking, not carry. Liquid's inner PRIME/PYUSD loan ($21.0M) finances a dollar asset, not ETH, and is outside the direct total.

## Two years of debt

Month-end dollar debt: Aug 2025: $47.9M; Sep 2025: $61.6M; Oct 2025: $15.8M; Apr 2026: $68.6M; May 2026: $17.5M; Jul 2026: $92.4M; Aug 2026: $239.5M; Sep 2026: $263.1M. Liquid ETH took its first Aave USDC loan in August 2025 and repaid in October; Reservoir peaked and emptied; Liquity borrowed from March 2026, YieldBasis WETH from May, Liquid's Morpho RLUSD, USDC and PYUSD loans from June. TAU unwound to dust. Rocksolid closed on 29 September and reopened on 7 October.

## Return and profit

The 30-day comparison and the four financed lots are in the [briefing](BRIEFING.md). Liquid's loop and dollar-leg split: [LIQUID-LOOP](LIQUID-LOOP.md); rewards: [REWARDS-SPLIT](REWARDS-SPLIT.md).

## Sources

[Canonical answers](../../../data/eth/economic_questions.json), [loan CSV](../../../data/eth/economic-dollar-loans.csv), [financing history CSV](../../../data/eth/economic-carry-history.csv), [status and capital CSV](../../../data/eth/carry-status-and-capital.csv), [product evidence](CARRY-PRODUCTS.md), [route decisions](CARRY-COVERAGE-AUDIT.md).
