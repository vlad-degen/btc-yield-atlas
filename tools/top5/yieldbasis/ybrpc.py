import json,urllib.request,time,itertools
from eth import sel,keccak
RPCS=['https://eth.drpc.org','https://gateway.tenderly.co/public/mainnet','https://eth-mainnet.public.blastapi.io','https://ethereum-rpc.publicnode.com']
_i=itertools.count()
def rpc(method,params,tries=8):
    last=None
    for k in range(tries):
        u=RPCS[(next(_i))%len(RPCS)]
        try:
            req=urllib.request.Request(u,data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'})
            res=json.loads(urllib.request.urlopen(req,timeout=40).read())
            if 'result' in res: return res['result']
            last=res
            if 'revert' in json.dumps(res).lower() or 'execution' in json.dumps(res).lower(): return None
        except Exception as e:
            last=str(e); time.sleep(0.5)
    raise Exception('rpc fail %s'%last)
def ec(to,sig,args='',block='latest'):
    b=block if isinstance(block,str) else hex(block)
    return rpc('eth_call',[{"to":to,"data":'0x'+sel(sig)+args},b])
def u(x): return None if x in (None,'0x') else int(x[2:66],16)
def words(x):
    if x in (None,'0x'): return None
    h=x[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
def addr(x): return None if x in (None,'0x') else '0x'+x[26:66]
def s(x): 
    if x in (None,'0x'): return x
    return int(x[2:66],16)-(1<<256) if int(x[2:66],16)>=(1<<255) else int(x[2:66],16)
def eu(v): return hex(v)[2:].rjust(64,'0')
def ea(a): return a.lower().replace('0x','').rjust(64,'0')
def batch_calls(calls,block='latest',chunk=40):
    """calls: list of (to,data). returns list of hex results"""
    out=[]
    for i in range(0,len(calls),chunk):
        ch=calls[i:i+chunk]
        payload=[{"jsonrpc":"2.0","id":j,"method":"eth_call","params":[{"to":t,"data":d},block if isinstance(block,str) else hex(block)]} for j,(t,d) in enumerate(ch)]
        for k in range(8):
            u_=RPCS[(next(_i))%len(RPCS)]
            try:
                req=urllib.request.Request(u_,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0 (Macintosh) Chrome/126.0'})
                res=json.loads(urllib.request.urlopen(req,timeout=60).read())
                if isinstance(res,list) and all('result' in r for r in res):
                    res=sorted(res,key=lambda r:r['id']); out+=[r['result'] for r in res]; break
            except Exception as e:
                time.sleep(0.5)
        else:
            raise Exception('batch fail')
    return out
