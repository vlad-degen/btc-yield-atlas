"""BTC token classification for the money-market data set.

BTC family = the map's list (tools/marketmap/scripts/lib.py: BTC_FULL, BTC_PARTIAL, LFBTC-*) plus ALIASES (the same tokens under
other DefiLlama keys; added because otherwise a DefiLlama rename shows up as a flow, e.g. JustLend 'BTCT' -> 'BTC' in 2025-07).
Classes:
  plain  - wrappers that earn nothing on their own (WBTC, cbBTC, BTCB, BTC.b, tBTC, kBTC, FBTC, xBTC, cirBTC, enzoBTC, UBTC, sBTC,
           base SolvBTC, bgBTC, native BTC, ...). The map excludes these wrappers as products, so their BTC is not counted anywhere.
  yb     - yield-bearing BTC tokens whose backing the map already counts at the issuer row (YB below: token -> map product).
Excluded (not BTC): STBTC on Stacks (= stSTXbtc, an STX token; the map drops it from Zest v2 for the same reason).
"""
from mmlib import btc_weight, BTC_PARTIAL

ALIASES = {  # DefiLlama key -> canonical symbol in the map's list
    'TBTCV2': 'TBTC',                         # tBTC v2 before DefiLlama renamed it (Aave, Compound, Spark, crvUSD ... to 2025)
    'BTCT': 'BTC',                            # JustLend (Tron) BTC token, keyed BTCT until 2025-06, BTC from 2025-07
    'COINBASE-WRAPPED-BTC': 'CBBTC', 'LOMBARD-STAKED-BTC': 'LBTC', 'COINGECKO:OKX-WRAPPED-BTC': 'XBTC',
    'SOLV-PROTOCOL-SOLVBTC-BBN': 'SOLVBTC.BBN', 'SOLVBTC.M': 'SOLVBTC', 'SOLVBTC.B': 'SOLVBTC', 'BRIDGED MBTC': 'M-BTC',
}
# yield-bearing tokens counted at an issuer row of the map (products.py / 10_build.py ISSUER, plus issuer rows whose DefiLlama
# token list contains the token: Solv Basis Trading holds SOLVBTC.ENA/.JUP; aHyperBTC = Accountable's Hyperithm vault share)
YB = {
    'LBTC': 'Lombard LBTC', 'BTCOC': 'Lombard LBTC (BTCOC, via Lombard Vaults)', 'LBTCV': 'Lombard Vaults (LBTCv/BTCe)',
    'UNIBTC': 'Bedrock uniBTC', 'BRBTC': 'Bedrock uniBTC', 'UNIBRBTC': 'Bedrock uniBTC',
    'PUMPBTC': 'PumpBTC', 'SOLVBTC.BBN': 'SolvBTC LSTs', 'SOLVBTC.CORE': 'SolvBTC LSTs', 'XSOLVBTC': 'SolvBTC LSTs',
    'SOLVBTC.TRADING': 'Solv Basis Trading', 'SOLVBTC.ENA': 'Solv Basis Trading', 'SOLVBTC.JUP': 'Solv Basis Trading',
    'BFBTC': 'BitFi bfBTC', 'GTBTC': 'Gate GTBTC', 'MHYPERBTC': 'Midas mHyperBTC', 'MRE7BTC': 'Midas mRe7BTC',
    'AHYPERBTC': 'Accountable (Hyperithm vault share)', 'EBTC': 'ether.fi eBTC', 'AVBTC': 'Avant avBTC', 'SAVBTC': 'Avant avBTC',
    'STBTC': 'Lorenzo stBTC (issuer row ~0 today)', 'ASBTC': 'Aster asBTC', 'YOBTC': 'YO Protocol yoBTC', 'WFRAGBTC': 'Fragmetric',
    'SCBTC': 'Trevee / Rings scBTC', 'YLBTCLST': 'Yield-bearing BTC LST wrapper', 'YLPUMPBTC': 'PumpBTC', 'LIQUIDBERABTC': 'ether.fi Liquid (Bera BTC)',
    'VYBTC': 'Yield-bearing BTC vault token', 'MEVBTC': 'MEV Capital BTC vault token', 'HEMICBWBTC': 'Hemi LP vault token',
}

def canon(sym):
    s = sym.upper()
    return ALIASES.get(s, s)

def classify(sym, chain):
    """-> (canonical symbol, weight, class) with class in plain | yb | None (not BTC). Weight: BTC share of the token value."""
    s = canon(sym)
    if s == 'STBTC' and chain.startswith('Stacks'):
        return s, 0.0, None
    if s == 'HBTC' and chain.startswith('Stacks'):
        return s, 1.0, 'yb'  # Hermetica hBTC (none found in lending venues)
    w = btc_weight(s)
    if w == 0:
        return s, 0.0, None
    return s, w, ('yb' if s in YB else 'plain')

def is_partial(s):
    return s in BTC_PARTIAL
