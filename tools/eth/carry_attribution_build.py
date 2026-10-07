"""Offline cash-flow and accrued-debt reconciliation of captured carry legs."""
from __future__ import annotations
import collections, csv, datetime as dt, hashlib, json, math
from decimal import Decimal, getcontext
from pathlib import Path
import carry_attribution_collect as c
from carry_economics_build import accrue, borrow_assets, abi_string

ROOT=c.ROOT;DATA=c.DATA
getcontext().prec=70
def read(n):return json.loads((DATA/(n+'.json')).read_text())
def addr(n):return '0x'+format(n,'040x')
def date(t):return dt.datetime.fromtimestamp(t,dt.timezone.utc).isoformat() if t else None
def ident(r):return (r['transactionHash'],int(r['logIndex'],16))
def ordered(rows):return sorted({ident(r):r for r in rows}.values(),key=lambda r:(int(r['blockNumber'],16),int(r['transactionIndex'],16),int(r['logIndex'],16)))
def proof(path):
 p=ROOT/path;digest=hashlib.sha256(p.read_bytes()).hexdigest()
 # Derived inputs owned by other researchers can be rebuilt. Preserve the
 # exact version used here so a later editorial rebuild cannot invalidate it.
 if path.startswith('data/eth/') and not p.name.startswith('carry_attribution_'):
  frozen=c.RAW/('input-'+p.stem+'-'+digest[:12]+p.suffix)
  if not frozen.exists():frozen.write_bytes(p.read_bytes())
  return {'path':str(frozen.relative_to(ROOT)),'sha256':digest,'original_path':path}
 return {'path':path,'sha256':digest}

def cash_basis(events,start_shares,start_assets,end_assets,decimals):
 """Explicit weighted-average cost basis, in raw native asset/share units."""
 shares=start_shares;basis=Decimal(start_assets);realized=Decimal(0)
 for row in sorted(events,key=lambda r:(r['block'],r['log_index'])):
  qty=int(row['shares_raw']);assets=Decimal(row['assets_raw'])
  if row['event']=='deposit':shares+=qty;basis+=assets
  else:
   used=basis*Decimal(qty)/Decimal(shares);realized+=assets-used;basis-=used;shares-=qty
 scale=Decimal(10**decimals)
 return {'redeemed_share_gain_assets':float(realized/scale),'remaining_claim_gain_assets':float((Decimal(end_assets)-basis)/scale),'remaining_cost_basis_assets':float(basis/scale),'basis_method':'Weighted-average assets paid per acquired share; common-window opening shares are marked at the opening book claim. Withdrawals include principal; only proceeds above assigned basis are labelled redeemed-share gain.'}

def ordered_funding(receipt,d,borrow_events):
 """Conservative in-transaction loan cash coverage through controlled hops.

 Trace only exact observed loan receipts. Internal controlled transfers retain
 cash coverage; any external outgoing transfer consumes it. A deposit before a
 loan receipt has zero loan coverage. These are fungible cash-coverage bounds,
 not a claim to identify unique dollars or assign later investment earnings.
 """
 if not receipt:return {'covered_raw':0,'loan_receipts':[],'hops':[],'destination_transfer':None}
 transfers=ordered([r for r in receipt['logs'] if r['address'].lower()==d['asset'] and r['topics'][0]==c.TOPIC['Transfer'] and int(r['logIndex'],16)<d['log_index']])
 destinations=[r for r in transfers if addr(int(r['topics'][1],16)) in c.ACCOUNTS and addr(int(r['topics'][2],16))==d['vault'] and int(r['data'],16)==int(d['assets_raw'])]
 target=destinations[-1] if destinations else None;cash=collections.defaultdict(int);sources=[];hops=[];covered=0;used=set()
 for transfer in transfers:
  sender=addr(int(transfer['topics'][1],16));receiver=addr(int(transfer['topics'][2],16));amount=int(transfer['data'],16);log_index=int(transfer['logIndex'],16)
  match=next((b for b in borrow_events if (b['transaction_hash'],b['log_index']) not in used and b['receiver']==receiver and int(b['assets_raw'])==amount and b['log_index']<log_index),None) if sender==c.MORPHO else None
  if match and receiver in c.ACCOUNTS:
   cash[receiver]+=amount;used.add((match['transaction_hash'],match['log_index']));sources.append({'loan_event_log_index':match['log_index'],'transfer_log_index':log_index,'receiver':receiver,'amount_raw':str(amount),'ledger_id':match['ledger_id']})
  elif sender in c.ACCOUNTS:
   tagged=min(cash[sender],amount);cash[sender]-=tagged
   if receiver in c.ACCOUNTS:cash[receiver]+=tagged
   hops.append({'from':sender,'to':receiver,'amount_raw':str(amount),'covered_loan_cash_raw':str(tagged),'log_index':log_index})
   if target and ident(transfer)==ident(target):covered=tagged
 return {'covered_raw':covered,'loan_receipts':sources,'hops':hops,'destination_transfer':{'log_index':int(target['logIndex'],16),'amount_raw':str(int(target['data'],16))} if target else None}

