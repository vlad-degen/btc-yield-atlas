import lib,collections,bisect
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
EN=lib.topic('Enter(address,address,uint256,address,uint256)'); EX=lib.topic('Exit(address,address,uint256,address,uint256)')
lg=lib.load('vault_all_logs_rpc.json')
mb=lib.load('month_blocks.json')
ends=sorted([(v['eth'],k) for k,v in mb.items() if k!='2024-11-14launch'])
rates=lib.load('rate_updates.json'); rb=[r['block'] for r in rates]
def rate_at_block(b):
    i=bisect.bisect_right(rb,b)-1
    return 1.0 if i<0 else rates[i]['new']/1e8
SYM={'2260fac5e5542a773aa44fbcfedf7c193bc2c599':'WBTC','8236a87084f8b84306f72007f36f2618a5634494':'LBTC','657e8c867d8b37dcc18fa4caead9c45eb088c642':'eBTC','cbb7c0000ab88b473b1f5afd9ef808440eed33bf':'cbBTC','0000000000000000000000000000000000000000':'bridge'}
def month(b):
    for eb,k in ends:
        if b<=eb: return k
    return 'after'
agg=collections.defaultdict(lambda:collections.defaultdict(float))
cnt=collections.defaultdict(lambda:collections.defaultdict(int))
for l in lg:
    t=l['topics'][0]
    if t not in (EN,EX): continue
    b=int(l['blockNumber'],16); d=l['data'][2:]
    amt=int(d[0:64],16); shares=int(d[64:128],16)
    asset=l['topics'][2][-40:]; s=SYM.get(asset,asset[:8])
    k=month(b); btc=shares/1e8*rate_at_block(b)
    kind=('dep' if t==EN else 'wd')+('_bridge' if s=='bridge' else '')
    agg[k][kind]+=btc; cnt[k][kind]+=1
    if s!='bridge': agg[k][kind+'_'+s]+=btc
rows=[]
for eb,k in ends:
    a=agg[k]
    rows.append({'month':k,**{kk:round(v,4) for kk,v in a.items()},'n_dep':cnt[k]['dep'],'n_wd':cnt[k]['wd'],'n_bridge_in':cnt[k]['dep_bridge'],'n_bridge_out':cnt[k]['wd_bridge']})
    print(k,'dep %.2f wd %.2f net %.2f | bridge in %.2f out %.2f | n_dep %d n_wd %d'%(a['dep'],a['wd'],a['dep']-a['wd'],a['dep_bridge'],a['wd_bridge'],cnt[k]['dep'],cnt[k]['wd']), {kk:round(v,1) for kk,v in a.items() if kk.startswith('dep_') and 'bridge' not in kk})
lib.save('flows_monthly.json',rows)
tot=collections.defaultdict(float)
for k in agg:
    for kk,v in agg[k].items(): tot[kk]+=v
print({k:round(v,1) for k,v in tot.items()})
