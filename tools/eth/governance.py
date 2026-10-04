"""Read timelock and proxy identities without treating latest explorer labels as T versions."""
import json,sys
from collect import ROOT,T,rpc_batch,read_latest
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_uint,keccak

def run():
 tag=hex(read_latest('block_ethereum_T')['height']);owner='0xd829f278016b90fec735f9a12bf8b75e06102c89';calls=[];labels=[]
 def add(label,a,sig,args=''):
  labels.append({'label':label,'address':a,'signature':sig});calls.append(('eth_call',[{'to':a,'data':'0x'+sel(sig)+args},tag]))
 add('etherfi_timelock_min_delay',owner,'getMinDelay()')
 for name in ['PROPOSER_ROLE','EXECUTOR_ROLE','CANCELLER_ROLE','DEFAULT_ADMIN_ROLE']:
  role=keccak(name.encode()).hex() if name!='DEFAULT_ADMIN_ROLE' else '0'*64
  add(name+'_count',owner,'getRoleMemberCount(bytes32)',role)
 slot='0x'+format(int.from_bytes(keccak(b'eip1967.proxy.implementation'),'big')-1,'064x')
 for a in ['0xb9dc54c8261745cb97070cefbe3d3d815aee8f20','0xd57588c73715b65e0ead36ae06c15644169501b7','0xd11c452fc99cf405034ee446803b6f6c1f6d5ed8']:
  labels.append({'label':'implementation_'+a,'address':a});calls.append(('eth_getStorageAt',[a,slot,tag]))
  if a!='0xd11c452fc99cf405034ee446803b6f6c1f6d5ed8':
   for sig in ['getTotalAllocated()','cachedTotalAssets()','getDeallocationOrder()']:add(a+'_'+sig,a,sig)
 result=rpc_batch('ethereum',calls,'governance_T');(ROOT/'data/eth/governance_T.json').write_text(json.dumps({'target_timestamp':T,'labels':labels,'responses':result},indent=2))
 print([(labels[x['id']-1]['label'],x.get('result'),x.get('error')) for x in result])

if __name__=='__main__':run()
