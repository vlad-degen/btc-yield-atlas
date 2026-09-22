# Minimal JSON-RPC helpers for the mHyperBTC deep dive
import json, urllib.request, time
RPCS={
 'eth':['https://ethereum-rpc.publicnode.com','https://eth.drpc.org'],
 'eth_arch':['https://rpc.mevblocker.io','https://eth-mainnet.public.blastapi.io','https://gateway.tenderly.co/public/mainnet','https://eth.drpc.org'],
 'monad':['https://rpc.monad.xyz','https://monad-mainnet.drpc.org','https://rpc1.monad.xyz','https://rpc3.monad.xyz'],
 'rsk':['https://public-node.rsk.co','https://rootstock.drpc.org'],
 'stable':['https://rpc.stable.xyz','https://stable-mainnet.drpc.org'],
}
UA={'content-type':'application/json','user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'}
def post(url,payload,timeout=60):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=UA)
    return json.load(urllib.request.urlopen(req,timeout=timeout))
def call(chain,method,params,tries=6):
    urls=RPCS.get(chain,[chain]); err=None
    for i in range(tries):
        u=urls[i%len(urls)]
        try:
            r=post(u,{'jsonrpc':'2.0','id':1,'method':method,'params':params})
            if 'error' in r: err=r['error']; 
            else: return r['result']
        except Exception as e: err=e
        time.sleep(0.5*(i+1))
    raise Exception(f'{chain} {method} failed: {err}')
def ecall(chain,to,data,block='latest'):
    if isinstance(block,int): block=hex(block)
    return call(chain,'eth_call',[{'to':to,'data':data},block])
def words(h):
    h=h[2:] if h.startswith('0x') else h
    return [int(h[i:i+64],16) for i in range(0,len(h),64)]
def a32(a): return a.lower().replace('0x','').rjust(64,'0')
def u32(n): return hex(n)[2:].rjust(64,'0')
def bal(chain,token,holder,block='latest'):
    return int(ecall(chain,token,'0x70a08231'+a32(holder),block),16)
def supply(chain,token,block='latest'):
    return int(ecall(chain,token,'0x18160ddd',block),16)
def blocknum(chain): return int(call(chain,'eth_blockNumber',[]),16)
def block_ts(chain,n): return int(call(chain,'eth_getBlockByNumber',[hex(n),False])['timestamp'],16)
def block_at(chain,ts):
    hi=blocknum(chain); lo=1
    # binary search
    while lo<hi:
        mid=(lo+hi+1)//2
        if block_ts(chain,mid)<=ts: lo=mid
        else: hi=mid-1
    return lo
try:
    from Crypto.Hash import keccak as _k
    def k256(b):
        k=_k.new(digest_bits=256); k.update(b); return k.hexdigest()
    def sel(sig): return '0x'+k256(sig.encode())[:8]
    def topic(sig): return '0x'+k256(sig.encode())
except ImportError:
    pass
def dec_str(h):
    h=h[2:] if h.startswith('0x') else h
    if len(h)<128:
        return bytes.fromhex(h).rstrip(b'\0').decode(errors='replace')
    off=int(h[:64],16)*2; ln=int(h[off:off+64],16)
    return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors='replace')
def getlogs(chain,addr,topics,frm,to,step=50000):
    out=[]; a=frm
    while a<=to:
        b=min(a+step-1,to)
        try:
            r=call(chain,'eth_getLogs',[{'address':addr,'topics':topics,'fromBlock':hex(a),'toBlock':hex(b)}])
            out+=r; a=b+1
        except Exception as e:
            if step<=100: raise
            step//=4
    return out
