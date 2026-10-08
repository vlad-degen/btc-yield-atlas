# Credit rows: on-chain check

Snapshot T: 2 Oct 2026 23:59:59 UTC. Ethereum block 26,108,081, Base 52,098,126, Arbitrum 511,139,919. Every number below is an archive `eth_call` at those blocks. Scripts: `tools/eth/credit_check/`. Raw output: `raw/eth/credit-check-2026-10-08/`. Rates at T: wstETH 1.24540 ETH, weETH 1.10494 ETH.

| Row | Map ETH | Verified ETH | Fits Credit | Recommendation |
|---|---:|---:|---|---|
| Cap | 22,666 | 22,679 cover, 0 lent | Yes (slashable cover for named operators) | Keep in Credit at 22,679 but take it out of the four rows that already count it, or drop the row |
| Native Credit Pool | 2,134 | 2,078 supplied (509 lent) | Yes | Keep, 2,078 |
| Wildcat | 1,927 | 1,919 supplied (1,918 lent) | Yes | Keep, 1,919 |
| Maple (ETH lending) | 10 | 9.5 idle, 0 lent | No | Drop |

## Cap

- Amount matches DefiLlama exactly. 43 agents are registered on Delegation `0xF3E3Eae671000612CE3Fd15e1019154C1a4d693F` (AddAgent logs). Coverage is read from the Symbiotic middleware `0x09a3976d8d63728d20dcdfee1e531c206ba91225` (`coverageByVault`). Total: 11,500.68 wstETH (14,323 ETH) and 7,562.30 weETH (8,356 ETH), so 22,679 ETH. Cap's EigenLayer operator set (`0xe65c3ecc...`) holds 0 ETH-family cover at T.
- No ETH is lent. The ETH is slashable cover. Operators borrow USDC from cUSD reserves through Lender `0x15622c3dbbc5614E6DFa9446603c1779647f01FC` (`debt(agent, asset)`). Against ETH cover they have drawn $19.31M, about 32% of the cover's value. All Cap agents together owe $55.38M, and cUSD supply is 61.5M.
- Every Cap vault is a Symbiotic vault from factory `0xAEb6bdd95c502390db8f52c8909F703E9Af6a346` (`isEntity` = 1). Each vault's stake comes from a product already on the map:

| Symbiotic vault (operator) | Cover | ETH | USDC drawn | Depositor | Map row that already counts it |
|---|---:|---:|---:|---|---|
| Vesper-wstETH `0x88a4...e444` (Odyssey Finance) | 5,029.98 wstETH | 6,264 | 8,428,059 | Vesper strategy `0x023d...35fb` | Vesper pools (stETH 6,296 in DefiLlama); also Symbiotic gross |
| Stakestone-wstETH `0xf40e...ac74` (Stakestone) | 4,714.89 wstETH | 5,872 | 4,808,004 | Safe `0x3e32...5f34` 4,585.49; 15 small wallets 129.4 | StakeStone STONE and the net Symbiotic row (see below) |
| Ether fi-M11 Credit-weETH `0x5c49...2f5b8b` (M11 Credit) | 7,562.30 weETH | 8,356 | 5,342,150 | ether.fi weETHs (Veda BoringVault `0x917c...9d88`) 7,560.6 | Veda: other ETH vaults (weETHs is valued in WETH there) |
| Renzo pzETH-Susquehanna Crypto `0x4b0b...9d9e` | 1,000.00 wstETH | 1,245 | 0 | pzETH (Mellow) | Mellow Restaking |
| MEV-Pareto-wstETH `0x1274...6f94` (Pareto) | 430.24 wstETH | 536 | 482,902 | amphrETH (Mellow) | Mellow Restaking |
| Re7 Labs-Re7 Capital `0x4163...afd8b9` | 325.44 wstETH | 405 | 250,057 | Re7LRT (Mellow) | Mellow Restaking |
| Hyperithm, Cap test, 1 other | 0.14 wstETH | 0.2 | 702 | | |

  Vault names and operators come from the symbioticfi/metadata-mainnet repo. Mellow vault membership comes from api.mellow.finance/v1/vaults, the source of DefiLlama's mellow-restaking adapter.
- StakeStone link: the STONE "Assets Management Strategy" `0x8f4998661618c5cc5dbcc0ae19923d6537622180` sent 8,000 ETH to Safe `0x3e32...` in tx `0x144bf271415de76c4edf6d3176136321d9f9a0ce0985b0c01ad9e1d3f0f67f9f` (block 23,562,108). The Safe wrapped it to wstETH and deposited into the Cap vault. The strategy reports a stored value of 7,326.65 ETH, which DefiLlama's STONE adapter adds up. So the Safe's 4,585 wstETH sits inside the STONE row. It also stays in the Symbiotic row, because the Symbiotic netting removes only Mellow, Vesper and Cap's weETH.
- Netting on the map today: the Cap row takes its wstETH out of Lido and its weETH out of ether.fi. It takes nothing out of Vesper, Veda, Mellow Restaking, STONE or Symbiotic, so the whole 22,679 ETH is shown twice:
  - The Vesper and Mellow parts (8,451 ETH) also leave Lido a second time, so Lido "staked and held" is too low by that amount.
  - Veda's weETHs (8,354 ETH) is booked as WETH and is not netted against ether.fi, so the total is too high by about 8,354.
  - The Stakestone vault (5,872 ETH) is counted in Cap, Symbiotic and STONE. STONE is booked as WETH and is not netted, so the total is too high by about 5,711, and Lido loses the amount once more through Symbiotic.
