"""Read Concrete multisig accounting and its ETH wallet credit positions."""
import json,sys,concurrent.futures
from collect import ROOT,T,V,read_latest,rpc_batch,request
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_addr

def run():
 tag=hex(read_latest('block_ethereum_T')['height']);strategies=['0xc8ea269d4dba296f7fbba812905c1b2efe5dbe1c','0x50a7510e73d79d60823dcac50e6b2c62e89ed82b'];calls=[];labels=[]
 for a in strategies:
  for sig in ['getMultiSig()','getVault()','asset()','totalAllocatedValue()','getAccountingValidityPeriod()','getNextAccountingNonce()','getLastUpdatedTimestamp()','getCooldownPeriod()','maxWithdraw()']:
   calls.append(('eth_call',[{'to':a,'data':'0x'+sel(sig)},tag]));labels.append({'strategy':a,'signature':sig})
 r=rpc_batch('ethereum',calls,'concrete_strategies_T');wallets=[]
 for rr in r:
  l=labels[rr['id']-1]
  if l['signature']=='getMultiSig()' and rr.get('result'):wallets.append({'strategy':l['strategy'],'wallet':'0x'+rr['result'][-40:]})
 calls=[];labs=[]
 for w in wallets:
  for name,a in [('aave','0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'),('spark','0xc13e21b648a5ee794902342038ff3adab66be987')]:
   calls.append(('eth_call',[{'to':a,'data':'0x'+sel('getUserAccountData(address)')+enc_addr(w['wallet'])},tag]));labs.append({**w,'protocol':name})
  for sig in ['getThreshold()','getOwners()']:
   calls.append(('eth_call',[{'to':w['wallet'],'data':'0x'+sel(sig)},tag]));labs.append({**w,'signature':sig})
 rr=rpc_batch('ethereum',calls,'concrete_wallet_accounts_T')
 (ROOT/'data/eth/concrete_lookthrough_T.json').write_text(json.dumps({'target_timestamp':T,'strategy_labels':labels,'strategy_responses':r,'wallet_labels':labs,'wallet_responses':rr},indent=2))
 jobs=[('concrete_wallet_tokens_'+w['wallet'],'https://eth.blockscout.com/api/v2/addresses/'+w['wallet']+'/token-balances') for w in wallets]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:list(p.map(lambda j:request(*j),jobs))
 print(wallets)

if __name__=='__main__':run()
