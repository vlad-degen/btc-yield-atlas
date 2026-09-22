"""Weekly snapshot of the BTC carry products and the markets they borrow from.

Appends one row per item to data/monitor.csv (timestamp, item, metric, value), so a spreadsheet or the site can
chart borrow-rate spikes, full caps and share-price growth over time. No API keys needed.

  python3 tools/monitor_carry.py            # append a snapshot
  python3 tools/monitor_carry.py --print    # print only

What it reads:
  - Morpho borrow markets (blue-api.morpho.org): utilization, borrow APY, supply and borrow in USD.
  - Vault share prices by eth_call: Kraken accountant on Ink (getRate), Yield Basis LT pricePerShare on Ethereum.
Add rows to MARKETS / RATES to track more products (for example ether.fi's accountant once its address is confirmed).
"""
import csv, datetime, json, os, sys, urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'monitor.csv')
MORPHO = 'https://blue-api.morpho.org/graphql'
RPC = {'eth': ['https://eth.drpc.org', 'https://rpc.mevblocker.io', 'https://ethereum-rpc.publicnode.com'],
       'ink': ['https://rpc-gel.inkonchain.com', 'https://ink.drpc.org']}
# (label, Morpho market id, chain id)
MARKETS = [
    ('kBTC/RLUSD (Kraken vault legs)', '0x15bb2a6af0c909eed19fb1f2ceeead34ecbdcba626de752c6b09389ee14eec32', 1),
    ('kBTC/PYUSD (Kraken vault legs)', '0xe51f9aaad25d0e755429cf77076b3c2d37cb1228ed81f8a5482f2102c220eef5', 1),
    ('cbBTC/USDT (mHyperBTC leg)', '0x4fe72543c5c95cd6b5f3cb516cd235ba882e2e705fe3424db6f99dfe5811d0d3', 1),
]
# (label, chain, contract, 4-byte selector, decimals)
RATES = [
    ('Kraken Bitcoin Vault share price (BTC)', 'ink', '0x4Bb6C416a00561ad6657110b76552c42d55Ff1d6', '0x679aefce', 8),   # getRate()
    ('Yield Basis yb-WBTC book price per share', 'eth', '0x651D4b8168488FA163D85304662E8278d4c55BAa', '0x99530b06', 18),  # pricePerShare()
    ('Yield Basis yb-cbBTC book price per share', 'eth', '0x722FC3640BA007C3E9867CCdB0dCa59F2e2F29F9', '0x99530b06', 18),
    ('Yield Basis yb-tBTC book price per share', 'eth', '0x771F7290428d830ECd41E980745c327e507823Ec', '0x99530b06', 18),
]


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'content-type': 'application/json', 'user-agent': 'curl/8'})
    return json.load(urllib.request.urlopen(req, timeout=60))


def eth_call(chain, to, data):
    for url in RPC[chain]:
        try:
            r = post(url, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call', 'params': [{'to': to, 'data': data}, 'latest']})
            if r.get('result') not in (None, '0x'):
                return int(r['result'][:66], 16)
        except Exception:
            continue
    return None


def main():
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')
    rows = []
    ids = [m[1] for m in MARKETS]
    q = '{ markets(first:50, where:{uniqueKey_in:%s}){ items{ marketId state{ utilization borrowApy supplyAssetsUsd borrowAssetsUsd } } } }' % json.dumps(ids)
    try:
        items = {i['marketId']: i['state'] for i in post(MORPHO, {'query': q})['data']['markets']['items']}
    except Exception as e:
        items = {}; print('Morpho API failed:', e)
    for label, mid, _ in MARKETS:
        st = items.get(mid)
        if not st: continue
        rows += [(now, label, 'utilization_pct', round(st['utilization'] * 100, 2)), (now, label, 'borrow_apy_pct', round(st['borrowApy'] * 100, 2)),
                 (now, label, 'supply_usd_m', round(st['supplyAssetsUsd'] / 1e6, 2)), (now, label, 'borrow_usd_m', round(st['borrowAssetsUsd'] / 1e6, 2))]
    for label, chain, to, sel, dec in RATES:
        v = eth_call(chain, to, sel)
        if v is not None: rows.append((now, label, 'value', round(v / 10 ** dec, 8)))
    for r in rows: print(' | '.join(map(str, r)))
    if '--print' in sys.argv: return
    new = not os.path.exists(OUT)
    with open(OUT, 'a', newline='') as f:
        w = csv.writer(f)
        if new: w.writerow(['utc', 'item', 'metric', 'value'])
        w.writerows(rows)
    print('appended', len(rows), 'rows to', os.path.relpath(OUT))


if __name__ == '__main__':
    main()
