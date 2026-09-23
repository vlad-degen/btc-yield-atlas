"""Scan every fetched protocol at the 2026-09-20 point (and the max over month-ends) for BTC-like token symbols.
Output raw/symbol_scan.json: {slug: {chainkey: {SYM: [units, usd]}}} for symbols that are in the map's BTC list or contain 'BTC'."""
import json, os, glob, datetime
from mmlib import *

def btc_like(s):
    su = s.upper()
    return btc_weight(su) > 0 or 'BTC' in su or su in ('RBTC', 'WRBTC')

out = {}
files = sorted(glob.glob(os.path.join(RAW, 'proto', '*.json')))
for f in files:
    slug = os.path.basename(f)[:-5]
    try:
        d = load(slug)
    except Exception as e:
        print('ERR', slug, e); continue
    res = {}
    for key, base, kind in chain_keys(d):
        su, _ = pick(series(d, key, True), SNAP, 1)
        sd, _ = pick(series(d, key, False), SNAP, 1)
        su = su or {}; sd = sd or {}
        # also max over month-ends (catch tokens that were large in the past)
        mx = {}
        su_s = series(d, key, True)
        for m, dl, pd in MONTHS:
            t, _ = pick(su_s, dl, 3)
            for s, v in (t or {}).items():
                if btc_like(s) and v:
                    mx[s] = max(mx.get(s, 0), v)
        syms = {s for s in set(su) | set(sd) if btc_like(s)} | set(mx)
        if syms:
            res[key] = {s: [su.get(s, 0), sd.get(s, 0), mx.get(s, 0)] for s in syms}
    if res:
        out[slug] = res
json.dump(out, open(os.path.join(RAW, 'symbol_scan.json'), 'w'))
print(len(files), 'files', len(out), 'with BTC-like symbols')
