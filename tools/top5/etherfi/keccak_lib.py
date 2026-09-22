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
def sel(sig): return keccak(sig.encode())[:4].hex()
RPCS=['https://ethereum-rpc.publicnode.com','https://eth.llamarpc.com','https://rpc.ankr.com/eth']
def call(to,data,rpc=None,block='latest'):
    for r in ([rpc] if rpc else RPCS):
        try:
            req=urllib.request.Request(r,data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},block]}).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
            res=json.loads(urllib.request.urlopen(req,timeout=30).read())
            if 'result' in res: return res['result']
            else: last=res
        except Exception as e:
            last=str(e)
    return 'ERR '+str(last)
def rpc(method,params,r=None):
    for u in ([r] if r else RPCS):
        try:
            req=urllib.request.Request(u,data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
            res=json.loads(urllib.request.urlopen(req,timeout=30).read())
            if 'result' in res: return res['result']
            last=res
        except Exception as e: last=str(e)
    return 'ERR '+str(last)
def enc_uint(v): return hex(v)[2:].rjust(64,'0')
def enc_addr(a): return a.lower().replace('0x','').rjust(64,'0')
def c(to,sig,*args,block='latest'):
    data='0x'+sel(sig)+''.join(args)
    return call(to,data,block=block)
if __name__=='__main__':
    print(keccak(b'').hex())
    print(sel('totalSupply()'))
