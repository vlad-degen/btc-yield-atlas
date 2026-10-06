"""Attach substantive launch, ownership and economic history to the BTC reader shape."""
import json
from pathlib import Path
from parity_depth_models import build as measure, read
from report_contract_build import table

ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'data/eth'; EN=ROOT/'research/eth/en'
E='https://etherscan.io/'; LIDO='https://research.lido.fi/t/'
def event(date,title,text,url,kind='history'):return dict(date=date,title=title,text=text,url=url,kind=kind)
def fmt(n,d=0):return f'{n:,.{d}f}'

def augment():
    m=measure(); pc=read('reader_product_chapters'); p={r['id']:r for r in pc['products']}
    growth=read('presentation_analysis');g=growth['growth_summary'];fee=m['feePayments']; own=m['ownership'];fh=m['fundingHistory']
    cash=own['liquidCash']; senior=own['receipts'][0]; gauge=own['receipts'][1]
    models=[r for r in m['cohortSensitivity']['rows'] if r['loanPrincipalPYUSD']==18000000]
    # Economic explanations replace snapshot-only timelines and policy labels.
    p['liquid']['story']={'title':'Staking leverage first, dollar carry later',
        'text':'Liquid began with ETH borrowing against staking collateral. Dollar financing followed in August 2025 through a managed account, then expanded into Cap and Sentora credit. Its two-year share return exceeds stETH by 1.36 percentage points, but that excess combines loops, carry and rewards.',
        'lesson':'Separate growth in capital, earnings per share and the spread on each financed investment.'}
    p['liquid']['timeline']=[
        event(fh['firstShareMint']['date'],'First observed share issuance','A 0.24446-share mint establishes use of the present contract. Deployment was 3 June; neither timestamp alone establishes the public launch.',fh['firstShareMint']['url'],'issuance'),
        event('2024-06-25','The Aave ETH loop begins','The main vault first borrows WETH. This increases staking exposure; it does not create dollar investment capital.',next(r for r in fh['legs'] if r['venue']=='Aave' and r['symbol']=='WETH')['firstBorrow']['url'],'funding'),
        event('2025-08-18','Dollar financing appears in the managed account','The controlled account 0x0a42…c02c first borrows USDC on Aave. It already owes 47.07M USDC at the August month end.',next(r for r in fh['legs'] if r['venue']=='Aave' and r['symbol']=='USDC')['firstBorrow']['url'],'funding'),
        event('2025-11-26','Cap becomes an investment destination','The captured stcUSD deposit history begins. Its receipt earns through Cap’s credit machinery; this is a new destination, not extra underlying ETH.','https://etherscan.io/tx/0x9b217842406c49d31c2dc5e32d0d8bc3cee67cf2aeb18c2bae3ef033dd64bc88','investment'),
        event('2026-03-24','Spark adds a second ETH loop','The first main-vault Spark WETH borrowing is observed. The main Aave and Spark accounts have different liquidations and funding costs.',next(r for r in fh['legs'] if r['venue']=='Spark' and r['symbol']=='WETH')['firstBorrow']['url'],'funding'),
        event('2026-06-23','Morpho dollar routes expand beyond the main vault','The controlled LoanManager begins RLUSD borrowing in June. The main vault adds weETH/RLUSD and weETH/PYUSD in July; Sentora RLUSD V2 deposits begin on 7 August.',next(r for r in read('carry_attribution_ledger')['borrowing_ledgers'] if r['account']=='0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3')['first_borrow']['sourceURL'],'funding'),
        event(cash['firstSupplyDate'],'Cash shares move into pooled custody','The captured Cash spoke history begins. By T, the Hub holds 20.53% of the whole Liquid book on behalf of 7,012 positive account positions.','https://optimistic.etherscan.io/address/'+cash['spoke'],'distribution'),
        event('2026-09-25','PRIME-backed financing enters the credit vault','An 18M PYUSD loan against PRIME is deposited into a PYUSD credit vault. Its claim and financing are measured through T.','https://etherscan.io/tx/0xb12b59b3177d97b6f2118b14b6712c09558c75c977fa78c5ef3eb1d4d2fbc176','funding'),
        event('2026-09-25','Kyber adds a distribution channel','Kyber announces Liquid ETH on KyberEarn. This establishes an integration announcement, not how many new deposits it generated.','https://blog.kyberswap.com/ether-fi-liquid-vaults-are-live-on-kyberearn/','distribution')]
    p['liquid']['depth']={
        'capitalText':f"Between September 2024 and September 2026, the ETH book grew by {fmt(g['NAV_change_ETH'])} ETH. Share-supply changes account for {fmt(g['share_supply_effect_ETH'])} ETH of that change; the share-price effect accounts for {fmt(g['accounting_rate_effect_ETH'])} ETH. This is an accounting bridge, not a cash-flow or carry-profit estimate.",
        'incomeText':f"For the 18M PYUSD investment originated on 25 September, FIFO, LIFO and proportional withdrawal allocation all give a negative claim-minus-funding result: {fmt(min(r['claimLessFundingPYUSD'] for r in models))} to {fmt(max(r['claimLessFundingPYUSD'] for r in models))} PYUSD through T. Rewards, collateral income, gas and outer fees are separate.",
        'feesText':f"The Ethereum management fee changed repeatedly: 1.50% in January 2025, zero in July, and 0.35% at T. Nineteen claimed payments total {fmt(fee['totalClaimedETH'],2)} ETH after converting each weETH payment at its own block. This is platform cash received, not operator profit.",
        'holdersText':f"The two largest Ethereum wallets together hold about 37% of the whole book. The Optimism Hub holds another {cash['wholeBookSharePct']:.2f}% across {cash['holderCount']:,} positive Cash account positions. Its single address conceals a distribution of claims; these accounts are not necessarily different people.",
        'ownerRows':[{'address':r['address'],'sharePct':r['shareOfHubPct'],'basis':'Share of Cash Hub','url':r['url']} for r in cash['rows'][:10]],
        'holderCSV':'parity-Liquid-Cash-beneficiaries.csv','historySummary':'The present contract was used in June 2024. ETH loops came first; Aave dollar borrowing appeared in August 2025. Morpho financing followed through the LoanManager in June 2026 and the main vault in July.',
        'distributionText':'The May 2025 Member Rewards proposal budgets 7.5M ETHFI across ether.fi for June to August and assigns Liquid ETH nine points per ETH per day, versus three for staking. This explains the distribution incentive; the ecosystem budget is not a measured payment to this vault or organic carry income.',
        'distributionURL':'https://governance.ether.fi/t/ether-fi-member-rewards/2974'}
    # The main borrowing panel previously showed four Aave/Spark account
    # totals while hiding Morpho elsewhere. Show every examined funding leg
    # in its own currency, and keep repaid dust outside the material table.
    old=p['liquid']['charts']['loanLegs']['rows']; monthly=fh['monthlyDebt']
    reserve=read('parity_depth_reserve_tokens')['records'][1:]
    def reserve_rate(venue,asset):
        pool='0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2' if venue=='Aave' else '0xc13e21b648a5ee794902342038ff3adab66be987'
        r=next(r for r in reserve if r['label']==pool+'_'+asset);s=r['response']['result']
        return int(s[2+4*64:2+5*64],16)/10**27*100
    legs=[]
    for row in old[:2]:
        symbol='WETH';venue='Aave' if row['protocol']=='Aave V3' else 'Spark'
        debt=next(r['indexedDebt'] for r in monthly if r['month']=='snapshot' and r['venue']==venue and r['symbol']==symbol)
        legs.append(dict(row,debtUnits=debt))
    for symbol,asset in [('USDC','0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'),('USDT','0xdac17f958d2ee523a2206206994597c13d831ec7')]:
        debt=next(r['indexedDebt'] for r in monthly if r['month']=='snapshot' and r['symbol']==symbol)
        legs.append(dict(old[2],protocol='Aave V3 · managed account',debtAsset=symbol,debtUnits=debt,debtUSD=debt,borrowAPR_pct=reserve_rate('Aave',asset),scope='Actual indexed debt token balance; dollar display assumes $1. Both currencies share the account-level health factor.'))
    sparkPYUSD=int(read('parity_depth_spark_debt')['records'][0]['response']['result'],16)/10**6
    legs.append(dict(old[3],protocol='Spark · managed account',debtAsset='PYUSD',debtUnits=sparkPYUSD,debtUSD=sparkPYUSD,borrowAPR_pct=reserve_rate('Spark','0x6c3ea9036406852006290770bedfcaba0e23a0e8'),scope='Actual indexed PYUSD variable debt token balance at T.'))
    dust=[]
    for r in read('carry_attribution_ledger')['borrowing_ledgers']:
        risk=next(s for s in fh['morphoAtT']if s['marketId']==r['market_id'] and s['account']==r['account'])
        row={'date':m['snapshot'],'chain':'Ethereum','account':r['account'],'protocol':'Morpho · '+('LoanManager' if r['account'].startswith('0xc936') else 'main vault'),'collateralAsset':'PRIME' if r['collateral_asset']=='0x19ebb35279a16207ec4ba82799cc64715065f7f6' else 'weETH','debtAsset':r['symbol'],'debtUnits':r['ending_accrued_debt_assets'],'debtUSD':r['ending_accrued_debt_assets'] if r['symbol']!='WETH' else None,'healthFactor':risk['healthFactor'],'borrowAPR_pct':risk['borrowAPR_pct'],'sourceURLs':[r['sourceURL']],'scope':'Exact accrued debt at T from debt-share accounting; dollar display assumes $1. This table does not add that loan to the outer book size. '+risk['basis']}
        (dust if r['ending_accrued_debt_assets']<1 else legs).append(row)
    p['liquid']['charts']['loanLegs'].update(rows=legs,dustRows=dust,scope='Nine material financing legs across the main vault and named controlled accounts. ETH-debt loops and dollar loans stay separate. Aave currencies share an account health factor. Dollar reference values assume $1; rates are point quotes at T, not average costs. Repaid Morpho WETH and PYUSD dust remain in the source ledger.')
    p['liquid']['depth']['fundingText']='At T, Aave USDC funding is 13.93% APR, versus 4.38% for Aave USDT and 4.39% for Spark PYUSD. Funding cost depends on the actual loan currency and venue; a low quote on one route does not describe the whole carry book.'
    launch='https://blog.lido.fi/introducing-the-lido-strategy-vault/'
    incident=LIDO+'kelp-incident-review-earneth-exposure-response-and-risk-framework-changes/11579'
    seed=LIDO+'lido-earn-dao-treasury-allocation-q2-2026/11831'
    p['lido-earn']['timeline']=[
        event('2025-11-06','stRATEGY launches before the current outer vault','Lido introduces the underlying strETH strategy with Aave, Ethena and Uniswap routes. Its announced 1% annual and 10% performance fees describe that launch, not the zero nested settings observed at T.',launch,'launch'),
        event('2026-02-19','DAO proposes a first-loss treasury allocation','The proposal assigns $3M in wstETH to EarnETH and $2M in USDC to EarnUSD. DAO shares can absorb losses by being burned; the budget is not a yield reward.',LIDO+'lido-earn-competing-on-trust-5m-treasury-allocation/11228','governance'),
        event('2026-03','Current EarnETH outer vault becomes materially funded','The first >1 ETH month-end book in the sampled outer-vault history is March. Earlier strETH capital belongs to its predecessor and is not backfilled into this chart.','https://docs.lido.fi/earn/deployment-contracts/','funding'),
        event('2026-04-18','Kelp-related market stress freezes the exit','The review reports roughly 113.2k rsETH collateral and 111.1k WETH debt in the affected strategy. Deposits and withdrawals pause for 27 days; funding costs become an actual loss.',incident,'incident'),
        event('2026-05-15','Operations resume after DAO loss absorption','The executed transaction burns 143.9766 earnETH shares. The later treasury report values the cover at 144.77 ETH. User protection came from reserve capital as well as recovery of the affected markets.',E+'tx/0xdfca0390d39299ec88e6be26f5254d873b9a1098f71591c42f357412d60e71c7','recovery'),
        event('2026-09-29','A directly financed USDT investment is measurable','A 5M USDT borrowing and new earnUSD claim in the same transaction gain 1,400.57 USDT after allocated interest through T, before gas and outer fees. Existing allocated shares are excluded.','https://etherscan.io/tx/'+read('finalization_reconstruction')['directFinancedLot']['transactionHash'] if 'transactionHash' in read('finalization_reconstruction')['directFinancedLot'] else read('finalization_reconstruction')['directFinancedLot']['receipt'],'funding')]
    p['lido-earn']['depth']={
        'incomeText':'The USDT-funded earnUSD claim earns a different spread from the leveraged ETH staking positions. The 5M USDT lot adds 1,400.57 USDT before gas and outer fees over 3.75 days; its mark remains an investment claim rather than redeemed cash.',
        'holdersText':'The outer token has 2,500 positive holder addresses, including managed accounts. Allocated but unclaimed shares sit outside that issued-token census. The DAO’s first-loss reserve is risk-bearing seed capital, not a deposit guarantee.',
        'historySummary':'The underlying strategy launched in November 2025; the present outer EarnETH book is measured from March 2026. Its April crisis and May recovery belong in the investment history.',
        'incidentText':'The Kelp review reports 143.98 ETH of operational loss from elevated funding costs. The treasury’s later account specifies 143.98 earnETH shares burned, worth 144.77 ETH. The executed burn confirms the share units. These disclosures use different measures and must not be added together.',
        'incidentURL':incident,'treasuryURL':seed}
    avantAPI='https://app.avantprotocol.com/api/metrics/aveth'
    p['avant']['timeline']=[
        event('2025-09','The measured avETH book becomes material','September is the first >1 ETH month-end issuer face supply in the captured history. The official yield series begins with the week ending 25 September; neither observation establishes an exact public launch date.',avantAPI,'funding'),
        event('2026-09-29','Issuer discloses a leveraged multi-chain portfolio','The dated disclosure reports $72.65M assets and $39.47M liabilities, with $33.18M net NAV. A $32.53M savUSD position makes own-issuer credit economically important. These are reported portfolio figures, not a T backing audit.',avantAPI,'disclosure'),
        event('2026-10-02','The senior claim and holder intermediaries are traced','savETH owns 88.08% of Ethereum avETH face supply. Its 83 direct holders include a Gearbox credit account, Morpho collateral custody and a CCIP bridge pool.',E+'address/'+senior['receipt'],'ownership')]
    savLarge=own['savETHLookThrough']['rows'][0]
    p['avant']['depth']={
        'holdersText':f"The 37 direct avETH holders do not describe senior investor ownership: savETH holds 88.08% of avETH and has {senior['holderCount']} direct receipt holders. After tracing Gearbox and Morpho custody and combining each named owner’s claims, the largest holds {savLarge['sharePct']:.2f}% of senior shares. The CCIP bridge still represents remote claims.",
        'ownerRows':[dict(r,basis='Share of senior savETH',url=E+'address/'+r['address']) for r in own['savETHLookThrough']['rows'][:10]],
        'holderCSV':'parity-savETH-holders.csv','historySummary':'avETH and senior savETH have a measured September 2025 origin in this study. Later issuer disclosures show a multi-chain, leveraged book; the measured Ethereum face supply is not that global NAV.',
        'incomeText':'Senior savETH earns from the avETH issuer structure. ETH collateral generates staking income while dollar loans finance credit claims, including the issuer’s own savUSD product. A senior return series does not disclose the complete strategy P&L or the junior loss waterfall.'}
    old='https://forum.yieldbasis.com/t/tweak-weth-pool-parameters/25';v3='https://news.curve.finance/curve-monthly-recap-may-june-2026/'
    p['yieldbasis']['timeline']=[
        event('2026-01-23','An earlier WETH pool is already operating','The parameter proposal identifies Curve pool 0x6e54…A9C2 and discusses dynamic swap fees, financing and temporary redemption discounts. Its history must not be confused with the current LT receipt.',old,'predecessor'),
        event('2026-05','The measured current WETH LT book appears','The present LT contract is absent at the sampled April end and funded at May end. Its AMM at T is 0x5f8d…233c, distinct from the January pool.',E+'address/0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea','funding'),
        event('2026-05 to 2026-06','V3 changes the liquidity architecture','Curve’s dated recap describes FXSwap upgrades and personal HybridVaults combining crypto exposure with crvUSD allocation. It reports an allocation adjustment from 55% to 45%; this is not an investor yield promise.',v3,'architecture'),
        event('2026-10-02','Staking changes the economic claim','The gauge holds 56.35% of direct LT supply for 155 receipt holders. Unstaked LT marks and gauge fee/reward rights are different investor outcomes.',E+'address/'+gauge['receipt'],'ownership')]
    ybLarge=own['yieldBasisLookThrough']['rows'][0]
    p['yieldbasis']['depth']={
        'holdersText':f"Of 332 direct LT addresses, the largest is a gauge with 56.35% of supply. Its {gauge['holderCount']} holders own the gauge claim. After replacing that custody balance and mapping four personal HybridVaults to their owners, the largest named-owner claim is {ybLarge['sharePct']:.2f}% of LT supply. Other contracts remain identified as custody.",
        'ownerRows':[dict(r,basis='Share of LT supply',url=E+'address/'+r['address']) for r in own['yieldBasisLookThrough']['rows'][:10]],
        'holderCSV':'parity-ybGauge-holders.csv','historySummary':'WETH liquidity existed by January 2026. The chart follows the current LT contract from May and does not splice the old Curve pool into its return series.',
        'incomeText':'Traders pay Curve swap fees. Those fees must fund rebalancing and crvUSD financing before the ETH holder earns a spread. A staked gauge receipt has additional fee and YB reward rights; the unstaked LT return chart excludes those cash flows.'}
    p['concrete']['depth']={'holdersText':'One externally owned address holds all issued Delta shares at T. That establishes concentration in this claim, while the shared custody Safe holds the actual strategy assets. It does not identify outside investor capital or assign the Safe’s dollar arbitrage profit to Delta.',
        'historySummary':'The share contract was deployed in December 2025. Its first completed-month weETH book is already large, but the native share price stays flat through T. The resulting ETH mark largely follows weETH staking conversion.',
        'incomeText':'The stated mandate includes neutral arbitrage and staking collateral financed with dollars. The shared account has observable loans, but Delta-specific investment principal, revenue and private fees are not publicly assigned. Its place at the top of the book-size table is therefore not evidence of dominance in verified carry capital.'}
    for id in ['concrete','liquid','lido-earn','avant','yieldbasis']:
        p[id]['substantiveReview']='2026-10-06'
        p[id]['sources'].append({'url':'data/parity_depth_measurements.json','label':'Launch, ownership and economics reconstruction'})
        p[id]['sources'].append({'url':'library/PRODUCT-EVOLUTION.html','label':'Product development and measured findings'})
    (D/'reader_product_chapters.json').write_text(json.dumps(pc,indent=2,allow_nan=False)+'\n')
    summary={'snapshot':m['snapshot'],'growthBridge':g,'feePayments':fee,'cohortModels':models,'monthlyDebt':fh['monthlyDebt'],
        'fundingLegs':[{k:v for k,v in r.items() if k!='events'} for r in fh['legs']],
        'cash':{k:v for k,v in cash.items() if k!='rows'},'seniorHolders':senior['holderCount'],'gaugeHolders':gauge['holderCount']}
    (D/'parity_depth_reader.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    return pc,m

def editorial():
    pc=read('reader_product_chapters');m=read('parity_depth_measurements');text='# Product development, ownership and carry economics\n\nFinancial snapshot: **2 October 2026, 23:59:59 UTC**. Public documents reviewed on 6 October. The main report retains the BTC eight-chapter route. This supporting chapter explains the history behind the five largest examined books.\n\n'
    for p in [p for p in pc['products'] if p.get('depth')]:
        depth=p['depth'];section='## '+p['name']+'\n\n'+depth['historySummary']+'\n\n'
        section+=table(['Date','Change','Economic significance'],[[r['date'],r['title'],r['text']+' [Primary evidence]('+r['url']+')'] for r in p['timeline']])+'\n\n'
        section+='### What the investor owns and earns\n\n'+depth['incomeText']+'\n\n'+depth['holdersText']+'\n\n'
        for key in ['capitalText','feesText','incidentText','distributionText','fundingText']:
            if key in depth:section+=depth[key]+'\n\n'
        if depth.get('distributionURL'):section+='[Distribution proposal]('+depth['distributionURL']+').\n\n'
        if 'ownerRows' in depth:section+=table(['Named owner / account','Share of stated claim','Denominator'],[['['+r['address']+']('+r['url']+')',f"{r['sharePct']:.4f}%",r['basis']] for r in depth['ownerRows']])+'\n\n'
        section+='[Reproducible measurement ledger](../../../data/eth/parity_depth_measurements.json).\n\n';text+=section
        # Reuse product dossiers where they already exist; never append twice.
        name={'liquid':'etherfi-liquid-eth','concrete':'concrete-eth'}.get(p['id'])
        if name:
            path=EN/'dossiers'/f'{name}.md';s=path.read_text().split('\n<!-- substantive-parity -->')[0]
            path.write_text(s+'\n<!-- substantive-parity -->\n'+section)
    text+='## Liquid: the same invested dollars under three withdrawal conventions\n\n'+m['cohortSensitivity']['method']+'\n\n'+table(['Convention','Borrowed PYUSD','Allocated claim growth','Exact debt interest','Claim less financing'],[[r['method'],fmt(r['loanPrincipalPYUSD']),fmt(r['allocatedClaimGainPYUSD'],6),fmt(r['exactLoanInterestPYUSD'],6),fmt(r['claimLessFundingPYUSD'],6)] for r in m['cohortSensitivity']['rows'] if r['loanPrincipalPYUSD']==18000000])+'\n\n'+m['cohortSensitivity']['scope']+'\n\n[Loan and investment transaction](https://etherscan.io/tx/0xb12b59b3177d97b6f2118b14b6712c09558c75c977fa78c5ef3eb1d4d2fbc176), [cohort CSV](../../../data/eth/parity-Liquid-cohort-sensitivity.csv).\n\n'
    text+='## Liquid: actual funding history\n\n'+table(['Venue','Account','Currency','First borrowing','Borrow / repay events'],[[r['venue'],r['account'],r['symbol'],'['+r['firstBorrow']['date']+']('+r['firstBorrow']['url']+')',str(r['borrowCount'])+' / '+str(r['repayCount'])] for r in m['fundingHistory']['legs']])+'\n\n'+m['fundingHistory']['scope']+'\n\n[Indexed monthly debt CSV](../../../data/eth/parity-Liquid-monthly-debt.csv), [Cash accounts CSV](../../../data/eth/parity-Liquid-Cash-beneficiaries.csv), [senior savETH CSV](../../../data/eth/parity-savETH-holders.csv), [YieldBasis gauge CSV](../../../data/eth/parity-ybGauge-holders.csv).\n'
    text+='\n## Reproduce the measurements\n\nThe input ledgers below retain the captured request, response, block and source fingerprint where available. The measurement file records SHA-256 hashes of every input. Receipt look-through changes ownership attribution, not capital.\n\n'
    text+='\n'.join('- ['+name+'](../../../data/eth/'+name+')' for name in m['sourceFiles'])+'\n'
    (EN/'PRODUCT-EVOLUTION.md').write_text(text)
    for name in ['BRIEFING','CARRY-PRODUCTS','CAPITAL-INCOME-EXIT','RETURN-DRIVERS']:
        path=EN/f'{name}.md';s=path.read_text().split('\n<!-- substantive-parity -->')[0]
        s+='\n<!-- substantive-parity -->\n\n## Product history behind the snapshot\n\nLiquid’s stablecoin borrowing predates its current Morpho routes: Aave USDC financing is observed in August 2025. Its 18M PYUSD cohort is negative after funding under three explicit withdrawal conventions, before rewards and other costs. Cash Hub ownership now resolves to 7,012 positive account positions. Lido’s current wrapper follows its November 2025 underlying strategy; its April crisis required a 27-day pause and DAO loss absorption. YieldBasis’s present LT history starts after an earlier WETH pool, and gauge investors have different income rights from unstaked holders. Avant’s senior holder analysis traces Gearbox and Morpho custody instead of treating their contracts as single investors.\n\n[Full product development, accounting assumptions and source evidence](PRODUCT-EVOLUTION.md).\n';path.write_text(s)
    print('Substantive parity: launch lineage, historical lenders, beneficial-account look-through and funding sensitivity integrated.')

if __name__=='__main__':augment();editorial()
