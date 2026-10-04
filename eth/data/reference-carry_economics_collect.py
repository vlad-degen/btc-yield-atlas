"""Capture additional read-only carry calls at the existing ETH research block.

All additions use a separate raw directory. Original captures are never written.
"""
from __future__ import annotations
import concurrent.futures, datetime as dt, hashlib, json, re, sys, threading, urllib.request
from pathlib import Path
from collect import ROOT, T, RPCS
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel, enc_addr, enc_uint

RAW=ROOT/'raw/eth/carry-economics-2026-10-04';LOCK=threading.Lock()
MORPHO='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
MORPHO_BY_CHAIN={'ethereum':MORPHO,'base':MORPHO,'arbitrum':'0x6c247b1f6182318877311737bac0844baa518f5e'}
V='0xf0bb20865277abd641a307ece5ee04e79073416c';LOAN='0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3'
NAMES={1:'ethereum',8453:'base',42161:'arbitrum',10:'optimism'}

def capture(key,url,payload=None):
 RAW.mkdir(parents=True,exist_ok=True);record={'key':key,'url':url,'retrieved_at':dt.datetime.now(dt.timezone.utc).isoformat(),'target_timestamp':T,'method':'POST' if payload is not None else 'GET'}
 if payload is not None:record['request']=payload
 try:
  request=urllib.request.Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json','User-Agent':'ETH-Yield-Research/1.0'})
  with urllib.request.urlopen(request,timeout=40) as response:
   body=response.read();record.update(status=response.status,source_HTTP_date=response.headers.get('Date'))
  digest=hashlib.sha256(body).hexdigest();path=RAW/(key+'-'+digest[:16]+('.json' if body.lstrip().startswith((b'{',b'[')) else '.txt'))
  if not path.exists():path.write_bytes(body)
  record.update(path=str(path.relative_to(ROOT)),sha256=digest,bytes=len(body));result=json.loads(body) if path.suffix=='.json' else body.decode()
 except Exception as error:
  record.update(error=type(error).__name__+': '+str(error)[:240]);result=None
 with LOCK:
  with (RAW/'requests.jsonl').open('a') as output:output.write(json.dumps(record)+'\n')
 return result

