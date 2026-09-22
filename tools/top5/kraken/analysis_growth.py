"""TVL growth (weekly/monthly, BTC and USD, flows vs price vs yield decomposition), holder count over time,
monthly net inflows, public-milestone cross-check, flow drivers, and operator fee economics.
Outputs: tvl_weekly.csv, raw/analysis_growth.json"""
import json, os, sys, math, bisect, datetime, csv, statistics, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, '..', 'raw'); OUTD = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from dec import *
UTC = datetime.timezone.utc
def ts_of(d): return int(datetime.datetime.fromisoformat(d).replace(tzinfo=UTC).timestamp())
D = load()
INK = json.load(open(os.path.join(RAW, 'ink_daily.json')))
INKD = {r['date']: r for r in INK}
CL = json.load(open(os.path.join(RAW, 'cl_btc_rounds.json'))); clt = [x[2] for x in CL]; clp = [x[1] for x in CL]
def btc_at(t):
    i = bisect.bisect_right(clt, t) - 1; return clp[max(i, 0)]
def eod_px(date): return btc_at(ts_of(date) + 86400 - 1)
res = {}
# ---------------- daily TVL ----------------
days = [r['date'] for r in INK if r['date'] >= '2026-04-09']
for k in days:
    r = INKD[k]; r['btc_usd_eod'] = eod_px(k); r['tvl_usd'] = r['tvl_btc'] * r['btc_usd_eod']
# ---------------- weekly ----------------
def agg(d0, d1):
    """window [d0, d1) of dates; start value = end of day before d0"""
    ks = [k for k in days if d0 <= k < d1]
    prev = (datetime.date.fromisoformat(d0) - datetime.timedelta(days=1)).isoformat()
    s = INKD.get(prev, dict(tvl_btc=0.0, holders=0, supply_shares=0.0, rate_eod=1.0, btc_usd_eod=eod_px(prev), tvl_usd=0.0))
    e = INKD[ks[-1]]
    dep = sum(INKD[k]['dep_btc'] for k in ks); wd = sum(INKD[k]['burn_btc'] for k in ks); req = sum(INKD[k]['req_btc'] for k in ks)
    flow_btc = dep - wd
    # yield in BTC: change in BTC TVL not explained by flows (shares valued at the rate prevailing at mint/burn)
    yld_btc = e['tvl_btc'] - s['tvl_btc'] - flow_btc
    p0 = s.get('btc_usd_eod') or eod_px(prev); p1 = e['btc_usd_eod']
    d_usd = e['tvl_btc'] * p1 - s['tvl_btc'] * p0
    price_eff = s['tvl_btc'] * (p1 - p0)
    flow_usd = sum((INKD[k]['dep_btc'] - INKD[k]['burn_btc']) * INKD[k]['btc_usd_eod'] for k in ks)
    flow_eff = flow_btc * p1; yld_eff = yld_btc * p1
    newdep = sum(INKD[k]['new_depositors'] for k in ks); depn = sum(INKD[k]['dep_n'] for k in ks)
    return dict(start=d0, end=d1, tvl_btc_start=s['tvl_btc'], tvl_btc_end=e['tvl_btc'], btc_usd_start=p0, btc_usd_end=p1,
                tvl_usd_start=s['tvl_btc'] * p0, tvl_usd_end=e['tvl_btc'] * p1, deposits_btc=dep, withdrawals_btc=wd, withdraw_requests_btc=req,
                net_flow_btc=flow_btc, yield_btc=yld_btc, d_tvl_usd=d_usd, flow_effect_usd=flow_eff, price_effect_usd=price_eff, yield_effect_usd=yld_eff,
                flow_usd_at_daily_px=flow_usd, holders_end=e['holders'], new_depositors=newdep, deposit_txs=depn,
                avg_deposit_btc=dep / depn if depn else None)
weeks = []
d = datetime.date(2026, 4, 6)
while d <= datetime.date(2026, 9, 14):
    w = agg(d.isoformat(), (d + datetime.timedelta(days=7)).isoformat()); w['week'] = d.isoformat(); weeks.append(w); d += datetime.timedelta(days=7)
res['weeks'] = weeks
months = []
for lab, d0, d1 in [('2026-04', '2026-04-01', '2026-05-01'), ('2026-05', '2026-05-01', '2026-06-01'), ('2026-06', '2026-06-01', '2026-07-01'),
                    ('2026-07', '2026-07-01', '2026-08-01'), ('2026-08', '2026-08-01', '2026-09-01'), ('2026-09 (to 20th)', '2026-09-01', '2026-09-21')]:
    m = agg(max(d0, days[0]), d1); m['month'] = lab; months.append(m)
