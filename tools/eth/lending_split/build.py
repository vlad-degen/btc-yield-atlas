"""Build the lending split: ETH and BTC collateral in lending markets, by collateral form and by what is borrowed against it.

Reads the raw captures in raw/eth/lending-split-2026-10-08/ and writes data/eth/lending_split.json and data/eth/lending_split_accounts.csv.
Cells: form A (staking / yield tokens) or B (plain ETH/WETH, plain BTC wrappers) x borrowed 1 (same asset: ETH loops / BTC against BTC),
2 (stablecoins), 3 (other), 4 (nothing: collateral of accounts with no debt, and supply not lent out).
Rules: pooled venues allocate each account's enabled family collateral to its debts pro rata by debt value in USD; family supply not enabled
as collateral and supply of accounts with no debt go to 4. Supply that is lent out (debt of the family asset) is taken out of cell 4 and
shown once as a memo line (the other side of cell 1). Pair venues (Morpho Blue, Compound v3, Fluid) assign each position to its loan asset.
Large accounts: family collateral of at least $500k at the venue. Everything else is the venue's small-accounts line.
"""
import csv, glob, json, os, collections
from lib import RAW, ROOT, OLD, fam, form

PX = {'eth': 2669.39, 'btc': 81178.0}
LARGE = 500_000
COL = {'own': 1, 'stable': 2, 'other': 3}
CELLS = [(f, c) for f in 'AB' for c in (1, 2, 3, 4)]
OUT = os.path.join(ROOT, 'data', 'eth')


def L(name):
    p = os.path.join(RAW, name)
    return json.load(open(p)) if os.path.exists(p) else None


def empty(): return {k: 0.0 for k in CELLS}


class Venue:
    def __init__(s, side, venue, chain, kind):
        s.side, s.venue, s.chain, s.kind = side, venue, chain, kind
        s.accts = []  # dicts: user, cells, stable_attr_usd, own_debt_attr, coll_native, large
        s.extra = empty(); s.extra_label = []  # estimated / remainder cells
        s.lender_gross = {'A': 0.0, 'B': 0.0}; s.lent = {'A': 0.0, 'B': 0.0}
        s.total_native = None; s.notes = []
        s.est_stable_usd = 0.0; s.est_own_debt = 0.0
        s.netmode = {'pooled': 'account', 'pair': 'pair'}.get(kind, 'pair')

    def add(s, user, cells, stable_attr, own_debt_attr, extra=None, net=None):
        c = sum(cells.values())
        if c <= 0: return
        d = dict(user=user, cells=cells, net=net or dict(cells), stable_attr_usd=stable_attr, own_debt_attr=own_debt_attr, coll_native=c,
                 large=c * PX[s.side] >= LARGE)
        if extra: d.update(extra)
        s.accts.append(d)

    def matrix(s):
        """gross: every holder's family collateral or supply as it holds it. net (counted once): less the part lent out."""
        g = empty(); n = empty()
        for a in s.accts:
            for k, v in a['cells'].items(): g[k] += v
            for k, v in a['net'].items(): n[k] += v
        rg = {f: sum(x for (ff, c), x in g.items() if ff == f) for f in 'AB'}
        rn = {f: sum(x for (ff, c), x in n.items() if ff == f) for f in 'AB'}
        for k, v in s.extra.items():
            g[k] += v; n[k] += v * (rn[k[0]] / rg[k[0]] if rg[k[0]] and s.netmode == 'account' else 1.0)
        for f in 'AB':
            g[(f, 4)] += s.lender_gross[f]; n[(f, 4)] += s.lender_gross[f]
        if s.netmode == 'pair':
            for f in 'AB':
                take = min(s.lent[f], n[(f, 4)]); n[(f, 4)] -= take; rest = s.lent[f] - take
                row = sum(n[(f, c)] for c in (1, 2, 3))
                if rest > 1e-6 and row:
                    for c in (1, 2, 3): n[(f, c)] -= rest * n[(f, c)] / row
                    s.notes.append('%s: %.0f lent out beyond idle supply, taken pro rata from the collateral cells' % (f, rest))
        elif s.netmode == 'pool':
            for f in 'AB':
                row = sum(g[(f, c)] for c in (1, 2, 3, 4))
                k = 1 - min(1.0, s.lent[f] / row) if row else 1.0
                for c in (1, 2, 3, 4): n[(f, c)] = g[(f, c)] * k
        return g, n


