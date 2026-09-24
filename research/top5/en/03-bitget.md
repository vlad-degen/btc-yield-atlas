# Bitget bgBTC Onchain Earn: deep dive (Morph × Gauntlet Aera × Morpho × RedStone × Chainlink)

*Scripts: [`tools/top5/bitget/`](../../../tools/top5/bitget/), data: [`data/top5/bitget/`](../../../data/top5/bitget/). Mentions of `scripts/` and `raw/` below refer to the working folder; the `raw/` dumps are not published.*

State as of 2026-09-21 ~22:30 UTC (Morph block 27,158,820). All on-chain numbers come from direct reads of the Morph archive RPC (`rpc-quicknode.morphl2.io`, `rpc.morphl2.io`, `morph.drpc.org`), Morph Blockscout (`explorer-api.morphl2.io`), Ethereum RPC and Blockscout, mempool.space, and the Chainlink PoR feed. Scripts are in `scripts/` and raw pulls in `raw/`. Web sources are in `raw/web/`, indexed in `raw/web/_sources_index.tsv`.

Labels used in this report:
- **(est.)** marks an estimate or model output.
- **(inf.)** marks an inference from on-chain linkage.
- Everything else was read directly.

---

## 0. The findings that matter most

1. **The BTC vault is one Bitget wallet, not retail.** The Aera vault `gtOVBG` (`0x85A1D961F1D1bbD9b4A6D96106c5bF9ae91f0510`) has 3 unit holders.
   - EOA `0x9EB53a82d9f390dBe94b6B8b15ca32B523195cA4` holds 798.7179 of 798.7180 units.
   - This is a Bitget omnibus (inf.). It was gas-funded by Bitget's hot wallet `0x1AB4973a…8F23` (labelled "Bitget: Hot Wallet" on Ethereum), and all its bgBTC arrived by CCIP from Ethereum.
   - Bitget's own API reports **801.41 BTC in "Gauntlet Bitget BGBTC"**, which equals the vault NAV to the satoshi.
   - Retail users hold BGBTC only on Bitget's books: 1,184 BGBTC, of which 67.68% is deployed and 32.32% (382.59) sits idle.
2. **The loop is closed, and the "yield" is Bitget's own USDC recycled.**
   - The vault posts 801.7 bgBTC and borrows $43.03M USDC. The USDC goes into gtusdc, where the vault owns 82.1% of shares. gtusdc's only adapter lends $47.79M back into the same market.
   - Every USD of incentive traced on-chain comes from **Bitget's hot wallet** `0x1AB4…`: 7 weekly USDC campaigns totalling $287,016. They reach a custom, unverified reward distributor `0x53d2…` via Safes/EOAs.
   - About 82% of claims go back to the Bitget-owned vault. The vault swaps them to bgBTC on Native RFQ, where the bgBTC liquidity is also Bitget's LP. It then posts the bgBTC as collateral.
   - No Morph-foundation or Merkl funding was found. An off-chain reimbursement by Morph cannot be excluded.
3. **Organic carry is negative every week.**
   - gtusdc organic APY runs 1.5–2.3%, against a 2.87–3.05% borrow APY. The organic spread is −0.55 to −1.57 pp.
   - The vault's net USD leg since launch:
     - Interest paid: −$121,276.
     - gtusdc organic gain: +$92,086.
     - Rewards claimed: +$192,518.
   - Realized BTC yield is **2.34% APY** since 31 Jul (weekly 2.1–2.6%). The unit price went from 1.0000178 to 1.0033735.
   - The advertised figures were "up to 3%" (BTC) and "~18%" (USDC). Bitget currently pays 1.70% APR on BGBTC.
4. **Growth stopped on 17–21 Aug.**
   - Vault collateral has been flat at about 801 bgBTC. USD TVL has moved only with the BTC price.
   - gtusdc's market cap is $50M (a 7-day timelocked `increaseAbsoluteCap`), and the incentive budget is fixed at about $38.7k a week. Both limit scale.
   - The extra 200 BGBTC Bitget minted on 1–2 Sep remains undeployed.
5. **Keys: one Bitget EOA, `0xdB255Fcc87BF82FAE85108428633784402Ebf860`, sits at the top of the whole BTC side.** It is:
   - owner of bgBTC on Ethereum (including the minter contract);
   - owner of bgBTC on Morph and its CCIP admin;
   - owner of both CCIP pools, and it changes the rate limits with no delay;
   - owner of the Aera vault and its RolesAuthority, which lets it set guardian roots, the provisioner and the fee calculator;
   - one of 2 required signers on the gtusdc owner Safe.
