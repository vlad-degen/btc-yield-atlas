"""Check financial conservation, missing states and exports in the reader bridge."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/eth'


def run():
    read = lambda name: json.loads((DATA / f'{name}.json').read_text())
    analysis, market = read('reader_analysis'), read('market_reader_chapter')
    candidates, chapters = read('carry_category_candidates'), read('product_chapters')
    checks = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    def close(a, b):
        return a is b if a is None or b is None else math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-8)
    check('exact_frozen_snapshot', analysis['snapshot'] == 1790985599)
    check('24_completed_months', analysis['months'] == [m['period'] for m in market['months']] and
          analysis['months'][0] == '2024-10' and analysis['months'][-1] == '2026-09' and len(analysis['months']) == 24)
    check('all_seven_without_size_cutoff', {p['name'] for p in analysis['books']} ==
          {p['product'] for p in candidates['products'] if p['classification'] == 'E4'})
    for name, sha in analysis['sources'].items():
        check('source_hash:' + name, hashlib.sha256((DATA / f'{name}.json').read_bytes()).hexdigest() == sha)
    for book in analysis['books']:
        original = next(p for p in candidates['products'] if p['product'] == book['name'])
        history = original.get('history') or next(p for p in chapters['products']
                     if p['name'] == book['name'])['charts']['capitalHistory']['rows']
        source = {r['month']: r for r in history}
        for row in book['history']:
            actual = source.get(row['month'], {})
            check(book['name'] + ':' + row['month'], close(row['eth'], actual.get('sizeETH')) and
                  close(row['usd'], actual.get('sizeUSD')) and row['status'] == actual.get('status', 'no_observation'))
    for i, month in enumerate(market['months']):
        for unit, field in [('eth', 'eth_ref'), ('usd', 'usd')]:
            values = [p['history'][i][unit] for p in analysis['adapterParents']]
            total = sum(v for v in values if v is not None) if any(v is not None for v in values) else None
            check('market_category_conservation:' + month['period'] + ':' + unit,
                  close(total, month['by_category']['carry'][field]))
    for view in ['all', 'parents', 'dedicated', 'category']:
        shown = analysis['adapterParents'] if view == 'category' else [p for p in analysis['books'] if
                view == 'all' or ((p['name'] in ['Concrete Delta weETH', 'ether.fi Liquid ETH']) == (view == 'parents'))]
        for unit in ['eth', 'usd']:
            path = ROOT / 'eth/data' / f'carry-history-{view}-{unit}.csv'
            rows = list(csv.DictReader(path.open()))
            check('CSV_count:' + path.name, len(rows) == 24)
            for i, row in enumerate(rows):
                values = [p['history'][i][unit] for p in shown]
                total = sum(v for v in values if v is not None) if any(v is not None for v in values) else None
                valid = row['month'] == analysis['months'][i] and int(row['observed_products']) == sum(v is not None for v in values)
                for product, value in zip(shown, values):
                    cell = row[product['name'] + '_' + unit.upper()]
                    valid &= cell == '' if value is None else close(float(cell), value)
                    valid &= row[product['name'] + '_status'] == product['history'][i]['status']
                cell = row['observed_gross_total_' + unit.upper()]
                valid &= cell == '' if total is None else close(float(cell), total)
                check('CSV_values:' + path.name + ':' + row['month'], valid)
    check('native_USDC_identity_on_L2', all(r['symbol'] == 'USDCn' for r in analysis['funding']
          if r['chain'] in ['arbitrum', 'optimism']))
    check('same_block_732_day_comparisons', len(analysis['matchedBenchmarks']) == 4 and all(
          r['windowDays'] == 732 and r['benchmarkId'] == 'steth_exact_blocks' and
          close(r['bookReturnPct'] - r['benchmarkBookReturnPct'], r['bookExcessPercentagePoints'])
          for r in analysis['matchedBenchmarks']))
    import importlib.util
    spec = importlib.util.spec_from_file_location('eth_site_builder', ROOT / 'tools/eth/site.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    ARTICLES = builder.ARTICLES
    payload = read('site_payload')
    check('complete_46_report_navigation', len(payload['reportLibrary']) == len(ARTICLES) == 46 and
          {r['id'] for r in payload['reportLibrary']} == set(ARTICLES) and all(
              (ROOT / 'eth' / r['href']).is_file() for r in payload['reportLibrary']))
    failures = [r for r in checks if not r['passed']]
    result = {'checks': len(checks), 'all_checks_passed': not failures, 'failed': failures,
              'financial_snapshot': '2026-10-02T23:59:59Z',
              'site_sha256': hashlib.sha256((ROOT / 'eth/index.html').read_bytes()).hexdigest()}
    (DATA / 'reader_alignment_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    assert not failures


if __name__ == '__main__':
    run()
