"""Read-only nested claims, request simulations and source binding captures."""
import json,sys
from backing_exit_capture import *

def nested():
    rows=[]; liquity='0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c'
    extra=['0x6131b5fae19ea4f9d964eac0408e4408b66337b5','0xefc6516323fbd28e80b85a497b65a86243a54b3e','0x7a01471fa544d9c6531b631e6a96a79a9ad05e9']
    for tok in extra:
        for sig,args in [('balanceOf(address)',enc_addr(liquity)),('decimals()',''),('symbol()',''),('asset()',''),('convertToAssets(uint256)',enc_uint(10**18))]:rows.append(call('liquity_'+tok+'_'+sig,tok,sig,args))
        fetch('liquity_token_'+tok,'https://eth.blockscout.com/api/v2/smart-contracts/'+tok)
    for caller in ['0x1676d23711186076fa74aa53511dda750a1f0d9a','0x8ff4d4a12a4df051abfbd1ff94f6b17d42cc3856']:
        rows.append(call('liquity_refresh_'+caller,liquity,'updateMarketsBalances(uint256[])',enc_uint(32)+enc_uint(4)+''.join(enc_uint(x)for x in [12,16,29,53]),caller))
    for name,tok in [('rock_pool','0x1ea5870f7c037930ce1d5d8d9317c670e89e13e3'),('rock_gauge','0x62a66eb9abf7a788f48d0ce7c0c065df9e09da19'),('rock_yield_gauge','0xd829456fd63ada7de0657714a3a7a26de403e3d8')]:
        for sig in ['asset()','getPoolId()','getVault()','totalSupply()','getActualSupply()','staking_token()','lp_token()','underlying()','getPoolTokens()']:
            rows.append(call(name+'_'+sig,tok,sig))
        fetch(name+'_verified','https://eth.blockscout.com/api/v2/smart-contracts/'+tok)
    rows.append(call('rock_spark_account','0xc13e21b648a5ee794902342038ff3adab66be987','getUserAccountData(address)',enc_addr('0x9ca1d6e730eb9fbfd45c9ff5f0ac4e3d172d8f4d')))
    rows.extend([call('concrete_vault_weETH','0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','balanceOf(address)',enc_addr('0xb9dc54c8261745cb97070cefbe3d3d815aee8f20')),call('concrete_plus_wstETH','0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','balanceOf(address)',enc_addr('0xd57588c73715b65e0ead36ae06c15644169501b7'))])
    rpc('nested_backing_T',rows)

