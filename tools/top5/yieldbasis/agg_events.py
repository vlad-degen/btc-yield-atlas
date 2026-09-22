# Aggregate YB API event datasets (interest collected, LT/gauge flows) per market per month
import json,collections,datetime
from load import NAMES
def mon(t): return datetime.datetime.fromtimestamp(t,datetime.UTC).strftime('%Y-%m')
fe=json.load(open('../raw/api/fees_amm_all.json'))
I=collections.defaultdict(float); D=collections.defaultdict(list)
for r in fe:
    k=(int(r['marketId']),mon(r['blockTimestamp'])); I[k]+=int(r['amountUsdRaw'])/1e18; D[k].append(int(r['debtRaw'])/1e18)
fl=json.load(open('../raw/api/flows_all.json'))
F=collections.defaultdict(lambda: collections.defaultdict(float)); U=collections.defaultdict(set)
for r in fl:
    k=(int(r['marketId']),mon(r['blockTimestamp']))
    dec=r['assetDecimals']; amt=int(r['assetsRaw'])/10**dec
    if r['venue']=='lt':
        tag=('mig_' if r['isMigration'] else '')+r['flowType']
        F[k][tag]+=amt; F[k][tag+'_usd']+=int(r['assetsUsdRaw'])/1e18; F[k][tag+'_n']+=1
        if r['flowType']=='deposit' and not r['isMigration']: U[k].add(r['resolvedOwner'])
    else:
        F[k]['gauge_'+r['flowType']+('_mig' if r['isMigration'] else '')]+=int(r['sharesRaw'])/1e18
out={}
for k in sorted(set(I)|set(F)):
    m,mo=k
    d=dict(market=NAMES[m],month=mo,interest_usd=round(I.get(k,0),2),avg_debt=round(sum(D[k])/len(D[k]),0) if D.get(k) else None)
    d.update({kk:round(v,6) for kk,v in F[k].items()}); d['unique_depositors']=len(U[k])
    out['%s|%s'%(NAMES[m],mo)]=d
json.dump(out,open('../raw/agg_events_monthly.json','w'),indent=1)
for k,v in out.items():
    if v['market'].startswith('v') and 'WETH' not in v['market']: print(k,{kk:vv for kk,vv in v.items() if kk in('interest_usd','avg_debt','deposit','withdraw','mig_deposit','mig_withdraw','unique_depositors')})
