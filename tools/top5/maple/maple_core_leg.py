#!/usr/bin/env python3
"""Reconstruct the CORE leg (delegated CORE) and BTC/CORE reward claims of the Maple-attributed cluster on Core.
Inputs: cl_*.jsonl from core_logs_by_addr.py. Block->date via block_calib.txt interpolation.
Outputs maple_core_leg_daily.csv (CORE staked by cluster), maple_rewards.csv (claims)."""
import json, csv, bisect, datetime, collections
R = '../raw/core'
cal = [(int(l.split()[1]), datetime.datetime.fromisoformat(l.split()[0]).replace(tzinfo=datetime.timezone.utc).timestamp()) for l in open(f'{R}/block_calib.txt')]
def bt(b):
    i = min(max(bisect.bisect_left([c[0] for c in cal], b), 1), len(cal) - 1)
    (b0, t0), (b1, t1) = cal[i-1], cal[i]
    return datetime.datetime.fromtimestamp(t0 + (b - b0) * (t1 - t0) / (b1 - b0), datetime.timezone.utc)
def logs(n): return [json.loads(l) for l in open(f'{R}/{n}.jsonl')]
def words(d): d = bytes.fromhex(d[2:]); return [int.from_bytes(d[i:i+32], 'big', signed=False) for i in range(0, len(d), 32)]
ev = []
for lg in logs('cl_delegatedCoin'):
    w = words(lg['data']); ev.append((int(lg['blockNumber'], 16), '0x'+lg['topics'][2][-40:], +w[0]/1e18, 'delegate'))
for lg in logs('cl_undelegatedCoin'):
    w = words(lg['data']); ev.append((int(lg['blockNumber'], 16), '0x'+lg['topics'][2][-40:], -w[0]/1e18, 'undelegate'))
ev.sort()
bal = collections.Counter(); daily = {}
for b, a, amt, k in ev:
    bal[a] += amt; daily[bt(b).date()] = sum(bal.values())
with open(f'{R}/maple_core_leg_events.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'block', 'delegator', 'core_amount', 'type'])
    for b, a, amt, k in ev: w.writerow([bt(b).strftime('%Y-%m-%d %H:%M'), b, a, round(amt, 2), k])
print('CORE leg path (end-of-day totals, CORE):')
for d in sorted(daily): print(' ', d, round(daily[d]/1e6, 3), 'M')
# BTC reward claims: claimedBtcReward(delegator, amount, unclaimedAmount, floatReward, accStakedAmount, dualStakingRate)
tot = 0; rows = []
for lg in logs('cl_claimedBtcReward'):
    d = bytes.fromhex(lg['data'][2:]); w = [d[i:i+32] for i in range(0, len(d), 32)]
    amt = int.from_bytes(w[0], 'big')/1e18; unc = int.from_bytes(w[1], 'big')/1e18; fl = int.from_bytes(w[2], 'big', signed=True)/1e18
    acc = int.from_bytes(w[3], 'big'); ds = int.from_bytes(w[4], 'big')
    b = int(lg['blockNumber'], 16); rows.append((bt(b).date(), '0x'+lg['topics'][1][-40:], amt, unc, fl, acc, ds)); tot += amt
cc = 0; crow = []
for lg in logs('cl_claimedCoinReward'):
    w = words(lg['data']); b = int(lg['blockNumber'], 16); crow.append((bt(b).date(), '0x'+lg['topics'][1][-40:], w[0]/1e18, w[1])); cc += w[0]/1e18
# StakeHub.claimedReward(delegator, amounts[]) -- amounts = [CORE-leg, hash-leg, BTC-leg]; used for 2026 claims
srow = []
for lg in logs('cl_claimedReward'):
    d = bytes.fromhex(lg['data'][2:]); n = int.from_bytes(d[32:64], 'big')
    arr = [int.from_bytes(d[64+32*i:96+32*i], 'big')/1e18 for i in range(n)]
    srow.append((bt(int(lg['blockNumber'], 16)).date(), '0x'+lg['topics'][1][-40:], arr))
with open(f'{R}/maple_rewards.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'delegator', 'leg', 'core_reward', 'unclaimed', 'float_reward', 'acc_staked_amount', 'dual_staking_rate_bp'])
    for r in rows: w.writerow([r[0], r[1], 'BTC', round(r[2], 4), round(r[3], 4), round(r[4], 4), r[5], r[6]])
    for r in crow: w.writerow([r[0], r[1], 'CORE', round(r[2], 4), '', '', r[3], ''])
    for dt_, a, arr in srow:
        # only add StakeHub claims dated after the last per-agent claim event (2026), to avoid double counting
        if dt_ > max([r[0] for r in rows] + [r[0] for r in crow]):
            w.writerow([dt_, a, 'CORE(StakeHub)', round(arr[0], 4), '', '', '', ''])
            w.writerow([dt_, a, 'BTC(StakeHub)', round(arr[2], 4), '', '', '', ''])
print('BTC-leg CORE rewards claimed:', round(tot), 'CORE-leg rewards claimed:', round(cc))
m = collections.defaultdict(lambda: [0, 0, collections.Counter()])
for r in rows: k = r[0].strftime('%Y-%m'); m[k][0] += r[2]; m[k][2][r[6]] += 1
for r in crow: k = r[0].strftime('%Y-%m'); m[k][1] += r[2]
for k in sorted(m): print(' ', k, 'btcleg', round(m[k][0]), 'coreleg', round(m[k][1]), 'dualRates', dict(m[k][2]))
