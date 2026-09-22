"""Babylon: stats + finality providers (staking-api) + all ACTIVE BTC delegations (Babylon LCD, publicnode).
Output: raw/babylon_stats.json, raw/babylon_fps.json, raw/babylon_active_delegations.json (slim)"""
import json, os, urllib.request, urllib.parse, time
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh) Chrome/124'}
def get(u):
    for a in range(5):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
        except Exception as e: print('retry', u[:80], e); time.sleep(5 + 5 * a)
    raise SystemExit('failed ' + u)
json.dump(get('https://staking-api.babylonlabs.io/v2/stats'), open(os.path.join(D, 'raw', 'babylon_stats.json'), 'w'))
fps = []; pk = ''
while True:
    d = get('https://staking-api.babylonlabs.io/v2/finality-providers' + ('?pagination_key=' + pk if pk else ''))
    fps += d['data']; pk = d.get('pagination', {}).get('next_key', '')
    if not pk: break
json.dump(fps, open(os.path.join(D, 'raw', 'babylon_fps.json'), 'w'))
out = []; key = None
while True:
    u = 'https://babylon-rest.publicnode.com/babylon/btcstaking/v1/btc_delegations/ACTIVE?pagination.limit=500'
    if key: u += '&pagination.key=' + urllib.parse.quote(key)
    d = get(u)
    for x in d['btc_delegations']:
        out.append({k: x.get(k) for k in ('staker_addr', 'btc_pk', 'fp_btc_pk_list', 'total_sat', 'start_height', 'end_height', 'staking_time', 'status_desc')})
    key = d.get('pagination', {}).get('next_key')
    print(len(out), flush=True)
    if not key: break
json.dump(out, open(os.path.join(D, 'raw', 'babylon_active_delegations.json'), 'w'))
print('done', len(out), sum(int(x['total_sat']) for x in out) / 1e8)
