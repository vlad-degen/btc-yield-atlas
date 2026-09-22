"""Build the BTC-yield market map: current snapshot (2026-09-20), monthly history 2024-09..2026-09, category aggregates,
overlap (double-count) splits, flow/price decomposition and sanity checks.
Inputs: raw/proto/*.json (DefiLlama), raw/pool_charts, raw/yield_pools_selected.json, raw/btc_daily.json,
        raw/babylon_active_delegations.json, raw/babylon_fps.json, raw/babylon_lst_staker_monthly.json (or ..._fp_monthly.json),
        raw/mm_by_project_0920.json, optional inputs/c1_histories.csv (month,product_id,tvl_btc) to merge pending C1 histories.
Outputs (marketmap/): market_map_current.csv, market_map_history_monthly.csv, category_history_monthly.csv,
        category_flows_monthly.csv, c1_pending_proxy_history.csv, raw/build_summary.json"""
import json, os, sys, csv, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from products import P

MP = month_points(); MONTHS = [m for m, _, _ in MP]
CUR = '2026-09'
CATNAME = {'C0': 'Context: BTC collateral / ~0% lending (not yield)', 'C1': 'BTC collateral + USD loan -> strategy (carry)',
           'C2': 'Staking & restaking', 'C3': 'Basis & delta-neutral', 'C4': 'Options selling', 'C5': 'Credit to institutions',
           'C6': 'LP, emissions, farming, DeFi vaults', 'EXCL': 'Excluded (wrapper/bridge/venue/USD-yield)'}
YIELD_CATS = ('C1', 'C2', 'C3', 'C4', 'C5', 'C6')
AGG_KEYS = {'borrowed', 'staking', 'pool2', 'vesting', 'offers', 'treasury', 'doublecounted', 'liquidstaking', 'dcAndLsOverlap'}
SUFFIX = ('-borrowed', '-staking', '-pool2', '-vesting', '-offers', '-treasury')

def cat_at(p, m):
    c = p['cat']
    if isinstance(c, str): return c
    cur = None
    for k in sorted(c):
        if m >= k: cur = c[k]
    return cur

# ---------- per-product monthly values ----------
def chain_keys(slug, borrowed):
    d = load(slug); ks = []
    for k in d['chainTvls']:
        if k in AGG_KEYS: continue
        if k.endswith(SUFFIX):
            if borrowed and k.endswith('-borrowed'): ks.append(k)
            continue
        ks.append(k)
    return ks

_ser_cache = {}
def tok_series(slug, key):
    if (slug, key) not in _ser_cache: _ser_cache[(slug, key)] = series_tokens(slug, key)
    return _ser_cache[(slug, key)]

def dl_value(p, date, back=3):
    """(usd, breakdown{sym: usd}, method) of BTC part at DefiLlama date"""
    slug = p['slug']; only = p.get('only'); excl = set(p.get('excl', set()))
    if p['src'] == 'dltotal':
        v, _ = pick(series_total(slug), date, back)
        if v is None: return 0.0, {}, 'total'
        return v, {'_TOTAL': v}, 'total'
    ecs = p.get('excl_chain_sym', set())
    if not p.get('borrowed') and not ecs:
        t, _ = pick(tok_series(slug, None), date, back)
        usd, br = btc_part(t, only=only, exclude=excl)
        return usd, br, 'token-breakdown'
    tot = 0.0; brall = collections.Counter()
    for k in chain_keys(slug, p.get('borrowed')):
        t, _ = pick(tok_series(slug, k), date, back)
        base = k.split('-borrowed')[0]
        ex = excl | {s for (c, s) in ecs if c == base}
        usd, br = btc_part(t, only=only, exclude=ex)
        tot += usd; brall.update(br)
    return tot, dict(brall), 'token-breakdown' + (' (+borrowed)' if p.get('borrowed') else '')

POOLS = json.load(open(os.path.join(RAW, 'yield_pools_selected.json')))
def pool_series(pid):
    f = os.path.join(RAW, 'pool_charts', pid + '.json')
    if not os.path.exists(f): return {}
    out = {}
    for r in json.load(open(f))['data']:
        out[datetime.date.fromisoformat(r['timestamp'][:10])] = r['tvlUsd'] or 0
    return out
