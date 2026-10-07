"""Verify the BTC chapter contract, new financial scenarios and portable view exports."""
import csv,hashlib,json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(name):return json.loads((ROOT/'data/eth'/f'{name}.json').read_text())
def run():
 checks=[]
 def check(name,ok,detail=None):checks.append({'check':name,'passed':bool(ok),'details':detail})
 m=read('market_reader_chapter');b=read('research_borrowers');e=read('carry_economics_chapter');p=read('product_chapters');source=(ROOT/'tools/eth/site/index.html').read_text();js=(ROOT/'tools/eth/site/strict.js').read_text();html=(ROOT/'eth/index.html').read_text()
 check('reduced_reader_navigation_and_preserved_evidence_anchors',re.findall(r'<section[^>]* id="([^"]+)"',source)==['top','map','how','top5','market','risks','do','data'] and re.findall(r'<a href="[^"]+">([^<]+)</a>',source[source.index('<nav'):source.index('</nav>')])==['Answer','Market','Top 5','Other carry','Risks','Data'] and '<section id="how" hidden>' in source and '<section id="do" hidden>' in source and '<details class="more" id="reader-risk-details">' in source)
 check('counted_once_categories_and_optional_financing',[c['id'] for c in m['categories']]==['staking','restaking','loops','carry','fixed_yield','basis','options','credit','farming','lending','cdp'] and m['default_selection']==[c['id'] for c in m['categories'] if c['id'] not in ('lending','cdp')])
 canonical=read('market_panel');byid={p['id']:p for p in canonical['products']};excluded=byid['justlend-v1']
 check('Tron_and_infrastructure_rows_excluded_with_reasons',not any(p['id'] in ('justlend-v1','ssv-network','obol','concrete') for p in m['products']) and all(r['reason'] for r in m['excluded_protocols']) and any(r['id']=='justlend-v1' for r in m['excluded_protocols']))
 check('Tron_exclusion_applies_to_every_month_category_and_chain',all(math.isclose(sum(p['history'][i]['usd'] for p in m['products'] if p['history'][i]['status']=='observed'),month['usd'],abs_tol=.0001) for i,month in enumerate(m['months'])) and not any(c['chain']=='Tron' for c in m['chains']) and all(p['id']!='justlend-v1' for p in m['products']))

 errors=[]
 for cohort in ['observed','constant']:
  for mask in [2**len(m['categories'])-1]:  # other mixes are built in the browser
   selected=[c for i,c in enumerate(m['categories']) if mask&(1<<i)]
   with (ROOT/'eth/data'/f'market-series-{cohort}-{mask}.csv').open() as f:rows=list(csv.DictReader(f))
   if len(rows)!=24:errors.append([cohort,mask,'row count'])
   for row,month in zip(rows,m['months']):
    values=[]
    for c in selected:
     base=month['by_category'][c['id']];x=base['constant_cohort'] if cohort=='constant' else base;n=x.get('protocol_count',0) if cohort=='constant' else base['coverage']['observed'];values.append(x if n else {'eth_ref':None,'usd':None})
    et=sum(x['eth_ref'] or 0 for x in values);us=sum(x['usd'] or 0 for x in values)
    if any(x['eth_ref'] is not None for x in values):
     if not math.isclose(float(row['selected_total_ETH']),et,abs_tol=1e-7) or not math.isclose(float(row['selected_total_USD']),us,abs_tol=.0001):errors.append([cohort,mask,month['period'],'total'])
    elif row['selected_total_ETH']!='' or row['selected_total_USD']!='':errors.append([cohort,mask,month['period'],'unmeasured total'])
    for c,x in zip(selected,values):
     for unit,key,total in [('ETH_equivalent','eth_ref',et),('USD','usd',us),('share_ETH','eth_ref',et),('share_USD','usd',us)]:
      val=x[key];expected=val if not unit.startswith('share') else (val/total if val is not None and total else None);actual=row[c['id']+'_'+unit]
      if expected is None:
       if actual!='':errors.append([cohort,mask,c['id'],unit,'null'])
      elif not math.isclose(float(actual),expected,rel_tol=1e-12,abs_tol=1e-9):errors.append([cohort,mask,c['id'],unit,'value'])
 check('all_512_selection_exports_match_data_and_nulls',not errors,errors[:12])
 check('main_exhibits_and_five_data_disclosures_exist',all(f'id="{x}"' in source for x in ['strict-worked-example','strict-venue-table','strict-borrow-markets','strict-curve-table','strict-calc-inputs','strict-top5-comparison','strict-product-tabs','strict-landscape','strict-borrowers-table','strict-risk-table','strict-playbook-scenarios','strict-reward-payers','strict-product-rules','strict-partners','strict-method','strict-exclusions','strict-discovery','strict-recheck','sources']))
 check('financial_state_date_is_frozen',e['target_timestamp']==m['financial_snapshot_timestamp']==b['financial_snapshot_timestamp']==1790985599 and e['financial_snapshot_refreshed'] is False and p['snapshot']=='2026-10-02T23:59:59Z')
 calc=e['calculator'];baseline=calc['staking_baseline']['annual_rate'];errors=[]
 for preset in calc['presets']:
  v=preset['inputs'];r=preset['result'];debt=v['collateral_share']*v['ltv'];net=baseline+debt*(v['parking_rate']-v['borrow_rate'])-v['operator_fee'];no=baseline+debt*(v['parking_rate']*(1-v['reward_share'])-v['borrow_rate'])-v['operator_fee']
  for key,expected in [('net_ETH_income',net),('no_reward_ETH_income',no),('health_factor',v['cf']/v['ltv']),('collateral_price_drop_to_liquidation',1-v['ltv']/v['cf'])]:
   if not math.isclose(r[key],expected,abs_tol=1e-12):errors.append([preset['id'],key])
 check('four_presets_match_seven_input_financial_model',len(calc['presets'])==4 and all(len(row['inputs'])==7 for row in calc['presets']) and not errors,errors)
 check('calculator_fee_and_liquidation_scope_explicit',calc['operator_fee_basis'].startswith('Annual NAV fee') and calc['liquidation_model']['status'].startswith('Illustrative') and all(x in js for x in ['v.operator_fee','debt*.5*1.05/price','debt*.5*.05/price','debt?v.cf/v.ltv:null']))
 check('worked_loan_does_not_claim_measured_income',e['worked_example']['modeled_income']['not_measured_income'] is True and e['worked_example']['measured_leg']['source_of_parked_funds_traced'] is False and e['worked_example']['measured_leg']['whole_product_carry_return'] is None)
 curves=[x for x in e['borrow_markets'] if x['rate_model']['points']];check('22_markets_and_seven_actual_models',len(e['borrow_markets'])==22 and len(curves)==7 and all(x['rate_model']['T_runtime_matches_verified_source'] is True for x in e['borrow_markets']) and sum(len(x['rate_model']['points']) for x in curves)==140)
 check('borrow_APR_and_annual_equivalent_consistent',all(math.isclose(math.expm1(x['borrow_apr']),x['borrow_apy'],abs_tol=1e-10) for x in e['borrow_markets']))
 opt=next(x for x in e['destinations'] if x['id']=='aave-usdc-optimism');check('missing_Optimism_rewards_remain_unknown',opt['reward_apy'] is None and math.isclose(opt['gross_apy'],opt['organic_apy']) and 'reward coverage unverified' in js)
 check('four_playbook_tables_have_research_rows',all(len(e['playbook'][key])>=4 for key in ['scenarios','reward_payers','rules','partners']))
 check('top_five_are_ranked_measured_carry_designs',[x['id'] for x in p['products']]==['concrete','liquid','rocksolid','liquity','royco'] and all(a['capitalETH']>=b['capitalETH'] for a,b in zip(p['products'],p['products'][1:])))
 check('same_product_chapter_sequence',all(x in js for x in ['data-product-part="flow"','data-product-part="actors"','data-product-part="payers"','data-product-part="capital"','data-product-part="holders"','data-product-part="loans"','data-product-part="timeline"']) and all(js.index('data-product-part="'+a+'"')<js.index('data-product-part="'+b+'"') for a,b in zip(['flow','actors','payers','capital','holders','loans'],['actors','payers','capital','holders','loans','timeline'])))
 check('each_product_has_ownership_and_event_evidence',all(row['charts']['walletDistribution']['rows'] and row['timeline'] and row['actors'] and row['sources'] for row in p['products']))
 with (ROOT/'eth/data/carry-category-history.csv').open() as f:rock_export=[r for r in csv.DictReader(f) if r['product']=='Rocksolid rETH']
 rock_points={r['month']:r for r in next(x for x in p['products'] if x['id']=='rocksolid')['charts']['capitalHistory']['rows']}
 check('Rocksolid_export_matches_capital_chart_and_preserves_missing',len(rock_export)==24 and all((r['book_NAV_ETH']=='' if r['month'] not in rock_points else math.isclose(float(r['book_NAV_ETH']),rock_points[r['month']]['sizeETH'],abs_tol=1e-9)) and r['historical_carry_allocation_percent']=='' and r['source_ledger']=='product_chapters.json' for r in rock_export))
 check('product_data_has_no_progress_placeholders',not re.search(r'in progress|being completed|pending integration',json.dumps(p),re.I))
 check('borrower_native_unit_and_identity_boundaries',len(b['positions'])==237 and len(b['borrowers'])==213 and b['summary']['identified_chain_addresses']==3 and all(x['carry_mechanism_verified'] is False and x['target_snapshot_verified'] is False for x in b['positions']) and math.isclose(sum(x['debt_usd'] for x in b['borrowers']),b['summary']['sampled_debt_usd'],abs_tol=.00001))
 refs=[]
 for r in e['sources']:
  if r.get('path') and r.get('sha256'):
   f=ROOT/r['path'];refs.append(f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'])
 check('new_economics_source_hashes_match',refs and all(refs))
 check('embedded_chapters_match',all(read('site_payload')[k]==v for k,v in [('marketChapter',m),('borrowersChapter',b),('economicsChapter',e),('productChapters',read('reader_product_chapters')),('borrowRateHistory',read('carry_borrow_rate_history'))]))
 h=read('carry_borrow_rate_history');check('funded_monthly_borrow_rates_keep_nulls',len(h['rows'])==48 and all(r['block_verified'] for r in h['rows']) and sum(r['borrow_apr'] is not None for r in h['rows'] if r['series_id']=='liquid-main-weeth-rlusd')==3 and all(r['borrow_apr'] is None for r in h['rows'] if r['series_id']=='liquid-main-weeth-rlusd' and not r['main_account_funded']))
 check('closed_examples_are_explicitly_adjacent',all(x['includedInE4ClosedUniverse'] is False and x['closureDate'] is None and x['returnLossClaim'] is None for x in p['closedProducts']) and 'stClosedProduct' in js)
 result={'all_checks_passed':all(r['passed'] for r in checks),'checks':checks,'site_sha256':hashlib.sha256(html.encode()).hexdigest(),'scope':'User-requested shorter reader navigation with retained evidence anchors, preserved source observations, financial scenarios and exported selection views. Coverage limits remain explicit; this is not an independent solvency audit.'}
 (ROOT/'data/eth/strict_audit_results.json').write_text(json.dumps(result,indent=2));print(json.dumps({'passed':sum(r['passed'] for r in checks),'checks':len(checks),'failed':[r for r in checks if not r['passed']]}))
 if not result['all_checks_passed']:raise SystemExit(1)
if __name__=='__main__':run()
