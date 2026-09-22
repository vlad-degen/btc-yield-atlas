"""Main analysis for the Kraken Bitcoin Vault deep dive (v3).
Builds weekly/monthly yield, spread, negative-carry, LTV, TVL, holder and fee series from the raw data.
Outputs: yield_weekly.csv, tvl_weekly.csv, ltv_weekly.csv, raw/analysis.json (+ monthly tables, daily series)"""
import json, os, sys, math, bisect, datetime, csv, statistics, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, '..', 'raw'); OUTD = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from dec import *
YR = 365 * 86400
UTC = datetime.timezone.utc
def ts_of(d): return int(datetime.datetime.fromisoformat(d).replace(tzinfo=UTC).timestamp())
def iso(ts): return datetime.datetime.fromtimestamp(ts, UTC).strftime('%Y-%m-%d %H:%M')
def apy_from_rate(r): return math.exp(r * YR) - 1           # r per second
def ann(ratio, dt): return ratio ** (YR / dt) - 1 if ratio and ratio > 0 and dt > 0 else None

B = json.load(open(os.path.join(RAW, 'blocks_daily.json')))
D = load()
SNAP_TS = 1789905600; NOW_BLOCK = D['now']['block']
# ---- ETH block -> timestamp (linear between daily anchors; anchors are exact) ----
anch = sorted((v['eth'], v['ts']) for k, v in B.items())
ab = [x[0] for x in anch]; at = [x[1] for x in anch]
def eth_ts(b):
    i = bisect.bisect_right(ab, b) - 1
    if i < 0: return at[0] - (ab[0] - b) * 12
    if i >= len(ab) - 1: return at[-1] + (b - ab[-1]) * 12
    return at[i] + (b - ab[i]) * (at[i + 1] - at[i]) / (ab[i + 1] - ab[i])
T_NOW = eth_ts(NOW_BLOCK)
# ---- accountant rate (Ink) ----
RH = json.load(open(os.path.join(HERE, '..', '..', '..', 'onchain-kraken', 'ink_rate_history.json')))
rts = [r['ts'] for r in RH]; rvs = [r['new'] / 1e8 for r in RH]
def vault_rate(ts):
    i = bisect.bisect_right(rts, ts) - 1
    return 1.0 if i < 0 else rvs[i]
def vault_rate_point(ts):
    """rate with the timestamp of the update that set it (for exact annualization)"""
    i = bisect.bisect_right(rts, ts) - 1
    return (1.0, rts[0]) if i < 0 else (rvs[i], rts[i])
# ---- borrow-rate intervals from AccrueInterest ----
ACC = json.load(open(os.path.join(RAW, 'accrue_events.json')))
INTV = {}
for m, rows in ACC['rows'].items():
    iv = []; prev_t = None
    for (blk, li, rate, interest, tx) in rows:
        t = eth_ts(blk)
        if prev_t is not None and t > prev_t:
            iv.append((prev_t, t, rate))
        prev_t = t
    INTV[m] = iv
def avg_rate(m, A, Bt):
    """time-weighted avg per-second borrow rate over [A,B) and covered seconds"""
    num = 0.0; den = 0.0
    for (s, e, r) in INTV[m]:
        if e <= A or s >= Bt: continue
        o = min(e, Bt) - max(s, A); num += r * o / 1e18; den += o
    return (num / den if den else None), den
def borrow_apy(m, A, Bt):
    r, cov = avg_rate(m, A, Bt)
    return apy_from_rate(r) if r is not None else None
def time_above(m, A, Bt, thr_apy):
    """seconds in [A,B) with interval-average borrow APY above thr"""
    s_ = 0.0
    for (s, e, r) in INTV[m]:
        if e <= A or s >= Bt: continue
        if apy_from_rate(r / 1e18) > thr_apy: s_ += min(e, Bt) - max(s, A)
    return s_
def max_rate(m, A, Bt):
    mx = None
    for (s, e, r) in INTV[m]:
        if e <= A or s >= Bt: continue
        v = apy_from_rate(r / 1e18)
        if mx is None or v > mx[0]: mx = (v, s, e)
    return mx
# ---- daily keyed helpers ----
DAYS = sorted(k for k in D if k[:2] == '20')
def row_at(ts):
    k = datetime.datetime.fromtimestamp(ts, UTC).date().isoformat()
    return D.get(k)
