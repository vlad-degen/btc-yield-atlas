"""Parallel variant of 02_fetch_protocols.py (4 workers, backoff on 429). Usage: python3 02b_fetch_parallel.py slugs.json"""
import json, os, sys, time, urllib.request, urllib.error, threading, queue
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, 'raw', 'proto')
slugs = json.load(open(sys.argv[1]))
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
q = queue.Queue()
for s in slugs:
    f = os.path.join(OUT, s + '.json')
    if not (os.path.exists(f) and os.path.getsize(f) > 200): q.put(s)
print('todo', q.qsize(), flush=True)
lock = threading.Lock(); done = [0]; pause = [0.0]
def worker():
    while True:
        try: s = q.get_nowait()
        except queue.Empty: return
        for attempt in range(6):
            while time.time() < pause[0]: time.sleep(1)
            try:
                req = urllib.request.Request('https://api.llama.fi/protocol/' + s, headers=UA)
                data = urllib.request.urlopen(req, timeout=120).read(); json.loads(data)
                open(os.path.join(OUT, s + '.json'), 'wb').write(data); break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    with lock: pause[0] = time.time() + 20
                    continue
                print(s, 'HTTP', e.code, flush=True); break
            except Exception as e:
                print(s, 'ERR', e, flush=True); time.sleep(3)
        with lock:
            done[0] += 1
            if done[0] % 100 == 0: print('progress', done[0], flush=True)
ts = [threading.Thread(target=worker) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
print('DONE', flush=True)
