"""Month-end collateral and dollar debt of the small carry products' lending accounts (archive eth_call, network step).

Reads, at every month-end block of data/eth/economic_questions.json and at the snapshot block 26,108,081:
- Morpho Blue positions (collateral units, borrow shares -> assets) in the dollar market each product used at the snapshot,
  collateral valued at the token's ETH rate at the same block (wstETH stEthPerToken, weETH getRate, rETH getExchangeRate);
- Aave v3 Core accounts: getUserAccountData collateral and debt (USD, 8 decimals) over the Aave oracle WETH price.
Raw replies: raw/eth/netmap-carry-accounts-2026-10-08/reads.json. Output: data/eth/netmap/carry_accounts_monthly.csv.
Avant's Aave v4 spoke and Morpho legs are read here too, and (8 Oct carry sweep) the borrower accounts of YieldNest ynETHx
(Aave Core), 9Summits Flagship ETH, Yearn yvWETH-2 and DAMM Ethereum Fund (Spark): aToken balances and dollar debt. Liquid ETH, Lido Earn, Avant (Aave v3, Spark), YieldBasis and Liquity are measured in data/eth/gap_top5_risk_series.csv; Rocksolid in
data/eth/gap_rocksolid_upshift.json. Run once; 03_build.py reads the CSV offline.
"""
import csv, json, os, time, urllib.request
from lib import OUT, ROOT

RAWDIR = os.path.join(ROOT, 'raw', 'eth', 'netmap-carry-accounts-2026-10-08')
RPCS = ['https://gateway.tenderly.co/public/mainnet', 'https://eth.drpc.org']
MORPHO = '0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
AAVE_POOL = '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
AAVE_ORACLE = '0x54586be62e3c3580375ae3723c145253060ca0c2'
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
RATE = {'0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0': '0x035faf82',   # wstETH stEthPerToken()
        '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee': '0x679aefce',   # weETH getRate()
        '0xae78736cd615f374d3085123a210448e74fc6393': '0xe6aa216c'}   # rETH getExchangeRate()
MORPHO_POS = {  # product -> (account, dollar market at the snapshot)
    'nemo-eth-prime': ('0x90882e7c28ddf0ac1177033a310aeed8eff25e90', '0x7e585a933ffe8443c371b4f8cfeb4430f5f6a14c2f32a898c26662c67a1cb8b8'),
    'sentora-eth': ('0xfb9776de51a24eb75e11110fae659e54b346658f', '0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4'),
    'makina-deth': ('0xd1a2d9df5db842da2ee81075fa441602b2352915', '0xe7e9694b754c4d4f7e21faf7223f6fa71abaeb10296a4c43a54a7977149687d2'),
    'royco-eth': ('0x3d8e2497497a3e29ad5391c08db2a1b3c32598c0', '0xf5c5df23559b0fb56560a7578ea17d81e245153ba64b8132df026c9358864d27'),
    'tau-infinifi': ('0xc50b2d51fd1e2ac67a9c09eaf63c24ea2465c64b', '0xb323495f7e4148be5643a4ea4a8221eef163e4bccfdedc2a6f4696baacbc86cc'),
}
AAVE_ACC = {'vesper-vaeth': ('0x666c80feca6fcd371b0535a9846e2d223cbf1d10', 'B'), 'reservoir-eth': ('0xf6cd9e8415162c8fb3c52676c7ca68812a34f76e', 'B'),
            'sentora-eth': ('0x38752981012591312bb56b1fb319511be12f6e2d', 'A')}  # form of the collateral: B = WETH, A = weETH
