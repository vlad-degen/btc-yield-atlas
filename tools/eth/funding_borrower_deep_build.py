"""Offline borrower identity and primary-receipt proceeds reconstruction.

Run from the repository root. No network calls, source mutations or inferred
global carry totals. Token quantities are exact decimal strings plus UI floats.
"""
from __future__ import annotations
import json, hashlib, sys, csv
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import keccak
DATA=ROOT/'data/eth'
RAW=ROOT/'raw/eth/funding-borrower-deep-2026-10-04'
T=1790985599; BLOCK=26108081
DS='0xd848f54280f8fe8661b796e3bb8d8922c87af452'
SAFE='0x99926ab8e1b589500ae87977632f13cf7f70f242'
CONCRETE='0x7ee29373f075ee1d83b1b93b4fe94ae242df5178'
ZERO='0x'+'0'*40
TRANSFER='0x'+keccak(b'Transfer(address,address,uint256)').hex()
BORROW='0x'+keccak(b'Borrow(address,address,address,uint256,uint8,uint256,uint16)').hex()
DEBT_MINT='0x'+keccak(b'Mint(address,address,uint256,uint256,uint256)').hex()
TRADE='0x'+keccak(b'Trade(address,address,address,uint256,uint256,uint256,bytes)').hex()
CHECKS=[]

def check(name,ok,detail=None):
 CHECKS.append({'name':name,'passed':bool(ok),'detail':detail})
 if not ok:raise AssertionError(name+': '+str(detail))
def read(name):return json.loads((DATA/(name+'.json')).read_text())
def words(h):return [int(h[2:][i:i+64],16) for i in range(0,len(h)-2,64)] if h and h.startswith('0x') and len(h)>2 else []
def address(w):return '0x'+format(w,'040x')
def topic_address(h):return '0x'+h[-40:].lower()
def exact(raw,decimals):return format(Decimal(raw)/(Decimal(10)**decimals),'f')
def units(raw,decimals):return float(Decimal(raw)/(Decimal(10)**decimals))
def utc(t):return datetime.fromtimestamp(t,timezone.utc).isoformat().replace('+00:00','Z')
def txurl(h):return 'https://etherscan.io/tx/'+h
def addrurl(a):return 'https://etherscan.io/address/'+a
def scalar(state,k):
 w=words(state.get(k,{}).get('result'));return w[0] if len(w)==1 else None
