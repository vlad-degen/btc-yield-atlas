#!/usr/bin/env python3
"""Trace the Bitcoin wind-down of the Maple BTC Yield program via mempool.space.
Hub = bc1pm9v0y2...c0pc4: receives the 2025-11-19 sweep of all remaining CLTV outputs (from btc_outspends.py),
then pays out to recipient addresses (each preceded by a 0.0001 BTC test send). Also follows the 200.09 BTC (15%)
transfer to bc1pdcj7... -> bc1pyed82... -> (2026-06-05) bc1q9tfmg8... -> bc1q5zly2...
Writes ../raw/core/btc_payouts.json and prints monthly payout totals, recipient count and size distribution."""
import json, urllib.request, datetime, time, collections
UA = {'User-Agent': 'Mozilla/5.0'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
def hist(A):
    txs = get(f'https://mempool.space/api/address/{A}/txs/chain'); allt = list(txs)
    while len(txs) == 25:
        txs = get(f'https://mempool.space/api/address/{A}/txs/chain/{txs[-1]["txid"]}'); allt += txs; time.sleep(0.3)
    return allt
HUB = 'bc1pm9v0y2gjh4hjm6wp7vsaqwzf96ugsrtzs9ujcawdm880fveuzrcs3c0pc4'
txs = hist(HUB); json.dump(txs, open('../raw/core/bc1pm9_txs.json', 'w'))
pay = collections.defaultdict(float); first = {}; bym = collections.defaultdict(float)
for t in sorted(txs, key=lambda t: t['status']['block_time']):
    d = datetime.datetime.fromtimestamp(t['status']['block_time'], datetime.timezone.utc).strftime('%Y-%m-%d')
    if d < '2025-11-19' or not any(v['prevout'].get('scriptpubkey_address') == HUB for v in t['vin']): continue
    for o in t['vout']:
        a = o.get('scriptpubkey_address'); v = o['value'] / 1e8
        if a == HUB or v < 0.01: continue
        pay[a] += v; first.setdefault(a, d); bym[d[:7]] += v
json.dump({'recipients': {a: [round(v, 8), first[a]] for a, v in pay.items()}}, open('../raw/core/btc_payouts.json', 'w'), indent=1)
tot = sum(pay.values()); sizes = sorted(pay.values(), reverse=True)
print('recipients', len(pay), 'total', round(tot, 3), 'by month', {k: round(v, 2) for k, v in sorted(bym.items())})
print('largest', [round(s, 2) for s in sizes[:10]], 'holdback share of total', round(sizes[0] / tot, 4))
ex = sizes[1:]; print('excluding holdback: n', len(ex), 'sum', round(sum(ex), 2), 'share', round(sum(ex) / tot, 4),
      'implied principal of largest lender (÷0.85)', round(ex[0] / 0.85, 1), 'top5 share', round(sum(ex[:5]) / sum(ex), 3))