def pooled_alloc(row, ref, side, util=None):
    """returns gross cells, net cells (each holding reduced by its reserve's utilization: the part lent out), stable debt and own debt attributed"""
    util = util or {}
    debts = collections.Counter()
    for sym, d in row.get('debts', {}).items(): debts[d['fam']] += d['usd']
    D = sum(debts.values())
    cells = empty(); net = empty(); en_usd = 0.0
    for sym, c in row['colls'].items():
        f = c['form']; k = 1 - util.get(sym, 0.0)
        if c.get('enabled', True) and D > 0:
            en_usd += c['usd']
            for fm, v in debts.items():
                cells[(f, COL[fm])] += c['native'] * v / D; net[(f, COL[fm])] += c['native'] * v / D * k
        else:
            cells[(f, 4)] += c['native']; net[(f, 4)] += c['native'] * k
    ratio = min(1.0, en_usd / row['coll_usd']) if row.get('coll_usd') else (1.0 if en_usd else 0.0)
    return cells, net, debts['stable'] * ratio, debts['own'] / ref * ratio


def scale_mix(accts, f):
    """cell fractions within form f from a list of accounts"""
    t = collections.Counter()
    for a in accts:
        for (ff, c), v in a['cells'].items():
            if ff == f: t[c] += v
    s = sum(t.values())
    return {c: t[c] / s for c in t} if s else None


def build_aave(side):
    out = []
    for p in sorted(glob.glob(os.path.join(RAW, 'aave_%s_*.json' % side))):
        d = json.load(open(p)); name = d['venue']
        own = [r for r in d['reserves'] if r['fam'] == 'own' and r['supply'] > 0]
        if not own: continue
        v = Venue(side, name, d['chain'], 'pooled'); ref = d['ref_price']
        util = {r['sym']: min(1.0, r['debt'] / r['supply']) for r in own}
        for r in d['rows']:
            cells, net, st, od = pooled_alloc(r, ref, side, util)
            usd = sum(c['usd'] for c in r['colls'].values())
            v.add(r['user'], cells, st, od, dict(debt_usd=r['debt_usd'], coll_usd_all=r['coll_usd'], fam_coll_usd=usd), net=net)
        tot = {'A': 0.0, 'B': 0.0}
        for r in own:
            tot[r['form']] += r['supply'] * r['price'] / ref
            v.lent[r['form']] += r['debt'] * r['price'] / ref
        v.total_native = tot
        read = {'A': 0.0, 'B': 0.0}
        for a in v.accts:
            for (f, c), x in a['cells'].items(): read[f] += x
        v.coverage = {f: (read[f] / tot[f] if tot[f] else None) for f in 'AB'}
        v.large_share = sum(a['coll_native'] for a in v.accts if a['large']) / (tot['A'] + tot['B'])
        v.enumerated = bool(d['rows'])
        for f in 'AB':
            rem = tot[f] - read[f]
            if rem <= 0: continue
            mix = scale_mix([a for a in v.accts if not a['large']], f) or scale_mix(v.accts, f)
            if mix is None: v.extra[(f, 'pending')] = rem; continue
            for c, x in mix.items(): v.extra[(f, c)] += rem * x
            v.extra_label.append('%s: %.0f unread (%.1f%%) spread by the mix of read small accounts' % (f, rem, 100 * rem / tot[f]))
        out.append(v)
    # pools with no enumeration: spread by the mix of the enumerated L2 pools
    l2 = [a for v in out if v.chain != 1 and v.enumerated for a in v.accts]
    for v in out:
        pend = [(k, x) for k, x in v.extra.items() if k[1] == 'pending']
        if not pend and v.enumerated: continue
        for (f, _), x in pend: del v.extra[(f, 'pending')]
        if not v.enumerated:
            for f in 'AB':
                mix = scale_mix(l2, f) or {}
                for c, frac in mix.items(): v.extra[(f, c)] += v.total_native[f] * frac
            v.extra_label = ['not enumerated (explorer holder pages unavailable): whole pool spread by the mix of the read Aave Base and Arbitrum accounts']
        else:
            for (f, _), x in pend:
                mix = scale_mix(l2, f) or {4: 1.0}
                for c, frac in mix.items(): v.extra[(f, c)] += x * frac
    return out


