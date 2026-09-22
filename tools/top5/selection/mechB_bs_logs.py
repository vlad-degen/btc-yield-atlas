import json, urllib.request, time, sys
base=sys.argv[1]; addr=sys.argv[2]; maxpages=int(sys.argv[3]) if len(sys.argv)>3 else 50
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
def get(p): return json.load(urllib.request.urlopen(urllib.request.Request(base+p, headers=H), timeout=60))
params=''; out=[]
for page in range(maxpages):
    for i in range(3):
        try: d=get(f'/api/v2/addresses/{addr}/logs{params}'); break
        except Exception as e: time.sleep(2)
    out+=d['items']
    np=d.get('next_page_params')
    if not np: break
    params='?'+'&'.join(f'{k}={v}' for k,v in np.items()); time.sleep(0.25)
json.dump(out, open(f'../raw/mechB/logs_{addr}.json','w'))
print(len(out),'logs')
