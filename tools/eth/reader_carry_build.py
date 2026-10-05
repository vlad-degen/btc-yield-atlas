"""Add the previously measured ETH LT carry book without rewriting source ledgers."""
import copy,datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data/eth'
T=1790985599;DATE='2026-10-02T23:59:59Z'
def run():
 read=lambda n:json.loads((D/(n+'.json')).read_text())
 candidate=copy.deepcopy(read('carry_category_candidates'));chapters=copy.deepcopy(read('product_chapters'))
 deep=next(p for p in read('strategy_universe_deep')['products'] if p['id']=='yb_weth_pool')
 contract=deep['contract'];url='https://etherscan.io/address/'+contract+'#code'
 docs='https://docs.yieldbasis.com/';state=deep['state']
 holders=read('yb_LT_holders_T')
 assert holders['reconciled'] and holders['timestamp']==T and holders['contract']==contract
 assert abs(sum(r['shares'] for r in holders['addresses'])-deep['shareSupply'])<1e-7
 holder_scope=holders['scope']+'. Gauge beneficiaries are not counted separately.'
 buckets=[]
 for label,lower,upper in [('Below 1 ETH',0,1),('1 to 10 ETH',1,10),('10 to 100 ETH',10,100),('100 to 1,000 ETH',100,1000),('1,000 ETH or more',1000,float('inf'))]:
  members=[r for r in holders['addresses'] if lower<=r['shares']*deep['ethPerShare']<upper]
  shares=sum(r['shares'] for r in members)
  buckets.append({'date':DATE,'chain':'Ethereum','bucket':label,'holders':len(members),'shares':shares,'capitalETH':shares*deep['ethPerShare'],'shareOfSupplyPct':100*shares/holders['totalShares'],'sourceURLs':[url],'scope':holder_scope})
 top_holders=[{'date':DATE,'chain':'Ethereum',**r,'capitalETH':r['shares']*deep['ethPerShare'],'shareOfSupplyPct':100*r['shares']/holders['totalShares'],'url':'https://etherscan.io/address/'+r['address']} for r in holders['addresses'][:10]]
 raw=ROOT/'raw/eth/parity-sweep-2026-10-05/yb_monthly_frozen.json';capture=json.loads(raw.read_text())
 records=capture['records'];words=lambda r:[int(r[i:i+64],16) for i in range(2,len(r),64)] if r and r!='0x' else []
 prices={r['timestamp']:r['price_USD'] for r in candidate['historical_price_references'] if r['timestamp']<T}
 history=[]
 for ts in sorted(prices):
  get=lambda sig:next(r for r in records if r.get('timestamp')==ts and r.get('signature')==sig)['response'].get('result')
  code=next(r for r in records if r.get('timestamp')==ts and r['method']=='eth_getCode')['response'].get('result')
  supply=words(get('updated_balances()'));mark=words(get('pricePerShare()'))
  absent=code=='0x';valid=bool(supply and mark and code and not absent)
  # updated_balances returns total and staked effective supply. Raw supply can
  # lag fee accrual, so it cannot substitute for the first word here.
  shares=supply[0]/1e18 if valid else None;pps=mark[0]/1e18 if valid else None
  capital=shares*pps if valid else None
  date=datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).isoformat().replace('+00:00','Z')
  history.append({'date':date,'month':date[:7],'timestamp':ts,'sizeETH':capital,'sizeUSD':capital*prices[ts] if valid else None,'sizeNative':capital,'sizeNativeSymbol':'WETH','shareSupply':shares,'ethBookPrice':pps,'status':'not_deployed' if absent else 'deployed_observed' if valid else 'no_observation','sourceURLs':[url],'sourcePath':str(raw.relative_to(ROOT))})
 whole={'product':'YieldBasis WETH','classification':'E4','classificationDate':'2026-10-05','classificationStatus':'dollar-financed liquidity: actual crvUSD debt measured','chain':'Ethereum','address':contract,'collateral':'WETH/crvUSD Curve liquidity','debt':'crvUSD','destination':'Leveraged WETH/crvUSD liquidity; fees and optional gauge rewards','sizeETH':deep['capitalETH'],'sizeUSD':deep['capitalUSD'],'sizeScope':'Whole LT pool net oracle book; staked and unstaked claims are the same capital','date':DATE,'status':'Active pool; crvUSD debt is 99.996% of oracle book equity','sourceURLs':[docs,url],'history':history}
 candidate['products'].append(whole)
 candidate['category_capital_total_ETH']=sum(p['sizeETH'] or 0 for p in candidate['products'] if p['classification']=='E4')
 candidate['category_capital_total_USD']=sum(p['sizeUSD'] or 0 for p in candidate['products'] if p['classification']=='E4')
 candidate['reader_extension']={'source':'strategy_universe_deep','monthly_capture_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'reason':'BTC classification parity; existing frozen actual-dollar-loan evidence'}
 # Answer the BTC chapter's same operational questions in the visible mechanics.
 # Additional explanations use the existing fixed-block chapters and exit study.
 mechanics={
 'concrete':[
 ('Mark the claim in ETH','The weETH unit share price is flat in the captured history. Its growth in ETH follows weETH’s staking conversion; that does not independently establish arbitrage profit.'),
 ('Separate ownership from custody','A large shared-wallet balance is not Delta’s beneficial asset allocation. Even attributing every captured visible asset leaves $339.41M of the $820.03M book unmapped; this is an evidence gap, not an established loss.'),
 ('Identify the fee controller','The configured outer management and performance fees are zero at T. The active vault-manager Safe can update fees; private strategy or service charges are not established.'),
 ('Request an exit','The examined 1%, 10% and 30% requests queue in snapshot simulations. Acceptance does not pay the investor. No receipt-verified historical payout was established for the examined wrapper route.')],
 'liquid':[
 ('Separate loan currencies','The main Aave loop owes WETH and has HF 1.027. It multiplies staking exposure. Dollar-carry loans must instead be tested against the ETH/USD collateral price and the specific debt token.'),
 ('Pay for the funding','The modeled RLUSD loan costs 4.30% annually. The separately dated investment quote earns 3.00% base plus 2.59% rewards. Debt / equity is 0.6436 in the worked example; base income alone does not clear funding.'),
 ('Recognize fees and share value','The outer annual NAV fee is 0.35% at T. Destination share values already recognize their own fee economics. The measured two-year 6.85% ETH book gain mixes strategies and is 1.36 pp above stETH.'),
 ('Return cash to holders','A complete exit must redeem the dollar claims, source the exact loan currencies, repay debt, release collateral and satisfy the share queue. Whole-book NAV is not an immediate-cash limit.')],
 'rocksolid':[
 ('Separate old routes from the current book','The August description is historical. At T, the examined direct Aave account has no debt, while the nested Liquity receipt retains exposure to the underlying Ebisu loan.'),
 ('Apply two sets of cash rights','The outer book includes a claim on Liquity rather than independently owned underlying collateral. Its outer 1% management and 10% performance settings are separate from underlying product fees.'),
 ('Settle the portfolio before payment','The strategy must turn nested receipts into rETH or the required settlement asset. Queue acceptance, strategy liquidity and actual investor payment are different stages.'),
 ('Read the closing state','The owner initiated Closing on 29 September. New requests fail at T. Closing does not establish final repayment, the cause of closure or the complete investor outcome.')],
 'liquity':[
 ('Look through the held LP','The held Curve gauge maps to ebUSD/USDC despite its legacy BOLDUSDC symbol. Its LP principal is reconstructed separately from the stored Uniswap V4 book; the symbol is not the debt asset.'),
 ('Identify what pays','Stablecoin swaps fund trading fees. Incentives require a funded campaign, actual payout and realization into the debt or accounting asset. An advertised LP rate is not net ETH carry income.'),
 ('Charge the outer fees','Fixed-block settings are 0.5% annual management and 10% performance. Borrower-set interest is not the entire financing cost: opening and rate-adjustment charges also matter.'),
 ('Reduce liquidity and repay ebUSD','An exit must unwind LP inventory, obtain ebUSD and repay the Trove before the wstETH collateral is released. Stablecoin discounts and thin LP liquidity can make this costly.'),
 ('Pay the investor','At T, the 1% book-demand withdrawal call succeeds while 10% and 30% fail. These are snapshot calls, separate from the receipt-verified historical payouts in the exit study.')],
 'royco':[
 ('Match the borrowing and investment currencies','The actual loan owes PYUSD, while the senior investment is USDC-denominated. Holdings alone do not trace every borrowed unit through a conversion into that receipt.'),
 ('Read the senior cash rights','Junior capital absorbs a finite first-loss amount in the published design. That protection does not eliminate underlying credit loss, currency mismatch or redemption timing.'),
 ('Separate fresh balances from stale marks','Fresh collateral, accrued debt and senior receipt balances are measured at T. Three parent position values are stale; their cached sum cannot substitute for a freshly reconciled book.'),
 ('Process the asynchronous exit','Immediate maxWithdraw is zero at T. Investment redemption, PYUSD repayment and share-queue fulfillment must be coordinated. A request or preview does not establish a paid withdrawal.')]
 }
 for product in chapters['products']:
  for title,text in mechanics[product['id']]:
   product['moneyFlow'].append({'step':len(product['moneyFlow'])+1,'title':title,'text':text,'contract':None,'url':None})
 first=next(r for r in history if r['ethBookPrice'] and r['sizeETH']>0)
 marks=[{'date':r['date'],'timestamp':r['timestamp'],'ethBookPrice':r['ethBookPrice'],'nativeBookPrice':r['ethBookPrice'],'cumulativeReturnPct':100*(r['ethBookPrice']/first['ethBookPrice']-1),'borrowAPR_pct':None,'borrowScope':'A realized product funding-cost series is unavailable','sourceURLs':[url]} for r in history if r['ethBookPrice'] and r['sizeETH']>0]
 marks.extend({'date':r['date'].replace('+00:00','Z'),'timestamp':r['timestamp'],'ethBookPrice':r['ethPerShare'],'nativeBookPrice':r['ethPerShare'],'cumulativeReturnPct':100*(r['ethPerShare']/first['ethBookPrice']-1),'borrowAPR_pct':None,'borrowScope':'A realized product funding-cost series is unavailable','sourceURLs':[url]} for r in deep['history'] if r['timestamp']>history[-1]['timestamp'] and r['ethPerShare'])
 # Include all observed recent return-window endpoints, keeping one row per date.
 marks=sorted({r['timestamp']:r for r in marks}.values(),key=lambda r:r['timestamp'])
 for r in deep['history']:
  if r.get('ethPerShare') and r['timestamp'] not in {x['timestamp'] for x in marks}:
   marks.append({'date':r['date'].replace('+00:00','Z'),'timestamp':r['timestamp'],'ethBookPrice':r['ethPerShare'],'nativeBookPrice':r['ethPerShare'],'cumulativeReturnPct':100*(r['ethPerShare']/first['ethBookPrice']-1),'borrowAPR_pct':None,'borrowScope':'Funding cost not isolated','sourceURLs':[url]})
 marks.sort(key=lambda r:r['timestamp']);windows=[]
 for days in [7,14,30]:
  start=next((r for r in marks if r['timestamp']==T-days*86400),None)
  if start:windows.append({'date':DATE,'startDate':start['date'],'windowDays':days,'cumulativeReturnPct':100*(deep['ethPerShare']/start['ethBookPrice']-1)})
 windows.extend({'date':DATE,'startDate':w['startDate'].replace('+00:00','Z'),'windowDays':w['windowDays'],'cumulativeReturnPct':w['bookReturnPct'],'benchmarkBookReturnPct':w.get('benchmarkBookReturnPct')} for w in deep['windowReturns'])
 admin=words(next(r for r in records if r['label']=='yb_T_admin()')['response'].get('result'))
 admin='0x'+format(admin[0],'040x') if admin else None
 steps=[
 ('Enter the LT pool','Deposit WETH and receive LT shares. The receipt represents net pool equity after its crvUSD liability.',contract),
 ('Borrow the dollar leg','The pool borrows crvUSD to supply both sides of WETH/crvUSD liquidity. Actual debt at T is 27,814,855.84 crvUSD, separate from the 64.14M allocation limit.',state['amm']),
 ('Maintain ETH exposure','The design uses roughly 2x gross liquidity versus equity. Automated debt adjustment seeks to keep the net payoff tied to WETH as the ETH price moves.',state['amm']),
 ('Earn trading fees','Swaps pay liquidity-provider fees. Financing, rebalancing and administration consume part of that income. A high gross LP yield is not a net ETH return.',state['amm']),
 ('Choose whether to stake','Staking LT shares in the gauge changes the fee-allocation and reward rights. At T, 5,875 ETH of net book is staked and 4,551 ETH is unstaked. These sum to one pool.',state['gauge']),
 ('Apply the fee mechanism','The minimum admin parameter is 10%. Actual fee allocation varies through the contract mechanism; it is not a flat 10% deduction from every holder’s gain.',contract),
 ('Mark the investor claim','Use updated effective supply and fair ETH value per LT unit. The unstaked mark fell 0.69% over 94 days while stETH gained 0.57%; this excludes external gauge rewards.',contract),
 ('Unwind and repay','Withdrawal removes liquidity, settles the crvUSD loan and releases WETH. The snapshot previews quote 104, 1,043 and 3,128 WETH for 1%, 10% and 30% of raw supply; no paid exit is established by a preview.',contract)]
 p={'id':'yieldbasis','rank':3,'name':'YieldBasis WETH','subtitle':'Dollar-financed liquidity, with automated leverage adjustment','classification':'E4','capitalETH':deep['capitalETH'],'capitalUSD':deep['capitalUSD'],
 'keyMetrics':[{'label':label,'value':value,'date':DATE,'scope':scope} for label,value,scope in [
 ('Capital at snapshot','10,426 ETH / $27.82M','Net fair-value pool book'),('Holder addresses at snapshot',str(holders['holderCount']),holder_scope),('Fees','10% minimum admin parameter','Variable allocation, not a flat investor fee'),('Contract deployment','Absent on 30 Apr; funded by 31 May 2026','Sampled block observations, not launch date'),('Observed 30-day ETH book return',f"{windows[2]['cumulativeReturnPct']:+.2f}%",'Unstaked fair mark; external rewards excluded'),('Organic carry estimate','Not independently isolated','Fees, financing and gauge rewards need separate cash attribution')]],
 'moneyFlow':[{'step':i+1,'title':title,'text':text,'contract':a,'url':'https://etherscan.io/address/'+a+'#code'} for i,(title,text,a) in enumerate(steps)],
 'actors':[{'who':'Configured LT admin','address':admin,'url':'https://etherscan.io/address/'+admin+'#code' if admin else docs,'role':'Configured administration at T','canChange':'Pool administration and supported fee or kill controls; governance path must be read separately','delay':'A universal execution delay is not established'}, {'who':'Pool and rebalancing mechanism','address':state['amm'],'url':'https://etherscan.io/address/'+state['amm']+'#code','role':'Adjusts the dollar liability and liquidity exposure','canChange':'Execution follows the deployed contracts and current market liquidity','delay':'Execution can be immediate'}, {'who':'Gauge / reward mechanism','address':state['gauge'],'url':'https://etherscan.io/address/'+state['gauge']+'#code','role':'Separates staked receipt economics from unstaked LT units','canChange':'Gauge balances and reward allocations require their own accounting','delay':'No common exit-delay claim is made'}],
 'incomePayers':[{'payer':'WETH/crvUSD traders','text':'Swap fees fund the LP component.'},{'payer':'Gauge incentive program','text':'External incentives belong to staked claims; reward income is excluded from the unstaked mark.'}],
 'charts':{'capitalHistory':{'title':'Whole LT pool net capital','rows':history,'scope':whole['sizeScope']},'returnVsBorrow':{'rows':marks,'windowReturns':windows,'scope':deep['historyMeasure']},'walletDistribution':{'rows':buckets,'topHolders':top_holders,'scope':holder_scope+' The gauge holds 56.35% of net book; this is not 56.35% of investors.','sourcePath':'data/eth/yb_LT_holders_T.json','sourceSHA256':hashlib.sha256((D/'yb_LT_holders_T.json').read_bytes()).hexdigest()},'loanLegs':{'rows':[{'date':DATE,'chain':'Ethereum','account':contract,'protocol':'YieldBasis / Curve','collateralAsset':'Curve WETH/crvUSD LP','collateralETH':None,'collateralUSD':None,'debtAsset':'crvUSD','debtUSD':state['loan']['debtCrvUSD'],'LTV_pct':None,'liquidationThreshold_pct':None,'healthFactor':None,'borrowAPR_pct':None,'classification':'E4','sourceURLs':[url,docs],'scope':'Actual crvUSD liability at nominal $1. Debt / net book equity is 99.996%; this is not an Aave collateral LTV or health factor.'}],'scope':'Allocation capacity, actual debt and net equity are different quantities.'}},
 'timeline':[{'date':r['month'],'title':'Month-end net pool book','text':f"{r['sizeETH']:,.0f} ETH of net oracle book; observed fair-value mark, not deposits.",'url':url} for r in history if r['sizeETH'] is not None],
 'sources':[docs,url,*deep['sourceURLs']],'limitations':deep['limitations']+['External gauge rewards, a realized financing-cost series and beneficial investor identities are not reconstructed.'],
 'liveRoute':{'collateral':whole['collateral'],'debt':'crvUSD','destination':whole['destination'],'status':whole['status'],'sourceURLs':[docs,url]}}
 chapters['products'].append(p);chapters['products'].sort(key=lambda p:-p['capitalETH'])
 for i,p in enumerate(chapters['products']):p['rank']=i+1
 chapters['rankingBasis']='Five largest examined carry-design whole books; additional measured cases remain accessible. Hybrid and nested books are not unique carry equity.'
 (D/'reader_carry_category.json').write_text(json.dumps(candidate,indent=2)+'\n')
 (D/'reader_product_chapters.json').write_text(json.dumps(chapters,indent=2)+'\n')
 print('Reader carry: 8 measured books; YieldBasis actual loan and 24 archive months retained.')
if __name__=='__main__':run()
