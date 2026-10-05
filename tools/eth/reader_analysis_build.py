"""Derive the report's analytical bridge from existing frozen measurements."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/eth'


def run():
    names = ['reader_carry_category', 'reader_product_chapters', 'market_reader_chapter',
             'funding_atlas_chapter', 'strategy_universe_deep', 'credit_expansion_deep']
    source = {name: json.loads((DATA / f'{name}.json').read_text()) for name in names}
    market = source['market_reader_chapter']
    chapters = source['reader_product_chapters']['products']
    books = []
    for product in source['reader_carry_category']['products']:
        if product['classification'] != 'E4':
            continue
        history = product.get('history') or next(
            p for p in chapters if p['name'] == product['product'])['charts']['capitalHistory']['rows']
        by_month = {r['month']: r for r in history}
        rows = []
        for month in market['months']:
            row = by_month.get(month['period'])
            rows.append({'month': month['period'], 'timestamp': month['target_timestamp'],
                         'eth': row.get('sizeETH') if row else None,
                         'usd': row.get('sizeUSD') if row else None,
                         'status': row.get('status', 'no_observation') if row else 'no_observation'})
        observed = [r for r in rows if r['eth'] is not None]
        funded = [r for r in observed if r['eth'] > 1]
        books.append({'name': product['product'], 'currentETH': product['sizeETH'],
                      'currentUSD': product['sizeUSD'], 'history': rows,
                      'firstMaterialMonth': funded[0]['month'] if funded else None,
                      'peak': max(observed, key=lambda r: r['eth']) if observed else None})
    books.sort(key=lambda p: -p['currentETH'])
    adapters = [{'name': p['name'], 'history': [
        {'month': r['period'], 'timestamp': m['target_timestamp'],
         'eth': r['eth_ref'] if r['status'] == 'observed' else None,
         'usd': r['usd'] if r['status'] == 'observed' else None, 'status': r['status']}
        for r, m in zip(p['history'], market['months'])]}
        for p in market['products'] if p['category'] == 'carry']
    funding = source['funding_atlas_chapter']['reserves']
    selected_funding = [next(r for r in funding if r['venue_id'] == venue and r['symbol'] == symbol)
                        for venue, symbol in [('aave-ethereum', 'USDC'), ('aave-ethereum', 'USDT'),
                                              ('aave-base', 'USDC'), ('aave-arbitrum', 'USDCn'),
                                              ('aave-optimism', 'USDCn')]]
    benchmarks = []
    for p in source['strategy_universe_deep']['products']:
        for window in p.get('windowReturns', []):
            if window['windowDays'] == 732:
                benchmarks.append({'name': p['name'], 'capitalETH': p['capitalETH'], **window})
    result = {'schemaVersion': 1, 'snapshot': 1790985599,
              'months': [m['period'] for m in market['months']], 'books': books,
              'adapterParents': adapters, 'funding': selected_funding,
              'matchedBenchmarks': benchmarks,
              'financedCashResults': source['credit_expansion_deep']['summary'],
              'scope': 'Gross whole-product books with current, historical or declared carry evidence; '
                       'not unique ETH, historical dollar allocations, deposits or earned income.',
              'sources': {name: hashlib.sha256((DATA / f'{name}.json').read_bytes()).hexdigest()
                          for name in names}}
    (DATA / 'reader_analysis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for view in ['all', 'parents', 'dedicated', 'category']:
        shown = adapters if view == 'category' else [p for p in books if view == 'all' or
                ((p['name'] in ['Concrete Delta weETH', 'ether.fi Liquid ETH']) == (view == 'parents'))]
        for unit in ['eth', 'usd']:
            with (DATA / f'carry-history-{view}-{unit}.csv').open('w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['month', 'measurement', *[p['name'] + '_' + unit.upper() for p in shown],
                                 'observed_gross_total_' + unit.upper(), 'observed_products',
                                 *[p['name'] + '_status' for p in shown]])
                for i, month in enumerate(result['months']):
                    rows = [p['history'][i] for p in shown]
                    values = [r[unit] for r in rows]
                    total = sum(v for v in values if v is not None) if any(v is not None for v in values) else None
                    writer.writerow([month, 'protocol_adapter_parents' if view == 'category' else 'gross_whole_product_books',
                                     *values, total, sum(v is not None for v in values), *[r['status'] for r in rows]])
    print(f'Reader analysis: {len(books)} books, 24 months, 8 view-matched CSVs; frozen inputs only.')
    return result


if __name__ == '__main__':
    run()
