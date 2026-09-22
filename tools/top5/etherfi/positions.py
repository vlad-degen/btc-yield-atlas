# Reconstruct vault positions at month-end blocks (Ethereum). Output raw/positions_raw.json
import lib,json,sys
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
VA=lib.enc_addr(V)
MB='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
AAVE='0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
SPARK='0xc13e21b648a5ee794902342038ff3adab66be987'
meta=lib.load('tokens_meta.json')
mk=lib.load('morpho_markets.json')
# token classes: kind, underlying valuation
BTC_1={'WBTC','cbBTC','aEthWBTC','aEthcbBTC','spWBTC','spcbBTC','BTCN','SY-EBTC','SY-LBTC','SY-cornLBTC','SY-corn-eBTC','SY-liquidBeraBTC','liquidBeraBTC','tacBTC'}
BTC_LBTC={'LBTC','aEthLBTC','spLBTC'}
BTC_EBTC={'eBTC','aEtheBTC'}
BTC_PT={'PT-LBTC-27MAR2025','PT-cornLBTC-27FEB2025','PT-corn-eBTC-27MAR2025','PT-liquidBeraBTC-10APR2025'}
BTC_4626={'MCwBTC','MCcbBTC','pWBTC'}
BTC_DEBT={'variableDebtEthWBTC'}
USD_1={'USDC','USDT','PYUSD','RLUSD','USR','cUSD','fxUSD','aEthUSDC','bUSD0','SY-USD0++'}
USD_4626={'USUALUSDC+','MC-USR','wstUSR','stcUSD','senPYUSDmain','senPYUSDPRIMEv2'}
USD_OTHER={'stUSR','USDCfxUSD'}
USD_DEBT={'variableDebtEthUSDC','variableDebtEthUSDT','variableDebtPYUSD','variableDebtUSDC'}
toks={}
for t,m in meta.items():
    s=m['symbol']
    if s in BTC_1|BTC_LBTC|BTC_EBTC|BTC_PT|BTC_4626|BTC_DEBT|USD_1|USD_4626|USD_OTHER|USD_DEBT|{'wstETH','WETH','ETHFI','MORPHO','CRV','CVX','FXN','PENDLE'}:
        toks[t]=m
mb=lib.load('month_blocks.json')
RP_LBTC='0x94916a66fc119a0ac7d612927f0d909cac15314c'
RP_EBTC='0x1b293dc39f94157fa0d1d36d7e0090c8b8b8c13f'
GAUGE='0xf1e141c804ba39b4a031fdf46e8c08dba7a0df60'; UVAULT='0x7ba41e927caed25bd8d25f5e6c82813bb1d51310'
LP='0x5018be882dcce5e3f2f3b0913ae2096b9b3fb61f'
out={}
keys=[k for k in mb if k!='2024-11-14launch']
if len(sys.argv)>1: keys=sys.argv[1:]
for k in keys:
    b=mb[k]['eth']
    tl=list(toks)
    calls=[(t,'0x'+lib.sel('balanceOf(address)')+VA) for t in tl]
    res=lib.batch_calls(calls,block=b)
    bals={}
    for t,r in zip(tl,res):
        v=lib.u(r) if r and r!='0x' else None
        if v: bals[toks[t]['symbol']]={'addr':t,'raw':v,'amt':v/10**toks[t]['decimals']}
    # ERC4626 conversions
    for s,d in bals.items():
        if s in BTC_4626|USD_4626:
            r=lib.c(d['addr'],'convertToAssets(uint256)',lib.enc_uint(d['raw']),block=b)
            asset=lib.a(lib.c(d['addr'],'asset()',block=b))
            adec=lib.u(lib.c(asset,'decimals()')) if asset else None
            d['assets']=lib.u(r)/10**adec if r and adec is not None else None
            d['asset']=asset
    if 'stUSR' in bals:
        pass
    # Morpho
    mpos={}
    for i,m in mk.items():
        p=lib.c(MB,'position(bytes32,address)',i[2:],VA,block=b)
        if not p: continue
        ss,bs,col=lib.u(p,0),lib.u(p,1),lib.u(p,2)
        if bs or col or ss:
            mm=lib.c(MB,'market(bytes32)',i[2:],block=b)
            tba,tbs=lib.u(mm,2),lib.u(mm,3)
            debt=bs*tba/tbs if tbs else 0
            mpos[m['csym']+'/'+m['lsym']]={'collateral':col/10**m['cdec'],'debt':debt/10**m['ldec'],'lltv':m['lltv']}
    # Aave / Spark account data
    acct={}
    for nm,pool in [('aave',AAVE),('spark',SPARK)]:
        r=lib.c(pool,'getUserAccountData(address)',VA,block=b)
        if r:
            vals=[lib.u(r,j) for j in range(6)]
            if vals[0] or vals[1]:
                acct[nm]={'coll_usd':vals[0]/1e8,'debt_usd':vals[1]/1e8,'liq_thr':vals[3]/1e4,'ltv_max':vals[4]/1e4,'hf':vals[5]/1e18 if vals[5]<2**255 else None}
    # rates
    rl=lib.u(lib.c(RP_LBTC,'getRate()',block=b)); re=lib.u(lib.c(RP_EBTC,'getRate()',block=b))
    # convex staked LP
    g=lib.u(lib.c(GAUGE,'balanceOf(address)',lib.enc_addr(UVAULT),block=b))
    lpvp=None
    if g:
        lpvp=lib.u(lib.c(LP,'get_virtual_price()',block=b))
    out[k]={'block':b,'bals':bals,'morpho':mpos,'acct':acct,'rate_lbtc':rl and rl/1e8,'rate_ebtc':re and re/1e8,'convex_lp':g and g/1e18,'lp_vp':lpvp and lpvp/1e18}
    print(k,b,{s:round(d['amt'],4) for s,d in bals.items()},mpos,acct,file=sys.stderr)
    lib.save('positions_raw.json' if len(sys.argv)==1 else 'positions_raw_partial.json',out)
