"""Turn the counted-once map into the market chapter the website reads (same shape as the earlier protocol ledger,
data/eth/research_market_chapter.json), so the existing charts, switches and tables show products counted once.

Writes data/eth/netmap/market_chapter.json.
"""
import calendar, csv, datetime, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import OUT, RAW, ROOT
from products import CATEGORIES
import decisions as DEC

M = json.load(open(os.path.join(OUT, 'map.json')))
SNAP, LABELS, PRICES, META, VALUES = M['snapshot'], M['months'], M['prices'], M['meta'], M['values']
SCREEN = json.load(open(os.path.join(RAW, 'screen.json')))


def read_csv(name):
    p = os.path.join(OUT, name)
    return {r['slug']: r for r in csv.DictReader(open(p))} if os.path.exists(p) else {}


NOTES = read_csv('product_notes.csv')
YIELDS = json.load(open(os.path.join(OUT, 'yields_T.json'))) if os.path.exists(os.path.join(OUT, 'yields_T.json')) else {}


def ts(label):
    if label == SNAP:
        return int(datetime.datetime(2026, 10, 2, 23, 59, 59, tzinfo=datetime.UTC).timestamp())
    y, m = map(int, label.split('-'))
    return int(datetime.datetime(y, m, calendar.monthrange(y, m)[1], 23, 59, 59, tzinfo=datetime.UTC).timestamp())


def obs(slug, label):
    v = VALUES[slug].get(label)
    if v is None:
        return {'period': label if label != SNAP else 'snapshot', 'usd': None, 'eth_ref': None, 'status': 'missing'}
    return {'period': label if label != SNAP else 'snapshot', 'usd': v * PRICES[label], 'eth_ref': v,
            'gross_positive_usd': v * PRICES[label], 'negative_usd': 0.0, 'reference_ETH_USD': PRICES[label],
            'source_timestamp': ts(label), 'status': 'observed', 'observed_zero': v == 0}


def yield_text(slug):
    n = NOTES.get(slug, {})
    if n.get('yield_eth'):
        return n['yield_eth']
    y = YIELDS.get(slug)
    if y and y.get('apy') is not None:
        r = f" + rewards {y['apy_reward']:.2f}" if y.get('apy_reward') else ''
        return f"{y['apy']:.2f}% ({y['symbol']} pool, base {y.get('apy_base') or 0:.2f}{r}; {y['date']})"
    return 'not published'


def product(slug):
    m = META[slug]
    hist = [obs(slug, l) for l in LABELS[:-1]]
    hv = [(h['period'], h['eth_ref']) for h in hist if h['eth_ref']]
    peak = max(hv, key=lambda x: x[1]) if hv else None
    n = NOTES.get(slug, {})
    dl = SCREEN.get(slug, {})
    return {
        'id': slug, 'name': n.get('product') or m['name'], 'category': m['category'], 'subtype': m.get('kind') or '',
        'source_category': m['dl_category'], 'row_kind': 'onchain_book' if slug.startswith('carry:') else ('pool_set' if slug.startswith('pools:') else 'protocol_net'),
        'current': obs(slug, SNAP), 'history': hist,
        'how_earns': n.get('how') or '', 'yield': yield_text(slug), 'operator': n.get('run_by') or '',
        'official_url': n.get('url') or dl.get('url') or '', 'source_url': f'https://defillama.com/protocol/{slug}' if ':' not in slug else '',
        'classification_scope': m['source'], 'peak': {'eth_ref': {'period': peak[0], 'value': peak[1]}} if peak else None,
        'baseline': hist[0], 'flag': n.get('flag') or '',
    }


def total(rows):
    valid = [r for r in rows if r['status'] == 'observed']
    v = {k: math.fsum(r[k] for r in valid) if valid else None for k in ('usd', 'eth_ref')}
    v['gross_positive_usd'], v['negative_usd'] = v['usd'], 0.0
    v['coverage'] = {'expected': len(rows), 'observed': len(valid), 'missing': 0, 'stale': 0, 'missing_protocols': [], 'stale_protocols': [], 'complete': True}
    return v


