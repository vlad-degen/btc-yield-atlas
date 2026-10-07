"""Month-end (Oct 2024-Sep 2026) + T archive reads of every top-5 dollar-debt account and destination share price.
Output: raw/eth/gap-2026-10-07/top5-risk/positions_raw.json (decoded + raw hex)."""
import json
from glib import *
AAVE = '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
SPARK = '0xc13e21b648a5ee794902342038ff3adab66be987'
MORPHO = '0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
POOL_ACCTS = [('liquid', 'Aave', AAVE, '0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c'), ('liquid', 'Spark', SPARK, '0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c'),
              ('lido-earn', 'Aave', AAVE, '0x181cb55f872450d16ae858d532b4e35e50eaa76d'), ('lido-earn', 'Spark', SPARK, '0x181cb55f872450d16ae858d532b4e35e50eaa76d'),
              ('lido-earn', 'Aave', AAVE, '0x9938a09fea37ba681a1bd53d33ddde2debec1da0'),
              ('avant', 'Aave', AAVE, '0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd'), ('avant', 'Spark', SPARK, '0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd')]
MARKETS = {'RLUSD': '0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4', 'USDC': '0x85252bb8485c99bba46fe149c7dd2aad83672640f53c630890673cf1848ba16e',
           'PYUSD': '0x85d59152eeeab7ca024804895b358868d8dd1e134171be400d7792d5604a212c'}
MORPHO_ACCTS = ['0xf0bb20865277abd641a307ece5ee04e79073416c', '0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3']
YB_AMM = '0x5f8d24f33cc5a1d5d1bf012261e6a2214c92233c'
EB_TM = '0xa2895d6a3bf110561dfe4b71ca539d84e1928b22'
EB_FEED = '0xe7aa2ba9e086a379d3beb224098bc634a46e314e'
TROVES = {'0xac40ba2aa0406f993c7a42e40582780a0b41faf53d5114ba6ff9b0dcfb20e5e1': (24633120, 24721894),
          '0xcc51338b5ab465b7ec52a0de0741899e636b082aacd3042d26869c7a48522064': (24728697, 24843550),
          '0xa7f1a2fe7a218624ee350df8a3295a00d33f9692a70d9769727c8889bffb4f93': (24843680, 25257843),
          '0x17fde209476c98d24130b7aeb255ce752bced0de896f10ad8ea519bad6dcf8b0': (25261237, None)}
DEST = {'senRLUSDv2': ('0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf', 18, 18), 'senPYUSDPRIMEv2': ('0xc21b08c16458202593d4d9b26b9984ee67b38bbd', 18, 6),
        'stcUSD': ('0x88887be419578051ff9f4eb6c858a951921d8888', 18, 18), 'PRIME': ('0x19ebb35279a16207ec4ba82799cc64715065f7f6', 6, 6)}
EARN_ORACLE = '0x827044735c9708a2cf850e7ea37eba43bc786028'
USDT = '0xdac17f958d2ee523a2206206994597c13d831ec7'
EB_POOL = '0xefc6516323fbd28e80b85a497b65a86243a54b3e'
CL_ETH = '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'

def main():
    M = months()
    params = {}
    r = batch([c(MORPHO, 'idToMarketParams(bytes32)', enc_b32(mid)) for mid in MARKETS.values()] + [c(YB_AMM, 'COLLATERAL()'), c(YB_AMM, 'LEVERAGE()'), c(EB_TM, 'MCR()') if False else c('0x0000000000000000000000000000000000000000', 'x()')], tag='static')
    for (sym, mid), h in zip(MARKETS.items(), r[:3]):
        w = words(h); params[sym] = dict(loan=dec_addr(w[0]), coll=dec_addr(w[1]), oracle=dec_addr(w[2]), irm=dec_addr(w[3]), lltv=w[4] / 1e18)
    yb_coll = dec_addr(words(r[3])[0]); yb_lev = words(r[4])[0] / 1e18
    out = {'months': [], 'morphoParams': params, 'ybCollateral': yb_coll, 'ybLeverage': yb_lev}
    for m, ts, b in M:
        calls = []; keys = []
        for prod, venue, pool, acct in POOL_ACCTS:
            calls.append(c(pool, 'getUserAccountData(address)', enc_addr(acct), b)); keys.append(('pool', prod, venue, acct))
        for sym, mid in MARKETS.items():
            calls.append(c(MORPHO, 'market(bytes32)', enc_b32(mid), b)); keys.append(('market', sym))
            calls.append(c(params[sym]['oracle'], 'price()', '', b)); keys.append(('oracle', sym))
            for acct in MORPHO_ACCTS:
                calls.append(c(MORPHO, 'position(bytes32,address)', enc_b32(mid) + enc_addr(acct), b)); keys.append(('pos', sym, acct))
        for sg in ['get_state()', 'value_oracle()', 'rate()', 'get_debt()']:
            calls.append(c(YB_AMM, sg, '', b)); keys.append(('yb', sg))
        calls.append(c(yb_coll, 'get_virtual_price()', '', b)); keys.append(('ybvp',))
        for tid in TROVES:
            calls.append(c(EB_TM, 'getLatestTroveData(uint256)', enc_b32(tid), b)); keys.append(('trove', tid))
        calls.append(c(EB_FEED, 'lastGoodPrice()', '', b)); keys.append(('ebprice',))
        calls.append(c(EB_TM, 'MCR()' , '', b)); keys.append(('ebmcr',))
        for name, (addr, sd, ad) in DEST.items():
            calls.append(c(addr, 'convertToAssets(uint256)', enc_uint(10 ** sd), b)); keys.append(('dest', name))
        calls.append(c(EARN_ORACLE, 'getReport(address)', enc_addr(USDT), b)); keys.append(('dest', 'earnUSD_report'))
        calls.append(c(EB_POOL, 'get_virtual_price()', '', b)); keys.append(('dest', 'curve_ebUSD_USDC_vp'))
        calls.append(c(CL_ETH, 'latestAnswer()', '', b)); keys.append(('ethusd',))
        res = batch(calls, tag='month_' + m)
        out['months'].append({'month': m, 'timestamp': ts, 'block': b, 'reads': [{'key': list(k), 'to': cc[0], 'data': cc[1], 'result': v} for k, cc, v in zip(keys, calls, res)]})
        print(m, b, sum(v is not None for v in res), '/', len(res), flush=True)
    json.dump(out, open(RAW / 'positions_raw.json', 'w'), indent=1)
if __name__ == '__main__':
    main()
