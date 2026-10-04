"""Archive staking benchmarks and the pilot's monthly share supply."""
import concurrent.futures, datetime as dt, json, sys
from collect import ROOT, RAW, T, V, read_latest, request, rpc_batch
from normalize import month_ends
sys.path.insert(0,str(ROOT/'tools'/'top5'/'etherfi'))
from keccak_lib import sel

def run():
 points={T}
 points.update(t for _,t in month_ends());points.update(T-d*86400 for d in [7,14,30,90,180,365,730])
 points.add(int(dt.datetime(2024,10,1,tzinfo=dt.timezone.utc).timestamp())-1)
 jobs=[]
 for t in sorted(points):
  for chain in ['ethereum','optimism']:
   jobs.append(('history_block_'+chain+'_'+str(t),'https://coins.llama.fi/block/'+chain+'/'+str(t)))
 existing={json.loads(x)['key'] for x in (RAW/'requests.jsonl').read_text().splitlines() if '"path"' in x}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(lambda j:request(*j),[j for j in jobs if j[0] not in existing]))
 for chain in ['ethereum','optimism']:
  calls=[];labels=[]
  for t in sorted(points):
   b=read_latest('history_block_'+chain+'_'+str(t))['height'];tag=hex(b)
   calls.append(('eth_getBlockByNumber',[tag,False]));labels.append({'metric':'block','target_timestamp':t,'block':b})
   calls.append(('eth_call',[{'to':V,'data':'0x'+sel('totalSupply()')},tag]));labels.append({'metric':'liquidETH_supply','target_timestamp':t,'block':b})
   if chain=='ethereum':
    for metric,address,sig in [('wstETH_rate','0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','stEthPerToken()'),('weETH_rate','0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','getRate()')]:
     calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)},tag]));labels.append({'metric':metric,'target_timestamp':t,'block':b})
  result=rpc_batch(chain,calls,'benchmark_history_'+chain)
  if result:(ROOT/'data'/'eth'/('benchmark_history_'+chain+'_rpc.json')).write_text(json.dumps({'chain':chain,'labels':labels,'responses':result},indent=2))

if __name__=='__main__':run()
