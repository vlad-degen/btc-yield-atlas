"""The lending layer of the ETH counted-once map: staking tokens and plain ETH in lending markets, split into leveraged staking
(loops), the carry products' own positions and money markets, at the snapshot and every month-end.

Snapshot (2 October 2026): data/eth/lending_split.json, counted-once matrix with the long tail (A = staking tokens,
B = plain ETH/WETH; 1 = ETH debt, 2 = dollars, 3 = other, 4 = nothing; lent-out WETH is not added), and the carry
products' own accounts in data/eth/netmap/carry_lending_snapshot.json (tools/eth/lending_split/product_accounts.py).
Month-ends:
- staking tokens and plain ETH in lending markets: DefiLlama token breakdowns of the lending rows (the matrix basis);
- loops: estimate. Month-end ETH debt (Aave Core, Prime and Spark on-chain, data/eth/gap_loop_regime_monthly.csv; every other
  lending market and chain from DefiLlama's borrowed WETH) times the snapshot ratio of loop collateral to ETH debt;
- carry products' collateral against dollar debt: archive reads of their accounts (gap_top5_risk_series.csv,
  carry_accounts_monthly.csv, gap_rocksolid_upshift.json), Avant's Aave v4 and Morpho legs estimated from its dollar debt;
- money markets = lending-market ETH less loops less the carry products' lending positions.
"""
import collections, csv, json, os
from lib import OUT, ROOT, load, pick, series
from products import ISSUERS
import decisions as DEC

PLAIN = {'ETH', 'WETH', 'WETH.E', 'ETH.E'}
D = os.path.join(ROOT, 'data', 'eth')
CELLS = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4']


def token_row(sym):
    """row that counts the ETH behind a token (staking-token issuer or product on the map), or None"""
    return ISSUERS.get(sym) or DEC.PRODUCT_TOKENS.get(sym)


def split_breakdown(br_eth, row_category):
    """lending-row breakdown (ETH) -> (issuer tokens {row: eth}, tokens with no row, plain ETH, product shares)
    Product shares are tokens of map products that are not staking/restaking issuers (tETH, savETH, weETHs ...): the product's
    own row or book counts what is behind them, so the lending layer leaves them out."""
    iss, none, plain, shares = collections.defaultdict(float), 0.0, 0.0, 0.0
    for k, v in br_eth.items():
        if k == 'SPETH':  # WETH lent into SparkLend: idle part counted in SparkLend, lent part with its borrowers
            continue
        if k in PLAIN:
            plain += v
            continue
        row = token_row(k)
        if row is None:
            none += v
        elif row_category.get(row) in ('staking', 'restaking'):
            iss[row] += v
        else:
            shares += v
    return iss, none, plain, shares


def borrowed_weth(slug, pdate, price):
    """plain WETH lent out by a lending row, per chain (DefiLlama '{chain}-borrowed' token series), ETH"""
    out = {}
    for k in (load(slug).get('chainTvls') or {}):
        if k.endswith('-borrowed'):
            tok, _ = pick(series(slug, k), pdate)
            out[k[:-len('-borrowed')]] = sum(x for s, x in (tok or {}).items() if s.upper() in PLAIN and x and x > 0) / price
    return out


def matrix():
    L = json.load(open(os.path.join(D, 'lending_split.json')))['eth']
    return {k: float(v) for k, v in L['matrix_counted_once_with_long_tail_native'].items()}, L


