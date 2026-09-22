# Snapshot liquidity checks behind liquidity_ladder.csv: Sentora/stcUSD redeem simulations from the vault, Cap burn capacity, queue terms, Spark oracle/config
import lib
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
S='0xb576765fb15505433af24fee2c0325895c559fb2'; ST='0x88887be419578051ff9f4eb6c858a951921d8888'; CU='0xcccc62962d17b8914c62d74ffb843d73b2a3cccc'
USDC='0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'; PY='0x6c3ea9036406852006290770bedfcaba0e23a0e8'
b=lib.load('month_blocks.json')['2026-09-20']['eth']; out={}
for nm,tok in [('sentora',S),('stcUSD',ST)]:
    sh=lib.bal(tok,V,block=b)
    data='0x'+lib.sel('redeem(uint256,address,address)')+lib.enc_uint(sh)+lib.enc_addr(V)+lib.enc_addr(V)
    try: out[nm+'_redeem_sim']=lib.u(lib.rpc('eth_call',[{'from':V,'to':tok,'data':data},hex(b)]))
    except Exception as e: out[nm+'_redeem_sim']='REVERT '+str(e)[:100]
out['sentora_idle_pyusd']=lib.bal(PY,S,block=b)/1e6; out['sentora_totalAssets']=lib.u(lib.c(S,'totalAssets()',block=b))/1e6
out['stc_lockDuration']=lib.u(lib.c(ST,'lockDuration()',block=b)); out['stc_lockedProfit']=lib.u(lib.c(ST,'lockedProfit()',block=b))/1e18
cusd=out['stcUSD_redeem_sim'] if isinstance(out['stcUSD_redeem_sim'],int) else 0
ba=lib.c(CU,'getBurnAmount(address,address,uint256)',lib.enc_addr(V),lib.enc_addr(USDC),lib.enc_uint(cusd),block=b)
out['cap_burn_usdc_out']=lib.u(ba,0)/1e6; out['cap_burn_fee']=lib.u(ba,1)/1e6
out['cap_available_usdc']=lib.u(lib.c(CU,'availableBalance(address)',lib.enc_addr(USDC),block=b))/1e6
out['cap_util_usdc']=lib.u(lib.c(CU,'utilization(address)',lib.enc_addr(USDC),block=b))/1e27
Q='0x77a2fd42f8769d8063f2e75061fc200014e41edf'
for s,a in {'WBTC':'0x2260fac5e5542a773aa44fbcfedf7c193bc2c599','eBTC':'0x657e8c867d8b37dcc18fa4caead9c45eb088c642','LBTC':'0x8236a87084f8b84306f72007f36f2618a5634494','cbBTC':'0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf'}.items():
    r=lib.c(Q,'withdrawAssets(address)',lib.enc_addr(a)); out['queue_'+s]=[lib.u(r,i) for i in range(6)]
r=lib.c('0xc13e21b648a5ee794902342038ff3adab66be987','getUserAccountData(address)',lib.enc_addr(V),block=b); out['spark_account']=[lib.u(r,i) for i in range(6)]
lib.save('liquidity_checks.json',out); print(out)
