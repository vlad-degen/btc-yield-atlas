"""Read public stablecoin vault allocation plumbing; no allocation assumptions from names."""
import json,sys,concurrent.futures
from collect import ROOT,T,V,read_latest,rpc_batch,request
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_uint,enc_addr

def run():
 tag=hex(read_latest('block_ethereum_T')['height']);vaults=['0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf','0xc21b08c16458202593d4d9b26b9984ee67b38bbd'];calls=[];labels=[]
 for a in vaults:
  for sig in ['asset()','totalAssets()','totalSupply()','adaptersLength()','liquidityAdapter()','liquidityData()','curator()','owner()','performanceFee()','managementFee()','lastUpdate()']:
   labels.append({'vault':a,'signature':sig});calls.append(('eth_call',[{'to':a,'data':'0x'+sel(sig)},tag]))
 rr=rpc_batch('ethereum',calls,'carry_vaults_T');counts={l['vault']:int(r['result'],16) for l,r in zip(labels,rr) if l['signature']=='adaptersLength()' and r.get('result')}
 calls2=[];labels2=[]
 for a,n in counts.items():
  assert n<100,'Unexpected number of adapters'
  for i in range(n):labels2.append({'vault':a,'index':i});calls2.append(('eth_call',[{'to':a,'data':'0x'+sel('adapters(uint256)')+enc_uint(i)},tag]))
 aa=rpc_batch('ethereum',calls2,'carry_adapters_T')
 adapters=list(set('0x'+r['result'][-40:] for r in aa if r.get('result')))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(lambda a:request('carry_adapter_abi_'+a,'https://eth.blockscout.com/api/v2/smart-contracts/'+a),adapters))
 out={'target_timestamp':T,'block':int(tag,16),'labels':labels,'responses':rr,'adapter_labels':labels2,'adapter_responses':aa,'adapter_addresses':adapters,'allocation_fractions_verified':False}
 (ROOT/'data/eth/carry_vaults_T.json').write_text(json.dumps(out,indent=2));print('adapters',adapters)

def markets():
 d=json.loads((ROOT/'data/eth/carry_vaults_T.json').read_text());tag=hex(d['block']);ads=d['adapter_addresses'];labels=[];calls=[]
 for a in ads:
  for sig in ['marketIdsLength()','parentVault()','realAssets()']:
   labels.append({'adapter':a,'signature':sig});calls.append(('eth_call',[{'to':a,'data':'0x'+sel(sig)},tag]))
 rr=rpc_batch('ethereum',calls,'carry_adapter_sizes_T');sizes={l['adapter']:int(r['result'],16) for l,r in zip(labels,rr) if l['signature']=='marketIdsLength()' and r.get('result')}
 ll=[];cc=[]
 for a,n in sizes.items():
  assert n<100,'Unexpected market count'
  for i in range(n):ll.append({'adapter':a,'index':i});cc.append(('eth_call',[{'to':a,'data':'0x'+sel('marketIds(uint256)')+enc_uint(i)},tag]))
 mids=rpc_batch('ethereum',cc,'carry_market_ids_T');lc=[];mc=[];morpho='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
 for l,r in zip(ll,mids):
  mid=r['result']
  for sig,target,extra,name in [('expectedSupplyAssets(bytes32)',l['adapter'],'','expectedSupplyAssets(bytes32)'),('supplyShares(bytes32)',l['adapter'],'','supplyShares(bytes32)'),('market(bytes32)',morpho,'','market(bytes32)'),('idToMarketParams(bytes32)',morpho,'','idToMarketParams(bytes32)'),('position(bytes32,address)',morpho,enc_addr(V),'main_borrower_position'),('position(bytes32,address)',morpho,enc_addr('0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3'),'loan_manager_position')]:
   lc.append({**l,'market_id':mid,'signature':name});mc.append(('eth_call',[{'to':target,'data':'0x'+sel(sig)+mid[2:]+extra},tag]))
 result=rpc_batch('ethereum',mc,'carry_market_allocation_T')
 (ROOT/'data/eth/carry_market_allocations_T.json').write_text(json.dumps({'target_timestamp':T,'block':d['block'],'adapter_labels':labels,'adapter_responses':rr,'market_labels':lc,'market_responses':result},indent=2));print('market count',len(mids))

if __name__=='__main__':markets() if len(sys.argv)>1 and sys.argv[1]=='markets' else run()