POOL_BY_PRODUCT = collections.defaultdict(list)
PNAME2ID = {'Midas mHyperBTC (Hyperithm)': 'midas-mhyperbtc', 'Midas mRe7BTC (Re7)': 'midas-mre7btc', 'Midas mBTC': 'midas-mbtc',
            'Tesseract TESS wBTC debt-loop vaults (IPOR Fusion)': 'tesseract', 'BTCD Labs / TAU BTC dollar-carry vaults (IPOR Fusion)': 'btcd-carry',
            'ether.fi eBTC': 'etherfi-ebtc'}
for x in POOLS: POOL_BY_PRODUCT[PNAME2ID[x['product']]].append(x['pool'])
def pools_value(pid_list, date):
    tot = 0.0; ok = False
    for pid in pid_list:
        s = pool_series(pid)
        v, _ = pick(s, date, 5)
        if v is not None: tot += v; ok = True
    return (tot if ok else 0.0)

# month -> (defillama date, pool date, price)
PT = {m: (dl, pd, price(pd)) for m, dl, pd in MP}

vals = {}   # id -> month -> dict(usd, btc, br, method)
for p in P:
    vals[p['id']] = {}
    for m in MONTHS:
        dl, pd, px = PT[m]
        if m == CUR: dl = SNAP; pd = SNAP; px = PRICE_SNAP
        rec = None
        if p['src'] in ('dl', 'dltotal'):
            if p['hist'] == 'none' and m != CUR: continue
            usd, br, meth = dl_value(p, dl, back=0 if m == CUR else 3)
            if m == CUR and usd == 0.0:  # snapshot day missing -> previous day
                usd, br, meth = dl_value(p, dl, back=1)
            for q in p.get('minus_pools', []):
                usd = max(0.0, usd - pools_value(POOL_BY_PRODUCT[q], pd))
            rec = dict(usd=usd, br=br, method=meth)
        elif p['src'] == 'pools':
            usd = pools_value(POOL_BY_PRODUCT[p['id']], pd)
            rec = dict(usd=usd, br={}, method='yields-pools')
        elif p['src'] in ('fixed', 'core'):
            if m != CUR: continue
            rec = dict(usd=p['btc'] * PRICE_SNAP, br={}, method={'fixed': 'disclosed' if p.get('offchain') else 'on-chain', 'core': 'on-chain API'}[p['src']])
            if p['id'] == 'two-prime-axiom': rec['method'] = 'disclosed'
        elif p['src'] == 'blank':
            if m != CUR: continue
            rec = dict(usd=None, br={}, method='unknown')
        rec['btc'] = None if rec['usd'] is None else rec['usd'] / px
        rec['price'] = px
        vals[p['id']][m] = rec

# optional merge of externally produced C1 histories
EXT = os.path.join(D, 'inputs', 'c1_histories.csv')
ext_merged = []
if os.path.exists(EXT):
    for r in csv.DictReader(open(EXT)):
        pid, m, b = r['product_id'], r['month'], float(r['tvl_btc'])
        if pid in vals and m != CUR:
            vals[pid][m] = dict(usd=b * PT[m][2], btc=b, br={}, method='on-chain (merged)', price=PT[m][2]); ext_merged.append((pid, m))

# products nested inside another row's DefiLlama balance: subtract them from the container (e.g. ether.fi Liquid BTC inside Veda)
for p in P:
    for q in p.get('minus_ids', []):
        for m, rec in vals[p['id']].items():
            o = vals.get(q, {}).get(m)
            if rec.get('usd') and o and o.get('btc'):
                rec['btc'] = max(0.0, rec['btc'] - o['btc']); rec['usd'] = rec['btc'] * rec['price']; rec['method'] = rec['method'] + ' (minus ' + q + ')'

PBY = {p['id']: p for p in P}

