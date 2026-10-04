"""Read-only expansion of dollar funding venues at the existing research block.

Reserve totals contain all collateral types. They are never ETH-only debt or
carry capital. Holder discovery is separately dated; positions are reread at T.
"""
from __future__ import annotations
import concurrent.futures, datetime as dt, hashlib, json, re, sys, threading, time, urllib.parse, urllib.request
from pathlib import Path
from collect import ROOT, T, RPCS
sys.path.insert(0, str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel, enc_addr

RAW=ROOT/'raw/eth/funding-atlas-2026-10-04'
LOCK=threading.Lock()
STABLE={'USDC','USDCN','USDT','USDT0','DAI','GHO','LUSD','USDS','RLUSD','PYUSD','USDG','USDE','CRVUSD','SUSD','USDBC'}
ETH={'WETH','WSTETH','RETH','CBETH','WEETH','EZETH','RSETH','OSETH','ETHX','SFRXETH','FRXETH','WOETH','OETH','WRSETH','TETH','ANKRETH','METH','UNIETH'}
ETH.update({'ETH','WETHE','WBETH','EETH','SWETH'})
RPCS.update({'bsc':['https://bsc-rpc.publicnode.com','https://bsc.drpc.org'],'polygon':['https://polygon-bor-rpc.publicnode.com','https://polygon-mainnet.public.blastapi.io','https://polygon.drpc.org'],'avalanche':['https://avalanche-c-chain-rpc.publicnode.com','https://ava-mainnet.public.blastapi.io'],'mantle':['https://rpc.mantle.xyz','https://mantle-rpc.publicnode.com'],'sonic':['https://rpc.soniclabs.com','https://sonic-rpc.publicnode.com'],'linea':['https://rpc.linea.build','https://linea-rpc.publicnode.com'],'scroll':['https://rpc.scroll.io','https://scroll-rpc.publicnode.com'],'monad':['https://rpc.monad.xyz','https://monad-mainnet.drpc.org']})
RPCS['bsc'].insert(0,'https://bsc-mainnet.public.blastapi.io')
RPCS['avalanche'].insert(0,'https://api.avax.network/ext/bc/C/rpc')

def capture(key,url,payload=None):
    RAW.mkdir(parents=True,exist_ok=True)
    rec={'key':key,'url':url,'captured_at':dt.datetime.now(dt.timezone.utc).isoformat(),'target_timestamp':T,'method':'POST' if payload is not None else 'GET'}
    if payload is not None:rec['request']=payload
    try:
        req=urllib.request.Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers={'User-Agent':'ETH-Yield-Research/2.0','Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=25) as response:
            body=response.read();rec.update(status=response.status,source_date=response.headers.get('Date'))
        digest=hashlib.sha256(body).hexdigest();path=RAW/(key+'-'+digest[:16]+('.json' if body.lstrip().startswith((b'{',b'[')) else '.txt'))
        if not path.exists():path.write_bytes(body)
        rec.update(path=str(path.relative_to(ROOT)),sha256=digest,bytes=len(body))
        result=json.loads(body) if path.suffix=='.json' else body.decode(errors='replace')
    except Exception as error:rec['error']=repr(error);result=None
    rec['completed_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    with LOCK:
        with (RAW/'requests.jsonl').open('a') as out:out.write(json.dumps(rec)+'\n')
    return result

def words(value):
    if not value or value=='0x':return None
    return [int(value[i:i+64],16) for i in range(2,len(value),64)]

def call(to,sig,args='',tag=hex(26108081)):
    return ('eth_call',[{'to':to,'data':'0x'+sel(sig)+args},tag])

def rpc(chain,requests,key):
    providers=RPCS[chain]
    if chain=='arbitrum':providers=['https://arbitrum-one.public.blastapi.io','https://arbitrum-one-rpc.publicnode.com']+providers
    if chain=='base':providers=['https://base-mainnet.public.blastapi.io','https://base-rpc.publicnode.com']+providers
    if chain=='ethereum':providers=providers+['https://ethereum-rpc.publicnode.com']
    result={}
    for attempt,url in enumerate(providers):
        missing=[(i,row) for i,row in enumerate(requests,1) if i not in result or 'result' not in result[i]]
        if not missing:break
        size=(5 if len(requests)<=1600 else 25) if chain=='ethereum' else 4
        for start in range(0,len(missing),size):
            chunk=missing[start:start+size]
            payload=[{'jsonrpc':'2.0','id':i,'method':m,'params':p} for i,(m,p) in chunk]
            response=capture(key+'_p'+str(attempt)+'_b'+str(start//size),url,payload)
            if isinstance(response,list) and any(r.get('error',{}).get('code')==429 for r in response):
                time.sleep(1.5)
                response=capture(key+'_p'+str(attempt)+'_b'+str(start//size)+'_retry',url,payload)
            if chain=='ethereum':time.sleep(.6 if size==5 else .4)
            if not isinstance(response,list):continue
            for row in response:
                if 'id' in row and ('result' in row or row['id'] not in result):result[row['id']]=row
    return [result.get(i,{'id':i,'error':{'message':'No captured result'}}) for i in range(1,len(requests)+1)]

def config(value):
    return {'decimals':(value>>48)&255,'ltv':(value&65535)/10000,'liquidation_threshold':((value>>16)&65535)/10000,'liquidation_bonus':((value>>32)&65535)/10000,'active':bool(value&(1<<56)),'frozen':bool(value&(1<<57)),'borrowing_enabled':bool(value&(1<<58)),'paused':bool(value&(1<<60)),'reserve_factor':((value>>64)&65535)/10000,'borrow_cap_tokens':(value>>80)&((1<<36)-1),'supply_cap_tokens':(value>>116)&((1<<36)-1),'isolation_debt_ceiling_raw':(value>>212)&((1<<40)-1)}

def books():
    manifest=[json.loads(line) for line in (ROOT/'raw/eth/2026-10-02/requests.jsonl').read_text().splitlines()]
    blocks={row['chain']:row['block'] for row in json.loads((ROOT/'data/eth/snapshot_manifest.json').read_text())['chains']}
    venues=[]
    for chain in ['ethereum','base','arbitrum','optimism']:
        rec=next(r for r in reversed(manifest) if r['key']=='aave_addressbook_'+chain and r.get('path'))
        text=(ROOT/rec['path']).read_text()
        constants={k:v.lower() for k,v in re.findall(r'\b(\w+)\s*=\s*(?:I\w+\()?\s*(0x[a-fA-F0-9]{40})',text)}
        assets=[{'symbol':k.removesuffix('_UNDERLYING'),'address':v,'role':'dollar' if k.removesuffix('_UNDERLYING').upper() in STABLE else 'ETH collateral'} for k,v in constants.items() if k.endswith('_UNDERLYING') and k.removesuffix('_UNDERLYING').upper() in STABLE|ETH]
        venues.append({'id':'aave-'+chain,'name':'Aave V3','chain':chain,'pool':constants['POOL'],'oracle':constants['ORACLE'],'block':blocks[chain],'assets':assets,'identity_source':rec})
    extra=[('ethereum','EthereumLido'),('ethereum','EthereumEtherFi'),('bsc','BNB'),('polygon','Polygon'),('avalanche','Avalanche'),('mantle','Mantle'),('sonic','Sonic'),('linea','Linea'),('scroll','Scroll'),('monad','Monad')]
    def extra_book(item):
        chain,suffix=item
        url='https://raw.githubusercontent.com/bgd-labs/aave-address-book/main/src/AaveV3'+suffix+'.sol'
        text=capture('aave_extra_book_'+suffix,url)
        if not isinstance(text,str):return None
        constants={k:v.lower() for k,v in re.findall(r'\b(\w+)\s*=\s*(?:I\w+\()?\s*(0x[a-fA-F0-9]{40})',text)}
        if 'POOL' not in constants or 'ORACLE' not in constants:return None
        assets=[{'symbol':k.removesuffix('_UNDERLYING'),'address':v,'role':'dollar' if k.removesuffix('_UNDERLYING').upper() in STABLE else 'ETH collateral'} for k,v in constants.items() if k.endswith('_UNDERLYING') and k.removesuffix('_UNDERLYING').upper() in STABLE|ETH]
        if not any(a['role']=='ETH collateral' for a in assets):return None
        proof=None
        if chain in blocks:block=blocks[chain]
        else:
            found=capture('block_'+chain+'_T','https://coins.llama.fi/block/'+chain+'/'+str(T))
            if not isinstance(found,dict) or not found.get('height'):return None
            block=found['height']
            proof=None
            for adjust in range(12):
                br=rpc(chain,[('eth_chainId',[]),('eth_getBlockByNumber',[hex(block),False]),('eth_getBlockByNumber',[hex(block+1),False])],'block_boundary_'+chain+'_T_'+str(adjust))
                if not br[1].get('result') or not br[2].get('result'):break
                before=int(br[1]['result']['timestamp'],16);after=int(br[2]['result']['timestamp'],16)
                millis=all(r['result'].get('milliTimestamp') for r in br[1:])
                before_precise=int(br[1]['result']['milliTimestamp'],16)/1000 if millis else before
                after_precise=int(br[2]['result']['milliTimestamp'],16)/1000 if millis else after
                if before_precise<=T<after_precise:
                    proof={'chain_id':int(br[0]['result'],16),'block_timestamp':before,'next_block_timestamp':after,'precise_block_timestamp':before_precise,'precise_next_block_timestamp':after_precise,'timestamp_precision':'milliseconds' if millis else 'seconds','responses':br};break
                block+=-1 if before_precise>T else 1
            if not proof:return None
        return {'id':'aave-'+suffix.lower(),'name':'Aave V3 '+('Lido instance' if suffix=='EthereumLido' else 'ether.fi instance' if suffix=='EthereumEtherFi' else ''),'chain':chain,'pool':constants['POOL'],'oracle':constants['ORACLE'],'block':block,'block_boundary':proof,'assets':assets,'identity_source_url':url}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        venues.extend(v for v in executor.map(extra_book,extra) if v)
    return venues

def snapshot(repair_only=False):
    old_snapshot=json.loads((ROOT/'data/eth/funding_atlas_snapshot.json').read_text()) if repair_only else None
    venues=[v for v in old_snapshot['venues'] if not v.get('USD_oracle_verified')] if repair_only else books()
    spark={'id':'spark-ethereum','name':'SparkLend','chain':'ethereum','pool':'0xc13e21b648a5ee794902342038ff3adab66be987','block':26108081,'assets':[]}
    r=rpc('ethereum',[call(spark['pool'],'ADDRESSES_PROVIDER()'),call(spark['pool'],'getReservesList()')],'spark_identity_T') if not repair_only else [{},{}]
    provider='0x'+r[0]['result'][-40:] if r[0].get('result') else None
    data=words(r[1].get('result'))
    if provider and data:
        addresses=['0x'+format(x,'040x') for x in data[2:2+data[1]]]
        rr=rpc('ethereum',[call(provider,'getPriceOracle()')]+[call(a,'symbol()') for a in addresses],'spark_assets_T')
        spark['oracle']='0x'+rr[0]['result'][-40:]
        for address,res in zip(addresses,rr[1:]):
            raw=res.get('result','0x');symbol=''
            try:
                w=words(raw);symbol=bytes.fromhex(raw[2:])[64:64+w[1]].decode() if w and w[0]==32 else bytes.fromhex(raw[2:]).rstrip(b'\0').decode()
            except Exception:pass
            if symbol.upper() in STABLE|ETH:spark['assets'].append({'symbol':symbol,'address':address,'role':'dollar' if symbol.upper() in STABLE else 'ETH collateral'})
        spark['addresses_provider']=provider;venues.append(spark)
    def venue_capture(venue):
        chain=venue['chain'];tag=hex(venue['block'])
        identity=rpc(chain,[call(venue['pool'],'ADDRESSES_PROVIDER()','',tag),call(venue['oracle'],'BASE_CURRENCY_UNIT()','',tag),call(venue['oracle'],'BASE_CURRENCY()','',tag)],venue['id']+'_oracle_identity_T')
        provider='0x'+identity[0]['result'][-40:] if identity[0].get('result') else None
        provider_oracle=rpc(chain,[call(provider,'getPriceOracle()','',tag)],venue['id']+'_provider_oracle_T')[0] if provider else {}
        actual='0x'+provider_oracle['result'][-40:] if provider_oracle.get('result') else None
        unit=int(identity[1]['result'],16) if identity[1].get('result') else None
        currency='0x'+identity[2]['result'][-40:] if identity[2].get('result') else None
        venue['identity_verification']={'addresses_provider':provider,'oracle_at_T':actual,'addressbook_oracle_matches_T':actual==venue['oracle'],'base_currency_unit':unit,'base_currency':currency,'responses':identity,'provider_oracle_response':provider_oracle}
        venue['USD_oracle_verified']=unit==10**8 and currency=='0x'+'0'*40 and actual==venue['oracle']
        requests=[];labels=[]
        for asset in venue['assets']:
            for field,to,sig,args in [('reserve',venue['pool'],'getReserveData(address)',enc_addr(asset['address'])),('price',venue['oracle'],'getAssetPrice(address)',enc_addr(asset['address']))]:
                labels.append((asset['address'],field));requests.append(call(to,sig,args,tag))
        rr=rpc(chain,requests,venue['id']+'_reserves_T');mapped={}
        for label,res in zip(labels,rr):mapped.setdefault(label[0],{})[label[1]]=res
        extra=[];extra_labels=[]
        for asset in venue['assets']:
            asset['raw']=mapped[asset['address']];state=words(asset['raw']['reserve'].get('result'))
            if not state or len(state)!=15 or state[8]==0:
                asset['status']='not listed or incompatible view at T';continue
            asset.update(status='measured at T',configuration=config(state[0]),reserve_id=state[7],a_token='0x'+format(state[8],'040x'),variable_debt_token='0x'+format(state[10],'040x'),supply_apr=state[2]/1e27,borrow_apr=state[4]/1e27,last_reserve_update=state[6],oracle_price_USD=int(asset['raw']['price']['result'],16)/unit if asset['raw']['price'].get('result') and venue['USD_oracle_verified'] else None)
            for field,to,sig,args in [('supply',asset['a_token'],'totalSupply()',''),('debt',asset['variable_debt_token'],'totalSupply()',''),('cash',asset['address'],'balanceOf(address)',enc_addr(asset['a_token']))]:
                extra_labels.append((asset['address'],field));extra.append(call(to,sig,args,tag))
        er=rpc(chain,extra,venue['id']+'_quantities_T')
        for (address,field),res in zip(extra_labels,er):mapped[address][field]=res
        for asset in venue['assets']:
            if asset['status']!='measured at T':continue
            decimals=asset['configuration']['decimals']
            for field in ['supply','debt','cash']:
                val=mapped[asset['address']][field].get('result');asset[field+'_units']=int(val,16)/10**decimals if val else None
                asset[field+'_USD']=asset[field+'_units']*asset['oracle_price_USD'] if asset[field+'_units'] is not None and asset['oracle_price_USD'] is not None else None
            asset['cash_scope']='Physical underlying at aToken, not an executable borrowing or withdrawal guarantee. GHO is issuer-funded and needs separate facilitator limits.'
        print(venue['id'],len(venue['assets']),'assets',sum(x['status']=='measured at T' for x in venue['assets']),'measured',flush=True)
        return venue
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:venues=list(executor.map(venue_capture,venues))
    if repair_only:
        repaired={v['id']:v for v in venues};venues=[repaired.get(v['id'],v) for v in old_snapshot['venues']]
    out={'schema_version':1,'target_timestamp':T,'financial_snapshot_refreshed':False,'venues':venues,'reserve_debt_scope':'All collateral types. No reserve total is ETH-only debt or confirmed carry.','raw_manifest':str((RAW/'requests.jsonl').relative_to(ROOT))}
    (ROOT/'data/eth/funding_atlas_snapshot.json').write_text(json.dumps(out,indent=2)+'\n')

def history(repair_only=False):
    snapshot=json.loads((ROOT/'data/eth/funding_atlas_snapshot.json').read_text())
    category=json.loads((ROOT/'data/eth/carry_category_candidates.json').read_text())
    points=category['historical_price_references']
    selected=[]
    for venue in snapshot['venues']:
        if venue['chain']!='ethereum':continue
        for asset in venue['assets']:
            if asset['symbol'] in ['USDC','USDT','DAI','USDS','GHO'] and asset['status']=='measured at T':selected.append((venue,asset))
    previous=json.loads((ROOT/'data/eth/funding_atlas_history.json').read_text()) if repair_only else None
    requests=[];labels=[]
    if repair_only:
        venues={v['id']:v for v in snapshot['venues']}
        for row in previous['rows']:
            if row['status']!='not available':continue
            labels.append({k:row[k] for k in ['venue','asset','address','month','timestamp','block']})
            requests.append(call(venues[row['venue']]['pool'],'getReserveData(address)',enc_addr(row['address']),hex(row['block'])))
    else:
        for venue,asset in selected:
            for point in points:
                labels.append({'venue':venue['id'],'asset':asset['symbol'],'address':asset['address'],'month':point['month'],'timestamp':point['timestamp'],'block':point['block']})
                requests.append(call(venue['pool'],'getReserveData(address)',enc_addr(asset['address']),hex(point['block'])))
    rr=rpc('ethereum',requests,'ethereum_monthly_dollar_rates');rows=[]
    for label,res in zip(labels,rr):
        state=words(res.get('result'));row={**label,'response':res,'borrow_apr':None,'supply_apr':None,'status':'not available'}
        if state and len(state)==15 and state[8]:row.update(status='measured',borrow_apr=state[4]/1e27,supply_apr=state[2]/1e27,last_reserve_update=state[6])
        elif state and not state[8]:row['status']='not listed at dated block'
        rows.append(row)
    if repair_only:
        replacements={(r['venue'],r['asset'],r['timestamp']):r for r in rows}
        rows=[replacements.get((r['venue'],r['asset'],r['timestamp']),r) for r in previous['rows']]
    out={'schema_version':1,'target_timestamp':T,'scope':'Instantaneous stored reserve APR at each dated block. Not an average rate, realized borrowing cost or strategy return. Current contract census; earlier versions and delisted reserves can be absent.','rows':rows,'raw_manifest':str((RAW/'requests.jsonl').relative_to(ROOT))}
    (ROOT/'data/eth/funding_atlas_history.json').write_text(json.dumps(out,indent=2)+'\n')
    print('history',len(rows),'measured',sum(x['status']=='measured' for x in rows),flush=True)

def holders():
    snapshot=json.loads((ROOT/'data/eth/funding_atlas_snapshot.json').read_text())
    venues=[v for v in snapshot['venues'] if v['chain']=='ethereum']
    records=[]
    for venue in venues:
        for asset in venue['assets']:
            if asset['symbol'] not in ['USDC','USDT','DAI','USDS','GHO'] or asset['status']!='measured at T' or (asset.get('debt_USD') or 0)<1e6:continue
            token=asset['variable_debt_token'];url='https://eth.blockscout.com/api/v2/tokens/'+token+'/holders';pages=[]
            for page in range(4):
                result=capture(venue['id']+'_'+asset['symbol']+'_holders_'+str(page),url)
                if not isinstance(result,dict) or not isinstance(result.get('items'),list):break
                pages.append(result);items=result['items']
                last=int(items[-1]['value'])/10**asset['configuration']['decimals']*asset['oracle_price_USD'] if items else 0
                if last<1e6 or not result.get('next_page_params'):break
                url='https://eth.blockscout.com/api/v2/tokens/'+token+'/holders?'+urllib.parse.urlencode(result['next_page_params'])
            records.append({'venue':venue['id'],'asset':asset['symbol'],'debt_token':token,'holder_pages':pages,'discovery_time_scope':'Post-T indexer, not historical exhaustive holder list. Fixed-T balances are queried separately.'})
            print('holder pages',venue['id'],asset['symbol'],len(pages),flush=True)
    requests=[];labels=[];seen=set()
    for record in records:
        venue=next(v for v in venues if v['id']==record['venue'])
        for item in [i for page in record['holder_pages'] for i in page['items']]:
            who=item['address']['hash'].lower();key=(venue['id'],who)
            if key in seen:continue
            seen.add(key)
            for field,to,sig,args in [('account',venue['pool'],'getUserAccountData(address)',enc_addr(who)),('configuration',venue['pool'],'getUserConfiguration(address)',enc_addr(who)),('emode',venue['pool'],'getUserEMode(address)',enc_addr(who))]:
                labels.append({'venue':venue['id'],'borrower':who,'field':field});requests.append(call(to,sig,args))
            for asset in venue['assets']:
                if asset['status']!='measured at T':continue
                field='collateral' if asset['role']=='ETH collateral' else 'debt'
                token=asset['a_token'] if field=='collateral' else asset['variable_debt_token']
                labels.append({'venue':venue['id'],'borrower':who,'field':field,'asset':asset['symbol'],'asset_address':asset['address']});requests.append(call(token,'balanceOf(address)',enc_addr(who)))
    rr=rpc('ethereum',requests,'discovered_borrower_positions_T')
    out={'schema_version':1,'target_timestamp':T,'scope':'Current debt-token holder discovery with fixed-T debt, ETH-family aToken balances, collateral-use bitmap and account views. Presence of collateral and debt is not confirmed investment or carry. Historical exited holders can be absent.','discovery':records,'position_calls':[{'label':label,'response':res} for label,res in zip(labels,rr)],'raw_manifest':str((RAW/'requests.jsonl').relative_to(ROOT))}
    (ROOT/'data/eth/funding_atlas_borrowers.json').write_text(json.dumps(out,indent=2)+'\n')
    print('borrower pairs',len(seen),'fixed-T calls',len(rr),flush=True)

def repair_holders():
    # Fewer unresolved calls are cheap enough for small public archive batches.
    RPCS['ethereum']=['https://eth-mainnet.public.blastapi.io']+RPCS['ethereum']
    path=ROOT/'data/eth/funding_atlas_borrowers.json'
    data=json.loads(path.read_text());snapshot=json.loads((ROOT/'data/eth/funding_atlas_snapshot.json').read_text())
    venues={v['id']:v for v in snapshot['venues']};requests=[];indices=[]
    for i,record in enumerate(data['position_calls']):
        if 'result' in record['response']:continue
        label=record['label'];venue=venues[label['venue']];field=label['field'];who=label['borrower']
        if field in ['account','configuration','emode']:
            sig={'account':'getUserAccountData(address)','configuration':'getUserConfiguration(address)','emode':'getUserEMode(address)'}[field];to=venue['pool']
        else:
            asset=next(a for a in venue['assets'] if a['address']==label['asset_address']);to=asset['a_token'] if field=='collateral' else asset['variable_debt_token'];sig='balanceOf(address)'
        requests.append(call(to,sig,enc_addr(who)));indices.append(i)
    responses=rpc('ethereum',requests,'repair_discovered_borrower_positions_T')
    for i,response in zip(indices,responses):data['position_calls'][i]['response']=response
    data['repair_completed_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    path.write_text(json.dumps(data,indent=2)+'\n')
    print('repaired',len(indices),'returned',sum('result' in x['response'] for x in data['position_calls']),'of',len(data['position_calls']),flush=True)

def repair_quantities():
    path=ROOT/'data/eth/funding_atlas_snapshot.json';data=json.loads(path.read_text())
    for venue in data['venues']:
        requests=[];labels=[]
        for asset in venue['assets']:
            if asset['status']!='measured at T':continue
            for leg,to,sig,args in [('supply',asset['a_token'],'totalSupply()',''),('debt',asset['variable_debt_token'],'totalSupply()',''),('cash',asset['address'],'balanceOf(address)',enc_addr(asset['a_token'])),('price',venue['oracle'],'getAssetPrice(address)',enc_addr(asset['address']))]:
                if 'result' not in asset['raw'][leg]:labels.append((asset,leg));requests.append(call(to,sig,args,hex(venue['block'])))
        if not requests:continue
        replies=rpc(venue['chain'],requests,venue['id']+'_repair_quantities_T')
        for (asset,leg),reply in zip(labels,replies):
            if 'result' in reply:asset['raw'][leg]=reply
        for asset in venue['assets']:
            if asset['status']!='measured at T':continue
            price=asset['raw']['price'].get('result');unit=venue['identity_verification']['base_currency_unit']
            asset['oracle_price_USD']=int(price,16)/unit if price and venue['USD_oracle_verified'] else None
            for leg in ['supply','debt','cash']:
                result=asset['raw'][leg].get('result');asset[leg+'_units']=int(result,16)/10**asset['configuration']['decimals'] if result else None
                asset[leg+'_USD']=asset[leg+'_units']*asset['oracle_price_USD'] if asset[leg+'_units'] is not None and asset['oracle_price_USD'] is not None else None
        print('quantity repair',venue['id'],len(requests),flush=True)
    path.write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':
    {'snapshot':snapshot,'history':history,'repair_history':lambda:history(True),'holders':holders,'repair_holders':repair_holders,'repair_quantities':repair_quantities,'repair_venues':lambda:snapshot(True)}[sys.argv[1] if len(sys.argv)>1 else 'snapshot']()
