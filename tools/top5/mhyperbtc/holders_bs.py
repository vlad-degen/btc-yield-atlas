# Current token holders via Blockscout v2 (Ethereum, Rootstock)
import json, sys, urllib.request, urllib.parse, time
UA={'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'}
def get(u):
    for i in range(8):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
        except Exception as e: print('retry',e,file=sys.stderr); time.sleep(3+2*i)
def holders(host,token):
    u=f'{host}/api/v2/tokens/{token}/holders'; out=[]; p=None
    while True:
        d=get(u+('?'+urllib.parse.urlencode(p) if p else '')); out+=d['items']; p=d.get('next_page_params')
        if not p: break
    return out
if __name__=='__main__':
    host,token,fn=sys.argv[1:4]
    H=holders(host,token)
    rows=[{'address':h['address']['hash'],'is_contract':h['address'].get('is_contract'),'name':h['address'].get('name'),'impl':[i.get('name') for i in (h['address'].get('implementations') or [])],'value':int(h['value'])/1e18} for h in H]
    json.dump(rows,open(fn,'w'),indent=0); print(len(rows), sum(r['value'] for r in rows))
