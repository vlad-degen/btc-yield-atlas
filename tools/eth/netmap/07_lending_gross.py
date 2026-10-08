"""ETH in lending markets before counting once, by protocol, on the BTC study's basis (collateral plus supply not lent out).

Splits each money market's ETH at the snapshot into staking tokens posted as collateral (counted at their issuers),
plain WETH as collateral or not lent (the Money markets segment) and WETH lent out (shown, never added: borrowers
mostly stake it again, so adding it counts the same ETH twice). Output: data/eth/netmap/lending_gross.json.
"""
import csv, datetime, json, os
from lib import OUT, SNAP_POINT, eth_weight, load, pick, price, series

PLAIN = {'ETH', 'WETH', 'WETH.E', 'ETH.E'}
# BTC study, money_markets.csv (20 Sep 2026): DefiLlama TVL of 68 money markets, plain wrappers vs BTC staking tokens
BTC = {'snapshot': '2026-09-20', 'btc_usd': 81178, 'total_btc': 173745, 'plain_btc': 166756, 'staking_tokens_btc': 6989,
       'lent_out_btc': 4049, 'counted_btc': 159433}


def borrowed_plain_usd(d):
    ct = d.get('chainTvls', {})
    keys = [k for k in ct if k.endswith('-borrowed')] or [k for k in ct if k == 'borrowed']
    usd = 0.0
    for k in keys:
        pts = {datetime.datetime.fromtimestamp(p['date'], datetime.UTC).date(): p['tokens'] for p in ct[k].get('tokensInUsd') or []}
        v, _ = pick(pts, SNAP_POINT)
        usd += sum(x for s, x in (v or {}).items() if s.upper() in PLAIN and x and x > 0)
    return usd


def main():
    p = price(SNAP_POINT)
    rows = []
    for r in csv.DictReader(open(os.path.join(OUT, 'market_map_current.csv'))):
        if r['category'] != 'lending':
            continue
        try:
            d = load(r['slug'])
        except FileNotFoundError:
            continue
        v, _ = pick(series(r['slug']), SNAP_POINT)
        plain = lst = 0.0
        for s, x in (v or {}).items():
            su, w = s.upper(), eth_weight(s)
            if w <= 0 or not x or x < 0 or su == 'SPETH':  # spETH is WETH already inside SparkLend
                continue
            if su in PLAIN:
                plain += x
            else:
                lst += w * x
        lent = borrowed_plain_usd(d)
        rows.append({'slug': r['slug'], 'name': r['product'], 'plain_eth': plain / p, 'staking_tokens_eth': lst / p,
                     'lent_out_eth': lent / p, 'counted_eth': float(r['eth'])})
    rows = [x for x in rows if x['plain_eth'] + x['staking_tokens_eth'] + x['lent_out_eth'] >= 1]
    rows.sort(key=lambda x: -(x['plain_eth'] + x['staking_tokens_eth']))
    tot = {k: sum(x[k] for x in rows) for k in ('plain_eth', 'staking_tokens_eth', 'lent_out_eth', 'counted_eth')}
    out = {'snapshot': '2026-10-02', 'eth_usd': p, 'basis': 'DefiLlama protocol TVL by token at the snapshot point '
           '(collateral plus supply not lent out) plus DefiLlama borrowed tokens for WETH lent out',
           'totals': tot, 'protocols': rows, 'btc': BTC}
    json.dump(out, open(os.path.join(OUT, 'lending_gross.json'), 'w'), indent=1)
    held = tot['plain_eth'] + tot['staking_tokens_eth']
    print(f"Lending gross: {held/1e6:.2f}M ETH held (${held*p/1e9:.1f}B): staking tokens {tot['staking_tokens_eth']/1e6:.2f}M, "
          f"plain {tot['plain_eth']/1e6:.2f}M; lent out {tot['lent_out_eth']/1e6:.2f}M; {len(rows)} protocols")


if __name__ == '__main__':
    main()