def morpho_valid(chain):
    return L('morpho_meta_%d.json' % chain) or {}


def build_morpho(side):
    out = []
    for p in sorted(glob.glob(os.path.join(RAW, 'morpho_%s_*.json' % side))):
        d = json.load(open(p)); ch = d['chain']; meta = morpho_valid(ch)
        v = Venue(side, 'morpho', ch, 'pair'); ref = d['ref_price_now']
        def ok_coll(mid):
            m = meta.get(mid); return bool(m and m['coll'] and m['coll'].get('priceUsd'))
        def ok_loan(mid):
            m = meta.get(mid)
            if not m: return False
            return bool(m['loan'] and m['loan'].get('priceUsd')) and (m['listed'] or (m['coll'] and m['coll'].get('priceUsd')))
        dropped = 0.0
        byu = collections.defaultdict(lambda: dict(cells=empty(), st=0.0, od=0.0))
        for r in d['rows']:
            if not ok_coll(r['market']): dropped += r['coll_native']; continue
            c = (form(r['coll_sym'], side), COL[r['loan_fam']] if r['debt_units'] > 0 else 4)
            u = byu[(r['user'], r['market'])]
            u['cells'][c] += r['coll_native']
            if r['debt_units'] > 0:
                if r['loan_fam'] == 'stable': u['st'] += r['debt_usd']
                if r['loan_fam'] == 'own': u['od'] += r['debt_native']
        # one account per user across the chain's markets
        agg = collections.defaultdict(lambda: dict(cells=empty(), st=0.0, od=0.0, markets=0))
        for (u, mid), x in byu.items():
            a = agg[u]
            for k, val in x['cells'].items(): a['cells'][k] += val
            a['st'] += x['st']; a['od'] += x['od']; a['markets'] += 1
        for u, a in agg.items(): v.add(u, a['cells'], a['st'], a['od'])
        for l in d['loan_markets']:
            if not ok_loan(l['market']): continue
            lf = form(l['loan_sym'], side); v.lender_gross[lf] += l['supply_native']; v.lent[lf] += l['borrow_native']
        if dropped > 1: v.notes.append('dropped %.0f native units of unpriced look-alike collateral' % dropped)
        v.coverage = {'A': 1.0, 'B': 1.0}; v.enumerated = True
        tot = {'A': 0.0, 'B': 0.0}
        for a in v.accts:
            for (f, c), x in a['cells'].items(): tot[f] += x
        v.total_native = tot
        v.large_share = (sum(a['coll_native'] for a in v.accts if a['large']) / (tot['A'] + tot['B'])) if tot['A'] + tot['B'] else None
        out.append(v)
    return out


def rate_map(side):
    rm = {}
    for p in glob.glob(os.path.join(RAW, 'aave_%s_*.json' % side)):
        d = json.load(open(p))
        for r in d['reserves']:
            if r['fam'] == 'own' and r['price']: rm.setdefault(r['sym'].upper(), r['price'] / d['ref_price'])
    return rm


