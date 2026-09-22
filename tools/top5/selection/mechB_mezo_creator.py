import json, urllib.request, time, sys
B='https://api.explorer.mezo.org/api/v2'
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
def get(p):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+p, headers=H), timeout=40))
addr='0x123694886DBf5Ac94DDA07135349534536D14cAf'
params=''; created=[]
for page in range(40):
    d=get(f'/addresses/{addr}/transactions?filter=from{params}')
    for t in d['items']:
        if t.get('created_contract'):
            c=t['created_contract']; created.append((t['block_number'], c.get('hash'), c.get('name'), t['timestamp']))
    np=d.get('next_page_params')
    if not np: break
    params='&'+'&'.join(f'{k}={v}' for k,v in np.items())
    time.sleep(0.2)
json.dump(created, open('../raw/mechB/mezo_creator_contracts.json','w'))
for c in created:
    if c[0]>=8400000: print(c)
print(len(created),'contracts created')