def pps_series(v):
    return {k: (v2(D[k], v) or {}).get('pps') for k in DAYS}
def organic(v, A, Bt):
    ra, rb = row_at(A), row_at(Bt)
    if not ra or not rb: return None
    xa, xb = v2(ra, v), v2(rb, v)
    if not xa or not xb or not xa['pps'] or not xb['pps'] or xa['ta'] < 1000: return None
    return ann(xb['pps'] / xa['pps'], Bt - A)
def prime_apy(A, Bt):
    ra, rb = row_at(A), row_at(Bt)
    if not ra or not rb or not ra.get('prime_feed') or not rb.get('prime_feed'): return None
    pa, pb = prime_rate(ra), prime_rate(rb)
    # use feed updatedAt for the time base
    ta, tb = ra['prime_feed'][1], rb['prime_feed'][1]
    return ann(pb / pa, tb - ta) if pa and pb and tb > ta else None
def aave_usdt_apy(A, Bt):
    ra, rb = row_at(A), row_at(Bt)
    if not ra or not rb: return None
    xa, xb = aave(ra), aave(rb)
    if not xa['vbi'] or not xb['vbi'] or xb['lu'] <= xa['lu']: return None
    return apy_from_rate(math.log(xb['vbi'] / xa['vbi']) / (xb['lu'] - xa['lu']))
# ---- Merkl rewards ----
MC = json.load(open(os.path.join(RAW, 'merkl_campaigns.json')))
VKEY = {'Sentora RLUSD Main': 'senRLUSDv2', 'Paypal USD Main': 'senPYUSDmain', 'Sentora PRIME Main': 'senPYUSDPRIMEv2', 'Sentora Huma PST Main': 'senPYUSDPST'}
CAMPS = collections.defaultdict(list)
for c in MC:
    if c['vault'] not in VKEY or c['token'] not in ('RLUSD', 'PYUSD'): continue
    if c['whitelist']: continue  # whitelisted test campaigns (98 RLUSD, 0 USDC) excluded
    cap = None
    dm = (c.get('params') or {}).get('distributionMethodParameters') or {}
    if dm.get('distributionMethod') == 'MAX_APR':
        cap = float(dm['distributionSettings']['apr'])
    CAMPS[VKEY[c['vault']]].append((c['start'], c['end'], c['amount'], cap))
def reward_apr(v, A, Bt):
    """budget-based reward APR over [A,B): sum of campaign emissions in window / avg TVL, capped at MAX_APR"""
    ra, rb = row_at(A), row_at(Bt)
    tvl = [x['ta'] for x in (v2(ra, v), v2(rb, v)) if x]
    # use daily TVL average inside window
    ks = [k for k in DAYS if A <= ts_of(k) <= Bt]
    tv = [v2(D[k], v)['ta'] for k in ks if v2(D[k], v)]
    tvl_avg = sum(tv) / len(tv) if tv else (sum(tvl) / len(tvl) if tvl else None)
    if not tvl_avg or tvl_avg < 1e5: return None
    em = 0.0; capw = []
    for (s, e, amt, cap) in CAMPS[v]:
        o = min(e, Bt) - max(s, A)
        if o <= 0: continue
        em += amt * o / (e - s); capw.append((cap, o))
    apr = em / tvl_avg * YR / (Bt - A)
    caps = [c for c, o in capw if c]
    if caps: apr = min(apr, max(caps))
    return apr
# ---- weekly grid ----
WEEKS = []
d = datetime.date(2026, 4, 20)
while d <= datetime.date(2026, 9, 14):
    WEEKS.append(d); d += datetime.timedelta(days=7)
def wk_bounds(w):
    A = ts_of(w.isoformat()); return A, A + 7 * 86400
LEGS = [  # name, debt source, borrow market or 'aave', deployment
    ('A-RLUSD', 'RLUSD-1', 'kBTC_RLUSD', 'senRLUSDv2'),
    ('B-RLUSD', 'RLUSD-2', 'kBTC_RLUSD', 'PRIME'),
    ('A-PYUSD', 'PYUSD-1', 'kBTC_PYUSD', 'senPYUSDmain'),
    ('B-PYUSD', 'PYUSD-2', 'kBTC_PYUSD', 'PRIME'),
    ('C-AAVE', 'aave', 'aave', 'senPYUSDPRIMEv2'),
    ('D-WBTCUSDT', 'WBTC-USDT', 'WBTC_USDT', 'senPYUSDPST'),
]
def debt_at(row, src):
    if src == 'aave': return aave(row)['debt']
    p = position(row, src); return p['debt'] if p else 0.0
