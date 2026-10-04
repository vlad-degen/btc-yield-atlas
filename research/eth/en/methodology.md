# Measuring the ETH yield market

The study separates three things: the ETH that backs the system, investors' claims on that capital, and positions that deploy it through protocols. Before adding balances, we verify units and remove repeated claims on the same assets. Aggregator catalogues help us find products, but their summed TVL is not a market total.

## Which date does each observation describe?

**Contract snapshot.** T is 2 October 2026, 23:59:59 UTC. On each chain, use the last block at or before T and confirm that the next block is later. Read balances, debt, share rates and rules at that block.

**Dated API data.** Use the nearest observation whose source timestamp is no later than the target, and retain its age. Monthly tables show actual source dates. Missing observations remain unavailable.

**Current discovery.** Aggregators, interfaces and registries captured after T identify products to investigate. Their amounts and portfolio mix require separate checks at T. Today's allocation cannot be used to fill the product's history.

Prices retain timestamps and distance from T. The nearest initial ETH/USD quote is T+1 second, used for preliminary conversion with that deviation disclosed. Balance/liquidation calculations additionally use actual oracles and conversion rates.

## Six worked balance sheets

The following are illustrative accounting examples, rather than market observations.

| Example | State | Unique ETH | External ETH capital | Why reported positions overlap |
|---|---|---:|---:|---|
| LST | 100 ETH backing; user holds 100 ETH-equivalent LST | 100 | 100 | Receipt and backing represent one claim |
| LST + restaking | 100 ETH backing; LST deposited with restaker; user holds receipt | 100 | 100 | Three claim layers on one backing |
| ETH loop | Investor supplies 100 ETH; external ETH lender supplies 90; strategy holds 190 ETH LST and 90 debt | 190 | 190 | Strategy equity 100 + lender claim 90; do not add issuer backing again |
| Dollar carry | Investor supplies 100 ETH; dollar debt and dollar deployment each equal 50 ETH | 100 | 100 | External dollar lender remains a separate dollar segment; vault asset and debt offset |
| PT + YT | SY backed by 100 ETH; illustrative PT value 90 ETH and YT value 10 | 100 | 100 | PT/YT split the claim; nominal redemption units cannot be added to SY |
| Multi-chain share | 100 ETH backing; 60 Ethereum shares and 40 L2 shares through burn/mint | 100 | 100 | Share geography and backing geography describe the same capital |

With lock/mint, 40 original shares remain in Ethereum totalSupply while escrowed: external capital is 100 although summed chain supply is 140. Prove bridge type through contracts/events before adding supply. ETH lenders belong to the ETH universe; dollar lenders belong to the dollar universe.

## Returns and debt mechanics

The main return measure is the change in an investor's ETH claim plus any distributions paid outside the share price, adjusted for cash flows. Time-weighted return (TWR) measures strategy performance; money-weighted return (MWR) also reflects when an investor deposited or withdrew. APR and APY use the same dates and state how the return is annualized. A principal token's fixed rate applies to its specified unit and maturity.

A complete profit-and-loss account separates staking, tips and MEV, paid security-service revenue, strategy income, debt interest, incentives, fees, gas and slippage. Any unexplained amount remains a residual. Points count as realized income only when their value is received. Rewards already included in the share price cannot be counted again as external distributions.

ETH borrowing does not prove looping: trace loan use. ETH→LST is correlated looping; USD→USD yield is dollar carry; USD→ETH adds directional exposure; ETH→USD yield changes ETH delta and forms a separate carry variant. Mixed financing requires complete balance/equity allocation; shared debt remains unallocated when evidence is insufficient.

## Comparability and risk

Compare holding ETH, simple staking after provider fees, lending and each strategy over the same dates. Show excess return in ETH and percentage points: 4% minus 3% is 1 percentage point. A scenario without incentives retains native staking income. Keep reported net asset value (NAV), market price and withdrawal proceeds for a specified size separate.

Health factor (HF) measures liquidation headroom for a specific account under its market's prices and rules. When both LST collateral and debt are denominated in ETH, an ETH/USD move can reprice both sides together. LST discounts and interest still matter. With dollar debt, an ETH/USD fall weakens collateral coverage. A vault with several accounts has no single universal HF.

Measure how much of each debt currency is available for repayment, then how much ETH can reach investors and when. Two routes drawing on the same cash are not independent reserves. Review administrators, contract permissions, managers, allowed strategy calls and modules even when a contract's `owner` is the zero address.

## Verification and evidence

Check major balances in two ways: shares multiplied by price per share (PPS), and assets minus liabilities across the product's controlled accounts. Include a nested vault once, at the value of the shares the product owns. The raw files retain their request, URL, capture time and SHA256 hash.

Each product and chain amount is labelled as fixed-block verified, a dated API estimate, current discovery or unknown. An incomplete list cannot prove that a product is absent. Preserve negative debt entries and missing fields as the source reports them. Material gaps and overlaps remain part of the audit.
