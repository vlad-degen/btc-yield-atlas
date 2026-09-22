import lib
mb=lib.load('month_blocks.json')
SPARK='0xc13e21b648a5ee794902342038ff3adab66be987'; AAVE='0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
A={'PYUSD':'0x6c3ea9036406852006290770bedfcaba0e23a0e8','USDC':'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','USDT':'0xdac17f958d2ee523a2206206994597c13d831ec7','WBTC':'0x2260fac5e5542a773aa44fbcfedf7c193bc2c599','cbBTC':'0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf','LBTC':'0x8236a87084f8b84306f72007f36f2618a5634494'}
keys=[k for k in mb if k!='2024-11-14launch']
res={}
for k in keys:
    b=mb[k]['eth']; res[k]={}
    for pool,pn in [(SPARK,'spark'),(AAVE,'aave')]:
        for s,ad in A.items():
            idx=lib.u(lib.c(pool,'getReserveNormalizedVariableDebt(address)',lib.enc_addr(ad),block=b))
            li=lib.u(lib.c(pool,'getReserveNormalizedIncome(address)',lib.enc_addr(ad),block=b))
            rd=lib.c(pool,'getReserveData(address)',lib.enc_addr(ad),block=b)
            spot_b=lib.u(rd,4)/1e27 if rd and len(rd)>10 else None
            spot_s=lib.u(rd,2)/1e27 if rd and len(rd)>10 else None
            res[k][f'{pn}_{s}']={'debt_idx':idx,'inc_idx':li,'spot_borrow':spot_b,'spot_supply':spot_s}
    print(k,{kk:(round(v['spot_borrow']*100,2) if v['spot_borrow'] is not None else None) for kk,v in res[k].items()})
lib.save('aave_spark_idx.json',res)
