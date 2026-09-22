"""Print markdown tables used in deepdive.md from the computed outputs (avoids hand transcription)."""
import json, os, csv
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw'); OUT = os.path.join(os.path.dirname(__file__), '..')
Y = json.load(open(os.path.join(RAW, 'analysis_yield.json'))); G = json.load(open(os.path.join(RAW, 'analysis_growth.json')))
P = lambda x: '–' if x is None else f'{100*x:.2f}'
print('### monthly yield')
print('| Month | Realized net | Borrow kBTC/RLUSD | Borrow kBTC/PYUSD | Borrow Aave USDT | RLUSD Main total (organic) | Paypal USD Main total (organic) | PRIME | PRIME Main total (organic) | Weighted spread | Organic spread | Model net on NAV (no rewards) |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for m in Y['months'][1:] + [dict(Y['since_launch'], month='Since launch (27.05–20.09)')]:
    L = lambda n, k: m[n][k]
    aave = P(L('C-AAVE', 'borrow')) if L('C-AAVE', 'debt') > 1e5 else '–'
    pm = f"{P(L('C-AAVE','deploy_total'))} ({P(L('C-AAVE','deploy_organic'))})" if L('C-AAVE', 'debt') > 1e5 else '–'
    print(f"| {m['month']} | {P(m['realized_net_apy'])} | {P(L('A-RLUSD','borrow'))} | {P(L('A-PYUSD','borrow'))} | {aave} | {P(L('A-RLUSD','deploy_total'))} ({P(L('A-RLUSD','deploy_organic'))}) | {P(L('A-PYUSD','deploy_total'))} ({P(L('A-PYUSD','deploy_organic'))}) | {P(L('B-RLUSD','deploy_total'))} | {pm} | {P(m['weighted_spread'])} | {P(m['organic_spread'])} | {P(m.get('model_net_on_nav'))} ({P(m.get('model_net_no_rewards'))}) |")
print('\n### weekly yield')
print('| Week (Mon) | Net | Borrow RLUSD | Borrow PYUSD | RLUSD Main tot/org | PYUSD Main tot/org | PRIME | W. spread | Org. spread | Debt $M | Debt/NAV | Model net (no rew.) |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for m in Y['weeks']:
    if m['week'] < '2026-05-25': continue
    L = lambda n, k: m[n][k]
    print(f"| {m['week']} | {P(m['realized_net_apy'])} | {P(L('A-RLUSD','borrow'))} | {P(L('A-PYUSD','borrow'))} | {P(L('A-RLUSD','deploy_total'))} / {P(L('A-RLUSD','deploy_organic'))} | {P(L('A-PYUSD','deploy_total'))} / {P(L('A-PYUSD','deploy_organic'))} | {P(L('B-RLUSD','deploy_total'))} | {P(m['weighted_spread'])} | {P(m['organic_spread'])} | {m['debt_total']/1e6:.0f} | {m.get('debt_to_nav',0):.2f} | {P(m.get('model_net_on_nav'))} ({P(m.get('model_net_no_rewards'))}) |")
print('\n### monthly TVL')
print('| Month | TVL end, BTC | TVL end, $M | Deposits BTC | Withdrawals BTC | Net flow BTC | Yield BTC | ΔTVL $M | = flows | + BTC price | + yield | Holders end | New depositors |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for m in G['months']:
    print(f"| {m['month']} | {m['tvl_btc_end']:,.1f} | {m['tvl_usd_end']/1e6:,.1f} | {m['deposits_btc']:,.1f} | {m['withdrawals_btc']:,.1f} | {m['net_flow_btc']:+,.1f} | {m['yield_btc']:.2f} | {m['d_tvl_usd']/1e6:+,.1f} | {m['flow_effect_usd']/1e6:+,.1f} | {m['price_effect_usd']/1e6:+,.1f} | {m['yield_effect_usd']/1e6:+,.2f} | {m['holders_end']:,} | {m['new_depositors']:,} |")
print('\n### weekly TVL')
print('| Week | TVL BTC | TVL $M | Holders | New dep. | Net flow BTC | Withdrawn BTC | Flow $M | Price $M |')
print('|---|---|---|---|---|---|---|---|---|')
for w in G['weeks']:
    if w['week'] < '2026-05-18': continue
    print(f"| {w['week']} | {w['tvl_btc_end']:,.0f} | {w['tvl_usd_end']/1e6:,.1f} | {w['holders_end']:,} | {w['new_depositors']:,} | {w['net_flow_btc']:+,.0f} | {w['withdrawals_btc']:,.0f} | {w['flow_effect_usd']/1e6:+,.1f} | {w['price_effect_usd']/1e6:+,.1f} |")
