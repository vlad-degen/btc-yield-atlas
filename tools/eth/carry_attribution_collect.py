"""Read-only public historical income captures; no canonical source is rewritten."""
from __future__ import annotations
import concurrent.futures, datetime as dt, hashlib, json, sys
from pathlib import Path
import carry_economics_collect as c
from carry_economics_collect import call, enc_addr, enc_uint, words
from keccak_lib import keccak

ROOT=c.ROOT; DATA=ROOT/'data/eth'; RAW=ROOT/'raw/eth/research-closure-2026-10-04/income'
c.RAW=RAW
T=c.T; BLOCK=26108081; START=19000000
MORPHO=c.MORPHO; MAIN=c.V; LOAN=c.LOAN
DRONE='0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c'
POSITION='0x528353aea55dbbbf18be26d5726afe6585898dc5'
ACCOUNTS=[MAIN,LOAN,DRONE,POSITION]
DESTINATIONS=[{'id':'rlusd-v2','address':'0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf','asset':'0x8292bb45bf1ee4d140127049757c2e0ff06317ed','symbol':'RLUSD','decimals':18}, {'id':'pyusd-prime-v2','address':'0xc21b08c16458202593d4d9b26b9984ee67b38bbd','asset':'0x6c3ea9036406852006290770bedfcaba0e23a0e8','symbol':'PYUSD','decimals':6}, {'id':'stcusd','address':'0x88887be419578051ff9f4eb6c858a951921d8888','asset':'0xcccc62962d17b8914c62d74ffb843d73b2a3cccc','symbol':'cUSD','decimals':18}, {'id':'prime','address':'0x19ebb35279a16207ec4ba82799cc64715065f7f6','asset':'0x6ad038ca6c04e885630851278ca0a856ad9a66cc','symbol':'PRIME-asset','decimals':6}]
EVENTS={'Transfer':'Transfer(address,address,uint256)','Deposit':'Deposit(address,address,uint256,uint256)','Withdraw':'Withdraw(address,address,address,uint256,uint256)','Borrow':'Borrow(bytes32,address,address,address,uint256,uint256)','Repay':'Repay(bytes32,address,address,uint256,uint256)','Liquidate':'Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)','AccrueInterest':'AccrueInterest(bytes32,uint256,uint256,uint256)','VaultAccrueInterest':'AccrueInterest(uint256,uint256,uint256,uint256)'}
TOPIC={k:'0x'+keccak(v.encode()).hex() for k,v in EVENTS.items()}
PROVIDERS=['https://gateway.tenderly.co/public/mainnet','https://eth-mainnet.public.blastapi.io','https://eth.drpc.org']

def read(name):return json.loads((DATA/(name+'.json')).read_text())
def raw_request(key,method,params):
    payload={'jsonrpc':'2.0','id':1,'method':method,'params':params}
    if (RAW/'requests.jsonl').exists():
        for line in reversed((RAW/'requests.jsonl').read_text().splitlines()):
            r=json.loads(line)
            if r.get('request')==payload and r.get('path'):
                result=json.loads((ROOT/r['path']).read_text())
                if isinstance(result,dict) and 'result' in result:return result
    last=None
    for index,url in enumerate(PROVIDERS):
        result=c.capture(key+'_provider'+str(index),url,payload)
        if isinstance(result,dict) and 'result' in result:return result
        last=result
    return last or {}

def logs(key,address,topics,start=START,end=BLOCK):
    params={'address':address,'fromBlock':hex(start),'toBlock':hex(end),'topics':topics}
    if address is None:params.pop('address')
    r=raw_request(key,'eth_getLogs',[params])
    if isinstance(r.get('result'),list):
        result=r['result']
        # A provider returns an explicit error for a truncated range. Accept
        # only successful arrays, and independently reconcile share/debt state.
        return {'key':key,'start':start,'end':end,'topics':topics,'complete':True,'logs':result}
    if end-start>1000:
        mid=(start+end)//2
        a=logs(key+'_a',address,topics,start,mid);b=logs(key+'_b',address,topics,mid+1,end)
        return {'key':key,'start':start,'end':end,'topics':topics,'complete':a['complete'] and b['complete'],'logs':a['logs']+b['logs'],'subranges':[{'start':a['start'],'end':a['end'],'complete':a['complete']},{'start':b['start'],'end':b['end'],'complete':b['complete']}]}
    return {'key':key,'start':start,'end':end,'topics':topics,'complete':False,'logs':[],'error':r.get('error')}