def onchain_debt():
    """month -> on-chain WETH debt of Aave Core, Aave Prime and SparkLend (Ethereum)"""
    out = {r['month']: float(r['total_weth_debt_eth']) for r in csv.DictReader(open(os.path.join(D, 'gap_loop_regime_monthly.csv')))}
    raw = os.path.join(ROOT, 'raw', 'eth', 'lending-split-2026-10-08')
    snap = 0.0
    for f in ('aave_eth_aave-core', 'aave_eth_aave-prime', 'aave_eth_spark'):
        d = json.load(open(os.path.join(raw, f + '.json')))
        snap += sum(r['debt'] for r in d['reserves'] if r['sym'] == 'WETH')
    out['snapshot'] = snap
    util = {r['month']: float(r['aave_core_weth_utilization']) for r in csv.DictReader(open(os.path.join(D, 'gap_loop_regime_monthly.csv')))}
    d = json.load(open(os.path.join(raw, 'aave_eth_aave-core.json')))
    w = next(r for r in d['reserves'] if r['sym'] == 'WETH')
    util['snapshot'] = w['debt'] / w['supply']
    return out, util


# ---- carry products: collateral against dollar debt, per month -----------------------------------------------------------
def _top5(points):
    """product -> month -> (collateral ETH against dollar debt (gross), dollar debt USD) from the 7 Oct archive reads"""
    rows = list(csv.DictReader(open(os.path.join(D, 'gap_top5_risk_series.csv'))))
    px = {r['period']: float(r['value']) for r in rows if r['metric'] == 'eth_usd'}
    out = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))
    for r in rows:
        if r['value'] in ('', None):
            continue
        per = r['period']
        if r['product'] == 'liquid' and r['account'] == 'ALL':
            if r['metric'] == 'collateral_usd':
                out['liquid-eth'][per][0] += float(r['value']) / px[per]
            elif r['metric'] == 'dollar_debt_usd':
                out['liquid-eth'][per][1] += float(r['value'])
        if r['product'] == 'lido-earn' and r['account'].startswith('0x181cb55f'):  # the sub-vault that borrows dollars; 0x9938 posts USDe
            if r['metric'] == 'collateral_usd:wstETH':
                out['lido-earn'][per][0] += float(r['value']) / px[per]
            elif r['metric'] == 'dollar_debt_usd':
                out['lido-earn'][per][1] += float(r['value'])
        if r['product'] == 'avant' and r['account'] == 'ALL':
            if r['metric'] == 'collateral_usd':
                out['avant-aveth'][per][0] += float(r['value']) / px[per]
            elif r['metric'] == 'dollar_debt_usd':
                out['avant-aveth'][per][1] += float(r['value'])
    return out