- Credit fit: yes, on the BTC rule. Lombard BTCe's LBTC posted as slashable cover for a Cap loan is C5. Here the operators are named: Odyssey Finance, M11 Credit, Stakestone, Susquehanna Crypto, Pareto and Re7 Capital. Susquehanna's 1,000 wstETH has no loan drawn against it at T.
- Recommendation: count 22,679 ETH in Credit once. Take 6,264 out of Vesper, 8,354 out of Veda, 2,187 out of Mellow Restaking and 5,872 out of Symbiotic, and cut 5,711 from STONE or Symbiotic, whichever keeps STONE whole, so it is not left in both. This matches the BTC map, which moved the Lombard Vaults row to C5 instead of adding Cap on top. The alternative is to drop the Cap row and leave the ETH in its host rows. Either way, `SYMBIOTIC_ALSO['cap']` (weETH only) is not enough.

## Native Credit Pool

- Vaults: Ethereum `0xe3D41d19564922C9952f692C5Dd0563030f5f2EF`, Base `0x74a4Cd023e5AfB88369E3f22b02440F2614a1367`, Arbitrum `0xbA1cf8A63227b46575AF823BEB4d83D1025eff09`. WETH LP tokens (`lpTokens(WETH)`): Ethereum `0x5994258ec80cc6853e2b6f047ec6d213fe89b24b`, Base `0x7f1bcc60ed3c80da906fd91a2ec63ec71442430a`, Arbitrum `0x8a5fca5429f5d572f71959bfec41495420528ce2`.
- LP `totalUnderlying` is what lenders supplied: Ethereum 2,026.28, Base 51.29, Arbitrum 0.08, total 2,077.65 ETH. On Ethereum the vault holds 1,517.29 WETH idle, and `positions(trader, WETH)` shows 508.99 lent. That trader is the only active one: EOA `0x129b3d9a0a6e4beab88f5cb1e57995d72a6e24f1`, with settler and recipient contracts owned by `0x83fc28e6962e41e38f7854308eff827e3f6b906b`. It posts no collateral and is long 781.8k USDC in the same vault, which is market-maker inventory. Idle plus lent equals totalUnderlying exactly.
- The map is about 56 too high because DefiLlama counts the whole vault WETH balance on L2s: Base 69.59 against 51.29 supplied, Arbitrum 32.44 against 0.08. The excess is the trader's own positive WETH positions, not lenders' ETH.
- Credit fit: yes. It is an uncollateralized credit line to a whitelisted market maker, but the borrower is not named on-chain.

## Wildcat

- ArchController `0xfEB516d9D946dD487A9346F6fee11f40C6945eE4` has 87 registered markets, 6 of them in WETH. Only one is live: Wintermute Trading Wrapped Ether `0xbad1b632e90ce02af868f07c572adb067eb98353`, borrower `0x5b15f94efc3a6e2c82d7db8efd8d5ba55da11feb`, 3.75% APR, 0% reserve. It shows totalSupply 1,919.12, idle 0.65, lent 1,918.47, and totalDebts 1,919.65.
- The other WETH markets are closed or empty: Wintermute `0x6053...`, Raven, Auros, and two Hyperithm markets, about 1.1 WETH together.
- Lenders: 19 accounts, nearly all EOAs or 7702 wallets. The largest holds 407.6. None is a product on the map; evaETH holds 1.0. The map's 1,927.5 is the DefiLlama point for 3 Oct converted at that day's price.
- Credit fit: yes. Uncollateralized WETH loan to a named market maker, the same as Wildcat in the BTC map.

## Maple (ETH lending)

- M11 Credit Maple Pool WETH1 `0xfff9a1caf78b2e5b0a49355a8637ea78b43fb6c3` is "Inactive" in the Maple API. It has totalAssets 9.52, all idle WETH, and its loan manager `0x373bdcf2...` has principalOut 0. The High Yield Corporate Loan WETH1 pool `0xccbc525e...` holds 0.02.
- Credit fit: no. Nothing is lent at T; it is leftover cash in a closed pool.

## Missing ETH credit above 500 ETH

None found. Checked every DefiLlama Uncollateralized Lending and RWA Lending protocol in the 7 Oct pull, plus Accountable, Clearpool, TrueFi, Goldfinch, 3Jane, Credit Coop, Union, Maple and Term:
- Accountable, Clearpool, TrueFi, Goldfinch, Credit Coop and Union: no ETH-family tokens.
- 3Jane: lends USDC.
- Pareto Credit: 22.8 WETH borrowed.
- Cap's EigenLayer operator set: 0 at T.
