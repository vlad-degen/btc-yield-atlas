"""Auditable numerical synthesis. Unknown market totals stay null."""
import collections, datetime as dt, json
from collect import ROOT,T,read_latest

DEST=ROOT/'data/eth'
def read(name):return json.loads((DEST/(name+'.json')).read_text())
def write(name,data):(DEST/(name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False))
def words(value):return [int(value[i:i+64],16) for i in range(2,len(value),64)]

def build():
 s=read('segment_checks_T');sv={l['signature']:r for l,r in zip(s['labels'],s['responses']) if l['address'].startswith('0xa0d370')}
 raw=words(sv['getNetAssets()']['result']);abi=read_latest('fluid_net_module_abi');spec=next(x['outputs'] for x in abi['abi'] if x.get('name')=='getNetAssets')
 def flatten(fields,prefix=''):
  out=[]
  for f in fields:
   name=prefix+f['name']
   if f['type']=='tuple':out.extend(flatten(f['components'],name+'.'))
   else:out.append(name)
  return out
 names=flatten(spec);assert len(names)==len(raw)
 f={'target_timestamp':T,'basis':'contract getNetAssets valuation; stETH/eETH/WETH parity assumptions in source, not independent market mark','decoded_raw':dict(zip(names,map(str,raw))),'gross_assets_eth_equivalent':raw[0]/1e18,'debt_eth_equivalent':raw[1]/1e18,'net_assets_eth_equivalent':raw[2]/1e18,'aggregated_debt_ratio':raw[3]/1e6,'collateral_leverage':raw[0]/raw[2],'withdraw_fee_for_one_stETH':int(sv['getWithdrawFee(uint256)']['result'],16)/1e18,'vault_DSA':'0x'+sv['vaultDSA()']['result'][-40:],'team_multisig_allocated_raw':str(int(sv['allocationToTeamMultisig()']['result'],16))}
 assert abs((raw[0]-raw[1]-raw[2])/1e18-int(sv['revenue()']['result'],16)/1e18)<1e-9
 write('fluid_lite_balance_T',f)
 cv=read('carry_vaults_T');values=collections.defaultdict(dict)
 for l,r in zip(cv['labels'],cv['responses']):values[l['vault']][l['signature']]=r.get('result')
 cm=read('carry_market_allocations_T');parents={l['adapter']:'0x'+r['result'][-40:] for l,r in zip(cm['adapter_labels'],cm['adapter_responses']) if l['signature']=='parentVault()'}
 rows=collections.defaultdict(dict)
 for l,r in zip(cm['market_labels'],cm['market_responses']):rows[(l['adapter'],l['market_id'])][l['signature']]=words(r['result']) if r.get('result') else None
 bs=read('etherfi_partial_balance_sheet');claims={x['label']:x['usd'] for x in bs['lines']}
 # Use the full claim values from fixed-block ERC4626 quotes, with stablecoins at $1.
 quotes=read('pilot_details_T');q={l['label']:r.get('result') for l,r in zip(quotes['labels'],quotes['responses'])}
 user_claims={'0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf':int(q['senRLUSDv2_convertToAssets'],16)/1e18,'0xc21b08c16458202593d4d9b26b9984ee67b38bbd':int(q['senPYUSDPRIMEv2_convertToAssets'],16)/1e6}
 out=[]
 for (adapter,mid),r in rows.items():
  vault=parents[adapter];p=r['idToMarketParams(bytes32)'];market=r['market(bytes32)'];dec=18 if p[0]==int('8292bb45bf1ee4d140127049757c2e0ff06317ed',16) else 6
  total=int(values[vault]['totalAssets()'],16)/10**dec;fraction=user_claims[vault]/total
  supplier_fraction=r['supplyShares(bytes32)'][0]/market[1] if market[1] else 0
  assert 0<=supplier_fraction<=1.000000001
  debtshares=sum(r[k][1] for k in ['main_borrower_position','loan_manager_position']);own_debt=debtshares/market[3]*market[2]/10**dec if market[3] else 0
  supplied=r['expectedSupplyAssets(bytes32)'][0]/10**dec
  out.append({'vault':vault,'adapter':adapter,'market_id':mid,'loan_asset':'0x'+hex(p[0])[2:].zfill(40),'collateral':'0x'+hex(p[1])[2:].zfill(40),'expected_adapter_supply_loan_units':supplied,'vault_book_assets_loan_units':total,'share_of_vault_assets':supplied/total,'liquidETH_claim_loan_units':user_claims[vault],'liquidETH_fraction_of_vault_book':fraction,'adapter_fraction_of_market_supply_shares':supplier_fraction,'main_plus_loan_manager_stored_debt':own_debt,'lookthrough_self_credit_notional_loan_units':fraction*supplier_fraction*own_debt,'stored_market_utilization':market[2]/market[0] if market[0] else None,'performance_fee_fraction':int(values[vault]['performanceFee()'],16)/1e18,'note':'Self-credit is an economic overlap diagnostic, not an additional asset or income; debt uses stored ratios without interest since lastUpdate. USD principal assumptions do not establish independent credit backing.'})
 write('carry_credit_lookthrough',out)
 m=read('etherfi_verified_metrics');stress=[]
 for a in m['aave_spark_accounts']:
  name=a['position'];C=a['collateral_oracle_usd'];D=a['debt_oracle_usd'];E=C-D
  stress.append({'account':name,'collateral':C,'debt':D,'account_equity':E,'HF':a['health_factor'],'oracle_markdown_to_HF_1':1-1/a['health_factor'],'collateral_leverage':C/E,'borrow_plus_100bp_isolated_equity_return_change_pp':-D/E,'borrow_plus_100bp_vault_return_change_pp':-D/m['published_book_nav_usd_nearest_quote'],'market_discount_1pct_equity_change_percent':-C/E,'note':'Isolated account sensitivity; no rate response, rebalancing, lending-income offsets or execution costs. Oracle markdown is not automatically DEX depeg or ETH/USD shock.'})
 write('stress_scenarios',stress)
 obs=[r for r in read('protocol_eth_observations') if r['period']=='snapshot'];obs.sort(key=lambda r:r['eth_family_reported_usd'],reverse=True)
 screen=read('discovery_summary');summary={**screen,'snapshot_UTC':dt.datetime.fromtimestamp(T,dt.timezone.utc).isoformat(),'unique_underlying_ETH':None,'verified_external_depositor_equity_ETH':None,'net_totals_status':'Not calculated: issuer overlap, leverage, bridge custody, internal shares and incomplete native consensus state remain open. Full mixed-pool screening sum is not a bound on unique ETH capital.','protocol_sources_with_token_history':sum(x.get('has_aggregate_token_history',False) for x in read('protocol_source_coverage')),'monthly_rows':len(read('protocol_eth_history_monthly')),'material_pools':len(read('material_pool_screen')),'top_dated_nonadditive_protocol_observations':obs[:25],'chain_screen':read('chain_screen')}
 write('market_summary',summary)
 print('Fluid leverage',f['collateral_leverage'],'carry self-credit diagnostics',[(r['market_id'],r['lookthrough_self_credit_notional_loan_units']) for r in out if r['lookthrough_self_credit_notional_loan_units']>1],'top dated observations',len(obs))

if __name__=='__main__':build()
