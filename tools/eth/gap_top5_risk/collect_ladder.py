"""Fixed-block (T) reads for the liquidity ladder. Output raw ladder_T_raw.json (decoded)."""
import json
from glib import *
MORPHO = '0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
TOK = {'RLUSD': ('0x8292bb45bf1ee4d140127049757c2e0ff06317ed', 18), 'USDC': ('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 6), 'USDT': ('0xdac17f958d2ee523a2206206994597c13d831ec7', 6),
       'PYUSD': ('0x6c3ea9036406852006290770bedfcaba0e23a0e8', 6), 'cUSD': ('0xcccc62962d17b8914c62d74ffb843d73b2a3cccc', 18), 'wYLDS': ('0x6ad038ca6c04e885630851278ca0a856ad9a66cc', 6),
       'USDe': ('0x4c9edd5852cd905f086c759e8383e09bff1e68b3', 18), 'USDS': ('0xdc035d45d973e3ec169d2276ddab16f1e407384f', 18), 'ebUSD': ('0x6440f144b7e50d6a8439336510312d2f54beb01d', 18),
       'WETH': ('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', 18), 'crvUSD': ('0xf939e0a03fb07f59a73314e73794be0e57ac1b4e', 18)}
VAULTS = {'senRLUSDv2': ('0x6dc58a0fdfc8d694e571dc59b9a52eeea780e6bf', 'RLUSD', 18), 'senPYUSDPRIMEv2': ('0xc21b08c16458202593d4d9b26b9984ee67b38bbd', 'PYUSD', 18),
          'stcUSD': ('0x88887be419578051ff9f4eb6c858a951921d8888', 'cUSD', 18), 'PRIME': ('0x19ebb35279a16207ec4ba82799cc64715065f7f6', 'wYLDS', 6)}
LIQ = ['0xf0bb20865277abd641a307ece5ee04e79073416c', '0xc936e848688c9f035fa0e7a0e4dbcf26a01245f3', '0x0a42b2f3a0d54157dbd7cc346335a4f1909fc02c']
LIDO = '0x181cb55f872450d16ae858d532b4e35e50eaa76d'; AVANT = '0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd'; LQTY = '0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c'
EARN = '0x4ce1ac8f43e0e5bd7a346a98af777bf8fbea1981'; EARN_VAULT = '0x014e6da8f283c4af65b2aa0f201438680a004452'
EB_POOL = '0xefc6516323fbd28e80b85a497b65a86243a54b3e'; EB_GAUGE = '0x07a01471fa544d9c6531b631e6a96a79a9ad05e9'
YB_POOL = '0x656341ef90b622c6634e0573772ffb7f3669b9f3'; YB_AMM = '0x5f8d24f33cc5a1d5d1bf012261e6a2214c92233c'; YB_LT = '0x2b9c9f3bdceb5d8e36a4704f08a78fca53343cea'
OUT = {'block': TB}
def one(to, sig, args=''):
    return batch([c(to, sig, args)], tag='ladder')[0]
def u(to, sig, args='', i=0):
    h = one(to, sig, args); return words(h)[i] if h else None
def main():
    struct = {k: json.load(open(RAW / 'http' / f'morpho_v2_structure_{v[0]}.json'))['data']['vaultV2ByAddress'] for k, v in VAULTS.items() if k.startswith('sen')}
    # holder balances
    hb = {}
    for h in LIQ + [LIDO, AVANT, LQTY]:
        hb[h] = {}
        for name, (addr, d) in TOK.items():
            v = u(addr, 'balanceOf(address)', enc_addr(h)); hb[h][name] = v / 10 ** d if v else 0
        for name, (addr, a, sd) in VAULTS.items():
            sh = u(addr, 'balanceOf(address)', enc_addr(h))
            if sh:
                ad = TOK[a][1]
                hb[h][name] = {'shares': sh / 10 ** sd, 'assets': u(addr, 'convertToAssets(uint256)', enc_uint(sh)) / 10 ** ad,
                               'maxWithdraw': (u(addr, 'maxWithdraw(address)', enc_addr(h)) or 0) / 10 ** ad}
    OUT['holders'] = hb
    # V2 vault liquidity
    v2 = {}
    for name, s in struct.items():
        addr, a, sd = VAULTS[name]; ad = TOK[a][1]
        idle = u(TOK[a][0], 'balanceOf(address)', enc_addr(addr)) / 10 ** ad
        ta = u(addr, 'totalAssets()') / 10 ** ad
        adapters = [x['address'].lower() for x in s['adapters']['items']]
        pen = {x: (u(addr, 'forceDeallocatePenalty(address)', enc_addr(x)) or 0) / 1e18 for x in adapters}
        mk = []
        for it in s['caps']['items']:
            dd = it['data']
            if dd['__typename'] != 'MarketV1CapData': continue
            mid = dd['market']['marketId']; adp = dd['adapterAddress'].lower()
            m = words(one(MORPHO, 'market(bytes32)', enc_b32(mid))); p = words(one(MORPHO, 'position(bytes32,address)', enc_b32(mid) + enc_addr(adp)))
            tsa, tss, tba, tbs = m[:4]
            sup = p[0] * tsa / tss / 10 ** ad if tss else 0
            mk.append({'marketId': mid, 'collateral': (dd['market']['collateralAsset'] or {}).get('symbol'), 'supply': tsa / 10 ** ad, 'borrow': tba / 10 ** ad,
                       'liquidity': (tsa - tba) / 10 ** ad, 'vaultSupply': sup, 'vaultWithdrawable': min(sup, (tsa - tba) / 10 ** ad)})
        v2[name] = {'address': addr, 'asset': a, 'idle': idle, 'totalAssets': ta, 'liquidityAdapter': s['liquidityAdapter'], 'forceDeallocatePenalty': pen, 'markets': mk}
    OUT['v2'] = v2
    # Cap cUSD reserves
    h = one(TOK['cUSD'][0], 'assets()'); w = words(h); n = w[1]; assets = [dec_addr(x) for x in w[2:2 + n]]
    cap = {}
    for x in assets:
        sym = dec_string(one(x, 'symbol()')); d = u(x, 'decimals()')
        cap[sym] = {'asset': x, 'availableBalance': u(TOK['cUSD'][0], 'availableBalance(address)', enc_addr(x)) / 10 ** d,
                    'totalSupplies': u(TOK['cUSD'][0], 'totalSupplies(address)', enc_addr(x)) / 10 ** d, 'totalBorrows': u(TOK['cUSD'][0], 'totalBorrows(address)', enc_addr(x)) / 10 ** d}
    OUT['cap'] = {'reserves': cap, 'stcUSD_lockDuration_s': u(VAULTS['stcUSD'][0], 'lockDuration()'), 'cUSD_totalSupply': u(TOK['cUSD'][0], 'totalSupply()') / 1e18}
    # Lido earnUSD
    rep = u('0x827044735c9708a2cf850e7ea37eba43bc786028', 'getReport(address)', enc_addr(TOK['USDT'][0]))
    ea = {'balance': u(EARN, 'balanceOf(address)', enc_addr(LIDO)) / 1e18, 'usdtPerShare': 1e30 / rep, 'totalSupply': u(EARN, 'totalSupply()') / 1e18, 'assets': {}}
    for i in range(u(EARN_VAULT, 'getAssetCount()')):
        x = dec_addr(u(EARN_VAULT, 'assetAt(uint256)', enc_uint(i))); sym = dec_string(one(x, 'symbol()')); d = u(x, 'decimals()')
        qs = []
        for j in range(u(EARN_VAULT, 'getQueueCount(address)', enc_addr(x)) or 0):
            q = dec_addr(u(EARN_VAULT, 'queueAt(address,uint256)', enc_addr(x) + enc_uint(j)))
            isdep = u(EARN_VAULT, 'isDepositQueue(address)', enc_addr(q))
            qs.append({'queue': q, 'isDeposit': bool(isdep), 'assetBalance': (u(x, 'balanceOf(address)', enc_addr(q)) or 0) / 10 ** d})
        ea['assets'][sym] = {'address': x, 'vaultIdle': (u(x, 'balanceOf(address)', enc_addr(EARN_VAULT)) or 0) / 10 ** d, 'queues': qs}
    OUT['earnUSD'] = ea
    # Avant Ethereum wallet ERC4626 receipts
    av = {}
    for name, addr in [('sdBOLD', '0xe92fc3ffd2872d5e3e5d8cb68580605979eac221'), ('eUSDC', '0xa45eac8e33168cefa0b225f500e6d93d43b8f1af')]:
        sh = u(addr, 'balanceOf(address)', enc_addr(AVANT)); asset = dec_addr(u(addr, 'asset()')); d = u(asset, 'decimals()')
        av[name] = {'shares': sh, 'assets': u(addr, 'convertToAssets(uint256)', enc_uint(sh)) / 10 ** d, 'maxWithdraw': (u(addr, 'maxWithdraw(address)', enc_addr(AVANT)) or 0) / 10 ** d,
                    'asset': asset, 'assetSymbol': dec_string(one(asset, 'symbol()'))}
    OUT['avant'] = av
    # Liquity: Curve ebUSD/USDC position
    lp = (u(EB_GAUGE, 'balanceOf(address)', enc_addr(LQTY)) or 0) + (u(EB_POOL, 'balanceOf(address)', enc_addr(LQTY)) or 0)
    OUT['liquity'] = {'lp': lp / 1e18, 'poolSupply': u(EB_POOL, 'totalSupply()') / 1e18,
                      'balances': [u(EB_POOL, 'balances(uint256)', enc_uint(0)) / 1e18, u(EB_POOL, 'balances(uint256)', enc_uint(1)) / 1e6],
                      'coins': [dec_addr(u(EB_POOL, 'coins(uint256)', enc_uint(i))) for i in range(2)],
                      'withdrawOneCoin_ebUSD': (u(EB_POOL, 'calc_withdraw_one_coin(uint256,int128)', enc_uint(lp) + enc_uint(0)) or 0) / 1e18,
                      'withdrawOneCoin_USDC': (u(EB_POOL, 'calc_withdraw_one_coin(uint256,int128)', enc_uint(lp) + enc_uint(1)) or 0) / 1e6}
    # YieldBasis
    st = words(one(YB_AMM, 'get_state()'))
    sup = u(YB_LT, 'totalSupply()')
    OUT['yb'] = {'ammCollateralLP': st[0] / 1e18, 'ammDebt': st[1] / 1e18, 'poolSupply': u(YB_POOL, 'totalSupply()') / 1e18,
                 'poolBalances': [u(YB_POOL, 'balances(uint256)', enc_uint(0)) / 1e18, u(YB_POOL, 'balances(uint256)', enc_uint(1)) / 1e18],
                 'coins': [dec_addr(u(YB_POOL, 'coins(uint256)', enc_uint(i))) for i in range(2)], 'ltSupply': sup / 1e18,
                 'preview_withdraw_all': (lambda v: v / 1e18 if v else None)(u(YB_LT, 'preview_withdraw(uint256)', enc_uint(sup))),
                 'preview_withdraw_99pct': (lambda v: v / 1e18 if v else None)(u(YB_LT, 'preview_withdraw(uint256)', enc_uint(sup * 99 // 100))),
                 'preview_withdraw_50pct': (lambda v: v / 1e18 if v else None)(u(YB_LT, 'preview_withdraw(uint256)', enc_uint(sup // 2)))}
    OUT['ethusd'] = u('0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419', 'latestAnswer()') / 1e8
    json.dump(OUT, open(RAW / 'ladder_T_raw.json', 'w'), indent=1)
    print(json.dumps(OUT, indent=1)[:6000])
if __name__ == '__main__':
    main()
