"""Step 1: classify every lending-split account whose collateral backing dollar debt (A2+B2) is >= 100 ETH.
Reads code at the snapshot block, probes view functions, and pulls Blockscout names/tags. Output raw/.../classify_raw.json."""
import csv, hashlib, json, os
from concurrent.futures import ThreadPoolExecutor
from common import *

SEL = {'name': '0x06fdde03', 'symbol': '0x95d89b41', 'totalSupply': '0x18160ddd', 'asset': '0x38d52e0f', 'owner': '0x8da5cb5b',
       'getOwners': '0xa0e67e2b', 'getThreshold': '0xe75235b8', 'authority': '0xbf7e214f', 'hook': '0x7f5a7c7b', 'vault': '0xfbfa77cf',
       'version': '0x54fd4d50', 'VERSION': '0xffa1ad74', 'cache': '0x60c7d295', 'totalAssets': '0x01e1d114', 'manager': '0x481c6a75',
       'creditManager': '0xc12c21c0', 'borrower': '0x7df1f1b9', 'factory': '0xc45a0155', 'admin': '0xf851a440', 'accountant': '0x4fb3ccc5',
       'getFuses': '0x4f41f9ed', 'curator': '0xe66f53b7', 'strategist': '0x1fe4a686', 'governance': '0x5aa6e675', 'keeper': '0xaced1661',
       'want': '0x1f1fcd51', 'pendingOwner': '0xe30c3978', 'subvaultIndex': '0x0b4c7e4d', 'implementations': '0x47b8d6d7'}
SLOT1967 = '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'
SLOTBEACON = '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'

def main():
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, 'data/eth/lending_split_accounts.csv')))
            if r['side'] == 'eth' and float(r['A2'] or 0) + float(r['B2'] or 0) >= 100]
    accts = {}
    for r in rows:
        a = r['account'].split('@')[0].lower(); ch = int(r['chain'])
        accts.setdefault((ch, a), []).append(r)
    log('accounts', len(accts))
    classify_keys(list(accts), 'classify_raw.json')


def tagb(ch):
    b = blk(ch)
    return hex(b) if b else 'latest'


def classify_keys(keys, cache):
    """keys: list of (chain, address). Probes code, view functions, proxy slots and Blockscout names; caches in RAW/cache."""
    res = load(cache, {})
    todo = [k for k in keys if '%d:%s' % k not in res]
    def code_of(k):
        ch, a = k
        try: return k, rpc(ch, 'eth_getCode', [a, tagb(ch)], retries=4)
        except Exception: return k, rpc(ch, 'eth_getCode', [a, 'latest'], retries=4)
    with ThreadPoolExecutor(8) as ex:
        codes = dict(ex.map(code_of, todo))
    for ch in sorted({k[0] for k in todo}):
        ks = [k for k in todo if k[0] == ch and codes[k] not in ('0x', '', None) and not codes[k].startswith('0xef0100')]
        cl = [(k[1], s) for k in ks for s in SEL.values()]
        try: out = mcall(ch, cl, tagb(ch), size=200)
        except Exception: out = [None] * len(cl)
        n = len(SEL)
        for i, k in enumerate(ks):
            probe = {}
            for j, nm in enumerate(SEL):
                v = out[i * n + j]
                if v and v != '0x': probe[nm] = v
            res['%d:%s' % k] = {'probe': probe}
        for k in todo:
            if k[0] != ch: continue
            c = codes[k] or '0x'
            rec = res.setdefault('%d:%s' % k, {})
            rec['codelen'] = (len(c) - 2) // 2
            rec['codehash'] = hashlib.sha256(bytes.fromhex(c[2:])).hexdigest()[:16] if len(c) > 2 else None
            rec['kind0'] = 'EOA' if c in ('0x', '') else ('EIP-7702' if c.startswith('0xef0100') else 'contract')
            if c.startswith('0xef0100'): rec['delegate'] = '0x' + c[8:48]
            if c.startswith('0x363d3d373d3d3d363d73'): rec['eip1167'] = '0x' + c[22:62]
            if rec['kind0'] == 'contract' and rec['codelen'] < 400: rec['code'] = c
        for k in ks:
            rec = res['%d:%s' % k]
            for nm, sl in (('impl1967', SLOT1967), ('beacon', SLOTBEACON)):
                try: v = rpc(ch, 'eth_getStorageAt', [k[1], sl, tagb(ch)], retries=3)
                except Exception: v = None
                if v and int(v, 16): rec[nm] = '0x' + v[-40:]
        save(cache, res)
        log('chain', ch, 'done', len(ks), 'contracts')
    # Blockscout names
    def bsinfo(key):
        ch, a = key.split(':'); ch = int(ch)
        if ch != 1: return key, None
        j = getjson(BSCOUT[ch] + '/api/v2/addresses/' + a, retries=5)
        if '_error' in j: return key, {'_error': j['_error']}
        return key, dict(name=j.get('name'), impl=[i.get('name') for i in (j.get('implementations') or [])],
                         tags=[t.get('display_name') for t in ((j.get('metadata') or {}).get('tags') or [])] + [t.get('display_name') for t in (j.get('public_tags') or [])],
                         creator=j.get('creator_address_hash'), token=(j.get('token') or {}).get('name'), ens=j.get('ens_domain_name'))
    todo = [k for k, v in res.items() if v.get('kind0') == 'contract' and 'bs' not in v]
    with ThreadPoolExecutor(4) as ex:
        for key, info in ex.map(bsinfo, todo):
            res[key]['bs'] = info
    save(cache, res)
    log('done', len(res))
    return res

if __name__ == '__main__':
    main()
