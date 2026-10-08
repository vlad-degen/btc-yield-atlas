"""Lending-market positions of the carry products' own accounts at the ETH snapshot, cell by cell, gross and counted once.

Runs the same venue builders as build.py over the saved captures (raw/eth/lending-split-2026-10-08/, no network) and keeps
the accounts listed below. Counted once: pooled venues reduce each holding by its reserve's utilization (the part lent out),
as build.py does per account; pair venues (Morpho, Compound, Fluid) scale each account by its venue's counted-once / gross
ratio for the same cell. Writes data/eth/netmap/carry_lending_snapshot.json, read by tools/eth/netmap/layers.py.

Cells: 1 = ETH borrowed against it (a loop), 2 = dollars borrowed (carry), 3 = other assets, 4 = no debt.
"""
import collections, contextlib, io, json, os
from build import CELLS, build_aave, build_compound, build_fluid, build_morpho, build_v4
from lib import ROOT

# product id (tools/eth/netmap/decisions.py CARRY ids) -> accounts that borrow or post collateral for it (research/eth/en,
# data/eth/economic_questions.json legs, data/eth/gap_rocksolid_upshift.json)
ACCOUNTS = {
    'liquid-eth': ['0xf0bb20865277abd641a307ece5ee04e79073416c', '0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c',
                   '0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3'],
    'lido-earn': ['0x181cb55f872450d16ae858d532b4e35e50eaa76d', '0x9938a09fea37ba681a1bd53d33ddde2debec1da0'],
    'avant-aveth': ['0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd'],
    'nemo-eth-prime': ['0x90882e7c28ddf0ac1177033a310aeed8eff25e90'],
    'sentora-eth': ['0xfb9776de51a24eb75e11110fae659e54b346658f', '0x38752981012591312bb56b1fb319511be12f6e2d'],
    'makina-deth': ['0xd1a2d9df5db842da2ee81075fa441602b2352915'],
    'royco-eth': ['0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0'],
    'tau-infinifi': ['0xc50b2d51fd1e2ac67a9c09eaf63c24ea2465c64b'],
    'vesper-vaeth': ['0x666c80feca6fcd371b0535a9846e2d223cbf1d10'],
    'reservoir-eth': ['0xf6cd9e8415162c8fb3c52676c7ca68812a34f76e'],
    'rocksolid': ['0x80c9dc967b77b5e0768e5179e92f18df9e95e18c', '0x9ca1d6e730eb9fbfd45c9ff5f0ac4e3d172d8f4d'],
}
WHO = {a: p for p, l in ACCOUNTS.items() for a in l}


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        vs = build_aave('eth') + build_v4('eth') + build_morpho('eth') + build_compound('eth') + build_fluid('eth')
    out = {p: {'gross': collections.Counter(), 'once': collections.Counter(), 'positions': []} for p in ACCOUNTS}
    for v in vs:
        g, n = v.matrix()
        meas = collections.Counter()
        for a in v.accts:
            for k, x in a['cells'].items():
                meas[k] += x
        for a in v.accts:
            p = WHO.get(a['user'].split('@')[0].lower())
            if not p:
                continue
            for k in CELLS:
                x = a['cells'][k]
                if x <= 0:
                    continue
                if v.netmode == 'account':
                    y = a['net'][k]
                else:  # pair / pool venues: the venue's counted-once ratio for the cell, measured accounts only
                    y = x * (n[k] / g[k] if g[k] else 1.0)
                c = '%s%d' % k
                out[p]['gross'][c] += x
                out[p]['once'][c] += y
                out[p]['positions'].append({'venue': v.venue, 'chain': v.chain, 'account': a['user'], 'cell': c,
                                            'gross_eth': round(x, 4), 'counted_once_eth': round(y, 4)})
    res = {'snapshot': '2026-10-02 23:59:59 UTC, Ethereum block 26,108,081', 'source': 'raw/eth/lending-split-2026-10-08 via tools/eth/lending_split/build.py',
           'cells': {'1': 'ETH debt (loop)', '2': 'dollar debt (carry)', '3': 'other debt', '4': 'no debt'}, 'accounts': ACCOUNTS, 'products': {}}
    for p, d in out.items():
        res['products'][p] = {'gross': {k: round(v, 4) for k, v in sorted(d['gross'].items())},
                              'counted_once': {k: round(v, 4) for k, v in sorted(d['once'].items())},
                              'positions': d['positions']}
    path = os.path.join(ROOT, 'data', 'eth', 'netmap', 'carry_lending_snapshot.json')
    json.dump(res, open(path, 'w'), indent=1)
    for p, d in res['products'].items():
        print(f"{p:16}", {k: round(v) for k, v in d['counted_once'].items() if v >= 0.5}, ' gross', {k: round(v) for k, v in d['gross'].items() if v >= 0.5})


if __name__ == '__main__':
    main()
