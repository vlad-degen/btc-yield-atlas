# Pull all Transfer logs of a token via RPC in chunks; save json; reconcile balances vs totalSupply
import sys, json, collections; sys.path.insert(0,'scripts')
from rpc import *
def pull(chain,url,token,frm,to,step):
    TR=topic('Transfer(address,address,uint256)'); out=[]; a=frm
    while a<=to:
        b=min(a+step-1,to)
        r=post(url,{'jsonrpc':'2.0','id':1,'method':'eth_getLogs','params':[{'address':token,'topics':[TR],'fromBlock':hex(a),'toBlock':hex(b)}]},timeout=120)
        if 'error' in r: raise Exception(r['error'])
        out+=r['result']; a=b+1
    return out
def balances(logs):
    bal=collections.Counter()
    for l in logs:
        fr='0x'+l['topics'][1][-40:]; to='0x'+l['topics'][2][-40:]; v=int(l['data'],16)
        bal[fr]-=v; bal[to]+=v
    return bal
if __name__=='__main__':
    chain,url,token,frm,step,fn=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
    to=blocknum(chain)
    L=pull(chain,url,token,frm,to,step); json.dump({'to_block':to,'logs':L},open(fn,'w'))
    b=balances(L); z='0x'+'0'*40
    s=supply(chain,token,to)
    print(len(L),'logs; minted-burned', -b[z]/1e18, 'totalSupply', s/1e18)
