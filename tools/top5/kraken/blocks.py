"""Daily 00:00 UTC block numbers. Ethereum: first block with timestamp >= 00:00 UTC, found by Newton
iteration on RPC block timestamps and verified (block-1 < ts <= block). Ink: 1-second blocks,
block = 56,407,189 + (ts - 1,789,905,600) (verified on samples).
Output raw/blocks_daily.json {date: {ts, eth, ink}}"""
import json, os, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from klib import *
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
SNAP_TS, SNAP_ETH, SNAP_INK = 1789905600, 26018583, 56407189
cache = {}
def T(b):
    if b not in cache: cache[b] = btime('eth', b)
    return cache[b]
def first_at_or_after(ts):
    b = SNAP_ETH - int((SNAP_TS - ts) / 12.05)
    for _ in range(8):
        t = T(b)
        step = int((ts - t) / 12)
        if step == 0: break
        b += step
    while T(b) < ts: b += 1
    while T(b - 1) >= ts: b -= 1
    return b
out = {}
d = datetime.date(2026, 4, 1)
while d <= datetime.date(2026, 9, 21):
    ts = int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp())
    out[d.isoformat()] = dict(ts=ts, eth=first_at_or_after(ts), ink=SNAP_INK + (ts - SNAP_TS))
    d += datetime.timedelta(days=1)
out['snapshot'] = dict(ts=SNAP_TS, eth=SNAP_ETH, ink=SNAP_INK)
json.dump(out, open(os.path.join(RAW, 'blocks_daily.json'), 'w'), indent=0)
for key in ['2026-04-01', '2026-06-01', '2026-09-21']:
    v = out[key]; print(key, v, 'ink ts', btime('ink', v['ink']), 'eth ts', T(v['eth']), T(v['eth'] - 1))
print(len(out), 'rpc calls', len(cache))
