# Concrete Delta weETH: who owns the 307k ETH

Snapshot T = **2 October 2026, 23:59:59 UTC**, Ethereum block **26,108,081**. All reads are read-only `eth_call` at the stated block (Tenderly public gateway and dRPC), or Blockscout/Etherscan indexes captured on 7 October 2026. ETH/USD display quote $2,667.9504418816. weETH rate at T **1.104943034**, wstETH `stEthPerToken` **1.245401879**. Machine-readable ledger: [gap_concrete.json](../../../../data/eth/gap_concrete.json). Raw captures: [raw/eth/gap-2026-10-07/concrete/](../../../../raw/eth/gap-2026-10-07/concrete/).

## Verdict

- **The ETH exists.** At T the execution Safe holds **307,227.7 ETH** of weETH and wstETH collateral. Delta's book is **307,362.9 ETH**, so the Safe covers 99.96% of it. The prior "41% unmapped" result left out the Safe's Morpho collateral.
- **The capital comes from one principal, not a pool of outside investors.** On 10 December 2025 the Safe absorbed the whole Aave position of wallet `0xc6badce2…`: 246,740 wstETH of collateral and about $499M of USDT debt. That wallet's 300,000 ETH came from long-dormant wallets funded in 2016–2017 by the address Etherscan labels **"Bitfinex 1"**. In September 2025 EmberCN publicly reported the wallet as Bitfinex-linked. The same wallet was the Safe's only owner from 30 November to 2 December 2025. At T it is still one of the five signers.
- **The strategy.** It holds 307k ETH of LST collateral on Aave v3 and Morpho. Against it, it borrows **$176.15M** of USDT, USDC and PYUSD, a combined loan-to-value of **21.5%**. The borrowed dollars go into Theo thBILL and thUSD, Concrete ctDefiUSDT and s0xUSD, plus about $24M sent to other chains or Safes. It also rotates between weETH and wstETH. No arbitrage venue, hedge or profit distribution is visible on-chain. Delta's book is fixed at 278,170.83 weETH: it does not subtract the stablecoin debt and does not mark the dollar leg.
- **How to count it once.** Show it as one **single-principal managed mandate of about 307.2k ETH**, not as a pooled ETH yield product. Its carry sleeve is the **$176.15M dollar loan**, not the 307k ETH. Exclude ctwstETH+ completely (**45,382 ETH**): it is Delta's own ETH re-wrapped by the Safe. DefiLlama's **352,861 ETH** therefore double counts **45,382 ETH (12.9%)**.

## 1. Holder 0x5bab73… is an unused custody EOA