def main():
    prods = [product(s) for s in VALUES if any(v for v in VALUES[s].values())]
    prods.sort(key=lambda p: -(p['current']['eth_ref'] or 0))
    # constant cohort: products observed with a positive value at every month-end
    cohort = [p['id'] for p in prods if all(h['eth_ref'] for h in p['history'])]
    months = []
    for i, label in enumerate(LABELS):
        rows = [(p, p['current'] if label == SNAP else p['history'][i]) for p in prods]
        per = {'period': label if label != SNAP else '2026-10 snapshot', 'target_timestamp': ts(label), **total([r for _, r in rows])}
        per['by_category'] = {}
        for c in CATEGORIES:
            cr = [r for p, r in rows if p['category'] == c['id']]
            t = total(cr)
            cc = [r for p, r in rows if p['category'] == c['id'] and p['id'] in cohort and r['status'] == 'observed']
            t['constant_cohort'] = {'protocol_count': len(cc), 'usd': math.fsum(r['usd'] for r in cc) if cc else None,
                                    'eth_ref': math.fsum(r['eth_ref'] for r in cc) if cc else None}
            per['by_category'][c['id']] = t
        cc = [r for p, r in rows if p['id'] in cohort and r['status'] == 'observed']
        per['constant_cohort'] = {'protocol_count': len(cc), 'usd': math.fsum(r['usd'] for r in cc), 'eth_ref': math.fsum(r['eth_ref'] for r in cc)}
        months.append(per)
    # chains: DefiLlama chain split of each row, scaled to the row's counted value
    chain_obs = []
    for p in prods:
        s = SCREEN.get(p['id'])
        v = p['current']['eth_ref'] or 0
        if s and s.get('chains_snap') and v:
            g = sum(s['chains_snap'].values())
            for ch, x in s['chains_snap'].items():
                if g and x * v / g >= 1:
                    chain_obs.append({'protocol': p['id'], 'chain': ch, 'category': p['category'], 'eth_ref': x * v / g,
                                      'usd': x * v / g * PRICES[SNAP], 'status': 'observed'})
        elif v:
            chain_obs.append({'protocol': p['id'], 'chain': 'Ethereum', 'category': p['category'], 'eth_ref': v, 'usd': v * PRICES[SNAP], 'status': 'observed'})
    chains = []
    for ch in sorted({r['chain'] for r in chain_obs}):
        rs = [r for r in chain_obs if r['chain'] == ch]
        c = {'chain': ch, **total(rs), 'protocol_count': len(rs), 'by_category': {}}
        for cat in CATEGORIES:
            c['by_category'][cat['id']] = total([r for r in rs if r['category'] == cat['id']])
        chains.append(c)
    chains.sort(key=lambda c: -(c['eth_ref'] or 0))
    cats = []
    for c in CATEGORIES:
        cats.append({**c, 'scope': c['how'], 'yield_scope': c['payer'],
                     'measurement': 'Products counted once: staking tokens held inside other products are counted in the product that holds them.'})
    default = [c['id'] for c in CATEGORIES if c['default']]
    excluded = sorted(({'id': k, 'name': SCREEN.get(k, {}).get('name', k), 'eth': SCREEN.get(k, {}).get('snap_eth'), 'reason': v}
                       for k, v in DEC.EXCLUDE.items()), key=lambda r: -(r['eth'] or 0))
    gap = os.path.join(ROOT, 'data', 'eth', 'gap_outside_totals.csv')
    outside = list(csv.DictReader(open(gap))) if os.path.exists(gap) else []
    chapter = {
        'schema_version': 'netmap-1', 'financial_snapshot_timestamp': ts(SNAP), 'basis': 'counted_once',
        'eth_ref_label': 'ETH', 'price_normalization_sentence': 'USD values use the ETH/USD price of each DefiLlama point (Lido adapter WETH price).',
        'categories': cats, 'months': months[:-1], 'current': months[-1], 'chart_points': months, 'products': prods,
        'chains': chains, 'chain_observations': chain_obs, 'chain_sum_usd': sum(c['usd'] or 0 for c in chains),
        'chain_vs_aggregate_difference_usd': sum(c['usd'] or 0 for c in chains) - (months[-1]['usd'] or 0),
        'constant_cohort_protocols': cohort, 'constant_cohort_count': len(cohort), 'prices': PRICES,
        'default_selection': default, 'excluded_protocols': excluded, 'outside_totals': outside,
        'default_current': total([p['current'] for p in prods if p['category'] in default]),
        'selection_configuration': {'category_count': len(CATEGORIES), 'mask_order': [c['id'] for c in CATEGORIES],
                                    'optional_off': [c['id'] for c in CATEGORIES if not c['default']]},
        'method': 'counted_once', 'products_count_default': sum(1 for p in prods if p['category'] in default and (p['current']['eth_ref'] or 0) >= 0.5),
    }
    json.dump(chapter, open(os.path.join(OUT, 'market_chapter.json'), 'w'), indent=1)
    print('products', len(prods), 'default', chapter['products_count_default'], 'total', round(chapter['default_current']['eth_ref']),
          'cohort', len(cohort), 'chains', len(chains))


if __name__ == '__main__':
    main()
