# Liquid Monad ETH

The [final capital, income and exit findings](../CAPITAL-INCOME-EXIT.md) extend this original reconstruction with dated cash flows, public backing and investor payout evidence. Original partial-reconstruction figures retain their original scope.


Snapshot T: 2 October 2026, 23:59:59 UTC. Liquid ETH holds this vault's shares within its portfolio. Adding the claim separately to market net asset value (NAV) would double count the same capital.

## What Liquid ETH owns

Ethereum BoringVault `0xa024063b630d554078bbf985718b22f3c6870ee0` is named Liquid Monad ETH. **Liquid ETH owns all 8,085.725173 Ethereum shares at T.** These shares are an investment by the parent portfolio. They do not establish independent external deposits into both products.

The shares' book value is 8,128.761773 ETH-equivalent, approximately **$21.687M**. Including this claim reduces Liquid ETH's unexplained balance from $34.140M to $12.453M, or from 7.223% to 2.634%. Valuation uses the nested vault's own accounts. It does not independently verify the assets deployed on other chains.

## Share pricing, fees and control links

Contract calls establish the identity chain: the vault's `hook()` returns Teller `0x0698ba360468a8c3f62d6c57b01b874016c2b854`, and the Teller's `accountant()` returns `0x5ce04a3d8d5297a24bf752d0172064941d8d853b`. Both Teller `vault()` and Accountant `vault()` return the original vault. Accountant `base()` returns Ethereum WETH.

At T, `getRate()` returns **1.005322540540 ETH/share**. The last update was 2 October, 21:22:35 UTC, approximately 2 hours 37 minutes before T. Platform and performance fee fields are zero at T. This does not establish the complete fee history or the scope of governance permissions.

## Why each chain needs its own accounts

The same vault address exists on Monad, chainId 143. Block 110,031,481 is timestamped T and the next block is T+1, confirming the snapshot boundary. Local share supply is zero at T, and `hook()` returns the same address as on Ethereum.

The Accountant at the same address on Monad reports a rate of 1.0, which differs from the Ethereum rate. A common share price across chains cannot be assumed without checking synchronization. Zero local supply also does not prove that the chain holds no portfolio assets.

Verified Teller source includes share bridging that burns shares on the sending chain and mints them on the receiving chain. Messages in transit and circulating supply on all other chains have not been reconstructed. Current Ethereum discovery mainly finds a WETH balance that is too small to establish complete value. One execution wallet does not reveal all deployment on other chains.

## Income and exit remain open

Liquid ETH's 3 October interface shows a 6.28% Monad allocation, approximately $29.7M at current TVL, meaning total value locked. This exceeds the nested Ethereum book claim at T. Different dates, refresh times, portfolio composition or additional claims could explain the gap, but none has been established.

The difference is neither inserted into the unexplained balance nor treated as a proven deficit. The exact deployment strategy, final income payers and executable exit remain unverified. A book conversion rate is insufficient to establish any of them.

## Evidence and next checks

Primary contracts: [verified vault source](https://eth.blockscout.com/address/0xa024063b630d554078bbf985718b22f3c6870ee0?tab=contract), [Teller](https://eth.blockscout.com/address/0x0698ba360468a8c3f62d6c57b01b874016c2b854?tab=contract), [Accountant](https://eth.blockscout.com/address/0x5ce04a3d8d5297a24bf752d0172064941d8d853b?tab=contract).

Fixed-block evidence: `mono_identity_T.json`, `mono_hook_T.json`, `mono_accountant_T.json`, `mono_remote_T.json`. A guessed GitBook URL returned HTTP 200 with “Page Not Found”, so it was excluded as product verification.

Next work covers assets and loans on other chains, asset bridges and custody, periodic price-per-share (PPS) reconciliation, and executable exit. Until those checks are complete, the nested book claim is not an independently verified measure of underlying NAV.
