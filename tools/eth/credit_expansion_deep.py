"""Bounded borrower lifecycle research. All financial observations remain at/before T."""
import json,sys,datetime as dt,urllib.parse,concurrent.futures
from pathlib import Path
import credit_expansion_capture as c
from credit_expansion_build import event,words,string
ROOT=c.ROOT;D=c.D;OLDRAW=c.RAW
c.RAW=ROOT/'raw/eth/credit-expansion-2026-10-04/deep'
RAW=c.RAW
MORPHO='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
A='0xa122687285dc5012141055a801045f069112e7c6'
B='0x4f87de7d21aef48090958f7342e1f69dff790545'
V1='0x2ca22cb25558fa2018ecb1ce4ed8af92ee7ea423'
V2='0x8381a156958711e230f325428b5eb4b6555c75d9'
ZERO='0x0000000000000000000000000000000000000000'
TXS={'A_redeem':'0x324c54a149f5fcdcd2cf22bf1dd338decfb06d767cedb5b5117758f7221430aa','A_first_deposit':'0x0b27c32083b7d0858e249d8bf164582dc035ae0fcd75e37dabd0c5c7243ececa','A_cash_out':'0x0bea263b3cee1f5d58d96a5ee5b25d830c8959d01123d58d497ee40b41889328','B_redeem':'0x72df97be87198f5077b3ad8f050b7ccef35157653649d3f4774162ce49923e98','B_repay':'0x1dc143ab1082e0ab4c2e5f94515a6c0ea9e9182c66606ebb8db21c16e7ecfe13'}

def old_record(key):
 rows=[json.loads(x) for x in (OLDRAW/'requests.jsonl').read_text().splitlines()]
 r=next(x for x in reversed(rows) if x['key']==key and x['http_status']==200)
 return r,json.loads((ROOT/r['path']).read_text())
def call(to,sig,args='',block=None):
 return ('eth_call',[{'to':to,'data':'0x'+c.sel(sig)+args},hex(block or c.BLOCKS['ethereum'])])
def sources():
 return [json.loads(x) for x in (RAW/'requests.jsonl').read_text().splitlines()] if (RAW/'requests.jsonl').exists() else []

def capture():
 v=json.loads((D/'credit_expansion.json').read_text());alltx={**TXS}
 for b in v['borrowers']:
  if b['address'] not in [A,B]:continue
  for p in b['proceeds']:
   if any(f['yield_vault_deposits_to_borrower'] for f in p['following_same_token_transfers']):
    alltx['borrow_'+p['borrow_transaction'][:12]]=p['borrow_transaction']
    for f in p['following_same_token_transfers']:
     if f['yield_vault_deposits_to_borrower']:alltx['deposit_'+f['transaction'][:12]]=f['transaction']
 calls=[('eth_getTransactionReceipt',[tx]) for tx in alltx.values()];rr,ss=c.batches('ethereum',calls,'lifecycle_receipts');receipts=[]
 for (label,tx),r in zip(alltx.items(),rr):receipts.append({'label':label,'transaction':tx,'response':r})
 blocks=sorted({int(x['response']['result']['blockNumber'],16) for x in receipts if x['response'].get('result')});rr,ss2=c.batches('ethereum',[('eth_getBlockByNumber',[hex(b),False]) for b in blocks],'lifecycle_blocks');ss+=ss2
 bs={str(b):r for b,r in zip(blocks,rr)}
 (D/'credit_expansion_deep_capture.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'transactions':receipts,'blocks':bs,'sources':ss},indent=2))
 jobs=[('silo_v1_tree','https://api.github.com/repos/silo-finance/silo-core-v1/git/trees/master?recursive=1'),('silo_v1_changelog','https://raw.githubusercontent.com/silo-finance/silo-core-v1/master/CHANGELOG.md')]
 for addr in ['0xe978f22157048e5db8e5d07971376e86671672b2']:
  jobs.append(('counterparty_'+addr,'https://eth.blockscout.com/api/v2/addresses/'+addr))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(lambda j:c.capture(*j),jobs))

