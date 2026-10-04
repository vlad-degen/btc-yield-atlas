# ETH yield strategy atlas: material families beyond the five carry chapters

The ETH market needs a broader product map than a list of carry vaults. A product can preserve ETH exposure, lend ETH, sell ETH options, supply trading liquidity or hedge ETH into a dollar claim. These strategies have different income payers, maturity payoffs and withdrawal rights. The same ETH can also appear as staking collateral, a lending deposit, an LP balance and a vault receipt. Those layers cannot be added as independent capital.

This review expands ten selected families and records 25 product identities. The financial snapshot remains **2 October 2026 at 23:59:59 UTC**. Product documentation and official registries were reviewed on **4 October**. The discovery yield feed was captured on **3 October at 13:40:39 UTC**. Its values are useful for selecting large products, but they are not frozen-snapshot NAV or proof of executable backing. No new discovery value has been joined to the snapshot market total.

## Material product map

The table deliberately preserves different size measures. There is no meaningful grand total to calculate from these rows.

| Family | Observed materiality and date | Main payoff | What is still missing |
| --- | --- | --- | --- |
| StakeWise osETH and Boost | osETH $419.41m; Genesis Vault $112.66m, 3 October discovery | ETH staking; Boost adds an ETH-funded staking loop | Separate Boost population, frozen balances and authority review; Genesis and osETH can overlap |
| mETH and cmETH | mETH $631.62m, 3 October discovery | Staking plus Aave buffer earnings; cmETH adds restaking risk and rewards | Buffer allocation, actual service fees, restaking exposure and independent cmETH capital |
| Curated ETH allocation | Euler K3 Monad WETH $63.92m; Yearn WETH $19.53m, 3 October discovery | Borrower interest and other permitted strategies | Exact K3 product-address binding, frozen allocations, role limits and investor return history |
| ETH principal/yield tokens | December 2027 stETH market $5.50m, 3 October discovery; $5.54m, official 4 October registry | PT maturity discount, YT future yield, or LP trading payoff | Historical outstanding principal, complete multichain census and actual ETH PT debt routes |
| autoETH | $20.82m, 3 October discovery | LST earnings, DEX fees and rewards, less execution costs | Frozen destination portfolio, actual charges and large-order exit evidence |
| YieldBasis WETH | Unstaked row $12.21m; staked row $15.23m, 3 October discovery | Leveraged LP mechanics with different fee and reward rights | Complete debt and receipt netting, parameter history and realized class-specific return |
| GMX GM/GLV | ETH-USDC $48.02m; ETH-ETH $18.80m, 3 October discovery | Inventory value, trading fees and net trader PnL | Historical total returns, reserved exit capacity and any separately managed hedge |
| ETH options | Ribbon reported a full 10,000 ETH call cap during June/July 2021; Thetanuts publishes current contract identities | Premium minus option settlement, with ETH inventory or USD put collateral | Current balances, active auction evidence, observed net returns and authority state |
| Dollar-neutral products | sUSDe $1.246bn, 3 October discovery, for the entire USD product | Funding/basis and other collateral income after hedge costs | The ETH-specific collateral/hedge allocation; whole USD supply is not ETH capital |
| Custodial and listed staking | WBETH $9.435bn, 3 October discovery; ETHE $2.703bn net assets at 31 December 2025 | Native staking through custodial receipts or fund shares | Current custodial decomposition and dated policy updates; no additional capital layer |

The structured file retains exact values, source URLs, addresses where verified, denomination, status, incentive treatment and explicit missing measurements: [strategy_universe_expansion.json](../../../data/eth/strategy_universe_expansion.json).

## Where the broader map changes the analysis

### Staking receipts can contain another strategy