def carry_parts(labels, prices, snap):
    """{product id: {label: dict(carry_lend, other_lend, carry_off, method)}} in ETH, counted once.

    carry_lend: collateral posted in a lending market against dollar debt; other_lend: the product's lending collateral
    that backs neither ETH nor dollar debt (no debt, or a month under $10k of dollar debt); carry_off: carry that does not sit
    in a lending market (YieldBasis' WETH in its Curve pool, Liquity ETH Carry's trove), the whole book in debt months."""
    snapc = json.load(open(os.path.join(OUT, 'carry_lending_snapshot.json')))['products']
    eq = json.load(open(os.path.join(D, 'economic_questions.json')))
    debt = {p['id']: {h['month']: h.get('debtUSD') or 0.0 for h in p['history']} | {snap: p['current'].get('debtUSD') or 0.0} for p in eq['products']}
    top5 = _top5(labels)
    acc, acc_v = collections.defaultdict(lambda: collections.defaultdict(list)), collections.defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(OUT, 'carry_accounts_monthly.csv'))):
        if r['product'] == 'avant-aveth':
            acc_v[(r['product'], r['venue'])][r['month']] = (float(r['collateral_eth']), float(r['dollar_debt_usd']))
        else:  # one entry per account and collateral form: (collateral ETH, dollar debt, collateral form, account)
            acc[r['product']][r['month']].append((float(r['collateral_eth']), float(r['dollar_debt_usd']), r['form'], r['account']))
    _, util = onchain_debt()
    rs = json.load(open(os.path.join(D, 'gap_rocksolid_upshift.json')))['rocksolid']
    rrate = {m['month']: m['rETH_rate'] for m in rs['monthlyBook']}
    rdebt = {h['month']: h for h in rs['dollarCarry']['debtHistory']}
    out = {}

    def once(pid, cells):
        return sum(snapc[pid]['counted_once'].get(c, 0.0) for c in cells)

    def gross(pid, cells):
        return sum(snapc[pid]['gross'].get(c, 0.0) for c in cells)

    for cid, (eid, _base) in DEC.DEBT_MONTHS.items():
        d = debt.get(eid, {}) if eid else {}
        per = {}
        for l in labels:
            dd = d.get(l, 0.0) or 0.0
            is_carry = dd >= 10000
            r = dict(carry_lend=0.0, other_lend=0.0, carry_off=0.0, method='')
            if cid in ('yieldbasis-weth', 'liquity-carry'):
                r['method'] = 'whole book in months with dollar debt (not in a lending market)'
                r['carry_off'] = None if is_carry else 0.0  # filled with the book in 03_build
            elif l == snap and cid in snapc:
                c2, c34 = once(cid, ['A2', 'B2']), once(cid, ['A3', 'A4', 'B3', 'B4'])
                r.update(carry_lend=c2 if is_carry else 0.0, other_lend=c34 + (0.0 if is_carry else c2),
                         method='lending split, product accounts counted once (snapshot)')
            elif cid in ('liquid-eth', 'lido-earn', 'avant-aveth'):
                g = top5[cid][l] if l in top5[cid] else (0.0, 0.0)
                k = once(cid, ['A2', 'B2']) / gross(cid, ['A2', 'B2'])
                coll, dd2 = g
                r['method'] = 'archive reads of the dollar-debt accounts (gap_top5_risk_series.csv)'
                if cid == 'avant-aveth':  # Aave v4 spoke and Morpho legs, read in carry_accounts_monthly.csv
                    for (c, dbt) in [acc_v[(cid, v)].get(l, (0.0, 0.0)) for v in ('aave-v4', 'morpho')]:
                        coll += c
                        dd2 += dbt
                    r['method'] = 'archive reads (Aave v3, Spark, Aave v4, Morpho); WETH counted once at the snapshot ratio'
                    is_carry = dd2 >= 10000
                r['carry_lend'] = coll * k if is_carry else 0.0
            elif cid in acc:
                # per account: carry when it owes at least $10k; WETH collateral on Aave counted once (less the part of the
                # WETH reserve that is lent out), staking-token collateral as it is
                r['method'] = 'archive reads of the product accounts (carry_accounts_monthly.csv); WETH on Aave less the reserve utilization'
                owed = collections.defaultdict(float)  # dollar debt per account (an account may post two collateral forms)
                for c, dbt, fm, a in acc[cid].get(l, []):
                    owed[a] += dbt
                for c, dbt, fm, a in acc[cid].get(l, []):
                    k = (1 - util.get(l, util['snapshot'])) if fm == 'B' else 1.0
                    if owed[a] >= 10000:
                        r['carry_lend'] += c * k
                    else:
                        r['other_lend'] += c * k
            elif cid == 'rocksolid':
                h = rdebt.get(l)
                if h and h['morpho_rETH_collateral']:
                    r['carry_lend'] = h['morpho_rETH_collateral'] * rrate.get(l, rrate['T']) if is_carry else 0.0
                    r['method'] = 'archive reads of the second strategy wallet (gap_rocksolid_upshift.json)'
                elif is_carry:  # March 2026: the USDC loan sat on Aave; collateral at the snapshot loan-to-value
                    ltv = debt[eid][snap] / (once(cid, ['A2']) * prices[snap])
                    r['carry_lend'] = dd / prices[l] / ltv
                    r['method'] = 'estimate: dollar debt over the snapshot loan-to-value'
            per[l] = r
        out[cid] = per
    return out




