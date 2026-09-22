# Paginate Blockscout v2 token-transfers for an address (any Blockscout host)
import json, sys, urllib.request, urllib.parse, time
UA={'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'}
def get(u):
    for i in range(8):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
        except Exception as e: print('retry',i,e,file=sys.stderr); time.sleep(3+3*i)
    raise Exception('fail '+u)
def transfers(addr,host='https://eth.blockscout.com',extra=''):
    u=f'{host}/api/v2/addresses/{addr}/token-transfers'; out=[]; p=None
    while True:
        q=(urllib.parse.urlencode(p)+'&' if p else '')+extra
        d=get(u+('?'+q if q else '')); out+=d['items']; p=d.get('next_page_params')
        if not p: break
        time.sleep(0.2)
    return out
if __name__=='__main__':
    addr,fn=sys.argv[1],sys.argv[2]; host=sys.argv[3] if len(sys.argv)>3 else 'https://eth.blockscout.com'
    L=transfers(addr,host); json.dump(L,open(fn,'w')); print(len(L))
