"""Lido Earn ETH and stRATEGY weekly share price, loop accounts and stETH (deep dive 2026-10-07).

Weekly blocks: the Friday 23:59:59 UTC blocks of data/eth/top5/liquid/loop_weekly.csv from 7 Nov 2025 (stRATEGY launch
6 Nov 2025) to T = 2 Oct 2026, block 26,108,081. Archive eth_call (public Tenderly, drpc, mevblocker):
  - stRATEGY oracle 0x8a78e6b7 getReport(ETH)  -> shares per ETH; price = 1 / report
  - Earn ETH oracle 0xada1f4c2 getReport(WETH) -> shares per WETH; price = 1 / report (from Feb 2026)
  - Earn ETH ShareManager 0xbbfc8683 totalShares(); stRATEGY ShareManager totalShares()
  - getUserAccountData on Aave Core / Spark for the stRATEGY subvaults (collateral, debt in USD 1e8, HF)
  - rsETH aToken and WETH variable-debt balances of subvault 0xcdfa7efe (the rsETH loop)
  - wstETH stEthPerToken, Kelp rsETHPrice, Chainlink ETH/USD, Aave Core / Spark WETH variable borrow rate
Output: data/eth/top5/lido-earn/yield_weekly.csv and data/eth/top5/lido-earn/loops_weekly.csv
"""
import csv, json, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools/top5/kraken'))
from klib import sel, words, enc_addr, dec_addr  # noqa: E402

RPCS = ['https://eth.drpc.org', 'https://rpc.mevblocker.io', 'https://eth-mainnet.public.blastapi.io', 'https://gateway.tenderly.co/public/mainnet']
CACHE_P = ROOT / 'raw/eth/top5/lido-earn/weekly_rpc_cache.json'
CACHE_P.parent.mkdir(parents=True, exist_ok=True)
CACHE = json.loads(CACHE_P.read_text()) if CACHE_P.exists() else {}
TB = 26108081

STR_ORACLE = '0x8a78e6b7e15c4ae3aeaee3bf0de4f2de4078c1cd'
EARN_ORACLE = '0xada1f4c24603ab2fe5abd35bcd12370e98a20358'
EARN_SM = '0xbbfc8683c8fe8cf73777fede7ab9574935fea0a4'
STR_VAULT = '0x277c6a642564a91ff78b008022d65683cee5ccc5'
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
RSETH = '0xa1290d69c65a6fe4df752f95823fae25cb99e5a7'
WSTETH = '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'
KELP_ORACLE = '0x349a73444b1a310bae67ef67973022020d70020d'
CL_ETHUSD = '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'
POOLS = {'AaveCore': '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2', 'Spark': '0xc13e21b648a5ee794902342038ff3adab66be987'}
SUBS = {'sub1': '0x893aa69fbaa1ee81b536f0fbe3a3453e86290080', 'sub2': '0x181cb55f872450d16ae858d532b4e35e50eaa76d',
        'sub3': '0x9938a09fea37ba681a1bd53d33ddde2debec1da0', 'sub4': '0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7',
        'sub6': '0xcdfa7efe670869c6b6be4375654e0b206ef49c89'}


def post(url, payload):
    r = subprocess.run(['curl', '-s', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json',
                        '--data-binary', '@-', url], input=json.dumps(payload).encode(), capture_output=True)
    try:
        return json.loads(r.stdout.decode())
    except Exception:
        return None