# ---------- nesting (LST held inside other listed products) ----------
ISSUER = {'LBTC': 'lombard-lbtc', 'BTCOC': 'lombard-lbtc', 'LBTCV': 'lombard-vaults', 'UNIBTC': 'bedrock-unibtc', 'BRBTC': 'bedrock-unibtc',
          'UNIBRBTC': 'bedrock-unibtc', 'PUMPBTC': 'pumpbtc', 'SOLVBTC.BBN': 'solvbtc-lsts', 'SOLVBTC.CORE': 'solvbtc-lsts', 'XSOLVBTC': 'solvbtc-lsts',
          'SOLVBTC.TRADING': 'solv-basis-trading', 'BFBTC': 'bitfi-basis', 'GTBTC': 'gtbtc', 'MHYPERBTC': 'midas-mhyperbtc', 'MRE7BTC': 'midas-mre7btc',
          'EBTC': 'etherfi-ebtc', 'AVBTC': 'avant-avbtc', 'SAVBTC': 'avant-avbtc', 'STBTC': 'lorenzo-stbtc', 'ASBTC': 'aster-asbtc'}

FAMILY = {'bitfi-basis': 'bfbtc', 'bitfi-btc': 'bfbtc'}
MIN_SPLIT = 5e4  # overlaps below $50k are not split out (negligible)
def counted(pid, m):
    p = PBY[pid]; v = vals[pid].get(m)
    return v is not None and v.get('usd') and p['net'] == 1 and not p['memo'] and cat_at(p, m) in YIELD_CATS

# Babylon LST overlap (BTC) by product, per month
fpmon = None
for f in ('babylon_lst_staker_monthly.json', 'babylon_lst_fp_monthly.json'):
    if os.path.exists(os.path.join(RAW, f)): fpmon = json.load(open(os.path.join(RAW, f))); FPSRC = f; break
GROUP2PID = {'Lombard LBTC': 'lombard-lbtc', 'SolvBTC LSTs': 'solvbtc-lsts', 'Bedrock uniBTC': 'bedrock-unibtc', 'PumpBTC': 'pumpbtc',
             'Lorenzo stBTC': 'lorenzo-stbtc', 'Chakra': 'chakra', 'alloBTC': 'allobtc', 'B2 Buzz': 'buzz-farming', 'GTBTC (Gate Earn)': 'gtbtc'}
FPMONIKER2GROUP = {'Lombard Finance': 'Lombard LBTC', 'Lombard x Figment': 'Lombard LBTC', 'Lombard x Galaxy': 'Lombard LBTC', 'Lombard x Kiln': 'Lombard LBTC',
                   'Lombard x P2P.org': 'Lombard LBTC', 'Solv Protocol': 'SolvBTC LSTs', 'Solv x DeFimans_SBI': 'SolvBTC LSTs', 'Solv x Kudasai': 'SolvBTC LSTs',
                   'RockX-Bedrock': 'Bedrock uniBTC', 'BSquared x Bedrock': 'Bedrock uniBTC', 'PumpBTC': 'PumpBTC', 'lorenzo': 'Lorenzo stBTC', 'Chakra': 'Chakra',
                   'Allo': 'alloBTC', 'BSquaredNetwork': 'B2 Buzz', 'BSquared x CertiK': 'B2 Buzz', 'BSquared x P2P.org': 'B2 Buzz', 'Gate Earn': 'GTBTC (Gate Earn)'}
fpname = {f['btc_pk']: f['description']['moniker'] for f in json.load(open(os.path.join(RAW, 'babylon_fps.json')))}
act = json.load(open(os.path.join(RAW, 'babylon_active_delegations.json')))
bab_cur_groups = collections.Counter(); bab_cur_fp = collections.Counter()
for x in act:
    mon = fpname.get(x['fp_btc_pk_list'][0], 'unknown'); b = int(x['total_sat']) / 1e8
    bab_cur_fp[mon] += b
    if mon in FPMONIKER2GROUP: bab_cur_groups[FPMONIKER2GROUP[mon]] += b

def babylon_overlap(m):
    """dict pid -> overlap BTC (Babylon stake attributable to a listed product), capped by product gross and Babylon gross"""
    raw = bab_cur_groups if m == CUR else collections.Counter(fpmon.get(m, {}))
    out = {}
    bgross = (vals['babylon'].get(m) or {}).get('btc') or 0.0
    for g, b in raw.items():
        pid = GROUP2PID.get(g)
        if not pid or not counted(pid, m): continue
        cap = vals[pid][m]['btc'] or 0.0
        out[pid] = min(b, cap)
    s = sum(out.values())
    if s > bgross and s > 0:
        out = {k: v * bgross / s for k, v in out.items()}
    return out

