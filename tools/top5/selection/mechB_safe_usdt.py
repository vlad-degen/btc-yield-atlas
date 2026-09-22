import json, urllib.request, time, sys
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))
for a in sys.argv[1:]:
    d=get(f'https://eth.blockscout.com/api/v2/addresses/{a}/token-transfers?type=ERC-20')
    items=d['items']
    np=d.get('next_page_params'); n=0
    while np and n<5:
        d=get(f'https://eth.blockscout.com/api/v2/addresses/{a}/token-transfers?type=ERC-20&'+'&'.join(f'{k}={v}' for k,v in np.items())); items+=d['items']; np=d.get('next_page_params'); n+=1; time.sleep(0.3)
    json.dump(items, open(f'../raw/mechB/tt_{a}.json','w'))
    print('==',a,len(items),'transfers')
    for t in reversed(items):
        tok=t['token']; dec=int(tok.get('decimals') or 18); v=int(t['total']['value'])/10**dec
        if v*(float(tok.get('exchange_rate') or 1))>100000:
            print(' ',t['timestamp'][:10], tok['symbol'], round(v,2), t['from']['hash'][:10], t['from'].get('name') or '', ((t['from'].get('metadata') or {}).get('tags') or [{}])[0].get('name',''), '->', t['to']['hash'][:10], t['to'].get('name') or '', ((t['to'].get('metadata') or {}).get('tags') or [{}])[0].get('name',''))
