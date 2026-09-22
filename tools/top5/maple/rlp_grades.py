#!/usr/bin/env python3
"""Decode RLP 'grades' values from agent_paramchange_decoded.txt into CORE-per-BTC thresholds and reward percentages.
Grade = (stakeRate [CORE per BTC], percentage [/10000 of reference BTC reward rate])."""
import sys
def rlp(b, i=0):
    p = b[i]
    if p < 0x80: return b[i:i+1], i+1
    if p < 0xb8: l = p-0x80; return b[i+1:i+1+l], i+1+l
    if p < 0xc0: ll = p-0xb7; l = int.from_bytes(b[i+1:i+1+ll],'big'); return b[i+1+ll:i+1+ll+l], i+1+ll+l
    if p < 0xf8: l = p-0xc0; s = i+1
    else: ll = p-0xf7; l = int.from_bytes(b[i+1:i+1+ll],'big'); s = i+1+ll
    out = []; j = s
    while j < s+l:
        it, j = rlp(b, j); out.append(it)
    return out, s+l
def toint(x): return int.from_bytes(x,'big') if x else 0
for line in open(sys.argv[1]):
    dt, tm, bn, key, val, tx = line.split()
    if key != 'grades': print(dt, tm, key, val); continue
    lst, _ = rlp(bytes.fromhex(val))
    g = [(toint(a), toint(b)) for a, b in lst]
    print(dt, tm, 'grades', ' | '.join(f'{r:>6} CORE/BTC -> {p/100:.0f}%' for r, p in g), tx)
