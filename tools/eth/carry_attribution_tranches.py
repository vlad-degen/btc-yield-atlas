"""Exact debt-share cohorts and retained destination-share claims at T."""
from __future__ import annotations
import csv,json
import carry_attribution_collect as c
from carry_attribution_build import read, ordered, addr, proof
from carry_economics_build import accrue, borrow_assets

def build():
 ledger=read('carry_attribution_ledger');states=read('carry_attribution_states');rpc=read('carry_attribution_rpc');claims=read('carry_attribution_tranche_rpc');tests=[];rows=[]
 def lookup(mid,field):return c.words(next(r['response']['result'] for r in states['records'] if r['kind']=='market' and r['id']==mid and r['field']==field))
 groups={r['key']:r for r in rpc['log_groups']}
 for loan in ledger['borrowing_ledgers']:
  if loan['repay_count']:continue
  events=[r for r in ledger['borrowing_events'] if r['ledger_id']==loan['id'] and r['event']=='borrow'];m=lookup(loan['market_id'],'market');rate=lookup(loan['market_id'],'borrow_rate')[0];projected=m[2]+accrue(m,rate,c.T)
  debt_raw_total=0
  for event in events:
   shares=int(event['shares_raw']);debt=borrow_assets(shares,projected,m[3]);debt_raw_total+=debt;principal=int(event['assets_raw']);cost=debt-principal
   destinations=[r for r in ledger['destination_events'] if r['event']=='deposit' and r['transaction_hash']==event['transaction_hash']]
   deposits=[]
   for d in destinations:
    if d['asset']==event['asset']:
     financing=next((r for r in ledger['funding_links'] if r['destination_event']=='deposit' and r['transaction_hash']==d['transaction_hash'] and r['destination_event_log_index']==d['log_index']),None)
     if not financing or not financing['direct_morpho_to_controlled_to_destination_transfers']:continue
    claim=next((r for r in claims['records'] if r['field']=='deposit_cohort_convertToAssets_T' and r['transaction_hash']==d['transaction_hash'] and r['destination_id']==d['destination_id'] and r['deposit_shares_raw']==d['shares_raw']),None)
    later=[r for r in ordered(groups[d['destination_id']+'_share_out']['logs']) if addr(int(r['topics'][1],16))==d['account'] and (int(r['blockNumber'],16),int(r['logIndex'],16))>(d['block'],d['log_index'])]
    no_later_outgoing=not later
    if claim:tests.append({'check':'retained '+d['destination_id']+' '+d['transaction_hash']+' has no later outgoing shares','passed':no_later_outgoing})
    dec=next(r['decimals'] for r in ledger['destination_ledgers'] if r['id']==d['destination_id'])
    ending=c.words(claim['response']['result'])[0] if claim and no_later_outgoing else None
    deposits.append({'destination_id':d['destination_id'],'asset':d['asset'],'symbol':d['symbol'],'deposit_cash_assets':d['assets'],'deposit_shares_raw':d['shares_raw'],'ending_claim_assets':ending/10**dec if ending is not None else None,
                     'net_accrued_claim_growth_assets':(ending-int(d['assets_raw']))/10**dec if ending is not None else None,
                     'no_later_outgoing_shares':no_later_outgoing,'same_native_asset_as_loan':d['asset']==event['asset'],
                     'additional_deposit_cash_beyond_loan_assets':d['assets']-event['assets'] if d['asset']==event['asset'] else None,
                     'sourceURL':d['sourceURL']})
   same=[d for d in deposits if d['same_native_asset_as_loan'] and d['ending_claim_assets'] is not None]
   component=sum(d['net_accrued_claim_growth_assets'] for d in same)-cost/10**loan['decimals'] if len(same)==1 else None
   rows.append({'loan_ledger_id':loan['id'],'market_id':loan['market_id'],'loan_asset':loan['loan_asset'],'loan_symbol':loan['symbol'],'account':loan['account'],'transaction_hash':event['transaction_hash'],'origination_date':event['date'],'origination_block':event['block'],
                'borrowed_cash_assets':event['assets'],'borrowed_cash_raw':event['assets_raw'],'borrowed_shares_raw':event['shares_raw'],'ending_debt_claim_assets':debt/10**loan['decimals'],'ending_debt_claim_raw':str(debt),
                'accrued_borrowing_interest_assets':cost/10**loan['decimals'],'accrued_borrowing_interest_raw':str(cost),'repaid_cash_assets':0,'destination_deposits':deposits,
                'lending_minus_borrowing_component_assets':component,'component_label':'Retained destination claim growth less accrued financing cost, before rewards, outer fees and own-credit allocation',
                'complete_strategy_profit':None,'sourceURL':event['sourceURL']})
  position=c.words(next(r['response']['result'] for r in states['records'] if r['kind']=='market' and r['id']==loan['market_id'] and r['field']=='position' and r['account']==loan['account']))
  account_debt=borrow_assets(position[1],projected,m[3])
  tests.append({'check':loan['id']+' debt cohorts reconcile within per-cohort ceiling rounding','passed':0<=debt_raw_total-account_debt<=len(events)-1,'raw_rounding_difference':str(debt_raw_total-account_debt)})
  tests.append({'check':loan['id']+' event share sum equals actual T debt shares','passed':sum(int(r['shares_raw']) for r in events)==int(loan['ending_borrow_shares_raw'])})
 paired=[r for r in rows if r['lending_minus_borrowing_component_assets'] is not None]
 summary=None
 if paired:
  tests.append({'check':'same-unit retained pairs all share PYUSD/PRIME market','passed':all(r['loan_symbol']=='PYUSD' and r['market_id']=='0x41c41d0c9aadbf4751f5ee215ed5a16954a4b34e1b70fca5393d4b08858fa3fa' for r in paired)})
  claim_gain=sum(d['net_accrued_claim_growth_assets'] for r in paired for d in r['destination_deposits'] if d['same_native_asset_as_loan'])
  cost=sum(r['accrued_borrowing_interest_assets'] for r in paired)
  summary={'id':'prime_pyusd_retained_pairs','symbol':'PYUSD','matched_transaction_count':len(paired),'loan_cash_assets':sum(r['borrowed_cash_assets'] for r in paired),
           'destination_deposits_assets':sum(d['deposit_cash_assets'] for r in paired for d in r['destination_deposits'] if d['same_native_asset_as_loan']),
           'additional_deposit_cash_assets':sum(d['additional_deposit_cash_beyond_loan_assets'] for r in paired for d in r['destination_deposits'] if d['same_native_asset_as_loan']),
           'net_accrued_destination_claim_growth_assets':claim_gain,'accrued_borrowing_interest_assets':cost,
           'lending_minus_borrowing_component_assets':claim_gain-cost,
           'origination_date':paired[0]['origination_date'],'window_seconds':c.T-next(e['timestamp'] for e in ledger['borrowing_events'] if e['transaction_hash']==paired[0]['transaction_hash']),
           'destination_cash_income_withdrawn_assets':0,'borrowing_interest_paid_cash_assets':0,
           'reward_cash_allocated':None,'outer_fee_allocation':None,'net_own_credit_interest_allocation':None,'complete_strategy_profit':None,
           'scope':'The final 3 million PYUSD borrow/deposit pair is retained for only 108 seconds to T. A deposit earlier in the same transaction occurred before the loan and is excluded. This is an exact-state diagnostic before rewards, outer fees and own-credit allocation, too short to establish strategy economics. The older 18 million PYUSD loan has later destination withdrawals, so its remaining destination basis is not uniquely assigned.'}
 fee_receipts=[]
 for r in claims['records']:
  if r['field']!='outer_fee_claim_receipt':continue
  receipt=r['response'].get('result');logs=receipt['logs'] if receipt else [];claim_event=next(e for e in read('etherfi_parameter_events') if e['transaction_hash']==r['transaction_hash'] and e['event']=='FeesClaimed');params={p['name']:p['value'] for p in claim_event['decoded']['parameters']};asset=params['feeAsset'].lower();amount=int(params['amount'])
  matches=[log for log in logs if log['address'].lower()==asset and log['topics'][0]==c.TOPIC['Transfer'] and addr(int(log['topics'][1],16))==c.MAIN and int(log['data'],16)==amount]
  # The accountant calls the teller/vault transfer; the actual payer is the
  # BoringVault custody address, not the Accountant itself.
  verified=bool(receipt and int(receipt['status'],16)==1 and matches)
  tests.append({'check':'Ethereum fee claim '+r['transaction_hash']+' has matching actual custody cash transfer','passed':verified})
  fee_receipts.append({'transaction_hash':r['transaction_hash'],'asset':asset,'amount_raw':str(amount),'cash_transfer_verified':verified,'recipient':addr(int(matches[0]['topics'][2],16)) if matches else None,'sourceURL':'https://etherscan.io/tx/'+r['transaction_hash']})
 output={'schema_version':1,'snapshot_timestamp':c.T,'ethereum_block':c.BLOCK,'debt_cohorts':rows,'retained_same_unit_pair_summary':summary,'outer_fee_payment_receipts':fee_receipts,
         'method':'For loans with no repayments, trace each actual minted borrow-share cohort to its exact accrued claim at T. Retained destination cohorts use a direct historical convertToAssets call for the actual deposit shares, only after verifying no later outgoing share event. Tranche claim/debt ceilings can differ by less than one smallest asset unit per cohort from the aggregate liability.',
         'boundaries':['Co-occurring borrowing and deposits do not imply an allocation of every later cash reward or product expense.','A retained destination claim is book income, with no assertion of immediate cash redemption.','Different-token destination income and financing costs remain separate native units.','USDC loan cohorts with later destination withdrawals do not receive an invented remaining destination cost basis.','The two same-PYUSD pairs are observed at different origination dates and marked at the same T; no lifetime figures from unrelated windows are combined.','PRIME collateral ownership and private backing are a separate question from the measured PYUSD loan/deposit cash flows.'],
         'sources':[proof('data/eth/'+name+'.json') for name in ['carry_attribution_ledger','carry_attribution_states','carry_attribution_rpc','carry_attribution_tranche_rpc','etherfi_parameter_events']],
         'verification':{'checks':tests,'passed':sum(r['passed'] for r in tests),'failed':sum(not r['passed'] for r in tests)}}
 if output['verification']['failed']:raise ValueError(json.dumps([r for r in tests if not r['passed']]))
 (c.DATA/'carry_attribution_tranches.json').write_text(json.dumps(output,indent=2,allow_nan=False))
 flat=[{k:v for k,v in r.items() if k!='destination_deposits'} for r in rows]
 with (c.DATA/'carry_attribution_debt_cohorts.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
 print(json.dumps({'retained_pair':summary,'fee_receipts':fee_receipts,'cohorts':len(rows),'verification':output['verification']},indent=2))
if __name__=='__main__':build()
