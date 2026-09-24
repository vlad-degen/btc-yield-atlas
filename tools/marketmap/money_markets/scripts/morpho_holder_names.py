"""Names of Morpho BTC-collateral depositors with >= 3 BTC (Ethereum, Base, Arbitrum, Katana via Blockscout) -> raw/morpho/holder_names.json"""
import json, os, subprocess, time
from mmlib import RAW
P = json.load(open(os.path.join(RAW, 'morpho', 'positions.json')))
HOST = {'Ethereum': 'eth.blockscout.com', 'Base': 'base.blockscout.com', 'Arbitrum One': 'arbitrum.blockscout.com', 'Katana': 'explorer.katanarpc.com'}
todo = {}
for k, x in P.items():
    m = x['market']; dec = m['collateralAsset']['decimals']; ch = m['chain']['network']
    for p in x['positions']:
        c = int(p['state']['collateral'] or 0) / 10 ** dec
        if c >= 3 and ch in HOST:
            key = (ch, p['user']['address'])
            todo.setdefault(key, []).append((m['collateralAsset']['symbol'] + '/' + m['loanAsset']['symbol'], round(c, 3)))
print(len(todo))
out = {}
f = os.path.join(RAW, 'morpho', 'holder_names.json')
if os.path.exists(f): out = json.load(open(f))
for (ch, a), pos in todo.items():
    kk = f'{ch}:{a}'
    if kk in out: continue
    r = subprocess.run(['curl', '-sS', '-m', '30', '-A', 'Mozilla/5.0', f'https://{HOST[ch]}/api/v2/addresses/{a}'], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        out[kk] = dict(name=d.get('name'), is_contract=d.get('is_contract'), impl=[i.get('name') for i in (d.get('implementations') or []) if i.get('name')], pos=pos)
    except Exception:
        out[kk] = dict(err=r.stdout[:100], pos=pos)
    time.sleep(0.25)
json.dump(out, open(f, 'w'), indent=0)
