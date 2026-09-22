# Replay share Transfer logs on Ethereum -> balances at month-ends, holder counts, flows (mint/burn)
import lib,collections,bisect,json
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'.lower()
T=lib.topic('Transfer(address,address,uint256)')
lg=[l for l in lib.load('vault_all_logs_rpc.json') if l['topics'][0]==T]
lg.sort(key=lambda l:(int(l['blockNumber'],16),int(l['logIndex'],16)))
mb=lib.load('month_blocks.json')
ends=sorted([(v['eth'],k) for k,v in mb.items() if k!='2024-11-14launch'])
bal=collections.defaultdict(int)
snap={}; i=0
mint=collections.defaultdict(int); burn=collections.defaultdict(int)
ZERO='0x'+'0'*40
def month_of(b):
    for eb,k in ends:
        if b<=eb: return k
    return 'after'
for eb,k in ends:
    while i<len(lg) and int(lg[i]['blockNumber'],16)<=eb:
        l=lg[i]; fr='0x'+l['topics'][1][-40:]; to='0x'+l['topics'][2][-40:]; v=int(l['data'],16)
        if fr!=ZERO: bal[fr]-=v
        else: mint[k]+=v
        if to!=ZERO: bal[to]+=v
        else: burn[k]+=v
        i+=1
    snap[k]={a:b for a,b in bal.items() if b>0}
    print(k,'holders',len(snap[k]),'sum',sum(snap[k].values())/1e8,'mint',mint[k]/1e8,'burn',burn[k]/1e8)
lib.save('eth_holder_snapshots.json',snap)
lib.save('eth_mint_burn.json',{'mint':mint,'burn':burn})