StakeWise Boost borrows ETH against osETH and stakes the borrowed ETH. Its extra return depends on a positive spread between staking and ETH debt costs. Published collateral thresholds do not remove market-sale, oracle or liquidation risk. The unlevered osETH receipt and the boosted position must be evaluated separately. [StakeWise documentation](https://docs.stakewise.io/), [official deployed contracts](https://github.com/stakewise/v3-core/blob/main/deployments/mainnet.json).

mETH introduced an ETH buffer deployed to Aave on 24 October 2025. The published return therefore combines validator and borrower income. Its current overview describes capped production testing, roughly 10% reward fees, a 4-basis-point staking entry charge and FIFO withdrawal with a minimum 12-hour delay. Available buffer liquidity and validator exits determine the actual wait. cmETH adds a separate restaking portfolio and cooldown. These are published policies, not independently verified parameters at the snapshot. [mETH overview](https://docs.mantle.xyz/meth/introduction/overview.md), [staking contracts](https://docs.mantle.xyz/meth/components/smart-contracts/staking-meth.md).

### Curated vaults need strategy-level classification

Yearn's official WETH registry lists Spark lending, Yearn OG WETH and a stETH accumulator. Calling the whole vault pure lending loses an important part of its income model. Euler Earn can allocate among approved lending and other ERC-4626 strategies, with separate manager powers, caps and withdrawal queues. The K3 discovery quote divides 2.69201% total APY into 1.20737% base and 1.48464% rewards. That is a useful subsidy signal, but the base label is not audited organic cash. [Yearn official registry](https://ydaemon.yearn.fi/1/vaults/all?orderBy=featuringScore&orderDirection=desc&strategiesDetails=withDetails&strategiesCondition=inQueue), [Euler Earn](https://docs.euler.finance/use/euler-earn/).

### Fixed yield is fixed in a particular unit

Five official registry pages contain 494 unique Ethereum Pendle markets. Of those, 117 are ETH tagged and four are active and unexpired at the 4 October discovery. Old maturities remain part of the historical universe. The largest current ETH market is PT-stETH December 2027: wstETH is the underlying token, while stETH is the accounting unit. This distinction changes how a maturity return is calculated.

The official Ethereum looping catalog contains 15 PT identities, and none matches an ETH-tagged market in the full registry. A generic looping diagram therefore does not establish an active ETH PT loop. It also says nothing about ETH PT collateral supplied through integrations outside that catalog. [Official market API](https://api-v2.pendle.finance/core/v1/1/markets?limit=100), [published loop catalog](https://api-v2.pendle.finance/core/v1/pt-looping/loop/pts/1/looping), [loop mechanics](https://docs.pendle.finance/pendle-v2/AppGuide/PTLooping).

The feed repeats the same market liquidity in a PT-buy row and an LP row. PT, YT and LP have distinct payoffs, but those quoted liquidity values are not independent capital. The captured registry and matched loop catalog are preserved in [registry data](../../../data/eth/strategy_universe_expansion_pendle_registry.json) and [loop data](../../../data/eth/strategy_universe_expansion_pendle_loops.json).

### Liquidity strategies earn more than their displayed fee APY

Auto Finance, formerly Tokemak, combines correlated ETH inventory, staking receipts, DEX fees and rewards. Exiting above idle WETH requires withdrawing destination assets and swapping them. Its official large-withdrawal guide explicitly discusses slippage and custom routes. “No lock” does not mean unlimited liquidity at the marked share price. [Contract catalog](https://docs.auto.finance/developer-docs/contracts-overview/contract-addresses.md), [allocation strategy](https://docs.auto.finance/developer-docs/contracts-overview/autopool-eth-contracts-overview/autopool-contracts-and-systems/autopool-strategy.md), [large withdrawals](https://docs.auto.finance/developer-docs/integrating/large-withdrawals.md).

YieldBasis uses leveraged liquidity to target underlying-asset performance. Its twofold leverage target is a model choice, not a guarantee that ETH exposure is lossless. Staked and unstaked receipts have different fee and incentive economics; their quoted APYs cannot simply be stacked. A debt-funded LP is also not automatically the same strategy as borrowing dollars to deploy into a dollar yield asset. [Official code](https://github.com/yield-basis/yb-core/blob/master/contracts/LT.vy), [design paper](https://github.com/yield-basis/yb-paper/blob/master/leveraged-liquidity-paper.pdf).

GMX LP value includes trader PnL and collateral price changes. ETH-USDC and ETH-ETH are different exposures. An ETH-index market backed solely by dollar assets is different again. A short hedge would add its own funding and liquidation costs and needs separate position evidence. Fee-only APY omits those parts of total return. Open-interest reserves can also constrain withdrawals. [GMX liquidity documentation](https://docs.gmx.io/docs/providing-liquidity/), [official Arbitrum market catalog](https://arbitrum-api.gmxinfra.io/markets).

### Options need a complete payoff, not an annualized premium

Covered calls trade ETH upside above the strike for premium. The total return includes option settlement losses and ETH price movement. A strategy can earn premiums and still underperform ETH sharply in a rally. A cash-secured put starts with USD collateral, so it belongs in an adjacent structured-product universe rather than ETH-principal capital.

Ribbon's primary retrospective documents a full ETH call cap growing from 5,000 to 10,000 ETH during its 2021 incentive program. That proves historical capacity, not current activity or unsubsidized demand. Thetanuts publishes ETH call contracts on Ethereum and Arbitrum and an mETH call on Mantle. Current capital and auctions remain unverified. [Ribbon retrospective](https://gov.ribbon.finance/t/retrospective-on-rgp-2/143), [historical fees](https://docs.ribbon.finance/theta-vault/theta-vault/fees), [Thetanuts contracts](https://docs.thetanuts.finance/contracts-and-security/deployed-contracts.md).

### Dollar-neutral and custodial products require their own perimeter

USDe and the historical Resolv design hedge crypto collateral with shorts to target a dollar claim. Ethena's current overview also describes lending, non-crypto basis and real-world-asset revenue. Its entire balance cannot be attributed to ETH basis. Removing rewards does not remove hedge costs, losses or discretion over distributions. [Ethena overview](https://docs.ethena.fi/overview/ethena-overview.md), [underlying derivatives](https://docs.ethena.fi/protocol-overview/underlying-derivatives.md).

WBETH and staking ETFs ultimately use the same native validator income as other staking products. What changes is custody, fees and the holder's exit channel. Binance's fee FAQ states a standard 10% reward commission and reserves the right to change it without advance notice. WBETH Flexible Simple Earn adds no second reward stream. ETHE's 2025 filing states a 2.5% annual sponsor fee and aggregate staking charges of 23% of gross rewards. The fund's shares can trade away from NAV. These dated terms must be kept separate from October 2026 policy verification. [Binance staking terms](https://www.binance.com/en/support/faq/detail/eecd04618b5042c79f2a5b07f895c498), [WBETH FAQ](https://www.binance.com/en/support/faq/detail/e252366155174ba6887f6b32e3798273), [ETHE annual filing](https://www.sec.gov/Archives/edgar/data/1725210/000119312526071965/ethe-20251231.htm).

## Historical products are part of the market

Yearn's official disclosure dates the yETH exploit to 30 November 2025 and states that V2 and V3 vaults were unaffected. The yETH interface now identifies the product as retired and recovery-only. The 4 October registry still records approximately $6.61m of WETH accounting assets in the recovery vault. That balance is a recovery claim, not ordinary new-deposit yield capacity. [Official disclosure](https://github.com/yearn/yearn-security/blob/master/disclosures/2025-12-01.md), [recovery interface](https://yeth.yearn.fi/?action=stake-unstake).

Resolv's official documentation records a 22 March 2026 incident, a paused recovery state and an extended claims deadline of 26 September. Older ordinary mint/redeem terms must not be used as the active exit policy. Its separately documented TAC-vault deprecation and HyperUSD strategy transition are distinct events; hiding a product from a UI does not prove every related contract closed. [Recovery policy](https://docs.resolv.xyz/litepaper/using-resolv/resolv-recovery-portal-overview.md), [deprecated and migrated products](https://docs.resolv.xyz/litepaper/using-resolv/vaults/deprecated-vaults.md).

Euler's April handover proposal similarly separates curator transfer from wind-down. The Monad WETH Earn row reported $7.75m at 8 April and a proposed K3 handover. That is a useful dated predecessor record, but it does not prove the final snapshot authority or that every deprecated market stopped accepting exits. [Official proposal and status updates](https://forum.euler.finance/t/sunsetting-of-dao-managed-market-and-vaults/1828).

## What this review completes

The expansion supplies an evidence-backed family atlas, primary contract catalogs, payer and full-payoff explanations, withdrawal/control terms, incentive treatment and specific historical transitions. It does not close whole-market capital or return coverage. The concrete remaining work is frozen-block product binding and positions for large selected wrappers, their realized return histories, actual fee and role configuration, product-level exit evidence, and multichain principal-token coverage. Options additionally need recent auctions and settlements before a current material-product claim is justified.

Rebuild offline with `python3 tools/eth/strategy_universe_expansion_build.py`. The [manifest](../../../data/eth/strategy_universe_expansion_manifest.json) records captured URLs, observation dates, input hashes, outputs and failed or non-content responses. Browser-read fact observations are explicitly distinguished from full HTTP source captures.
