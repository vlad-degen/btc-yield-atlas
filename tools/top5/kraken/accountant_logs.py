"""All event logs of the Ink accountant 0x4bb6...f1d6 and the fee PaymentSplitter 0x600d...0a4a via Blockscout v2 API.
Output raw/accountant_logs.json, raw/splitter_logs.json"""
import json, os, subprocess, time
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36'
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
def get(url):
    for t in range(6):
        r = subprocess.run(['curl', '-s', '-m', '60', '-A', UA, url], capture_output=True)
        try: return json.loads(r.stdout.decode())
        except Exception: time.sleep(2 + t)
def all_logs(base, addr):
    out = []; np = None
    while True:
        url = f'{base}/api/v2/addresses/{addr}/logs' + ('?' + '&'.join(f'{k}={v}' for k, v in np.items()) if np else '')
        d = get(url)
        out += d.get('items', [])
        np = d.get('next_page_params')
        if not np: break
        time.sleep(0.3)
    return out
for name, base, addr in [('accountant_logs', 'https://explorer.inkonchain.com', '0x4bb6c416a00561ad6657110b76552c42d55ff1d6'),
                         ('splitter_logs_ink', 'https://explorer.inkonchain.com', '0x600D6e1CAd85d4eDAc4A8EB3922d9Ae48dE00a4A'),
                         ('splitter_logs_eth', 'https://eth.blockscout.com', '0x600D6e1CAd85d4eDAc4A8EB3922d9Ae48dE00a4A')]:
    L = all_logs(base, addr)
    slim = [dict(block=l['block_number'], tx=l['transaction_hash'], ts=l.get('block_timestamp'), topics=l['topics'], data=l['data'],
                 decoded=(l.get('decoded') or {}).get('method_call'), params=[(p['name'], p['value']) for p in ((l.get('decoded') or {}).get('parameters') or [])])
            for l in L]
    json.dump(slim, open(os.path.join(RAW, name + '.json'), 'w'), indent=0)
    import collections
    print(name, len(slim), collections.Counter(x['decoded'].split('(')[0] if x['decoded'] else x['topics'][0][:10] for x in slim))
