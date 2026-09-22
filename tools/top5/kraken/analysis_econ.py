"""Operator economics (fees, Sentora downstream fees, issuer incentives) + cap-binding days + events.csv.
Output raw/analysis_econ.json, events.csv"""
import json, os, sys, math, bisect, datetime, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, '..', 'raw'); OUTD = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from dec import *
UTC = datetime.timezone.utc
def ts_of(d): return int(datetime.datetime.fromisoformat(d).replace(tzinfo=UTC).timestamp())
def dstr(t): return datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%d %H:%M')
D = load(); B = json.load(open(os.path.join(RAW, 'blocks_daily.json')))
anch = sorted((v['eth'], v['ts']) for v in B.values()); ab = [x[0] for x in anch]; at = [x[1] for x in anch]
def eth_ts(b):
    i = bisect.bisect_right(ab, b) - 1
    if i < 0: return at[0] - (ab[0] - b) * 12
    if i >= len(ab) - 1: return at[-1] + (b - ab[-1]) * 12.05
    return at[i] + (b - ab[i]) * (at[i + 1] - at[i]) / (ab[i + 1] - ab[i])
CL = json.load(open(os.path.join(RAW, 'cl_btc_rounds.json'))); clt = [x[2] for x in CL]; clp = [x[1] for x in CL]
def btc_at(t): i = bisect.bisect_right(clt, t) - 1; return clp[max(i, 0)]
S = D['snapshot']; NOW = D['now']
res = {}
# ---------------- vault fees ----------------
G = json.load(open(os.path.join(RAW, 'analysis_growth.json')))
claims = G['fees']['claimed']
fee_usd = sum(k * btc_at(ts_of(d) + 12 * 3600) for d, k in claims)
owed = G['fees']['owed_now_kbtc']
sep_acc = G['fees']['modeled_accrual_by_month_kbtc']['2026-09']
sep_days = (1789941682 - ts_of('2026-09-01')) / 86400   # last rate update used 2026-09-20 22:01
ann_kbtc = sep_acc * 365 / sep_days
px_now = btc_usd(NOW); px_snap = btc_usd(S)
tvl_now_btc = 6548.63858733 * 1.00466057
res['vault_fees'] = dict(claimed_kbtc=G['fees']['claimed_total_kbtc'], claimed_usd_at_claim=fee_usd, owed_kbtc=owed,
                         total_kbtc=G['fees']['claimed_total_kbtc'] + owed, total_usd_now=(G['fees']['claimed_total_kbtc'] + owed) * px_now,
                         sep_accrual_kbtc=sep_acc, annualized_kbtc=ann_kbtc, annualized_usd_now=ann_kbtc * px_now,
                         split_80_15_5_usd=[ann_kbtc * px_now * x for x in (0.8, 0.15, 0.05)], tvl_now_btc=tvl_now_btc, btc_now=px_now,
                         fee_as_pct_tvl=ann_kbtc / tvl_now_btc)
# ---------------- Sentora downstream fees (annualized at snapshot sizes, Sep realized organic) ----------------
Y = json.load(open(os.path.join(RAW, 'analysis_yield.json')))
sep = [m for m in Y['months'] if m['month'].startswith('2026-09')][0]
org = {'senRLUSDv2': sep['A-RLUSD']['deploy_organic'], 'senPYUSDmain': sep['A-PYUSD']['deploy_organic'],
       'senPYUSDPRIMEv2': sep['C-AAVE']['deploy_organic'], 'senPYUSDPST': sep['D-WBTCUSDT']['deploy_organic']}
fees = {'senRLUSDv2': ('perf', 0.10), 'senPYUSDmain': ('mgmt', 0.01), 'senPYUSDPRIMEv2': ('perf', 0.15), 'senPYUSDPST': ('perf', 0.15)}
kr = {'senRLUSDv2': ys(S, 'RLUSD-A') * v2(S, 'senRLUSDv2')['pps'], 'senPYUSDmain': ys(S, 'PYUSD-A') * v2(S, 'senPYUSDmain')['pps'],
      'senPYUSDPRIMEv2': ys(S, 'YS1-PRIMEMain') * v2(S, 'senPYUSDPRIMEv2')['pps'], 'senPYUSDPST': ys(S, 'YS2-PST') * v2(S, 'senPYUSDPST')['pps']}
down = {}
for v, (kind, f) in fees.items():
    ta = v2(S, v)['ta']
    if kind == 'perf':
        gross = org[v] / (1 - f); rate = gross * f
    else:
        rate = f
    down[v] = dict(kind=kind, fee=f, tvl=ta, fee_rate_on_tvl=rate, total_usd=ta * rate, kraken_position=kr[v], kraken_share=kr[v] / ta, from_kraken_usd=kr[v] * rate)
