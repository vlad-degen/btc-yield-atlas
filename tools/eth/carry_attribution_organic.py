"""Offline source classification of destination receipts and dated benchmarks."""
from __future__ import annotations
import collections, json
from decimal import Decimal
import carry_attribution_collect as c
from carry_attribution_build import read, ordered, addr, proof, date

def build():
 raw=read('carry_attribution_organic_rpc');ledger=read('carry_attribution_ledger');window=ledger['common_window'];start=window['start_block'];groups={r['key']:r for r in raw['log_groups']}
 rows=[];tests=[];unmatched=[]
 for d in c.DESTINATIONS[:2]:
  id=d['id'];inc=ordered(groups[id+'_underlying_in']['logs']);deposits=ordered(groups[id+'_all_deposits']['logs']);hist=ordered(groups[id+'_adapter_history']['logs']);adapters={addr(int(r['topics'][1],16)) for r in hist}
  capital_by_tx=collections.defaultdict(int);incoming_by_tx=collections.defaultdict(int);classified=[]
  for r in deposits:capital_by_tx[r['transactionHash']]+=c.words(r['data'])[0]
  for r in inc:
   sender=addr(int(r['topics'][1],16));amount=int(r['data'],16)
   kind='adapter return' if sender in adapters else 'self transfer' if sender==d['address'] else 'deposit capital' if r['transactionHash'] in capital_by_tx else 'unassigned external receipt'
   if kind=='deposit capital':incoming_by_tx[r['transactionHash']]+=amount
   classified.append({'symbol':d['symbol'],'sender':sender,'kind':kind,'amount_raw':amount,'block':int(r['blockNumber'],16),'transaction_hash':r['transactionHash'],'sourceURL':'https://etherscan.io/tx/'+r['transactionHash']})
  for tx,amount in capital_by_tx.items():
   diff=incoming_by_tx[tx]-amount
   tests.append({'check':id+' deposit '+tx+' equals non-adapter/non-self asset receipts','passed':diff==0})
   if diff:unmatched.append({'destination_id':id,'transaction_hash':tx,'asset_difference':diff/10**d['decimals'],'sourceURL':'https://etherscan.io/tx/'+tx})
  summaries=[]
  for sender,kind in sorted({(r['sender'],r['kind']) for r in classified}):
   chosen=[r for r in classified if r['sender']==sender and r['kind']==kind];inside=[r for r in chosen if r['block']>start]
   summaries.append({'sender':sender,'kind':kind,'lifetime_transfer_count':len(chosen),'lifetime_assets':sum(r['amount_raw'] for r in chosen)/10**d['decimals'],
                    'common_window_transfer_count':len(inside),'common_window_assets':sum(r['amount_raw'] for r in inside)/10**d['decimals']})
  external=[r for r in classified if r['kind']=='unassigned external receipt']
  common=[r for r in external if r['block']>start]
  rows.append({'destination_id':id,'symbol':d['symbol'],'vault':d['address'],'historical_adapters':sorted(adapters),'asset_receipt_senders':summaries,
               'unassigned_external_lifetime_assets':sum(r['amount_raw'] for r in external)/10**d['decimals'],
               'unassigned_external_common_window_assets':sum(r['amount_raw'] for r in common)/10**d['decimals'],
               'unassigned_external_receipts':[dict(r,amount_raw=str(r['amount_raw']),amount=r['amount_raw']/10**d['decimals']) for r in external],
               'gross_organic_lending_interest':None,'scope':'All captured underlying-token receipts are compared with vault deposit events, historical adapter returns and self transfers. No unmatched external receipt is observed during the common window. This does not isolate gross lending interest from fee dilution, rate caps, losses or book recognition.'})
 benchmarks=[]
 for name in ['stETH','weETH','LiquidETH_Ethereum']:
  values={r['period']:int(r['response']['result'],16) for r in raw['benchmarks'] if r['name']==name}
  gain=float(Decimal(values['end'])/Decimal(values['start'])-1)
  benchmarks.append({'name':name,'opening_rate_raw':str(values['start']),'ending_rate_raw':str(values['end']),'opening_ETH_per_share':values['start']/1e18,'ending_ETH_per_share':values['end']/1e18,'window_return':gain,
                     'scope':'Whole Ethereum share or issuer conversion return over the same blocks. It is not causal carry-income attribution and is not a USD return.'})
 events=json.loads((c.DATA/'etherfi_parameter_events.json').read_text());payments=[];fees=[]
 for event in events:
  params={p['name']:p['value'] for p in event['decoded']['parameters']}
  if event['event']=='FeesClaimed' and window['start_timestamp']<event['timestamp']<=c.T:
   asset=params['feeAsset'].lower();payments.append({'asset':asset,'symbol':'weETH' if asset==c.DESTINATIONS[0].get('collateral','0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee') else 'WETH' if asset=='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2' else 'unknown','amount_raw':params['amount'],'amount':int(params['amount'])/1e18,'timestamp':event['timestamp'],'date':date(event['timestamp']),'transaction_hash':event['transaction_hash'],'sourceURL':'https://etherscan.io/tx/'+event['transaction_hash']})
  if event['event']=='ManagementFeeUpdated':fees.append({'timestamp':event['timestamp'],'old_fee_bps':int(params['oldFee']),'new_fee_bps':int(params['newFee']),'transaction_hash':event['transaction_hash']})
 fees.sort(key=lambda r:r['timestamp']);initial=next((r['new_fee_bps'] for r in reversed(fees) if r['timestamp']<=window['start_timestamp']),None);rate=initial;cursor=window['start_timestamp'];weighted=0
 for event in fees:
  if not window['start_timestamp']<event['timestamp']<=c.T:continue
  weighted+=rate*(event['timestamp']-cursor);rate=event['new_fee_bps'];cursor=event['timestamp']
 weighted+=rate*(c.T-cursor)
 output={'schema_version':1,'start_block':start,'end_block':c.BLOCK,'destination_source_review':rows,'deposit_receipt_discrepancies':unmatched,'matched_benchmarks':benchmarks,
         'outer_fees_common_window':{'scope':'Liquid ETH Ethereum Accountant only. Payments are not assigned to a strategy or the period in which the fee was earned.','payments':payments,
                                     'amounts_by_asset':[{'symbol':symbol,'amount':sum(r['amount'] for r in payments if r['symbol']==symbol),'payment_count':sum(r['symbol']==symbol for r in payments)} for symbol in sorted({r['symbol'] for r in payments})],
                                     'initial_management_fee_bps':initial,'ending_management_fee_bps':rate,'calendar_time_weighted_fee_bps':weighted/(c.T-window['start_timestamp']),
                                     'actual_fee_charge_on_carry':None,'already_included_in_Ethereum_net_share_return':True},
         'sources':[proof('data/eth/'+n+'.json') for n in ['carry_attribution_organic_rpc','etherfi_parameter_events']],
         'verification':{'check_count':len(tests),'passed':sum(t['passed'] for t in tests),'failed':sum(not t['passed'] for t in tests),'failures':[t for t in tests if not t['passed']]},
         'boundaries':['A zero count of unexplained token receipts is not proof that all claim growth is pure gross organic interest.','Adapter returns combine principal and accrued lending claims; transfer amounts are not counted as yield.','stcUSD source economics and PRIME transferred-share basis remain unresolved.','The separately observed one-RLUSD receipt predates the common window and the tracked RLUSD V2 position.']}
 if output['verification']['failed']:raise ValueError(json.dumps(output['verification']['failures'][:5]))
 (c.DATA/'carry_attribution_organic.json').write_text(json.dumps(output,indent=2,allow_nan=False))
 print(json.dumps({'source_rows':[{k:r[k] for k in ['destination_id','unassigned_external_lifetime_assets','unassigned_external_common_window_assets']} for r in rows],'benchmarks':benchmarks,'fees':output['outer_fees_common_window'],'verification':output['verification']},indent=2))
if __name__=='__main__':build()
