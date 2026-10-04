"""Follow the nested Liquid Monad receipt through public fixed-block getters."""
import json,sys
from collect import ROOT,T,V,read_latest,rpc_batch,request
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_addr

MONO='0xa024063b630d554078bbf985718b22f3c6870ee0'
def run():
 tag=hex(read_latest('block_ethereum_T')['height']);labels=[];calls=[]
 for sig in ['hook()','authority()','totalSupply()','owner()']:
  labels.append({'address':MONO,'signature':sig});calls.append(('eth_call',[{'to':MONO,'data':'0x'+sel(sig)},tag]))
 labels.append({'address':MONO,'signature':'balanceOf(address)'});calls.append(('eth_call',[{'to':MONO,'data':'0x'+sel('balanceOf(address)')+enc_addr(V)},tag]))
 r=rpc_batch('ethereum',calls,'mono_identity_T');out={'target_timestamp':T,'block':int(tag,16),'labels':labels,'responses':r}
 (ROOT/'data/eth/mono_identity_T.json').write_text(json.dumps(out,indent=2))
 hook='0x'+r[0]['result'][-40:];request('mono_hook_abi','https://eth.blockscout.com/api/v2/smart-contracts/'+hook)
 r2=rpc_batch('ethereum',[('eth_call',[{'to':hook,'data':'0x'+sel(s)},tag]) for s in ['accountant()','vault()']],'mono_hook_T')
 out={'hook':hook,'signatures':['accountant()','vault()'],'responses':r2};(ROOT/'data/eth/mono_hook_T.json').write_text(json.dumps(out,indent=2));print(out)
 if r2[0].get('result') and len(r2[0]['result'])==66:
  acc='0x'+r2[0]['result'][-40:];request('mono_accountant_abi','https://eth.blockscout.com/api/v2/smart-contracts/'+acc)
  specs=['getRate()','base()','vault()','accountantState()'];r3=rpc_batch('ethereum',[('eth_call',[{'to':acc,'data':'0x'+sel(s)},tag]) for s in specs],'mono_accountant_T')
  out={'target_timestamp':T,'accountant':acc,'signatures':specs,'responses':r3};(ROOT/'data/eth/mono_accountant_T.json').write_text(json.dumps(out,indent=2));print(out)
  b=read_latest('block_monad_T')['height'];mtag=hex(b)
  specs=[('eth_chainId',[]),('eth_getBlockByNumber',[mtag,False]),('eth_getBlockByNumber',[hex(b+1),False]),('eth_getCode',[MONO,mtag]),('eth_call',[{'to':MONO,'data':'0x'+sel('totalSupply()')},mtag]),('eth_call',[{'to':acc,'data':'0x'+sel('getRate()')},mtag]),('eth_call',[{'to':MONO,'data':'0x'+sel('hook()')},mtag])]
  payload=[{'jsonrpc':'2.0','id':i+1,'method':m,'params':p} for i,(m,p) in enumerate(specs)]
  rr=request('mono_remote_T','https://rpc.monad.xyz',payload)
  (ROOT/'data/eth/mono_remote_T.json').write_text(json.dumps({'target_timestamp':T,'block':b,'requests':payload,'responses':rr},indent=2));print('remote responses',[(x['id'],str(x.get('result'))[:150],x.get('error')) for x in rr] if isinstance(rr,list) else rr)

if __name__=='__main__':run()
