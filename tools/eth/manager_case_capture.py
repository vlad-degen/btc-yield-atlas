"""Read a further material managed ETH product at the frozen research dates."""
import json,sys
from pathlib import Path
import funding_atlas_capture as cap
from keccak_lib import keccak
ROOT=Path(__file__).resolve().parents[2];cap.RAW=ROOT/'raw/eth/manager-case-2026-10-04'
HG='0xc824a08db624942c5e5f330d56530cd1598859fd';RS='0xa1290d69c65a6fe4df752f95823fae25cb99e5a7'
def run():
    source=cap.capture('hg_verified_contract','https://eth.blockscout.com/api/v2/smart-contracts/'+HG)
    cap.capture('kernel_primary_docs','https://kerneldao.gitbook.io/kernel-dao/restaking-products/gain')
    periods=[p for p in json.loads((ROOT/'data/eth/carry_category_candidates.json').read_text())['historical_price_references'] if p['month'] in ['2026-04','2026-06','2026-09','snapshot_T']]
    calls=[];labels=[]
    signatures=['totalAssets()','totalSupply()','asset()','convertToAssets(uint256)','depositsPaused()','withdrawalsPaused()','managementFeePercent()','withdrawalFee()','totalCollectableFees()','owner()','settlementAccount()','loansOperator()','loansDeployerAddress()','maxSupply()','maxDepositAmount()']
    if isinstance(source,dict):
        abi=source.get('abi') or []
        signatures+=[''+a['name']+'()' for a in abi if a.get('type')=='function' and not a.get('inputs') and any(w in a['name'].lower() for w in ['loan','pause','fee'])]
    signatures=list(dict.fromkeys(signatures))
    for point in periods:
        for sig in signatures:
            labels.append({'month':point['month'],'timestamp':point['timestamp'],'block':point['block'],'signature':sig})
            calls.append(cap.call(HG,sig,format(10**18,'064x') if sig=='convertToAssets(uint256)' else '',hex(point['block'])))
        labels.append({'month':point['month'],'timestamp':point['timestamp'],'block':point['block'],'signature':'rsETH buffer balance'})
        calls.append(cap.call(RS,'balanceOf(address)',cap.enc_addr(HG),hex(point['block'])))
        labels.append({'month':point['month'],'timestamp':point['timestamp'],'block':point['block'],'signature':'rsETH config'})
        calls.append(cap.call(RS,'lrtConfig()','',hex(point['block'])))
    replies=cap.rpc('ethereum',calls,'hgeth_state_and_history');rows=[{'label':l,'response':r} for l,r in zip(labels,replies)]
    cfgs=[r for r in rows if r['label']['signature']=='rsETH config' and r['response'].get('result')]
    oracle_reads=cap.rpc('ethereum',[cap.call('0x'+r['response']['result'][-40:],'getContract(bytes32)',keccak(b'LRT_ORACLE').hex(),hex(r['label']['block'])) for r in cfgs],'hgeth_rsETH_oracle_identity')
    prices=cap.rpc('ethereum',[cap.call('0x'+r['result'][-40:],'rsETHPrice()','',hex(c['label']['block'])) for c,r in zip(cfgs,oracle_reads) if r.get('result')],'hgeth_rsETH_conversion')
    oracle_rows=[{'label':c['label'],'oracle':'0x'+o['result'][-40:],'price_response':p} for c,o,p in zip(cfgs,oracle_reads,prices) if o.get('result')]
    implementation_slot='0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc';tag=hex(26108081)
    owner='0x'+next(r['response']['result'] for r in rows if r['label']['month']=='snapshot_T' and r['label']['signature']=='owner()')[-40:]
    control=cap.rpc('ethereum',[('eth_getStorageAt',[HG,implementation_slot,tag]),cap.call(owner,'getThreshold()','',tag),cap.call(owner,'getOwners()','',tag),('eth_getCode',[HG,tag])],'hgeth_control_T')
    if control[0].get('result'):cap.capture('hg_implementation_source','https://eth.blockscout.com/api/v2/smart-contracts/0x'+control[0]['result'][-40:])
    implementation='0x'+control[0]['result'][-40:]
    extra=cap.rpc('ethereum',[cap.call(HG,'getTotalLoansDeployed()','',tag),cap.call(HG,'globalLoansAmount()','',tag),cap.call(HG,'maxRedeem(address)',cap.enc_addr(owner),tag),cap.call(HG,'maxWithdraw(address)',cap.enc_addr(owner),tag),('eth_getCode',[implementation,tag])],'hgeth_loans_exit_and_implementation_T')
    count=int(extra[0]['result'],16) if extra[0].get('result') else 0
    loans=cap.rpc('ethereum',[cap.call(HG,'loansDeployed(uint256)',format(i,'064x'),tag) for i in range(min(count,500))],'hgeth_loan_registry_T')
    out={'snapshot_timestamp':cap.T,'address':HG,'asset':RS,'state':rows,'oracle_history':oracle_rows,'control':control,'raw_manifest':str((cap.RAW/'requests.jsonl').relative_to(ROOT))}
    out['loan_and_exit_views']=extra;out['loan_registry']=[{'index':i,'response':r} for i,r in enumerate(loans)];out['registry_query_limit']=500
    signatures=['gainAdapter()','globalLiabilityShares()','maxWithdrawalAmount()','lagDuration()','liquidationHour()','feesCollector()']
    views=cap.rpc('ethereum',[cap.call(HG,sig,'',tag) for sig in signatures],'hg_adapter_and_exit_terms_T')
    out['additional_views']=[{'signature':sig,'response':r} for sig,r in zip(signatures,views)]
    if views[0].get('result'):
        adapter='0x'+views[0]['result'][-40:]
        out['gainAdapter']=adapter
        out['adapter_reserves']=cap.rpc('ethereum',[cap.call(adapter,'getEthReservedAmount(address)',cap.enc_addr(HG),tag),cap.call(adapter,'getRsETHValueFromETHAmount(uint256)',format(10**18,'064x'),tag)],'hg_reserved_adapter_T')
    (ROOT/'data/eth/manager_case_capture.json').write_text(json.dumps(out,indent=2)+'\n')
    print('hgETH dated state views',len(rows),'valid',sum('result' in r['response'] for r in rows),'oracle marks',len(oracle_rows))
if __name__=='__main__':run()
