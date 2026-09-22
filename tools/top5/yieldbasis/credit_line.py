# Bisect the blocks where Curve DAO changed crvUSD debt_ceiling for the YB Factory (credit line)
from ybrpc import *
import datetime,json
CF='0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC'; F='0x370a449FeBb9411c95bf897021377fe0B7D100c0'
def dc(b): return (u(ec(CF,'debt_ceiling(address)',ea(F),block=b)) or 0)//10**18
def ts(b): return datetime.datetime.fromtimestamp(int(rpc('eth_getBlockByNumber',[hex(b),False])['timestamp'],16),datetime.UTC).isoformat()
def bis(lo,hi):
    v=dc(lo)
    while hi-lo>1:
        mid=(lo+hi)//2
        if dc(mid)==v: lo=mid
        else: hi=mid
    return hi
out=[]
for lo,hi in [(23371200,23434000),(23560000,23700000),(23990000,24000000)]:
    b=bis(lo,hi); out.append(dict(block=b,time=ts(b),debt_ceiling=dc(b)))
    print(out[-1])
json.dump(out,open('../raw/credit_line_changes.json','w'),indent=1)
