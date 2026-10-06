"""Independently verify launch lineage, account claims, cash fees and carry scope."""
import collections, hashlib, json, math, re
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'data/eth'
def read(name):return json.loads((D/(name+'.json')).read_text())
def run():
    m=read('parity_depth_measurements');pc={p['id']:p for p in read('reader_product_chapters')['products']}
    checks=[]
    def ck(name,value):checks.append({'name':name,'passed':bool(value)})
    ck('fixed_financial_boundary',m['snapshot']=='2026-10-02T23:59:59Z' and m['ethereumBlock']==26108081)
    for name,sha in m['sourceHashes'].items():ck('input_hash:'+name,hashlib.sha256((D/name).read_bytes()).hexdigest()==sha)
    captures={}
    def walk(value):
        if isinstance(value,list):
            for v in value:walk(v)
        elif isinstance(value,dict):
            if 'sha256' in value and 'path' in value:captures[value['path']]=value
            for v in value.values():walk(v)
    for name in m['sourceFiles']:walk(json.loads((D/name).read_text()))
    for path,c in captures.items():
        body=(ROOT/path).read_bytes();ck('capture:'+path,('bytes' not in c or len(body)==c['bytes']) and hashlib.sha256(body).hexdigest()==c['sha256'])
    for receipt in m['ownership']['receipts']:
        key=receipt['key'];ledger=collections.defaultdict(int)
        source=next(r for r in read('parity_depth_holder_transfers')['records']if r['label'].startswith(key+'_'))
        for e in source['response']['result']:
            sender,receiver=['0x'+t[-40:] for t in e['topics'][1:]];n=int(e['data'],16)
            if int(sender,16):ledger[sender]-=n
            if int(receiver,16):ledger[receiver]+=n
        balances={a:n for a,n in ledger.items()if n};exported={r['address']:int(r['sharesRaw'])for r in receipt['rows']}
        ck('receipt_replay:'+key,balances==exported and sum(balances.values())==int(receipt['supplyRaw']))
        ck('receipt_underlying_not_one_to_one:'+key,not math.isclose(receipt['assetsPerShare'],1,abs_tol=1e-4) and math.isclose(sum(r['proportionalUnderlyingClaim']for r in receipt['rows']),int(receipt['totalAssetsRaw'])/1e18,abs_tol=1e-8))
    senior=m['ownership']['savETHLookThrough'];sav=m['ownership']['receipts'][0]
    ck('senior_lookthrough_preserves_claim',sum(int(r['sharesRaw'])for r in senior['rows'])==int(sav['supplyRaw']))
    ck('senior_concentration_includes_all_traced_claims',42.90<senior['rows'][0]['sharePct']<42.91 and 'Gearbox and Morpho' in pc['avant']['depth']['holdersText'])
    ck('bridge_residual_not_unique_investor',any(r['address']==senior['bridgeAddress']for r in senior['rows']) and 'remote claims' in pc['avant']['depth']['holdersText'])
    cash=m['ownership']['liquidCash'];ck('Cash_is_account_positions_not_people',cash['holderCount']==7012 and cash['testedAccounts']==7351 and 'unique people' in cash['scope'])
    ck('Cash_integer_claims_conserve',sum(int(r['sharesRaw'])for r in cash['rows'])==int(cash['hubLiquidSharesRaw']))
    op=read('parity_depth_op_beneficiary_events')['records'];ck('Cash_origin_from_supply_event',int(op[0]['response']['result'][0]['blockTimestamp'],16)==1786273221 and cash['firstSupplyDate'].startswith('2026-08-09T11:00:21'))
    yb=m['ownership']['yieldBasisLookThrough'];ck('YB_personal_accounts_not_share_vaults',len(m['ownership']['yieldBasisPersonalVaultOwners'])==4 and 21.77<yb['rows'][0]['sharePct']<21.78)
    growth=read('presentation_analysis')['growth_summary'];ck('growth_decomposition_conserves',math.isclose(growth['NAV_change_ETH'],growth['accounting_rate_effect_ETH']+growth['share_supply_effect_ETH'],abs_tol=1e-8) and 'not a cash-flow' in pc['liquid']['depth']['capitalText'])
    f=m['feePayments'];actual=read('parity_depth_fee_receipts')['records'];totals=collections.defaultdict(int)
    for r in actual:
        receipt=r['response']['result'];ck('successful_fee_receipt:'+r['label'],receipt['status']=='0x1')
        for e in receipt['logs']:
            if e['topics'][0].startswith('0x9493e5bb') and e['address'].lower()=='0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198':totals['0x'+e['topics'][1][-40:]]+=int(e['data'],16)
    expected={r['asset']:int(r['raw_amount']) for r in read('presentation_analysis')['fees']['claims']}
    ck('fee_cash_matches_receipt_events',dict(totals)==expected and f['paymentCount']==19 and all(r['receiptConfirmed']for r in f['verifiedPayments']))
    ck('fee_payment_block_conversion',math.isclose(f['totalClaimedETH'],2130.60490269813,abs_tol=1e-9) and math.isclose(f['totalClaimedETH'],f['WETHPaymentsETH']+f['weETHPaymentsETH']))
    scenarios=[r for r in m['cohortSensitivity']['rows']if r['loanPrincipalPYUSD']==18000000]
    cohort=next(r for r in read('carry_attribution_tranches')['debt_cohorts']if r['borrowed_cash_assets']==18000000)
    ck('carry_models_use_exact_same_loan',len(scenarios)==3 and {r['method']for r in scenarios}=={'FIFO','LIFO','Pro rata'} and all(r['loanTransaction']==cohort['transaction_hash'] and r['exactLoanInterestPYUSD']==int(cohort['accrued_borrowing_interest_raw'])/1e6 for r in scenarios))
    ck('carry_models_recompute_result',all(math.isclose(r['claimLessFundingPYUSD'],r['allocatedClaimGainPYUSD']-r['exactLoanInterestPYUSD'],abs_tol=1e-8) and -5361<r['claimLessFundingPYUSD']<-4583 for r in scenarios))
    ck('carry_sensitivity_not_complete_profit','not rigorous' in m['cohortSensitivity']['scope'] and 'Rewards' in m['cohortSensitivity']['scope'])
    history=m['fundingHistory'];ck('historical_lenders_before_Morpho',any(r['venue']=='Aave' and r['symbol']=='USDC' and r['firstBorrow']['date'].startswith('2025-08-18')for r in history['legs']))
    ck('month_end_debt_not_TVL',len(history['monthlyDebt'])==100 and all(r['indexedDebt']is None for r in history['monthlyDebt']if r['status']!='observed'))
    legs=pc['liquid']['charts']['loanLegs'];ck('all_material_Liquid_funding_routes_visible',len(legs['rows'])==9 and {r['debtAsset']for r in legs['rows']}=={'WETH','USDC','USDT','PYUSD','RLUSD'} and len(legs['dustRows'])==2)
    ck('material_Liquid_rates_and_health_factors_measured',all(r['healthFactor']is not None and r['borrowAPR_pct']is not None for r in legs['rows']))
    known=read('carry_economics_chapter')['borrow_markets']
    for r in m['fundingHistory']['morphoAtT']:
        original=next((s for s in known if s['id']==r['marketId']),None)
        if original:
            position=next((s for s in original.get('positions',[])if s['account']==r['account']),None)
            if position:ck('independent_Morpho_HF:'+r['marketId']+r['account'],math.isclose(r['healthFactor'],position['health_factor'],rel_tol=1e-8))
    ck('Liquid_point_rates_not_average_cost',any(r['debtAsset']=='USDC' and 13.93<r['borrowAPR_pct']<13.94 for r in legs['rows']if r['borrowAPR_pct']is not None) and 'point quotes' in legs['scope'])
    for id in ['concrete','liquid','lido-earn','avant','yieldbasis']:
        p=pc[id];ck('substantive_flagship:'+id,p['substantiveReview']=='2026-10-06' and all(p['depth'].get(k)for k in ['incomeText','holdersText','historySummary']) and all(r.get('url','').startswith('http')for r in p['timeline']))
    liquid=pc['liquid'];ck('distribution_budget_not_vault_profit','ecosystem budget' in liquid['depth']['distributionText'] and any(r['url'].startswith('https://blog.kyberswap.com')for r in liquid['timeline']))
    ck('Lido_predecessor_and_real_incident',pc['lido-earn']['timeline'][0]['date']=='2025-11-06' and '27 days' in pc['lido-earn']['timeline'][3]['text'] and '144.77 ETH' in pc['lido-earn']['depth']['incidentText'])
    ck('YB_predecessor_not_current_receipt_launch',pc['yieldbasis']['timeline'][0]['date']=='2026-01-23' and 'does not splice' in pc['yieldbasis']['depth']['historySummary'])
    markers=['## Native stake: measured backing','## Additional carry books: fixed-block reconstruction','## Two additional dollar investment and funding ledgers','## Fixed-maturity and option capacity','<!-- substantive-parity -->']
    for path in (ROOT/'research/eth/en').rglob('*.md'):
        s=path.read_text();ck('no_repeated_generated_sections:'+path.name,all(s.count(marker)<=1 for marker in markers))
    ck('reader_same_eight_chapters',len(re.findall(r'<section\b[^>]*id="(?:top|map|how|top5|market|risks|do|data)"',(ROOT/'tools/eth/site/index.html').read_text()))==8)
    ck('shared_custody_note_requires_Delta_bound','b.unattributedBounds?.attributableVisibleToDeltaUpperUSD!=null' in (ROOT/'tools/eth/site/reader.js').read_text())
    ck('BTC_root_preserved',hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()=='ee05709e085406a6b0da19717e974834c6ae48cea54f34840c830fbc9eaf1222')
    output={'snapshot':m['snapshot'],'reviewDate':'2026-10-06','checks':checks,'allPassed':all(r['passed']for r in checks),'scope':'Source/capture fingerprints, receipt supply, named custody look-through, fee cash, historical funding, three carry accounting scenarios, predecessor boundaries and reader parity. Private strategy P&L and unique global capital are not certified.'}
    (D/'parity_depth_verification.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'allPassed':output['allPassed'],'failed':[r['name']for r in checks if not r['passed']]}));assert output['allPassed']
if __name__=='__main__':run()
