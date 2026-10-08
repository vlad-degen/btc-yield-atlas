"""Merge the venue sweep outputs (raw/eth/carry-sweep-2026-10-08/venues/*.json): per venue ETH collateral backing dollar debt at the
snapshot, what the >= 100 ETH positions cover, and the positions not already in data/eth/lending_split_accounts.csv (deduplicated by
venue, chain, account). Output: venues/carry_sweep_lending_summary.json
"""
import collections, glob, json, os
import sweep_lib as S

SKIP = ('summary.json', 'blocks_extra.json', 'hyperevm_ueth_atoken_recipients.json')


def main():
    mine = ('lowband_existing', 'aave_', 'compound_', 'fluid_', 'hyperevm')  # this sweep's files only (the folder holds other scans too)
    files = sorted((f for f in glob.glob(os.path.join(S.VOUT, '*.json')) if not f.endswith('_rows.json') and os.path.basename(f) not in SKIP
                   and os.path.basename(f).startswith(mine)), key=lambda f: (not f.endswith('lowband_existing.json'), f))  # full enumerations override the lending-split estimate
    have = S.csv_keys()
    csv_by_venue = collections.Counter()
    import csv
    for r in csv.DictReader(open(os.path.join(S.ROOT, 'data', 'eth', 'lending_split_accounts.csv'))):
        if r['side'] == 'eth' and float(r['A2'] or 0) + float(r['B2'] or 0) >= 100:
            csv_by_venue[(r['venue'], int(r['chain']))] += float(r['A2'] or 0) + float(r['B2'] or 0)
    pos = {}; venues = {}
    for f in files:
        d = json.load(open(f)); src = os.path.basename(f)[:-5]
        for m in d['meta']:
            if 'venue' not in m or 'chain' not in m: continue
            k = (m['venue'], m['chain'])
            if src == 'lowband_existing':
                venues[k] = dict(source=src, eth_backing_dollar_total=m['cell2_total_eth'], read_share=m['read_share_of_total'],
                                 total_basis='lending-split builders: measured accounts plus the estimated unread remainder')
            elif 'eth_backing_dollar_total' in m or 'note' in m or 'error' in m:
                prev = venues.get(k)
                v = dict(source=src, eth_backing_dollar_total=m.get('eth_backing_dollar_total'), note=m.get('note') or m.get('error'),
                         total_basis='every stablecoin borrower (Aave pools) / every position (pair venues) read at the snapshot')
                if prev and v['eth_backing_dollar_total'] is None: continue
                if prev: v['lending_split_total_before'] = prev['eth_backing_dollar_total']
                venues[k] = v
        for p in d['positions']:
            key = (p['venue'], p['chain'], p['account'].split('@')[0] if p['venue'] != 'aave-v4' else p['account'])
            if (p['venue'], p['chain'], p['account']) in have: continue
            if key in pos and pos[key]['eth_backing_dollar'] >= p['eth_backing_dollar']: continue
            p = dict(p); p['source'] = src; pos[key] = p
    P = sorted(pos.values(), key=lambda p: -p['eth_backing_dollar'])
    by = collections.defaultdict(lambda: [0, 0.0])
    for p in P:
        by[(p['venue'], p['chain'])][0] += 1; by[(p['venue'], p['chain'])][1] += p['eth_backing_dollar']
    vout = []
    for k, v in sorted(venues.items(), key=lambda kv: -(kv[1]['eth_backing_dollar_total'] or 0)):
        tot = v['eth_backing_dollar_total'] or 0
        n, s = by.get(k, [0, 0.0]); c = csv_by_venue.get(k, 0.0)
        vout.append(dict(venue=k[0], chain=k[1], **v, csv_ge100_eth=round(c, 1), new_ge100=n, new_ge100_eth=round(s, 1),
                         share_covered_by_ge100=round((c + s) / tot, 4) if tot else None))
    kinds = collections.Counter(p['code_kind'] for p in P)
    contracts = [p for p in P if p['code_kind'] == 'contract']
    res = dict(meta=dict(snapshot='2026-10-02 23:59:59 UTC', rule='eth_backing_dollar >= 100 ETH, (venue, chain, account) not in data/eth/lending_split_accounts.csv',
                         positions=len(P), positions_eth=round(sum(p['eth_backing_dollar'] for p in P), 1), code_kinds=dict(kinds),
                         contract_positions=len(contracts), contract_eth=round(sum(p['eth_backing_dollar'] for p in contracts), 1)),
               venues=vout, positions=P)
    json.dump(res, open(os.path.join(S.VOUT, 'carry_sweep_lending_summary.json'), 'w'), indent=1, default=str)
    print(json.dumps(res['meta'], indent=1))
    for v in vout:
        print('%-15s %7s total %10.1f csv>=100 %10.1f new %4d %9.1f cover %s  %s' % (v['venue'], v['chain'], v['eth_backing_dollar_total'] or 0, v['csv_ge100_eth'],
              v['new_ge100'], v['new_ge100_eth'], v['share_covered_by_ge100'], (v.get('note') or '')[:60]))
    print('top contracts')
    for p in contracts[:20]:
        print(p['account'], p['chain'], p['venue'], p['eth_backing_dollar'], p['dollar_debt_usd'], p['collateral_symbols'])


if __name__ == '__main__':
    main()
