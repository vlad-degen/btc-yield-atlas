import json
from addrinfo import classify
from concurrent.futures import ThreadPoolExecutor
rows=json.load(open('../raw/morpho_top_borrowers.json'))
uniq={}
for r in rows: uniq.setdefault((r['chainId'],r['user']),[]).append(r)
def w(k):
    try: return k,classify(*k)
    except Exception as e: return k,{'err':str(e)}
out={}
with ThreadPoolExecutor(6) as ex:
    for k,v in ex.map(w,list(uniq)): out['%d:%s'%k]=v
json.dump(out,open('../raw/morpho_borrowers_classified.json','w'),indent=1)
import collections
print(collections.Counter(v.get('kind','?').split('(')[0] for v in out.values()))
for k,v in sorted(out.items(),key=lambda kv:-sum(x['debt_usd'] for x in uniq[(int(kv[0].split(':')[0]),kv[0].split(':')[1])])):
    ch,a=k.split(':'); debt=sum(x['debt_usd'] for x in uniq[(int(ch),a)])
    if v.get('kind')!='EOA':
        print(f"{ch:>6} {a} ${debt/1e6:7.2f}M {v.get('kind')} safe={v.get('safe',{}).get('threshold')}/{len(v.get('safe',{}).get('owners',[]))} name={v.get('name()')} bs={v.get('bs_name')} impl={v.get('impl')} tags={v.get('tags')} owner={v.get('owner()')}")
