"""Compact inputs for the atlas layer of the ETH reader (tools/eth/site/atlas.js): risk history, repayment ladder and
reward payers of the five main carry products, from the 7 October archive reads (data/eth/gap_top5_*).
Writes data/eth/atlas_top5_risk.json. Offline."""
import calendar, csv, datetime, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; D = ROOT / 'data/eth'
DEST = {'liquid': ['senRLUSDv2', 'senPYUSDPRIMEv2', 'stcUSD'], 'lido-earn': ['earnUSD'], 'avant': ['savUSD'],
        'liquity': ['curve_ebUSD_USDC'], 'yieldbasis': ['yb_curve_WETH_crvUSD_lp']}


def ts(period):
    if period == 'T':
        return 1790985599
    y, m = map(int, period.split('-'))
    return int(datetime.datetime(y, m, calendar.monthrange(y, m)[1], 23, 59, 59, tzinfo=datetime.UTC).timestamp())


def run():
    rows = list(csv.DictReader((D / 'gap_top5_risk_series.csv').open()))
    ladder = json.loads((D / 'gap_top5_liquidity_ladder.json').read_text())['products']
    rewards = json.loads((D / 'gap_top5_rewards.json').read_text())
    out = {'source': 'data/eth/gap_top5_risk_series.csv, gap_top5_liquidity_ladder.json, gap_top5_rewards.json (archive reads, 7 Oct 2026)', 'products': {}}
    for pid in DEST:
        def ser(metric, account='ALL', product=pid):
            pts = sorted((ts(r['period']), float(r['value'])) for r in rows
                         if r['product'] == product and r['metric'] == metric and (account is None or r['account'] == account) and r['value'] not in ('', None))
            return pts
        p = {m: ser(m) for m in ('health_factor', 'ltv', 'liquidation_threshold', 'borrow_rate_debt_weighted', 'dollar_debt_usd', 'collateral_usd')}
        if not p['health_factor']:
            p = {m: ser(m, None) for m in p}
        p['parking'] = {d: ser('parking_yield_apr_month', d, 'destinations') for d in DEST[pid]}
        p['parking30d'] = {d: (ser('parking_yield_apr_30d', d, 'destinations') or [[None, None]])[-1][1] for d in DEST[pid]}
        lad = ladder.get(pid, {})
        p['ladder'] = [{'tier': t['tier'], 'usd': t['usd'], 'pct': t['pct'], 'ethReleased': t.get('ethReleased'), 'detail': t.get('detail', '')} for t in lad.get('tiers', [])]
        p['dollarDebtUSD'] = lad.get('dollarDebtUSD')
        r = rewards.get(pid) if isinstance(rewards.get(pid), dict) else None
        if r:
            p['rewards'] = [{k: c.get(k) for k in ('opportunity', 'token', 'creator', 'creatorMerklTags', 'rewardAPRatT', 'liquidRewardUSDperYearAtT', 'amount')} for c in r.get('activeCampaignsAtT', [])]
            p['rewardsNote'] = {k: v for k, v in r.items() if k != 'activeCampaignsAtT' and not isinstance(v, (list, dict))}
        out['products'][pid] = p
    bpath = D / 'gap_borrowers.csv'
    if bpath.exists():
        out['borrowers'] = {r['address'].lower(): {k: r[k] for k in ('who', 'kind', 'pooled_product', 'product_if_any', 'dollar_debt_usd_T', 'weth_debt_T', 'destination_of_dollars', 'evidence')} for r in csv.DictReader(bpath.open())}
    lr = D / 'gap_loop_regime_monthly.csv'
    if lr.exists():
        out['loopRegime'] = [{k: r[k] for k in ('month', 'aave_core_weth_borrow_apr_month_avg', 'steth_holder_apr_month', 'spread_steth_minus_aave_core_borrow_month_avg', 'aave_core_weth_utilization', 'total_weth_debt_eth', 'lido_gross_cl_apr', 'lido_gross_el_apr')} for r in csv.DictReader(lr.open())]
    (D / 'atlas_top5_risk.json').write_text(json.dumps(out, indent=1) + '\n')
    print('Atlas top-5 risk:', {k: len(v['health_factor']) for k, v in out['products'].items()})


if __name__ == '__main__':
    run()
