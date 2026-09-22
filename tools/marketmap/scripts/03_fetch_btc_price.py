"""Binance BTCUSDT daily klines 2024-08-25 .. today -> raw/btc_daily.json {date: close}"""
import json, os, urllib.request, datetime
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
start = int(datetime.datetime(2024, 8, 25, tzinfo=datetime.UTC).timestamp() * 1000)
url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&startTime={start}&limit=1000'
rows = json.loads(urllib.request.urlopen(url, timeout=60).read())
out = {}
for r in rows:
    d = datetime.datetime.fromtimestamp(r[0] / 1000, datetime.UTC).date().isoformat()
    out[d] = dict(open=float(r[1]), close=float(r[4]))
json.dump(out, open(os.path.join(D, 'raw', 'btc_daily.json'), 'w'), indent=0)
print(len(out), min(out), max(out), out.get('2026-09-20'))
