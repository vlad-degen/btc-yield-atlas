"""Check the report's financial meanings and synchronisation, not only UI wiring."""
import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'data/eth'


def run():
    read = lambda n: json.loads((D / (n + '.json')).read_text())
    c, pc, m = read('report_contract'), read('reader_product_chapters'), read('market_reader_chapter')
    checks = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    def close(a, b):
        return math.isclose(a, b, abs_tol=1e-8, rel_tol=1e-12)
    check('unknown_global_measures_are_not_zero_or_sample_totals', c['globalUniqueETH'] is None and c['globalCarryEquityETH'] is None)
    check('fixed_receipt_headline_uses_only_its_layer', close(c['headline']['receiptClaimsETH'], m['current']['by_category']['staking']['eth_ref']))
    check('active_count_is_status_count_not_all_books', c['headline']['currentRoutes'] == sum(r['status'] == 'active' for r in c['census']) == 10 and len(c['census']) == 13)
    for name, sha in c['sources'].items():
        check('source_hash:' + name, hashlib.sha256((D / (name + '.json')).read_bytes()).hexdigest() == sha)
    # Independently recompute every common return from the two share marks.
    for r in c['matched30dReturns']:
        p = next(p for p in pc['products'] if p['id'] == r['id'])
        rows = p['charts']['returnVsBorrow']['rows']
        start = next(x for x in rows if x['date'] == r['start'])
        end = next(x for x in rows if x['date'] == r['end'])
        check('share_mark_return:' + r['id'], close(r['bookReturnPct'], 100 * (end['ethBookPrice'] / start['ethBookPrice'] - 1)))
        check('common_dates:' + r['id'], r['start'] == '2026-09-02T23:59:59Z' and r['end'] == c['snapshot'] and r['days'] == 30)
        check('excess_arithmetic:' + r['id'], close(r['excessPercentagePoints'], r['bookReturnPct'] - r['benchmarkReturnPct']) and r['carryOnlyProfit'] is None)
    bench = next(r for r in read('etherfi_staking_comparison') if r['days'] == 30)
    check('benchmark_matches_same_frozen_window', all(close(r['benchmarkReturnPct'], 100 * bench['stETH_cumulative_return']) for r in c['matched30dReturns']) and bench['end_timestamp'] - bench['start_timestamp'] == 30 * 86400)
    for r, original in zip(c['financedLots'], read('credit_expansion_deep')['cases']):
        check('financed_lot:' + r['id'], r['id'] == original['id'] and r['currency'] == original['debt_currency'] and r['borrowed'] == original['borrowed_units'] and close(r['resultBeforeGas'], r['income'] - r['fundingCost']) and r['completeWalletProfit'] is None)
    status = {r['name']: r for r in c['census']}
    check('unverified_and_closed_capital_not_active_carry', status['Concrete Delta weETH']['status'] == 'unverified' and status['Concrete Delta weETH']['carryEquityETH'] is None and status['Rocksolid rETH']['status'] == 'closing' and status['TAU InfiniFi ETH Carry']['status'] == 'historical')
    yb = next(p for p in pc['products'] if p['id'] == 'yieldbasis')
    check('YB_pool_equity_and_actual_loan_are_distinct', close(status['YieldBasis WETH']['carryEquityETH'], yb['capitalETH']) and yb['charts']['loanLegs']['rows'][0]['debtUSD'] > yb['capitalUSD'] * .99)
    screen = read('carry_coverage_audit')['materialPools']
    check('discovery_count_does_not_claim_strategy_census', c['discovery']['exhaustiveStrategyCensus'] is False and c['discovery']['parentDispositions'] == sum(r['disposition'].startswith('Parent covered') for r in screen))
    for filename in ['carry-common-30d.csv', 'carry-status-and-capital.csv', 'report_contract.json']:
        check('download_and_mirror:' + filename, (ROOT / 'eth/data' / filename).read_bytes() == (D / filename).read_bytes())
    exported = list(csv.DictReader((D / 'carry-common-30d.csv').open()))
    for r, row in zip(c['matched30dReturns'], exported):
        check('exported_common_return:' + r['id'], row['start'] == r['start'] and row['end'] == r['end'] and close(float(row['ETH_book_return_pct']), r['bookReturnPct']))
    for stem in ['BRIEFING', 'MARKET-STRUCTURE', 'CARRY-CATEGORY', 'MARKET-COVERAGE', 'CARRY-PRODUCTS']:
        md = (ROOT / 'research/eth/en' / (stem + '.md')).read_text()
        page = (ROOT / 'eth/library' / (stem + '.html')).read_text()
        check('no_stale_primary_metrics:' + stem, not re.search(r'96\.81|53\.88|all seven measured|two examined carry parents', md + page))
    briefing = (ROOT / 'eth/library/BRIEFING.html').read_text()
    check('briefing_has_all_census_and_common_return_values', all(r['name'] in briefing for r in c['census']) and all(f"{r['bookReturnPct']:.4f}%" in briefing for r in c['matched30dReturns']))
    reader = (ROOT / 'tools/eth/site/reader.js').read_text()
    index = (ROOT / 'tools/eth/site/index.html').read_text()
    check('primary_comparison_has_no_mixed_return_windows', 'filter(r=>[94,90,365]' not in reader and 'measuredReturn' not in reader)
    check('headlines_use_contract_not_filter_denominator', 'h.nativeActiveETH' in reader and 'h.examinedBooks' in reader and 'h.liquid730dExcessPP' in reader)
    check('market_headline_is_the_counted_once_map', 'All the ETH that earns a yield' in index and read('market_reader_chapter')['basis'] == 'counted_once' and 'top two / measured carry books' not in index)
    failures = [r for r in checks if not r['passed']]
    result = {'checks': len(checks), 'all_checks_passed': not failures, 'failed': failures,
              'scope': 'Financial definitions, independently recomputed matched returns, status, discovery scope, canonical reports and exports. Unknown global capital and complete carry P&L are not certified.'}
    (D / 'report_contract_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    assert not failures


if __name__ == '__main__':
    run()
