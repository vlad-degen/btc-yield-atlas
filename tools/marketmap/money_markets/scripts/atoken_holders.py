"""Top holders of the main BTC aTokens (Aave v3 Ethereum/Base/Arbitrum, Spark) from Blockscout (no key), with contract name /
implementation name, to find map products that supply BTC to these markets. Read 2026-09-23 (current balances).
-> raw/atoken_holders.json"""
import json, os, subprocess, time
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK = {  # (blockscout host, aToken, label, decimals)
    'aave-v3 Ethereum aEthWBTC': ('eth.blockscout.com', '0x5ee5bf7ae06d1be5997a1a72006fe6c607ec6de8', 8),
    'aave-v3 Ethereum aEthcbBTC': ('eth.blockscout.com', '0x5c647ce0ae10658ec44fa4e11a51c96e94efd1dd', 8),
    'aave-v3 Ethereum aEthtBTC': ('eth.blockscout.com', '0x10ac93971cdb1f5c778144084242374473c350da', 18),
    'aave-v3 Ethereum aEthFBTC': ('eth.blockscout.com', '0xcca43cef272c30415866914351fdfc3e881bb7c2', 8),
    'aave-v3 Ethereum aEthLBTC': ('eth.blockscout.com', '0x65906988adee75306021c417a1a3458040239602', 8),
    'aave-v3 Ethereum aEtheBTC': ('eth.blockscout.com', '0x5fefd7069a7d91d01f269dade14526ccf3487810', 8),
    'sparklend Ethereum spWBTC': ('eth.blockscout.com', '0x4197ba364ae6698015ae5c1468f54087602715b2', 8),
    'sparklend Ethereum spcbBTC': ('eth.blockscout.com', '0xb3973d459df38ae57797811f2a1fd061da1bc123', 8),
    'sparklend Ethereum spLBTC': ('eth.blockscout.com', '0xa9d4ecebd48c282a70cfd3c469d6c8f178a5738e', 8),
    'aave-v3 Base aBascbBTC': ('base.blockscout.com', '0xbdb9300b7cde636d9cd4aff00f6f009ffbbc8ee6', 8),
    'aave-v3 Arbitrum aArbWBTC': ('arbitrum.blockscout.com', '0x078f358208685046a11c85e8ad32895ded33a249', 8),
}
def get(url):
    for a in range(5):
        r = subprocess.run(['curl', '-sS', '-m', '60', '-A', 'Mozilla/5.0', url], capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(3 * (a + 1))
    return {}
out = {}
for label, (host, tok, dec) in TOK.items():
    items = []; params = ''
    for page in range(2):  # top 100
        d = get(f'https://{host}/api/v2/tokens/{tok}/holders' + params)
        items += d.get('items', [])
        npp = d.get('next_page_params')
        if not npp:
            break
        params = '?' + '&'.join(f'{k}={v}' for k, v in npp.items())
        time.sleep(0.5)
    rows = []
    for it in items:
        a = it['address']
        impl = [i.get('name') for i in (a.get('implementations') or []) if i.get('name')]
        rows.append(dict(address=a['hash'], name=a.get('name'), is_contract=a.get('is_contract'), impl=impl, btc=int(it['value']) / 10 ** dec))
    out[label] = rows
    print(label, len(rows), round(sum(r['btc'] for r in rows), 1))
    time.sleep(0.5)
json.dump(out, open(os.path.join(D, 'raw', 'atoken_holders.json'), 'w'), indent=0)
