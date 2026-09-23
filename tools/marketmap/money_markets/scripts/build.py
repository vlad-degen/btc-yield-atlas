"""Build the deliverable tables from out/mm_long.json (process.py) and the DefiLlama yields pools.

Writes (scratch folder mm/):
  mm_monthly.csv           segment, protocol, slug, month, btc_total, btc_plain, btc_yieldbearing, btc_borrowed, usd (+ source)
  mm_monthly_by_chain.csv  same per chain
  mm_tokens_snapshot.csv   2026-09-20 BTC per protocol x chain x token, with class and the map product the token is counted at
  mm_protocols.csv         protocol list: slug, DefiLlama category, segment, why included, snapshot and peak, yields 09-20 check
  mm_apy.csv               current (2026-09-23) supply APY of the largest BTC lending pools (DefiLlama yields)
  out/summary.json         numbers used in mm_notes.md
"""
import collections, csv, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mmlib import *
from tokens import YB

OUTD = D
L = json.load(open(os.path.join(D, 'out', 'mm_long.json')))
SCR = {r['slug']: r for r in json.load(open(os.path.join(D, 'out', 'screen_results.json')))}
PR = {p['slug']: p for p in json.load(open(os.path.join(RAW, 'protocols.json')))}
FL = json.load(open(os.path.join(RAW, 'fetch_list.json')))
POOLS = json.load(open(os.path.join(RAW, 'btc_lending_pools.json')))
PRICE = map_prices()
MLAB = [m for m, _, _ in MONTHS]
sys.path.insert(0, os.path.join(REPO, 'tools', 'marketmap', 'scripts'))
from products import P as PRODUCTS  # noqa: E402
C0NAME = {p['slug']: p['product'].split(': ', 1)[-1] for p in PRODUCTS if p['cat'] == 'C0'}
C0SEG = {s: seg for seg, ss in FL['c0'].items() for s in ss}
# the map's own C0 curator exclusions: tokens that are map products, not curated lending vaults (products.py excl)
CUR_EXCL = {'sentora-curator': {'KBTC'}, 'hyperithm': {'MHYPERBTC'}}
ONE_M = 1e6 / PRICE_SNAP  # 12.32 BTC

# ---------- selection ----------
EXCLUDE = {'cap': 'Cap (DefiLlama "Lending"): its BTC is restaked LBTC/uniBTC/SolvBTC delegated to Cap through Symbiotic/EigenLayer '
                  '(DefiLlama methodology: "total delegated assets on networks"); counted in the map as Symbiotic (C2) / Lombard Vaults (C5), not a money market'}
sel = {}
for s, r in SCR.items():
    today = r['snap_btc'] + r['snap_borrowed']
    if s in C0SEG:
        sel[s] = (C0SEG[s], 'C0 slug in products.py')
    elif s in EXCLUDE:
        continue
    elif r['segment'] in ('money_market', 'cdp'):
        if today >= ONE_M:
            sel[s] = (r['segment'], f"{r['category']}: >$1M of BTC on 2026-09-20" + ('' if r['segment'] == 'money_market' else ' (CDP not in products.py)'))
        elif r['peak_supplied'] >= 100:
            sel[s] = (r['segment'], f"{r['category']}: <$1M today, >=100 BTC at a month-end since 2024-09 (kept for the history)")
sel['takara-lend'] = ('money_market', 'Lending: ~545 BTC in DefiLlama yields pools (Sei); protocol data counts it until 2026-01, then 0 (yields-filled from 2026-02)')
sel['townsquare-lending'] = ('money_market', 'Lending: DefiLlama yields pool (enzoBTC, Monad) ~951 BTC; protocol TVL adapter shows ~0 (yields-sourced)')

def pname(s):
    return C0NAME.get(s) or PR.get(s, {}).get('name') or s

# ---------- yields: per project 09-20 (pool charts) and month-end series for yields-sourced rows ----------
def chart(pid):
    f = os.path.join(RAW, 'charts', pid + '.json')
    if not os.path.exists(f):
        return None
    return {r['timestamp'][:10]: r for r in json.load(open(f))['data']}

