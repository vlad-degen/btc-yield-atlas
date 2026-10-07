"""Daily TVL charts of the DEX pools used for projects without a token breakdown (DefiLlama yields /chart/{pool})."""
import concurrent.futures as cf, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import RAW
from decisions import POOL_PROJECTS, pool_eth_share

D = os.path.join(RAW, 'pool_charts'); os.makedirs(D, exist_ok=True)
pools = [p for p in json.load(open(os.path.join(RAW, 'yield_pools.json')))['data']
         if p['project'] in POOL_PROJECTS and p['tvlUsd'] >= 1e6 and pool_eth_share([x.upper() for x in p['symbol'].replace('/', '-').split('-')]) > 0]


def get(pid):
    path = os.path.join(D, pid + '.json')
    if os.path.exists(path):
        return
    for i in range(4):
        try:
            with urllib.request.urlopen(f'https://yields.llama.fi/chart/{pid}', timeout=60) as r:
                data = r.read()
            open(path, 'wb').write(data); return
        except Exception:
            time.sleep(3 + 3 * i)


with cf.ThreadPoolExecutor(6) as ex:
    list(ex.map(get, [p['pool'] for p in pools]))
print(len(pools), 'pools;', len(os.listdir(D)), 'charts')
