"""A reproducible discovery disposition; discovery values never enter frozen TVL."""
import csv,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data/eth'
def run():
 manifest=json.loads((D/'parity_discovery_manifest.json').read_text());source=next(r for r in manifest if r['key']=='yield_pools');body=ROOT/source['path'];pools=json.loads(body.read_text())['data']
 ledger=json.loads((D/'market_reader_chapter.json').read_text());ids={p['id']:p['category'] for p in ledger['products']}
 candidates=[p for p in pools if re.search('ETH',p['symbol'],re.I)];large=[p for p in candidates if p['tvlUsd']>=5e6]
 aliases={'liquid-collective':'liquid-collective-staking','crypto.com-liquid-staking':'crypto.com-liquid-staking','midas-rwa':'midas','yieldnest':'yieldnest-restaking'}
 pending={'avant-aveth':'Managed market-neutral mandate; ETH-collateral dollar-financing ledger unverified','makina':'DETH mandate includes LRTs, lending, AMMs, PTs and loops; sibling DBIT carry cannot be assigned to DETH','geth':'Guarda staking wrapper; no dollar investment leg established','meta-pool-eth':'Validator-income receipt; downstream collateral use is separate','nodedao':'Staking-family discovery; no dollar investment leg established','orca-dex':'Solana LP discovery; full mixed-pool TVL is not ETH-side principal','justlend-v1':'Excluded: Tron token name does not prove Ethereum-backed redemption'}
 rows=[]
 for p in large:
  project=p['project'];join=project if project in ids else aliases.get(project)
  status='Parent covered in frozen ledger; pool TVL is not additive ETH capital' if join in ids else pending.get(project,'Discovery only; token identity and frozen ETH-side exposure need verification')
  rows.append({k:p.get(k) for k in ['pool','project','chain','symbol','tvlUsd','poolMeta'] }|{'parent_id':join if join in ids else None,'parent_role':ids.get(join),'disposition':status,'valuation_date':'5 Oct discovery; not frozen T'})
 reviewed=[
 {'product':'YieldBasis WETH','decision':'Confirmed dollar-financed LP; moved from farming to carry','evidence':'Actual frozen crvUSD loan, effective supply and fair ETH mark; 24 archive month ends','source':'https://docs.yieldbasis.com/','counted':True},
 {'product':'ZenSats wstETH / LlamaLend','decision':'Documented E4 route; frozen capital unmeasured','evidence':'wstETH collateral → crvUSD loan → Curve crvUSD/USDT → StakeDAO; CRV harvest converts to debt asset','source':'https://www.zensats.app/docs/strategy','counted':False},
 {'product':'ZenSats wstETH / pmUSD','decision':'Documented legacy E4; withdraw-only','evidence':'Aave USDT loan → crvUSD swap → RAAC pmUSD/crvUSD → StakeDAO; historical book unmeasured','source':'https://www.zensats.app/docs/strategy','counted':False},
 {'product':'Vesper ETH / stETH / msETH','decision':'Mixed strategy family; current dollar-loan allocation unresolved','evidence':'Official strategies distinguish same-token leverage from a different-token loan routed to another Vesper pool. msETH is an ETH synth, not proof of dollar debt.','source':'https://docs.vesper.finance/vesper-pools-and-strategies/strategies','counted':False},
 {'product':'Makina DETH','decision':'Mixed ETH allocator; dollar carry unverified','evidence':'Official DETH mandate names restaking, lending, AMMs, PTs and loops. The same article assigns explicit stablecoin carry to DBIT; it does not prove DETH dollar debt.','source':'https://makinafi.substack.com/p/operator-deep-dive-dialectic','counted':False},
 {'product':'Avant savETH / avETHx','decision':'ETH managed and tranched return; dollar-carry portfolio unresolved','evidence':'ETH base and senior/junior wrappers are documented. The ETH-collateral dollar loan, counterparties and portfolio weights are not reconstructed.','source':'https://docs.avantprotocol.com/overview/core-tokens','counted':False},
 {'product':'yoETH','decision':'ETH pool allocator; dollar-carry allocation unverified','evidence':'Published design is an ETH-pool basket with operator-reported balances and cash-dependent asynchronous redemptions. A receipt denomination does not prove dollar borrowing.','source':'https://docs.yo.xyz/protocol/yovault-tokens','counted':False},
 {'product':'9Summits Flagship ETH / Lagoon','decision':'Staking and DeFi mandate; dollar-carry allocation unverified','evidence':'ETH denomination, curator and settlement model are documented; no frozen dollar-funded destination ledger is established.','source':'https://9summits.io/','counted':False},
 {'product':'Lido earnETH / GGV / stRATEGY','decision':'Mixed ETH allocation; sub-vault lookthrough needed','evidence':'earnETH sub-vaults are documented. earnUSD accepts dollars and is not automatically an ETH-collateral carry product.','source':'https://docs.lido.fi/earn/','counted':False},
 {'product':'YieldNest ynETHx','decision':'Mixed MAX vault; dollar-loan allocation unverified','evidence':'Restaking and multi-strategy vault design do not establish actual stablecoin debt.','source':'https://docs.yieldnest.finance/protocol-design/max-vaults','counted':False},
 {'product':'Lucidly cyETH','decision':'Unverified product claim; excluded from measured carry','evidence':'Search-indexed official pages claim an ETH carry product. Direct hosts failed DNS and no fixed-T deployed book was verified. Do not assign the sibling cyBTC route or marketing APR.','source':'https://www.lucidly.finance/','counted':False}]
 result={'reviewDate':'2026-10-05','frozenTimestamp':1790985599,'totalPools':len(pools),'keywordCandidates':len(candidates),'materialKeywordPools':len(large),'materialProjects':len({p['project'] for p in large}),'screenRule':'Case-insensitive ETH in symbol; TVL >= USD 5M. This is a broad discovery rule, not verified ETH capital.','source':{'url':source['url'],'path':source['path'],'sha256':hashlib.sha256(body.read_bytes()).hexdigest()},'materialPools':rows,'reviewedCases':reviewed,'documentedRoutes':[r for r in reviewed if r['product'].startswith('ZenSats')],'boundary':'A finite public-feed and primary-document sweep covers the significant observed strategy families. Wallet-level carry, private mandates and unsupported adapter histories remain outside a verified exhaustive global capital total.'}
 (D/'carry_coverage_audit.json').write_text(json.dumps(result,indent=2)+'\n')
 with (D/'carry-discovery-dispositions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 report=f'''# ETH carry coverage: what belongs in the category

Reviewed 5 October 2026. Financial balances remain frozen at 2 October 2026, 23:59:59 UTC. Later discovery is used to find omissions, not to replace historical values.

## The material correction

YieldBasis WETH belongs in dollar-financed carry under the same economic definition used for BTC. At T its actual liability is 27,814,855.84 crvUSD and its net oracle book is 10,425.999 ETH. The 64.14M crvUSD allocation limit is not current debt. Effective pool supply, fair value and 24 month-end archive reads now feed the carry chart. Staked and unstaked LT claims represent one pool. This reclassification moves an existing parent between categories; it adds no new market capital. [Pool](https://etherscan.io/address/0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea#code), [design](https://docs.yieldbasis.com/).

The measured carry-design sample now contains eight whole books, about 510,924 ETH in gross claims. Concrete and Liquid remain hybrid parents. Rocksolid owns 728 ETH of Liquity claims. This sum is neither unique investor equity nor the dollars currently invested in carry. Protocol-parent exposure uses a separate adapter price convention.

## The public-feed sweep

The saved DefiLlama feed contains {len(pools):,} pools. An ETH-name screen finds {len(candidates):,} candidates; {len(large):,} pools from {result['materialProjects']} projects report at least $5M. Every material row has a disposition in the downloadable CSV. A pool can contain stablecoins, non-ETH tokens or reused vault claims. Its entire TVL cannot enter the ETH numerator. The matching review checks parent coverage, token or strategy ambiguity, aliases and missing deployments. [Feed](https://yields.llama.fi/pools).

## Product decisions

| Product / family | Decision | Evidence and remaining boundary |
|---|---|---|
'''
 for r in reviewed:report+=f"| [{r['product']}]({r['source']}) | {r['decision']} | {r['evidence']} |\n"
 report+='''
## The significant carry routes

1. **Lending or credit.** ETH collateral funds a dollar loan; dollars buy a lending-vault or credit receipt. The investor retains ETH exposure plus borrower and redemption risk. Liquid and Royco have measured loan and destination evidence. Loan principal, destination principal and self-owned credit must be reconciled separately.
2. **Stablecoin savings, including nested leverage.** The first loan buys a savings receipt. The receipt can collateralize a second loan, so both spreads and both repayment sequences matter. Reservoir has two observed loans; TAU has historical financing but only dust first-layer debt at T.
3. **Dollar liquidity and rewards.** A dollar loan finances stablecoin LPs, whose fees and paid incentives must clear borrowing and swap costs. Liquity ETH Carry uses ebUSD at T. ZenSats documents active crvUSD and legacy USDT routes; their fixed-T sizes remain unmeasured rather than zero.
4. **Dollar-financed ETH liquidity.** YieldBasis adds a dollar liability inside an ETH/ stablecoin LP and adjusts leverage. Net ETH exposure, financing and rebalancing differ from simply lending the dollars. Gauge returns and unstaked LT marks are separate cash rights.
5. **Fixed-maturity investments.** Borrowed dollars can buy a dollar PT or other dated claim. A fixed redemption amount does not fix floating loan cost or guarantee early liquidity. The underlying receipt issuer and maturity must match the repayment plan; ETH PT exposure without a dollar loan belongs in Fixed yield.
6. **Market-neutral trading.** Dollars borrowed against retained ETH can fund hedged trading. Concrete discloses this mandate, but its shared wallet and private venues leave Delta-specific earnings unresolved. A spot ETH asset offset by an ETH short instead has a dollar-neutral payoff and belongs in Basis.
7. **Manual CDP carry.** A user can create a dollar liability against ETH through a CDP and place proceeds in savings, lending or liquidity. Collateral totals and stablecoin supply alone do not identify the invested proceeds. This feasible route does not become an extra measured product book without wallet-level financing and destination evidence.
8. **Permissioned or cross-chain credit.** Bridges, gated funds and remote sub-accounts can implement any of the preceding routes. They change control, credit and repayment constraints; they are not additional capital categories. The lender, investment chain and receipt-issuance chain can differ.

## Why carry can look small

The market denominator includes large staking and downstream collateral claims. A stablecoin loan does not establish an invested carry destination; a managed ETH receipt does not establish a stablecoin loan. Counted carry therefore answers a narrower question than all ETH-secured borrowing or all ETH vaults. Assigning entire Vesper, Makina, Avant, YO or Lido Earn books to carry without their actual loan ledgers would make the category larger by assumption.

This audit resolves the YieldBasis classification omission and records two additional documented ZenSats routes. It disposes of the material public-feed candidates and preserves unresolved managed books for lookthrough. It does not claim a complete global sum of private or wallet-level carry.

Data: [material-pool dispositions](../../../data/eth/carry-discovery-dispositions.csv), [coverage audit](../../../data/eth/carry_coverage_audit.json), [carry book observations](../../../data/eth/reader_carry_category.json), [product chapters](../../../data/eth/reader_product_chapters.json).
'''
 (ROOT/'research/eth/en/CARRY-COVERAGE-AUDIT.md').write_text(report)
 print(f"Coverage: {len(large)} material keyword pools, {result['materialProjects']} projects, {len(reviewed)} explicit product decisions.")
 return result
if __name__=='__main__':run()
