"""Fluid NFT look-through using verified static return ABI."""
import json,sys
from collect import ROOT,T,rpc_batch,read_latest
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_uint,enc_addr

def decode_static(fields,words,index=0):
 out={}
 for field in fields:
  typ=field['type'];name=field.get('name') or str(index)
  if typ=='tuple':value,index=decode_static(field['components'],words,index)
  else:
   raw=words[index];index+=1
   if typ=='address':value='0x'+format(raw,'040x')
   elif typ=='bool':value=bool(raw)
   elif typ.startswith('int'):value=raw-2**256 if raw>=2**255 else raw
   elif typ.startswith('uint'):value=raw
   elif typ=='bytes32':value='0x'+format(raw,'064x')
   else:raise ValueError('unsupported ABI '+typ)
  out[name]=value
 return out,index

def run():
 tag=hex(read_latest('block_ethereum_T')['height']);resolver='0xa5c3e16523eeeddcc34706b0e6be88b4c6ea95cc';dexresolver='0x7af0c11f5c787632e567e6418d74e5832d8ffd4c'
 abi=read_latest('fluid_vaultresolver_candidate')['abi'];func=next(a for a in abi if a.get('name')=='positionByNftId')
 calls=[('eth_call',[{'to':resolver,'data':'0x'+sel('positionByNftId(uint256)')+enc_uint(4241)},tag])]
 r=rpc_batch('ethereum',calls,'fluid_pilot_position')
 val=r[0].get('result') if r else None
 if not val:print(r);return
 words=[int(val[i:i+64],16) for i in range(2,len(val),64)];decoded,n=decode_static(func['outputs'],words);assert n==len(words)
 dex=decoded['vaultData_']['constantVariables']['supply']
 dexabi=read_latest('fluid_dexresolver_abi')['abi'];labels=[];calls=[]
 for sig in ['getDexCollateralReserves(address)','getTotalSupplySharesRaw(address)','getDexState(address)']:
  func2=next(a for a in dexabi if a.get('name')==sig.split('(')[0]);labels.append(func2)
  calls.append(('eth_call',[{'to':dexresolver,'data':'0x'+sel(sig)+enc_addr(dex)},tag]))
 results=rpc_batch('ethereum',calls,'fluid_pilot_dex')
 for rr,ff in zip(results,labels):
  if rr.get('result'):
   ww=[int(rr['result'][i:i+64],16) for i in range(2,len(rr['result']),64)];dd,nn=decode_static(ff['outputs'],ww);assert nn==len(ww);decoded[ff['name']]=dd
  else:decoded[ff['name']]={'error':rr.get('error')}
 (ROOT/'data/eth/fluid_pilot_decoded.json').write_text(json.dumps({'target_timestamp':T,'block':int(tag,16),'resolver':resolver,'data':decoded},indent=2))
 print(json.dumps(decoded['userPosition_'],indent=2));print('dex',dex);print('dex results',[(l['name'],rr.get('error')) for l,rr in zip(labels,results)])

if __name__=='__main__':run()
