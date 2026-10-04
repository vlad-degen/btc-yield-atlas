"""Bounded borrower identity and proceeds captures, exact T plus dated discovery."""
from __future__ import annotations
import json,hashlib,time,sys,concurrent.futures
from pathlib import Path
import carry_economics_collect as c
from carry_economics_collect import call,enc_addr,words
from keccak_lib import keccak
ROOT=c.ROOT;DATA=ROOT/'data/eth';RAW=ROOT/'raw/eth/funding-borrower-deep-2026-10-04';c.RAW=RAW;T=c.T;BLOCK=26108081
ORIGINAL=c.capture
def capture(key,url,payload=None):
 manifest=RAW/'requests.jsonl'
 if manifest.exists():
  for line in reversed(manifest.read_text().splitlines()):
   r=json.loads(line)
   if r.get('key')==key and r.get('url')==url and r.get('request')==payload and r.get('path'):
    p=ROOT/r['path'];return json.loads(p.read_text()) if p.suffix=='.json' else p.read_text()
 return ORIGINAL(key,url,payload)
def rpc(req,key):
 payload=[{'jsonrpc':'2.0','id':i+1,'method':m,'params':p} for i,(m,p) in enumerate(req)];out=[]
 for start in range(0,len(payload),4):
  r=capture(key+'_batch'+str(start//4),'https://eth-mainnet.public.blastapi.io',payload[start:start+4]);out.extend(r if isinstance(r,list) else []);time.sleep(.25)
 return {r['id']:r for r in out}
def read(n):return json.loads((DATA/(n+'.json')).read_text())
def init():
 x=read('funding_atlas_chapter');assert x['summary']['successful_borrower_calls']==15704
 RAW.mkdir(parents=True,exist_ok=True);body=(DATA/'funding_atlas_chapter.json').read_bytes();digest=hashlib.sha256(body).hexdigest();f=RAW/('input_funding_atlas-'+digest[:16]+'.json');f.write_bytes(body)
 top=x['borrowers'][:10];addresses=sorted({r['address'].lower() for r in top});req=[];labels=[]
 for a in addresses:
  labels.append((a,'code_T'));req.append(('eth_getCode',[a,hex(BLOCK)]))
  for sig in ['owner()','getOwners()','getThreshold()','masterCopy()']:labels.append((a,sig));req.append(call(a,sig,'',hex(BLOCK)))
 rr=rpc(req,'top10_identity_T');named={}
 for i,(a,k) in enumerate(labels):named.setdefault(a,{})[k]=rr.get(i+1,{})
 sources=[]
 for a in addresses:
  u='https://eth.blockscout.com/api/v2/addresses/'+a;sources.append({'key':'address_'+a,'url':u,'response':capture('address_'+a,u)})
  if named[a]['code_T'].get('result') not in [None,'0x']:
   u='https://eth.blockscout.com/api/v2/smart-contracts/'+a;sources.append({'key':'source_'+a,'url':u,'response':capture('source_'+a,u)})
  time.sleep(.15)
 targets=['0xd848f54280f8fe8661b796e3bb8d8922c87af452','0x99926ab8e1b589500ae87977632f13cf7f70f242'];pools={v['id']:v['pool'] for v in read('funding_atlas_snapshot')['venues']};topic='0x'+keccak(b'Borrow(address,address,address,uint256,uint8,uint256,uint16)').hex();logs=[]
 for a in targets:
  for venue in ['aave-ethereum','spark-ethereum']:
   q={'address':pools[venue],'fromBlock':hex(BLOCK-1000000),'toBlock':hex(BLOCK),'topics':[topic,None,'0x'+enc_addr(a)]};rr=rpc([('eth_getLogs',[q])],'borrow_logs_'+a+'_'+venue);logs.append({'address':a,'venue':venue,'pool':pools[venue],'from_block':BLOCK-1000000,'to_block':BLOCK,'response':rr.get(1,{})});print(a,venue,'logs',len(rr.get(1,{}).get('result',[])),flush=True)
  for kind in ['transactions','token-transfers']:
   u='https://eth.blockscout.com/api/v2/addresses/'+a+'/'+kind;sources.append({'key':kind+'_'+a,'url':u,'response':capture(kind+'_'+a,u)})
 (DATA/'funding_borrower_deep_capture.json').write_text(json.dumps({'target_timestamp':T,'block':BLOCK,'input':{'path':str(f.relative_to(ROOT)),'sha256':digest},'top10':top,'identities':named,'sources':sources,'borrow_logs':logs,'targets':targets},indent=2));print('Identity and proceeds discovery captured',flush=True)
def receipts():
 x=read('funding_borrower_deep_capture');hashes=set();samples=[]
 for row in x['borrow_logs']:
  logs=row['response'].get('result')
  if not isinstance(logs,list):continue
  # Latest two dollar borrows per venue/account, excluding ETH debt.
  loans={r['address'].lower():r['symbol'] for r in read('funding_atlas_chapter')['reserves'] if r['venue_id']==row['venue']}
  relevant=[r for r in logs if r['topics'][1][-40:].lower() in [a[2:] for a in loans]]
  selected=sorted(relevant,key=lambda r:(int(r['blockNumber'],16),int(r['logIndex'],16)))[-2:]
  for l in selected:samples.append({'address':row['address'],'venue':row['venue'],'log':l});hashes.add(l['transactionHash'])
 if not hashes:
  # Broad log queries have a ten-block limit on this public endpoint. Use
  # indexed debt-mint discovery, then verify Borrow cash principal from the
  # complete primary transaction receipt. Debt mint can include old interest.
  reserves=read('funding_atlas_chapter')['reserves'];debtmap={r['variable_debt_token'].lower():r for r in reserves if r['chain']=='ethereum'}
  for a in x['targets']:
   page=next(r['response'] for r in x['sources'] if r['key']=='token-transfers_'+a);candidates={}
   for t in page.get('items',[]):
    addr=t['token']['address_hash'].lower();r=debtmap.get(addr)
    if r and t['from']['hash'].lower()=='0x'+'0'*40 and t['to']['hash'].lower()==a and t['block_number']<=BLOCK:candidates.setdefault(r['venue_id'],[]).append((t,r))
   for venue,items in candidates.items():
    seen=set()
    for t,r in sorted(items,key=lambda pair:(pair[0]['block_number'],pair[0]['log_index']),reverse=True):
     h=t['transaction_hash']
     if h in seen:continue
     seen.add(h);hashes.add(h);samples.append({'address':a,'venue':venue,'discovery':'Indexed debt-token mint; cash principal must be taken from Borrow and underlying transfer receipt.','indexed_mint':t,'loan_asset':r['address'],'loan_symbol':r['symbol']})
     if len(seen)>=2:break
 req=[];labels=[]
 for h in sorted(hashes):
  for m in ['eth_getTransactionReceipt','eth_getTransactionByHash']:labels.append((h,m));req.append((m,[h]))
 rr=rpc(req,'representative_borrow_receipts');named={}
 for i,(h,k) in enumerate(labels):named.setdefault(h,{})[k]=rr.get(i+1,{})
 sources=[]
 for h in sorted(hashes):
  for kind in ['', '/token-transfers','/internal-transactions']:
   u='https://eth.blockscout.com/api/v2/transactions/'+h+kind;k='receipt_index_'+h+kind.replace('/','_');sources.append({'key':k,'url':u,'response':capture(k,u)})
 # Follow the actual T owner addresses, without equating ownership with a
 # named entity. Latest indexed pages are filtered to pre-T downstream flows.
 owners=set()
 for a in x['targets']:
  o=words(x['identities'][a].get('owner()',{}).get('result'))
  if not o:
   o=words(x['identities'][a].get('getOwners()',{}).get('result'));o=o[2:] if o else []
  for v in o:owners.add('0x'+format(v,'040x'))
 for a in sorted(owners):
  for kind in ['','/transactions','/token-transfers']:
   u='https://eth.blockscout.com/api/v2/addresses/'+a+kind;k='owner_'+a+kind.replace('/','_');sources.append({'key':k,'url':u,'response':capture(k,u)})
   time.sleep(.2)
 (DATA/'funding_borrower_deep_receipts.json').write_text(json.dumps({'target_timestamp':T,'samples':samples,'transactions':named,'sources':sources},indent=2));print('Sample borrow transaction receipts',len(hashes),flush=True)
def downstream():
 x=read('funding_borrower_deep_capture');rc=read('funding_borrower_deep_receipts');targets={};owners={};hashes=set();sources=[]
 for a in x['targets']:
  w=words(x['identities'][a].get('owner()',{}).get('result')) or words(x['identities'][a].get('getOwners()',{}).get('result'))[2:];owner='0x'+format(w[0],'040x');owners[a]=owner
  tx=next(r['response'] for r in rc['sources'] if r['key']=='owner_'+owner+'_transactions')
  for t in tx['items']:
   if t['from']['hash'].lower()!=owner or t['block_number']>BLOCK:continue
   if t['method']=='transfer' and t['to']['hash'].lower() in ['0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','0xdac17f958d2ee523a2206206994597c13d831ec7','0xdc035d45d973e3ec169d2276ddab16f1e407384f']:
    d={p['name']:p['value'] for p in t['decoded_input']['parameters']};to=d.get('to') or d.get('_to');amount=d.get('value') or d.get('_value');targets[t['hash']]={'account':a,'owner':owner,'recipient':to.lower(),'token':t['to']['hash'].lower(),'raw_amount':amount,'block':t['block_number'],'timestamp':t['timestamp']}
    if t['timestamp'][:10] in ['2026-09-30','2026-09-26','2026-09-11']:hashes.add(t['hash'])
 # Primary source shows direct settlement DAI paid to DSProxy and then burned
 # in the Maker recipe, but does not prove an external exchange's business.
 dsowner=owners[x['targets'][0]];page=next(r['response'] for r in rc['sources'] if r['key']=='owner_'+dsowner+'_token-transfers')
 for t in page['items']:
  if t['timestamp'][:10]=='2026-09-30' and t['token']['address_hash'].lower()=='0x6b175474e89094c44da98b954eedeac495271d0f' and int(t['total'].get('value') or 0)>10**24:hashes.add(t['transaction_hash'])
 req=[];labels=[]
 for h in sorted(hashes):
  for m in ['eth_getTransactionReceipt','eth_getTransactionByHash']:labels.append((h,m));req.append((m,[h]))
 rr=rpc(req,'downstream_receipts');named={}
 for i,(h,k) in enumerate(labels):named.setdefault(h,{})[k]=rr.get(i+1,{})
 recipients=sorted({r['recipient'] for r in targets.values()})
 for a in recipients:
  u='https://eth.blockscout.com/api/v2/addresses/'+a;sources.append({'key':'recipient_'+a,'url':u,'response':capture('recipient_'+a,u)})
 for h in sorted(hashes):
  for suffix in ['', '/token-transfers','/internal-transactions']:
   u='https://eth.blockscout.com/api/v2/transactions/'+h+suffix;k='downstream_index_'+h+suffix.replace('/','_');sources.append({'key':k,'url':u,'response':capture(k,u)})
 # Top ten unique borrowers contain two additional addresses beyond the top
 # ten venue rows. Their debt measures are reused without ownership guesses.
 frozen=json.loads((ROOT/x['input']['path']).read_text());groups={}
 for r in frozen['borrowers']:
  key=(r['chain'],r['address'].lower());groups.setdefault(key,0);groups[key]+=r['dollar_debt_USD']
 extra=[a for (chain,a),n in sorted(groups.items(),key=lambda kv:kv[1],reverse=True)[:10] if chain=='ethereum' and a not in x['identities']]
 req=[];labels=[]
 for a in extra:
  labels.append((a,'code_T'));req.append(('eth_getCode',[a,hex(BLOCK)]))
  for sig in ['owner()','getOwners()','getThreshold()','masterCopy()']:labels.append((a,sig));req.append(call(a,sig,'',hex(BLOCK)))
  u='https://eth.blockscout.com/api/v2/addresses/'+a;sources.append({'key':'extra_address_'+a,'url':u,'response':capture('extra_address_'+a,u)})
 stable=[('USDC','0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',6),('USDT','0xdac17f958d2ee523a2206206994597c13d831ec7',6),('USDS','0xdc035d45d973e3ec169d2276ddab16f1e407384f',18),('DAI','0x6b175474e89094c44da98b954eedeac495271d0f',18)]
 balance_labels=[]
 for owner in sorted(owners.values()):
  labels.append((owner,'code_T'));req.append(('eth_getCode',[owner,hex(BLOCK)]))
  sampleblocks=sorted({int(rc['transactions'][t['indexed_mint']['transaction_hash']]['eth_getTransactionReceipt']['result']['blockNumber'],16)-1 for t in rc['samples'] if owners[t['address']]==owner and t['indexed_mint']['timestamp'][:10] in ['2026-09-30','2026-09-26']})
  for b in [*sampleblocks,BLOCK]:
   for symbol,token,dec in stable:
    labels.append((owner,'balance:'+symbol+':'+str(b)));balance_labels.append({'owner':owner,'symbol':symbol,'token':token,'decimals':dec,'block':b});req.append(call(token,'balanceOf(address)',enc_addr(owner),hex(b)))
 byid=rpc(req,'extra_identity_owner_cash_T');state={}
 for i,(a,k) in enumerate(labels):state.setdefault(a,{})[k]=byid.get(i+1,{})
 (DATA/'funding_borrower_deep_downstream.json').write_text(json.dumps({'target_timestamp':T,'owners':owners,'indexed_owner_outgoing_transfers':list(targets.values()),'transactions':named,'sources':sources,'state':state,'balance_labels':balance_labels},indent=2));print('Downstream receipts',len(hashes),'recipient identities',len(recipients),'cash probes',len(balance_labels),flush=True)
def finish():
 x=read('funding_borrower_deep_downstream');rc=read('funding_borrower_deep_receipts');sources=[];req=[];labels=[]
 addresses=['0xfe02a32cbe0cb9ad9a945576a5bb53a3c123a3a3','0xa0d089c10b986e8778873bef44d747d64241bf59','0xe68aed979af6f85516ff485d098804c0f9ed9a5b','0x63c0c19a282a1b52b07dd5a65b58948a07dae32b']
 for a in addresses:
  labels.append(('code',a));req.append(('eth_getCode',[a,hex(BLOCK)]))
  for suffix in ['addresses/','smart-contracts/']:
   u='https://eth.blockscout.com/api/v2/'+suffix+a;k='final_'+suffix.replace('/','_')+a;sources.append({'key':k,'url':u,'response':capture(k,u)});time.sleep(.15)
 blocks=sorted({r['eth_getTransactionReceipt']['result']['blockNumber'] for r in [*rc['transactions'].values(),*x['transactions'].values()]})
 for b in blocks:labels.append(('block',b));req.append(('eth_getBlockByNumber',[b,False]))
 rr=rpc(req,'final_code_and_dates');state={}
 for i,(k,v) in enumerate(labels):state.setdefault(k,{})[v]=rr.get(i+1,{})
 owner=x['owners']['0x99926ab8e1b589500ae87977632f13cf7f70f242'];u='https://eth.blockscout.com/api/v2/addresses/'+owner+'/token-transfers?type=ERC-20&token=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48';sources.append({'key':'owner_canonical_USDC_page','url':u,'response':capture('owner_canonical_USDC_page',u)})
 (DATA/'funding_borrower_deep_final_captures.json').write_text(json.dumps({'target_timestamp':T,'state':state,'sources':sources},indent=2));print('Final primary source and timestamp probes captured',flush=True)
def settlements():
 x=read('funding_borrower_deep_final_captures');sources=[];owner='0x54d250405d22e858d125ce2c1affc7d73afe6029';settlement='0x9008d19f58aabd9ed0d60971565aa8510560ab41';page=next(r['response'] for r in x['sources'] if r['key']=='owner_canonical_USDC_page');selected=[t for t in page['items'] if t['timestamp'].startswith('2026-09-26') and t['timestamp']>'2026-09-26T01:05:59' and t['token']['address_hash'].lower()=='0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' and t['from']['hash'].lower()==owner and t['to']['hash'].lower()==settlement and int(t['total'].get('value') or 0)>0];hashes=sorted({t['transaction_hash'] for t in selected});req=[];labels=[]
 for h in hashes:
  for m in ['eth_getTransactionReceipt','eth_getTransactionByHash']:labels.append((h,m));req.append((m,[h]))
 rr=rpc(req,'cow_settlement_receipts');named={}
 for i,(h,k) in enumerate(labels):named.setdefault(h,{})[k]=rr.get(i+1,{})
 for suffix in ['addresses/','smart-contracts/']:
  u='https://eth.blockscout.com/api/v2/'+suffix+settlement;k='cow_'+suffix.replace('/','_');sources.append({'key':k,'url':u,'response':capture(k,u)})
 req=[];labels=[]
 for b in sorted({r['eth_getTransactionReceipt']['result']['blockNumber'] for r in named.values()}):labels.append(('block',b));req.append(('eth_getBlockByNumber',[b,False]))
 labels.append(('code',settlement));req.append(('eth_getCode',[settlement,hex(BLOCK)]))
 for b in [26058232]:
  for token,symbol in [('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','USDC'),('0xdac17f958d2ee523a2206206994597c13d831ec7','USDT')]:labels.append(('balance',symbol+':'+str(b)));req.append(call(token,'balanceOf(address)',enc_addr(owner),hex(b)))
 rr=rpc(req,'cow_dates_code_opening');state={}
 for i,(k,v) in enumerate(labels):state.setdefault(k,{})[v]=rr.get(i+1,{})
 (DATA/'funding_borrower_deep_settlements.json').write_text(json.dumps({'target_timestamp':T,'owner':owner,'settlement':settlement,'indexed_selected':selected,'transactions':named,'sources':sources,'state':state},indent=2));print('CoW settlements captured',len(hashes),flush=True)
if __name__=='__main__':settlements() if '--settlements' in sys.argv else finish() if '--finish' in sys.argv else downstream() if '--downstream' in sys.argv else receipts() if '--receipts' in sys.argv else init()
