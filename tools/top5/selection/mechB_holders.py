import json, urllib.request, time, sys
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))
base=sys.argv[1]
for a in sys.argv[2:]:
    try:
        t=get(f'{base}/api/v2/tokens/{a}')
        h=get(f'{base}/api/v2/tokens/{a}/holders')
        dec=int(t.get('decimals') or 18); ts=int(t.get('total_supply') or 0)
        print('==',a,t.get('name'),t.get('symbol'),'holders',t.get('holders_count') or t.get('holders'),'supply',ts/10**dec)
        for x in h['items'][:6]:
            ad=x['address']; print('   ',ad['hash'],ad.get('name'),ad.get('is_contract'),round(int(x['value'])/10**dec,4), f"{int(x['value'])/ts*100:.1f}%" if ts else '')
    except Exception as e: print(a,'ERR',e)
    time.sleep(0.3)
