"""Helpers for the money-market BTC data set. Same conventions as tools/marketmap/scripts/lib.py (DefiLlama daily points
stamped 00:00 UTC; month-end = point stamped on the 1st of the next month; snapshot = 2026-09-20 point)."""
import csv, datetime, json, os, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(D, 'raw')
REPO = os.path.abspath(os.path.join(D, '..', '..', '..'))  # repo root (this folder is tools/marketmap/money_markets)
sys.dont_write_bytecode = True  # never write __pycache__ into the repo when importing its modules
sys.path.insert(0, os.path.join(REPO, 'tools', 'marketmap', 'scripts'))
from lib import BTC_FULL, BTC_PARTIAL, btc_weight, month_points, SNAP, PRICE_SNAP  # noqa: E402  (the map's own lists)

# chain keys that are not per-chain TVL (same list as 10_build.py AGG_KEYS) and suffixes to skip
AGG_KEYS = {'borrowed', 'staking', 'pool2', 'vesting', 'offers', 'treasury', 'doublecounted', 'liquidstaking', 'dcAndLsOverlap'}
SKIP_SUFFIX = ('-staking', '-pool2', '-vesting', '-offers', '-treasury', '-doublecounted', '-liquidstaking', '-dcAndLsOverlap')

_cache = {}
def load(slug):
    if slug not in _cache:
        _cache.clear()  # keep memory bounded: one big protocol at a time
        _cache[slug] = json.load(open(os.path.join(RAW, 'proto', slug + '.json')))
    return _cache[slug]

def chain_keys(d):
    """[(key, base_chain, kind)] kind = 'tvl' | 'borrowed'"""
    out = []
    for k in d.get('chainTvls', {}):
        if k in AGG_KEYS or k.endswith(SKIP_SUFFIX):
            continue
        if k.endswith('-borrowed'):
            out.append((k, k[:-len('-borrowed')], 'borrowed'))
        else:
            out.append((k, k, 'tvl'))
    return out

def _d(ts):
    return datetime.datetime.fromtimestamp(int(ts), datetime.UTC).date()

def series(d, key, units=True):
    """{date: {SYM: value}} for chain key (None = protocol level). 00:00 UTC point preferred for a date."""
    src = d if key is None else d['chainTvls'].get(key, {})
    arr = src.get('tokens' if units else 'tokensInUsd') or []
    out = {}
    for r in arr:
        dt = _d(r['date'])
        if dt not in out or int(r['date']) % 86400 == 0:
            out[dt] = r['tokens']
    return out

def series_tvl(d, key):
    src = d if key is None else d['chainTvls'].get(key, {})
    out = {}
    for r in src.get('tvl') or []:
        dt = _d(r['date'])
        if dt not in out or int(r['date']) % 86400 == 0:
            out[dt] = r['totalLiquidityUSD']
    return out

def pick(s, date, back=3):
    for k in range(back + 1):
        dd = date - datetime.timedelta(days=k)
        if dd in s:
            return s[dd], dd
    return None, None

def map_prices():
    """month -> BTC price the map uses (net USD / net BTC in data/category_history_monthly.csv; 2026-09 = 81,178)."""
    rows = list(csv.DictReader(open(os.path.join(REPO, 'data', 'category_history_monthly.csv'))))
    out = {}
    for m in sorted({r['month'] for r in rows}):
        u = sum(float(r['tvl_usd_net']) for r in rows if r['month'] == m)
        b = sum(float(r['tvl_btc_net']) for r in rows if r['month'] == m)
        out[m] = u / b
    out['2026-09'] = PRICE_SNAP
    return out

MONTHS = month_points()  # [(label, defillama_date, price_date)]
