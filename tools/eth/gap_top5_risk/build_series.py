"""Decode positions_raw.json + reuse data/eth/economic-dollar-loans.csv (leg debt and quoted APR) and write
data/eth/gap_top5_risk_series.csv (long format)."""
import json, csv, collections
from glib import *
from collect_positions import POOL_ACCTS, MARKETS, MORPHO_ACCTS, TROVES, DEST
P = json.load(open(RAW / 'positions_raw.json'))
D30 = json.load(open(RAW / 'dest_30d_raw.json'))
YEAR = 365 * 86400
EBISU_MCR = 1.2  # raw/eth/2026-10-04/strict-products/trove_final_rpc.json MCR() = 1.2e18
YB_CRIT = 9 / 16  # LEVAMM get_x0: critical debt/coll_value for L=2 (p_amm = 9/16 p_o)
YB_SAFE = 8.5 / 16  # MAX_SAFE_DEBT for L=2
LOANDEC = {'RLUSD': 18, 'USDC': 6, 'PYUSD': 6}
rows = []
def add(prod, acct, period, metric, value, unit, source):
    if value is None: return
    rows.append(dict(product=prod, account=acct, period=period, metric=metric, value=value, unit=unit, source=source))
SRC_ARCH = 'archive eth_call @ month-end block (raw/eth/gap-2026-10-07/top5-risk/positions_raw.json)'
SRC_LEG = 'data/eth/economic-dollar-loans.csv (reused leg debt and quoted APR)'
SRC_LEGS = 'archive eth_call per reserve (raw/eth/gap-2026-10-07/top5-risk/aave_legs_raw.json)'
DOLLARS = {'USDC', 'USDT', 'PYUSD', 'USDS', 'DAI', 'USDe', 'RLUSD', 'GHO', 'USDtb', 'FRAX', 'crvUSD', 'LUSD', 'pyUSD', 'USDG'}
LEGS = {mm['month']: mm['accounts'] for mm in json.load(open(RAW / 'aave_legs_raw.json'))['months']}
legs = collections.defaultdict(list)
for r in csv.DictReader(open(ROOT / 'data/eth/economic-dollar-loans.csv')):
    per = 'T' if r['month'] == 'snapshot' else r['month']
    legs[(r['id'], per)].append(r)
def get(m, *key):
    for r in m['reads']:
        if tuple(r['key']) == key: return r['result']