def rpc(chain,requests,key):
 payload=[{'jsonrpc':'2.0','id':i+1,'method':method,'params':params} for i,(method,params) in enumerate(requests)]
 providers=(['https://arbitrum-one.public.blastapi.io','https://arbitrum-one-rpc.publicnode.com'] if chain=='arbitrum' else ['https://base-mainnet.public.blastapi.io','https://base-rpc.publicnode.com'] if chain=='base' else [])+RPCS[chain]
 for provider,url in enumerate(providers):
  result=[];size=25 if chain=='ethereum' else 4
  for start in range(0,len(payload),size):
   response=capture(key+'_provider'+str(provider)+'_batch'+str(start//size),url,payload[start:start+size])
   if not isinstance(response,list):break
   result.extend(response)
  if len(result)==len(payload) and sum(r.get('result') not in [None,'0x'] for r in result)>len(result)//2:return sorted(result,key=lambda r:r['id'])
 return result

def words(hexdata):return [int(hexdata[i:i+64],16) for i in range(2,len(hexdata),64)] if hexdata and hexdata!='0x' else None
def call(address,signature,args,tag):return ('eth_call',[{'to':address,'data':'0x'+sel(signature)+args},tag])

def run():
 snapshot=json.loads((ROOT/'data/eth/snapshot_manifest.json').read_text());blocks={r['chain']:r for r in snapshot['chains']};screen=json.loads((ROOT/'data/eth/morpho_borrower_screen.json').read_text());rows=[]
 for row in screen:
  m=row['market'];items=(row.get('positions') or {}).get('items',[])
  if not items or m['loanAsset']['symbol']=='WETH':continue
  chain=NAMES[items[0]['market']['chain']['id']];rows.append({'id':m['marketId'],'chain':chain,'discovery':m})
 collected=[]
 for chain in sorted({row['chain'] for row in rows}):
  selected=[row for row in rows if row['chain']==chain];tag=hex(blocks[chain]['block']);requests=[];labels=[];morpho=MORPHO_BY_CHAIN[chain]
  for row in selected:
   for signature,args,name in [('idToMarketParams(bytes32)',row['id'][2:],'params'),('market(bytes32)',row['id'][2:],'market'),('position(bytes32,address)',row['id'][2:]+enc_addr(V),'main_position'),('position(bytes32,address)',row['id'][2:]+enc_addr(LOAN),'loan_manager_position')]:labels.append({'market_id':row['id'],'field':name});requests.append(call(morpho,signature,args,tag))
  response=rpc(chain,requests,'morpho_'+chain+'_markets_T');byid={r['id']:r for r in response};named={}
  for i,label in enumerate(labels):named.setdefault(label['market_id'],{})[label['field']]=byid.get(i+1,{})
  follow=[];followlabels=[]
  for row in selected:
   row.update(block=blocks[chain]['block'],block_hash=blocks[chain]['block_hash'],block_timestamp=blocks[chain]['block_timestamp'],morpho=morpho,raw=named[row['id']]);params=words(row['raw']['params'].get('result'));market=words(row['raw']['market'].get('result'))
   if not params or not market:continue
   oracle='0x'+format(params[2],'040x');irm='0x'+format(params[3],'040x');encoded=''.join(enc_uint(x) for x in params+market)
   for target,signature,args,name in [(oracle,'price()','','oracle_price'),(irm,'rateAtTarget(bytes32)',row['id'][2:],'rate_at_target'),(irm,'MORPHO()','','irm_morpho'),(irm,'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',encoded,'borrow_rate_view')]:followlabels.append({'market_id':row['id'],'field':name});follow.append(call(target,signature,args,tag))
   for role,index in [('loan_asset',0),('collateral_asset',1)]:
    token='0x'+format(params[index],'040x')
    for signature in ['symbol()','decimals()']:followlabels.append({'market_id':row['id'],'field':role+'_'+signature});follow.append(call(token,signature,'',tag))
  followresponse=rpc(chain,follow,'morpho_'+chain+'_rates_T');followbyid={r['id']:r for r in followresponse}
  for i,label in enumerate(followlabels):named[label['market_id']][label['field']]=followbyid.get(i+1,{})
  collected.extend(selected)
  print(chain,len(selected),'fixed-block markets captured',flush=True)
 # Contract source identities are captured separately; the T addresses come from
 # fixed-block market parameters rather than an inferred generic model.
 irms=sorted({('0x'+format(words(row['raw']['params'].get('result'))[3],'040x'),row['chain']) for row in collected if words(row['raw']['params'].get('result'))})
 urls={'ethereum':'https://eth.blockscout.com','base':'https://base.blockscout.com','arbitrum':'https://arbitrum.blockscout.com','optimism':'https://optimism.blockscout.com'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda item:capture('irm_source_'+item[1]+'_'+item[0],urls[item[1]]+'/api/v2/smart-contracts/'+item[0]),irms))
 (ROOT/'data/eth/carry_economics_primary_T.json').write_text(json.dumps({'target_timestamp':T,'captured_at':dt.datetime.now(dt.timezone.utc).isoformat(),'markets':collected,'raw_directory':str(RAW.relative_to(ROOT))},indent=2))

def curves():
 d=json.loads((ROOT/'data/eth/carry_economics_primary_T.json').read_text());wanted={'0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4','0x85252bb8485c99bba46fe149c7dd2aad83672640f53c630890673cf1848ba16e','0xe7e9694b754c4d4f7e21faf7223f6fa71abaeb10296a4c43a54a7977149687d2'};rows=[];requests=[];labels=[]
 for row in d['markets']:
  if row['id'] not in wanted:continue
  params=words(row['raw']['params'].get('result'));market=words(row['raw']['market'].get('result'));irm='0x'+format(params[3],'040x')
  for util in [0,.1,.2,.3,.4,.5,.6,.7,.8,.85,.89,.9,.91,.92,.94,.95,.96,.98,.99,1]:
   state=market.copy();state[2]=int(state[0]*util);state[4]=row['block_timestamp'];encoded=''.join(enc_uint(x) for x in params+state);labels.append({'market_id':row['id'],'utilization':util,'market_input':state});requests.append(call(irm,'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',encoded,hex(row['block'])))
 rr=rpc('ethereum',requests,'morpho_frozen_target_curves_T');(ROOT/'data/eth/carry_economics_curves_T.json').write_text(json.dumps({'target_timestamp':T,'curve_basis':'Primary IRM view calls at T, holding the stored per-market target rate constant by setting hypothetical lastUpdate to the block timestamp. No time adaptation or balance forecast.','labels':labels,'responses':rr},indent=2));print('curve points',len(rr))

def aave():
 manifest=[json.loads(line) for line in (ROOT/'raw/eth/2026-10-02/requests.jsonl').read_text().splitlines()];blocks={r['chain']:r for r in json.loads((ROOT/'data/eth/snapshot_manifest.json').read_text())['chains']};out=[]
 for chain in ['ethereum','base','arbitrum','optimism']:
  book=next(r for r in reversed(manifest) if r['key']=='aave_addressbook_'+chain and r.get('path'));text=(ROOT/book['path']).read_text();constant=lambda n:re.search(r'\b'+n+r'\s*=\s*(?:IPool\()?\s*(0x[a-fA-F0-9]{40})',text).group(1).lower();pool=constant('POOL');loan=constant('USDCn_UNDERLYING' if chain in ['arbitrum','optimism'] else 'USDC_UNDERLYING');coll=constant('wstETH_UNDERLYING');tag=hex(blocks[chain]['block']);requests=[call(pool,'getReserveData(address)',enc_addr(a),tag) for a in [loan,coll]];rr=rpc(chain,requests,'aave_usdc_'+chain+'_reserves_T');byid={r['id']:r for r in rr};loanstate=words(byid.get(1,{}).get('result'));collstate=words(byid.get(2,{}).get('result'));row={'chain':chain,'block':blocks[chain],'pool':pool,'loan_asset':loan,'collateral_asset':coll,'loan_reserve':byid.get(1,{}),'collateral_reserve':byid.get(2,{})}
  if loanstate and collstate:
   at='0x'+format(loanstate[8],'040x');vd='0x'+format(loanstate[10],'040x');irm='0x'+format(loanstate[11],'040x');row['irm']=irm
   calls=[call(at,'totalSupply()','',tag),call(vd,'totalSupply()','',tag),call(loan,'balanceOf(address)',enc_addr(at),tag),call(irm,'getInterestRateData(address)',enc_addr(loan),tag),call(irm,'getBaseVariableBorrowRate(address)',enc_addr(loan),tag),call(irm,'getVariableRateSlope1(address)',enc_addr(loan),tag),call(irm,'getVariableRateSlope2(address)',enc_addr(loan),tag)]
   cr=rpc(chain,calls,'aave_usdc_'+chain+'_balances_model_T');row['extra_labels']=['lender_claim','variable_debt','cash','interest_rate_data','base_rate','slope1','slope2'];row['extra_responses']=cr
   capture('aave_irm_source_'+chain+'_'+irm,{'ethereum':'https://eth.blockscout.com','base':'https://base.blockscout.com','arbitrum':'https://arbitrum.blockscout.com','optimism':'https://optimism.blockscout.com'}[chain]+'/api/v2/smart-contracts/'+irm)
  out.append(row);print(chain,'USDC reserve captured',bool(loanstate),flush=True)
 (ROOT/'data/eth/carry_economics_aave_T.json').write_text(json.dumps({'target_timestamp':T,'markets':out},indent=2))

def supplement():
 primary=json.loads((ROOT/'data/eth/carry_economics_primary_T.json').read_text());aaves=json.loads((ROOT/'data/eth/carry_economics_aave_T.json').read_text());checks=[]
 for chain in ['ethereum','base','arbitrum','optimism']:
  models=sorted({addr for row in primary['markets'] if row['chain']==chain and (params:=words(row['raw']['params'].get('result'))) for addr in ['0x'+format(params[3],'040x')]})
  models+=sorted({r['irm'] for r in aaves['markets'] if r['chain']==chain and r.get('irm')});row=next(r for r in aaves['markets'] if r['chain']==chain);block=row['block']['block'];calls=[('eth_getCode',[model,hex(block)]) for model in models]+[call(row['pool'],'getVirtualUnderlyingBalance(address)',enc_addr(row['loan_asset']),hex(block))];response=rpc(chain,calls,'model_bytecode_'+chain+'_T');checks.append({'chain':chain,'block':block,'model_addresses':models,'responses':response,'virtual_cash_response_index':len(models)+1})
 docs=[('morpho_core_source','https://eth.blockscout.com/api/v2/smart-contracts/'+MORPHO),('morpho_irm_docs','https://docs.morpho.org/developers/contracts/irm/'),('morpho_address_docs','https://docs.morpho.org/developers/contracts/addresses/'),('morpho_rewards_docs','https://docs.morpho.org/learn/concepts/rewards/'),('sentora_case_study','https://morpho.org/stories/sentora'),('hastra_prime_docs','https://help.hastra.io/24d233935654815fb088ffef227d7f5a')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda item:capture(*item),docs))
 (ROOT/'data/eth/carry_economics_model_proof_T.json').write_text(json.dumps({'target_timestamp':T,'bytecodes':checks},indent=2));print('model code checks',sum(len(r['model_addresses']) for r in checks))

if __name__=='__main__':curves() if '--curves' in sys.argv else aave() if '--aave' in sys.argv else supplement() if '--supplement' in sys.argv else run()
