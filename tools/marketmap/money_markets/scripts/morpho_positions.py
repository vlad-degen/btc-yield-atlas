"""Morpho API: top collateral positions in every BTC-collateral market with >= 5 BTC collateral (current state, read 2026-09-23),
and all MetaMorpho (v1) and Vault V2 vaults whose asset is a BTC-family token. -> raw/morpho/positions.json, raw/morpho/vaults.json"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mmlib import btc_weight, RAW
from mgql import gql

M = json.load(open(os.path.join(RAW, 'morpho', 'markets.json')))
def isbtc(a):
    return bool(a) and btc_weight((a.get('symbol') or '').upper()) >= 1
sel = []
for m in M:
    ca, la, st = m.get('collateralAsset'), m.get('loanAsset'), m.get('state') or {}
    if isbtc(ca) and st.get('collateralAssets') and int(st['collateralAssets']) / 10 ** ca['decimals'] >= 5:
        sel.append(m)
print('markets', len(sel), flush=True)
QP = '''query($keys:[String!], $chain:[Int!], $skip:Int){ marketPositions(first: 200, skip: $skip, orderBy: Collateral, orderDirection: Desc,
  where: { marketUniqueKey_in: $keys, chainId_in: $chain, collateral_gte: 0 }) { pageInfo { countTotal }
  items { user { address } market { marketId } state { collateral collateralUsd borrowAssets borrowAssetsUsd supplyAssets } } } }'''
pos = {}
for m in sel:
    key, chain = m['marketId'], m['chain']['id']
    items = []
    d = gql(QP, {'keys': [key], 'chain': [chain], 'skip': 0})
    items = d['data']['marketPositions']['items']
    pos[f"{chain}:{key}"] = dict(market=m, positions=items, count=d['data']['marketPositions']['pageInfo']['countTotal'])
    time.sleep(0.3)
json.dump(pos, open(os.path.join(RAW, 'morpho', 'positions.json'), 'w'))
print('positions saved', flush=True)

QV = '''query($skip:Int){ vaults(first: 1000, skip: $skip) { pageInfo { countTotal }
  items { address name symbol chain { id network } asset { symbol address decimals }
   state { totalAssets totalAssetsUsd curator allocation { market { marketId collateralAsset { symbol } loanAsset { symbol } } supplyAssets supplyAssetsUsd } } } } }'''
vaults = []; skip = 0
while True:
    d = gql(QV, {'skip': skip})
    it = d['data']['vaults']['items']; vaults += it
    if len(it) < 1000: break
    skip += 1000
QV2 = '''query($skip:Int){ vaultV2s(first: 1000, skip: $skip) { pageInfo { countTotal }
  items { address name symbol chain { id network } asset { symbol address decimals } totalAssets totalAssetsUsd curator { address }
   adapters { items { address type assets assetsUsd } } } } }'''
v2 = []; skip = 0
while True:
    try:
        d = gql(QV2, {'skip': skip})
    except SystemExit:
        print('vaultV2 query failed'); break
    it = d['data']['vaultV2s']['items']; v2 += it
    if len(it) < 1000: break
    skip += 1000
json.dump(dict(v1=[v for v in vaults if isbtc(v.get('asset'))], v2=[v for v in v2 if isbtc(v.get('asset'))]),
          open(os.path.join(RAW, 'morpho', 'vaults.json'), 'w'))
print('vaults v1', len(vaults), 'v2', len(v2))
