"""Public product identity and ERC-4626 book data at fixed blocks, with failures retained."""
import json,sys,concurrent.futures
from collect import ROOT,T,request,rpc_batch,read_latest
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_uint

def run():
 products=[]
 for a,s in [('0xb9dc54c8261745cb97070cefbe3d3d815aee8f20','Concrete Delta weETH'),('0xd57588c73715b65e0ead36ae06c15644169501b7','Concrete wstETH Plus'),('0xa0d3707c569ff8c87fa923d3823ec5d81c98be78','Fluid Lite ETH V2'),('0xc383a3833a87009fd9597f8184979af5edfad019','Fluid Lite ETH V1'),('0xd11c452fc99cf405034ee446803b6f6c1f6d5ed8','Treehouse tETH')]:products.append({'address':a,'name_hint':s,'chain':'ethereum'})
 text=read_latest('adapter_cian-yield-layer');first=text.split('preVaults:')[0]
 import re
 products += [{'address':a.lower(),'name_hint':'CIAN raw vault','chain':'ethereum'} for a in re.findall(r'"(0x[0-9A-Fa-f]{40})"',first)]
 tag=hex(read_latest('block_ethereum_T')['height']);calls=[];labels=[]
 for p in products:
  for sig in ['asset()','totalAssets()','totalSupply()','decimals()','convertToAssets(uint256)','owner()','getCurrentExchangePrice()']:
   calls.append(('eth_call',[{'to':p['address'],'data':'0x'+sel(sig)+(enc_uint(10**18) if 'uint256' in sig else '')},tag]));labels.append({'product':p['address'],'signature':sig})
 r=rpc_batch('ethereum',calls,'vault_registry_T')
 (ROOT/'data/eth/vault_registry_rpc_T.json').write_text(json.dumps({'block':int(tag,16),'target_timestamp':T,'products':products,'labels':labels,'responses':r},indent=2))
 jobs=[('vault_abi_'+p['address'],'https://eth.blockscout.com/api/v2/smart-contracts/'+p['address']) for p in products[:5]+products[5:7]]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda j:request(*j),jobs))
 assets=sorted({x['result'][-40:] for x in r if x.get('result') and len(x['result'])==66 and labels[x['id']-1]['signature']=='asset()' and int(x['result'],16)>0});calls=[];labels=[]
 for a in assets:
  for sig in ['name()','symbol()','decimals()']:
   calls.append(('eth_call',[{'to':'0x'+a,'data':'0x'+sel(sig)},tag]));labels.append({'asset':'0x'+a,'signature':sig})
 rr=rpc_batch('ethereum',calls,'vault_assets_T') if calls else []
 (ROOT/'data/eth/vault_assets_T.json').write_text(json.dumps({'block':int(tag,16),'labels':labels,'responses':rr},indent=2))

if __name__=='__main__':run()