6. **Exit is fast in USDC and slow in BTC.**
   - The whole $43M debt can be unwound atomically, because the funding is circular.
   - Moving bgBTC out of Morph is capped by the CCIP rate limit at **65 bgBTC per day**, about 12 days for 801.7 bgBTC (est.). The owner EOA can lift that instantly; it did so on 29 Jul and 14 Aug.
   - Bitget suspended BGBTC–Morph deposits and withdrawals on 28 Aug ("wallet maintenance"). No resumption notice was found.

---

## A. Passport

| Field | Value | Source |
|---|---|---|
| Product | "BGBTC" in Bitget Earn > On-chain Elite (bitget.com/finance/on-chain-elite/bitget-btc). USDC side: "USDC Earn Vault on Morph" in Bitget Wallet | Bitget product page and API; Morph blog, 21 Aug |
| Launch | bgBTC option on 31 Jul 2026 (Bitget "BGBTC upgraded" article dated 30 Jul). USDC option in Bitget Wallet on 3 Aug | Bitget support 12560603889792; bitpinas |
| Pre-launch on-chain | Morpho market created 30 Jun. Aera vault registered 9 Jul. First bridging 16 Jul. First vault deposit 22 Jul (0.1 bgBTC test) | `raw/morpho_logs_market.json`, `raw/pfc_logs_vault.json`, `raw/omnibus_token_transfers.json` |
| Chains | Bitcoin (reserve) → Ethereum (BGBTC ERC-20 `0x0520930F21b14Cafac7a27b102487beE7138a017`) → Morph via CCIP (bgBTC `0x31011317764E097b28d159a8145B92BFA453F606`) | CCIP pools read on-chain |
| Status | Live. Vault not paused. Subscriptions rationed by quota campaigns. BGBTC–Morph exchange deposits and withdrawals suspended since 28 Aug | on-chain; Bitget support 12560603893675 |
| Size, BTC | Vault NAV 801.41 bgBTC (798.72 units × 1.00337348). Collateral 801.71 bgBTC. BGBTC supply 1,184. PoR reserves 1,419.9997 BTC | `raw/state_now.json`; Chainlink PoR |
| Size, USD | Vault NAV $69.38M at $86,569 (RedStone). Debt $43.03M. gtusdc $52.35M (external holders $9.35M). Headline "BTC collateral + USDC vault" = $121.75M, which double-counts $43.0M of looped USDC. Net external capital $78.75M (est.) | `tvl_weekly.csv` |
| Depositors | On-chain: 1 (Bitget omnibus) in the BTC vault. 1,386 non-vault gtusdc wallets. 1,258 unique reward claimers. Bitget user count for BGBTC: not disclosed. "125M+ users" is Bitget-wide | `holders.csv` |
| Legal entity | Bitget ToU operator: **BTG Technology Holdings Limited**, Hong Kong law, HKIAC arbitration (ToU 14 Aug 2026). The On-chain Earn Agreement says the service "is not a product registered with any government". Bitget Wallet: BGW Technology Limited (Anjouan, Comoros). No BGBTC-specific licence found | `raw/web/bitget_terms_of_use.txt`, `…onchain_earn_agreement.txt`, `bitget_wallet_terms.txt` |
| Eligibility | Bitget prohibited list includes the US, Canada, Austria, France, Germany, Hong Kong, Japan, Singapore, Malaysia, Thailand, Kazakhstan and sanctioned states (not the UK). Subscription limits vary by VIP level. The Gauntlet API says the vault is "only available to Bitget users" | same; `raw/web/gauntlet_api_v1_vault_gtOVBG.json` |

## B. Mechanics, step by step (verified path)

1. **User → Bitget.**
   - The user converts BTC to BGBTC 1:1 inside Bitget. BGBTC is also usable as margin, loan collateral and in PoolX.
   - Yield accrues from T+1 and is paid in BGBTC.
   - Standard redemption is T+4 (3–5 days) with no fee. Express redemption is instant at 0.1% (VIP discounts).
   - Bitget shows annualRate 1.70% and invest-list APR "3.00" for Gauntlet.
2. **Minting and custody.**
   - BTC moves from Bitget's exchange wallet `1FWQiwK27EnGXb6BiBMRLJvunJQZZPMcGd` (DefiLlama's "bitget" CEX list) into a **single P2PKH address, `19pFLWW3CwjZujRWpVEMdguBMZEqPuj5nA`**. It holds 1,419.9997 BTC. Inflows: +130 on 31 Jul, +300 on 14 Aug, +300 on 1 Sep.
   - BGBTC on Ethereum is minted by `MinterContract 0x0b24cf5a…` to a fixed EOA `mintDestination 0x8f1aae29…`.
     - Limits: 1–100 per mint and 500 per day.
     - There is **no on-chain PoR check** at mint.
   - Chainlink PoR (proxy `0xADcc914F882965Ef1B2f1043522b3B81ED081491`) reports what Bitget's own "Wallet Address Manager" lists. Its history: 690 BTC (Mar–Jul) → 820 (31 Jul) → 1,120 (14 Aug) → 1,420 (1 Sep).
   - Custodian: none named. Reserves are self-custodied by Bitget (inf.).
