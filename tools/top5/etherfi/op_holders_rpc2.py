import lib,time,sys
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
U='https://mainnet.optimism.io'
lg=lib.load('share_transfers_op.json')
addrs=set()
for l in lg:
    addrs.add('0x'+l['topics'][1][-40:]); addrs.add('0x'+l['topics'][2][-40:])
for x in lib.load('op_holders.json'): addrs.add(x['address']['hash'].lower())
addrs.discard('0x'+'0'*40); addrs=sorted(addrs)
mb=lib.load('month_blocks.json'); S=lib.load('supply_monthly.json'); snaps={}
sel='0x'+lib.sel('balanceOf(address)')
for k in ['2026-04','2026-05','2026-06','2026-07','2026-08','2026-09-20']:
    b=hex(mb[k]['op']); bals={}
    for st in range(0,len(addrs),10):
        sub=addrs[st:st+10]
        payload=[{'jsonrpc':'2.0','id':i,'method':'eth_call','params':[{'to':V,'data':sel+lib.enc_addr(a)},b]} for i,a in enumerate(sub)]
        for t in range(10):
            try:
                r=lib.post(U,payload,timeout=30)
                if isinstance(r,list) and all('result' in x for x in r):
                    for x in r: bals[sub[x['id']]]=int(x['result'],16)/1e8
                    break
            except Exception as e: pass
            time.sleep(1.5*(t+1))
        time.sleep(0.15)
    nz={a:v for a,v in bals.items() if v>0}
    sup=(S[k]['op'] or 0)/1e8
    print(k,'holders',len(nz),'sum',round(sum(nz.values()),4),'supply',sup,'read',len(bals),'/',len(addrs),flush=True)
    snaps[k]=nz
lib.save('op_holder_snapshots_rpc.json',snaps); lib.save('op_bal_snap.json',snaps['2026-09-20'])
