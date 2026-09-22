"""Risk section: LTV per position over time (daily/weekly + intraday path from Chainlink rounds and position events),
delever reaction lags (price-driven and rate-spike-driven), stress test at the snapshot, liquidity ladder.
Outputs: ltv_weekly.csv, liquidity_ladder.csv, raw/analysis_risk.json"""
import json, os, sys, math, bisect, datetime, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, '..', 'raw'); OUTD = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from dec import *
UTC = datetime.timezone.utc
def ts_of(d): return int(datetime.datetime.fromisoformat(d).replace(tzinfo=UTC).timestamp())
def iso(ts): return datetime.datetime.fromtimestamp(ts, UTC).strftime('%Y-%m-%d %H:%M')
D = load(); B = json.load(open(os.path.join(RAW, 'blocks_daily.json')))
LLTV = 0.86; TGT_HF = 1.2113; TGT_LTV = LLTV / TGT_HF
POS = ['RLUSD-1', 'RLUSD-2', 'PYUSD-1', 'PYUSD-2']
DAYS = sorted(k for k in D if k[:2] == '20')
res = {}
# ---------------- weekly LTV table ----------------
mondays = [d for d in DAYS if datetime.date.fromisoformat(d).weekday() == 0 and d >= '2026-05-25']
rows = []
for k in mondays + ['snapshot', 'now']:
    r = D[k]; px = btc_usd(r)
    rec = dict(date=k if k not in ('snapshot', 'now') else {'snapshot': '2026-09-20 12:00 (snapshot)', 'now': '2026-09-21 22:33 (live)'}[k], btc_usd=round(px))
    tc = td = tcu = 0
    for p in POS:
        x = position(r, p)
        rec[p + '_coll_kbtc'] = round(x['coll'], 2); rec[p + '_debt_musd'] = round(x['debt'] / 1e6, 2)
        rec[p + '_ltv'] = round(100 * x['ltv'], 2) if x['ltv'] else ''
        rec[p + '_hf'] = round(x['hf'], 3) if x['hf'] else ''
        rec[p + '_liq_px'] = round(x['liq_px']) if x['liq_px'] else ''
        rec[p + '_drop_to_liq_pct'] = round(100 * (1 - x['liq_px'] / x['px']), 1) if x['liq_px'] else ''
        tc += x['coll']; td += x['debt']; tcu += x['coll_usd'] or 0
    rec['kbtc_total_ltv'] = round(100 * td / tcu, 2) if tcu else ''
    a = aave(r)
    rec['aave_wbtc'] = round(a['awbtc'], 2); rec['aave_usdt_debt_musd'] = round(a['debt'] / 1e6, 2)
    rec['aave_hf'] = round(a['hf'], 3) if a['hf'] and a['hf'] < 100 else ''
    rec['aave_liq_px'] = round(px / a['hf']) if a['hf'] and a['hf'] < 100 else ''
    w = position(r, 'WBTC-USDT')
    rec['morpho_wbtc_usdt_ltv'] = round(100 * w['ltv'], 2) if w and w['ltv'] else ''
    rec['morpho_wbtc_usdt_debt_musd'] = round(w['debt'] / 1e6, 2) if w else ''
    rows.append(rec)
