"""A source-calculated dollar-financing ledger, never a proxy carry-equity total."""
import csv, hashlib, json, math
from pathlib import Path
from economic_capture import words,address,TOKENS
from carry_economics_build import accrue,borrow_assets
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data/eth';EN=ROOT/'research/eth/en';YEAR=31536000
def read(n):return json.loads((D/(n+'.json')).read_text())
def write(n,v):(D/(n+'.json')).write_text(json.dumps(v,indent=2)+'\n')
def rows(n):return {r['label']:r for r in read(n)['records']}
def proof(n):p=D/(n+'.json');return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def table(head,body):return '| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+''.join('| '+' | '.join(str(x).replace('|','/') for x in r)+' |\n' for r in body)
def run():
 inventory=read('economic_aave_legs'); reserves=rows('economic_reserves_history'); debts=rows('economic_aave_debt_history');months=inventory['months'];obs=[];pc=read('reader_product_chapters')
 for m in months:
  for l in inventory['legs']:
   key='|'.join([m['month'],l['id'],l['account'],l['venue'],l['symbol']]);rr=reserves[m['month']+'|'+l['venue']+'|'+l['symbol']+'|reserve'];w=words(rr['response'].get('result'));r=debts.get(key);dw=words(r['response'].get('result')) if r else []
   absent=bool(w and len(w)>10 and not w[10]);amount=dw[0]/10**TOKENS[l['symbol']][1] if dw else 0 if absent else None
   obs.append({**m,**l,'outer':True,'debtUSD':amount,'apr':w[4]/1e27 if amount and w else None,'status':'observed' if amount is not None else 'unavailable','principalBasis':'Indexed variable debt token; nominal stablecoin USD','source':r['label'] if r else rr['label'],'sourceFile':'economic_aave_debt_history.json' if r else 'economic_reserves_history.json'})
 x=read('economic_morpho_legs');mr=rows('economic_morpho_history');rates=rows('economic_morpho_rates');tokens={v[0]:(k,v[1]) for k,v in TOKENS.items()}; tokens.update({'0x8292bb45bf1ee4d140127049757c2e0ff06317ed':('RLUSD',18),'0x09d4214c03d01f49544c0448dbe3a27f768f2b34':('rUSD',18)})
 for m in months:
  for l in x['legs']:
   mid=l['market'];ps=words(mr[m['month']+'|'+mid+'|params']['response'].get('result'));mk=words(mr[m['month']+'|'+mid+'|market']['response'].get('result'));pos=words(mr['|'.join([m['month'],l['id'],l['account'].lower(),mid,'position'])]['response'].get('result'));rw=words(rates.get(m['month']+'|'+mid+'|rate',{}).get('response',{}).get('result'));ow=words(rates.get(m['month']+'|'+mid+'|oracle',{}).get('response',{}).get('result'))
   sym,dec=tokens.get(address(ps[0]),('unknown',18)) if ps and ps[0] else ('not_created',18)
   amount=0 if pos and not pos[1] else borrow_assets(pos[1],mk[2]+accrue(mk,rw[0],m['timestamp']),mk[3])/10**dec if pos and mk and rw else None
   collateral=pos[2]*ow[0]/10**36/10**dec if pos and ow else None
   obs.append({**m,**l,'account':l['account'].lower(),'venue':'Morpho','symbol':sym,'debtUSD':amount,'collateralUSD':collateral,'apr':rw[0]/1e18*YEAR if amount and rw else None,'status':'observed' if amount is not None else 'unavailable','principalBasis':'Borrow shares converted with virtual accrual; nominal USD','source':'|'.join([m['month'],l['id'],l['account'].lower(),mid,'position']),'sourceFile':'economic_morpho_history.json'})
  y=words(mr[m['month']+'|yieldbasis|get_state']['response'].get('result'));yr=words(mr[m['month']+'|yieldbasis|rate']['response'].get('result'));tv=words(mr[m['month']+'|liquity|trove']['response'].get('result'))
  # Undeployed AMM calls return empty, not proof of zero active capital.
  for pid,a,apr,venue,symbol in [('yieldbasis',y[1]/1e18 if y else None,yr[0]/1e18*YEAR if yr else None,'Curve','crvUSD'),('liquity',tv[0]/1e18 if tv else None,tv[6]/1e18 if tv and len(tv)>6 else None,'Ebisu','ebUSD')]:
   obs.append({**m,'id':pid,'outer':True,'account':next(p for p in pc['products'] if p['id']==pid)['charts']['loanLegs']['rows'][0]['account'].lower(),'venue':venue,'symbol':symbol,'debtUSD':a,'apr':apr if a else None,'status':'observed' if a is not None else 'unavailable','principalBasis':'Accrued contract debt at nominal dollar parity','source':m['month']+'|'+pid+'|'+('get_state' if pid=='yieldbasis' else 'trove'),'sourceFile':'economic_morpho_history.json'})
 def summarize(rr):
  known=[r for r in rr if r['debtUSD'] is not None]; total=sum(r['debtUSD'] for r in known); rated=[r for r in known if r['debtUSD']>=1 and r['apr'] is not None];rd=sum(r['debtUSD'] for r in rated)
  return {'debtUSD':total if known else None,'apr':sum(r['debtUSD']*r['apr'] for r in rated)/rd if rd else None,'ratedDebtUSD':rd,'observedLegs':len(known),'expectedLegs':len(rr),'fundedLegs':sum(r['debtUSD']>=1 for r in known),'allObserved':len(known)==len(rr)}
 products=[]
 for pid in sorted(set(r['id'] for r in obs)):
  rr=[r for r in obs if r['id']==pid and r['outer']];p=next((p for p in pc['products'] if p['id']==pid),None); name=p['name'] if p else next((r.get('name') for r in rr if r.get('name')),{'tau-infinifi':'TAU InfiniFi ETH Carry','reservoir-eth':'Reservoir ETH Yield'}.get(pid,pid));h=[{**m,**summarize([r for r in rr if r['month']==m['month']])} for m in months];t=h[-1]
  products.append({'id':pid,'name':name,'bookETH':p['capitalETH'] if p else None,'bookUSD':p['capitalUSD'] if p else None,'attribution':'operator-associated, not included in attributed total' if pid.startswith('upshift-') else 'attributed product account / direct loan','included':not pid.startswith('upshift-'),'current':t,'history':h[:-1],'currentLegs':[r for r in rr if r['month']=='snapshot']})
 # 7 Oct per-asset archive reads (tools/eth/gap_top5_risk, data/eth/gap_top5_risk_series.csv) replace the month-end
 # dollar debt of three products: Lido Earn's USDe/sUSDe loop is not ETH-backed carry and its USDC/USDe legs were missing;
 # Avant and Liquity had funded months the leg inventory missed.
 gap=ROOT/'data/eth/gap_top5_risk_series.csv'
 if gap.exists():
  g={}
  for r in csv.DictReader(gap.open()):
   if r['metric'] in ('dollar_debt_usd','borrow_rate_debt_weighted'):g[(r['product'],r['metric'],r['period'])]=float(r['value'])
  for p in products:
   if p['id'] not in ('lido-earn','avant','liquity'):continue
   for h in p['history']:
    d=g.get((p['id'],'dollar_debt_usd',h['month']))
    if d is not None:h.update(debtUSD=d,apr=g.get((p['id'],'borrow_rate_debt_weighted',h['month'])) if d>=1 else None,source='gap_top5_risk_series.csv')
 # 7 Oct reconstruction (data/eth/gap_rocksolid_upshift.json): NEMO ETH Prime and Sentora ETH books reconcile only with
 # their loans inside, so the loans are attributed; Sentora also has a 907,092 USDC Aave loan; Rocksolid's second wallet
 # borrows USDC on Morpho against rETH.
 gr=ROOT/'data/eth/gap_rocksolid_upshift.json'
 if gr.exists():
  G=json.loads(gr.read_text())
  for p in products:
   if p['id'].startswith('upshift-'):p.update(included=True,attribution='attributed product account / direct loan (vault book reconciles with the loan)')
   if p['id']=='upshift-sentora-eth':
    c=p['current'];d0=c['debtUSD'] or 0;extra=G['attributedTotal']['addSentoraAaveUSDC_new'];c['apr']=((c['apr'] or 0)*d0+0.1393*extra)/(d0+extra);c['debtUSD']=d0+extra
  dc=G['rocksolid']['dollarCarry'];dh={r['month']:(r.get('aaveUSDC') or 0)+(r.get('morphoUSDC') or 0) for r in dc['debtHistory']}
  if not any(p['id']=='rocksolid' for p in products):
   hist=[{**m,'debtUSD':dh.get(m['month']),'apr':None,'ratedDebtUSD':0,'observedLegs':1 if m['month'] in dh else 0,'expectedLegs':1,'fundedLegs':1 if dh.get(m['month']) else 0,'allObserved':m['month'] in dh} for m in months[:-1]]
   products.append({'id':'rocksolid','name':'Rocksolid rETH','bookETH':G['rocksolid']['bookAtT']['ETH'],'bookUSD':G['rocksolid']['bookAtT']['USD'],'attribution':'attributed product account / direct loan (second strategy wallet)','included':True,'current':{**months[-1],'debtUSD':dc['directDebtUSD'],'apr':dc['debtAPR_atT'],'ratedDebtUSD':dc['directDebtUSD'],'observedLegs':1,'expectedLegs':1,'fundedLegs':1,'allObserved':True},'history':hist,'currentLegs':[]})
 products.sort(key=lambda p:-(p['current']['debtUSD'] or 0));included=[p for p in products if p['included']];total=sum(p['current']['debtUSD'] or 0 for p in included);top=[p for p in included if p['id']in{q['id'] for q in pc['products']} and (p['current']['debtUSD'] or 0)>=1][:5]
 bindings=rows('economic_upshift_binding_T')
 for p in products:
  if p['id'].startswith('upshift-'):
   name=p['name'];get=lambda suffix:words(bindings.get(name+'|'+suffix,{}).get('response',{}).get('result'))
   assets=get('getTotalAssets()');updated=get('assetsUpdatedOn()');allowed=get('whitelist|'+p['currentLegs'][0]['account'])
   p['discoveryBinding']={'accountPermittedAtT':bool(allowed[0]) if allowed else None,'permissionTypeAtT':allowed[0] if allowed else None,'vaultBookAssetsETH':assets[0]/1e18 if assets else None,'markUpdatedTimestamp':updated[0] if updated else None,'source':'economic_upshift_binding_T.json','bookScope':'Vault accounting mark, not independently assigned EOA assets'}
 for p in pc['products']:
  p['sampleBookRank']=p['rank'];p['rank']=next((i+1 for i,q in enumerate(top) if p['id']==q['id']),6+p['sampleBookRank']);p['financing']=next((q for q in products if p['id']==q['id']),None)
  if p['financing']:
   for l in p['charts']['loanLegs']['rows']:
    venue='Spark' if 'Spark' in l['protocol'] else 'Aave' if 'Aave' in l['protocol'] else 'Morpho' if 'Morpho' in l['protocol'] else 'Curve' if p['id']=='yieldbasis' else 'Ebisu'
    match=next((r for r in p['financing']['currentLegs'] if r['account']==l['account'].lower() and r['venue']==venue and (r['symbol']==l['debtAsset'] or r['symbol']=='ebUSD' and l['debtAsset'].startswith('ebUSD')) and (venue!='Morpho' or any(r['market'] in u for u in l.get('sourceURLs',[])))),None)
    if match and match['apr'] is not None:l['borrowAPR_pct']=match['apr']*100
 pc['products'].sort(key=lambda p:p['rank']);pc['rankingBasis']='Five largest attributed active direct-dollar loan books in the examined product census; loan balances, not total vault NAV or global carry equity.';write('reader_product_chapters',pc)
 exclusions=[{'item':'Concrete Delta weETH','reason':'Shared Safe debt cannot be assigned to Delta; excluded from attributed totals and top five.','dollars':105736216.10060266},{'item':'Liquid PRIME / PYUSD','reason':'Inner dollar-credit collateral financing; excluded from direct ETH-backed total.','dollars':21017993.331603},{'item':'ETH-debt staking loops','reason':'WETH loans multiply staking exposure; never included as dollar carry.','dollars':None},{'item':'Rocksolid Liquity shares','reason':'A nested claim on the included Liquity book; underlying loan counted once.','dollars':None}]
 known_nested=[r for r in obs if not r['outer'] and r['month']=='snapshot'];history=[]
 for i,m in enumerate(months[:-1]):
  vals=[p['history'][i] for p in included];history.append({**m,'debtUSD':sum(r['debtUSD'] or 0 for r in vals),'observedProducts':sum(r['debtUSD'] is not None for r in vals),'allLegsObservedProducts':sum(r['allObserved'] for r in vals),'expectedProducts':len(vals)})
 panel=read('market_reader_chapter'); default=[p for p in panel['products'] if p['category'] in [c['id'] for c in panel['categories'] if c['default']] and p['current']['status']=='observed'];gross=sum(p['current']['eth_ref'] for p in default);grossUSD=sum(p['current']['usd'] for p in default);netting=read('market_netting_closure');example=netting['dedup_examples']
 snapshots=[proof(n) for n in ['economic_aave_legs','economic_reserves_history','economic_aave_debt_history','economic_morpho_legs','economic_morpho_history','economic_morpho_rates','economic_upshift_eth_registry','economic_upshift_positions_T','economic_upshift_binding_T','market_reader_chapter','market_netting_closure']]
 out={'schemaVersion':1,'financialTimestamp':1790985599,'financialDate':'2026-10-02T23:59:59Z','ethereumBlock':26108081,'scope':'Tracked direct ETH-backed dollar financing of public ETH yield products. Current route inventory backcast at month ends; closed alternate markets not exhaustively recovered. It is outstanding debt, not TVL, equity, outside deposits or use-of-proceeds cash attribution. Stablecoins are nominal USD.','products':products,'loanObservations':obs,'history':history,'attributedDollarDebtUSD':total,'topFive':[p['id'] for p in top],'topTwoDebtShare':sum(p['current']['debtUSD'] for p in top[:2])/total,'nestedDollarDebtAtT':known_nested,'excluded':exclusions,'market':{'defaultGrossETHReference':gross,'defaultGrossUSD':grossUSD,'defaultObservedProtocols':len(default),'globalNetYieldCapitalETH':None,'globalCarryEquityShare':None,'sameBlockDedupExamples':example},'sources':snapshots,'nullPolicy':'Unavailable calls and unfunded loan-rate periods stay absent. Predeployment call failures are not treated as measured zero debt.'}
 write('economic_questions',out)
 with (D/'economic-dollar-loans.csv').open('w') as f:
  keys=['month','timestamp','block','id','account','venue','symbol','outer','debtUSD','collateralUSD','apr','status','sourceFile','source'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(obs)
 with (D/'economic-carry-history.csv').open('w') as f:
  keys=['month','timestamp','block']+[p['id'] for p in included]+['observedTotalUSD'];w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader()
  for i,m in enumerate(months[:-1]):w.writerow({**{k:m[k] for k in ['month','timestamp','block']},**{p['id']:p['history'][i]['debtUSD'] for p in included},'observedTotalUSD':history[i]['debtUSD']})
 editorial(out,pc)
 print('Economic answers:',round(total,2),'attributed nominal dollar debt;',len(obs),'loan-month observations; top five',out['topFive'])
 return out

def editorial(x,pc):
 body=table(['Product','Direct dollar debt at T','Debt-weighted quoted APR','Whole book ETH','Scope'],[[p['name'],f"${p['current']['debtUSD']:,.0f}" if p['current']['debtUSD'] is not None else 'Unavailable',f"{p['current']['apr']*100:.2f}%" if p['current']['apr'] is not None else 'Unavailable',f"{p['bookETH']:,.0f}" if p['bookETH'] else 'Not reconstructed',p['attribution']] for p in x['products']])
 text=f'''# ETH dollar carry: financing, ownership and economics

Financial snapshot: 2 October 2026, 23:59:59 UTC. Ethereum block 26,108,081. Later discovery documents are dated separately.

## What the category actually contains

The attributed product accounts owe **${x['attributedDollarDebtUSD']:,.0f}** of direct ETH-backed dollar debt at the snapshot. This measures financing, not carry equity. Whole hybrid vault books contain other strategies, while outstanding debt includes accrued interest and can differ from dollars invested. The top two account for **{x['topTwoDebtShare']*100:.2f}%** of this measured financing sample, not the global ETH yield market.

{body}

## The corrected historical comparison

Twenty-four month-end samples now reconstruct actual dollar liabilities and funded financing quotes. The series excludes ETH-debt loops, duplicate nested product claims and unassigned Concrete debt. Inner savings loans remain in the full loan ledger with `outer=false`; they do not inflate the direct ETH-backed chart. The inventory follows markets identified by the present and historical research, so earlier alternate or retired markets can remain missing. An empty call is not a measured zero. Rates are debt-weighted month-end model quotes, not paid monthly average costs.

[Monthly loan observations](../../../data/eth/economic-dollar-loans.csv) and [product financing bars](../../../data/eth/economic-carry-history.csv) contain the account, currency, block and source labels. The existing whole-book histories remain in product chapters. They are not relabelled as carry allocation history.

## Why Concrete is outside the verified five

Its 307,363 ETH book is a manager-issued claim. The shared strategy Safe has dollar loans, but the records do not assign its backing or debt wholly to Delta. The initial mint is not an underlying deposit transfer. Counting the entire claim as measured carry would conflate issuance with beneficial ownership. The case and its full evidence remain accessible.

## Funding is a separate unit from ETH return

A cumulative ETH book return cannot be reduced by an annual dollar loan quote. A cash spread needs identical dollar principal, dates, investment income, interest and costs. The matched cash ledgers include four financed lots and two flow-adjusted claim/funding records. Lido's 5M USDT lot earns a positive recognised margin over 29 September to the snapshot, before gas and outer fees. Vesper's vDAI accrual falls short of its DAI cost. These narrow results are not whole-product organic annual yields.

For Liquid, the larger controlled Aave USDC debt matters alongside the lower-rate RLUSD markets. Its weighted dollar funding cost differs materially from quoting the RLUSD route alone. Destinations, rewards and fees must be assigned per loan before estimating the whole carry sleeve's income. [Source-calculated ledger](../../../data/eth/economic_questions.json).

## Additional manager routes

The full official Upshift registry was examined after finding Sentora ETH's documented weETH/RLUSD route. Archive calls also establish NEMO-associated wstETH/USDC debt. Vault permissions and manager-associated accounts are disclosed separately; permission to use an account is not a complete beneficial-ownership reconciliation. These loans are shown as associated candidates and excluded from the attributed aggregate. API NAV and APR fetched on 6 October are discovery data and never substituted for the frozen financial balances.

## Market accounting

The default protocol panel contains {x['market']['defaultObservedProtocols']} observed parents and {x['market']['defaultGrossETHReference']:,.0f} ETH equivalents of reported exposure. The headline, donut, category table and two-year bars all use that same selection. Issuer, restaking, lending and vault claims overlap; this is a protocol-exposure market map. Exact-block Lido, Aave and Spark reconciliation demonstrates the duplication numerically. Public inputs do not establish a complete global net yield-capital total or carry-equity share, and neither number is manufactured from the panel.

## Sources and reproduction

[Canonical answers](../../../data/eth/economic_questions.json), [loan CSV](../../../data/eth/economic-dollar-loans.csv), [financing history CSV](../../../data/eth/economic-carry-history.csv), [product mechanics](CARRY-PRODUCTS.md), [ownership reconciliation](CAPITAL-INCOME-EXIT.md), [product evolution](PRODUCT-EVOLUTION.md).
'''
 (EN/'ECONOMIC-ANSWERS.md').write_text(text)
 (EN/'CARRY-CATEGORY.md').write_text(text)
 selection=[next(p for p in x['products'] if p['id']==pid) for pid in x['topFive']]
 (EN/'PRODUCT-SELECTION.md').write_text('# Five attributed dollar-financing books\n\nThe main five are active public ETH products ordered by direct ETH-backed dollar debt at the snapshot. Whole vault NAV, ETH collateral and financing are disclosed separately. This is the examined census, not a certified global league table. Concrete is excluded until shared-wallet ownership is reconciled; Rocksolid overlaps Liquity; TAU is historical at the snapshot.\n\n'+table(['Rank','Product','Dollar debt','Whole book ETH'],[[i+1,p['name'],f"${p['current']['debtUSD']:,.0f}",f"{p['bookETH']:,.0f}"] for i,p in enumerate(selection)])+'\n\n[Financing, dates and sources](ECONOMIC-ANSWERS.md).\n')
 text='## Current financing comparison\n\n'+body+'\n\nThe principal five are ordered by attributed direct dollar financing. Monthly quotes and whole-book ETH returns measure different units. Concrete is an unresolved case, not a verified member of the five. [Economic answers and historical debt](ECONOMIC-ANSWERS.md).\n\n'
 for name in ['BRIEFING','CARRY-PRODUCTS']:
  path=EN/(name+'.md');old=path.read_text().split('\n<!-- economic-answers -->')[0];path.write_text((old+'\n<!-- economic-answers -->\n'+text).rstrip()+'\n')

if __name__=='__main__':run()
