"""Screen fetched protocols: ETH-family value at the snapshot and every month-end, per chain.

Writes raw/eth/netmap-2026-10-07/screen.json: {slug: {name, category, doublecounted, snap_eth, peak_eth, peak_month,
months: {label: eth}, tokens_snap: {sym: eth}, chains_snap: {chain: eth}}} and unknown_symbols.json for review.
Keeps a protocol when it holds >= 100 ETH at the snapshot or >= 1,000 ETH at any month-end (BTC map: ~$0.25M / $3M).
"""
import collections, json, os
from lib import RAW, eth_part, load, month_points, pick, price, series, unknown_ethlike

SKIP_CHAIN_KEYS = ('borrowed', 'staking', 'pool2', 'vesting', 'treasury', 'offers', 'doublecounted', 'liquidstaking', 'dcAndLsOverlap')


def chain_keys(d):
    """per-chain keys without the '-borrowed'/'-staking' style sub-keys DefiLlama adds"""
    return [c for c in (d.get('chainTvls') or {}) if not any(c.endswith('-' + k) or c == k for k in SKIP_CHAIN_KEYS)]


def main():
    cand = json.load(open(os.path.join(RAW, 'candidates.json')))
    pts = month_points()
    out, unknown = {}, collections.Counter()
    for slug, meta in cand.items():
        p = os.path.join(RAW, 'proto', slug + '.json.gz')
        if not os.path.exists(p):
            continue
        try:
            d = load(slug)
        except (EOFError, OSError, ValueError):
            print('unreadable (fetch in progress?):', slug)
            continue
        ser = series(slug)
        if not ser:  # some adapters only publish per-chain token series
            continue
        months = {}
        for label, pdate, _ in pts:
            tok, _dt = pick(ser, pdate)
            pr = price(pdate)
            if tok is None or not pr:
                continue
            usd, br = eth_part(tok)
            months[label] = usd / pr
            if label == pts[-1][0]:
                tokens_snap = {k: v / pr for k, v in br.items()}
                for s, v in tok.items():
                    if v and v > 1e5 and unknown_ethlike(s):
                        unknown[s.upper()] += v
        snap = months.get(pts[-1][0], 0.0)
        hist = {k: v for k, v in months.items() if k != pts[-1][0]}
        peak_m = max(hist, key=hist.get) if hist else None
        peak = hist.get(peak_m, 0.0) if peak_m else 0.0
        if snap < 100 and peak < 1000:
            continue
        chains = {}
        pr = price(pts[-1][1])
        for ch in chain_keys(d):
            tok, _ = pick(series(slug, ch), pts[-1][1])
            if tok:
                v, _b = eth_part(tok)
                if v > 0:
                    chains[ch] = v / pr
        out[slug] = dict(name=d.get('name'), category=d.get('category'), doublecounted=d.get('doublecounted'),
                         parent=d.get('parentProtocol'), url=d.get('url'), snap_eth=snap, peak_eth=peak, peak_month=peak_m,
                         months=months, tokens_snap=locals().get('tokens_snap', {}), chains_snap=chains)
        tokens_snap = {}
    json.dump(out, open(os.path.join(RAW, 'screen.json'), 'w'), indent=1)
    json.dump(unknown.most_common(), open(os.path.join(RAW, 'unknown_symbols.json'), 'w'), indent=1)
    print(len(out), 'protocols kept; unknown ETH-like symbols (USD at snapshot):')
    for s, v in unknown.most_common(60):
        print(f'  {s:28} {v/1e6:10.1f}M')


if __name__ == '__main__':
    main()
