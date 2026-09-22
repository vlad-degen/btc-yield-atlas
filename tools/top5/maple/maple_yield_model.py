#!/usr/bin/env python3
"""Estimate the gross staking yield earned on-chain by the Maple-attributed cluster, per month and overall.
Gross yield (BTC terms) = sum(CORE rewards claimed * CORE/USD on claim date) / sum(BTC staked * BTC/USD per day) * 365.
This EXCLUDES: CORE price P&L on the ~40-50M CORE inventory, put-option payoffs from Core Foundation, USDC borrow cost,
Maple fees. Claims are lumpy, so monthly values are indicative; the overall figure is more robust."""
import csv, datetime, collections
R = '../raw'
px = {r['date']: (float(r['core_usd']), float(r['btc_usd'])) for r in csv.DictReader(open(f'{R}/prices_daily.csv')) if r['core_usd'] and r['btc_usd']}
st = {r['date']: float(r['cluster_btc']) for r in csv.DictReader(open(f'{R}/core/maple_cluster_daily.csv'))}
rw = list(csv.DictReader(open(f'{R}/core/maple_rewards.csv')))
m = collections.defaultdict(lambda: dict(core_btcleg=0, core_coreleg=0, usd_rew=0, btc_days=0, usd_btc_days=0, core_px=[], btc_px=[]))
for d, b in st.items():
    if d not in px or b == 0: continue
    k = d[:7]; m[k]['btc_days'] += b; m[k]['usd_btc_days'] += b * px[d][1]
for d in px:
    k = d[:7]
    if k in m: m[k]['core_px'].append(px[d][0]); m[k]['btc_px'].append(px[d][1])
for r in rw:
    d = r['date']; k = d[:7]; c = float(r['core_reward'])
    if r['leg'].startswith('BTC'): m[k]['core_btcleg'] += c
    else: m[k]['core_coreleg'] += c
    m[k]['usd_rew'] += c * px.get(d, (0, 0))[0]
out = []
T = dict(usd_rew=0, usd_btc_days=0, core=0, btc_days=0)
for k in sorted(m):
    x = m[k]
    if not x['btc_days'] and not x['usd_rew']: continue
    days = len(x['core_px']) or 1
    avg_btc = x['btc_days'] / days
    gross = (x['usd_rew'] / x['usd_btc_days'] * 365) if x['usd_btc_days'] else None
    out.append([k, round(avg_btc, 1), round(x['core_btcleg']), round(x['core_coreleg']), round(sum(x['core_px'])/days, 4), round(x['usd_rew']), f"{gross*100:.2f}" if gross is not None else ''])
    T['usd_rew'] += x['usd_rew']; T['usd_btc_days'] += x['usd_btc_days']; T['core'] += x['core_btcleg'] + x['core_coreleg']; T['btc_days'] += x['btc_days']
with open(f'{R}/core/maple_yield_model.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['month', 'avg_btc_staked', 'core_rewards_btc_leg', 'core_rewards_core_leg', 'avg_core_usd', 'rewards_usd_at_claim', 'implied_gross_apr_pct_btc_terms'])
    w.writerows(out)
for o in out: print(o)
print('TOTAL rewards CORE', round(T['core']), 'USD', round(T['usd_rew']), 'BTC-days', round(T['btc_days']), 'overall gross APR %', round(T['usd_rew']/T['usd_btc_days']*365*100, 2))
