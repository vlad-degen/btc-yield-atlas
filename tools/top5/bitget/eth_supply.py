"""bgBTC on Ethereum: supply / CCIP-locked / Bitget-hot-wallet history from token transfers (eth.blockscout.com)."""
import json, urllib.request, urllib.parse, datetime, time
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36'
B='https://eth.blockscout.com/api/v2'
T='0x0520930f21b14cafac7a27b102487bee7138a017'; P='0xa1f0caf824d5bbf103b33172a711e58c6cab2a04'; HOT='0x1ab4973a48dc892cd9971ece8e01dcc7688f8f23'
def g(path,params=None):
    u=B+path+('?'+urllib.parse.urlencode(params) if params else '')
    for i in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'user-agent':UA,'accept':'application/json'}),timeout=60))
        except Exception as e: print('exc',e); time.sleep(3*(i+1))
items=[]; params={}
while True:
    r=g(f'/tokens/{T}/transfers',params); items+=r['items']
    if not r.get('next_page_params'): break
    params=r['next_page_params']
json.dump(items,open('../raw/bgbtc_eth_transfers.json','w'))
items.sort(key=lambda x:(x['block_number'],x.get('log_index',0)))
Z='0x0000000000000000000000000000000000000000'
sup=0; pool=0; hot=0; ev=[]
for x in items:
    v=int(x['total']['value'])/1e8; f=x['from']['hash'].lower(); t=x['to']['hash'].lower()
    if f==Z: sup+=v
    if t==Z: sup-=v
    if t==P: pool+=v
    if f==P: pool-=v
    if t==HOT: hot+=v
    if f==HOT: hot-=v
    if f==Z or t==Z or t==P or f==P:
        ev.append(dict(ts=x['timestamp'][:19],kind='mint' if f==Z else 'burn' if t==Z else 'ccip_lock' if t==P else 'ccip_release',amount=v,frm=f,to=t,supply=round(sup,8),pool=round(pool,8),hot=round(hot,8),tx=x['transaction_hash']))
json.dump(ev,open('../raw/bgbtc_eth_supply_events.json','w'),indent=0)
print('transfers',len(items),'final supply',round(sup,6),'pool',round(pool,6),'hot',round(hot,6))
for e in ev:
    if e['amount']>=1: print(e['ts'],e['kind'],e['amount'],'supply',e['supply'],'pool',e['pool'])
