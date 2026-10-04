"""Build an isolated ETH market panel from the frozen adapter observations.

Reported token balances are layered exposures, not unique capital. ETH-reference
values normalize adapter USD marks by Lido's contemporaneous implied ETH quote.
No network request, mixed-pool TVL, new financial snapshot or global net estimate.
"""
from __future__ import annotations
import csv,datetime as dt,hashlib,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'data/eth';T=1790985599;MAX_AGE=72*3600
FAMILY=set('ETH WETH STETH WSTETH EETH WEETH WEETHS RETH CBETH WBETH BETH FRXETH SFRXETH ETHX OETH WOETH METH CMETH EZETH RSETH WRSETH PUFETH SWETH RSWETH ANKRETH AETHC RETH2 SETH2 OSETH ETHPLUS ETH+ LIQUIDETH STKETH DINEROETH PXETH APXETH STONE QETH HETH TETH UNIETH VETH VBETH WETH.E ETH.E WSTETH.E AWETH AETHWETH AETHWEETH SPWSTETH'.split())
# Explicitly identified ETH receipts/debt in the captured observations. The
# AETH network prefix alone is insufficient; it also precedes stablecoin/BTC names.
EXTRA={'AETHWSTETH','AETHLIDOWSTETH','VARIABLEDEBTETHWETH','VARIABLEDEBTWETH'}
ALIASES={'OP Mainnet':'Optimism','Hyperliquid L1':'HyperEVM','Binance':'BNB Chain','BSC':'BNB Chain','xDai':'Gnosis','zkSync Era':'ZKsync Era','Klaytn':'Kaia','RSK':'Rootstock','Op_Bnb':'opBNB','Reya Network':'ReyaChain'}
CATEGORIES=[
 {'id':'staking','label':'Staking issuers','color':'#7c6ce7','default':True,'scope':'ETH-related assets reported by staking issuers; some backing can be receipt tokens issued by another protocol.'},
 {'id':'restaking','label':'Restaking layers','color':'#42a5a0','default':True,'scope':'Restaking and liquid-restaking collateral claims; overlaps staking issuers.'},
 {'id':'lending','label':'Lending and collateral','color':'#e7ae54','default':True,'scope':'Selected ETH loan assets and collateral; collateral is not necessarily earning lender interest.'},
 {'id':'liquidity','label':'Liquidity and trading pools','color':'#cf6e8a','default':True,'scope':'Selected ETH token balances in DEX, trading and bridge-liquidity protocols; excludes the non-ETH side of mixed pools.'},
 {'id':'fixed_yield','label':'Fixed-yield pools','color':'#5596cf','default':True,'scope':'ETH-related token balances visible in Pendle and Spectra adapters; not all outstanding PT principal or all SY backing.'},
 {'id':'managed','label':'Managed and yield vaults','color':'#8fa65c','default':True,'scope':'Selected ETH assets and signed ETH debts in managed/yield protocols; partial token exposure, not full product NAV or unique deposits.'},
]
read=lambda n:json.loads((DATA/(n+'.json')).read_text())
def stamp(t):return dt.datetime.fromtimestamp(t,dt.timezone.utc).isoformat().replace('+00:00','Z') if t is not None else None
def previous(a,t):return max((p for p in a if p['date']<=t),key=lambda p:p['date'],default=None)
def ratio(n,d):return n/d if d else None
def cat(p):
 if p['slug'] in ['ethena-usde','midas-rwa']:return None
 if p['slug'] in ['pendle-v2','spectra-v2']:return 'fixed_yield'
 c=p['category']
 if c=='Liquid Staking':return 'staking'
 if c in ['Restaking','Liquid Restaking','Collateral Markets']:return 'restaking'
 if c in ['Lending','CDP','Synthetics']:return 'lending'
 if c in ['Dexs','Derivatives','Cross Chain Bridge','Leveraged Farming']:return 'liquidity'
 if c in ['Yield','Yield Aggregator','Onchain Capital Allocator','Indexes','DOR']:return 'managed'
 raise ValueError((p['slug'],c))
