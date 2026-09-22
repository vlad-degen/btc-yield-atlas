"""River Smart/Prime Vault on-chain reader (mechA). Reads every SmartVault listed in the
DefiLlama satoshi-protocol adapter + any found via SmartVaultCreated logs, and dumps state to
raw/mechA/river_vaults_state.json.  Functions read (SmartVault impl 'SmartVault', River):
  underlyingAsset(), getTotalDepositedUnderlying(), totalSupply(), getMintedDebt(),
  getStakingAmount(), stakingFactor(), getVaultConfig(), rewardVault(), smartVaultManager(),
  getRewardTokenList(), isDepositEnabled(), isWhitelistMode(), paused(), lastUpdateTime();
  manager: debtToken(), stakingVault(), vaultBeacon(); stakingVault: balanceOf(vault), convertToAssets().
"""
import sys, json, time
sys.path.insert(0, '.')
from mechA_rpc import *
RPCS.update({'bob':'https://rpc.gobob.xyz','hemi':'https://rpc.hemi.network/rpc','eth':'https://ethereum-rpc.publicnode.com',
             'bsc':'https://bsc-dataseed.bnbchain.org','base':'https://base-rpc.publicnode.com'})
VAULTS = {
 'bsc': ['0x30349Af0cDcC2a93Ea4101953101BC0DEc43c53E','0x8f10C801B62Ae0b67B87B56a5f8ce05437ba6b7f'],
 'base':['0xCe07D2B5CC6Ff466BF497ceEa8eD168fB0Eb8F97','0xd72dCb68fF80aB8666f7A800BE438212581914c6'],
 'bob': ['0x3eeF93169c34F50919063eF56A118BFF26C8dfb8','0xd62E2F6b6616271001DCd0988AD2D73DEeE1b491','0xEdE84f536448cC822a9318548Aa8618183743c4f','0x4f4EbFAeEa78d7ebc13c4aAb481fd8E36D9DC1Be'],
 'hemi':['0xC7ab85e1afB80EC40eC3745D4Be6e7DE618735f2'],
 'eth': ['0xDd7eCb0dc1686020A8a23EE55126D7596a2eA03b','0x05EA42F72F2e627497423663Faf7b00eA7DdA2C1','0x11054D3584F94B542379Ff4Cf9e7897D50AE8317','0xaC586e941d5846B79cEF71c8aef3ecC50BE12DCb'],
}
BEACON_SLOT='0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'
def addr_list(h):
    if not h or h.startswith('ERR'): return h
    w=words(h); n=int(w[1],16); return ['0x'+w[2+i][24:] for i in range(n)]
def read_vault(ch,v):
    o={'chain':ch,'vault':v}
    o['name']=s(c(ch,v,'name()')); o['symbol']=s(c(ch,v,'symbol()'))
    o['vault_decimals']=u(c(ch,v,'decimals()'))
    ua=a(c(ch,v,'underlyingAsset()')); o['underlying']=ua
    e=erc20(ch,ua) if ua else {}
    o['underlying_symbol']=e.get('symbol'); o['underlying_dec']=e.get('dec')
    d=e.get('dec') or 18
    dep=u(c(ch,v,'getTotalDepositedUnderlying()')); o['totalDepositedUnderlying']=dep and dep/10**d
    o['underlying_balance_in_vault']=(bal(ch,ua,v) or 0)/10**d if ua else None
    ts=u(c(ch,v,'totalSupply()')); o['vault_totalSupply']=ts and ts/10**(o['vault_decimals'] or 18)
    md=u(c(ch,v,'getMintedDebt()')); o['mintedDebt_satUSD']=md and md/1e18
    st=u(c(ch,v,'getStakingAmount()')); o['stakingAmount_satUSD']=st and st/1e18
    o['stakingFactor_bps']=u(c(ch,v,'stakingFactor()'))
    cfg=c(ch,v,'getVaultConfig()')
    if cfg and not cfg.startswith('ERR'):
        w=[int(x,16) for x in words(cfg)]
        keys=['depositCap','depositCapPerUser','depositStartTime','depositEndTime','claimStartTime','claimEndTime','withdrawStartTime','withdrawEndTime','stakingFactor','isStakingEnabled','isWhitelistMode']
        o['vaultConfig']=dict(zip(keys,w))
    o['rewardVault']=a(c(ch,v,'rewardVault()')); mgr=a(c(ch,v,'smartVaultManager()')); o['smartVaultManager']=mgr
    rtl=addr_list(c(ch,v,'getRewardTokenList()')); o['rewardTokenList']=rtl
    o['rewardTokens']={}
    if isinstance(rtl,list):
        for t in rtl:
            rc=c(ch,v,'getRewardConfig(address)',enc_addr(t))
            o['rewardTokens'][t]={'symbol':s(c(ch,t,'symbol()')),'rewardConfig':[int(x,16) for x in words(rc)] if rc and not rc.startswith('ERR') else rc,
                                  'lastRewardPerToken':u(c(ch,v,'lastRewardPerToken(address)',enc_addr(t)))}
    for f in ['isDepositEnabled()','isWhitelistMode()','paused()','isClaimable()','lastUpdateTime()']:
        o[f]=u(c(ch,v,f))
    try:
        bslot=rpc(ch,'eth_getStorageAt',[v,BEACON_SLOT,'latest']); beacon='0x'+bslot[-40:]; o['beacon']=beacon
        o['implementation']=a(c(ch,beacon,'implementation()'))
    except Exception as ex: o['beacon']=str(ex)[:80]
    if mgr:
        dt=a(c(ch,mgr,'debtToken()')); sv=a(c(ch,mgr,'stakingVault()')); o['debtToken']=dt; o['stakingVault']=sv
        o['debtToken_symbol']=s(c(ch,dt,'symbol()')) if dt else None
        o['satUSD_balance_in_vault']=(bal(ch,dt,v) or 0)/1e18 if dt else None
        if sv:
            o['stakingVault_symbol']=s(c(ch,sv,'symbol()'))
            sh=bal(ch,sv,v) or 0; o['stakingVault_shares_held']=sh/1e18
            ca=u(c(ch,sv,'convertToAssets(uint256)',enc_uint(sh))) if sh else 0
            o['stakingVault_assets_of_vault_satUSD']=(ca or 0)/1e18
            o['stakingVault_totalAssets']=(u(c(ch,sv,'totalAssets()')) or 0)/1e18
            o['stakingVault_asset']=a(c(ch,sv,'asset()'))
            o['stakingVault_emissionListLength']=u(c(ch,sv,'emissionListLength()'))
            if dt: o['satUSD_totalSupply_chain']=(u(c(ch,dt,'totalSupply()')) or 0)/1e18
        try:
            pr=c(ch,mgr,'fetchPriceUnsafe(address)',enc_addr(ua)); o['mgr_fetchPriceUnsafe']=[int(x,16) for x in words(pr)] if pr and not pr.startswith('ERR') else pr
        except Exception: pass
    o['block']=int(rpc(ch,'eth_blockNumber',[]),16); o['read_at_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    return o
if __name__=='__main__':
    out=[]
    for ch,vs in VAULTS.items():
        for v in vs:
            try: o=read_vault(ch,v)
            except Exception as ex: o={'chain':ch,'vault':v,'error':str(ex)[:200]}
            out.append(o); print(json.dumps(o)[:1600]); print()
    json.dump(out,open('../raw/mechA/river_vaults_state.json','w'),indent=1)
