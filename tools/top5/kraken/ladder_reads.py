"""Archive reads at the snapshot block for the liquidity ladder: every Morpho market each Sentora V2 vault
(that the Kraken vault holds) allocates to, the V2 adapter's supply position there, V2 idle, force-deallocate
penalties, and the PRIME/PYUSD and PST/PYUSD market params. Output raw/ladder_snapshot.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from klib import *
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
S = int(sys.argv[1]) if len(sys.argv) > 1 else 26018583
MORPHO = '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
struct = json.load(open(os.path.join(RAW, 'v2_structure_now.json')))
out = {'block': S, 'vaults': {}}
for vaddr, r in struct.items():
    v = r['data']['vaultV2ByAddress']
    asset = a('eth', vaddr, 'asset()', '', S)
    adec = u('eth', asset, 'decimals()')
    idle = u('eth', asset, 'balanceOf(address)', enc_addr(vaddr), S) / 10 ** adec
    ta = u('eth', vaddr, 'totalAssets()', '', S) / 10 ** adec
    adapters = [x['address'] for x in v['adapters']['items']]
    pen = {ad: u('eth', vaddr, 'forceDeallocatePenalty(address)', enc_addr(ad), S) for ad in adapters}
    liq_ad = a('eth', vaddr, 'liquidityAdapter()', '', S)
    mkts = []
    for c in v['caps']['items']:
        dd = c['data']
        if dd['__typename'] != 'MarketV1CapData': continue
        mid = dd['market']['marketId']; ad = dd['adapterAddress']
        m = words(callsig('eth', MORPHO, 'market(bytes32)', enc_b32(mid), S))
        p = words(callsig('eth', MORPHO, 'position(bytes32,address)', enc_b32(mid) + enc_addr(ad), S))
        mp = words(callsig('eth', MORPHO, 'idToMarketParams(bytes32)', enc_b32(mid)))
        tsa, tss, tba, tbs = m[:4]
        pos_assets = p[0] * tsa / tss / 10 ** adec if tss else 0
        mkts.append(dict(id=mid, loan=dd['market']['loanAsset']['symbol'], coll=(dd['market']['collateralAsset'] or {}).get('symbol'),
                         lltv=mp[4] / 1e18, supply=tsa / 10 ** adec, borrow=tba / 10 ** adec, liquidity=(tsa - tba) / 10 ** adec,
                         util=tba / tsa if tsa else None, v2_supply=pos_assets, v2_share=(p[0] / tss if tss else None),
                         v2_withdrawable=min(pos_assets, (tsa - tba) / 10 ** adec)))
    out['vaults'][v['symbol']] = dict(address=vaddr, asset=asset, idle=idle, totalAssets=ta, liquidityAdapter=liq_ad,
                                      forceDeallocatePenalty=pen, markets=mkts)
    print(v['symbol'], 'idle', round(idle / 1e6, 2), 'TA', round(ta / 1e6, 2), 'liqAdapter', liq_ad, 'penalty', pen)
    for mm in mkts:
        print('   ', mm['coll'], 'lltv', mm['lltv'], 'util', round(mm['util'] or 0, 4), 'liq', round(mm['liquidity'] / 1e6, 2), 'v2', round(mm['v2_supply'] / 1e6, 2), 'wd', round(mm['v2_withdrawable'] / 1e6, 2))
json.dump(out, open(os.path.join(RAW, f'ladder_{S}.json'), 'w'), indent=1)
