"""Independent checks of the counted-once ETH map (data/eth/netmap). Prints JSON; exits 1 on failure."""
import csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import OUT
import decisions as DEC

ch = json.load(open(os.path.join(OUT, 'market_chapter.json')))
checks = []
def check(name, ok, detail=None): checks.append({'check': name, 'passed': bool(ok), 'detail': detail})
P = ch['products']; cats = {c['id'] for c in ch['categories']}; default = set(ch['default_selection'])
check('every_product_has_a_known_category', all(p['category'] in cats for p in P))
check('no_negative_balance', all((r['eth_ref'] or 0) >= -1e-6 for p in P for r in [p['current'], *p['history']]),
      [p['id'] for p in P if any((r['eth_ref'] or 0) < -1e-6 for r in [p['current'], *p['history']])])
for i, m in enumerate([*ch['months'], ch['current']]):
    rows = [(p, p['current'] if m is ch['current'] else p['history'][i]) for p in P]
    for c in ch['categories']:
        s = math.fsum(r['eth_ref'] or 0 for p, r in rows if p['category'] == c['id'])
        if not math.isclose(s, m['by_category'][c['id']]['eth_ref'] or 0, abs_tol=1e-6):
            check(f"category_sum:{m['period']}:{c['id']}", False, [s, m['by_category'][c['id']]['eth_ref']])
check('category_sums_reconcile_every_month', not any(c['check'].startswith('category_sum') for c in checks))
tot = math.fsum(p['current']['eth_ref'] or 0 for p in P if p['category'] in default)
check('headline_equals_default_products', math.isclose(tot, ch['default_current']['eth_ref'], rel_tol=1e-12), tot)
ids = {p['id'] for p in P}
check('excluded_rows_not_counted_and_have_reasons', not (ids & set(DEC.EXCLUDE)) and all(DEC.EXCLUDE.values()))
check('concrete_delta_not_counted', not any('concrete' in p['id'] for p in P))
check('carry_rows_are_the_examined_books', {p['name'] for p in P if p['id'].startswith('carry:') and not p['id'].endswith(':nodebt')} <= {v['name'] for v in DEC.CARRY.values()})
native = 43_805_557.723  # archived consensus state at T (research/eth/en/BRIEFING.md)
st = math.fsum(p['current']['eth_ref'] or 0 for p in P if p['category'] in ('staking', 'restaking'))
check('staking_and_restaking_below_native_stake', st < native, [st, native])
check('no_duplicate_names', len({p['name'] for p in P}) == len(P))
notes = {r['slug'] for r in csv.DictReader(open(os.path.join(OUT, 'product_notes.csv')))} if os.path.exists(os.path.join(OUT, 'product_notes.csv')) else set()
missing = [p['id'] for p in P if p['category'] in default and (p['current']['eth_ref'] or 0) >= 100 and p['id'] not in notes and p['id'].replace(':nodebt','') not in notes]
check('products_over_100_ETH_have_notes', not missing, missing)
failed = [c for c in checks if not c['passed']]
print(json.dumps({'checks': len(checks), 'passed': len(checks) - len(failed), 'failed': failed}, indent=1))
sys.exit(1 if failed else 0)
