"""Liquid ETH weekly share price vs stETH and weETH (deep dive 2026-10-07).

Reads, at the 105 weekly blocks already used in data/eth/top5/liquid/loop_weekly.csv
(Fridays 23:59:59 UTC, 4 Oct 2024 to T = 2 Oct 2026, block 26,108,081):
  - Accountant 0x0d05...8198 getRate()            (Liquid ETH per share, Ethereum)
  - BoringVault 0xf0bb...416c totalSupply()        (Ethereum shares only; Optimism not read)
  - wstETH stEthPerToken(), weETH getRate()
Archive eth_call via public Tenderly / drpc. Raw responses cached in raw/eth/top5/liquid/weekly_rpc_cache.json.
Output: data/eth/top5/liquid/yield_weekly.csv
"""
import csv, json, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools/top5/kraken'))
from klib import sel, words  # noqa: E402

RPCS = ['https://gateway.tenderly.co/public/mainnet', 'https://eth.drpc.org', 'https://mainnet.gateway.tenderly.co', 'https://rpc.mevblocker.io']
CACHE_P = ROOT / 'raw/eth/top5/liquid/weekly_rpc_cache.json'
CACHE_P.parent.mkdir(parents=True, exist_ok=True)
CACHE = json.loads(CACHE_P.read_text()) if CACHE_P.exists() else {}

ACC = '0x0d05d94a5f1e76c18fbeb7a13d17c8a314088198'
VAULT = '0xf0bb20865277abd641a307ece5ee04e79073416c'
WSTETH = '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'
WEETH = '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee'
CALLS = [('liquid_rate', ACC, 'getRate()'), ('liquid_supply_eth', VAULT, 'totalSupply()'),
         ('wsteth_rate', WSTETH, 'stEthPerToken()'), ('weeth_rate', WEETH, 'getRate()')]


def post(url, payload):
    r = subprocess.run(['curl', '-s', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json',
                        '--data-binary', '@-', url], input=json.dumps(payload).encode(), capture_output=True)
    try:
        return json.loads(r.stdout.decode())
    except Exception:
        return None


def batch(items):
    """items: list of (key, to, data, block). Returns dict key -> hex."""
    out = {}
    todo = []
    for k, to, data, b in items:
        ck = f'{to}|{data}|{b}'
        if ck in CACHE:
            out[k] = CACHE[ck]
        else:
            todo.append((k, to, data, b, ck))
    for s in range(0, len(todo), 10):
        chunk = todo[s:s + 10]
        payload = [{'jsonrpc': '2.0', 'id': i, 'method': 'eth_call',
                    'params': [{'to': to, 'data': data}, hex(b)]} for i, (k, to, data, b, ck) in enumerate(chunk)]
        for attempt in range(8):
            url = RPCS[attempt % len(RPCS)]
            res = post(url, payload)
            if isinstance(res, list) and len(res) == len(chunk) and all('result' in r for r in res):
                for r in res:
                    k, to, data, b, ck = chunk[r['id']]
                    out[k] = CACHE[ck] = r['result']
                break
            print('retry', url, str(res)[:200], flush=True)
            time.sleep(2 + 3 * attempt)
        else:
            raise RuntimeError('rpc failed')
        time.sleep(0.6)
    CACHE_P.write_text(json.dumps(CACHE))
    return out


def main():
    rows = list(csv.DictReader(open(ROOT / 'data/eth/top5/liquid/loop_weekly.csv')))
    weeks = sorted({(r['week_end'], int(r['block'])) for r in rows})
    items = [(f'{w}|{n}', to, '0x' + sel(sig), b) for w, b in weeks for n, to, sig in CALLS]
    res = batch(items)
    out = []
    prev = None
    for w, b in weeks:
        v = {n: words(res[f'{w}|{n}'])[0] / 1e18 for n, _, _ in CALLS}
        row = {'week_end': w, 'utc': f'{w} 23:59:59', 'block': b,
               'liquid_rate': f"{v['liquid_rate']:.12f}", 'wsteth_rate': f"{v['wsteth_rate']:.12f}",
               'weeth_rate': f"{v['weeth_rate']:.12f}", 'liquid_shares_ethereum': f"{v['liquid_supply_eth']:.6f}",
               'liquid_eth_ethereum': f"{v['liquid_supply_eth'] * v['liquid_rate']:.3f}"}
        if prev:
            for k, n in (('liquid_apy_week', 'liquid_rate'), ('steth_apy_week', 'wsteth_rate'), ('weeth_apy_week', 'weeth_rate')):
                row[k] = f"{((v[n] / prev[n]) ** (365 / 7) - 1) * 100:.4f}"
            row['excess_vs_steth_pp'] = f"{float(row['liquid_apy_week']) - float(row['steth_apy_week']):.4f}"
        row['source'] = 'archive eth_call at block: Accountant 0x0d05d94a getRate, vault totalSupply (Ethereum), wstETH stEthPerToken, weETH getRate; APY = weekly ratio compounded to 365 days'
        out.append(row)
        prev = v
    cols = ['week_end', 'utc', 'block', 'liquid_rate', 'wsteth_rate', 'weeth_rate', 'liquid_apy_week', 'steth_apy_week',
            'weeth_apy_week', 'excess_vs_steth_pp', 'liquid_shares_ethereum', 'liquid_eth_ethereum', 'source']
    with open(ROOT / 'data/eth/top5/liquid/yield_weekly.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader()
        for r in out:
            wr.writerow({c: r.get(c, '') for c in cols})
    print(len(out), 'weeks written')


if __name__ == '__main__':
    main()
