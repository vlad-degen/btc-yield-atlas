"""Screening list -> raw/fetch_list.json: DefiLlama Lending / Uncollateralized Lending / CDP protocols with TVL > $1M (raw/protocols.json,
api.llama.fi/protocols read 2026-09-23) plus every C0 slug of tools/marketmap/scripts/products.py (cdp / venue / curator)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mmlib import RAW, REPO
sys.path.insert(0, os.path.join(REPO, 'tools', 'marketmap', 'scripts'))
from products import P as PRODUCTS
PR = json.load(open(os.path.join(RAW, 'protocols.json')))
c0 = {'cdp': [], 'venue': [], 'curator': []}
for p in PRODUCTS:
    if p['cat'] == 'C0':
        if p['id'].startswith('cdp-'): c0['cdp'].append(p['slug'])
        elif p['id'].startswith('mm-'): c0['venue'].append(p['slug'])
        elif p['id'].startswith('cur-'): c0['curator'].append(p['slug'])
screen = sorted(p['slug'] for p in PR if p['category'] in ('Lending', 'Uncollateralized Lending', 'CDP') and (p.get('tvl') or 0) > 1e6)
fetch = sorted(set(screen) | set(sum(c0.values(), [])))
json.dump(dict(c0=c0, screen=screen, fetch=fetch), open(os.path.join(RAW, 'fetch_list.json'), 'w'), indent=0)
print(len(screen), 'screened', len(fetch), 'to fetch')