prev = {}
agg = collections.defaultdict(lambda: collections.defaultdict(float))
for m in P['months']:
    per, b, ts = m['month'], m['block'], m['timestamp']
    ethusd = words(get(m, 'ethusd'))[0] / 1e8
    add('all', 'chainlink:ETH/USD', per, 'eth_usd', ethusd, 'USD', SRC_ARCH)
    # Aave / Spark accounts: account totals from getUserAccountData, legs from aave_legs_raw.json
    LM = {(a['product'], a['venue'], a['account']): a for a in LEGS.get(per, [])}
    for prod, venue, pool, acct in POOL_ACCTS:
        w = words(get(m, 'pool', prod, venue, acct))
        coll, debt, lt, hf = w[0] / 1e8, w[1] / 1e8, w[3] / 1e4, w[5] / 1e18
        a = f'{acct}@{venue}V3'
        if debt <= 0 and coll <= 0: continue
        L = LM.get((prod, venue, acct), {'legs': []})['legs']
        stable_loop = acct == '0x9938a09fea37ba681a1bd53d33ddde2debec1da0'
        add(prod, a, per, 'collateral_usd', coll, 'USD (protocol oracle)', SRC_ARCH)
        for l in L:
            if l['collateral'] and l['supplied'] > 0:
                add(prod, a, per, 'collateral_usd:' + l['symbol'], l['supplied'] * l['priceUSD'], 'USD (protocol oracle)', SRC_LEGS)
        add(prod, a, per, 'debt_usd_account_total', debt, 'USD (protocol oracle)', SRC_ARCH)
        dl = [l for l in L if l['debt'] > 0 and l['symbol'] in DOLLARS]
        ddebt = sum(l['debt'] * l['priceUSD'] for l in dl)
        for l in L:
            if l['debt'] > 0:
                add(prod, a, per, 'debt_usd:' + l['symbol'], l['debt'] * l['priceUSD'], 'USD (protocol oracle)', SRC_LEGS)
                add(prod, a, per, 'borrow_rate:' + l['symbol'], l['variableBorrowAPR'], 'APR fraction (reserve variable rate)', SRC_LEGS)
        add(prod, a, per, 'dollar_debt_usd', ddebt, 'USD (protocol oracle)', SRC_LEGS)
        prior = sum(float(r['debtUSD']) for r in legs[(prod, per)] if r['account'] == acct and r['venue'] == venue and float(r['debtUSD'] or 0) > 0)
        add(prod, a, per, 'dollar_debt_usd_prior_dataset', prior, 'USD', SRC_LEG)
        if ddebt > 0:
            add(prod, a, per, 'borrow_rate_debt_weighted', sum(l['debt'] * l['priceUSD'] * l['variableBorrowAPR'] for l in dl) / ddebt, 'APR fraction', SRC_LEGS)
        if debt > 0:
            add(prod, a, per, 'ltv', debt / coll if coll else None, 'fraction', SRC_ARCH)
            add(prod, a, per, 'health_factor', hf, 'ratio', SRC_ARCH)
            add(prod, a, per, 'dollar_share_of_account_debt', min(ddebt / debt, 1.0), 'fraction', 'derived')
        add(prod, a, per, 'liquidation_threshold', lt, 'fraction (weighted)', SRC_ARCH)
        if stable_loop:
            add(prod, a, per, 'classification', 1, 'flag: USDe/sUSDe e-mode stable loop, excluded from ALL', 'getUserConfiguration/getUserEMode')
            continue
        if ddebt > 0:
            share = min(ddebt / debt, 1.0) if debt else 1
            g = agg[(prod, per)]
            g['coll'] += coll * share; g['debt'] += ddebt; g['liqcoll'] += coll * lt * share
            for l in dl: g['rate_num'] += l['debt'] * l['priceUSD'] * l['variableBorrowAPR']; g['rate_den'] += l['debt'] * l['priceUSD']
    # Morpho
    for sym, mid in MARKETS.items():
        mk = get(m, 'market', sym); orc = get(m, 'oracle', sym)
        if not mk or not orc: continue
        tsa, tss, tba, tbs = words(mk)[:4]; price = words(orc)[0]
        lltv = P['morphoParams'][sym]['lltv']
        for acct in MORPHO_ACCTS:
            ps = get(m, 'pos', sym, acct)
            if not ps: continue
            ss, bs, col = words(ps)[:3]
            debt = (bs * tba / tbs if tbs else 0) / 10 ** LOANDEC[sym]
            cv = col * price / 1e36 / 10 ** LOANDEC[sym]
            if debt < 1 and cv < 1: continue
            a = f'{acct}@Morpho:weETH/{sym}'
            add('liquid', a, per, 'collateral_usd', cv, 'USD (Morpho oracle, loan-token units)', SRC_ARCH)
            add('liquid', a, per, 'collateral_weeth', col / 1e18, 'weETH', SRC_ARCH)
            add('liquid', a, per, 'dollar_debt_usd', debt, 'USD (loan-token face, stored index)', SRC_ARCH)
            add('liquid', a, per, 'liquidation_threshold', lltv, 'fraction (LLTV)', SRC_ARCH)
            if debt >= 1:
                add('liquid', a, per, 'ltv', debt / cv, 'fraction', SRC_ARCH)
                add('liquid', a, per, 'health_factor', lltv * cv / debt, 'ratio (LLTV x collateral / debt)', 'derived')
                lr = [r for r in legs[('liquid', per)] if r['account'] == acct and r['venue'] == 'Morpho' and r['symbol'] == sym]
                if lr and lr[0]['apr']:
                    add('liquid', a, per, 'borrow_rate_debt_weighted', float(lr[0]['apr']), 'APR fraction', SRC_LEG)
                    agg[('liquid', per)]['rate_num'] += debt * float(lr[0]['apr']); agg[('liquid', per)]['rate_den'] += debt
                agg[('liquid', per)]['coll'] += cv; agg[('liquid', per)]['debt'] += debt; agg[('liquid', per)]['liqcoll'] += cv * lltv
    # YieldBasis
    st = get(m, 'yb', 'get_state()'); vo = get(m, 'yb', 'value_oracle()'); rt = get(m, 'yb', 'rate()')
    if st and vo:
        coll, debt, x0 = words(st)[:3]; p_o, val = words(vo)[:2]
        cv = p_o * coll / 1e36; debt /= 1e18
        if debt > 0:
            a = '0x5f8d24f33cc5a1d5d1bf012261e6a2214c92233c@YB-LEVAMM (LT 0x2b9c9f3b)'
            apr = words(rt)[0] * YEAR / 1e18
            add('yieldbasis', a, per, 'collateral_usd', cv, 'crvUSD (LP x LP oracle)', SRC_ARCH)
            add('yieldbasis', a, per, 'dollar_debt_usd', debt, 'crvUSD face', SRC_ARCH)
            add('yieldbasis', a, per, 'ltv', debt / cv, 'fraction', SRC_ARCH)
            add('yieldbasis', a, per, 'liquidation_threshold', YB_CRIT, 'fraction (LEVAMM critical debt/value, L=2; no liquidation engine)', 'LEVAMM source get_x0')
            add('yieldbasis', a, per, 'max_safe_ltv', YB_SAFE, 'fraction (deposit-time MAX_SAFE_DEBT)', 'LEVAMM source __init__')
            add('yieldbasis', a, per, 'target_ltv', 0.5, 'fraction ((L-1)/L)', 'LEVAMM source')
            add('yieldbasis', a, per, 'health_factor', YB_CRIT * cv / debt, 'ratio (critical LTV / LTV)', 'derived')
            add('yieldbasis', a, per, 'net_value_usd', val / 1e18, 'crvUSD (value_oracle)', SRC_ARCH)
            add('yieldbasis', a, per, 'borrow_rate_debt_weighted', apr, 'APR fraction (AMM rate())', SRC_ARCH)
            agg[('yieldbasis', per)].update(coll=cv, debt=debt, liqcoll=cv * YB_CRIT, rate_num=debt * apr, rate_den=debt)
    # Ebisu troves
    pr = get(m, 'ebprice')
    if pr:
        price = words(pr)[0] / 1e18
        for tid in TROVES:
            h = get(m, 'trove', tid)
            if not h: continue
            w = words(h); debt, coll, rate = w[0] / 1e18, w[1] / 1e18, w[6] / 1e18
            if debt <= 0: continue
            cv = coll * price
            a = f'0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c@Ebisu-wstETH trove {tid[:10]}'
            add('liquity', a, per, 'collateral_usd', cv, 'USD (branch lastGoodPrice)', SRC_ARCH)
            add('liquity', a, per, 'collateral_wsteth', coll, 'wstETH', SRC_ARCH)
            add('liquity', a, per, 'dollar_debt_usd', debt, 'ebUSD face', SRC_ARCH)
            add('liquity', a, per, 'ltv', debt / cv, 'fraction', SRC_ARCH)
            add('liquity', a, per, 'liquidation_threshold', 1 / EBISU_MCR, 'fraction (1/MCR)', 'trove_final_rpc.json MCR')
            add('liquity', a, per, 'health_factor', cv / debt / EBISU_MCR, 'ratio (ICR / MCR)', 'derived')
            add('liquity', a, per, 'borrow_rate_debt_weighted', rate, 'APR fraction (trove annualInterestRate)', SRC_ARCH)
            g = agg[('liquity', per)]; g['coll'] += cv; g['debt'] += debt; g['liqcoll'] += cv / EBISU_MCR; g['rate_num'] += debt * rate; g['rate_den'] += debt
    # destinations
    dest = {}
    for name, (addr, sd, ad) in DEST.items():
        h = get(m, 'dest', name)
        if h: dest[name] = words(h)[0] / 10 ** ad
    h = get(m, 'dest', 'earnUSD_report')
    if h and words(h)[0]: dest['earnUSD'] = 1e18 / words(h)[0] * 1e12  # oracle priceD18 = shares per USDT unit -> USDT per share
    h = get(m, 'dest', 'curve_ebUSD_USDC_vp')
    if h: dest['curve_ebUSD_USDC'] = words(h)[0] / 1e18
    h = get(m, 'ybvp')
    if h: dest['yb_curve_WETH_crvUSD_lp'] = words(h)[0] / 1e18
    for name, v in dest.items():
        add('destinations', name, per, 'share_price', v, 'asset per share', SRC_ARCH)
        if name in prev and prev[name][1] > 0:
            p0, v0, t0 = prev[name][0], prev[name][1], prev[name][2]
            add('destinations', name, per, 'parking_yield_apr_month', (v / v0 - 1) * YEAR / (ts - t0), 'APR fraction (simple, since previous sample)', 'derived from share_price')
        prev[name] = (per, v, ts)
    # aggregates
    for (prod, pp), g in list(agg.items()):
        if pp != per or g['debt'] < 1000: continue
        add(prod, 'ALL', per, 'collateral_usd', g['coll'], 'USD (dollar-debt share of account collateral)', 'derived')
        add(prod, 'ALL', per, 'dollar_debt_usd', g['debt'], 'USD', 'derived')
        add(prod, 'ALL', per, 'ltv', g['debt'] / g['coll'], 'fraction', 'derived')
        add(prod, 'ALL', per, 'liquidation_threshold', g['liqcoll'] / g['coll'], 'fraction (collateral-weighted)', 'derived')
        add(prod, 'ALL', per, 'health_factor', g['liqcoll'] / g['debt'], 'ratio (aggregate)', 'derived')
        if g['rate_den'] > 0: add(prod, 'ALL', per, 'borrow_rate_debt_weighted', g['rate_num'] / g['rate_den'], 'APR fraction', 'derived')
