"""Replay fixed-block public captures, then augment the existing eight-chapter report.
No network, extrapolation of missing observations, or summing nested claims.
"""
import csv, hashlib, json
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
getcontext().prec=60
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'data/eth'; EN=ROOT/'research/eth/en'
T='2026-10-02T23:59:59Z'; START='2026-09-02T23:59:59Z'; PRICE=Decimal('2667.9504418816')
WETH='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'; USDT='0xdac17f958d2ee523a2206206994597c13d831ec7'; DAI='0x6b175474e89094c44da98b954eedeac495271d0f'
def read(n):return json.loads((D/(n+'.json')).read_text())
def save(n,d):(D/(n+'.json')).write_text(json.dumps(d,indent=2)+'\n')
def date(t):return datetime.fromtimestamp(t,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def words(value):return [int(value[i:i+64],16)for i in range(2,len(value),64)]
class Evidence:
 def __init__(self):
  self.sources={};self.rows={}
  for path in sorted(D.glob('finalization_*.json')):
   if '_retry_' in path.name or path.stem in ['finalization_reconstruction','finalization_financial_ledgers','finalization_verification']:continue
   d=json.loads(path.read_text());self.sources[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
   for r in d.get('records',[])if isinstance(d,dict)else[]:
    if isinstance(r.get('response',{}).get('result'),str)and r['response']['result']!='0x':self.rows[r['label']]=r
 def raw(self,label):
  r=self.rows[label];assert 'error'not in r['response'];return words(r['response']['result'])
 def n(self,label,scale=18,index=0):return Decimal(self.raw(label)[index])/Decimal(10)**scale
 def maybe(self,label,scale=18,index=0):
  return self.n(label,scale,index)if label in self.rows else None
 def proof(self,label):
  r=self.rows[label];return {'label':label,'block':r.get('block'),'address':r.get('address'),'signature':r.get('signature'),'rawResult':r['response']['result'],'capture':r['capture']['path'],'captureSHA256':r['capture']['sha256']}

def loan(e,prefix,venue,token,decimals,account,collateral,accountLabel=None):
 label=prefix+'_'+venue+'_reserve_'+token+'_debt'; amount=e.n(label,decimals)
 if amount<Decimal('.001'):return None
 symbol={'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48':'USDC',USDT:'USDT',WETH:'WETH','0xdc035d45d973e3ec169d2276ddab16f1e407384f':'USDS','0x6c3ea9036406852006290770bedfcaba0e23a0e8':'PYUSD'}.get(token,token)
 a=e.raw(accountLabel)if accountLabel else None
 return {'date':T,'chain':'Ethereum','account':account,'protocol':venue.title()+' V3','collateralAsset':collateral,'collateralETH':None,'collateralUSD':float(Decimal(a[0])/10**8)if a else None,'debtAsset':symbol,'debtUnits':float(amount),'debtUSD':float(amount*(PRICE if token==WETH else 1)),'LTV_pct':float(Decimal(a[1])*100/a[0])if a and a[0]else None,'healthFactor':float(Decimal(a[5])/10**18)if a else None,'borrowAPR_pct':None,'sourceURLs':['https://etherscan.io/address/'+account],'scope':'Archived reserve debt; USD token uses face value. ETH loans are staking loops, not dollar carry.','evidence':e.proof(label)}

def build():
 e=Evidence();market=read('market_reader_chapter');months=market['months']; native=read('finalization_native_T_summary');native['activeBalanceETH']=float(Decimal(native['activeBalanceGwei'])/10**9);native['activeEffectiveBalanceETH']=float(Decimal(native['activeEffectiveBalanceGwei'])/10**9)
 history=read('finalization_product_history')['records']; hm={r['label']:r for r in history}
 products=[]
 specs=[('lido-earn','Lido Earn ETH','0xBBFC8683C8fE8cF73777feDE7ab9574935fea0A4','https://docs.lido.fi/earn/deployment-contracts/','Oracle-valued ETH claim; includes allocated, unclaimed shares'),('avant','Avant avETH / savETH','0x9469470C9878bf3d6d0604831d9A3A366156f7EE','https://docs.avantprotocol.com/security/contract-addresses','avETH face supply; returns belong to the senior savETH claim'),('makina-deth','Makina DETH','0x871aB8E36CaE9AF35c6A3488B049965233DeB7ed','https://docs.makina.finance/strategies/deployments','Cached reported ETH book; accounting timestamp retained'),('vesper','Vesper vaETH','0xd1C117319B3595fbc39b471AB1fd485629eb05F2','https://docs.vesper.finance','Reported ETH pool book; carry is one strategy'),('zensats','ZenSats wstETH','0x23F189dE34EED95f6303CfF1C77f7676F211Dd2c','https://www.zensats.app/llms-full.txt','Reported wstETH managed assets converted to ETH; not independently netted carry equity')]
 def measurement(id,period):
  if id=='lido-earn':
   shares=e.maybe('lidoEarn_'+period+'_totalShares()');report=e.maybe('lidoEarnRoot_'+period+'_WETH_report',0)
   if shares is None or report is None:return None,None
   pps=Decimal(10)**18/report;return shares*pps,pps
  if id=='avant':return e.maybe('avETH_'+period+'_totalSupply()'),e.maybe('savETH_'+period+'_convertToAssets(uint256)')
  if id=='makina-deth':
   a=e.maybe('makina_'+period+'_lastTotalAum()');s=e.maybe('dethSupply_'+period)
   return a,a/s if a is not None and s else None
  if id=='vesper':return e.maybe('vesper_'+period+'_totalValue()'),e.maybe('vesper_'+period+'_pricePerShare()')
  a=e.maybe('zensats_'+period+'_totalAssets()');s=e.maybe('zensats_'+period+'_totalSupply()');rate=e.maybe('wstETH_'+period)
  return a*rate if a is not None and rate else None,a/s*rate if a is not None and s and rate else None
 for id,name,address,source,basis in specs:
  rows=[];marks=[]
  for m in months:
   p=m['period'];value,pps=measurement(id,p);price=m.get('eth_price_USD')or m.get('priceUSD')or None
   # Reference prices are the same frozen month quotes already used by Liquid.
   existing=next(x for x in read('reader_carry_category')['products']if x['product']=='ether.fi Liquid ETH')['history'];price=next(r['priceUSD']for r in existing if r['month']==p)
   row={'month':p,'timestamp':m['target_timestamp'],'date':date(m['target_timestamp']),'sizeETH':float(value)if value is not None else None,'sizeUSD':float(value*Decimal(str(price)))if value is not None else None,'sizeNative':float(value)if value is not None else None,'sizeNativeSymbol':'ETH-equivalent','status':'archived_reported_book'if value is not None else 'no_usable_book_observation','carryAllocationPercent':None,'sourceURLs':[source]};rows.append(row)
   if pps is not None and pps>0:marks.append({'date':row['date'],'timestamp':row['timestamp'],'ethBookPrice':float(pps),'borrowAPR_pct':None,'sourceURLs':[source]})
  value,pps=measurement(id,'snapshot');_,startpps=measurement(id,'30d_start');assert value is not None and pps and startpps,(id,value,pps,startpps)
  ret=float((pps/startpps-1)*100);w={'windowDays':30,'date':T,'startDate':START,'cumulativeReturnPct':ret,'endBookPrice':float(pps),'startBookPrice':float(startpps),'basis':basis}
  marks.append({'date':START,'timestamp':1788393599,'ethBookPrice':float(startpps),'borrowAPR_pct':None,'sourceURLs':[source]})
  marks.sort(key=lambda r:r['timestamp'])
  marks.append({'date':T,'timestamp':1790985599,'ethBookPrice':float(pps),'borrowAPR_pct':None,'sourceURLs':[source]})
  products.append({'id':id,'name':name,'address':address,'source':source,'capitalETH':float(value),'capitalUSD':float(value*PRICE),'capitalBasis':basis,'history':rows,'marks':marks,'window':w})
 # Actual reserve currency, balances and account-specific liquidation headroom.
 legs={id:[]for id,*_ in specs}; subs={1:'0x893aa69fbaa1ee81b536f0fbe3a3453e86290080',2:'0x181cb55f872450d16ae858d532b4e35e50eaa76d',3:'0x9938a09fea37ba681a1bd53d33ddde2debec1da0',4:'0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7',6:'0xcdfa7efe670869c6b6be4375654e0b206ef49c89'}
 for i,venue,token,dec in [(1,'aave',WETH,18),(6,'aave',WETH,18),(4,'spark',WETH,18),(2,'aave',USDT,6),(2,'spark',USDT,6),(3,'aave','0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',6)]:
  legs['lido-earn'].append(loan(e,'strATEGY_sub_'+str(i),venue,token,dec,subs[i],'wstETH / ETH-family collateral','strATEGY_sub_'+str(i)+'_'+venue))
 avantwallet='0x6CC60A0b57bc882A0471980D0e2D4aD7DDf3C4bD'
 for venue,token,dec in [('aave','0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',6),('spark','0xdc035d45d973e3ec169d2276ddab16f1e407384f',18),('spark','0x6c3ea9036406852006290770bedfcaba0e23a0e8',6)]:legs['avant'].append(loan(e,'avant_wallet',venue,token,dec,avantwallet,'WETH, wstETH and weETH','avETH_wallet_4_'+venue))
 legs['makina-deth'].append(loan(e,'deth','aave',WETH,18,'0xD1A2d9DF5db842DA2Ee81075Fa441602B2352915','weETH'))
 debt=e.n('vesper_xy_debtDAI_balance');legs['vesper']=[{'date':T,'chain':'Ethereum','account':'0x666C80fEcA6Fcd371B0535A9846E2d223CbF1d10','protocol':'Aave V3 → Vesper vDAI','collateralAsset':'WETH','collateralETH':float(e.n('vesper_xy_aWETH_balance')),'debtAsset':'DAI','debtUnits':float(debt),'debtUSD':float(debt),'healthFactor':None,'borrowAPR_pct':None,'sourceURLs':['https://etherscan.io/address/0x666C80fEcA6Fcd371B0535A9846E2d223CbF1d10'],'scope':'Actual variable DAI loan. PoolAccountant strategy allocation is a different quantity.'}]
 zd=e.n('zensats_active_loan_getCurrentDebt()');legs['zensats']=[{'date':T,'chain':'Ethereum','account':'0xCf9f54218666a32BE9da1d60BC81412BA86730C7','protocol':'Curve LlamaLend','collateralAsset':'wstETH','collateralETH':None,'debtAsset':'crvUSD','debtUnits':float(zd),'debtUSD':float(zd),'healthFactor':None,'borrowAPR_pct':None,'sourceURLs':['https://etherscan.io/address/0xCf9f54218666a32BE9da1d60BC81412BA86730C7'],'scope':'LlamaLend soft-liquidation mechanics differ from Aave health factor.'}]
 # Morpho cached market debt is explicitly labelled before pending interest.
 morpho=[]
 for r in read('finalization_route_finals_T')['records']:
  if 'marketParams'in r['label'] or 'position'in r['label'] or 'market'in r['label']:morpho.append({'label':r['label'],'rawResult':r.get('response',{}).get('result'),'capture':r['capture']['path']})
 mid='e7e9694b754c4d4f7e21faf7223f6fa71abaeb10296a4c43a54a7977149687d2'
 pos=e.raw('makina_morpho_'+mid+'_position(bytes32,address)');mkt=e.raw('makina_morpho_'+mid+'_market(bytes32)')
 stored=Decimal(pos[1])*(mkt[2]+1)/(mkt[3]+10**6)/10**6
 legs['makina-deth'].append({'date':T,'chain':'Ethereum','account':'0xD1A2d9DF5db842DA2Ee81075Fa441602B2352915','protocol':'Morpho USDT / wstETH','collateralAsset':'wstETH','collateralUnits':float(Decimal(pos[2])/10**18),'debtAsset':'USDT','debtUnits':float(stored),'debtUSD':float(stored),'healthFactor':None,'borrowAPR_pct':None,'sourceURLs':['https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'],'scope':'Stored indexed debt before pending interest. This is a distinct dollar route from the larger Aave WETH loop.'})
 metrics=next(r for r in read('finalization_native_and_avant')if r['key']=='avant_metrics_aveth');avant=json.loads((ROOT/metrics['path']).read_text())
 out={'schemaVersion':1,'snapshot':T,'ethereumBlock':26108081,'native':native,'nativeHistory':read('finalization_native_history'),'newProducts':products,'loanLegs':legs,'makinaMorpho':morpho,'makinaAccountingInstructions':read('finalization_makina_instruction_decode'),'avantPublishedAllocation':avant,'avantAllocationSource':metrics,'sourceFileHashes':e.sources,'limitations':['Native active balance is an independently defined consensus layer; no wrapper balances are added. Earlier native states are pruned at tested public endpoints.','All thirteen carry-linked books are a public product census, not all private wallet strategies or unique market carry equity.','Oracle, cached and face-value books have different claim and exit conventions.','Observed investment share marks are not guaranteed redemption cash.']}
 pt=[]
 for market in ['0x384509537ce5daa5740baeb6d1ee0eb2847ea8a8','0x79a8b102dd39329aafecc69499c0f6d07f2f959d','0x34280882267ffa6383b363e278b027be083bbe3b','0x392ac82951ef3b32512bc5be0dfb6a762c43bb81']:
  prefix='pendle_'+market+'_';tokens=e.raw(prefix+'market LP_readTokens()');info=e.raw(prefix+'standardized yield_assetInfo()');expiry=e.raw(prefix+'principal token_expiry()')[0]
  assert tokens[0]==e.raw(prefix+'principal token_SY()')[0] and tokens[2]==e.raw(prefix+'principal token_YT()')[0] and expiry>1790985599
  asset='0x'+hex(info[1])[2:].rjust(40,'0');pt.append({'market':market,'SY':'0x'+hex(tokens[0])[2:].rjust(40,'0'),'PT':'0x'+hex(tokens[1])[2:].rjust(40,'0'),'YT':'0x'+hex(tokens[2])[2:].rjust(40,'0'),'faceSupply':float(e.n(prefix+'principal token_totalSupply()')),'accountingAsset':asset,'accountingUnit':'native ETH'if info[1]==0 else 'stETH'if asset=='0xae7ab96520de3a18e5e111b5eaab095312d7fe84'else'WETH','expiry':date(expiry),'pyIndex':float(e.n(prefix+'pyIndex')),'scope':'Examined active subset; PT face, pool liquidity and unique underlying capital differ.'})
 out['fixedMaturity']=pt
 out['options']={'ribbonResidualBookETH':float(e.n('ribbon_totalBalance')),'currentOptionExpiry':date(e.raw('ribbon_current_expiryTimestamp()')[0]),'ongoingPremiumActivityProven':False,'thetanutsFullCapacity':None,'scope':'Residual Ribbon book has an expired current option; idle token cash is not total invested capacity.'}
 from finalization_financial_ledgers import run as build_financial_ledgers
 ledgers = build_financial_ledgers()
 out.update(flowAdjustedLedgers=ledgers['flowAdjustedLedgers'],directFinancedLot=ledgers['directFinancedLot'])
 save('finalization_reconstruction',out)
 with (D/'native-staking-observations.csv').open('w',newline='')as f:
  writer=csv.writer(f);writer.writerow(['month','active_actual_ETH','active_effective_ETH','validators','status','state_root'])
  for r in out['nativeHistory']:writer.writerow([r['month'],float(Decimal(r['activeBalanceGwei'])/10**9)if r.get('activeBalanceGwei')else None,float(Decimal(r['activeEffectiveBalanceGwei'])/10**9)if r.get('activeEffectiveBalanceGwei')else None,r.get('activeValidatorCount'),r['status'],r.get('stateRoot')])
 return out

# The long-form explanations stay inside existing product chapters, not new top-level panels.
DETAILS={
'lido-earn':{
 'title':'A large nested allocator with two different borrowing risks',
 'text':'Earn ETH reports 83,309 ETH. Its main holding is stRATEGY, whose book must not be added again. The nested portfolio owes about 355,217 WETH in staking loops and 25.55M USDT in its main dollar-carry account. Those are gross loans, not the carry sleeve’s equity.',
 'lesson':'Separate the WETH loop from the USDT investment before judging income or liquidation risk.',
 'collateral':'wstETH and other ETH-family receipts','debt':'WETH loops; USDT carry; a small USDC position','destination':'earnUSD for the USDT sleeve; separate leveraged staking positions','operator':'Lido / Mellow / stRATEGY curator','fees':'15% performance + 0.20% annual outer fee; nested stRATEGY and earnUSD settings are zero',
 'risk':'Thin loop headroom; nested credit, oracle and redemption queues',
 'flow':[('Buy the outer ETH claim','Deposits enter the outer queue. Oracle processing allocates shares, which can remain unclaimed. Total shares, rather than minted supply alone, form the reported book.'),('Follow the nested holding','The main subvault holds 79,267 strETH shares. stRATEGY reports 84,664 ETH, but almost all its shares are already represented inside Earn ETH. Count the outer book once.'),('Keep ETH loops separate','Aave and Spark WETH borrowing totals about 355,217 ETH. Health factors are 1.035 to 1.039. These loops depend on collateral conversion and funding; they are not dollar carry.'),('Borrow dollars in the carry account','The separate account owes 22.240M USDT on Aave and 3.313M USDT on Spark. Their health factors are 2.124 and 2.488. Loan cost accrues in USDT even when the investor holds an ETH claim.'),('Invest in the dollar vault','That account holds 24.726M earnUSD shares. The oracle reports shares per asset: invert its six-decimal USDT price to value the claim. Share growth and changing deposits must be separated.'),('Apply the fee layers once','The outer fee settings are 15% of performance and 0.20% annually. stRATEGY and earnUSD settings are zero at T. Fees already recognised in the reported share price are not deducted again.'),('Exit through two liquidity decisions','EarnUSD must provide dollar liquidity so the carry account can repay USDT; the outer vault must then settle the investor’s ETH redemption. Oracle pricing and liquidity settlement are separate steps. A quoted NAV is not immediate cash.')],
 'payers':['Validator issuance, tips and MEV on the staking collateral','Borrowers and strategies inside earnUSD; recognised rewards can be part of its reported price'],
 'actors':[('Outer fee owner','0x0dd73341d6158a72b4d224541f1094188f57076e','Controls the outer fee-manager settings; owner and fee recipient are distinct'),('Carry account','0x181cb55f872450d16ae858d532b4e35e50eaa76d','Executes the separately traced Aave / Spark USDT position'),('Oracle and curators',None,'Authorised reports price claims; curators arrange swaps and queue liquidity')],
 'limits':['The outer ETH oracle mark is about 17 hours old at T; this is a reported claim, not an independently recomputed exit NAV.','Loop loan balances are gross and cannot be used as carry-equity weights.','The earning period, borrower mix and incentive sponsor inside earnUSD require further look-through before calling all share growth organic income.']},
'avant':{
 'title':'Dollar carry with its own issuer credit inside the destination',
 'text':'The published 29 September portfolio has a $33.18M net NAV and a $32.53M savUSD position. Ethereum reads at T confirm USDC, USDS and PYUSD borrowing against ETH collateral. The large own-credit destination makes this a concentrated issuer dependency.',
 'lesson':'A second product from the same issuer does not create independent credit diversification.',
 'collateral':'WETH, wstETH and weETH','debt':'USDC, USDS and PYUSD in the traced Ethereum account; other chains separately disclosed','destination':'savUSD / avUSD, dollar credit and liquidity positions across chains','operator':'Avant / strategy wallets / NAV reporting','fees':'Senior savETH conversion measured; fee rights depend on the mint, redemption and tranche contracts','risk':'Own-credit concentration; cross-chain custody, NAV freshness and tranche allocation',
 'flow':[('Distinguish the token claims','avETH is the issuer’s nominal ETH liability. savETH is a senior staking claim on avETH. The book-size row uses avETH supply; the return row uses savETH conversion. They do not describe the same investor right.'),('Post ETH collateral','A listed strategy wallet has WETH, wstETH and weETH supplied on Ethereum. At T its Aave health factor is 1.382 and Spark health factor 1.370.'),('Borrow several dollar currencies','The traced wallet owes 2.211M USDC on Aave, plus 7.322M USDS and 0.502M PYUSD on Spark. Repayment requires those specific tokens, not merely any dollar balance.'),('Follow the published investments','The latest saved allocation is dated 29 September, three days before T. It includes 32.535M dollars of savUSD plus avUSD, credit receipts and stablecoin liquidity. This disclosure is dated separately from the fixed-block debt.'),('Look through the issuer relationship','savUSD and avUSD are Avant claims. The dollar portfolio’s borrower credit, reserve backing and valuation affect the ETH product through this link. The roughly 98% savUSD / net-NAV ratio is a concentration indicator, not a carry-allocation percentage.'),('Assign income to the tranche','Senior savETH receives income under its distribution and vesting rules. Issuer NAV growth, junior income and a senior conversion return cannot be substituted for one another.'),('Complete the redemption chain','savETH has a one-day cooldown at T. Converting it to avETH is one step; receiving final ETH still depends on avETH redemption, reserve liquidity and strategy unwinds. The cooldown does not guarantee the whole exit.')],
 'payers':['Validator income on supplied ETH receipts','Dollar borrowers and investment positions in the Avant dollar portfolio; internal tranche allocation determines savETH income'],
 'actors':[('Issuer and NAV process',None,'Publishes portfolio NAV and distributes income; disclosure is dated'),('Traced Ethereum strategy wallet','0x6CC60A0b57bc882A0471980D0e2D4aD7DDf3C4bD','Holds collateral and debt on Aave and Spark'),('savETH contract','0xDA06eE2dACF9245Aa80072a4407deBDea0D7e341','Controls senior conversion, vesting and cooldown state')],
 'limits':['avETH face supply is not an independently verified reserve NAV.','The fixed-block Ethereum loans do not reconstruct all cross-chain weights at T.','The common 30-day return belongs to savETH’s senior claim; it is not whole-issuer or organic carry profit.']},
'makina-deth':{
 'title':'A restaking loop with a smaller dollar-financed credit position',
 'text':'DETH reports 2,499 ETH in a cached book. Its hub has 15,065 WETH of Aave debt against weETH, plus a Morpho USDT / wstETH carry route. Verified accounting instructions identify the credit receipts instead of relying on the vault name.',
 'lesson':'The biggest gross position is an ETH loop; the USDT route has separate currency and exit risk.',
 'collateral':'weETH and wstETH','debt':'Large WETH loop; Morpho USDT carry and minor other debt','destination':'Senior PYUSD credit receipt and nested strategy shares','operator':'Makina / strategy operator / hub Caliber','fees':'Machine fee manager and redemption module identified; quoted book is a cached accounting value','risk':'Stale accounting; cross-currency carry, nested shares and exit controls',
 'flow':[('Start with the machine book','DETH shares reference a WETH-accounted machine. The last reported AUM is 2,499 ETH. Its accounting timestamp is about 14.5 hours before T.'),('Inspect the actual accounting instructions','The saved accounting transaction decodes 15 positions, their debt flags, commands and affected tokens. This identifies what the machine values and prevents classifying every position as carry.'),('Separate the dominant loop','The hub owes 15,065 WETH on Aave and supplies 15,110 weETH units. The gross borrowed ETH is leveraged restaking exposure; it is not new investor capital or a dollar loan.'),('Trace the dollar route','A Morpho wstETH / USDT market has 279.57 wstETH collateral and about 384,701 USDT of stored indexed debt before pending interest. The small USDC loan is a different position.'),('Identify the investment claim','Accounting includes senPYUSDmain and nested DQAeETH / DCM shares. USDT funding and a PYUSD destination introduce currency sourcing and borrower credit. The whole receipt cannot be assigned to a single loan without transaction allocation.'),('Respect stale and cross-chain state','The fresh accounting getter rejects stale positions. Cached AUM is retained as a book observation. Configured spokes do not prove substantial deployments: the reported spoke balances at T are negligible.'),('Use the redemption module','Selling a DETH share and redeeming through the machine are different routes. A complete unwind needs updated accounting, the configured redeemer and sufficient hub liquidity, including repayment of both WETH and dollar debts.')],
 'payers':['Ethereum staking / restaking income after WETH funding','Borrowers in the senior dollar-credit receipt; nested strategy income'],
 'actors':[('Machine','0x0447D0aD7FD6a3409B48Ecbb9DDB075C1e11D735','Sets the reported share book and connects fees, depositor and redeemer modules'),('Hub Caliber','0xD1A2d9DF5db842DA2Ee81075Fa441602B2352915','Executes and accounts for permitted investment positions')],
 'limits':['A cached book is not an executable fresh NAV.','Morpho stored debt requires pending-interest treatment before final repayment sizing.','Nested receipts and debt do not establish a uniquely attributed carry-equity amount.']},
'vesper':{
 'title':'A small, directly traceable DAI carry sleeve inside an ETH pool',
 'text':'vaETH reports 1,052 ETH. Its XY strategy supplies 57.35 WETH, owes 68,998 DAI and holds 60,034 vDAI shares. Other strategies in the same pool are lending or liquidity positions, so the whole pool cannot be labelled carry.',
 'lesson':'The strategy’s actual dollar loan is different from its pool-accounting allocation.',
 'collateral':'WETH','debt':'DAI on Aave V3','destination':'Vesper vDAI dollar lending pool','operator':'Vesper / pool accountant / XY strategy','fees':'Pool universalFee is 100 bps at T; strategy and realised profit fees require the pool’s fee formula','risk':'Dollar funding versus vDAI return; reward dependence and withdrawal liquidity',
 'flow':[('Hold a share of the ETH pool','vaETH shares represent the combined pool book. The eight registered strategies include lending, nested pools, liquidity and a dollar-carry route.'),('Select the funded XY strategy','The funded AaveV3_Vesper_Xy_ETH_DAI strategy posts WETH. Another registered ETH / DAI strategy has zero actual debt at T; an active flag alone does not establish deployment.'),('Read the lender liability','The XY account’s variable DAI debt is 68,998 DAI. The pool accountant’s totalDebtOf is the allocation owed to the ETH pool, not the DAI loan amount.'),('Value the dollar investment','The account holds 60,034 vDAI shares. The archived share price is 1.148609 DAI per share. Multiply to value the destination; keep VSP and other externally paid rewards separate.'),('Account for flows before income','During the matched 30 days both the loan and vDAI share balance fell materially. A simple end-minus-start balance would confuse withdrawals with losses.'),('Return income to the ETH book','Dollar yield after DAI interest and strategy costs supports the ETH pool. The pool’s observed 30-day ETH share gain is a different measure from carry-only profit.'),('Unwind the lending route','Redeem vDAI, source and repay DAI, withdraw WETH collateral and provide ETH-pool liquidity. A destination share price does not guarantee redemption at the required size.')],
 'payers':['Borrowers in the vDAI pool','Borrowers, validators and traders in the other vaETH strategies; external rewards separately'],
 'actors':[('ETH pool','0xd1C117319B3595fbc39b471AB1fd485629eb05F2','Issues shares and combines strategy accounting'),('Funded XY strategy','0x666C80fEcA6Fcd371B0535A9846E2d223CbF1d10','Manages WETH collateral, DAI debt and vDAI shares')],
 'limits':['Carry is one strategy in a mixed pool.','Dollar share growth excludes unassigned external reward cash.','Pool-reported NAV, loan interest and investor exit cash answer different questions.']},
'zensats':{
 'title':'An active but very small soft-liquidation carry route',
 'text':'The active vault manages less than one ETH and owes about 953 crvUSD. The old Aave / RAAC vault has zero share supply and assets at T. A documented strategy can be real without being a large market category.',
 'lesson':'Use frozen balances to distinguish a live micro-position from an empty legacy design.',
 'collateral':'wstETH','debt':'crvUSD on LlamaLend','destination':'Curve crvUSD / USDT liquidity through StakeDAO','operator':'ZenSats / loan manager / yield strategy','fees':'Configured vault fee settings are zero at T','risk':'Soft liquidation, pool inventory and incentive expiry',
 'flow':[('Use the active deployment','The active vault differs from the withdraw-only legacy deployment. Archived supply and assets establish which book is funded.'),('Post staking collateral','The loan manager supplies wstETH. Staking income remains on the collateral while the loan is denominated in crvUSD.'),('Borrow with soft liquidation','LlamaLend converts collateral exposure across price bands during soft liquidation. Its risk cannot be expressed as an Aave health factor.'),('Supply dollar liquidity','The strategy invests crvUSD in the crvUSD / USDT pool and StakeDAO route. Trading fees, inventory changes and incentives contribute differently to its result.'),('Compare the dollar claim with debt','The saved strategy value is about 951 crvUSD against 953 crvUSD of debt. This snapshot comparison does not by itself establish full realised profit, including collateral staking and rewards.'),('Keep the legacy product separate','The old Aave / RAAC route is withdraw-only in documentation and has zero share supply / assets at T. Do not add its historical design as current funded capital.'),('Exit in the debt currency','Withdraw or rebalance the liquidity position, source crvUSD, repay the controller and release wstETH. Soft-liquidation inventory and pool liquidity determine actual proceeds.')],
 'payers':['Ethereum validator income on wstETH collateral','Curve traders and separately funded StakeDAO / pool incentives'],
 'actors':[('Active vault','0x23F189dE34EED95f6303CfF1C77f7676F211Dd2c','Issues the current wstETH-accounted claim'),('Loan manager','0xCf9f54218666a32BE9da1d60BC81412BA86730C7','Manages the LlamaLend collateral and crvUSD debt'),('Yield strategy','0x8bD4d875E2Cf1174e282B532Fa534b6633F59B5f','Holds the dollar investment claim')],
 'limits':['This micro-position is included for route completeness, not evidence of large carry-market capital.','Reported managed assets are not independently netted carry equity.','No complete reward-adjusted investor cash return is claimed.']}
}

def augment():
 out=build();e=Evidence();cc=read('reader_carry_category');pc=read('reader_product_chapters')
 ids={r['id']for r in out['newProducts']};pc['products']=[p for p in pc['products']if p['id']not in ids];names={p['name']for p in out['newProducts']};cc['products']=[p for p in cc['products']if p['product']not in names]
 for x in out['newProducts']:
  id=x['id'];d=DETAILS[id];source=x['source'];route={k:d[k]for k in ['collateral','debt','destination']};ret=x['window']['cumulativeReturnPct'];basis=x['capitalBasis'];src=[{'url':source,'label':'Official deployments and strategy documentation'},{'url':'https://etherscan.io/address/'+x['address'],'label':'Fixed-block share contract'},{'url':'data/finalization_reconstruction.json','label':'Reconstruction, timestamps and source hashes'}]
  metrics=[{'label':'Capital at snapshot','value':f"{x['capitalETH']:,.2f} ETH","scope":basis,'date':T},{'label':'Holder addresses at snapshot','value':'Not independently replayed','scope':'No current holder count substituted for the frozen snapshot','date':T},{'label':'Fees','value':d['fees'],'scope':'Configured state and applicable claim layer','date':T},{'label':'First measured material month','value':next((r['month']for r in x['history']if(r['sizeETH']or 0)>1),'Micro-position'),'scope':'First >1 ETH archived book in the sampled history; not launch date','date':T},{'label':'Observed 30-day ETH claim return','value':f'{ret:+.4f}%','numeric':ret,'scope':x['window']['basis'],'date':T},{'label':'Carry-only investor profit','value':'Claim and funding evidence shown separately','scope':'No whole-book return presented as organic carry profit','date':T}]
  p={'id':id,'rank':0,'name':x['name'],'subtitle':d['title'],'classification':'E4','capitalETH':x['capitalETH'],'capitalUSD':x['capitalUSD'],'capitalBasis':basis,'returnBasis':basis,'keyMetrics':metrics,'moneyFlow':[{'step':i+1,'title':t,'text':text,'url':source,'contract':None}for i,(t,text)in enumerate(d['flow'])],'actors':[{'who':who,'address':address,'role':role,'canChange':role,'delay':'Contract-specific; no blanket timelock assumed','url':'https://etherscan.io/address/'+address if address else source}for who,address,role in d['actors']],'incomePayers':[{'payer':s,'text':s}for s in d['payers']],'charts':{'capitalHistory':{'title':'Whole-product book history','rows':x['history'],'scope':basis+'. Missing observations stay absent.'},'returnVsBorrow':{'title':'ETH claim value','rows':x['marks'],'windowReturns':[x['window']],'scope':basis+'. External payouts and executable exit costs are separate.'},'walletDistribution':{'title':'Share ownership','rows':[],'topHolders':[],'holderCounts':{},'scope':'A complete all-transfer holder replay at T is not included for this additional product; the report does not replace it with a current holder count.'},'loanLegs':{'title':'Actual borrowing accounts','rows':[r for r in out['loanLegs'][id]if r],'scope':'Actual debt currency and individual account headroom at T. Gross loops, dollar loans and product equity are different quantities.'}},'timeline':[{'date':T,'title':'Frozen route and book measured','text':d['text'],'url':source}],'sources':src,'limitations':d['limits'],'liveRoute':route,'story':{k:d[k]for k in ['title','text','lesson']},'comparison':{'route':d['collateral']+' → '+d['debt'],'destination':d['destination'],'fees':d['fees'],'operator':d['operator'],'risk':d['risk']},'status':'active','statusLabel':'Active hybrid'if id in ['lido-earn','avant','makina-deth','vesper']else'Active micro-position','allocationEvidence':d['text'],'captureStatus':'Archived financial state and matched claim returns; capital convention explicit','newReconstruction':True}
  pc['products'].append(p);cc['products'].append({'product':x['name'],'classification':'E4','address':x['address'],'chain':'Ethereum; cross-chain disclosure separate'if id=='avant'else'Ethereum','sizeETH':x['capitalETH'],'sizeUSD':x['capitalUSD'],'sizeNative':x['capitalETH'],'sizeNativeSymbol':'ETH-equivalent','sizeScope':basis,'date':T,'status':p['statusLabel'],'sourceURLs':[source],'history':x['history'],**route})
 pc['products'].sort(key=lambda p:-p['capitalETH'])
 for i,p in enumerate(pc['products']):p['rank']=i+1
 pc['rankingBasis']='Thirteen examined carry-linked books. Claim conventions differ; status and overlap are explicit.'
 holders={}
 for r in read('finalization_holder_transfers')['records']:
  assert isinstance(r['response'].get('result'),list)
  balances=defaultdict(int)
  for log in r['response']['result']:
   amount=int(log['data'],16);sender='0x'+log['topics'][1][-40:];receiver='0x'+log['topics'][2][-40:]
   if int(sender,16):balances[sender]-=amount
   if int(receiver,16):balances[receiver]+=amount
  assert all(v>=0 for v in balances.values())
  positive={a:v for a,v in balances.items()if v};id='lido-earn'if r['label'].startswith('lidoEarn')else'avant';p=next(x for x in pc['products']if x['id']==id);supply=sum(positive.values());expected=e.n('lido_share_manager_totalSupply',0)if id=='lido-earn'else e.n('avETH_snapshot_totalSupply()',0)
  assert supply==expected
  rate=Decimal(str(p['charts']['returnVsBorrow']['windowReturns'][0]['endBookPrice']))if id=='lido-earn'else Decimal(1)
  bucketRows=[]
  for label,lo,hi in [('Below 1 ETH',0,1),('1 to 10 ETH',1,10),('10 to 100 ETH',10,100),('100 to 1,000 ETH',100,1000),('1,000 ETH and above',1000,float('inf'))]:
   items=[(a,v)for a,v in positive.items()if lo<=float(Decimal(v)/10**18*rate)<hi];total=sum(v for a,v in items)
   bucketRows.append({'date':T,'chain':'Ethereum','bucket':label,'holders':len(items),'shares':float(Decimal(total)/10**18),'capitalETH':float(Decimal(total)/10**18*rate),'shareOfSupplyPct':total*100/supply,'sourceURLs':['https://etherscan.io/address/'+p['sources'][1]['url'].split('/')[-1]],'scope':'Positive issued-token balances, not beneficial investor identities; allocated unclaimed shares excluded.'})
  top=[{'chain':'Ethereum','address':a,'shares':float(Decimal(v)/10**18),'capitalETH':float(Decimal(v)/10**18*rate),'shareOfSupplyPct':v*100/supply,'url':'https://etherscan.io/address/'+a}for a,v in sorted(positive.items(),key=lambda x:-x[1])[:10]]
  scope='All Transfer events from block 0 through T reconcile exactly to archived issued totalSupply. Contracts count as addresses, not people. '+('The outer book additionally includes 788.324 allocated, unclaimed shares; these are outside the issued-token distribution.'if id=='lido-earn'else'Issuer face-token ownership is different from savETH senior-tranche ownership.')
  p['charts']['walletDistribution'].update(rows=bucketRows,topHolders=top,holderCounts={'Ethereum':len(positive)},supplyReconciled=True,scope=scope)
  p['keyMetrics'][1].update(value=f'{len(positive):,} on Ethereum',numeric=len(positive),scope=scope)
  holders[id]={'count':len(positive),'issuedSupplyRaw':str(supply),'positiveBalancesRaw':{a:str(v)for a,v in positive.items()},'scope':scope,'transferCapture':r['capture']}
 out['topFiveHolderReconstruction']=holders
 save('finalization_reconstruction',out)
 save('reader_product_chapters',pc);save('reader_carry_category',cc)
 coverage=read('carry_coverage_audit')
 for r in coverage['reviewedCases']:
  match=next((p for p in out['newProducts']if p['name'].split()[0].lower()in r['product'].lower()),None)
  if match:r.update(counted=True,decision='Fixed-block dollar funding route confirmed; included in the examined product census.',evidence=DETAILS[match['id']]['text'])
 coverage['documentedRoutes']=[];save('carry_coverage_audit',coverage)
 return out
if __name__=='__main__':augment()