# Avant's legs that the 7 Oct archive series (Aave v3, Spark) does not cover: Aave v4 spoke and Morpho weETH/RLUSD
AVANT = '0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd'
AVANT_V4_SPOKE = '0x94e7a5dcbe816e498b89ab752661904e2f56c485'
AVANT_V4_RESERVES = {0: ('WETH', WETH, 18), 1: ('wstETH', '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0', 18), 2: ('weETH', '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee', 18)}
AVANT_V4_DEBT = {7: ('USDC', 6), 8: ('USDT', 6), 10: ('RLUSD', 18), 11: ('USDG', 6), 12: ('frxUSD', 18), 13: ('GHO', 18)}
AVANT_MORPHO = '0xea4bfb18df0ee6bffb7b3f0270899a8adb92ab6b684709634c8276128813cfd4'
# Carry sweep, 8 Oct (data/eth/carry_discovery.csv, research/eth/en/CARRY-DISCOVERY.md): borrower accounts of four open vaults.
# ETH-family collateral from aToken balances (wstETH and weETH at their ETH rate: form A; WETH: form B), dollar debt =
# getUserAccountData total debt less WETH debt (USD, 8 decimals). Aave Core and Spark both price in USD.
SPARK_POOL = '0xc13e21b648a5ee794902342038ff3adab66be987'
WSTETH, WEETH = '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0', '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee'
LENDING_TOKENS = {  # venue -> (pool, {underlying: aToken}, WETH variable-debt token)
    'aave-core': (AAVE_POOL, {WETH: '0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8', WSTETH: '0x0b925ed163218f6662a35e0f0371ac234f9e9371',
                              WEETH: '0xbdfa7b7893081b35fb54027489e2bc7a38275129'}, '0xea51d7853eefb32b6ee06b1c12e6dcca88be0ffe'),
    'spark': (SPARK_POOL, {WETH: '0x59cd1c87501baa753d0b5b5ab5d8416a45cd71db', WSTETH: '0x12b54025c112aa61face2cdb7118740875a566e9',
                           WEETH: '0x3cfd5c0d4acaa8faee335842e4f31159fc76b008'}, '0x2e7576042566f8d6990e07a1b61ad1efd86ae70d'),
}
SWEEP_ACC = {  # product -> borrower account (read on Aave Core and Spark every month; the venue at the snapshot in the comment)
    'yieldnest-ynethx': '0x24d2486f5b2c2c225b6be8b4f72d46349cbf4458',   # ynETHx LVG1 Safe, wstETH against USDe (Aave Core)
    '9summits-eth': '0xc868bfb240ed207449afe71d2ecc781d5e10c85c',       # 9Summits Flagship ETH Safe, weETH against USDS (Spark; Aave Core in Jul 2025)
    'yearn-yvweth2': '0x41cfe42d221a591c6308dcea419015ba8570b380',      # yvWETH-2 lender-borrower strategy, wstETH against USDS (Spark)
    'damm-eth': '0xe39cd9b36b9a86a8227ec3f5159b610bf2a30e69',           # DAMM Ethereum Fund Safe, wstETH against USDC+USDT (Spark)
}


def rpc(method, params):
    for i in range(10):
        try:
            req = urllib.request.Request(RPCS[i % 2], data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode(),
                                         headers={'content-type': 'application/json', 'user-agent': 'Mozilla/5.0'})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if 'error' in r:
                if 'revert' in json.dumps(r['error']).lower() or 'execution' in json.dumps(r['error']).lower():
                    return '0x'
                raise Exception(r['error'])
            return r['result']
        except Exception:
            time.sleep(1 + i)
    raise SystemExit('rpc failed: %s %s' % (method, params))


def call(to, data, block):
    return rpc('eth_call', [{'to': to, 'data': data}, hex(block)])


def w(h, i):
    return int(h[2 + 64 * i: 2 + 64 * (i + 1)], 16)


def blocks():
    eq = json.load(open(os.path.join(ROOT, 'data', 'eth', 'economic_questions.json')))
    out = {h['month']: h['block'] for h in eq['products'][0]['history']}
    out['2026-10-02'] = 26108081
    return out