def batch(items):
    out, todo = {}, []
    for k, to, data, b in items:
        ck = f'{to}|{data}|{b}'
        if ck in CACHE:
            out[k] = CACHE[ck]
        else:
            todo.append((k, to, data, b, ck))
    for s in range(0, len(todo), 3):
        chunk = todo[s:s + 3]
        payload = [{'jsonrpc': '2.0', 'id': i, 'method': 'eth_call',
                    'params': [{'to': to, 'data': data}, hex(b)]} for i, (k, to, data, b, ck) in enumerate(chunk)]
        for attempt in range(40):
            url = RPCS[(attempt + s // 3) % len(RPCS)]
            res = post(url, payload)
            ok = isinstance(res, list) and len(res) == len(chunk) and all(
                'result' in r or 'revert' in str(r.get('error', '')).lower() or 'execution' in str(r.get('error', '')).lower() for r in res)
            if ok:
                for r in res:
                    k, to, data, b, ck = chunk[r['id']]
                    v = r.get('result')
                    out[k] = CACHE[ck] = (v if v and v != '0x' else None)
                break
            if attempt % len(RPCS) == len(RPCS) - 1:
                time.sleep(4)
        else:
            raise RuntimeError('rpc failed')
        time.sleep(0.8)
        if s % 60 == 0:
            CACHE_P.write_text(json.dumps(CACHE))
    CACHE_P.write_text(json.dumps(CACHE))
    return out


def c(sig, args=''):
    return '0x' + sel(sig) + args


def main():
    rows = list(csv.DictReader(open(ROOT / 'data/eth/top5/liquid/loop_weekly.csv')))
    weeks = sorted({(r['week_end'], int(r['block'])) for r in rows if r['week_end'] >= '2025-11-07'})
    # resolve tokens at T
    head = batch([('sm', STR_VAULT, c('shareManager()'), TB),
                  ('rs', POOLS['AaveCore'], c('getReserveData(address)', enc_addr(RSETH)), TB),
                  ('we', POOLS['AaveCore'], c('getReserveData(address)', enc_addr(WETH)), TB),
                  ('wes', POOLS['Spark'], c('getReserveData(address)', enc_addr(WETH)), TB)])
    str_sm = dec_addr(words(head['sm'])[0])
    a_rseth = dec_addr(words(head['rs'])[8])
    v_weth = dec_addr(words(head['we'])[10])
    items = []
    for w, b in weeks:
        add = lambda n, to, d: items.append((f'{w}|{n}', to, d, b))
        add('str_report', STR_ORACLE, c('getReport(address)', enc_addr('0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')))
        add('earn_report', EARN_ORACLE, c('getReport(address)', enc_addr(WETH)))
        add('earn_shares', EARN_SM, c('totalShares()'))
        add('str_shares', str_sm, c('totalShares()'))
        add('wsteth', WSTETH, c('stEthPerToken()'))
        add('rseth', KELP_ORACLE, c('rsETHPrice()'))
        add('ethusd', CL_ETHUSD, c('latestAnswer()'))
        add('rate_core', POOLS['AaveCore'], c('getReserveData(address)', enc_addr(WETH)))
        add('rate_spark', POOLS['Spark'], c('getReserveData(address)', enc_addr(WETH)))
        add('sub6_rseth', a_rseth, c('balanceOf(address)', enc_addr(SUBS['sub6'])))
        add('sub6_weth_debt', v_weth, c('balanceOf(address)', enc_addr(SUBS['sub6'])))
        for pn, sn in (('AaveCore', 'sub1'), ('AaveCore', 'sub2'), ('AaveCore', 'sub6'), ('Spark', 'sub2'), ('Spark', 'sub4')):
            add(f'acct|{sn}|{pn}', POOLS[pn], c('getUserAccountData(address)', enc_addr(SUBS[sn])))
    res = batch(items)
    yrows, lrows = [], []
    prev = None
    for w, b in weeks:
        g = lambda n: res.get(f'{w}|{n}')
        v = {}
        sr, er = g('str_report'), g('earn_report')
        v['str_price'] = 1e18 / words(sr)[0] if sr and words(sr)[0] else None
        v['earn_price'] = 1e18 / words(er)[0] if er and words(er)[0] else None
        v['wsteth'] = words(g('wsteth'))[0] / 1e18
        v['rseth'] = words(g('rseth'))[0] / 1e18 if g('rseth') else None
        ethusd = words(g('ethusd'))[0] / 1e8
        es = words(g('earn_shares'))[0] / 1e18 if g('earn_shares') else 0
        ss = words(g('str_shares'))[0] / 1e18 if g('str_shares') else 0
        row = {'week_end': w, 'utc': f'{w} 23:59:59', 'block': b,
               'strategy_price_eth': f"{v['str_price']:.10f}" if v['str_price'] else '',
               'earn_price_eth': f"{v['earn_price']:.10f}" if v['earn_price'] else '',
               'wsteth_rate': f"{v['wsteth']:.12f}",
               'earn_eth_book': f"{es * v['earn_price']:.3f}" if v['earn_price'] else '',
               'strategy_eth_book': f"{ss * v['str_price']:.3f}" if v['str_price'] else '',
               'eth_usd': f'{ethusd:.2f}'}
        if prev:
            for k, n in (('strategy_apy_week', 'str_price'), ('earn_apy_week', 'earn_price'), ('steth_apy_week', 'wsteth')):
                if v[n] and prev[n]:
                    row[k] = f"{((v[n] / prev[n]) ** (365 / 7) - 1) * 100:.4f}"
        row['source'] = 'archive eth_call: Mellow oracles getReport (price = 1/report), ShareManager totalShares, wstETH stEthPerToken, Chainlink ETH/USD; APY = weekly ratio compounded to 365 days'
        yrows.append(row)
        prev = v
        lr = {'week_end': w, 'block': b,
              'aave_weth_borrow_apr': f"{words(g('rate_core'))[4] / 1e27 * 100:.4f}",
              'spark_weth_borrow_apr': f"{words(g('rate_spark'))[4] / 1e27 * 100:.4f}",
              'rseth_rate': f"{v['rseth']:.10f}" if v['rseth'] else '',
              'sub6_rseth_collateral': f"{words(g('sub6_rseth'))[0] / 1e18:.3f}" if g('sub6_rseth') else '',
              'sub6_weth_debt': f"{words(g('sub6_weth_debt'))[0] / 1e18:.3f}" if g('sub6_weth_debt') else ''}
        for pn in POOLS:
            for sn in SUBS:
                h = g(f'acct|{sn}|{pn}')
                ww = words(h) if h else None
                if ww and (ww[0] or ww[1]):
                    lr[f'{sn}_{pn}_coll_eth'] = f'{ww[0] / 1e8 / ethusd:.1f}'
                    lr[f'{sn}_{pn}_debt_eth'] = f'{ww[1] / 1e8 / ethusd:.1f}'
                    lr[f'{sn}_{pn}_hf'] = f'{min(ww[5] / 1e18, 99):.4f}'
        lr['source'] = 'archive eth_call getUserAccountData (USD 1e8 / Chainlink ETH/USD), getReserveData currentVariableBorrowRate, aToken / variable-debt balanceOf'
        lrows.append(lr)
    ycols = ['week_end', 'utc', 'block', 'strategy_price_eth', 'earn_price_eth', 'wsteth_rate', 'strategy_apy_week',
             'earn_apy_week', 'steth_apy_week', 'strategy_eth_book', 'earn_eth_book', 'eth_usd', 'source']
    with open(ROOT / 'data/eth/top5/lido-earn/yield_weekly.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=ycols)
        wr.writeheader()
        [wr.writerow({k: r.get(k, '') for k in ycols}) for r in yrows]
    lcols = ['week_end', 'block', 'aave_weth_borrow_apr', 'spark_weth_borrow_apr', 'rseth_rate', 'sub6_rseth_collateral', 'sub6_weth_debt']
    for pn in POOLS:
        for sn in SUBS:
            if any(f'{sn}_{pn}_hf' in r for r in lrows):
                lcols += [f'{sn}_{pn}_coll_eth', f'{sn}_{pn}_debt_eth', f'{sn}_{pn}_hf']
    lcols.append('source')
    with open(ROOT / 'data/eth/top5/lido-earn/loops_weekly.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=lcols)
        wr.writeheader()
        [wr.writerow({k: r.get(k, '') for k in lcols}) for r in lrows]
    print(len(yrows), 'weeks;', 'subvault tokens', str_sm, a_rseth, v_weth)


if __name__ == '__main__':
    main()
