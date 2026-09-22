#!/usr/bin/env python3
"""Decode Core BitcoinStake 'delegated' and 'btcExpired' events into a per-stake table
(txid, block, approx UTC time, delegator = CORE reward address, candidate, BTC amount, CLTV locktime from script).
Block->time via linear interpolation on block_calib.txt (monthly anchors from binary search)."""
import json, datetime, bisect, collections, csv, sys
R = sys.argv[1] if len(sys.argv) > 1 else '../raw/core'
cal = []
for l in open(f'{R}/block_calib.txt'):
    d, b = l.split(); cal.append((int(b), datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).timestamp()))
def bt(b):
    i = bisect.bisect_left([c[0] for c in cal], b)
    i = min(max(i, 1), len(cal) - 1)
    (b0, t0), (b1, t1) = cal[i-1], cal[i]
    return datetime.datetime.fromtimestamp(t0 + (b - b0) * (t1 - t0) / (b1 - b0), datetime.timezone.utc)
def locktime(script):
    # first push = locktime (little-endian), followed by OP_CLTV (0xb1)
    if not script: return None
    op = script[0]
    if 1 <= op <= 75 and len(script) > op + 1 and script[op+1] == 0xb1:
        return int.from_bytes(script[1:1+op], 'little')
    if op == 0xb1: return None
    return None
stakes = {}
for line in open(f'{R}/btc_delegated.jsonl'):
    lg = json.loads(line); t = lg['topics']; d = bytes.fromhex(lg['data'][2:])
    so = int.from_bytes(d[0:32], 'big'); oi = int.from_bytes(d[32:64], 'big'); amt = int.from_bytes(d[64:96], 'big'); fee = int.from_bytes(d[96:128], 'big')
    sl = int.from_bytes(d[so:so+32], 'big'); script = d[so+32:so+32+sl]
    bn = int(lg['blockNumber'], 16)
    stakes[t[1]] = dict(txid=t[1], block=bn, time=bt(bn), candidate='0x'+t[2][-40:], delegator='0x'+t[3][-40:], btc=amt/1e8, lock=locktime(script), script=script.hex(), expired=None)
for line in open(f'{R}/btc_expired.jsonl'):
    lg = json.loads(line); t = lg['topics']; bn = int(lg['blockNumber'], 16)
    if t[1] in stakes: stakes[t[1]]['expired'] = bt(bn)
    else: stakes.setdefault('EXP_ONLY_'+t[1], dict(txid=t[1], block=None, time=None, candidate=None, delegator='0x'+t[2][-40:], btc=0, lock=None, script='', expired=bt(bn)))
with open(f'{R}/btc_stakes.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['txid','block','time_utc','delegator','candidate','btc','cltv_locktime','lock_utc','expired_utc'])
    for s in sorted(stakes.values(), key=lambda s: (s['block'] or 0)):
        lk = s['lock']; lku = datetime.datetime.fromtimestamp(lk, datetime.timezone.utc).strftime('%Y-%m-%d') if lk and lk > 500000000 else (lk or '')
        w.writerow([s['txid'], s['block'], s['time'].strftime('%Y-%m-%d %H:%M') if s['time'] else '', s['delegator'], s['candidate'], s['btc'], lk, lku, s['expired'].strftime('%Y-%m-%d') if s['expired'] else ''])
print('stakes', len(stakes))
