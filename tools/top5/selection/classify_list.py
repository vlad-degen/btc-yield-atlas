import sys, json
from addrinfo import classify
from concurrent.futures import ThreadPoolExecutor
ch=int(sys.argv[1]); addrs=sys.argv[2:]
def w(a):
    try: return a,classify(ch,a)
    except Exception as e: return a,{'err':str(e)}
with ThreadPoolExecutor(4) as ex:
    for a,d in ex.map(w,addrs):
        print(a,d.get('kind'),'safe=%s'%(str(d['safe']['threshold'])+'/'+str(len(d['safe']['owners'])) if d.get('safe') else None),'name=',d.get('name()'),'bs=',d.get('bs_name'),'impl=',d.get('impl'),'owner=',d.get('owner()'),'tags=',d.get('tags'),'ens=',d.get('ens'), d.get('err',''))