res['months'] = months
tot = agg('2026-04-09', '2026-09-21'); tot['label'] = 'since first deposit (2026-04-09) to 2026-09-20 end'
res['total'] = tot
launch = agg('2026-05-27', '2026-09-21'); launch['label'] = 'since public launch 2026-05-27'; res['since_launch'] = launch
with open(os.path.join(OUTD, 'tvl_weekly.csv'), 'w', newline='') as f:
    cols = ['week', 'tvl_btc_end', 'btc_usd_end', 'tvl_usd_end_m', 'holders_end', 'new_depositors', 'deposit_txs', 'deposits_btc', 'withdrawals_btc',
            'withdraw_requests_btc', 'net_flow_btc', 'yield_btc', 'd_tvl_usd_m', 'flow_effect_usd_m', 'price_effect_usd_m', 'yield_effect_usd_m', 'avg_deposit_btc']
    wr = csv.writer(f); wr.writerow(cols)
    for w in weeks:
        wr.writerow([w['week'], round(w['tvl_btc_end'], 2), round(w['btc_usd_end']), round(w['tvl_usd_end'] / 1e6, 2), w['holders_end'], w['new_depositors'], w['deposit_txs'],
                     round(w['deposits_btc'], 2), round(w['withdrawals_btc'], 2), round(w['withdraw_requests_btc'], 2), round(w['net_flow_btc'], 2), round(w['yield_btc'], 3),
                     round(w['d_tvl_usd'] / 1e6, 2), round(w['flow_effect_usd'] / 1e6, 2), round(w['price_effect_usd'] / 1e6, 2), round(w['yield_effect_usd'] / 1e6, 3),
                     round(w['avg_deposit_btc'], 4) if w['avg_deposit_btc'] else ''])
    f.write('# week = Monday 00:00 UTC to next Monday; values at week end. TVL BTC = Ink share supply x accountant rate (all shares live on Ink; Ethereum supply 0).\n')
    f.write('# USD at Chainlink BTC/USD (Ethereum) end of week. deposits = mints x rate at mint; withdrawals = burns by the solver x rate at burn; requests = transfers into the BoringOnChainQueue.\n')
    f.write('# d_tvl_usd = flow_effect (net flow BTC x end price) + price_effect (start BTC TVL x change in BTC price) + yield_effect (BTC growth from the exchange rate x end price).\n')
    f.write('# holders = addresses with non-zero balance (excl. queue/solver/zero). new_depositors = first-ever mint to that address.\n')
for w in weeks: print(w['week'], round(w['tvl_btc_end'], 1), round(w['tvl_usd_end'] / 1e6, 1), w['holders_end'], round(w['net_flow_btc'], 1), w['new_depositors'])
for m in months: print(m['month'], round(m['tvl_btc_end'], 1), round(m['tvl_usd_end'] / 1e6, 1), 'net', round(m['net_flow_btc'], 1), 'dep', round(m['deposits_btc'], 1), 'wd', round(m['withdrawals_btc'], 1),
                       'dUSD', round(m['d_tvl_usd'] / 1e6, 1), 'flow', round(m['flow_effect_usd'] / 1e6, 1), 'px', round(m['price_effect_usd'] / 1e6, 1), 'yld', round(m['yield_effect_usd'] / 1e6, 2), 'holders', m['holders_end'], 'new', m['new_depositors'])
print('TOTAL', {k: (round(v, 2) if isinstance(v, float) else v) for k, v in tot.items()})
# ---------------- public milestones cross-check ----------------
MIL = [('2026-05-27', 'Veda/Cointelegraph: $30M in 10 hours (launch day)', 30e6), ('2026-05-29', 'Sentora on X: BTC vault > $70M', 70e6),
       ('2026-06-01', 'Kraken on X: "Over $100M"', 100e6), ('2026-06-10', 'Veda blog: BTC vault > $100M, 12,000+ users', 100e6),
       ('2026-06-16', 'Veda on X: > $220M in < 3 weeks', 220e6), ('2026-07-31', 'Sentora case study (as of July): $320M+', 320e6),
       ('2026-08-14', 'Payward Q2 release: ~ $400M deposits', 400e6)]
mil = []
for dte, lab, v in MIL:
    r = INKD[dte]; prev = INKD[(datetime.date.fromisoformat(dte) - datetime.timedelta(days=1)).isoformat()]
    mil.append(dict(date=dte, claim=lab, claim_usd_m=v / 1e6, onchain_tvl_btc_eod=round(r['tvl_btc'], 1), onchain_tvl_usd_eod_m=round(r['tvl_usd'] / 1e6, 1),
                    onchain_holders_eod=r['holders'], onchain_prev_day_usd_m=round(prev['tvl_usd'] / 1e6, 1)))
