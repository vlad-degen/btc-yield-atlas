# Who the large ETH-collateral borrowers are (T = 2026-10-02 23:59:59 UTC, block 26,108,081)

*Data: [`data/eth/gap_borrowers.csv`](../../../data/eth/gap_borrowers.csv). Raw pulls and scripts: `raw/eth/gap-2026-10-07/borrowers/` (not published).*

## Scope and method

- **Who is in.** Every Ethereum address in `research_borrowers.json` with more than $5M of dollar debt at T, plus the 10 largest WETH borrowers in that sample. 23 addresses.
- **Debt at T.** Read by archive `eth_call` at block 26,108,081 (Tenderly, Blast, dRPC):
  - Morpho Blue `position` and `market`, for every market the address has ever used (Morpho API list), not only the 25 sampled markets.
  - Aave v3 Core, Aave v3 Prime and Spark variable-debt and aToken balances, reserve by reserve.
- **The $5M test** counts all three venues. Dollar tokens are counted at $1. EURCV is reported separately and not counted.
  - Four addresses pass only because of debt outside the sample: `0x1676`, `0x8328`, `0x6cc6`, `0x5775`.
  - `0xde6b2a06` falls just short at $4.78M and is left out.
- **Identity checks**, as in the BTC [selection method](../../top5/en/00-selection.md):
  - Contract code and verified source (Blockscout).
  - Safe owners and modules.
  - Etherscan name tags and "Funded By" chains, up to 4 hops.
  - First transactions and stablecoin counterparties in the 1,000 token transfers before T (Routescan).
  - Vault shares minted to the wallet, and receipts for key transactions.
- **What did not work.**
  - Arkham returned 403.
  - Fake "USDC" and "RLUSD" contracts from address poisoning showed up in transfer lists (for example 180M "USDC" at `0xdead020b…`). They are excluded: only official token contracts are counted.

## Result

