"""Classify dated basis disclosures. No network and no imputation of ETH allocation."""
import hashlib,json,re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'raw/eth/research-closure-2026-10-04/basis'

class Text(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ['script','style']:self.skip+=1
    def handle_endtag(self,tag):
        if tag in ['script','style']:self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip():self.rows.append(data.strip())

def run():
    sources=json.loads((RAW/'manifest.json').read_text())
    source={r['id']:r for r in sources}
    for row in sources:
        if 'path' in row:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    june=json.loads((ROOT/source['ethena_june_update']['path']).read_text())
    cooked=june['post_stream']['posts'][0]['cooked']
    assert '$39M' in cooked and '1.0%' in cooked and '-0.1%' in cooked
    parser=Text();parser.feed((ROOT/source['ethena_weekly_reserves']['path']).read_text())
    weekly=' '.join(parser.rows)
    assert all(x in weekly for x in ['Oct 2, 2026','4,903.84','4,905.76','4,967.84'])
    out={
        'snapshot':'2026-10-02T23:59:59Z','financial_data_refreshed':False,
        'exact_T_ETH_basis_notional_USD':None,
        'findings':[
            {'date':'2026-07-03','scope':'All crypto basis, not ETH alone','value_USD':39000000,'value_type':'rounded issuer-dashboard figure reproduced in commissioned governance report','ETH_notional_USD':None,'source':source['ethena_june_update']['url'],'interpretation':'The report places all crypto basis at about $39M (1.0% of backing), with a reported -0.1% APY. It does not separate ETH.'},
            {'date':'2026-10-02T00:08:00Z','scope':'All USDe backing, not ETH allocation','value_USD':4905760000,'token_supply_USD':4903840000,'backing_plus_reserve_USD':4967840000,'value_type':'rounded weekly automated reserve feed','ETH_notional_USD':None,'source':source['ethena_weekly_reserves']['url'],'interpretation':'The weekly feed reports $4,905.76M backing for $4,903.84M supply, about 23 hours 52 minutes before T. It provides no ETH allocation. Its weekly output is not a continuous audit opinion.'}
        ],
        'conclusion':'No exact-T ETH basis amount can be recovered from these dated public disclosures. The total reserve figure and the sUSDe reward rate cannot substitute for it. The separately captured 3 October ETH allocation remains a later observation.',
        'required_record':'Dated ETH spot and derivative positions, custody ownership, margin balances and valuations at T, with ETH separated from BTC, equities, lending, cash and RWA.',
        'sources':sources,
    }
    (ROOT/'data/eth/basis_closure_disclosures.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Basis disclosures: source hashes and dated figures verified; exact-T ETH amount remains null')

if __name__=='__main__':run()
