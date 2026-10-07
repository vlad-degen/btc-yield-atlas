"""What each product paid around the snapshot: the largest ETH pool of each map row on DefiLlama's yields list,
its base and reward APY on 2026-10-02 (pool chart), for the site's product table."""
import concurrent.futures as cf, datetime, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import RAW, OUT, eth_weight

D = os.path.join(RAW, 'pool_charts'); os.makedirs(D, exist_ok=True)
pools = json.load(open(os.path.join(RAW, 'yield_pools.json')))['data']
meta = json.load(open(os.path.join(OUT, 'map.json')))['meta']
best = {}
for p in pools:
    slug = p['project']
    if slug not in meta:
        continue
    parts = [x.upper() for x in p['symbol'].replace('/', '-').split('-')]
    if not any(eth_weight(x) for x in parts):
        continue
    if slug not in best or p['tvlUsd'] > best[slug]['tvlUsd']:
        best[slug] = p


def get(pid):
    path = os.path.join(D, pid + '.json')
    if not os.path.exists(path):
        for i in range(4):
            try:
                with urllib.request.urlopen(f'https://yields.llama.fi/chart/{pid}', timeout=60) as r:
                    open(path, 'wb').write(r.read()); break
            except Exception:
                time.sleep(3 + 3 * i)
    return pid


with cf.ThreadPoolExecutor(6) as ex:
    list(ex.map(get, [p['pool'] for p in best.values()]))
T = datetime.date(2026, 10, 2)
out = {}
for slug, p in best.items():
    try:
        rows = json.load(open(os.path.join(D, p['pool'] + '.json')))['data']
    except Exception:
        continue
    pick = None
    for r in rows:
        d = datetime.date.fromisoformat(r['timestamp'][:10])
        if d <= T and (pick is None or d >= pick[0]):
            pick = (d, r)
    if pick:
        d, r = pick
        out[slug] = dict(pool=p['pool'], symbol=p['symbol'], chain=p['chain'], date=d.isoformat(),
                         apy_base=r.get('apyBase'), apy_reward=r.get('apyReward'), apy=r.get('apy'), tvl_usd=r.get('tvlUsd'))
json.dump(out, open(os.path.join(OUT, 'yields_T.json'), 'w'), indent=1)
print(len(out), 'products with a dated pool yield')