# trailing 30d to T
d30 = {r['key']: r['result'] for r in D30['reads']}
Tm = P['months'][-1]
for name, (addr, sd, ad) in DEST.items():
    v0 = words(d30[name])[0] / 10 ** ad; v1 = words(get(Tm, 'dest', name))[0] / 10 ** ad
    add('destinations', name, 'T', 'parking_yield_apr_30d', (v1 / v0 - 1) * YEAR / (Tm['timestamp'] - D30['timestamp']), 'APR fraction (2026-09-02 -> T)', 'raw dest_30d_raw.json + positions_raw.json')
for name, key, f in [('earnUSD', 'earnUSD_report', lambda w: 1e30 / w), ('curve_ebUSD_USDC', 'curve_ebUSD_USDC_vp', lambda w: w / 1e18), ('yb_curve_WETH_crvUSD_lp', 'yb_lp_vp', lambda w: w / 1e18)]:
    v0 = f(words(d30[key])[0])
    v1 = [r for r in rows if r['product'] == 'destinations' and r['account'] == name and r['period'] == 'T' and r['metric'] == 'share_price'][0]['value']
    add('destinations', name, 'T', 'parking_yield_apr_30d', (v1 / v0 - 1) * YEAR / (Tm['timestamp'] - D30['timestamp']), 'APR fraction (2026-09-02 -> T)', 'raw dest_30d_raw.json + positions_raw.json')