3. **Bridge.**
   - CCIP Lock/Release pool on Ethereum `0xa1f0cAF8…2a04` (835.019 bgBTC locked) ↔ Burn/Mint pool on Morph `0xf50Be8eA…4e4b`. Morph supply is 835.019.
   - Bridged amounts: 25 bgBTC (16 Jul), 500 (29 Jul) and 300 (14 Aug), each by the omnibus EOA.
   - Rate limits were raised to 500 for each big transfer and then cut back. Current Morph outbound is 65 bgBTC capacity with 65/day refill. Inbound is 80/day.
4. **Aera vault (bgBTC Earn, gtOVBG, Aera v3 MultiDepositorVault).**
   - The omnibus calls `ProvisionerV2.requestDeposit`. The Gauntlet guardian solves it in about 1–2 min.
   - Deposits: 0.1, then 60 (30 Jul), 440 (31 Jul) and 300 (17 Aug). Redemptions: 0.0001 and 1.0 unit (9 Sep, solved in 40 min).
   - The unit price is pushed hourly by accountant bot `0xDd99…` via Forwarder `0x416b…` into `PriceAndFeeCalculatorV2 0x8996…`. Guard band is ±1% per update, with at least 60 min between updates.
   - Vault fees are **0% TVL and 0% performance**, and protocol fees are 0.
5. **Morpho market** `0x37d156e96a4230c1fe9545579086e4b40d08b4aae8b3c78ee91031f2a22c1a5c` on Morpho Blue `0xAd10d079…4905`.
   - Loan token: USDC `0xCfb1186F…372B`. Collateral: bgBTC.
   - Oracle: `MorphoChainlinkOracleV2 0x22b3d927…` with base feed `0xb81131B6…` = "RedStone Price Feed for BTC" (MorphPriceFeedBtcWithoutRoundsV1, upgradeable proxy whose ProxyAdmin is owned by a 2-of-3 Safe).
   - **bgBTC is priced as BTC.** There is no bgBTC/BTC leg.
   - IRM: AdaptiveCurveIrm `0xfB69467D…3319`. rateAtTarget went from 2.31% APR (31 Jul) to 2.80% (21 Sep).
   - LLTV 77% (liquidation incentive factor 1.074). Market fee 0.
   - Other bgBTC markets (LLTV 38.5%, 77% with a different oracle, and 91.5%) are empty.
6. **USDC borrowed → gtusdc.**
   - The vault borrowed $58.61M gross and repaid $15.70M. Debt is now $43.03M at 2.825% APR (2.87% APY), with utilization at 90.03%.
   - All borrowed USDC is deposited into **gtusdc** (Morpho VaultV2 "Gauntlet USDC", `0x9131EB40bD0bDcE73c72755f1BB2Cf39a9453341`), where the vault owns 42.844M of 52.158M shares.
7. **Back into the same market.**
   - gtusdc's single adapter `MorphoMarketV1AdapterV2 0x2214…7e62` supplies $47.79M to the same market. It is the market's only material supplier; one tiny 0.9 USDC test account aside.
   - $4.56M sits idle in gtusdc. `liquidityAdapter` has been 0x0 since 21 Jul, so deposits stay idle until allocator bot `0xa690…` allocates them.
8. **Where the yield comes from.**
   - Weekly USDC campaigns on the unverified distributor `0x53D239FEEF1fc7C8Cf80bC6e920796d33DB0c027`: #8, #19, #20, #21, #26, #28, #29, worth $38.7k–44.0k each over 7–8.5 days.
   - Merkle roots are updated every ~8h by EOA `0x54BA…`.
   - The rewards are paid to gtusdc holders in proportion to their holdings (inf.). The vault's claims track its gtusdc share: 50% in week 1, 79–81% since late August.
   - No Merkl campaigns exist on Morph (Merkl API returns only test tokens), and no Morph token exists.
9. **Converting rewards to BTC.**
   - In one guardian transaction (bot `0x1A57…` → Forwarder `0x58C6…` → `vault.submit`), the vault:
     1. claims USDC from `0x53d2`;
     2. swaps it on **Native RFQ** (NativeRFQPool; CreditVault `0x4Df7…CC19`);
     3. supplies the resulting bgBTC as Morpho collateral.
   - There were 89 swaps in total: $192,517.95 → 2.607971 bgBTC, at a USDC-weighted +1.6 bps versus RedStone (range −39 to +79 bps).
   - The bgBTC side of Native is **wNLP-BGBTC, 99.99% owned by the Bitget omnibus** (25 bgBTC seeded on 16 Jul; 22.4 left). The USDC side was seeded with $1M by Bitget ops EOA `0xbd5b…`.
