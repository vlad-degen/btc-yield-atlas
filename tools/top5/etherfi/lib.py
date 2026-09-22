import json, urllib.request, time, sys, os, datetime
sys.path.insert(0, os.path.dirname(__file__))
from keccak_lib import keccak
RAW=os.path.join(os.path.dirname(__file__),'..','raw')
RPCS={'eth':['https://ethereum-rpc.publicnode.com','https://eth.drpc.org','https://eth-mainnet.public.blastapi.io','https://gateway.tenderly.co/public/mainnet'],
      'op':['https://optimism-rpc.publicnode.com','https://mainnet.optimism.io','https://optimism.drpc.org'],
      'base':['https://base-rpc.publicnode.com']}
UA={'Content-Type':'application/json','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
def sel(sig): return keccak(sig.encode())[:4].hex()
def topic(sig): return '0x'+keccak(sig.encode()).hex()
def post(url,payload,timeout=60):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=UA)
    return json.loads(urllib.request.urlopen(req,timeout=timeout).read())
def rpc(method,params,chain='eth',tries=3):
    last=None
    for t in range(tries):
        for u in RPCS[chain]:
            try:
                r=post(u,{'jsonrpc':'2.0','id':1,'method':method,'params':params})
                if 'result' in r: return r['result']
                last=r
            except Exception as e: last=str(e)
        time.sleep(1+t)
    raise Exception(f'rpc fail {method} {last}')
def call(to,data,block='latest',chain='eth'):
    if isinstance(block,int): block=hex(block)
    if not data.startswith('0x'): data='0x'+data
    try:
        return rpc('eth_call',[{'to':to,'data':data},block],chain)
    except Exception as e:
        return None
def enc_uint(v): return hex(v)[2:].rjust(64,'0')
def enc_addr(a): return a.lower().replace('0x','').rjust(64,'0')
def c(to,sig,*args,block='latest',chain='eth'):
    return call(to,'0x'+sel(sig)+''.join(args),block=block,chain=chain)
def u(h,i=0):
    if h is None or h=='0x': return None
    h=h[2:]; return int(h[64*i:64*(i+1)],16)
def a(h,i=0):
    if h is None or h=='0x': return None
    h=h[2:]; return '0x'+h[64*i+24:64*(i+1)]
def s(h):
    if h is None or len(h)<4: return None
    h=h[2:]
    if len(h)==64: return bytes.fromhex(h).rstrip(b'\0').decode(errors='replace')
    off=int(h[:64],16)*2; ln=int(h[off:off+64],16)
    return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors='replace')
def bal(tok,holder,block='latest',chain='eth'):
    return u(c(tok,'balanceOf(address)',enc_addr(holder),block=block,chain=chain))
def get(url,tries=4):
    last=None
    for t in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA['User-Agent'],'Accept':'application/json'}),timeout=90).read())
        except Exception as e:
            last=e; time.sleep(2*(t+1))
    raise Exception(f'get fail {url} {last}')
def block_at(ts,chain='eth'):
    # binary search
    lo=1; hi=int(rpc('eth_blockNumber',[],chain),16)
    def bts(n): return int(rpc('eth_getBlockByNumber',[hex(n),False],chain)['timestamp'],16)
    if bts(hi)<=ts: return hi
    while lo<hi:
        mid=(lo+hi+1)//2
        if bts(mid)<=ts: lo=mid
        else: hi=mid-1
    return lo
def dt(ts): return datetime.datetime.fromtimestamp(ts,datetime.UTC).strftime('%Y-%m-%d %H:%M')
def save(name,obj):
    json.dump(obj,open(os.path.join(RAW,name),'w'),indent=1)
def load(name):
    return json.load(open(os.path.join(RAW,name)))
def logs(address=None,topics=None,frm=0,to='latest',chain='eth',step=100000,verbose=False):
    if to=='latest': to=int(rpc('eth_blockNumber',[],chain),16)
    out=[];b=frm
    while b<=to:
        e=min(b+step-1,to)
        f={'fromBlock':hex(b),'toBlock':hex(e)}
        if address: f['address']=address
        if topics: f['topics']=topics
        try:
            r=rpc('eth_getLogs',[f],chain,tries=2)
            out+=r; b=e+1
            if verbose: print(b,len(out),file=sys.stderr)
        except Exception as ex:
            if step<=500: raise
            step=step//4
            if verbose: print('shrink',step,str(ex)[:200],file=sys.stderr)
    return out
def batch_calls(calls,block='latest',chain='eth',chunk=40):
    """calls: list of (to,data). returns list of hex or None"""
    if isinstance(block,int): block=hex(block)
    out=[None]*len(calls)
    for st in range(0,len(calls),chunk):
        sub=calls[st:st+chunk]
        payload=[{'jsonrpc':'2.0','id':i,'method':'eth_call','params':[{'to':t,'data':d if d.startswith('0x') else '0x'+d},block]} for i,(t,d) in enumerate(sub)]
        ok=False
        for t in range(3):
            for url in RPCS[chain]:
                try:
                    r=post(url,payload,timeout=90)
                    if isinstance(r,list):
                        for x in r:
                            out[st+x['id']]=x.get('result')
                        ok=True; break
                except Exception as e: pass
            if ok: break
            time.sleep(2)
        if not ok:
            for i,(to,d) in enumerate(sub): out[st+i]=call(to,d,block,chain)
    return out