def chart_val(ch, label):
    if ch is None:
        return None
    if label == '2026-09':
        r = ch.get('2026-09-20')
        return r['tvlUsd'] if r else None
    y, m = int(label[:4]), int(label[5:])
    last = datetime.date(y + m // 12, m % 12 + 1, 1) - datetime.timedelta(days=1)
    for b in range(7):
        r = ch.get((last - datetime.timedelta(days=b)).isoformat())
        if r:
            return r['tvlUsd']
    return None

y0920 = collections.defaultdict(float); y0920_n = collections.Counter()
for p in POOLS:
    v = chart_val(chart(p['pool']), '2026-09')
    if v is None:
        v = 0.0 if chart(p['pool']) is not None else p['tvlUsd'] * PRICE_SNAP / 85362.09  # small pools without chart: scaled 09-23 value
    y0920[p['project']] += v; y0920_n[p['project']] += 1

# ---------- per slug x month x chain aggregates ----------
def agg_chain(s, m, ch):
    x = L[s][m].get(ch, {'tvl': {}, 'borrowed': {}})
    ex = CUR_EXCL.get(s, set())
    t = {k: v for k, v in x['tvl'].items() if k not in ex}
    b = {k: v for k, v in x['borrowed'].items() if k not in ex}
    tot = sum(v[0] for v in t.values())
    yb = sum(v[0] for v in t.values() if v[2] == 'yb')
    return dict(btc_total=tot, btc_plain=tot - yb, btc_yieldbearing=yb, btc_borrowed=sum(v[0] for v in b.values()),
                usd=sum(v[1] for v in t.values()))

YIELDS_FILL = {'takara-lend': '2026-02'}
rows_m, rows_c = [], []
for s, (sg, why) in sorted(sel.items()):
    for m in MLAB:
        if s == 'townsquare-lending':
            pids = [p['pool'] for p in POOLS if p['project'] == s]
            usd = sum(chart_val(chart(pid), m) or 0.0 for pid in pids)
            b = usd / PRICE[m]
            rec = dict(btc_total=b, btc_plain=b, btc_yieldbearing=0.0, btc_borrowed=0.0, usd=usd)
            rows_c.append(dict(segment=sg, protocol=pname(s), slug=s, chain='Monad', month=m, **rec))
            rows_m.append(dict(segment=sg, protocol=pname(s), slug=s, month=m, **rec, source='defillama-yields-pool (enzoBTC tvlUsd / BTC price)'))
            continue
        tot = collections.Counter()
        for ch in sorted(L[s][m]):
            rec = agg_chain(s, m, ch)
            if any(abs(v) > 1e-9 for v in rec.values()):
                rows_c.append(dict(segment=sg, protocol=pname(s), slug=s, chain=ch, month=m, **rec))
            tot.update(rec)
        src = 'defillama-protocol (token units)'
        if s in YIELDS_FILL and m >= YIELDS_FILL[s] and tot.get('btc_total', 0.0) < 1.0:
            # DefiLlama protocol data drops this protocol's BTC to 0 while its yields pools keep reporting (Takara Lend, Sei, from 2026-02)
            pids = [p['pool'] for p in POOLS if p['project'] == s]
            usd = sum(chart_val(chart(pid), m) or 0.0 for pid in pids)
            b = usd / PRICE[m]
            tot = collections.Counter(btc_total=b, btc_plain=b, btc_yieldbearing=0.0, btc_borrowed=0.0, usd=usd)
            rows_c.append(dict(segment=sg, protocol=pname(s), slug=s, chain='Sei', month=m, **tot))
            src = 'defillama-yields-pools (protocol data shows 0 from 2026-02; enzoBTC/UBTC/M-BTC tvlUsd / BTC price)'
        rows_m.append(dict(segment=sg, protocol=pname(s), slug=s, month=m, **{k: tot.get(k, 0.0) for k in
                      ('btc_total', 'btc_plain', 'btc_yieldbearing', 'btc_borrowed', 'usd')}, source=src))

def w(path, rows, fields):
    with open(path, 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        wr.writeheader()
        for r in rows:
            wr.writerow({k: (round(r[k], 4) if k.startswith('btc') else round(r[k]) if k == 'usd' else r[k]) for k in fields})
F = ['segment', 'protocol', 'slug', 'month', 'btc_total', 'btc_plain', 'btc_yieldbearing', 'btc_borrowed', 'usd']
segorder = {'money_market': 0, 'cdp': 1, 'venue': 2, 'curator': 3}
snapsize = {s: -sum(r['btc_total'] + r['btc_borrowed'] for r in rows_m if r['slug'] == s and r['month'] == '2026-09') for s in sel}
rows_m.sort(key=lambda r: (segorder[r['segment']], snapsize[r['slug']], r['slug'], r['month']))
rows_c.sort(key=lambda r: (segorder[r['segment']], snapsize[r['slug']], r['slug'], r['chain'], r['month']))
w(os.path.join(OUTD, 'mm_monthly.csv'), rows_m, F + ['source'])
w(os.path.join(OUTD, 'mm_monthly_by_chain.csv'), rows_c, ['segment', 'protocol', 'slug', 'chain', 'month', 'btc_total', 'btc_plain', 'btc_yieldbearing', 'btc_borrowed', 'usd'])

# ---------- token snapshot ----------
tok = []
for s, (sg, why) in sel.items():
    if s == 'takara-lend':
        for p in POOLS:
            if p['project'] == s and p['tvlUsd'] > 3e5:
                v = chart_val(chart(p['pool']), '2026-09') or 0.0
                tok.append(dict(segment=sg, protocol=pname(s), slug=s, chain='Sei', token=p['symbol'], cls='plain', counted_at='', btc_idle=v / PRICE_SNAP, btc_borrowed=0.0, usd=v))
        continue
    if s == 'townsquare-lending':
        tok.append(dict(segment=sg, protocol=pname(s), slug=s, chain='Monad', token='ENZOBTC', cls='plain', counted_at='',
                        btc_idle=[r for r in rows_m if r['slug'] == s and r['month'] == '2026-09'][0]['btc_total'], btc_borrowed=0.0, usd=0))
        continue
    for ch, x in L[s]['2026-09'].items():
        syms = set(x['tvl']) | set(x['borrowed'])
        for k in syms:
            if k in CUR_EXCL.get(s, set()):
                continue
            t = x['tvl'].get(k, [0, 0, None]); b = x['borrowed'].get(k, [0, 0, None])
            cl = t[2] or b[2]
            if t[0] or b[0]:
                tok.append(dict(segment=sg, protocol=pname(s), slug=s, chain=ch, token=k, cls=cl, counted_at=YB.get(k, '') if cl == 'yb' else '',
                                btc_idle=t[0], btc_borrowed=b[0], usd=t[1]))
tok.sort(key=lambda r: (segorder[r['segment']], -(r['btc_idle'] + r['btc_borrowed'])))
with open(os.path.join(OUTD, 'mm_tokens_snapshot.csv'), 'w', newline='') as f:
    wr = csv.writer(f, lineterminator='\n')
    wr.writerow(['segment', 'protocol', 'slug', 'chain', 'token', 'class', 'counted_at_map_product', 'btc_in_tvl', 'btc_borrowed', 'usd_in_tvl'])
    for r in tok:
        wr.writerow([r['segment'], r['protocol'], r['slug'], r['chain'], r['token'], r['cls'], r['counted_at'], round(r['btc_idle'], 4), round(r['btc_borrowed'], 4), round(r['usd'])])

# ---------- protocol list ----------
def ser(s, key):
    return {r['month']: r[key] for r in rows_m if r['slug'] == s}
prot = []
for s, (sg, why) in sel.items():
    tt = ser(s, 'btc_total'); bb = ser(s, 'btc_borrowed')
    sup = {m: tt[m] + bb[m] for m in MLAB}
    pk = max(MLAB, key=lambda m: sup[m])
    chains = sorted({r['chain'] for r in rows_c if r['slug'] == s and r['month'] == '2026-09' and r['btc_total'] + r['btc_borrowed'] > 0.01})
    prot.append(dict(segment=sg, protocol=pname(s), slug=s, defillama_category=PR.get(s, {}).get('category', ''), included_because=why,
                     btc_total_0920=tt['2026-09'], btc_borrowed_0920=bb['2026-09'], btc_yieldbearing_0920=ser(s, 'btc_yieldbearing')['2026-09'],
                     peak_month=pk, peak_btc_supplied=sup[pk], btc_total_2024_09=tt['2024-09'],
                     yields_pools_0920_btc=(y0920[s] / PRICE_SNAP) if s in y0920 else '', yields_pools_n=y0920_n.get(s, ''),
                     chains_0920=' '.join(chains)))
prot.sort(key=lambda r: (segorder[r['segment']], -(r['btc_total_0920'] + r['btc_borrowed_0920'])))
with open(os.path.join(OUTD, 'mm_protocols.csv'), 'w', newline='') as f:
    fields = list(prot[0].keys())
    wr = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); wr.writeheader()
    for r in prot:
        wr.writerow({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})

# ---------- APY table (current yields pools, read 2026-09-23; DefiLlama APY fields are in percent) ----------
apy = []
COLL_ONLY = ('morpho-blue', 'compound-v3')  # BTC pools of these are collateral pools: the BTC is never lent, supply APY 0 by construction
for p in POOLS:
    if p['category'] not in ('Lending', 'CDP', 'Uncollateralized Lending') or p['tvlUsd'] < 5e6:
        continue
    sup, bor = p.get('totalSupplyUsd'), p.get('totalBorrowUsd')
    coll = p['project'] in COLL_ONLY and not p['extra_symbol'] and (p['apyBase'] or 0) == 0
    cdp = p['category'] == 'CDP'
    apy.append(dict(project=p['project'], chain=p['chain'], symbol=p['symbol'], pool_meta=p['poolMeta'] or '', btc_0923=round(p['tvlUsd'] / 85362.09, 1),
                    tvl_usd_0923=round(p['tvlUsd']), btc_can_be_lent='no' if (coll or cdp) else 'yes',
                    supply_apy_base_pct=p['apyBase'] if p['apyBase'] is not None else 0, supply_apy_reward_pct=p['apyReward'] or 0,
                    supply_apy_total_pct=p['apy'] or 0, supply_apy_mean30d_pct=p.get('apyMean30d') if p.get('apyMean30d') is not None else '',
                    btc_utilization=(round(bor / sup, 4) if (sup and bor is not None and not coll and not cdp) else ''),
                    btc_borrow_apy_pct=(p.get('apyBaseBorrow') if not (coll or cdp) else ''),
                    dollar_loan_apy_pct=(p.get('apyBaseBorrow') if (coll or cdp) else ''),
                    note=('collateral pool: BTC is not lent; dollar_loan_apy = rate paid on the loan taken against it' if coll else
                          'CDP collateral: BTC earns nothing; dollar_loan_apy = stability fee / borrow rate' if cdp else
                          ('uncollateralized credit vault' if p['category'] == 'Uncollateralized Lending' else ''))))
apy.sort(key=lambda r: -r['tvl_usd_0923'])
with open(os.path.join(OUTD, 'mm_apy.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(apy[0].keys()), lineterminator='\n'); wr.writeheader(); wr.writerows(apy)
def wavg(pred):
    num = den = nb = nr = 0.0
    for p in POOLS:
        if p['category'] in ('Lending', 'Uncollateralized Lending') and not p['extra_symbol'] and pred(p):
            den += p['tvlUsd']; num += p['tvlUsd'] * (p['apy'] or 0); nb += p['tvlUsd'] * (p['apyBase'] or 0); nr += p['tvlUsd'] * (p['apyReward'] or 0)
    return dict(usd=den, apy=num / den, base=nb / den, reward=nr / den)
APYSTAT = dict(all=wavg(lambda p: True), lendable=wavg(lambda p: not (p['project'] in COLL_ONLY and (p['apyBase'] or 0) == 0)),
               lendable_ex_credit=wavg(lambda p: p['category'] == 'Lending' and not (p['project'] in COLL_ONLY and (p['apyBase'] or 0) == 0)))

# ---------- summary ----------
S = collections.defaultdict(dict)
for sg in segorder:
    for m in MLAB:
        rr = [r for r in rows_m if r['segment'] == sg and r['month'] == m]
        S[sg][m] = {k: sum(r[k] for r in rr) for k in ('btc_total', 'btc_plain', 'btc_yieldbearing', 'btc_borrowed', 'usd')}
json.dump(dict(segments=S, apy=APYSTAT, n=dict(collections.Counter(v[0] for v in sel.values())), yields_0920_usd=dict(y0920),
               selection={s: v for s, v in sel.items()}), open(os.path.join(D, 'out', 'summary.json'), 'w'), indent=0)
for sg in segorder:
    x = S[sg]['2026-09']
    print(f"{sg:13s} n={collections.Counter(v[0] for v in sel.values())[sg]:3d} total={x['btc_total']:10.1f} plain={x['btc_plain']:10.1f} yb={x['btc_yieldbearing']:9.1f} borrowed={x['btc_borrowed']:8.1f} usd={x['usd']/1e9:6.2f}B")
