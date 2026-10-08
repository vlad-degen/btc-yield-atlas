"""Morpho market metadata (token addresses and whether the API prices them), used by build.py to drop look-alike tokens
(e.g. a fake 'cbBTC' loan token or an unpriced 'wsBTCD' collateral that would otherwise count at a 1:1 rate).
Usage: python3 morpho_meta.py <chainId> [...]
"""
import sys
from lib import *
for c in sys.argv[1:]:
    ch = int(c); out = {}; skip = 0
    while True:
        j = gql('''{ markets(first:500, skip:%d, where:{chainId_in:[%d]}){ items{ marketId listed collateralAsset{address symbol priceUsd} loanAsset{address symbol priceUsd} } pageInfo{countTotal} } }''' % (skip, ch))
        if not j.get('data'): break
        for m in j['data']['markets']['items']:
            out[m['marketId']] = dict(listed=m['listed'], coll=m['collateralAsset'], loan=m['loanAsset'])
        skip += 500
        if skip >= j['data']['markets']['pageInfo']['countTotal']: break
    save('morpho_meta_%d.json' % ch, out); log(ch, len(out))
