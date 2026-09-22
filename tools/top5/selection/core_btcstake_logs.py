# Scan Core BitcoinStake (0x...1014) delegated / btcExpired / undelegated events via public RPC
import json, urllib.request, sys, time
RPC='https://rpc.coredao.org'
ADDR='0x0000000000000000000000000000000000001014'
T={'delegated':'0x3391934a441f8a4f5bd3ffdc8b4c59b386061114e16b83d51cc73b1e41c0c0a0',
   'btcExpired':'0xab9cd399cf9f01321f73b32d2b1e2c6034d379277171bcd887b269416c0ef3bb',
   'undelegated':'0x11e4685d914d513c078f2520ce18170550bf421495a0b11d9a2e82b0ac02ac32'}
def rpc(method, params):
    for i in range(5):
        try:
            req=urllib.request.Request(RPC, data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(), headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
            r=json.load(urllib.request.urlopen(req, timeout=120))
            if 'error' in r: raise Exception(r['error'])
            return r['result']
        except Exception as e:
            print('retry',method,e,file=sys.stderr); time.sleep(3)
    raise SystemExit('rpc failed')
latest=int(rpc('eth_blockNumber',[]),16)
out={k:[] for k in T}
step=int(sys.argv[1]) if len(sys.argv)>1 else 2000000
b=int(sys.argv[2]) if len(sys.argv)>2 else 0
while b<=latest:
    e=min(b+step-1,latest)
    for k,t in T.items():
        logs=rpc('eth_getLogs',[{'address':ADDR,'fromBlock':hex(b),'toBlock':hex(e),'topics':[t]}])
        out[k]+=logs
    print(b,e,{k:len(v) for k,v in out.items()},file=sys.stderr)
    b=e+1
json.dump({'latest':latest,'logs':out}, open(sys.argv[3] if len(sys.argv)>3 else 'core_btcstake_logs.json','w'))
