"""Wildcat (Ethereum): every registered market whose asset is WETH, at T: supplied (totalSupply, normalized), idle (totalAssets),
lent out, borrower, name."""
from common import *
ARCH = '0xfEB516d9D946dD487A9346F6fee11f40C6945eE4'
r = c(1, ARCH, 'getRegisteredMarkets()')
mk = addr_list(r)
assets = mcall(1, [(m, sel('asset()')) for m in mk], B1)
weth = [m for m, a in zip(mk, assets) if a and A(a) == WETH[1]]
print(len(mk), 'markets,', len(weth), 'WETH')
rows = []
for m in weth:
    g = lambda s: c(1, m, s)
    row = dict(market=m, name=dec_str(g('name()')), symbol=dec_str(g('symbol()')), borrower=A(g('borrower()')),
               totalSupply=U(g('totalSupply()')) / 1e18, totalAssets=U(g('totalAssets()')) / 1e18, weth_balance=bal(1, WETH[1], m) / 1e18)
    for s in ['totalDebts()', 'outstandingDebt()', 'borrowableAssets()', 'scaleFactor()', 'annualInterestBips()', 'reserveRatioBips()',
              'accruedProtocolFees()', 'isClosed()', 'version()', 'delinquentDebt()']:
        try:
            v = g(s)
            if v and v != '0x': row[s] = U(v) / (1e18 if s in ('totalDebts()', 'outstandingDebt()', 'borrowableAssets()', 'accruedProtocolFees()', 'delinquentDebt()') else 1)
        except Exception: pass
    row['lent'] = max(0.0, row['totalSupply'] - row['totalAssets'])
    rows.append(row); print(json.dumps(row))
tot = dict(n=len(rows), supplied=sum(r['totalSupply'] for r in rows), idle=sum(r['totalAssets'] for r in rows), lent=sum(r['lent'] for r in rows))
print(tot)
save('wildcat.json', dict(block=B1, all_markets=len(mk), weth_markets=rows, totals=tot))
