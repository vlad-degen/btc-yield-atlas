"""A partial claims/control/debt graph, explicitly not a market-wide netting engine."""
import json
from collect import ROOT,T,V

def run():
 d=ROOT/'data/eth';read=lambda n:json.loads((d/(n+'.json')).read_text());edges=[]
 def edge(a,b,kind,source,**kw):edges.append({'from':a,'to':b,'kind':kind,'target_timestamp':T,'evidence':source,'status':'verified_selected_relationship','amount_is_additive_market_capital':False,**kw})
 for a in read('etherfi_verified_metrics')['aave_spark_accounts']:
  edge(V if a['position'].startswith('main') else '0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c',a['position'].split('_')[-1]+'_account','collateral_and_debt','etherfi_verified_metrics.json',collateral_USD=a['collateral_oracle_usd'],debt_USD=a['debt_oracle_usd'],net_account_equity_USD=a['equity_oracle_usd'])
 for address in ['0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3','0x528353aea55dbbbf18be26d5726afe6585898dc5']:
  edge(V,address,'owner_control','pilot_details_T.json')
 edge(V,'0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c','exclusive_controller','pilot_details_T.json; verified BoringDrone source')
 bs=read('etherfi_partial_balance_sheet')
 line=next(x for x in bs['lines'] if x['label']=='Liquid Monad ETH nested book claim')
 edge(V,'0xa024063b630d554078bbf985718b22f3c6870ee0','nested_share_claim','mono_identity_T.json; mono_accountant_T.json',ETH_book_claim=line['usd']/read('snapshot_manifest')['price']['coins']['coingecko:ethereum']['price'],owns_entire_Ethereum_supply=True,remote_backing_verified=False)
 for name,addr in [('senRLUSDv2','0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf'),('senPYUSDPRIMEv2','0xc21b08c16458202593d4d9b26b9984ee67b38bbd'),('STCUSD','0x88887be419578051ff9f4eb6c858a951921d8888')]:
  ll=next(x for x in bs['lines'] if x['label']==name);edge(V,addr,'ERC4626_claim','pilot_details_T.json',book_claim_USD_at_par=ll['usd'])
 ca={x['address']:x['symbol'] for x in read('carry_collateral_assets_T')['assets']}
 for x in read('carry_credit_lookthrough'):
  edge(x['vault'],x['adapter'],'approved_allocator','carry_vaults_T.json; carry_market_allocations_T.json')
  edge(x['adapter'],x['market_id'],'market_supply','carry_market_allocations_T.json',collateral_symbol=ca[x['collateral']],loan_asset=x['loan_asset'],expected_supply_units=x['expected_adapter_supply_loan_units'],market_supply_share=x['adapter_fraction_of_market_supply_shares'])
  if x['main_plus_loan_manager_stored_debt']>1:
   edge('Liquid ETH + controlled LoanManager',x['market_id'],'borrow_debt','carry_market_allocations_T.json',loan_asset=x['loan_asset'],stored_debt_units=x['main_plus_loan_manager_stored_debt'],economic_self_credit_notional=x['lookthrough_self_credit_notional_loan_units'])
 safe='0x7ee29373f075ee1d83b1b93b4fe94ae242df5178'
 for vault,strategy in [('0xb9dc54c8261745cb97070cefbe3d3d815aee8f20','0xc8ea269d4dba296f7fbba812905c1b2efe5dbe1c'),('0xd57588c73715b65e0ead36ae06c15644169501b7','0x50a7510e73d79d60823dcac50e6b2c62e89ed82b')]:
  edge(vault,strategy,'accounting_strategy','concrete_lookthrough_T.json');edge(strategy,safe,'custody_manager','concrete_lookthrough_T.json',asset_allocation_exclusive_to_parent=False)
 edge(safe,'0xd57588c73715b65e0ead36ae06c15644169501b7','holds_entire_supply','concrete_self_holdings_T.json; vault_registry_rpc_T.json',external_deposit_provenance_verified=False)
 out={'target_timestamp':T,'scope':'selected product claim/control/debt graph; not full market coverage','market_wide_netting_complete':False,'edges':edges,'unresolved':['native consensus total','issuers and all receipts','remote bridge backing','exclusive allocation of shared Concrete Safe','external beneficial holders','in-flight shares','full account universe and historic edges']}
 # Identical allocator edges are de-duplicated before saving.
 seen=set();unique=[]
 for e in edges:
  key=(e['from'],e['to'],e['kind'])
  if key not in seen:unique.append(e);seen.add(key)
 out['edges']=unique;(d/'dependency_graph.json').write_text(json.dumps(out,indent=2));print('Selected verified relationships',len(unique))

if __name__=='__main__':run()