def state():
 v=json.loads((D/'credit_expansion_deep_capture.json').read_text());labels=[];calls=[]
 for tx in v['transactions']:
  r=tx['response'].get('result')
  if not r:continue
  block=int(r['blockNumber'],16);label=tx['label'];wallet=A if label.startswith('A') or any(A[2:] in t for l in r['logs'] for t in l['topics']) else B;vault=V1 if wallet==A else V2
  for height,when in [(block-1,'before'),(block,'after')]:
   for sig,args in [('balanceOf(address)',c.enc_addr(wallet)),('convertToAssets(uint256)',c.enc_uint(10**18)),('totalAssets()',''),('totalSupply()','')]:labels.append({'transaction':tx['transaction'],'label':label,'wallet':wallet,'vault':vault,'when':when,'block':height,'signature':sig});calls.append(call(vault,sig,args,height))
   ids={e['market_id'] for l in r['logs'] if (e:=event(l))};ids.add('0xb8fef900b383db2dbbf4458c7f46acf5b140f26d603a6d1829963f241b82510e' if wallet==A else '0x85d59152eeeab7ca024804895b358868d8dd1e134171be400d7792d5604a212c')
   for id in ids:
    for sig,args in [('market(bytes32)',id[2:]),('idToMarketParams(bytes32)',id[2:]),('position(bytes32,address)',id[2:]+c.enc_addr(wallet))]:labels.append({'transaction':tx['transaction'],'label':label,'wallet':wallet,'market_id':id,'when':when,'block':height,'signature':sig});calls.append(call(MORPHO,sig,args,height))
 labels.append({'signature':'eth_getCode','address':'0xe978f22157048e5db8e5d07971376e86671672b2','block':c.BLOCKS['ethereum']});calls.append(('eth_getCode',['0xe978f22157048e5db8e5d07971376e86671672b2',hex(c.BLOCKS['ethereum'])]))
 rr,ss=c.batches('ethereum',calls,'lifecycle_states')
 for l,r in zip(labels,rr):l['response']=r
 (D/'credit_expansion_deep_state.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'labels':labels,'sources':ss},indent=2))

def silo_sources():
 jobs=[('silo_v1_repository_'+chain,'https://raw.githubusercontent.com/silo-finance/silo-core-v1/master/deployments/'+chain+'/SiloRepository.json') for chain in ['mainnet','arbitrum']]
 jobs += [('silo_v1_lens_'+chain,'https://raw.githubusercontent.com/silo-finance/silo-core-v1/master/deployments/'+chain+'/SiloLens.json') for chain in ['mainnet','arbitrum']]
 jobs += [('silo_v1_silo_source','https://raw.githubusercontent.com/silo-finance/silo-core-v1/master/contracts/Silo.sol'),('silo_v1_interface_source','https://raw.githubusercontent.com/silo-finance/silo-core-v1/master/contracts/interfaces/ISilo.sol')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(lambda j:c.capture(*j),jobs))

def raw_latest(key):
 rows=sources();r=next(x for x in reversed(rows) if x['key']==key and x['http_status']==200);return r,json.loads((ROOT/r['path']).read_text())

def funding():
 v=json.loads((D/'credit_expansion_deep_state.json').read_text());labels=[];calls=[]
 for txlabel in ['A_redeem','A_cash_out']:
  ls=[x for x in v['labels'] if x.get('label')==txlabel and x.get('when')=='after' and x.get('market_id')=='0xb8fef900b383db2dbbf4458c7f46acf5b140f26d603a6d1829963f241b82510e'];vals={x['signature']:words(x['response'].get('result')) for x in ls};p=vals['idToMarketParams(bytes32)'];m=vals['market(bytes32)'];irm='0x'+format(p[3],'040x');args=''.join(c.enc_uint(n) for n in p+m)
  labels.append({'label':txlabel,'block':ls[0]['block'],'market_id':ls[0]['market_id'],'market_params':p,'stored_market':m,'irm':irm,'signature':'borrowRateView'});calls.append(call(irm,'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',args,ls[0]['block']))
 for wallet,vault,id in [(A,V1,'0xb8fef900b383db2dbbf4458c7f46acf5b140f26d603a6d1829963f241b82510e'),(B,V2,'0x85d59152eeeab7ca024804895b358868d8dd1e134171be400d7792d5604a212c')]:
  for sig,to,args in [('position(bytes32,address)',MORPHO,id[2:]+c.enc_addr(wallet)),('market(bytes32)',MORPHO,id[2:]),('convertToAssets(uint256)',vault,c.enc_uint(10**18)),('balanceOf(address)',vault,c.enc_addr(wallet))]:labels.append({'label':'T','wallet':wallet,'vault':vault,'market_id':id,'block':c.BLOCKS['ethereum'],'signature':sig});calls.append(call(to,sig,args))
 rr,ss=c.batches('ethereum',calls,'funding_and_terminal')
 for l,r in zip(labels,rr):l['response']=r
 (D/'credit_expansion_deep_funding.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'labels':labels,'sources':ss},indent=2))
 c.capture('morpho_accrual_source','https://raw.githubusercontent.com/morpho-org/morpho-blue/main/src/Morpho.sol');c.capture('morpho_math_source','https://raw.githubusercontent.com/morpho-org/morpho-blue/main/src/libraries/MathLib.sol')

def silo_legacy():
 _,repo=raw_latest('silo_v1_repository_mainnet');_,lens=raw_latest('silo_v1_lens_mainnet');labels=[];calls=[]
 tokens={'wstETH':'0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','stETH':'0xae7ab96520de3a18e5e111b5eaab095312d7fe84','rETH':'0xae78736cd615f374d3085123a210448e74fc6393','weETH':'0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','WETH':'0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'}
 for symbol,asset in tokens.items():labels.append({'symbol':symbol,'asset':asset,'signature':'getSilo(address)'});calls.append(call(repo['address'],'getSilo(address)',c.enc_addr(asset)))
 labels.append({'signature':'getBridgeAssets()'});calls.append(call(repo['address'],'getBridgeAssets()'))
 rr,ss=c.batches('ethereum',calls,'silo_v1_routes')
 for l,r in zip(labels,rr):l['response']=r
 _,arb=raw_latest('silo_v1_repository_arbitrum')
 for url in ['https://arbitrum-one-rpc.publicnode.com','https://arbitrum.blockpi.network/v1/rpc/public']:
  r,v=c.capture('silo_arb_archive_probe_'+url.split('/')[2],url,{'jsonrpc':'2.0','id':1,'method':'eth_call','params':[{'to':arb['address'],'data':'0x'+c.sel('getBridgeAssets()')},hex(c.BLOCKS['arbitrum'])]});ss.append(r)
  if isinstance(v,dict) and v.get('result'):print('Archive available',url,flush=True)
 bridges=c.array_addresses(labels[-1]['response'].get('result'));more=[];calls=[]
 for b in bridges:
  for sig in ['symbol()','decimals()']:more.append({'asset':b,'signature':sig});calls.append(call(b,sig))
 for l in labels[:-1]:
  r=l['response'].get('result')
  if not r or r=='0x' or int(r,16)==0:continue
  silo='0x'+r[-40:]
  for asset in bridges+[l['asset']]:
   for sig,args,to in [('assetConfigs(address,address)',c.enc_addr(silo)+c.enc_addr(asset),repo['address']),('isSiloPaused(address,address)',c.enc_addr(silo)+c.enc_addr(asset),repo['address']),('totalBorrowAmountWithInterest(address,address)',c.enc_addr(silo)+c.enc_addr(asset),lens['address']),('totalDepositsWithInterest(address,address)',c.enc_addr(silo)+c.enc_addr(asset),lens['address']),('borrowAPY(address,address)',c.enc_addr(silo)+c.enc_addr(asset),lens['address'])]:more.append({'collateral_symbol':l['symbol'],'silo':silo,'asset':asset,'signature':sig});calls.append(call(to,sig,args))
 rr,ss2=c.batches('ethereum',calls,'silo_v1_states');ss+=ss2
 for l,r in zip(more,rr):l['response']=r
 (D/'credit_expansion_deep_silo_legacy.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'repository':repo['address'],'lens':lens['address'],'labels':labels+more,'sources':ss,'scope':'Five selected Ethereum ETH-family assets in official Silo V1 repository. Bridge-asset loan totals are market-wide, not an allocation to particular collateral accounts.'},indent=2))

def wrapper():
 addr='0xe978f22157048e5db8e5d07971376e86671672b2';slot='0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc';labels=[];calls=[]
 for sig in ['underlying()','name()','symbol()','rate()','decimals()','nonConfidentialTotalSupply()']:
  labels.append({'signature':sig,'block':c.BLOCKS['ethereum']});calls.append(call(addr,sig))
 labels.append({'signature':'EIP1967_implementation','block':c.BLOCKS['ethereum']});calls.append(('eth_getStorageAt',[addr,slot,hex(c.BLOCKS['ethereum'])]))
 labels.append({'signature':'cash_out_transaction'});calls.append(('eth_getTransactionByHash',[TXS['A_cash_out']]))
 rr,ss=c.batches('ethereum',calls,'confidential_wrapper_T')
 for l,r in zip(labels,rr):l['response']=r
 (D/'credit_expansion_deep_wrapper.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'wrapper':addr,'labels':labels,'sources':ss},indent=2))
 jobs=[('zama_official_registry','https://raw.githubusercontent.com/zama-ai/protocol-apps/main/docs/addresses/mainnet/ethereum.md'),('zama_official_explanation','https://www.zama.org/confidential-tokens'),('zama_wrapper_verified_source','https://eth.blockscout.com/api/v2/smart-contracts/'+addr)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(lambda j:c.capture(*j),jobs))

def fees_sources():
 jobs=[('yield_vault_verified_'+v,'https://eth.blockscout.com/api/v2/smart-contracts/'+v) for v in [V1,V2]]
 jobs += [('vault_v2_official_source','https://raw.githubusercontent.com/morpho-org/vault-v2/main/src/VaultV2.sol'),('zama_official_wrapper_source','https://raw.githubusercontent.com/zama-ai/protocol-apps/main/contracts/confidential-token/ConfidentialWrapper.sol')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(lambda j:c.capture(*j),jobs))
 labels=[];calls=[];cap=json.loads((D/'credit_expansion_deep_capture.json').read_text())
 for v,label in [(V1,'A_redeem'),(V2,'B_redeem')]:
  tx=next(x for x in cap['transactions'] if x['label']==label);r=tx['response']['result'];b=int(r['blockNumber'],16);topic='0x'+__import__('keccak_lib').keccak(b'Withdraw(address,address,address,uint256,uint256)').hex();e=next(x for x in r['logs'] if x['address']==v and x['topics'][0]==topic);shares=words(e['data'])[1]
  for height,when in [(b-1,'before_exit'),(b,'after_exit'),(c.BLOCKS['ethereum'],'T')]:
   for sig,args in [('previewRedeem(uint256)',c.enc_uint(shares)),('convertToAssets(uint256)',c.enc_uint(shares)),('managementFee()',''),('performanceFee()',''),('owner()','')]:labels.append({'vault':v,'label':label,'signature':sig,'when':when,'block':height,'shares_raw':str(shares)});calls.append(call(v,sig,args,height))
 for sig in ['owner()','pauser()','paused()','getObservers()','observers()']:
  labels.append({'vault':'0xe978f22157048e5db8e5d07971376e86671672b2','signature':sig,'when':'T','block':c.BLOCKS['ethereum']});calls.append(call(labels[-1]['vault'],sig))
 rr,ss=c.batches('ethereum',calls,'exit_fee_and_control_reads')
 for l,r in zip(labels,rr):l['response']=r
 (D/'credit_expansion_deep_fees.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'labels':labels,'sources':ss,'interpretation':'Compare actual cash with historical preview and conversion. Getter absence is unknown, not zero. Before-block discrepancies can include twelve seconds of accrual and realized allocation changes.'},indent=2))

def controls_sources():
 jobs=[('zama_implementation_verified_source','https://eth.blockscout.com/api/v2/smart-contracts/0x2abad2203eba104b52cf040cccfa100df15687f8'),('zama_protocol_apps_tree','https://api.github.com/repos/zama-ai/protocol-apps/git/trees/main?recursive=1'),('zama_wrapper_official_source','https://raw.githubusercontent.com/zama-ai/protocol-apps/main/contracts/confidential-wrapper/contracts/ConfidentialWrapper.sol'),('zama_wrapper_official_documentation','https://raw.githubusercontent.com/zama-ai/protocol-apps/main/docs/confidential-wrapper.md')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:list(p.map(lambda j:c.capture(*j),jobs))
 labels=[{'address':v,'block':c.BLOCKS['ethereum']} for v in [V1,V2,'0x2abad2203eba104b52cf040cccfa100df15687f8']]
 rr,ss=c.batches('ethereum',[('eth_getCode',[l['address'],hex(l['block'])]) for l in labels],'verified_code_T')
 for l,r in zip(labels,rr):l['response']=r
 (D/'credit_expansion_deep_bytecode.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'labels':labels,'sources':ss},indent=2))

def compound_retry():
 path=D/'credit_expansion_compound_T.json';original=json.loads(path.read_text());out=json.loads(json.dumps(original));chain=next(x for x in out['chains'] if x['chain']=='arbitrum');labels=chain['labels'];sources=[];pending=[x for x in labels if x['response'].get('result') in [None,'0x']]
 c.RPCS['arbitrum']=['https://arbitrum-one.public.blastapi.io']+c.RPCS['arbitrum']
 def batch(ls,key):
  rr,ss=c.batches('arbitrum',[c.ethcall(x['market_id'],x['signature'],x.get('args',''),chain='arbitrum') for x in ls],key);sources.extend(ss)
  for x,r in zip(ls,rr):x['response']=r
 batch(pending,'compound_retry_initial_arbitrum');extra=[]
 for address in sorted({x['market_id'] for x in labels}):
  ls=[x for x in labels if x['market_id']==address];values={x['signature']:x['response'].get('result') for x in ls};common={k:ls[0][k] for k in ['chain','market_id','registry_path']}
  if values['numAssets()'] not in [None,'0x']:
   for i in range(int(values['numAssets()'],16)):extra.append({**common,'signature':'getAssetInfo(uint8)','index':i,'args':c.enc_uint(i)})
  if values['getUtilization()'] not in [None,'0x']:
   for sig in ['getBorrowRate(uint256)','getSupplyRate(uint256)']:extra.append({**common,'signature':sig,'args':c.enc_uint(int(values['getUtilization()'],16))})
 batch(extra,'compound_retry_assets_arbitrum');more=[];calls=[]
 for x in extra:
  if x['signature']!='getAssetInfo(uint8)' or x['response'].get('result') in [None,'0x']:continue
  vals=words(x['response']['result']);token='0x'+format(vals[1],'040x');feed='0x'+format(vals[2],'040x');common={k:x[k] for k in ['chain','market_id','registry_path']}
  for sig,to,args in [('symbol()',token,''),('decimals()',token,''),('totalsCollateral(address)',x['market_id'],c.enc_addr(token)),('getPrice(address)',x['market_id'],c.enc_addr(feed))]:more.append({**common,'asset':token,'signature':sig});calls.append(c.ethcall(to,sig,args,chain='arbitrum'))
 rr,ss=c.batches('arbitrum',calls,'compound_retry_collateral_arbitrum');sources.extend(ss)
 for x,r in zip(more,rr):x['response']=r
 code_calls=[('eth_getCode',[address,hex(c.BLOCKS['arbitrum'])]) for address in sorted({x['market_id'] for x in labels})];rr,ss=c.batches('arbitrum',code_calls,'compound_retry_code_arbitrum');sources.extend(ss)
 codes=[{'address':call[1][0],'response':r} for call,r in zip(code_calls,rr)]
 chain['labels']+=extra+more;chain['sources']+=sources
 measured=sum(x['signature']=='totalBorrow()' and x['response'].get('result') not in [None,'0x'] for x in labels)
 result={'financial_snapshot_timestamp':c.T,'chain':'arbitrum','block':c.BLOCKS['arbitrum'],'markets_measured':measured,'codes':codes,'patched_only_failed_initial_fields':True,'original_good_chains_preserved':all(x==next(y for y in original['chains'] if y['chain']==x['chain']) for x in out['chains'] if x['chain']!='arbitrum'),'sources':sources,'updated_chain':chain}
 (D/'credit_expansion_deep_compound_retry.json').write_text(json.dumps(result,indent=2))
 if measured:path.write_text(json.dumps(out,indent=2))
 print('Compound Arbitrum markets measured:',measured,flush=True)

def silo_arb_retry():
 _,repo=raw_latest('silo_v1_repository_arbitrum');_,lens=raw_latest('silo_v1_lens_arbitrum');factory='0xAFd8F792cb025A76C4916652CfC8e20eee3b6fe2';labels=[];calls=[];sources=[]
 c.RPCS['arbitrum']=['https://arbitrum-one.public.blastapi.io']+c.RPCS['arbitrum']
 markets=json.loads((D/'credit_expansion.json').read_text())['markets'];tokens={a['symbol']:a['asset_address'] for m in markets if m['protocol']=='Compound V3' and m['chain']=='arbitrum' for a in m['ETH_collateral_routes']}
 for address,sig in [(repo['address'],'getBridgeAssets()'),(factory,'getNextSiloId()')]:labels.append({'address':address,'signature':sig});calls.append(c.ethcall(address,sig,chain='arbitrum'))
 for symbol,asset in tokens.items():labels.append({'address':repo['address'],'asset':asset,'symbol':symbol,'signature':'getSilo(address)'});calls.append(c.ethcall(repo['address'],'getSilo(address)',c.enc_addr(asset),chain='arbitrum'))
 rr,ss=c.batches('arbitrum',calls,'silo_arb_retry_registry');sources+=ss
 for l,r in zip(labels,rr):l['response']=r
 n=next(l['response'].get('result') for l in labels if l['signature']=='getNextSiloId()');n=int(n,16) if n not in [None,'0x'] else None;ids=list(range(3000,n)) if n is not None and n<=3050 else [];configs=[]
 if ids:
  rr,ss=c.batches('arbitrum',[c.ethcall(factory,'idToSiloConfig(uint256)',c.enc_uint(i),chain='arbitrum') for i in ids],'silo_arb_retry_factory_ids');sources+=ss
  configs=[{'id':i,'response':r} for i,r in zip(ids,rr)]
 bridges=c.array_addresses(next(l['response'].get('result') for l in labels if l['signature']=='getBridgeAssets()'));more=[];calls=[]
 for b in bridges:
  for sig in ['symbol()','decimals()']:more.append({'address':b,'asset':b,'signature':sig});calls.append(c.ethcall(b,sig,chain='arbitrum'))
 for l in labels:
  if l['signature']!='getSilo(address)' or not l['response'].get('result') or not int(l['response']['result'],16):continue
  silo='0x'+l['response']['result'][-40:]
  for asset in bridges:
   for sig,to in [('totalBorrowAmountWithInterest(address,address)',lens['address']),('totalDepositsWithInterest(address,address)',lens['address']),('borrowAPY(address,address)',lens['address']),('isSiloPaused(address,address)',repo['address'])]:more.append({'address':to,'silo':silo,'collateral_symbol':l['symbol'],'asset':asset,'signature':sig});calls.append(c.ethcall(to,sig,c.enc_addr(silo)+c.enc_addr(asset),chain='arbitrum'))
 rr,ss=c.batches('arbitrum',calls,'silo_arb_retry_states');sources+=ss
 for l,r in zip(more,rr):l['response']=r
 codes=[('eth_getCode',[a,hex(c.BLOCKS['arbitrum'])]) for a in [repo['address'],lens['address'],factory]];rr,ss=c.batches('arbitrum',codes,'silo_arb_retry_code');sources+=ss
 result={'financial_snapshot_timestamp':c.T,'chain':'arbitrum','block':c.BLOCKS['arbitrum'],'repository':repo['address'],'lens':lens['address'],'factory':factory,'next_silo_id':n,'factory_configs':configs,'factory_enumeration_complete':n is not None and n<=3050,'labels':labels+more,'codes':[{'address':p[1][0],'response':r} for p,r in zip(codes,rr)],'sources':sources,'scope':'Existing official V1 repository and lens plus the previously queried current factory generation. Selected ETH assets come from the measured official Compound Arbitrum collateral routes. Not all Silo generations or assets.'}
 (D/'credit_expansion_deep_silo_arb_retry.json').write_text(json.dumps(result,indent=2));print('Silo Arbitrum next ID:',n,'nonzero sampled V1 entries:',sum(l['signature']=='getSilo(address)' and bool(l['response'].get('result')) and int(l['response']['result'],16)>0 for l in labels),flush=True)

def silo_arb_pairs():
 path=D/'credit_expansion_deep_silo_arb_retry.json';v=json.loads(path.read_text());c.RPCS['arbitrum']=['https://arbitrum-one.public.blastapi.io'];configs=[{'id':x['id'],'config':'0x'+x['response']['result'][-40:]} for x in v['factory_configs'] if x['response'].get('result') and int(x['response']['result'],16)];sources=[]
 rr,ss=c.batches('arbitrum',[c.ethcall(x['config'],'getSilos()',chain='arbitrum') for x in configs],'silo_arb_retry_pairs');sources+=ss
 for x,r in zip(configs,rr):x['pair_response']=r;x['silos']=['0x'+format(a,'040x') for a in words(r.get('result'))] if r.get('result') else []
 calls=[c.ethcall(address,'asset()',chain='arbitrum') for x in configs for address in x['silos']];rr,ss=c.batches('arbitrum',calls,'silo_arb_retry_pair_assets');sources+=ss;assets={address:'0x'+r['result'][-40:] for address,r in zip([a for x in configs for a in x['silos']],rr) if r.get('result') not in [None,'0x']};tokens=sorted(set(assets.values()));labels=[];calls=[]
 for a in tokens:
  for sig in ['symbol()','decimals()']:labels.append({'asset':a,'signature':sig});calls.append(c.ethcall(a,sig,chain='arbitrum'))
 rr,ss=c.batches('arbitrum',calls,'silo_arb_retry_pair_metadata');sources+=ss
 for l,r in zip(labels,rr):l['response']=r
 v['current_factory_pairs']=configs;v['current_factory_assets']=assets;v['current_factory_token_metadata']=labels;v['sources']+=sources;path.write_text(json.dumps(v,indent=2));c.capture('silo_v2_interface_source','https://raw.githubusercontent.com/silo-finance/silo-contracts-v2/master/silo-core/contracts/interfaces/ISilo.sol')
 print('Current factory resolved configs:',len(configs),flush=True)

def silo_arb_credit():
 path=D/'credit_expansion_deep_silo_arb_retry.json';v=json.loads(path.read_text());c.RPCS['arbitrum']=['https://arbitrum-one.public.blastapi.io'];labels=[];calls=[]
 for x in v['current_factory_pairs']:
  tokens=[v['current_factory_assets'][a] for a in x['silos']]
  if set(tokens)!={'0x82af49447d8a07e3bd95bd0d56f35241523fbab1','0xaf88d065e77c8cc2239327c5edb3a432268e5831'}:continue
  for address,asset in zip(x['silos'],tokens):
   for sig in ['getDebtAssets()','getCollateralAssets()','getSiloStorage()']:
    labels.append({'id':x['id'],'config':x['config'],'silo':address,'asset':asset,'signature':sig});calls.append(c.ethcall(address,sig,chain='arbitrum'))
   labels.append({'id':x['id'],'config':x['config'],'silo':address,'asset':asset,'signature':'getConfig(address)'});calls.append(c.ethcall(x['config'],'getConfig(address)',c.enc_addr(address),chain='arbitrum'))
 rr,ss=c.batches('arbitrum',calls,'silo_arb_retry_credit')
 for l,r in zip(labels,rr):l['response']=r
 v['current_factory_credit_states']=labels;v['sources']+=ss;path.write_text(json.dumps(v,indent=2))
 for key,url in [('silo_v2_config_interface_source','https://raw.githubusercontent.com/silo-finance/silo-contracts-v2/master/silo-core/contracts/interfaces/ISiloConfig.sol'),('silo_v2_silo_source','https://raw.githubusercontent.com/silo-finance/silo-contracts-v2/master/silo-core/contracts/Silo.sol')]:c.capture(key,url)

def destination_metadata():
 states=json.loads((D/'credit_expansion_deep_state.json').read_text());ids=['0x17f7ae1b52670010976b3fe41324cbb2b1eb7dd8f492e51764b2828371b86b84','0xb4977179610abfecfc8b76255a002c16b33f46d077beb86e5911e1fe9ee6e512'];labels=[];calls=[]
 for mid in ids:
  x=next(l for l in states['labels'] if l.get('market_id')==mid and l['signature']=='idToMarketParams(bytes32)');params=words(x['response']['result']);asset='0x'+format(params[1],'040x')
  for sig in ['name()','symbol()','decimals()']:labels.append({'market_id':mid,'asset':asset,'signature':sig,'block':c.BLOCKS['ethereum']});calls.append(call(asset,sig))
 rr,ss=c.batches('ethereum',calls,'destination_credit_metadata')
 for l,r in zip(labels,rr):l['response']=r
 (D/'credit_expansion_deep_destination_metadata.json').write_text(json.dumps({'financial_snapshot_timestamp':c.T,'labels':labels,'sources':ss},indent=2))

def public_boundary():
 from keccak_lib import keccak
 addr='0xe978f22157048e5db8e5d07971376e86671672b2';start=25990373;end=c.BLOCKS['ethereum'];wallet='0x'+c.enc_addr(A);topic=lambda sig:'0x'+keccak(sig.encode()).hex();queries=[('confidential_from_wallet',[topic('ConfidentialTransfer(address,address,bytes32)'),wallet]),('confidential_to_wallet',[topic('ConfidentialTransfer(address,address,bytes32)'),None,wallet]),('wrap_to_wallet',[topic('Wrap(address,uint256,bytes32)'),wallet]),('unwrap_to_wallet',[topic('UnwrapFinalized(address,bytes32,bytes32,uint64)'),wallet]),('public_amount_disclosures',[topic('AmountDisclosed(bytes32,uint64)')])];c.RPCS['ethereum']=['https://gateway.tenderly.co/public/mainnet','https://ethereum-rpc.publicnode.com','https://eth.drpc.org'];labels=[];calls=[]
 for key,topics in queries:labels.append({'kind':key,'from_block':start,'to_block':end});calls.append(('eth_getLogs',[{'address':addr,'fromBlock':hex(start),'toBlock':hex(end),'topics':topics}]))
 rr,ss=c.batches('ethereum',calls,'post_wrap_public_boundary');result=[]
 for l,r in zip(labels,rr):
  if 'result' in r:result.append({**l,'response':r,'complete':True});continue
  logs=[];failed=[]
  topics=next(topics for key,topics in queries if key==l['kind'])
  calls=[('eth_getLogs',[{'address':addr,'fromBlock':hex(b),'toBlock':hex(min(b+4999,end)),'topics':topics}]) for b in range(start,end+1,5000)];rs,sources=c.batches('ethereum',calls,'post_wrap_public_boundary_chunks_'+l['kind'],size=1);ss+=sources
  for call,r in zip(calls,rs):
   if 'result'in r:logs+=r['result']
   else:failed.append({'range':call[1][0],'response':r})
  result.append({**l,'response':{'result':logs},'complete':not failed,'failed_ranges':failed})
 blocks=sorted({int(log['blockNumber'],16) for x in result for log in x['response'].get('result',[])})
 rr,sources=c.batches('ethereum',[('eth_getBlockByNumber',[hex(b),False]) for b in blocks],'post_wrap_public_boundary_blocks');ss+=sources
 out={'financial_snapshot_timestamp':c.T,'contract':addr,'wallet':A,'from_block':start,'to_block':end,'queries':result,'blocks':{str(b):r for b,r in zip(blocks,rr)},'sources':ss,'scope':'Public cUSDC event census for this wallet from its measured wrap through T, plus public amount disclosures in that wrapper. Ciphertext handles are not plaintext amounts. Receiver-filtered unwraps do not cover unwrapping to other receiver addresses.'}
 (D/'credit_expansion_deep_public_boundary.json').write_text(json.dumps(out,indent=2));print('Post-wrap public events:',[(x['kind'],len(x['response'].get('result',[])),x['complete']) for x in result],flush=True)

def boundary_receipts():
 path=D/'credit_expansion_deep_public_boundary.json';v=json.loads(path.read_text());c.RPCS['ethereum']=['https://gateway.tenderly.co/public/mainnet'];txs=sorted({l['transactionHash'] for q in v['queries'] for l in q['response'].get('result',[]) if l['transactionHash']!=TXS['A_cash_out']});addresses=['0x11c6acfd368ddfab97d15649eb8043c0197fac4c','0x2deafb36f3b118d434cde4708e8350eae918724d'];rr,ss=c.batches('ethereum',[('eth_getTransactionReceipt',[tx]) for tx in txs],'post_wrap_boundary_receipts');v['receipts']={tx:r for tx,r in zip(txs,rr)};rr,sources=c.batches('ethereum',[('eth_getCode',[a,hex(c.BLOCKS['ethereum'])]) for a in addresses],'post_wrap_counterparty_code');ss+=sources;v['counterparty_codes']={a:r for a,r in zip(addresses,rr)};v['sources']+=ss;path.write_text(json.dumps(v,indent=2))
 for a in addresses:c.capture('post_wrap_counterparty_'+a,'https://eth.blockscout.com/api/v2/smart-contracts/'+a)

if __name__=='__main__':{'capture':capture,'state':state,'silo_sources':silo_sources,'funding':funding,'silo_legacy':silo_legacy,'wrapper':wrapper,'fees':fees_sources,'controls_sources':controls_sources,'compound_retry':compound_retry,'silo_arb_retry':silo_arb_retry,'silo_arb_pairs':silo_arb_pairs,'silo_arb_credit':silo_arb_credit,'destination_metadata':destination_metadata,'public_boundary':public_boundary,'boundary_receipts':boundary_receipts}[sys.argv[1]]()
