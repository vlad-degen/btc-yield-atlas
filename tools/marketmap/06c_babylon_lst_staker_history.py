"""Babylon stake of LST / BTC-yield products, month-end 2024-09..2026-09, by STAKER KEY (captures phase-1 and
delegations to non-branded finality providers).
1) staker BTC keys = keys that ever delegated to a product-branded FP (Lombard*, Solv*, Bedrock, PumpBTC, lorenzo,
   Chakra, Allo, BSquared*, Gate Earn) -- Babylon LCD per-FP delegation lists (all statuses);
2) all phase-2 (v2) and phase-1 (v1) delegations of those keys -- staking-api.babylonlabs.io;
3) end of each stake = min(block height of the tx spending the staking output [mempool.space], timelock end);
   spend lookups for stakes >= 2 BTC; smaller non-active stakes use the timelock end (upper-bound style) or midpoint for early unbonds;
4) phase-1 'overflow' stakes excluded (not counted by Babylon).
Output: raw/babylon_lst_staker_monthly.json {month: {group: btc}}, raw/babylon_lst_stakes.json"""
import json, os, sys, time, urllib.request, urllib.parse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import RAW
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh) Chrome/124'}
def get(u, tries=5):
    for a in range(tries):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            print('retry', u[:100], e, flush=True); time.sleep(4 + 4 * a)
        except Exception as e: print('retry', u[:100], e, flush=True); time.sleep(4 + 4 * a)
    return None
GROUPS = {'Lombard Finance': 'Lombard LBTC', 'Lombard x Figment': 'Lombard LBTC', 'Lombard x Galaxy': 'Lombard LBTC', 'Lombard x Kiln': 'Lombard LBTC',
          'Lombard x P2P.org': 'Lombard LBTC', 'Solv Protocol': 'SolvBTC LSTs', 'Solv x DeFimans_SBI': 'SolvBTC LSTs', 'Solv x Kudasai': 'SolvBTC LSTs',
          'RockX-Bedrock': 'Bedrock uniBTC', 'BSquared x Bedrock': 'Bedrock uniBTC', 'PumpBTC': 'PumpBTC', 'lorenzo': 'Lorenzo stBTC', 'Chakra': 'Chakra',
          'Allo': 'alloBTC', 'BSquaredNetwork': 'B2 Buzz', 'BSquared x CertiK': 'B2 Buzz', 'BSquared x P2P.org': 'B2 Buzz', 'Gate Earn': 'GTBTC (Gate Earn)'}
fps = json.load(open(os.path.join(RAW, 'babylon_fps.json')))
pk_amt = collections.defaultdict(lambda: collections.Counter())
for f in fps:
    g = GROUPS.get(f['description']['moniker'])
    if not g: continue
    key = None
    while True:
        u = f"https://babylon-rest.publicnode.com/babylon/btcstaking/v1/finality_providers/{f['btc_pk']}/delegations?pagination.limit=200"
        if key: u += '&pagination.key=' + urllib.parse.quote(key)
        d = get(u) or {}
        for grp in d.get('btc_delegator_delegations', []):
            for x in grp['dels']: pk_amt[g][x['btc_pk']] += int(x['total_sat'])
        key = (d.get('pagination') or {}).get('next_key')
        if not key: break
# keys covering 99% of each group's delegated amount (max 60 keys per group); a key is assigned to one group
pk_group = {}
for g, c in pk_amt.items():
    tot = sum(c.values()); run = 0
    for pk, a in c.most_common(60):
        if pk not in pk_group: pk_group[pk] = g
        run += a
        if run >= 0.99 * tot: break
print({g: sum(1 for p in pk_group.values() if p == g) for g in pk_amt}, flush=True)
stakes = {}
for pk, g in pk_group.items():
    pg = ''
    while True:  # phase-2
        d = get(f'https://staking-api.babylonlabs.io/v2/delegations?staker_pk_hex={pk}' + (f'&pagination_key={pg}' if pg else '')) or {}
        for x in d.get('data', []):
            s = x['delegation_staking']
            if not s.get('start_height'): continue  # pending / not yet included on Bitcoin
            stakes[s['staking_tx_hash_hex']] = dict(group=g, pk=pk, sat=s['staking_amount'], start=s['start_height'], end=s['end_height'],
                                                    state=x.get('state'), vout=s.get('staking_output_idx', 0), phase=2)
        pg = (d.get('pagination') or {}).get('next_key', '')
        if not pg: break
    pg = ''
    while True:  # phase-1
        d = get(f'https://staking-api.babylonlabs.io/v1/staker/delegations?staker_btc_pk={pk}' + (f'&pagination_key={pg}' if pg else '')) or {}
        for x in d.get('data', []):
            h = x['staking_tx_hash_hex']
            if h in stakes or x.get('is_overflow'): continue
            st = x['staking_tx']
            if not st.get('start_height'): continue
            stakes[h] = dict(group=g, pk=pk, sat=x['staking_value'], start=st['start_height'], end=st['start_height'] + st['timelock'],
                             state='P1_' + x.get('state', ''), vout=st.get('output_index', 0), phase=1)
        pg = (d.get('pagination') or {}).get('next_key', '')
        if not pg: break
print('stakes', len(stakes), flush=True)
n = 0
for h, s in stakes.items():
    active = s['state'] in ('ACTIVE',) or s['state'] == 'P1_active'
    if active: s['stop'] = 10**9; continue
    if s['sat'] >= 2e8:
        r = get(f"https://mempool.space/api/tx/{h}/outspend/{s['vout']}") or {}
        sh = (r.get('status') or {}).get('block_height') if r.get('spent') else None
        s['stop'] = min(sh, s['end']) if sh else s['end']; s['stop_src'] = 'outspend' if sh else 'timelock'
        n += 1; time.sleep(0.2)
    else:
        early = any(k in (s['state'] or '') for k in ('EARLY', 'unbond', 'UNBOND'))
        s['stop'] = (s['start'] + s['end']) // 2 if early else s['end']; s['stop_src'] = 'approx'
print('outspend lookups', n, flush=True)
json.dump(stakes, open(os.path.join(RAW, 'babylon_lst_stakes.json'), 'w'))
hts = json.load(open(os.path.join(RAW, 'btc_heights.json')))
res = {}
for m, H in hts.items():
    agg = collections.Counter()
    for s in stakes.values():
        if s['start'] <= H < s['stop']: agg[s['group']] += s['sat'] / 1e8
    res[m] = dict(agg)
json.dump(res, open(os.path.join(RAW, 'babylon_lst_staker_monthly.json'), 'w'), indent=1)
for m in res: print(m, {k: round(v) for k, v in sorted(res[m].items())})
