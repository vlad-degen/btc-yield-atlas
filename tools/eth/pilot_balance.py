"""Independent partial asset/debt reconstruction; retain rather than fill the NAV residual."""
import json,sys
from decimal import Decimal,getcontext
from collect import ROOT,T,read_latest
from pilot_analyze import rpc_named
getcontext().prec=60

def run():
 out=ROOT/'data/eth';details=rpc_named('pilot_details_T.json');metrics=json.loads((out/'etherfi_verified_metrics.json').read_text());price=Decimal(str(read_latest('prices_T')['coins']['coingecko:ethereum']['price']));lines=[]
 def add(label,value,kind,method):lines.append({'label':label,'usd':float(value),'kind':kind,'valuation_method':method})
 for a in metrics['aave_spark_accounts']:add(a['position'],Decimal(str(a['equity_oracle_usd'])),'net_position','Aave/Spark oracle account collateral minus accrued debt; not spot-price balance')
 markets=read_latest('morpho_etherfi_current')['data']['userByAddress']['marketPositions'];prime_price=None
 for p in markets:
  mid=p['market']['marketId'];pos=details['morpho_position_'+mid];state=details['morpho_market_'+mid];oracle=details['morpho_oracle_'+mid][0];loan=p['market']['loanAsset'];ld=loan['decimals'];coll=p['market']['collateralAsset'];cd=coll['decimals']
  debt=Decimal(pos[1])*Decimal(state[2])/Decimal(state[3]) if state[3] else Decimal(0)
  gross=Decimal(pos[2])*Decimal(oracle)/Decimal(10**36);value=(gross-debt)/Decimal(10**ld)
  iseth=loan['symbol']=='WETH';add('main Morpho '+coll['symbol']+'/'+loan['symbol'],value*(price if iseth else 1),'net_position','stored market debt ratio plus collateral oracle; stable loan at assumed $1; unaccrued interest not included')
  if coll['symbol']=='PRIME':prime_price=Decimal(oracle)*Decimal(10**cd)/Decimal(10**(36+ld))
 loan_supply=Decimal(details['loan_getSupply()'][0])/Decimal(10**18);loan_borrow=Decimal(details['loan_getBorrow()'][0])/Decimal(10**18);loan_quote=Decimal(details['loan_getPrices()'][0])/Decimal(10**27)
 add('controlled LoanManager',loan_supply*loan_quote-loan_borrow,'net_position','manager view supplied weETH at oracle USD quote minus RLUSD debt; $1 RLUSD assumption')
 if prime_price is not None:
  data=details['position_underlyings'];ai=data[0]//32;bi=data[1]//32
  assert data[ai]==1 and data[bi]==1
  assert '0x'+format(data[ai+1],'040x')=='0x19ebb35279a16207ec4ba82799cc64715065f7f6'
  add('controlled PositionManager PRIME',Decimal(data[bi+1])/Decimal(10**6)*prime_price,'asset','ABI-decoded PRIME amount times independent Morpho PRIME/PYUSD oracle, $1 PYUSD assumption')
 coins={}
 for i in range(3):coins.update(read_latest('pilot_prices_T_'+str(i))['coins'])
 excluded={'aEthweETH','spwstETH','variableDebtEthWETH','variableDebtWETH','liquidMonadETH'}
 unvalued=[]
 for ch in ['ethereum','optimism']:
  data=json.loads((out/('balances_'+ch+'_T.json')).read_text())
  for r in data['responses']:
   lab=data['labels'][r['id']-1];sym=lab['symbol'];addr=lab.get('address');dec=int(lab.get('decimals') or 18);raw=int(r['result'],16) if r.get('result') else None
   if raw is None or raw==0:continue
   if sym in excluded:continue
   quote=coins.get(ch+':'+str(addr))
   if sym=='native ETH':add(ch+' native ETH',Decimal(raw)/Decimal(10**dec)*price,'asset','ETH quote T+1 second');continue
   if sym in ['STCUSD','senRLUSDv2','senPYUSDPRIMEv2','kpdWETH']:
    dd=6 if sym=='senPYUSDPRIMEv2' else 18;assets=Decimal(details[sym+'_convertToAssets'][0])/Decimal(10**dd)
    add(sym,assets*(price if sym=='kpdWETH' else 1),'asset','ERC4626 assets from convertToAssets; USD assets at assumed $1');continue
   if quote and quote.get('confidence',0)>=.9:
    add(ch+' '+sym,Decimal(raw)/Decimal(10**dec)*Decimal(str(quote['price'])),'asset','dated aggregator price; timestamp and source in raw pilot_prices_T; reward ownership requires checking')
   else:unvalued.append({'chain':ch,'symbol':sym,'address':addr,'raw_balance':str(raw),'reason':'no qualified dated price; zero has not been assigned'})
 add('Uniswap NFT principal',Decimal(str(metrics['uniswap_principal_usd'])),'asset','sqrtPrice and tick principal; pending fee growth omitted')
 fluid=json.loads((out/'fluid_pilot_decoded.json').read_text())['data'];pos=fluid['userPosition_'];state=fluid['getDexState']['state_'];res=fluid['getDexCollateralReserves']['reserves_'];fraction=Decimal(pos['supply'])/Decimal(state['totalSupplyShares']);weeth_rate=Decimal(details['weETH_rate'][0])/Decimal(10**18);wst_rate=Decimal(details['wstETH_rate'][0])/Decimal(10**18)
 # getDexState confirms totalSupplyShares is the low 128 bits of packed storage.
 assert state['totalSupplyShares']==fluid['getTotalSupplySharesRaw']['0']%(2**128)
 coll_eth=fraction*(Decimal(res['token0RealReserves'])*weeth_rate+Decimal(res['token1RealReserves']))/Decimal(10**18);debt_eth=Decimal(pos['borrow'])*wst_rate/Decimal(10**18)
 add('Fluid NFT 4241',(coll_eth-debt_eth)*price,'net_position','pro-rata real reserves of weETH/native ETH smart collateral minus resolver wstETH debt; issuer conversion rates')
 add('Lido finalized withdrawal NFT 122235',Decimal('25.06952018133245')*price,'asset','fixed-block finalized and unclaimed request amount; exact payout not simulated')
 mono=json.loads((out/'mono_accountant_T.json').read_text());mi=json.loads((out/'mono_identity_T.json').read_text())
 mr={x['id']:x.get('result') for x in mono['responses']};ir={x['id']:x.get('result') for x in mi['responses']}
 assert '0x'+mr[2][-40:]=='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
 assert '0x'+mr[3][-40:]=='0xa024063b630d554078bbf985718b22f3c6870ee0'
 mono_claim=Decimal(int(ir[5],16))*Decimal(int(mr[1],16))/Decimal(10**36)
 add('Liquid Monad ETH nested book claim',mono_claim*price,'asset','own fixed-block Accountant ETH-denominated rate times shares held by Liquid ETH; remote backing not independently reconciled')
 total=sum(x['usd'] for x in lines);nav=metrics['published_book_nav_usd_nearest_quote'];result={'target_timestamp':T,'partial_reconstruction_usd':total,'published_book_nav_usd':nav,'unresolved_residual_usd':nav-total,'unresolved_residual_pct':100*(nav-total)/nav,'lines':lines,'unvalued_tokens':unvalued,'material_gaps':['Liquid Monad ETH valued via own Accountant book rate; underlying remote assets remain unresolved and same-address Monad accountant has a different rate','Asset universe starts from current token/NFT discovery, so positions held at T but disposed before discovery may be missed','Uncollected Uniswap fee growth omitted','Royco positions and reward entitlements need economic ownership verification','Morpho main debt uses stored ratio; interest since lastUpdate not projected','Mixed oracle and dated price marks, stablecoins assumed $1; residual is not proof of deficit or solvency']}
 (out/'etherfi_partial_balance_sheet.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k not in ['lines','unvalued_tokens','material_gaps']});print('Fluid equity ETH',float(coll_eth-debt_eth))

if __name__=='__main__':run()
