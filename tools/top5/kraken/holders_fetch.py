"""Paginate Blockscout (Ink) token holders of the vault share token sentoraBTC.
Output: raw/holders_ink.jsonl (one compact row per holder) + raw/holders_meta.json
Run: python3 holders_fetch.py   (resumable: continues from last saved next_page_params)
"""
import json, subprocess, time, os, sys
BASE = 'https://explorer.inkonchain.com/api/v2/tokens/0x7dee0120739b7ec048b469939efb178adbbb19b2/holders'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
OUT = os.path.join(os.path.dirname(__file__), '..', 'raw', 'holders_ink.jsonl')
STATE = os.path.join(os.path.dirname(__file__), '..', 'raw', 'holders_state.json')

def get(url):
    for t in range(8):
        r = subprocess.run(['curl', '-s', '-m', '60', '-A', UA, url], capture_output=True)
        try:
            return json.loads(r.stdout.decode())
        except Exception:
            time.sleep(2 + 3 * t)
    raise RuntimeError('failed ' + url)

state = json.load(open(STATE)) if os.path.exists(STATE) else {'next': None, 'pages': 0, 'started': time.time()}
f = open(OUT, 'a')
while True:
    url = BASE
    if state['next']:
        np = state['next']
        url += '?' + '&'.join(f'{k}={v}' for k, v in np.items())
    elif state['pages'] > 0:
        break
    d = get(url)
    if 'items' not in d:
        print('bad', str(d)[:200]); time.sleep(10); continue
    for it in d['items']:
        a = it['address']
        row = dict(addr=a['hash'], v=int(it['value']), c=a.get('is_contract'), p=a.get('proxy_type'),
                   impl=[i.get('name') for i in (a.get('implementations') or [])],
                   impl_addr=[i.get('address_hash') for i in (a.get('implementations') or [])],
                   name=a.get('name'), tags=[t.get('display_name') for t in (a.get('public_tags') or [])])
        f.write(json.dumps(row) + '\n')
    f.flush()
    state['pages'] += 1
    state['next'] = d.get('next_page_params')
    json.dump(state, open(STATE, 'w'))
    if state['pages'] % 25 == 0:
        print('pages', state['pages'], 'last value', d['items'][-1]['value'] if d['items'] else None, flush=True)
    if not state['next']:
        break
    time.sleep(0.35)
state['finished'] = time.time()
json.dump(state, open(STATE, 'w'))
print('done pages', state['pages'])
