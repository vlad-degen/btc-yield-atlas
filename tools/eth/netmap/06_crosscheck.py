"""Cross-check of the map against DefiLlama's yields list: ETH pools above $1M whose project is neither a map row
nor an explained exclusion. Writes data/eth/netmap/crosscheck.json (read by the site's Data section)."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import OUT, RAW, eth_weight
import decisions as DEC

pools = json.load(open(os.path.join(RAW, 'yield_pools.json')))['data']
ch = json.load(open(os.path.join(OUT, 'market_chapter.json')))
mapped = {p['id'] for p in ch['products']} | {p['id'].split(':', 1)[1] for p in ch['products'] if p['id'].startswith('pools:')} | set(DEC.LOOPS_IN_LENDING)  # loop products: inside leveraged staking
screen = json.load(open(os.path.join(RAW, 'screen.json')))
by = collections.defaultdict(lambda: {'pools': 0, 'tvlUsd': 0.0, 'symbols': []})
total = collections.Counter()
for p in pools:
    parts = [x.upper() for x in p['symbol'].replace('/', '-').split('-')]
    if p['tvlUsd'] < 1e6 or not any(eth_weight(x) for x in parts):
        continue
    proj = p['project']
    status = 'map' if proj in mapped else 'excluded' if proj in DEC.EXCLUDE else 'screened out (under 100 ETH today and under 1,000 at every month-end)' if proj in json.load(open(os.path.join(RAW, 'candidates.json'))) else 'not a candidate'
    total[status] += p['tvlUsd']
    if status in ('map', 'excluded'):
        continue
    r = by[proj]; r['pools'] += 1; r['tvlUsd'] += p['tvlUsd']; r['symbols'].append(p['symbol']); r['status'] = status; r['chain'] = p['chain']
rows = sorted(({'project': k, **v, 'symbols': v['symbols'][:4]} for k, v in by.items()), key=lambda r: -r['tvlUsd'])
out = {'pools_checked': sum(1 for p in pools if p['tvlUsd'] >= 1e6 and any(eth_weight(x.upper()) for x in p['symbol'].replace('/', '-').split('-'))),
       'tvl_by_status': dict(total), 'not_in_map': rows,
       'note': 'Pool TVL is the whole pool in USD on 7 October (DefiLlama yields list), not its ETH side at the snapshot.'}
json.dump(out, open(os.path.join(OUT, 'crosscheck.json'), 'w'), indent=1)
print(out['pools_checked'], 'pools;', {k: round(v / 1e6) for k, v in total.items()}, '$M;', len(rows), 'projects not in map')
for r in rows[:25]:
    print(f"  {r['project']:32} {r['tvlUsd']/1e6:8.1f}M {r['pools']:3} {r['status'][:20]} {r['symbols']}")

# Re-check: the largest DefiLlama rows read again at the latest point in the pull (7 October), ETH part at that point's price
from lib import series, price, eth_part
import datetime
latest = datetime.date(2026, 10, 7)
rows = []
for p in sorted(ch['products'], key=lambda p: -(p['current']['eth_ref'] or 0)):
    if ':' in p['id'] or p['category'] in ('lending', 'cdp'):
        continue
    ser = series(p['id'])
    if not ser:
        continue
    last = max(ser); pr = price(last); snap = screen[p['id']]['snap_eth']
    later = eth_part(ser[last])[0] / pr if pr else None
    rows.append({'product': p['name'], 'snapshot_gross_eth': snap, 'later_gross_eth': later, 'later_date': last.isoformat(),
                 'change': (later / snap - 1) if snap and later is not None else None})
    if len(rows) >= 15:
        break
out['recheck'] = rows
json.dump(out, open(os.path.join(OUT, 'crosscheck.json'), 'w'), indent=1)
print('recheck', [(r['product'], round((r['change'] or 0) * 100, 2)) for r in rows])
