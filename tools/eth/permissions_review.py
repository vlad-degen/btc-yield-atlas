"""Read-only historical permission audit; separate from the frozen source collection."""
import datetime as dt,hashlib,json,time,urllib.request
from pathlib import Path
from urllib.parse import urlencode
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_addr
T=1790985599;BLOCK=26108081
RAW=ROOT/'raw/eth/presentation-review';RAW.mkdir(parents=True,exist_ok=True)
AUTH='0x485bde66bb668a51f2372e34e45b1c6226798122';ACC='0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198';VAULT='0xf0bb20865277abd641a307ece5ee04e79073416c'
def fetch(key,url,body=None):
 payload=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request(url,data=payload,headers={'User-Agent':'ETH-Yield-Research/1.0','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=25) as r:content=r.read()
 h=hashlib.sha256(content).hexdigest();path=RAW/f'{key}-{h[:16]}.json';path.write_bytes(content)
 rec={'key':key,'url':url,'retrieved_at':dt.datetime.now(dt.timezone.utc).isoformat(),'path':str(path.relative_to(ROOT)),'sha256':h,'requested_block':BLOCK if body is not None else None,'request':body}
 with (RAW/'requests.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
 return json.loads(content)
def run():
 url=f'https://eth.blockscout.com/api/v2/addresses/{AUTH}/logs';items=[];page={};pages=0
 for i in range(60):
  page=fetch(f'authority_logs_{i+1}',url);items.extend(page.get('items',[]));pages+=1
  if not page.get('next_page_params'):break
  url=f'https://eth.blockscout.com/api/v2/addresses/{AUTH}/logs?'+urlencode(page['next_page_params'])
  time.sleep(.15)
 complete=not page.get('next_page_params')
 users=set();eligible=[]
 for row in items:
  if row['block_number']>BLOCK:continue
  decoded=row.get('decoded') or {};event=decoded.get('method_call','').split('(')[0]
  if event=='UserRoleUpdated':
   user=next(p['value'] for p in decoded['parameters'] if p['name']=='user').lower();users.add(user);eligible.append(row)
 calls=[];labels=[]
 for user in sorted(users):
  labels.append({'kind':'user_roles','user':user});calls.append({'jsonrpc':'2.0','id':len(calls)+1,'method':'eth_call','params':[{'to':AUTH,'data':'0x'+sel('getUserRoles(address)')+enc_addr(user)},hex(BLOCK)]})
 functions=[(VAULT,'manage(address,bytes,uint256)'),(VAULT,'enter(address,address,uint256,address,uint256)'),(VAULT,'exit(address,address,uint256,address,uint256)'),(ACC,'updateExchangeRate(uint96)'),(ACC,'updateManagementFee(uint16)'),(ACC,'pause()'),(ACC,'unpause()'),(ACC,'setRateProviderData(address,bool,address)')]
 for target,sig in functions:
  sigword=sel(sig).ljust(64,'0');args=enc_addr(target)+sigword
  for getter in ['getRolesWithCapability(address,bytes4)','isCapabilityPublic(address,bytes4)']:
   labels.append({'kind':'capability','target':target,'function':sig,'getter':getter});calls.append({'jsonrpc':'2.0','id':len(calls)+1,'method':'eth_call','params':[{'to':AUTH,'data':'0x'+sel(getter)+args},hex(BLOCK)]})
 responses=[]
 for i in range(0,len(calls),25):responses.extend(fetch(f'permissions_T_batch_{i//25}','https://eth-mainnet.public.blastapi.io',calls[i:i+25]))
 rows=[];cap=[]
 for response in responses:
  label=labels[response['id']-1]
  if not response.get('result'):label['error']=response.get('error');cap.append(label);continue
  value=int(response['result'],16)
  if label['kind']=='user_roles':rows.append({**label,'role_mask':str(value),'roles':[i for i in range(256) if value&(1<<i)]})
  else:cap.append({**label,'value':str(value),'roles':[i for i in range(256) if value&(1<<i)] if 'getRoles' in label['getter'] else None})
 out={'target_timestamp':T,'block':BLOCK,'authority':AUTH,'logs_paginated_to_creation':complete,'pages':pages,'role_events_at_or_before_T':len(eligible),'users_seen_in_role_events':len(users),'role_holders_T':rows,'capabilities_T':cap,'labels':labels,'responses':responses,'limits':['Address roles are measured at T; beneficial identities are not inferred.','Authority owner can change roles; emergency calls need not use the owner timelock.','Capabilities tested are selected functions, not every selector or strategy Merkle root.']}
 (ROOT/'data/eth/permissions_review_T.json').write_text(json.dumps(out,indent=2));print(json.dumps({'pages':pages,'complete':complete,'role_event_users':len(users),'active_users':sum(bool(r['roles']) for r in rows),'capability_reads':len(cap),'rpc_errors':sum('error' in r for r in responses)}))
if __name__=='__main__':run()