# ---- the layer --------------------------------------------------------------------------------------------------------
def lending_rows(dl, leftover_from):
    """lending rows of the map that make up the layer each month (leftover rows drop out from their leftover month)"""
    return {s: r for s, r in dl.items() if r['category'] == 'lending'}


def build_layer(dl, pts, prices, leftover_from, row_category):
    """per month: lending-market ETH by row and by issuer, loops, and the inputs money markets need"""
    rows = lending_rows(dl, leftover_from)
    mat, L = matrix()
    debt_on, util = onchain_debt()
    snap = pts[-1][0]
    layer = {}
    for label, pdate, _ in pts:
        pr = prices[label]
        per_row, iss_tot, shares_tot, debt_rows = {}, collections.defaultdict(float), 0.0, {}
        for slug, r in rows.items():
            br = r['per'].get(label)
            if br is None or (slug in leftover_from and label >= leftover_from[slug]):
                continue
            br = {k: v / pr for k, v in br.items()}
            iss, none, plain, shares = split_breakdown(br, row_category)
            per_row[slug] = dict(issuer=dict(iss), no_row=none, plain=plain, shares=shares, total=sum(iss.values()) + none + plain)
            for k, v in iss.items():
                iss_tot[k] += v
            shares_tot += shares
            debt_rows[slug] = borrowed_weth(slug, pdate, pr)
        # month-end ETH debt: on-chain Aave Core/Prime and Spark replace DefiLlama's Ethereum figures for aave-v3 and sparklend
        key = 'snapshot' if label == snap else label
        dsum = {}
        for slug, byc in debt_rows.items():
            v = sum(byc.values())
            if slug in ('aave-v3', 'sparklend'):
                v -= byc.get('Ethereum', 0.0)
            dsum[slug] = v
        oc = debt_on.get(key)
        aave_share = None
        if oc is not None:  # split the on-chain figure between Aave and Spark by DefiLlama's Ethereum shares
            a, s = debt_rows.get('aave-v3', {}).get('Ethereum', 0.0), debt_rows.get('sparklend', {}).get('Ethereum', 0.0)
            aave_share = a / (a + s) if a + s else 0.8
            dsum['aave-v3'] = dsum.get('aave-v3', 0.0) + oc * aave_share
            dsum['sparklend'] = dsum.get('sparklend', 0.0) + oc * (1 - aave_share)
        layer[label] = dict(rows=per_row, issuer=dict(iss_tot), shares=shares_tot, debt=dsum, debt_total=sum(dsum.values()),
                            total=sum(x['total'] for x in per_row.values()))
    # loops: the matrix at the snapshot (A1 + B1, counted once, long tail included) less product shares (tETH, savETH ...),
    # which are looped against ETH (tETH on Aave Prime and Compound, savETH on Morpho, read in the lending-split captures)
    s = layer[snap]
    loops_snap = mat['A1'] + mat['B1'] - s['shares']
    ratio = loops_snap / s['debt_total']
    for label, x in layer.items():
        x['loops'] = loops_snap if label == snap else ratio * x['debt_total']
        x['loops_by_row'] = {k: ratio * v for k, v in x['debt'].items()}
        if label == snap:  # rows sum to the matrix exactly
            f = loops_snap / sum(x['loops_by_row'].values())
            x['loops_by_row'] = {k: v * f for k, v in x['loops_by_row'].items()}
    meta = dict(matrix=mat, loops_snapshot=loops_snap, debt_snapshot=s['debt_total'], loops_per_eth_debt=ratio,
                loop_cell_collateral_over_debt=L['same_asset_loops']['collateral_native'] / L['same_asset_loops']['own_debt_native'],
                loop_equity_snapshot=L['same_asset_loops']['equity_native'],
                loop_equity_share=L['same_asset_loops']['equity_native'] / L['same_asset_loops']['collateral_native'], shares_snapshot=s['shares'],
                matrix_total=sum(mat.values()), layer_total_snapshot=s['total'] + s['shares'])
    return layer, meta
