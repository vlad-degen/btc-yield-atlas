"""Cap's wstETH/weETH Symbiotic vaults: are they in the Symbiotic vault factory (DefiLlama Symbiotic row), who deposits into them."""
from common import *
FACT = '0xAEb6bdd95c502390db8f52c8909F703E9Af6a346'
d = json.load(open(os.path.join(OUT, 'cap.json')))
out = []
DEP = topic('Deposit(address,address,uint256,uint256)')
for a in d['agents']:
    if (a.get('collateral') or '') not in (WSTETH, WEETH) or not a.get('vault_bal'):
        continue
    v = a['vault']
    r = dict(agent=a['agent'], vault=v, collateral=a['collateral'], cover=a['coverage_tokens'] / 1e18, bal=a['vault_bal'] / 1e18,
             in_factory=U(c(1, FACT, 'isEntity(address)', v)), version=U(c(1, v, 'version()')),
             total_stake=U(c(1, v, 'totalStake()')) / 1e18, debt_usdc=sum(a['debt'].values()) / 1e6)
    lg = logs(1, v, [DEP], a['block'] - 50000, B1)
    deps = sorted({'0x' + l['topics'][2][-40:] for l in lg})
    hold = {}
    for x in deps:
        b = U(c(1, v, 'activeBalanceOf(address)', x)) / 1e18
        if b > 0.01: hold[x] = b
    r['holders'] = hold
    for x in hold:
        nm = c(1, x, 'name()'); r.setdefault('holder_names', {})[x] = dec_str(nm) if nm else None
    try: r['burner'] = A(c(1, a['slasher'], 'burner()')) if a.get('slasher') else None
    except Exception: pass
    out.append(r); print(json.dumps(r))
save('cap_vaults.json', out)
