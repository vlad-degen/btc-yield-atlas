"""Independent arithmetic, source integrity and scope checks for the new chapters."""
import collections,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'data/eth';T=1790985599
def read(n):return json.loads((DATA/(n+'.json')).read_text())
def close(a,b):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-7)
def run():
    checks=[]
    def check(name,value,detail=None):checks.append({'check':name,'passed':bool(value),'detail':detail})
    snap=read('funding_atlas_snapshot');chapter=read('funding_atlas_chapter');history=read('funding_atlas_history');borrowers=read('funding_atlas_borrowers')
    check('Original financial timestamp retained',snap['target_timestamp']==chapter['target_timestamp']==history['target_timestamp']==borrowers['target_timestamp']==T and not snap['financial_snapshot_refreshed'] and not chapter['financial_snapshot_refreshed'])
    check('Every measured pool oracle is verified in USD',all(v['USD_oracle_verified'] and v['identity_verification']['addressbook_oracle_matches_T'] and v['identity_verification']['base_currency_unit']==10**8 for v in snap['venues']))
    boundaries=[v['block_boundary'] for v in snap['venues'] if v.get('block_boundary')]
    check('Extra chain blocks enclose T including millisecond precision',all(b['precise_block_timestamp']<=T<b['precise_next_block_timestamp'] for b in boundaries),len(boundaries))
    errors=[]
    for v in snap['venues']:
        for a in v['assets']:
            if a['status']!='measured at T':continue
            raw=a['raw'];state=[int(raw['reserve']['result'][i:i+64],16) for i in range(2,len(raw['reserve']['result']),64)]
            d=(state[0]>>48)&255
            if d!=a['configuration']['decimals'] or not close(a['borrow_apr'],state[4]/1e27) or not close(a['supply_apr'],state[2]/1e27):errors.append(v['id']+'/'+a['symbol']+'/rate or decimal')
            for leg in ['supply','debt','cash']:
                units=int(raw[leg]['result'],16)/10**d
                if not close(a[leg+'_units'],units) or not close(a[leg+'_USD'],units*a['oracle_price_USD']):errors.append(v['id']+'/'+a['symbol']+'/'+leg)
    check('Reserve quantities decimals oracle marks and ray rates independently reconcile',not errors,errors)
    check('Dollar reserves counted without duplicate venue/address pairs',len(chapter['reserves'])==len({(r['venue_id'],r['address']) for r in chapter['reserves']})==chapter['summary']['dollar_reserves'])
    check('Stored monthly rates independently match archived reserve words',all(r['borrow_apr'] is None and r['supply_apr'] is None if r['status']!='measured' else close(r['borrow_apr'],int(r['response']['result'][2+4*64:2+5*64],16)/1e27) and close(r['supply_apr'],int(r['response']['result'][2+2*64:2+3*64],16)/1e27) for r in history['rows']))
    check('Historical missing listings remain absent not zero',all(r['borrow_apr'] is None for r in history['rows'] if r['status']=='not listed at dated block') and all(r['timestamp']<=T for r in history['rows']))
    check('Every requested borrower call resolved',all('result' in r['response'] and r['response']['result']!='0x' for r in borrowers['position_calls']),len(borrowers['position_calls']))
    check('Borrower cohort selected views complete',all(b['complete_queried_T_state'] and b['dollar_debt_USD']>=1e6 and b['ETH_collateral_USD']>0 for b in chapter['borrowers']))
    check('Collateral selection follows user bitmap not all aToken balances',all(l['enabled_as_collateral']==bool(b['user_configuration']&(1<<(2*l['reserve_id']+1))) for b in chapter['borrowers'] for l in b['ETH_collateral']))
    check('Enabled collateral and dollar debt subtotals reconcile',all(close(b['ETH_collateral_USD'],sum(l['oracle_USD'] or 0 for l in b['ETH_collateral'] if l['enabled_as_collateral'])) and close(b['dollar_debt_USD'],sum(l['oracle_USD'] or 0 for l in b['dollar_debt'])) for b in chapter['borrowers']))
    check('Holder census remains a separately dated sample without carry inference',all(b['carry_use_verified'] is False for b in chapter['borrowers']) and chapter['summary']['global_carry_capital_USD'] is None and chapter['summary']['global_ETH_only_dollar_debt_USD'] is None)
    rates={r['symbol']:r for r in chapter['reserves'] if r['venue_id']=='aave-ethereum'}
    check('USDC USDT funding difference reconciles',close((rates['USDC']['borrow_apr']-rates['USDT']['borrow_apr'])*100,chapter['summary']['aave_ethereum_USDC_minus_USDT_borrow_pp']))
    check('Restricted reserves cannot pass opening base rules',all(not r['base_rules_allow_new_borrow'] for r in chapter['reserves'] if r['configuration']['frozen'] or r['configuration']['paused'] or not r['configuration']['borrowing_enabled']))
    credit=read('credit_expansion');simple=[r for r in credit['markets'] if r['protocol']=='Fluid' and not r['is_smart_debt'] and r['collateral_scope']=='ETH family only']
    check('Fluid nominal debt subtotal uses simple ETH-only pairs',len(simple)==credit['summary']['simple_ETH_only_collateral_Fluid_USD_routes'] and close(sum(r['debt_units'] for r in simple),credit['summary']['simple_ETH_only_collateral_Fluid_nominal_dollar_debt_units']))
    stable=[b for b in credit['borrowers'] if b['sampled_dollar_debt_USD_valuation']>=5e6]
    check('WETH-valued loans excluded from unknown dollar-debt subtotal',len(stable)==7 and close(sum(b['sampled_dollar_debt_USD_valuation'] for b in stable),credit['summary']['unknown_stablecoin_borrowers_sampled_debt_USD_valuation']) and next(b for b in credit['borrowers'] if b['address'].startswith('0x462a'))['sampled_dollar_debt_USD_valuation']==0)
    variants=read('carry_variants_expansion');p={r['id']:r for r in variants['products']};tau=p['tau-infinifi'];reservoir=p['reservoir-eth']
    check('TAU dust debt not assigned whole NAV carry capital',close(sum(r['accrued_debt_loan_units'] for r in tau['positionsT']),.022132) and tau['category_capital_USD'] is None and any(sum(l.get('stored_debt_loan_units',0) for l in h['loans'])>3e6 for h in tau['historical_checkpoints']))
    check('Nested loan rates use separate funding costs',close(reservoir['economics']['destination_minus_outer_loan_apy'],reservoir['economics']['destination_configured_apy']-reservoir['economics']['outer_loan_frozen_apy']) and close(reservoir['economics']['destination_minus_inner_loan_apy'],reservoir['economics']['destination_configured_apy']-reservoir['economics']['inner_loan_frozen_apy']))
    check('Manager published mark ages match T and fees use verified denominators',all(r['navT']['oracle_age_days_at_T']>0 and close(r['terms']['fees']['redemption_instant_fee_rate'],r['terms']['fees']['redemption_instant_fee_raw']/10000) and r['category_capital_USD'] is None for r in variants['products'] if r['id'] in ['mre7eth','mhypereth']))
    check('Withdrawal request window never promoted to payout deadline',all(r['terms']['exit']['guaranteed_wait_seconds'] is None for r in variants['products'] if r['id'] in ['tau-infinifi','reservoir-eth']))
    strategy=read('strategy_universe_expansion');check('PT active registry and loop intersection boundaries preserved',strategy['summary']['primaryRegistryEthereumMarkets']==494 and strategy['summary']['ethTaggedRegistryMarkets']==117 and strategy['summary']['activeUnexpiredETHTaggedRegistryMarkets']==4 and strategy['summary']['ethTaggedPublishedPTLoopMatches']==0)
    coverage=read('research_expansion_coverage');check('Coverage does not claim global completeness or unknown capital',not coverage['complete_global_market_census'] and coverage['global_unique_ETH'] is None and coverage['global_carry_capital_USD'] is None)
    input_errors=[]
    for obj in [chapter,coverage]:
        for r in obj['inputs']:
            if hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()!=r['sha256']:input_errors.append(r['path'])
    check('New chapter inputs match captured source hashes',not input_errors,input_errors)
    manifest=ROOT/'raw/eth/funding-atlas-2026-10-04/requests.jsonl';records=[json.loads(s) for s in manifest.read_text().splitlines()];bad=[];read_only=True
    for r in records:
        if r.get('path') and hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()!=r['sha256']:bad.append(r['path'])
        for q in r.get('request',[]):
            if q['method'] not in ['eth_call','eth_getBlockByNumber','eth_getCode','eth_chainId']:read_only=False
    check('Every funding capture matches its response hash',not bad,{'request_records':len(records),'errors':bad})
    check('Funding collector used only public reads',read_only)
    if (DATA/'credit_expansion_deep.json').exists():
        deep=read('credit_expansion_deep');s=deep['summary']
        check('USDC lot income and funding result independently reconcile',close(sum(c['allocated_vault_income_units'] for c in deep['cases'] if c['debt_currency']=='USDC'),s['A_borrowed_lots_allocated_vault_income_USDC']) and close(s['A_borrowed_lots_allocated_vault_income_USDC']-s['A_borrowed_lots_funding_cost_at_redemption_USDC'],s['A_borrowed_lots_allocated_funded_result_before_gas_USDC']))
        b=next(c for c in deep['cases'] if c['debt_currency']=='PYUSD')
        check('PYUSD repayment residual liability and funded result reconcile',close(b['paid_debt_units']+b['residual_debt_units_at_repayment']-b['borrowed_units'],b['funding_cost_through_repayment_units']) and close(b['redemption_units']-b['deposited_units']-b['funding_cost_through_repayment_units'],b['funded_result_before_gas_units']))
        check('Carry lifecycles do not fabricate owners or whole-wallet profit',all(c['beneficial_owner'] is None and c['whole_wallet_profit'] is None for c in deep['cases']) and s['whole_wallet_profit'] is None)
    sd=read('strategy_universe_deep');bench={h['timestamp']:h for h in sd['benchmarks'][0]['history']}
    check('Additional returns use matched dated stETH blocks',all(close(w['bookExcessPercentagePoints'],w['bookReturnPct']-w['benchmarkBookReturnPct']) and next(h['block'] for h in p['history'] if h['date']==w['startDate'])==bench[next(h['timestamp'] for h in p['history'] if h['date']==w['startDate'])]['block'] for p in sd['products'] for w in p['windowReturns']))
    md=read('manager_case_chapter');mc=read('manager_case_capture')
    check('hgETH loan buffer fees and reserved adapter reconcile',close(md['loanBookRsETH']+md['physicalRsETH']-md['collectableFeesRsETH']+md['reservedAdapterRsETH'],md['bookRsETH']) and md['control']['runtimeMatchesVerifiedSource'] and not md['carryUseVerified'])
    check('hgETH history and ownership remain fixed-T scoped',all(r['timestamp']<=T for r in md['history']) and md['control']['threshold']==3 and len(md['control']['signers'])==5 and md['wholeInvestorProfit'] is None)
    manager_records=[json.loads(s) for s in (ROOT/mc['raw_manifest']).read_text().splitlines()]
    check('hgETH capture source hashes match',all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in manager_records if r.get('path')))
    fd=read('funding_borrower_deep_chapter');swap=fd['traced_accounts'][1]['dollar_conversion']
    check('Largest Safe conversion reconciles cash plus opening balance',close(swap['cash_loan_USDC']+swap['opening_owner_USDC'],swap['USDC_sold']) and close(sum(s['buy_amount'] for s in swap['settlements']),swap['USDT_received']) and swap['CoW_settlement_count']==19)
    check('Largest borrowers are not fabricated carry positions',all(not r['whole_account_carry_use_verified'] and r['carry_investment_capital_USD'] is None and r['profit_or_yield_attributed'] is None for r in fd['traced_accounts']))
    result={'all_checks_passed':all(c['passed'] for c in checks),'financial_snapshot_timestamp':T,'site_sha256':hashlib.sha256((ROOT/'eth/index.html').read_bytes()).hexdigest(),'checks':checks,'scope':'Independent captured-unit, arithmetic, read-only source and presentation-boundary checks. This is not a global census or audit of private portfolio solvency.'}
    (DATA/'research_expansion_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':sum(c['passed'] for c in checks),'checks':len(checks),'failed':[c for c in checks if not c['passed']]}))
    if not result['all_checks_passed']:raise SystemExit(1)
if __name__=='__main__':run()
