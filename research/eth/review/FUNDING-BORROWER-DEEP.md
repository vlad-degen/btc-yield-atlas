# What the largest ETH-backed dollar borrowers actually do

The largest measured borrowers are not automatically the largest carry investors. Following their cash reveals dollar conversion, transfers to external wallets and repayment of existing debt. Those uses belong in the funding landscape, but they do not establish a yield investment or its return.

This review uses the frozen **2 October 2026, 23:59:59 UTC** snapshot, Ethereum block **26,108,081**. Public contract labels and verified source discovery were captured on **4 October** and are dated separately. The [structured exhibit](../../../data/eth/funding_borrower_deep_chapter.json) contains exact loan units, account collateral boundaries, historical owner calls, ordered receipts and source hashes.

## First separate a pool account from a borrower address

The underlying screen measures 350 material venue-account rows with at least $1M of selected dollar debt and enabled ETH-family collateral. All 15,704 requested fixed-T calls succeeded, and all 350 selected account views are complete. Discovery begins with bounded current holder pages. It can miss borrowers that exited after T, so this is an observed sample rather than the full borrower universe.

A wallet can borrow from both Aave and Spark. Ranking each pool account separately places the largest Aave row at $126.067M. Combining distinct pool liabilities for the same chain-address reveals two larger borrowers: **$212.364M** at `0xd848...f452` and **$205.877M** at `0x9992...f242`. This sum combines liabilities only. Each pool still has its own collateral, liquidation threshold and health factor.

Dollar marks use each venue's asset-specific oracle at T. USDC, USDT, DAI and other dollar assets are not all forced to exactly $1. Selected dollar liabilities can coexist with other collateral or other debt. They cannot be allocated to ETH using a proportional assumption. The [frozen atlas input](../../../raw/eth/funding-borrower-deep-2026-10-04/input_funding_atlas-94d1d4e9dc321477.json) preserves both selected token positions and the broader account totals.

