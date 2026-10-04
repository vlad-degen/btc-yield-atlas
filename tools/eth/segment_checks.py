"""Additional evidence for accounting units, vault leverage and Tron yield semantics."""
import json, sys
from decimal import Decimal
from collect import ROOT, T, read_latest, rpc_batch, request
sys.path.insert(0, str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel, enc_uint, enc_addr

def run():
    tag=hex(read_latest('block_ethereum_T')['height'])
    fluid='0xa0d3707c569ff8c87fa923d3823ec5d81c98be78'
    tree='0xd11c452fc99cf405034ee446803b6f6c1f6d5ed8'
    iau='0x1b6238e95bbcabee58997c99badd4154ad68ba92'
    labels=[];calls=[]
    def add(address, signature, args=''):
        labels.append({'address':address,'signature':signature})
        calls.append(('eth_call',[{'to':address,'data':'0x'+sel(signature)+args},tag]))
    for sig in ['getNetAssets()','vaultDSA()','aggrMaxVaultRatio()','revenue()','withdrawalFeePercentage()','withdrawFeeAbsoluteMin()','getAdmin()','allocationToTeamMultisig()','maxAllocationToTeamMultisig()','getWithdrawFee(uint256)']:
        add(fluid,sig,enc_uint(10**18) if sig.endswith('(uint256)') else '')
    add(fluid,'getSigsImplementation(bytes4)',sel('getNetAssets()').ljust(64,'0'))
    for a in [tree,iau]:add(a,'getUnderlying()')
    # Verify the sole share holder at T, rather than extrapolating the current holder list.
    add('0xb9dc54c8261745cb97070cefbe3d3d815aee8f20','balanceOf(address)',enc_addr('0x5bab73f561a5365c9e4bbc7c52fe0fa384fcf324'))
    result=rpc_batch('ethereum',calls,'segments_T')
    out={'target_timestamp':T,'block':int(tag,16),'labels':labels,'responses':result}
    (ROOT/'data/eth/segment_checks_T.json').write_text(json.dumps(out,indent=2))
    impl=result[10].get('result')
    if impl and impl!='0x':request('fluid_net_module_abi','https://eth.blockscout.com/api/v2/smart-contracts/0x'+impl[-40:])
    history=json.loads((ROOT/'data/eth/benchmark_history_ethereum_rpc.json').read_text())
    histlabels=[x for x in history['labels'] if x['metric']=='block']
    rr=rpc_batch('ethereum',[('eth_call',[{'to':tree,'data':'0x'+sel('getUnderlying()')},hex(l['block'])]) for l in histlabels],'tree_historical_underlying')
    wst='0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'
    identity=all(r.get('result') and '0x'+r['result'][-40:]==wst for r in rr)
    (ROOT/'data/eth/treehouse_denomination_history.json').write_text(json.dumps({'labels':histlabels,'responses':rr,'historical_wstETH_denomination_verified':identity,'note':'This verifies the book unit, not independent asset backing or redemption execution.'},indent=2))
    markets=read_latest('justlend_markets_current');rewards=read_latest('justlend_rewards_current')
    assert markets['code']==rewards['code']==0
    directory=read_latest('justlend_contracts')['networks']['mainnet']['jtokens']
    tron=[]
    for r in markets['data']['tokenList']:
        if r['underlyingAddress'] not in ['THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF','TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh']:continue
        dec=lambda k:Decimal(r[k])
        net=dec('cash')+dec('totalBorrows')-dec('reserves')
        share_claim=dec('totalSupply')*dec('exchangeRate')
        bonus=Decimal(rewards['data'].get(r['address'],{}).get('USDD','0'))
        tron.append({**r,'directory_status':directory[r['symbol']]['status'],'supply_claim_underlying':str(share_claim),'cash_plus_borrow_minus_reserves':str(net),'claim_reconciliation_difference':str(share_claim-net),'utilization':str(dec('totalBorrows')/(dec('cash')+dec('totalBorrows'))),'supply_apy_percent':str(dec('supplyRate')*100),'mining_apy_percent':str(bonus*100),'native_ETH_backing_verified':False,'observation':'current API on 2026-10-03, not historical block T','source':'https://openapi.just.network/lend/jtoken'})
    (ROOT/'data/eth/justlend_eth_semantics.json').write_text(json.dumps(tron,indent=2))
    print('Tron markets',len(tron),'Treehouse denomination history',identity)

if __name__=='__main__':run()
