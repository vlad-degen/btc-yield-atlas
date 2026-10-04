"""Read-only public-source collector. Keeps immutable response files and provenance."""
from __future__ import annotations
import argparse, concurrent.futures, datetime as dt, hashlib, json, pathlib, threading, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
T = int(dt.datetime(2026, 10, 2, 23, 59, 59, tzinfo=dt.timezone.utc).timestamp())
RAW = ROOT / 'raw' / 'eth' / '2026-10-02'
LOCK = threading.Lock()
V = '0xf0bb20865277abd641a307ece5ee04e79073416c'
ACC = '0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198'
RPCS = {
 'ethereum': ['https://eth-mainnet.public.blastapi.io', 'https://gateway.tenderly.co/public/mainnet', 'https://eth.drpc.org'],
 'optimism': ['https://mainnet.optimism.io', 'https://optimism-mainnet.public.blastapi.io', 'https://optimism.drpc.org'],
 'base': ['https://mainnet.base.org', 'https://base.drpc.org'],
 'arbitrum': ['https://arb1.arbitrum.io/rpc', 'https://arbitrum.drpc.org'],
}

def stamp(): return dt.datetime.now(dt.timezone.utc).isoformat()

def request(key, url, payload=None):
    RAW.mkdir(parents=True, exist_ok=True)
    started = stamp()
    rec = {'key': key, 'url': url, 'method': 'POST' if payload is not None else 'GET', 'retrieved_at': started, 'target_timestamp': T}
    if payload is not None: rec['request'] = payload
    try:
        body = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=body, headers={'User-Agent': 'ETH-Yield-Research/1.0', **({'Content-Type': 'application/json'} if body else {})})
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read(); rec.update(status=r.status, content_type=r.headers.get('Content-Type'), source_date=r.headers.get('Date'))
        digest = hashlib.sha256(data).hexdigest()
        ext = 'json' if data.lstrip().startswith((b'{',b'[')) else 'txt'
        path = RAW / f'{key}-{digest[:16]}.{ext}'
        if not path.exists(): path.write_bytes(data)
        rec.update(sha256=digest, bytes=len(data), path=str(path.relative_to(ROOT)), completed_at=stamp())
        result = json.loads(data) if ext == 'json' else data.decode('utf-8', errors='replace')
    except Exception as e:
        rec.update(status=getattr(e, 'code', None), error=f'{type(e).__name__}: {str(e)[:240]}', completed_at=stamp()); result=None
        if isinstance(e, urllib.error.HTTPError):
            error_data=e.read(1048576)
            if error_data:
                digest=hashlib.sha256(error_data).hexdigest();error_path=RAW/f'{key}-error-{digest[:16]}.txt'
                if not error_path.exists():error_path.write_bytes(error_data)
                rec['error_response_path']=str(error_path.relative_to(ROOT));rec['error_response_excerpt']=error_data.decode('utf-8',errors='replace')[:500]
    with LOCK:
        with (RAW/'requests.jsonl').open('a') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\n')
        print(json.dumps({k:rec[k] for k in ['key','status','bytes','error'] if k in rec}), flush=True)
    return result

def bootstrap():
    jobs = [
      ('protocols','https://api.llama.fi/protocols'), ('yield_pools','https://yields.llama.fi/pools'),
      ('chains','https://api.llama.fi/v2/chains'),
      ('prices_T',f'https://coins.llama.fi/prices/historical/{T}/coingecko:ethereum'),
      ('etherfi_vault_doc','https://etherfi.gitbook.io/etherfi/products/liquid/live-vaults/liquid-eth-vault.md'),
      ('veda_doc','https://etherfi.gitbook.io/etherfi/products/liquid/veda-vault.md'),
      ('lido_doc','https://docs.lido.fi/contracts/wsteth/'),
      ('vault_eth_abi',f'https://eth.blockscout.com/api/v2/smart-contracts/{V}'),
      ('vault_op_abi',f'https://optimism.blockscout.com/api/v2/smart-contracts/{V}'),
      ('acc_eth_abi',f'https://eth.blockscout.com/api/v2/smart-contracts/{ACC}'),
      ('vault_eth_address',f'https://eth.blockscout.com/api/v2/addresses/{V}'),
      ('vault_eth_tokens',f'https://eth.blockscout.com/api/v2/addresses/{V}/token-balances'),
      ('vault_op_tokens',f'https://optimism.blockscout.com/api/v2/addresses/{V}/token-balances'),
      ('etherfi_live_html','https://www.ether.fi/app/cash/earn/liquid/eth-yield'),
    ] + [(f'block_{chain}_T', f'https://coins.llama.fi/block/{chain}/{T}') for chain in RPCS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(lambda j:request(*j),jobs))

