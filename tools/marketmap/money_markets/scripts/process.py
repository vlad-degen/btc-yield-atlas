"""Money-market / CDP / venue / curator BTC by protocol, chain and month from DefiLlama /protocol/{slug} token units.

Month points (map convention): month-end = DefiLlama point stamped 00:00 UTC on the 1st of the next month (3 days back if
missing); 2026-09 = the 2026-09-20 point (1 day back if missing). Token units from chainTvls[chain].tokens; keys ending
'-borrowed' give borrowed BTC; 'borrowed', 'staking', 'pool2' (and the other aggregate keys, same list as 10_build.py) skipped.
Output: out/mm_long.json (slug -> month -> chain -> {tvl: {sym: [units, usd]}, borrowed: {...}}) and out/segments.json."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mmlib import *
from tokens import classify, is_partial
sys.path.insert(0, os.path.join(REPO, 'tools', 'marketmap', 'scripts'))
from products import P as PRODUCTS  # noqa: E402

OUT = os.path.join(D, 'out'); os.makedirs(OUT, exist_ok=True)
FL = json.load(open(os.path.join(RAW, 'fetch_list.json')))
PR = {p['slug']: p for p in json.load(open(os.path.join(RAW, 'protocols.json')))}
PRICE = map_prices()

C0 = {'cdp': FL['c0']['cdp'], 'venue': FL['c0']['venue'], 'curator': FL['c0']['curator']}
c0_slugs = {s: seg for seg, ss in C0.items() for s in ss}
c0_name = {p['slug']: p['product'].split(': ', 1)[-1] for p in PRODUCTS if p['cat'] == 'C0'}

ADJ = []
def values(slug):
    d = load(slug)
    res = {}
    for m, dl, pd in MONTHS:
        snap = (m == '2026-09')
        px = PRICE[m]
        per_chain = {}
        for key, base, kind in chain_keys(d):
            su, dd = pick(series(d, key, True), dl, 1 if snap else 3)
            sd, _ = pick(series(d, key, False), dl, 1 if snap else 3)
            su = su or {}; sd = sd or {}
            acc = per_chain.setdefault(base, {'tvl': {}, 'borrowed': {}, 'other_btc_like': {}})
            for s in set(su) | set(sd):
                cs, w, cl = classify(s, base)
                u, usd = su.get(s) or 0.0, sd.get(s) or 0.0
                if cl is None:
                    if 'BTC' in s.upper() and kind == 'tvl' and (u or usd):
                        acc['other_btc_like'][s] = [u, usd]
                    continue
                if is_partial(cs):  # LP tokens: BTC share of USD value / BTC price (the map's estimate)
                    units = w * usd / px
                else:
                    units = u * w
                    if units > 0 and usd <= 0:
                        ADJ.append((slug, m, key, s, units, 'unpriced: not in DefiLlama TVL, skipped'))
                        continue
                    if units > 0 and usd < 0.5 * units * px:  # depegged / mispriced wrapper (e.g. Huobi HBTC on Kava): BTC value, not units
                        ADJ.append((slug, m, key, s, units, f'depegged: {units:.2f} units valued at {usd / px:.2f} BTC; value used'))
                        units = usd / px
                if units == 0 and usd == 0:
                    continue
                slot = acc[kind].setdefault(cs, [0.0, 0.0, cl])
                slot[0] += units; slot[1] += usd * w
        res[m] = per_chain
    return res

# ---------- universe: every fetched slug of the screen + C0 slugs ----------
EXTRA = ['accountable', 'townsquare-lending']  # Uncollateralized/Lending protocols below the $1M TVL screen (TVL excludes borrowed; yields-only BTC)
slugs = sorted(set(FL['fetch']) | set(EXTRA))
long = {}; seg = {}
for s in slugs:
    if not os.path.exists(os.path.join(RAW, 'proto', s + '.json')):
        print('missing', s); continue
    long[s] = values(s)
json.dump(long, open(os.path.join(OUT, 'mm_long.json'), 'w'))
json.dump(ADJ, open(os.path.join(OUT, 'unit_adjustments.json'), 'w'), indent=0)

def tot(slug, m, kind='tvl'):
    return sum(v[0] for ch in long[slug][m].values() for v in ch[kind].values())

rows = []
for s in slugs:
    if s not in long: continue
    cat = PR.get(s, {}).get('category', '')
    snap_t, snap_b = tot(s, '2026-09'), tot(s, '2026-09', 'borrowed')
    peak = max(tot(s, m) + tot(s, m, 'borrowed') for m, _, _ in MONTHS)
    if s in c0_slugs:
        sg, why = c0_slugs[s], 'C0 slug in products.py'
    elif cat == 'CDP':
        sg, why = 'cdp', 'CDP category, not in products.py'
    elif cat in ('Lending', 'Uncollateralized Lending'):
        sg, why = 'money_market', f'{cat} category'
    else:
        sg, why = None, f'category {cat}'
    rows.append(dict(slug=s, name=PR.get(s, {}).get('name', c0_name.get(s, s)), category=cat, segment=sg, why=why,
                     snap_btc=snap_t, snap_borrowed=snap_b, peak_supplied=peak))
json.dump(rows, open(os.path.join(OUT, 'screen_results.json'), 'w'), indent=0)
thr = 1e6 / PRICE_SNAP
for r in sorted(rows, key=lambda x: -(x['snap_btc'] + x['snap_borrowed'])):
    if r['snap_btc'] + r['snap_borrowed'] >= 1 or r['peak_supplied'] >= 50:
        print(f"{str(r['segment']):12s} {r['slug']:30s} {r['category'][:22]:22s} now={r['snap_btc']:10.2f} bor={r['snap_borrowed']:8.2f} peak={r['peak_supplied']:10.2f}")
