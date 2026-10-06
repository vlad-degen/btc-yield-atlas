"""Derive the presentation universe; retain the complete captured ledger unchanged."""
import copy,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'data/eth'
def run():
 src=D/'research_market_chapter.json';original=json.loads(src.read_text());m=copy.deepcopy(original)
 # A matching ETH symbol on Tron does not verify an Ethereum-backed claim.
 labels={'staking':'Staking / restaking claims','loops':'Loop-focused vaults','carry':'Carry-linked parents','basis':'Basis / hedged ETH','fixed_yield':'Fixed-yield venues','farming':'Liquidity / mixed vaults','lending':'Lending infrastructure','cdp':'CDP collateral'}
 for c in m['categories']:
  c['label']=labels.get(c['id'],c['label'])
  c['measurement']='Protocol-family exposure; not a measured strategy allocation or unique ETH capital.'
 excluded=[p for p in m['products'] if p['id']=='justlend-v1'];m['products']=[p for p in m['products'] if p['id']!='justlend-v1'];m['constant_cohort_protocols']=[p for p in m['constant_cohort_protocols'] if p!='justlend-v1'];m['constant_cohort_count']=len(m['constant_cohort_protocols'])
 # Match the BTC report's economic classification: a dollar-financed LT pool
 # belongs to carry even though DefiLlama labels its parent Leveraged Farming.
 # This changes presentation roles, never the captured token observations.
 yb=next(p for p in m['products'] if p['id']=='yield-basis')
 yb.update(category='carry',subtype='dollar_financed_liquidity',how_earns='Borrow crvUSD to maintain leveraged WETH/crvUSD liquidity; trading fees must cover financing and administration.')
 for r in m['chain_observations']:
  if r['protocol']=='yield-basis':r['category']='carry'
 cohort=set(m['constant_cohort_protocols'])
 def total(rows,ids):
  rs=[(p,r) for p,r in rows if p in ids];present=[(p,r) for p,r in rs if r['status']=='observed'];valid=[r for p,r in present];stale=[p for p,r in rs if r['status']=='stale'];missing=[p for p,r in rs if r['status']=='missing']
  v={k:math.fsum(r[k] for r in valid if r.get(k) is not None) if valid else None for k in ['usd','eth_ref','gross_positive_usd','negative_usd']}
  v['coverage']={'expected':len(rs),'observed':len(valid),'missing':len(missing),'stale':len(stale),'missing_protocols':missing,'stale_protocols':stale,'complete':len(valid)==len(rs)}
  cr=[r for p,r in present if p in cohort];v['constant_cohort']={'protocol_count':len(cr),**{k:math.fsum(r[k] for r in cr) if cr else None for k in ['usd','eth_ref']}};return v
 ids={p['id'] for p in m['products']}
 for i,period in enumerate([*m['months'],m['current']]):
  rs=[(p['id'],p['current'] if i==24 else p['history'][i]) for p in m['products']];period.update(total(rs,ids))
  for c in m['categories']:period['by_category'][c['id']]=total(rs,{p['id'] for p in m['products'] if p['category']==c['id']})
 m['chart_points']=m['months']+[m['current']]
 m['chain_observations']=[r for r in m['chain_observations'] if r['protocol']!='justlend-v1' and r['chain']!='Tron']
 chains=[]
 for chain in m['chains']:
  if chain['chain']=='Tron':continue
  obs=[r for r in m['chain_observations'] if r['chain']==chain['chain']];rs=[(r['protocol'],r) for r in obs];ci={r['protocol'] for r in obs};chain.update(total(rs,ci));chain['protocol_count']=chain['coverage']['observed']
  for c in m['categories']:chain['by_category'][c['id']]=total(rs,{r['protocol'] for r in obs if r['category']==c['id']})
  chains.append(chain)
 m['chains']=chains;m['chain_sum_usd']=sum(c['usd'] or 0 for c in chains);m['chain_vs_aggregate_difference_usd']=m['chain_sum_usd']-m['current']['usd']
 selected=set(m['default_selection']);m['default_current']=total([(p['id'],p['current']) for p in m['products']],{p['id'] for p in m['products'] if p['category'] in selected})
 m['excluded_representations']=[{'id':p['id'],'name':p['name'],'reason':'Tron mapped ETH: Ethereum backing and redemption not verified. Excluded from all reader totals, category histories and chain charts; full captured observations retained in the source ledger.','current':p['current'],'history':p['history'],'source_url':p['source_url']} for p in excluded]
 m['excluded_protocols']+= [{'id':'justlend-v1','reason':m['excluded_representations'][0]['reason']}]
 m['presentation_universe']={'source_path':'data/eth/research_market_chapter.json','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'policy':'Exclude unverified Tron mapped-ETH representation; classify YieldBasis WETH as dollar-financed carry, consistently with BTC. Captured observations are unchanged.','excluded_protocols':['justlend-v1'],'reclassified_protocols':{'yield-basis':{'from':'farming','to':'carry','evidence':'strategy_universe_deep: yb_weth_pool actual crvUSD loan'}},'raw_protocol_rows':len(original['products']),'reader_protocol_rows':len(m['products'])}
 m['presentation_universe']['category_policy']='Group protocol families for discovery. Carry-linked parents and mixed vaults retain their entire reported ETH exposure; unmeasured sleeve weights are never inferred. Lending and CDP are optional financing layers. Historical categories use the same family mapping, not historical portfolio allocations.'
 (D/'market_reader_chapter.json').write_text(json.dumps(m,indent=2)+'\n');print('Reader universe:',len(m['products']),'rows; Tron mapped ETH retained outside counts.')
if __name__=='__main__':run()
