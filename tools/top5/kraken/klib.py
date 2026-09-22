"""Minimal on-chain helper: pure-python keccak256, ABI encode/decode, JSON-RPC via curl."""
import json, subprocess, time, sys

# ---------------- keccak256 (pure python) ----------------
RC = [0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,0x000000000000808B,0x0000000080000001,
      0x8000000080008081,0x8000000000008009,0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,
      0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,0x8000000000008002,0x8000000000000080,
      0x000000000000800A,0x800000008000000A,0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
ROT = [[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]
M64 = (1<<64)-1
def _rol(x,n): n%=64; return ((x<<n)|(x>>(64-n))) & M64
def _f(A):
    for rnd in range(24):
        C=[A[x][0]^A[x][1]^A[x][2]^A[x][3]^A[x][4] for x in range(5)]
        D=[C[(x-1)%5]^_rol(C[(x+1)%5],1) for x in range(5)]
        A=[[A[x][y]^D[x] for y in range(5)] for x in range(5)]
        B=[[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                B[y][(2*x+3*y)%5]=_rol(A[x][y],ROT[x][y])
        A=[[B[x][y]^((~B[(x+1)%5][y])&B[(x+2)%5][y]) for y in range(5)] for x in range(5)]
        A[0][0]^=RC[rnd]
    return A
def keccak(data: bytes) -> bytes:
    rate=136
    p=bytearray(data); p.append(0x01)
    while len(p)%rate: p.append(0)
    p[-1]|=0x80
    A=[[0]*5 for _ in range(5)]
    for off in range(0,len(p),rate):
        blk=p[off:off+rate]
        for i in range(rate//8):
            x,y=i%5,i//5
            A[x][y]^=int.from_bytes(blk[8*i:8*i+8],'little')
        A=_f(A)
    out=b''
    for i in range(4):
        x,y=i%5,i//5
        out+=A[x][y].to_bytes(8,'little')
    return out
def sel(sig): return keccak(sig.encode())[:4].hex()
def topic(sig): return '0x'+keccak(sig.encode()).hex()

# ---------------- ABI ----------------
def enc_addr(a): return a.lower().replace('0x','').rjust(64,'0')
def enc_uint(n): return hex(n)[2:].rjust(64,'0')
def enc_b32(b): return b.lower().replace('0x','').rjust(64,'0')
def words(h):
    h=h[2:] if h.startswith('0x') else h
    return [int(h[i:i+64],16) for i in range(0,len(h),64)]
def dec_addr(w): return '0x'+hex(w)[2:].rjust(40,'0')
def dec_string(h):
    h=h[2:] if h.startswith('0x') else h
    if len(h)<128: return None
    off=int(h[0:64],16)*2; ln=int(h[off:off+64],16)
    return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors='replace')

# ---------------- RPC ----------------
RPCS = {
 'eth': ['https://rpc.mevblocker.io','https://eth-mainnet.public.blastapi.io','https://mainnet.gateway.tenderly.co','https://eth.drpc.org','https://eth.merkle.io','https://ethereum-rpc.publicnode.com'],
 'ink': ['https://rpc-gel.inkonchain.com','https://ink.drpc.org','https://rpc-qnd.inkonchain.com'],
}
def _post(url, payload, timeout=60):
    r=subprocess.run(['curl','-s','-m',str(timeout),'-X','POST','-H','Content-Type: application/json','--data-binary','@-',url],
                     input=json.dumps(payload).encode(),capture_output=True)
    return json.loads(r.stdout.decode()) if r.stdout else None
def rpc(chain, method, params, tries=3):
    last=None
    for url in RPCS[chain]:
        for t in range(tries):
            try:
                res=_post(url,{'jsonrpc':'2.0','id':1,'method':method,'params':params})
                if res is None: last='empty'; time.sleep(1); continue
                if 'error' in res:
                    last=res['error']
                    msg=str(res['error'])
                    if 'revert' in msg.lower() or 'execution' in msg.lower(): return {'error':res['error']}
                    time.sleep(1); continue
                return res['result']
            except Exception as e:
                last=str(e); time.sleep(1)
    return {'error':last}
def call(chain, to, data, block='latest'):
    if isinstance(block,int): block=hex(block)
    if not data.startswith('0x'): data='0x'+data
    return rpc(chain,'eth_call',[{'to':to,'data':data},block])
def callsig(chain,to,sig,args='',block='latest'):
    return call(chain,to,sel(sig)+args,block)
def u(chain,to,sig,args='',block='latest',idx=0):
    r=callsig(chain,to,sig,args,block)
    if isinstance(r,dict) or r in (None,'0x'): return r
    return words(r)[idx]
def a(chain,to,sig,args='',block='latest'):
    r=callsig(chain,to,sig,args,block)
    if isinstance(r,dict) or r in (None,'0x'): return r
    return dec_addr(words(r)[0])
def s(chain,to,sig,args='',block='latest'):
    r=callsig(chain,to,sig,args,block)
    if isinstance(r,dict) or r in (None,'0x'): return r
    try: return dec_string(r)
    except Exception: return r
def blocknum(chain): return int(rpc(chain,'eth_blockNumber',[]),16)
def block(chain,n): return rpc(chain,'eth_getBlockByNumber',[hex(n) if isinstance(n,int) else n,False])
def btime(chain,n): return int(block(chain,n)['timestamp'],16)
def block_at(chain,ts):
    hi=blocknum(chain); lo=1
    th=btime(chain,hi)
    if ts>=th: return hi
    # estimate
    while lo<hi:
        mid=(lo+hi)//2
        if btime(chain,mid)<ts: lo=mid+1
        else: hi=mid
    return lo
def storage(chain,addr,slot,block='latest'):
    if isinstance(block,int): block=hex(block)
    if isinstance(slot,int): slot=hex(slot)
    return rpc(chain,'eth_getStorageAt',[addr,slot,block])
def code(chain,addr,block='latest'):
    return rpc(chain,'eth_getCode',[addr,block])
def getlogs(chain,params):
    return rpc(chain,'eth_getLogs',[params])
def curl_json(url, data=None, timeout=60):
    cmd=['curl','-s','-m',str(timeout)]
    if data is not None:
        cmd+=['-X','POST','-H','Content-Type: application/json','--data-binary','@-']
        r=subprocess.run(cmd+[url],input=json.dumps(data).encode(),capture_output=True)
    else:
        r=subprocess.run(cmd+[url],capture_output=True)
    try: return json.loads(r.stdout.decode())
    except Exception: return {'raw':r.stdout.decode()[:500]}
def gql(q, variables=None):
    return curl_json('https://blue-api.morpho.org/graphql',{'query':q,'variables':variables or {}})

BS={'eth':'https://eth.blockscout.com','ink':'https://explorer.inkonchain.com'}
def bslogs(chain,address,topic0=None,fromBlock=0,toBlock='latest',topic1=None,topic2=None,topic3=None):
    """Etherscan-compatible getLogs via Blockscout, paginated by advancing fromBlock."""
    out=[]; fb=fromBlock
    while True:
        url=f"{BS[chain]}/api?module=logs&action=getLogs&fromBlock={fb}&toBlock={toBlock}&address={address}"
        if topic0: url+=f"&topic0={topic0}"
        for i,t in [(1,topic1),(2,topic2),(3,topic3)]:
            if t: url+=f"&topic{i}={t}&topic0_{i}_opr=and"
        r=curl_json(url,timeout=120)
        res=r.get('result') if isinstance(r,dict) else None
        if not isinstance(res,list):
            print('bslogs err',str(r)[:300]); break
        out+=res
        if len(res)<1000: break
        last=int(res[-1]['blockNumber'],16)
        if last==fb: break
        fb=last
        # remove dups of block `last` later
    seen=set(); ded=[]
    for l in out:
        k=(l['transactionHash'],l.get('logIndex'))
        if k in seen: continue
        seen.add(k); ded.append(l)
    return ded

# ---------------- batch JSON-RPC (added for v3) ----------------
def batch_calls(chain, calls, chunk=40, tries=5):
    """calls: list of (to, data, block). Returns list of hex results (or None on revert)."""
    out = [None] * len(calls)
    for i in range(0, len(calls), chunk):
        part = calls[i:i + chunk]
        payload = [{'jsonrpc': '2.0', 'id': j, 'method': 'eth_call',
                    'params': [{'to': to, 'data': (d if d.startswith('0x') else '0x' + d)}, hex(b) if isinstance(b, int) else b]}
                   for j, (to, d, b) in enumerate(part)]
        done = False
        for t in range(tries):
            for url in RPCS[chain]:
                try:
                    res = _post(url, payload, timeout=90)
                except Exception:
                    res = None
                if isinstance(res, list) and len(res) == len(part) and all('result' in r or 'error' in r for r in res):
                    errs = [r for r in res if 'error' in r and 'revert' not in str(r['error']).lower() and 'execution' not in str(r['error']).lower()]
                    if errs:
                        continue
                    for r in res:
                        out[i + r['id']] = r.get('result')
                    done = True
                    break
            if done:
                break
            time.sleep(1 + t)
        if not done:
            # fall back to single calls
            for j, (to, d, b) in enumerate(part):
                r = call(chain, to, d, b)
                out[i + j] = r if isinstance(r, str) else None
    return out
