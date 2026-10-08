"""Native Credit Vault (Ethereum): traders (TraderSet), their WETH positions (negative = borrowed from the pool) and WETH collateral at T."""
from common import *
V = '0xe3D41d19564922C9952f692C5Dd0563030f5f2EF'; W = WETH[1]
lg = logs(1, V, [topic('TraderSet(address,bool,bool,address,address)')], 22173196, B1, step=200000)
tr = sorted({'0x' + l['topics'][1][-40:] for l in lg})
rows = []
for t in tr:
    p = U(c(1, V, 'positions(address,address)', t, W)); p = p - 2 ** 256 if p >= 2 ** 255 else p
    col = U(c(1, V, 'collateral(address,address)', t, W))
    act = U(c(1, V, 'traders(address)', t))
    rows.append(dict(trader=t, active=act, weth_position=p / 1e18, weth_collateral=col / 1e18,
                     recipient=A(c(1, V, 'traderToRecipient(address)', t)), settler=A(c(1, V, 'traderToSettler(address)', t))))
res = dict(traders=rows, reserve_fees=U(c(1, V, 'reserveFees(address)', W)) / 1e18, vault_weth=bal(1, W, V) / 1e18,
           lp_total_underlying=U(c(1, '0x5994258ec80cc6853e2b6f047ec6d213fe89b24b', 'totalUnderlying()')) / 1e18,
           borrowed=-sum(r['weth_position'] for r in rows if r['weth_position'] < 0),
           long=sum(r['weth_position'] for r in rows if r['weth_position'] > 0),
           collateral=sum(r['weth_collateral'] for r in rows))
for r in rows:
    if abs(r['weth_position']) > 0.01 or r['weth_collateral'] > 0.01: print(r)
print({k: v for k, v in res.items() if k != 'traders'})
save('native_traders.json', res)
