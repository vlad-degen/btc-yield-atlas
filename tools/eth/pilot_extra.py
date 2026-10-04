"""Additional read-only contract evidence at the verified snapshot."""
import json,sys
from collect import ROOT,V,ACC,rpc_batch,request,read_latest
sys.path.insert(0,str(ROOT/'tools'/'top5'/'etherfi'))
from keccak_lib import sel,enc_uint

def run():
 manifest=json.loads((ROOT/'data/eth/snapshot_manifest.json').read_text())
 for chain in ['ethereum','optimism']:
  tag=hex(next(x['block'] for x in manifest['chains'] if x['chain']==chain));calls=[];labels=[]
  def add(label,target,sig,args=''):
   calls.append(('eth_call',[{'to':target,'data':'0x'+sel(sig)+args},tag]));labels.append({'label':label,'target':target,'signature':sig})
  add('accountant_state',ACC,'accountantState()')
  if chain=='ethereum':
   add('fluid_vault74','0x324c5dc1fc42c7a4d43d92df1eba58a54d13bf2d','getVaultAddress(uint256)',enc_uint(74))
   safe='0xd829f278016b90fec735f9a12bf8b75e06102c89'
   add('authority_owner_threshold',safe,'getThreshold()');add('authority_owner_owners',safe,'getOwners()')
  r=rpc_batch(chain,calls,'pilot_extra_'+chain)
  if r:
   (ROOT/'data/eth'/('pilot_extra_'+chain+'.json')).write_text(json.dumps({'block':int(tag,16),'labels':labels,'responses':r},indent=2))
   if chain=='ethereum':
    val=next(x.get('result') for x in r if x['id']==2)
    if val and len(val)==66:request('fluid_vault74_abi','https://eth.blockscout.com/api/v2/smart-contracts/0x'+val[-40:])

if __name__=='__main__':run()
