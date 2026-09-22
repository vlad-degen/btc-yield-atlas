import json
from addrinfo import classify
from concurrent.futures import ThreadPoolExecutor
d=json.load(open('../raw/aave_spark_btc_borrowers.json'))
rows=[(k,r) for k,v in d.items() for r in v if r['stable_debt']>=2e6]
print('candidates',len(rows))
def w(kr):
    k,r=kr
    try: return k,r,classify(r['chain'],r['user'])
    except Exception as e: return k,r,{'err':str(e)}
out=[]
with ThreadPoolExecutor(4) as ex:
    for k,r,c in ex.map(w,rows):
        r['class']=c; r['market']=k; out.append(r)
json.dump(out,open('../raw/aave_spark_classified.json','w'),indent=1)
import collections
print(collections.Counter(r['class'].get('kind','?').split('(')[0] for r in out))
for r in sorted(out,key=lambda r:-r['stable_debt']):
    c=r['class']
    if c.get('kind')!='EOA':
        print(r['market'],r['user'],'stable $%.2fM'%(r['stable_debt']/1e6),r['btc_coll'],c.get('kind'),'safe',(c.get('safe') or {}).get('threshold'),len((c.get('safe') or {}).get('owners',[])),'name',c.get('name()'),'bs',c.get('bs_name'),'impl',c.get('impl'),'owner',c.get('owner()'))