res['milestones'] = mil
for m in mil: print(m)
# launch-day intraday: deposits in first 10 hours of 2026-05-27 (launch hour unknown -> report hourly cumulative)
tr = json.load(open(os.path.join(RAW, 'share_transfers.json')))['rows']
RH = json.load(open(os.path.join(HERE, '..', '..', '..', 'onchain-kraken', 'ink_rate_history.json')))
rts = [r['ts'] for r in RH]; rvs = [r['new'] / 1e8 for r in RH]
def vrate(ts):
    i = bisect.bisect_right(rts, ts) - 1; return 1.0 if i < 0 else rvs[i]
SNAP_TS, SNAP_INK = 1789905600, 56407189
Z = '0x' + '0' * 40
hourly = collections.OrderedDict()
wallets = set()
for (blk, li, fr, to, v, tx) in tr:
    t = SNAP_TS + (blk - SNAP_INK)
    if ts_of('2026-05-26') <= t < ts_of('2026-05-29') and fr == Z:
        h = datetime.datetime.fromtimestamp(t, UTC).strftime('%m-%d %H:00')
        hourly.setdefault(h, [0.0, 0, set()]); hourly[h][0] += v / 1e8 * vrate(t); hourly[h][1] += 1; hourly[h][2].add(to)
cum = 0.0; cumw = set(); launch_hours = []
for h, (b, n, ws) in hourly.items():
    cum += b; cumw |= ws
    launch_hours.append(dict(hour=h, dep_btc=round(b, 2), cum_btc=round(cum, 2), cum_usd_m=round(cum * 74000 / 1e6, 1), deposits=n, cum_wallets=len(cumw)))
res['launch_hours'] = launch_hours
print('LAUNCH HOURS'); [print(x) for x in launch_hours[:40]]
# ---------------- flow drivers ----------------
yw = {m['week']: m for m in json.load(open(os.path.join(RAW, 'analysis_yield.json')))['weeks']}
xs = []; ys_ = []; zs = []
for w in weeks:
    if w['week'] < '2026-06-01': continue
    prevw = (datetime.date.fromisoformat(w['week']) - datetime.timedelta(days=7)).isoformat()
    if prevw in yw and yw[prevw]['realized_net_apy'] is not None:
        xs.append(yw[prevw]['realized_net_apy']); ys_.append(w['net_flow_btc']); zs.append(w['btc_usd_end'] / w['btc_usd_start'] - 1)
def corr(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b)); den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else None
res['flow_corr'] = dict(n=len(xs), corr_flow_vs_prev_week_apy=corr(xs, ys_), corr_flow_vs_same_week_btc_return=corr(zs, ys_))
print('CORR', res['flow_corr'])
# daily: deposits vs BTC daily return
dd = [(INKD[k]['dep_btc'], INKD[k]['burn_btc'], eod_px(k) / eod_px((datetime.date.fromisoformat(k) - datetime.timedelta(days=1)).isoformat()) - 1) for k in days if '2026-06-01' <= k <= '2026-09-20']
res['flow_corr']['daily_deposits_vs_btc_return'] = corr([x[2] for x in dd], [x[0] for x in dd])
res['flow_corr']['daily_withdrawals_vs_btc_return'] = corr([x[2] for x in dd], [x[1] for x in dd])
print('CORR daily', res['flow_corr'])
# ---------------- fees ----------------
AL = json.load(open(os.path.join(RAW, 'accountant_logs.json')))
claims = sorted([(x['ts'], int(dict(x['params'])['amount']) / 1e8) for x in AL if x['decoded'] and x['decoded'].startswith('FeesClaimed')])
# supply at each rate update (replay)
sup_ts = []; s = 0
for (blk, li, fr, to, v, tx) in tr:
    t = SNAP_TS + (blk - SNAP_INK)
    if fr == Z: s += v
    elif to == Z: s -= v
    sup_ts.append((t, s))
stt = [x[0] for x in sup_ts]
def supply_at(t):
    i = bisect.bisect_right(stt, t) - 1; return sup_ts[i][1] / 1e8 if i >= 0 else 0.0
hwm = 1.0; accr = collections.defaultdict(float); total_acc = 0.0; prev_t = None
T_FEE = ts_of('2026-08-24') + 12 * 3600 + 32 * 60
for r in RH:
    new = r['new'] / 1e8; t = r['ts']
    pf = 0.25 if t < T_FEE else 0.3333
    if new > hwm:
        fee = (new - hwm) * supply_at(t) * pf
        accr[datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m')] += fee; total_acc += fee; hwm = new
res['fees'] = dict(claimed=[(datetime.datetime.fromisoformat(c[0].replace('Z', '+00:00')).strftime('%Y-%m-%d'), round(c[1], 4)) for c in claims],
                   claimed_total_kbtc=sum(c[1] for c in claims), owed_now_kbtc=0.27286948, modeled_accrual_total_kbtc=total_acc,
                   modeled_accrual_by_month_kbtc={k: round(v, 4) for k, v in accr.items()})
print('FEES', res['fees'])
json.dump(res, open(os.path.join(RAW, 'analysis_growth.json'), 'w'), indent=1, default=str)