def nesting(m):
    """returns (nested_usd[issuer] -> {holder: usd}, symb_in_lvaults_usd)"""
    nested = collections.defaultdict(lambda: collections.Counter())
    lv = vals['lombard-vaults'].get(m) or {}
    btcoc = lv.get('br', {}).get('BTCOC', 0.0) if counted('lombard-vaults', m) else 0.0
    sym = vals['symbiotic'].get(m) or {}
    symb_lbtc = sym.get('br', {}).get('LBTC', 0.0) if counted('symbiotic', m) else 0.0
    symb_in_lv = min(symb_lbtc, btcoc)
    for p in P:
        h = p['id']
        if not counted(h, m): continue
        for s, u in (vals[h][m].get('br') or {}).items():
            iss = ISSUER.get(s)
            if not iss or iss == h or iss not in vals or not counted(iss, m): continue
            if FAMILY.get(h) and FAMILY.get(h) == FAMILY.get(iss): continue  # same token on another chain, not a holder
            if h == 'symbiotic' and s == 'LBTC': u = u - symb_in_lv
            if u > 0: nested[iss][h] += u
    return nested, symb_in_lv

# ---------- rows per month (with splits) ----------
def rows_for_month(m):
    rows = []
    nested, symb_in_lv = nesting(m)
    bov = babylon_overlap(m) if vals['babylon'].get(m) else {}
    px = vals['babylon'][m]['price'] if vals['babylon'].get(m) else PT[m][2]
    for p in P:
        v = vals[p['id']].get(m)
        if v is None: continue
        c = cat_at(p, m)
        base = dict(id=p['id'], product=p['product'], slug=p['slug'], cat=c, sub=p['sub'], method=v['method'], offchain=p['offchain'], memo=p['memo'],
                    net=p['net'], note='', price=v['price'])
        usd = v['usd']
        if usd is None:
            rows.append(dict(base, usd=None, btc=None)); continue
        split = []
        if p['id'] == 'babylon' and bov and sum(bov.values()) * v['price'] >= MIN_SPLIT:
            ov_btc = sum(bov.values()); ov_usd = min(usd, ov_btc * v['price'])
            parts = ', '.join(f"{PBY[k]['product']} {b:,.0f}" for k, b in sorted(bov.items(), key=lambda kv: -kv[1]) if b >= 0.5)
            split.append((f"{p['product']} - stake attributed to listed LSTs/products", ov_usd, 0, f'counted in: {parts} BTC'))
        if p['id'] in nested and sum(nested[p['id']].values()) >= MIN_SPLIT:
            tot = sum(nested[p['id']].values()); tot = min(tot, usd)
            parts = ', '.join(f"{PBY[h]['product']} ${u/1e6:,.1f}M" for h, u in nested[p['id']].most_common() if u >= 5e4)
            split.append((f"{p['product']} - held inside other listed products", tot, 0, 'counted at holder level: ' + parts))
        if p['id'] == 'symbiotic' and symb_in_lv >= MIN_SPLIT:
            split.append((f"{p['product']} - LBTC credit cover for Lombard BTCe", min(symb_in_lv, usd), 0, 'counted in Lombard Vaults (BTCOC)'))
        rest = usd - sum(s[1] for s in split)
        if split:
            for name, u, net, note in split:
                rows.append(dict(base, product=name, usd=u, btc=u / v['price'], net=0, note=note, split='overlap'))
            rows.append(dict(base, product=p['product'] + (' - direct / other holders' if p['id'] != 'babylon' else ' - other stakers (Kraken, Binance, OKX, Figment, direct)'),
                             usd=max(rest, 0.0), btc=max(rest, 0.0) / v['price'], split='net-remainder'))
        else:
            rows.append(dict(base, usd=usd, btc=v['btc']))
    return rows

ALL = {m: rows_for_month(m) for m in MONTHS}

def in_gross(r): return r['cat'] in YIELD_CATS and not r['memo'] and r['usd'] is not None
def in_net(r): return in_gross(r) and r['net'] == 1