| Address | Who | Kind | Pooled? | Dollar debt at T | WETH debt at T |
|---|---|---|---|---|---|
| [0x7ee29373](https://etherscan.io/address/0x7ee29373f075ee1d83b1b93b4fe94ae242df5178) | Concrete Delta weETH Safe (Bitfinex-linked principal) | product, single principal | no | $176.15M | 0 |
| [0xf0bb2086](https://etherscan.io/address/0xf0bb20865277abd641a307ece5ee04e79073416c) | ether.fi Liquid ETH | product | yes | $87.61M | 441,176 |
| [0xc936e848](https://etherscan.io/address/0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3) | ether.fi Liquid ETH loan manager | product | yes | $34.29M | 0 |
| [0x4f87de7d](https://etherscan.io/address/0x4f87de7d21aef48090958f7342e1f69dff790545) | Manager of private rSHARE vault #2 | private managed vault | borderline | $33.70M (+EURCV 4.68M) | 69,424 |
| [0xa1226872](https://etherscan.io/address/0xa122687285dc5012141055a801045f069112e7c6) | Manager of private rSHARE vault #1 | private managed vault | borderline | $31.72M (+EURCV 5.92M) | 5,549 |
| [0x83284466](https://etherscan.io/address/0x8328446602cb4c3b2b4a25beca6488e947b6f54a) | Unlabeled 7702 EOA, BTC and ETH collateral | unknown | no | $30.64M (ETH-backed 3.99M) | 0 |
| [0xa56da9bb](https://etherscan.io/address/0xa56da9bb528fedf8379b02e95fbbdad34d45846f) | Manager of private rSHARE vault #3 | private managed vault | borderline | $21.70M | 0 |
| [0x1676d237](https://etherscan.io/address/0x1676d23711186076fa74aa53511dda750a1f0d9a) | 3-of-6 Safe, top holder of Liquity ETH Carry | unknown, likely fund | no | $19.56M | 2,168 |
| [0xaa34d20b](https://etherscan.io/address/0xaa34d20be3f9623ccf5bff53ef4dfa765c3f5dd5) | Stablecoin farmer EOA | individual | no | $18.37M (ETH-backed 5.60M) | 0 |
| [0x17787674](https://etherscan.io/address/0x1778767436111ec0adb10f9ba4f51a329d0e7770) | Fasanara Capital-linked | fund / market maker | no | $17.88M | 0 |
| [0x6cc60a0b](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) | Avant strategy wallet (gas from Avant's minting custodian) | product | yes | $13.74M | 0 |
| [0x577557e0](https://etherscan.io/address/0x577557e04ce02cf279b265c7a7b77540acba4a81) | Stablecoin looper EOA | individual | no | $10.12M (ETH-backed 3.73M) | 189 |
| [0x90882e7c](https://etherscan.io/address/0x90882e7c28ddf0ac1177033a310aeed8eff25e90) | NEMO ETH Prime wallet | product | yes | $5.61M | 0 |
| [0x20f6c325](https://etherscan.io/address/0x20f6c325df578a11209817a30ebb2f0d5454176d) | 1-of-1 Safe of a Binance user | individual | no | $5.52M | 0 |
| [0x893aa69f](https://etherscan.io/address/0x893aa69fbaa1ee81b536f0fbe3a3453e86290080) | Mellow strETH Sub Vault 2 (Lido Earn ETH) | product | yes | 0 | 82,555 |
| [0x13d05033](https://etherscan.io/address/0x13d0503352f34b751cacfbe27e694b58561f2983) | Safe under a 3-of-8 Safe | unknown, likely fund | no | 0 | 32,472 |
| [0x462a336d](https://etherscan.io/address/0x462a336dcac6eaf544106266914caa5a18b831d0) | Unlabeled EOA | individual | no | 0 | 31,385 |
| [0x9a3569c7](https://etherscan.io/address/0x9a3569c7053f9fb5abeb7ccb1678bd33c47ad278) | Contango v2 position of Safe `0xe979438b` | individual via platform | no | 0 | 4,100 |
| [0x5cede91b](https://etherscan.io/address/0x5cede91b3c5783d093b2f6c29cb2571a11204b27) | Instadapp DSA of `0x56f91d80` | individual | no | 0 | 4,055 |
| [0x4b441cd7](https://etherscan.io/address/0x4b441cd7c5085d0c255eff3db7ec3417cca1a1a0) | Etherscan label "Abyss Finance: Eth2 Depositor 138" | individual | no | 0 | 2,943 |
| [0xb224f589](https://etherscan.io/address/0xb224f589297a5a207e6069de5dafd4b120129817) | Seamless WSTETH-ETH-25x lending adapter | product (ETH loop) | yes | 0 | 2,560 |
| [0xfb74196e](https://etherscan.io/address/0xfb74196eccf35a260dd5cfd300baa37ae058b6c0) | 2021 Binance-funded EOA | individual | no | $1.89M | 1,634 |
| [0xb7829e0a](https://etherscan.io/address/0xb7829e0a55975e9380e76e27d89391a795807a7f) | Instadapp DSA of dankest.eth | individual | no | $0.78M | 1,488 |

**Summary of the 23 addresses:**

- **Named: 13.**
  - Product wallets: 6 (Concrete Delta, ether.fi Liquid ETH ×2, NEMO, Mellow strETH, Seamless).
  - Fasanara Capital: 1.
  - Managers of the private rSHARE vault structure: 3.
  - Labeled individuals or platform positions: 3 (dankest.eth, the Abyss-labeled EOA, the Contango position).
- **Profiled but unnamed: 10.** Each has a funding path and behavior profile, but no name tag.

## Main finding: three private WETH vaults run one carry book

`0xa122`, `0x4f87` and `0xa56d` are each the `manager` of a verified **ManagedReceiptVault** issuing "Receipt Vault Share" (rSHARE) against WETH. The three vaults are:

- [`0x66723dc7`](https://etherscan.io/address/0x66723dc7bc8929846a3a1ef1e3d1cc9e8c15303c#code)
- [`0xc802afc4`](https://etherscan.io/address/0xc802afc401266bc64a485a3ee11bac07c1cdcf30#code)
- [`0x49a6f032`](https://etherscan.io/address/0x49a6f0325f77fd4d8a1607353ac6b614af0c1bc8#code)

How the contract works (from its source comments):

- Deposits go straight to the manager wallet, and shares are minted to the depositor.
- The owner sets the price per share from an off-chain NAV.
- Deposits are whitelist-only.
- Shares are non-transferable.

What we read at T:

- **Supply.** 39,966.65 + 25,361.63 + 17,720.33 = **83,048.6 rSHARE**, about 83k WETH deposited.
- **Price per share** is still the initial 1.0 in all three vaults. No NAV has ever been posted.
- **Depositors.** Each vault has 2 to 10 holders. All are fresh wallets that deposited round amounts. In vault `0xc802afc4`, for example, five deposits are about 2,028.6 WETH and five are about 3,043 WETH.
- **Where the depositors' money came from.** On 23 and 24 March 2026 the depositor wallets received gas, then ETH in the thousands, from intermediate wallets. Etherscan shows those intermediates were funded by Binance 16, 18 and 20 hot wallets. The depositors then swapped the ETH to WETH through Velora and deposited it.
- **Owners and deployers.** The three vault owners are separate fresh EOAs. The deployers were gas-funded by Bybit Hot Wallet 12.

Same operator across all three:

- All three managers were created on **26 March 2026**. Each received a 0.1 WETH test deposit that was returned, then the bulk deposit.
- `0xa122` and `0x4f87` were gas-funded by **FixedFloat Hot Wallet 2**, about 38 minutes apart, with almost identical amounts (0.00496549 and 0.00496591 ETH). Transactions: [`0xf9bb558d`](https://etherscan.io/tx/0xf9bb558d56145182457364838e9d5e641651d96309373645199e04626cc36a03), [`0x92a3b1b0`](https://etherscan.io/tx/0x92a3b1b07edf2463f79f99bd2585e21f5c6dea0c536110571e5ef2943042f4e0).
- `0x4f87` and `0xa56d` mint USDe directly through Ethena Mint and Redeem V2, which requires Ethena whitelisting. The `Mint` events name each wallet as benefactor ([`0x0d9b99f4`](https://etherscan.io/tx/0x0d9b99f40c98f42426a88936e6014c5009bbe52936e62310d2e80fd6ad4d8eed), [`0x1d91ecbe`](https://etherscan.io/tx/0x1d91ecbe9aa6e2e994a388e16cddcfa5d579f1d81ac503767bf575cb71ae8b80)).

Combined book at T:

- **$87.1M of dollar debt**, plus 10.6M EURCV and 75k WETH. The WETH debt is mostly a weETH loop on Aave.
- **Collateral:** weETH, wstETH, OETH and rsETH across Morpho, Aave and Spark.

Where the borrowed dollars went (shares minted to the wallets before T):

- RockawayX USDC Yield, f(x) and Tori.
- Sentora RLUSD Main, PRIME Main and Huma PST.
- Hastra wYLDS and PRIME.
- Bitwise Premium RWA AUSD.
- Wintermute USDC Select.
- Pendle Ecosystem USDC.
- Ember Y10K.
- Coinshift USPC ([`0xf8c95d01`](https://etherscan.io/tx/0xf8c95d0182615b399e3c01221d64ab9131cb500a07231294b356dc31fd71f13c)).
- Ethena mints.
- Zama confidential cUSDC.
- Circle CCTP bridging.

**Is it a carry product?** Mechanically yes: an ETH vault with shares, a manager who borrows dollars, and yield deployment. But the structure is permissioned, its NAV is never published, and its depositors look like one principal splitting capital across fresh wallets. We treat it like Concrete Delta: **list it beside the census as a private vault, not as a public product.** If the census rule is "a vault contract with share accounting", it qualifies and would rank second by dollar debt.

## Other findings

- **Fasanara Capital** (`0x1778`). Evidence for the link:
  - Its first gas in 2021 came from `0x4831c121` ([tx](https://etherscan.io/tx/0x1bc663624c0c03de37d889b9c4e2e03fd25a557f740da59dea30b54816667645)).
  - Etherscan shows that `0x4831c121` was funded by [Fasanara Capital `0x85464b20`](https://etherscan.io/address/0x85464b207d7c1fce8da13d2f3d950c796e399a9c) ([tx](https://etherscan.io/tx/0x60ee8148fbae47e8bf45ed6446a27460f8414a333038977779e53de5c062840f)).
  - It sends 7.0M USDT to `0x1c68c3de` ([tx](https://etherscan.io/tx/0x67e87c14923408f7584144be843ff551d67d1b55411724288d4eba94e6bc4ae7)), which was funded by the same Fasanara address ([tx](https://etherscan.io/tx/0x621b0a32570fb7ee09524d12557d5f7719313606d1909dd9d61cc040f81eecd1)).

  Where the borrowed USDT and USDC went:
  - Mostly to Binance deposit `0xbd9f00b3`: 54.5M in the window, for example [10M USDC](https://etherscan.io/tx/0x368ccf7c10e6a1a5241e160399b2d65f1e356e3b6dd54c799da68507891070ab).
  - Inflows come from Coinbase 10 and Bullish.

  This is exchange trading capital, not a product.
- **`0x1676`** is a 3-of-6 Safe and the largest holder (36.9%) of Liquity ETH Carry (IPOR Fusion `0xb9e806e8`).
  - It borrows GHO on Aave Prime and USDS on Spark. The stables go to Compound Institutional USDC ([5M](https://etherscan.io/tx/0xc883b3adf840b0a464b584f813627a757daaaa791e1796afbf1415913b38c6da)), sGHO ([5M](https://etherscan.io/tx/0x5bf78ff304ddc7fc922ca8b2fc0c372f088c179a69f6dfd94c59ddbd57bc2c37)), Sky USDS Flagship and Paypal USD Main.
  - It borrows WETH on Morpho and deposits it into Liquity ETH Carry ([1,000 WETH](https://etherscan.io/tx/0x6365234678dad2cb2fba5484d3b90f7ae3df3231d96f1ad8026f831180f5a055)).
  - Safe `0x458cd345` has the same six owners. Signers were funded by noca.eth and by "Gnosis: Active Treasury Management".
  - Not named.
- **`0x8328`** is in the BTC study's scan as an out-of-scope EOA. Of its $30.6M dollar debt, $17.4M is against kBTC and WBTC and only $4.0M against weETH.
- **`0xaa34`, `0x5775` and `0x6cc6`** mostly loop stablecoins against stablecoins: PT-reUSD, reUSD, strUSD and savUSD. Only $5.6M, $3.7M and about $10.7M of their dollar debt is ETH-backed. `0x6cc6` also uses the Aave v4 Core Hub ([tx](https://etherscan.io/tx/0xfbbe886be81b554f09a480fa45f757e471b1b7cc8640e53953776e41bed6be6a)).
- **WETH loops.**
  - **Products:** Mellow strETH Sub Vault 2 (82,555 WETH; already counted under Lido Earn ETH) and Seamless WSTETH-ETH-25x (2,560 WETH, adapter created in [`0x32a45b87`](https://etherscan.io/tx/0x32a45b87b76e195798c1aebfc07cfc770ff7a84087ec658079b505f2c76a664f)). Seamless is not in the study.
  - **Contango:** `0x9a35` was deployed by Contango's verified [`UnderlyingPositionFactory`](https://etherscan.io/address/0xdaba83815404f5e1bc33f5885db7d96f51e127f5#code). It belongs to one trader, a 3-of-7 Safe.
  - **Not products:** `0x13d0` and `0x462a`, each with about 31k to 32k WETH, have no labels.

## Pooled carry products missed by the census

- **No public pooled dollar-carry product** was missed among the addresses above $5M.
- **Closest: the rSHARE vault structure.** It has about 83k WETH of deposits and $87.1M of dollar debt, run through three manager wallets. See above for whether to include it.
- **ETH-debt loops not covered:** Seamless WSTETH-ETH-25x is a public ETH-debt loop and is not in the study.

## Limits

- Debt is read at T. Destinations are counterparty totals and minted shares over the last 1,000 token transfers up to T. They are not exclusive tracing of each loan, because tokens are fungible.
- "Funded By" shows where the gas came from, not who owns the wallet.
- Etherscan tag lists also contain spam token names. We used only the page title and named funders.
