"""Public primary discovery and fixed-T captures for carry variant expansion."""
from __future__ import annotations
import concurrent.futures, gzip,json,re,sys
from pathlib import Path
import carry_economics_collect as c
from carry_economics_collect import call,enc_addr,enc_uint,words
ROOT=c.ROOT;DATA=ROOT/'data/eth';RAW=ROOT/'raw/eth/carry-variants-expansion-2026-10-04';c.RAW=RAW
T=c.T;BLOCK=26108081
ORIGINAL_CAPTURE=c.capture
CASES=[{'id':'tau-infinifi','name':'TAU InfiniFi ETH Carry','chain':'ethereum','address':'0xc50b2d51fd1e2ac67a9c09eaf63c24ea2465c64b'}, {'id':'reservoir-eth','name':'Reservoir ETH Yield','chain':'ethereum','address':'0xf6cd9e8415162c8fb3c52676c7ca68812a34f76e'}, {'id':'concrete-wsteth','name':'Concrete wstETH Plus','chain':'ethereum','address':'0xd57588c73715b65e0ead36ae06c15644169501b7'}, {'id':'mre7eth','name':'Midas mRe7ETH','chain':'optimism','address':'0xe7ba07519dfa06e60059563f484d6090dedf21b3'}]
def read(n):return json.loads((DATA/(n+'.json')).read_text())
def capture(key,url,payload=None):
 if (RAW/'requests.jsonl').exists():
  for line in reversed((RAW/'requests.jsonl').read_text().splitlines()):
   r=json.loads(line)
   if r.get('key')==key and r.get('url')==url and r.get('request')==payload and r.get('path'):
    p=ROOT/r['path'];body=p.read_bytes()
    if body.startswith(b'\x1f\x8b'):body=gzip.decompress(body)
    return json.loads(body) if body.lstrip().startswith((b'{',b'[')) else body.decode()
 result=ORIGINAL_CAPTURE(key,url,payload)
 if result is None and (RAW/'requests.jsonl').exists():
  for line in reversed((RAW/'requests.jsonl').read_text().splitlines()):
   r=json.loads(line)
   if r.get('key')==key and r.get('path'):
    body=(ROOT/r['path']).read_bytes()
    if body.startswith(b'\x1f\x8b'):return json.loads(gzip.decompress(body))
    break
 return result
c.capture=capture
def rpc(chain,requests,key):
 # Interface probes may correctly revert for most contracts. Retain those
 # explicit errors rather than discarding a complete batch on success ratio.
 payload=[{'jsonrpc':'2.0','id':i+1,'method':method,'params':params} for i,(method,params) in enumerate(requests)]
 candidates=[]
 size=4
 providers=(['https://optimism-rpc.publicnode.com'] if chain=='optimism' else ['https://ethereum-rpc.publicnode.com','https://eth-mainnet.public.blastapi.io'] if chain=='ethereum' else [])+c.RPCS[chain]
 for provider,url in enumerate(providers):
  result=[]
  for start in range(0,len(payload),size):
   response=capture(key+'_provider'+str(provider)+'_batch'+str(start//size),url,payload[start:start+size])
   if not isinstance(response,list):break
   result.extend(response)
  candidates.append(result)
  if len(result)==len(payload) and not any(r.get('error',{}).get('code') in [429,-32005] for r in result):return sorted(result,key=lambda r:r['id'])
 # Prefer the batch with actual results when all endpoints have rate errors.
 return max(candidates,key=lambda rows:sum('result' in r for r in rows),default=[])
def bootstrap():
 urls={'fusion_home':'https://app.ipor.io/fusion','fusion_reservoir':'https://app.ipor.io/fusion/ethereum/'+CASES[1]['address']+'/vault-info','fusion_tau':'https://app.ipor.io/fusion/ethereum/'+CASES[0]['address']+'/vault-info','midas_re7':'https://midas.app/mRe7ETH','midas_hyper':'https://midas.app/mHyperETH','midas_transparency':'https://midas.app/transparency','midas_docs':'https://docs.midas.app/','concrete_catalogue':'https://app.concrete.xyz/earn','fusion_docs':'https://docs.ipor.io/fusion'}
 for p in CASES:urls[p['id']+'_source']=('https://optimism.blockscout.com' if p['chain']=='optimism' else 'https://eth.blockscout.com')+'/api/v2/smart-contracts/'+p['address']
 def worker(item):
  key,url=item;value=capture(key,url);print(key,type(value).__name__,flush=True);return {'key':key,'url':url,'response':value}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(worker,urls.items()))
 (DATA/'carry_variants_expansion_bootstrap.json').write_text(json.dumps({'snapshot_timestamp':T,'discovery_date':'2026-10-04','rows':rows},indent=2))
 follow=[]
 for row in rows:
  data=row['response']
  if isinstance(data,dict):
   for impl in data.get('implementations',[]):
    address=impl.get('address') or impl.get('address_hash')
    follow.append((row['key']+'_implementation_'+address,row['url'].rsplit('/',1)[0]+'/'+address))
  elif isinstance(data,str) and row['key'] in ['fusion_home','midas_re7','concrete_catalogue']:
   for src in re.findall(r'<script[^>]+src=["\']([^"\']+)',data):
    if 'index' in src or 'main' in src:
     from urllib.parse import urljoin
     follow.append((row['key']+'_javascript',urljoin(row['url'],src)))
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:extra=list(pool.map(worker,follow))
 (DATA/'carry_variants_expansion_follow.json').write_text(json.dumps({'rows':extra},indent=2))
 print('Followed',len(extra),flush=True)
def catalogue():
 urls={'fusion_official_catalogue':'https://api.ipor.io/dapp/plasma-vaults-list','midas_marketplace':'https://api-prod.midas.app/api/marketplace/products','midas_tvl':'https://api-prod.midas.app/api/data/tvl','midas_re7_price':'https://api-prod.midas.app/api/data/mre7eth/price','midas_hyper_price':'https://api-prod.midas.app/api/data/mhypereth/price'}
 def worker(item):
  key,url=item;value=capture(key,url);print(key,type(value).__name__,flush=True);return {'key':key,'url':url,'response':value}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(worker,urls.items()))
 (DATA/'carry_variants_expansion_catalogues.json').write_text(json.dumps({'snapshot_timestamp':T,'discovery_date':'2026-10-04','rows':rows},indent=2))
