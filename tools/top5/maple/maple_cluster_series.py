#!/usr/bin/env python3
"""Reconstruct BTC staked on Core by the address cluster attributed (by shared BTC owner scripts and by the
584.047 BTC / 2025-10-15 and 756.983 BTC / 2025-11-19 CLTV maturities that match the Cayman judgment) to Maple's
BTC Yield program. Active = from delegation time until the CLTV lock time (or btcExpired event if earlier).
Outputs daily series for the cluster and for all Core BTC stakes decoded from events (stakes migrated before
2024-11-19 have no amount in events and are excluded from the network total)."""
import csv, datetime, collections, sys
R = '../raw/core'
CLUSTER = {'0xadfaaa5f085cf52d4fabbdf3181521f1ae9cab7c', '0x74bb2c9ffa90aeb2d3e7b958d418a36ab31acd52',
           '0xfd818e3544a8a72632ab53324eae6370bbe9bad7', '0x87f34109e4782736b6869daff588626ffb4764d3',
           '0x2ed725c8ee00fd5a3043bf54716dff85abb29353'}
rows = [r for r in csv.DictReader(open(f'{R}/btc_stakes.csv')) if r['block']]
def d(s): return datetime.date.fromisoformat(s[:10])
start, end = datetime.date(2024, 11, 20), datetime.date(2026, 9, 21)
days = [start + datetime.timedelta(i) for i in range((end - start).days + 1)]
cl = collections.Counter(); net = collections.Counter(); per = collections.defaultdict(collections.Counter)
for r in rows:
    s = d(r['time_utc']); e = d(r['lock_utc']) if r['lock_utc'] and '-' in r['lock_utc'] else None
    if r['expired_utc']: e = min(e, d(r['expired_utc'])) if e else d(r['expired_utc'])
    if not e: e = end + datetime.timedelta(1)
    b = float(r['btc'])
    for day in days:
        if s <= day < e:
            net[day] += b
            if r['delegator'] in CLUSTER: cl[day] += b; per[r['delegator']][day] += b
with open(f'{R}/maple_cluster_daily.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'cluster_btc', 'network_btc_from_events', 'cluster_share'] + sorted(CLUSTER))
    for day in days:
        w.writerow([day, round(cl[day], 4), round(net[day], 4), round(cl[day] / net[day], 4) if net[day] else ''] + [round(per[a][day], 4) for a in sorted(CLUSTER)])
# summary
peak = max(days, key=lambda x: cl[x])
print('cluster peak', peak, round(cl[peak], 2))
for day in days:
    if day.day in (1, 15) or day in (datetime.date(2025, 10, 14), datetime.date(2025, 10, 16), datetime.date(2025, 11, 18), datetime.date(2025, 11, 20)):
        print(day, round(cl[day], 2), round(net[day], 2), f"{cl[day]/net[day]*100:.1f}%" if net[day] else '')
