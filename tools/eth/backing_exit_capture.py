"""Reproducible read-only fixed-block backing and exit captures.

This collector exclusively uses eth_call, eth_getStorageAt, eth_getCode,
eth_getLogs, eth_getTransactionReceipt and ordinary HTTP GET. It never signs
or broadcasts transactions. Non-view eth_call simulations do not persist.
"""
from __future__ import annotations
import datetime as dt, hashlib, json, pathlib, sys, time, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[2]
RAW=ROOT/'raw/eth/research-closure-2026-10-04/exit'
T=1790985599
BLOCK=26108081
TAG=hex(BLOCK)
RPC='https://eth-mainnet.public.blastapi.io'
LOG_RPC='https://gateway.tenderly.co/public/mainnet'
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel, enc_addr, enc_uint, keccak

def fetch(key,url,payload=None):
    RAW.mkdir(parents=True,exist_ok=True)
    request={'key':key,'url':url,'observedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'financialTimestamp':T}
    if payload is not None: request['request']=payload
    req=urllib.request.Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers={'User-Agent':'ETH-Yield-Research/1.0',**({'Content-Type':'application/json'} if payload is not None else {})})
    try:
        with urllib.request.urlopen(req,timeout=55) as r: body=r.read();request.update(status=r.status,sourceDate=r.headers.get('Date'))
        request.update(sha256=hashlib.sha256(body).hexdigest(),bytes=len(body))
        path=RAW/(key+'-'+request['sha256'][:16]+('.json' if body.lstrip().startswith((b'{',b'[')) else '.txt'))
        path.write_bytes(body);request['path']=str(path.relative_to(ROOT))
        result=json.loads(body) if path.suffix=='.json' else body.decode('utf8',errors='replace')
    except Exception as e:
        request.update(error=repr(e)); result=None
    with (RAW/'requests.jsonl').open('a') as f: f.write(json.dumps(request)+'\n')
    print(json.dumps({k:request[k] for k in ['key','status','bytes','error'] if k in request}),flush=True)
    return result