def fixed_state():
 tag=hex(BLOCK);labels=[];requests=[];rows=[]
 for p in CASES[:3]:
  names=['asset()','totalAssets()','totalSupply()','decimals()','authority()','PLASMA_VAULT_BASE()','getFuses()','getPerformanceFeeData()','getManagementFeeData()','getPriceOracleMiddleware()','getRewardsClaimManagerAddress()','getWithdrawManager()'] if p['id']!='concrete-wsteth' else ['asset()','totalAssets()','totalSupply()','decimals()','owner()','allocateModule()','getStrategies()','getTotalAllocated()','getFeeConfig()','getHurdleRateOracle()','getUnwindCostCap()','isQueueActive()','paused()','getEpochState()']
  for sig in names:labels.append((p['id'],sig));requests.append(call(p['address'],sig,'',tag))
  if p['id']!='concrete-wsteth':
   labels.append((p['id'],'getBalanceFuseInfo(address)'));requests.append(call('0x870e1fb75bedbc2efb92857dc2b2cf171a0aec1f','getBalanceFuseInfo(address)',enc_addr(p['address']),tag))
   for mid in [1,12,14,19]:
    for sig in ['getMarketSubstrates(uint256)','totalAssetsInMarket(uint256)']:labels.append((p['id'],sig+':'+str(mid)));requests.append(call(p['address'],sig,enc_uint(mid),tag))
 rr=rpc('ethereum',requests,'initial_state_T');byid={r['id']:r for r in rr};named={p['id']:{} for p in CASES[:3]}
 for i,(pid,label) in enumerate(labels):named[pid][label]=byid.get(i+1,{})
 for p in CASES[:3]:rows.append(dict(p,block=BLOCK,raw=named[p['id']]))
 (DATA/'carry_variants_expansion_state_T.json').write_text(json.dumps({'target_timestamp':T,'products':rows},indent=2));print('Fixed-T state',len(rr),'responses',flush=True)
