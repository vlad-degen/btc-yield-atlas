"""Step 2b: classify the owners of venue positions found in step 2 (raw/.../venues/*.json, eth_backing_dollar >= 100 ETH)
with the same probes as classify.py. Cache raw/.../classify_venues.json."""
import glob, json, os
import chains  # noqa: adds RPCs for extra chains in memory
import vcommon  # noqa
from common import *
from classify import classify_keys
L.RPCS.setdefault(534352, ['https://rpc.scroll.io', 'https://scroll.drpc.org'])
L.RPCS.setdefault(324, ['https://mainnet.era.zksync.io'])
L.RPCS.setdefault(42220, ['https://forno.celo.org'])

def venue_positions():
    out = []
    for f in sorted(glob.glob(os.path.join(RAW, 'venues', '*.json'))):
        b = os.path.basename(f)
        if b.startswith('blocks') or b.endswith('_rows.json') or b.endswith('_parts.json') or 'summary' in b: continue
        d = json.load(open(f))
        for p in d.get('positions', []):
            if (p.get('eth_backing_dollar') or 0) >= 100:
                p = dict(p); p['_file'] = b; out.append(p)
    return out

def main():
    ps = venue_positions()
    keys = sorted({(int(p['chain']), p['account'].split('@')[0].lower()) for p in ps})
    log('positions', len(ps), 'accounts', len(keys))
    classify_keys(keys, 'classify_venues.json')

if __name__ == '__main__':
    main()