def main():
    os.makedirs(RAWDIR, exist_ok=True)
    path = os.path.join(RAWDIR, 'reads.json')
    raw = json.load(open(path)) if os.path.exists(path) else {}
    B = blocks()
    params = {}
    for p, (acct, mid) in MORPHO_POS.items():
        key = 'params:' + mid
        if key not in raw:
            raw[key] = call(MORPHO, '0x2c3c9157' + mid[2:], B['2026-10-02'])
        h = raw[key]
        loan, coll = '0x' + h[26:66], '0x' + h[90:130]
        if 'dec:' + loan not in raw:
            raw['dec:' + loan] = call(loan, '0x313ce567', B['2026-10-02'])
        params[p] = (loan, coll, int(raw['dec:' + loan], 16))
    rows = []
    for label, blk in sorted(B.items()):
        def get(key, to, data):
            k = f'{label}:{key}'
            if k not in raw:
                raw[k] = call(to, data, blk)
            return raw[k]
        eth_usd = int(get('oracle:weth', AAVE_ORACLE, '0xb3596f07' + WETH[2:].rjust(64, '0')), 16) / 1e8
        for p, (acct, mid) in MORPHO_POS.items():
            loan, coll, dec = params[p]
            pos = get(f'pos:{p}', MORPHO, '0x93c52062' + mid[2:] + acct[2:].rjust(64, '0'))
            mkt = get(f'mkt:{mid}', MORPHO, '0x5c60e39a' + mid[2:])
            rate = int(get(f'rate:{coll}', coll, RATE[coll]), 16) / 1e18 if coll in RATE else None
            if rate is None:
                raise SystemExit('no ETH rate for collateral ' + coll)
            coll_units = w(pos, 2) / 1e18
            tba, tbs = w(mkt, 2), w(mkt, 3)
            debt = w(pos, 1) * tba / tbs / 10 ** dec if tbs else 0.0
            rows.append(dict(month=label, product=p, venue='morpho', account=acct, market=mid, collateral_eth=round(coll_units * rate, 6),
                             dollar_debt_usd=round(debt, 2), eth_usd=round(eth_usd, 4), block=blk, form='A'))
        # Avant: Aave v4 (reverts before the spoke existed) and Morpho
        coll = debt = 0.0
        for i, (sym, und, dec) in AVANT_V4_RESERVES.items():
            h = get(f'v4s:{i}', AVANT_V4_SPOKE, '0xf1568a89' + hex(i)[2:].rjust(64, '0') + AVANT[2:].rjust(64, '0'))
            px = int(get(f'oracle:{und}', AAVE_ORACLE, '0xb3596f07' + und[2:].rjust(64, '0')), 16) / 1e8
            coll += (int(h, 16) / 10 ** dec * px / eth_usd) if h and h != '0x' else 0.0
        for i, (sym, dec) in AVANT_V4_DEBT.items():
            h = get(f'v4d:{i}', AVANT_V4_SPOKE, '0x9b7172a6' + hex(i)[2:].rjust(64, '0') + AVANT[2:].rjust(64, '0'))
            debt += int(h, 16) / 10 ** dec if h and h != '0x' else 0.0
        rows.append(dict(month=label, product='avant-aveth', venue='aave-v4', account=AVANT, market=AVANT_V4_SPOKE, collateral_eth=round(coll, 6),
                         dollar_debt_usd=round(debt, 2), eth_usd=round(eth_usd, 4), block=blk, form='AB'))
        pos = get('pos:avant', MORPHO, '0x93c52062' + AVANT_MORPHO[2:] + AVANT[2:].rjust(64, '0'))
        mkt = get(f'mkt:{AVANT_MORPHO}', MORPHO, '0x5c60e39a' + AVANT_MORPHO[2:])
        rate = int(get('rate:0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee', '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee', '0x679aefce'), 16) / 1e18
        tba, tbs = w(mkt, 2), w(mkt, 3)
        rows.append(dict(month=label, product='avant-aveth', venue='morpho', account=AVANT, market=AVANT_MORPHO, collateral_eth=round(w(pos, 2) / 1e18 * rate, 6),
                         dollar_debt_usd=round(w(pos, 1) * tba / tbs / 1e18 if tbs else 0.0, 2), eth_usd=round(eth_usd, 4), block=blk, form='A'))
        for p, (acct, fm) in AAVE_ACC.items():
            h = get(f'aave:{p}', AAVE_POOL, '0xbf92857c' + acct[2:].rjust(64, '0'))
            rows.append(dict(month=label, product=p, venue='aave-core', account=acct, market='', collateral_eth=round(w(h, 0) / 1e8 / eth_usd, 6),
                             dollar_debt_usd=round(w(h, 1) / 1e8, 2), eth_usd=round(eth_usd, 4), block=blk, form=fm))
        # carry sweep accounts: one row per collateral form (A = wstETH/weETH, B = WETH); the account's dollar debt on the A row
        for (p, acct), venue in [(x, v) for x in SWEEP_ACC.items() for v in LENDING_TOKENS]:
            pool, atok, vweth = LENDING_TOKENS[venue]
            num = lambda h: int(h, 16) if h and h != '0x' else 0
            bal = {u: num(get(f'bal:{a}:{acct}', a, '0x70a08231' + acct[2:].rjust(64, '0'))) / 1e18 for u, a in atok.items()}
            rate = {u: int(get(f'rate:{u}', u, RATE[u]), 16) / 1e18 for u in (WSTETH, WEETH)}
            h = get(f'ud:{venue}:{acct}', pool, '0xbf92857c' + acct[2:].rjust(64, '0'))
            coll_usd, debt_usd = (w(h, 0) / 1e8, w(h, 1) / 1e8) if h and h != '0x' else (0.0, 0.0)
            weth_debt = num(get(f'bal:{vweth}:{acct}', vweth, '0x70a08231' + acct[2:].rjust(64, '0'))) / 1e18
            dollar = max(0.0, debt_usd - weth_debt * eth_usd)
            a_eth, b_eth = bal[WSTETH] * rate[WSTETH] + bal[WEETH] * rate[WEETH], bal[WETH]
            if coll_usd > 1000 and abs((a_eth + b_eth) * eth_usd / coll_usd - 1) > 0.05:
                print('note: non-ETH collateral or price gap', label, p, round(coll_usd), round((a_eth + b_eth) * eth_usd))
            for fm, c, d in (('A', a_eth, dollar), ('B', b_eth, 0.0)):
                rows.append(dict(month=label, product=p, venue=venue, account=acct, market='', collateral_eth=round(c, 6),
                                 dollar_debt_usd=round(d, 2), eth_usd=round(eth_usd, 4), block=blk, form=fm))
        json.dump(raw, open(path, 'w'), indent=0)
    with open(os.path.join(OUT, 'carry_accounts_monthly.csv'), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    for r in rows:
        if r['month'] in ('2026-09', '2026-10-02') or r['collateral_eth'] > 1:
            print(r['month'], r['product'], r['collateral_eth'], r['dollar_debt_usd'])


if __name__ == '__main__':
    main()
