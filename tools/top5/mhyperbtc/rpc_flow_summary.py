# Summarise RPC Transfer logs of a wallet: resolve token symbols; group by token/direction/counterparty
import sys, json, collections; sys.path.insert(0,'scripts')
from rpc import *
chain,fn,W=sys.argv[1],sys.argv[2],sys.argv[3].lower()
d=json.load(open(fn)); L=d['logs']
tok={}
def meta(a):
    if a in tok: return tok[a]
    try: s=dec_str(ecall(chain,a,sel('symbol()')))
    except: s='?'
    try: dcm=int(ecall(chain,a,sel('decimals()')),16)
    except: dcm=18
    tok[a]=(s,dcm); return tok[a]
agg=collections.defaultdict(lambda:[0.0,0,None,None]); 
for l in L:
    if len(l['topics'])<3 or len(l['data'])<66: continue
    a=l['address'].lower(); s,dcm=meta(a)
    fr='0x'+l['topics'][1][-40:]; to='0x'+l['topics'][2][-40:]; v=int(l['data'][:66],16)/10**dcm
    if fr==W: k=(s,a,'OUT',to)
    elif to==W: k=(s,a,'IN',fr)
    else: continue
    g=agg[k]; g[0]+=v; g[1]+=1; bn=int(l['blockNumber'],16); g[2]=min(g[2] or bn,bn); g[3]=max(g[3] or bn,bn)
json.dump({'|'.join(k):v for k,v in agg.items()},open(fn.replace('.json','_summary.json'),'w'),indent=0)
for k,v in sorted(agg.items(),key=lambda kv:(kv[0][0],kv[0][2],-kv[1][0])):
    if v[0]>0: print(f'{k[0]:20s} {k[1]} {k[2]:3s} {v[0]:16,.4f} n={v[1]:4d} blocks {v[2]}..{v[3]} {k[3]}')
