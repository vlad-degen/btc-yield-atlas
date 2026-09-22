# Current holders per chain, BTC-eq buckets, top-N concentration, contract vs EOA, collateral re-use (look-through)
import sys,json,csv,collections; sys.path.insert(0,'scripts')
from rpc import *
NAV=1.02606813
ETH=json.load(open('raw/holders_eth_rpc.json'))                   # from full Transfer-log replay (reconciles to totalSupply)
from token_transfers_rpc import balances
MON={a:v/1e18 for a,v in balances(json.load(open('raw/monad_mhyperbtc_transfers.json'))['logs']).items() if v>0 and a!='0x'+'0'*40}
RSKbs=json.load(open('raw/holders_rsk.json'))
RSK={}
for h in RSKbs:
    b=bal('rsk','0x7F71f02aE0945364F658860d67dbc10c86Ca3a3C',h['address'])/1e18
    if b>0: RSK[h['address'].lower()]=b
print('rsk verified sum',sum(RSK.values()),'n',len(RSK))
LAB={'0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb':'contract: Morpho Blue (collateral)','0x95fc228a926828b4d95f52c1d52b345e743153f0':'contract: Pendle SY (PT/YT/LP)',
 '0xd5d960e8c380b724a48ac59e2dff1b2cb4a1eaee':'contract: Morpho Blue Monad (collateral)','0xde613a694874484a983ad8fc367e156e094da746':'contract: Uniswap V3 pool (Rootstock)',
 '0x4eac61bd2efb19df67d23df775fe447b67d267b4':'contract: aToken (Rootstock lending)','0x9c8abfb7466de265a00223ece1aa71c270969d36':'contract: Uniswap V3 pool (Rootstock)',
 '0xa100b72bf090e813a117e46939bf02e39ef2dcae':'Midas: instant-redemption fee wallet','0x933adedd85824da75ec8a334a7907e69e7c02833':'Midas: strategy wallet SMA1'}
def kind(chain,a):
    if a in LAB: return LAB[a]
    code=call({'ethereum':'eth','monad':'monad','rootstock':'rsk'}[chain],'eth_getCode',[a,'latest'])
    if code=='0x': return 'EOA'
    if code.startswith('0xef0100'): return 'EOA (EIP-7702 delegated)'
    return 'contract: other'
rows=[]
for chain,H in [('ethereum',ETH),('monad',MON),('rootstock',RSK)]:
    for a,v in H.items():
        rows.append(dict(chain=chain,address=a,mhyperbtc=v,btc_eq=v*NAV,type=kind(chain,a.lower())))
json.dump(rows,open('raw/holders_current.json','w'),indent=0)
B=[('<0.01',0,0.01),('0.01-0.1',0.01,0.1),('0.1-1',0.1,1),('1-10',1,10),('10-100',10,100),('>100',100,1e9)]
out=[]
for chain in ['ethereum','monad','rootstock','all']:
    R=[r for r in rows if chain=='all' or r['chain']==chain]
    tot=sum(r['btc_eq'] for r in R)
    for name,lo,hi in B:
        S=[r for r in R if lo<=r['btc_eq']<hi]
        out.append(dict(chain=chain,bucket_btc_eq=name,holders=len(S),btc_eq=round(sum(r['btc_eq'] for r in S),4),share=round(sum(r['btc_eq'] for r in S)/tot,4) if tot else 0,
                        contracts=sum(1 for r in S if r['type'].startswith('contract')),eoas=sum(1 for r in S if r['type'].startswith('EOA') or r['type'].startswith('Midas')),note=''))
    out.append(dict(chain=chain,bucket_btc_eq='TOTAL',holders=len(R),btc_eq=round(tot,4),share=1.0,contracts=sum(1 for r in R if r['type'].startswith('contract')),eoas=sum(1 for r in R if not r['type'].startswith('contract')),note=''))
# concentration (address level, all chains) and look-through
allr=sorted(rows,key=lambda r:-r['btc_eq']); tot=sum(r['btc_eq'] for r in allr)
for n in (1,10,100):
    out.append(dict(chain='all',bucket_btc_eq=f'top{n}_addresses',holders=min(n,len(allr)),btc_eq=round(sum(r['btc_eq'] for r in allr[:n]),4),share=round(sum(r['btc_eq'] for r in allr[:n])/tot,4),contracts='',eoas='',note='address level, contracts counted as holders'))
# look-through: replace Morpho contracts by borrowers' collateral
LT=collections.Counter()
for r in rows:
    if r['address'].lower() in ('0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb','0xd5d960e8c380b724a48ac59e2dff1b2cb4a1eaee'): continue
    LT[r['address'].lower()]+=r['btc_eq']
for a,v in [('0x763f13d4e788c9a61fa87ec160868c35fa26603f',49.2794),('0xcc63cc49db99f9e228470cec57b64190bd019a74',10.8531),('0x6108c803c9ad8ea24f9fe70b72e57d8d0e80a64f',9.9076),('0x265f29c9138e4cbe1ebd7c7302f082524837015b',0.1726),('0xcc63cc49db99f9e228470cec57b64190bd019a74',57.0733)]:
    LT[a]+=v*NAV
lt=sorted(LT.items(),key=lambda kv:-kv[1]); tl=sum(LT.values())
for n in (1,4,10):
    out.append(dict(chain='all',bucket_btc_eq=f'top{n}_lookthrough',holders=n,btc_eq=round(sum(v for _,v in lt[:n]),4),share=round(sum(v for _,v in lt[:n])/tl,4),contracts='',eoas='',note='Morpho collateral attributed to borrowers; Pendle SY kept as one holder: '+'; '.join(f'{a[:10]} {v:.1f}' for a,v in lt[:n])))
reuse=sum(r['btc_eq'] for r in rows if r['type'].startswith('contract: Morpho'))+sum(r['btc_eq'] for r in rows if 'Pendle' in r['type'])+sum(r['btc_eq'] for r in rows if 'Rootstock' in r['type'])
out.append(dict(chain='all',bucket_btc_eq='in_defi_contracts',holders='',btc_eq=round(reuse,4),share=round(reuse/tot,4),contracts='',eoas='',note='Morpho collateral (ETH 70.21 + Monad 57.07 mHyperBTC) + Pendle SY 36.13 + Rootstock pools/aToken'))
with open('holders_buckets.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for o in out: print(o)