[`0x5bab73f561a5365c9e4bbc7c52fe0fa384fcf324`](https://etherscan.io/address/0x5bab73f561a5365c9e4bbc7c52fe0fa384fcf324)

- It is an EOA. At T its nonce is **0**, its ETH balance is **0**, and it has no code. Its whole history is **one** token transfer: 278,170.834212774 ctDeltaWeETH received in the [mint transaction](https://etherscan.io/tx/0xce658f57edc490798ddc55e3f67169e3190fe23afe50a4ce4ca411d0714edada) on 16 December 2025 (block 24,024,905).
- It has no Etherscan or Blockscout label. It is not a contract, bridge, exchange or Concrete vault.
- It fits a cold custody address, but because it never transacted it cannot be linked on-chain to the principal.
- Sources: [address](../../../../raw/eth/gap-2026-10-07/concrete/holder_addr.json), [counters](../../../../raw/eth/gap-2026-10-07/concrete/holder_counters.json), [RPC at T](../../../../raw/eth/gap-2026-10-07/concrete/holder_rpc_T.json).

The economic source of the shares is the principal wallet [`0xc6badce2…4699c7`](https://etherscan.io/address/0xc6badce2f5e10db90d74dbe023768259ec4699c7), which received 300,000 ETH in three transfers:

| Date (UTC) | ETH | Immediate sender | Upstream |
|---|---:|---|---|
| 2025-09-26 12:51 | 100,000 | [`0x0a4c79ce…`](https://etherscan.io/tx/0x7d6bf26c3a832feefa85d29647d8bb7d9123ae1ff36bf69a08f5df5de2b16289) | Funded 17 Apr 2017 with 165,254 ETH from `0xb45a9436…`, itself funded Mar–Apr 2017 by **Bitfinex 1** `0x1151314c…` ([tx](https://etherscan.io/tx/0x836965e6f6e2254d5873b03314dd35152acd34009abda500200f5b97ed0ad8f7)) |
| 2025-09-26 13:45 | 100,000.5 | [`0x057f88dd…`](https://etherscan.io/tx/0x75412bdf2dc08023cee7256b2f1a1636e2915199ebd5b90310e243bcc9c1306f) | ← `0xbf3aeb96…` ([tx](https://etherscan.io/tx/0xadbe81aa9f3472f69f87ba1f8d71d08f80b3ad694a4b5c91bbcba561e1a440b1)), funded 26 Mar 2017 with 187,063 ETH by `0xcf690d4b…`, which was fed by Bitfinex 1 in 2016–2017 ([tx](https://etherscan.io/tx/0xec978d838f3e2883a32e63a98cf91b96961474167485fdee12ec3fdbcc075270)) |
| 2025-10-24 00:36 | 99,998 | [`0xf7a2d744…`](https://etherscan.io/tx/0x6352ad8df655bf9cbbeda8ae55ee6e074bb992e0e349907613e13150b3bfadac) | ← `0x0a4c79ce…` ([tx](https://etherscan.io/tx/0x69cca42680114fab956c5a07e460dea93dc2aeb3f5f7a1be61ccaadf67d62948)) |

- `0x0a4c79ce…` still held about 54k ETH on 7 October 2026, and `0xbf3aeb96…` about 87k ETH.
- Press: EmberCN on 26 September 2025 reported that 0xc6b…9c7 received 100,000 ETH from an address "suspected to belong to Bitfinex", and that it was unclear whether the funds belonged to users or to Bitfinex ([TechFlow](https://www.techflowpost.com/en-US/newsletter/100072), [Blockchain.News](https://blockchain.news/flashnews/bitfinex-linked-100-000-eth-moved-to-aave)).
- The address labels come from Etherscan page titles captured on 7 October 2026 (for example, [Bitfinex 1](../../../../raw/eth/gap-2026-10-07/concrete/etherscan_0x1151314c646ce4e0efd76d1af4760ae66a9fe30f.html)).

**What the principal did before Delta (Sep–Nov 2025).** It staked the ETH in Lido, supplied wstETH and WETH on Aave, and borrowed USDT: **$201M by end-September** and **$499.6M by end-October**.

- In September it sent about $200M into the Plasma USD pre-deposit (`depositAndBridge`).
- On 23 October it sent USDT through deposit addresses to the hot wallet labelled **BTSE 1** (`0xbb4d1dc5…`). BTSE 1 then funded 11 fresh wallets that deposited **$499.26M** into Concrete's Stable pre-deposit vault ctStableUSDT.

## 2. The Safe's ETH is exactly the migrated position

The Safe [`0x7ee29373…`](https://etherscan.io/address/0x7ee29373f075ee1d83b1b93b4fe94ae242df5178) was created on 30 November 2025 (block 23,913,931). Its owner history:

- **Block 23,914,197:** ownership set to **1-of-1 `0xc6badce2…`** ([tx](https://etherscan.io/tx/0xaa8f55788904490923a969ab547c06e9f08cb2e976783bffb02f148b703b9590)).
- **2 December:** `0xc6badce2…` itself executed the change to **3-of-5**, adding four unlabelled EOAs ([tx](https://etherscan.io/tx/0xb36f83c1a895223a0da52dc8370b6cb09d4a7c4b3adb3067b6d68d6f9e04a3af)).
- None of the five signers sits on Concrete's owner Safe (`0x8f5f1d40…`, 1-of-2) or on the setup Safe (`0x70ebf87b…`, 2-of-3) ([owners at T](../../../../raw/eth/gap-2026-10-07/concrete/)).

Timeline of how the position entered the Safe:

1. **2 Dec 2025:** the 11 depositor wallets transfer their 499.26M ctStableUSDT receipts into the Safe.
2. **10 Dec 2025, block 23,984,118** ([tx](https://etherscan.io/tx/0x54fa78b045b3cbddad15681b217f84745e7efe23fb097e5be5dd13197926ec37)): the Safe pulls **246,740.152 aWstETH** from `0xc6badce2…`. A helper contract (`0xe051fb91…`) unwraps it to **301,384.067 stETH** and deposits that into ether.fi as **278,170.831 weETH**, which lands in the Safe as aWeETH. It borrows **$502.38M USDT** on the Safe to repay **$498.99M** of the principal's debt. The same day the 499.26M ctStableUSDT is burned ([tx](https://etherscan.io/tx/0xc245f6c70912ff0060b2da3ffb3a351a4b047e11d70467ee507e65c95e564c19)).
3. **16 Dec 2025, 11:35:** Delta `unbackedMint` of **278,170.834 shares** to holder `0x5bab73…`. This equals the migrated weETH within 0.003 weETH. Strategy `AdjustTotalAssets` is at nonce 1, and `getNextAccountingNonce` = 2 at T, so the book has been set once and never re-marked.
4. **16 Dec 2025, 17:15–19:08:** **499.88M USDT** arrives from the USDT0 OAdapter, bridged back from Stable ([tx](https://etherscan.io/tx/0x499b7a74430a7f1da324878a2d7ae727611f226332ec42d22ec90e3bafa5a2b5)), and repays **499.48M** of the debt ([tx](https://etherscan.io/tx/0x5d1fa825f27ca8c55047da84d7c1e289c9e36314c1db3d28370b0b2b499b1543)).

**Later movements stay inside the Safe.**

- **Into ETH and Lido:** 61,100 weETH went through ether.fi WeETHWithdrawAdapter (5 Feb and 6 Mar 2026). It came back as ETH and was staked in Lido as 44,698 + 21,794 stETH ([10 Feb](https://etherscan.io/tx/0xb787e5f06f855924f51e9e7434253696809f11b659447ed7cd2709fe59aa538b), [20 Mar](https://etherscan.io/tx/0x20193e3a92af847f5fd86e4249b8c123733765317cd89b10e878256ba6f469f7)).
- **Into Morpho:** 217,071 weETH was redeemed through EtherFiRedemptionManager for stETH (25 Mar and 1 Apr), wrapped, and posted as Morpho wstETH collateral.
- **Back to Aave:** from June to September, wstETH moved from Morpho to Aave and was partly swapped back to weETH.

No ETH-family inflow from any other party was found in the [386 Safe token transfers](../../../../raw/eth/gap-2026-10-07/concrete/safe_flow_summary.txt).

**Fixed-block balance sheet at T** ([reads](../../../../raw/eth/gap-2026-10-07/concrete/fixed_block_reads_T.json)):

| Line | Native | ETH | USD |
|---|---:|---:|---:|
| Aave aEthweETH | 123,978.982 weETH | 136,989.7 | |
| Aave aEthwstETH | 41,612.010 wstETH | 51,823.7 | |
| Morpho wstETH/USDT collateral | 95,070.479 wstETH | 118,401.0 | $315.89M |
| Wallet weETH | 12.05 | 13.3 | |
| **ETH-family collateral** | | **307,227.7** | **$819.67M** |
| Aave debt (USDT 65,474,274.98 + USDC 40,275,257.31) | | | −$105.75M |
| Morpho wstETH/USDT debt, accrued to T | | | **−$70,398,363.15** |
| Ethereum dollar claims (thUSD 46.29M, ctDefiUSDT $26.18M, s0xUSD $10.39M) | | | +$82.86M |
| Dollar outflows that left Ethereum (thBILL 98.43M via OFT adapter on 29 Jan; 10M USDT via USDT0; 14M to two other Safes) | | | not valued |

**4. Morpho debt exactly at block 26,108,081.** Market [`0xe7e9694b…87d2`](https://app.morpho.org/ethereum/market/0xe7e9694b754c4d4f7e21faf7223f6fa71abaeb10296a4c43a54a7977149687d2) (wstETH/USDT, 86% LLTV).

- Position: borrowShares 60,860,017,055,423,129,847; collateral 95,070.479149784 wstETH.
- Debt at the stored market totals: 70,398,322.72 USDT.
- Accrued 564 s to T at the IRM rate (3.2108% APR): **70,398,363.15 USDT**.
- The wstETH/PYUSD market position is zero.
- [Computation](../../../../raw/eth/gap-2026-10-07/concrete/morpho_debt_T.json)

**Corrected backing.**

- Adding the omitted Morpho net position (**+$245.49M**) to the earlier $480.62M Ethereum reconstruction gives **$726.11M**. That leaves **$93.92M** (11.5%) of book unmapped.
- The unmapped amount is smaller than the **$122.4M** of dollar outflows that left Ethereum, so no shortfall is indicated. Off-chain value is not verified.
- Mixed price bases: Aave is valued at the protocol oracle, Morpho collateral at the LST rate × display quote, and dollar claims at nominal $1.

## 3. Concrete products sharing the Safe

A scan of all 23 Ethereum Concrete vaults with API TVL above $1k checked each vault's strategies for `getMultiSig()` at T ([scan](../../../../raw/eth/gap-2026-10-07/concrete/concrete_vault_strategy_multisigs_T.json)). Only two vaults point at this Safe:

| Vault | Book at T | Notes |
|---|---:|---|
| ctDeltaWeETH | 278,170.834 weETH = 307,362.9 ETH | Sole holder `0x5bab73…` |
| ctwstETH+ [`0xd57588c7…`](https://etherscan.io/address/0xd57588c73715b65e0ead36ae06c15644169501b7) | 36,439.686 wstETH = **45,382.1 ETH** ($121.08M) | 100% held by the Safe. Funded from Delta's own weETH (41,100 weETH → ETH → Lido → wstETH), [deposited](https://etherscan.io/tx/0x5167dd6022a361f61e0feed5f1afd4b046978e78dd8fac6ea69634690b8c3722) and [allocated back](https://etherscan.io/tx/0x059e196a9e06a9bc86f1b33d2206afca708cf4c25095d1daa66e3dbb78051d19) to the Safe on 25 Feb 2026, then moved to Morpho on 4 Mar |

The Safe also holds 24.95M ctDefiUSDT shares. That vault uses a different multisig (`0xf67ace04…`), so it is a destination claim, not a sibling book.

## 5. DefiLlama

- **Adapter:** [`projects/concrete-xyz/index.js`](https://github.com/DefiLlama/DefiLlama-Adapters/blob/main/projects/concrete-xyz/index.js), last commit 790fae3462 on 22 Sep 2026 ([copy](../../../../raw/eth/gap-2026-10-07/concrete/defillama_adapter_concrete-xyz_index.js)).
- **Method:** it sums `totalAssets()` (falling back to `cachedTotalAssets()`) for every vault listed by Concrete's TVL API. It skips only vaults whose *asset* is another Concrete vault and does not look through strategy custody.
- **ETH-family at T:** 278,170.83 weETH + 36,532.87 wstETH = **352,861 ETH**. The wstETH is ctwstETH+ (36,439.69) plus the Royco wstETH wrapper (93.18).
- **Double count:** ctwstETH+'s **45,382 ETH (12.9%)** is already inside Delta's ETH.
- **Precision:** Royco's 116 ETH is a separate product, but it duplicates a Royco row if the map also counts Royco.
- **Separate error:** Delta's totalAssets does not subtract $176M of stablecoin debt, so the USD TVL is gross collateral rather than equity.
- Source: [DefiLlama capture](../../../../raw/eth/2026-10-02/protocol_concrete-c8b1742ee36108df.json).

## 6. Public documentation

- The Concrete app lists "WeETH Vault" as permissioned, with private APY, a stated strategy of stablecoin borrowing against weETH into "delta-neutral arbitrage", a 7-day withdrawal delay and 30 days to yield ([UI observation, 3 Oct](../../../../raw/eth/2026-10-02/concrete_ui_observation.json)). The API names it "Concrete Delta WeETH" and reports peak TVL of $1.014B ([API](../../../../raw/eth/gap-2026-10-07/concrete/concrete_api_tvl_all.json)).
- No Concrete, ether.fi or Blueprint announcement names the client or the investors.
- The only public attribution is the EmberCN Bitfinex report cited above.
- No deposit, withdrawal request or claim exists on the vault since the mint ([prior event census](../../../../raw/eth/research-closure-2026-10-04/exit/concrete_exitlogs_T.json)).

## 7. Monthly book history, October 2024 – September 2026

Month-end blocks are the study's existing ones ([reads](../../../../raw/eth/gap-2026-10-07/concrete/fixed_block_reads_monthly.json), [derived](../../../../raw/eth/gap-2026-10-07/concrete/monthly_book_table_derived.json)). Morpho debt here uses stored market totals.

| Month | Block | Delta book ETH | ctwstETH+ ETH (internal) | Safe ETH-family ETH | Safe stable debt $M | Precursor wallet ETH | Precursor USDT debt $M |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024-10 … 2025-08 | 21,089,068 … 23,264,565 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2025-09 | 23,479,243 | 0 | 0 | 0 | 0.0 | 200,012 | 201.2 |
| 2025-10 | 23,700,766 | 0 | 0 | 0 | 0.0 | 300,511 | 499.6 |
| 2025-11 | 23,914,920 | 0 | 0 | 0 | 0.0 | 301,172 | 501.7 |
| 2025-12 | 24,136,052 | 301,799 | 0 | 301,799 | 68.0 | 0 | 0.0 |
| 2026-01 | 24,358,292 | 302,425 | 0 | 302,425 | 128.3 | 0 | 0.0 |
| 2026-02 | 24,558,867 | 303,007 | 44,752 | 302,990 | 128.7 | 0 | 0.0 |
| 2026-03 | 24,781,026 | 303,643 | 44,848 | 303,602 | 129.7 | 0 | 0.0 |
| 2026-04 | 24,996,367 | 304,265 | 44,940 | 304,223 | 155.1 | 0 | 0.0 |
| 2026-05 | 25,218,797 | 304,866 | 45,033 | 304,858 | 160.6 | 0 | 0.0 |
| 2026-06 | 25,433,938 | 305,491 | 45,123 | 305,465 | 174.6 | 0 | 0.0 |
| 2026-07 | 25,656,292 | 306,121 | 45,208 | 306,040 | 174.9 | 0 | 0.0 |
| 2026-08 | 25,878,704 | 306,738 | 45,293 | 306,615 | 175.5 | 0 | 0.0 |
| 2026-09 | 26,093,737 | 307,322 | 45,377 | 307,189 | 176.1 | 0 | 0.0 |
| T | 26,108,081 | 307,363 | 45,382 | 307,228 | 176.1 | 0 | 0.0 |

Delta's ETH book rises only through the weETH exchange rate. In every month the Safe's ETH equals Delta's book and also contains ctwstETH+.

## Limits

- The Bitfinex attribution rests on Etherscan's "Bitfinex 1" label, 2016–2017 funding paths and press reports. It does not show whether the funds belong to Bitfinex itself, an affiliate or exchange customers.
- The holder `0x5bab73…` cannot be linked on-chain to `0xc6badce2…`.
- The identities of the four other signers are not public.
- The value and destination chain of the thBILL that left Ethereum, and of the other dollar outflows, were not verified.
- Private agreements on fees and payouts remain unknown.
