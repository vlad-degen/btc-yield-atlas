# Fetch ERC-20 holders of LT (yb-LP) and gauge tokens from Blockscout
import json,urllib.parse,sys,time
from bs import get
from markets import M
def holders(addr):
    out=[];params=None
    while True:
        url='https://eth.blockscout.com/api/v2/tokens/%s/holders'%addr+('?'+urllib.parse.urlencode(params) if params else '')
        d=get(url); out+=d['items']
        params=d.get('next_page_params')
        if not params: break
        time.sleep(0.2)
    return out
res={}
for k in ['v3-WBTC','v3-cbBTC','v3-tBTC','v2-WBTC','v2-cbBTC','v2-tBTC','v1-WBTC','v1-cbBTC','v1-tBTC']:
    m=M[k]
    for kind,a in [('lt',m['lt']),('gauge',m['staker'])]:
        h=holders(a)
        res[k+'|'+kind]=[dict(addr=x['address']['hash'],is_contract=x['address'].get('is_contract'),name=x['address'].get('name'),value=x['value'],impl=(x['address'].get('implementations') or None)) for x in h]
        print(k,kind,len(h))
json.dump(res,open('../raw/holders_blockscout.json','w'))
