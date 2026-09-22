"""Daily (00:00 UTC) + snapshot archive reads on Ethereum for the Kraken BTC vault's legs.
Output raw/daily_eth.json {date: {...decoded values...}}"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from klib import *
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
B = json.load(open(os.path.join(RAW, 'blocks_daily.json')))
if len(sys.argv) > 1:  # extra named blocks, e.g. now=26030000
    for kv in sys.argv[1:]:
        k, v = kv.split('='); B[k] = dict(eth=int(v))
MORPHO = '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
MK = {
    'kBTC_RLUSD': '0x15bb2a6af0c909eed19fb1f2ceeead34ecbdcba626de752c6b09389ee14eec32',
    'kBTC_PYUSD': '0xe51f9aaad25d0e755429cf77076b3c2d37cb1228ed81f8a5482f2102c220eef5',
    'WBTC_USDT': '0xa921ef34e2fc7a27ccc50ae7e4b154e16c9799d3387076c421423ef52ac4df99',
    'PRIME_PYUSD': '0x41c41d0c9aadbf4751f5ee215ed5a16954a4b34e1b70fca5393d4b08858fa3fa',
    'PST_PYUSD': '0xb4977179610abfecfc8b76255a002c16b33f46d077beb86e5911e1fe9ee6e512',
}
POS = {  # (market, holder)
    'RLUSD-1': ('kBTC_RLUSD', '0x0774b5B15B0CEe5E2e14814CCF4d4611fF78CcF5'),
    'RLUSD-2': ('kBTC_RLUSD', '0x7fB9f8F775e3Ff458ce5D9d146f36e9e4639205E'),
    'PYUSD-1': ('kBTC_PYUSD', '0xd18DF3c05D2D11BDeDBd9F7501f651e43b9bd986'),
    'PYUSD-2': ('kBTC_PYUSD', '0x1E8f4752209A50eFE5b6126f5c534dC7018d9489'),
    'WBTC-USDT': ('WBTC_USDT', '0x5EE1E2e3540eFCE54Fc477d6648537e07080f884'),
}
ORACLE = {'kBTC_RLUSD': '0xbcc3d9834b84b32cf540dbe948ded4b47bec5ddb', 'kBTC_PYUSD': '0x007db14ca0d171fa583955fef3917b2b9a95cf18',
          'WBTC_USDT': '0x008bf4b1cda0cc9f0e882e0697f036667652e1ef'}
CL_BTC = '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c'
PRIME_FEED = '0xf17C0EdcAA28371e9c8012D7699bF40ECF0F58d1'
V2 = {'senRLUSDv2': ('0x6dC58a0FdfC8D694e571DC59B9A52EEEa780E6bf', '0x8292bb45bf1ee4d140127049757c2e0ff06317ed', 18),
      'senPYUSDmain': ('0xb576765fB15505433aF24FEe2c0325895C559FB2', '0x6c3ea9036406852006290770bedfcaba0e23a0e8', 6),
      'senPYUSDPRIMEv2': ('0xC21b08C16458202593D4D9B26b9984Ee67b38BbD', '0x6c3ea9036406852006290770bedfcaba0e23a0e8', 6),
      'senPYUSDPST': ('0x8381a156958711E230f325428B5eb4b6555C75D9', '0x6c3ea9036406852006290770bedfcaba0e23a0e8', 6)}
PRIME = '0x19ebb35279A16207Ec4ba82799CC64715065F7F6'
YS = {  # holder -> token
    'RLUSD-A': ('0xb03d620e49b6a21ea9d02142831c3f61c2fcbabc', 'senRLUSDv2'),
    'PYUSD-A': ('0x4dd13fba19ac587d041646d0d941b1aa18d58c2f', 'senPYUSDmain'),
    'RLUSD-B': ('0x3884f27b834de0413e4fe703fe35d1d43b9a124a', 'PRIME'),
    'PYUSD-B': ('0xef8068287f1a0fc19159bdd43e283beee877950b', 'PRIME'),
    'YS1-PRIMEMain': ('0xfd58a8d52c0e1ad8d086aea623c90f77fb39efdc', 'senPYUSDPRIMEv2'),
    'YS2-PST': ('0x574395d60c16514c1a353d4676a9df674ecabd01', 'senPYUSDPST'),
}
AAVE_POOL = '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'; USDT = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
AWBTC = '0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8'; VDUSDT = '0x6df1C1E379bC5a00a7b4C6e67A203333772f45A8'
LMA = '0xf523259262979a26095474974b56443ad34c53b7'
out_path = os.path.join(RAW, 'daily_eth.json')
OUT = json.load(open(out_path)) if os.path.exists(out_path) else {}
keys = [k for k in B if k not in OUT]
if os.environ.get("ONLY"): keys = [k for k in keys if k == os.environ["ONLY"]]
for k in keys:
    b = B[k]['eth']
    calls, names = [], []
    def add(name, to, data): names.append(name); calls.append((to, data, b))
    for m, mid in MK.items(): add(('market', m), MORPHO, sel('market(bytes32)') + enc_b32(mid))
    for p, (m, h) in POS.items(): add(('pos', p), MORPHO, sel('position(bytes32,address)') + enc_b32(MK[m]) + enc_addr(h))
    for m, o in ORACLE.items(): add(('oracle', m), o, sel('price()'))
    add(('cl_btc',), CL_BTC, sel('latestRoundData()'))
    add(('prime_feed',), PRIME_FEED, sel('latestRoundData()'))
    for v, (addr, asset, dec) in V2.items():
        add(('v2_pps', v), addr, sel('convertToAssets(uint256)') + enc_uint(10 ** 18))
        add(('v2_ta', v), addr, sel('totalAssets()'))
        add(('v2_ts', v), addr, sel('totalSupply()'))
        add(('v2_idle', v), asset, sel('balanceOf(address)') + enc_addr(addr))
    for y, (h, t) in YS.items():
        tok = PRIME if t == 'PRIME' else V2[t][0]
        add(('ys', y), tok, sel('balanceOf(address)') + enc_addr(h))
    add(('aave_usdt',), AAVE_POOL, sel('getReserveData(address)') + enc_addr(USDT))
    add(('aave_awbtc',), AWBTC, sel('balanceOf(address)') + enc_addr(LMA))
    add(('aave_vdusdt',), VDUSDT, sel('balanceOf(address)') + enc_addr(LMA))
    add(('aave_acct',), AAVE_POOL, sel('getUserAccountData(address)') + enc_addr(LMA))
    add(('eth_ts',), '0xcA11bde05977b3631167028862bE2a173976CA11', sel('getCurrentBlockTimestamp()'))
    res = batch_calls('eth', calls, chunk=30)
    row = {'block': b}
    for n, r in zip(names, res):
        w = words(r) if isinstance(r, str) and r not in ('0x',) else None
        key = '|'.join(n)
        if w is None: row[key] = None; continue
        if n[0] == 'market': row[key] = w[:6]
        elif n[0] == 'pos': row[key] = w[:3]
        elif n[0] in ('cl_btc', 'prime_feed'): row[key] = [w[1], w[3]]
        elif n[0] == 'aave_usdt': row[key] = w[:7]
        elif n[0] == 'aave_acct': row[key] = w[:6]
        else: row[key] = w[0]
    OUT[k] = row
    json.dump(OUT, open(out_path, 'w'))
    print(k, b, 'nulls', sum(1 for v in row.values() if v is None), flush=True)
