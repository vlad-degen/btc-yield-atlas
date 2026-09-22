# Upgrade / pause events on mHyperBTC Ethereum contracts (token, deposit vault, redemption vault, oracle) via getLogs (tenderly, 500k-block chunks, throttled)
import sys,json,datetime,time; sys.path.insert(0,'scripts')
from rpc import *
U='https://gateway.tenderly.co/public/mainnet'
def logs(addr,tp,frm,to):
    out=[]; a=frm
    while a<=to:
        b=min(a+499999,to)
        for i in range(8):
            try:
                r=post(U,{'jsonrpc':'2.0','id':1,'method':'eth_getLogs','params':[{'address':addr,'topics':[tp],'fromBlock':hex(a),'toBlock':hex(b)}]},timeout=60); break
            except Exception as e: time.sleep(5*(i+1))
        out+=r.get('result',[]); a=b+1; time.sleep(0.7)
    return out
T={'Upgraded':topic('Upgraded(address)'),'Paused(address)':topic('Paused(address)'),'Unpaused(address)':topic('Unpaused(address)'),'PauseFn':topic('PauseFn(address,bytes4)'),'UnpauseFn':topic('UnpauseFn(address,bytes4)'),'SetRoundData?':topic('AnswerUpdated(int256,uint256,uint256)')}
res=[]
head=int(post(U,{'jsonrpc':'2.0','id':1,'method':'eth_blockNumber','params':[]})['result'],16)
for name,a in [('token','0xC8495EAFf71D3A563b906295fCF2f685b1783085'),('depositVault','0xeD22A9861C6eDd4f1292aeAb1E44661D5f3FE65e'),('redemptionVault','0x16d4f955B0aA1b1570Fe3e9bB2f8c19C407cdb67'),('oracle','0x3359921992C33ef23169193a6C91F2944A82517C')]:
    for lab,tp in T.items():
        if lab=='SetRoundData?': continue
        for l in logs(a,tp,23500000,head):
            ts=int(l['blockTimestamp'],16)
            res.append((datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).strftime('%Y-%m-%d %H:%M'),name,lab,l['transactionHash'],l['data'][:140],[t[-40:] for t in l['topics'][1:]]))
res.sort()
json.dump(res,open('raw/admin_events.json','w'),indent=0)
for r in res: print(r)
