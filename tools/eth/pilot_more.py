"""Additional fixed-block positions, withdrawals and permissions."""
import json,re,sys
from collect import ROOT,V,ACC,RAW,read_latest,rpc_batch
sys.path.insert(0,str(ROOT/'tools'/'top5'/'etherfi'))
from keccak_lib import sel,enc_addr,enc_uint

def run():
 tag=hex(read_latest('block_ethereum_T')['height']);calls=[];labels=[]
 def add(label,target,sig,args=''):
  calls.append(('eth_call',[{'to':target,'data':'0x'+sel(sig)+args},tag]));labels.append({'label':label,'target':target,'signature':sig})
 weth='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2';weeth='0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee'
 queue='0x0d2df071207e18ca8638b4f04e98c53155ec2ce0';authority='0x485bde66bb668a51f2372e34e45b1c6226798122';teller='0x9aa79c84b79816ab920bbce20f8f74557b514734'
 for asset in [weth,weeth]:add('queue_asset_'+asset,queue,'withdrawAssets(address)',enc_addr(asset));add('teller_asset_'+asset,teller,'assetData(address)',enc_addr(asset))
 add('queue_vault',queue,'boringVault()');add('queue_accountant',queue,'accountant()');add('authority_owner',authority,'owner()');add('authority_authority',authority,'authority()');add('teller_vault',teller,'vault()');add('teller_accountant',teller,'accountant()')
 pools=set()
 for x in read_latest('etherfi_nfts')['items']:
  manager=x['token']['address_hash'].lower();tid=int(x['id'])
  add('nft_owner_'+str(tid),manager,'ownerOf(uint256)',enc_uint(tid))
  if manager=='0xc36442b4a4522e871399cd717abdd847ab11fe88':
   add('uni_position_'+str(tid),manager,'positions(uint256)',enc_uint(tid))
   desc=(x.get('metadata') or {}).get('description','');m=re.search(r'Pool Address: (0x[0-9a-fA-F]{40})',desc)
   if m:pools.add(m.group(1).lower())
 for p in pools:add('uni_slot0_'+p,p,'slot0()');add('uni_token0_'+p,p,'token0()');add('uni_token1_'+p,p,'token1()')
 add('lido_withdraw_status','0x889edc2edab5f40e902b864ad4d7ade8e412f9b1','getWithdrawalStatus(uint256[])',enc_uint(32)+enc_uint(1)+enc_uint(122235))
 factory='0x324c5dc1fc42c7a4d43d92df1eba58a54d13bf2d'
 # Factory's token config stores the associated vault id in the high bits.
 slot=__import__('keccak_lib').keccak(bytes.fromhex(enc_uint(4241)+enc_uint(3))).hex()
 add('fluid_nft_config',factory,'readFromStorage(bytes32)',slot)
 for who in [V,ACC,teller,queue]:add('roles_'+who,authority,'getUserRoles(address)',enc_addr(who))
 r=rpc_batch('ethereum',calls,'pilot_more_T')
 if r:(ROOT/'data'/'eth'/'pilot_more_T.json').write_text(json.dumps({'block':int(tag,16),'labels':labels,'responses':r},indent=2))

if __name__=='__main__':run()