def deploy_yield(dep, A, Bt):
    if dep == 'PRIME':
        y = prime_apy(A, Bt); return y, y, 0.0
    o = organic(dep, A, Bt); r = reward_apr(dep, A, Bt) or 0.0
    return ((o + r) if o is not None else None), o, r
def borrow_leg(bm, A, Bt):
    return aave_usdt_apy(A, Bt) if bm == 'aave' else borrow_apy(bm, A, Bt)
def nav_usd(ts):
    ink = json.load(open(os.path.join(RAW, 'ink_daily.json'))) if not hasattr(nav_usd, 'c') else nav_usd.c
    nav_usd.c = ink
    k = datetime.datetime.fromtimestamp(ts - 1, UTC).date().isoformat()
    for r in ink:
        if r['date'] == k: return r['tvl_btc']
    return None
INK = json.load(open(os.path.join(RAW, 'ink_daily.json')))
INKD = {r['date']: r for r in INK}
def tvl_btc_at(ts):  # end of previous day == value at 00:00 of ts
    k = datetime.datetime.fromtimestamp(ts - 1, UTC).date().isoformat()
    r = INKD.get(k); return r['tvl_btc'] if r else 0.0
def fee_gross_mult(ts): return 1.25 if ts < ts_of('2026-08-24') else 4 / 3   # net -> gross (2500 bps / 3333 bps on net)

def window_metrics(A, Bt):
    ra, rb = row_at(A), row_at(Bt)
    out = {}
    ra_, ta_ = vault_rate_point(A); rb_, tb_ = vault_rate_point(Bt)
    out['realized_net_apy'] = ann(rb_ / ra_, tb_ - ta_) if tb_ > ta_ else None
    tot_debt = 0.0; wsum = 0.0; osum = 0.0; gross_nav = 0.0
    btc_px = [btc_usd(r) for r in (ra, rb) if r and btc_usd(r)]
    px = sum(btc_px) / len(btc_px) if btc_px else None
    for (name, src, bm, dep) in LEGS:
        da = debt_at(ra, src) if ra else 0.0; db = debt_at(rb, src) if rb else 0.0
        debt = (da + db) / 2
        b = borrow_leg(bm, A, Bt); tot, org, rew = deploy_yield(dep, A, Bt)
        out[name] = dict(debt=debt, borrow=b, deploy_total=tot, deploy_organic=org, deploy_reward=rew,
                         spread=(tot - b) if (tot is not None and b is not None) else None,
                         spread_org=(org - b) if (org is not None and b is not None) else None)
        if debt > 1e5 and out[name]['spread'] is not None:
            tot_debt += debt; wsum += debt * out[name]['spread']; osum += debt * out[name]['spread_org']
    out['debt_total'] = tot_debt
    out['weighted_spread'] = wsum / tot_debt if tot_debt else None
    out['organic_spread'] = osum / tot_debt if tot_debt else None
    nav_btc = (tvl_btc_at(A) + tvl_btc_at(Bt)) / 2
    out['nav_btc'] = nav_btc; out['btc_px'] = px
    if nav_btc and px:
        out['debt_to_nav'] = tot_debt / (nav_btc * px)
        out['model_gross_on_nav'] = wsum / (nav_btc * px)
        out['model_gross_on_nav_no_rewards'] = osum / (nav_btc * px)
        out['model_net_on_nav'] = out['model_gross_on_nav'] / fee_gross_mult((A + Bt) / 2)
        out['model_net_no_rewards'] = out['model_gross_on_nav_no_rewards'] / fee_gross_mult((A + Bt) / 2)
    return out
res = {'weeks': [], 'months': []}
for w in WEEKS:
    A, Bt = wk_bounds(w)
    m = window_metrics(A, Bt); m['week'] = w.isoformat(); res['weeks'].append(m)
