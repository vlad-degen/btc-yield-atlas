# All ERC-20 Transfer logs in/out of a wallet on an RPC chain (no explorer available: Monad, Stable)
import sys, json, datetime; sys.path.insert(0,'scripts')
from rpc import *
chain,url,wallet,frm,step,fn=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
TR=topic('Transfer(address,address,uint256)'); W='0x'+a32(wallet)
to=blocknum(chain); out=[]
for side in (1,2):
    a=frm; st=step
    while a<=to:
        b=min(a+st-1,to)
        tp=[TR,W,None] if side==1 else [TR,None,W]
        try:
            r=post(url,{'jsonrpc':'2.0','id':1,'method':'eth_getLogs','params':[{'topics':tp,'fromBlock':hex(a),'toBlock':hex(b)}]},timeout=120)
        except Exception as e:
            r={'error':str(e)}
        if 'error' in r:
            if st>1000: st//=4; continue
            raise Exception(r['error'])
        out+=r['result']; a=b+1; st=step
json.dump({'to_block':to,'logs':out},open(fn,'w')); print(len(out))
