import lib
lib.RPCS['op']=['https://mainnet.optimism.io']
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
lg=lib.load('share_transfers_op.json')
addrs=set()
for l in lg:
    addrs.add('0x'+l['topics'][1][-40:]); addrs.add('0x'+l['topics'][2][-40:])
for x in lib.load('op_holders.json'): addrs.add(x['address']['hash'].lower())
addrs.discard('0x'+'0'*40); addrs=sorted(addrs)
print('addresses',len(addrs))
mb=lib.load('month_blocks.json'); snaps={}
for k in ['2026-04','2026-05','2026-06','2026-07','2026-08','2026-09-20']:
    b=mb[k]['op']
    res=lib.batch_calls([(V,'0x'+lib.sel('balanceOf(address)')+lib.enc_addr(a)) for a in addrs],block=b,chain='op',chunk=10)
    nz={a:(lib.u(r) or 0)/1e8 for a,r in zip(addrs,res) if r and lib.u(r)}
    sup=(lib.load('supply_monthly.json')[k]['op'] or 0)/1e8
    print(k,'holders',len(nz),'sum',round(sum(nz.values()),4),'supply',sup,'failed',sum(1 for r in res if r is None))
    snaps[k]=nz
lib.save('op_holder_snapshots_rpc.json',snaps); lib.save('op_bal_snap.json',snaps['2026-09-20'])