def rpc(key,rows,url=RPC):
    records=[]
    for i in range(0,len(rows),20):
        chunk=rows[i:i+20]
        payload=[{'jsonrpc':'2.0','id':i+j+1,'method':r['method'],'params':r['params']} for j,r in enumerate(chunk)]
        res=fetch(key+'_batch_'+str(i//20),url,payload)
        if isinstance(res,dict):res=[res]
        byid={r['id']:r for r in (res or []) if 'id' in r}
        for j,r in enumerate(chunk): records.append({**r,'response':byid.get(i+j+1,{'error':{'message':'Capture failed'}})})
    out={'financialTimestamp':T,'ethereumBlock':BLOCK,'records':records}
    (RAW/(key+'.json')).write_text(json.dumps(out,indent=2))
    return out

def call(label,to,sig,args='',caller=None,tag=TAG,gas=30000000):
    tx={'to':to,'data':'0x'+sel(sig)+args,'gas':hex(gas)}
    if caller:tx['from']=caller
    return {'label':label,'method':'eth_call','params':[tx,tag]}

def state(label,method,address,tag=TAG,*extra):
    return {'label':label,'method':method,'params':[address,*extra,tag]}

def initial():
    machine='0x0fdf9f1920e160ea8ae267bde13e725def81e5ee'
    caliber='0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0'
    risk='0x82eece4a736db0767370d2dffde9bdf6e38aaeb8'
    slot='0x'+(int.from_bytes(keccak(b'eip1967.proxy.beacon'),'big')-1).to_bytes(32,'big').hex()
    rows=[]
    for name,address in [('machine',machine),('caliber',caliber)]:
        rows.append(state(name+'_beacon','eth_getStorageAt',address,TAG,slot))
        rows.append(state(name+'_code','eth_getCode',address))
    rows.append(state('risk_manager_code','eth_getCode',risk))
    for sig in ['getThreshold()','getOwners()','getMinDelay()','owner()','authority()','getModuleGuard()','getGuard()']:
        rows.append(call('risk_'+sig,risk,sig))
    for sig in ['riskManager()','riskManagerTimelock()','redeemer()','lastTotalAum()','lastGlobalAccountingTime()','maxWithdraw()','hubCaliber()']:
        rows.append(call('machine_'+sig,machine,sig))
    for sig in ['isAccountingFresh()','getNetAum()','getDetailedAum()','timelockDuration()','positionStaleThreshold()','hubMachineEndpoint()','pendingTimelockExpiry()','allowedInstrRoot()','pendingAllowedInstrRoot()']:
        rows.append(call('caliber_'+sig,caliber,sig))
    for label,caller in [('risk',risk),('random','0x1111111111111111111111111111111111111111')]:
        rows.append(call('simulation_set_duration_'+label,caliber,'setTimelockDuration(uint256)',enc_uint(0),caller))
    out=rpc('royco_authority_initial_T',rows)
    for key,url in [('risk_manager_verified','https://eth.blockscout.com/api/v2/smart-contracts/'+risk),('concrete_wallet_tokens','https://eth.blockscout.com/api/v2/addresses/0x7ee29373f075ee1d83b1b93b4fe94ae242df5178/token-balances'),('rocksolid_wallet_tokens','https://eth.blockscout.com/api/v2/addresses/0x9ca1d6e730eb9fbfd45c9ff5f0ac4e3d172d8f4d/token-balances'),('monad_wallet_tokens','https://monad.blockscout.com/api/v2/addresses/0xa024063b630d554078bbf985718b22f3c6870ee0/token-balances'),('spark_price_T',f'https://coins.llama.fi/prices/historical/{T}/ethereum:0xe92ec83d8ea27f802393f084004491e463209acb')]:fetch(key,url)
    return out

def authority():
    machine='0x0fdf9f1920e160ea8ae267bde13e725def81e5ee'; caliber='0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0'
    risk='0x82eece4a736db0767370d2dffde9bdf6e38aaeb8'; admin='0x35518d5e1fd8105fc325c5c171c329c3b10b254c'
    rows=[]
    for name,beacon in [('machine','0x5c680ec39bafe8524f3c2fa9d5f6d65f09bd7333'),('caliber','0x3f5a881db86d6f495823028a1e892e7b2cd7e162')]:
        rows.extend([call(name+'_implementation',beacon,'implementation()'),call(name+'_beacon_owner',beacon,'owner()'),state(name+'_beacon_code','eth_getCode',beacon)])
        fetch(name+'_beacon_verified','https://eth.blockscout.com/api/v2/smart-contracts/'+beacon)
    for name,target,sig in [('set_duration',caliber,'setTimelockDuration(uint256)'),('schedule_root',caliber,'scheduleAllowedInstrRootUpdate(bytes32)'),('change_risk_timelock',machine,'setRiskManagerTimelock(address)')]:
        selector=sel(sig).ljust(64,'0')
        rows.append(call(name+'_role',risk,'getTargetFunctionRole(address,bytes4)',enc_addr(target)+selector))
        for who in [admin,'0x7c405bbd131e42af506d14e752f2e59b19d49997','0x425bbc2cff0c7e7960baa9bac2f0cb67b41d3bef']:
            rows.append(call(name+'_canCall_'+who,risk,'canCall(address,address,bytes4)',enc_addr(who)+enc_addr(target)+selector))
        rows.append(call(name+'_admin_delay',risk,'getTargetAdminDelay(address)',enc_addr(target)))
        rows.append(call(name+'_target_closed',risk,'isTargetClosed(address)',enc_addr(target)))
    rows.append(call('initial_admin_access',risk,'getAccess(uint64,address)',enc_uint(0)+enc_addr(admin)))
    out=rpc('royco_authority_mapped_T',rows)
    for r in out['records']:
        if '_implementation' in r['label'] and r['response'].get('result'):
            address='0x'+r['response']['result'][-40:]
            fetch(r['label']+'_verified_T','https://eth.blockscout.com/api/v2/smart-contracts/'+address)
    topic='0x'+keccak(b'RoleGranted(uint64,address,uint32,uint48,bool)').hex()
    rows=[{'label':'risk_roles_'+str(start),'method':'eth_getLogs','params':[{'address':risk,'fromBlock':hex(start),'toBlock':hex(min(start+999999,BLOCK)),'topics':[topic]}]} for start in range(23000000,BLOCK+1,1000000)]
    rpc('royco_role_grants_T',rows,LOG_RPC)
    fetch('spark_token_verified','https://eth.blockscout.com/api/v2/smart-contracts/0xe92ec83d8ea27f802393f084004491e463209acb')
    fetch('spark_token_info','https://eth.blockscout.com/api/v2/tokens/0xe92ec83d8ea27f802393f084004491e463209acb')
    fetch('spark_native_price_T',f'https://coins.llama.fi/prices/historical/{T}/ethereum:0xc20059e0317de91738d13af027dfc4a50781b066')
    return out

def exits():
    # Each percentage uses the product's native totalAssets denomination. Holder
    # capacity is explicitly measured so oversized calls are not called exits.
    products=[('concrete','0xb9dc54c8261745cb97070cefbe3d3d815aee8f20','0x5bab73f561a5365c9e4bbc7c52fe0fa384fcf324',278170834212774056088739),('royco','0x41ce72e04d349eb957bdc373baa9c69207032c56','0xfef0bb8df6210e441f03de23edafb0150129e176',93184063921112563200),('liquity','0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c','0x1676d23711186076fa74aa53511dda750a1f0d9a',6014001735111082411023),('rocksolid','0x936facdf10c8c36294e7b9d28345255539d81bc7','0xeadb3840596cabf312f2bc88a4bb0b93a4e1ff5f',8293351833532688818973)]
    rows=[]
    for name,address,holder,assets in products:
        for sig in ['totalAssets()','totalSupply()','asset()','isQueueActive()','latestEpochID()','pastEpochsUnclaimedAssets()','totalRequestedSharesForCurrentEpochs()']:
            rows.append(call(name+'_'+sig,address,sig))
        rows.extend([call(name+'_holder_balance',address,'balanceOf(address)',enc_addr(holder)),call(name+'_max_withdraw',address,'maxWithdraw(address)',enc_addr(holder)),call(name+'_max_redeem',address,'maxRedeem(address)',enc_addr(holder))])
        for pct in [1,10,30]:
            amount=assets*pct//100
            rows.append(call(name+'_withdraw_'+str(pct)+'pct',address,'withdraw(uint256,address,address)',enc_uint(amount)+enc_addr(holder)+enc_addr(holder),holder))
            rows.append(call(name+'_preview_shares_'+str(pct)+'pct',address,'previewWithdraw(uint256)',enc_uint(amount)))
        rows.append(call(name+'_withdraw_1native',address,'withdraw(uint256,address,address)',enc_uint(10**18)+enc_addr(holder)+enc_addr(holder),holder))
    return rpc('withdraw_simulations_T',rows)

if __name__=='__main__':
    command=sys.argv[1] if len(sys.argv)>1 else 'initial'
    {'initial':initial,'authority':authority,'exits':exits}[command]()
