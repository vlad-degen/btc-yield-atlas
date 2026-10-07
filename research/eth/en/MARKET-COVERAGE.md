# Coverage of the ETH yield market

Financial snapshot: **2 October 2026**. This is a family-by-family map of measured evidence, not a claim that every wallet, private strategy or protocol is fully reconstructed.

## Capital, history and investor returns

| Family | Income mechanism | Capital evidence | History evidence | Return evidence |
| --- | --- | --- | --- | --- |
| Native validator staking | Consensus issuance, tips and MEV | 43.806M actual active ETH; 43.740M effective active ETH | Five archived month ends; earlier states pruned at tested public endpoints | Issuer benchmarks only |
| Liquid staking / restaking | Validator income; additional service rewards where realised | Issuer and security-layer claims; overlapping | 24-month protocol observations | Matched share conversions for selected issuers |
| ETH lending | Borrower interest | Lending claims, cash and debt measured separately | Protocol histories; selected reserve histories | Selected rates and share returns |
| ETH-debt loops | Leveraged staking-minus-ETH-funding spread | Fluid / Treehouse parents; Liquid, CIAN and Yearn positions | Selected product books, not monthly loop weights | Selected matched ETH book returns |
| Dollar carry | Dollar investment income minus dollar funding | Thirteen examined books; ten current traced routes; carry equity remains distinct from whole books | 24 monthly whole-book observations; allocation weights incomplete | Matched 30-day claims; four financed lots plus two flow-adjusted investment / funding ledgers |
| Spot / short basis | Funding or dated-futures premium | Frozen ETH slice unmeasured; later Ethena disclosure separate | No complete frozen ETH-slice history | No matched ETH-long strategy comparison |
| Fixed maturity | Underlying income or principal-claim discount | Pendle / Spectra parent claims; market registries screened | Parent histories; four active Ethereum PT faces verified at T; maturity coverage remains partial | Payoff denomination checked; no full investor-return panel |
| DEX / trading liquidity | Swap fees; inventory and trader P&L | 28 verified ETH-custody pools; broader adapters incomplete | 24 month ends for that same pool subset | Custody is not LP profit; selected positions traced |
| Options / structured yield | Option premiums in exchange for contingent payoff | Ribbon residual book: 713 ETH; current option expired in December 2025; other funded capacity partial | Historical / retired product screens | No full premium, settlement and cash-return ledger |
| Mixed allocators / tranches | A blend of the mechanisms above | Parent books and selected sleeves; never add both as unique capital | Parent NAV; changing allocation weights incomplete | Selected share marks; strategy attribution incomplete |

## Discovery is not strategy attribution

The saved DefiLlama screen contains **299** ETH-name pools above $5M from **86** projects. **221** are joined to an existing parent; the other **78** receive separate dispositions. These are discovery decisions, not 299 independently reconstructed strategies or additive ETH capital. [Individual decisions](CARRY-COVERAGE-AUDIT.md).

## Three boundaries that affect the answer

1. **Capital:** receipt claims, lending collateral, managed shares and underlying custody overlap. Global unique ETH and global carry equity are not measured. Native consensus balances are outside the protocol panel. Four major liquidity adapters lack usable token history at T; the 28-pool custody reconstruction is a separate bounded subset.
2. **History:** categories group protocol families consistently. Their monthly NAV is not a history of strategy allocations or external deposits. A constant cohort controls observation availability, while current discovery can omit dead products.
3. **Income:** matched book returns, financed investment-lot results and complete strategy profit answer different questions. Reward sponsor, earning period, own-credit flows, outer fees and exit cash must be assigned before stating organic carry profit.

## Carry routes and current status

