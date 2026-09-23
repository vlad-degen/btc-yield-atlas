"""Fetch https://yields.llama.fi/chart/{pool} for BTC lending pools (tvlUsd >= MIN today) into raw/charts/ (cached).
Pools: raw/btc_lending_pools.json (written by select_pools.py). Spaced requests, backoff on errors / Cloudflare pages."""
import json, os, subprocess, sys, time
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, 'raw', 'charts')
os.makedirs(OUT, exist_ok=True)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 3e5
pools = [p for p in json.load(open(os.path.join(D, 'raw', 'btc_lending_pools.json'))) if p['tvlUsd'] >= MIN]
todo = [p['pool'] for p in pools if not os.path.exists(os.path.join(OUT, p['pool'] + '.json'))]
print('todo', len(todo), 'of', len(pools), flush=True)
for i, pid in enumerate(todo):
    f = os.path.join(OUT, pid + '.json')
    for attempt in range(6):
        r = subprocess.run(['curl', '-sS', '--compressed', '-A', UA, '-o', f + '.part', '-w', '%{http_code}', '--max-time', '120',
                            'https://yields.llama.fi/chart/' + pid], capture_output=True, text=True)
        code = r.stdout.strip()
        ok = False
        if code == '200':
            try:
                d = json.load(open(f + '.part'))
                if isinstance(d, dict) and 'data' in d:
                    os.replace(f + '.part', f); ok = True
            except Exception:
                pass
        if ok:
            break
        print(pid, 'code', code, 'retry', attempt, flush=True)
        time.sleep(10 * (attempt + 1))
    else:
        print('FAILED', pid, flush=True)
    if i % 20 == 0:
        print('progress', i, len(todo), flush=True)
    time.sleep(1.5)
print('DONE', flush=True)
