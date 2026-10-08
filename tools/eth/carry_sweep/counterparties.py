"""Step 1c: for every Ethereum EOA, EIP-7702 account and Safe in the step-1 set, read its latest ERC-20 transfers from Blockscout
(up to 3 pages, about 150 transfers) and keep the contract counterparties with their Blockscout names. A wallet run for a vault
shows the vault (or its silo / strategy) as a counterparty. Output raw/.../counterparties.json."""
import json, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from common import *

def main():
    res = load('classify_raw.json'); c2 = load('classify2.json')
    out = load('counterparties.json', {})
    todo = [k for k, v in res.items() if k.startswith('1:') and (v['kind0'] in ('EOA', 'EIP-7702') or 'owners' in c2.get(k, {})) and k not in out]
    def one(k):
        a = k.split(':')[1]; url = BSCOUT[1] + '/api/v2/addresses/%s/token-transfers' % a
        cps = {}; nxt = None; n = 0
        for p in range(3):
            j = getjson(url + ('?' + urllib.parse.urlencode(nxt) if nxt else ''), retries=5)
            if '_error' in j: return k, {'_error': j['_error'], 'cps': cps}
            for it in j.get('items', []):
                n += 1
                for side in ('from', 'to'):
                    x = it.get(side) or {}
                    h = (x.get('hash') or '').lower()
                    if h == a or not x.get('is_contract'): continue
                    d = cps.setdefault(h, {'name': x.get('name'), 'impl': [i.get('name') for i in (x.get('implementations') or [])], 'n': 0, 'tokens': {}})
                    d['n'] += 1
                    sym = (it.get('token') or {}).get('symbol'); d['tokens'][sym] = d['tokens'].get(sym, 0) + 1
            nxt = j.get('next_page_params')
            if not nxt: break
        return k, {'n_transfers': n, 'cps': cps}
    done = 0
    with ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(one, todo):
            out[k] = r; done += 1
            if done % 100 == 0: save('counterparties.json', out); log('done', done, len(todo))
    save('counterparties.json', out); log('finished', len(out))

if __name__ == '__main__':
    main()
