"""Use OP's own Accountant rate for historical book NAV, retaining bridge timing differences."""
import json,sys
from collect import ROOT,ACC,rpc_batch
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel

def run():
 d=json.loads((ROOT/'data/eth/benchmark_history_optimism_rpc.json').read_text());labels=[x for x in d['labels'] if x['metric']=='block'];calls=[('eth_call',[{'to':ACC,'data':'0x'+sel('getRate()')},hex(x['block'])]) for x in labels];rr=rpc_batch('optimism',calls,'op_history_accountant_rates')
 (ROOT/'data/eth/op_history_rates_rpc.json').write_text(json.dumps({'labels':labels,'responses':rr},indent=2))

if __name__=='__main__':run()
