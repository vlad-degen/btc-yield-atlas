"""Independent offline checks against raw source events, receipts and state.

This verifier does not import either income calculation or accounting helper.
It independently recomputes native-asset endpoint residuals and tests temporal
cash coverage, primary-state reconciliation, source hashes and scope limits.
"""
from __future__ import annotations
import collections,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'data/eth';checks=[]
T=1790985599;BLOCK=26108081;MAIN='0xf0bb20865277abd641a307ece5ee04e79073416c';MORPHO='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
def read(name):return json.loads((DATA/(name+'.json')).read_text())
def words(value):return [int(value[i:i+64],16) for i in range(2,len(value),64)]
def address(topic):return '0x'+topic[-40:].lower()
def check(label,ok,detail=None):
 row={'check':label,'passed':bool(ok)}
 if detail is not None:row['detail']=detail
 checks.append(row)
def nearly(a,b,dec=18):return math.isclose(a,b,rel_tol=1e-13,abs_tol=1e-8 if dec==18 else .5/10**dec)
def state(rows,kind,id,field,account=None):
 r=next(r for r in rows if r['kind']==kind and r.get('id')==id and r['field']==field and (account is None or r.get('account')==account));return words(r['response']['result'])
def debt(market,rate,timestamp,shares):
 # Morpho's source rounds each Taylor term down, then the account debt up.
 elapsed=timestamp-market[4];x=rate*elapsed;second=(x*x)//(2*10**18);third=(second*x)//(3*10**18)
 interest=(market[2]*(x+second+third))//10**18
 numerator=shares*(market[2]+interest+1);denominator=market[3]+10**6
 return (numerator+denominator-1)//denominator
