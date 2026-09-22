import json, urllib.request, time, sys
import json, urllib.request, sys
RC=[0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,0x000000000000808B,0x0000000080000001,0x8000000080008081,0x8000000000008009,0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,0x8000000000008002,0x8000000000000080,0x000000000000800A,0x800000008000000A,0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
ROT=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]
M=(1<<64)-1
def rol(x,n): return ((x<<n)|(x>>(64-n)))&M if n else x
def f(A):
    for rc in RC:
        C=[A[x][0]^A[x][1]^A[x][2]^A[x][3]^A[x][4] for x in range(5)]
        D=[C[(x-1)%5]^rol(C[(x+1)%5],1) for x in range(5)]
        A=[[A[x][y]^D[x] for y in range(5)] for x in range(5)]
        B=[[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                B[y][(2*x+3*y)%5]=rol(A[x][y],ROT[x][y])
        A=[[B[x][y]^((~B[(x+1)%5][y])&B[(x+2)%5][y]) for y in range(5)] for x in range(5)]
        A[0][0]^=rc
    return A
def keccak(data):
    rate=136
    data=bytearray(data)+b'\x01'
    while len(data)%rate: data+=b'\x00'
    data[-1]|=0x80
    A=[[0]*5 for _ in range(5)]
    for i in range(0,len(data),rate):
        blk=data[i:i+rate]
        for j in range(rate//8):
            x,y=j%5,j//5
            A[x][y]^=int.from_bytes(blk[8*j:8*j+8],'little')
        A=f(A)
    out=b''
    for j in range(4):
        x,y=j%5,j//5
        out+=A[x][y].to_bytes(8,'little')
    return out

RPCS={'eth':'https://ethereum-rpc.publicnode.com','base':'https://base-rpc.publicnode.com','bsc':'https://bsc-rpc.publicnode.com',
 'arb':'https://arbitrum-one-rpc.publicnode.com','avax':'https://avalanche-c-chain-rpc.publicnode.com/ext/bc/C/rpc','monad':'https://rpc.monad.xyz',
 'hyperevm':'https://rpc.hyperliquid.xyz/evm','bob':'https://rpc.gobob.xyz','ailayer':'https://mainnet-rpc.ailayer.xyz','bera':'https://rpc.berachain.com',
 'sonic':'https://rpc.soniclabs.com','bsquared':'https://rpc.bsquared.network','flare':'https://flare-api.flare.network/ext/C/rpc'}
def k256(b): return keccak(b)
def sel(sig): return k256(sig.encode()).hex()[:8]
def post(url,payload,retries=4):
    body=json.dumps(payload).encode()
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,data=body,headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req,timeout=60))
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    raise Exception('rpc failed %s'%last)
def rpc(chain,method,params):
    r=post(RPCS.get(chain,chain),{'jsonrpc':'2.0','id':1,'method':method,'params':params})
    if 'error' in r: raise Exception(str(r['error']))
    return r['result']
def enc_addr(a): return a.lower().replace('0x','').rjust(64,'0')
def enc_uint(n): return hex(n)[2:].rjust(64,'0')
def c(chain,to,sig,*args,block='latest'):
    data='0x'+sel(sig)+''.join(args)
    try: return rpc(chain,'eth_call',[{'to':to,'data':data},block])
    except Exception as e: return 'ERR '+str(e)[:200]
def u(h,i=0):
    if not h or h.startswith('ERR') or h=='0x': return None
    h=h[2:]; return int(h[64*i:64*(i+1)],16)
def words(h):
    h=h[2:]; return [h[i:i+64] for i in range(0,len(h),64)]
def s(h):
    if not h or h.startswith('ERR') or h=='0x': return h
    h=h[2:]
    try:
        off=int(h[:64],16)*2; ln=int(h[off:off+64],16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors='replace')
    except Exception: return bytes.fromhex(h).rstrip(b'\0').decode(errors='replace')
def a(h,i=0):
    if not h or h.startswith('ERR') or h=='0x': return None
    return '0x'+h[2:][64*i+24:64*(i+1)]
def erc20(chain,tok):
    return dict(name=s(c(chain,tok,'name()')),symbol=s(c(chain,tok,'symbol()')),dec=u(c(chain,tok,'decimals()')),supply=u(c(chain,tok,'totalSupply()')))
def bal(chain,tok,owner): return u(c(chain,tok,'balanceOf(address)',enc_addr(owner)))