MONTHS = [('2026-04', ts_of('2026-04-20'), ts_of('2026-05-01')), ('2026-05', ts_of('2026-05-01'), ts_of('2026-06-01')),
          ('2026-06', ts_of('2026-06-01'), ts_of('2026-07-01')), ('2026-07', ts_of('2026-07-01'), ts_of('2026-08-01')),
          ('2026-08', ts_of('2026-08-01'), ts_of('2026-09-01')), ('2026-09*', ts_of('2026-09-01'), ts_of('2026-09-21'))]
for (lab, A, Bt) in MONTHS:
    m = window_metrics(A, Bt); m['month'] = lab; res['months'].append(m)
# since-launch & snapshot-window
res['since_launch'] = window_metrics(ts_of('2026-05-27'), ts_of('2026-09-20'))
# ---- write yield_weekly.csv ----
def P(x, n=2): return '' if x is None else round(100 * x, n)
with open(os.path.join(OUTD, 'yield_weekly.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['week', 'realized_net_apy', 'borrow_rlusd', 'borrow_pyusd', 'depl_rlusd_total', 'depl_rlusd_organic', 'depl_pyusd_total',
                'depl_pyusd_organic', 'prime', 'weighted_spread', 'organic_spread',
                'borrow_aave_usdt', 'borrow_morpho_wbtc_usdt', 'depl_prime_main_total', 'depl_prime_main_organic', 'depl_pst_total', 'depl_pst_organic',
                'debt_A_RLUSD_musd', 'debt_B_RLUSD_musd', 'debt_A_PYUSD_musd', 'debt_B_PYUSD_musd', 'debt_C_AAVE_musd', 'debt_D_WBTCUSDT_musd',
                'debt_to_nav', 'model_gross_on_nav', 'model_net_on_nav', 'model_net_no_rewards'])
    for m in res['weeks']:
        L = lambda n, k: m[n][k]
        w.writerow([m['week'], P(m['realized_net_apy']), P(L('A-RLUSD', 'borrow')), P(L('A-PYUSD', 'borrow')), P(L('A-RLUSD', 'deploy_total')),
                    P(L('A-RLUSD', 'deploy_organic')), P(L('A-PYUSD', 'deploy_total')), P(L('A-PYUSD', 'deploy_organic')), P(L('B-RLUSD', 'deploy_total')),
                    P(m['weighted_spread']), P(m['organic_spread']), P(L('C-AAVE', 'borrow')), P(L('D-WBTCUSDT', 'borrow')),
                    P(L('C-AAVE', 'deploy_total')), P(L('C-AAVE', 'deploy_organic')), P(L('D-WBTCUSDT', 'deploy_total')), P(L('D-WBTCUSDT', 'deploy_organic')),
                    *[round(m[n]['debt'] / 1e6, 2) for n in ['A-RLUSD', 'B-RLUSD', 'A-PYUSD', 'B-PYUSD', 'C-AAVE', 'D-WBTCUSDT']],
                    round(m.get('debt_to_nav', 0), 3) if m.get('debt_to_nav') else '', P(m.get('model_gross_on_nav')), P(m.get('model_net_on_nav')), P(m.get('model_net_no_rewards'))])
    f.write('# APY in %. week = Monday 00:00 UTC to next Monday. realized_net_apy from Ink accountant exchange rate. borrow = time-weighted Morpho AccrueInterest prevBorrowRate (kBTC markets), Aave v3 USDT variableBorrowIndex.\n')
    f.write('# depl_*_organic = Sentora V2 share-price growth (net of V2 fees); depl_*_total = organic + Merkl reward APR (weekly campaign budget / avg V2 totalAssets, capped at MAX_APR 3.9%). prime = Chainlink PRIME/wYLDS feed growth.\n')
    f.write('# weighted_spread / organic_spread = debt-weighted (deploy - borrow) over all legs with debt > $0.1M (A/B kBTC legs, Aave USDT -> Sentora PRIME Main, Morpho WBTC/USDT -> Huma PST Main).\n')
json.dump(res, open(os.path.join(RAW, 'analysis_yield.json'), 'w'), indent=1, default=str)