def build_compound(side):
    out = []; rm = rate_map(side)
    mixes = {}
    files = sorted(glob.glob(os.path.join(RAW, 'compound_%s_*.json' % side)))
    data = [json.load(open(p)) for p in files]
    # Ethereum mix of collateral with / without debt by base family
    for d in data:
        if d['chain'] != 1: continue
        base = {c['comet']: c['base_fam'] for c in d['comets']}
        for r in d['rows']:
            bf = base[r['comet']]; m = mixes.setdefault(bf, [0.0, 0.0])
            x = sum(u * rm.get(s.upper(), 1.0) for s, u in r['colls'].items())
            m[0 if r['debt_units'] > 0 else 1] += x
    for d in data:
        ch = d['chain']; v = Venue(side, 'compound-v3', ch, 'pair')
        base = {c['comet']: c for c in d['comets']}
        byu = collections.defaultdict(lambda: dict(cells=empty(), st=0.0, od=0.0))
        for r in d['rows']:
            c = base[r['comet']]; bf = c['base_fam']
            u = byu[r['user']]
            for s, x in r['colls'].items():
                n = x * rm.get(s.upper(), 1.0); f = form(s, side)
                u['cells'][(f, COL[bf] if r['debt_units'] > 0 else 4)] += n
            if r['debt_units'] > 0:
                if bf == 'stable': u['st'] += r['debt_units']
                if bf == 'own': u['od'] += r['debt_units'] * rm.get(c['base'].upper(), 1.0)
        for user, a in byu.items(): v.add(user, a['cells'], a['st'], a['od'])
        tot = {'A': 0.0, 'B': 0.0}
        for c in d['comets']:
            if c.get('base_fam') == 'own':
                r_ = rm.get(c['base'].upper(), 1.0)
                v.lender_gross[c['base_form']] += c['total_supply'] * r_; v.lent[c['base_form']] += c['total_borrow'] * r_
            for s, x in c['collateral'].items():
                n = x * rm.get(s.upper(), 1.0); f = form(s, side); tot[f] += n
                if not c['enumerated']:
                    m = mixes.get(c['base_fam'], [1, 0]); w = m[0] / (m[0] + m[1]) if sum(m) else 1.0
                    v.extra[(f, COL[c['base_fam']])] += n * w; v.extra[(f, 4)] += n * (1 - w)
                    if c['base_fam'] == 'stable': v.est_stable_usd += 0  # debt not read on non-enumerated Comets
        if any(not c['enumerated'] for c in d['comets']):
            v.extra_label.append('Comet totals only; split with / without debt from the Ethereum Comets with the same base asset')
        v.total_native = tot
        read = sum(a['coll_native'] for a in v.accts)
        v.coverage = {'all': read / (tot['A'] + tot['B']) if tot['A'] + tot['B'] else None}
        v.large_share = sum(a['coll_native'] for a in v.accts if a['large']) / (tot['A'] + tot['B']) if tot['A'] + tot['B'] else None
        v.enumerated = any(c['enumerated'] for c in d['comets'])
        if tot['A'] + tot['B'] + v.lender_gross['A'] + v.lender_gross['B'] > 0: out.append(v)
    return out


def build_fluid(side):
    out = []
    for p in sorted(glob.glob(os.path.join(RAW, 'fluid_%s_*.json' % side))):
        d = json.load(open(p)); ch = d['chain']; ref = d['ref_price_now']
        v = Venue(side, 'fluid', ch, 'pair'); v.netmode = 'pool'
        byu = collections.defaultdict(lambda: dict(cells=empty(), st=0.0, od=0.0))
        own_debt_total = 0.0
        for r in d['rows']:
            D = sum(r['debt_usd_by_fam'].values()); u = byu[r['user']]
            for f, x in r['coll_by_form'].items():
                if D > 0:
                    for fm, dv in r['debt_usd_by_fam'].items(): u['cells'][(f, COL[fm])] += x * dv / D
                else: u['cells'][(f, 4)] += x
            u['st'] += r['debt_usd_by_fam'].get('stable', 0); u['od'] += r['debt_usd_by_fam'].get('own', 0) / ref
            own_debt_total += r['debt_usd_by_fam'].get('own', 0) / ref
        for user, a in byu.items(): v.add(user, a['cells'], a['st'], a['od'])
        for m in d['vaults']:
            if m.get('error'):
                sup = int(m['api_totalSupply']); bf = m['borrow_usd_per_unit_by_fam']; D = sum(bf.values()) or 1
                for f, x in m['form_native_per_unit'].items():
                    for fm, dv in bf.items(): v.extra[(f, COL[fm])] += sup * x * dv / D
                own_debt_total += int(m['api_totalBorrow']) * bf.get('own', 0) / ref
                v.extra_label.append('vault %s (%s): position resolver not read (off Ethereum); vault totals on the scan day from the Fluid API, all collateral assigned to its debt asset' % (m['id'], m['pair']))
        for l in d.get('lending', []):
            v.lender_gross[l['form']] += l['native']
        v.lent['B'] += own_debt_total  # ETH-family debt of vaults is mostly WETH; staking-token debt is small and counted with WETH here
        tot = {'A': 0.0, 'B': 0.0}
        for a in v.accts:
            for (f, c), x in a['cells'].items(): tot[f] += x
        for (f, c), x in v.extra.items(): tot[f] += x
        v.total_native = tot; v.coverage = {'all': 1.0}; v.enumerated = True
        v.large_share = sum(a['coll_native'] for a in v.accts if a['large']) / (tot['A'] + tot['B']) if tot['A'] + tot['B'] else None
        out.append(v)
    return out


