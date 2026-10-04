"""Fixed-block read calls for the hybrid vault and its disclosed strategy accounts."""
import json, sys
from collect import ROOT, RAW, T, V, ACC, rpc_batch, read_latest, request
sys.path.insert(0,str(ROOT/'tools'/'top5'/'etherfi'))
from keccak_lib import sel, enc_addr, enc_uint

def run():
    b=read_latest('block_ethereum_T')['height'];tag=hex(b); calls=[];labels=[]
    def add(label,target,sig,args=''):
        calls.append(('eth_call',[{'to':target,'data':'0x'+sel(sig)+args},tag]));labels.append({'label':label,'target':target,'signature':sig})
    for sig in ['base()','decimals()','vault()','owner()','authority()','accountantState()']:
        add('accountant_'+sig,ACC,sig)
    add('vault_owner',V,'owner()');add('vault_authority',V,'authority()')
    for c in ['0x528353aea55dbbbf18be26d5726afe6585898dc5','0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3']:
        for sig in ['owner()','pendingOwner()','getPositionAssets()']:
            add(c+'_'+sig,c,sig)
    loan='0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3'
    for sig in ['marketId()','morphoBlue()','getBorrow()','getSupply()','getHealthFactor()','getMarketParams()','getPositionDataSnapshot()','getPrices()','getBorrowRate()','getSupplyRate()']:
        add('loan_'+sig,loan,sig)
    pos='0x528353aea55dbbbf18be26d5726afe6585898dc5'
    add('position_underlyings',pos,'getUnderlyings()')
    drone='0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c'
    for name,pool in [('aave','0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'),('spark','0xc13e21b648a5ee794902342038ff3adab66be987')]:
        add('drone_'+name,pool,'getUserAccountData(address)',enc_addr(drone))
    tokens=read_latest('vault_eth_tokens')
    for sym in ['senRLUSDv2','senPYUSDPRIMEv2','kpdWETH','STCUSD']:
        t=next(x for x in tokens if x['token'].get('symbol')==sym)['token'];address=t['address_hash']
        d=json.loads((ROOT/'data'/'eth'/'balances_ethereum_T.json').read_text())
        index=next(i+1 for i,x in enumerate(d['labels']) if (x.get('address') or '').lower()==address.lower())
        shares=int(next(x['result'] for x in d['responses'] if x['id']==index),16)
        add(sym+'_asset',address,'asset()');add(sym+'_convertToAssets',address,'convertToAssets(uint256)',enc_uint(shares))
    add('weETH_rate','0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','getRate()')
    add('wstETH_rate','0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0','stEthPerToken()')
    markets=read_latest('morpho_etherfi_current')['data']['userByAddress']['marketPositions']
    for p in markets:
        mid=p['market']['marketId'];morpho='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
        add('morpho_position_'+mid,morpho,'position(bytes32,address)',mid[2:]+enc_addr(V))
        add('morpho_market_'+mid,morpho,'market(bytes32)',mid[2:])
        add('morpho_oracle_'+mid,p['market']['oracle']['address'],'price()')
    result=rpc_batch('ethereum',calls,'pilot_details_T')
    if result:(ROOT/'data'/'eth'/'pilot_details_T.json').write_text(json.dumps({'block':b,'target_timestamp':T,'labels':labels,'responses':result},indent=2))
    # Read verified constructor/source, and recipe receipt metadata.
    d=read_latest('bundle_abi_'+drone)
    print('Drone constructor',d.get('constructor_args') or d.get('constructor_arguments'))
    print('Drone source',d.get('source_code','')[:9000])

if __name__=='__main__':run()
