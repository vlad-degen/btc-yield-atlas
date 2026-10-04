"""Discovery views; reported pool TVL is not net market capital."""
from __future__ import annotations
import collections, datetime as dt, json, re
from collect import ROOT, T, RAW, read_latest

FAMILY=set('ETH WETH STETH WSTETH EETH WEETH WEETHS RETH CBETH WBETH BETH FRXETH SFRXETH ETHX OETH WOETH METH CMETH EZETH RSETH WRSETH PUFETH SWETH RSWETH ANKRETH AETHC RETH2 SETH2 OSETH ETHPLUS ETH+ LIQUIDETH STKETH DINEROETH PXETH APXETH STONE QETH HETH TETH UNIETH VETH VBETH WETH.E ETH.E WSTETH.E AWETH AETHWETH AETHWEETH SPWSTETH'.split())
EXCLUDED_SYMBOLS={'ETHW','WETHW','SETH'} # PoW fork and synthetic exposure require a separate perimeter.
ALIASES={'OP Mainnet':'Optimism','Hyperliquid L1':'HyperEVM','Binance':'BNB Chain','BSC':'BNB Chain'}

def components(symbol):
    s=symbol.upper()
    parts=re.split(r'[-/\s(),]+',s)
    hits=[x for x in parts if x in FAMILY]
    # Discovery-only candidates with a new ETH-denominated receipt name.
    possible=[x for x in parts if x.endswith('ETH') and x not in FAMILY and x not in EXCLUDED_SYMBOLS]
    return hits,possible

def build():
    pools=read_latest('yield_pools')['data']; protocols=read_latest('protocols')
    proto={r['slug']:r for r in protocols}
    out=[]; uncertain=[]
    for r in pools:
        hits,new=components(r['symbol'])
        if not hits:
            if new:uncertain.append({**r,'candidate_components':new,'status':'symbol_only_unverified'})
            continue
        chain=ALIASES.get(r['chain'],r['chain'])
        rec={**r,'normalized_chain':chain,'matched_components':hits,'source_layer':'discovery_current','target_snapshot_verified':False,'amount_meaning':'reported full-pool USD TVL; mixed pools include non-ETH assets','mechanism_verified':False}
        rec['category_hint']=proto.get(r['project'],{}).get('category')
        out.append(rec)
    out.sort(key=lambda r:r.get('tvlUsd') or 0,reverse=True)
    chains=collections.defaultdict(lambda:{'pools':0,'reported_full_pool_tvl_usd':0.0,'protocols':set(),'above_5m_pools':0})
    projects=collections.defaultdict(lambda:{'pools':0,'reported_full_pool_tvl_usd':0.0})
    for r in out:
        c=chains[r['normalized_chain']];c['pools']+=1;c['reported_full_pool_tvl_usd']+=r.get('tvlUsd') or 0;c['protocols'].add(r['project']);c['above_5m_pools']+=int((r.get('tvlUsd') or 0)>=5e6)
        p=projects[r['project']];p['pools']+=1;p['reported_full_pool_tvl_usd']+=r.get('tvlUsd') or 0
    chainrows=[{'chain':k,**v,'protocols':len(v['protocols'])} for k,v in chains.items()]
    chainrows.sort(key=lambda r:r['reported_full_pool_tvl_usd'],reverse=True)
    mandatory={'Ethereum','Base','Arbitrum','Optimism'}
    allgross=sum(r['reported_full_pool_tvl_usd'] for r in chainrows)
    for r in chainrows:r['screen_share']=r['reported_full_pool_tvl_usd']/allgross;r['deep_candidate']=r['chain'] in mandatory or r['reported_full_pool_tvl_usd']>=25e6 or r['screen_share']>=.01
    projectrows=sorted([{'slug':k,**v,'name':proto.get(k,{}).get('name'),'category':proto.get(k,{}).get('category')} for k,v in projects.items()],key=lambda r:r['reported_full_pool_tvl_usd'],reverse=True)
    selected={r['slug'] for r in projectrows if r['reported_full_pool_tvl_usd']>=5e6}
    # Historical and issuer candidates absent from the yields feed remain visible.
    seeds=['lido','rocket-pool','coinbase-wrapped-staked-eth','binance-staked-eth','frax-ether','stakewise-v3','mantle-staked-eth','stader','origin-ether','ether.fi-stake','ether.fi-liquid','eigencloud','symbiotic','renzo','kelp','puffer-finance','swell-liquid-staking','swell-liquid-restaking','mellow-lrt','cian-yield-layer','fluid-lite','gearbox','summer.fi','yearn-finance','pendle','spectra-v2','aave-v3','morpho-blue','spark','euler-v2','fluid-lending','fluid-dex','ethena-usde','lagoon','upshift','tokemak','reserve-protocol','treehouse-protocol','concrete']
    selected.update(s for s in seeds if s in proto)
    registry=[{'slug':s,'name':proto[s]['name'],'category':proto[s].get('category'),'url':proto[s].get('url'),'adapter_module':proto[s].get('module'),'reported_protocol_tvl_usd':proto[s].get('tvl'),'status':'candidate_not_eth_nav_verified','source':'https://api.llama.fi/protocols'} for s in sorted(selected) if s in proto]
    dest=ROOT/'data'/'eth';dest.mkdir(parents=True,exist_ok=True)
    for name,data in [('yield_pool_candidates',out),('unverified_symbols',uncertain),('chain_screen',chainrows),('protocol_screen',projectrows),('protocol_candidates',registry)]:
        (dest/f'{name}.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
    summary={'all_protocols':len(protocols),'all_yield_pools':len(pools),'matched_pool_candidates':len(out),'symbol_only_candidates':len(uncertain),'candidate_protocols':len(registry),'candidate_chains':len(chainrows),'deep_candidate_chains':[r['chain'] for r in chainrows if r['deep_candidate']],'reported_full_pool_tvl_usd':allgross,'not_net_market_capital':True}
    (dest/'discovery_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
    print('Top pools:',[(r['project'],r['normalized_chain'],r['symbol'],r['tvlUsd']) for r in out[:15]])

if __name__=='__main__':build()