def build_v4(side):
    d = L('aave_v4_%s.json' % side)
    if not d: return []
    v = Venue(side, 'aave-v4', 1, 'pooled'); v.netmode = 'pool'; ref = d['ref_price']
    lent = 0.0
    for r in d['rows']:
        cells, net, st, od = pooled_alloc(r, ref, side)
        v.add(r['user'] + '@' + r['spoke'][:10], cells, st, od, dict(debt_usd=r['debt_usd'], coll_usd_all=r['coll_usd']))
        lent += sum(x['usd'] for x in r['debts'].values() if x['fam'] == 'own') / ref
    v.lent['B'] += lent
    tot = {'A': 0.0, 'B': 0.0}
    for a in v.accts:
        for (f, c), x in a['cells'].items(): tot[f] += x
    v.total_native = tot; v.coverage = {'all': 1.0}; v.enumerated = True
    v.large_share = sum(a['coll_native'] for a in v.accts if a['large']) / (tot['A'] + tot['B']) if tot['A'] + tot['B'] else None
    v.notes.append('lent out = family debt of accounts that also hold family collateral (borrowers against other collateral not read)')
    return [v]


def summarize(vs, side):
    res = []; tot = empty(); totn = empty(); tot_g4 = {'A': 0.0, 'B': 0.0}; lent = {'A': 0.0, 'B': 0.0}
    st_usd = 0.0; od = 0.0; cells_meas = empty()
    for v in vs:
        m, mn = v.matrix(); g4 = {f: m[(f, 4)] for f in 'AB'}
        meas = empty()
        for a in v.accts:
            for k, x in a['cells'].items(): meas[k] += x
        est = {k: x for k, x in v.extra.items()}
        st = sum(a['stable_attr_usd'] for a in v.accts); o = sum(a['own_debt_attr'] for a in v.accts)
        # estimated remainder: scale debt by the venue's read ratio for the same cells
        c2r = meas[('A', 2)] + meas[('B', 2)]; c1r = meas[('A', 1)] + meas[('B', 1)]
        c2e = est.get(('A', 2), 0) + est.get(('B', 2), 0); c1e = est.get(('A', 1), 0) + est.get(('B', 1), 0)
        st_est = st / c2r * c2e if c2r else 0.0; o_est = o / c1r * c1e if c1r else 0.0
        large = [a for a in v.accts if a['large']]
        res.append(dict(venue=v.venue, chain=v.chain, kind=v.kind,
                        matrix_native={'%s%d' % k: round(x, 2) for k, x in m.items()},
                        matrix_counted_once_native={'%s%d' % k: round(x, 2) for k, x in mn.items()},
                        matrix_usd={'%s%d' % k: round(x * PX[side]) for k, x in m.items()},
                        measured_accounts_native={'%s%d' % k: round(x, 2) for k, x in meas.items()},
                        estimated_native={'%s%s' % k: round(x, 2) for k, x in est.items() if x},
                        lender_supply_gross_native={f: round(v.lender_gross[f], 2) for f in 'AB'},
                        cell4_gross_native={f: round(g4[f], 2) for f in 'AB'},
                        lent_out_native={f: round(v.lent[f], 2) for f in 'AB'},
                        collateral_total_native={f: round(x, 2) for f, x in (v.total_native or {}).items()},
                        coverage_read=getattr(v, 'coverage', None), large_accounts=len(large),
                        large_accounts_share_of_collateral=getattr(v, 'large_share', None),
                        stable_debt_attributed_usd=round(st + st_est), stable_debt_attributed_read_usd=round(st),
                        own_debt_attributed_native=round(o + o_est, 2), estimate_notes=v.extra_label, notes=v.notes))
        for k, x in m.items(): tot[k] += x
        for k, x in mn.items(): totn[k] += x
        for f in 'AB': tot_g4[f] += g4[f]; lent[f] += v.lent[f]
        st_usd += st + st_est; od += o + o_est
    return res, tot, totn, tot_g4, lent, st_usd, od


