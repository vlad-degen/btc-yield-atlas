"""Replay every sentoraBTC Transfer on Ink -> daily supply, holders, deposits, withdrawals (BTC at accountant rate),
per-address balances at the snapshot, holder buckets/concentration, and address-type classification.
Inputs: raw/share_transfers.json, ../../onchain-kraken/ink_rate_history.json, raw/holders_ink.jsonl, raw/daily_eth.json
Outputs: raw/ink_daily.json, raw/balances_snapshot.json, holders_buckets.csv, holders_types.csv"""
import json, os, sys, bisect, datetime, collections, csv, math
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, '..', 'raw'); OUTD = os.path.join(HERE, '..')
SNAP_TS, SNAP_INK = 1789905600, 56407189
Z = '0x' + '0' * 40
QUEUE = '0x5f210d9c163e5f1d96fd880b0178c3239fef89fb'
SOLVER = '0xd7a26610d388421e02e1c8382564c56810683c33'
SPECIAL = {Z, QUEUE, SOLVER}
tr = json.load(open(os.path.join(RAW, 'share_transfers.json')))['rows']
rh = json.load(open(os.path.join(HERE, '..', '..', '..', 'onchain-kraken', 'ink_rate_history.json')))
rts = [r['ts'] for r in rh]; rv = [r['new'] / 1e8 for r in rh]
def rate_at(ts):
    i = bisect.bisect_right(rts, ts) - 1
    return 1.0 if i < 0 else rv[i]
def bts(block): return SNAP_TS + (block - SNAP_INK)
def day(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).date().isoformat()

bal = collections.defaultdict(int)
first_seen = {}
daily = collections.OrderedDict()
def D(d):
    if d not in daily:
        daily[d] = dict(dep_shares=0, dep_btc=0.0, dep_n=0, dep_addrs=set(), new_depositors=0, req_shares=0, req_btc=0.0, req_n=0,
                        burn_shares=0, burn_btc=0.0, burn_n=0, p2p_n=0)
    return daily[d]
supply = 0
snap_bal = None
holders = 0
end_of_day = {}
last_day = None
for (blk, li, fr, to, v, tx) in tr:
    ts = bts(blk)
    if snap_bal is None and blk > SNAP_INK:
        snap_bal = {a: b for a, b in bal.items() if b > 0}
        snap_supply = supply
    d = day(ts)
    if last_day is not None and d != last_day:
        end_of_day[last_day] = dict(supply=supply, holders=holders)
    last_day = d
    rec = D(d); r = rate_at(ts)
    if fr == Z:
        supply += v
        rec['dep_shares'] += v; rec['dep_btc'] += v * r / 1e8; rec['dep_n'] += 1; rec['dep_addrs'].add(to)
        if to not in first_seen:
            first_seen[to] = ts; rec['new_depositors'] += 1
    elif to == Z:
        supply -= v
        rec['burn_shares'] += v; rec['burn_btc'] += v * r / 1e8; rec['burn_n'] += 1
    elif to == QUEUE:
        rec['req_shares'] += v; rec['req_btc'] += v * r / 1e8; rec['req_n'] += 1
    elif fr not in SPECIAL and to not in SPECIAL:
        rec['p2p_n'] += 1
    # balances / holder count (exclude special addresses)
    for a, delta in ((fr, -v), (to, v)):
        if a in SPECIAL:
            bal[a] += delta; continue
        before = bal[a]; bal[a] += delta; after = bal[a]
        if before <= 0 < after: holders += 1
        elif before > 0 >= after: holders -= 1
end_of_day[last_day] = dict(supply=supply, holders=holders)
if snap_bal is None:
    snap_bal = {a: b for a, b in bal.items() if b > 0}; snap_supply = supply
# fill every calendar day from first activity
days = sorted(daily)
d0 = datetime.date.fromisoformat(days[0]); d1 = datetime.date.fromisoformat(days[-1])
series = []
cur = d0; prev = dict(supply=0, holders=0)
while cur <= d1:
    k = cur.isoformat()
    rec = daily.get(k) or D(k)
    eod = end_of_day.get(k, prev)
    ts_end = int(datetime.datetime(cur.year, cur.month, cur.day, tzinfo=datetime.timezone.utc).timestamp()) + 86400
    series.append(dict(date=k, supply_shares=eod['supply'] / 1e8, holders=eod['holders'], rate_eod=rate_at(ts_end - 1),
                       tvl_btc=eod['supply'] / 1e8 * rate_at(ts_end - 1),
                       dep_btc=rec['dep_btc'], dep_n=rec['dep_n'], dep_unique=len(rec['dep_addrs']), new_depositors=rec['new_depositors'],
                       req_btc=rec['req_btc'], req_n=rec['req_n'], burn_btc=rec['burn_btc'], burn_n=rec['burn_n'],
                       net_flow_btc=rec['dep_btc'] - rec['burn_btc'], p2p_n=rec['p2p_n']))
    prev = eod; cur += datetime.timedelta(days=1)
json.dump(series, open(os.path.join(RAW, 'ink_daily.json'), 'w'), indent=0)
print('supply at snapshot', snap_supply / 1e8, 'final supply', supply / 1e8, 'holders final', holders,
      'lifetime depositors', len(first_seen))

# ---------- snapshot distribution ----------
RATE_SNAP = rate_at(SNAP_TS)
queue_bal = snap_bal.pop(QUEUE, 0) / 1e8 * RATE_SNAP
for a in list(snap_bal):
    if a in SPECIAL: snap_bal.pop(a)
btc = sorted((b / 1e8 * RATE_SNAP for b in snap_bal.values()), reverse=True)
tot = sum(btc)
n = len(btc)
json.dump({'rate': RATE_SNAP, 'queue_btc': queue_bal, 'balances': {a: b / 1e8 for a, b in snap_bal.items()}},
          open(os.path.join(RAW, 'balances_snapshot.json'), 'w'))