def read_latest(key):
    rows=[json.loads(s) for s in (RAW/'requests.jsonl').read_text().splitlines()]
    row=next(r for r in reversed(rows) if r['key']==key and 'path' in r)
    path=ROOT/row['path'];content=path.read_text()
    return json.loads(content) if path.suffix=='.json' else content

def rpc_batch(chain, calls, key):
    payload=[{'jsonrpc':'2.0','id':i+1,'method':m,'params':p} for i,(m,p) in enumerate(calls)]
    for i,url in enumerate(RPCS[chain]):
        results=[]
        # Public providers differ in their accepted batch size.
        size=30 if chain=='ethereum' else 4
        for j in range(0,len(payload),size):
            result=request(f'{key}_provider{i}_batch{j//size}',url,payload[j:j+size])
            if not isinstance(result,list) or not any('result' in x for x in result): break
            results.extend(result)
        if len(results)==len(payload): return results
    return None

def pilot():
    for chain in ['ethereum','optimism']:
        b=read_latest(f'block_{chain}_T')['height']; tag=hex(b)
        contracts={'vault':V,'accountant':ACC,'teller':'0x9aa79c84b79816ab920bbce20f8f74557b514734','authority':'0x485bde66bb668a51f2372e34e45b1c6226798122','queue':'0x0d2df071207e18ca8638b4f04e98c53155ec2ce0','manager':'0xf9f7969c357ce6dfd7973098ea0d57173592bcca' if chain=='ethereum' else '0x227975088c28dbbb4b421c6d96781a53578f19a8'}
        calls=[('eth_chainId',[]),('eth_getBlockByNumber',[tag,False]),('eth_getBlockByNumber',[hex(b+1),False])]
        labels=['chainId','block','next_block']
        for name,address in contracts.items(): labels.append(name+'_code'); calls.append(('eth_getCode',[address,tag]))
        for name,target,selector in [('totalSupply',V,'0x18160ddd'),('decimals',V,'0x313ce567'),('name',V,'0x06fdde03'),('symbol',V,'0x95d89b41'),('getRate',ACC,'0x679aefce')]:
            labels.append(name); calls.append(('eth_call',[{'to':target,'data':selector},tag]))
        for name,pool in ([('aave','0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'),('spark','0xc13e21b648a5ee794902342038ff3adab66be987')] if chain=='ethereum' else [('aave','0x794a61358d6845594f94dc1db02a252b5b4814ad')]):
            labels.append(name+'_account'); calls.append(('eth_call',[{'to':pool,'data':'0xbf92857c'+V[2:].rjust(64,'0')},tag]))
        result=rpc_batch(chain,calls,f'pilot_{chain}_T')
        if result:
            out={'chain':chain,'requested_block':b,'target_timestamp':T,'labels':{str(i+1):s for i,s in enumerate(labels)},'responses':result}
            dest=ROOT/'data'/'eth';dest.mkdir(parents=True,exist_ok=True)
            (dest/f'pilot_{chain}_rpc.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('bootstrap'); sub.add_parser('pilot')
    sub.add_parser('discovery')
    sub.add_parser('protocols')
    sub.add_parser('morpho')
    sub.add_parser('balances')
    sub.add_parser('bundle')
    sub.add_parser('manifest')
    sub.add_parser('consensus')
    sub.add_parser('pilotmeta')
    sub.add_parser('ratelogs')
    get=sub.add_parser('get'); get.add_argument('key'); get.add_argument('url')
    a=ap.parse_args()
    if a.command=='bootstrap': bootstrap()
    elif a.command=='pilot': pilot()
    elif a.command=='discovery':
        jobs=[('protocol_etherfi_liquid','https://api.llama.fi/protocol/ether.fi-liquid'),('protocol_lido','https://api.llama.fi/protocol/lido'),('protocol_cian','https://api.llama.fi/protocol/cian-yield-layer'),('etherfi_adapter','https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/master/projects/etherfi-liquid/index.js'),('veda_api_docs','https://api.veda.tech/docs'),('veda_openapi','https://api.veda.tech/openapi.json')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda j:request(*j),jobs))
    elif a.command=='get': request(a.key,a.url)
    elif a.command=='protocols':
        candidates=json.loads((ROOT/'data'/'eth'/'protocol_candidates.json').read_text())
        existing={json.loads(s)['key'] for s in (RAW/'requests.jsonl').read_text().splitlines() if '"path"' in s}
        jobs=[('protocol_'+r['slug'].replace('.','_'), 'https://api.llama.fi/protocol/'+r['slug']) for r in candidates]
        jobs=[j for j in jobs if j[0] not in existing]
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(lambda j:request(*j),jobs))
    elif a.command=='morpho':
        q='''query($address:String!){userByAddress(address:$address,chainId:1){address marketPositions{market{marketId lltv oracle{address} irmAddress loanAsset{address symbol decimals} collateralAsset{address symbol decimals} state{borrowApy supplyApy utilization liquidityAssetsUsd}} state{collateral collateralUsd borrowShares borrowAssets borrowAssetsUsd supplyAssets supplyAssetsUsd}} vaultPositions{vault{address name}state{assets assetsUsd shares}}}}'''
        request('morpho_etherfi_current','https://api.morpho.org/graphql',{'query':q,'variables':{'address':V}})
        request('veda_etherfi_snapshot','https://api.veda.tech/v1/vaults/ethereum/'+V+'/metrics/snapshot/latest')
    elif a.command=='balances':
        for chain in ['ethereum','optimism']:
            rows=read_latest('vault_eth_tokens' if chain=='ethereum' else 'vault_op_tokens')
            tokens=[r['token'] for r in rows if r['token'].get('type')=='ERC-20' and int(r['value'])>0 and not any(x in (r['token'].get('symbol') or '').lower() for x in ['http','www.','visit','tablehockey','optibase'])]
            tag=hex(read_latest('block_'+chain+'_T')['height'])
            calls=[('eth_call',[{'to':t['address_hash'],'data':'0x70a08231'+V[2:].rjust(64,'0')},tag]) for t in tokens]
            labels=[{'symbol':t.get('symbol'),'address':t['address_hash'],'decimals':t.get('decimals')} for t in tokens]
            calls.append(('eth_getBalance',[V,tag]));labels.append({'symbol':'native ETH','address':None,'decimals':18})
            result=rpc_batch(chain,calls,'balances_'+chain+'_T')
            if result:(ROOT/'data'/'eth'/('balances_'+chain+'_T.json')).write_text(json.dumps({'chain':chain,'block':int(tag,16),'labels':labels,'responses':result},indent=2))
    elif a.command=='bundle':
        addresses=json.loads((RAW/'etherfi_bundle_observation.json').read_text())['addresses'][1:]
        jobs=[('bundle_tokens_'+a,'https://eth.blockscout.com/api/v2/addresses/'+a+'/token-balances') for a in addresses]
        jobs += [('bundle_abi_'+a,'https://eth.blockscout.com/api/v2/smart-contracts/'+a) for a in addresses[:4]]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda j:request(*j),jobs))
    elif a.command=='manifest':
        records=[]
        for chain in RPCS:
            if chain in ['ethereum','optimism']:
                d=json.loads((ROOT/'data'/'eth'/('pilot_'+chain+'_rpc.json')).read_text())
                results={d['labels'][str(r['id'])]:r.get('result') for r in d['responses']}
                block=results['block']; nxt=results['next_block'];cid=int(results['chainId'],16)
            else:
                height=read_latest('block_'+chain+'_T')['height']
                res=rpc_batch(chain,[('eth_chainId',[]),('eth_getBlockByNumber',[hex(height),False]),('eth_getBlockByNumber',[hex(height+1),False])],chain+'_block_check')
                if not res:records.append({'chain':chain,'status':'api_height_unverified'});continue
                r={x['id']:x.get('result') for x in res};cid=int(r[1],16);block=r[2];nxt=r[3]
                if not int(block['timestamp'],16)<=T<int(nxt['timestamp'],16):
                    # L2 APIs can return a nearest block after T; Arbitrum has
                    # multiple blocks within the same integer second.
                    near=rpc_batch(chain,[('eth_getBlockByNumber',[hex(h),False]) for h in range(height-8,height+9)],chain+'_block_neighbors')
                    candidates=[x['result'] for x in (near or []) if x.get('result')]
                    before=[x for x in candidates if int(x['timestamp'],16)<=T]
                    if before:
                        block=max(before,key=lambda x:int(x['number'],16))
                        nxt=next((x for x in candidates if int(x['number'],16)==int(block['number'],16)+1),nxt)
            verified=int(block['timestamp'],16)<=T<int(nxt['timestamp'],16)
            records.append({'chain':chain,'chain_id':cid,'block':int(block['number'],16),'block_hash':block['hash'],'block_timestamp':int(block['timestamp'],16),'next_timestamp':int(nxt['timestamp'],16),'last_block_at_or_before_T_verified':verified})
        manifest={'target_timestamp':T,'target_utc':dt.datetime.fromtimestamp(T,dt.timezone.utc).isoformat(),'created_at':stamp(),'chains':records,'price':read_latest('prices_T'),'price_timestamp_offset_seconds':read_latest('prices_T')['coins']['coingecko:ethereum']['timestamp']-T,'discovery_data_is_not_snapshot':True}
        (ROOT/'data'/'eth'/'snapshot_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
    elif a.command=='consensus':
        slot=(T-1606824023)//12;epoch=slot//32
        jobs=[('beacon_epoch_T','https://beaconcha.in/api/v1/epoch/'+str(epoch)),('beacon_header_T','https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/headers/'+str(slot)),('beacon_finality_T','https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/'+str(slot)+'/finality_checkpoints')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda j:request(*j),jobs))
    elif a.command=='pilotmeta':
        addresses={'queue':'0x0d2df071207e18ca8638b4f04e98c53155ec2ce0','authority':'0x485bde66bb668a51f2372e34e45b1c6226798122','teller':'0x9aa79c84b79816ab920bbce20f8f74557b514734','fluid_factory':'0x324c5dc1fc42c7a4d43d92df1eba58a54d13bf2d'}
        jobs=[(name+'_abi','https://eth.blockscout.com/api/v2/smart-contracts/'+addr) for name,addr in addresses.items()]
        jobs += [('accountant_logs_page1','https://eth.blockscout.com/api/v2/addresses/'+ACC+'/logs'),('fluid_deployments','https://raw.githubusercontent.com/Instadapp/fluid-contracts-public/main/deployments/mainnet.json'),('beacon_lodestar_header','https://lodestar-mainnet.chainsafe.io/eth/v1/beacon/headers/'+str((T-1606824023)//12))]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda j:request(*j),jobs))
    elif a.command=='ratelogs':
        from urllib.parse import urlencode
        page=read_latest('accountant_logs_page1');allrows=list(page.get('items',[]));n=1
        while page.get('next_page_params') and n<200:
            n+=1
            page=request('accountant_logs_page'+str(n),'https://eth.blockscout.com/api/v2/addresses/'+ACC+'/logs?'+urlencode(page['next_page_params']))
            if not page:break
            allrows.extend(page.get('items',[]))
        (ROOT/'data'/'eth'/'accountant_logs.json').write_text(json.dumps({'items':allrows,'pages':n,'complete':isinstance(page,dict) and not page.get('next_page_params')},indent=2))
        print('Accountant logs',len(allrows),'pages',n)
