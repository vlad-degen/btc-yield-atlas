"""Read-only credit expansion, immutable captures and fixed financial T."""
import concurrent.futures,datetime as dt,hashlib,json,sys,threading,urllib.request,urllib.error,time
import urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'raw/eth/credit-expansion-2026-10-04'
D=ROOT/'data/eth'
T=1790985599
BLOCKS={'ethereum':26108081,'base':52098126,'arbitrum':511139919,'optimism':157693411}
RPCS={'ethereum':['https://eth.drpc.org','https://gateway.tenderly.co/public/mainnet','https://eth-mainnet.public.blastapi.io'],'base':['https://base.drpc.org','https://mainnet.base.org'],'arbitrum':['https://arbitrum.drpc.org','https://arb1.arbitrum.io/rpc'],'optimism':['https://optimism.drpc.org','https://mainnet.optimism.io']}
LOCK=threading.Lock()
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_addr,enc_uint

def capture(key,url,payload=None,timeout=35):
 RAW.mkdir(parents=True,exist_ok=True);encoded=None if payload is None else json.dumps(payload).encode()
 req=urllib.request.Request(url,data=encoded,headers={'User-Agent':'ETHResearch/1.0','Content-Type':'application/json','Accept':'application/json,text/html,*/*'})
 error=None
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r:body,status=r.read(),r.status
 except urllib.error.HTTPError as e:body,status,error=e.read(),e.code,str(e)
 except Exception as e:body,status,error=str(e).encode(),None,str(e)
 sha=hashlib.sha256(body).hexdigest()
 try:value=json.loads(body);suffix='.json'
 except (ValueError,UnicodeDecodeError):value=None;suffix='.txt'
 path=RAW/(key+'-'+sha[:16]+suffix);path.write_bytes(body)
 record={'key':key,'url':url,'request':payload,'method':'POST' if payload is not None else 'GET','captured_at_UTC':dt.datetime.now(dt.timezone.utc).isoformat(),'http_status':status,'sha256':sha,'path':str(path.relative_to(ROOT)),'bytes':len(body),'error':error}
 with LOCK:
  with (RAW/'requests.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
 print(key,status,len(body),flush=True)
 return record,value

def rpc(chain,calls,key):
 payload=[{'jsonrpc':'2.0','id':i+1,'method':m,'params':p} for i,(m,p) in enumerate(calls)];good={};last={};sources=[]
 for provider,url in enumerate(RPCS[chain]):
  remaining=[x for x in payload if x['id'] not in good]
  if not remaining:break
  r,v=capture(key+f'_provider{provider}',url,remaining,45);sources.append(r)
  if isinstance(v,list):
   for x in v:
    last[x['id']]=x
    if 'result' in x:good[x['id']]=x
 return [good.get(i+1,last.get(i+1,{'id':i+1,'error':{'message':'No valid response'}})) for i in range(len(calls))],sources

def latest(key):
 records=[json.loads(x) for x in (RAW/'requests.jsonl').read_text().splitlines() if x]
 r=next(x for x in reversed(records) if x['key']==key and x['http_status']==200)
 return r,json.loads((ROOT/r['path']).read_text())

def unknowns():
 a=json.loads((D/'market_completeness_audit_2026-10-04.json').read_text())['measured_scope']['largest_unidentified_borrowers']
 calls=[];labels=[]
 for x in a:
  address=x['address']
  for method,args,kind in [('eth_getCode',[address,hex(BLOCKS['ethereum'])],'code'),('eth_getBalance',[address,hex(BLOCKS['ethereum'])],'native_balance')]:labels.append({**x,'kind':kind});calls.append((method,args))
 rr,sources=rpc('ethereum',calls,'top_unknowns_state_T')
 (D/'credit_expansion_unknown_state_T.json').write_text(json.dumps({'financial_target_timestamp':T,'block':BLOCKS['ethereum'],'labels':labels,'responses':rr,'sources':sources},indent=2))
 jobs=[]
 for x in a:
  address=x['address']
  jobs.extend([(f'address_{address}','https://eth.blockscout.com/api/v2/addresses/'+address),
               (f'transfers_{address}_page0','https://eth.blockscout.com/api/v2/addresses/'+address+'/token-transfers?type=ERC-20'),
               (f'contract_{address}','https://eth.blockscout.com/api/v2/smart-contracts/'+address)])
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:list(p.map(lambda j:capture(*j),jobs))

def registries():
 jobs=[('compound_docs','https://docs.compound.finance/'),('compound_borrow_docs','https://docs.compound.finance/collateral-and-borrowing/'),
       ('compound_deployments_tree','https://api.github.com/repos/compound-finance/comet/git/trees/main?recursive=1'),
       ('euler_contract_docs','https://docs.euler.finance/developers/contract-addresses/'),('euler_subgraph_docs','https://docs.euler.finance/build/data-querying/subgraphs/'),
       ('euler_factory_source','https://raw.githubusercontent.com/euler-xyz/euler-vault-kit/master/src/GenericFactory/GenericFactory.sol'),
       ('euler_api_docs','https://docs.euler.finance/build/data-querying/api/'),
       ('silo_deployments_tree','https://api.github.com/repos/silo-finance/silo-contracts-v2/git/trees/master?recursive=1'),
       ('silo_contract_docs','https://docs.silo.finance/'),('fluid_resolvers','https://docs.fluid.instadapp.io/integrate-instadapp/integrate-resolvers')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as p:list(p.map(lambda j:capture(*j),jobs))

def detail_registries():
 paths=['mainnet/usdc','mainnet/usdt','mainnet/usds','base/usdbc','base/usdc','base/usds','arbitrum/usdc.e','arbitrum/usdc','arbitrum/usdt','optimism/usdc','optimism/usdt']
 jobs=[('compound_roots_'+p.replace('/','_'),'https://raw.githubusercontent.com/compound-finance/comet/main/deployments/'+p+'/roots.json') for p in paths]
 jobs += [('silo_factory_'+c,'https://raw.githubusercontent.com/silo-finance/silo-contracts-v2/master/silo-core/deployments/'+c+'/SiloFactory.sol.json') for c in ['mainnet','arbitrum_one','base','optimism']]
 jobs += [('euler_contract_registry','https://raw.githubusercontent.com/euler-xyz/euler-interfaces/master/addresses/EulerChains.json'),('euler_docs_actual','https://docs.euler.finance/build/contract-addresses'),('euler_interface_source','https://raw.githubusercontent.com/euler-xyz/euler-vault-kit/master/src/EVault/IEVault.sol'),('fluid_deployments','https://raw.githubusercontent.com/Instadapp/fluid-contracts-public/main/deployments/deployments.md'),('fluid_vault_resolver_source','https://raw.githubusercontent.com/Instadapp/fluid-contracts-public/main/contracts/periphery/resolvers/vault/main.sol')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as p:list(p.map(lambda j:capture(*j),jobs))

def paginate_unknowns():
 a=json.loads((D/'market_completeness_audit_2026-10-04.json').read_text())['measured_scope']['largest_unidentified_borrowers']
 def one(x):
  address=x['address'];_,v=latest('transfers_'+address+'_page0')
  for page in range(1,5):
   cursor=v.get('next_page_params')
   if not cursor:break
   _,v=capture('transfers_'+address+'_page'+str(page),'https://eth.blockscout.com/api/v2/addresses/'+address+'/token-transfers?'+urllib.parse.urlencode({'type':'ERC-20',**cursor}))
   if not isinstance(v,dict):break
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(one,a))

def ethcall(to,sig,args='',chain='ethereum'):
 return ('eth_call',[{'to':to,'data':'0x'+sel(sig)+args},hex(BLOCKS[chain])])

def batches(chain,calls,key,size=3):
 results=[];sources=[]
 for i in range(0,len(calls),size):
  rr,ss=rpc(chain,calls[i:i+size],key+'_'+str(i));results+=rr;sources+=ss
  time.sleep(.3)
 return results,sources

def compound_T():
 paths={'ethereum':['mainnet/usdc','mainnet/usdt','mainnet/usds'],'base':['base/usdbc','base/usdc','base/usds'],'arbitrum':['arbitrum/usdc.e','arbitrum/usdc','arbitrum/usdt'],'optimism':['optimism/usdc','optimism/usdt']}
 def one(item):
  chain,ps=item;labels=[];calls=[];regs=[]
  for path in ps:
   source,v=latest('compound_roots_'+path.replace('/','_'));address=v['comet'];regs.append(source)
   for sig in ['baseToken()','numAssets()','totalBorrow()','totalSupply()','getUtilization()','baseBorrowMin()']:
    labels.append({'protocol':'Compound V3','chain':chain,'market_id':address,'registry_path':path,'signature':sig});calls.append(ethcall(address,sig,chain=chain))
  rr,ss=batches(chain,calls,'compound_initial_'+chain)
  for label,result in zip(labels,rr):label['response']=result
  extra=[];calls=[]
  for path in ps:
   ls=[x for x in labels if x['registry_path']==path];address=ls[0]['market_id'];values={x['signature']:x['response'].get('result') for x in ls}
   if values['numAssets()'] in [None,'0x']:continue
   n=int(values['numAssets()'],16);u=values['getUtilization()']
   for i in range(n):
    extra.append({'chain':chain,'market_id':address,'registry_path':path,'signature':'getAssetInfo(uint8)','index':i});calls.append(ethcall(address,'getAssetInfo(uint8)',enc_uint(i),chain))
   if u and u!='0x':
    for sig in ['getBorrowRate(uint256)','getSupplyRate(uint256)']:
     extra.append({'chain':chain,'market_id':address,'registry_path':path,'signature':sig});calls.append(ethcall(address,sig,enc_uint(int(u,16)),chain))
  rr,ss2=batches(chain,calls,'compound_assets_'+chain)
  for label,result in zip(extra,rr):label['response']=result
  labels+=extra;more=[];calls=[]
  for label in extra:
   if label['signature']=='getAssetInfo(uint8)' and label['response'].get('result') not in [None,'0x']:
    words=[label['response']['result'][i:i+64] for i in range(2,len(label['response']['result']),64)];token='0x'+words[1][-40:];feed='0x'+words[2][-40:]
    for sig,to,arg in [('symbol()',token,''),('decimals()',token,''),('totalsCollateral(address)',label['market_id'],enc_addr(token)),('getPrice(address)',label['market_id'],enc_addr(feed))]:
     more.append({'chain':chain,'market_id':label['market_id'],'registry_path':label['registry_path'],'asset':token,'signature':sig});calls.append(ethcall(to,sig,arg,chain))
  rr,ss3=batches(chain,calls,'compound_collateral_'+chain)
  for label,result in zip(more,rr):label['response']=result
  return {'chain':chain,'labels':labels+more,'sources':regs+ss+ss2+ss3}
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:out=list(p.map(one,paths.items()))
 (D/'credit_expansion_compound_T.json').write_text(json.dumps({'financial_target_timestamp':T,'blocks':BLOCKS,'chains':out},indent=2))

def factory_counts():
 r,e=capture('euler_contract_registry_actual','https://raw.githubusercontent.com/euler-xyz/euler-interfaces/master/EulerChains.json')
 print(str(e)[:1000],flush=True)
 jobs=[]
 for chain,network in [('ethereum','mainnet'),('base','base'),('arbitrum','arbitrum_one'),('optimism','optimism')]:
  source,s=latest('silo_factory_'+network);jobs.append((chain,'Silo',s['address'],'getNextSiloId()',source))
  if chain!='optimism':jobs.append((chain,'Fluid','0xa5c3e16523eeeddcc34706b0e6be88b4c6ea95cc','getAllVaultsAddresses()',None))
 if isinstance(e,list):
  for cid,chain in [(1,'ethereum'),(8453,'base'),(42161,'arbitrum'),(10,'optimism')]:
   x=next((x for x in e if x['chainId']==cid),{})
   factory=x.get('addresses',{}).get('coreAddrs',{}).get('eVaultFactory')
   if factory:jobs.append((chain,'Euler',factory,'getProxyListLength()',r))
 out=[]
 for chain,protocol,address,sig,source in jobs:
  rr,ss=rpc(chain,[ethcall(address,sig,chain=chain)],'factory_count_'+protocol+'_'+chain)
  out.append({'chain':chain,'protocol':protocol,'address':address,'signature':sig,'response':rr[0],'sources':([source] if source else [])+ss})
 (D/'credit_expansion_factory_counts_T.json').write_text(json.dumps({'financial_target_timestamp':T,'rows':out},indent=2))

def morpho_unknown_T():
 from credit_expansion_build import USD
 borrowers=json.loads((D/'research_borrowers.json').read_text())['borrowers'];addresses={x['address'].lower() for x in borrowers if not x['identity_verified'] and sum(m['debt_usd'] for m in x['markets'] if m['debt'] in USD)>=5e6};addresses.add('0x462a336dcac6eaf544106266914caa5a18b831d0')
 positions=[x for x in json.loads((D/'research_borrowers.json').read_text())['positions'] if x['address'].lower() in addresses and x['chain_id']==1]
 labels=[];calls=[];contract='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
 for p in positions:
  for sig,args in [('position(bytes32,address)',p['market_id'][2:]+enc_addr(p['address'])),('market(bytes32)',p['market_id'][2:])]:labels.append({**p,'signature':sig});calls.append(ethcall(contract,sig,args))
 rr,ss=batches('ethereum',calls,'unknown_morpho_T')
 for l,r in zip(labels,rr):l['fixed_T_response']=r
 (D/'credit_expansion_morpho_unknown_T.json').write_text(json.dumps({'financial_target_timestamp':T,'block':BLOCKS['ethereum'],'labels':labels,'sources':ss},indent=2))

def array_addresses(result):
 if not result or result=='0x':return []
 w=[result[i:i+64] for i in range(2,len(result),64)];offset=int(w[0],16)//32;n=int(w[offset],16)
 return ['0x'+x[-40:] for x in w[offset+1:offset+1+n]]

def multicall(chain,targets,key):
 # Standard Multicall3 aggregate3, allowing each target call to fail independently.
 bodies=[enc_addr(a)+enc_uint(1)+enc_uint(96)+enc_uint(len(data)//2)+data.ljust(((len(data)+63)//64)*64,'0') for a,data in targets]
 offsets=[];position=32*len(bodies)
 for body in bodies:offsets.append(enc_uint(position));position+=len(body)//2
 args=enc_uint(32)+enc_uint(len(bodies))+''.join(offsets)+''.join(bodies)
 rr,ss=rpc(chain,[ethcall('0xca11bde05977b3631167028862be2a173976ca11','aggregate3((address,bool,bytes)[])',args,chain)],key)
 result=rr[0].get('result');out=[]
 if result and result!='0x':
  data=result[2:];base=int(data[:64],16)*2;n=int(data[base:base+64],16);arraybase=base+64
  for i in range(n):
   entry=arraybase+int(data[arraybase+64*i:arraybase+64*(i+1)],16)*2;success=int(data[entry:entry+64],16);b=entry+int(data[entry+64:entry+128],16)*2;length=int(data[b:b+64],16)
   out.append({'success':bool(success),'result':'0x'+data[b+64:b+64+length*2]})
 return out,ss

def euler_T():
 counts=json.loads((D/'credit_expansion_factory_counts_T.json').read_text());out=[]
 for row in counts['rows']:
  if row['protocol']!='Euler' or row['chain'] not in ['ethereum','base'] or not row['response'].get('result'):continue
  n=int(row['response'].get('result','0x0'),16);chain=row['chain'];factory=row['address']
  rr,ss=rpc(chain,[ethcall(factory,'getProxyListSlice(uint256,uint256)',enc_uint(0)+enc_uint(n),chain)],'euler_all_proxies_'+chain);proxies=array_addresses(rr[0].get('result'));assets=[]
  for i in range(0,len(proxies),180):
   results,sources=multicall(chain,[(a,sel('asset()')) for a in proxies[i:i+180]],'euler_assets_'+chain+'_'+str(i));ss+=sources
   assets += [{'vault':a,'asset':'0x'+r['result'][-40:] if r['success'] and len(r['result'])>=66 else None} for a,r in zip(proxies[i:i+180],results)]
  usd={'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','0xdac17f958d2ee523a2206206994597c13d831ec7','0x6b175474e89094c44da98b954eedeac495271d0f','0x83f20f44975d03b1b09e64809b757c47f942beea','0x8292bb45bf1ee4d140127049757c2e0ff06317ed','0x4c9edd5852cd905f086c759e8383e09bff1e68b3','0xd9d920aa40f578ab794426f5c90f6c731d159def','0xdc035d45d973e3ec169d2276ddab16f1e407384f','0x833589fcd6edb6e08f4c7c32d4f71b54bda02913','0xfde4c96c8593536e31f229ea8f37b2ad a2699bb2'.replace(' ','')}
  stable=[x for x in assets if x['asset'] and x['asset'].lower() in usd];calls=[];labels=[]
  for v in stable:
   for sig in ['LTVList()','totalBorrows()','cash()','interestRate()','caps()','decimals()']:
    calls.append((v['vault'],sel(sig)));labels.append({**v,'signature':sig})
  for i in range(0,len(calls),150):
   results,sources=multicall(chain,calls[i:i+150],'euler_stable_'+str(i));ss+=sources
   for label,result in zip(labels[i:i+150],results):label['response']=result
  out.append({'chain':chain,'factory':factory,'registered_proxy_count':n,'proxies':proxies,'assets':assets,'stable_labels':labels,'sources':ss})
 (D/'credit_expansion_euler_T.json').write_text(json.dumps({'financial_target_timestamp':T,'chains':out},indent=2))

def fluid_T():
 from collect import read_latest
 from fluid_pilot import decode_static
 abi=read_latest('fluid_vaultresolver_candidate')['abi'];func=next(x for x in abi if x.get('name')=='getVaultEntireData');counts=json.loads((D/'credit_expansion_factory_counts_T.json').read_text());out=[]
 for row in counts['rows']:
  if row['protocol']!='Fluid' or not row['response'].get('result'):continue
  chain=row['chain'];vaults=array_addresses(row['response']['result']);ss=[];decoded=[]
  for i in range(0,len(vaults),15):
   subset=vaults[i:i+15];args=enc_uint(32)+enc_uint(len(subset))+''.join(enc_addr(a) for a in subset)
   rr,sources=rpc(chain,[ethcall(row['address'],'getVaultsEntireData(address[])',args,chain)],'fluid_all_'+chain+'_'+str(i));ss+=sources;result=rr[0].get('result')
   if result:
    words=[int(result[j:j+64],16) for j in range(2,len(result),64)];offset=words[0]//32;n=words[offset];index=offset+1
    for j in range(n):
     value,index=decode_static(func['outputs'],words,index);decoded.append(value['vaultData_'])
    assert index==len(words)
  out.append({'chain':chain,'registered_vault_count':len(vaults),'vaults':vaults,'decoded':decoded,'sources':ss})
 (D/'credit_expansion_fluid_T.json').write_text(json.dumps({'financial_target_timestamp':T,'chains':out},indent=2))

def silo_T():
 counts=json.loads((D/'credit_expansion_factory_counts_T.json').read_text());out=[]
 for row in counts['rows']:
  if row['protocol']!='Silo' or not row['response'].get('result'):continue
  chain=row['chain'];n=int(row['response']['result'],16);ids=list(range(3000,n));rr,ss=multicall(chain,[(row['address'],sel('idToSiloConfig(uint256)')+enc_uint(i)) for i in ids],'silo_configs_'+chain)
  configs=[{'id':i,'config':'0x'+r['result'][-40:]} for i,r in zip(ids,rr) if r['success'] and int(r['result'],16)>0];rr,ss2=multicall(chain,[(r['config'],sel('getSilos()')) for r in configs],'silo_pairs_'+chain);ss+=ss2
  for c,r in zip(configs,rr):c['response']=r;c['silos']=['0x'+r['result'][i:i+64][-40:] for i in [2,66]] if r['success'] else []
  calls=[(a,sel('asset()')) for c in configs for a in c['silos']];rr,ss2=multicall(chain,calls,'silo_assets_'+chain);ss+=ss2;assets={a:'0x'+r['result'][-40:] for (a,_),r in zip(calls,rr) if r['success']}
  out.append({'chain':chain,'factory':row['address'],'next_silo_id':n,'configs':configs,'assets':assets,'sources':ss})
 (D/'credit_expansion_silo_T.json').write_text(json.dumps({'financial_target_timestamp':T,'chains':out},indent=2))

def borrower_receipts():
 a=json.loads((D/'market_completeness_audit_2026-10-04.json').read_text())['measured_scope']['largest_unidentified_borrowers'];manifest=[json.loads(x) for x in (RAW/'requests.jsonl').read_text().splitlines()];txs={}
 for b in a:
  for page in range(5):
   _,v=latest('transfers_'+b['address']+'_page'+str(page))
   for x in v['items']:
    if x['block_number']>BLOCKS['ethereum']:continue
    sym=x['token']['symbol'];amount=int(x['total']['value'])/10**int(x['token']['decimals'] or 18)
    if x['from']['hash'].lower()=='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb' and sym in ['USDC','USDT','DAI','PYUSD','RLUSD','USDS'] and amount>=10000:txs[x['transaction_hash']]={'borrower':b['address'],'transfer':x}
 calls=[('eth_getTransactionReceipt',[tx]) for tx in txs];rr,ss=batches('ethereum',calls,'borrow_receipts')
 for item,result in zip(txs.values(),rr):item['receipt_response']=result
 (D/'credit_expansion_borrow_receipts.json').write_text(json.dumps({'financial_target_timestamp':T,'transactions':txs,'sources':ss},indent=2))

def metadata_T():
 chains={};sources=[]
 for protocol in ['euler','fluid','silo','compound']:
  path=D/('credit_expansion_'+protocol+'_T.json')
  if not path.exists():continue
  v=json.loads(path.read_text())
  for c in v['chains']:
   chain=c['chain'];tokens=chains.setdefault(chain,set())
   if protocol=='euler':tokens.update(x['asset'] for x in c['assets'] if x['asset'])
   elif protocol=='silo':tokens.update(c['assets'].values())
   elif protocol=='fluid':tokens.update(a for x in c['decoded'] for side in ['supplyToken','borrowToken'] for a in x['constantVariables'][side].values())
   else:tokens.update(x['asset'] for x in c['labels'] if x.get('asset'))
 out=[]
 for chain,tokens in chains.items():
  tokens=sorted(t for t in tokens if t.lower() not in ['0x0000000000000000000000000000000000000000','0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee']);labels=[];calls=[]
  for token in tokens:
   for sig in ['symbol()','decimals()']:labels.append({'chain':chain,'token':token,'signature':sig});calls.append((token,sel(sig)))
  for i in range(0,len(calls),180):
   rr,ss=multicall(chain,calls[i:i+180],'token_metadata_'+chain+'_'+str(i));sources+=ss
   for l,r in zip(labels[i:i+180],rr):out.append({**l,'response':r})
 (D/'credit_expansion_token_metadata_T.json').write_text(json.dumps({'financial_target_timestamp':T,'labels':out,'sources':sources},indent=2))

def crosscheck_receipts():
 v=json.loads((D/'credit_expansion_borrow_receipts.json').read_text());tx=next(iter(v['transactions']));capture('receipt_second_provider_'+tx,'https://gateway.tenderly.co/public/mainnet',{'jsonrpc':'2.0','id':1,'method':'eth_getTransactionReceipt','params':[tx]});capture('explorer_transaction_'+tx,'https://eth.blockscout.com/api/v2/transactions/'+tx);capture('morpho_event_library','https://raw.githubusercontent.com/morpho-org/morpho-blue/main/src/libraries/EventsLib.sol');capture('euler_cap_library','https://raw.githubusercontent.com/euler-xyz/euler-vault-kit/master/src/EVault/shared/lib/AmountCapLib.sol')

def credit_followup():
 from credit_expansion_build import token_metadata
 from discover import FAMILY
 meta=token_metadata();out=[]
 for chain in json.loads((D/'credit_expansion_euler_T.json').read_text())['chains']:
  assetmap={x['vault']:x['asset'] for x in chain['assets']};calls=[];labels=[]
  for label in chain['stable_labels']:
   if label['signature']!='LTVList()' or not label.get('response',{}).get('success'):continue
   for cv in array_addresses(label['response']['result']):
    asset=assetmap.get(cv);symbol=meta.get((chain['chain'],asset),{}).get('symbol','')
    if symbol.upper() in FAMILY:
     for sig in ['LTVBorrow(address)','LTVLiquidation(address)']:
      labels.append({'chain':chain['chain'],'loan_vault':label['vault'],'collateral_vault':cv,'collateral_asset':asset,'collateral_symbol':symbol,'signature':sig});calls.append((label['vault'],sel(sig)+enc_addr(cv)))
  for i in range(0,len(calls),150):
   rr,ss=multicall(chain['chain'],calls[i:i+150],'euler_ltv_'+chain['chain']+'_'+str(i))
   for l,r in zip(labels[i:i+150],rr):l['response']=r
   out.append({'labels':labels[i:i+150],'sources':ss})
 (D/'credit_expansion_euler_ltv_T.json').write_text(json.dumps({'financial_target_timestamp':T,'chunks':out},indent=2))
 capture('morpho_official_addresses','https://docs.morpho.org/developers/contracts/addresses/')
 capture('euler_source_tree','https://api.github.com/repos/euler-xyz/euler-vault-kit/git/trees/master?recursive=1')
 v=json.loads((D/'credit_expansion_borrow_receipts.json').read_text());candidates=[]
 for tx,item in v['transactions'].items():
  source=item['transfer'];addr=item['borrower'];collected=[]
  for page in range(5):
   _,p=latest('transfers_'+addr+'_page'+str(page));collected+=p['items']
  forward=sorted([x for x in collected if x['block_number']>=source['block_number'] and x['block_number']<=source['block_number']+900 and x['block_number']<=BLOCKS['ethereum'] and x['from']['hash'].lower()==addr and x['token']['address_hash'].lower()==source['token']['address_hash'].lower() and int(x['total']['value'])>0],key=lambda x:(x['block_number'],x['log_index']))
  for x in forward[:3]:candidates.append({'borrow_transaction':tx,'borrower':addr,'transfer':x})
 seen={};calls=[]
 for x in candidates:
  tx=x['transfer']['transaction_hash']
  if tx not in seen:seen[tx]=None;calls.append(('eth_getTransactionReceipt',[tx]))
 rr,ss=batches('ethereum',calls,'borrow_following_receipts')
 for tx,r in zip(seen,rr):seen[tx]=r
 (D/'credit_expansion_proceeds_receipts.json').write_text(json.dumps({'financial_target_timestamp':T,'candidate_following_transfers':candidates,'receipts':seen,'sources':ss,'attribution_rule':'Following same-token outflows are observed, not proof of exclusive fungible loan-proceeds attribution.'},indent=2))

def destinations():
 jobs=[('euler_cap_library_actual','https://raw.githubusercontent.com/euler-xyz/euler-vault-kit/master/src/EVault/shared/types/AmountCap.sol')]
 for addr in ['0x90882e7c28ddf0ac1177033a310aeed8eff25e90','0xaa34d20be3f9623ccf5bff53ef4dfa765c3f5dd5','0x20f6c325df578a11209817a30ebb2f0d5454176d']:
  jobs.append(('address_'+addr,'https://eth.blockscout.com/api/v2/addresses/'+addr));jobs.append(('transfers_'+addr+'_page0','https://eth.blockscout.com/api/v2/addresses/'+addr+'/token-transfers?type=ERC-20'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(lambda j:capture(*j),jobs))
 labels=[];calls=[]
 for vault,borrower in [('0x2ca22cb25558fa2018ecb1ce4ed8af92ee7ea423','0xa122687285dc5012141055a801045f069112e7c6'),('0x8381a156958711e230f325428b5eb4b6555c75d9','0x4f87de7d21aef48090958f7342e1f69dff790545')]:
  for sig,args in [('name()',''),('symbol()',''),('asset()',''),('decimals()',''),('totalAssets()',''),('balanceOf(address)',enc_addr(borrower)),('convertToAssets(uint256)',enc_uint(10**18))]:labels.append({'vault':vault,'borrower':borrower,'signature':sig});calls.append((vault,sel(sig)+args))
 rr,ss=multicall('ethereum',calls,'confirmed_carry_destinations_T')
 for l,r in zip(labels,rr):l['response']=r
 (D/'credit_expansion_destinations_T.json').write_text(json.dumps({'financial_target_timestamp':T,'labels':labels,'sources':ss},indent=2))

if __name__=='__main__':
 {'unknowns':unknowns,'registries':registries,'details':detail_registries,'paginate':paginate_unknowns,'compound':compound_T,'factories':factory_counts,'morpho':morpho_unknown_T,'euler':euler_T,'fluid':fluid_T,'silo':silo_T,'receipts':borrower_receipts,'metadata':metadata_T,'crosscheck':crosscheck_receipts,'followup':credit_followup,'destinations':destinations}[sys.argv[1]]()
