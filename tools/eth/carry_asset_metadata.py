"""Identify collateral contracts used by the stablecoin legs at the research block."""
import json,sys
from collect import ROOT,T,rpc_batch,read_latest
from catalog import abi_string
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel
def run():
 rows=json.loads((ROOT/'data/eth/carry_credit_lookthrough.json').read_text());assets=sorted(set(r['collateral'] for r in rows));labels=[];calls=[];tag=hex(read_latest('block_ethereum_T')['height'])
 for a in assets:
  for sig in ['symbol()','decimals()','asset()']:
   labels.append({'address':a,'signature':sig});calls.append(('eth_call',[{'to':a,'data':'0x'+sel(sig)},tag]))
 rr=rpc_batch('ethereum',calls,'carry_asset_metadata_T');out={}
 for l,r in zip(labels,rr):
  p=out.setdefault(l['address'],{'address':l['address'],'target_timestamp':T});v=r.get('result')
  if not v or v=='0x':continue
  if l['signature']=='symbol()':p['symbol']=abi_string(v)
  elif l['signature']=='decimals()':p['decimals']=int(v,16)
  else:p['erc4626_asset']='0x'+v[-40:]
 (ROOT/'data/eth/carry_collateral_assets_T.json').write_text(json.dumps({'assets':list(out.values()),'labels':labels,'responses':rr},indent=2));print([(r.get('symbol'),r['address']) for r in out.values()])
if __name__=='__main__':run()
