"""Paced retries of archive provider errors, preserving every failed response."""
import json,time,sys
from backing_exit_capture import *

def run():
    names=['nested_backing_T','liquid_queue_payout_receipts','rocksolid_payout_receipts','liquity_payout_receipts','royco_accounting_transactions','rocksolid_exit_block_headers']
    for name in names:
        d=json.loads((RAW/(name+'.json')).read_text()); records=d['records']
        bad=[i for i,r in enumerate(records)if not r['response'].get('result') and r['response'].get('error',{}).get('code')in[429,-32000]]
        for j in range(0,len(bad),5):
            indices=bad[j:j+5];rows=[{k:v for k,v in records[i].items()if k!='response'}for i in indices]
            rr=rpc(name+'_retry_'+str(j//5),rows,LOG_RPC)
            for i,r in zip(indices,rr['records']):records[i]=r
            time.sleep(.8)
        d['records']=records;d['retryPolicy']='Paced batch-of-five on second provider. Original error responses preserved.'
        (RAW/(name+'_repaired.json')).write_text(json.dumps(d,indent=2))
        print(name,'remaining errors',sum(1 for r in records if 'error'in r['response']),flush=True)

if __name__=='__main__':run()
