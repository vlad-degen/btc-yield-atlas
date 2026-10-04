# ETH representations in JustLend on Tron

Public API observation: 3 October 2026. These figures are current disclosures, not values restored from a historical Tron block at T. The latest dated DefiLlama observation on 2 October reports approximately $1.310B ETH cash and $236.5K borrowed ETH separately.

## Treatment in the main report

JustLend’s Tron mapped-ETH balances remain in the captured evidence, but are excluded from the reader’s current market total, every historical category sum and every chain chart. The token symbol and oracle price do not verify Ethereum backing or an executable redemption route. This is an explicit scope decision; it does not establish a loss or say that the token cannot be redeemed.

## What the markets actually hold

JustLend lends tokens that represent ETH on Tron. Their backing and redemption routes matter as much as their symbols.

| Market | Underlying TRC20 | Delegator | Current directory |
|---|---|---|---|
| jETH | `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF` | `TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV` | active |
| jETHB | `TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh` | `TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6` | active |

The [deployed-contract directory](https://docs.justlend.org/developers/deployed_contracts/) explains the renaming: current ETH was formerly ETHOLD, and current ETHB was formerly ETH. The addresses did not change. The 2023 offboarding article describes the decision at that time; the current directory and API show today's names and status. Active status does not independently verify issuer backing.

The [2023 announcement](https://support.justlend.org/hc/en-us/articles/20625315184793-Announcement-on-Enabling-Supply-and-Borrowing-of-ETH-New-and-Offboarding-ETHOLD) distinguishes a centralized representation from the newer BTTC bridge token. Renaming does not remove the differences in their risks.

## How much capital earns interest

The [public API](https://docs.justlend.org/developers/apis/) reports approximately 484,121.559906 jETH cash units, 87.513298 `totalBorrows` and 4.694534 reserves. jToken supply multiplied by the human-readable exchange rate was independently compared with `cash+borrows−reserves`.

API values are already expressed in human-readable units. Dividing them again by 1e18 would produce an incorrect result. The jToken has 8 decimals; its underlying token has 18.

Utilization, the share of available capital borrowed, is approximately 0.0181%. The base annual supply rate is 0.0002899115%, and active USDD mining rewards are zero. Borrowers pay approximately 2.0054% annually. With so little capital borrowed, their payments generate very little income relative to the total supply.

jETHB is much smaller. It has approximately 472.99 token units of cash and approximately 0.00904 debt. Its reserve factor is 100%, with a zero base supply rate and zero mining rewards. This is an economically different market despite the related name.

## The finding

Large dollar total value locked (TVL) does not establish a large income-producing market. Here the headline mainly reflects balances of ETH representations, rather than strong demand for ETH loans.

Capital provenance, issuer reserves and an executable redemption route to Ethereum remain unreconstructed. An oracle that prices a token as ETH does not prove native-ETH backing or eliminate the risk of the representation.

## Exit, controls and remaining checks

Withdrawal and borrowing controls, holder concentration and historical yield require separate Tron archive work. The current API alone does not establish exit capacity or restore governance and fee settings at T.

Data: `justlend_eth_semantics.json`; raw `justlend_markets_current`, `justlend_rewards_current`, `justlend_contracts`, preserving current status and exact addresses.