def build():
 raw=read('carry_attribution_rpc');states=read('carry_attribution_states');flowpath=DATA/'carry_attribution_flows.json';flows=read('carry_attribution_flows') if flowpath.exists() else {}
 if (DATA/'carry_attribution_closure_proof.json').exists():
  pr=read('carry_attribution_closure_proof')
  meta={r['key']:r['response'].get('result') for r in pr['records']}
  prime=next(d for d in c.DESTINATIONS if d['id']=='prime')
  prime['symbol']=abi_string(meta['prime_underlying_symbol()'])
  prime['decimals']=c.words(meta['prime_underlying_decimals()'])[0]
 rows=states['records'];groups={r['key']:r for r in raw['log_groups']}
 times={r['block']:int(r['response']['result']['timestamp'],16) for r in states['event_blocks'] if r['response'].get('result')}
 tests=[]
 def check(ok,label):
  tests.append({'check':label,'passed':bool(ok)})
 def lookup(kind,ident,field,account=None):
  r=next((r for r in rows if r['kind']==kind and (r.get('id')==ident or r.get('address')==ident) and r['field']==field and (account is None or r.get('account')==account)),None)
  return c.words(r['response'].get('result')) if r else None
 def event_meta(r):
  b=int(r['blockNumber'],16);return {'block':b,'timestamp':times.get(b),'date':date(times.get(b)),'transaction_hash':r['transactionHash'],'log_index':int(r['logIndex'],16),'sourceURL':'https://etherscan.io/tx/'+r['transactionHash']}
 dests=[];dest_events=[]
 for d in c.DESTINATIONS:
  deposits=ordered(groups[d['id']+'_deposit']['logs']);withdrawals=ordered(groups[d['id']+'_withdraw']['logs']);transfers=ordered(groups[d['id']+'_share_in']['logs']+groups[d['id']+'_share_out']['logs']);byaccount=[]
  for account in c.ACCOUNTS:
   dep=[r for r in deposits if addr(int(r['topics'][2],16))==account];wd=[r for r in withdrawals if addr(int(r['topics'][3],16))==account]
   incoming=[r for r in transfers if addr(int(r['topics'][2],16))==account];outgoing=[r for r in transfers if addr(int(r['topics'][1],16))==account]
   dw=[c.words(r['data']) for r in dep];ww=[c.words(r['data']) for r in wd]
   deposit_raw=sum(r[0] for r in dw);withdraw_raw=sum(r[0] for r in ww);minted=sum(r[1] for r in dw);burned=sum(r[1] for r in ww)
   balance=lookup('destination',d['id'],'balanceOf(address)',account);value=lookup('destination',d['id'],'convertToAssets',account)
   end_shares=balance[0] if balance else None;end_assets=value[0] if value else None
   transfer_delta=sum(int(r['data'],16) for r in incoming)-sum(int(r['data'],16) for r in outgoing)
   outside_in=[r for r in incoming if addr(int(r['topics'][1],16)) not in c.ACCOUNTS+['0x'+'0'*40]];outside_out=[r for r in outgoing if addr(int(r['topics'][2],16)) not in c.ACCOUNTS+['0x'+'0'*40]]
   check(end_shares==transfer_delta,d['id']+' '+account+' transfer ledger matches T shares')
   direct_closed=not outside_in and not outside_out and end_shares==minted-burned
   net=(end_assets+withdraw_raw-deposit_raw) if end_assets is not None and direct_closed else None
   if dep or wd or end_shares or outside_in or outside_out:
    byaccount.append({'account':account,'deposit_count':len(dep),'withdrawal_count':len(wd),'deposited_assets':deposit_raw/10**d['decimals'],'withdrawn_cash_assets':withdraw_raw/10**d['decimals'],'ending_shares_raw':str(end_shares),'ending_claim_assets':end_assets/10**d['decimals'] if end_assets is not None else None,'mint_burn_share_reconciliation':end_shares==minted-burned,'transfer_share_reconciliation':end_shares==transfer_delta,'outside_share_receipts':len(outside_in),'outside_share_sends':len(outside_out),'net_accrued_claim_income_assets':net/10**d['decimals'] if net is not None else None,'attribution_closed':direct_closed,'first_deposit':event_meta(dep[0]) if dep else None,'last_event':event_meta(ordered(dep+wd+incoming+outgoing)[-1]),'scope':'Net claim growth after destination fees recognized in share value, not cash paid income or isolated organic lending interest.' if direct_closed else 'Income cannot be isolated from unvalued incoming/outgoing share transfers and collateral movements.'})
   for event,logs in [('deposit',dep),('withdraw',wd)]:
    for r in logs:
     w=c.words(r['data']);dest_events.append({'destination_id':d['id'],'vault':d['address'],'asset':d['asset'],'symbol':d['symbol'],'account':account,'event':event,'assets':w[0]/10**d['decimals'],'assets_raw':str(w[0]),'shares_raw':str(w[1]),'sender':addr(int(r['topics'][1],16)),'receiver':addr(int(r['topics'][2],16)) if event=='withdraw' else d['address'],**event_meta(r)})
  if byaccount:
   dests.append({**d,'accounts':byaccount,'total_deposited_assets':sum(r['deposited_assets'] for r in byaccount),'total_withdrawn_cash_assets':sum(r['withdrawn_cash_assets'] for r in byaccount),'ending_claim_assets':sum(r['ending_claim_assets'] or 0 for r in byaccount),'net_accrued_claim_income_assets':sum(r['net_accrued_claim_income_assets'] or 0 for r in byaccount) if all(r['attribution_closed'] for r in byaccount) else None,'status':'cash-flow and share ledger reconciled' if all(r['attribution_closed'] for r in byaccount) else 'unclosed share-transfer basis','organic_interest_vs_donations_split':None,'outer_fees_deducted_again':False})
 for d in dests:
  if d['net_accrued_claim_income_assets'] is not None:
   byaccount=[]
   for account in d['accounts']:
    ev=[r for r in dest_events if r['destination_id']==d['id'] and r['account']==account['account']]
    ending=lookup('destination',d['id'],'convertToAssets',account['account'])[0]
    basis=cash_basis(ev,0,0,ending,d['decimals']);account.update(basis);byaccount.append(basis)
   d['redeemed_share_gain_assets']=sum(r['redeemed_share_gain_assets'] for r in byaccount);d['remaining_claim_gain_assets']=sum(r['remaining_claim_gain_assets'] for r in byaccount)
 loans=[];loan_events=[]
 allborrow=ordered(groups['morpho_borrow']['logs']);allrepay=ordered(groups['morpho_repay']['logs']);liqs=groups['morpho_liquidate']['logs'];check(not liqs,'no tracked Morpho liquidation logs')
 mids=sorted({r['topics'][1] for r in allborrow+allrepay})
 for mid in mids:
  params=lookup('market',mid,'params');market=lookup('market',mid,'market');loan=addr(params[0]);coll=addr(params[1]);dec=lookup('asset',loan,'decimals()')[0];symbolrow=next(r for r in rows if r['kind']=='asset' and r['address']==loan and r['field']=='symbol()');sym=abi_string(symbolrow['response']['result']);rate=lookup('market',mid,'borrow_rate')[0];pending=accrue(market,rate,c.T);projected=market[2]+pending
  for account in c.ACCOUNTS:
   b=[r for r in allborrow if r['topics'][1]==mid and addr(int(r['topics'][2],16))==account];rep=[r for r in allrepay if r['topics'][1]==mid and addr(int(r['topics'][3],16))==account]
   pos=lookup('market',mid,'position',account)
   if not b and not rep and not pos[1]:continue
   bs=sum(c.words(r['data'])[2] for r in b);rs=sum(c.words(r['data'])[1] for r in rep);principal=sum(c.words(r['data'])[1] for r in b);paid=sum(c.words(r['data'])[0] for r in rep);ending=borrow_assets(pos[1],projected,market[3]);stored=borrow_assets(pos[1],market[2],market[3]);interest=ending+paid-principal
   check(bs-rs==pos[1],mid+' '+account+' borrow shares reconcile to T')
   check(interest>=0,mid+' '+account+' cumulative debt interest nonnegative')
   ledger={'id':mid+':'+account,'protocol':'Morpho Blue','market_id':mid,'account':account,'loan_asset':loan,'symbol':sym,'decimals':dec,'collateral_asset':coll,'mechanism':'E3 ETH debt loop' if sym=='WETH' else 'Dollar destination leverage against PRIME' if coll==c.DESTINATIONS[3]['address'] else 'E4 ETH-collateral dollar borrowing','borrow_count':len(b),'repay_count':len(rep),'borrowed_cash_assets':principal/10**dec,'repaid_cash_assets':paid/10**dec,'ending_stored_debt_assets':stored/10**dec,'ending_accrued_debt_assets':ending/10**dec,'pending_interest_since_market_update_assets':(ending-stored)/10**dec,'cumulative_accrued_borrowing_interest_assets':interest/10**dec,'ending_borrow_shares_raw':str(pos[1]),'event_net_borrow_shares_raw':str(bs-rs),'share_reconciled':bs-rs==pos[1],'first_borrow':event_meta(b[0]) if b else None,'last_borrow':event_meta(b[-1]) if b else None,'sourceURL':'https://app.morpho.org/ethereum/market/'+mid,'measurement':'Ending accrued debt + actual repayments - actual borrowed cash; all source events through T. Includes outstanding accrued interest, not just paid interest. No month-end APR interpolation.'}
   loans.append(ledger)
   for event,logs in [('borrow',b),('repay',rep)]:
    for r in logs:
     w=c.words(r['data']);loan_events.append({'ledger_id':ledger['id'],'market_id':mid,'account':account,'event':event,'asset':loan,'symbol':sym,'assets':w[1 if event=='borrow' else 0]/10**dec,'assets_raw':str(w[1 if event=='borrow' else 0]),'shares_raw':str(w[2 if event=='borrow' else 1]),'receiver':addr(int(r['topics'][3],16)) if event=='borrow' else c.MORPHO,**event_meta(r)})
 links=[];cross_links=[]
 receipts={r['transaction_hash']:r['response'].get('result') for r in flows.get('receipts',[])}
 for d in dest_events:
  matches=[r for r in loan_events if r['transaction_hash']==d['transaction_hash'] and r['asset']==d['asset'] and r['event']==('borrow' if d['event']=='deposit' else 'repay')]
  if not matches:continue
  receipt=receipts.get(d['transaction_hash']);transfers=[]
  if receipt:
   transfers=[r for r in receipt['logs'] if r['address'].lower()==d['asset'] and r['topics'][0]==c.TOPIC['Transfer']]
  financing=ordered_funding(receipt,d,matches) if d['event']=='deposit' else None
  directfunding=bool(financing and financing['covered_raw']>0)
  transfer_rows=[{'from':addr(int(r['topics'][1],16)),'to':addr(int(r['topics'][2],16)),'amount_raw':str(int(r['data'],16)),'log_index':int(r['logIndex'],16)} for r in transfers]
  dec=next(x['decimals'] for x in c.DESTINATIONS if x['id']==d['destination_id'])
  links.append({'destination_id':d['destination_id'],'destination_event':d['event'],'destination_event_log_index':d['log_index'],'transaction_hash':d['transaction_hash'],'sourceURL':d['sourceURL'],'symbol':d['symbol'],'destination_assets':d['assets'],'loan_cash_assets':sum(r['assets'] for r in matches),'cooccurring_nominal_assets':financing['covered_raw']/10**dec if financing else min(d['assets'],sum(r['assets'] for r in matches)),'loan_ledger_ids':sorted({r['ledger_id'] for r in matches}),'direct_morpho_to_controlled_to_destination_transfers':directfunding if d['event']=='deposit' else None,'receipt_ordered_cash_coverage':financing,'receipt_verified':bool(receipt and int(receipt.get('status','0x0'),16)==1),'token_transfers':transfer_rows,'scope':'Ordered same-transaction cash coverage from exact loan receipts through controlled hops to destination payment. Earlier deposits or consumed cash are excluded. Fungible balances do not identify unique dollars or allocate later profit to a borrowing source.'})
 for d in dest_events:
  if d['event']!='deposit':continue
  matches=[r for r in loan_events if r['event']=='borrow' and r['transaction_hash']==d['transaction_hash'] and r['asset']!=d['asset']]
  receipt=receipts.get(d['transaction_hash'])
  if not matches or not receipt:continue
  token_transfers=[]
  for log in receipt['logs']:
   if log['topics'][0]!=c.TOPIC['Transfer'] or log['address'].lower() not in {d['asset']}|{r['asset'] for r in matches}:continue
   token_transfers.append({'asset':log['address'].lower(),'from':addr(int(log['topics'][1],16)),'to':addr(int(log['topics'][2],16)),'amount_raw':str(int(log['data'],16)),'log_index':int(log['logIndex'],16)})
  loan_in=all(any(t['asset']==r['asset'] and t['from']==c.MORPHO and t['to']==r['receiver'] and t['amount_raw']==r['assets_raw'] for t in token_transfers) for r in matches)
  destination_in=any(t['asset']==d['asset'] and t['from'] in c.ACCOUNTS and t['to']==d['vault'] and t['amount_raw']==d['assets_raw'] for t in token_transfers)
  cross_links.append({'destination_id':d['destination_id'],'destination_symbol':d['symbol'],'destination_assets':d['assets'],'destination_assets_raw':d['assets_raw'],'transaction_hash':d['transaction_hash'],
                      'block':d['block'],'date':d['date'],'sourceURL':d['sourceURL'],'loans':[{'ledger_id':r['ledger_id'],'asset':r['asset'],'symbol':r['symbol'],'amount':r['assets'],'amount_raw':r['assets_raw'],'receiver':r['receiver']} for r in matches],
                      'loan_receipt_transfers_verified':loan_in,'controlled_destination_payment_verified':destination_in,'receipt_verified':int(receipt.get('status','0x0'),16)==1,'token_transfers':token_transfers,
                      'scope':'Different-token borrowing and destination deposit in the same successful transaction. Actual native loan receipt and destination payment are shown; no peg assumption, unique-dollar provenance or later-income assignment is made.'})
 window_output=None;reward_output={'status':'not analyzed','amounts':None}
 if (DATA/'carry_attribution_window_states.json').exists():
  window=read('carry_attribution_window_states');opening=window['records'];start=window['start_block']
  times.update({r['block']:int(r['response']['result']['timestamp'],16) for r in window['blocks'] if r['response'].get('result')})
  def win_lookup(kind,ident,field,account=None):
   row=next((r for r in opening if r['kind']==kind and r['id']==ident and r['field']==field and (account is None or r.get('account')==account)),None)
   return c.words(row['response'].get('result')) if row else None
  wdests=[];wloans=[]
  for d in dests:
   if d['net_accrued_claim_income_assets'] is None:continue
   account=c.MAIN;open_value=win_lookup('destination',d['id'],'convertToAssets',account)[0];open_shares=win_lookup('destination',d['id'],'balanceOf(address)',account)[0];end_value=lookup('destination',d['id'],'convertToAssets',account)[0];end_shares=lookup('destination',d['id'],'balanceOf(address)',account)[0]
   ev=[r for r in dest_events if r['destination_id']==d['id'] and r['account']==account and r['block']>start]
   cashin=sum(int(r['assets_raw']) for r in ev if r['event']=='deposit');cashout=sum(int(r['assets_raw']) for r in ev if r['event']=='withdraw');gain=end_value-open_value+cashout-cashin
   share_delta=sum(int(r['shares_raw'])*(1 if r['event']=='deposit' else -1) for r in ev)
   check(open_shares+share_delta==end_shares,d['id']+' common-window share reconciliation')
   row={'destination_id':d['id'],'symbol':d['symbol'],'account':account,'opening_claim_assets':open_value/10**d['decimals'],'deposits_assets':cashin/10**d['decimals'],'withdrawn_cash_assets':cashout/10**d['decimals'],'ending_claim_assets':end_value/10**d['decimals'],'net_accrued_claim_income_assets':gain/10**d['decimals'],'deposit_count':sum(r['event']=='deposit' for r in ev),'withdrawal_count':sum(r['event']=='withdraw' for r in ev),'sourceURL':'https://etherscan.io/address/'+d['address'],'scope':'Net destination book-claim growth after destination fees; rewards paid separately are outside this measure.'}
   row.update(cash_basis(ev,open_shares,open_value,end_value,d['decimals']));wdests.append(row)
  for l in loans:
   market=win_lookup('market',l['market_id'],'market');pos=win_lookup('market',l['market_id'],'position',l['account']);rate=win_lookup('market',l['market_id'],'borrow_rate')
   debt=borrow_assets(pos[1],market[2]+accrue(market,rate[0],times[start]),market[3]) if rate and market[4] else 0
   ev=[r for r in loan_events if r['ledger_id']==l['id'] and r['block']>start];borrowed=sum(int(r['assets_raw']) for r in ev if r['event']=='borrow');repaid=sum(int(r['assets_raw']) for r in ev if r['event']=='repay')
   endpos=lookup('market',l['market_id'],'position',l['account']);endmarket=lookup('market',l['market_id'],'market');endrate=lookup('market',l['market_id'],'borrow_rate')[0];ending=borrow_assets(endpos[1],endmarket[2]+accrue(endmarket,endrate,c.T),endmarket[3]);interest=ending-debt+repaid-borrowed
   share_delta=sum(int(r['shares_raw'])*(1 if r['event']=='borrow' else -1) for r in ev);check(pos[1]+share_delta==endpos[1],l['id']+' common-window debt share reconciliation')
   wloans.append({'ledger_id':l['id'],'market_id':l['market_id'],'account':l['account'],'symbol':l['symbol'],'mechanism':l['mechanism'],'opening_accrued_debt_assets':debt/10**l['decimals'],'borrowed_cash_assets':borrowed/10**l['decimals'],'repaid_cash_assets':repaid/10**l['decimals'],'ending_accrued_debt_assets':ending/10**l['decimals'],'accrued_borrowing_interest_assets':interest/10**l['decimals'],'borrow_count':sum(r['event']=='borrow' for r in ev),'repay_count':sum(r['event']=='repay' for r in ev),'sourceURL':l['sourceURL']})
  meta={}
  for token in sorted({r['address'] for r in window['reward_token_metadata']}):
   r={x['field']:x['response'].get('result') for x in window['reward_token_metadata'] if x['address']==token};meta[token]={'symbol':abi_string(r['symbol()']),'decimals':c.words(r['decimals()'])[0]}
  rg=next(g for g in flows['log_groups'] if g['key']=='merkl_cash_reward_transfers');payments=[]
  for log in ordered(rg['logs']):
   token=log['address'].lower();info=meta[token];payments.append({'asset':token,'symbol':info['symbol'],'recipient':addr(int(log['topics'][2],16)),'amount_raw':str(int(log['data'],16)),'amount':int(log['data'],16)/10**info['decimals'],'within_common_window':int(log['blockNumber'],16)>start,'distributor':flows['merkl_distributor'],**event_meta(log),'scope':'Actual cash transfer from Merkl; the token does not identify the sponsor, campaign or earning period.'})
  totals=[]
  for token in meta:
   allpay=[r for r in payments if r['asset']==token];within=[r for r in allpay if r['within_common_window']];totals.append({'asset':token,'symbol':meta[token]['symbol'],'lifetime_payment_count':len(allpay),'lifetime_cash_amount':sum(r['amount'] for r in allpay),'common_window_payment_count':len(within),'common_window_cash_amount':sum(r['amount'] for r in within),'attributed_to_specific_destination':False})
  reward_output={'status':'Actual historical cash transfers measured; campaign and earning-period allocation unresolved','payments':payments,'totals':totals,'scope':flows['merkl_scope'],'campaign_earning_periods':None,'redirected_beneficiaries_reviewed':False,'sourceURL':flows['merkl_address_source']}
  window_output={'start_block':start,'start_timestamp':times[start],'start_date':date(times[start]),'end_block':c.BLOCK,'end_timestamp':c.T,'end_date':date(c.T),'days':(c.T-times[start])/86400,'start_convention':window['start_convention'],'destination_ledgers':wdests,'borrowing_ledgers':wloans,'cash_reward_totals':totals,'funding_links':[r for r in links if receipts.get(r['transaction_hash']) and int(receipts[r['transaction_hash']]['blockNumber'],16)>start],'cross_currency_funding_links':[r for r in cross_links if r['block']>start],'complete_sleeve_net_income':None,'scope':'Identical historical start/end for actual claim growth, debt accrual and paid rewards. Components remain separate where funding, earlier destinations and campaign assignments are unresolved.'}
 fees=read('presentation_analysis')['fees'];credit=read('carry_credit_lookthrough');balance=read('etherfi_partial_balance_sheet');pc=read('product_chapters')
 output={'schema_version':1,'snapshot_timestamp':c.T,'snapshot_date':date(c.T),'ethereum_block':c.BLOCK,'capture_start_block':c.START,'scope':'Actual contract cash-flow and accrued-claim ledgers for four controlled Liquid ETH accounts and four examined destinations. These are leg measures, not complete whole-product P&L.','destination_ledgers':dests,'destination_events':dest_events,'borrowing_ledgers':loans,'borrowing_events':loan_events,'funding_links':links,'common_window':window_output,'cash_reward_review':reward_output,'own_credit_overlap':{'status':'T notional measured; historical own-interest recycling not yet isolated','snapshot_rows':credit,'historical_income':None,'scope':'Do not apply current ownership fractions backward to interest.'},'fees':{'status':'Ethereum Accountant claim payments separately measured; no allocation to carry legs','source_fee_summary':fees,'source':'data/eth/presentation_analysis.json'},'whole_product_boundary':{'T_book_NAV_USD':balance['published_book_nav_usd'],'T_partial_reconstruction_USD':balance['partial_reconstruction_usd'],'T_unresolved_residual_USD':balance['unresolved_residual_usd'],'historical_strategy_income_unattributed':True,'scope':'Snapshot residual is an asset-reconciliation gap, not unexplained historical profit or an established deficit.'},'top5_coverage':[{'product':p['name'],'whole_book_ETH':p['capitalETH'],'organic_carry_income_closed':False,'status':'Actual destination/debt ledgers available; whole portfolio and historical income source split remain incomplete' if p['id']=='liquid' else 'Flat native weETH book; ETH change is issuer conversion, private payouts unverified' if p['id']=='concrete' else 'Nested claim or active route known; realized strategy cash-flow attribution not reconstructed'} for p in pc['products']],'sources':[proof('data/eth/'+n+'.json') for n in ['carry_attribution_rpc','carry_attribution_states','carry_credit_lookthrough','presentation_analysis','etherfi_partial_balance_sheet','product_chapters']]+([proof('data/eth/carry_attribution_flows.json')] if flows else [])+([proof('data/eth/carry_attribution_window_states.json')] if window_output else []),'raw_manifest':str((c.RAW/'requests.jsonl').relative_to(ROOT)),'verification':{'checks':tests,'passed':sum(r['passed'] for r in tests),'failed':sum(not r['passed'] for r in tests)},'limitations':['Net destination claim growth can include recognized lending income, donations or other changes in its assets; external rewards paid to the holder are separate.','Cash withdrawals contain returned principal and income together; the entire withdrawal is not yield.','Loan repayments contain principal and interest; the interest residual includes unpaid accrued interest still owed at T.','Funding links show transactions and controlled hops, not a complete fungible-dollar provenance ledger or allocation of whole-product income.','No current allocation or reward rate is applied retroactively.','Aave/Spark dollar borrowing and earlier destination vaults are outside these first ledgers.']}
 (DATA/'carry_attribution_ledger.json').write_text(json.dumps(output,indent=2,allow_nan=False))
 output['cross_currency_funding_links']=cross_links
 output['whole_product_boundary']['measurement_scope']='Original published partial reconstruction at T, before the separate backing and exit closure. This is not the latest comprehensive reconciliation.'
 next(r for r in output['destination_ledgers'] if r['id']=='prime')['ending_claim_scope']='wYLDS claim corresponding to PRIME shares in the four controlled custody balances. Shares posted as Morpho collateral are not part of these wallet balances; transferred-share acquisition basis is unclosed.'
 output['sources']+=[proof('data/eth/carry_attribution_closure_proof.json')]
 (DATA/'carry_attribution_ledger.json').write_text(json.dumps(output,indent=2,allow_nan=False))
 for name,table in [('destination_events',dest_events),('borrowing_events',loan_events),('funding_links',links),('cross_currency_funding_links',cross_links)]:
  if table:
   columns=list(dict.fromkeys(k for r in table for k in r))
   with (DATA/('carry_attribution_'+name+'.csv')).open('w') as f:
    w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows({k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in table)
 print(json.dumps({'destinations':[{k:r[k] for k in ['id','total_deposited_assets','total_withdrawn_cash_assets','ending_claim_assets','net_accrued_claim_income_assets','status']} for r in dests],'loans':[{k:r[k] for k in ['symbol','mechanism','account','borrowed_cash_assets','repaid_cash_assets','ending_accrued_debt_assets','cumulative_accrued_borrowing_interest_assets','share_reconciled']} for r in loans],'funding_links':len(links),'verification':output['verification']['failed']},indent=2))

if __name__=='__main__':build()