def main():
    out = {'snapshots': {'eth': '2026-10-02 23:59:59 UTC, Ethereum block 26,108,081 (L2: last block at or before)',
                         'btc': '2026-09-20 12:00:00 UTC, Ethereum block 26,018,583 (L2: last block at or before)'},
           'prices_usd': PX, 'large_account_usd': LARGE,
           'cells': {'A': 'staking / yield tokens', 'B': 'plain ETH/WETH or plain BTC wrappers', '1': 'borrowed the same asset (ETH against ETH, BTC against BTC)',
                     '2': 'stablecoins', '3': 'other assets', '4': 'nothing (no debt, or supply not lent out)'}}
    gap = {r['address'].lower(): r for r in csv.DictReader(open(os.path.join(OUT, 'gap_borrower_scan.csv')))}
    big38 = {a for a, r in gap.items() if float(r['eth_backed_stablecoin_debt_usd_T'] or 0) >= 20e6}
    pooled = {a for a, r in gap.items() if r['pooled_product'].startswith('yes')}
    acc_rows = []
    for side in ('eth', 'btc'):
        vs = build_aave(side) + build_v4(side) + build_morpho(side) + build_compound(side) + build_fluid(side)
        res, tot, totn, g4, lent, st, od = summarize(vs, side)
        p = PX[side]
        # concentration per cell over measured accounts (venue, chain, user)
        cellacc = collections.defaultdict(list)
        for v in vs:
            for a in v.accts:
                for k, x in a['cells'].items():
                    if x > 0: cellacc[k].append((x, v.venue, v.chain, a['user']))
        conc = {}
        for k in CELLS:
            l = sorted(cellacc[k], reverse=True); s = sum(x for x, *_ in l)
            conc['%s%d' % k] = dict(accounts=len(l), measured_native=round(s, 2), top20_share=(sum(x for x, *_ in l[:20]) / s if s else None))
        # low-LTV check on the stablecoin cell: collateral in accounts whose attributed stablecoin debt is under 10% / 20% of it
        lo = {0.1: 0.0, 0.2: 0.0}; c2all = 0.0
        for v in vs:
            for a in v.accts:
                c2 = a['cells'][('A', 2)] + a['cells'][('B', 2)]
                if c2 <= 0: continue
                c2all += c2; l = a['stable_attr_usd'] / (c2 * p)
                for t in lo:
                    if l < t: lo[t] += c2
        lowltv = {'under_10pct': lo[0.1] / c2all if c2all else None, 'under_20pct': lo[0.2] / c2all if c2all else None}
        est_once = 0.0
        for r in res:
            for k, x in r['estimated_native'].items(): est_once += x
        stats = {}
        if side == 'eth':
            c2 = lambda a: a['cells'][('A', 2)] + a['cells'][('B', 2)]
            for nm, S in (('big38', big38), ('pooled_products', pooled), ('all_gap_scan_164', set(gap))):
                x = sum(c2(a) for v in vs for a in v.accts if a['user'].split('@')[0] in S)
                y = sum(a['stable_attr_usd'] for v in vs for a in v.accts if a['user'].split('@')[0] in S)
                stats[nm] = dict(cell2_collateral_native=round(x, 2), stable_debt_attr_usd=round(y))
        # long tail: DefiLlama's collateral-plus-unlent basis (lending_gross.json / BTC money_markets) less what is measured, by form,
        # spread by the measured counted-once mix of the same form. Labelled estimate.
        lg = json.load(open(os.path.join(OUT, 'netmap', 'lending_gross.json')))
        if side == 'eth':
            dl = {'A': lg['totals']['staking_tokens_eth'], 'B': lg['totals']['plain_eth']}
        else:
            dl = {'A': lg['btc']['staking_tokens_btc'], 'B': lg['btc']['plain_btc']}
        tail = empty(); tail_note = {}
        for f in 'AB':
            meas = sum(totn[(f, c)] for c in (1, 2, 3, 4)); rest = dl[f] - meas; tail_note[f] = dict(defillama=round(dl[f], 2), measured_counted_once=round(meas, 2), long_tail=round(rest, 2))
            if rest > 0 and meas:
                for c in (1, 2, 3, 4): tail[(f, c)] = rest * totn[(f, c)] / meas
        allin = {k: totn[k] + tail[k] for k in CELLS}
        c1 = tot[('A', 1)] + tot[('B', 1)]; c2t = tot[('A', 2)] + tot[('B', 2)]
        out[side] = dict(
            venues=res,
            matrix_native={'%s%d' % k: round(x, 2) for k, x in tot.items()},
            matrix_usd={'%s%d' % k: round(x * p) for k, x in tot.items()},
            total_native=round(sum(tot.values()), 2),
            matrix_counted_once_native={'%s%d' % k: round(x, 2) for k, x in totn.items()},
            matrix_counted_once_usd={'%s%d' % k: round(x * p) for k, x in totn.items()},
            total_counted_once_native=round(sum(totn.values()), 2), lent_out_native={f: round(lent[f], 2) for f in 'AB'},
            cell4_gross_native={f: round(g4[f], 2) for f in 'AB'},
            long_tail_estimate=dict(note='DefiLlama basis (collateral plus supply not lent out) less the measured counted-once total, per form, spread by the measured mix (estimate)',
                                    by_form=tail_note, matrix_native={'%s%d' % k: round(x, 2) for k, x in tail.items()}),
            matrix_counted_once_with_long_tail_native={'%s%d' % k: round(x, 2) for k, x in allin.items()},
            matrix_counted_once_with_long_tail_usd={'%s%d' % k: round(x * p) for k, x in allin.items()},
            same_asset_loops=dict(collateral_native=round(c1, 2), own_debt_native=round(od, 2), equity_native=round(c1 - od, 2)),
            stablecoin_loans=dict(collateral_native=round(c2t, 2), collateral_usd=round(c2t * p), debt_usd=round(st), implied_ltv=(st / (c2t * p) if c2t else None)),
            concentration=conc, borrower_groups=stats, stablecoin_cell_low_ltv_share=lowltv,
            estimated_share_of_measured_venues=(est_once / sum(tot.values()) if sum(tot.values()) else None))
        for v in vs:
            for a in v.accts:
                if not a['large']: continue
                u = a['user'].split('@')[0]; g = gap.get(u, {})
                acc_rows.append(dict(side=side, venue=v.venue, chain=v.chain, account=a['user'], coll_native=round(a['coll_native'], 4),
                                     **{'%s%d' % k: round(x, 4) for k, x in a['cells'].items()},
                                     main_cell=max(a['cells'], key=a['cells'].get) and '%s%d' % max(a['cells'], key=a['cells'].get),
                                     stable_debt_attr_usd=round(a['stable_attr_usd']), own_debt_attr_native=round(a['own_debt_attr'], 4),
                                     gap_scan_who=g.get('who', ''), gap_scan_category=g.get('category', ''), pooled_product=g.get('pooled_product', ''),
                                     in_big38=('yes' if u in big38 else '')))
    json.dump(out, open(os.path.join(OUT, 'lending_split.json'), 'w'), indent=1, default=str)
    acc_rows.sort(key=lambda r: (r['side'], -r['coll_native']))
    with open(os.path.join(OUT, 'lending_split_accounts.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(acc_rows[0].keys())); w.writeheader(); w.writerows(acc_rows)
    for side in ('eth', 'btc'):
        o = out[side]; m = o['matrix_native']
        print(side.upper(), 'total %.0f' % o['total_native'], 'lent out', o['lent_out_native'])
        mn = o['matrix_counted_once_native']
        for f in 'AB': print('  ', f, 'gross', [round(m['%s%d' % (f, c)]) for c in (1, 2, 3, 4)], 'once', [round(mn['%s%d' % (f, c)]) for c in (1, 2, 3, 4)])
        print('  total once %.0f' % o['total_counted_once_native'])
        print('  loops', o['same_asset_loops'], '\n  stables', o['stablecoin_loans'])
        for v in o['venues']:
            mm = v['matrix_native']
            print('   %-14s %6s' % (v['venue'], v['chain']), ' '.join('%9.0f' % mm[k] for k in ('A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4')),
                  'cov', v['coverage_read'] and {k: round(x, 3) for k, x in v['coverage_read'].items() if x is not None}, 'large', v['large_accounts'],
                  v['large_accounts_share_of_collateral'] and round(v['large_accounts_share_of_collateral'], 3))


if __name__ == '__main__':
    main()
