import lib,json,urllib.request,time,concurrent.futures as cf
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
T=lib.topic('Transfer(address,address,uint256)')
urls=['https://mainnet.optimism.io','https://optimism.drpc.org','https://op-pokt.nodies.app']
start=150000000; head=int(lib.rpc('eth_blockNumber',[],'op'),16)
ranges=[(b,min(b+9999,head)) for b in range(start,head+1,10000)]
def fetch(rg,i=[0]):
    for t in range(8):
        u=urls[(hash(rg)+t)%len(urls)]
        try:
            r=lib.post(u,{'jsonrpc':'2.0','id':1,'method':'eth_getLogs','params':[{'address':V,'topics':[T],'fromBlock':hex(rg[0]),'toBlock':hex(rg[1])}]},timeout=60)
            if 'result' in r: return r['result']
        except Exception as e: pass
        time.sleep(1+t)
    raise Exception('fail %s'%(rg,))
out=[]
with cf.ThreadPoolExecutor(6) as ex:
    for res in ex.map(fetch,ranges): out+=res
out.sort(key=lambda l:(int(l['blockNumber'],16),int(l['logIndex'],16)))
lib.save('share_transfers_op.json',out); print('op logs',len(out),'ranges',len(ranges))
