"""Find BSC block by timestamp and pull River bfBTC Prime Vault logs around given timestamps (mechA)."""
import sys,json; sys.path.insert(0,'.')
from mechA_rpc import *
LOGRPC='https://bsc.rpc.blxrbdn.com'
HDR='https://bsc-dataseed.bnbchain.org'
V='0x8f10C801B62Ae0b67B87B56a5f8ce05437ba6b7f'
def blk_ts(n):
    r=post(HDR,{'jsonrpc':'2.0','id':1,'method':'eth_getBlockByNumber','params':[hex(n),False]})
    return int(r['result']['timestamp'],16)
def find_block(ts):
    hi=int(post(HDR,{'jsonrpc':'2.0','id':1,'method':'eth_blockNumber','params':[]})['result'],16); lo=hi-80_000_000
    while hi-lo>1:
        mid=(lo+hi)//2
        if blk_ts(mid)<ts: lo=mid
        else: hi=mid
    return hi
TOPICS={'0x'+k256(s.encode()).hex():s for s in ['Deposit(uint256,address,address)','Withdraw(uint256,address,address)','MintedDebtToken(uint256)','BurnedDebtToken(uint256)','StakedDebtToken(uint256,uint256)','UnstakedDebtToken(uint256,uint256)','Transfer(address,address,uint256)','StakingFactorUpdated(uint256)','VaultConfigUpdated((uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool,bool))','StrategyExecuted(address,bytes)','Initialized(uint64)','WhitelistedUpdated(address,bool)','StakingEnabledUpdated(bool)']}
def logs(frm,to,addr=V):
    out=[]
    b=frm
    while b<=to:
        e=min(b+4999,to)
        r=post(LOGRPC,{'jsonrpc':'2.0','id':1,'method':'eth_getLogs','params':[{'address':addr,'fromBlock':hex(b),'toBlock':hex(e)}]})
        if 'error' in r: print('err',r['error']); break
        out+=r['result']; b=e+1
    return out
if __name__=='__main__':
    res={}
    for ts in [int(x) for x in sys.argv[1:]]:
        bn=find_block(ts); print('ts',ts,'-> block',bn)
        L=logs(bn-3000,bn+3000)
        for l in L:
            t=TOPICS.get(l['topics'][0],l['topics'][0][:10])
            print('  ',int(l['blockNumber'],16),l['transactionHash'],t,[x[-40:] for x in l['topics'][1:]],l['data'][:200])
        res[ts]={'block':bn,'logs':L}
    json.dump(res,open('../raw/mechA/river_bsc_pv_logs_%s.json'%('_'.join(sys.argv[1:])),'w'),indent=1)
