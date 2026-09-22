"""Screen all candidates: BTC-token part at the 2026-09-20 point. Output raw/screen_0920.json + printed table."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
cand = json.load(open(os.path.join(RAW, 'candidates.json')))
rows = []
for s, meta in cand.items():
    try: d = load(s)
    except Exception as e:
        rows.append(dict(slug=s, err=str(e))); continue
    tk = series_tokens(s); tot = series_total(s)
    t20, dt = pick(tk, SNAP, 0); v20, _ = pick(tot, SNAP, 0)
    usd, br = btc_part(t20)
    tok_sum = sum(v for v in (t20 or {}).values() if v) if t20 else None
    rows.append(dict(slug=s, name=d.get('name'), category=d.get('category'), total_0920=v20, tok_sum_0920=tok_sum,
                     has_tokens=bool(tk), btc_usd_0920=usd, btc_breakdown={k: round(v) for k, v in sorted(br.items(), key=lambda kv: -kv[1])}))
json.dump(rows, open(os.path.join(RAW, 'screen_0920.json'), 'w'), indent=1)
rows = [r for r in rows if 'err' not in r]
print('no token breakdown:', [(r['slug'], round((r['total_0920'] or 0) / 1e6, 1)) for r in rows if not r['has_tokens'] and (r['total_0920'] or 0) > 1e6])
for r in sorted(rows, key=lambda r: -r['btc_usd_0920']):
    if r['btc_usd_0920'] < 3e5: continue
    print(f"{r['slug']:34} {str(r['category'])[:20]:20} tot={ (r['total_0920'] or 0)/1e6:8.1f} btc={r['btc_usd_0920']/1e6:8.2f}  {list(r['btc_breakdown'].items())[:5]}")