def main():
 closure=read('carry_attribution_closure');ledger=read('carry_attribution_ledger');raw=read('carry_attribution_rpc');states=read('carry_attribution_states');win=read('carry_attribution_window_states');flows=read('carry_attribution_flows');proof=read('carry_attribution_closure_proof');start=win['start_block'];topics=raw['event_topics'];groups={g['key']:g for g in raw['log_groups']};times={r['block']:int(r['response']['result']['timestamp'],16) for r in win['blocks']}
 check('T timestamp is exact last captured Ethereum block timestamp',times[BLOCK]==T)
 check('presentation snapshot matches fixed source state',closure['snapshot']['timestamp']==T and closure['snapshot']['ethereum_block']==BLOCK and states['block']==BLOCK)
 check('common window begins immediately before actual first RLUSD deposit',start+1==min(int(r['blockNumber'],16) for r in groups['rlusd-v2_deposit']['logs']))
 check('every requested source log group completed',all(g['complete'] for name in ['carry_attribution_rpc','carry_attribution_flows','carry_attribution_recycling_rpc','carry_attribution_organic_rpc'] for g in read(name)['log_groups']))
 check('all captured income events are at or before T block',all(int(r['blockNumber'],16)<=BLOCK for g in raw['log_groups'] for r in g['logs']))
 check('tracked account code absent at beginning of scanned history',all(r['response'].get('result')=='0x' for r in proof['records'] if r['key'].startswith('opening_code_')))
 check('PRIME underlying decimals are verified six, not inferred from USD value',words(next(r['response']['result'] for r in proof['records'] if r['key']=='prime_underlying_decimals()'))[0]==6)
 for loan in ledger['borrowing_ledgers']:
  id=loan['market_id'];account=loan['account'];dec=loan['decimals'];events=[r for r in ledger['borrowing_events'] if r['ledger_id']==loan['id']]
  em=state(states['records'],'market',id,'market');ep=state(states['records'],'market',id,'position',account);er=state(states['records'],'market',id,'borrow_rate')[0]
  params=state(states['records'],'market',id,'params')
  check(loan['id']+' bound to AdaptiveCurveIRM',address(hex(params[3]))=='0x870ac11d48b15db9a138cf899d20f13f79ba00bc')
  end=debt(em,er,T,ep[1]);borrow=sum(int(r['assets_raw']) for r in events if r['event']=='borrow');repaid=sum(int(r['assets_raw']) for r in events if r['event']=='repay')
  netshares=sum(int(r['shares_raw'])*(1 if r['event']=='borrow' else -1) for r in events)
  check(loan['id']+' raw event shares equal ending contract position',netshares==ep[1])
  check(loan['id']+' lifetime interest independently recomputed',nearly((end+repaid-borrow)/10**dec,loan['cumulative_accrued_borrowing_interest_assets'],dec))
  wr=next(r for r in ledger['common_window']['borrowing_ledgers'] if r['ledger_id']==loan['id']);om=state(win['records'],'market',id,'market');op=state(win['records'],'market',id,'position',account)
  opening=debt(om,state(win['records'],'market',id,'borrow_rate')[0],times[start],op[1]) if om[4] else 0
  ev=[r for r in events if r['block']>start];b=sum(int(r['assets_raw']) for r in ev if r['event']=='borrow');r=sum(int(r['assets_raw']) for r in ev if r['event']=='repay')
  check(loan['id']+' common-window interest independently recomputed',nearly((end-opening+r-b)/10**dec,wr['accrued_borrowing_interest_assets'],dec))
  check(loan['id']+' common-window starting and ending debt are independently marked',nearly(opening/10**dec,wr['opening_accrued_debt_assets'],dec) and nearly(end/10**dec,wr['ending_accrued_debt_assets'],dec))
 for destination in ledger['common_window']['destination_ledgers']:
  id=destination['destination_id'];dec=next(r['decimals'] for r in ledger['destination_ledgers'] if r['id']==id);account=destination['account']
  opening=state(win['records'],'destination',id,'convertToAssets',account)[0];ending=state(states['records'],'destination',id,'convertToAssets',account)[0]
  events=[r for r in ledger['destination_events'] if r['destination_id']==id and r['account']==account and r['block']>start]
  deposits=sum(int(r['assets_raw']) for r in events if r['event']=='deposit');withdrawals=sum(int(r['assets_raw']) for r in events if r['event']=='withdraw')
  check(id+' native claim growth independently recomputed',nearly((ending-opening+withdrawals-deposits)/10**dec,destination['net_accrued_claim_income_assets'],dec))
  check(id+' redeemed and retained claim gains add to net claim growth',nearly(destination['redeemed_share_gain_assets']+destination['remaining_claim_gain_assets'],destination['net_accrued_claim_income_assets'],dec))
  open_shares=state(win['records'],'destination',id,'balanceOf(address)',account)[0];end_shares=state(states['records'],'destination',id,'balanceOf(address)',account)[0]
  share_delta=sum(int(r['shares_raw'])*(1 if r['event']=='deposit' else -1) for r in events)
  check(id+' exact native share ledger preserves opening and ending balances',open_shares+share_delta==end_shares)
 reward_group=next(g for g in flows['log_groups'] if g['key']=='merkl_cash_reward_transfers');meta={}
 for record in win['reward_token_metadata']:
  if record['field']=='decimals()':meta[record['address']]=words(record['response']['result'])[0]
 for total in ledger['cash_reward_review']['totals']:
  actual=[r for r in reward_group['logs'] if r['address'].lower()==total['asset'] and int(r['blockNumber'],16)>start];amount=sum(int(r['data'],16) for r in actual)
  check(total['symbol']+' reward amounts equal actual in-window cash transfers',len(actual)==total['common_window_payment_count'] and nearly(amount/10**meta[total['asset']],total['common_window_cash_amount'],meta[total['asset']]))
  check(total['symbol']+' reward payer and receivers verified',all(address(r['topics'][1])==flows['merkl_distributor'] and address(r['topics'][2]) in raw['accounts'] for r in actual))
 receipts={r['transaction_hash']:r['response']['result'] for r in flows['receipts']}
 direct=[r for r in ledger['common_window']['funding_links'] if r['destination_event']=='deposit' and r['direct_morpho_to_controlled_to_destination_transfers']]
 check('corrected ordered direct funding count is12',len(direct)==12)
 check('corrected RLUSD coverage is36 million',sum(r['cooccurring_nominal_assets'] for r in direct if r['symbol']=='RLUSD')==36000000)
 check('corrected PYUSD coverage is39.4 million',sum(r['cooccurring_nominal_assets'] for r in direct if r['symbol']=='PYUSD')==39400000)
 for row in direct:
  receipt=receipts[row['transaction_hash']];cashproof=row['receipt_ordered_cash_coverage'];logs={int(r['logIndex'],16):r for r in receipt['logs']};balances=collections.defaultdict(int);covered=0
  events=sorted([(r['transfer_log_index'],'source',r) for r in cashproof['loan_receipts']]+[(r['log_index'],'hop',r) for r in cashproof['hops']],key=lambda x:x[0])
  for index,kind,entry in events:
   log=logs[index];actual=int(log['data'],16);sender=address(log['topics'][1]);receiver=address(log['topics'][2])
   check(row['transaction_hash']+' '+str(index)+' actual transfer matches cash proof',actual==int(entry['amount_raw']) and log['topics'][0]==topics['Transfer'])
   if kind=='source':
    b=next(r for r in ledger['borrowing_events'] if r['transaction_hash']==row['transaction_hash'] and r['log_index']==entry['loan_event_log_index'])
    check(row['transaction_hash']+' source exactly matches preceding loan',sender==MORPHO and receiver==b['receiver'] and actual==int(b['assets_raw']) and b['log_index']<index)
    balances[receiver]+=actual
   else:
    tagged=int(entry['covered_loan_cash_raw']);check(row['transaction_hash']+' '+str(index)+' controlled-hop coverage feasible',sender in raw['accounts'] and tagged==min(actual,balances[sender]) and entry['from']==sender and entry['to']==receiver)
    balances[sender]-=tagged
    if receiver in raw['accounts']:balances[receiver]+=tagged
    if index==cashproof['destination_transfer']['log_index']:covered=tagged
  check(row['transaction_hash']+' covered funding precedes deposit event',covered==int(cashproof['covered_raw']) and covered>0 and cashproof['destination_transfer']['log_index']<row['destination_event_log_index'])
 early=[r for r in ledger['common_window']['funding_links'] if r['transaction_hash']=='0x3e66faeae23a347b524536ae17291e0f7c9d89c39bbba2e711cae76afd21e12d' and r['destination_event']=='deposit' and r['destination_event_log_index']==180]
 check('deposit before loan is explicitly unfunded in this transaction',len(early)==1 and early[0]['cooccurring_nominal_assets']==0 and early[0]['direct_morpho_to_controlled_to_destination_transfers'] is False)
 for row in ledger['common_window']['cross_currency_funding_links']:
  receipt=receipts[row['transaction_hash']];destination=next(d for d in ledger['destination_events'] if d['transaction_hash']==row['transaction_hash'] and d['destination_id']==row['destination_id'] and d['event']=='deposit')
  loan_transfers=[r for r in receipt['logs'] if r['topics'][0]==topics['Transfer'] and r['address'].lower() in {x['asset'] for x in row['loans']} and address(r['topics'][1])==MORPHO]
  check(row['transaction_hash']+' cross-currency cash received before destination deposit',bool(loan_transfers) and all(int(r['logIndex'],16)<destination['log_index'] for r in loan_transfers) and row['loan_receipt_transfers_verified'] and row['controlled_destination_payment_verified'])
 for name in ['carry_attribution_recycling','carry_attribution_organic','carry_attribution_tranches']:
  result=read(name);check(name+' own source-ledger checks pass',result['verification']['failed']==0)
  for source in result['sources']:
   path=ROOT/source['path'];check(name+' source '+source['path']+' immutable hash matches',path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256'])
 cohort=read('carry_attribution_tranches')['retained_same_unit_pair_summary']
 check('short retained PYUSD cohort is108 seconds, not investment economics',cohort['window_seconds']==108 and cohort['loan_cash_assets']==3000000 and nearly(cohort['net_accrued_destination_claim_growth_assets'],.557687,6) and nearly(cohort['accrued_borrowing_interest_assets'],.751967,6) and nearly(cohort['lending_minus_borrowing_component_assets'],-.19428,6))
 for strategy in closure['strategies']:
  check(strategy['id']+' complete profit remains unknown',strategy['complete_sleeve_net_income'] is None and 'not sleeve profit' in strategy['component_balance_label'])
  check(strategy['id']+' unpaired deposits are preserved',strategy['funding_coverage']['deposit_principal_without_same_token_same_transaction_link']>=0)
 check('all Top5 complete organic-carry attribution remains open',len(closure['top5_coverage'])==5 and all(r['organic_carry_income_closed'] is False for r in closure['top5_coverage']))
 for source in closure['sources']:
  path=ROOT/source['path'];check('closure source '+source['path']+' hash matches',path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256'])
 manifest=ROOT/closure['raw_manifest'];entries=[json.loads(line) for line in manifest.read_text().splitlines()];successful=[r for r in entries if r.get('path')]
 check('all successful public captures preserve matching content hashes',all((ROOT/r['path']).exists() and hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in successful))
 output={'schema_version':1,'snapshot_timestamp':T,'ethereum_block':BLOCK,'verification_command':'python3 tools/eth/carry_attribution_verify.py','passed':sum(r['passed'] for r in checks),'failed':sum(not r['passed'] for r in checks),'checks':checks,
         'public_captures_hashed':len(successful),'failed_capture_attempts_preserved':sum(not bool(r.get('path')) for r in entries),
         'scope':'Independent source-state residuals, exact cash transfers and loan-ordering/controlled-hop coverage. This confirms the bounded accounting, not complete economic attribution of the product.'}
 (DATA/'carry_attribution_verification.json').write_text(json.dumps(output,indent=2))
 print(json.dumps({k:output[k] for k in ['passed','failed','public_captures_hashed','failed_capture_attempts_preserved']},indent=2))
 if output['failed']:raise SystemExit(json.dumps([r for r in checks if not r['passed']],indent=2))
if __name__=='__main__':main()
