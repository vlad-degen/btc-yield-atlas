"""Archive ERC4626 rates and asset identities at month ends and return window endpoints."""
import json,sys
from collect import ROOT,rpc_batch
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_uint

def run():
 source=json.loads((ROOT/'data/eth/benchmark_history_ethereum_rpc.json').read_text());points=[l for l in source['labels'] if l['metric']=='block']
 vaults=[('Fluid Lite ETH','0xa0d3707c569ff8c87fa923d3823ec5d81c98be78'),('CIAN rsETH','0xd87a19ff681ae98bf10d2220d1ae3fbd374ade4e'),('Treehouse tETH','0xd11c452fc99cf405034ee446803b6f6c1f6d5ed8'),('Concrete Delta weETH','0xb9dc54c8261745cb97070cefbe3d3d815aee8f20'),('Concrete wstETH Plus','0xd57588c73715b65e0ead36ae06c15644169501b7')]
 labels=[];calls=[]
 for p in points:
  for name,a in vaults:
   for sig in ['asset()','convertToAssets(uint256)']:
    calls.append(('eth_call',[{'to':a,'data':'0x'+sel(sig)+(enc_uint(10**18) if 'uint256' in sig else '')},hex(p['block'])]));labels.append({'name':name,'vault':a,'timestamp':p['target_timestamp'],'block':p['block'],'signature':sig})
 rr=rpc_batch('ethereum',calls,'vault_history')
 (ROOT/'data/eth/vault_history_rpc.json').write_text(json.dumps({'labels':labels,'responses':rr},indent=2))

if __name__=='__main__':run()
