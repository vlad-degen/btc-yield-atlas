import lib
mb=lib.load('month_blocks.json')
ITB=['0x7aaf9539b7359470def1920ca41b5aaa05c13726','0xcb67e9d2dc346f06c4f5274a0cb8acd22c0b2877','0x8950daa8c142e63eae0e8efef4c970c4e6602d56',
     '0xfbca329e2ee0c44d8f115a4b8f7ceda9e109f436','0x86761be7d4e6fe6f35b3335765a20b2b2e1849a3','0x832fe608c50ade63700d216636ca48b9e8a7d89e',
     '0x11fd9e49c41738b7500748f7b94b4dbb0e8c13d2','0x2afbd96fb854083574b738b36af34703c89b8656','0x075734ae0d7a4c89db7799f73de32f6c53feafd6']
LOANMGR={'0xcb67e9d2dc346f06c4f5274a0cb8acd22c0b2877':'itb1_eBTC_aave_RLUSD','0x86761be7d4e6fe6f35b3335765a20b2b2e1849a3':'itb2_eBTC_aave_RLUSD','0x2afbd96fb854083574b738b36af34703c89b8656':'itb3_LBTC_spark_PYUSD'}
TOK={'eBTC':('0x657e8c867d8b37dcc18fa4caead9c45eb088c642',8),'LBTC':('0x8236a87084f8b84306f72007f36f2618a5634494',8),
     'aEtheBTC':('0x5fefd7069a7d91d01f269dade14526ccf3487810',8),'spLBTC':('0xa9d4ecebd48c282a70cfd3c469d6c8f178a5738e',8),
     'variableDebtEthRLUSD':('0xbdfe7ad7976d5d7e0965ea83a81ca1bcff7e84a9',18),'variableDebtPYUSD':('0x3357d2db7763d6cd3a99f0763ebf87e0096d95f9',6),
     'RLUSD':('0x8292bb45bf1ee4d140127049757c2e0ff06317ed',18),'PYUSD':('0x6c3ea9036406852006290770bedfcaba0e23a0e8',6),
     'eRLUSD-1':('0xe1ce9af672f8854845e5474400b6ddc7ae458a10',18),'eRLUSD-7':('0xaf5372792a29dc6b296d6ffd4aa3386aff8f9bb2',18),'ePYUSD-6':('0xba98fc35c9dfd69178ad5dce9fa29c64554783b5',6)}
EUL={'eRLUSD-1':18,'eRLUSD-7':18,'ePYUSD-6':6}
AAVE='0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'; SPARK='0xc13e21b648a5ee794902342038ff3adab66be987'
out={}
for k,v in mb.items():
    if k=='2024-11-14launch': continue
    b=v['eth']
    if b<23040000: continue
    calls=[];idx=[]
    for a in ITB:
        for s,(t,d) in TOK.items():
            calls.append((t,'0x'+lib.sel('balanceOf(address)')+lib.enc_addr(a))); idx.append((a,s,d))
    res=lib.batch_calls(calls,block=b)
    agg={}
    per={}
    for (a,s,d),r in zip(idx,res):
        x=lib.u(r) if r and r!='0x' else 0
        if not x: continue
        amt=x/10**d
        if s in EUL:
            ca=lib.u(lib.c(TOK[s][0],'convertToAssets(uint256)',lib.enc_uint(x),block=b))
            amt=ca/10**EUL[s] if ca is not None else None
            s=s+'->assets'
        agg[s]=agg.get(s,0)+amt; per.setdefault(a,{})[s]=amt
    acct={}
    for lm,nm in LOANMGR.items():
        for pn,pool in [('aave',AAVE),('spark',SPARK)]:
            r=lib.c(pool,'getUserAccountData(address)',lib.enc_addr(lm),block=b)
            if r:
                vals=[lib.u(r,j) for j in range(6)]
                if vals[0] or vals[1]:
                    acct[nm]={'pool':pn,'coll_usd':vals[0]/1e8,'debt_usd':vals[1]/1e8,'liq_thr':vals[3]/1e4,'hf':vals[5]/1e18 if vals[5]<2**255 else None}
    out[k]={'agg':agg,'per':per,'acct':acct}
    print(k,{s:round(x,2) for s,x in agg.items()},{n:(round(a['coll_usd']/1e6,2),round(a['debt_usd']/1e6,2),a['hf'] and round(a['hf'],3)) for n,a in acct.items()})
lib.save('itb_positions.json',out)