res['sentora_downstream'] = down
res['sentora_downstream_total'] = sum(x['total_usd'] for x in down.values())
res['sentora_downstream_from_kraken'] = sum(x['from_kraken_usd'] for x in down.values())
prime_hold = (ys(S, 'RLUSD-B') + ys(S, 'PYUSD-B')) * prime_rate(S)
res['hastra_50bp_on_kraken_prime'] = prime_hold * 0.005
# ---------------- issuer incentives ----------------
MC = json.load(open(os.path.join(RAW, 'merkl_campaigns.json')))
VK = {'Sentora RLUSD Main': 'senRLUSDv2', 'Paypal USD Main': 'senPYUSDmain', 'Sentora PRIME Main': 'senPYUSDPRIMEv2', 'Sentora Huma PST Main': 'senPYUSDPST'}
inc = {}
for name, v in VK.items():
    cs = [c for c in MC if c['vault'] == name and c['token'] in ('RLUSD', 'PYUSD') and not c['whitelist']]
    cs.sort(key=lambda c: c['start'])
    cur = cs[-1]; wk = cur['amount'] * 604800 / (cur['end'] - cur['start'])
    since_launch = sum(c['amount'] * max(0, min(c['end'], ts_of('2026-09-20') + 43200) - max(c['start'], ts_of('2026-05-27'))) / (c['end'] - c['start']) for c in cs)
    total = sum(c['amount'] for c in cs if c['start'] < ts_of('2026-09-21'))
    ta = v2(S, v)['ta']
    inc[v] = dict(token=cur['token'], first=dstr(cs[0]['start'])[:10], campaigns=len(cs), total_paid=total, current_weekly=wk, annual_run_rate=wk * 365 / 7,
                  budget_apr=wk * 365 / 7 / ta, tvl=ta, kraken_position=kr[v], kraken_share=kr[v] / ta, to_kraken_annual=wk * 365 / 7 * kr[v] / ta,
                  paid_since_launch_all=since_launch)
res['incentives'] = inc
tot_ann = sum(x['annual_run_rate'] for x in inc.values()); to_k = sum(x['to_kraken_annual'] for x in inc.values())
nav_snap_usd = 6492.475 * px_snap
res['incentives_total'] = dict(annual_all=tot_ann, annual_to_kraken_positions=to_k, kraken_nav_usd_snap=nav_snap_usd, per_usd_of_kraken_tvl=to_k / nav_snap_usd,
                               v2_tvl_total=sum(x['tvl'] for x in inc.values()), per_usd_of_v2_tvl=tot_ann / sum(x['tvl'] for x in inc.values()))
# realized since launch: reward income to Kraken legs from the carry model
C = json.load(open(os.path.join(RAW, 'analysis_carry.json')))
res['rewards_to_kraken_since_launch_model'] = sum(v['reward_usd'] for v in C['per_leg'].values())
res['gross_carry_since_launch_model'] = C['total_pnl_usd']
# depositor net yield $ run-rate at snapshot
res['depositor_net_runrate_usd'] = 0.0101 * nav_snap_usd
res['gross_runrate_usd'] = 0.0101 * 4 / 3 * nav_snap_usd
print(json.dumps(res, indent=1, default=str))
# ---------------- cap-binding days ----------------
CE = json.load(open(os.path.join(RAW, 'v2_cap_events.json')))
caps = collections.defaultdict(list)
for e in CE:
    if e['event'] == 'IncreaseAbsoluteCap' and e.get('newCap') and e['newCap'] < 1e12 and (e.get('kbtc') or e.get('prime')):
        caps[(e['vault'], 'kbtc' if e.get('kbtc') else 'prime')].append((eth_ts(e['block']), e['newCap'], e['block']))
res['cap_history'] = {f'{k[0]}:{k[1]}': [(dstr(t), c) for t, c, b in sorted(v)] for k, v in caps.items()}
def cap_at(key, t):
    v = [c for (tt, c, b) in sorted(caps[key]) if tt <= t]; return v[-1] if v else None
bind = {}
for key, m in [(('senRLUSDv2', 'kbtc'), 'kBTC_RLUSD'), (('senPYUSDmain', 'kbtc'), 'kBTC_PYUSD')]:
    days = []
    for k in sorted(x for x in D if x[:2] == '20'):
        mk = market(D[k], m); c = cap_at(key, ts_of(k))
        if mk and c and mk['supply'] >= 0.99 * c: days.append(k)
    bind[m] = dict(n_days_at_99pct_cap=len(days), days=days)
res['cap_binding_daily'] = bind
print(json.dumps(res['cap_history'], indent=1)); print({k: v['n_days_at_99pct_cap'] for k, v in bind.items()}, bind['kBTC_RLUSD']['days'][-10:], bind['kBTC_PYUSD']['days'][-10:])
json.dump(res, open(os.path.join(RAW, 'analysis_econ.json'), 'w'), indent=1, default=str)
