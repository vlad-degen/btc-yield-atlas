"""Verify the market ledger and fixed-block carry evidence against captured inputs."""
import csv, hashlib, itertools, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/eth'
def read(name):return json.loads((DATA/(name+'.json')).read_text())
def close(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=.002)
def run():
 m=read('market_panel');c=read('carry_category_candidates');payload=read('site_payload');checks=[]
 def check(name,ok,details=None):checks.append({'check':name,'passed':bool(ok),'details':details})
 check('market_inputs_match_captured_hashes',all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in m['inputs']+m['chain_inputs']))
 check('24_closed_months_and_separate_snapshot',len(m['months'])==24 and m['months'][0]['period']=='2024-10' and m['months'][-1]['period']=='2026-09' and m['current']['period'].endswith('snapshot') and m['current']['target_timestamp']==1790985599)
 check('USD_and_ETH_category_totals_reconcile',all(close(p[k],sum((v[k] or 0) for v in p['by_category'].values())) for p in m['months']+[m['current']] for k in ['usd','eth_ref','gross_positive_usd','negative_usd']))
 points=[p['current'] for p in m['products']]+[r for p in m['products'] for r in p['history']]
 check('signed_balances_and_ETH_reference_conversion',all(close(r['usd'],r['gross_positive_usd']+r['negative_usd']) and close(r['eth_ref'],r['usd']/r['reference_ETH_USD']) for r in points if r['usd'] is not None))
 check('missing_and_stale_points_stay_null',all(r['usd'] is None and r['eth_ref'] is None for r in points if r['status']=='missing') and all(r['source_age_seconds']>m['maximum_source_age_seconds'] for r in points if r['status']=='stale') and any(r['status']!='observed' for r in points))
 check('non_ETH_prefixes_excluded_from_core',m['selection']['arbitrary_AETH_prefix_allowed'] is False and all(not any(t in r.get('selected_tokens_usd',{}) for t in ['AETHUSDC','AETHRLUSD','AETHPYUSD','AETHUSDT','AETHWBTC']) for r in points))
 check('each_role_reconciles_to_protocol_rows',all(close(t[k],sum((r[k] or 0) if r['status']=='observed' else 0 for p in m['products'] if p['category']==category for r in ([p['current']] if period.endswith('snapshot') else [next(h for h in p['history'] if h['period']==period)]))) for period,point in [(p['period'],p) for p in m['months']+[m['current']]] for category,t in point['by_category'].items() for k in ['usd','eth_ref']))
 check('coverage_reconciles_and_liquidity_gap_visible',all(x['coverage']['expected']==x['coverage']['observed']+x['coverage']['missing']+x['coverage']['stale'] for point in m['months']+[m['current']] for x in [point]+list(point['by_category'].values())) and {'uniswap-v3','uniswap-v4','balancer-v2','sushiswap'}<=set(m['current']['coverage']['missing_protocols']))
 masks=[]
 for mask in itertools.product([False,True],repeat=6):
  ids={m['categories'][i]['id'] for i,v in enumerate(mask) if v}
  for point in m['months']+[m['current']]:
   rows=[p['current'] if point['period'].endswith('snapshot') else next(h for h in p['history'] if h['period']==point['period']) for p in m['products'] if p['category'] in ids]
   for k in ['usd','eth_ref']:
    byrows=sum((r[k] or 0) for r in rows if r['status']=='observed');bycats=sum(v[k] or 0 for key,v in point['by_category'].items() if key in ids)
    if not close(byrows,bycats):masks.append([mask,point['period'],k])
 check('all_64_category_selections_reconcile',not masks,{'violations':len(masks),'examples':masks[:4]})
 check('constant_cohort_reconciles_for_every_month_and_role',all(close(point['by_category'][category]['constant_cohort'][k],sum((r[k] or 0) for p in m['products'] if p['category']==category and p['id'] in m['constant_cohort_protocols'] for r in ([p['current']] if point['period'].endswith('snapshot') else [next(h for h in p['history'] if h['period']==point['period'])]))) for point in m['months']+[m['current']] for category in point['by_category'] for k in ['usd','eth_ref']))
 check('chain_view_keeps_aggregate_difference',close(m['chain_sum_usd'],sum(r['usd'] or 0 for r in m['chains'])) and close(m['chain_vs_aggregate_difference_usd'],m['chain_sum_usd']-m['current']['usd']) and m['chain_reconciliation_complete'] is False)
 check('new_market_data_is_embedded_exactly',payload['marketPanel']==m and payload['carryCategory']['products']==c['products'])
 captures=c['rpc_captures']+c['history_captures']+c['supplementary_captures']
 hashes=[]
 for cap in captures:
  expected=cap.get('response_sha256') or cap.get('response_canonical_json_sha256');sort='response_canonical_json_sha256' in cap
  actual=hashlib.sha256(json.dumps(cap['responses'],sort_keys=sort,separators=(',',':')).encode()).hexdigest()
  if actual!=expected:hashes.append(expected)
 check('carry_RPC_response_hashes_match',not hashes,hashes)
 check('carry_RPC_calls_are_historical_and_read_only',all(r['method'] in ['eth_call','eth_getCode'] and r['params'][-1].startswith('0x') for cap in captures for r in cap['request_payload']) and c['rpc_captures'][0]['block']==26108081)
 rpc=c['history_rpc_records']+c['supplementary_rpc_records']
 check('predeployment_is_backed_by_empty_code',all(r['raw_response'].get('result')=='0x' and r['code_check_response'].get('result')=='0x' for r in rpc if r['status']=='absent_predeployment'))
 check('decoded_archive_units_match_raw_words',all(close(r['native_value'],int(r['raw_response']['result'],16)/10**r['decoded_decimals']) for r in rpc if r.get('native_value') is not None and r.get('decoded_decimals') is not None))
 histories=[r for p in c['products'] for r in p['history']]
 check('carry_allocations_not_invented_backwards',len(histories)==168 and all(r['carryAllocationPercent'] is None and r['categoryCapitalETH'] is None and r['categoryCapitalUSD'] is None for r in histories))
 check('carry_product_history_coverage_matches_rows',all(p['historyCoverage']['availableMonths']==len([r for r in p['history'] if r['sizeETH'] is not None]) for p in c['products']) and all(r['sizeETH'] is None for r in histories if r['status']=='absent_predeployment'))
 check('carry_USD_marks_match_book_ETH',all(close(r['sizeUSD'],r['sizeETH']*r['priceUSD']) for r in histories if r['sizeUSD'] is not None) and all(r['timestamp']>=r['priceUpdatedAt'] and r['timestamp']-r['priceUpdatedAt']<=3420 for r in histories if r.get('priceUpdatedAt') is not None))
 with (ROOT/'eth/data/carry-category-history.csv').open() as f:rows=list(csv.DictReader(f))
 original_rows=[r for r in rows if r['source_ledger']=='carry_category_candidates.json']
 check('carry_CSV_preserves_all_products_and_nulls',len(rows)==192 and len(original_rows)==168 and all((row['book_NAV_ETH']=='' if r['sizeETH'] is None else close(float(row['book_NAV_ETH']),r['sizeETH'])) and row['historical_carry_allocation_percent']=='' for row,r in zip(original_rows,histories)))
 html=(ROOT/'eth/index.html').read_text();js=(ROOT/'tools/eth/site/market.js').read_text()
 check('main_page_has_market_to_carry_reading_order',html.index('id="map"')<html.index('id="market-history"')<html.index('id="market-categories"')<html.index('id="how"')<html.index('id="top5"')<html.index('id="market"')<html.index('id="risks"')<html.index('id="do"')<html.index('id="data"') and all(id in html for id in ['id="m-category-changes"','id="m-chain-table"','id="c-history-table"']))
 check('small_carry_products_are_retained',all(name in js for name in ['Liquity ETH Carry','TAU InfiniFi ETH Carry','Reservoir ETH Yield','Royco ETH']) and 'max>=' not in js and '.filter(p=>CARRY_DEDICATED.includes(p.product))' in js)
 result={'all_checks_passed':all(r['passed'] for r in checks),'checks':checks,'site_sha256':hashlib.sha256((ROOT/'eth/index.html').read_bytes()).hexdigest(),'scope':'Accounting and provenance of the measured layered exposure ledger and carry book histories. Not unique-market sizing, historical carry attribution, custody reconciliation or executable returns.'}
 (DATA/'market_audit_results.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({'passed':sum(r['passed'] for r in checks),'checks':len(checks),'failed':[r for r in checks if not r['passed']]}))
 if not result['all_checks_passed']:raise SystemExit(1)
if __name__=='__main__':run()