edges = [0, 0.001, 0.01, 0.1, 1, 10, 100, float('inf')]
labels = ['<0.001', '0.001-0.01', '0.01-0.1', '0.1-1', '1-10', '10-100', '>100']
rows = []
for lo, hi, lab in zip(edges[:-1], edges[1:], labels):
    sel_ = [x for x in btc if lo <= x < hi]
    rows.append(dict(bucket_btc=lab, holders=len(sel_), holders_pct=round(100 * len(sel_) / n, 2), btc=round(sum(sel_), 4),
                     btc_pct=round(100 * sum(sel_) / tot, 2), avg_btc=round(sum(sel_) / len(sel_), 5) if sel_ else 0))
hhi = sum((x / tot) ** 2 for x in btc) * 10000
med = btc[n // 2] if n % 2 else (btc[n // 2 - 1] + btc[n // 2]) / 2
stats = dict(date='2026-09-20 12:00 UTC (Ink block 56,407,189)', holders=n, btc_total=tot, queue_pending_btc=queue_bal, rate=RATE_SNAP,
             top1_pct=100 * btc[0] / tot, top10_pct=100 * sum(btc[:10]) / tot, top100_pct=100 * sum(btc[:100]) / tot,
             top1000_pct=100 * sum(btc[:1000]) / tot, hhi=hhi, median_btc=med, mean_btc=tot / n,
             top1_btc=btc[0], top10=[round(x, 3) for x in btc[:10]])
with open(os.path.join(OUTD, 'holders_buckets.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    f.write('\n# snapshot 2026-09-20 12:00 UTC, Ink block 56407189; BTC-equivalent = shares x accountant rate %.8f; excludes withdraw queue (%.2f BTC pending) \n' % (RATE_SNAP, queue_bal))
    for k, v in stats.items():
        if k not in ('top10',): f.write(f'# {k},{v}\n')
json.dump(stats, open(os.path.join(RAW, 'holders_stats.json'), 'w'), indent=1)
print(json.dumps(stats, indent=1))
for r in rows: print(r)

# ---------- address types ----------
bs = {}
for l in open(os.path.join(RAW, 'holders_ink.jsonl')):
    r = json.loads(l); bs[r['addr'].lower()] = r
UK = {}
_ukp = os.path.join(RAW, 'unknown_type_codes.json')
if os.path.exists(_ukp):
    UK = json.load(open(_ukp))['codes']
def classify(a):
    r = bs.get(a)
    if r is None:
        c = UK.get(a)
        if c and c.startswith('0xef0100'):
            return 'EIP-7702 -> ZeroDev Kernel (Kraken/Privy embedded wallet)' if c[8:].lower() == 'd6cedde84be40893d153be9d467cd6ad37875b28' else 'EIP-7702 -> other (0x%s)' % c[8:]
        if c in ('0x', '0x0'): return 'plain EOA'
        if c: return 'other contract'
        return 'unknown (exited after snapshot)'
    if r['p'] == 'eip7702':
        ia = [x.lower() for x in r['impl_addr'] if x]
        if '0xd6cedde84be40893d153be9d467cd6ad37875b28' in ia: return 'EIP-7702 -> ZeroDev Kernel (Kraken/Privy embedded wallet)'
        return 'EIP-7702 -> other (%s)' % (','.join(x for x in r['impl'] if x) or ','.join(ia))
    if not r['c']: return 'plain EOA'
    if any('safe' in (x or '').lower() for x in r['impl']) or 'safe' in (r['name'] or '').lower(): return 'Safe multisig'
    return 'other contract (%s)' % (r['name'] or '')
tstat = collections.defaultdict(lambda: [0, 0.0])
unknown = []
for a, b in snap_bal.items():
    c = classify(a)
    if c.startswith('unknown'): unknown.append(a)
    tstat[c][0] += 1; tstat[c][1] += b / 1e8 * RATE_SNAP
json.dump(unknown, open(os.path.join(RAW, 'unknown_type_addrs.json'), 'w'))
trows = [dict(type=k, holders=v[0], holders_pct=round(100 * v[0] / n, 3), btc=round(v[1], 4), btc_pct=round(100 * v[1] / tot, 3))
         for k, v in sorted(tstat.items(), key=lambda kv: -kv[1][1])]
# current (2026-09-21 ~22:00 UTC, Blockscout) view as well
cur = collections.defaultdict(lambda: [0, 0.0]); ncur = 0; tcur = 0
for a, r in bs.items():
    if a in SPECIAL: continue
    c = classify(a); cur[c][0] += 1; cur[c][1] += r['v'] / 1e8; ncur += 1; tcur += r['v'] / 1e8
with open(os.path.join(OUTD, 'holders_types.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['view', 'type', 'holders', 'holders_pct', 'shares_or_btc', 'balance_pct'])
    for r in trows: w.writerow(['snapshot 2026-09-20 12:00 (BTC-eq)', r['type'], r['holders'], r['holders_pct'], r['btc'], r['btc_pct']])
    for k, v in sorted(cur.items(), key=lambda kv: -kv[1][1]):
        w.writerow(['Blockscout 2026-09-21 ~22:00 (shares)', k, v[0], round(100 * v[0] / ncur, 3), round(v[1], 4), round(100 * v[1] / tcur, 3)])
    f.write('# classification: Blockscout proxy_type=eip7702 + delegate implementation (EIP-7702 code prefix 0xef0100); 431 addresses that held at the snapshot but exited before the Blockscout pull were classified by eth_getCode on Ink at the snapshot block (classify_unknown.py)\n')
for r in trows: print(r)
print('unknown', len(unknown))
