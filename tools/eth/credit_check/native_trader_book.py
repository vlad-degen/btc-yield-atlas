"""Native Credit Vault (Ethereum): the borrowing trader's positions and collateral in the vault's other markets at T."""
from common import *
V = '0xe3D41d19564922C9952f692C5Dd0563030f5f2EF'; T = '0x129b3d9a0a6e4beab88f5cb1e57995d72a6e24f1'
lg = logs(1, V, [topic('MarketListed(address)')], 22173196, B1, step=200000)
lps = ['0x' + l['data'][-40:] for l in lg]
out = []
for lp in lps:
    u = A(c(1, lp, 'underlying()')); d = U(c(1, u, 'decimals()')); s = dec_str(c(1, u, 'symbol()'))
    p = U(c(1, V, 'positions(address,address)', T, u)); p = p - 2 ** 256 if p >= 2 ** 255 else p
    out.append(dict(lp=lp, token=u, symbol=s, lp_total=U(c(1, lp, 'totalUnderlying()')) / 10 ** d, vault_cash=bal(1, u, V) / 10 ** d,
                    trader_position=p / 10 ** d, trader_collateral=U(c(1, V, 'collateral(address,address)', T, u)) / 10 ** d))
    print(out[-1])
save('native_trader_book.json', out)