def source(response_sources,key):return next((r for r in response_sources if r['key']==key),None)
def raw_manifest():
 rows=[json.loads(l) for l in (RAW/'requests.jsonl').read_text().splitlines()]
 for r in rows:
  if r.get('path'):
   check('raw SHA256 '+r['path'],hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'])
 return rows
def freeze_input(name):
 paths=list(RAW.glob('input_'+name+'-*.json'));check('one immutable '+name+' input',len(paths)==1)
 p=paths[0];digest=hashlib.sha256(p.read_bytes()).hexdigest();check('immutable input file hash label '+name,digest.startswith(p.stem.rsplit('-',1)[1]))
 return json.loads(p.read_text()),{'path':str(p.relative_to(ROOT)),'sha256':digest}

def build():
 cap=read('funding_borrower_deep_capture');rec=read('funding_borrower_deep_receipts');down=read('funding_borrower_deep_downstream');fin=read('funding_borrower_deep_final_captures');cow=read('funding_borrower_deep_settlements')
 market=json.loads((ROOT/cap['input']['path']).read_text());check('frozen funding atlas hash',hashlib.sha256((ROOT/cap['input']['path']).read_bytes()).hexdigest()==cap['input']['sha256'])
 variants,variant_input=freeze_input('carry_variants_expansion');products,products_input=freeze_input('product_chapters')
 manifest=raw_manifest();check('complete refreshed selected borrower calls',market['summary']['successful_borrower_calls']==15704 and market['summary']['requested_borrower_calls']==15704)
 rows=market['borrowers'];check('all 350 selected account states complete',len(rows)==350 and all(r['complete_queried_T_state'] for r in rows))
 groups=defaultdict(list)
 for r in rows:groups[(r['chain'],r['address'].lower())].append(r)
 ranking=sorted(groups.items(),key=lambda item:sum(r['dollar_debt_USD'] for r in item[1]),reverse=True)
 ids={**cap['identities'],**{a:v for a,v in down['state'].items() if a not in down['owners'].values()}}
 allsources=[*cap['sources'],*rec['sources'],*down['sources'],*fin['sources'],*cow['sources']]
 blockstates={**fin['state']['block'],**cow['state']['block']}
 blocks={int(b,16):r['result'] for b,r in blockstates.items()}
 reserves={(r['venue_id'],r['address'].lower()):r for r in market['reserves']}
 tokens={r['address'].lower():{'symbol':r['symbol'],'decimals':r['configuration']['decimals']} for r in market['reserves'] if r['chain']=='ethereum'}
 tokens['0x6b175474e89094c44da98b954eedeac495271d0f']={'symbol':'DAI','decimals':18}
 tokens['0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2']={'symbol':'WETH','decimals':18}
 def transfers(receipt):
  out=[]
  for l in sorted(receipt['logs'],key=lambda a:int(a['logIndex'],16)):
   if len(l['topics'])==3 and l['topics'][0]==TRANSFER and l['address'].lower() in tokens:
    token=l['address'].lower();raw=int(l['data'],16);tm=tokens[token]
    if raw:out.append({'token':token,'asset':tm['symbol'],'from':topic_address(l['topics'][1]),'to':topic_address(l['topics'][2]),'raw_amount':str(raw),'amount':units(raw,tm['decimals']),'amount_exact':exact(raw,tm['decimals']),'log_index':int(l['logIndex'],16)})
  return out
 def contract_identity(a):
  state=ids[a];code=state['code_T'].get('result');check('code measured at T '+a,code is not None)
  meta=next((r['response'] for r in allsources if r['key'] in ['address_'+a,'extra_address_'+a]),{})
  own=scalar(state,'owner()');ow=words(state.get('getOwners()',{}).get('result'));signers=[address(v) for v in ow[2:]] if ow and ow[0]==32 else []
  threshold=scalar(state,'getThreshold()');master=scalar(state,'masterCopy()')
  typename='No deployed code at T' if code=='0x' else 'DSProxy' if own else 'Safe proxy' if signers else 'Contract, authorization unresolved'
  implementation=None
  if a=='0x3a0dc3fc4b84e2427ced214c9ce858ea218e97d9':
   implementation='0xfe02a32cbe0cb9ad9a945576a5bb53a3c123a3a3';check('InstaAccount implementation encoded in T clone',implementation[2:] in code.lower());typename='InstaAccountV2 clone, authorization unresolved'
  matches=[]
  if a==CONCRETE:
   q=next(r for r in variants['products'] if r['id']=='concrete-wsteth');check('exact Concrete execution Safe match',q['terms']['control']['execution_multisig'].lower()==a)
   matches=[{'product_id':'concrete-wsteth','product_name':'Concrete wstETHPlus and shared Concrete execution account','match_type':'exact getMultiSig address at T','status':'shared execution account, attribution unresolved','source_input':variant_input['path'],'sourceURL':addrurl(q['address']),'boundary':'This account is shared. Its full dollar debt cannot be assigned to either product or added to product NAV.'}]
  proceeds='Untraced; ETH collateral and dollar debt do not establish carry use.'
  if a==DS:proceeds='Sampled owner transfer and Maker debt repayment sequence; external conversion and whole-account use unresolved.'
  if a==SAFE:proceeds='Sampled USDC-to-USDT CoW conversion and later external-wallet payment; no yield destination proved.'
  if a==CONCRETE:proceeds='Shared execution account, product attribution unresolved.'
  verified=source(allsources,'source_'+a)
  current_bytecode=verified['response'].get('deployed_bytecode') if verified else None
  return {'address':a,'chain':'ethereum','code_at_T':{'status':'measured','block':BLOCK,'bytes':(len(code)-2)//2,'sha256':hashlib.sha256(bytes.fromhex(code[2:])).hexdigest(),'is_empty':code=='0x','code':code},'contract_type':typename,'owner_or_signers_at_T':{'owner':address(own) if own else None,'signers':signers,'threshold':threshold,'master_copy':address(master) if master else None,'implementation_from_clone_code':implementation,'boundary':'On-chain control addresses and signature threshold, not identified legal entities. Safe modules and other authorization paths were not enumerated. Generic ownership selectors reverting on an InstaAccount do not prove absence of authorized users.'},'exact_product_matches':matches,'public_labels_discovery':{'date':'2026-10-04','contract_name':meta.get('name'),'public_tags':meta.get('public_tags',[]),'ens_name':meta.get('ens_domain_name'),'verified_source_bytecode_equals_T':current_bytecode.lower()==code.lower() if current_bytecode else None,'boundary':'Explorer discovery labels are dated separately. Technical contract identity does not identify a manager or establish investment use.'},'proceeds_status':proceeds,'sourceURLs':[addrurl(a),'https://eth.blockscout.com/api/v2/addresses/'+a]}
 identities={a:contract_identity(a) for (chain,a),v in ranking[:10]}
 for a,expected in [('0xfe02a32cbe0cb9ad9a945576a5bb53a3c123a3a3','InstaAccountV2'),('0x63c0c19a282a1b52b07dd5a65b58948a07dae32b','EIP7702StatelessDeleGator')]:
  q=source(fin['sources'],'final_smart-contracts_'+a)['response'];check('verified implementation source and T code '+a,q['name']==expected and q['deployed_bytecode'].lower()==fin['state']['code'][a]['result'].lower())
 def venue_view(r):
  return {'venue_id':r['venue_id'],'venue':r['venue'],'chain':r['chain'],'block':r['block'],'selected_ETH_collateral_USD':r['ETH_collateral_USD'],'selected_dollar_debt_USD':r['dollar_debt_USD'],'ETH_collateral':r['ETH_collateral'],'dollar_debt':r['dollar_debt'],'account':r['account'],'complete_selected_state':r['complete_queried_T_state'],'sourceURL':next(q['source_url'] for q in market['reserves'] if q['venue_id']==r['venue_id']),'boundary':'Selected dollar liabilities can coexist with other collateral and other debt. Account-level health factor and thresholds belong to this pool only.'}
 def borrower_row(group,rank):
  a=group[0]['address'].lower();out=dict(identities[a]);out.update({'rank':rank,'venue_debt_rows':[venue_view(r) for r in group],'measured_dollar_debt_USD':sum(r['dollar_debt_USD'] for r in group),'account_collateral_boundary':'Distinct pool liabilities are summed for ranking. Collateral, lending limits and health factors remain separate by venue. Selected dollar debt is not attributed proportionally to ETH and is not measured carry capital.'});return out
 topunique=[borrower_row(v,i+1) for i,((chain,a),v) in enumerate(ranking[:10])]
 topvenue=[borrower_row([r],i+1) for i,r in enumerate(rows[:10])]
 loans=[]
 for sample in rec['samples']:
  h=sample['indexed_mint']['transaction_hash'];tx=rec['transactions'][h];receipt=tx['eth_getTransactionReceipt']['result'];block=int(receipt['blockNumber'],16);a=sample['address'];owner=down['owners'][a];asset=sample['loan_asset'].lower();reserve=reserves[(sample['venue'],asset)];dec=reserve['configuration']['decimals'];cash=transfers(receipt)
  events=[l for l in receipt['logs'] if l['address'].lower()==reserve['pool'] and l['topics'][0]==BORROW and topic_address(l['topics'][1])==asset and topic_address(l['topics'][2])==a];check('one actual Borrow event '+h,len(events)==1)
  event=events[0];w=words(event['data']);principal=w[1];incoming=[r for r in cash if r['token']==asset and r['from']==reserve['a_token'] and r['to']==a and int(r['raw_amount'])==principal];outgoing=[r for r in cash if r['token']==asset and r['from']==a and r['to']==owner and int(r['raw_amount'])==principal];check('full direct cash link '+h,len(incoming)==1 and len(outgoing)==1 and incoming[0]['log_index']<outgoing[0]['log_index'])
  check('successful pre-T receipt '+h,receipt['status']=='0x1' and block<=BLOCK and int(blocks[block]['timestamp'],16)<=T)
  debt_token=reserve['variable_debt_token'];mint=[l for l in receipt['logs'] if l['address'].lower()==debt_token and l['topics'][0]==TRANSFER and len(l['topics'])==3 and topic_address(l['topics'][1])==ZERO and topic_address(l['topics'][2])==a];check('one debt mint receipt '+h,len(mint)==1);mint_raw=int(mint[0]['data'],16);check('debt mint not smaller than cash '+h,mint_raw>=principal)
  debt_events=[l for l in receipt['logs'] if l['address'].lower()==debt_token and l['topics'][0]==DEBT_MINT and topic_address(l['topics'][2])==a];check('one explicit accrued balance Mint event '+h,len(debt_events)==1);mint_words=words(debt_events[0]['data']);interest_raw=mint_words[1];rounding_raw=mint_raw-principal-interest_raw;check('Mint balance increase explains excess within one base unit '+h,mint_words[0]==mint_raw and abs(rounding_raw)<=1)
  loans.append({'account':a,'owner_address_at_T':owner,'venue_id':sample['venue'],'loan_asset':sample['loan_symbol'],'loan_token':asset,'block':block,'timestamp':int(blocks[block]['timestamp'],16),'date':utc(int(blocks[block]['timestamp'],16)),'transaction_hash':h,'cash_principal_raw':str(principal),'cash_principal':units(principal,dec),'cash_principal_exact':exact(principal,dec),'debt_token_mint_raw':str(mint_raw),'debt_token_mint':units(mint_raw,dec),'debt_mint_minus_new_cash':units(mint_raw-principal,dec),'Mint_event_accrued_balance_increase_raw':str(interest_raw),'Mint_event_accrued_balance_increase':units(interest_raw,dec),'Mint_event_accrued_balance_increase_exact':exact(interest_raw,dec),'mint_minus_cash_minus_accrued_interest_raw_rounding':rounding_raw,'debt_mint_boundary':'Debt mint includes accrued pre-existing interest and possible one-base-unit rounding. Borrow event and underlying cash transfer measure new loan principal. The difference is not investment income.','borrow_event_APR':w[3]/1e27,'borrow_event_log_index':int(event['logIndex'],16),'cash_transfers':[incoming[0],outgoing[0]],'first_hop_cash_verified':True,'loan_transaction_from':tx['eth_getTransactionByHash']['result']['from'].lower(),'sourceURL':txurl(h)})
 loans.sort(key=lambda r:r['timestamp'])
 downstream=[]
 for h,tx in down['transactions'].items():
  receipt=tx['eth_getTransactionReceipt']['result'];block=int(receipt['blockNumber'],16);check('successful downstream pre-T '+h,receipt['status']=='0x1' and block<=BLOCK)
  downstream.append({'transaction_hash':h,'block':block,'timestamp':int(blocks[block]['timestamp'],16),'date':utc(int(blocks[block]['timestamp'],16)),'transaction_from':tx['eth_getTransactionByHash']['result']['from'].lower(),'transaction_to':tx['eth_getTransactionByHash']['result']['to'].lower(),'transfers':transfers(receipt),'sourceURL':txurl(h)})
 trades=[]
 for h,tx in cow['transactions'].items():
  receipt=tx['eth_getTransactionReceipt']['result'];block=int(receipt['blockNumber'],16);cash=transfers(receipt);selected=[l for l in receipt['logs'] if l['address'].lower()==cow['settlement'] and l['topics'][0]==TRADE and topic_address(l['topics'][1])==cow['owner']];check('one actual owner CoW trade '+h,len(selected)==1)
  l=selected[0];w=words(l['data']);sell=address(w[0]);buy=address(w[1]);sr=w[2];br=w[3];fee=w[4];selling=[r for r in cash if r['token']==sell and r['from']==cow['owner'] and r['to']==cow['settlement'] and int(r['raw_amount'])==sr];buying=[r for r in cash if r['token']==buy and r['from']==cow['settlement'] and r['to']==cow['owner'] and int(r['raw_amount'])==br];check('CoW actual settlement cash '+h,len(selling)==1 and len(buying)==1)
  check('successful CoW pre-T '+h,receipt['status']=='0x1' and block<=BLOCK)
  trades.append({'transaction_hash':h,'block':block,'date':utc(int(blocks[block]['timestamp'],16)),'owner':cow['owner'],'sell_asset':tokens[sell]['symbol'],'buy_asset':tokens[buy]['symbol'],'sell_token':sell,'buy_token':buy,'sell_raw':str(sr),'buy_raw':str(br),'sell_amount':units(sr,tokens[sell]['decimals']),'sell_amount_exact':exact(sr,tokens[sell]['decimals']),'buy_amount':units(br,tokens[buy]['decimals']),'buy_amount_exact':exact(br,tokens[buy]['decimals']),'Trade_event_fee_amount':units(fee,tokens[sell]['decimals']),'trade_log_index':int(l['logIndex'],16),'actual_transfers':[selling[0],buying[0]],'sourceURL':txurl(h)})
 trades.sort(key=lambda r:(r['block'],r['trade_log_index']))
 check('19 verified USDC to USDT settlements',len(trades)==19 and all(r['sell_asset']=='USDC' and r['buy_asset']=='USDT' for r in trades))
 safeopening=scalar(down['state'][cow['owner']],'balance:USDC:26058231');selltotal=sum(int(r['sell_raw']) for r in trades);buytotal=sum(int(r['buy_raw']) for r in trades);loan=next(r for r in loans if r['account']==SAFE and r['loan_asset']=='USDC');check('CoW sales equal loan plus exact opening USDC',selltotal==int(loan['cash_principal_raw'])+safeopening)
 check('post-loan owner USDC equals loan plus opening',int(cow['state']['balance']['USDC:26058232']['result'],16)==selltotal)
 check('CoW source bytecode equals T',source(cow['sources'],'cow_smart-contracts_')['response']['deployed_bytecode'].lower()==cow['state']['code'][cow['settlement']]['result'].lower())
 ds_receipt=next(r for r in downstream if r['transaction_hash']=='0x897ec0dae37a3bf12da50e036356c9f92ac5e9cbf666c0dd1fd13ac75ec349c5');dsowner=down['owners'][DS];pull=[r for r in ds_receipt['transfers'] if r['asset']=='DAI' and r['from']==dsowner and r['to']==DS];burn=[r for r in ds_receipt['transfers'] if r['asset']=='DAI' and r['from']==DS and r['to']==ZERO];check('Maker exact cash pull and burn',len(pull)==len(burn)==1 and pull[0]['raw_amount']==burn[0]['raw_amount'] and pull[0]['log_index']<burn[0]['log_index'])
 action_address='0xe68aed979af6f85516ff485d098804c0f9ed9a5b';action=source(fin['sources'],'final_smart-contracts_'+action_address);check('McdPayback action identity and exact T code',action['response']['name']=='McdPayback' and action['response']['deployed_bytecode'].lower()==fin['state']['code'][action_address]['result'].lower())
 payback=down['transactions'][ds_receipt['transaction_hash']];payback_input=payback['eth_getTransactionByHash']['result']['input'];check('payback receipt executes verified action',payback_input.startswith('0x1cff79cd') and address(words('0x'+payback_input[10:])[0])==action_address)
 manager_notes=[l for l in payback['eth_getTransactionReceipt']['result']['logs'] if l['address'].lower()=='0x5ef30b9986345249bc32d8928b7ee64de9435e39' and l['topics'][0].startswith('0x45e6bdcd')];check('one Maker manager frob event',len(manager_notes)==1);maker_note=manager_notes[0];maker_id=int(maker_note['topics'][2],16);data_bytes=bytes.fromhex(maker_note['data'][2:]);offset=int.from_bytes(data_bytes[:32]);length=int.from_bytes(data_bytes[offset:offset+32]);calldata=data_bytes[offset+32:offset+32+length];args=words('0x'+calldata[4:].hex());dart=args[2]-(1<<256) if args[2]>>255 else args[2];check('Maker frob reduces normalized debt',calldata[:4].hex()=='45e6bdcd' and args[0]==maker_id and dart<0)
 vat_notes=[l for l in payback['eth_getTransactionReceipt']['result']['logs'] if l['address'].lower()=='0x35d1b3f3d7966a1dfe207aa4514c12a259a0492b' and l['topics'][0].startswith('0x76088703')];check('one Maker Vat collateral type',len(vat_notes)==1);maker_ilk=bytes.fromhex(vat_notes[0]['topics'][1][2:]).rstrip(b'\0').decode()
 dai_receipt=next(r for r in downstream if r['transaction_hash']=='0x0126e61bdc9052e2e8d4beca9a32441514de1db9c08e1a4d50f3deb82a5fca70');daiin=next(r for r in dai_receipt['transfers'] if r['asset']=='DAI' and r['to']==dsowner)
 balances=[]
 for b in down['balance_labels']:
  raw=scalar(down['state'][b['owner']],'balance:'+b['symbol']+':'+str(b['block']));check('historical cash balance '+str(b),raw is not None);balances.append({**b,'raw_balance':str(raw),'balance':units(raw,b['decimals']),'balance_exact':exact(raw,b['decimals'])})
 recipients=[]
 for r in down['sources']:
  if r['key'].startswith('recipient_'):
   a=r['key'][len('recipient_'):];q=r['response'];recipients.append({'address':a,'public_label':q.get('name'),'public_tags':q.get('public_tags',[]),'is_contract_at_discovery':q.get('is_contract'),'discovery_date':'2026-10-04','identity_status':'Unidentified legal entity','sourceURL':r['url'],'boundary':'An unlabelled recipient is not assumed to be an exchange, manager or yield vault.'})
 traceds=[]
 for a in [DS,SAFE]:
  selected=[r for r in loans if r['account']==a];principal=defaultdict(Decimal)
  for r in selected:principal[r['loan_asset']]+=Decimal(r['cash_principal_exact'])
  relevant_downstream=[r for r in downstream if r['transaction_from'] in [a,down['owners'][a]] or any(t['to']==down['owners'][a] for t in r['transfers'])];actual_counterparties={v for r in relevant_downstream for t in r['transfers'] for v in [t['from'],t['to']]}
  item={'address':a,'measured_dollar_debt_USD':next(r['measured_dollar_debt_USD'] for r in topunique if r['address']==a),'owner_at_T':down['owners'][a],'representative_loans':selected,'sampled_new_loan_principal_by_currency':{k:float(v) for k,v in principal.items()},'same_transaction_owner_transfer_by_currency':{k:float(v) for k,v in principal.items()},'first_hop_cash_link_coverage':f'All {len(selected)} sampled loans for this account transfer the complete new principal to its T owner address. This is sample coverage, not coverage of outstanding debt or lifetime borrowing.','whole_account_carry_use_verified':False,'carry_investment_capital_USD':None,'profit_or_yield_attributed':None,'owner_cash_balances': [r for r in balances if r['owner']==down['owners'][a]],'recipients':[r for r in recipients if r['address'] in actual_counterparties],'downstream_receipts':relevant_downstream,'scope':'Representative pre-T loan samples discovered from one current indexed debt-mint page. Primary receipts verify cash, not an exhaustive borrowing history.'}
  if a==DS:
   ds_out=defaultdict(Decimal);ds_principal=defaultdict(Decimal)
   for r in relevant_downstream:
    for t in r['transfers']:
     if t['from']==dsowner and t['to']==daiin['from']:ds_out[t['asset']]+=Decimal(t['amount_exact'])
   for r in selected:
    if r['date'].startswith('2026-09-30'):ds_principal[r['loan_asset']]+=Decimal(r['cash_principal_exact'])
   item.update({'use_classification':'Sampled external-wallet transfer followed by Maker debt repayment','moneyFlow':'Aave USDT and Spark USDS/USDC -> DSProxy -> owner -> unidentified external wallet. The external wallet later pays DAI to the owner, which pulls DAI into the DSProxy and repays a Maker ETH-C vault.','refinancing_sequence':{'date':'2026-09-30','owner_to_external_by_currency':{k:float(v) for k,v in ds_out.items()},'owner_to_external_by_currency_exact':{k:format(v,'f') for k,v in ds_out.items()},'same_currency_sampled_new_principal_by_currency':{k:float(v) for k,v in ds_principal.items()},'external_recipient':daiin['from'],'DAI_received':daiin['amount'],'DAI_received_exact':daiin['amount_exact'],'DAI_repaid_to_Maker':pull[0]['amount'],'DAI_repaid_exact':pull[0]['amount_exact'],'Maker_vault_id':maker_id,'Maker_ilk':maker_ilk,'Maker_normalized_debt_decrease_raw':str(-dart),'payback_action':action_address,'DAI_in_sourceURL':dai_receipt['sourceURL'],'payback_sourceURL':ds_receipt['sourceURL'],'interpretation':'Receipts show the payment sequence and an actual debt repayment. They do not reveal the external wallet agreement, exchange rate, prior balances, or whether all dollars funded the DAI payment. This is a bounded refinancing sequence, not a closed carry-income ledger.'},'unresolved':['Legal identity of owner and external recipient.','The external conversion or settlement agreement and its full cash history.','Use of the 24 September 4,000,000 USDC sample beyond its direct owner hop.','Investment use and income attribution for the remaining outstanding account debt.']})
  else:
   openingUSDT=scalar(down['state'][cow['owner']],'balance:USDT:26058231')
   item.update({'use_classification':'Verified USDC-to-USDT conversion, then external-wallet transfer','moneyFlow':'Aave USDC -> Safe -> owner -> 19 CoW USDC/USDT settlements -> owner -> unidentified external wallet.','dollar_conversion':{'date':'2026-09-26','cash_loan_USDC':loan['cash_principal'],'opening_owner_USDC':units(safeopening,6),'opening_owner_USDC_exact':exact(safeopening,6),'post_loan_owner_USDC':units(selltotal,6),'CoW_settlement_count':len(trades),'USDC_sold':units(selltotal,6),'USDC_sold_exact':exact(selltotal,6),'USDT_received':units(buytotal,6),'USDT_received_exact':exact(buytotal,6),'opening_owner_USDT':units(openingUSDT,6),'later_USDT_test_payment':100,'later_USDT_main_payment':10014900,'external_recipient':'0x2a28632f061a7558252441564d6bc1ec0c29bfe5','external_payment_sourceURLs':[txurl('0x46a9e43de5d17f3fd348a308e3f3e1d8c32ce7a776ec4ac36d22ab2680e4ddad'),txurl('0xaaa77e9f37ab49e1fc91000bf29df0e164f7ed8392477a54086d7b489fdbbeef')],'nominal_buy_minus_sell_token_units':units(buytotal-selltotal,6),'nominal_difference_boundary':'Different dollar-token units are compared only as nominal quantities. This is not USD profit, interest income, an annual return or a complete conversion cost. Trade feeAmount fields are zero but may not capture price-embedded fees, gas or execution costs.','funding_link':'The 19 USDC sales exactly equal new loan cash plus the independently measured USDC opening balance. Actual CoW Trade events and underlying transfers return USDT to the same owner. Later USDT transfers combine these proceeds with existing USDT. No allocation of each final payment to loan versus pre-existing USDT is claimed.','settlements':trades},'unresolved':['Legal identity of Safe signer and final external recipient.','Purpose of the final external-wallet payment, including any off-chain activity.','Use of the 10 and 11 September sampled USDS loans beyond the direct owner hop.','Any basis position, yield investment, ETH purchase or return for the remaining outstanding account debt.']})
  traceds.append(item)
 scope={'population':'Current/post-T holder discovery followed by complete selected token views at T for 350 material venue-account rows. Holder discovery is bounded and can miss accounts that exited after T.','ranking':'Top venue accounts and top unique chain-addresses are separate rankings. Unique ranking sums distinct pool liabilities, with no pooled collateral or health factor.','dollar_valuation':'Loan-token units are valued with each lending venue asset oracle at T. Stablecoins are not forced to exactly one USD.','selected_debt_boundary':'Measured dollar debt backed partly or wholly by enabled ETH-family collateral. Other collateral and debt may coexist. No ETH-only attribution or global carry-capital total is produced.','identity':'Technical contract types and on-chain control addresses. No named legal entity is inferred from a contract name, signer, transfer recipient or transaction pattern.','proceeds':'Seven representative cash loans, eight downstream receipts and 19 CoW settlements. Sampled use does not classify full account debt.','history_limit':'Broad eth_getLogs requests failed because this public endpoint permits a maximum ten-block range. These errors are preserved and are not interpreted as zero borrowing. Loan discovery uses a current indexed debt-mint page; pre-T primary receipts verify actual events.','token_filter':'Canonical token addresses and positive receipt cash transfers are required. Same-symbol fake tokens, zero transferFrom records and dust incoming transfers are not owner investment transactions.','control_limit':'Safe modules, guards and full historical authorization changes were not enumerated. The one Safe owner has EIP-7702 delegation code at T, so it is not described as a plain no-code wallet.','income':'No yield or closed whole-account profit is measured for either unidentified account. Global carry amount and borrower-universe coverage percentage remain null.'}
 findings=[{'id':'rank','title':'Pool accounts and unique borrowers are different rankings','text':f'The two largest unique chain-addresses owe ${topunique[0]["measured_dollar_debt_USD"]/1e6:.3f}M and ${topunique[1]["measured_dollar_debt_USD"]/1e6:.3f}M across Aave and Spark. Their collateral and health factors remain separate by venue.','sources':[addrurl(DS),addrurl(SAFE)]},{'id':'refinancing','title':'Borrowing can replace existing debt','text':f'The DSProxy sends 3,000,000 USDT, 5,000,000 USDS and 1,000,000 USDC of sampled new principal to its owner on 30 September. The subsequent sequence includes {pull[0]["amount"]:,.6f} DAI repaid to Maker. It establishes a sampled refinancing route, with the external settlement agreement unresolved.','sources':[dai_receipt['sourceURL'],ds_receipt['sourceURL']]},{'id':'conversion','title':'The largest Safe sample converts dollars rather than buying ETH','text':f'The Safe borrows 6,862,300 USDC. Its owner sells that principal plus 12.398204 USDC of opening cash in 19 CoW trades and receives {units(buytotal,6):,.6f} USDT. A later payment goes to an unidentified external wallet. No investment yield is established.','sources':[loan['sourceURL'],trades[0]['sourceURL'],trades[-1]['sourceURL']]},{'id':'shared','title':'A known manager match still needs a product allocation','text':'The 0x7ee execution Safe is an exact Concrete match and owes $105.736M in the selected Aave dollar view. It is shared with another Concrete product. The debt cannot be counted as new product capital or assigned entirely to one share book.','sources':[addrurl(CONCRETE)]},{'id':'mint','title':'A debt-token mint is not all newly borrowed cash','text':'One DSProxy transaction mints 3,223,198.640147 variable-debt USDT but transfers only 3,000,000 USDT of new cash. Accrued interest on pre-existing debt explains why mint amount is an unsafe cash-principal proxy.','sources':[txurl('0x9e563c3d6155b1cf734f08ec3dff4462a8f60b2b4ca2bde8895e5ef4129c8ecf')]}]
 delegation=down['state'][cow['owner']]['code_T']['result'];check('Safe owner EIP7702 delegation at T',delegation.startswith('0xef0100'));identity_findings={'named_legal_entities_verified':0,'exact_shared_execution_account_matches':1,'top10_unique_control_types':dict(__import__('collections').Counter(r['contract_type'] for r in topunique)),'Safe_sample_owner_code_at_T':{'address':cow['owner'],'code':delegation,'delegation_target':'0x'+delegation[8:],'verified_discovery_name':'EIP7702StatelessDeleGator','boundary':'Delegated owner account, not a plain no-code wallet or identified legal entity.'},'explorer_discovery_date':'2026-10-04'}
 out={'schema_version':1,'snapshot':{'timestamp':T,'date':utc(T),'chain':'ethereum','block':BLOCK,'discovery_date':'2026-10-04'},'input':{'funding_atlas':cap['input'],'carry_variants':variant_input,'product_chapters_for_exact_match_context':products_input},'top10_venue_accounts':topvenue,'top10_unique_addresses':topunique,'identity_findings':identity_findings,'traced_accounts':traceds,'findings':findings,'scope':scope,'raw_manifest':{'path':str((RAW/'requests.jsonl').relative_to(ROOT)),'capture_count':len(manifest),'source_records':[{k:r.get(k) for k in ['key','url','retrieved_at','target_timestamp','status','path','sha256']} for r in manifest]},'verification':{'checks':CHECKS,'passed':len(CHECKS),'failed':sum(not r['passed'] for r in CHECKS),'network_required':False,'command':'python3 tools/eth/funding_borrower_deep_build.py','sampled_cash_loans':len(loans),'same_transaction_full_owner_transfers':sum(r['first_hop_cash_verified'] for r in loans),'downstream_receipts':len(downstream),'CoW_settlements':len(trades),'closed_carry_income_ledgers':0},'global_carry_capital_USD':None,'borrower_universe_coverage_percent':None}
 (DATA/'funding_borrower_deep_chapter.json').write_text(json.dumps(out,indent=2)+'\n')
 with (DATA/'funding_borrower_deep_rankings.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['ranking','rank','chain','address','measured_dollar_debt_USD','venues','contract_type','control_threshold','control_signers','proceeds_status'])
  for name,array in [('unique_chain_address',topunique),('venue_account',topvenue)]:
   for r in array:w.writerow([name,r['rank'],r['chain'],r['address'],r['measured_dollar_debt_USD'],';'.join(v['venue_id'] for v in r['venue_debt_rows']),r['contract_type'],r['owner_or_signers_at_T']['threshold'],';'.join(r['owner_or_signers_at_T']['signers']),r['proceeds_status']])
 print(f'{len(CHECKS)} checks passed; seven full first-hop loan links; 19 exact CoW settlements; zero claimed carry-income ledgers.')
 return out
if __name__=='__main__':build()
