"""Screen every fetched protocol for its BTC-token part at month-ends 2024-09..2026-09 (catches products that are small/dead today).
Output: raw/history_screen.json {slug: {category, max_usd, max_month, cur_usd, months:{m: usd}}}"""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
MP = month_points()
out = {}
for f in glob.glob(os.path.join(RAW, 'proto', '*.json')):
    s = os.path.basename(f)[:-5]
    try: d = load(s)
    except Exception: continue
    tk = series_tokens(s)
    btc_named = d.get('category') in ('Restaked BTC', 'Anchor BTC') or 'btc' in (d.get('name', '') + s).lower()
    tot = series_total(s) if (not tk and btc_named) else None
    months = {}
    for m, dl, _ in MP:
        if tot is not None:
            months[m] = pick(tot, dl)[0] or 0.0; continue
        t, _ = pick(tk, dl)
        months[m] = btc_part(t)[0] if t else 0.0
    mx = max(months.values()) if months else 0
    if mx < 1e6: continue
    mm = max(months, key=months.get)
    out[s] = dict(name=d.get('name'), category=d.get('category'), max_usd=mx, max_month=mm, cur_usd=months['2026-09'],
                  has_tokens=bool(tk), months=months)
json.dump(out, open(os.path.join(RAW, 'history_screen.json'), 'w'))
print(len(out))
