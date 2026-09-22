import json, urllib.request, time, sys
B='https://api.explorer.mezo.org/api/v2'
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
def get(p): return json.load(urllib.request.urlopen(urllib.request.Request(B+p, headers=H), timeout=40))
addr=sys.argv[1]; minamt=float(sys.argv[2]) if len(sys.argv)>2 else 1000
params=''; allt=[]
for page in range(30):
    d=get(f'/addresses/{addr}/token-transfers?type=ERC-20{params}')
    allt+=d['items']
    np=d.get('next_page_params')
    if not np: break
    params='&'+'&'.join(f'{k}={v}' for k,v in np.items()); time.sleep(0.2)
json.dump(allt, open(f'../raw/mechB/mezo_tt_full_{addr}.json','w'))
print(len(allt),'transfers')
for t in reversed(allt):
    tok=t['token']; dec=int(tok.get('decimals') or 18); v=int(t['total']['value'])/10**dec
    if (tok['symbol'] in ('MUSD','sMUSD','BTC','mUSDC','morphoBTC-mUSDC') and v>=minamt/ (1 if tok['symbol']!='BTC' else 100000)):
        print(t['timestamp'][:10], tok['symbol'], round(v,4), t['from']['hash'][:12], t['from'].get('name'), '->', t['to']['hash'][:12], t['to'].get('name'), t.get('method'))
