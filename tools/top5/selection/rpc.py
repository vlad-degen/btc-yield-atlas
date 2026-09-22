import json, urllib.request, time
from Crypto.Hash import keccak
RPCS={'eth':'https://ethereum-rpc.publicnode.com','base':'https://base-rpc.publicnode.com','etha':'https://gateway.tenderly.co/public/mainnet','etha2':'https://eth-mainnet.public.blastapi.io','etha3':'https://eth.drpc.org'}
def k256(b):
    k=keccak.new(digest_bits=256); k.update(b); return k.digest()
def sel(sig): return '0x'+k256(sig.encode()).hex()[:8]
def post(url,payload,retries=10):
    body=json.dumps(payload).encode()
    for i in range(retries):
        try:
            req=urllib.request.Request(url,data=body,headers={'content-type':'application/json','user-agent':'curl/8'})
            return json.load(urllib.request.urlopen(req,timeout=90))
        except Exception as e:
            print('rpc exc',url,e); time.sleep(3*(i+1))
    raise Exception('rpc failed')
def call(chain,method,params):
    r=post(RPCS.get(chain,chain),{'jsonrpc':'2.0','id':1,'method':method,'params':params})
    if 'error' in r: raise Exception(str(r['error']))
    return r['result']
def batch(chain,calls):
    payload=[{'jsonrpc':'2.0','id':i,'method':m,'params':p} for i,(m,p) in enumerate(calls)]
    r=post(RPCS.get(chain,chain),payload)
    if isinstance(r,dict): raise Exception(str(r))
    r=sorted(r,key=lambda x:x['id'])
    return [x.get('result') if 'result' in x else ('ERR',x.get('error')) for x in r]
def eth_call(chain,to,data,block='latest'):
    return call(chain,'eth_call',[{'to':to,'data':data},block])
def enc_addr(a): return a.lower().replace('0x','').rjust(64,'0')
def enc_uint(n): return hex(n)[2:].rjust(64,'0')
def dec_uint(h,i=0):
    h=h[2:] if h.startswith('0x') else h
    return int(h[64*i:64*(i+1)],16)
def dec_str(h):
    h=h[2:]
    if len(h)<128: 
        try: return bytes.fromhex(h).rstrip(b'\0').decode()
        except: return h
    off=int(h[:64],16)*2; ln=int(h[off:off+64],16)
    return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors='replace')
