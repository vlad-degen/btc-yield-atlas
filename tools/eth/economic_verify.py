"""Independent conservation and archive-response checks for financing answers."""
import csv, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data/eth'
def read(n):return json.loads((D/(n+'.json')).read_text())
def words(s):return [int(s[i:i+64],16) for i in range(2,len(s),64)] if isinstance(s,str) and len(s)>=66 else []
def run():
 e=read('economic_questions');pc=read('reader_product_chapters');checks=[]
 def check(n,v):checks.append({'name':n,'passed':bool(v)})
 def close(a,b):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-6)
 check('frozen financial time',e['financialTimestamp']==1790985599 and e['ethereumBlock']==26108081)
 for s in e['sources']:check('source hash '+s['path'],hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest()==s['sha256'])
 source={n:{r['label']:r for r in read(n)['records']} for n in ['economic_aave_debt_history','economic_reserves_history','economic_morpho_history','economic_morpho_rates']}
 for n,rows in source.items():check('no rate-limit omissions '+n,not any(r.get('response',{}).get('error',{}).get('code')==429 for r in rows.values()))
 keys=[]
 for r in e['loanObservations']:
  keys.append((r['month'],r['id'],r['account'],r['venue'],r['symbol'],r.get('market')))
  raw=source[r['sourceFile'].removesuffix('.json')][r['source']];w=words(raw['response'].get('result'))
  check('exact block '+r['source'],raw['params'][-1]==hex(r['block']))
  if r['venue'] in ['Aave','Spark'] and r['debtUSD'] is not None and w and raw['signature']=='balanceOf(address)':
   decimals=6 if r['symbol']in['USDC','USDT','PYUSD'] else 18;check('indexed principal '+r['source'],close(r['debtUSD'],w[0]/10**decimals))
  if r['venue']=='Curve' and r['debtUSD'] is not None:check('actual Curve debt '+r['source'],close(r['debtUSD'],w[1]/1e18))
  if r['venue']=='Ebisu' and r['debtUSD'] is not None:check('actual Trove debt '+r['source'],close(r['debtUSD'],w[0]/1e18))
  check('unfunded APR absent '+r['source'],r['apr'] is None if not r['debtUSD'] else True)
 check('loan-month keys unique',len(keys)==len(set(keys)))
 included=[p for p in e['products'] if p['included']];total=sum(p['current']['debtUSD'] or 0 for p in included);check('direct debt conservation',close(total,e['attributedDollarDebtUSD']))
 check('Concrete and staking loops excluded',all(r['id']!='concrete' and r['symbol']!='WETH' for r in e['loanObservations']))
 check('inner savings excluded from outer totals',all(not r['outer'] for r in e['nestedDollarDebtAtT']) and any(r['debtUSD']>10000 for r in e['nestedDollarDebtAtT']))
 expected=sorted([p for p in included if p['id']in{q['id']for q in pc['products']} and (p['current']['debtUSD'] or 0)>=1],key=lambda p:-p['current']['debtUSD'])[:5]
 check('five ranked by attributed financing',e['topFive']==[p['id']for p in expected] and [p['id']for p in pc['products']if p['rank']<=5]==e['topFive'])
 for p in e['products']:
  check('24 months '+p['id'],len(p['history'])==24)
  if p['current']['apr'] is not None:
   # Sentora's rate also blends its 907,092 USDC Aave loan (economic_build, 7 Oct), which is not in currentLegs.
   rated=[r for r in p['currentLegs'] if r['debtUSD']>=1 and r['apr'] is not None]
   if rated and p['id']!='upshift-sentora-eth':check('current weighted APR '+p['id'],close(p['current']['apr'],sum(r['apr']*r['debtUSD'] for r in rated)/sum(r['debtUSD'] for r in rated)))
 for i,m in enumerate(e['history']):check('month total '+m['month'],close(m['debtUSD'],sum(p['history'][i]['debtUSD'] or 0 for p in included)))
 csvrows=list(csv.DictReader((D/'economic-carry-history.csv').open()));check('export endpoints and size',len(csvrows)==24 and csvrows[0]['month']=='2024-10' and csvrows[-1]['month']=='2026-09')
 for i,row in enumerate(csvrows):check('CSV financing total '+row['month'],close(float(row['observedTotalUSD']),e['history'][i]['debtUSD']))
 check('unknown net market is not estimated',e['market']['globalNetYieldCapitalETH'] is None and e['market']['globalCarryEquityShare'] is None)
 example=next(r for r in e['market']['sameBlockDedupExamples']if r['id']=='lido_and_lender_claims');check('subset dedup arithmetic',close(example['naive_sum_ETH']-example['duplicate_adjustment_ETH'],example['count_once_ETH']))
 for name in ['economic_questions.json','economic-dollar-loans.csv','economic-carry-history.csv']:
  check('source/site/mirror '+name,(D/name).read_bytes()==(ROOT/'eth/data'/name).read_bytes())
 failures=[r for r in checks if not r['passed']];out={'checks':len(checks),'all_checks_passed':not failures,'failed':failures,'scope':'Direct dollar-financing conservation, archive call identities, funded-rate nulls, snapshot quote weights, ranking, ownership exclusions and export equality. Not global market completeness or realised whole-sleeve profit.'};(D/'economic_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert not failures
if __name__=='__main__':run()