def csv_write(name,rows,keys):
 with (DATA/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
def run():
 reg=read('protocol_candidates');registry={p['slug']:p for p in reg};members={p['slug']:cat(p) for p in reg};core={p for p,c in members.items() if c};history=read('protocol_eth_history_monthly');current=[r for r in read('protocol_eth_observations') if r['period']=='snapshot']
 records=[json.loads(l) for l in (ROOT/'raw/eth/2026-10-02/requests.jsonl').read_text().splitlines()];manifest={r['key']:r for r in records if r.get('path')};lr=manifest['protocol_lido'];lido=json.loads((ROOT/lr['path']).read_text());units={r['date']:r['tokens'] for r in lido['tokens']};quotes={}
 for p in lido['tokensInUsd']:
  t=p['date'];u=units.get(t,{}).get('WETH');v=p['tokens'].get('WETH')
  if u and v:quotes[t]=v/u
 def point(r,period=None):
  if not r or r.get('eth_family_reported_usd') is None:return {'period':period or (r or {}).get('period'),'usd':None,'eth_ref':None,'gross_positive_usd':None,'negative_usd':None,'source_timestamp':None,'source_age_seconds':None,'status':'missing','excluded_tokens_usd':{}}
  selected={s:v for s,v in r['tokens_usd'].items() if s.upper() in FAMILY|EXTRA};excluded={s:v for s,v in r['tokens_usd'].items() if s.upper() not in FAMILY|EXTRA};usd=math.fsum(selected.values());q=quotes.get(r['source_timestamp']);age=r['source_age_seconds'];fresh=age<=MAX_AGE
  return {'period':period or r['period'],'usd':usd,'eth_ref':ratio(usd,q),'gross_positive_usd':math.fsum(v for v in selected.values() if v>0),'negative_usd':math.fsum(v for v in selected.values() if v<0),'source_timestamp':r['source_timestamp'],'source_age_seconds':age,'reference_ETH_USD':q,'status':'observed' if fresh else 'stale','observed_zero':usd==0 and not any(selected.values()),'excluded_tokens_usd':excluded,'legacy_selector_usd':r['eth_family_reported_usd'],'token_source_sha256':r.get('source_sha256'),'misrepresented_tokens':r.get('misrepresented_tokens')}
 H={(r['protocol'],r['period']):point(r) for r in history};C={r['protocol']:point(r,'snapshot') for r in current};periods=sorted({r['period'] for r in history});targets={r['period']:r['target_timestamp'] for r in history};cohort={p for p in core if all(H[(p,m)]['status']=='observed' for m in periods)}
 def summarize(ps,rows):
  present={p:rows[p] for p in ps if p in rows and rows[p]['status']=='observed'};stale=[p for p in ps if p in rows and rows[p]['status']=='stale'];missing=[p for p in ps if p not in rows or rows[p]['status']=='missing'];allobs=[rows[p] for p in ps if p in rows and rows[p]['status']!='missing']
  sums=lambda k:math.fsum(r[k] for r in present.values() if r.get(k) is not None) if present else None
  # None is preserved for an entirely missing category. Partial sums retain coverage.
  value={'usd':sums('usd'),'eth_ref':sums('eth_ref'),'gross_positive_usd':sums('gross_positive_usd'),'negative_usd':sums('negative_usd'),'coverage':{'expected':len(ps),'observed':len(present),'missing':len(missing),'stale':len(stale),'zero_ETH_observations':sum(bool(r.get('observed_zero')) for r in present.values()),'missing_protocols':sorted(missing),'stale_protocols':sorted(stale),'complete':len(present)==len(ps),'source_dates':dict(sorted(Counter(stamp(r['source_timestamp']) for r in present.values()).items())),'max_source_age_seconds':max((r['source_age_seconds'] for r in present.values()),default=None)},'including_stale_usd':math.fsum(r['usd'] for r in allobs) if allobs else None,'including_stale_eth_ref':math.fsum(r['eth_ref'] for r in allobs if r.get('eth_ref') is not None) if allobs else None}
  cs=[present[p] for p in cohort&set(ps) if p in present];value['constant_cohort']={'protocol_count':len(cs),'usd':math.fsum(r['usd'] for r in cs) if cs else None,'eth_ref':math.fsum(r['eth_ref'] for r in cs) if cs else None}
  return value
 months=[]
 for m in periods:
  rows={p:H[(p,m)] for p in core};v=summarize(core,rows);v.update({'period':m,'target_timestamp':targets[m],'by_category':{c['id']:summarize({p for p in core if members[p]==c['id']},rows) for c in CATEGORIES}});months.append(v)
 snap=summarize(core,C);snap.update({'period':'2026-10 snapshot','target_timestamp':T,'by_category':{c['id']:summarize({p for p in core if members[p]==c['id']},C) for c in CATEGORIES}})
 products=[]
 for p in sorted(core):
  pr=registry[p];cur=C.get(p,point(None,'snapshot'));cur=dict(cur);cur['selected_tokens_usd']=next((r['tokens_usd'] for r in current if r['protocol']==p),{})
  cur['selected_tokens_usd']={s:v for s,v in cur['selected_tokens_usd'].items() if s.upper() in FAMILY|EXTRA}
  products.append({'id':p,'name':pr['name'],'category':members[p],'source_category':pr['category'],'row_kind':'protocol_adapter','current':cur,'history':[H[(p,m)] for m in periods],'source_url':'https://api.llama.fi/protocol/'+p})
 products.sort(key=lambda p:-(p['current']['usd'] if p['current']['usd'] is not None else -1))
 def comparison(a,b,la,lb):
  ps={p for p in core if a.get(p,{}).get('status')=='observed' and b.get(p,{}).get('status')=='observed'};av=summarize(ps,a);bv=summarize(ps,b)
  return {'start':la,'end':lb,'common_protocol_count':len(ps),'common_protocols':sorted(ps),'start_usd':av['usd'],'end_usd':bv['usd'],'change_usd':bv['usd']-av['usd'],'change_usd_percent':100*(bv['usd']/av['usd']-1),'start_eth_ref':av['eth_ref'],'end_eth_ref':bv['eth_ref'],'change_eth_ref':bv['eth_ref']-av['eth_ref'],'change_eth_ref_percent':100*(bv['eth_ref']/av['eth_ref']-1),'not_net_inflows':True}
 first={p:H[(p,periods[0])] for p in core};last={p:H[(p,periods[-1])] for p in core};comparisons={'current_vs_first':comparison(first,C,periods[0],'snapshot'),'current_vs_last':comparison(last,C,periods[-1],'snapshot'),'first_vs_last':comparison(first,last,periods[0],periods[-1])}
 # Validate normalization against independently implied ETH/WETH marks, keeping
 # dispersion visible instead of pretending daily timestamps are atomic prices.
 deviations=defaultdict(list)
 for r in history+current:
  if not r.get('tokens_units') or not r.get('source_timestamp') in quotes:continue
  ref=quotes[r['source_timestamp']]
  for s in ['ETH','WETH','ETH.E','WETH.E']:
   u=(r.get('tokens_units') or {}).get(s);v=r.get('tokens_usd',{}).get(s)
   if u and u>0 and v and v>=10000:deviations[r['source_timestamp']].append({'protocol':r['protocol'],'symbol':s,'implied_ETH_USD':v/u,'deviation_percent':100*((v/u)/ref-1),'reported_usd':v})
 price_dates=sorted({r['source_timestamp'] for r in history+current if r.get('source_timestamp')});prices=[]
 for t in price_dates:
  x=deviations[t];ds=[r['deviation_percent'] for r in x];prices.append({'source_timestamp':t,'source_UTC':stamp(t),'ETH_USD':quotes.get(t),'method':'Lido tokensInUsd[WETH] / tokens[WETH] at the same adapter date','source_url':lr['url'],'source_sha256':lr['sha256'],'corroborating_native_pairs':len(x),'native_pair_deviation_min_percent':min(ds) if ds else None,'native_pair_deviation_median_percent':statistics.median(ds) if ds else None,'native_pair_deviation_max_percent':max(ds) if ds else None,'outliers_above_1pct':[r for r in x if abs(r['deviation_percent'])>1]})
 # Named chain views only; borrowed/staking/pool2 and other API subviews are
 # retained as exclusions, rather than being mistaken for additional chains.
 chain_source=manifest['chains'];knownchains={ALIASES.get(r['name'],r['name']) for r in json.loads((ROOT/chain_source['path']).read_text())};chain_detail=[];excluded_views=[];rawproof=[]
 for p in sorted(core):
  rec=manifest.get('protocol_'+p.replace('.','_'))
  if not rec:continue
  d=json.loads((ROOT/rec['path']).read_text());rawproof.append({'path':rec['path'],'sha256':rec['sha256']})
  for source_chain,v in d.get('chainTvls',{}).items():
   norm=ALIASES.get(source_chain,source_chain);usdpoint=previous(v.get('tokensInUsd',[]),T)
   if not usdpoint:continue
   selected={s:x for s,x in usdpoint['tokens'].items() if s.upper() in FAMILY|EXTRA}
   if not selected:continue
   if norm not in knownchains:
    excluded_views.append({'protocol':p,'view':source_chain,'selected_ETH_token_usd':math.fsum(selected.values()),'reason':'Not a named chain in captured chain registry; auxiliary view is not added.'});continue
   x={'protocol':p,'chain':norm,'source_timestamp':usdpoint['date'],'source_age_seconds':T-usdpoint['date'],'tokens_usd':selected,'eth_family_reported_usd':math.fsum(selected.values()),'source_sha256':rec['sha256'],'misrepresented_tokens':d.get('misrepresentedTokens'),'period':'snapshot'};z=point(x);z.update({'protocol':p,'chain':norm,'category':members[p]});chain_detail.append(z)
 chains=[]
 for chain in sorted({r['chain'] for r in chain_detail}):
  rs=[r for r in chain_detail if r['chain']==chain];mapping={r['protocol']:r for r in rs};ids=set(mapping);v=summarize(ids,mapping);v.update({'chain':chain,'protocol_count':v['coverage']['observed'],'by_category':{c['id']:summarize({p for p in ids if members[p]==c['id']},mapping) for c in CATEGORIES},'source_dates':v['coverage']['source_dates']});chains.append(v)
 chains.sort(key=lambda x:-(x['usd'] or 0))
 chain_sum=math.fsum(r['usd'] for r in chains if r['usd'] is not None)
 sources=['protocol_candidates','protocol_eth_history_monthly','protocol_eth_observations','asset_registry','benchmark_history_ethereum_rpc','op_history_rates_rpc'];proof=[{'path':str((DATA/(n+'.json')).relative_to(ROOT)),'sha256':hashlib.sha256((DATA/(n+'.json')).read_bytes()).hexdigest()} for n in sources]
 price_T=json.loads((ROOT/manifest['prices_T']['path']).read_text())['coins']['coingecko:ethereum']
 excluded_tokens=defaultdict(float)
 for r in current:
  for s,v in point(r).get('excluded_tokens_usd',{}).items():excluded_tokens[s]+=v
 out={'schema_version':1,'financial_snapshot_timestamp':T,'financial_data_refreshed':False,'basis':'Selected ETH-family adapter balances, signed and overlapping across protocol layers; not unique capital, complete market NAV or a global net total.','eth_ref_label':'ETH at the adapter-date reference price','price_normalization_sentence':'Each adapter USD balance is divided by Lido\'s same-date implied ETH price; this is a value equivalent, not a count of physically backed ETH.','maximum_source_age_seconds':MAX_AGE,'freshness_policy':'Primary sums include observations no older than 72 hours; stale and missing product observations retain their status and original values. No missing value is filled with zero.','categories':CATEGORIES,'months':months,'current':snap,'chart_points':months+[snap],'products':products,'chains':chains,'chain_observations':chain_detail,'chain_excluded_views':excluded_views,'chain_sum_usd':chain_sum,'chain_vs_aggregate_difference_usd':chain_sum-snap['usd'],'chain_reconciliation_complete':False,'chain_name_aliases':ALIASES,'comparisons':comparisons,'constant_cohort_protocols':sorted(cohort),'constant_cohort_count':len(cohort),'prices':prices,'nearest_snapshot_ETH_quote':price_T,'nearest_snapshot_quote_not_used_to_reprice_adapter_history':True,'excluded_protocols':[{'id':p,'reason':'Dollar basis product is separate from ETH-long exposure; empty adapter ETH tokens do not prove zero ETH basis.' if p=='ethena-usde' else 'No captured ETH token history; RWA product identity and ETH exposure need separate verification.'} for p,c in members.items() if c is None],'excluded_non_ETH_selector_tokens_current':dict(excluded_tokens),'selection':{'exact_family_symbols':sorted(FAMILY),'explicit_ETH_receipt_debt_symbols':sorted(EXTRA),'arbitrary_AETH_prefix_allowed':False},'global_unique_ETH':None,'global_net_market_NAV':None,'market_share_denominator':None,'source_survivorship_limit':'The protocol universe was selected from current discovery and historical seeds. Dead/missing products can be absent; constant cohort controls data availability, not survivorship.','verified_receipt_rate_history_note':'Captured wstETH, weETH and rsETH archive histories cover selected endpoints, not every adapter-date/token/chain. They are not substituted for all receipt conversions in this market panel.','inputs':proof+[{'path':lr['path'],'sha256':lr['sha256']},{'path':chain_source['path'],'sha256':chain_source['sha256']}],'chain_inputs':rawproof}
 panel_path=DATA/'market_panel.json';temporary=panel_path.with_suffix('.json.tmp');temporary.write_text(json.dumps(out,indent=2));temporary.replace(panel_path)
 csvrows=[]
 for m in months+[snap]:
  for c in CATEGORIES:
   r=m['by_category'][c['id']];csvrows.append({'period':m['period'],'category':c['id'],'usd':r['usd'],'eth_ref':r['eth_ref'],'gross_positive_usd':r['gross_positive_usd'],'negative_usd':r['negative_usd'],'expected_protocols':r['coverage']['expected'],'observed_protocols':r['coverage']['observed'],'missing_protocols':r['coverage']['missing'],'stale_protocols':r['coverage']['stale'],'constant_cohort_usd':r['constant_cohort']['usd'],'constant_cohort_eth_ref':r['constant_cohort']['eth_ref']})
 csv_write('market_panel_monthly.csv',csvrows,list(csvrows[0]))
 csvrows=[{'id':r['id'],'name':r['name'],'category':r['category'],**{k:r['current'].get(k) for k in ['usd','eth_ref','gross_positive_usd','negative_usd','source_timestamp','source_age_seconds','status']},'source_url':r['source_url']} for r in products];csv_write('market_panel_protocols.csv',csvrows,list(csvrows[0]))
 csvrows=[{k:r[k] for k in ['chain','usd','eth_ref','gross_positive_usd','negative_usd','protocol_count']} for r in chains];csv_write('market_panel_chains.csv',csvrows,list(csvrows[0]))
 csv_write('market_panel_prices.csv',prices,['source_timestamp','source_UTC','ETH_USD','corroborating_native_pairs','native_pair_deviation_min_percent','native_pair_deviation_median_percent','native_pair_deviation_max_percent'])
 assert len(months)==24 and len(products)==85 and all(p['ETH_USD'] for p in prices)
 assert all(math.isclose(r['usd'],r['gross_positive_usd']+r['negative_usd'],abs_tol=.001) for p in products for r in [p['current']]+p['history'] if r['usd'] is not None)
 assert all(math.isclose(m['usd'],math.fsum(v['usd'] or 0 for v in m['by_category'].values()),abs_tol=.001) for m in months+[snap])
 print(json.dumps({'months':len(months),'categories':len(CATEGORIES),'products':len(products),'chains':len(chains),'constant_cohort':len(cohort),'price_dates':len(prices),'current_usd':snap['usd'],'current_eth_ref':snap['eth_ref'],'current_coverage':snap['coverage'],'first_usd':months[0]['usd'],'last_usd':months[-1]['usd'],'current_non_ETH_selector_exclusions':dict(excluded_tokens),'chain_difference_usd':chain_sum-snap['usd'],'comparisons':comparisons},indent=2))
if __name__=='__main__':run()
