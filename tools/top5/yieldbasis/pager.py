import sys,json,time
from ybapi import api
name,path=sys.argv[1],sys.argv[2]
extra=dict(a.split('=') for a in sys.argv[3:])
out=[];off=0
while True:
    d=api(path,chainId=1,limit=200,offset=off,isDesc='false',includeLegacy='true',**extra)
    if 'data' not in d: print('ERR',off,d); time.sleep(3); continue
    rows=d['data']; out+=rows; off+=len(rows)
    tc=int(d.get('totalCount',0))
    if not rows or off>=tc: break
json.dump(out,open('../raw/api/%s_all.json'%name,'w'))
print(name,len(out))
