"""Evidence integrity, financial units and time/scope checks for this release."""
import collections,datetime as dt,hashlib,json,math,re
from collect import ROOT,RAW,T

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def run():
 dest=ROOT/'data/eth';read=lambda n:json.loads((dest/(n+'.json')).read_text());checks=[]
 def check(name,condition,details=None):
  checks.append({'check':name,'passed':bool(condition),'details':details})
 inv=json.loads((ROOT/'research/project-study-inventory.json').read_text())['inventory'];bad=[]
 for f in inv:
  p=ROOT/f['path']
  if not p.is_file() or p.stat().st_size!=f['bytes'] or digest(p)!=f['sha256']:bad.append(f['path'])
 check('original_BTC_files_unchanged',not bad,{'checked':len(inv),'changed':bad})
 records=[json.loads(s) for s in (RAW/'requests.jsonl').read_text().splitlines()];expected={r['path']:r['sha256'] for r in records if r.get('path')};rawfiles=[];errors=[]
 for p in sorted(RAW.rglob('*')):
  if not p.is_file():continue
  path=str(p.relative_to(ROOT));sha=digest(p)
  if path in expected and sha!=expected[path]:errors.append(path)
  rawfiles.append({'path':path,'bytes':p.stat().st_size,'sha256':sha,'collector_response':path in expected})
 for path in expected:
  if not (ROOT/path).is_file():errors.append(path)
 check('immutable_raw_response_hashes',not errors,{'response_files':len(expected),'all_raw_files_including_manual_UI':len(rawfiles),'errors':errors})
 rawmanifest={'created_at':dt.datetime.now(dt.timezone.utc).isoformat(),'target_timestamp':T,'request_records':len(records),'files':rawfiles,'total_bytes':sum(x['bytes'] for x in rawfiles),'manual_observation_rule':'Manual public-UI observations are marked in file content, hashed here, and are not independently fetched collector API responses.'}
 (dest/'raw_manifest.json').write_text(json.dumps(rawmanifest,indent=2))
 snap=read('snapshot_manifest');check('four_mandatory_execution_block_boundaries',len(snap['chains'])==4 and all(x['block_timestamp']<=T<x['next_timestamp'] and x['last_block_at_or_before_T_verified'] for x in snap['chains']))
 future=[];nblocks=0
 for name in ['benchmark_history_ethereum_rpc','benchmark_history_optimism_rpc']:
  x=read(name)
  for r in x['responses']:
   lab=x['labels'][r['id']-1]
   if lab['metric']=='block' and r.get('result'):
    nblocks+=1
    if int(r['result']['timestamp'],16)>lab['target_timestamp']:future.append({'source':name,'target':lab['target_timestamp'],'block':lab['block']})
 check('archive_benchmark_no_future_blocks',not future,{'blocks':nblocks,'violations':future})
 hist=read('etherfi_history_points');check('published_PPS_not_taken_from_future',all(x['liquidETH_rate_timestamp']<=x['target_timestamp'] for x in hist))
 m=read('etherfi_verified_metrics');check('Liquid_ETH_book_NAV_arithmetic',math.isclose((m['ethereum_shares']+m['optimism_shares'])*m['rate_eth_per_share'],m['published_book_nav_eth'],rel_tol=1e-12))
 bs=read('etherfi_partial_balance_sheet');check('partial_NAV_keeps_visible_residual',math.isclose(sum(x['usd'] for x in bs['lines']),bs['partial_reconstruction_usd'],rel_tol=1e-12) and math.isclose(bs['published_book_nav_usd']-bs['partial_reconstruction_usd'],bs['unresolved_residual_usd'],abs_tol=1e-6))
 uni=read('etherfi_uniswap_positions');check('Uniswap_token_order_and_principal_units',all(x['token0']=='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2' and x['token1']=='0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee' for x in uni) and math.isclose(sum(x['backing_equivalent_eth'] for x in uni),m['uniswap_principal_eth'],rel_tol=1e-12))
 fl=read('fluid_lite_balance_T');check('Fluid_real_aggregate_leverage_not_gross_TVL',fl['debt_eth_equivalent']>0 and math.isclose(fl['gross_assets_eth_equivalent']/fl['net_assets_eth_equivalent'],fl['collateral_leverage'],rel_tol=1e-12))
 check('Treehouse_history_denomination_proof',read('treehouse_denomination_history')['historical_wstETH_denomination_verified'])
 check('rsETH_history_oracle_identity_proof',read('rseth_benchmark_rpc')['historical_oracle_identity_verified'])
 comparative=read('comparable_ETH_wealth');checksreturns=[]
 for name,ps in comparative['series'].items():
  checksreturns.append(ps[0]['timestamp']==T-730*86400 and ps[-1]['timestamp']==T and all(p['ETH_book_unit_value']>0 for p in ps) and math.isclose(ps[0]['normalized_ETH_book_wealth'],100,abs_tol=1e-9))
 check('six_products_use_same_ETH_return_window',all(checksreturns),{'observed_points':{n:len(p) for n,p in comparative['series'].items()},'missing_intermediate_points_are_not_zero':True})
 rows=read('protocol_eth_history_monthly');pairs={(r['protocol'],r['period']) for r in rows};missing=sum(x.get('eth_family_reported_usd') is None for x in rows)
 check('24_month_rows_unique_and_missing_retained',len(pairs)==len(rows)==87*24,{'rows':len(rows),'missing_token_observations':missing})
 futureobs=[x['protocol'] for x in rows if x.get('source_timestamp',0)>x['target_timestamp']];check('protocol_history_no_future_points',not futureobs,{'violations':futureobs})
 c=read('carry_credit_lookthrough');check('carry_share_fractions_use_supplyShares',all(0<=x['adapter_fraction_of_market_supply_shares']<=1 and 0<=x['liquidETH_fraction_of_vault_book']<=1 and x['lookthrough_self_credit_notional_loan_units']>=0 for x in c))
 symbols={x['address']:x['symbol'] for x in read('carry_collateral_assets_T')['assets']};check('kBTC_and_syrupUSDC_are_distinct',symbols['0x73e0c0d45e048d25fc26fa3159b0aa04bfa4db98']=='kBTC' and symbols['0x80ac24aa929eaf5013f6436cda2a7ba190f5cc0b']=='syrupUSDC')
 mono=read('mono_identity_T');mm={r['id']:r.get('result') for r in mono['responses']};check('nested_Monad_receipt_internal_share_supply',mm[3]==mm[5] and int(mm[3],16)>0)
 remote=read('mono_remote_T');rm={r['id']:r.get('result') for r in remote['responses']};check('Monad_extra_block_boundary',int(rm[2]['timestamp'],16)<=T<int(rm[3]['timestamp'],16) and int(rm[1],16)==143)
 holdings=read('concrete_self_holdings_T');vr=read('vault_registry_rpc_T');vvals={l['product'].lower():{} for l in vr['labels']}
 for l,r in zip(vr['labels'],vr['responses']):
  if r.get('result'):vvals[l['product'].lower()][l['signature']]=r['result']
 wst='0xd57588c73715b65e0ead36ae06c15644169501b7';check('Concrete_wst_supply_is_held_by_custody_Safe',int(holdings['responses'][1]['result'],16)==int(vvals[wst]['totalSupply()'],16))
 seg=read('segment_checks_T');deltaheld=next(r['result'] for l,r in zip(seg['labels'],seg['responses']) if l['address']=='0xb9dc54c8261745cb97070cefbe3d3d815aee8f20' and l['signature']=='balanceOf(address)');check('Concrete_Delta_entire_supply_single_holder_T',int(deltaheld,16)==int(vvals['0xb9dc54c8261745cb97070cefbe3d3d815aee8f20']['totalSupply()'],16))
 ps=read('pendle_eth_market_screen');check('Pendle_expiry_keeps_claims',len(ps)==126 and sum(x['expired_at_T'] for x in ps)==122 and all(x['pt'] for x in ps))
 pc=read('pendle_source_coverage');check('Pendle_list_pages_complete_for_four_chains',sum(x['listed_markets'] for x in pc)==626 and all(x['listed_markets']==x['collected_unique_markets'] for x in pc))
 screen=read('market_summary');check('unresolved_net_market_totals_are_null',screen['unique_underlying_ETH'] is None and screen['verified_external_depositor_equity_ETH'] is None and screen['not_net_market_capital'])
 wm=read('weth_lending_markets_T')['markets'];ws=read('weth_lending_summary_T')
 check('selected_WETH_markets_have_fixed_chain_blocks',len(wm)==5 and all(x['target_timestamp']==T and x['block']==next(s['block'] for s in snap['chains'] if s['chain']==x['chain']) and x['lender_claim_units']>0 and x['debt_units']>0 for x in wm))
 check('WETH_claim_debt_subtotals_and_deficit_not_zero_filled',math.isclose(sum(x['lender_claim_units'] for x in wm),ws['selected_WETH_lender_claims'],rel_tol=1e-12) and math.isclose(sum(x['debt_units'] for x in wm),ws['selected_WETH_debt'],rel_tol=1e-12) and next(x for x in wm if x['protocol']=='spark')['extra_getters']=={})
 chain=read('chain_screen');pool=read('yield_pool_candidates');check('gross_discovery_sums_reconcile_without_net_label',math.isclose(sum(x['reported_full_pool_tvl_usd'] for x in chain),sum(x['tvlUsd'] for x in pool),rel_tol=1e-12) and len(chain)==57 and len(pool)==5688)
 badlinks=[]
 for p in (q for q in (ROOT/'research/eth').rglob('*.md') if 'curated' not in q.parts):
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if target.startswith(('http:','https:','#')):continue
   target=target.split('#')[0].strip('<>')
   target=re.sub(r':\d+$','',target)  # Codex clickable source links may carry a line number.
   if target and not (p.parent/target).exists():badlinks.append({'file':str(p.relative_to(ROOT)),'target':target})
 check('local_report_links_resolve',not badlinks,{'broken':badlinks})
 ledger=read('evidence_ledger');badproof=[]
 for c in ledger['claims']:
  for p in c['semantic_inputs']:
   if not (ROOT/p['path']).is_file() or digest(ROOT/p['path'])!=p['sha256']:badproof.append(c['id']+':semantic_input_hash')
  for p in c['manual_UI_files']:
   if not (ROOT/p).is_file():badproof.append(c['id']+':manual_UI_missing')
  if c['id']!='C22' and not c['source_responses'] and not c['manual_UI_files']:badproof.append(c['id']+':raw_provenance_missing')
 check('claim_ledger_input_hashes_and_raw_provenance',not badproof,{'claims':len(ledger['claims']),'violations':badproof})
 result={'created_at':dt.datetime.now(dt.timezone.utc).isoformat(),'target_timestamp':T,'all_integrity_checks_passed':all(c['passed'] for c in checks),'is_full_financial_audit':False,'checks':checks,'raw_stats':{k:rawmanifest[k] for k in ['request_records','total_bytes']},'research_completion':'First substantial release; full net-market sizing and execution stress remain open.'}
 (dest/'audit_results.json').write_text(json.dumps(result,indent=2));print(json.dumps({'passed':sum(x['passed'] for x in checks),'checks':len(checks),'failed':[x for x in checks if not x['passed']],'raw_files':len(rawfiles),'raw_MB':rawmanifest['total_bytes']/1e6,'BTC_files':len(inv)},ensure_ascii=False))
 if not result['all_integrity_checks_passed']:raise SystemExit(1)

if __name__=='__main__':run()
