#!/usr/bin/env python3
"""Daily and monthly CORE/USDT and BTC/USDT closes from Bybit public spot klines (no key).
Writes ../raw/prices_daily.csv and ../raw/prices_monthly.csv (UTC)."""
import json, urllib.request, datetime, csv
UA = "Mozilla/5.0"
def kl(sym, interval, start_ms, limit=1000):
    u = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={sym}&interval={interval}&start={start_ms}&limit={limit}"
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30))["result"]["list"]
def daily(sym, start):
    out = {}; s = start
    while True:
        rows = kl(sym, "D", s)
        if not rows: break
        for r in rows: out[int(r[0])] = float(r[4])
        mx = max(int(r[0]) for r in rows)
        if len(rows) < 1000: break
        s = mx + 86400000
    return out
st = int(datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
c = daily("COREUSDT", st); b = daily("BTCUSDT", st)
with open("../raw/prices_daily.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date", "core_usd", "btc_usd"])
    for k in sorted(set(c) | set(b)):
        w.writerow([datetime.datetime.fromtimestamp(k/1000, datetime.timezone.utc).date(), c.get(k, ""), b.get(k, "")])
m = {}
for sym in ("COREUSDT", "BTCUSDT"):
    for r in kl(sym, "M", st, 40): m.setdefault(int(r[0]), {})[sym] = (float(r[1]), float(r[4]))
with open("../raw/prices_monthly.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["month", "core_open", "core_close", "btc_open", "btc_close"])
    for k in sorted(m):
        d = datetime.datetime.fromtimestamp(k/1000, datetime.timezone.utc).strftime("%Y-%m")
        w.writerow([d, *m[k].get("COREUSDT", ("", "")), *m[k].get("BTCUSDT", ("", ""))])
print(len(c), len(b))