# ---------- current CSV ----------
DC_NOTE = {
    'babylon': 'Babylon split by finality-provider attribution (Babylon LCD active delegations 2026-09-21).',
    'lombard-lbtc': 'LBTC -> LBTCv/BTCe (Lombard Vaults) and other holders counted once at the holder; LBTC in Babylon is ~0 (42 BTC).',
    'gtbtc': 'GTBTC BTC is staked in Babylon (Gate Earn FP); the Babylon row excludes it.',
    'bedrock-unibtc': 'uniBTC deposited in Symbiotic/Mellow/others counted at holder; 153 BTC Babylon stake excluded from Babylon.',
    'kraken-vault': 'Veda (Ink KBTC) and Sentora-curator KBTC are the same vault: excluded there. Possible overlap with Kraken Babylon stake not verifiable.',
    'bitget-bgbtc-earn': 'Same as DefiLlama aera-v3 BGBTC; bgBTC wrapper excluded.',
    'etherfi-liquid-btc': 'ether.fi-liquid WBTC (DefiLlama) covers the same vault.',
    'symbiotic': 'uniBTC/LBTC inside Symbiotic counted here (holder); 582.8 LBTC = Lombard BTCe credit cover counted in Lombard Vaults.',
    'lombard-vaults': 'Holds LBTC/BTCOC (LBTC-backed): counted here, removed from LBTC.',
    'syntetika': 'Same product as the off-chain Syntetika memo row (not double counted).',
    'solv-basis-trading': 'SolvBTC.TRADING supply; base SolvBTC wrapper excluded; no overlap with SolvBTC LSTs (different token supply).',
    'ailayer-farm': 'Presumed same BTC as bfBTC on AILayer.',
    'core-staking': 'May overlap b14g (partly Core-staked) and Maple BTC Yield: unmeasured; included in net (range in overlap.md).',
    'endur': 'Endur LSTs delegate into Starknet BTC Staking: counted there.',
    'hyperbeat-earn': 'Same hbBTC balance as the UBTC in Upshift: counted in Upshift.',
    'royco-v1': 'Gross only: campaign wrapper; deposits sit in destination vaults.',
    'yieldnest': 'Gross only: ynBTCk deposits are restaked in Kernel (counted there).',
}
cur_rows = ALL[CUR]
extra = []
# off-chain / memo rows
extra.append(dict(id='coinbase-cbyf', product='Coinbase Bitcoin Yield Fund (CBYF)', slug='-', cat='C3', sub='Off-chain cash-and-carry fund', usd=None, btc=None,
                  method='disclosed', offchain=1, memo=0, net=0, note='AUM not disclosed (blank)'))
extra.append(dict(id='starboard-sygnum', product='Starboard Sygnum BTC Alpha Fund', slug='-', cat='C3', sub='Off-chain market-neutral overlay fund', usd=750 * PRICE_SNAP, btc=750.0,
                  method='disclosed', offchain=1, memo=0, net=1, note='"750+ BTC" disclosed: lower bound'))
extra.append(dict(id='syntetika-memo', product='Syntetika hBTC disclosed AUM (memo)', slug='syntetika', cat='C3', sub='Memo: same as on-chain Syntetika row', usd=16.1e6, btc=16.1e6 / PRICE_SNAP,
                  method='disclosed', offchain=1, memo=1, net=0, note='memo only: ~$16.1M disclosed vs $15.1M on-chain (DefiLlama); counted once via the on-chain row'))
extra.append(dict(id='lombard-cc-memo', product='Lombard LBTC covered call (Bitwise) (memo)', slug='lombard-lbtc', cat='C4', sub='Memo: already counted via LBTC', usd=None, btc=None,
                  method='disclosed', offchain=1, memo=1, net=0, note='memo only: the covered-call program runs on LBTC collateral already counted in the LBTC row'))
mm = json.load(open(os.path.join(RAW, 'mm_by_project_0920.json')))
mm_tot = sum(v['d20'] for v in mm.values()); mm_adj = mm_tot - mm.get('zest-v2', {}).get('d20', 0) - mm.get('accountable', {}).get('d20', 0)
extra.append(dict(id='c0-money-markets', product='Money-market BTC collateral (Aave, Morpho, Spark, Venus, Compound, JustLend, Kamino, ...)', slug='(62 lending/CDP projects)',
                  cat='C0', sub='Context: BTC collateral, ~0% supply APY', usd=mm_adj, btc=mm_adj / PRICE_SNAP, method='yields-pools', offchain=0, memo=0, net=0,
                  note=f'DefiLlama yields pools 09-20: ${mm_tot/1e9:.2f}B less Zest v2 and Accountable (classified C6/C5 here)'))
