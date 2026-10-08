"""Reverse lookups for products whose borrowing wallet is a Safe or EOA: Lagoon vault safes (vault.safe() at T, vault list from
app.lagoon.finance/api/vaults) and Upshift/August vault subaccounts, operators and strategists (api.augustdigital.io).
Output raw/.../registries.json: {address: [ {product, source, chain} ]}"""
import json, re
from common import *

def main():
    out = {}
    lag = json.load(open(os.path.join(RAW, 'apis', 'lagoon_vaults.json')))['vaults']
    by = {}
    for v in lag:
        ch = int(v['chain']['id']); by.setdefault(ch, []).append(v)
    for ch, vs in by.items():
        if ch not in L.RPCS: log('lagoon chain not in RPCS', ch, len(vs)); continue
        try:
            b = blk(ch) if ch in (1, 8453, 42161) else None
            r = []
            for v in vs:
                try: r.append(rpc(ch, 'eth_call', [{'to': v['address'], 'data': '0x186f0354'}, hex(b) if ch in (1, 8453, 42161) else 'latest'], retries=8))
                except Exception: r.append(None)
        except Exception as e:
            log('lagoon fail', ch, e); continue
        for v, x in zip(vs, r):
            s = A(x) if x else None
            if s:
                out.setdefault(s.lower(), []).append(dict(product='Lagoon: %s (%s)' % (v['name'], v['symbol']), vault=v['address'], chain=ch,
                                                           asset=v['asset']['symbol'], tvl_usd=v['state'].get('totalAssetsUsd'), source='lagoon safe()'))
    aug = json.load(open(os.path.join(RAW, 'apis', 'august_tokenized_vault.json')))
    for v in aug:
        for fld in ('subaccounts', 'operators', 'eoa_operators', 'hardcoded_strategists', 'iat_traders'):
            for a in set(re.findall(r'0x[0-9a-fA-F]{40}', json.dumps(v.get(fld)))):
                out.setdefault(a.lower(), []).append(dict(product='Upshift: %s' % v.get('vault_name'), vault=v['address'], chain=v.get('chain'),
                                                          tvl_usd=v.get('latest_reported_tvl') or v.get('tvl'), source='august ' + fld))
    save('registries.json', out)
    log('addresses', len(out))

if __name__ == '__main__':
    main()
