"""Step 1b: second pass on classify_raw.json. Safe owners/threshold/modules, explorer page titles (name tags) for every
account, Blockscout retries. Output raw/.../classify2.json."""
import json, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from common import *

UA = L.UA
DOM = {1: 'etherscan.io', 8453: 'basescan.org', 42161: 'arbiscan.io', 480: 'worldscan.org', 747474: 'katanascan.com'}

def es_title(ch, a):
    if ch not in DOM: return None
    for i in range(4):
        try:
            h = urllib.request.urlopen(urllib.request.Request('https://%s/address/%s' % (DOM[ch], a), headers={'user-agent': UA}), timeout=60).read().decode('utf8', 'ignore')
            t = ' '.join(re.search(r'<title>(.*?)</title>', h, re.S).group(1).split())
            cn = re.search(r'Contract Name\s*(?:<[^>]+>\s*)*([^<]+)', h)
            tok = re.search(r'Token Tracker.{0,600}?href="/token/0x[0-9a-fA-F]{40}"[^>]*>(?:<[^>]+>)*([^<]+)', h, re.S)
            return dict(title=t, cname=cn and cn.group(1).strip(), token=tok and tok.group(1).strip())
        except Exception as e:
            time.sleep(3 * (i + 1)); err = str(e)
    return {'_error': err}

def main():
    res = load('classify_raw.json')
    out = load('classify2.json', {})
    # Safe details
    safes = [k for k, v in res.items() if 'getOwners' in v.get('probe', {}) and k not in out]
    for ch in sorted({int(k.split(':')[0]) for k in safes}):
        ks = [k for k in safes if int(k.split(':')[0]) == ch]; b = blk(ch)
        cl = []
        for k in ks:
            a = k.split(':')[1]
            cl += [(a, '0xa0e67e2b'), (a, '0xe75235b8'), (a, '0xcc2f8452' + a32('0x0000000000000000000000000000000000000001') + u32(20))]
        r = mcall(ch, cl, b, size=150)
        for i, k in enumerate(ks):
            ow = L.addr_list(r[3 * i]) if r[3 * i] else []
            th = U(r[3 * i + 1])
            mods = []
            if r[3 * i + 2]:
                h = r[3 * i + 2][2:]; off = int(h[:64], 16) * 2; n = int(h[off:off + 64], 16)
                mods = ['0x' + h[off + 64 + 64 * j + 24: off + 128 + 64 * j] for j in range(n)]
            out[k] = dict(owners=ow, threshold=th, modules=mods)
        # owner kinds
        allo = sorted({o for k in ks for o in out[k]['owners']})
        codes = {}
        def gc(o): return o, rpc(ch, 'eth_getCode', [o, hex(b)])
        with ThreadPoolExecutor(8) as ex:
            for o, c in ex.map(gc, allo): codes[o] = 'EOA' if c in ('0x', '', None) else ('EIP-7702' if c.startswith('0xef0100') else 'contract')
        for k in ks: out[k]['owner_kinds'] = [codes[o] for o in out[k]['owners']]
        save('classify2.json', out)
        log('safes chain', ch, len(ks))
    # single owner() for DSProxy / DPM / other
    for k, v in res.items():
        if k in out and 'owner' in out[k]: continue
        o = v.get('probe', {}).get('owner')
        if o: out.setdefault(k, {})['owner'] = A(o)
    # Blockscout retries on chain 1
    def bsinfo(key):
        ch, a = key.split(':')
        j = getjson(BSCOUT[int(ch)] + '/api/v2/addresses/' + a, retries=5)
        if '_error' in j: return key, {'_error': j['_error']}
        return key, dict(name=j.get('name'), impl=[i.get('name') for i in (j.get('implementations') or [])],
                         tags=[t.get('display_name') for t in ((j.get('metadata') or {}).get('tags') or [])] + [t.get('display_name') for t in (j.get('public_tags') or [])],
                         creator=j.get('creator_address_hash'), token=(j.get('token') or {}).get('name'), ens=j.get('ens_domain_name'))
    todo = [k for k, v in res.items() if k.startswith('1:') and (v.get('bs') is None or '_error' in (v.get('bs') or {}))]
    with ThreadPoolExecutor(2) as ex:
        for key, info in ex.map(bsinfo, todo):
            out.setdefault(key, {})['bs'] = info
    save('classify2.json', out)
    log('blockscout retries', len(todo))
    # explorer titles for everything
    todo = [k for k in res if 'es' not in out.get(k, {})]
    def one(k):
        ch, a = k.split(':'); time.sleep(0.3)
        return k, es_title(int(ch), a)
    n = 0
    with ThreadPoolExecutor(3) as ex:
        for k, t in ex.map(one, todo):
            out.setdefault(k, {})['es'] = t; n += 1
            if n % 100 == 0: save('classify2.json', out); log('titles', n)
    save('classify2.json', out)
    log('done')

if __name__ == '__main__':
    main()
