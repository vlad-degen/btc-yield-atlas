"""Step 1 of the venue sweep: positions in the existing lending-split captures (raw/eth/lending-split-2026-10-08/) whose ETH-family
collateral backing dollar debt (cells A2+B2 from tools/eth/lending_split/build.py) is >= 100 ETH and that are missing from
data/eth/lending_split_accounts.csv (which keeps only accounts with >= $500k family collateral). No rescanning: the builders run over
the saved captures; code kind is read at the snapshot block.

Output: raw/eth/carry-sweep-2026-10-08/venues/lowband_existing.json
"""
import collections, contextlib, io, json, os
import sweep_lib as S
from build import build_aave, build_compound, build_fluid, build_morpho, build_v4, rate_map
from lib import RAW, is_stable

MIN = 100


def details():
    """(venue, chain, user-key) -> symbols, dollar debt USD, other debt USD, block, read from the raw rows"""
    det = {}
    def put(k, syms, st, oth, b):
        d = det.setdefault(k, dict(syms=set(), st=0.0, oth=0.0, block=b))
        d['syms'] |= set(syms); d['st'] += st; d['oth'] += oth
    for p in sorted(os.listdir(RAW)):
        fp = os.path.join(RAW, p)
        if p.startswith('aave_eth_'):
            d = json.load(open(fp))
            for r in d['rows']:
                st = sum(x['usd'] for x in r['debts'].values() if x['fam'] == 'stable')
                put((d['venue'], d['chain'], r['user']), r['colls'].keys(), st, sum(x['usd'] for x in r['debts'].values()) - st, d['block'])
        elif p == 'aave_v4_eth.json':
            d = json.load(open(fp))
            for r in d['rows']:
                st = sum(x['usd'] for x in r['debts'].values() if x['fam'] == 'stable')
                put(('aave-v4', 1, r['user'] + '@' + r['spoke'][:10]), r['colls'].keys(), st, sum(x['usd'] for x in r['debts'].values()) - st, d['block'])
        elif p.startswith('morpho_eth_'):
            d = json.load(open(fp))
            for r in d['rows']:
                st = r['debt_usd'] if r['loan_fam'] == 'stable' else 0.0
                put(('morpho', d['chain'], r['user']), [r['coll_sym']], st, r['debt_usd'] - st, d['block'])
        elif p.startswith('compound_eth_'):
            d = json.load(open(fp)); rm = rate_map('eth')
            for r in d['rows']:
                st = r['debt_units'] if is_stable(r['base']) else 0.0
                oth = 0.0 if st else r['debt_units'] * rm.get(r['base'].upper(), 1.0) * S.ETH_PX  # WETH / wstETH bases (WBTC Comet has no ETH collateral)
                put(('compound-v3', d['chain'], r['user']), r['colls'].keys(), st, oth, d['block'])
        elif p.startswith('fluid_eth_'):
            d = json.load(open(fp))
            for r in d['rows']:
                st = r['debt_usd_by_fam'].get('stable', 0.0)
                put(('fluid', d['chain'], r['user']), r['pair'].split(' -> ')[0].split('+'), st, sum(r['debt_usd_by_fam'].values()) - st, d['block'])
    return det


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        vs = build_aave('eth') + build_v4('eth') + build_morpho('eth') + build_compound('eth') + build_fluid('eth')
    have = S.csv_keys(); det = details()
    pos = []; venues = []
    for v in vs:
        c2 = lambda a: a['cells'][('A', 2)] + a['cells'][('B', 2)]
        meas = sum(c2(a) for a in v.accts); est = v.extra.get(('A', 2), 0) + v.extra.get(('B', 2), 0)
        big = [a for a in v.accts if c2(a) >= MIN]
        new = [a for a in big if (v.venue, v.chain, a['user'].lower()) not in have]
        venues.append(dict(venue=v.venue, chain=v.chain, cell2_measured_eth=round(meas, 1), cell2_estimated_unread_eth=round(est, 1),
                           cell2_total_eth=round(meas + est, 1), positions_ge100=len(big), positions_ge100_eth=round(sum(c2(a) for a in big), 1),
                           new_ge100=len(new), new_ge100_eth=round(sum(c2(a) for a in new), 1),
                           share_of_total_in_ge100=round(sum(c2(a) for a in big) / (meas + est), 4) if meas + est else None,
                           read_share_of_total=round(meas / (meas + est), 4) if meas + est else None,
                           note='; '.join(v.extra_label) if v.extra_label else ''))
        for a in new:
            dd = det.get((v.venue, v.chain, a['user']), dict(syms=set(), st=a['stable_attr_usd'], oth=0, block=None))
            pos.append(S.pos(v.venue, v.chain, dd['block'], a['user'], a['coll_native'], dd['syms'], dd['st'], dd['oth'], c2(a),
                             cells={'%s%d' % k: round(x, 3) for k, x in a['cells'].items() if x > 0.0005}))
    kinds = S.code_kinds((p['chain'], p['block'], p['account'].split('@')[0]) for p in pos)
    for p in pos: p['code_kind'] = kinds.get((p['chain'], p['account'].split('@')[0]))
    pos.sort(key=lambda p: -p['eth_backing_dollar'])
    meta = [dict(snapshot='2026-10-02 23:59:59 UTC (unix 1790985599), Ethereum block 26108081, L2 last block at or before',
                 source='raw/eth/lending-split-2026-10-08 captures via tools/eth/lending_split/build.py builders',
                 rule='eth_backing_dollar = cells A2+B2 (enabled ETH-family collateral x dollar debt / total debt for pooled venues; pair venues by loan asset); kept if >= 100 and (venue, chain, account) not in data/eth/lending_split_accounts.csv',
                 eth_price_usd=S.ETH_PX)] + venues
    S.write('lowband_existing', meta, pos)
    for x in venues: print(x)
    print('new positions', len(pos), 'eth %.0f' % sum(p['eth_backing_dollar'] for p in pos), collections.Counter(p['code_kind'] for p in pos))


if __name__ == '__main__':
    main()