| Product | Status | Attribution boundary |
| --- | --- | --- |
| Concrete Delta weETH | Declared arbitrage; shared custody | Dollar debt is observed in a shared Safe; assets and debt attributable to Delta are unresolved. |
| ether.fi Liquid ETH | Active hybrid | Dollar loans and destination claims are measured; full carry-sleeve equity is not reconciled. |
| Lido Earn ETH | Active hybrid | Earn ETH reports 83,309 ETH. Its main holding is stRATEGY, whose book must not be added again. The nested portfolio owes about 355,217 WETH in staking loops and 25.55M USDT in its main dollar-carry account. Those are gross loans, not the carry sleeve’s equity. |
| Avant avETH / savETH | Active hybrid | The published 29 September portfolio has a $33.18M net NAV and a $32.53M savUSD position. Ethereum reads at T confirm USDC, USDS and PYUSD borrowing against ETH collateral. The large own-credit destination makes this a concentrated issuer dependency. |
| YieldBasis WETH | Active dollar-financed LP | Net fair-value WETH pool equity is measured separately from actual crvUSD debt; gauge income is separate. |
| Rocksolid rETH | Closing; nested carry | 728.48 ETH of Liquity shares is the evidenced nested carry claim; direct Aave debt is zero. |
| Liquity ETH Carry | Active minted-dollar LP | Ebisu collateral, ebUSD debt and dollar LP positions are measured; do not equate collateral with sleeve equity. |
| Makina DETH | Active hybrid | DETH reports 2,499 ETH in a cached book. Its hub has 15,065 WETH of Aave debt against weETH, plus a Morpho USDT / wstETH carry route. Verified accounting instructions identify the credit receipts instead of relying on the vault name. |
| Vesper vaETH | Active hybrid | vaETH reports 1,052 ETH. Its XY strategy supplies 57.35 WETH, owes 68,998 DAI and holds 60,034 vDAI shares. Other strategies in the same pool are lending or liquidity positions, so the whole pool cannot be labelled carry. |
| Royco ETH | Loan traced; parent marks stale | Morpho PYUSD debt and the senior credit receipt are traced; parent accounting and immediate exit remain restricted. |
| TAU InfiniFi ETH Carry | Historical; dust debt at T | Accrued debt is 0.022132 USDC at T; the old whole book is not current active carry equity. |
| Reservoir ETH Yield | Small current nested savings | Outer dollar borrowing and borrowing inside the savings destination are distinct liabilities. |
| ZenSats wstETH | Active micro-position | The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category. |

Ten examined products have current traced routes, including the small Reservoir and ZenSats positions and stale-mark Royco. Rocksolid is Closing, TAU's current debt is dust, and Concrete's published arbitrage mandate does not establish a product-attributed sleeve. ZenSats has a measured sub-one-ETH LlamaLend / Curve / StakeDAO book. Its withdraw-only legacy Aave / RAAC vault has zero assets and supply at T. [Official strategy documentation](https://www.zensats.app/docs/strategy).

## How to read TVL

DefiLlama separates borrowed balances and flags reused receipt assets. Native validator staking also has a different scope from chain DeFi TVL. Our token panel is a custom ETH-family exposure view, so it must not be labelled as their global TVL or unique market capital. [DefiLlama definitions](https://docs.llama.fi/analysts/data-definitions).

## Supporting research

[Team briefing](BRIEFING.md), [market structure](MARKET-STRUCTURE.md), [carry product evidence](CARRY-PRODUCTS.md), [custody and exits](CAPITAL-INCOME-EXIT.md), [additional product histories](PRODUCT-FINANCIAL-HISTORY.md), [strategy families](STRATEGY-UNIVERSE-EXPANSION.md). Financial observations retain their dates; later documentation does not fill missing values at T.


## Native stake: measured backing, not another wrapper

The archived consensus state at T has **43,805,557.723 actual active ETH**, **43,739,959 effective active ETH** and **874,362 active validators**. Actual balance and effective stake answer different questions. The active set includes 22,432 exiting validators. These balances are measured directly from validator objects, including compounding validators; they are not validator count multiplied by 32. Receipt claims are a separate, overlapping layer.

The archived slot is **15346798**, state root `0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282`. The public provider marks the response finalized and execution optimistic. The header state root agrees with the saved header; we do not claim an independent state-root recomputation from the validator JSON. Five successful monthly state reads cover May to September 2026. Earlier headers exist but their complete states are pruned at the tested public endpoints. Those missing balances remain absent.

[Archived state endpoint](http://testing.mainnet.beacon-api.nimbus.team/eth/v1/beacon/states/15346798/validators?status=active_ongoing,active_exiting,active_slashed), [monthly observations](../../../data/eth/native-staking-observations.csv), [normalised reconstruction and receipt hashes](../../../data/eth/finalization_reconstruction.json).


## Fixed-maturity and option capacity at the snapshot

Four active, unexpired Ethereum Pendle markets from the saved registry have verified PT, YT and SY identities at T. Their PT face supplies are **153.219 superWETH**, **123.843 pufETH**, **305.243 stETH** and **5.969 mixWETH** units. SY accounting assets are WETH, native ETH, stETH and WETH respectively. Face supply, market liquidity and underlying unique ETH are different measurements. The zero-address SY asset denotes native ETH, not missing metadata. PT redemption also depends on its conversion index and underlying asset performance. These four markets are an examined active subset, not all fixed-income ETH products.

Ribbon ETH Theta has **712.655 ETH of residual reported capital**. Its current option expired on **12 December 2025**. That residual book does not prove active premium selling in October 2026. Thetanuts has a deployed share contract, but the tested public interface does not expose a verified full portfolio valuation; a zero idle WETH balance does not establish zero invested capacity.

[Archived contract states and source hashes](../../../data/eth/finalization_reconstruction.json), [PT identity reads](../../../data/eth/finalization_financial_bindings_T.json), [option-state reads](../../../data/eth/finalization_options_T.json).
