"""Reserve rates and executable debt-asset cash, without transaction simulation."""
import json,sys
from collect import ROOT,T,rpc_batch,read_latest,request
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_addr

WETH='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
POOLS={'aave':'0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2','spark':'0xc13e21b648a5ee794902342038ff3adab66be987'}
COLLS={'aave':'0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee','spark':'0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'}
def run():
 tag=hex(read_latest('block_ethereum_T')['height']);calls=[];labs=[]
 for n,p in POOLS.items():
  for token in [WETH,COLLS[n]]:
   labs.append({'pool':n,'address':p,'asset':token});calls.append(('eth_call',[{'to':p,'data':'0x'+sel('getReserveData(address)')+enc_addr(token)},tag]))
 rr=rpc_batch('ethereum',calls,'lending_reserve_T');rows=[];cashcalls=[];cashlabels=[]
 fields=['configuration','liquidityIndex','currentLiquidityRate','variableBorrowIndex','currentVariableBorrowRate','currentStableBorrowRate','lastUpdateTimestamp','id','aTokenAddress','stableDebtTokenAddress','variableDebtTokenAddress','interestRateStrategyAddress','accruedToTreasury','unbacked','isolationModeTotalDebt']
 for l,r in zip(labs,rr):
  if not r.get('result'):continue
  w=[int(r['result'][i:i+64],16) for i in range(2,len(r['result']),64)];assert len(w)==15
  at='0x'+format(w[8],'040x');row={**l,'raw_fields':{k:str(v) for k,v in zip(fields,w)},'aToken':at,'supply_APR':w[2]/1e27,'variable_borrow_APR':w[4]/1e27,'lastUpdateTimestamp':w[6],'status':'fixed_block_legacy_reserve_layout_15_words'}
  rows.append(row);cashlabels.append(l);cashcalls.append(('eth_call',[{'to':l['asset'],'data':'0x'+sel('balanceOf(address)')+enc_addr(at)},tag]))
 cash=rpc_batch('ethereum',cashcalls,'lending_cash_T')
 for l,r in zip(rows,cash):l['underlying_cash_units']=int(r['result'],16)/1e18 if r.get('result') else None
 (ROOT/'data/eth/lending_reserve_T.json').write_text(json.dumps({'target_timestamp':T,'block':int(tag,16),'labels':labs,'responses':rr,'cash_responses':cash,'decoded':rows,'note':'Cash is a debt-token balance at reserve aToken, not assured maximum flash-loan or withdrawal amount; caps, paused state and repayment sequencing matter. APR is instantaneous RAY rate, not historical realized APY.'},indent=2))
 print([(x['pool'],x['asset'],x['supply_APR'],x['variable_borrow_APR'],x['underlying_cash_units']) for x in rows])

if __name__=='__main__':run()
