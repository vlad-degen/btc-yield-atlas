"""Read-only archive financial/state capture for bounded large ETH family cases.
No signing, eth_sendTransaction, account impersonation persistence or broadcasting.
"""
import concurrent.futures,datetime,hashlib,json,pathlib,sys,time,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2];RAW=ROOT/'raw/eth/strategy-universe-deep-2026-10-04';RAW.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'));from keccak_lib import sel,enc_addr,enc_uint,keccak
T=1790985599;BLOCK=26108081;TAG=hex(BLOCK);RPC='https://eth-mainnet.public.blastapi.io'
CONTRACTS={'oseth':'0xf1c9acdc66974dfb6decb12aa385b9cd01190e38','oseth_controller':'0x2a261e60fb14586b474c208b1b7ac6d0f5000306','oseth_redeemer':'0xc43a7b16a7a167c0318390cba16787c11e9e1fd0','stakewise_genesis':'0xac0f906e433d58fa868f936e8a43230473652885','meth':'0xd5f7838f5c461feff7fe49ea5ebaf7728bb0adfa','meth_staking':'0xe3cbd06d7dadb3f4e6557bab7edd924cd1489e8f','cmeth':'0xe6829d9a7ee3040e1276fa75293bde931859e8fa','cmeth_vault':'0x33272d40b247c4cd9c646582c9bbad44e85d4fe4','cmeth_accountant':'0x6049bd892f14669a4466e46981eced75d610a2ec','cmeth_withdraw':'0x12be34be067ebd201f6eaf78a861d90b2a66b113','yearn_weth':'0xc56413869c6cdf96496f2b1ef801fedbdfa7ddb0','autoeth':'0x0a2b94f6871c1d7a32fe58e1ab5e6dea2f114e56','yb_weth':'0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea'}
def fetch(key,url,payload=None):
 meta={'key':key,'url':url,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'financialTimestamp':T,'ethereumBlock':BLOCK,'request':payload}
 try:
  req=urllib.request.Request(url,data=json.dumps(payload).encode()if payload is not None else None,headers={'User-Agent':'ETH-Yield-Research/1.0','Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=45)as r:body=r.read();meta.update(status=r.status,HTTPDate=r.headers.get('Date'))
  h=hashlib.sha256(body).hexdigest();p=RAW/(key+'-'+h[:16]+'.json');p.write_bytes(body);meta.update(path=str(p.relative_to(ROOT)),sha256=h,bytes=len(body));data=json.loads(body)
 except Exception as e:meta.update(error=str(e));data=None
 with(RAW/'requests.jsonl').open('a')as f:f.write(json.dumps(meta)+'\n')
 return data

def call(label,to,sig,args='',tag=TAG,caller=None):
 tx={'to':to,'data':'0x'+sel(sig)+args,'gas':'0x1c9c380'}
 if caller:tx['from']=caller
 return{'label':label,'address':to,'signature':sig,'method':'eth_call','params':[tx,tag]}
def rpc(key,rows,url=RPC):
 out=[]
 for i in range(0,len(rows),10):
  rr=rows[i:i+10];payload=[{'jsonrpc':'2.0','id':j+1,'method':x['method'],'params':x['params']}for j,x in enumerate(rr)];d=fetch(key+'_batch'+str(i//10),url,payload);d=[d]if isinstance(d,dict)else(d or[]);byid={x['id']:x for x in d if isinstance(x,dict)and'id'in x}
  time.sleep(.5)
  out += [{**x,'response':byid.get(j+1,{'error':{'message':'No successful response capture'}})}for j,x in enumerate(rr)]
 (RAW/(key+'.json')).write_text(json.dumps({'financialTimestamp':T,'ethereumBlock':BLOCK,'records':out},indent=2)+'\n');print(key,sum('result'in x['response']for x in out),'/',len(out),flush=True);return out

def interfaces():
 w=[(k+'_interface','https://eth.blockscout.com/api/v2/smart-contracts/'+a)for k,a in CONTRACTS.items()]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as p:r=list(p.map(lambda x:fetch(*x),w))
 print([(w[i][0],bool(x),len(x.get('abi')or[])if isinstance(x,dict)else 0)for i,x in enumerate(r)])

def initial():
 rows=[]
 for k,a in CONTRACTS.items():
  rows.append({'label':k+'_code','address':a,'method':'eth_getCode','params':[a,TAG]})
  for sig in ['totalSupply()','decimals()','asset()','totalAssets()','owner()','paused()']:
   rows.append(call(k+'_'+sig,a,sig))
  for sig in ['convertToAssets(uint256)','previewRedeem(uint256)']:
   rows.append(call(k+'_'+sig,a,sig,enc_uint(10**18)))
  rows.append({'label':k+'_native_balance','address':a,'method':'eth_getBalance','params':[a,TAG]})
  rows.append(call(k+'_looseWETH','0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2','balanceOf(address)',enc_addr(a)))
  rows.append(call(k+'_looseMETH',CONTRACTS['meth'],'balanceOf(address)',enc_addr(a)))
 rpc('initial_Blast_T',rows)

def targeted():
 rows=[]
 terms=['fee','Fee','paused','unlock','Unlock','withdraw','Withdraw','queue','Queue','total','Total','buffer','Buffer','rate','Rate','nonce','Nonce','minimum','Minimum','max','Max','treasury','Treasury','authority','Authority','owner','Owner','accountant','Accountant','reward','Reward','staking','Staking','timestamp','Timestamp']
 for k,a in CONTRACTS.items():
  files=list(RAW.glob(k+'_implementation_interface-*'))or list(RAW.glob(k+'_interface-*'))
  if not files:continue
  d=json.loads(files[-1].read_text());abi=d.get('abi')or[]
  for x in abi:
   if x.get('type')!='function'or x.get('stateMutability')not in['view','pure']:continue
   name=x['name'];ins=x.get('inputs')or[]
   if not any(t in name for t in terms)and name not in ['getAssetBreakdown','getDestinations','get_default_queue','isShutdown','is_killed','liquidity','stablecoin_allocated','stablecoin_allocation','admin','amm','staker','ASSET_TOKEN','STABLECOIN','getSystemRegistry','accessController','getRateSafe','base']:continue
   if len(ins)>0:continue
   sig=name+'()';rows.append(call(k+'_'+sig,a,sig))
 for k,a,sig in [('meth_staking',CONTRACTS['meth_staking'],'mETHToETH(uint256)'),('oseth_controller',CONTRACTS['oseth_controller'],'convertToAssets(uint256)'),('cmeth_accountant',CONTRACTS['cmeth_accountant'],'getRate()'),('cmeth_accountant',CONTRACTS['cmeth_accountant'],'getRateInQuote(address)')]:
  rows.append(call(k+'_'+sig,a,sig,enc_uint(10**18)if sig.endswith('(uint256)')else enc_addr(CONTRACTS['meth'])if sig.endswith('(address)')else''))
 slot='0x'+(int.from_bytes(keccak(b'eip1967.proxy.implementation'),'big')-1).to_bytes(32,'big').hex()
 for k in ['meth','meth_staking','cmeth','cmeth_vault','stakewise_genesis']:
  rows.append({'label':k+'_implementation_slot_T','address':CONTRACTS[k],'method':'eth_getStorageAt','params':[CONTRACTS[k],slot,TAG]})
 rpc('targeted_T',rows)

def history():
 old=json.loads((ROOT/'data/eth/vault_history_rpc.json').read_text());blocks=sorted({(x['timestamp'],x['block'])for x in old['labels']if x['timestamp']<=T});blocks=[x for x in blocks if datetime.datetime.fromtimestamp(x[0],datetime.timezone.utc).strftime('%Y-%m')in['2024-09','2024-12','2025-03','2025-06','2025-09','2025-12','2026-03','2026-06','2026-09']]+[(T,BLOCK)]
 rows=[]
 for ts,b in blocks:
  for k in ['oseth','oseth_controller','meth','meth_staking','cmeth_vault','cmeth_accountant','yearn_weth','autoeth']:
   a=CONTRACTS[k];rows.append({'label':k+'_'+str(ts)+'_code','productKey':k,'timestamp':ts,'block':b,'method':'eth_getCode','params':[a,hex(b)]})
   methods=['totalSupply()']if k in['oseth','meth','cmeth_vault']else['totalAssets()','convertToAssets(uint256)']if k in['oseth_controller','yearn_weth','autoeth']else['mETHToETH(uint256)']if k=='meth_staking'else['getRate()']
   for sig in methods:
    x=call(k+'_'+str(ts)+'_'+sig,a,sig,enc_uint(10**18)if'(uint256)'in sig else'',hex(b));x.update(productKey=k,timestamp=ts,block=b);rows.append(x)
 rpc('historical_endpoints_Blast',rows)
if __name__=='__main__':{'interfaces':interfaces,'initial':initial,'targeted':targeted,'history':history}[sys.argv[1]]()