10. **Withdrawals.**
    - For users: from Bitget's balance sheet (T+4 or express).
    - On-chain: omnibus `requestRedeem` → guardian solves → bgBTC → CCIP → Ethereum → Bitget burn. The one observed redemption (9 Sep) ended as 1 bgBTC sent to a Bitget deposit address on Morph.

## C. Counterparty chain and ownership

| Layer | Holder / controller | Evidence |
|---|---|---|
| BTC reserves | Bitget, single P2PKH address (key custody unknown; no third-party custodian named). Coverage 1,420 BTC vs 1,184 BGBTC (119.9%) | mempool.space; Chainlink PoR; Bitget API |
| BGBTC (ETH) | Owner, and owner of the MinterContract: EOA `0xdB25…f860`. Minter caller `0x69c4…`. Holders: CCIP pool 835.02 (70.5%), Bitget hot wallet 348.47 (29.4%), dust | Ethereum Blockscout; RPC |
| bgBTC (Morph) and CCIP | Token owner and CCIP admin: EOA `0xdB25`. Both pool owners: EOA `0xdB25` (Morph pool ownership moved to it on 14 Jul) | `raw/morph_ccip_pool_logs.json` |
| Aera vault shares | **Bitget omnibus EOA `0x9EB5…` holds 99.9999%** (inf. Bitget) | token holders |
| Aera vault control | Owner and RolesAuthority owner: EOA `0xdB25` (can set guardian roots with no timelock) | RPC |
| Aera operations | Guardians: Forwarders `0x58C6` (bot `0x1A57`, 421 txs) and `0x3C98` (unused). Accountant Forwarder `0x416b` (bot `0xDd99`, 1,480 price pushes). Forwarders and Provisioner are owned by TimelockController `0xcDA0` (**6 h**), whose proposer, executor and canceller is a **1-of-1 Safe `0x4b6c`** (signer `0x98eb…`) | RPC; RoleGranted logs |
| Aera platform (PFC, oracle registry, whitelist) | TimelockController `0xf77a` (**24 h**). Proposer: Safe `0x5548` (3-of-7), with the same 7 signers as Safe `0x759b` (Forwarder owner). Aera/Gauntlet platform multisig (inf.; the PFC serves several vaults) | RPC |
| gtusdc owner | Safe `0xc2ae` **2-of-2** = {Bitget EOA `0xdB25`, Safe `0x7c8e` 4-of-7 (Gauntlet signers)} | RPC |
| gtusdc curator | Safe `0xae95` 3-of-7 (the same 7 signers). Gauntlet (inf.) | RPC |
| gtusdc allocators | `0xae95` and bot `0xa690` | RPC |
| gtusdc sentinels | `0xaff2` (3-of-7, Gauntlet signers), `0x72c5` (4-of-6; also owner of the reward distributor; shares 2 signers with the Bitget-funded Safe `0x8a0e`, so Bitget/Morph side, inf.), `0x41a5` (EOA) | RPC |
| gtusdc timelocks | 7 days on caps, adapters and timelock changes. 1 day on setIsAllocator, fees and forceDeallocatePenalty. Owner-only actions (setCurator, setIsSentinel) are instant by VaultV2 design, but need the Bitget+Gauntlet 2-of-2. Gates and adapter registry abdicated. forceDeallocatePenalty 0.001%. Absolute cap $50M | `raw/governance.json`, `raw/gtusdc_logs.json` |
| Incentives | Funders: Safe `0x8fa6` (2-of-3), Safe `0x8a0e` (2-of-3), EOA `0xbd5b`, **all topped up from the Bitget hot wallet `0x1AB4`**. Campaign creators: EOAs `0x73b2`, `0x26a7`. Root poster: EOA `0x54BA` | `raw/tt_*.json`, `raw/campaigns.json` |
| Oracle | RedStone BTC/USD feed proxy (admin: 2-of-3 Safe, no timelock). Morpho oracle contract immutable | RPC |
| L2 | Morph: L2BEAT Stage 0. Optimistic rollup with ZK fault proofs and whitelisted challengers. Centralized sequencer; forced inclusion after 7 days. **4-of-6 upgrade multisig with no delay (CRITICAL)** | `raw/web/l2beat_morph.txt` |

## D. Who manages

