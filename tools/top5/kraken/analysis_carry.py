"""Negative-carry episodes and carry P&L by leg (daily), plus the 21 Sep 2026 live day.
Uses raw/daily_legs.json (analysis.py) and raw/accrue_events.json. Output raw/analysis_carry.json"""
import json, os, sys, math, datetime, collections, bisect
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, '..', 'raw')
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location('an', os.path.join(HERE, 'analysis.py'))
UTC = datetime.timezone.utc
DL = json.load(open(os.path.join(RAW, 'daily_legs.json')))
LEGS = ['A-RLUSD', 'B-RLUSD', 'A-PYUSD', 'B-PYUSD', 'C-AAVE', 'D-WBTCUSDT']
res = {'per_leg': {}, 'monthly_pnl': {}}
pnl_m = collections.defaultdict(lambda: collections.defaultdict(float))
for leg in LEGS:
    st = dict(days=0, neg_days_with_rewards=0, neg_days_without_rewards=0, hours_borrow_above_total=0.0, hours_borrow_above_organic=0.0,
              pnl_usd=0.0, pnl_org_usd=0.0, reward_usd=0.0, avg_debt=0.0, neg_dates_with_rewards=[])
    for r in DL:
        if r['date'] < '2026-05-27': continue
        x = r[leg]
        if not x['debt'] or x['debt'] < 1e5 or x['borrow'] is None or x['deploy_total'] is None: continue
        st['days'] += 1; st['avg_debt'] += x['debt']
        if x['borrow'] > x['deploy_total']:
            st['neg_days_with_rewards'] += 1; st['neg_dates_with_rewards'].append((r['date'], round(100 * x['borrow'], 2), round(100 * x['deploy_total'], 2)))
        if x['deploy_organic'] is not None and x['borrow'] > x['deploy_organic']: st['neg_days_without_rewards'] += 1
        st['hours_borrow_above_total'] += x['hours_above_total'] or 0
        st['hours_borrow_above_organic'] += x['hours_above_organic'] or 0
        p = x['debt'] * (x['deploy_total'] - x['borrow']) / 365
        po = x['debt'] * ((x['deploy_organic'] if x['deploy_organic'] is not None else x['deploy_total']) - x['borrow']) / 365
        st['pnl_usd'] += p; st['pnl_org_usd'] += po; st['reward_usd'] += p - po
        m = r['date'][:7]
        pnl_m[m][leg + '_total'] += p; pnl_m[m][leg + '_organic'] += po
    if st['days']: st['avg_debt'] /= st['days']
    res['per_leg'][leg] = st
res['monthly_pnl'] = {m: {k: round(v / 1e6, 3) for k, v in d.items()} for m, d in sorted(pnl_m.items())}
tot = sum(v['pnl_usd'] for v in res['per_leg'].values()); tot_o = sum(v['pnl_org_usd'] for v in res['per_leg'].values())
res['total_pnl_usd'] = tot; res['total_pnl_organic_usd'] = tot_o; res['reward_share_of_gross'] = 1 - tot_o / tot if tot else None
for leg, st in res['per_leg'].items():
    print(leg, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in st.items() if k != 'neg_dates_with_rewards'}, st['neg_dates_with_rewards'][:6])
print('TOTAL gross carry since launch $%.2fM, organic-only $%.2fM, rewards share %.1f%%' % (tot / 1e6, tot_o / 1e6, 100 * res['reward_share_of_gross']))
for m, d in res['monthly_pnl'].items():
    t = sum(v for k, v in d.items() if k.endswith('_total')); o = sum(v for k, v in d.items() if k.endswith('_organic'))
    print(m, 'total', round(t, 2), 'organic', round(o, 2), d)
# ---- 21 Sep live day (00:00 -> latest block) for kBTC/RLUSD ----
ACC = json.load(open(os.path.join(RAW, 'accrue_events.json')))
B = json.load(open(os.path.join(RAW, 'blocks_daily.json')))
anch = sorted((v['eth'], v['ts']) for v in B.values()); ab = [x[0] for x in anch]; at = [x[1] for x in anch]
def eth_ts(b):
    i = bisect.bisect_right(ab, b) - 1
    if i >= len(ab) - 1: return at[-1] + (b - ab[-1]) * 12.05
    return at[i] + (b - ab[i]) * (at[i + 1] - at[i]) / (ab[i + 1] - ab[i])
A = int(datetime.datetime(2026, 9, 21, tzinfo=UTC).timestamp())
live = []
prev = None
for (blk, li, rate, interest, tx) in ACC['rows']['kBTC_RLUSD']:
    t = eth_ts(blk)
    if prev is not None and t > A:
        live.append((max(prev, A), t, math.exp(rate / 1e18 * 365 * 86400) - 1, tx))
    prev = t
tot_s = sum(e - s for s, e, r, tx in live)
avg = sum((e - s) * r for s, e, r, tx in live) / tot_s if tot_s else None
res['sep21_kbtc_rlusd'] = dict(covered_hours=round(tot_s / 3600, 2), time_weighted_borrow_apy=avg,
                               intervals=[(datetime.datetime.fromtimestamp(s, UTC).strftime('%H:%M'), datetime.datetime.fromtimestamp(e, UTC).strftime('%H:%M'), round(100 * r, 2)) for s, e, r, tx in live])
print('21 SEP kBTC/RLUSD', res['sep21_kbtc_rlusd'])
json.dump(res, open(os.path.join(RAW, 'analysis_carry.json'), 'w'), indent=1, default=str)
