"""Offline, evidence-preserving expansion of ETH collateral borrowing routes."""
import collections,datetime as dt,hashlib,json,sys
from pathlib import Path
from credit_expansion_capture import ROOT,D,RAW,T,BLOCKS,array_addresses
from discover import FAMILY
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import keccak
USD={'USDC','USDT','USDS','DAI','GHO','USDe','RLUSD','PYUSD','USDbC','USDC.e','USD0','crvUSD'}

def read(name):
 p=D/('credit_expansion_'+name+'.json');return json.loads(p.read_text()) if p.exists() else {}
def words(result):
 return [int(result[i:i+64],16) for i in range(2,len(result),64)] if result and result!='0x' else []
def string(result):
 if not result or result=='0x':return None
 b=bytes.fromhex(result[2:]);off=int.from_bytes(b[:32])
 return (b[off+32:off+32+int.from_bytes(b[off:off+32])] if off==32 else b.rstrip(b'\0')).decode(errors='replace')
def token_metadata():
 out={}
 for l in read('token_metadata_T').get('labels',[]):
  if not l['response'].get('success'):continue
  r=l['response'].get('result');m=out.setdefault((l['chain'],l['token']),{})
  if l['signature']=='symbol()':m['symbol']=string(r)
  elif r and r!='0x':m['decimals']=int(r,16)
 for c in BLOCKS:out[(c,'0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')]={'symbol':'ETH','decimals':18}
 return out

def event(log):
 names={'Borrow(bytes32,address,address,address,uint256,uint256)':'Borrow','Repay(bytes32,address,address,uint256,uint256)':'Repay','Supply(bytes32,address,address,uint256,uint256)':'Supply','SupplyCollateral(bytes32,address,address,uint256)':'SupplyCollateral','WithdrawCollateral(bytes32,address,address,address,uint256)':'WithdrawCollateral'}
 topics={'0x'+keccak(sig.encode()).hex():name for sig,name in names.items()}
 if log['address'].lower()!='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb':return None
 name=topics.get(log['topics'][0]);w=words(log['data']);t=log['topics']
 if not name:return None
 nonindexedcaller=name in ['Borrow','WithdrawCollateral']
 out={'event':name,'market_id':t[1],'caller':'0x'+format(w[0],'064x')[-40:] if nonindexedcaller else '0x'+t[2][-40:],'on_behalf':'0x'+t[2 if nonindexedcaller else 3][-40:],'assets_raw':str(w[1 if nonindexedcaller else 0]),'shares_raw':str(w[2 if nonindexedcaller else 1]) if len(w)>(2 if nonindexedcaller else 1) else None}
 if nonindexedcaller:out['receiver']='0x'+t[3][-40:]
 return out

