"""Decoding helpers for raw/daily_eth.json rows."""
import json, os, math
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
LDEC = {'kBTC_RLUSD': 18, 'kBTC_PYUSD': 6, 'WBTC_USDT': 6, 'PRIME_PYUSD': 6, 'PST_PYUSD': 6}
CDEC = {'kBTC_RLUSD': 8, 'kBTC_PYUSD': 8, 'WBTC_USDT': 8, 'PRIME_PYUSD': 6, 'PST_PYUSD': 18}
POSM = {'RLUSD-1': 'kBTC_RLUSD', 'RLUSD-2': 'kBTC_RLUSD', 'PYUSD-1': 'kBTC_PYUSD', 'PYUSD-2': 'kBTC_PYUSD', 'WBTC-USDT': 'WBTC_USDT'}
V2DEC = {'senRLUSDv2': 18, 'senPYUSDmain': 6, 'senPYUSDPRIMEv2': 6, 'senPYUSDPST': 6}
def load():
    D = json.load(open(os.path.join(RAW, 'daily_eth.json')))
    return D
def market(row, m):
    x = row.get('market|' + m)
    if not x or x[0] == 0: return None
    tsa, tss, tba, tbs, lu, fee = x; d = 10 ** LDEC[m]
    return dict(supply=tsa / d, borrow=tba / d, util=tba / tsa if tsa else 0, liquidity=(tsa - tba) / d, lastUpdate=lu,
                sshare=tsa / tss if tss else 0, bshare=tba / tbs if tbs else 0)
def oracle_px(row, m):
    p = row.get('oracle|' + m)
    if not p: return None
    return p / 10 ** (36 + LDEC[m] - CDEC[m])
def position(row, p):
    m = POSM[p]; mk = market(row, m); x = row.get('pos|' + p)
    if not mk or not x: return None
    ss, bs, coll = x
    debt = bs * mk['bshare'] / 10 ** LDEC[m] if x[1] else 0.0
    # bshare is in raw units per share: tba/tbs; debt raw = bs * tba / tbs
    raw_tba, raw_tbs = row['market|' + m][2], row['market|' + m][3]
    debt = bs * raw_tba / raw_tbs / 10 ** LDEC[m] if raw_tbs else 0.0
    c = coll / 10 ** CDEC[m]; px = oracle_px(row, m)
    cv = c * px if px else None
    ltv = debt / cv if cv else None
    return dict(coll=c, debt=debt, px=px, coll_usd=cv, ltv=ltv, hf=(0.86 / ltv) if ltv else None,
                liq_px=(debt / (c * 0.86)) if c else None)
def btc_usd(row):
    x = row.get('cl_btc'); return x[0] / 1e8 if x else None
def prime_rate(row):
    x = row.get('prime_feed'); return x[0] / 1e18 if x else None
def v2(row, v):
    pps = row.get('v2_pps|' + v); ta = row.get('v2_ta|' + v); ts = row.get('v2_ts|' + v); idle = row.get('v2_idle|' + v)
    if not pps: return None
    d = 10 ** V2DEC[v]
    return dict(pps=pps / d, ta=ta / d, ts=ts / 1e18, idle=(idle or 0) / d)
def ys(row, y):
    x = row.get('ys|' + y)
    if x is None: return 0.0
    return x / (1e6 if y in ('RLUSD-B', 'PYUSD-B') else 1e18)
def aave(row):
    r = row.get('aave_usdt'); a = row.get('aave_awbtc'); v = row.get('aave_vdusdt'); acct = row.get('aave_acct')
    return dict(vbi=r[3] / 1e27 if r else None, vrate=r[4] / 1e27 if r else None, lu=r[6] if r else None,
                awbtc=(a or 0) / 1e8, debt=(v or 0) / 1e6,
                hf=(acct[5] / 1e18 if acct and acct[1] else None), liq_th=(acct[3] / 1e4 if acct else None),
                coll_usd=(acct[0] / 1e8 if acct else None), debt_usd=(acct[1] / 1e8 if acct else None))
