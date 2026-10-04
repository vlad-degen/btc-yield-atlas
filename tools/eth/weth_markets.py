"""Fixed-block WETH lender claims/debt on mandatory Aave chains plus Spark."""
import concurrent.futures,json,re,sys
from collect import ROOT,T,request,read_latest,rpc_batch,RPCS
sys.path.insert(0,str(ROOT/'tools/top5/etherfi'))
from keccak_lib import sel,enc_addr

def run():
 RPCS['arbitrum']=['https://arbitrum-one.public.blastapi.io','https://arbitrum-one-rpc.publicnode.com']+RPCS['arbitrum']
 names={'ethereum':'Ethereum','optimism':'Optimism','base':'Base','arbitrum':'Arbitrum'}
 jobs=[('aave_addressbook_'+c,'https://raw.githubusercontent.com/bgd-labs/aave-address-book/main/src/AaveV3'+n+'.sol') for c,n in names.items()]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:list(p.map(lambda j:request(*j),jobs))
 out=[];allraw=[]
 for chain in names:
  src=read_latest('aave_addressbook_'+chain);pool=re.search(r'POOL = IPool\((0x[0-9a-fA-F]{40})\)',src).group(1).lower();token=re.search(r'WETH_UNDERLYING = (0x[0-9a-fA-F]{40})',src).group(1).lower();b=next(x['block'] for x in json.loads((ROOT/'data/eth/snapshot_manifest.json').read_text())['chains'] if x['chain']==chain)
  pools=[('aave',pool)]
  if chain=='ethereum':pools.append(('spark','0xc13e21b648a5ee794902342038ff3adab66be987'))
  for protocol,pool in pools:
   tag=hex(b);spec=[('eth_call',[{'to':pool,'data':'0x'+sel('getReserveData(address)')+enc_addr(token)},tag])]
   r=rpc_batch(chain,spec,'weth_market_reserve_'+protocol+'_'+chain+'_T');allraw.append({'chain':chain,'pool':pool,'requests':spec,'responses':r})
   value=r[0].get('result') if r else None
   if not value or value=='0x':out.append({'chain':chain,'protocol':protocol,'status':'reserve_unavailable','data':None});continue
   w=[int(value[i:i+64],16) for i in range(2,len(value),64)];assert len(w)==15
   at='0x'+format(w[8],'040x');sd='0x'+format(w[9],'040x');vd='0x'+format(w[10],'040x');calls=[('eth_call',[{'to':at,'data':'0x'+sel('totalSupply()')},tag]),('eth_call',[{'to':vd,'data':'0x'+sel('totalSupply()')},tag]),('eth_call',[{'to':token,'data':'0x'+sel('balanceOf(address)')+enc_addr(at)},tag])]
   if w[9]:calls.append(('eth_call',[{'to':sd,'data':'0x'+sel('totalSupply()')},tag]))
   rr=rpc_batch(chain,calls,'weth_market_balances_'+protocol+'_'+chain+'_T');allraw.append({'chain':chain,'pool':pool,'requests':calls,'responses':rr});byid={r['id']:r for r in rr};units=lambda i:int(byid[i]['result'],16)/1e18 if byid.get(i,{}).get('result') and byid[i]['result']!='0x' else None
   stable=units(4) if w[9] else 0
   row={'chain':chain,'protocol':protocol,'block':b,'target_timestamp':T,'pool':pool,'WETH':token,'aToken':at,'variableDebtToken':vd,'stableDebtToken':sd,'lender_claim_units':units(1),'variable_debt_units':units(2),'stable_debt_units':stable,'reserve_cash_units':units(3),'supply_APR':w[2]/1e27,'variable_borrow_APR':w[4]/1e27,'source':'primary address book with T getReserveData identity; fixed-block token totalSupply/balanceOf','is_market_wide_unique_capital':False}
   row['debt_units']=row['variable_debt_units']+stable if stable is not None else None;row['borrow_over_lender_claim']=row['debt_units']/row['lender_claim_units'] if row['debt_units'] is not None else None;out.append(row)
   extra_sigs=['getReserveDeficit(address)','getVirtualUnderlyingBalance(address)']
   ec=[('eth_call',[{'to':pool,'data':'0x'+sel(s)+enc_addr(token)},tag]) for s in extra_sigs]
   er=rpc_batch(chain,ec,'weth_market_deficit_'+protocol+'_'+chain+'_T');allraw.append({'chain':chain,'pool':pool,'requests':ec,'responses':er})
   row['extra_getters']={s:(int(r['result'],16)/1e18 if r.get('result') and r['result']!='0x' else None) for s,r in zip(extra_sigs,er or [])}
   row['lender_claim_minus_cash_and_debt_units']=row['lender_claim_units']-row['reserve_cash_units']-row['debt_units'] if row['debt_units'] is not None else None
 (ROOT/'data/eth/weth_lending_markets_T.json').write_text(json.dumps({'target_timestamp':T,'markets':out,'raw_calls':allraw,'scope':'Aave V3 four mandatory chains and Spark Ethereum; WETH lender claims/debt, not net total of ETH yield economy'},indent=2));print(out)

if __name__=='__main__':run()
