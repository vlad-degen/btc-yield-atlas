"""Minimal JSON-RPC eth_call helper over public RPC endpoints (no keys)."""
import json, subprocess, time
RPC = {'ethereum': ['https://ethereum-rpc.publicnode.com', 'https://eth.llamarpc.com', 'https://rpc.ankr.com/eth'],
       'base': ['https://base-rpc.publicnode.com', 'https://mainnet.base.org'],
       'arbitrum': ['https://arbitrum-one-rpc.publicnode.com', 'https://arb1.arbitrum.io/rpc'],
       'bsc': ['https://bsc-rpc.publicnode.com', 'https://bsc-dataseed.binance.org'],
       'morph': ['https://rpc-quicknode.morphl2.io', 'https://rpc.morphl2.io'],
       'ink': ['https://rpc-gel.inkonchain.com', 'https://rpc-qnd.inkonchain.com']}
def call(chain, to, data, block='latest'):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call', 'params': [{'to': to, 'data': data}, block]})
    last = None
    for url in RPC[chain] * 2:
        r = subprocess.run(['curl', '-sS', '-m', '40', '-H', 'Content-Type: application/json', '-A', 'Mozilla/5.0', url, '-d', body],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            if 'result' in d:
                return d['result']
            last = d
        except Exception as e:
            last = r.stdout[:200]
        time.sleep(0.5)
    raise RuntimeError(f'rpc failed {chain} {to} {last}')
def addr_arg(a):
    return a.lower().replace('0x', '').rjust(64, '0')
def words(h):
    h = h[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]
def balance_of(chain, token, holder, block='latest'):
    return int(call(chain, token, '0x70a08231' + addr_arg(holder), block), 16)
