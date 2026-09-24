"""Select BTC-family lending pools from DefiLlama yields /pools (read 2026-09-23) -> raw/btc_lending_pools.json.
BTC family = the map's list (tools/marketmap/scripts/lib.py btc_weight == 1) plus a few symbols seen in lending pools that the
list lacks (vault-share / bridged BTC tokens, flagged 'extra_symbol'). Category from api.llama.fi/protocols."""
import json, os, sys, collections
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(D, '..', 'scripts')))
from lib import btc_weight
P = json.load(open(os.path.join(D, 'raw', 'pools.json')))['data']
PR = json.load(open(os.path.join(D, 'raw', 'protocols.json')))
LB = {x['pool']: x for x in json.load(open(os.path.join(D, 'raw', 'lendborrow.json')))}
cat = {p['slug']: p['category'] for p in PR}
LEND_CATS = ('Lending', 'Uncollateralized Lending', 'CDP', 'Collateral Markets', 'Risk Curators', 'Leveraged Farming', 'NFT Lending')
# BTC-family symbols missing from the map's list, seen in lending pools (vault shares / bridged BTC); weight 1, flagged
EXTRA = {'SVBTC', 'GTWBTCC', 'GTCBBTCC', 'HYPERCBBTCA', 'MWCBBTC', 'CDCBTC', 'GOBTC', 'IBTC', 'WBTC-NTT', 'ZWBTC', 'SBWBTC',
         'XWBTC', 'XSTRKBTC', 'XSBTC', 'XLBTC', 'XTBTC', 'ZENBTC', 'ARMCWBTC', 'YVVBWBTC', 'VBGTWBTC', 'WMTWBTC', 'V-WMTWBTC',
         'WMTCBBTC', 'GHEMIBTC', 'GAMIWBTC', 'DWBTC-V3-0', 'STSTXBTC', 'HYPERWILDCATFASTCBBTC', 'AUROSCBBTC'}
out = []
for p in P:
    c = cat.get(p['project'])
    if c not in LEND_CATS:
        continue
    s = (p['symbol'] or '').upper()
    w = btc_weight(s)
    extra = s in EXTRA
    if w < 1 and not extra:
        continue
    lb = LB.get(p['pool'], {})
    out.append(dict(pool=p['pool'], project=p['project'], category=c, chain=p['chain'], symbol=p['symbol'], poolMeta=p.get('poolMeta'),
                    tvlUsd=p['tvlUsd'], apy=p['apy'], apyBase=p['apyBase'], apyReward=p['apyReward'], apyMean30d=p.get('apyMean30d'),
                    apyBase7d=p.get('apyBase7d'), rewardTokens=p.get('rewardTokens'), underlyingTokens=p.get('underlyingTokens'),
                    totalSupplyUsd=lb.get('totalSupplyUsd'), totalBorrowUsd=lb.get('totalBorrowUsd'), ltv=lb.get('ltv'),
                    borrowable=lb.get('borrowable'), apyBaseBorrow=lb.get('apyBaseBorrow'), extra_symbol=extra))
out.sort(key=lambda x: -x['tvlUsd'])
json.dump(out, open(os.path.join(D, 'raw', 'btc_lending_pools.json'), 'w'), indent=0)
by = collections.defaultdict(float)
for x in out:
    by[x['category']] += x['tvlUsd']
print(len(out), 'pools', {k: round(v / 1e6, 1) for k, v in by.items()})
print('>=1M:', sum(1 for x in out if x['tvlUsd'] >= 1e6), ' >=0.3M:', sum(1 for x in out if x['tvlUsd'] >= 3e5))
