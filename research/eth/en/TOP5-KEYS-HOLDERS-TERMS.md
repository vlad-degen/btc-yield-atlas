# Top-5 ETH: holders, keys, fees, terms

Snapshot **T = 2 Oct 2026 23:59:59 UTC**, Ethereum block **26,108,081**. Pulled 7 Oct 2026. Same template as the BTC Kraken chapter: depositors, keys and delays, fee history, terms and loss order, dated events.

Data: [`data/eth/top5/<product>/`](../../../data/eth/top5/) (`holders_monthly.csv`, `holder_buckets.csv`, `keys.csv`, `fees.csv`, `events.csv`; Liquid has holder files only). Scripts and raw pulls: `raw/eth/gap-2026-10-07/keys-holders/` (`scripts/`, `logs/`, `rpc_log.jsonl`, `http/docs/`).

Address note: the YieldBasis WETH LT is `0x2b9c9f3b…3cea`. `0x2b2a612c…` in the brief is a transaction hash, not the LT.

## Findings

1. **Avant is controlled by one EOA.** `0xd4d23209…57cb` has no contract code at T. It is:
   - owner of avETH, so it can add any minter (unlimited avETH);
   - admin of savETH (cooldown, blacklist, moving a restricted holder's balance);
   - admin of the minting contract;
   - owner of both CCIP bridge pools.

   Nothing it does has a delay. Avant's docs say its keys are MPC wallets; that cannot be checked on-chain.
2. **The Avant admin shortened the savETH exit 30 times without notice.** It cut the 24h cooldown to 60 seconds on 30 occasions between 20 Apr and 27 Sep 2026, 219 hours in total. The longest window was 30 Jul to 6 Aug (166 h).
   - **Reserve fund at T:** 38.01 savETH (about 40 ETH), **0.36%** of savETH.
   - **Junior avETHx:** 1,353.65 MAX avETH units, holding no avETH or savETH on Ethereum.
3. **One Avant address holds 37.8% of the product.** EOA `0x3d461625…7904` holds savETH directly, through a Gearbox credit account and as Morpho savETH/WETH collateral (a leveraged loop).
   - **Owners:** 109 after look-through, but the top 10 hold 92.6%.
   - **Bridged out:** 16.3% of savETH sits in the CCIP pool for holders on other chains.
4. **Lido Earn ETH has no timelock on any key.**
   - **Lazy Vault Admin (Safe 5-of-8):** gives itself a role and uses it in the same transaction. It did this on 3 Mar, 18 Apr (paused all deposit queues), 7 Jul and 23 Jul.
   - **Proxy Admin (Safe 5-of-8):** can upgrade all five core contracts instantly. It upgraded the share token on 2 Mar 2026.
   - **Pause path:** a 0-second timelock holds 16 pre-scheduled pause calls. One executor is the Mellow Pauser, a **1-of-8** Safe.
   - **Curator Safe:** 3-of-6 on-chain; Lido's docs say 3/5.
5. **Lido Earn changed fees three times in two months, with no delay.**
   - The fee path ran 0 → 10% + 1%/yr (1 Jul) → 0 (21 Jul) → **15% + 0.2%/yr** (3 Sep, current).
   - **Fee shares minted to the Treasury Safe:** 154.28 earnETH in total, of which 114.73 came in the 20 days of July.
6. **YieldBasis code is immutable; its parameters move by veYB vote.**
   - **Vote rules:** 7-day vote, 55% support, 30% quorum. EarlyExecution mode lets a vote execute before the 7 days end, and there is no separate timelock.
   - **Emergency Safe (5-of-9):** can kill the market. `emergency_withdraw` stays open.
   - **Limit setters:** two contracts, HybridVaultFactory and LTMigrator, can raise the crvUSD allocation without a vote.
7. **The YieldBasis admin fee is about 40%, not 10%, but none has been taken since 20 Jul.**
   - **Why 40%:** the fee follows the staking ratio, `1 - 0.9 x sqrt(1 - staked share)`. At T 56.35% of LT is staked, giving 40.54%; the monthly range was 30% to 43%.
   - **Why nothing is taken:** all 5 fee withdrawals since 20 Jul minted 0 LT, so the staked side is still below its high-water mark. Only 5.47 LT was ever taken, all in June.
8. **YieldBasis looks spread out until you look through its holders.**
   - **Direct:** the gauge holds 56% and the top 10 hold 93.3%.
   - **Look-through** (gauge stakers and HybridVault owners resolved): 407 owners; top 1 holds 21.8% (owner of HybridVault `0xbaec9eb1…`), top 10 hold 70.7%.
9. **Liquity ETH Carry is run by one Safe 2-of-3 with zero delays.**
   - **What the Safe holds:** owner, guardian, atomist and fuse-manager (it decides which protocols the strategist may touch).
   - **No delays:** the execution delay is 0 on every role, there is no `ADMIN_ROLE` holder, and the vault implementation is immutable (EIP-1167 clone).
   - **Fees, 28 May:** performance 2% → 10% and management 0.3% → 0.5%.
   - **Fees, 19 May:** 0.2% each on deposit, instant withdrawal and withdrawal request.
   - **Concentration:** one Safe 3-of-6 holds 36.9%. Rocksolid's execution account holds 12.1%, and Rocksolid entered Closing on 29 Sep.
10. **Liquid ETH holder counts are mostly dust.** Ethereum has 7,793 holder addresses (Optimism, which adds 1,511, is not counted here).
    - **Dust:** 82.4% of addresses hold under 1 ETH and together own 0.26% of capital.
    - **Large holders:** 11 addresses hold 70.3%; two unlabelled EOAs hold 47.3%.
    - **Legacy contract:** the old Liquid1 migration contract still holds 3.19% (4,431 ETH).
    - **Over time:** the address count doubled in Oct 2025 (4,635 → 9,710) with dust. Holders with at least 0.01 ETH fell from 4,439 to 3,151.

## Holders

Positive balances come from replaying every Transfer up to T. Every replay matches `totalSupply` exactly. ETH values use the share price at T:

| Product | ETH per share | Source |
|---|---:|---|
| Liquid | 1.106822 | accountant `getRate` |
| LT | 1.005888 | `pricePerShare` |
| earnETH | 1.018484 | 1 / oracle report |
| savETH | 1.059208 avETH | `totalAssets / totalSupply` |
| Liquity | 0.973079 | 20-decimal shares |

Addresses are not people, and contracts count as one address unless looked through.

### Concentration at T

| Product (view) | Addresses | Median | Top 1 | Top 10 | Top 100 | HHI |
|---|---:|---:|---:|---:|---:|---:|
| Liquid, Ethereum direct | 7,793 | 0.0025 ETH | 25.4% | 69.5% | 89.0% | 1,230 |
| YieldBasis, direct LT | 332 | 0.006 ETH | 56.4% (gauge) | 93.3% | 99.97% | 3,580 |
| YieldBasis, look-through | 407 | 0.097 ETH | 21.8% | 70.7% | 99.0% | 801 |
| Lido Earn, earnETH token | 2,500 | 0.66 ETH | 19.8% | 47.7% | 80.8% | 563 |
| Avant, savETH direct | 83 | 3.35 ETH | 32.1% (Gearbox CA) | 93.4% | 100% | 1,795 |
| Avant, avETH + savETH look-through | 109 | 1.21 ETH | 37.8% | 92.6% | 100% | 1,953 |
| Liquity ETH Carry | 130 | 5.01 ETH | 36.9% (Safe 3-of-6) | 77.4% | 99.9% | 1,723 |

### Size buckets at T (share of addresses / share of capital)

| Bucket | Liquid | YieldBasis (look-through) | Lido Earn | Avant (look-through) | Liquity |
|---|---|---|---|---|---|
| <1 ETH | 82.4% / 0.3% | 65.1% / 0.3% | 54.1% / 0.3% | 46.8% / 0.1% | 26.2% / 0.1% |
| 1 to 10 | 11.3% / 2.1% | 17.9% / 2.7% | 26.6% / 2.7% | 27.5% / 1.0% | 33.1% / 2.5% |
| 10 to 100 | 4.8% / 7.7% | 12.5% / 15.7% | 14.6% / 14.3% | 15.6% / 5.4% | 36.2% / 25.6% |
| 100 to 1k | 1.3% / 19.7% | 4.2% / 59.6% | 4.2% / 35.1% | 6.4% / 19.9% | 3.8% / 34.9% |
| >1k | 0.14% / 70.3% | 0.25% / 21.8% | 0.4% / 47.7% | 3.7% / 73.7% | 0.8% / 36.9% |

### Look-through of large contract holders

- **YieldBasis**
  - The gauge (56.35% of LT) resolves to 155 stakers.
  - 81 HybridVaults (personal crvUSD-backed vaults, holding LT directly or in the gauge) resolve to their `owner()`.
  - The largest owner, `0x0b077c44…`, holds 2,270 ETH through HybridVault `0xbaec9eb1…`.
- **Avant**
  - The savETH contract holds 88.08% of avETH and is replaced by savETH holders.
  - Gearbox credit account `0x6cc892a7…` (32.06% of savETH) resolves to borrower `0x3d461625…`.
  - Morpho Blue (17.63%) resolves to 5 collateral positions (3 material) in two savETH/WETH markets. The largest are `0xe29bb87d…` (886 savETH), `0x3d461625…` (571) and `0x8c252705…` (388).
  - The CCIP LockRelease pool (16.27%) stays one row: those are bridged holders on Avalanche, Linea and Arbitrum.
- **Liquity:** the 12.11% at `0x9ca1d6e7…` is Rocksolid rETH's execution account, a nested product.
- **Liquid:** `0xea1a6307…` ("Ether.fi-Liquid1") is the 2024 migration contract. It received the whole 191,654-share first mint and still holds 3.19%.
- **Lido Earn:** the top 10 include three Safes: 2-of-2 `0xf5c7ec06…` (also a top-10 Liquid holder), 2-of-2 `0xaf3f8594…` and 5-of-9 `0xf6f0732c…`. 788.3 allocated but unclaimed shares sit outside the token supply.

### Holders over time (month-end, full series in CSV)

| Month-end | Liquid | YieldBasis LT | Lido earnETH | savETH | Liquity |
|---|---:|---:|---:|---:|---:|
| 2025-03 | 4,893 | | | | |
| 2025-09 | 4,635 | | | 22 | |
| 2025-10 | 9,710 (4,439 ≥0.01 ETH) | | | 29 | |
| 2026-03 | 8,898 | | 1,195 | 42 | 4 |
| 2026-05 | 8,260 | 26 | 1,118 | 73 | 43 |
| 2026-06 | 8,135 | 164 | 1,527 | 78 | 61 |
| 2026-07 | 8,056 | 243 | 2,389 | 76 | 92 |
| 2026-08 | 7,934 | 324 | 2,429 | 78 | 112 |
| 2026-09 | 7,811 | 334 | 2,500 | 82 | 131 |
| T | 7,793 | 332 | 2,500 | 83 | 130 |

Capital at the same dates (ETH) is in the CSVs. It shows the Lido Earn exit after the April pause (107,422 → 42,805 ETH) and Liquity's doubling in September (2,814 → 6,017 ETH).

## Keys and roles at T

Every role was read at block 26,108,081: Safe thresholds, modules and guards; EIP-1967 admin slots; `getMinDelay`; IPOR `getAccess`; Aragon plugin settings. None of the Safes listed has a module or guard. Full rows are in `keys.csv`.

| Product | Who can change strategy or parameters | Who can upgrade | Pause or kill | Delay |
|---|---|---|---|---|
| YieldBasis | veYB DAO (Aragon TokenVoting) through HybridFactoryOwner → Factory → LT | nobody (immutable Vyper) | Safe 5-of-9 can kill; `emergency_withdraw` stays open | 7-day vote with early execution; kill has none |
| Lido Earn | Lazy Admin Safe 5-of-8 (all roles). Active Admin Safe 3-of-8 sets limits. Curator Safe 3-of-6 moves assets. Oracle Updater Safe 3-of-8 prices | Proxy Admin Safe 5-of-8 (also owns subvaults and stRATEGY proxies) | 0-second timelock with pre-scheduled calls; Lido Pauser 3-of-5 or Mellow Pauser 1-of-8 can execute | none |
| Avant | EOA `0xd4d23209…`; minter/redeemer EOA `0xaf6fd55a…`; rewarder EOA `0xdb87e930…`; strategy wallet EOA `0x6cc60a0b…` | none (no proxies), but the owner can add minters | owner can `disableMintRedeem` and set the cooldown up to 90 days | none |
| Liquity | Safe 2-of-3 `0x32787cd5…` (owner, atomist, fuse manager, guardian); strategists are a PlasmaVaultWrapper and EOA `0xad34f0fe…` | nobody (clone) | Safe 2-of-3 (guardian) closed the vault for 15 minutes on 26 May | 0 on every role |

## Fees

| Product | Current (T) | History (on-chain setter events) |
|---|---|---|
| YieldBasis | LEVAMM fee 1.3%; crvUSD rate 10%/yr (recycled to the pool); admin fee 40.5% of positive value change at 56% staked (10% floor) | no SetFee/SetRate since market creation (25 May 2026). Fee receiver changed: DAO (12 Nov 2025) → `0xd11b4165` (3 Dec 2025) → FeeSplitter, 15% split (20 Jul 2026) |
| Lido Earn | 15% performance (high-water mark) + 0.2%/yr; deposit and redeem fees 0; nested stRATEGY 0 | 0 (2 Feb) → 10% + 1% (1 Jul) → 0 (21 Jul) → 15% + 0.2% (3 Sep); 154.28 earnETH minted to the Treasury |
| Avant | No fee state on-chain. Docs: 10% performance plus a variable fee to trading partners; yield on unstaked avETH kept by the protocol; 10% of yield redirected to junior avETHx; redemption fee shown in the app | none on-chain. Net yield pushed to savETH: 248.6 avETH since Sep 2025 (43.0 in August, the peak) |
| Liquity | 10% performance (curator 8%, IPOR DAO 2%), 0.5%/yr management (0.2% + 0.3%), 0.2% deposit, 0.2% withdraw, 0.2% request | 2% / 0.3% at launch (30 Jan); in/out fees 0.2% (19 May); 10% / 0.5% (28 May). Harvested to T: 8.25 shares, about 8.0 WETH |

## Terms

| Product | Issuer / interface | What the depositor owns | Loss order | Exit |
|---|---|---|---|---|
| YieldBasis | No issuer. The interface is "YieldBasis" (terms 13 Mar 2026, Swiss arbitration in Zurich); the contracts are by Scientia Spectra AG ([terms](https://yieldbasis.com/terms)) | LT share of a 2× WETH/crvUSD Curve LP position, net of crvUSD debt; unstaked LT earns through price per share, staked LT earns YB instead | Pro rata through price per share. Staked holders are protected by a high-water mark that fees refill before any admin fee ([fees](https://docs.yieldbasis.com/user/protocol/fee-mechanics), [risks](https://docs.yieldbasis.com/user/reference/risks)) | Any time on-chain; output can sit below fundamental value; `emergency_withdraw` if killed |
| Lido Earn | Interface by Lido DAO contributors (Cayman law, LCIA arbitration; US and UK persons excluded); Mellow is curator ([terms](https://lido.fi/terms-of-use), [docs](https://docs.lido.fi/earn/)) | earnETH share of a Mellow core vault holding stRATEGY and GGV subvaults | Share price falls; DAO first-loss shares are burned first (done 15 May 2026). The terms say "Firelight first loss protection" is not insurance | Request, then claim, in wstETH. Requests cannot be cancelled. Settlement at the first oracle report ≥24h after the request; about 3 days typical ([redeem queue](https://docs.lido.fi/earn/architecture/queues/redeemqueue)) |
| Avant | Avant Protocol Foundation (BVI law and arbitration; US excluded) ([terms](https://docs.avantprotocol.com/legal-and-risk/terms-of-use)) | avETH: issuer token backed by its strategies, earning nothing unstaked. savETH: ERC-4626 share of avETH (senior tranche) | Reserve fund first (0.36% of savETH at T), then junior avETHx, then savETH ([reserve](https://docs.avantprotocol.com/security/reserve-fund), [tokens](https://docs.avantprotocol.com/overview/core-tokens)) | savETH cooldown 24h (admin can set 60 s to 90 days). avETH redemption is permissioned, up to 7 days, with a fee ([unstake](https://docs.avantprotocol.com/overview/using-avant-protocol/unstaking-savassets), [redeem](https://docs.avantprotocol.com/overview/using-avant-protocol/redeeming-avassets)) |
| Liquity | Interface by IPOR Labs AG (Swiss law; US and China excluded) ([terms](https://www.ipor.io/terms-of-use)); the curator is the Safe 2-of-3 (brand not provable on-chain) | ERC-4626 PlasmaVault share, accounted in WETH; the strategy is an Ebisu wstETH trove borrowing ebUSD into LP | Pro rata through share price; strategy losses are the depositors' ([risks](https://docs.ipor.io/fusion-for-depositors/user-guide/risks)) | Instant if liquid (0.2% fee); otherwise request plus a 24h window (0.2% fee) ([withdrawing](https://docs.ipor.io/fusion-for-depositors/user-guide/withdrawing)) |

## Events

At most 10 dated rows per product are in `events.csv`. Key items not covered above:

- **YieldBasis**
  - The current LT started on 25 May 2026; the January 2026 WETH market is a separate, older LT.
  - On 10 Sep the LTMigrator became a limit setter.
- **Lido Earn**
  - The migration of 13 Mar 2026 brought in 8,703 strETH, 3,280 GG, 2,884 DVstETH and 1,404 wstETH.
  - The pause ran from 18 Apr to 15 May and ended with the DAO burning 143.98 earnETH.
- **Avant**
  - Control passed to the current EOA on 4 Sep 2025.
  - The cooldown was cut from 7 days to 1 day on 5 Sep 2025.
  - Per-block mint and redeem caps rose 20× on 15 Oct 2025.
- **Liquity**
  - Deposits were whitelist-only until 19 May 2026.
  - Control moved from an EIP-7702 EOA to the Safe 2-of-3 between 6 and 11 Jun.
  - Two large holders entered on 25 Aug (Safe) and 23 Sep (Rocksolid).

## Method and limits

- **Logs.** Transfer and admin-event logs come from Tenderly `eth_getLogs` over full ranges. Calls are archive `eth_call` at T or at month-end blocks (the same blocks as `economic-dollar-loans.csv`, plus computed blocks for June to September 2024). Role names come from contract constants and IPOR `Roles.sol`. Two Mellow role hashes (`0x877766a8…`, `0xfc199f68…`) are unresolved.
- **Holder counts include dust and contracts.** `holders_ge_0.01eth` in the monthly CSV filters the dust. The Liquid figures are Ethereum only.
- **ETH prices are book marks.** The Lido monthly ETH uses the oracle report at each block. Avant avETH is valued at face (1 ETH).
- **EOA ≠ single key.** An EOA can be an MPC wallet; the on-chain data cannot tell. Avant says it uses MPC.
- **Documents were read on 7 Oct 2026.** Pages are saved under `raw/eth/gap-2026-10-07/keys-holders/http/docs/`. Policy text and contract state are kept apart. Where they differ, the contract value at T is used: the Lido curator threshold, and Avant's fees, which are not on-chain.
