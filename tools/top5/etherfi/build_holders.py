import lib,csv,os,collections,bisect
OUT=os.path.join(os.path.dirname(__file__),'..')
RATE=1.03424999  # accountant rate at 2026-09-20 14:00 UTC snapshot
BTCPX=None
mb=lib.load('month_blocks.json')
import json
px=json.load(open(lib.RAW+'/btc_px.json')); pts=[p[0] for p in px]; BTCPX=px[bisect.bisect_right(pts,mb['2026-09-20']['ts'])-1][1]
ec=lib.load('eth_holders_class.json')
try:
    oc=lib.load('op_holders_class.json'); src_op='RPC balanceOf over all 1,363 addresses seen in OP Transfer logs + Blockscout list'
    if not oc: raise Exception()
except Exception:
    oc=lib.load('op_holders_class_bs.json'); src_op='Blockscout holder list re-read via RPC balanceOf (99.94% of supply)'
ocb=lib.load('op_holders_class_bs.json')
for a,v in oc.items():
    if a in ocb and ocb[a].get('impl'): v['impl']=ocb[a]['impl']
BK=[(0,0.01,'<0.01'),(0.01,0.1,'0.01-0.1'),(0.1,1,'0.1-1'),(1,10,'1-10'),(10,100,'10-100'),(100,1e9,'>100')]
def typ(v,chain):
    t=v['type']
    if chain=='optimism' and t=='Safe multisig' and 'GnosisSafeL2' in (v.get('impl') or []): return 'Safe multisig (GnosisSafeL2)'
    if chain=='optimism' and t=='Safe multisig': return 'ether.fi Cash account (EtherFiSafe / Safe-type contract)'
    if chain=='optimism' and 'HubInstance' in (v.get('impl') or []): return 'Aave v4 HubInstance (other)'
    if chain=='optimism' and 'TopUpDest' in (v.get('impl') or []): return 'ether.fi Cash TopUpDest'
    return t
rows=[]
def analyze(chain,cl):
    vals={a:v['shares']*RATE for a,v in cl.items() if v['shares']>0}
    tot=sum(vals.values()); n=len(vals)
    for lo,hi,lab in BK:
        sel=[x for x in vals.values() if lo<=x<hi]
        rows.append(['bucket_btc_eq',chain,lab,len(sel),round(sum(sel),4),round(sum(sel)/tot*100,2)])
    srt=sorted(vals.values(),reverse=True)
    for k in [1,10,100]:
        rows.append(['concentration',chain,f'top{k}_share',min(k,n),round(sum(srt[:k]),4),round(sum(srt[:k])/tot*100,2)])
    hhi=sum((x/tot*100)**2 for x in srt)
    rows.append(['concentration',chain,'HHI (0-10000)',n,round(tot,4),round(hhi,0)])
    tc=collections.defaultdict(lambda:[0,0])
    for a,v in cl.items():
        if v['shares']<=0: continue
        t=typ(v,chain); tc[t][0]+=1; tc[t][1]+=v['shares']*RATE
    for t,(c,b) in sorted(tc.items(),key=lambda x:-x[1][1]):
        rows.append(['address_type',chain,t,c,round(b,4),round(b/tot*100,2)])
    rows.append(['total',chain,'all holders',n,round(tot,4),100.0])
    return vals
ve=analyze('ethereum',ec); vo=analyze('optimism',oc)
comb={}
for d in (ve,vo):
    for a,x in d.items(): comb[a]=comb.get(a,0)+x
# combined buckets (address-level; Aave v4 Hub counted as one address)
tot=sum(comb.values())
for lo,hi,lab in BK:
    sel=[x for x in comb.values() if lo<=x<hi]
    rows.append(['bucket_btc_eq','combined',lab,len(sel),round(sum(sel),4),round(sum(sel)/tot*100,2)])
srt=sorted(comb.values(),reverse=True)
for k in [1,10,100]: rows.append(['concentration','combined',f'top{k}_share',k,round(sum(srt[:k]),4),round(sum(srt[:k])/tot*100,2)])
rows.append(['concentration','combined','HHI (0-10000)',len(srt),round(tot,4),round(sum((x/tot*100)**2 for x in srt),0)])
# retail vs whale (Ethereum, EOA-level): whale >=10 BTC
w=[x for x in ve.values() if x>=10]; r=[x for x in ve.values() if x<1]
rows.append(['retail_vs_whale','ethereum','holders >=10 BTC-eq (whales)',len(w),round(sum(w),4),round(sum(w)/sum(ve.values())*100,2)])
rows.append(['retail_vs_whale','ethereum','holders <1 BTC-eq (retail)',len(r),round(sum(r),4),round(sum(r)/sum(ve.values())*100,2)])
with open(os.path.join(OUT,'holders_buckets.csv'),'w',newline='') as f:
    wr=csv.writer(f); wr.writerow(['section','chain','label','holders','btc_eq','share_pct_or_value'])
    wr.writerow(['meta','all',f'snapshot 2026-09-20 14:00 UTC; BTC-eq = shares x {RATE}; BTC ${BTCPX:,.0f}; OP source: {src_op}; Ethereum: full replay of share Transfer logs','','',''])
    for x in rows: wr.writerow(x)
for x in rows: print(x)
