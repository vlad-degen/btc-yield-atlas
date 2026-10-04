"""Offline numerical and evidence verification for the bounded ETH deep layer."""
import hashlib,json,math,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];RAW=ROOT/'raw/eth/strategy-universe-deep-2026-10-04';checks=0

def check(label,value):
 global checks
 checks+=1
 if not value:raise AssertionError(label)
def close(label,a,b,tol=1e-9):check(label,abs(a-b)<=tol)
d=json.loads((ROOT/'data/eth/strategy_universe_deep.json').read_text());m=json.loads((ROOT/'data/eth/strategy_universe_deep_manifest.json').read_text());ps={x['id']:x for x in d['products']}
for x in m['inputs']+m['outputs']:
 p=ROOT/x['path'];check('exists '+x['path'],p.is_file());check('hash '+x['path'],hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'])
check('fixed snapshot',d['snapshot']['timestamp']==1790985599 and d['snapshot']['ethereumBlock']==26108081);check('quote offset declared',d['snapshot']['quoteOffsetSeconds']==1)
check('six non-additive marks',len(ps)==6 and all(x['additiveAcrossProducts']is False for x in ps.values()))
check('no historical payout invention',d['coverage']['paidCashReceiptsAdded']==0 and all(x['paidCashReceipt']is False for p in ps.values()for x in p['exitTests']))
bench=d['benchmarks'][0];bh={x['timestamp']:x for x in bench['history']};check('13 exact benchmark states',len(bh)==13)
for p in ps.values():
 close('USD translation '+p['id'],p['capitalUSD'],p['capitalETH']*d['snapshot']['ETH_USD'],1e-6)
 for path in p['sourcePaths']:check('numeric evidence '+p['id']+'/'+path,(ROOT/path).is_file())
 for h in p['history']:
  check('no post-T history',h['timestamp']<=d['snapshot']['timestamp']);check('actual header before target',h['observedBlockTimestamp']<=h['timestamp']);check('bounded target/block lag',h['targetMinusBlockSeconds']<=12)
  if h['ethPerShare']is not None:
   b=bh[h['timestamp']];check('same block '+p['id']+h['date'],b['block']==h['block'])
  if h['status'].startswith('absent'):check('absence not zero',h['capitalETH']is None and h['ethPerShare']is None)
 for w in p['windowReturns']:
  a=next(x for x in p['history']if x['date']==w['startDate']);z=next(x for x in p['history']if x['date']==w['endDate']);br=(bh[z['timestamp']]['ethPerShare']/bh[a['timestamp']]['ethPerShare']-1)*100
  close('measured window '+p['id'],w['bookReturnPct'],(z['ethPerShare']/a['ethPerShare']-1)*100);close('matched benchmark '+p['id'],br,w['benchmarkBookReturnPct']);close('excess pp '+p['id'],w['bookExcessPercentagePoints'],w['bookReturnPct']-br);check('not annualized '+p['id'],w['annualized']is False)
  check('window days '+p['id'],w['windowDays']==(z['timestamp']-a['timestamp'])/86400)
 for x in p['exitTests']:
  close('request denominator '+p['id'],x['requestedAssetsWETH'],p['capitalETH']*x['requestedPctNAV']/100,1e-9);check('caller stated '+p['id'],bool(re.fullmatch('0x[0-9a-f]{40}',x['caller'])));check('simulation labelled '+p['id'],'read-only' in x['status'])
y=ps['yearn_weth'];close('Yearn exact four-strategy reconciliation',sum(x['bookWETH']for x in y['state']['allocations'])+y['state']['idleWETH'],y['capitalETH']);loop=y['state']['sparkLooper'];close('loan LTV cross-check',loop['currentLTV_pct'],100*loop['oracleDebtUSD']/loop['oracleCollateralUSD'],1e-6);close('loan leverage cross-check',loop['currentLeverage'],loop['oracleCollateralUSD']/(loop['oracleCollateralUSD']-loop['oracleDebtUSD']),1e-5)
check('fourth strategy not default queue',len(y['state']['allocations'])==4 and next(x for x in y['state']['allocations']if'Looper'in x['name'])['inDefaultWithdrawalQueue']is False)
check('Yearn actual fees',y['fees']['managementFee_pct']==0 and y['fees']['performanceFee_pct']==10);check('auto actual zero fees',ps['autoeth']['fees']['periodicFee_bps']==0 and ps['autoeth']['fees']['streamingFee_bps']==0);check('osETH controller fee',ps['oseth']['fees']['controllerRewardFee_pct']==5)
s=ps['meth']['state'];c=s['bufferCashflowCounters'];close('buffer net income',c['grossInterestClaimedETH']-c['feesCollectedETH'],c['netInterestToppedUpETH']);close('queue native cash',s['queueAllocatedCumulativeETH']-s['queueClaimedCumulativeETH'],s['queueNativeETH'],1e-8);close('queue deficit',s['queueRequestedCumulativeETH']-s['queueAllocatedCumulativeETH'],s['queueFundingDeficitETH'],1e-8)
check('buffer getter not native cash',s['bufferAvailableGetterETH']==20000 and s['bufferNativeETH']==0);check('buffer fee',ps['meth']['fees']['bufferInterestFee_pct']==10)
yb=ps['yb_weth_pool'];close('pool classes netted',yb['state']['stakedBookETH']+yb['state']['unstakedBookETH'],yb['capitalETH']);check('allocation not debt',yb['state']['stablecoinAllocated']!=yb['state']['loan']['debtCrvUSD'])
a=ps['autoeth'];tests={x['requestedPctNAV']:x for x in a['exitTests']};check('1/10 accepted 30 rejected',all(tests[i]['returnedShares']is not None for i in[1,10])and tests[30]['returnedShares']is None);check('specific pricing revert',tests[30]['decodedError']['name']=='PositivePriceRecoupNotCovered(uint256)');check('nonzero modeled unwind cost despite zero fees',tests[10]['simulatedSharesAboveBook_pct']>0)
check('cmETH principal qualified','Nominal'in ps['cmeth']['capitalScope']and'Not a reconstructed'in ps['cmeth']['capitalScope'])
article=ROOT/'research/eth/review/STRATEGY-UNIVERSE-DEEP.md';check('reader article',article.is_file());text=article.read_text();check('human punctuation','\u2013'not in text and'\u2014'not in text)
for ref in re.findall(r'\]\(([^)]+)\)',text):
 if not ref.startswith(('http://','https://','#')):check('article local link '+ref,(article.parent/ref).resolve().is_file())
print('PASS',checks,'checks')

report={'status':'passed','checks':checks,'datasetSHA256':hashlib.sha256((ROOT/'data/eth/strategy_universe_deep.json').read_bytes()).hexdigest(),'snapshot_timestamp':d['snapshot']['timestamp'],'scope':'Captured evidence, matched-block share benchmarks, financing and withdrawal accounting; no complete investor return or global market claim.'}
(ROOT/'data/eth/strategy_universe_deep_verification.json').write_text(json.dumps(report,indent=2)+'\n')
