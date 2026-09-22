"""Babylon phase-2 delegations (all statuses) of finality providers operated by/for LST & BTC-yield products,
reconstructed into month-end active stake. Heights->dates via mempool.space.
Output: raw/babylon_lst_fp_delegations.json, raw/btc_heights.json, raw/babylon_lst_fp_monthly.json"""
import json, os, sys, time, urllib.request, urllib.parse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import RAW, month_points
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh) Chrome/124'}
def get(u):
    for a in range(5):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
        except Exception as e: print('retry', u[:90], e, flush=True); time.sleep(4 + 4 * a)
    raise SystemExit('fail ' + u)
GROUPS = {  # moniker -> product group
    'Lombard Finance': 'Lombard LBTC', 'Lombard x Figment': 'Lombard LBTC', 'Lombard x Galaxy': 'Lombard LBTC',
    'Lombard x Kiln': 'Lombard LBTC', 'Lombard x P2P.org': 'Lombard LBTC',
    'Solv Protocol': 'SolvBTC LSTs', 'Solv x DeFimans_SBI': 'SolvBTC LSTs', 'Solv x Kudasai': 'SolvBTC LSTs',
    'RockX-Bedrock': 'Bedrock uniBTC', 'BSquared x Bedrock': 'Bedrock uniBTC',
    'PumpBTC': 'PumpBTC', 'lorenzo': 'Lorenzo stBTC', 'Chakra': 'Chakra', 'Allo': 'alloBTC',
    'BSquaredNetwork': 'B2 Buzz', 'BSquared x CertiK': 'B2 Buzz', 'BSquared x P2P.org': 'B2 Buzz',
    'Gate Earn': 'GTBTC (Gate Earn)',
    'Kraken': 'Kraken (exchange staking)', 'Kraken02': 'Kraken (exchange staking)', 'Binance Finality Provider': 'Binance (exchange)',
    'OKX Earn': 'OKX Earn (exchange)', 'Figment': 'Figment (institutional, unattributed)',
}
fps = json.load(open(os.path.join(RAW, 'babylon_fps.json')))
import hashlib
def txid(hexs):
    b = bytes.fromhex(hexs)
    # strip segwit marker/flag + witness for txid: parse minimal (non-witness serialization)
    if b[4] == 0 and b[5] == 1:
        # rebuild without witness: version | inputs | outputs | locktime
        i = 6
        def varint(i):
            v = b[i]
            if v < 0xfd: return v, i + 1
            if v == 0xfd: return int.from_bytes(b[i+1:i+3], 'little'), i + 3
            if v == 0xfe: return int.from_bytes(b[i+1:i+5], 'little'), i + 5
            return int.from_bytes(b[i+1:i+9], 'little'), i + 9
        start = i; n, i = varint(i)
        for _ in range(n):
            i += 36; l, i = varint(i); i += l + 4
        n, i = varint(i)
        for _ in range(n):
            i += 8; l, i = varint(i); i += l
        body = b[start:i]
        raw = b[:4] + body + b[-4:]
    else:
        raw = b
    return hashlib.sha256(hashlib.sha256(raw).digest()).digest()[::-1].hex()
out = []
for f in fps:
    g = GROUPS.get(f['description']['moniker'])
    if not g: continue
    key = None
    while True:
        u = f"https://babylon-rest.publicnode.com/babylon/btcstaking/v1/finality_providers/{f['btc_pk']}/delegations?pagination.limit=200"
        if key: u += '&pagination.key=' + urllib.parse.quote(key)
        d = get(u)
        for grp in d.get('btc_delegator_delegations', []):
            for x in grp['dels']:
                ub = (x.get('undelegation_response') or {}).get('delegator_unbonding_info_response')
                out.append(dict(group=g, fp=f['description']['moniker'], sat=int(x['total_sat']), start=x['start_height'], end=x['end_height'],
                                status=x.get('status_desc'), staking_txid=txid(x['staking_tx_hex']), vout=x.get('staking_output_idx', 0)))
        key = d.get('pagination', {}).get('next_key')
        if not key: break
    print(f['description']['moniker'], len(out), flush=True)
# UNBONDED: unbond height = block height of the tx spending the staking output (mempool.space outspend);
# looked up for delegations >= 2 BTC (>97% of unbonded amount); smaller ones use the midpoint of [start, end] (approximation)
for x in out:
    if x['status'] == 'UNBONDED':
        if x['sat'] >= 2e8 and not x['group'].startswith(('Kraken', 'Binance', 'OKX')):
            try:
                st = get(f"https://mempool.space/api/tx/{x['staking_txid']}/outspend/{x['vout']}")
                x['unbond_height'] = (st.get('status') or {}).get('block_height'); x['unbond_src'] = 'outspend'
            except SystemExit:
                x['unbond_height'] = None
            time.sleep(0.25)
        if not x.get('unbond_height'):
            x['unbond_height'] = (x['start'] + x['end']) // 2; x['unbond_src'] = 'midpoint-approx'
json.dump(out, open(os.path.join(RAW, 'babylon_lst_fp_delegations.json'), 'w'))
# month-end heights
hts = {}
for m, dl, _ in month_points():
    ts = int(datetime.datetime(dl.year, dl.month, dl.day, tzinfo=datetime.UTC).timestamp())
    hts[m] = get(f'https://mempool.space/api/v1/mining/blocks/timestamp/{ts}')['height']; time.sleep(0.2)
json.dump(hts, open(os.path.join(RAW, 'btc_heights.json'), 'w'))
res = {}
for m, h in hts.items():
    agg = {}
    for x in out:
        if x['start'] > h: continue
        if x['status'] == 'ACTIVE' or x['status'] == 'VERIFIED': endh = 10**9 if x['status'] == 'ACTIVE' else -1
        elif x['status'] == 'UNBONDED': endh = x['unbond_height']
        else: endh = x['end']
        if h < endh: agg[x['group']] = agg.get(x['group'], 0) + x['sat'] / 1e8
    res[m] = agg
json.dump(res, open(os.path.join(RAW, 'babylon_lst_fp_monthly.json'), 'w'), indent=1)
for m in res: print(m, {k: round(v) for k, v in sorted(res[m].items())})
