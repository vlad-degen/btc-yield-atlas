"""Additional read-only archive captures for backing and actual exit history."""
import json,sys,time,pathlib
from backing_exit_capture import ROOT,RAW,T,BLOCK,TAG,RPC,LOG_RPC,fetch,rpc,call,state,sel,enc_addr,enc_uint,keccak

def load(prefix):
    rows=[json.loads(x) for x in (RAW/'requests.jsonl').read_text().splitlines()]
    row=next(x for x in reversed(rows) if x['key']==prefix and x.get('path'))
    return json.loads((ROOT/row['path']).read_text())

def follow_authority():
    risk='0x82eece4a736db0767370d2dffde9bdf6e38aaeb8'; caliber='0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0'
    d=json.loads((RAW/'royco_role_grants_T.json').read_text())
    pairs=sorted({(int(x['topics'][1],16),'0x'+x['topics'][2][-40:]) for r in d['records'] for x in r['response'].get('result',[])})
    rows=[call('risk_access_'+str(role)+'_'+acc,risk,'getAccess(uint64,address)',enc_uint(role)+enc_addr(acc)) for role,acc in pairs]
    manager='0x84d37a25e46029ce161111420e07ceb78880119e'
    rows.extend([state('duration_controller_code','eth_getCode',manager),call('duration_controller_owners',manager,'getOwners()'),call('duration_controller_threshold',manager,'getThreshold()'),call('duration_canCall',risk,'canCall(address,address,bytes4)',enc_addr(manager)+enc_addr(caliber)+sel('setTimelockDuration(uint256)').ljust(64,'0'))])
    # AccessManager.execute(address,bytes) ABI encoding. This call is simulated
    # from an actual mapped holder; it requires the controller's own permission.
    payload=sel('setTimelockDuration(uint256)')+enc_uint(0)
    args=enc_addr(caliber)+enc_uint(64)+enc_uint(len(payload)//2)+payload.ljust(128,'0')
    rows.append(call('duration_controller_execute_without_schedule',risk,'execute(address,bytes)',args,manager))
    for kind,address in [('machine','0x6a759cae19aa25b41237089eb0bbbc4473bfb996'),('caliber','0xe5504cf018e67be842b0e6f738d9a32230c05ec3')]:rows.append(state(kind+'_implementation_code_T','eth_getCode',address))
    rpc('royco_authority_active_T',rows)
    fetch('duration_controller_verified','https://eth.blockscout.com/api/v2/smart-contracts/'+manager)

def balances():
    rows=[]
    for name,wallet,key in [('concrete','0x7ee29373f075ee1d83b1b93b4fe94ae242df5178','concrete_wallet_tokens'),('rocksolid','0x9ca1d6e730eb9fbfd45c9ff5f0ac4e3d172d8f4d','rocksolid_wallet_tokens')]:
        data=load(key); tokens=data if isinstance(data,list) else data.get('items',[])
        for x in tokens:
            tok=x['token'];symbol=tok.get('symbol') or ''
            if tok.get('type')!='ERC-20' or not(tok.get('exchange_rate') or any(s in symbol.lower() for s in ['eth','usd','bold'])):continue
            rows.append({**call(name+'_'+symbol,tok['address_hash'],'balanceOf(address)',enc_addr(wallet)),'token':tok,'wallet':wallet})
        rows.append(state(name+'_native_ETH','eth_getBalance',wallet))
    for name,address in [('s0xUSD','0x0000b10c4656aea2ccd28a94a223ef090356ca2a'),('ctDefiUSDT','0x0e609b710da5e0aa476224b6c0e5445ccc21251e'),('ctwstETH','0xd57588c73715b65e0ead36ae06c15644169501b7'),('royco_srUSDC','0xcd9f5907f92818bc06c9ad70217f089e190d2a32')]:
        for sig in ['asset()','totalAssets()','totalSupply()','decimals()','convertToAssets(uint256)']:
            rows.append(call(name+'_'+sig,address,sig,enc_uint(10**18) if '(' in sig and 'uint256' in sig else ''))
        if name=='royco_srUSDC':
            cal='0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0'
            for sig in ['balanceOf(address)','maxWithdraw(address)','maxRedeem(address)']:rows.append(call(name+'_'+sig,address,sig,enc_addr(cal)))
    rpc('backing_token_balances_T',rows)
    for name,address in [('s0xUSD','0x0000b10c4656aea2ccd28a94a223ef090356ca2a'),('ctDefiUSDT','0x0e609b710da5e0aa476224b6c0e5445ccc21251e'),('royco_srUSDC','0xcd9f5907f92818bc06c9ad70217f089e190d2a32')]:fetch(name+'_verified','https://eth.blockscout.com/api/v2/smart-contracts/'+address)

def exit_logs():
    # Capture every relevant vault event from each vault's creation block to T.
    # A null topic list is deliberate for small contracts. Liquid's larger queue
    # uses only request / solve / cancel events, excluding unrelated events.
    targets=[('concrete','0xb9dc54c8261745cb97070cefbe3d3d815aee8f20',int('16e2695',16),None),('royco','0x41ce72e04d349eb957bdc373baa9c69207032c56',int('17723c0',16),None),('rocksolid','0x936facdf10c8c36294e7b9d28345255539d81bc7',23000000,None),('liquity','0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c',24000000,['0x'+keccak(b'Withdraw(address,address,address,uint256,uint256)').hex()]),('royco_caliber','0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0',25000000,None)]
    topic_sigs=['OnChainWithdrawRequested(bytes32,address,address,uint96,uint128,uint128,uint40,uint24,uint24)','OnChainWithdrawSolved(bytes32,address,uint256)','OnChainWithdrawCancelled(bytes32,address,uint256)']
    targets.append(('liquid_queue','0x0d2df071207e18ca8638b4f04e98c53155ec2ce0',20000000,[['0x'+keccak(x.encode()).hex() for x in topic_sigs]]))
    for name,address,start,topics in targets:
        records=[]
        for b in range(start,BLOCK+1,500000):
            query={'address':address,'fromBlock':hex(b),'toBlock':hex(min(b+499999,BLOCK))}
            if topics:query['topics']=topics
            out=rpc(name+'_exitlogs_'+str(b),[{'label':name+'_logs','method':'eth_getLogs','params':[query]}],LOG_RPC)
            records.extend(out['records']);time.sleep(.6)
        (RAW/(name+'_exitlogs_T.json')).write_text(json.dumps({'financialTimestamp':T,'fromBlock':start,'toBlock':BLOCK,'records':records},indent=2))

def receipts():
    # All recorded cash-claim transactions, not a convenience sample.
    signatures={'liquid_queue':'OnChainWithdrawSolved(bytes32,address,uint256)','rocksolid':'Withdraw(address,address,address,uint256,uint256)','liquity':'Withdraw(address,address,address,uint256,uint256)'}
    for name,sig in signatures.items():
        topic='0x'+keccak(sig.encode()).hex()
        logs=[x for r in json.loads((RAW/(name+'_exitlogs_T.json')).read_text())['records']for x in r['response'].get('result',[]) if x['topics'][0]==topic]
        txs=sorted({x['transactionHash'] for x in logs})
        rows=[{'label':tx,'method':'eth_getTransactionReceipt','params':[tx]}for tx in txs]
        rpc(name+'_payout_receipts',rows)
    royco_logs=[x for r in json.loads((RAW/'royco_caliber_exitlogs_T.json').read_text())['records'] for x in r['response'].get('result',[])]
    txs=sorted({x['transactionHash']for x in royco_logs})
    rpc('royco_accounting_transactions',[{'label':tx,'method':'eth_getTransactionByHash','params':[tx]}for tx in txs])
    # Lagoon event payloads contain epochs but no timestamps. Retain headers for
    # every request/settlement/claim block so waits use observed chain time.
    wanted=['RedeemRequest(address,address,uint256,address,uint256)','SettleRedeem(uint40,uint40,uint256,uint256,uint256,uint256)','Withdraw(address,address,address,uint256,uint256)']
    topics={'0x'+keccak(x.encode()).hex()for x in wanted}
    logs=[x for r in json.loads((RAW/'rocksolid_exitlogs_T.json').read_text())['records']for x in r['response'].get('result',[]) if x['topics'][0]in topics]
    blocks=sorted({int(x['blockNumber'],16)for x in logs})
    rpc('rocksolid_exit_block_headers',[{'label':str(b),'method':'eth_getBlockByNumber','params':[hex(b),False]}for b in blocks])

if __name__=='__main__':{'authority':follow_authority,'balances':balances,'logs':exit_logs,'receipts':receipts}[sys.argv[1]]()
