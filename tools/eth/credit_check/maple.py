"""Maple WETH pools at T: totalAssets, WETH cash, loans (principalOut via the pool manager), totalSupply."""
from common import *
P = {'0xfff9a1caf78b2e5b0a49355a8637ea78b43fb6c3': 'M11 Credit Maple Pool WETH1', '0xccbc525ed9d85ad8325b7b6c4c6a79f5566dea3b': 'High Yield Corporate Loan Maple Pool WETH1'}
out = {}
for p, n in P.items():
    pm = A(c(1, p, 'manager()'))
    r = dict(name=n, asset=A(c(1, p, 'asset()')), totalAssets=U(c(1, p, 'totalAssets()')) / 1e18, totalSupply=U(c(1, p, 'totalSupply()')) / 1e18,
             weth_cash=bal(1, WETH[1], p) / 1e18, manager=pm)
    try: r['unrealizedLosses'] = U(c(1, pm, 'unrealizedLosses()')) / 1e18
    except Exception: pass
    try:
        n_lm = U(c(1, pm, 'loanManagerListLength()')); r['loan_managers'] = []
        for i in range(n_lm):
            lm = A(c(1, pm, 'loanManagerList(uint256)', i))
            r['loan_managers'].append(dict(lm=lm, assetsUnderManagement=U(c(1, lm, 'assetsUnderManagement()')) / 1e18,
                                           principalOut=U(c(1, lm, 'principalOut()')) / 1e18))
    except Exception as e: r['lm_err'] = str(e)[:100]
    try: r['strategies'] = U(c(1, pm, 'strategyListLength()'))
    except Exception: pass
    out[p] = r; print(p, json.dumps(r))
save('maple.json', out)
