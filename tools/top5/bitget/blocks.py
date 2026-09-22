from rpc import *
import json, os
CACHE=os.path.join(os.path.dirname(__file__),'../raw/blockts_cache.json')
try: _c=json.load(open(CACHE))
except: _c={}
def bts(n):
    k=str(n)
    if k not in _c:
        b=call('morph','eth_getBlockByNumber',[hex(n),False]); _c[k]=int(b['timestamp'],16)
        json.dump(_c,open(CACHE,'w'))
    return _c[k]
def latest(): return int(call('morph','eth_blockNumber',[]),16)
def block_at(ts):
    lo,hi=1,latest()
    if bts(hi)<=ts: return hi
    while hi-lo>1:
        # interpolation-ish bisection
        mid=(lo+hi)//2
        if bts(mid)<=ts: lo=mid
        else: hi=mid
    return lo