def requests():
    rows=[]
    rock='0x936facdf10c8c36294e7b9d28345255539d81bc7';holder='0xeadb3840596cabf312f2bc88a4bb0b93a4e1ff5f'
    raw=json.loads((RAW/'withdraw_simulations_T.json').read_text());by={r['label']:r for r in raw['records']}
    supply=int(by['rocksolid_totalSupply()']['response']['result'],16)
    for pct in [1,10,30]:rows.append(call('rock_request_'+str(pct)+'pct',rock,'requestRedeem(uint256,address,address)',enc_uint(supply*pct//100)+enc_addr(holder)+enc_addr(holder),holder))
    for name,address,who in [('concrete','0xb9dc54c8261745cb97070cefbe3d3d815aee8f20','0x5bab73f561a5365c9e4bbc7c52fe0fa384fcf324'),('royco','0x41ce72e04d349eb957bdc373baa9c69207032c56','0xfef0bb8df6210e441f03de23edafb0150129e176')]:
        rows.append(call(name+'_claim_epoch1',address,'claimWithdrawal(uint256[])',enc_uint(32)+enc_uint(1)+enc_uint(1),who))
        rows.append(call(name+'_epoch1_state',address,'getEpochState(uint256)',enc_uint(1)))
    liquid='0xf0bb20865277abd641a307ece5ee04e79073416c';queue='0x0d2df071207e18ca8638b4f04e98c53155ec2ce0';weeth='0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee'
    holderdata=json.loads((ROOT/'raw/eth/2026-10-04/strict-products/liquid_holder_distribution_T.json').read_text())
    entries=holderdata.get('holders') or holderdata.get('topHolders') or []
    # Derive holders from canonical distribution schema rather than inventing.
    if not entries:
        entries=holderdata.get('balances',[])
    if isinstance(entries,dict):entries=[{'address':k,'rawBalance':v}for k,v in entries.items()]
    print('holder entry keys',list(entries[0]) if entries else list(holderdata))
    for x in entries[:25]:
        who=x.get('address') or x.get('holder')
        if who:rows.append(call('liquid_allowance_'+who,liquid,'allowance(address,address)',enc_addr(who)+enc_addr(queue)))
    for sig,args in [('isPaused()',''),('withdrawAssets(address)',enc_addr(weeth)),('nonce()','')]:rows.append(call('liquid_queue_'+sig,queue,sig,args))
    # Immediate direct vault exits need contract authorization; a token holder
    # alone is not thereby an authorized BoringVault withdraw caller.
    who='0xc51828dd0e827e6d7e0f4176eef87160de7efb4b'
    rows.append(call('liquid_direct_exit_holder',liquid,'exit(address,address,uint256,address,uint256)',enc_addr(who)+enc_addr(weeth)+enc_uint(10**18)+enc_addr(who)+enc_uint(10**18),who))
    rpc('request_and_claim_simulations_T',rows)

def monad():
    # The remote block boundary was previously independently checked. All new
    # Monad reads retain its exact archived block, never a latest-state balance.
    vault='0xa024063b630d554078bbf985718b22f3c6870ee0';tag=hex(110031481)
    rows=[]
    for sig in ['totalSupply()','hook()','authority()','owner()']:
        rows.append(call('monad_vault_'+sig,vault,sig,tag=tag))
    rows.append(state('monad_native_MON','eth_getBalance',vault,tag))
    acc='0x5ce04a3d8d5297a24bf752d0172064941d8d853b'
    for sig in ['base()','getRate()','accountantState()']:
        rows.append(call('monad_accountant_'+sig,acc,sig,tag=tag))
    out=rpc('monad_remote_backing_identity_T',rows,'https://rpc.monad.xyz')
    for r in out['records']:
        if r['label']=='monad_accountant_base()' and r['response'].get('result'):
            base='0x'+r['response']['result'][-40:]
            rpc('monad_base_balance_T',[call('monad_base_balance',base,'balanceOf(address)',enc_addr(vault),tag=tag),call('monad_base_symbol',base,'symbol()',tag=tag)],'https://rpc.monad.xyz')
    for key,url in [('monadscan_vault','https://monadscan.com/address/'+vault),('etherfi_monad_docs','https://etherfi.gitbook.io/etherfi/products/liquid/live-vaults/liquid-monad-eth-vault.md')]:fetch(key,url)

def closure():
    rows=[];rock='0x936facdf10c8c36294e7b9d28345255539d81bc7'
    slot='0x'+(int.from_bytes(keccak(b'eip1967.proxy.implementation'),'big')-1).to_bytes(32,'big').hex()
    rows.append(state('rock_implementation_slot_T','eth_getStorageAt',rock,TAG,slot))
    rows.append(state('rock_implementation_code_T','eth_getCode','0xe50554ec802375c9c3f9c087a8a7bb8c26d3dedf'))
    rows.extend([call('rock_paused_T',rock,'paused()'),call('rock_max_deposit_T',rock,'maxDeposit(address)',enc_addr('0xeadb3840596cabf312f2bc88a4bb0b93a4e1ff5f'))])
    tx='0xb3ed2719618ec664e52d904c4f65eb9dcbbddd7ff1ae5c5599148bbadf23b70a'
    rows.extend([{'label':'rock_closing_tx','method':'eth_getTransactionByHash','params':[tx]},{'label':'rock_closing_header','method':'eth_getBlockByNumber','params':['0x18df3bd',False]}])
    topic='0x'+keccak(b'StateUpdated(uint8)').hex()
    rows.append({'label':'rock_state_events_after_T','method':'eth_getLogs','params':[{'address':rock,'fromBlock':hex(BLOCK+1),'toBlock':'latest','topics':[topic]}]})
    # Exact bytes32 substrate addresses preserve leading zeroes.
    liq='0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c';tok='0x07a01471fa544d9c6531b631e6a96a79a9ad05e90'
    md=json.loads((ROOT/'raw/eth/2026-10-04/strict-products/market_controls_rpc.json').read_text());raw=md['records'][0]['response']['result'][2:]
    substrate=[('0x'+raw[i:i+64][-40:])for i in range(128,len(raw),64)]
    for tok in substrate:
        if tok in ['0x6440f144b7e50d6a8439336510312d2f54beb01d','0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','0xae78736cd615f374d3085123a210448e74fc6393','0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2','0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0']:continue
        for sig,args in [('balanceOf(address)',enc_addr(liq)),('decimals()',''),('symbol()','')]:rows.append(call('liquity_substrate_'+tok+'_'+sig,tok,sig,args))
    rpc('final_controls_and_substrates_T',rows,LOG_RPC)
    vault='0xa024063b630d554078bbf985718b22f3c6870ee0';tag=hex(110031481)
    toks=['0x10aeaf63194db8d453d4d85a06e5efe1dd0b5417','0x754704bc059f8c67012fed69bc8a327a5aafb603','0xbeef04b01e0275d4ac2e2986256bb14e3ff6ef42','0x3bd359c1119da7da1d913d1c4d2b7c461115433a']
    rows=[]
    for tok in toks:
        for sig,args in [('balanceOf(address)',enc_addr(vault)),('decimals()',''),('symbol()',''),('asset()',''),('convertToAssets(uint256)',enc_uint(10**18))]:rows.append(call('monad_'+tok+'_'+sig,tok,sig,args,tag=tag))
    rpc('monad_token_claims_T',rows,'https://rpc.monad.xyz')

def binding():
    rock='0x936facdf10c8c36294e7b9d28345255539d81bc7'
    slot='0x'+(int.from_bytes(keccak(b'eip1967.proxy.implementation'),'big')-1).to_bytes(32,'big').hex()
    rows=[state('rock_implementation_slot_T','eth_getStorageAt',rock,TAG,slot),state('rock_implementation_code_T','eth_getCode','0xe50554ec802375c9c3f9c087a8a7bb8c26d3dedf'),{'label':'rock_closing_tx','method':'eth_getTransactionByHash','params':['0xb3ed2719618ec664e52d904c4f65eb9dcbbddd7ff1ae5c5599148bbadf23b70a']},{'label':'rock_closing_header','method':'eth_getBlockByNumber','params':['0x18df3bd',False]},{'label':'rock_state_events_after_T','method':'eth_getLogs','params':[{'address':rock,'fromBlock':hex(BLOCK+1),'toBlock':'latest','topics':[topic] if (topic:='0x'+keccak(b'StateUpdated(uint8)').hex()) else []}]}]
    rpc('rocksolid_implementation_binding_T',rows,LOG_RPC)

def targeted():
    rock='0x9ca1d6e730eb9fbfd45c9ff5f0ac4e3d172d8f4d';liq='0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c'
    rows=[call('rock_spark_account','0xc13e21b648a5ee794902342038ff3adab66be987','getUserAccountData(address)',enc_addr(rock))]
    pool='0x1ea5870f7c037930ce1d5d8d9317c670e89e13e3'
    for sig in ['getTokens()','getCurrentLiveBalances()','getRate()','totalSupply()','getTokenInfo()']:
        rows.append(call('rock_pool_'+sig,pool,sig))
    gauge='0xd829456fd63ada7de0657714a3a7a26de403e3d8'
    for sig,args in [('convertToAssets(uint256)',enc_uint(95442884323733179066)),('maxWithdraw(address)',enc_addr(rock))]:rows.append(call('rock_yield_gauge_'+sig,gauge,sig,args))
    yp='0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea'
    for sig in ['asset()','getRate()','getTokens()','getCurrentLiveBalances()','totalSupply()','decimals()']:
        rows.append(call('rock_yield_pool_'+sig,yp,sig))
    md=json.loads((ROOT/'raw/eth/2026-10-04/strict-products/market_controls_rpc.json').read_text());raw=md['records'][0]['response']['result'][2:]
    substrate=[('0x'+raw[i:i+64][-40:])for i in range(128,len(raw),64)]
    for tok in substrate:
        if tok in ['0x6440f144b7e50d6a8439336510312d2f54beb01d','0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','0xae78736cd615f374d3085123a210448e74fc6393','0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2','0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0']:continue
        for sig,args in [('balanceOf(address)',enc_addr(liq)),('decimals()',''),('symbol()','')]:rows.append(call('liquity_substrate_'+tok+'_'+sig,tok,sig,args))
    for caller in ['0x1676d23711186076fa74aa53511dda750a1f0d9a','0x32787cd59244581a358a068d52e460eb00df6543']:
        rows.append(call('liquity_refresh_'+caller,liq,'updateMarketsBalances(uint256[])',enc_uint(32)+enc_uint(4)+''.join(enc_uint(x)for x in [12,16,29,53]),caller))
    for sig in ['getRewardsClaimManagerAddress()','getTotalAssetsInAllMarkets()','getBalanceFuses()']:
        rows.append(call('liquity_'+sig,liq,sig))
    # Keep this bounded read paced; these are only explicitly held/authorized
    # claims from the saved inventory, not a new market or wallet crawl.
    out=[]
    for i in range(0,len(rows),5):
        out.extend(rpc('known_nested_claims_T_'+str(i//5),rows[i:i+5],LOG_RPC)['records']);time.sleep(.8)
    (RAW/'known_nested_claims_T.json').write_text(json.dumps({'financialTimestamp':T,'records':out},indent=2))
    mono='0xa024063b630d554078bbf985718b22f3c6870ee0';tag=hex(110031481);steak='0xbeef04b01e0275d4ac2e2986256bb14e3ff6ef42'
    rpc('monad_steak_exit_T',[call('steak_maxWithdraw',steak,'maxWithdraw(address)',enc_addr(mono),tag=tag),call('steak_claim',steak,'convertToAssets(uint256)',enc_uint(7427621860255962622306),tag=tag),call('steak_withdraw_1WETH',steak,'withdraw(uint256,address,address)',enc_uint(10**18)+enc_addr(mono)+enc_addr(mono),mono,tag=tag)],'https://rpc.monad.xyz')

def pools():
    pool='0xefc6516323fbd28e80b85a497b65a86243a54b3e';yp='0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea'
    rows=[call('curve_'+sig,pool,sig,args)for sig,args in [('get_balances()',''),('totalSupply()',''),('coins(uint256)',enc_uint(0)),('coins(uint256)',enc_uint(1))]]
    rows[2]['label']='curve_coin_0';rows[3]['label']='curve_coin_1'
    for sig,args in [('lp_token()',''),('balanceOf(address)',enc_addr('0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c'))]:rows.append(call('curve_gauge_'+sig,'0x07a01471fa544d9c6531b631e6a96a79a9ad05e9',sig,args))
    for sig in ['getPoolId()','getVault()','totalSupply()','getRate()','getTokens()','getCurrentLiveBalances()']:
        rows.append(call('rock_yield_pool_'+sig,yp,sig))
    rows.extend([call('rock_pool_wrappedWETH_asset','0x0bfc9d54fc184518a81162f8fb99c2eaca081202','asset()'),call('rock_pool_wrappedWETH_convert','0x0bfc9d54fc184518a81162f8fb99c2eaca081202','convertToAssets(uint256)',enc_uint(10**18)),call('rock_gauge_lp_balance','0x1ea5870f7c037930ce1d5d8d9317c670e89e13e3','balanceOf(address)',enc_addr('0x62a66eb9abf7a788f48d0ce7c0c065df9e09da19'))])
    out=[]
    for i in range(0,len(rows),4):
        out.extend(rpc('explicit_pool_claims_T_'+str(i//4),rows[i:i+4],RPC)['records']);time.sleep(1.5)
    (RAW/'explicit_pool_claims_T.json').write_text(json.dumps({'financialTimestamp':T,'records':out},indent=2))
    fetch('rock_yield_pool_verified','https://eth.blockscout.com/api/v2/smart-contracts/'+yp)

def proof():
    morpho='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb';mid='f5c5df23559b0fb56560a7578ea17d81e245153ba64b8132df026c9358864d27';cal='0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0';yp='0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea'
    rows=[call('royco_morpho_params',morpho,'idToMarketParams(bytes32)',mid),call('royco_morpho_market',morpho,'market(bytes32)',mid),call('royco_morpho_position',morpho,'position(bytes32,address)',mid+enc_addr(cal))]
    for sig,args in [('ASSET_TOKEN()',''),('STABLECOIN()',''),('pricePerShare()',''),('updated_balances()',''),('preview_withdraw(uint256)',enc_uint(94021507076728137104))]:rows.append(call('rock_yb_'+sig,yp,sig,args))
    for tok in ['0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2','0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','0x35fa164735182de50811e8e2e824cfb9b6118ac2']:
        rows.append(call('monad_Ethereum_local_'+tok,tok,'balanceOf(address)',enc_addr('0xa024063b630d554078bbf985718b22f3c6870ee0')))
    rows.append(call('rock_vault_rETH','0xae78736cd615f374d3085123a210448e74fc6393','balanceOf(address)',enc_addr('0x936facdf10c8c36294e7b9d28345255539d81bc7')))
    rows.append(call('eETH_decimals','0x35fa164735182de50811e8e2e824cfb9b6118ac2','decimals()'))
    out=[]
    for i in range(0,len(rows),4):
        out.extend(rpc('remaining_known_claims_T_'+str(i//4),rows[i:i+4],RPC)['records']);time.sleep(1.5)
    data={'financialTimestamp':T,'records':out};(RAW/'remaining_known_claims_T.json').write_text(json.dumps(data,indent=2))
    by={r['label']:r['response'].get('result')for r in out}
    params=by.get('royco_morpho_params');market=by.get('royco_morpho_market')
    if params and market:
        words=[params[i:i+64]for i in range(2,len(params),64)];oracle='0x'+words[2][-40:];irm='0x'+words[3][-40:]
        rpc('royco_morpho_accrual_T',[call('oracle_price',oracle,'price()'),call('borrow_rate',irm,'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',params[2:]+market[2:])],RPC)
        fetch('royco_irm_verified','https://eth.blockscout.com/api/v2/smart-contracts/'+irm)

if __name__=='__main__':{'nested':nested,'requests':requests,'monad':monad,'closure':closure,'binding':binding,'targeted':targeted,'pools':pools,'proof':proof}[sys.argv[1]]()
