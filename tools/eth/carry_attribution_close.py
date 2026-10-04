"""Presentation dataset for matched-window, measured carry-income components.

Every component is a claim, cash flow, or accrued liability. It is deliberately
not a strategy-profit calculation: matching dates do not match principal,
campaign earning periods, or all financing and portfolio costs.
"""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import carry_attribution_collect as c
from carry_attribution_build import proof

DATA=c.DATA
def read(name):return json.loads((DATA/(name+'.json')).read_text())
def export(name,table):
 if not table:return
 with (DATA/('carry_attribution_'+name+'.csv')).open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in table for k in row)));writer.writeheader();writer.writerows({k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in table)

def build():
 ledger=read('carry_attribution_ledger');window=ledger['common_window'];strategies=[];all_components=[]
 loans=window['borrowing_ledgers'];rewards=window['cash_reward_totals']
 for destination in window['destination_ledgers']:
  id=destination['destination_id'];symbol=destination['symbol']
  debt=[row for row in loans if row['symbol']==symbol] if id!='stcusd' else []
  cash=next((row for row in rewards if row['symbol']==symbol),None)
  links=[row for row in window['funding_links'] if row['destination_id']==id and row['destination_event']=='deposit']
  direct=[row for row in links if row['receipt_verified'] and row['direct_morpho_to_controlled_to_destination_transfers']]
  cross=[row for row in window.get('cross_currency_funding_links',[]) if row['destination_id']==id]
  cross_verified=[row for row in cross if row['receipt_verified'] and row['loan_receipt_transfers_verified'] and row['controlled_destination_payment_verified']]
  # Each tracked destination deposit is unique by transaction and log. The
  # same-token matches have at most one destination deposit per transaction.
  matched=sum(row['cooccurring_nominal_assets'] for row in direct)
  interest=sum(row['accrued_borrowing_interest_assets'] for row in debt)
  receipt=cash['common_window_cash_amount'] if cash else 0
  components=[{'id':'claim_growth','label':'Net growth in destination claim','value':destination['net_accrued_claim_income_assets'],'kind':'book claim','sourceURL':destination['sourceURL']},
              {'id':'paid_rewards','label':'Cash rewards paid to tracked accounts','value':receipt if cash else None,'kind':'cash receipt','sourceURL':ledger['cash_reward_review']['sourceURL']}]
  for row in debt:
   label='PRIME-backed borrowing cost' if 'against PRIME' in row['mechanism'] else 'LoanManager borrowing cost' if row['account']==c.LOAN else 'ETH-collateral borrowing cost'
   components.append({'id':'borrowing_cost_'+row['market_id'][2:10]+row['account'][2:10],'label':label,'value':-row['accrued_borrowing_interest_assets'],'kind':'accrued liability','sourceURL':row['sourceURL']})
  boundaries=[
   'The tracked debt and destination claim have different principal sizes and allocations. Their components cannot be paired into a complete sleeve profit.',
   'Rewards are measured on payment dates. A payment inside this window may relate to an earlier earning period, and its campaign or sponsor is not assigned.',
   'Net destination claim growth already reflects fees recognized in its share value. Outer product fees and operating costs are not allocated.',
   'Interest can circulate through credit supplied by the same product. Gross own-credit overlap is not independent external income.',
   'Same-transaction funding links establish cash movements, not unique fungible-dollar provenance or an allocation of subsequent earnings.'
  ]
  row={'id':id,'label':{'rlusd-v2':'Liquid ETH: RLUSD lending and financing','pyusd-prime-v2':'Liquid ETH: PYUSD lending and financing','stcusd':'Liquid ETH: stcUSD destination claim'}[id],
       'asset':destination['symbol'],'unit':destination['symbol'],'account':destination['account'],'claim':destination,'loans':debt,
       'claim_growth':destination['net_accrued_claim_income_assets'],'cash_rewards':receipt if cash else None,
       'cash_reward_payment_count':cash['common_window_payment_count'] if cash else 0,'accrued_borrow_cost':interest if debt else None,
       'components':components,'component_balance':destination['net_accrued_claim_income_assets']+receipt-interest if debt else None,
       'component_balance_label':'Partial component comparison, not sleeve profit','complete_sleeve_net_income':None,
       'funding_coverage':{'deposit_cash_assets':destination['deposits_assets'],'deposit_count':destination['deposit_count'],
                           'same_transaction_direct_link_count':len(direct),'same_transaction_cooccurring_assets':matched,
                           'same_transaction_share_of_deposits':matched/destination['deposits_assets'] if destination['deposits_assets'] else None,
                           'deposit_principal_without_same_token_same_transaction_link':destination['deposits_assets']-matched,
                           'cross_currency_same_transaction_deposit_count':len(cross_verified),
                           'cross_currency_same_transaction_destination_assets':sum(r['destination_assets'] for r in cross_verified),
                           'deposits_without_same_transaction_link_after_cross_currency_screen':destination['deposits_assets']-matched-sum(r['destination_assets'] for r in cross_verified),
                           'opening_destination_claim_assets':destination['opening_claim_assets'],
                           'opening_tracked_accrued_debt_assets':sum(r['opening_accrued_debt_assets'] for r in debt) if debt else None,
                           'ending_destination_claim_assets':destination['ending_claim_assets'],
                           'ending_tracked_accrued_debt_assets':sum(r['ending_accrued_debt_assets'] for r in debt) if debt else None,
                           'scope':'Native same-token loan cash coverage verified in receipt log order through controlled-wallet hops. Deposits before loan receipt and cash consumed earlier in the transaction are excluded. Unmatched cash is retained; it is not assumed unborrowed.'},
       'funding_links':links,'cross_currency_funding_links':cross,'boundaries':boundaries,'status':'Measured components; whole sleeve profit unresolved','sourceURL':destination['sourceURL']}
  strategies.append(row)
  all_components.extend({'strategy_id':id,'symbol':symbol,**x} for x in components)
 recycling=read('carry_attribution_recycling') if (DATA/'carry_attribution_recycling.json').exists() else None
 organic=read('carry_attribution_organic') if (DATA/'carry_attribution_organic.json').exists() else None
 tranches=read('carry_attribution_tranches') if (DATA/'carry_attribution_tranches.json').exists() else None
 output={'schema_version':1,
  'snapshot':{'timestamp':ledger['snapshot_timestamp'],'date':ledger['snapshot_date'],'ethereum_block':ledger['ethereum_block'],'source_type':'Historical Ethereum contract state and logs, captured separately after T'},
  'title':'What the carry legs actually earned and owed',
  'scope':'A historical reconciliation of selected Liquid ETH destinations, tracked Morpho debt and rewards paid to four controlled accounts. Components are measured; a complete carry sleeve or whole-product profit is not established.',
  'common_window':{k:window[k] for k in ['start_block','start_timestamp','start_date','end_block','end_timestamp','end_date','days','start_convention']},
  'price_convention':'Amounts remain in their native loan or destination asset. No $1 peg assumption, historical USD conversion or ETH-value attribution is used.',
  'strategies':strategies,
  'funding_coverage':{'controlled_accounts':c.ACCOUNTS,'common_window_links':window['funding_links'],'same_token_direct_deposit_link_count':sum(s['funding_coverage']['same_transaction_direct_link_count'] for s in strategies),
                      'cross_currency_common_window_links':window.get('cross_currency_funding_links',[]),
                      'scope':'Same-transaction Morpho loan receipts and controlled-wallet destination deposits, with actual token transfers in successful receipts. Different currencies and earlier cash inventory are not silently paired.'},
  'cash_rewards':ledger['cash_reward_review'],
  'own_credit_recycling':recycling or {'status':'Snapshot own-credit exposure measured; historical own-interest allocation unresolved','historical_income':None,'snapshot_source':'data/eth/carry_credit_lookthrough.json','boundary':'The product supplies credit to markets in which it also borrows. The snapshot ownership share is not applied backward to historical interest.'},
  'organic_source_review':organic,
  'matched_debt_and_destination_cohorts':tranches,
  'fees':ledger['fees'],
  'fees_common_window':organic['outer_fees_common_window'] if organic else None,
  'matched_window_share_returns':organic['matched_benchmarks'] if organic else None,
  'other_measured_debt':loans,
  'prime_destination':next(row for row in ledger['destination_ledgers'] if row['id']=='prime'),
  'whole_product_boundary':ledger['whole_product_boundary'],
  'top5_coverage':ledger['top5_coverage'],
  'findings':[
   {'id':'book_vs_cash','title':'Claim growth and paid rewards are different forms of income','text':'Across the same 56.29-day window, the RLUSD claim grew by 145,919.43 RLUSD and the PYUSD claim by 164,823.37 PYUSD after deposits and withdrawals. Separately, tracked accounts received 172,802.40 RLUSD and 150,678.52 PYUSD in Merkl cash rewards. The payments do not establish the earning period or campaign.'},
   {'id':'financing_is_observed','title':'Funding cost is reconstructed from debt, not a current APR','text':'For the same window, the two tracked RLUSD loans accrued 405,516.92 RLUSD of interest. The ETH-collateral PYUSD loan accrued 208,331.44 PYUSD, with another 17,993.33 PYUSD on PRIME-backed borrowing. These liabilities have different principal sizes and allocations from the destination claims.'},
   {'id':'funding_link','title':'Some cash links are proven; principal remains unmatched','text':'Successful receipts establish 12 ordered same-token borrow/deposit cash links: 36.0 million RLUSD and 39.4 million PYUSD. A PYUSD deposit made before its transaction\'s loan receipt is excluded. Four more receipts show USDC borrowing alongside deposits of 18.67 million RLUSD and 1.99 million PYUSD. Native currencies, opening positions and remaining unmatched principal stay explicit.'},
   {'id':'profit_boundary','title':'The component comparison is not complete strategy profit','text':'The ledgers do not allocate every dollar of debt to one destination, every reward payment to its earning period, the product\'s own-credit interest, or outer fees. Whole-product income attributable to carry remains unresolved.'}
  ],
  'sources':ledger['sources']+[proof('data/eth/carry_attribution_ledger.json')]+([proof('data/eth/carry_attribution_recycling.json')] if recycling else [])+([proof('data/eth/carry_attribution_organic.json')] if organic else [])+([proof('data/eth/carry_attribution_tranches.json')] if tranches else []),
  'raw_manifest':ledger['raw_manifest'],'verification':ledger['verification'],
  'limitations':ledger['limitations']+['No measured partial component balance is labelled realized carry profit.','The four controlled accounts and selected destinations do not cover every Liquid ETH chain, lender or former investment.'],
  'offline_rebuild':['python3 tools/eth/carry_attribution_build.py','python3 tools/eth/carry_attribution_recycling.py','python3 tools/eth/carry_attribution_organic.py','python3 tools/eth/carry_attribution_tranches.py','python3 tools/eth/carry_attribution_close.py']}
 if (DATA/'carry_attribution_verification.json').exists():
  independent=read('carry_attribution_verification')
  output['verification']['independent']={k:independent[k] for k in ['verification_command','passed','failed','public_captures_hashed','failed_capture_attempts_preserved']}
  output['verification']['independent']['report']='data/eth/carry_attribution_verification.json'
  output['offline_verify']='python3 tools/eth/carry_attribution_verify.py'
 for row in output['strategies']:
  row['boundaries'].append('USDC borrowing cost is measured separately: its funding receipts include deposits in different currencies. It is not converted or silently assigned to an RLUSD or PYUSD component bar.')
 (DATA/'carry_attribution_closure.json').write_text(json.dumps(output,indent=2,allow_nan=False))
 export('common_window_components',all_components);export('cash_rewards',ledger['cash_reward_review']['payments'])
 export('common_window_claims',window['destination_ledgers']);export('common_window_debt',loans)
 print(json.dumps({'file':'data/eth/carry_attribution_closure.json','strategies':len(strategies),'component_rows':len(all_components),'window_days':window['days'],'verification':ledger['verification']['failed']},indent=2))
if __name__=='__main__':build()
