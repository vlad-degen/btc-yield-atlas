"""Shared helpers for the ETH counted-once market map (mirrors tools/marketmap/scripts/lib.py for BTC).

Snapshot T = 2026-10-02 23:59:59 UTC. DefiLlama's daily point stamped 2026-10-03 00:00 UTC is the end of 2 October.
Month-ends: point stamped 00:00 UTC on the 1st of the next month, priced at the ETH close of the last day.
"""
import datetime, functools, gzip, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = os.path.join(ROOT, 'raw', 'eth', 'netmap-2026-10-07')
OUT = os.path.join(ROOT, 'data', 'eth', 'netmap')
SNAP_LABEL = '2026-10-02'
SNAP_POINT = datetime.date(2026, 10, 3)      # DefiLlama point stamped 2026-10-03 00:00 UTC
SNAP_PRICE_DATE = datetime.date(2026, 10, 2)

# ETH-family symbols as DefiLlama prints them (upper case). Value counts in full, as ETH equivalent at the dated ETH price.
ETH_FULL = set('''SPETH ETH WETH WETH.E ETH.E STETH WSTETH RETH CBETH WBETH BETH WEETH EETH WEETHS EZETH RSETH WRSETH PUFETH OSETH METH CMETH
SWETH RSWETH SFRXETH FRXETH ETHX ANKRETH LSETH OETH WOETH SUPEROETHB SUPEROETH WSUPEROETHB UNIETH ETH+ PXETH APXETH RSTETH AGETH
HGETH TETH EARNETH LIQUIDETH EGETH INWSTETH INETH YNETH YNLSDE PRIMEETH AMPHRETH STEAKLRT RE7LRT SETH2 RETH2 STONE
WSTETH.E SAVETH AVETH DETH VAETH ROYWSTETH ETHPLUS OSETH2 GETH WEETH.E SCETH PZETH INSTETH ULTRAETHS RSETH.E WRSETH.E
SPETH SPWETH BBETH MEVETH YVWETH GTWETH STEAKETH BBQETH ROETH SUPERETH SUPERWETH MIXWETH LEETH STKETH RUBYETH CETH SOLVETH
ESETH OBETH DWETH EBETH BWETH NETH NWETH TWETH YETH STYETH SYETH WRETH ETHFIETH HYPERETH VETH ZETH BRETH UNIBTCETH'''.split())
EXCLUDE = set('''ETHFI ETHW ETHPOW ENA ETHENA SETH SETHX ETHDYDX ETHBULL ETHBEAR ETH2X-FLI ETHX-ALT ETHG METHANE ETHOS META'''.split())
ETH_PARTIAL = {  # mixed LP tokens with an estimated ETH share, flagged as estimates
    'CRVUSDTWBTCWETH': 1/3, 'CRVUSDCWBTCWETH': 1/3, 'CRVUSDBTCETH': 1/3, 'BTCGHOETH': 1/3, 'CRVCRVUSDTBTCWSTETH': 1/3,
    'GHOBTCWSTE': 1/3, 'WBTC/WETH SLP': 0.5, 'WBTC/WETH UNI-V2': 0.5, 'USDC/WETH UNI-V2': 0.5, 'WETH/USDT UNI-V2': 0.5,
    'B-33WETH-33WBTC-33USDC': 1/3, 'CRVFRAXTBTCFRXETH': 1/3,
}
_ETHLIKE = re.compile(r'^(W|A|C|S|V|Y|GT|STEAK|BBQ|RE7)?[A-Z0-9]*ETH[A-Z0-9.]*$')


def eth_weight(sym):
    s = (sym or '').upper()
    if s in EXCLUDE:
        return 0.0
    if s in ETH_FULL:
        return 1.0
    if s in ETH_PARTIAL:
        return ETH_PARTIAL[s]
    return 0.0


def unknown_ethlike(sym):
    """symbols that look ETH-denominated but are not classified: reported for review, never silently counted."""
    s = (sym or '').upper()
    return s not in ETH_FULL and s not in EXCLUDE and s not in ETH_PARTIAL and 'ETH' in s and len(s) <= 24


def _d(ts):
    return datetime.datetime.fromtimestamp(int(ts), datetime.UTC).date()


@functools.lru_cache(maxsize=None)
def load(slug):
    p = os.path.join(RAW, 'proto', slug + '.json.gz')
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def series(slug, chain=None, kind='tokensInUsd'):
    """{date: value}; kind is tokensInUsd / tokens (dicts) or tvl (float). Midnight points win over intraday ones."""
    d = load(slug)
    src = d if chain is None else (d.get('chainTvls') or {}).get(chain, {})
    arr = src.get(kind) or []
    out = {}
    for r in arr:
        dt = _d(r['date'])
        v = r.get('tokens') if kind != 'tvl' else r.get('totalLiquidityUSD')
        if dt not in out or int(r['date']) % 86400 == 0:
            out[dt] = v
    return out


def pick(ser, date, back=3):
    for k in range(back + 1):
        dd = date - datetime.timedelta(days=k)
        if dd in ser:
            return ser[dd], dd
    return None, None


def month_points():
    """(label, DefiLlama point date, price date) for 2024-10 .. 2026-09 month-ends plus the 2026-10-02 snapshot."""
    out = []
    y, m = 2024, 10
    while (y, m) <= (2026, 9):
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        first_next = datetime.date(ny, nm, 1)
        out.append((f'{y}-{m:02d}', first_next, first_next - datetime.timedelta(days=1)))
        y, m = ny, nm
    out.append((SNAP_LABEL, SNAP_POINT, SNAP_PRICE_DATE))
    return out


@functools.lru_cache(maxsize=None)
def _lido_price():
    usd, units = series('lido', kind='tokensInUsd'), series('lido', kind='tokens')
    return {k: usd[k]['WETH'] / units[k]['WETH'] for k in usd if k in units and (units[k] or {}).get('WETH')}


def price(point_date):
    """ETH/USD implied by Lido's adapter (tokensInUsd[WETH] / tokens[WETH]) at the same DefiLlama point,
    the convention of the existing ETH market ledger."""
    v, _ = pick(_lido_price(), point_date)
    return v


def eth_part(tokens_usd, exclude=()):
    """ETH-family USD in a tokensInUsd dict: (usd, {sym: usd})."""
    tot, br = 0.0, {}
    for s, v in (tokens_usd or {}).items():
        if v is None or v <= 0:
            continue
        su = s.upper()
        if su in exclude:
            continue
        w = eth_weight(su)
        if w > 0:
            tot += w * v
            br[su] = br.get(su, 0) + w * v
    return tot, br
