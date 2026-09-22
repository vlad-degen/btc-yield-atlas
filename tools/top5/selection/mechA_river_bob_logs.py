"""Pull Transfer/Deposit logs for River vaults on BOB via RPC (mechA). Output raw/mechA/river_bob_logs.json"""
import sys,json; sys.path.insert(0,'.')
from mechA_rpc import *
R='https://rpc.gobob.xyz'
VAULTS=['0xEdE84f536448cC822a9318548Aa8618183743c4f','0xd62E2F6b6616271001DCd0988AD2D73DEeE1b491','0x4f4EbFAeEa78d7ebc13c4aAb481fd8E36D9DC1Be','0x3eeF93169c34F50919063eF56A118BFF26C8dfb8']
TR='0x'+k256(b'Transfer(address,address,uint256)').hex()
def getlogs(addr,frm,to,step):
    out=[];b=frm
    while b<=to:
        e=min(b+step-1,to)
        r=post(R,{'jsonrpc':'2.0','id':1,'method':'eth_getLogs','params':[{'address':addr,'topics':[TR],'fromBlock':hex(b),'toBlock':hex(e)}]})
        if 'error' in r:
            if step>1000: return getlogs(addr,b,to,step//4)
            raise Exception(r['error'])
        out+=r['result']; b=e+1
    return out
if __name__=='__main__':
    head=int(post(R,{'jsonrpc':'2.0','id':1,'method':'eth_blockNumber','params':[]})['result'],16)
    res={}
    for v in VAULTS:
        L=getlogs(v,20_000_000,head,2_000_000)
        res[v]=L
        bals={}
        for l in L:
            fr='0x'+l['topics'][1][-40:]; to='0x'+l['topics'][2][-40:]; amt=int(l['data'],16)/1e18
            blk=int(l['blockNumber'],16)
            print(v[:10],blk,l['transactionHash'][:14],fr,'->',to,amt)
            bals[fr]=bals.get(fr,0)-amt; bals[to]=bals.get(to,0)+amt
        print(v,'balances',{k:round(x,6) for k,x in bals.items() if abs(x)>1e-9 and k!='0x'+'0'*40})
    json.dump(res,open('../raw/mechA/river_bob_logs.json','w'),indent=1)
