"""Check the integrated final exhibits, arithmetic and preserved evidence boundaries."""
import hashlib, json, math
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'data/eth'
def read(name):return json.loads((D/(name+'.json')).read_text())
def near(a,b):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-6)

def run():
    checks=[]
    def check(name,ok,detail=None):checks.append({'check':name,'passed':bool(ok),'detail':detail})
    m,a,b,basis=[read(name) for name in ['market_netting_closure','carry_attribution_closure','backing_exit_closure','basis_closure_disclosures']]
    payload=read('site_payload')
    check('frozen market timestamp and block',m['financial_as_of_timestamp']==1790985599 and m['block']==26108081 and not m['financial_data_refreshed'])
    check('global capital and earning coverage not invented',all(m[k] is None for k in ['global_unique_ETH','global_unique_ETH_upper_bound','global_net_market_NAV','market_share_denominator']) and m['headline']['earning_capital_floor_ETH'] is None and m['headline']['coverage_percentage'] is None)
    nodes=m['root_nodes'];included=[r for r in nodes if r['included_in_primary_custody_floor']]
    check('physical node identities unique',len(nodes)==len({(r['chain_id'],r['address'],r['asset']) for r in nodes}))
    physical=sum(Decimal(r['raw_wei'])/Decimal(10**18) for r in included)
    check('physical custody independently sums exact wei',near(float(physical),m['headline']['physical_custody_floor_ETH']))
    check('grouped custody reconciles floor',near(sum(m['root_groups_ETH'].values()),float(physical)))
    check('withdrawal custody remains separate',near(m['headline']['extended_floor_including_withdrawal_queue_ETH'],float(physical)+m['headline']['withdrawal_queue_ETH']) and m['withdrawal_queue']['native_minus_locked_ETH']==0)
    check('WETH supply and native escrow agree',m['canonical_WETH']['reconciliation_difference_ETH']==0)
    check('receipt repetition does not add physical capital',all(r['independent_root_addition_ETH']==0 and not r['additive_with_other_edges'] for r in m['duplicate_edges']))
    check('issuer accounting components reconcile without consensus promotion',near(sum(m['issuer_accounting']['components'].values()),m['issuer_accounting']['lido_book_ETH']) and not m['issuer_accounting']['is_actual_consensus_balance_at_T'])
    history=m['lp']['monthly_history']
    check('bounded LP history has 25 complete 28-pool observations',len(history)==25 and all(r['observed_pools']==r['expected_pools']==28 for r in history) and len([r for r in history if r['month']>='2024-10'])==24)
    w=a['common_window']
    check('income window ends at frozen T',w['end_timestamp']==1790985599 and w['end_block']==26108081 and near(w['days'],(w['end_timestamp']-w['start_timestamp'])/86400))
    for s in a['strategies']:
        c=s['claim'];f=s['funding_coverage']
        check(s['id']+' claim cash-flow equation',near(c['ending_claim_assets']-c['opening_claim_assets']+c['withdrawn_cash_assets']-c['deposits_assets'],s['claim_growth']))
        check(s['id']+' complete profit stays unavailable',s['complete_sleeve_net_income'] is None)
        check(s['id']+' partial direct funding reconciles',near(f['deposit_cash_assets'],f['same_transaction_cooccurring_assets']+f['deposit_principal_without_same_token_same_transaction_link']))
        check(s['id']+' cross-currency amounts remain bounded',f['deposits_without_same_transaction_link_after_cross_currency_screen']>=-1e-6)
        for l in s['loans']:
            check(s['id']+' loan equation '+l['account']+l['symbol'],near(l['ending_accrued_debt_assets']-l['opening_accrued_debt_assets']+l['repaid_cash_assets']-l['borrowed_cash_assets'],l['accrued_borrowing_interest_assets']))
        if s['loans']:check(s['id']+' loan-cost aggregation',near(sum(l['accrued_borrowing_interest_assets'] for l in s['loans']),s['accrued_borrow_cost']))
    check('income ledger validation checks pass',all(x['passed'] for x in a['verification']['checks']))
    check('own-credit diagnostic not allocated as net or paid profit',all(r['allocated_net_destination_own_interest'] is None and r['actually_paid_own_interest'] is None for r in a['own_credit_recycling']['rows']))
    check('PRIME underlying retains its actual currency',a['prime_destination']['symbol']=='wYLDS' and a['prime_destination']['decimals']==6)
    for p in b['products']:
        x=p['backing'];h=p['historicalExits']
        check(p['id']+' book/reconstruction/residual equation',near(p['bookNAV_USD'],x['reconstructedUSD']+x['residualUSD']))
        check(p['id']+' signed reconstructed positions sum',near(sum(r.get('USD',r.get('usd',0)) for r in x['lines']),x['reconstructedUSD']))
        if x.get('nestedReceiptReplacementReconstructionUSD') is not None:check(p['id']+' alternate nested-receipt replacement reconciles',near(x['nestedReceiptReplacementReconstructionUSD']+x['nestedReceiptReplacementResidualUSD'],p['bookNAV_USD']))
        check(p['id']+' demand scenarios cover three whole-book shares',sorted(d['navPct'] for d in p['demandScenarios'])==[1,10,30])
        for d in p['demandScenarios']:
            check(p['id']+' demand denominator '+str(d['navPct']),near(d['USD'],p['bookNAV_USD']*d['navPct']/100) and near(d['ETH'],p['bookNAV_ETH']*d['navPct']/100))
        check(p['id']+' cash receipt counts agree with payout records',h['receiptVerifiedCount']==h['fulfilledCount'])
        if h['waitHours']['median'] is not None:check(p['id']+' waiting quantiles ordered',0<=h['waitHours']['min']<=h['waitHours']['median']<=h['waitHours']['p90']<=h['waitHours']['max'])
        check(p['id']+' example payouts have receipt verification',all(r['tokenTransferVerified'] for r in h['examples']))
    liquid=next(p for p in b['products'] if p['id']=='liquid')
    check('untested Liquid aggregate demands remain explicit',all(d.get('response') is None and not d['simulatedImmediatePayout'] and not d['simulatedRequest'] for d in liquid['demandScenarios']))
    concrete=next(p for p in b['products'] if p['id']=='concrete')['backing']
    bounds=concrete['unattributedBounds']
    check('Concrete shared custody remains a conditional attribution range',bounds['attributableVisibleToDeltaLowerUSD']==0 and near(bounds['attributableVisibleToDeltaUpperUSD'],concrete['reconstructedUSD']) and near(bounds['minimumDeltaBookUnmappedToCapturedSharedAssetsUSD'],concrete['residualUSD']))
    check('exact-T ETH basis is not inferred from all-asset disclosures',basis['exact_T_ETH_basis_notional_USD'] is None and not basis['financial_data_refreshed'])
    for key,data in [('marketNetting',m),('carryAttribution',a),('backingExit',b),('basisDisclosures',basis)]:check(key+' embedded latest ledger',payload[key]==data)
    sources=m['sources']+m['raw_sources']+a['sources']+basis['sources']+read('backing_exit_manifest')['inputs']
    unique={(r['path'],r['sha256']) for r in sources}
    for path,expected in sorted(unique):
        file=ROOT/path;check('evidence hash '+path,file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest()==expected)
    html=(ROOT/'eth/index.html').read_text()
    check('eight original research sections preserved',all('id="'+x+'"' in html for x in ['top','map','how','top5','market','risks','do','data']))
    check('detailed closure exhibits retained_and_linked',all('id="'+x+'"' in (ROOT/'eth/exhibits.html').read_text() for x in ['market-net-capital','carry-earned-income','investor-exits','research-conclusions']) and 'href="exhibits.html"' in html)
    check('BTC reference unchanged',hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()=='ee05709e085406a6b0da19717e974834c6ae48cea54f34840c830fbc9eaf1222')
    for folder in ['eth','site/eth']:
        check(folder+' latest full closure exports',all((ROOT/folder/'data'/f'{name}.json').read_bytes()==(D/f'{name}.json').read_bytes() for name in ['market_netting_closure','carry_attribution_closure','backing_exit_closure','basis_closure_disclosures']))
    report={'all_checks_passed':all(r['passed'] for r in checks),'site_sha256':hashlib.sha256(html.encode()).hexdigest(),'checks':checks,'check_count':len(checks),'scope':'Verifies captured calculations, provenance and integrated presentation. Does not establish global unique earning capital, complete carry profit, independent solvency or a future executed withdrawal.'}
    (D/'research_closure_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    failures=[r['check'] for r in checks if not r['passed']]
    print(json.dumps({'checks':len(checks),'passed':report['all_checks_passed'],'failures':failures}))
    if failures:raise SystemExit(1)

if __name__=='__main__':run()
