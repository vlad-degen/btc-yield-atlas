"""Offline verification of registry completeness within scope, dates, sources and schemas."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[2];checks=0

def check(message,value):
 global checks
 checks+=1
 if not value:raise AssertionError(message)
d=json.loads((ROOT/'data/eth/strategy_universe_expansion.json').read_text());m=json.loads((ROOT/'data/eth/strategy_universe_expansion_manifest.json').read_text())
for x in m['inputs']+m['outputs']:
 p=ROOT/x['path'];check('file exists '+x['path'],p.is_file());check('SHA256 '+x['path'],hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'])
check('T boundary',d['snapshot']['timestamp']=='2026-10-02T23:59:59Z'and d['snapshot']['ethereumBlock']==26108081)
check('no discovery financial joins',d['summary']['fixedTProductFinancialJoinsAdded']==0)
check('coverage unknown',d['summary']['financialMarketCoverageStatus']=='unknown')
sources={x['id']:x for x in d['sources']};ps={x['id']:x for x in d['products']}
for f in d['families']:
 for k in ['id','name','mechanic','payers','products','ETHexposure','returnBasis','exitTerms','controls','risks','capacity','incentivesOff','coverageStatus','sources']:check('family field '+f['id']+'/'+k,bool(f[k]))
 check('risk list '+f['id'],isinstance(f['risks'],list));check('source binding '+f['id'],all(x in sources for x in f['sourceIds']));check('product binding '+f['id'],all(x in ps and ps[x]['familyId']==f['id']for x in f['products']))
for p in d['products']:
 check('product source binding '+p['id'],all(x in sources for x in p['sourceIds']));check('limitations '+p['id'],bool(p['missingMeasurements']))
 for c in p['contracts']:check('address '+p['id'],bool(re.fullmatch(r'0x[0-9a-f]{40}',c['address'])))
 for o in p['quantitativeObservations']:
  check('discovery not T '+p['id'],o['fixedBlockVerified']is False and o['measuredDate']!=d['snapshot']['timestamp']);check('not additive '+p['id'],o['additive']is False);check('denominator stated '+p['id'],bool(o['scope'])and bool(o['unit']))
r=json.loads((ROOT/'data/eth/strategy_universe_expansion_pendle_registry.json').read_text());l=json.loads((ROOT/'data/eth/strategy_universe_expansion_pendle_loops.json').read_text())
check('full 494 pagination',len(r)==494 and len({x['market']for x in r})==494);eth=[x for x in r if'eth'in x['categoryIds']];check('117 ETH tagged',len(eth)==117);check('4 active unexpired ETH',len([x for x in eth if x['isActiveAtDiscovery']and x['expiry']>'2026-10-04T00:00:00Z'])==4);check('15 loop records no ETH match',len(l)==15 and not any(x['isETHFamilyMatch']for x in l))
article=ROOT/'research/eth/review/STRATEGY-UNIVERSE-EXPANSION.md';check('article exists',article.is_file());t=article.read_text();check('no long dashes','\u2013'not in t and'\u2014'not in t)
for ref in re.findall(r'\]\(([^)]+)\)',t):
 if not ref.startswith(('http://','https://','#')):check('local article link '+ref,(article.parent/ref).resolve().is_file())
print('PASS',checks,'checks')
