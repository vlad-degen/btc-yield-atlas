import sys
from addrinfo import rpc
def ts(ch,b): return int(rpc(ch,'eth_getBlockByNumber',[hex(b),False])['timestamp'],16)
def block_at(ch,t):
    hi=int(rpc(ch,'eth_blockNumber',[]),16); lo=max(1,hi-2_000_000)
    while ts(ch,lo)>t: lo=max(1,lo-2_000_000)
    while hi-lo>1:
        mid=(lo+hi)//2
        if ts(ch,mid)<=t: lo=mid
        else: hi=mid
    return lo
if __name__=='__main__':
    ch=int(sys.argv[1]); t=int(sys.argv[2]); b=block_at(ch,t); print(b,hex(b),ts(ch,b))
