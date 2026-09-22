#!/usr/bin/env python3
"""Attribute Core BTC-staking reward addresses to one owner by shared Bitcoin owner scripts.
Each Core BTC stake script = <locktime> OP_CLTV OP_DROP <owner script>. Delegators (CORE reward addresses) whose
stakes lock BTC under the same owner script control/stake the same custodial BTC wallet.
Seed: 0x74bb2c9f... (its CLTV maturities 584.047 BTC @2025-10-15 and 756.983 BTC @2025-11-19 match the
'584 Bitcoins ... due on 15 October 2025' and '19 November 2025' repayment dates in [2025] Cayman judgment FSD 2025-0268)."""
import json, collections
R = '../raw/core'
def tail(s):
    op = s[0]
    if 1 <= op <= 75 and len(s) > op + 2 and s[op+1] == 0xb1 and s[op+2] == 0x75: return s[op+3:]
    return s
by = collections.defaultdict(collections.Counter)
for line in open(f'{R}/btc_delegated.jsonl'):
    lg = json.loads(line); t = lg['topics']; d = bytes.fromhex(lg['data'][2:])
    so = int.from_bytes(d[0:32], 'big'); amt = int.from_bytes(d[64:96], 'big')
    sl = int.from_bytes(d[so:so+32], 'big'); s = d[so+32:so+32+sl]
    by[tail(s).hex()]['0x' + t[3][-40:]] += amt / 1e8
seed = {'0x74bb2c9ffa90aeb2d3e7b958d418a36ab31acd52'}
cluster = set(seed); scripts = set()
changed = True
while changed:
    changed = False
    for sc, dl in by.items():
        if cluster & set(dl) and sc not in scripts:
            scripts.add(sc); new = set(a for a, v in dl.items() if v > 0) - cluster
            if new: cluster |= new; changed = True
print('cluster delegators:', sorted(cluster))
for sc in scripts:
    print(sc[:24] + '...', {a[:10]: round(v, 2) for a, v in by[sc].items()})