# Avant destination: savUSD/avUSD Chainlink exchange-rate feed (timestamps = feed updatedAt)
EX = json.load(open(RAW / 'extra_raw.json'))
SRC_SAV = 'Chainlink SAVUSD/AVUSD feed 0x9fbb7d07 latestRoundData @ block (raw extra_raw.json)'
pv = None
for x in EX['savusd']:
    if x['rate'] is None or x['period'] == 'T-30d': continue
    add('destinations', 'savUSD', x['period'], 'share_price', x['rate'], 'avUSD per savUSD', SRC_SAV)
    if pv: add('destinations', 'savUSD', x['period'], 'parking_yield_apr_month', (x['rate'] / pv['rate'] - 1) * YEAR / (x['updatedAt'] - pv['updatedAt']), 'APR fraction (simple, between feed updates)', 'derived')
    pv = x
a, z = [x for x in EX['savusd'] if x['period'] == 'T-30d'][0], [x for x in EX['savusd'] if x['period'] == 'T'][0]
add('destinations', 'savUSD', 'T', 'parking_yield_apr_30d', (z['rate'] / a['rate'] - 1) * YEAR / (z['updatedAt'] - a['updatedAt']), 'APR fraction (feed updates ~2026-09-02 -> T)', 'derived')
# product -> destination mapping rows
for prod, dests in {'liquid': 'senRLUSDv2|senPYUSDPRIMEv2|stcUSD|PRIME', 'lido-earn': 'earnUSD', 'avant': 'savUSD (Avalanche, per issuer portfolio)', 'liquity': 'curve_ebUSD_USDC (+Uniswap V4 BOLD/USDC, not measured)', 'yieldbasis': 'yb_curve_WETH_crvUSD_lp (borrowed crvUSD is the LP stable leg, not parked)'}.items():
    add(prod, 'ALL', 'T', 'destination_map', dests, 'text', 'docs + fixed-block holdings (ladder_T_raw.json)')
with open(ROOT / 'data/eth/gap_top5_risk_series.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['product', 'account', 'period', 'metric', 'value', 'unit', 'source']); w.writeheader()
    for r in rows:
        r = dict(r); r['value'] = repr(round(r['value'], 8)) if isinstance(r['value'], float) else r['value']; w.writerow(r)
print(len(rows))