def collect():
    accounts=['0x'+enc_addr(a) for a in ACCOUNTS]
    jobs=[('morpho_borrow',MORPHO,[TOPIC['Borrow'],None,accounts]),('morpho_repay',MORPHO,[TOPIC['Repay'],None,None,accounts]),('morpho_liquidate',MORPHO,[TOPIC['Liquidate'],None,None,accounts])]
    for d in DESTINATIONS:
        for label,topics in [('deposit',[TOPIC['Deposit'],None,accounts]),('withdraw',[TOPIC['Withdraw'],None,None,accounts]),('share_in',[TOPIC['Transfer'],None,accounts]),('share_out',[TOPIC['Transfer'],accounts])]:jobs.append((d['id']+'_'+label,d['address'],topics))
        if 'v2' in d['id']:jobs.append((d['id']+'_accrual',d['address'],[TOPIC['VaultAccrueInterest']]))
    captured=[]
    def worker(job):
        r=logs(*job);print(job[0],len(r['logs']),r['complete'],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:captured=list(pool.map(worker,jobs))
    payload={'schema_version':1,'snapshot_timestamp':T,'block':BLOCK,'start_block':START,'captured_at':dt.datetime.now(dt.timezone.utc).isoformat(),'accounts':ACCOUNTS,'destinations':DESTINATIONS,'event_signatures':EVENTS,'event_topics':TOPIC,'log_groups':captured,'raw_manifest':str((RAW/'requests.jsonl').relative_to(ROOT))}
    (DATA/'carry_attribution_rpc.json').write_text(json.dumps(payload,indent=2))
    print('Captured groups',len(captured),flush=True)

def states():
    raw=read('carry_attribution_rpc');ids=sorted({r['topics'][1] for g in raw['log_groups'] if g['key'].startswith('morpho_') for r in g['logs']})
    labels=[];calls=[];tag=hex(BLOCK)
    for market in ids:
        for name,sig,args in [('params','idToMarketParams(bytes32)',market[2:]),('market','market(bytes32)',market[2:])]:labels.append({'kind':'market','id':market,'field':name});calls.append(call(MORPHO,sig,args,tag))
        for account in ACCOUNTS:labels.append({'kind':'market','id':market,'field':'position','account':account});calls.append(call(MORPHO,'position(bytes32,address)',market[2:]+enc_addr(account),tag))
    for d in DESTINATIONS:
        for sig in ['asset()','decimals()','totalAssets()','totalSupply()']:
            labels.append({'kind':'destination','id':d['id'],'field':sig});calls.append(call(d['address'],sig,'',tag))
        for account in ACCOUNTS:
            labels.append({'kind':'destination','id':d['id'],'field':'balanceOf(address)','account':account});calls.append(call(d['address'],'balanceOf(address)',enc_addr(account),tag))
    result=c.rpc('ethereum',calls,'income_states_T');byid={r['id']:r for r in result};named=[{**l,'response':byid.get(i+1,{})} for i,l in enumerate(labels)]
    follow=[];flabels=[]
    for l in named:
        w=words(l['response'].get('result'))
        if l['kind']=='market' and l['field']=='params' and w:
            m=next(x for x in named if x['kind']=='market' and x['id']==l['id'] and x['field']=='market');mw=words(m['response'].get('result'));loan='0x'+format(w[0],'040x')
            flabels.append({'kind':'market','id':l['id'],'field':'borrow_rate'});follow.append(call('0x'+format(w[3],'040x'),'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',''.join(enc_uint(x) for x in w+mw),tag))
            for sig in ['symbol()','decimals()']:flabels.append({'kind':'asset','address':loan,'field':sig});follow.append(call(loan,sig,'',tag))
        if l['kind']=='destination' and l['field']=='balanceOf(address)' and w:
            d=next(d for d in DESTINATIONS if d['id']==l['id']);flabels.append({'kind':'destination','id':l['id'],'field':'convertToAssets','account':l['account']});follow.append(call(d['address'],'convertToAssets(uint256)',enc_uint(w[0]),tag))
    fres=c.rpc('ethereum',follow,'income_states_T_follow');fby={r['id']:r for r in fres};named += [{**l,'response':fby.get(i+1,{})} for i,l in enumerate(flabels)]
    blocks=sorted({int(r['blockNumber'],16) for g in raw['log_groups'] if not g['key'].endswith('_accrual') for r in g['logs']})
    headercalls=[('eth_getBlockByNumber',[hex(b),False]) for b in blocks];headers=c.rpc('ethereum',headercalls,'income_event_blocks') if blocks else []
    headerrows=[{'block':b,'response':{r['id']:r for r in headers}.get(i+1,{})} for i,b in enumerate(blocks)]
    (DATA/'carry_attribution_states.json').write_text(json.dumps({'snapshot_timestamp':T,'block':BLOCK,'records':named,'event_blocks':headerrows},indent=2))
    print('State rows',len(named),'event blocks',len(headerrows),flush=True)

def flows():
    accounts=['0x'+enc_addr(a) for a in ACCOUNTS]
    merkl='0x3ef3d8ba38ebe18db133cec108f4d14ce00dd9ae'
    jobs=[]
    for d in DESTINATIONS[:3]:
        jobs += [(d['id']+'_asset_in',d['asset'],[TOPIC['Transfer'],None,accounts]),(d['id']+'_asset_out',d['asset'],[TOPIC['Transfer'],accounts])]
    jobs.append(('merkl_cash_reward_transfers',None,[TOPIC['Transfer'],'0x'+enc_addr(merkl),accounts]))
    def worker(j):
        r=logs(*j);print(j[0],len(r['logs']),r['complete'],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:groups=list(pool.map(worker,jobs))
    rpc=read('carry_attribution_rpc')
    txs=sorted({r['transactionHash'] for g in rpc['log_groups'] if not g['key'].endswith('_accrual') for r in g['logs']}|{r['transactionHash'] for g in groups if g['key']=='merkl_cash_reward_transfers' for r in g['logs']})
    rr=c.rpc('ethereum',[('eth_getTransactionReceipt',[tx]) for tx in txs],'income_receipts');byid={r['id']:r for r in rr}
    docs=[('morpho_rewards_claim_docs','https://docs.morpho.org/developers/rewards/tutorials/claim-rewards/'),('merkl_distributor_source','https://eth.blockscout.com/api/v2/smart-contracts/'+merkl),('rlusd_destination_source','https://eth.blockscout.com/api/v2/smart-contracts/'+DESTINATIONS[0]['address']),('pyusd_destination_source','https://eth.blockscout.com/api/v2/smart-contracts/'+DESTINATIONS[1]['address'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda item:c.capture(*item),docs))
    (DATA/'carry_attribution_flows.json').write_text(json.dumps({'snapshot_timestamp':T,'block':BLOCK,'log_groups':groups,'receipts':[{'transaction_hash':tx,'response':byid.get(i+1,{})} for i,tx in enumerate(txs)],'merkl_distributor':merkl,'merkl_address_source':'https://docs.morpho.org/developers/rewards/tutorials/claim-rewards/','merkl_scope':'Transfer events from the documented Merkl distributor to the four tracked accounts, at blocks no later than T. Other distributors, redirected beneficiaries, unclaimed rewards and offchain payouts are not inferred.'},indent=2))
    print('Transfer groups',len(groups),'receipts',len(rr),flush=True)

def window():
    raw=read('carry_attribution_rpc');state=read('carry_attribution_states');flows=read('carry_attribution_flows')
    start=min(int(r['blockNumber'],16) for g in raw['log_groups'] if g['key']=='rlusd-v2_deposit' for r in g['logs'])-1
    tag=hex(start);ids=sorted({r['id'] for r in state['records'] if r['kind']=='market'})
    labels=[];calls=[]
    for mid in ids:
        labels.append({'kind':'market','id':mid,'field':'market'});calls.append(call(MORPHO,'market(bytes32)',mid[2:],tag))
        for a in ACCOUNTS:labels.append({'kind':'market','id':mid,'field':'position','account':a});calls.append(call(MORPHO,'position(bytes32,address)',mid[2:]+enc_addr(a),tag))
    for d in DESTINATIONS:
        for a in ACCOUNTS:labels.append({'kind':'destination','id':d['id'],'field':'balanceOf(address)','account':a});calls.append(call(d['address'],'balanceOf(address)',enc_addr(a),tag))
    result=c.rpc('ethereum',calls,'income_common_start_states');byid={r['id']:r for r in result};records=[{**l,'response':byid.get(i+1,{})} for i,l in enumerate(labels)]
    follow=[];flabels=[]
    for row in records:
        w=words(row['response'].get('result'))
        if row['kind']=='market' and row['field']=='market' and w and w[4]:
            params=words(next(x['response']['result'] for x in state['records'] if x['kind']=='market' and x['id']==row['id'] and x['field']=='params'))
            flabels.append({'kind':'market','id':row['id'],'field':'borrow_rate'});follow.append(call('0x'+format(params[3],'040x'),'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',''.join(enc_uint(x) for x in params+w),tag))
        if row['kind']=='destination' and row['field']=='balanceOf(address)' and w:
            d=next(d for d in DESTINATIONS if d['id']==row['id']);flabels.append({'kind':'destination','id':row['id'],'field':'convertToAssets','account':row['account']});follow.append(call(d['address'],'convertToAssets(uint256)',enc_uint(w[0]),tag))
    rr=c.rpc('ethereum',follow,'income_common_start_follow');byid={r['id']:r for r in rr};records += [{**l,'response':byid.get(i+1,{})} for i,l in enumerate(flabels)]
    merkl=next(g for g in flows['log_groups'] if g['key']=='merkl_cash_reward_transfers')['logs'];blocks=sorted({int(r['blockNumber'],16) for r in merkl}|{start,start+1,BLOCK})
    rr=c.rpc('ethereum',[('eth_getBlockByNumber',[hex(b),False]) for b in blocks],'income_window_reward_blocks');byid={r['id']:r for r in rr};headers=[{'block':b,'response':byid.get(i+1,{})} for i,b in enumerate(blocks)]
    tokens=sorted({r['address'].lower() for r in merkl});labelsmeta=[];callsmeta=[]
    for token in tokens:
        for sig in ['symbol()','decimals()']:labelsmeta.append({'address':token,'field':sig});callsmeta.append(call(token,sig,'',hex(BLOCK)))
    rr=c.rpc('ethereum',callsmeta,'income_reward_metadata');byid={r['id']:r for r in rr};metadata=[{**l,'response':byid.get(i+1,{})} for i,l in enumerate(labelsmeta)]
    code=c.rpc('ethereum',[('eth_getCode',[a,hex(START)]) for a in ACCOUNTS],'income_accounts_start_code')
    (DATA/'carry_attribution_window_states.json').write_text(json.dumps({'snapshot_timestamp':T,'start_block':start,'end_block':BLOCK,'start_convention':'Last block before first tracked RLUSD V2 deposit; common window for every included loan, claim and reward payment.','records':records,'blocks':headers,'reward_token_metadata':metadata,'code_at_capture_start':[{'address':a,'response':r} for a,r in zip(ACCOUNTS,code)]},indent=2))
    print('Common window blocks',start,BLOCK,'records',len(records),'reward blocks',len(headers),flush=True)

def recycling():
    window=read('carry_attribution_window_states');start=window['start_block'];accounts=['0x'+enc_addr(a) for a in ACCOUNTS]
    targets=[{'destination_id':'rlusd-v2','market_id':'0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4','adapter':'0x3c6eab22cfc03fc32ad1bf836f2f886a5015dfff'}, {'destination_id':'pyusd-prime-v2','market_id':'0x41c41d0c9aadbf4751f5ee215ed5a16954a4b34e1b70fca5393d4b08858fa3fa','adapter':'0x93d6393e66b56449b7926b9abfeb37606732de89'}]
    signatures={'Supply':'Supply(bytes32,address,address,uint256,uint256)','MorphoWithdraw':'Withdraw(bytes32,address,address,address,uint256,uint256)','SetFee':'SetFee(bytes32,uint256)'}
    topics={**TOPIC,**{k:'0x'+keccak(v.encode()).hex() for k,v in signatures.items()}}
    eventnames=['Supply','MorphoWithdraw','Borrow','Repay','Liquidate','AccrueInterest','SetFee']
    jobs=[('own_credit_market_events',MORPHO,[[topics[e] for e in eventnames],[t['market_id'] for t in targets]])]
    for t in targets:
        d=next(d for d in DESTINATIONS if d['id']==t['destination_id']);jobs.append((t['destination_id']+'_all_share_transfers',d['address'],[TOPIC['Transfer']]))
    groups=[]
    def worker(j):
        r=logs(*j,start=start+1);print(j[0],len(r['logs']),r['complete'],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:groups=list(pool.map(worker,jobs))
    labels=[];calls=[]
    for t in targets:
        labels.append({'destination_id':t['destination_id'],'market_id':t['market_id'],'field':'adapter_position'});calls.append(call(MORPHO,'position(bytes32,address)',t['market_id'][2:]+enc_addr(t['adapter']),hex(start)))
        d=next(d for d in DESTINATIONS if d['id']==t['destination_id']);labels.append({'destination_id':t['destination_id'],'field':'vault_total_supply'});calls.append(call(d['address'],'totalSupply()','',hex(start)))
    labels.append({'field':'morpho_fee_recipient'});calls.append(call(MORPHO,'feeRecipient()','',hex(BLOCK)))
    rr=c.rpc('ethereum',calls,'income_recycling_opening_states');byid={r['id']:r for r in rr}
    (DATA/'carry_attribution_recycling_rpc.json').write_text(json.dumps({'snapshot_timestamp':T,'start_block':start,'end_block':BLOCK,'targets':targets,'event_signatures':{**EVENTS,**signatures},'event_topics':topics,'log_groups':groups,'opening_records':[{**l,'response':byid.get(i+1,{})} for i,l in enumerate(labels)]},indent=2))
    print('Own-credit event capture complete',flush=True)

def organic():
    jobs=[]
    for d in DESTINATIONS[:2]:
        jobs += [(d['id']+'_all_deposits',d['address'],[TOPIC['Deposit']]),(d['id']+'_underlying_in',d['asset'],[TOPIC['Transfer'],None,'0x'+enc_addr(d['address'])]),(d['id']+'_adapter_history',d['address'],[['0x'+keccak(s.encode()).hex() for s in ['AddAdapter(address)','RemoveAdapter(address)']]])]
    def worker(j):
        r=logs(*j);print(j[0],len(r['logs']),r['complete'],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:groups=list(pool.map(worker,jobs))
    # Same-block staking and Ethereum share-value comparisons, with no current
    # annual rate extrapolated over the common window.
    window=read('carry_attribution_window_states');labels=[];calls=[]
    for period,block in [('start',window['start_block']),('end',BLOCK)]:
        for name,target,sig in [('stETH','0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','stEthPerToken()'),('weETH','0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','getRate()'),('LiquidETH_Ethereum','0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198','getRate()')]:
            labels.append({'period':period,'block':block,'name':name});calls.append(call(target,sig,'',hex(block)))
    rr=c.rpc('ethereum',calls,'income_matched_benchmarks');byid={r['id']:r for r in rr}
    (DATA/'carry_attribution_organic_rpc.json').write_text(json.dumps({'snapshot_timestamp':T,'log_groups':groups,'benchmarks':[{**l,'response':byid.get(i+1,{})} for i,l in enumerate(labels)]},indent=2))
    print('Organic-source and matched benchmark captures complete',flush=True)

def closure_proof():
    # Individual requests retain explicit failures instead of silently dropping
    # an unavailable archive batch. This also verifies native PRIME asset units.
    jobs=[('opening_code_'+a,'eth_getCode',[a,hex(START)]) for a in ACCOUNTS]
    for sig in ['symbol()','decimals()']:
        method,params=call(DESTINATIONS[3]['asset'],sig,'',hex(BLOCK))
        jobs.append(('prime_underlying_'+sig,method,params))
    jobs.append(('historical_rlusd_adapter_source','GET',['https://eth.blockscout.com/api/v2/smart-contracts/0x5705f2c343dfc4600c77cbcf6b7a7b5eb579ba01']))
    for target in read('carry_attribution_recycling_rpc')['targets']:
        method,params=call(MORPHO,'position(bytes32,address)',target['market_id'][2:]+enc_addr(target['adapter']),hex(BLOCK))
        jobs.append((target['destination_id']+'_ending_adapter_position',method,params))
    def worker(item):
        key,method,params=item
        response=c.capture(key,params[0]) if method=='GET' else raw_request(key,method,params)
        print(key,'ok' if response.get('result') is not None or response.get('source_code') else 'unavailable',flush=True)
        return {'key':key,'method':method,'params':params,'response':response}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(worker,jobs))
    (DATA/'carry_attribution_closure_proof.json').write_text(json.dumps({'snapshot_timestamp':T,'records':rows},indent=2))

def tranches():
    ledger=read('carry_attribution_ledger');labels=[];calls=[]
    selected=[]
    for d in ledger['destination_events']:
        if d['event']!='deposit':continue
        # Only label a destination cohort still held when there is no later
        # outgoing share transfer or withdrawal from the tracked holder.
        later=[r for r in ledger['destination_events'] if r['destination_id']==d['destination_id'] and r['account']==d['account'] and r['event']=='withdraw' and (r['block'],r['log_index'])>(d['block'],d['log_index'])]
        borrows=[r for r in ledger['borrowing_events'] if r['event']=='borrow' and r['transaction_hash']==d['transaction_hash']]
        if later or not borrows:continue
        debts=[r for r in ledger['borrowing_ledgers'] if r['id'] in {b['ledger_id'] for b in borrows}]
        if any(r['repay_count'] for r in debts):continue
        selected.append(d)
        labels.append({'destination_id':d['destination_id'],'account':d['account'],'transaction_hash':d['transaction_hash'],'deposit_shares_raw':d['shares_raw'],'deposit_assets_raw':d['assets_raw'],'field':'deposit_cohort_convertToAssets_T'})
        calls.append(call(d['vault'],'convertToAssets(uint256)',enc_uint(int(d['shares_raw'])),hex(BLOCK)))
    events=read('etherfi_parameter_events')
    for e in events:
        if e['event']=='FeesClaimed' and ledger['common_window']['start_timestamp']<e['timestamp']<=T:
            labels.append({'transaction_hash':e['transaction_hash'],'field':'outer_fee_claim_receipt'});calls.append(('eth_getTransactionReceipt',[e['transaction_hash']]))
    rr=c.rpc('ethereum',calls,'income_held_cohort_T_and_fee_receipts');byid={r['id']:r for r in rr}
    (DATA/'carry_attribution_tranche_rpc.json').write_text(json.dumps({'snapshot_timestamp':T,'block':BLOCK,'records':[{**l,'response':byid.get(i+1,{})} for i,l in enumerate(labels)]},indent=2))
    print('Held cohort claims',len(selected),'total calls',len(calls),flush=True)

if __name__=='__main__':tranches() if '--tranches' in sys.argv else closure_proof() if '--proof' in sys.argv else organic() if '--organic' in sys.argv else recycling() if '--recycling' in sys.argv else window() if '--window' in sys.argv else flows() if '--flows' in sys.argv else states() if '--states' in sys.argv else collect()