def build():
 meta=token_metadata();markets=[];borrowers=[];findings=[];coverage=[]
 for c in read('compound_T').get('chains',[]):
  chain=c['chain'];group=collections.defaultdict(list)
  for l in c['labels']:group[l['market_id']].append(l)
  for address,labels in group.items():
   primary={l['signature']:l['response'].get('result') for l in labels if not l.get('asset') and l['signature']!='getAssetInfo(uint8)'}
   base='0x'+primary['baseToken()'][-40:] if primary.get('baseToken()') not in [None,'0x'] else None
   bm=meta.get((chain,base),{});base_dec=bm.get('decimals',6 if labels[0]['registry_path'].endswith(('usdc','usdt','usdbc','usdc.e')) else 18)
   assets=[]
   for l in labels:
    if l['signature']!='getAssetInfo(uint8)':continue
    w=words(l['response'].get('result'))
    if not w:continue
    token='0x'+format(w[1],'040x');m=meta.get((chain,token),{});related={x['signature']:x['response'].get('result') for x in labels if x.get('asset')==token};symbol=m.get('symbol') or string(related.get('symbol()'));dec=m.get('decimals',int(related['decimals()'],16) if related.get('decimals()') not in [None,'0x'] else None)
    totals=words(related.get('totalsCollateral(address)'));price=words(related.get('getPrice(address)'));units=totals[0]/10**dec if totals and dec is not None else None
    assets.append({'asset_address':token,'symbol':symbol,'decimals':dec,'ETH_family':bool(symbol and symbol.upper() in FAMILY),'deposited_units':units,'oracle_USD_per_unit':price[0]/1e8 if price else None,'deposited_oracle_USD':units*price[0]/1e8 if units is not None and price else None,'borrow_collateral_factor':w[4]/1e18,'liquidation_collateral_factor':w[5]/1e18,'supply_cap_units':w[7]/10**dec if dec is not None else None})
   selected=[x for x in assets if x['ETH_family']]
   markets.append({'protocol':'Compound V3','chain':chain,'market_id':address,'registry_path':labels[0]['registry_path'],'financial_timestamp':T,'block':BLOCKS[chain],'debt_asset':base,'debt_symbol':bm.get('symbol') or labels[0]['registry_path'].split('/')[-1].upper(),'ETH_collateral_routes':selected,'all_collateral_assets':assets,'debt_units':int(primary['totalBorrow()'],16)/10**base_dec if primary.get('totalBorrow()') not in [None,'0x'] else None,'debt_scope':'Entire base-token market, including non-ETH collateral. Not an ETH-only debt measure.','borrow_APR':int(primary['getBorrowRate(uint256)'],16)*31536000/1e18 if primary.get('getBorrowRate(uint256)') not in [None,'0x'] else None,'supply_APR':int(primary['getSupplyRate(uint256)'],16)*31536000/1e18 if primary.get('getSupplyRate(uint256)') not in [None,'0x'] else None,'utilization':int(primary['getUtilization()'],16)/1e18 if primary.get('getUtilization()') not in [None,'0x'] else None,'status':'fixed_T_read' if primary.get('totalBorrow()') not in [None,'0x'] else 'historical_state_unavailable','source_artifact':'data/eth/credit_expansion_compound_T.json'})
 for c in read('fluid_T').get('chains',[]):
  chain=c['chain'];eligible=0
  for x in c['decoded']:
   cv=x['constantVariables'];coll=[{'asset_address':a,**meta.get((chain,a),{})} for a in cv['supplyToken'].values() if int(a,16)];debt=[{'asset_address':a,**meta.get((chain,a),{})} for a in cv['borrowToken'].values() if int(a,16)]
   if not any(a.get('symbol','').upper() in FAMILY for a in coll) or not any(a.get('symbol') in USD for a in debt):continue
   eligible+=1;simple=not x['isSmartDebt'];pureETH=all(a.get('symbol','').upper() in FAMILY for a in coll);dm=debt[0];dec=dm.get('decimals');amount=x['totalSupplyAndBorrow']['totalBorrowVault']/10**dec if simple and dec is not None else None
   markets.append({'protocol':'Fluid','chain':chain,'market_id':x['vault'],'vault_id':cv['vaultId'],'vault_type':cv['vaultType'],'financial_timestamp':T,'block':BLOCKS[chain],'collateral_assets':coll,'debt_assets':debt,'is_smart_collateral':x['isSmartCol'],'is_smart_debt':x['isSmartDebt'],'collateral_scope':'ETH family only' if pureETH else 'Mixed LP inventory including ETH','debt_units':amount,'debt_symbol':dm.get('symbol') if simple else 'DEX debt shares','debt_scope':'Pair-specific dollar debt against ETH-family collateral' if simple and pureETH else 'Mixed LP route; smart-debt shares cannot be presented as dollars.','borrow_APR':x['exchangePricesAndRates']['borrowRateVault']/10000 if simple else None,'supply_APR':x['exchangePricesAndRates']['supplyRateVault']/10000 if not x['isSmartCol'] else None,'collateral_factor':x['configs']['collateralFactor']/10000,'liquidation_threshold':x['configs']['liquidationThreshold']/10000,'borrow_limit_units':x['limitsAndAvailability']['borrowLimit']/10**dec if simple and dec is not None else None,'borrowable_units':x['limitsAndAvailability']['borrowable']/10**dec if simple and dec is not None else None,'collateral_units':x['totalSupplyAndBorrow']['totalSupplyVault']/10**coll[0]['decimals'] if not x['isSmartCol'] and coll[0].get('decimals') is not None else None,'total_positions':x['vaultState']['totalPositions'],'status':'fixed_T_read','source_artifact':'data/eth/credit_expansion_fluid_T.json'})
  coverage.append({'protocol':'Fluid','chain':chain,'registry_entries':c['registered_vault_count'],'decoded_entries':len(c['decoded']),'ETH_USD_eligible_routes':eligible})
 ltv={}
 for chunk in read('euler_ltv_T').get('chunks',[]):
  for l in chunk['labels']:
   w=words(l.get('response',{}).get('result'))
   if w:ltv[(l['chain'],l['loan_vault'],l['collateral_vault'],l['signature'])]=w[0]/10000
 for c in read('euler_T').get('chains',[]):
  chain=c['chain'];am={x['vault']:x['asset'] for x in c['assets']};group=collections.defaultdict(list)
  for l in c['stable_labels']:group[l['vault']].append(l)
  eligible=0
  for vault,labels in group.items():
   values={l['signature']:l.get('response',{}).get('result') if l.get('response',{}).get('success') else None for l in labels};coll=[]
   for cv in array_addresses(values.get('LTVList()')):
    asset=am.get(cv);m=meta.get((chain,asset),{});sym=m.get('symbol');ratio=ltv.get((chain,vault,cv,'LTVBorrow(address)'))
    if sym and sym.upper() in FAMILY:coll.append({'collateral_vault':cv,'asset_address':asset,**m,'borrow_LTV':ratio,'liquidation_LTV':ltv.get((chain,vault,cv,'LTVLiquidation(address)'))})
   if not coll:continue
   eligible+=1;debt_asset=labels[0]['asset'];m=meta.get((chain,debt_asset),{});dec=m.get('decimals');w=words(values.get('caps()'))
   caps=[None if value==0 else (10**(value&63)*(value>>6)//100)/10**dec for value in w] if dec is not None else None
   markets.append({'protocol':'Euler','chain':chain,'market_id':vault,'financial_timestamp':T,'block':BLOCKS[chain],'debt_asset':debt_asset,'debt_symbol':m.get('symbol'),'ETH_collateral_routes':coll,'active_ETH_collateral_routes':sum(bool(x.get('borrow_LTV') and x['borrow_LTV']>0) for x in coll),'all_accepted_collateral_count':len(array_addresses(values.get('LTVList()'))),'debt_units':int(values['totalBorrows()'],16)/10**dec if values.get('totalBorrows()') and dec is not None else None,'cash_units':int(values['cash()'],16)/10**dec if values.get('cash()') and dec is not None else None,'borrow_APR':int(values['interestRate()'],16)*31536000/1e27 if values.get('interestRate()') else None,'caps_encoded_uint16':w or None,'caps_units':{'supply':caps[0],'borrow':caps[1],'null_means':'No limit configured, when encoded value equals zero.'} if caps else None,'debt_scope':'Entire loan vault debt. ETH is an eligible collateral route; debt is not allocated to ETH borrowers.','status':'fixed_T_registry_read','source_artifact':'data/eth/credit_expansion_euler_T.json'})
  coverage.append({'protocol':'Euler','chain':chain,'registry_entries':c['registered_proxy_count'],'asset_reads':len(c['assets']),'canonical_dollar_vaults_screened':len(group),'ETH_collateral_routes':eligible,'asset_allowlist_scope':'Canonical USDC/USDT/DAI/sDAI/PYUSD/USDe/RLUSD/USDS and native Base USDC. Other dollar synthetics remain unenumerated.'})
 for c in read('silo_T').get('chains',[]):
  pairs=[]
  for config in c['configs']:
   assets=[{'silo':a,'asset_address':c['assets'].get(a),**meta.get((c['chain'],c['assets'].get(a)),{})} for a in config['silos']]
   if any(a.get('symbol','').upper() in FAMILY for a in assets) and any(a.get('symbol') in USD for a in assets):pairs.append({'id':config['id'],'config':config['config'],'assets':assets})
  coverage.append({'protocol':'Silo V2','chain':c['chain'],'configs_screened':len(c['configs']),'assets_read':len(c['assets']),'ETH_USD_pairs':pairs,'scope':'The current official V2 factory and id range starting 3000. Legacy V1, earlier factory generations and failed Arbitrum archive state are not covered.'})
 screen=json.loads((D/'research_borrowers.json').read_text());fixed=read('morpho_unknown_T');fixedgroup=collections.defaultdict(dict)
 for l in fixed.get('labels',[]):
  if l['chain_id']==1:fixedgroup[(l['chain_id'],l['address'],l['market_id'])][l['signature']]=l
 for b in screen['borrowers']:
  if b['identity_verified']:continue
  stable=sum(x['debt_usd'] for x in b['markets'] if x['debt'] in USD)
  if stable<5e6 and not (b['address']=='0x462a336dcac6eaf544106266914caa5a18b831d0' and b['chain_id']==1):continue
  positions=[]
  for m in b['markets']:
   f=fixedgroup.get((b['chain_id'],b['address'],m['market_id']),{});p=words(f.get('position(bytes32,address)',{}).get('fixed_T_response',{}).get('result'));state=words(f.get('market(bytes32)',{}).get('fixed_T_response',{}).get('result'));l=f.get('position(bytes32,address)',{});debt_raw=(p[1]*(state[2]+1)+(state[3]+1000000)-1)//(state[3]+1000000) if p and state else None
   positions.append({**m,'fixed_T_collateral_units':p[2]/10**l['collateral_decimals'] if p else None,'fixed_T_debt_units':debt_raw/10**l['debt_decimals'] if debt_raw is not None else None,'fixed_T_debt_raw':str(debt_raw) if debt_raw is not None else None,'fixed_T_measurement':'Stored market debt converted from borrow shares, rounded up. Does not accrue additional interest since the last market update.','fixed_T_status':'read' if p and state else 'not_yet_read'})
  history=[];records=[json.loads(x) for x in (RAW/'requests.jsonl').read_text().splitlines()]
  for page in range(5):
   hits=[r for r in records if r['key']=='transfers_'+b['address']+'_page'+str(page) and r['http_status']==200]
   if hits:
    v=json.loads((ROOT/hits[-1]['path']).read_text());history+=v['items']
  borrowers.append({'address':b['address'],'chain':b['chain'],'chain_id':b['chain_id'],'beneficial_owner':None,'identity_status':'unverified','sampled_debt_USD_valuation_all_currencies':b['debt_usd'],'sampled_dollar_debt_USD_valuation':stable,'sampled_ETH_debt_USD_valuation':sum(m['debt_usd'] for m in b['markets'] if m['debt'] in ['WETH','ETH']),'discovery_capture_start':b['capture_start'],'discovery_capture_end':b['capture_end'],'financial_snapshot_timestamp':T,'positions':positions,'captured_transfer_count':len(history),'oldest_captured_transfer_date':min((x['timestamp'] for x in history),default=None),'newest_captured_transfer_date':max((x['timestamp'] for x in history),default=None),'confirmed_carry_purpose':False,'whole_book_carry_classification':False,'proceeds':[]})
 receipts=read('borrow_receipts');follow=read('proceeds_receipts');byaddr={b['address']:b for b in borrowers}
 for tx,item in receipts.get('transactions',{}).items():
  receipt=item['receipt_response'].get('result',{});events=[e for l in receipt.get('logs',[]) if (e:=event(l)) and e['event']=='Borrow'];linked=[]
  for f in follow.get('candidate_following_transfers',[]):
   if f['borrow_transaction']!=tx:continue
   r=follow['receipts'].get(f['transfer']['transaction_hash'],{}).get('result',{});ev=[e for l in r.get('logs',[]) if (e:=event(l))];x=f['transfer'];deposit_topic='0x'+keccak(b'Deposit(address,address,uint256,uint256)').hex();deposits=[]
   for log in r.get('logs',[]):
    if log['topics'][0]==deposit_topic and len(log['topics'])==3 and '0x'+log['topics'][2][-40:]==item['borrower']:
     w=words(log['data']);deposits.append({'vault':log['address'],'receiver':item['borrower'],'assets_raw':str(w[0]),'shares_raw':str(w[1]),'evidence':'ERC4626 Deposit and shares minted to the same borrower; transaction also supplies the underlying to Morpho.'})
   linked.append({'timestamp':x['timestamp'],'token':x['token']['symbol'],'units':int(x['total']['value'])/10**int(x['token']['decimals']),'to':x['to']['hash'],'transaction':x['transaction_hash'],'Morpho_events':ev,'yield_vault_deposits_to_borrower':deposits,'exclusive_loan_proceeds_attribution':False})
  if item['borrower'] in byaddr:byaddr[item['borrower']]['proceeds'].append({'borrow_transaction':tx,'timestamp':item['transfer']['timestamp'],'token':item['transfer']['token']['symbol'],'transfer_units':int(item['transfer']['total']['value'])/10**int(item['transfer']['token']['decimals']),'verified_Borrow_events':events,'following_same_token_transfers':linked})
 destinations={}
 for l in read('destinations_T').get('labels',[]):
  if not l['response'].get('success'):continue
  r=l['response']['result'];destinations.setdefault(l['vault'],{'vault':l['vault'],'borrower':l['borrower'],'financial_timestamp':T})[l['signature']]=string(r) if l['signature'] in ['name()','symbol()'] else '0x'+r[-40:] if l['signature']=='asset()' else str(int(r,16))
 for b in borrowers:
  b['confirmed_credit_to_yield_sequences']=sum(bool(f['yield_vault_deposits_to_borrower']) for p in b['proceeds'] for f in p['following_same_token_transfers'])
  b['yield_destination_contracts']=[d for d in destinations.values() if d['borrower']==b['address']]
 simple_fluid=[m for m in markets if m['protocol']=='Fluid' and not m['is_smart_debt'] and m['collateral_scope']=='ETH family only'];nominal=sum(m['debt_units'] or 0 for m in simple_fluid)
 findings=[{'title':'Dollar value is not dollar debt','text':'The $40.585M sampled debt valuation of 0x462a is WETH debt. It must not be labelled ETH/USD carry. Seven unidentified sampled borrowers, not fifteen, have at least $5M of stablecoin debt; their sampled stablecoin-debt valuation totals $85.049M.'},{'title':'Fluid exposes material missing pair-specific routes','text':f'{len(simple_fluid)} simple dollar-debt routes have exclusively ETH-family collateral on Ethereum/Base, totaling {nominal:,.2f} nominal dollar-token units of stored/resolver debt. This is a scoped route measure, not a global carry allocation or a fresh market-price valuation.'},{'title':'Factory registration is not a strategy endorsement','text':'Euler vaults are permissionless. The screen identifies actual accepted ETH collateral and loan terms, but entire vault debt can include other collateral. Beneficial ownership, capital use, trusted frontend inclusion, hooks and account allocation require separate proof.'},{'title':'Public identity evidence remains limited','text':'The top investigated borrowers have no verified strategy-contract ownership. Borrow events prove loan mechanics and recipients. Following transfers can show refinancing or off-address movements, but fungible funds and unidentified destinations prevent an automatic carry classification.'},{'title':'Silo coverage has a precise boundary','text':'The examined current Silo V2 factory generation has no canonical ETH-family/USD pair on Ethereum, Base or Optimism. This does not exclude historical Silo V1 or unqueried Arbitrum markets.'}]
 findings.append({'title':'Two unknown borrowers visibly deploy credit into yield vaults','text':'A122 borrowed 350,000 USDC on 14 and 15 September and deposited similar amounts into RockawayX f(x) Protocol Ecosystem USDC minutes later. 4f87 borrowed 1,000,000 PYUSD on 17 September and deposited 1,000,000 PYUSD into Sentora Huma PST Main. Receipts mint vault shares to the borrowers and show underlying supplied to Morpho. Both direct destination share balances are zero at T. These are historical credit-to-yield sequences; beneficial owners and current whole-book carry allocation remain unknown.'})
 sources=[json.loads(x) for x in (RAW/'requests.jsonl').read_text().splitlines()]
 compound_retry_path=D/'credit_expansion_deep_compound_retry.json'
 compound_archive_repaired=False
 if compound_retry_path.exists():
  retry=json.loads(compound_retry_path.read_text());sources+=retry.get('sources',[]);compound_archive_repaired=retry.get('markets_measured')==3
 summary={'financial_snapshot_timestamp':T,'financial_snapshot_UTC':'2026-10-02T23:59:59Z','blocks':BLOCKS,'protocols_added':['Compound V3','Euler','Fluid','Silo V2'],'market_rows':len(markets),'fixed_T_route_rows':sum(m['status'].startswith('fixed_T') for m in markets),'simple_ETH_only_collateral_Fluid_USD_routes':len(simple_fluid),'simple_ETH_only_collateral_Fluid_nominal_dollar_debt_units':nominal,'unknown_stablecoin_borrowers_at_least_5M_in_original_post_T_sample':7,'unknown_stablecoin_borrowers_sampled_debt_USD_valuation':sum(b['sampled_dollar_debt_USD_valuation'] for b in borrowers if b['sampled_dollar_debt_USD_valuation']>=5e6),'unknown_owners_resolved':0,'verified_Borrow_transactions':sum(bool(p['verified_Borrow_events']) for b in borrowers for p in b['proceeds']),'carry_purpose_confirmed_count':0,'global_ETH_collateral_dollar_debt':None,'coverage_complete':False}
 summary['borrowers_with_observed_credit_to_yield_sequences']=sum(b['confirmed_credit_to_yield_sequences']>0 for b in borrowers);summary['observed_credit_to_yield_sequences']=sum(b['confirmed_credit_to_yield_sequences'] for b in borrowers)
 out={'schema_version':1,'summary':summary,'markets':markets,'borrowers':borrowers,'findings':findings,'coverage':coverage,'sources':sources,'yield_destinations':list(destinations.values()),'limitations':['Arbitrum historical state unavailable from captured public providers.','Euler account-level collateral/debt allocation and other dollar synthetics remain incomplete.','Silo legacy factories and V1 remain outside this expansion.','Borrower history is a bounded transfer sample, not full lifecycle or an ownership census.','Nominal stablecoin units assume a common one-dollar denomination only for the clearly labelled Fluid subtotal. They do not verify token pegs.','Financial snapshot is unchanged; explorer discovery was captured after T and every pre-T flow is selected by block.']}
 if compound_archive_repaired:
  out['limitations'][0]='The three Compound V3 Arbitrum archive failures were repaired through a public Blast endpoint at the same frozen block. Other unmeasured Arbitrum protocol generations remain separate scope.'
  out['findings'].append({'title':'Compound Arbitrum historical coverage repaired','text':'All three official Arbitrum Comet deployments are now read at block 511139919, including accepted collateral, debt, utilisation, rates, caps and oracle values. Earlier missing-trie-node errors were provider limitations, not evidence that the markets were absent.'})
 (D/'credit_expansion.json').write_text(json.dumps(out,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':build()
