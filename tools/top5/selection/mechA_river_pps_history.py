"""Historical satUSD+ price-per-share and vault state on Base/BOB/BSC via archive eth_call where available (mechA).
Output raw/mechA/river_pps_history.json"""
import sys,json,time; sys.path.insert(0,'.')
from mechA_rpc import *
RPCS.update({'bob':'https://rpc.gobob.xyz'})
ARCH={'base':['https://base-rpc.publicnode.com','https://mainnet.base.org','https://base.drpc.org'],'bob':['https://rpc.gobob.xyz'],'bsc':['https://bsc-dataseed.bnbchain.org']}
SV={'base':('0x7fe7de5d72633b981191eaee2ccaed95c77e79a9','0xCe07D2B5CC6Ff466BF497ceEa8eD168fB0Eb8F97',2.0),'bob':('0xacee663ae580cf15bc8f07a2b2ca23622938d9bf','0xEdE84f536448cC822a9318548Aa8618183743c4f',2.0),'bsc':('0x03d9c4e4bc5d3678a9076cac50db0251d8676872','0x8f10C801B62Ae0b67B87B56a5f8ce05437ba6b7f',0.45)}
def call_at(ch,to,data,blk):
    for r in ARCH[ch]:
        try:
            res=post(r,{'jsonrpc':'2.0','id':1,'method':'eth_call','params':[{'to':to,'data':data},hex(blk)]},retries=1)
            if 'result' in res: return res['result']
        except Exception: pass
    return None
out={}
for ch,(sv,vault,bt) in SV.items():
    head=int(rpc(ch,'eth_blockNumber',[]),16); rows=[]
    for days in [0,30,90,180,270,365]:
        blk=head-int(days*86400/bt)
        pps=call_at(ch,sv,'0x'+sel('convertToAssets(uint256)')+enc_uint(10**18),blk)
        md=call_at(ch,vault,'0x'+sel('getMintedDebt()'),blk); st=call_at(ch,vault,'0x'+sel('getStakingAmount()'),blk)
        ta=call_at(ch,sv,'0x'+sel('totalAssets()'),blk)
        row={'days_ago':days,'block':blk,'pps':(int(pps,16)/1e18 if pps and pps!='0x' else None),'vault_mintedDebt':(int(md,16)/1e18 if md and md!='0x' else None),
             'vault_staking':(int(st,16)/1e18 if st and st!='0x' else None),'pool_totalAssets':(int(ta,16)/1e18 if ta and ta!='0x' else None)}
        rows.append(row); print(ch,row)
    out[ch]=rows
json.dump(out,open('../raw/mechA/river_pps_history.json','w'),indent=1)