JUST = {p['id']: p['just'] for p in P}
JUST.update({'coinbase-cbyf': 'Spot BTC vs derivatives (cash-and-carry); USCBYF adds private credit.', 'starboard-sygnum': 'Directional BTC + market-neutral overlay (perps, futures, options).',
             'syntetika-memo': 'See on-chain Syntetika row.', 'lombard-cc-memo': 'See LBTC row.', 'c0-money-markets': 'Plain collateral in money markets earns ~0%: context only (plan 0.1).'})
SRC = {p['id']: p.get('source', '') for p in P}
FLAG = {p['id']: p.get('flag', '') for p in P}
def source_of(r):
    if SRC.get(r['id']): return SRC[r['id']]
    if r['method'].startswith('token') or r['method'] == 'total': return f"DefiLlama /protocol/{r['slug']} (2026-09-20 00:00 UTC point)"
    if r['method'] == 'yields-pools': return 'DefiLlama yields pools (2026-09-20)'
    return {'starboard-sygnum': 'fund disclosures (dossier)', 'coinbase-cbyf': 'Coinbase disclosures (AUM not disclosed)', 'syntetika-memo': 'Syntetika/Hilbert disclosures',
            'lombard-cc-memo': 'Lombard/Bitwise announcement', 'c0-money-markets': 'DefiLlama yields pools, BTC-symbol pools of lending/CDP projects (market-data/mm_by_project.json)'}.get(r['id'], '')
hdr = ['product', 'slug', 'category_code', 'category_name', 'subcategory', 'tvl_usd', 'tvl_btc', 'source', 'method', 'offchain', 'double_count_note', 'include_net', 'justification']
out_rows = []
for r in cur_rows + extra:
    if r['usd'] is not None and r['usd'] < 5e4 and r['cat'] not in ('C1',) and r.get('split') is None and r['id'] not in ('lorenzo-stbtc', 'acre', 'satlayer'):
        continue  # drop dust rows (<$50k) except named C1/known products
    note = '; '.join(x for x in [r.get('note', ''), DC_NOTE.get(r['id'], '') if r.get('split') != 'overlap' else '', FLAG.get(r['id'], '')] if x)
    inc = 1 if in_net(r) else 0
    out_rows.append([r['product'], r['slug'], r['cat'], CATNAME[r['cat']], r['sub'], '' if r['usd'] is None else round(r['usd']), '' if r['btc'] is None else round(r['btc'], 2),
                     source_of(r), r['method'], r['offchain'], note, inc, JUST.get(r['id'], '')])
