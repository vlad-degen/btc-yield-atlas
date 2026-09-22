# Scroll share supply + vault token holdings on Optimism and Scroll at month-ends (used by value_positions2.py)
import lib
lib.RPCS['scroll']=['https://rpc.scroll.io','https://scroll.drpc.org','https://scroll-rpc.publicnode.com']
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
mb=lib.load('month_blocks.json'); S=lib.load('supply_monthly.json')
head=int(lib.rpc('eth_blockNumber',[],'scroll'),16)
def bts(n): return int(lib.rpc('eth_getBlockByNumber',[hex(n),False],'scroll')['timestamp'],16)
def block_at(ts,lo=1,hi=head):
    while lo<hi:
        mid=(lo+hi+1)//2
        if bts(mid)<=ts: lo=mid
        else: hi=mid-1
    return lo
OPT={'eBTC':('0x657e8c867d8b37dcc18fa4caead9c45eb088c642',8),'WBTC':('0x68f180fcce6836688e9084f035309e29bf0a2095',8),'USDC':('0x0b2c639c533813f4aa9d7837caf62653d097ff85',6)}
SCR={'eBTC':('0x657e8c867d8b37dcc18fa4caead9c45eb088c642',8),'WBTC':('0x3c1bca5a656e69edcd0d4e36bebb3fcdaca60cf1',8),'USDC':('0x06efdbff2a14a7c8e15944d1f4a48f9f95f663a4',6)}
oph={}; sch={}
for k,v in mb.items():
    v['scroll']=block_at(v['ts']); S[k]['scroll']=lib.u(lib.c(V,'totalSupply()',block=v['scroll'],chain='scroll'))
    if k=='2024-11-14launch': continue
    oph[k]={s:(lib.bal(t,V,block=v['op'],chain='op') or 0)/10**d for s,(t,d) in OPT.items()}
    sch[k]={s:(lib.bal(t,V,block=v['scroll'],chain='scroll') or 0)/10**d for s,(t,d) in SCR.items()}
lib.save('month_blocks.json',mb); lib.save('supply_monthly.json',S); lib.save('op_vault_holdings.json',oph); lib.save('scroll_vault_holdings.json',sch)