- **Gauntlet** (strategy, risk and bots).
  - The only person named publicly is **Matt Dobel**, VP of Growth (Blockhead, 7 Aug). No product-level risk staff are named.
  - Vault description (Gauntlet API): "seeks yield on bgBTC through a portfolio of carry trades…".
  - Gauntlet is also the first curator in Bitget's "Curator framework".
- **Bitget:** CEO **Gracy Chen** (quoted at launch). Bitget holds the keys to the BTC side (EOA `0xdB25`) and is the sole depositor.
- **Morph:** **Kate Wong**, Liquidity and DeFi Lead. Morph is BGB-based: Bitget gave 440M BGB to the Morph Foundation in Sep 2025.
- **Audits.**
  - Aera v3: Spearbit (Jun 2025); a Cantina competition (report dated 13 Aug 2025); a managed review of Provisioner, PriceAndFeeCalculator and the Morpho-V2 adapter (17–26 Mar 2026, report 15 Apr 2026).
  - **ProvisionerV2 and PriceAndFeeCalculatorV2**, as deployed here, were renamed in the repo on 16 Jul 2026. No audit names the V2 files.
  - Morpho Vault V2: Spearbit, Zellic, ChainSecurity, Blackthorn and a Cantina competition. The Morpho Blue core on Morph is verified source; the official deployment listing was not checked.
  - **Not audited or not verified:** the reward distributor `0x53d2` (unverified source), BGBTC and MinterContract (DefiLlama "audits: 0"), and the RedStone Morph feed implementation.
- **Keys and timelocks:** see C. Summary: user funds on the BTC side are under one Bitget EOA with no timelock. Gauntlet operations are behind 6 h (1-of-1 Safe) and 24 h (3-of-7) timelocks. The USDC vault requires both Bitget and Gauntlet for ownership actions and 7 days for cap and adapter changes.

## E. Yield (see `yield_weekly.csv`; weeks measured 00:00 UTC to 00:00 UTC)

| Week from | Vault realized APY | Borrow APY | gtusdc organic | Incentives APR | Spread (org+inc−borrow) | Organic spread |
|---|---|---|---|---|---|---|
| 31 Jul | 2.63 | 3.05 | 1.48 | 14.89 | 13.32 | −1.57 |
| 7 Aug | 2.47 | 2.93 | 1.48 | 7.57 | 6.12 | −1.45 |
| 14 Aug | 2.35 | 2.92 | 1.80 | 5.04 | 3.92 | −1.12 |
| 21 Aug | 2.11 | 2.88 | 2.27 | 3.83 | 3.21 | −0.62 |
| 28 Aug | 2.18 | 2.88 | 2.30 | 3.91 | 3.33 | −0.58 |
| 4 Sep | 2.17 | 2.87 | 2.32 | 4.14 | 3.59 | −0.56 |
| 11 Sep | 2.31 | 2.87 | 2.30 | 4.20 | 3.63 | −0.57 |
| 18–21 Sep | 2.59 | 2.87 | 2.32 | 4.02 | 3.47 | −0.55 |

