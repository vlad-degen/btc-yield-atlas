"""Historical own-credit overlap, reconstructed at actual accrual events.

This is a gross economic overlap diagnostic. It is not cash returned to Liquid,
an allocation of net destination income, or independent external yield.
"""
from __future__ import annotations
import csv, json
from decimal import Decimal, getcontext
import carry_attribution_collect as c
from carry_attribution_build import read, ordered, addr, proof
from carry_economics_build import accrue
getcontext().prec=70
ZERO='0x'+'0'*40

def build():
 raw=read('carry_attribution_recycling_rpc');opening=read('carry_attribution_window_states');ending=read('carry_attribution_states');ledger=read('carry_attribution_ledger')
 checks=[];table=[];outputs=[]
 def state(period,kind,id,field,account=None):
  rows=opening['records'] if period=='start' else ending['records']
  row=next(r for r in rows if r['kind']==kind and r.get('id')==id and r['field']==field and (account is None or r.get('account')==account));return c.words(row['response']['result'])
 topics={v:k for k,v in raw['event_topics'].items()}
 groups={g['key']:g for g in raw['log_groups']}
 for target in raw['targets']:
  id=target['destination_id'];mid=target['market_id'];adapter=target['adapter'];d=next(d for d in c.DESTINATIONS if d['id']==id)
  m=state('start','market',mid,'market');supply_assets,supply_shares,borrow_assets,borrow_shares,update,fee=m
  starting_rate=state('start','market',mid,'borrow_rate')[0]
  pending_open=accrue(m,starting_rate,ledger['common_window']['start_timestamp'])
  adapter_shares=c.words(next(r['response']['result'] for r in raw['opening_records'] if r.get('market_id')==mid and r['field']=='adapter_position'))[0]
  vault_supply=c.words(next(r['response']['result'] for r in raw['opening_records'] if r.get('destination_id')==id and r['field']=='vault_total_supply'))[0]
  product_shares=state('start','destination',id,'balanceOf(address)',c.MAIN)[0]
  tracked={a:state('start','market',mid,'position',a)[1] for a in c.ACCOUNTS}
  events=ordered([r for r in groups['own_credit_market_events']['logs'] if r['topics'][1]==mid]+groups[id+'_all_share_transfers']['logs'])
  total_interest=Decimal(0);tracked_interest=Decimal(0);own_overlap=Decimal(0);external_overlap=Decimal(0);first_accrual=True;counts={};market_fee_changed=False
  for r in events:
   name=topics[r['topics'][0]];w=c.words(r['data']);counts[name]=counts.get(name,0)+1
   if name=='Transfer':
    sender=addr(int(r['topics'][1],16));receiver=addr(int(r['topics'][2],16));amount=w[0]
    if sender==ZERO:vault_supply+=amount
    if receiver==ZERO:vault_supply-=amount
    if sender==c.MAIN:product_shares-=amount
    if receiver==c.MAIN:product_shares+=amount
    continue
   if name=='AccrueInterest':
    interest=w[1];window_interest=interest-pending_open if first_accrual else interest
    # The opening book already contains pending interest at the start. Remove
    # it once, rather than double counting the period before the common window.
    if window_interest<0:raise ValueError('Opening pending interest exceeds first accrual')
    total_interest+=window_interest
    borrower_fraction=Decimal(sum(tracked.values()))/Decimal(borrow_shares+10**6)
    adapter_fraction=Decimal(adapter_shares)/Decimal(supply_shares+10**6)
    owner_fraction=Decimal(product_shares)/Decimal(vault_supply+10**max(18-d['decimals'],0))
    own=Decimal(window_interest)*borrower_fraction*adapter_fraction*owner_fraction
    external=Decimal(window_interest)*(1-borrower_fraction)*adapter_fraction*owner_fraction
    tracked_interest+=Decimal(window_interest)*borrower_fraction;own_overlap+=own;external_overlap+=external
    table.append({'destination_id':id,'symbol':d['symbol'],'market_id':mid,'block':int(r['blockNumber'],16),'transaction_hash':r['transactionHash'],'log_index':int(r['logIndex'],16),
                  'market_recorded_interest_raw':str(interest),'prewindow_interest_removed_raw':str(pending_open if first_accrual else 0),'window_interest_raw':str(window_interest),
                  'tracked_borrower_fraction':float(borrower_fraction),'adapter_supply_fraction':float(adapter_fraction),'product_vault_share_fraction':float(owner_fraction),
                  'gross_own_credit_overlap_assets':float(own/10**d['decimals']),'gross_external_credit_overlap_assets':float(external/10**d['decimals']),
                  'sourceURL':'https://etherscan.io/tx/'+r['transactionHash']})
    supply_assets+=interest;borrow_assets+=interest;supply_shares+=w[2];first_accrual=False
   elif name=='Supply':
    supply_assets+=w[0];supply_shares+=w[1]
    if addr(int(r['topics'][3],16))==adapter:adapter_shares+=w[1]
   elif name=='MorphoWithdraw':
    supply_assets-=w[1];supply_shares-=w[2]
    if addr(int(r['topics'][2],16))==adapter:adapter_shares-=w[2]
   elif name=='Borrow':
    borrow_assets+=w[1];borrow_shares+=w[2];a=addr(int(r['topics'][2],16))
    if a in tracked:tracked[a]+=w[2]
   elif name=='Repay':
    borrow_assets-=w[0];borrow_shares-=w[1];a=addr(int(r['topics'][3],16))
    if a in tracked:tracked[a]-=w[1]
   elif name=='Liquidate':
    borrow_assets-=w[0]+w[3];borrow_shares-=w[1]+w[4];supply_assets-=w[3];a=addr(int(r['topics'][3],16))
    if a in tracked:tracked[a]-=w[1]+w[4]
   elif name=='SetFee':fee=w[0];market_fee_changed=True
   if min(supply_assets,supply_shares,borrow_assets,borrow_shares,adapter_shares,vault_supply,product_shares,*tracked.values())<0:raise ValueError('Negative reconstructed balance')
  endm=state('end','market',mid,'market')
  for label,a,b in [('market_supply_assets',supply_assets,endm[0]),('market_supply_shares',supply_shares,endm[1]),('market_borrow_assets',borrow_assets,endm[2]),('market_borrow_shares',borrow_shares,endm[3]),('market_fee',fee,endm[5]),('vault_supply',vault_supply,state('end','destination',id,'totalSupply()')[0]),('product_vault_shares',product_shares,state('end','destination',id,'balanceOf(address)',c.MAIN)[0])]:checks.append({'check':id+' '+label+' matches actual T state','passed':a==b})
  for account,shares in tracked.items():checks.append({'check':id+' borrower '+account+' shares match actual T','passed':shares==state('end','market',mid,'position',account)[1]})
  if (c.DATA/'carry_attribution_closure_proof.json').exists():
   pr=read('carry_attribution_closure_proof');row=next(r for r in pr['records'] if r['key']==id+'_ending_adapter_position')
   checks.append({'check':id+' adapter supply shares match actual T','passed':adapter_shares==c.words(row['response']['result'])[0]})
  outputs.append({**target,'symbol':d['symbol'],'accrual_event_count':counts.get('AccrueInterest',0),'event_counts':counts,
                  'market_recorded_interest_in_window_assets':float(total_interest/10**d['decimals']),
                  'tracked_borrower_recorded_interest_assets':float(tracked_interest/10**d['decimals']),
                  'event_weighted_gross_own_credit_overlap_assets':float(own_overlap/10**d['decimals']),
                  'event_weighted_gross_external_credit_overlap_assets':float(external_overlap/10**d['decimals']),
                  'allocated_net_destination_own_interest':None,'actually_paid_own_interest':None,
                  'opening_pending_market_interest_removed_assets':pending_open/10**d['decimals'],
                  'market_fee_fraction':fee/1e18,'market_fee_changed':market_fee_changed,
                  'scope':'Gross interest overlap at actual market accrual events, with reconstructed contemporaneous borrower, adapter and product shares. It is before destination fees and rate caps; claim recognition and cash settlement are not allocated.'})
 output={'schema_version':1,'start_block':raw['start_block'],'end_block':raw['end_block'],'status':'Historical share ownership and market cash-flow ledgers reconciled; net own-credit income and settlement remain unassigned',
         'historical_income':None,'rows':outputs,'events':table,
         'method':'For each recorded market-interest event, multiply interest after the common-window opening adjustment by the tracked borrow-share fraction, the adapter supply-share fraction, and Liquid\'s contemporaneous destination-share fraction. All fractions follow actual transfers, supplies, withdrawals, borrowing and repayments. No T ownership fraction is applied backward.',
         'boundaries':['Event-time ownership attributes recognized interest, not an exact ownership-weighted integration of its economic earning time between accrual events.','The diagnostic is gross of destination fees, rate caps, pending fee dilution and whole-product fees.','Pending interest after the last market update at T is included in debt-cost ledgers but excluded from this recorded-event diagnostic.','Gross own-credit overlap is neither additional income nor independently funded external yield.','No net returned interest or campaign allocation is inferred.'],
         'sources':[proof('data/eth/'+n+'.json') for n in ['carry_attribution_recycling_rpc','carry_attribution_window_states','carry_attribution_states','carry_attribution_closure_proof']],
         'verification':{'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks)}}
 if output['verification']['failed']:raise ValueError(json.dumps([x for x in checks if not x['passed']]))
 (c.DATA/'carry_attribution_recycling.json').write_text(json.dumps(output,indent=2,allow_nan=False))
 with (c.DATA/'carry_attribution_recycling_events.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
 print(json.dumps({'rows':outputs,'verification':output['verification']},indent=2))
if __name__=='__main__':build()
