# Convert Blockscout holder balances to BTC-equivalent, bucket, concentration, holder type
import json,collections,csv
from ybrpc import *
from markets import M
h=json.load(open('../raw/holders_blockscout.json'))
def htype(x):
    if not x['is_contract']: return 'EOA'
    nm=x['name'] or ''; im=(x['impl'][0].get('name') or '') if x['impl'] else ''
    if nm=='LiquidityGauge': return 'gauge'
    if 'Safe' in nm or 'Safe' in im: return 'multisig(Safe)'
    if im=='HybridVault': return 'HybridVault'
    if nm=='FeeDistributor': return 'YB FeeDistributor'
    if im.startswith('EIP7702') or im in ('Kernel','AmbireAccount7702','WalletCore','CaliburEntry','SmartWalletEntry') : return 'smart-account/7702 (user)'
    if nm in ('Morpho','PoolManager','Locker') or 'Silo' in nm: return 'DeFi protocol (%s)'%('Silo' if 'Silo' in nm else nm)
    if im=='StrategyYieldBasis' or nm=='Strategy': return 'StakeDAO-type strategy'
    return 'other contract'
res={}; rows=[]
BUCKETS=[(0,0.01,'<0.01'),(0.01,0.1,'0.01-0.1'),(0.1,1,'0.1-1'),(1,10,'1-10'),(10,100,'10-100'),(100,1e9,'>100')]
summary=[]
for mk in ['v3-WBTC','v3-cbBTC','v3-tBTC','v2-WBTC','v2-cbBTC','v2-tBTC','v1-WBTC','v1-cbBTC','v1-tBTC']:
    m=M[mk]
    pps=u(ec(m['lt'],'pricePerShare()'))/1e18
    gts=u(ec(m['staker'],'totalSupply()')); gta=u(ec(m['staker'],'totalAssets()'))
    g2lt=gta/gts if gts else 1
    pos=collections.defaultdict(lambda: dict(unst=0.0,st=0.0,type=None))
    # Blockscout balances can be stale (LT token_reduction rebase); re-read balanceOf on-chain
    ltx=[x for x in h[mk+'|lt'] if htype(x)!='gauge']; gx=h[mk+'|gauge']
    bl=batch_calls([(m['lt'],'0x'+sel('balanceOf(address)')+ea(x['addr'])) for x in ltx])
    bg=batch_calls([(m['staker'],'0x'+sel('balanceOf(address)')+ea(x['addr'])) for x in gx])
    for x,b in zip(ltx,bl):
        p=pos[x['addr'].lower()]; p['unst']+=int(b,16)/1e18*pps; p['type']=htype(x)
    for x,b in zip(gx,bg):
        p=pos[x['addr'].lower()]; p['st']+=int(b,16)/1e18*g2lt*pps; p['type']=p['type'] or htype(x)
    vals={a:p['unst']+p['st'] for a,p in pos.items() if p['unst']+p['st']>0}
    tot=sum(vals.values()); srt=sorted(vals.values(),reverse=True)
    hhi=sum((v/tot*100)**2 for v in srt)
    b=collections.OrderedDict((lab,[0,0.0]) for _,_,lab in BUCKETS)
    for v in srt:
        for lo,hi,lab in BUCKETS:
            if lo<=v<hi: b[lab][0]+=1; b[lab][1]+=v
    ty=collections.defaultdict(lambda:[0,0.0])
    for a,v in vals.items(): ty[pos[a]['type']][0]+=1; ty[pos[a]['type']][1]+=v
    st=sum(p['st'] for p in pos.values()); 
    s=dict(market=mk,pps=pps,lt_supply=u(ec(m['lt'],'totalSupply()'))/1e18,gauge_supply=gts/1e18,holders=len(vals),total_btc=tot,staked_btc=st,staked_share=st/tot if tot else 0,top1=srt[0]/tot,top10=sum(srt[:10])/tot,top100=sum(srt[:100])/tot,hhi=hhi,buckets={k:(v[0],round(v[1],3)) for k,v in b.items()},types={k:(v[0],round(v[1],3)) for k,v in ty.items()})
    summary.append(s); print(json.dumps(s))
    for lab,(n,v) in b.items(): rows.append([mk,lab,n,round(v,4),round(v/tot*100,2) if tot else 0])
    res[mk]={a:dict(btc=v,**pos[a]) for a,v in vals.items()}
json.dump(dict(summary=summary,positions=res),open('../raw/holders_btc.json','w'),indent=1)
with open('../holders_buckets.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['market','bucket_btc_equiv','holders','btc_equiv','share_of_market_pct'])
    for r in rows: w.writerow(r)
