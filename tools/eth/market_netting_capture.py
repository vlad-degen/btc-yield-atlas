"""Append-only evidence capture for market netting, fixed to the original ETH T.

This collector never rewrites the canonical market panel or snapshot. HTTP pages
are context unless the returned data independently identifies T or its block.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'raw/eth/research-closure-2026-10-04/market'
T = 1790985599
BLOCK = 26108081
SLOT = 15346798
STATE_ROOT = '0x14a3c4ae7fcd440993b15b81da8e0cc491d93d866ccc1b4d858add1d30441282'
_LOCK = threading.Lock()

def capture(key, url, payload=None, timeout=35):
    RAW.mkdir(parents=True, exist_ok=True)
    encoded = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(url, data=encoded, headers={
        'User-Agent': 'ETHResearch/1.0 (historical read-only research)',
        'Accept': 'application/json,text/html,*/*',
        'Content-Type': 'application/json'})
    error = None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body, status, content_type = response.read(), response.status, response.headers.get('Content-Type', '')
    except urllib.error.HTTPError as exc:
        body, status, content_type = exc.read(), exc.code, exc.headers.get('Content-Type', '')
        error = str(exc)
    except Exception as exc:
        body, status, content_type = str(exc).encode(), None, 'text/plain'
        error = str(exc)
    sha = hashlib.sha256(body).hexdigest()
    try:
        value = json.loads(body)
        suffix = '.json'
    except (ValueError, UnicodeDecodeError):
        value = None
        suffix = '.txt'
    path = RAW / (key + '-' + sha[:16] + suffix)
    path.write_bytes(body)
    record = {'key': key, 'url': url, 'method': 'POST' if payload is not None else 'GET',
              'request': payload, 'captured_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'http_status': status, 'content_type': content_type, 'sha256': sha,
              'bytes': len(body), 'path': str(path.relative_to(ROOT)), 'error': error,
              'financial_target_timestamp': T, 'is_financial_observation_at_T': False}
    with _LOCK:
        with (RAW / 'requests.jsonl').open('a') as out:
            out.write(json.dumps(record) + '\n')
    print(key, status, len(body), error or '', flush=True)
    return record, value

def consensus_probes():
    tasks = [
        ('beacon_publicnode_slot_balance', f'https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/{SLOT}/validator_balances?id=0'),
        ('beacon_publicnode_epoch_balance', 'https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/15346784/validator_balances?id=0'),
        ('beacon_publicnode_root_validator', f'https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/{STATE_ROOT}/validators/0'),
        ('beacon_lodestar_slot_balance', f'https://lodestar-mainnet.chainsafe.io/eth/v1/beacon/states/{SLOT}/validator_balances?id=0'),
        ('beacon_lightclient_slot_balance', f'https://www.lightclientdata.org/eth/v1/beacon/states/{SLOT}/validator_balances?id=0'),
        ('beacon_drpc_slot_balance', f'https://eth-beacon-chain.drpc.org/rest/eth/v1/beacon/states/{SLOT}/validator_balances?id=0'),
        ('beacon_alchemy_slot_balance', f'https://eth-mainnetbeacon.g.alchemy.com/v2/docs-demo/eth/v1/beacon/states/{SLOT}/validator_balances?id=0'),
        ('beaconchain_ethstore_day', f'https://beaconcha.in/api/v1/ethstore/{(T-1606824023)//86400}'),
        ('beaconchain_ethstore_page', 'https://www.beaconcha.in/ethstore'),
        ('beaconchain_staked_chart', 'https://beaconcha.in/charts/staked_ether'),
        ('beaconchain_ethstore_docs', 'https://docs.beaconcha.in/api-reference/ethereum/eth-store'),
        ('migalabs_balance_docs', 'https://docs.migalabs.io/validators/active_val_effective_balance'),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda item: capture(*item), tasks))
    (ROOT/'data/eth/market_netting_consensus_probes.json').write_text(json.dumps([x[0] for x in results], indent=2))

def rpc(calls, key):
    payload = [{'jsonrpc':'2.0','id':i+1,'method':method,'params':params} for i,(method,params) in enumerate(calls)]
    good={};last_by_id={}
    for i,url in enumerate(['https://eth-mainnet.public.blastapi.io','https://gateway.tenderly.co/public/mainnet','https://eth.drpc.org']):
        remaining=[item for item in payload if item['id'] not in good]
        if not remaining:break
        record,value = capture(key+f'_provider{i}',url,remaining,timeout=45)
        if isinstance(value,list):
            for item in value:
                last_by_id[item['id']]=item
                if 'result' in item:good[item['id']]=item
        if len(good)==len(calls):break
    return record,[good.get(i+1,last_by_id.get(i+1,{'id':i+1,'error':{'message':'No successful RPC response'}})) for i in range(len(calls))]

def lido_and_weth():
    sys.path.insert(0, str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel, enc_addr
    steth='0xae7ab96520de3a18e5e111b5eaab095312d7fe84'
    weth='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    labels=[];calls=[]
    for sig in ['getTotalPooledEther()','getBufferedEther()','getBeaconStat()','getBalanceStats()','getExternalEther()','getLidoLocator()','totalSupply()']:
        labels.append({'kind':'call','address':steth,'signature':sig})
        calls.append(('eth_call',[{'to':steth,'data':'0x'+sel(sig)},hex(BLOCK)]))
    labels.append({'kind':'call','address':weth,'signature':'totalSupply()'})
    calls.append(('eth_call',[{'to':weth,'data':'0x'+sel('totalSupply()')},hex(BLOCK)]))
    for address,name in [(weth,'canonical WETH escrow'),(steth,'Lido contract buffer'),('0x889edc2edab5f40e902b864ad4d7ade8e412f9b1','Lido withdrawal queue')]:
        labels.append({'kind':'native_balance','address':address,'name':name})
        calls.append(('eth_getBalance',[address,hex(BLOCK)]))
    record,responses=rpc(calls,'issuer_and_weth_T')
    (ROOT/'data/eth/market_netting_issuer_calls_T.json').write_text(json.dumps({'target_timestamp':T,'block':BLOCK,'labels':labels,'responses':responses,'source':record},indent=2))

def alternatives():
    payload={'range':{'epoch':{'start':479587,'end':479588}},'chain':'mainnet','cursor':'','page_size':2}
    tasks=[
        ('beaconchain_epoch_v2','https://beaconcha.in/api/v2/ethereum/epoch',{'epoch':479587,'chain':'mainnet'}),
        ('beaconchain_ethstore_v2','https://beaconcha.in/api/v2/ethereum/eth-store',payload),
        ('migalabs_effective_balance','https://www.migalabs.io/api/eth/v1/beacon/consensus/validators/active_val_effective_balance?network=mainnet'),
        ('beacon_publicnode_slot_validators',f'https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/{SLOT}/validators?id=0'),
        ('beacon_publicnode_state_root',f'https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/{SLOT}/root'),
        ('beacon_publicnode_blockroot_validator','https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/0xb06fee15650a3960182cc1011553328d3e14210c76834db38b0d840059a18e29/validators/0'),
        ('beaconstate_provider','https://beaconstate.info/'),
        ('lido_accounting_docs','https://docs.lido.fi/contracts/accounting/'),
        ('lido_pool_docs','https://docs.lido.fi/contracts/lido/'),
        ('lido_locator_docs','https://docs.lido.fi/contracts/lido-locator/'),
        ('eip_max_effective','https://eips.ethereum.org/EIPS/eip-7251'),
        ('ethereum_beacon_api_spec','https://raw.githubusercontent.com/ethereum/beacon-APIs/master/apis/beacon/states/validator_balances.yaml'),
        ('beaconchain_ethstore_source','https://raw.githubusercontent.com/gobitfly/eth.store/master/main.go'),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(lambda item:capture(*item),tasks))
    (ROOT/'data/eth/market_netting_alternative_probes.json').write_text(json.dumps([x[0] for x in results],indent=2))

def custody():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr
    first=json.loads((ROOT/'data/eth/market_netting_issuer_calls_T.json').read_text())
    locator='0x'+first['responses'][5]['result'][-40:]
    labels=[];calls=[]
    def call(address,sig,args='',name=None):
        labels.append({'kind':'call','address':address,'signature':sig,'name':name})
        calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)+args},hex(BLOCK)]))
    for sig in ['withdrawalVault()','elRewardsVault()','accountingOracle()','stakingRouter()','withdrawalQueue()','vaultHub()','accounting()']:
        call(locator,sig)
    record,rr=rpc(calls,'lido_locator_T')
    out={'target_timestamp':T,'block':BLOCK,'locator':locator,'labels':labels,'responses':rr,'source':record}
    (ROOT/'data/eth/market_netting_locator_T.json').write_text(json.dumps(out,indent=2))
    labels=[];calls=[]
    for l,r in zip(out['labels'],rr):
        if 'result' not in r or len(r['result'])<66:continue
        address='0x'+r['result'][-40:]
        labels.append({'kind':'native_balance','address':address,'name':'Lido '+l['signature']})
        calls.append(('eth_getBalance',[address,hex(BLOCK)]))
        if l['signature']=='accountingOracle()':
            for sig in ['getLastProcessingRefSlot()','getConsensusReport()','getProcessingState()']:
                call(address,sig,name='Lido oracle timing')
    weth='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    for pool in sorted({x['pool'] for x in json.loads((ROOT/'data/eth/etherfi_uniswap_positions.json').read_text())}):
        for sig in ['token0()','token1()','fee()','liquidity()','slot0()']:
            call(pool,sig,name='Liquid ETH Uniswap V3 pool')
        call(weth,'balanceOf(address)',enc_addr(pool),name='Liquid ETH Uniswap V3 pool WETH cash')
    for protocol,address in [('Aave','0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'),('Spark','0xc13e21b648a5ee794902342038ff3adab66be987')]:
        call(address,'getReservesList()',name=protocol+' reserve list')
    record,rr=rpc(calls,'root_custody_T')
    (ROOT/'data/eth/market_netting_custody_T.json').write_text(json.dumps({'target_timestamp':T,'block':BLOCK,'labels':labels,'responses':rr,'source':record},indent=2))

def lending_edges():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr
    pools={'aave':'0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2','spark':'0xc13e21b648a5ee794902342038ff3adab66be987'}
    assets={'wstETH':'0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','weETH':'0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','rETH':'0xae78736cd615f374d3085123a210448e74fc6393'}
    labels=[];calls=[]
    for protocol,pool in pools.items():
        for symbol,asset in assets.items():
            labels.append({'protocol':protocol,'pool':pool,'symbol':symbol,'asset':asset,'signature':'getReserveData(address)'})
            calls.append(('eth_call',[{'to':pool,'data':'0x'+sel('getReserveData(address)')+enc_addr(asset)},hex(BLOCK)]))
    record,rr=rpc(calls,'receipt_reserve_identity_T')
    identity={'target_timestamp':T,'block':BLOCK,'labels':labels,'responses':rr,'source':record}
    (ROOT/'data/eth/market_netting_reserve_identity_T.json').write_text(json.dumps(identity,indent=2))
    labels=[];calls=[]
    for l,r in zip(identity['labels'],rr):
        if not r.get('result') or r['result']=='0x':continue
        s=r['result'][2:];words=[s[i:i+64] for i in range(0,len(s),64)]
        if len(words)<11:continue
        a_token='0x'+words[8][-40:];debt_token='0x'+words[10][-40:]
        if int(a_token,16)==0:continue
        for address,sig,arg,kind in [(l['asset'],'balanceOf(address)',enc_addr(a_token),'cash'),(a_token,'totalSupply()','','lender_claim'),(debt_token,'totalSupply()','','debt')]:
            labels.append({**l,'signature':sig,'address':address,'aToken':a_token,'debtToken':debt_token,'kind':kind})
            calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)+arg},hex(BLOCK)]))
    for symbol,address,sig in [('wstETH',assets['wstETH'],'stEthPerToken()'),('weETH',assets['weETH'],'getEETHByWeETH(uint256)'),('rETH',assets['rETH'],'getExchangeRate()')]:
        from keccak_lib import enc_uint
        labels.append({'symbol':symbol,'address':address,'signature':sig,'kind':'exchange_rate'})
        calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)+(enc_uint(10**18) if symbol=='weETH' else '')},hex(BLOCK)]))
    # These receipt reserves are different claims on existing issuer backing.
    sources=[];responses=[]
    for start in range(0,len(calls),25):
        record,rr=rpc(calls[start:start+25],f'receipt_reserve_balances_T_{start}')
        sources.append(record);responses.extend(rr)
    (ROOT/'data/eth/market_netting_lending_edges_T.json').write_text(json.dumps({'target_timestamp':T,'block':BLOCK,'labels':labels,'responses':responses,'sources':sources},indent=2))

def primary_lp():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr,enc_uint
    factory='0x1f98431c8ad98523631ae4a59f267346ea31f984'
    weth='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    tokens={'USDC':'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48','USDT':'0xdac17f958d2ee523a2206206994597c13d831ec7','DAI':'0x6b175474e89094c44da98b954eedeac495271d0f','wstETH':'0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','weETH':'0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','rETH':'0xae78736cd615f374d3085123a210448e74fc6393'}
    labels=[];calls=[]
    for symbol,token in tokens.items():
        for fee in [100,500,3000,10000]:
            labels.append({'kind':'pool_discovery','counterasset':symbol,'counterasset_address':token,'fee':fee,'factory':factory})
            calls.append(('eth_call',[{'to':factory,'data':'0x'+sel('getPool(address,address,uint24)')+enc_addr(weth)+enc_addr(token)+enc_uint(fee)},hex(BLOCK)]))
    record,rr=rpc(calls,'canonical_v3_pool_discovery_T')
    discovery={'target_timestamp':T,'block':BLOCK,'labels':labels,'responses':rr,'source':record}
    (ROOT/'data/eth/market_netting_lp_discovery_T.json').write_text(json.dumps(discovery,indent=2))
    found=[]
    for l,r in zip(labels,rr):
        if r.get('result') and int(r['result'],16):found.append({**l,'address':'0x'+r['result'][-40:]})
    labels=[];calls=[]
    for pool in found:
        for sig,address,arg,kind in [('token0()',pool['address'],'','token0'),('token1()',pool['address'],'','token1'),('balanceOf(address)',weth,enc_addr(pool['address']),'WETH_cash')]:
            labels.append({**pool,'kind':kind,'signature':sig})
            calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)+arg},hex(BLOCK)]))
    labels.append({'kind':'native_ETH_cash','address':'0xdc24316b9ae028f1497c275eb9192a3ea0f67022','name':'Curve stETH original pool'})
    calls.append(('eth_getBalance',['0xdc24316b9ae028f1497c275eb9192a3ea0f67022',hex(BLOCK)]))
    for i in [0,1]:
        labels.append({'kind':'curve_coin','address':'0xdc24316b9ae028f1497c275eb9192a3ea0f67022','coin_index':i})
        calls.append(('eth_call',[{'to':'0xdc24316b9ae028f1497c275eb9192a3ea0f67022','data':'0x'+sel('coins(uint256)')+enc_uint(i)},hex(BLOCK)]))
    responses=[];sources=[]
    for start in range(0,len(calls),24):
        record,rr=rpc(calls[start:start+24],f'primary_lp_cash_T_{start}')
        responses.extend(rr);sources.append(record)
    (ROOT/'data/eth/market_netting_lp_cash_T.json').write_text(json.dumps({'target_timestamp':T,'block':BLOCK,'discovered_pools':found,'labels':labels,'responses':responses,'sources':sources,'scope':'Six specified WETH pairs at all four canonical V3 fee tiers, plus one named Curve pool. Not all LP venues or pools.'},indent=2))
    tasks=[('uniswap_factory_docs','https://docs.uniswap.org/contracts/v3/reference/core/interfaces/IUniswapV3Factory'),('uniswap_factory_source','https://raw.githubusercontent.com/Uniswap/v3-core/main/contracts/UniswapV3Factory.sol'),('curve_main_pools_directory','https://api.curve.fi/v1/getPools/ethereum/main'),('beaconchain_openapi','https://docs.beaconcha.in/v3/bundled.yaml')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda item:capture(*item),tasks))

def curve_main():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_uint,enc_addr
    source=max(RAW.glob('curve_main_pools_directory-*.json'),key=lambda p:p.stat().st_size)
    directory=json.loads(source.read_text())['data']['poolData']
    root_assets={'0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':'native_ETH','0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2':'WETH'}
    found=[];labels=[];calls=[]
    for item in directory:
        for i,coin in enumerate(item.get('coins',[])):
            asset=coin['address'].lower()
            if asset not in root_assets:continue
            row={'name':item['name'],'address':item['address'].lower(),'coin_index':i,'asset':asset,'root_asset':root_assets[asset]}
            found.append(row)
            labels.append({**row,'kind':'code'});calls.append(('eth_getCode',[row['address'],hex(BLOCK)]))
            labels.append({**row,'kind':'coin'});calls.append(('eth_call',[{'to':row['address'],'data':'0x'+sel('coins(uint256)')+enc_uint(i)},hex(BLOCK)]))
            labels.append({**row,'kind':'cash'})
            calls.append(('eth_getBalance',[row['address'],hex(BLOCK)]) if row['root_asset']=='native_ETH' else ('eth_call',[{'to':asset,'data':'0x'+sel('balanceOf(address)')+enc_addr(row['address'])},hex(BLOCK)]))
    record,rr=rpc(calls,'curve_main_root_cash_T')
    (ROOT/'data/eth/market_netting_curve_cash_T.json').write_text(json.dumps({'target_timestamp':T,'block':BLOCK,'directory_metadata_captured_after_T':True,'directory_source':str(source.relative_to(ROOT)),'directory_pool_count':len(directory),'selected_root_pools':found,'labels':labels,'responses':rr,'source':record,'historical_identity_checked':True},indent=2))

def lp_history():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr
    records=json.loads((ROOT/'data/eth/benchmark_history_ethereum_rpc.json').read_text())
    blocks=[]
    for label,response in zip(records['labels'],records['responses']):
        if label['metric']!='block':continue
        date=dt.datetime.fromtimestamp(label['target_timestamp'],dt.timezone.utc)
        if (date+dt.timedelta(seconds=1)).day!=1 or date.hour!=23:continue
        block=response['result'];assert int(block['timestamp'],16)<=label['target_timestamp']
        blocks.append({**label,'month':date.strftime('%Y-%m'),'block_timestamp':int(block['timestamp'],16),'block_hash':block['hash']})
    blocks=sorted({x['target_timestamp']:x for x in blocks}.values(),key=lambda x:x['target_timestamp'])
    lp=json.loads((ROOT/'data/eth/market_netting_lp_cash_T.json').read_text())
    curve=json.loads((ROOT/'data/eth/market_netting_curve_cash_T.json').read_text())
    pools=[{'address':x['address'],'asset':'WETH','label':x['counterasset']+' / WETH '+str(x['fee'])} for x in lp['discovered_pools']]
    pools+=[{'address':x['address'],'asset':x['root_asset'],'label':x['name']} for x in curve['selected_root_pools']]
    labels=[];calls=[];weth='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    for block in blocks:
        for item in pools:
            tag=hex(block['block'])
            labels.append({**block,**item,'kind':'code'});calls.append(('eth_getCode',[item['address'],tag]))
            labels.append({**block,**item,'kind':'cash'})
            calls.append(('eth_getBalance',[item['address'],tag]) if item['asset']=='native_ETH' else ('eth_call',[{'to':weth,'data':'0x'+sel('balanceOf(address)')+enc_addr(item['address'])},tag]))
    responses=[];sources=[]
    chunks=list(range(0,len(calls),24))
    def get(start):
        record,rr=rpc(calls[start:start+24],f'bounded_lp_history_{start}')
        return start,record,rr
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        collected=sorted(pool.map(get,chunks),key=lambda x:x[0])
    for start,record,rr in collected:sources.append(record);responses.extend(rr)
    (ROOT/'data/eth/market_netting_lp_history_rpc.json').write_text(json.dumps({'financial_target_timestamp':T,'blocks':blocks,'pools':pools,'labels':labels,'responses':responses,'sources':sources,'scope':'Root native ETH or canonical WETH custody at named pools. Current bounded pool universe, not a market-wide census, LP investor NAV, LP return or deposits. Nonexistent contracts are separately labelled. No interpolation.'},indent=2))

def repair_history():
    """Recover partial successes, then retry only unresolved cash reads gently."""
    import time
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr
    path=ROOT/'data/eth/market_netting_lp_history_rpc.json'
    v=json.loads(path.read_text());responses=v['responses'];manifest=[json.loads(line) for line in (RAW/'requests.jsonl').read_text().splitlines()]
    for record in manifest:
        key=record['key']
        if not key.startswith('bounded_lp_history_') or 'provider' not in key:continue
        start=int(key.split('_')[3]);p=ROOT/record['path']
        try:items=json.loads(p.read_text())
        except ValueError:continue
        if not isinstance(items,list):continue
        for item in items:
            index=start+item['id']-1
            if 'result' in item and index<len(responses):responses[index]=item
    unresolved=[i for i,l in enumerate(v['labels']) if l['kind']=='cash' and 'result' not in responses[i]]
    print('Recovered historical cash',sum(l['kind']=='cash' and 'result' in r for l,r in zip(v['labels'],responses)),'retrying',len(unresolved),flush=True)
    weth='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    for start in range(0,len(unresolved),2):
        indexes=unresolved[start:start+2];calls=[]
        for index in indexes:
            l=v['labels'][index];tag=hex(l['block'])
            calls.append(('eth_getBalance',[l['address'],tag]) if l['asset']=='native_ETH' else ('eth_call',[{'to':weth,'data':'0x'+sel('balanceOf(address)')+enc_addr(l['address'])},tag]))
        record,rr=rpc(calls,f'bounded_lp_cash_repair_{start}')
        v['sources'].append(record)
        for index,result in zip(indexes,rr):responses[index]=result
        time.sleep(.2)
    v['responses']=responses
    v['cash_retries_only']=True
    path.write_text(json.dumps(v,indent=2))

def correct_consensus_schema():
    # The captured official OpenAPI defines object selectors, not bare numbers.
    tasks=[('beaconchain_epoch_v2_valid','https://beaconcha.in/api/v2/ethereum/epoch',{'epoch':{'number':479587},'chain':'mainnet'}),('beaconchain_ethstore_v2_valid','https://beaconcha.in/api/v2/ethereum/eth-store',{'range':{'epoch':{'start':{'number':479362},'end':{'number':479587}}},'chain':'mainnet','cursor':'','page_size':2}),('beaconchain_ethstore_v2_alltime','https://beaconcha.in/api/v2/ethereum/eth-store',{'range':{'window':'all_time'},'chain':'mainnet','page_size':3})]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda item:capture(*item),tasks))

def restaking_sources():
    tasks=[
        ('eigenlayer_adapter_source','https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/eigenlayer/index.js'),
        ('kelp_adapter_source','https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/kelp-dao/index.js'),
        ('symbiotic_adapter_source','https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/symbiotic/index.js'),
        ('eigenlayer_official_deployments','https://raw.githubusercontent.com/Layr-Labs/eigenlayer-contracts/master/script/output/mainnet/M2_deployment_data.json'),
        ('eigenlayer_official_readme','https://raw.githubusercontent.com/Layr-Labs/eigenlayer-contracts/master/README.md'),
        ('lido_wsteth_docs','https://docs.lido.fi/contracts/wsteth/'),
        ('lido_withdrawal_queue_docs','https://docs.lido.fi/contracts/withdrawal-queue-erc721/'),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(lambda item:capture(*item),tasks))

def restaking_edges():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr,enc_uint
    steth='0xae7ab96520de3a18e5e111b5eaab095312d7fe84'
    strategy='0x93c4b944d05dfe6df7645a86cd2206016c51564d'
    manager='0x858646372cc42e1a627fce94aa7a7033e7cf075a'
    kelp='0x036676389e48133b63a802f8635ad39e752d375d'
    labels=[];calls=[]
    def call(address,sig,args='',name=None):
        labels.append({'address':address,'signature':sig,'name':name})
        calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)+args},hex(BLOCK)]))
    call(strategy,'underlyingToken()',name='Eigen stETH strategy token identity')
    call(manager,'strategyIsWhitelistedForDeposit(address)',enc_addr(strategy),name='Eigen stETH strategy permission')
    call(strategy,'totalShares()',name='Eigen stETH strategy total shares')
    call(steth,'balanceOf(address)',enc_addr(strategy),name='Eigen stETH custody')
    call(kelp,'lrtConfig()',name='Kelp configuration identity')
    call(kelp,'getTotalAssetDeposits(address)',enc_addr(steth),name='Kelp stETH accounting claim')
    call(kelp,'getNodeDelegatorQueue()',name='Kelp node delegators')
    record,rr=rpc(calls,'restaking_duplicate_edges_T')
    out={'target_timestamp':T,'block':BLOCK,'labels':labels,'responses':rr,'source':record}
    if len(rr)>2 and rr[2].get('result'):
        share=int(rr[2]['result'],16)
        record2,rr2=rpc([('eth_call',[{'to':strategy,'data':'0x'+sel('sharesToUnderlying(uint256)')+enc_uint(share)},hex(BLOCK)])],'eigen_steth_underlying_T')
        out['strategy_underlying']={'shares':str(share),'response':rr2[0],'source':record2}
    (ROOT/'data/eth/market_netting_restaking_edges_T.json').write_text(json.dumps(out,indent=2))

def kelp_nested():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr,enc_uint
    first=json.loads((ROOT/'data/eth/market_netting_restaking_edges_T.json').read_text())
    s=first['responses'][6]['result'][2:]
    nodes=['0x'+s[i+24:i+64] for i in range(128,len(s),64)]
    manager='0x858646372cc42e1a627fce94aa7a7033e7cf075a'
    strategy='0x93c4b944d05dfe6df7645a86cd2206016c51564d'
    steth='0xae7ab96520de3a18e5e111b5eaab095312d7fe84'
    labels=[];calls=[]
    for node in nodes:
        for address,sig,args,kind in [(manager,'stakerDepositShares(address,address)',enc_addr(node)+enc_addr(strategy),'eigen_deposit_shares'),(manager,'stakerStrategyShares(address,address)',enc_addr(node)+enc_addr(strategy),'legacy_eigen_shares'),(steth,'balanceOf(address)',enc_addr(node),'direct_stETH')]:
            labels.append({'node':node,'address':address,'signature':sig,'kind':kind})
            calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)+args},hex(BLOCK)]))
    record,rr=rpc(calls,'kelp_eigen_nesting_T')
    out={'target_timestamp':T,'block':BLOCK,'nodes':nodes,'labels':labels,'responses':rr,'source':record}
    shares=[(l,int(r['result'],16)) for l,r in zip(labels,rr) if l['kind']=='eigen_deposit_shares' and r.get('result') and r['result']!='0x']
    if shares:
        record,results=rpc([('eth_call',[{'to':strategy,'data':'0x'+sel('sharesToUnderlying(uint256)')+enc_uint(share)},hex(BLOCK)]) for l,share in shares],'kelp_eigen_underlying_T')
        out['converted_node_shares']=[{'node':l['node'],'shares':str(share),'response':r} for (l,share),r in zip(shares,results)]
        out['conversion_source']=record
    (ROOT/'data/eth/market_netting_kelp_nesting_T.json').write_text(json.dumps(out,indent=2))
    capture('eigenlayer_strategy_manager_source','https://raw.githubusercontent.com/Layr-Labs/eigenlayer-contracts/v1.13.0/src/contracts/core/StrategyManager.sol')

def final_checks():
    sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
    from keccak_lib import sel,enc_addr
    queue='0x889edc2edab5f40e902b864ad4d7ade8e412f9b1'
    kelp='0x036676389e48133b63a802f8635ad39e752d375d'
    steth='0xae7ab96520de3a18e5e111b5eaab095312d7fe84'
    labels=[];calls=[]
    for address,sig,args,name in [(queue,'getLockedEtherAmount()','','Lido ETH reserved for finalized withdrawal claims'),(queue,'unfinalizedStETH()','','Lido unfinalized stETH requests'),(steth,'balanceOf(address)',enc_addr(kelp),'Kelp deposit-pool direct stETH custody')]:
        labels.append({'address':address,'signature':sig,'name':name})
        calls.append(('eth_call',[{'to':address,'data':'0x'+sel(sig)+args},hex(BLOCK)]))
    labels.extend([{'kind':'chain_id'},{'kind':'canonical_block'}])
    calls.extend([('eth_chainId',[]),('eth_getBlockByNumber',[hex(BLOCK),False])])
    record,rr=rpc(calls,'market_netting_final_checks_T')
    (ROOT/'data/eth/market_netting_final_checks_T.json').write_text(json.dumps({'target_timestamp':T,'block':BLOCK,'labels':labels,'responses':rr,'source':record},indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['consensus','issuer','alternatives','custody','lending','lp','curve','history','history_repair','consensus_schema','restaking_sources','restaking','kelp','final_checks'])
    args=parser.parse_args()
    {'consensus':consensus_probes,'issuer':lido_and_weth,'alternatives':alternatives,'custody':custody,'lending':lending_edges,'lp':primary_lp,'curve':curve_main,'history':lp_history,'history_repair':repair_history,'consensus_schema':correct_consensus_schema,'restaking_sources':restaking_sources,'restaking':restaking_edges,'kelp':kelp_nested,'final_checks':final_checks}[args.mode]()
