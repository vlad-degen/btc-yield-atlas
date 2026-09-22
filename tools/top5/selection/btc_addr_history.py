import json,sys,urllib.request,datetime,time
a=sys.argv[1]; out=[]; last=None
while True:
    u=f'https://mempool.space/api/address/{a}/txs/chain'+(f'/{last}' if last else '')
    page=json.load(urllib.request.urlopen(u,timeout=60))
    if not page: break
    out+=page; last=page[-1]['txid']
    if len(page)<25: break
    time.sleep(0.3)
json.dump(out,open(sys.argv[2],'w'))
print('txs',len(out))
