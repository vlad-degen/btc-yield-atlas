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
    candidates, chapters = read('reader_carry_category'), read('reader_product_chapters')
    checks = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    def close(a, b):
        return a is b if a is None or b is None else math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-8)
    check('exact_frozen_snapshot', analysis['snapshot'] == 1790985599)
    check('24_completed_months', analysis['months'] == [m['period'] for m in market['months']] and
          analysis['months'][0] == '2024-10' and analysis['months'][-1] == '2026-09' and len(analysis['months']) == 24)
    check('all_thirteen_without_size_cutoff', len(analysis['books']) == 13 and {p['name'] for p in analysis['books']} ==
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
                view == 'all' or ((p['name'] in ['Concrete Delta weETH', 'ether.fi Liquid ETH', 'Lido Earn ETH', 'Avant avETH / savETH']) == (view == 'parents'))]
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
    check('complete_report_navigation', len(payload['reportLibrary']) == len(ARTICLES) and
          {r['id'] for r in payload['reportLibrary']} == set(ARTICLES) and all(
              (ROOT / 'eth' / r['href']).is_file() for r in payload['reportLibrary']))
    original = read('research_market_chapter')
    excluded = next(p for p in original['products'] if p['id'] == 'justlend-v1')
    for i, month in enumerate(market['months']):
        check('unchanged_market_exposure:' + month['period'], close(month['eth_ref'],
              original['months'][i]['eth_ref'] - (excluded['history'][i]['eth_ref'] or 0)))
    yb = next(p for p in chapters['products'] if p['id'] == 'yieldbasis')
    old_yb = next(p for p in read('strategy_universe_deep')['products'] if p['id'] == 'yb_weth_pool')
    check('YB_frozen_capital_conserved', close(yb['capitalETH'], old_yb['capitalETH']) and close(yb['capitalUSD'], old_yb['capitalUSD']))
    check('YB_rank_five_actual_USD_loan', yb['rank'] == 5 and close(yb['charts']['loanLegs']['rows'][0]['debtUSD'], old_yb['state']['loan']['debtCrvUSD']))
    check('YB_no_fabricated_predeployment_capital', all(r['sizeETH'] is None for r in yb['charts']['capitalHistory']['rows'] if r['month'] <= '2026-04'))
    holders = read('yb_LT_holders_T')
    distribution = yb['charts']['walletDistribution']
    check('YB_direct_holder_balances_reconcile', holders['reconciled'] and len(holders['addresses']) == holders['holderCount'] == 332 and close(sum(r['shares'] for r in holders['addresses']), old_yb['shareSupply']))
    check('YB_holder_distribution_conserves_book', sum(r['holders'] for r in distribution['rows']) == 332 and close(sum(r['capitalETH'] for r in distribution['rows']), old_yb['capitalETH']) and close(sum(r['shareOfSupplyPct'] for r in distribution['rows']), 100))
    check('YB_holder_source_hash', distribution['sourceSHA256'] == hashlib.sha256((DATA/'yb_LT_holders_T.json').read_bytes()).hexdigest())
    discovered = set()
    transfers = json.loads((ROOT/holders['sourcePaths'][0]).read_text())['records']
    balances = json.loads((ROOT/holders['sourcePaths'][1]).read_text())['records']
    for record in transfers:
        for log in record['response']['result']:
            for topic in log['topics'][1:3]:
                address = '0x' + topic[-40:]
                if int(address, 16): discovered.add(address)
    check('YB_all_discovered_addresses_read_at_T', len(balances) == len(discovered) and {r['label'].removeprefix('yb_LT_balance_') for r in balances} == discovered and all(r['params'][-1] == hex(26108081) and 'result' in r['response'] for r in balances))
    check('YB_positive_archive_balances_match', {r['address']:r['shares'] for r in holders['addresses']} == {r['label'].removeprefix('yb_LT_balance_'):int(r['response']['result'],16)/1e18 for r in balances if int(r['response']['result'],16)>0})
    coverage = read('carry_coverage_audit')
    check('material_screen_disposed', coverage['materialKeywordPools'] == len(coverage['materialPools']) and all(p['disposition'] for p in coverage['materialPools']))
    import re
    discovery = json.loads((ROOT/coverage['source']['path']).read_text())['data']
    material = [p for p in discovery if re.search('ETH', p['symbol'], re.I) and p['tvlUsd'] >= 5e6]
    check('material_screen_matches_saved_feed', {p['pool'] for p in material} == {p['pool'] for p in coverage['materialPools']} and len(material) == 299 and len({p['project'] for p in material}) == coverage['materialProjects'] == 86)
    check('material_feed_source_hash', hashlib.sha256((ROOT/coverage['source']['path']).read_bytes()).hexdigest() == coverage['source']['sha256'])
    manifest = read('parity_discovery_manifest')
    check('new_discovery_capture_hashes', all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() == r['sha256'] if r.get('path') else bool(r.get('error')) for r in manifest))
    check('YB_monthly_capture_hash', candidates['reader_extension']['monthly_capture_sha256'] == hashlib.sha256((ROOT/'raw/eth/parity-sweep-2026-10-05/yb_monthly_frozen.json').read_bytes()).hexdigest())
    check('documented_routes_replaced_by_fixed_block_cases', not coverage['documentedRoutes'] and any(p['name']=='ZenSats wstETH' for p in analysis['books']))
    failures = [r for r in checks if not r['passed']]
    result = {'checks': len(checks), 'all_checks_passed': not failures, 'failed': failures,
              'financial_snapshot': '2026-10-02T23:59:59Z',
              'site_sha256': hashlib.sha256((ROOT / 'eth/index.html').read_bytes()).hexdigest()}
    (DATA / 'reader_alignment_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    assert not failures


if __name__ == '__main__':
    run()
