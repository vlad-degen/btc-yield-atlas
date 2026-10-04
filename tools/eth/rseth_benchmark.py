"""Read rsETH oracle history through its configured contract identity."""
import json,sys
from collect import ROOT,T,rpc_batch,request,read_latest
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,keccak

def run():
 tag=hex(read_latest('block_ethereum_T')['height']);token='0xa1290d69c65a6fe4df752f95823fae25cb99e5a7'
 rr=rpc_batch('ethereum',[('eth_call',[{'to':token,'data':'0x'+sel('lrtConfig()')},tag]),('eth_call',[{'to':token,'data':'0x'+sel('paused()')},tag]),('eth_call',[{'to':token,'data':'0x'+sel('custodyAddress()')},tag])],'rseth_config_T')
 cfg='0x'+rr[0]['result'][-40:];rr2=rpc_batch('ethereum',[('eth_call',[{'to':cfg,'data':'0x'+sel('getContract(bytes32)')+keccak(b'LRT_ORACLE').hex()},tag])],'rseth_oracle_identity_T')
 oracle='0x'+rr2[0]['result'][-40:];request('rseth_oracle_abi','https://eth.blockscout.com/api/v2/smart-contracts/'+oracle)
 (ROOT/'data/eth/rseth_oracle_identity.json').write_text(json.dumps({'target_timestamp':T,'token':token,'config':cfg,'oracle':oracle,'state_calls':rr},indent=2))
 history=json.loads((ROOT/'data/eth/benchmark_history_ethereum_rpc.json').read_text());labels=[x for x in history['labels'] if x['metric']=='block'];calls=[('eth_call',[{'to':oracle,'data':'0x'+sel('rsETHPrice()')},hex(x['block'])]) for x in labels]
 r=rpc_batch('ethereum',calls,'rseth_benchmark_history')
 configs=rpc_batch('ethereum',[('eth_call',[{'to':token,'data':'0x'+sel('lrtConfig()')},hex(x['block'])]) for x in labels],'rseth_historical_configs')
 historical_oracles=rpc_batch('ethereum',[('eth_call',[{'to':'0x'+x['result'][-40:],'data':'0x'+sel('getContract(bytes32)')+keccak(b'LRT_ORACLE').hex()},hex(l['block'])]) for x,l in zip(configs,labels)],'rseth_historical_oracles')
 verified=all(x.get('result') and ('0x'+x['result'][-40:]).lower()==oracle.lower() for x in historical_oracles)
 (ROOT/'data/eth/rseth_benchmark_rpc.json').write_text(json.dumps({'historical_oracle_identity_verified':verified,'oracle':oracle,'labels':labels,'responses':r,'configs':configs,'historical_oracles':historical_oracles},indent=2))

if __name__=='__main__':run()
