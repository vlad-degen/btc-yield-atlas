"""Read River satUSD+ staking vaults (mechA): share price, emission list, claimable rewards of SmartVaults, and
the vaults' share of each pool. Output raw/mechA/river_staking.json"""
import sys,json,time; sys.path.insert(0,'.')
from mechA_rpc import *
RPCS.update({'bob':'https://rpc.gobob.xyz','bsc':'https://bsc-dataseed.bnbchain.org'})
SV={'bsc':('0x03d9c4e4bc5d3678a9076cac50db0251d8676872',['0x8f10C801B62Ae0b67B87B56a5f8ce05437ba6b7f']),
    'base':('0x7fe7de5d72633b981191eaee2ccaed95c77e79a9',['0xCe07D2B5CC6Ff466BF497ceEa8eD168fB0Eb8F97','0xd72dCb68fF80aB8666f7A800BE438212581914c6']),
    'bob':('0xacee663ae580cf15bc8f07a2b2ca23622938d9bf',['0xEdE84f536448cC822a9318548Aa8618183743c4f']),
    'eth':('0xcdace5073d9ca7379498ea8c728302e06d2f4f9b',[])}
out={}
for ch,(sv,vaults) in SV.items():
    o={'stakingVault':sv,'name':s(c(ch,sv,'name()')),'symbol':s(c(ch,sv,'symbol()'))}
    o['totalAssets']=(u(c(ch,sv,'totalAssets()')) or 0)/1e18; o['totalSupply']=(u(c(ch,sv,'totalSupply()')) or 0)/1e18
    o['pps']=(u(c(ch,sv,'convertToAssets(uint256)',enc_uint(10**18))) or 0)/1e18
    n=u(c(ch,sv,'emissionListLength()')) or 0; o['emissions']=[]
    for i in range(n):
        t=a(c(ch,sv,'emissionList(uint256)',enc_uint(i))); o['emissions'].append({'token':t,'symbol':s(c(ch,t,'symbol()')),
            'claimable_by_vaults':{v:(u(c(ch,sv,'claimableReward(address,address)',enc_addr(t),enc_addr(v))) or 0)/1e18 for v in vaults}})
    for f in ['rewardRate()','getRewardRate()','rewardConfig()','owner()','paused()','cooldownDuration()','unstakeDelay()']:
        r=c(ch,sv,f); o[f]=r[:130]
    o['vault_shares']={v:(bal(ch,sv,v) or 0)/1e18 for v in vaults}
    o['vault_share_pct']=sum(o['vault_shares'].values())/o['totalSupply'] if o['totalSupply'] else None
    o['block']=int(rpc(ch,'eth_blockNumber',[]),16); o['read_at_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    out[ch]=o; print(ch,json.dumps(o)[:1200])
json.dump(out,open('../raw/mechA/river_staking.json','w'),indent=1)
