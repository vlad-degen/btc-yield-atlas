# month-end share prices of deployment vaults + borrow indices of every venue used
import lib
mb=lib.load('month_blocks.json')
V4626={'stcUSD':('0x88887be419578051ff9f4eb6c858a951921d8888',18,18),'senPYUSDmain':('0xb576765fb15505433af24fee2c0325895c559fb2',18,6),
       'senPYUSDPRIMEv2':('0xc21b08c16458202593d4d9b26b9984ee67b38bbd',18,6),'USUALUSDC+':('0xd63070114470f685b75b74d60eec7c1113d33a3d',18,6),
       'MC-USR':('0xd50da5f859811a91fd1876c9461fd39c23c747ad',18,18),'wstUSR':('0x1202f5c7b4b9e47a1a484e8b270be34dbbc75055',18,18),
       'eRLUSD-1':('0xe1ce9af672f8854845e5474400b6ddc7ae458a10',18,18),'eRLUSD-7':('0xaf5372792a29dc6b296d6ffd4aa3386aff8f9bb2',18,18),
       'ePYUSD-6':('0xba98fc35c9dfd69178ad5dce9fa29c64554783b5',6,6),'pWBTC':('0x2f1abb81ed86be95bcf8178ba62c8e72d6834775',18,8),
       'MCwBTC':('0x1c530d6de70c05a81bf1670157b9d928e9699089',18,8),'MCcbBTC':('0x98cf0b67da0f16e1f8f1a1d23ad8dc64c0c70e0b',18,8)}
MB='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
mk=lib.load('morpho_markets.json')
AAVE='0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
RLUSD='0x8292bb45bf1ee4d140127049757c2e0ff06317ed'
LP='0x5018be882dcce5e3f2f3b0913ae2096b9b3fb61f'
out={}
for k,v in mb.items():
    if k=='2024-11-14launch': continue
    b=v['eth']; row={}
    for s,(a,sd,ad) in V4626.items():
        r=lib.c(a,'convertToAssets(uint256)',lib.enc_uint(10**sd),block=b)
        row[s]=lib.u(r)/10**ad if r and r!='0x' else None
    for i,m in mk.items():
        mm=lib.c(MB,'market(bytes32)',i[2:],block=b)
        if mm and mm!='0x':
            tba,tbs=lib.u(mm,2),lib.u(mm,3); tsa,tss=lib.u(mm,0),lib.u(mm,1)
            row['morpho_borrow_idx:'+m['csym']+'/'+m['lsym']]=tba/tbs if tbs else None
    row['aave_RLUSD_debt_idx']=lib.u(lib.c(AAVE,'getReserveNormalizedVariableDebt(address)',lib.enc_addr(RLUSD),block=b))
    rd=lib.c(AAVE,'getReserveData(address)',lib.enc_addr(RLUSD),block=b)
    row['aave_RLUSD_spot']=lib.u(rd,4)/1e27 if rd and len(rd)>10 else None
    row['curveLP_vp']=lib.u(lib.c(LP,'get_virtual_price()',block=b))
    out[k]=row
    print(k,{kk:(round(x,6) if isinstance(x,float) else x) for kk,x in row.items() if x and not kk.startswith('morpho')})
# OP liquidRWA
lib.save('share_prices.json',out)
