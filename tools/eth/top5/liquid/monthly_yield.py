"""Liquid ETH month-end share price vs stETH and weETH (deep dive 2026-10-07).

Month-end blocks are the end_block column of data/eth/top5/liquid/pnl_monthly.csv (start block of Oct 2024 added),
i.e. the study's verified month-end blocks, last one T = block 26,108,081.
Reads Accountant getRate, wstETH stEthPerToken, weETH getRate (archive eth_call, cached like weekly_yield.py).
Output: data/eth/top5/liquid/yield_monthly.csv
"""
import csv, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from weekly_yield import ROOT, ACC, WSTETH, WEETH, batch  # noqa: E402
from klib import sel, words  # noqa: E402


def main():
    P = list(csv.DictReader(open(ROOT / 'data/eth/top5/liquid/pnl_monthly.csv')))
    pts = [('2024-09', 20874085)] + [(r['month'], int(r['end_block'])) for r in P]
    items = []
    for m, b in pts:
        for n, to, sig in (('l', ACC, 'getRate()'), ('s', WSTETH, 'stEthPerToken()'), ('w', WEETH, 'getRate()')):
            items.append((f'{m}|{n}', to, '0x' + sel(sig), b))
    res = batch(items)
    v = {m: {n: words(res[f'{m}|{n}'])[0] / 1e18 for n in 'lsw'} for m, _ in pts}
    cols = ['month', 'end_block', 'days', 'liquid_return_pct', 'steth_return_pct', 'weeth_return_pct', 'liquid_apy_pct',
            'steth_apy_pct', 'excess_vs_steth_pp_apy', 'source']
    days = {r['month']: float(r['days']) for r in P}
    with open(ROOT / 'data/eth/top5/liquid/yield_monthly.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader()
        for (m0, _), (m, b) in zip(pts, pts[1:]):
            d = days[m]
            lr, sr, wr_ = (v[m][k] / v[m0][k] - 1 for k in 'lsw')
            la, sa = ((1 + lr) ** (365 / d) - 1) * 100, ((1 + sr) ** (365 / d) - 1) * 100
            wr.writerow({'month': m, 'end_block': b, 'days': d, 'liquid_return_pct': f'{lr * 100:.4f}',
                         'steth_return_pct': f'{sr * 100:.4f}', 'weeth_return_pct': f'{wr_ * 100:.4f}',
                         'liquid_apy_pct': f'{la:.3f}', 'steth_apy_pct': f'{sa:.3f}', 'excess_vs_steth_pp_apy': f'{la - sa:.3f}',
                         'source': 'archive eth_call at month-end block: Accountant 0x0d05d94a getRate, wstETH stEthPerToken, weETH getRate; APY compounded'})


if __name__ == '__main__':
    main()