order = {'C1': 1, 'C2': 2, 'C3': 3, 'C4': 4, 'C5': 5, 'C6': 6, 'C0': 7, 'EXCL': 8}
out_rows.sort(key=lambda x: (order[x[2]], -(x[5] or 0) if x[5] != '' else 0))
with open(os.path.join(D, 'market_map_current.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(out_rows)

# ---------- history CSV + category aggregates ----------
hist_rows = []; cat = collections.defaultdict(lambda: collections.defaultdict(float))
for m in MONTHS:
    for r in ALL[m]:
        if r['usd'] is None: continue
        merged_ids = {e[0] for e in ext_merged}
        if PBY.get(r['id'], {}).get('hist') in ('none', 'pending') and not any(e[0] == r['id'] and e[1] == m for e in ext_merged) \
                and not (m == CUR and r['id'] in merged_ids):
            continue  # current-only rows are not part of the history (unless a merged history exists: then the current value closes it)
        if r['cat'] not in YIELD_CATS: continue
        if r['usd'] < 1 and r.get('split') is None: continue
        hist_rows.append([m, r['product'], r['cat'], round(r['usd']), round(r['btc'], 3), 1 if in_net(r) else 0])
        cat[(m, r['cat'])]['usd_g'] += r['usd']; cat[(m, r['cat'])]['btc_g'] += r['btc']
        if in_net(r): cat[(m, r['cat'])]['usd_n'] += r['usd']; cat[(m, r['cat'])]['btc_n'] += r['btc']
with open(os.path.join(D, 'market_map_history_monthly.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['month', 'product', 'category_code', 'tvl_usd', 'tvl_btc', 'include_net']); w.writerows(hist_rows)
cat_rows = []; leaders = {}
for m in MONTHS:
    totn = sum(cat[(m, c)]['usd_n'] for c in YIELD_CATS)
    for c in YIELD_CATS:
        a = cat[(m, c)]
        cat_rows.append([m, c, round(a['usd_g']), round(a['btc_g'], 2), round(a['usd_n']), round(a['btc_n'], 2), round(a['usd_n'] / totn, 4) if totn else 0])
    leaders[m] = max(YIELD_CATS, key=lambda c: cat[(m, c)]['usd_n'])
with open(os.path.join(D, 'category_history_monthly.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['month', 'category_code', 'tvl_usd_gross', 'tvl_btc_gross', 'tvl_usd_net', 'tvl_btc_net', 'share_net']); w.writerows(cat_rows)
changes = [(MONTHS[i], leaders[MONTHS[i - 1]], leaders[MONTHS[i]]) for i in range(1, len(MONTHS)) if leaders[MONTHS[i]] != leaders[MONTHS[i - 1]]]

# ---------- flows vs price (net basis, midpoint decomposition) ----------
flow_rows = []; cum = collections.defaultdict(lambda: collections.Counter())
for i in range(1, len(MONTHS)):
    m0, m1 = MONTHS[i - 1], MONTHS[i]
    p0, p1 = PT[m0][2], (PRICE_SNAP if m1 == CUR else PT[m1][2])
    for c in list(YIELD_CATS) + ['ALL']:
        if c == 'ALL':
            b0 = sum(cat[(m0, k)]['btc_n'] for k in YIELD_CATS); b1 = sum(cat[(m1, k)]['btc_n'] for k in YIELD_CATS)
            u0 = sum(cat[(m0, k)]['usd_n'] for k in YIELD_CATS); u1 = sum(cat[(m1, k)]['usd_n'] for k in YIELD_CATS)
        else:
            b0, b1, u0, u1 = cat[(m0, c)]['btc_n'], cat[(m1, c)]['btc_n'], cat[(m0, c)]['usd_n'], cat[(m1, c)]['usd_n']
        flow_usd = (b1 - b0) * (p0 + p1) / 2; price_usd = (p1 - p0) * (b0 + b1) / 2
        flow_rows.append([m1, c, round(u1 - u0), round(b1 - b0, 2), round(flow_usd), round(price_usd), round(u1 - u0 - flow_usd - price_usd)])
        cum[c].update(dict(d_usd=u1 - u0, flow_btc=b1 - b0, flow_usd=flow_usd, price_usd=price_usd))
with open(os.path.join(D, 'category_flows_monthly.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['month', 'category_code', 'delta_usd_net', 'net_flow_btc', 'net_flow_usd', 'price_effect_usd', 'residual_usd']); w.writerows(flow_rows)

# ---------- C1 pending proxy histories (DefiLlama) ----------
prox = []
for m in MONTHS:
    dl, pd, px = PT[m]
    if m == CUR: dl, px = SNAP, PRICE_SNAP
    k = pick(series_tokens('veda', 'Ink', units=True), dl, 3)[0] or {}
    b = pick(series_tokens('aera-v3', None, units=True), dl, 3)[0] or {}
    e = pick(series_tokens('ether.fi-liquid', None, units=True), dl, 3)[0] or {}
    prox.append([m, round(k.get('KBTC', 0), 2), round(b.get('BGBTC', 0), 2), round(sum(v for s, v in e.items() if btc_weight(s) == 1), 2)])
with open(os.path.join(D, 'c1_pending_proxy_history.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['month', 'kraken_vault_proxy_veda_ink_kbtc_units', 'bitget_earn_proxy_aera_v3_bgbtc_units', 'etherfi_liquid_proxy_btc_units_all_vaults']); w.writerows(prox)

# ---------- methodology-jump detection (daily, DefiLlama BTC part) ----------
jumps = []
for p in P:
    if p['src'] not in ('dl', 'dltotal') or cat_at(p, CUR) in ('EXCL', 'C0'): continue
    s = series_total(p['slug']) if p['src'] == 'dltotal' else None
    tk = None if s is not None else tok_series(p['slug'], None)
    days = [d for d in sorted((s or tk).keys()) if datetime.date(2024, 8, 31) <= d <= SNAP]
    ser = [(d, s[d] if s is not None else btc_part(tk[d], only=p.get('only'), exclude=set(p.get('excl', set())))[0]) for d in days]
    for i in range(1, len(ser) - 6):
        (d0, v0), (d1, v1), (d6, v6) = ser[i - 1], ser[i], ser[i + 6]
        if v0 <= 0 or abs(v1 - v0) < 25e6 or abs(v1 / v0 - 1) < 0.35: continue
        if abs(v6 / v0 - 1) < 0.35: continue  # reverted within a week -> data glitch, not a re-scope
        bp0, bp1 = btc_prices().get(d0.isoformat()), btc_prices().get(d1.isoformat())
        if bp0 and bp1 and abs(bp1 / bp0 - 1) > 0.1: continue
        jumps.append(dict(product=p['product'], slug=p['slug'], date=d1.isoformat(), from_usd=round(v0), to_usd=round(v1), after_7d_usd=round(v6), change=round(v1 / v0 - 1, 3)))

# ---------- sanity checks ----------
checks = {}
for m in MONTHS:
    g = sum(cat[(m, c)]['usd_g'] for c in YIELD_CATS); n = sum(cat[(m, c)]['usd_n'] for c in YIELD_CATS)
    rs = sum(r[3] for r in hist_rows if r[0] == m); rn = sum(r[3] for r in hist_rows if r[0] == m and r[5] == 1)
    checks[m] = dict(gross_usd=g, net_usd=n, net_le_gross=n <= g + 1, rows_sum_eq_gross=abs(rs - g) < len(hist_rows) + 10, rows_net_eq_net=abs(rn - n) < len(hist_rows) + 10)
cur_g = sum(r[5] for r in out_rows if r[2] in YIELD_CATS and r[5] != '' and 'memo' not in r[8] and not r[0].endswith('(memo)'))
cur_hist_ids = {p['id'] for p in P if p['hist'] in ('dl', 'pools')}
cur_like = sum(r['usd'] for r in ALL[CUR] if in_gross(r) and PBY[r['id']]['hist'] in ('dl', 'pools'))
checks['current_vs_history'] = dict(history_2026_09_gross=sum(cat[(CUR, c)]['usd_g'] for c in YIELD_CATS), current_like_for_like_gross=cur_like)

tot = collections.defaultdict(float)
for r in out_rows:
    c = r[2]
    if c not in YIELD_CATS or r[5] == '': continue
    memo = r[0].endswith('(memo)')
    if memo: continue
    tot['gross_usd'] += r[5]; tot['gross_btc'] += r[6]
    if r[9] == 0: tot['gross_onchain_usd'] += r[5]; tot['gross_onchain_btc'] += r[6]
    if r[11] == 1:
        tot['net_usd'] += r[5]; tot['net_btc'] += r[6]; tot[f'net_{c}_btc'] += r[6]; tot[f'net_{c}_usd'] += r[5]
        if r[9] == 0: tot['net_onchain_usd'] += r[5]; tot['net_onchain_btc'] += r[6]
    tot[f'gross_{c}_btc'] += r[6]; tot[f'gross_{c}_usd'] += r[5]
summary = dict(totals=dict(tot), leaders=leaders, leader_changes=changes, checks=checks, jumps=jumps,
               babylon_current_fp=dict(bab_cur_fp.most_common()), babylon_current_groups=dict(bab_cur_groups), babylon_hist_source=FPSRC,
               babylon_overlap_monthly={m: babylon_overlap(m) for m in MONTHS if vals['babylon'].get(m)},
               nesting_current={k: dict(v) for k, v in nesting(CUR)[0].items()}, symb_in_lv_current=nesting(CUR)[1],
               cum_flows={k: dict(v) for k, v in cum.items()}, mm_total_0920=mm_tot, mm_adj=mm_adj, ext_merged=len(ext_merged))
json.dump(summary, open(os.path.join(RAW, 'build_summary.json'), 'w'), indent=1, default=str)
print(json.dumps(dict(tot), indent=1))
print('leaders', leaders); print('changes', changes); print('jumps', len(jumps))
print('checks', {k: v for k, v in checks.items() if k == 'current_vs_history' or not (v['net_le_gross'] and v['rows_sum_eq_gross'] and v['rows_net_eq_net'])})
