"""Fetch https://api.llama.fi/protocol/{slug} for the screening list into raw/proto/{slug}.json (streamed by curl, cached).
Usage: python3 fetch_protocols.py [slug ...]  (default: raw/fetch_list.json 'fetch')"""
import json, os, random, subprocess, sys, time
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, 'raw', 'proto')
os.makedirs(OUT, exist_ok=True)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
slugs = sys.argv[1:] or json.load(open(os.path.join(D, 'raw', 'fetch_list.json')))['fetch']
# big first so that the rest can proceed if they time out
todo = [s for s in slugs if not (os.path.exists(os.path.join(OUT, s + '.json')) and os.path.getsize(os.path.join(OUT, s + '.json')) > 200)]
print('todo', len(todo), 'of', len(slugs), flush=True)
for i, s in enumerate(todo):
    f = os.path.join(OUT, s + '.json')
    tmp = f + '.part'
    ok = False
    for attempt in range(14):
        # a cached 502 at the edge for some slugs: the API is case-insensitive, so vary the case on retries
        variant = s if attempt == 0 else ''.join(c.upper() if random.random() < 0.5 else c for c in s)
        r = subprocess.run(['curl', '-sS', '--compressed', '-A', UA, '-o', tmp, '-w', '%{http_code}', '--max-time', '600',
                            'https://api.llama.fi/protocol/' + variant], capture_output=True, text=True)
        code = r.stdout.strip()
        if code == '200':
            try:
                with open(tmp) as fh:
                    json.load(fh)
                os.replace(tmp, f)
                ok = True
                break
            except Exception as e:
                print(s, 'bad json', e, flush=True)
                time.sleep(5)
        elif code == '429':
            print(s, '429, waiting', flush=True)
            time.sleep(30 + 15 * attempt)
        else:
            print(s, 'HTTP', code, r.stderr[:200], flush=True)
            if code in ('404', '400'):
                break
            if code in ('502', '504', '500') and attempt >= 12:
                break  # server-side failure for this slug: skip, retry in a later pass
            time.sleep(1.5)
    if not ok:
        print('FAILED', s, flush=True)
    else:
        print(i, s, os.path.getsize(f) // 1024, 'KB', flush=True)
    time.sleep(0.6)
print('DONE', flush=True)
