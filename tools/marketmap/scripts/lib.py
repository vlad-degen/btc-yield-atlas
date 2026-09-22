"""Shared helpers: DefiLlama protocol loading, BTC-token filtering, date points."""
import json, os, datetime, functools
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(D, 'raw')
SNAP = datetime.date(2026, 9, 20)
PRICE_SNAP = 81178.0  # Binance BTCUSDT close 2026-09-20

# BTC-denominated token symbols (DefiLlama uppercases symbols). weight = BTC share of token value.
BTC_FULL = set('''BTC WBTC CBBTC BTCB BTC.B KBTC LBTC TBTC FBTC SOLVBTC SOLVBTC.BBN SOLVBTC.CORE SOLVBTC.TRADING SOLVBTC.JUP SOLVBTC.ENA
XSOLVBTC UNIBTC BRBTC UNIBRBTC ENZOBTC STBTC BGBTC SBTC UBTC EBTC LBTCV PUMPBTC M-BTC MBTC YBTC YBTC.B CIRBTC XBTC ZBTC BFBTC
RBTC WRBTC HBTC HEMIBTC AVBTC SAVBTC MHYPERBTC MRE7BTC MBTC AHYPERBTC BTCOC WBTC.E BTC.BTC FEUBTC VBWBTC MCBBTC STRKBTC HEMICBWBTC
YOBTC MEVBTC SCBTC WCBTC CBTC DBTC OWBTC WANBTC LIQUIDBERABTC YLBTCLST YLPUMPBTC VYBTC GTBTC OBTC RENBTC IWBTC IWBTC.E BTCK
CBBTC-WBTC TBTC/CBBTC 2BTC-NG 2BTC-F 2BTC CRVRENWBTC CRVRENWSBTC TBTC/SBTCCRV EBTCTBTC TRIBTC IBBTC/SBTCCRV-F OBTC/SBTCCRV BBTC/SBTCCRV
PBTC/SBTCCRV CRVWSBTC BADGERWBTC-F IBBTCB UNIBTCWBTC BELTBTC WFRAGBTC ASBTC NBTC CKBTC ABTC SUBFROSTBTC FRBTC TZBTC LSTBTC
PLP-UNIBTC-19FEB2026 WBTCN'''.split())
BTC_PARTIAL = {  # mixed LP tokens: estimated BTC share (flagged as estimates)
    'CRVUSDTWBTCWETH': 1/3, 'CRVUSDCWBTCWETH': 1/3, 'CRVCRVUSDTBTCWSTETH': 1/3, 'CRVUSDBTCETH': 1/3, 'BTCGHOETH': 1/3,
    'GHOBTCWSTE': 1/3, 'WBTC/WETH SLP': 0.5, 'WBTC/WETH UNI-V2': 0.5, 'WBTC/USDC UNI-V2': 0.5, 'WBTC-USDC-GMX-V2': 0.5,
    'CRVFRAXTBTCFRXETH': 1/3, 'B-33WETH-33WBTC-33USDC': 1/3, '50WBTC-50WBERA-WEIGHTED': 0.5, 'KODI WBTC-WBERA': 0.5,
    'WBTC.E/WAVAX PGL': 0.5, 'WBTC/BADGER UNI-V2': 0.5, 'WBTC/DIGG SLP': 0.5, '20WBTC-80BADGER': 0.2,
}
def btc_weight(sym):
    s = sym.upper()
    if s in BTC_FULL: return 1.0
    if s.startswith('LFBTC-'): return 1.0      # Function "Locked FBTC" partner tokens
    if s in BTC_PARTIAL: return BTC_PARTIAL[s]
    return 0.0

@functools.lru_cache(maxsize=None)
def load(slug):
    return json.load(open(os.path.join(RAW, 'proto', slug + '.json')))

def _d(ts):
    return datetime.datetime.fromtimestamp(int(ts), datetime.UTC).date()

def series_tokens(slug, chain=None, units=False):
    """{date: {SYM: usd}} from tokensInUsd (or tokens for units). Daily points at 00:00 UTC; last intraday point dropped if duplicate date."""
    d = load(slug)
    src = d if chain is None else d['chainTvls'].get(chain, {})
    arr = src.get('tokens' if units else 'tokensInUsd') or []
    out = {}
    for r in arr:
        dt = _d(r['date'])
        if dt not in out or (int(r['date']) % 86400 == 0):
            out[dt] = r['tokens']
    return out

def series_total(slug, chain=None):
    d = load(slug)
    arr = d['tvl'] if chain is None else d['chainTvls'].get(chain, {}).get('tvl', [])
    out = {}
    for r in arr:
        dt = _d(r['date'])
        if dt not in out or (int(r['date']) % 86400 == 0):
            out[dt] = r['totalLiquidityUSD']
    return out

def pick(series, date, back=3):
    """value at date, else nearest earlier within `back` days"""
    for k in range(back + 1):
        dd = date - datetime.timedelta(days=k)
        if dd in series: return series[dd], dd
    return None, None

def month_points():
    """list of (month_label, defillama_date, price_date). month-end = 00:00 UTC snapshot on the 1st of next month
    (= end of last day), priced at Binance close of the last day. 2026-09 = snapshot 2026-09-20 at the 09-20 close."""
    out = []
    y, m = 2024, 9
    while (y, m) <= (2026, 8):
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        first_next = datetime.date(ny, nm, 1)
        out.append((f'{y}-{m:02d}', first_next, first_next - datetime.timedelta(days=1)))
        y, m = ny, nm
    out.append(('2026-09', SNAP, SNAP))
    return out

@functools.lru_cache(maxsize=None)
def btc_prices():
    return {k: v['close'] for k, v in json.load(open(os.path.join(RAW, 'btc_daily.json'))).items()}

def price(d):
    if d == SNAP: return PRICE_SNAP
    return btc_prices()[d.isoformat()]

def btc_part(tokens_usd, only=None, exclude=()):
    """sum of BTC-token USD (weighted); returns (usd, {sym: usd})"""
    tot = 0.0; br = {}
    for s, v in (tokens_usd or {}).items():
        if v is None: continue
        su = s.upper()
        if only is not None and su not in only: continue
        if su in exclude: continue
        w = btc_weight(su)
        if w > 0 and v > 0:
            tot += w * v; br[su] = br.get(su, 0) + w * v
    return tot, br