# ---- stability ----
wk_net = [m['realized_net_apy'] for m in res['weeks'] if m['realized_net_apy'] is not None and m['week'] >= '2026-05-25']
mo_net = [m['realized_net_apy'] for m in res['months'] if m['month'] not in ('2026-04', '2026-05')]
stab = dict(weekly_mean=statistics.mean(wk_net), weekly_stdev=statistics.stdev(wk_net), weekly_min=min(wk_net), weekly_max=max(wk_net),
            worst_week=min((m for m in res['weeks'] if m['week'] >= '2026-05-25'), key=lambda m: m['realized_net_apy'])['week'],
            best_week=max((m for m in res['weeks'] if m['week'] >= '2026-05-25'), key=lambda m: m['realized_net_apy'])['week'],
            monthly_values=mo_net, monthly_stdev=statistics.stdev(mo_net), n_weeks=len(wk_net))
# daily realized (for worst day) using accountant updates
upd = [(r['ts'], r['old'] / 1e8, r['new'] / 1e8) for r in RH]
res['stability'] = stab
print('STABILITY', json.dumps(stab, indent=1))

# ---- negative carry: daily ----
neg = []
daily_rows = []
for k in DAYS:
    A = ts_of(k); Bt = A + 86400
    if k < '2026-05-20' or Bt > T_NOW: continue
    rowd = dict(date=k)
    # 7-day trailing deployment yields ending at B (smoother than 1-day share price)
    A7 = Bt - 7 * 86400
    for (name, src, bm, dep) in LEGS:
        debt = debt_at(D[k], src) if D.get(k) else 0.0
        b = borrow_leg(bm, A, Bt)
        tot, org, rew = deploy_yield(dep, A7, Bt)
        mx = max_rate(bm, A, Bt) if bm != 'aave' else None
        rowd[name] = dict(debt=debt, borrow=b, deploy_total=tot, deploy_organic=org, max_intraday=mx[0] if mx else None,
                          hours_above_total=(time_above(bm, A, Bt, tot) / 3600 if (bm != 'aave' and tot is not None) else None),
                          hours_above_organic=(time_above(bm, A, Bt, org) / 3600 if (bm != 'aave' and org is not None) else None))
        if debt > 1e5 and b is not None and tot is not None:
            if b > tot or b > (org if org is not None else 9):
                neg.append(dict(date=k, leg=name, debt_musd=round(debt / 1e6, 2), borrow=round(100 * b, 2), deploy_total=round(100 * tot, 2),
                                deploy_organic=round(100 * org, 2) if org is not None else None, negative_with_rewards=b > tot,
                                negative_without_rewards=(org is not None and b > org)))
    daily_rows.append(rowd)
res['neg_days'] = neg
json.dump(daily_rows, open(os.path.join(RAW, 'daily_legs.json'), 'w'), default=str)
# intraday spike episodes (kBTC markets) with borrow APY > 6% (roughly above RLUSD Main total yield)
spikes = []
for m in ['kBTC_RLUSD', 'kBTC_PYUSD', 'WBTC_USDT']:
    cur = None
    for (s, e, r) in INTV[m]:
        v = apy_from_rate(r / 1e18)
        if s < ts_of('2026-05-20'): continue
        if v > 0.06:
            if cur and s - cur['end'] < 1800: cur['end'] = e; cur['max'] = max(cur['max'], v); cur['secs'] += e - s
            else:
                if cur: spikes.append(cur)
                cur = dict(market=m, start=s, end=e, max=v, secs=e - s)
    if cur: spikes.append(cur)
res['spikes'] = [dict(market=x['market'], start=iso(x['start']), end=iso(x['end']), hours=round(x['secs'] / 3600, 2), max_apy=round(100 * x['max'], 2)) for x in spikes]
# share of time each kBTC market's borrow APY exceeded thresholds since launch
A0, B0 = ts_of('2026-05-27'), T_NOW
res['time_above'] = {m: {f'>{int(t*100)}%': round(100 * time_above(m, A0, B0, t) / (B0 - A0), 2) for t in (0.04, 0.05, 0.06, 0.08, 0.10)} for m in ['kBTC_RLUSD', 'kBTC_PYUSD', 'WBTC_USDT']}
print('TIME ABOVE', res['time_above'])
print('SPIKES', len(res['spikes']))
for s_ in res['spikes'][:60]: print(s_)
json.dump(res, open(os.path.join(RAW, 'analysis_yield.json'), 'w'), indent=1, default=str)
print('NEG DAYS', len(neg))
cnt = collections.Counter((n['leg'], n['negative_with_rewards'], n['negative_without_rewards']) for n in neg)
print(cnt)