- **Since launch:** unit price +0.3356% over 52.9 days, which is **2.34% APY**.
- **Daily path:** the annualized rate ranged 1.74–3.08% on a daily basis after 1 Aug; no day was negative. The Gauntlet API shows a 7-day APY of 2.42% and a 30-day of 2.25%.
- **Hourly path:** the unit price fell 30 times, by up to −1.9 bp on 25 Aug. That is the negative carry accruing between reward claims.
- **Negative-carry mechanics.** gtusdc earns less than the borrow rate by construction: about 10% of supply is kept unborrowed at the 90% target, and $4–11M sits idle. The vault therefore loses about 0.3–0.5% a year of NAV on the organic leg (est.). Since launch that leg is −$29.2k: interest −$121.3k against gtusdc gain +$92.1k. It is **positive only because of incentives**: +$192.5k claimed, which became 2.608 bgBTC.
- **How "up to 3%" and "~18%" relate to the loop.**
  - The 18% was an APR on a tiny gtusdc TVL in the first days. Week 1 averaged 14.9% incentives + 1.5% organic, about 16.4%.
  - With a fixed ~$40k a week and TVL at $48–52M, it fell to about 6.3% (Morph's own 21 Aug figure: "6% APY").
  - Because the BTC vault owns about 80% of gtusdc, **about 80% of that USDC subsidy is the BTC yield**: $1.65M a year out of the $2.02M run-rate, about 2.4% on $69M NAV. Subtract the negative organic carry and about 2.1–2.3% remains.
  - Bitget passes users 1.70% because 32% of BGBTC sits idle (0.677 × 2.34% ≈ 1.58%; Bitget pays slightly more, est.).
- **Stability.** The yield is smooth because the budget is fixed in USD, but it is effectively set by Bitget's weekly campaign decision.
  - The USD budget converts to fewer BTC as BTC rises: $38.7k/week is about 0.45 BTC/week at $86k.
  - More deposits dilute the rate: a fixed budget spread over more TVL.

## F. Risk management

- **LTV path (6-hourly, `raw/ltv_path.json`).**
  - Ramp: 18% (31 Jul) → 38% (7 Aug) → 44% (14 Aug) → about 62% (from 18 Aug).
  - Since then it has held in a tight **61.9–64.1% band**; the maximum was 64.05% on 1 Sep 18:55, with BTC at $76,690.
  - The bot re-levers when BTC rises and repays when it falls. On 20 Aug, during a +13% BTC day, it cycled about 148 bgBTC of collateral out and back in hourly steps.
- **Liquidation.** The liquidation price is **$69,704**, 19.5% below $86,569. At the LTV peak the buffer was 16.8%. Liquidation incentive is 7.4%. The only liquidation so far was a 4.84-USDC test borrower on 9 Jul (liquidator contract `0xaa3c…`).
- **RedStone Atom.** RedStone describes Atom as "being enabled" and as "live". No Atom liquidation has been observed.
- **Can liquidators sell 800 bgBTC?** The only on-chain bgBTC liquidity is 22.4 bgBTC in Native, the Bitget LP. A real liquidation would leave gtusdc with seized bgBTC it cannot sell; in practice Bitget would have to absorb it (inf.).
- **Repaying the $43M is circular, and therefore easy.**
  - Real external USDC is $9.35M, held by gtusdc holders other than the vault. It sits as $4.56M idle plus $4.76M unborrowed in the market: **99.7% instantly liquid**.
  - The vault can repay the whole debt atomically. It withdraws gtusdc ($9.32M), repays, lets the allocator (or the permissionless `forceDeallocate`, 0.001% penalty) pull the freed liquidity, and repeats about 5 times, or it uses a flash loan.
  - Economically the vault holds $43.00M of gtusdc against $43.03M of debt, so its USD exposure is flat. BTC moves do not change the NAV.
- **Liquidity ladder** (`liquidity_ladder.csv`):
  - Same block: $9.32M for external USDC holders; full debt unwind for the vault.
  - About 1 h: vault-unit redemption.
  - Per day: 65 bgBTC through CCIP.
  - About 12 days: full bgBTC exit at current limits (est.).
  - For users: T+4, or instant express backed by Bitget's balance sheet and 382.6 idle BGBTC.
- **bgBTC depeg and the oracle.** The oracle is BTC/USD only. A bgBTC impairment (Bitget failure, key compromise of `0xdB25`, or unbacked minting on Morph through a new CCIP minter) **would not trigger liquidations**.
  - Loss would fall on gtusdc lenders: 82% of them is the vault itself, and $9.35M belongs to Bitget Wallet users.
  - bgBTC minting on Morph is controlled by EOA `0xdB25`, which can grant minters, with no timelock.
- **Morph bridge.**
  - bgBTC exits via CCIP: rate-limited as above, not via the canonical bridge.
  - USDC exits via Morph's canonical bridge: about 2 days finalization per L2BEAT; the docs walkthrough shows 7 days.
  - The sequencer is centralized, and upgrades by a 4-of-6 multisig have no delay.
- **Operational.**
  - The PFC ±1%/h band limits NAV manipulation by the accountant bot.
  - The reward distributor is unverified. Its root poster is an EOA, and its owner is Safe `0x72c5`.
  - Bitget suspended BGBTC–Morph deposits and withdrawals on 28 Aug.

## G. Depositors

- **The BTC vault is a Bitget omnibus**, so the relevant disclosure is Bitget's: supply 1,184 BGBTC; 801.41 in the vault (67.68%); 382.59 idle; reserves 1,420.01 (119.93%). No user count or per-user distribution is published.
- Subscriptions are quota-rationed:
  - tiers of 0.2/2/5/30 BGBTC (14 Aug);
  - 1:1 to net BTC deposits, up to 50, for 2–3 Sep;
  - 1 per 4 BTC, up to 25, for VIPs on 22–24 Sep.

  The design targets many small users; the actual distribution is unknown.
- **gtusdc holders.**
  - 1,387 holders. The vault holds 82.14%.
  - The other 1,386 are EIP-7702 wallets delegated to unverified implementation `0x490Aac77…`, likely Bitget Wallet smart accounts (inf.). They hold $9.35M together.
  - Median $32.92. 14 hold more than $100k, 122 more than $10k, and 830 less than $100. The top 10 non-vault holders have 50.2% of the external USDC.
  - 1,258 unique addresses have claimed rewards. The largest campaign had 736 claimers.
- **bgBTC holders.**
  - Morph: 28 holders. Morpho 801.71, Native 22.40, EOA `0x2620…` 9.74, Bitget hot wallet 1.16, the rest dust.
  - Ethereum: 18 holders. CCIP pool 835.02, Bitget hot wallet 348.47.

  bgBTC has no independent secondary market. See `holders.csv`.

## H. TVL growth (see `tvl_weekly.csv`)

| Date | Vault collateral bgBTC | Vault NAV $M | Debt $M | LTV | gtusdc $M (external) | bgBTC Morph / ETH supply | PoR BTC |
|---|---|---|---|---|---|---|---|
| 31 Jul | 60.1 | 3.9 | 0.7 | 17.6% | 1.9 (1.2) | 535 / 684 | 690 |
| 7 Aug | 500.4 | 32.2 | 12.1 | 37.7% | 23.5 (11.4) | 535 / 784 | 820 |
| 14 Aug | 500.6 | 31.8 | 14.0 | 44.0% | 26.5 (12.5) | 535 / 784 | 820 |
| 21 Aug | 801.0 | 58.7 | 36.4 | 62.0% | 48.5 (12.2) | 835 / 984 | 1,120 |
| 28 Aug | 801.3 | 64.3 | 40.1 | 62.3% | 50.3 (10.2) | 835 / 984 | 1,120 |
| 4 Sep | 801.7 | 65.1 | 40.7 | 62.6% | 49.5 (8.7) | 835 / 1,184 | 1,420 |
| 11 Sep | 801.0 | 61.3 | 38.5 | 62.8% | 48.0 (9.6) | 835 / 1,184 | 1,420 |
| 18 Sep | 801.5 | 61.3 | 38.4 | 62.6% | 48.0 (9.7) | 835 / 1,184 | 1,420 |
| 21 Sep | 801.7 | 69.4 | 43.0 | 62.0% | 52.3 (9.3) | 835 / 1,184 | 1,420 |

- **Pre-launch history.** BGBTC existed before this product: 1,089 minted Mar–Apr 2025, then burned down to 489 by Aug 2025. Supply ranged 489–839 between Aug 2025 and Jul 2026, and was 544 on 10 Jul 2026.
- **DefiLlama.** "bitget-bgbtc" tracks the three BTC reserve addresses. It shows about 0 BTC from 6 Feb to 18 Aug, although `19pFLW…` held 500–690 BTC then, so that address was evidently added to the adapter only around 19 Aug (inf.). It then shows $82.6M on 21 Aug and $123.5M on 21 Sep. It is BTC reserves, not the vault.
- **External USDC in gtusdc has shrunk.** It went from $12.5M (14 Aug) to $9.3M, as the incentive APR fell from 15% to 4%.

## I. Growth drivers (see `events.csv`)

- **31 Jul launch (Morph/RedStone/TipRanks) and 30 Jul Bitget article.** First 500 bgBTC deployed 30–31 Jul. This was Bitget's own allocation, not organic inflow: 500 bgBTC were bridged a day before launch.
- **3 Aug Bitget Wallet USDC option with ~18% APR.** External gtusdc grew from $1.2M to $11.4M by 7 Aug and $12.5M by 14 Aug. This was the only clearly incentive-driven third-party inflow. It has since declined with the APR.
- **7 Aug "$55M in a week" (Blockhead).** It adds $32.1M of BTC collateral to a $23.2M USDC vault that already contains the $12.1M borrowed against that collateral. Net new external capital was about $43.5M (est.).
- **14 Aug quota campaign.** BGBTC supply rose from 784 to 984. The omnibus bridged 300 on 14 Aug and deposited them on 17 Aug. **This is the last TVL step for the vault.**
- **18–23 Aug PoolX (UNI).** 25 Aug net-deposit campaign. 15 Sep VIP campaign. BGBTC supply rose from 984 to 1,184 (1–2 Sep), but **none of it reached the vault**: it sits idle at the Bitget hot wallet on Ethereum (348 bgBTC).
- **Morph incentives.** None identified on-chain for this product; all traced incentive USDC came from Bitget.
- **Gauntlet curator framework.** Brand and marketing effect; no measurable TVL step.
- **CCIP adoption.** Enabling only. The bridging bursts were controlled by the owner EOA lifting rate limits.
- **What moved TVL.** (1) Bitget's decisions to allocate BGBTC (30–31 Jul and 14–17 Aug). (2) BTC price: +18% from $73.3k on 21 Aug to $86.6k on 21 Sep explains all USD growth since 21 Aug (+34% since the 31 Jul launch at $64.7k). (3) For the USDC side, the incentive APR.

## J. Economics

- **Fees.**
  - Aera vault: 0% TVL and 0% performance (PFC `VaultAccruals`).
  - gtusdc: 0% management and 0% performance.
  - Morpho market fee: 0.
  - Gauntlet's compensation is **off-chain and undisclosed**.
  - Bitget's spread: the vault earns about 2.34% on 67.7% of supply, and Bitget pays 1.70% on 100%. The user payout slightly exceeds vault income (≈20.1 BTC vs ≈18.8 BTC a year), so Bitget appears to top up (est.).
- **Incentive spend (on-chain).**
  - $287,016 USDC over 7 campaigns (29 Jul–22 Sep). The run-rate is **$38.7k/week, about $2.02M a year**.
  - Funded from Bitget's hot wallet.
  - $233.5k claimed, of which the vault took $192.5k (82.4%).
- **Cost per $ of TVL (est.).**
  - $2.02M/yr ÷ $121.75M headline TVL = **1.66%**.
  - ÷ $78.75M net external capital = **2.56%**.
  - Only about 18% (≈$0.36M/yr, plus about $0.2M/yr of interest leakage) reaches third parties. That is **≈6% a year on $9.35M of genuinely external USDC**.
  - The rest (≈$1.65M/yr) is Bitget paying its own BTC vault, which is then passed to BGBTC holders.
- **In substance (est.).** Bitget runs about 1.7–2.0% a year of BTC yield for BGBTC holders out of its own USDC budget. The DeFi loop adds a small net cost: the external holders' share plus negative organic carry. It gains verifiable on-chain rails and about $90M of Morph TVL (DefiLlama: Morpho on Morph $78.6M, Aera $69.3M; Morph chain TVL went from $9.5M on 1 Aug to about $92M).

## K. Verdict: copy and avoid

**Copy**
- The Aera v3 accounting pattern:
  - on-chain unit price pushed hourly within a hard ±1% band and a 90-day staleness limit;
  - async deposits and redeems solved by the guardian;
  - 0/0 on-chain fees with transparent NAV;
  - a Gauntlet API with 7d and 30d APY.
- Tight LTV band management: 62% target versus 77% LLTV, adjusted in both directions.
- A USDC vault where ownership needs both parties (2-of-2 of Bitget and a Gauntlet 4-of-7), with 7-day cap and adapter timelocks and gates abdicated.
- Chainlink PoR plus a public vault API that reconciles to the satoshi with the exchange's own dashboard (801.41).
- Quota-rationed subscriptions to keep the yield from being diluted.

**Avoid**
- Presenting a closed loop as "institutional DeFi yield". The borrower, the main lender and the incentive payer are the same group. Organic carry is negative. Headline TVL double-counts about $43M.
- Incentives funded by the distributor itself and routed through an unverified contract. Disclose the funder and the budget.
- A single EOA owning the token on two chains, the CCIP pools and rate limits, and the vault, with no timelock. Minting without an on-chain PoR check.
- Oracle pricing the wrapper as BTC with no wrapper/BTC leg, and no deep bgBTC liquidity for liquidators.
- A bridge exit throttled to 65 bgBTC/day, while the exchange rail (BGBTC–Morph) has been suspended since 28 Aug.
- Advertising "up to 3%" and "~18%" when the steady state is about 2.3% (vault), 1.70% (paid) and about 6% (USDC).

---

### Corrections vs `BTC-Carry-Vaults-Dossiers.md` §4.4 and dossier-peers §3

1. "The subsidy is paid by L2 Morph": **not supported on-chain.** All traced incentive USDC came from Bitget's hot wallet.
2. "LTV 62–67%": the observed 6-hourly range since 18 Aug is **61.9–64.1%**. The 67% figure paired today's debt with an older, lower BTC price.
3. "$121.8M DefiLlama" is **BTC reserves** (1,420 BTC). Product TVL is the vault NAV ($69.4M, 801.4 BTC).
4. "Realized yield not verified": now verified. **2.34% APY** since 31 Jul, from on-chain unit price.
5. "Fees not published": the on-chain fees are **0/0/0**. Redemption: T+4 standard; express 0.1%.

### Files
- `deepdive.md` (this report)
- `tvl_weekly.csv`
- `yield_weekly.csv` (full decomposition in `raw/yield_detail.json`)
- `liquidity_ladder.csv`
- `holders.csv`
- `events.csv`
- `scripts/`:
  - `rpc.py`, `bs.py`, `blocks.py`, `morphoev.py`, `abidec.py`
  - `fetch_all.py`, `state_now.py`, `snap.py`, `weekly.py`, `yields.py`, `swaps.py`, `ltv_path.py`, `pfc_decode.py`, `por.py`, `eth_supply.py`, `governance.py`
  - `build_tvl.py`, `build_misc.py`, `build_events.py`
- `raw/`: on-chain pulls and `raw/web/` pages.