with open(os.path.join(OUTD, 'ltv_weekly.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    f.write('# Monday 00:00 UTC archive reads (Ethereum). LTV = debt / (collateral x Morpho oracle price); HF = 0.86/LTV; liq_px = BTC price at which LTV hits LLTV 86%.\n')
    f.write('# Target HF 1.2113 => target LTV %.2f%%. Aave leg: WBTC collateral vs USDT variable debt, liquidation threshold 78%%, liq_px = BTC/HF.\n' % (100 * TGT_LTV))
res['ltv_weekly'] = rows

# ---------------- intraday LTV path ----------------
CL = json.load(open(os.path.join(RAW, 'cl_btc_rounds.json')))   # [block, px, updatedAt]
clt = [x[2] for x in CL]; clp = [x[1] for x in CL]
def btc_at(t):
    i = bisect.bisect_right(clt, t) - 1
    return clp[max(i, 0)]
LM = json.load(open(os.path.join(HERE, '..', '..', '..', 'onchain-kraken', 'lm_history.json')))
ev = collections.defaultdict(list)
for x in LM: ev[x['pos']].append(x)
for p in ev: ev[p].sort(key=lambda x: x['ts'])
paths = {}
excursions = []
for p in POS:
    pts = []
    for k in DAYS:
        if k < '2026-05-20': continue
        r = D[k]; x = position(r, p)
        if not x or x['coll'] < 1: continue
        t0 = ts_of(k); t1 = t0 + 86400
        coll, debt = x['coll'], x['debt']
        # stable/oracle ratio correction (oracle = BTC/USD / stable/USD)
        corr = x['px'] / btc_usd(r) if btc_usd(r) else 1.0
        day_ev = [e for e in ev[p] if t0 <= e['ts'] < t1]
        times = sorted(set([t for t in clt if t0 <= t < t1] + [e['ts'] for e in day_ev] + [t0]))
        ei = 0
        for t in times:
            while ei < len(day_ev) and day_ev[ei]['ts'] <= t:
                e = day_ev[ei]
                if e['type'] == 'SupplyCollateral': coll += e['amt']
                elif e['type'] == 'WithdrawCollateral': coll -= e['amt']
                elif e['type'] == 'Borrow': debt += e['amt']
                elif e['type'] == 'Repay': debt -= e['amt']
                ei += 1
            px = btc_at(t) * corr
            if coll > 0: pts.append((t, debt / (coll * px), coll, debt, px))
    paths[p] = pts
    # excursions above target LTV and above 75% / 80%
    for thr in (TGT_LTV, 0.75, 0.80):
        cur = None
        for (t, ltv, c, d_, px) in pts:
            if ltv > thr and d_ > 1e6:
                if cur is None: cur = dict(pos=p, thr=round(thr, 4), start=t, peak=ltv, peak_t=t, px_start=px)
                elif ltv > cur['peak']: cur['peak'] = ltv; cur['peak_t'] = t
            elif cur is not None:
                cur['end'] = t; cur['hours'] = (t - cur['start']) / 3600
                excursions.append(cur); cur = None
        if cur: cur['end'] = None; cur['hours'] = None; excursions.append(cur)
res['max_ltv_intraday'] = {p: max(((ltv, iso(t)) for (t, ltv, c, d_, px) in paths[p] if d_ > 1e6), default=None) for p in POS}
def hours_above(p, thr):
    s = 0.0; pts = paths[p]
    for i in range(len(pts) - 1):
        if pts[i][1] > thr and pts[i][3] > 1e6: s += pts[i + 1][0] - pts[i][0]
    return s / 3600
res['hours_above'] = {p: {f'>{int(round(100*thr))}%': round(hours_above(p, thr), 1) for thr in (TGT_LTV, 0.75, 0.78, 0.80)} for p in POS}
long_exc = [dict(pos=e['pos'], thr=e['thr'], start=iso(e['start']), end=iso(e['end']) if e['end'] else None, hours=round(e['hours'], 1) if e['hours'] else None,
                 peak_ltv=round(100 * e['peak'], 2), peak_at=iso(e['peak_t'])) for e in excursions if e['thr'] >= 0.75 or (e['hours'] or 99) > 24]
res['excursions'] = long_exc
print('MAX LTV', res['max_ltv_intraday']); print('HOURS ABOVE', res['hours_above'])
for e in long_exc: print(e)

# ---------------- repay events and reaction lags ----------------
ACCI = json.load(open(os.path.join(RAW, 'analysis_yield.json')))['spikes']
reps = []
for p in POS:
    for e in ev[p]:
        if e['type'] != 'Repay' or e['amt'] < 5e4: continue
        t = e['ts']
        # LTV just before repay, BTC drawdown vs 7-day high, and nearest preceding rate spike in that market
        prev = [x for x in paths[p] if x[0] < t]
        ltv_b = prev[-1][1] if prev else None
        hi7 = max(btc_at(tt) for tt in range(t - 7 * 86400, t, 3600))
        dd7 = btc_at(t) / hi7 - 1
        # time LTV first exceeded target in the preceding 14 days (continuous excursion leading to the repay)
        first_above = None
        for (tt, l, c, d_, px) in reversed(prev):
            if tt < t - 14 * 86400: break
            if l > TGT_LTV: first_above = tt
            else: break
        mk = 'kBTC_RLUSD' if p.startswith('RLUSD') else 'kBTC_PYUSD'
        sp = [s for s in ACCI if s['market'] == mk and ts_of(s['start'][:10]) <= t and datetime.datetime.strptime(s['start'], '%Y-%m-%d %H:%M').replace(tzinfo=UTC).timestamp() <= t
              and datetime.datetime.strptime(s['start'], '%Y-%m-%d %H:%M').replace(tzinfo=UTC).timestamp() > t - 2 * 86400]
        wc = [x for x in ev[p] if x['type'] == 'WithdrawCollateral' and abs(x['ts'] - t) < 3600]
        reps.append(dict(pos=p, time=iso(t), repay_musd=round(e['amt'] / 1e6, 2), ltv_before=round(100 * ltv_b, 2) if ltv_b else None,
                         btc=round(btc_at(t)), btc_vs_7d_high=round(100 * dd7, 1),
                         above_target_since=iso(first_above) if first_above else None,
                         lag_h_from_target_breach=round((t - first_above) / 3600, 1) if first_above else None,
                         rate_spike=(sp[-1] if sp else None), lag_h_from_spike=(round((t - datetime.datetime.strptime(sp[-1]['start'], '%Y-%m-%d %H:%M').replace(tzinfo=UTC).timestamp()) / 3600, 1) if sp else None),
                         with_collateral_withdrawal=round(sum(x['amt'] for x in wc), 2) if wc else 0))
reps.sort(key=lambda r: r['time'])
res['repays'] = reps
for r in reps: print(r)

# ---------------- stress test at snapshot ----------------
S = D['snapshot']; px0 = btc_usd(S)
stress = []
for shock in (0.0, 0.10, 0.20, 0.30, 0.40):
    rec = dict(shock=f'-{int(shock*100)}%', btc=round(px0 * (1 - shock)))
    need = 0.0; liq = []
    for p in POS:
        x = position(S, p); pxn = x['px'] * (1 - shock)
        ltv = x['debt'] / (x['coll'] * pxn)
        tgt_debt = x['coll'] * pxn * LLTV / TGT_HF
        rep = max(0.0, x['debt'] - tgt_debt)
        rec[p] = dict(ltv=round(100 * ltv, 1), liquidatable=ltv >= LLTV, repay_to_target_musd=round(rep / 1e6, 2))
        need += rep
        if ltv >= LLTV: liq.append(p)
    a = aave(S); hf = a['hf'] * (1 - shock)
    tgt_debt_a = a['coll_usd'] * (1 - shock) * a['liq_th'] / 1.20   # Aave leg operates at HF ~1.20 (observed)
    rep_a = max(0.0, a['debt_usd'] - tgt_debt_a)
    rec['AAVE'] = dict(hf=round(hf, 3), liquidatable=hf < 1, repay_to_hf1_20_musd=round(rep_a / 1e6, 2))
    if hf < 1: liq.append('AAVE')
    w = position(S, 'WBTC-USDT'); ltvw = w['debt'] / (w['coll'] * w['px'] * (1 - shock))
    rec['WBTC-USDT'] = dict(ltv=round(100 * ltvw, 1), liquidatable=ltvw >= LLTV)
    rec['repay_needed_musd'] = round((need + rep_a) / 1e6, 2); rec['liquidatable'] = liq
    # liquidation bonus cost if liquidated in full before action (Morpho LIF at 86% LLTV = 1/(0.3*0.86+0.7))
    lif = min(1.15, 1 / (0.3 * LLTV + 0.7)) - 1
    rec['max_liq_penalty_musd'] = round(sum(position(S, p)['debt'] for p in POS if p in liq) * lif / 1e6 + (a['debt_usd'] * 0.05 if 'AAVE' in liq else 0) / 1e6, 2)
    stress.append(rec)
res['stress'] = stress
for s in stress: print(s)

# ---------------- liquidity ladder at snapshot ----------------
L = json.load(open(os.path.join(RAW, 'ladder_26018583.json')))['vaults']
def v2_access(sym):
    v = L[sym]; return v['idle'] + sum(m['v2_withdrawable'] for m in v['markets']), v
claims = {}
ys = {'RLUSD-A': ys(S, 'RLUSD-A'), 'PYUSD-A': ys(S, 'PYUSD-A'), 'RLUSD-B': ys(S, 'RLUSD-B'), 'PYUSD-B': ys(S, 'PYUSD-B'), 'YS1': ys(S, 'YS1-PRIMEMain'), 'YS2': ys(S, 'YS2-PST')}
claim_rl = ys['RLUSD-A'] * v2(S, 'senRLUSDv2')['pps']; claim_py = ys['PYUSD-A'] * v2(S, 'senPYUSDmain')['pps']
claim_pm = ys['YS1'] * v2(S, 'senPYUSDPRIMEv2')['pps']; claim_pst = ys['YS2'] * v2(S, 'senPYUSDPST')['pps']
prime_px = prime_rate(S)
claim_prime = (ys['RLUSD-B'] + ys['PYUSD-B']) * prime_px
debts = {p: position(S, p)['debt'] for p in POS}; debt_aave = aave(S)['debt']; debt_wu = position(S, 'WBTC-USDT')['debt']
total_debt = sum(debts.values()) + debt_aave + debt_wu
acc_rl, vrl = v2_access('senRLUSDv2'); acc_py, vpy = v2_access('senPYUSDmain'); acc_pm, vpm = v2_access('senPYUSDPRIMEv2'); acc_pst, vpst = v2_access('senPYUSDPST')
kbtc_rl = [m for m in vrl['markets'] if m['coll'] == 'kBTC'][0]; kbtc_py = [m for m in vpy['markets'] if m['coll'] == 'kBTC'][0]
t1_rl = min(claim_rl, debts['RLUSD-1'], acc_rl); t1_py = min(claim_py, debts['PYUSD-1'], acc_py)
t1_pm = min(claim_pm, debt_aave, acc_pm); t1_pst = min(claim_pst, debt_wu, acc_pst)
# recycle: repaying kBTC/RLUSD frees the same amount of market liquidity that the V2 can force-deallocate (1 bp penalty) -> rest of the A-legs
t1b_rl = min(claim_rl, debts['RLUSD-1'], kbtc_rl['v2_supply'] + vrl['idle']) - t1_rl
t1b_py = min(claim_py, debts['PYUSD-1'], kbtc_py['v2_supply'] + vpy['idle']) - t1_py
prime_legs = debts['RLUSD-2'] + debts['PYUSD-2']
residual_A = debts['RLUSD-1'] + debts['PYUSD-1'] - (t1_rl + t1b_rl + t1_py + t1b_py)
ladder = [
    dict(tier='T1a same block, static', source='Sentora RLUSD Main: idle %.2fM + force-deallocatable market liquidity %.2fM (kBTC/RLUSD %.2fM) -> RLUSD-1' % (vrl['idle'] / 1e6, (acc_rl - vrl['idle']) / 1e6, kbtc_rl['v2_withdrawable'] / 1e6), usd=t1_rl),
    dict(tier='T1a same block, static', source='Paypal USD Main: idle %.2fM + force-deallocatable %.2fM (kBTC/PYUSD %.2fM) -> PYUSD-1' % (vpy['idle'] / 1e6, (acc_py - vpy['idle']) / 1e6, kbtc_py['v2_withdrawable'] / 1e6), usd=t1_py),
    dict(tier='T1a same block, static (needs PYUSD->USDT swap)', source='Sentora PRIME Main: idle %.2fM + PRIME/PYUSD liquidity %.2fM -> Aave USDT debt' % (vpm['idle'] / 1e6, (acc_pm - vpm['idle']) / 1e6), usd=t1_pm),
    dict(tier='T1a same block, static (needs PYUSD->USDT swap)', source='Sentora Huma PST Main: PST/PYUSD liquidity %.2fM -> Morpho WBTC/USDT debt' % (acc_pst / 1e6), usd=t1_pst),
    dict(tier='T1b same block / minutes, with repay-recycle', source='Repaying kBTC/RLUSD and kBTC/PYUSD debt re-creates the same liquidity in those markets; V2 force-deallocates it (1 bp) and pays the vault again (flash loan or a few executor txs + Sentora allocator)', usd=t1b_rl + t1b_py),
    dict(tier='T2 within 1 day', source='PRIME sold on DEX (Uniswap v3 PRIME/USDC 0.01%% pool, TVL ~$9.0M on DefiLlama 21.09) or posted to Morpho PRIME/PYUSD (liquidity %.2fM, competes with Sentora PRIME Main exits) - capacity only, not committed' % ((acc_pm - vpm['idle']) / 1e6), usd=0.0),
    dict(tier='T3 1-7 days', source='PRIME -> wYLDS (instant) -> USDC via Hastra operator, 1-2 business days; on-chain payout wallet held ~$85k vs $%.1fM needed' % (claim_prime / 1e6), usd=min(prime_legs, claim_prime)),
    dict(tier='T4 longer / uncertain', source='Residual (A-leg shortfall if V2 liquidity is taken by other depositors first; PRIME redemptions beyond Hastra/Figure capacity)', usd=max(0.0, residual_A) + max(0.0, prime_legs - claim_prime)),
]
cum = 0.0
for r in ladder:
    cum += r['usd']; r['usd_m'] = round(r['usd'] / 1e6, 2); r['pct_of_debt'] = round(100 * r['usd'] / total_debt, 1); r['cum_pct'] = round(100 * cum / total_debt, 1)
with open(os.path.join(OUTD, 'liquidity_ladder.csv'), 'w', newline='') as f:
    wr = csv.writer(f); wr.writerow(['tier', 'usd_m', 'pct_of_debt', 'cum_pct', 'source'])
    for r in ladder: wr.writerow([r['tier'], r['usd_m'], r['pct_of_debt'], r['cum_pct'], r['source']])
    f.write('# snapshot 2026-09-20 12:00 UTC (ETH block 26018583). Total vault debt $%.2fM = kBTC legs $%.2fM + Aave USDT $%.2fM + Morpho WBTC/USDT $%.2fM.\n' % (total_debt / 1e6, sum(debts.values()) / 1e6, debt_aave / 1e6, debt_wu / 1e6))
    f.write('# Vault claims: senRLUSDv2 $%.2fM, senPYUSDmain $%.2fM, PRIME $%.2fM (NAV %.4f), Sentora PRIME Main $%.2fM, Huma PST Main $%.2fM.\n' % (claim_rl / 1e6, claim_py / 1e6, claim_prime / 1e6, prime_px, claim_pm / 1e6, claim_pst / 1e6))
    f.write('# Sentora RLUSD Main / Paypal USD Main have no liquidity adapter (withdrawals served from idle only); forceDeallocate is permissionless with a 1 bp penalty (read on-chain). Assumes no competing withdrawals by other V2 depositors.\n')
res['ladder'] = ladder; res['ladder_meta'] = dict(total_debt=total_debt, claim_rl=claim_rl, claim_py=claim_py, claim_prime=claim_prime, claim_pm=claim_pm, claim_pst=claim_pst,
                                                  acc_rl=acc_rl, acc_py=acc_py, acc_pm=acc_pm, acc_pst=acc_pst, debts=debts, debt_aave=debt_aave, debt_wu=debt_wu)
for r in ladder: print(r['tier'], r['usd_m'], r['pct_of_debt'], r['cum_pct'])
# stress vs tier 1: can repay-needed be covered by T1a / T1a+T1b of the relevant legs?
t1a_kbtc = t1_rl + t1_py; t1ab_kbtc = t1a_kbtc + t1b_rl + t1b_py
for s in stress:
    need_k = sum(s[p]['repay_to_target_musd'] for p in POS) * 1e6
    need_prime = sum(s[p]['repay_to_target_musd'] for p in ('RLUSD-2', 'PYUSD-2')) * 1e6
    need_a = sum(s[p]['repay_to_target_musd'] for p in ('RLUSD-1', 'PYUSD-1')) * 1e6
    s['need_A_legs_musd'] = round(need_a / 1e6, 2); s['need_PRIME_legs_musd'] = round(need_prime / 1e6, 2)
    # A legs repaid from own V2 claims; PRIME legs have no same-block source except cross-use of A-leg proceeds within the same loan token
    rl_cap = t1_rl + t1b_rl - s['RLUSD-1']['repay_to_target_musd'] * 1e6
    py_cap = t1_py + t1b_py - s['PYUSD-1']['repay_to_target_musd'] * 1e6
    s['T1a_covers_kbtc_need'] = t1a_kbtc >= need_k; s['T1ab_covers_kbtc_need'] = t1ab_kbtc >= need_k
    s['spare_same_token_for_PRIME_legs_musd'] = dict(RLUSD=round(max(0, min(rl_cap, claim_rl - s['RLUSD-1']['repay_to_target_musd'] * 1e6)) / 1e6, 2),
                                                    PYUSD=round(max(0, min(py_cap, claim_py - s['PYUSD-1']['repay_to_target_musd'] * 1e6)) / 1e6, 2))
    print(s['shock'], 'need kBTC legs', round(need_k / 1e6, 2), 'A', s['need_A_legs_musd'], 'PRIME', s['need_PRIME_legs_musd'], 'T1a', round(t1a_kbtc / 1e6, 2), 'T1ab', round(t1ab_kbtc / 1e6, 2), s['spare_same_token_for_PRIME_legs_musd'], 'Aave', s['AAVE'])
json.dump(res, open(os.path.join(RAW, 'analysis_risk.json'), 'w'), indent=1, default=str)
