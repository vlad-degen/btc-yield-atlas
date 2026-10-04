"""Read configured rate providers and dated prices, retaining valuation provenance."""
import json,sys,concurrent.futures
from collect import ROOT,RAW,T,V,ACC,rpc_batch,read_latest,request
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_addr

def run():
 tag=hex(read_latest('block_ethereum_T')['height']);mono='0xa024063b630d554078bbf985718b22f3c6870ee0';owner='0xd829f278016b90fec735f9a12bf8b75e06102c89'
 calls=[('eth_call',[{'to':ACC,'data':'0x'+sel('rateProviderData(address)')+enc_addr(mono)},tag]),('eth_call',[{'to':ACC,'data':'0x'+sel('getRateInQuote(address)')+enc_addr(mono)},tag]),('eth_getCode',[owner,tag])]
 r=rpc_batch('ethereum',calls,'pilot_quotes_T');(ROOT/'data/eth/pilot_quotes_T.json').write_text(json.dumps({'block':int(tag,16),'responses':r},indent=2))
 if r and r[0].get('result'):
  provider='0x'+r[0]['result'][-40:]
  rr=rpc_batch('ethereum',[('eth_call',[{'to':provider,'data':'0x'+sel('getRate()')},tag])],'mono_rate_T')
  (ROOT/'data/eth/mono_rate_T.json').write_text(json.dumps({'provider':provider,'responses':rr},indent=2));request('mono_rate_provider_abi','https://eth.blockscout.com/api/v2/smart-contracts/'+provider)
 tokens=[]
 for ch in ['ethereum','optimism']:
  d=json.loads((ROOT/'data/eth'/('balances_'+ch+'_T.json')).read_text());tokens += [ch+':'+x['address'] for x in d['labels'] if x.get('address')]
 for i in range(0,len(tokens),30):request('pilot_prices_T_'+str(i//30),'https://coins.llama.fi/prices/historical/'+str(T)+'/'+','.join(tokens[i:i+30]))
 request('acc_op_abi','https://optimism.blockscout.com/api/v2/smart-contracts/'+ACC)

if __name__=='__main__':run()
