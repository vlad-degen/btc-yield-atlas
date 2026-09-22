"""Fetch https://api.llama.fi/protocol/{slug} for every candidate into raw/proto/ (cached; delete a file to refetch).
Usage: python3 02_fetch_protocols.py [slug ...]   (no args = all candidates)"""
import json, os, sys, time, urllib.request, urllib.error
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, 'raw', 'proto'); os.makedirs(OUT, exist_ok=True)
slugs = sys.argv[1:] or list(json.load(open(os.path.join(D, 'raw', 'candidates.json'))).keys())
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
todo = [s for s in slugs if not (os.path.exists(os.path.join(OUT, s + '.json')) and os.path.getsize(os.path.join(OUT, s + '.json')) > 200)]
print('todo', len(todo), 'of', len(slugs), flush=True)
for i, s in enumerate(todo):
    for attempt in range(6):
        try:
            req = urllib.request.Request('https://api.llama.fi/protocol/' + s, headers=UA)
            data = urllib.request.urlopen(req, timeout=120).read()
            json.loads(data)
            open(os.path.join(OUT, s + '.json'), 'wb').write(data)
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(i, s, '429 wait', flush=True); time.sleep(20 + 10 * attempt); continue
            print(i, s, 'HTTP', e.code, flush=True); break
        except Exception as e:
            print(i, s, 'ERR', e, flush=True); time.sleep(5)
    time.sleep(0.35)
    if i % 25 == 0: print('progress', i, len(todo), flush=True)
print('DONE', flush=True)