def positions():
 state=read('carry_variants_expansion_state_T');tag=hex(BLOCK);req=[];labels=[];out=[]
 for p in state['products'][:2]:
  for mid in words(p['raw']['getMarketSubstrates(uint256):14'].get('result'))[2:]:
   market='0x'+format(mid,'064x');row={'product_id':p['id'],'vault':p['address'],'market_id':market,'raw':{}};out.append(row)
   for sig,args,key in [('idToMarketParams(bytes32)',market[2:],'params'),('market(bytes32)',market[2:],'market'),('position(bytes32,address)',market[2:]+enc_addr(p['address']),'position')]:labels.append((len(out)-1,key));req.append(call(c.MORPHO,sig,args,tag))
 rr=rpc('ethereum',req,'morpho_positions_T');byid={r['id']:r for r in rr}
 for i,(j,k) in enumerate(labels):out[j]['raw'][k]=byid.get(i+1,{})
 req=[];labels=[];tokens=set()
 for j,r in enumerate(out):
  ps=words(r['raw']['params'].get('result'));mk=words(r['raw']['market'].get('result'))
  if not ps or not mk:continue
  r['loan_asset']='0x'+format(ps[0],'040x');r['collateral_asset']='0x'+format(ps[1],'040x');r['oracle']='0x'+format(ps[2],'040x');r['irm']='0x'+format(ps[3],'040x');r['lltv']=ps[4]/1e18;tokens|={r['loan_asset'],r['collateral_asset']}
  for addr,sig,args,key in [(r['oracle'],'price()','','oracle_price'),(r['irm'],'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',''.join(enc_uint(x) for x in ps+mk),'borrow_rate')]:labels.append((j,key));req.append(call(addr,sig,args,tag))
 rr=rpc('ethereum',req,'morpho_positions_oracles_rates_T');byid={r['id']:r for r in rr}
 for i,(j,k) in enumerate(labels):out[j]['raw'][k]=byid.get(i+1,{})
 labels=[];req=[];tr={}
 for tok in sorted(tokens):
  tr[tok]={}
  for sig in ['symbol()','decimals()','asset()','totalAssets()','totalSupply()']:
   labels.append((tok,sig));req.append(call(tok,sig,'',tag))
  for p in state['products'][:2]:labels.append((tok,'balanceOf:'+p['id']));req.append(call(tok,'balanceOf(address)',enc_addr(p['address']),tag))
 rr=rpc('ethereum',req,'underlying_tokens_T');byid={r['id']:r for r in rr}
 for i,(tok,k) in enumerate(labels):tr[tok][k]=byid.get(i+1,{})
 (DATA/'carry_variants_expansion_positions_T.json').write_text(json.dumps({'target_timestamp':T,'morpho_markets':out,'tokens':tr},indent=2));print('Morpho exact positions',len(out),'token identities',len(tr),flush=True)
 # Verified source identities are current discovery, while all balances above are T.
 urls=[('token_source_'+tok,'https://eth.blockscout.com/api/v2/smart-contracts/'+tok) for tok in sorted(tokens)]
 urls+=[('fusion_base_'+p['id'],'https://eth.blockscout.com/api/v2/smart-contracts/0x'+format(words(p['raw']['PLASMA_VAULT_BASE()'].get('result'))[0],'040x')) for p in state['products'][:2]]
 def worker(i):key,url=i;return {'key':key,'url':url,'response':capture(key,url)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:src=list(pool.map(worker,urls))
 (DATA/'carry_variants_expansion_identity_sources.json').write_text(json.dumps({'rows':src},indent=2))
 print('Underlying contract sources',len(src),flush=True)
def supplement():
 state=read('carry_variants_expansion_state_T');tag=hex(BLOCK);req=[];labels=[];named={}
 pool=read('carry_economics_aave_T')['markets'][0]['pool'];tokens=set()
 for p in state['products'][:2]:
  for mid in [7]:
   for sig in ['getMarketSubstrates(uint256)','totalAssetsInMarket(uint256)']:labels.append((p['id'],sig+':'+str(mid)));req.append(call(p['address'],sig,enc_uint(mid),tag))
  for sig in ['getInstantWithdrawalFuses()','getWithdrawManagerAddress()']:labels.append((p['id'],sig));req.append(call(p['address'],sig,'',tag))
  for mid in [12,19]:tokens|={('0x'+format(v,'040x'),p['id'],p['address']) for v in words(p['raw']['getMarketSubstrates(uint256):'+str(mid)].get('result'))[2:] if v<2**160}
 for token,pid,vault in sorted(tokens):
  for sig,args in [('balanceOf(address)',enc_addr(vault)),('symbol()',''),('decimals()',''),('asset()',''),('totalAssets()',''),('totalSupply()','')]:labels.append((pid,token+':'+sig));req.append(call(token,sig,args,tag))
 p=state['products'][1]
 for sig,args in [('getUserAccountData(address)',enc_addr(p['address']))]:labels.append((p['id'],'aave:'+sig));req.append(call(pool,sig,args,tag))
 for tok in ['0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2','0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48']:labels.append((p['id'],'aaveReserve:'+tok));req.append(call(pool,'getReserveData(address)',enc_addr(tok),tag))
 concrete=state['products'][2];strategy=words(concrete['raw']['getStrategies()'].get('result'))[2];addr='0x'+format(strategy,'040x');labels.append((concrete['id'],'getStrategyData:'+addr));req.append(call(concrete['address'],'getStrategyData(address)',enc_addr(addr),tag))
 rr=rpc('ethereum',req,'supplement_T');byid={r['id']:r for r in rr}
 for i,(pid,k) in enumerate(labels):named.setdefault(pid,{})[k]=byid.get(i+1,{})
 urls={'midas_registry':'https://docs.midas.app/resources/smart-contracts-registry','midas_product_legal':'https://docs.midas.app/resources/legal-product-documentation','midas_configuration':'https://midas.app/assets/src-CYJgf4Il.js','midas_repo_tree':'https://api.github.com/repos/midas-apps/contracts/git/trees/main?recursive=1','reservoir_docs':'https://docs.reservoir.xyz/','infinifi_docs':'https://docs.infinifi.xyz/','yearn_yeth_actual':'https://gov.yearn.fi/t/yeth-vault-strategy-w-uni-mining/5930','hgeth_primary_report':'https://curation.yearn.fi/report/kerneldao-hgeth/','concrete_strategy_source':'https://eth.blockscout.com/api/v2/smart-contracts/'+addr,'mhyper_source':'https://eth.blockscout.com/api/v2/smart-contracts/0x5a42864b14c0c8241ef5ab62dae975b163a2e0c1'}
 for tok in ['mre7eth','mhypereth']:urls['midas_'+tok+'_history']='https://api-prod.midas.app/api/data/'+tok+'/price?timestampFrom=1730419199000&timestampTo=1790985599000&environment=mainnet'
 def worker(i):key,url=i;return {'key':key,'url':url,'response':capture(key,url)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:src=list(executor.map(worker,urls.items()))
 (DATA/'carry_variants_expansion_supplement.json').write_text(json.dumps({'target_timestamp':T,'aave_pool':pool,'concrete_strategy':addr,'state':named,'sources':src},indent=2));print('Supplement',len(rr),'calls',len(src),'sources',flush=True)
def final_calls():
 st=read('carry_variants_expansion_state_T');sup=read('carry_variants_expansion_supplement');tag=hex(BLOCK);req=[];labels=[];out={}
 for p in st['products'][:2]:labels.append((p['id'],'withdraw_manager_storage'));req.append(('eth_getStorageAt',[p['address'],'0xb37e8684757599da669b8aea811ee2b3693b2582d2c730fab3f4965fa2ec3e11',tag]))
 p=st['products'][1]
 for key,r in sup['state'][p['id']].items():
  if key.startswith('aaveReserve:'):
   w=words(r.get('result'))
   for role,index in [('aToken',8),('variableDebtToken',10)]:
    token='0x'+format(w[index],'040x');labels.append((p['id'],key+':'+role));req.append(call(token,'balanceOf(address)',enc_addr(p['address']),tag))
 for tok,sigs in [('0xd3fd63209fa2d55b07a0f6db36c2f43900be3094',['apy()','cap()','compoundFactor()','currentRate()','lastTimestamp()','convertToAssets(uint256)']),('0xdbdc1ef57537e34680b898e1febd3d68c7389bcb',['paused()','yieldSharing()','core()','convertToAssets(uint256)'])]:
  for sig in sigs:labels.append(('destination',tok+':'+sig));req.append(call(tok,sig,enc_uint(10**18) if sig.endswith('(uint256)') else '',tag))
 rr=rpc('ethereum',req,'closure_probes_T');byid={r['id']:r for r in rr}
 for i,(pid,k) in enumerate(labels):out.setdefault(pid,{})[k]=byid.get(i+1,{})
 req=[];labels=[]
 for p in st['products'][:2]:
  w=words(out[p['id']]['withdraw_manager_storage'].get('result'));addr='0x'+format(w[0]%(2**160),'040x');out[p['id']]['withdraw_manager_address']=addr
  for sig in ['getWithdrawFee()','getRequestFee()','getWithdrawWindow()','getSharesToRelease()']:labels.append((p['id'],sig));req.append(call(addr,sig,'',tag))
 rr=rpc('ethereum',req,'withdraw_terms_T');byid={r['id']:r for r in rr}
 for i,(pid,k) in enumerate(labels):out[pid][k]=byid.get(i+1,{})
 blocks={r['chain']:r for r in read('snapshot_manifest')['chains']};midas=[{'id':'mre7eth','chain':'optimism','token':CASES[3]['address'],'oracle':'0xcffe26979e96b9e0454cc83aa03fc973c9eb0e5e','issuance':'0xc562f73add198ce47e9af5b0752de3d7c991225d','redemption':'0x2c8aee33a6b1ebdd047903b5fde01d71b8854e6d'},{'id':'mhypereth','chain':'ethereum','token':'0x5a42864b14c0c8241ef5ab62dae975b163a2e0c1','oracle':'0x5c81ee2c3ee8aaac2eef68ecb512472d9e08a0fd','issuance':'0x57b3be350c777892611cedc93bcf8c099a9ecdab','redemption':'0x15f724b35a75f0c28f352b952ea9d1b24e348c57'}]
 sources=[]
 for m in midas:
  tag=hex(blocks[m['chain']]['block']);labels=[];req=[]
  for role,signatures in [('token',['totalSupply()','decimals()','paused()','accessControl()']),('oracle',['getDataInBase18()','latestRoundData()','aggregator()']),('issuance',['tokensReceiver()','feeReceiver()','mTokenDataFeed()','instantFee()','instantDailyLimit()','minAmount()']),('redemption',['tokensReceiver()','feeReceiver()','mTokenDataFeed()','instantFee()','instantDailyLimit()','minAmount()'])]:
   for sig in signatures:labels.append(role+':'+sig);req.append(call(m[role],sig,'',tag))
  rr=rpc(m['chain'],req,'midas_'+m['id']+'_T');byid={r['id']:r for r in rr};m['block']=blocks[m['chain']];m['raw']={k:byid.get(i+1,{}) for i,k in enumerate(labels)}
  base='https://optimism.blockscout.com' if m['chain']=='optimism' else 'https://eth.blockscout.com'
  for role in ['oracle','issuance','redemption']:sources.append({'key':m['id']+'_'+role+'_source','url':base+'/api/v2/smart-contracts/'+m[role],'response':capture(m['id']+'_'+role+'_source',base+'/api/v2/smart-contracts/'+m[role])})
  for field in ['oracle:aggregator()','issuance:mTokenDataFeed()']:
   w=words(m['raw'][field].get('result'))
   if w:
    a='0x'+format(w[0],'040x');rr=rpc(m['chain'],[call(a,'latestRoundData()','',tag),call(a,'getDataInBase18()','',tag)],'midas_'+m['id']+'_'+field.replace(':','_')+'_T');m[field+'_follow']={'address':a,'responses':rr}
  priceurl='https://api-prod.midas.app/api/data/'+m['id']+'/price?timestampFrom=1730419199&timestampTo=1790985599&environment=mainnet';sources.append({'key':m['id']+'_dated_prices','url':priceurl,'response':capture(m['id']+'_dated_prices',priceurl)})
 # The strategy's current verified implementation identifies its accounting
 # design. The strategy address and product allocation came from exact T calls.
 urls=[('concrete_multisig_implementation','https://eth.blockscout.com/api/v2/smart-contracts/0x1cef0d42eecc0f12747a5db2b42b5d81c04d3a32')]
 for key,url in urls:sources.append({'key':key,'url':url,'response':capture(key,url)})
 (DATA/'carry_variants_expansion_final_calls.json').write_text(json.dumps({'target_timestamp':T,'fusion':out,'midas':midas,'sources':sources},indent=2));print('Final product state and oracle terms',flush=True)
def verify_extension():
 state=read('carry_variants_expansion_state_T');old=read('carry_category_candidates');pos=read('carry_variants_expansion_positions_T');fin=read('carry_variants_expansion_final_calls');tag=hex(BLOCK);req=[];labels=[];named={};slot='0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'
 strategy=read('carry_variants_expansion_supplement')['concrete_strategy']
 for sig in ['getMultiSig()','totalAllocatedValue()','getAccountingValidityPeriod()','getCooldownPeriod()','getLastUpdatedTimestamp()','getMaxAccountingChangeThreshold()','maxWithdraw()']:
  labels.append(('concrete',sig));req.append(call(strategy,sig,'',tag))
 for a in [strategy,CASES[2]['address']]:labels.append(('concrete','implementation:'+a));req.append(('eth_getStorageAt',[a,slot,tag]))
 for mid in [m for m in fin['midas'] if m['chain']=='ethereum']:
  labels.append((mid['id'],'oracle_decimals'));req.append(call(mid['oracle'],'decimals()','',tag))
  labels.append((mid['id'],'fee_denominator'));req.append(call(mid['redemption'],'ONE_HUNDRED_PERCENT()','',tag))
  a=address_from_response(mid['raw']['redemption:mTokenDataFeed()']);labels.append((mid['id'],'feed_value'));req.append(call(a,'getDataInBase18()','',tag))
 rr=rpc('ethereum',req,'verification_extension_T');byid={r['id']:r for r in rr}
 for i,(pid,k) in enumerate(labels):named.setdefault(pid,{})[k]=byid.get(i+1,{})
 m=fin['midas'][0];rr=rpc('optimism',[call(m['oracle'],'decimals()','',hex(m['block']['block'])),call(m['redemption'],'ONE_HUNDRED_PERCENT()','',hex(m['block']['block']))],'mre7_oracle_decimals_T');named.setdefault('mre7eth',{})['oracle_decimals']=rr[0] if rr else {};named['mre7eth']['fee_denominator']=rr[1] if len(rr)>1 else {}
 hist=[]
 for pid in ['tau-infinifi','reservoir-eth']:
  p=next(p for p in old['products'] if p['address']==next(c['address'] for c in CASES if c['id']==pid));valid=[r for r in p['history'] if r.get('sizeUSD') is not None];dates=[max(valid,key=lambda r:r['sizeUSD']),valid[-1]]
  for d in dates:
   req=[];labels=[];markets=[m for m in pos['morpho_markets'] if m['product_id']==pid];tag=hex(d['block']);row={'product_id':pid,'month':d['month'],'block':d['block'],'timestamp':d['timestamp'],'book_usd':d['sizeUSD'],'scope':'Two selected historical checkpoints in markets authorized at T. Earlier alternate markets and transaction-level cash provenance are not fully reconstructed.','raw':{}}
   for market in markets:
    mid=market['market_id']
    for sig,args,k in [('position(bytes32,address)',mid[2:]+enc_addr(p['address']),'position'),('market(bytes32)',mid[2:],'market')]:labels.append(mid+':'+k);req.append(call(c.MORPHO,sig,args,tag))
   if pid=='reservoir-eth':labels.append('aave_account');req.append(call(read('carry_variants_expansion_supplement')['aave_pool'],'getUserAccountData(address)',enc_addr(p['address']),tag))
   rr=rpc('ethereum',req,'history_'+pid+'_'+d['month']);byid={r['id']:r for r in rr};row['raw']={k:byid.get(i+1,{}) for i,k in enumerate(labels)};hist.append(row)
 src=[]
 for m in fin['midas']:
  d=next(r['response'] for r in fin['sources'] if r['key']==m['id']+'_redemption_source');base='https://optimism.blockscout.com' if m['chain']=='optimism' else 'https://eth.blockscout.com'
  for impl in d.get('implementations',[]):
   a=impl.get('address_hash') or impl.get('address');url=base+'/api/v2/smart-contracts/'+a;src.append({'key':m['id']+'_redemption_implementation','url':url,'response':capture(m['id']+'_redemption_implementation',url)})
 (DATA/'carry_variants_expansion_verification_extension.json').write_text(json.dumps({'state':named,'historical_checkpoints':hist,'sources':src},indent=2));print('Bounded extension',len(hist),'historical checkpoints',flush=True)
def address_from_response(r):return '0x'+format(words(r.get('result'))[0],'040x')
if __name__=='__main__':verify_extension() if '--verify-extension' in sys.argv else final_calls() if '--final-calls' in sys.argv else supplement() if '--supplement' in sys.argv else positions() if '--positions' in sys.argv else fixed_state() if '--state' in sys.argv else catalogue() if '--catalogue' in sys.argv else bootstrap()