| Unique chain-address rank | Borrower | Selected dollar debt, USD | Venues | Control measured at T |
|---|---|---:|---|---|
| 1 | [0xd848...f452](https://etherscan.io/address/0xd848f54280f8fe8661b796e3bb8d8922c87af452) | $212.364M | Aave and Spark | DSProxy with an owner address |
| 2 | [0x9992...f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | $205.877M | Aave and Spark | Safe, 1 required signature from 1 owner |
| 3 | [0x741a...31f3](https://etherscan.io/address/0x741aa7cfb2c7bf2a1e7d4da2e3df6a56ca4131f3) | $126.067M | Aave | No deployed code |
| 4 | [0xed0c...4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | $125.347M | Spark | No deployed code |
| 5 | [0xb99a...bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | $115.405M | Spark | No deployed code |
| 6 | [0x28a5...a6b0](https://etherscan.io/address/0x28a55c4b4f9615fde3cdaddf6cc01fcf2e38a6b0) | $112.194M | Aave and Spark | No deployed code |
| 7 | [0x7ee2...5178](https://etherscan.io/address/0x7ee29373f075ee1d83b1b93b4fe94ae242df5178) | $105.736M | Aave | Safe, 3 required signatures from 5 owners; shared Concrete execution account |
| 8 | [0xe40d...03bf](https://etherscan.io/address/0xe40d278afd00e6187db21ff8c96d572359ef03bf) | $86.535M | Aave | Safe, 2 required signatures from 5 owners |
| 9 | [0x2835...62b1](https://etherscan.io/address/0x28355886a65848488cf0a3646fca395db0a762b1) | $84.180M | Spark | No deployed code |
| 10 | [0x3a0d...97d9](https://etherscan.io/address/0x3a0dc3fc4b84e2427ced214c9ce858ea218e97d9) | $79.442M | Spark | InstaAccountV2 clone; authorized users unresolved |

The 10 venue-account ranking is exported separately in the [CSV](../../../data/eth/funding_borrower_deep_rankings.csv). The repeated addresses in that ranking are real distinct pool positions, not additional unique borrowers.

## Contract identity is stronger than a guessed company name

Fixed-T bytecode and ownership calls identify one DSProxy, three Safe proxies, five addresses with no deployed code, and one InstaAccountV2 clone. The DSProxy has one returned owner address. The three Safes expose their signer sets and required signature thresholds. These calls identify control addresses, not legal owners. Safe modules, guards and all other authorization paths were not enumerated, so a signature threshold alone is not a complete control audit.

The InstaAccount's T clone code points to the verified `InstaAccountV2` implementation. Generic `owner()` and Safe ownership selectors revert. This does not prove that the account has no authorized users; its authorization system needs different selectors and records. It is left unresolved.

The owner of the largest Safe has EIP-7702 delegation code at T, pointing to `EIP7702StatelessDeleGator`. It should not be described as a plain wallet with no code. No legal entity behind either traced owner was verified.

There is one exact known product match. `0x7ee2...5178` is returned by the Concrete strategy's `getMultiSig` call at T. It is a **shared execution account, attribution unresolved**. Its $105.736M of selected Aave dollar debt cannot be assigned entirely to Delta or wstETHPlus and cannot be added to product NAV as new capital. The [Concrete route evidence](CARRY-VARIANTS-EXPANSION.md) preserves this distinction.

## DSProxy: sampled dollar borrowing precedes a Maker repayment

The largest unique borrower has separate Spark and Aave health factors of **2.167813** and **2.149257** at T. These values describe the respective pools, not a pooled account.

Its owner is [`0x7d61...41b4`](https://etherscan.io/address/0x7d6149ad9a573a6e2ca6ebf7d4897c1b766841b4). Four sampled borrowing transactions verify new principal of 3,000,000 USDT, 5,000,000 USDC and 5,000,000 USDS. In every transaction, the underlying moves from the lender's aToken to the DSProxy and then to this owner. The receipt proves each first hop with the same currency, amount and transfer order.

Three of these loans occur on 30 September. The owner then sends their currencies to one unlabelled external address, [`0x1c11...3bc5`](https://etherscan.io/address/0x1c11ba15939e1c16ec7ca1678df6160ea2063bc5).

| Time on 30 September, UTC | Measured cash movement | Evidence |
|---|---|---|
| 06:24:23 | Owner sends 3,000,000.000200 USDT to the external address | [USDT receipt](https://etherscan.io/tx/0x00040a8a82663df5182f016437c63e3bcc6f331ee60769664d0b359c1ab4cd63) |
| 06:24:59 | Owner sends 5,000,000 USDS to the same address | [USDS receipt](https://etherscan.io/tx/0x5e15e6d5bdd0cb345c94aaae5cd88f87488e96174fd8ce0f34e1ad28151fde57) |
| 06:25:59 | Owner sends 1,000,000.001210 USDC to the same address | [USDC receipt](https://etherscan.io/tx/0x730118790e05193fd925abd1971808458545d6da06876dc74fec07d6081240e5) |
| 06:36:47 | External address sends 8,695,638.564718991967544147 DAI to the owner | [DAI receipt](https://etherscan.io/tx/0x0126e61bdc9052e2e8d4beca9a32441514de1db9c08e1a4d50f3deb82a5fca70) |
| 06:38:59 | Owner supplies 8,678,761.525602902876553977 DAI to the DSProxy; the DSProxy burns the same amount in a Maker payback | [Maker repayment receipt](https://etherscan.io/tx/0x897ec0dae37a3bf12da50e036356c9f92ac5e9cbf666c0dd1fd13ac75ec349c5) |

The repayment uses the verified `McdPayback` action, whose captured source bytecode matches its code at T. Maker logs identify vault **31,214**, collateral type **ETH-C**, and an actual decrease in normalized debt. The DAI owner-to-proxy transfer precedes an equal DAI burn in the same receipt.

This is a concrete refinancing sequence: dollar loans, a transfer through an external wallet, a DAI return and repayment of existing Maker debt. The external wallet's conversion agreement and full cash history remain unknown. We do not treat the nominal difference between dollar-token amounts and DAI as an exchange fee, a profit or a loss. The 24 September 4,000,000 USDC loan is verified only through its owner hop in this bounded trace. Neither the sample nor the refinancing sequence explains the use of all $212.364M of outstanding selected dollar debt.

## Safe: a loan-funded USDC-to-USDT conversion, then an external payment

The second-largest unique borrower is a Safe with one owner and a threshold of one. Its separate T health factors are **1.857750** on Aave and **1.336275** on Spark. The owner address is [`0x54d2...6029`](https://etherscan.io/address/0x54d250405d22e858d125ce2c1affc7d73afe6029).

On 26 September at 01:05:59 UTC, the Safe borrows **6,862,300 USDC** from Aave and sends the complete new principal to its owner in the same transaction. Immediately before the loan block, the owner's measured balance is **12.398204 USDC**. After the loan block it is **6,862,312.398204 USDC**. [Loan receipt](https://etherscan.io/tx/0xb8e2a05fa7ce638258d1e1f20088645369203851105468162ab185ca8e023c2b).

Between 01:08:11 and 01:42:47 UTC, **19 CoW settlement transactions** sell exactly **6,862,312.398204 USDC** and return **6,862,475.911340 USDT** to that owner. The aggregate USDC sales equal the loan plus the measured opening balance exactly. Each settlement's primary `Trade` event names the owner, the USDC sell token, the USDT buy token and both amounts. Canonical underlying transfers verify the owner's USDC debit and USDT receipt. All 19 receipts are exported in `traced_accounts[1].dollar_conversion.settlements` in the [dataset](../../../data/eth/funding_borrower_deep_chapter.json).

The owner already has **3,154,764.749982 USDT** immediately before the loan block. It later sends **100 USDT** as a test, then **10,014,900 USDT** to [`0x2a28...bfe5`](https://etherscan.io/address/0x2a28632f061a7558252441564d6bc1ec0c29bfe5). These final payments combine converted proceeds with existing USDT. The exact share funded by the new loan is not assigned to each individual payment. The recipient has no verified public legal-entity label in the captured primary index. [Test payment](https://etherscan.io/tx/0x46a9e43de5d17f3fd348a308e3f3e1d8c32ce7a776ec4ac36d22ab2680e4ddad), [main payment](https://etherscan.io/tx/0xaaa77e9f37ab49e1fc91000bf29df0e164f7ed8392477a54086d7b489fdbbeef).

The measured use is a dollar-token conversion followed by an external-wallet transfer. This trace does not establish an ETH purchase, a yield deposit, a centralised exchange account or a basis trade. It cannot measure income earned after the payment leaves the observed wallet.

The nominal USDT received exceeds the nominal USDC sold by **163.513136 token units**. That is a comparison between different dollar tokens, not a measured USD profit or an annual return. The `Trade` fee fields are zero, but this does not prove that price-embedded fees, gas or all execution costs are zero. Two additional sampled Spark loans, **9,653,000 USDS** on 10 September and **2,174,000 USDS** on 11 September, are verified through their direct owner hop. Their subsequent investment use remains unresolved.

## Debt-token mints can overstate newly borrowed cash

The 30 September DSProxy USDT transaction mints **3,223,198.640147 variable-debt USDT** while transferring only **3,000,000 USDT** of new underlying cash. The `Mint` event separately records **223,198.640146 USDT** of accrued balance increase; one additional base unit, **0.000001 USDT**, is a rounding difference. Treating the mint as loan principal would overstate new funding by **223,198.640147 USDT**. The primary `Borrow` event and the underlying cash transfer provide the actual principal. [Transaction evidence](https://etherscan.io/tx/0x9e563c3d6155b1cf734f08ec3dff4462a8f60b2b4ca2bde8895e5ef4129c8ecf).

This distinction matters in borrower attribution. Debt growth includes financing cost. It is not necessarily new cash, and it is never evidence of an investment return by itself.

## Evidence coverage and reproducibility

The study verifies **seven sampled new loans**, all seven complete same-transaction owner cash links, **eight downstream receipts** and **19 CoW settlements**. These are representative cash paths, not a full history of borrowing or a coverage percentage of outstanding debt. No closed carry-income ledger is claimed for either unidentified account.

The public RPC rejected broad historical log queries because it permits a maximum ten-block range. Those failures remain in the raw capture. They are not interpreted as zero loans. An indexed debt-token mint page supplies bounded discovery; archived primary receipts verify the actual loan events and cash amounts.

Canonical token addresses are essential. The unfiltered transfer index includes fake tokens sharing familiar symbols, zero transfers and tiny incoming amounts. The Safe's meaningful USDC conversion appears in a canonical-token filtered page. Only the actual USDC and USDT contracts, positive receipt cash movements and matching settlement events enter the conversion ledger.

Run the offline builder:

```sh
python3 tools/eth/funding_borrower_deep_build.py
```

It currently passes **306 checks**. These verify captured body hashes, immutable input hashes, all 350 selected states, measured code for the top 10 unique borrowers, primary loan cash links, explicit accrued-interest Mint fields and base-unit rounding, successful pre-T receipts, every CoW owner debit and receipt, the exact USDC loan-plus-opening-cash reconciliation, the Maker pull and burn, an actual decrease in normalized Maker debt, and verified action and implementation bytecode at T. No network is needed to rebuild the [JSON](../../../data/eth/funding_borrower_deep_chapter.json) and [ranking CSV](../../../data/eth/funding_borrower_deep_rankings.csv). All public raw requests, source URLs, capture times and SHA256 hashes are recorded in the [raw manifest](../../../raw/eth/funding-borrower-deep-2026-10-04/requests.jsonl).

For presentation, classify these two traces by observed use: **refinancing sequence** and **dollar conversion with external transfer**. Keep their full measured debt visible in the funding table and their unresolved investment use visible beside it. They demonstrate why ETH-backed dollar credit is a larger category than proven carry investment.
