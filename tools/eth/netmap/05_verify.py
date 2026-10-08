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
check('carry_rows_are_the_examined_books', {p['name'] for p in P if p['id'].startswith('carry:') and not p['id'].endswith((':nodebt', ':rest'))} <= {v['name'] for v in DEC.CARRY.values()})
check('carry_category_is_only_carry_rows', all(p['id'].startswith('carry:') and not p['id'].endswith(':rest') for p in P if p['category'] == 'carry'))
check('loop_products_inside_leveraged_staking', all((p['current']['eth_ref'] or 0) == 0 for p in P if p['id'] in DEC.LOOPS_IN_LENDING))
# the lending layer at the snapshot reconciles with the lending split's counted-once matrix (data/eth/lending_split.json)
LL = json.load(open(os.path.join(OUT, 'lending_layer.json')))
lm, snap = LL['meta'], LL['months'][LL['snapshot']]
check('loops_equal_matrix_A1_B1_less_product_shares', math.isclose(snap['loops'], lm['matrix']['A1'] + lm['matrix']['B1'] - lm['shares_snapshot'], rel_tol=1e-9))
check('lending_layer_equals_matrix_plus_rows_outside_its_basis', abs(lm['layer_total_snapshot'] - lm['matrix_total']) < 5000, lm['layer_total_snapshot'] - lm['matrix_total'])
cat = ch['current']['by_category']
rest_mm = sum(p['current']['eth_ref'] or 0 for p in P if p['category'] == 'lending' and p['id'].endswith(':rest'))
check('categories_equal_the_layer', math.isclose(cat['loops']['eth_ref'], snap['loops'], rel_tol=1e-9) and math.isclose(cat['lending']['eth_ref'] - rest_mm, snap['money_markets'], rel_tol=1e-9),
      [cat['loops']['eth_ref'], snap['loops'], cat['lending']['eth_ref'], snap['money_markets']])
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
