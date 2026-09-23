"""Overlap of money-market / CDP / venue / curator BTC with products the map already counts -> mm_overlap.csv (+ out/overlap_summary.json).

Groups (column 'group'):
  A  yield-bearing BTC tokens (LBTC, SolvBTC LSTs, uniBTC, eBTC, bfBTC, mHyperBTC, aHyperBTC, ...) sitting in the venue: their backing is
     counted at the issuer row of the map. Exact from DefiLlama token units, every month.
  B  plain-wrapper positions that belong to products the map counts (Kraken, Bitget, ether.fi Liquid BTC, Midas mHyperBTC, IPOR Fusion
     vaults incl. Tesseract/BTCD, Upshift, Concrete, Yearn, Moonwell/Seamless vaults, Harvest, Superform, Vesper): on-chain reads
     (repo deep dives, Morpho API, IPOR API, Blockscout aToken holders), month-ends where a history exists.
  C  venues that are themselves map products (Zest v2, Accountable, Wildcat, Native Credit Pool): all of their counted BTC.
  D  curator vaults: BTC already inside the money-market totals (Morpho / Euler supply) or counted in a map product.
Column 'in_column': which column of mm_monthly.csv the BTC sits in (btc_total = in DefiLlama TVL, i.e. collateral or idle supply;
btc_borrowed = lent out). Confidence: high (on-chain / exact token data), medium (on-chain snapshot but date or venue split inferred),
low (assumed from the product's stated strategy)."""
import collections, csv, datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mmlib import *
from tokens import YB

L = json.load(open(os.path.join(D, 'out', 'mm_long.json')))
SUMM = json.load(open(os.path.join(D, 'out', 'summary.json')))
SEL = SUMM['selection']
PR = {p['slug']: p for p in json.load(open(os.path.join(RAW, 'protocols.json')))}
MLAB = [m for m, _, _ in MONTHS]
MM = {(r['slug'], r['month']): r for r in csv.DictReader(open(os.path.join(D, 'mm_monthly.csv')))}
HIST = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(REPO, 'data', 'market_map_history_monthly.csv'))):
    HIST[r['product']][r['month']] = HIST[r['product']].get(r['month'], 0.0) + float(r['tvl_btc'])
CUR = {r['product']: r for r in csv.DictReader(open(os.path.join(REPO, 'data', 'market_map_current.csv')))}
CUR_EXCL = {'sentora-curator': {'KBTC'}, 'hyperithm': {'MHYPERBTC'}}

def pname(s):
    return PR.get(s, {}).get('name', s)
rows = []
def add(group, product, slug, month, btc, col, method, conf, chain='', note='', segment=None):
    if btc is None or abs(btc) < 1e-6:
        return
    rows.append(dict(product_already_counted=product, protocol=pname(slug) if slug in PR else slug, btc=btc, method=method, confidence=conf,
                     month=month, group=group, segment=segment or SEL.get(slug, ['?'])[0], slug=slug, chain=chain, in_column=col, note=note))

# ---------- A: yield-bearing tokens in every selected venue ----------
for s, (seg, why) in SEL.items():
    if s not in L or seg == 'curator':  # curator overlaps are handled in group D (their yield-bearing tokens sit inside Euler/Morpho)
        continue
    for m in MLAB:
        acc = collections.defaultdict(float)
        for ch, x in L[s][m].items():
            for kind, col in (('tvl', 'btc_total'), ('borrowed', 'btc_borrowed')):
                for k, v in x[kind].items():
                    if v[2] == 'yb' and k not in CUR_EXCL.get(s, set()):
                        acc[(YB.get(k, k), col, ch)] += v[0]
        for (prod, col, ch), b in acc.items():
            add('A', prod, s, m, b, col, 'DefiLlama token units: yield-bearing token, backing counted at the issuer row', 'high', chain=ch)

# ---------- C: venues that are map products ----------
def venue_rows(slug, product, only=None, months=None, cols=('btc_total', 'btc_borrowed'), note='', mapname=None):
    for m in MLAB:
        if months is not None and m not in months:
            continue
        parts = []
        for ch, x in L[slug][m].items():
            for kind, col in (('tvl', 'btc_total'), ('borrowed', 'btc_borrowed')):
                if col not in cols:
                    continue
                parts.append((ch, col, sum(v[0] for k, v in x[kind].items() if (only is None or k in only) and v[2] == 'plain')))
        tot = sum(p[2] for p in parts)
        cap = HIST.get(mapname, {}).get(m) if mapname else None
        f = min(1.0, cap / tot) if (cap is not None and tot > 0 and m != '2026-09') else 1.0  # never more than the map row counts that month
        for ch, col, b in parts:
            add('C', product, slug, m, b * f, col, 'the venue is a map product: the BTC it counts (DefiLlama token units, capped at the map row)', 'high', chain=ch, note=note)
hm = lambda p: {m for m, v in HIST.get(p, {}).items() if v > 0}
venue_rows('zest-v2', 'Zest v2 (sBTC supply) [C6]', only={'SBTC'}, months=hm('Zest v2 (sBTC supply)') | {'2026-09'}, note='map counts sBTC idle + borrowed; STBTC (stSTXbtc) excluded', mapname='Zest v2 (sBTC supply)')
venue_rows('accountable', 'Accountable YieldApp (cbBTC/wcBTC) [C5]', months=hm('Accountable YieldApp (cbBTC/wcBTC)') | {'2026-09'}, note='map counts borrowed + idle', mapname='Accountable YieldApp (cbBTC/wcBTC)')
venue_rows('wildcat-protocol', 'Wildcat (BTC) [C5]', months={'2026-09'}, note='map row is snapshot-only (total supplied 160.97 BTC on the 09-23 page)')
venue_rows('native-credit-pool', 'Native Credit Pool (BTC part) [C5]', months=hm('Native Credit Pool (BTC part)'), cols=('btc_total',),
           note='map counts the idle BTC only; the 53.35 BTC lent to market makers (btc_borrowed) is not in the map', mapname='Native Credit Pool (BTC part)')

# ---------- B: plain positions of counted products ----------
# B1 Kraken Bitcoin Vault: kBTC collateral in 4 Morpho positions (markets kBTC/RLUSD 0x15bb2a6a.., kBTC/PYUSD 0xe51f9aaa..), WBTC/USDT on
# Morpho (0x5ee1..f884), WBTC on Aave v3 Core (loan manager 0xF523..53B7). Weekly Monday 00:00 UTC reads: data/top5/kraken/ltv_weekly.csv
KW = {}
for r in csv.DictReader(l for l in open(os.path.join(REPO, 'data', 'top5', 'kraken', 'ltv_weekly.csv')) if not l.startswith('#')):
    try:
        d = datetime.date.fromisoformat(r['date'][:10])
    except ValueError:
        continue
    if len(r['date']) > 10:
        continue
    k = sum(float(r[c] or 0) for c in ('RLUSD-1_coll_kbtc', 'RLUSD-2_coll_kbtc', 'PYUSD-1_coll_kbtc', 'PYUSD-2_coll_kbtc'))
    KW[d] = (k, float(r['aave_wbtc'] or 0))
def interp(d):
    ds = sorted(KW)
    if d <= ds[0]:
        return KW[ds[0]] if d == ds[0] else (0.0, 0.0)
    for a, b in zip(ds, ds[1:]):
        if a <= d <= b:
            f = (d - a).days / (b - a).days
            return tuple(KW[a][i] + (KW[b][i] - KW[a][i]) * f for i in range(2))
    return KW[ds[-1]]
for m, dl, pd in MONTHS:
    if m == '2026-09':
        add('B', 'Kraken Bitcoin Vault [C1]', 'morpho-blue', m, 5395.41, 'btc_total', 'on-chain: Morpho position() of the 4 loan managers, ETH block 26018582 (2026-09-20 12:00 UTC)', 'high', 'Ethereum', 'kBTC collateral, markets kBTC/RLUSD and kBTC/PYUSD')
        add('B', 'Kraken Bitcoin Vault [C1]', 'morpho-blue', m, 90.01, 'btc_total', 'on-chain: Morpho WBTC/USDT position (loan manager 0x5EE1..f884), same block', 'high', 'Ethereum', 'WBTC collateral')
        add('B', 'Kraken Bitcoin Vault [C1]', 'aave-v3', m, 347.10, 'btc_total', 'on-chain: Aave getUserAccountData / aEthWBTC balance of loan manager 0xF523..53B7, same block', 'high', 'Ethereum', 'WBTC collateral (Aave WBTC 2% utilised: all counted in TVL)')
        continue
    if dl < datetime.date(2026, 5, 20):
        continue
    k, a = interp(dl)
    add('B', 'Kraken Bitcoin Vault [C1]', 'morpho-blue', m, k, 'btc_total', 'on-chain weekly reads (Monday 00:00 UTC, ltv_weekly.csv) interpolated to the month-end point', 'medium', 'Ethereum', 'kBTC collateral')
    add('B', 'Kraken Bitcoin Vault [C1]', 'aave-v3', m, a, 'btc_total', 'on-chain weekly reads interpolated to the month-end point', 'medium', 'Ethereum', 'WBTC collateral')
# B2 Bitget: all bgBTC in Morpho on Morph is the Aera vault's collateral (market bgBTC/USDC 0x37d156e9..; 801.58 at Morph block 27081170)
for m in MLAB:
    b = L['morpho-blue'][m].get('Morph', {'tvl': {}})['tvl'].get('BGBTC', [0])[0]
    add('B', 'Bitget bgBTC Onchain Earn [C1]', 'morpho-blue', m, b, 'btc_total', 'DefiLlama Morpho (Morph) BGBTC = the Aera vault position (on-chain 801.58 bgBTC at 09-20 12:00); DefiLlama tracks Morph only from 2026-08-19',
        'high', 'Morph', 'the vault held 60-500 bgBTC on Morph in 2026-07, before DefiLlama tracked the chain (not in the money-market totals then)')
# B3 Midas mHyperBTC (snapshot; Midas transparency API + RPC at ETH block 26018582; Monad reads 09-22)
for slug, b, col, how, ch, note, conf in [
        ('morpho-blue', 126.0002, 'btc_total', 'on-chain Morpho position() of strategy wallet 0x933a..2833, cbBTC/USDT', 'Ethereum', 'collateral', 'high'),
        ('sparklend', 113.416, 'btc_total', 'on-chain spcbBTC balance / getUserAccountData', 'Ethereum', 'collateral (Spark cbBTC 3% utilised)', 'high'),
        ('aave-v3', 1.3643, 'btc_total', 'on-chain aEthWBTC balance', 'Ethereum', 'idle collateral', 'high'),
        ('euler-v2', 69.4233, 'btc_borrowed', 'RPC convertToAssets, Hyperithm Earn cbBTC (EVK ecbBTC-4/-6), read 2026-09-22', 'Monad', 'lent cbBTC; the EVK vault is ~94% utilised, so almost all sits in Euler borrowed', 'medium'),
        ('morpho-blue', 35.0545, 'btc_borrowed', 'RPC convertToAssets of Morpho V2 Hyperithm cbBTC Apex share (42% of the vault), read 2026-09-22', 'Monad', 'lent cbBTC into mHyperBTC/cbBTC and aHyperBTC/cbBTC markets (~93% utilised)', 'medium')]:
    add('B', 'Midas mHyperBTC [C1]', slug, '2026-09', b, col, how + ' (data/top5/mhyperbtc/positions.csv)', conf, ch, note)
# B4 ether.fi Liquid BTC: plain-wrapper money-market positions from data/top5/etherfi/positions_monthly.csv (LBTC/eBTC legs are group A)
VEN = {'morpho': 'morpho-blue', 'aEth': 'aave-v3', 'sp': 'sparklend'}
for r in csv.DictReader(open(os.path.join(REPO, 'data', 'top5', 'etherfi', 'positions_monthly.csv'))):
    m = r['month'][:7]
    btcside = r['holdings'].split('|')[0].replace('BTC-side:', '')
    for part in btcside.split(';'):
        part = part.strip()
        mt = re.match(r'(ITB:)?(morpho:|aEth|sp)(WBTC|cbBTC)\s+([0-9.]+)', part)
        if mt:
            ven = VEN[mt.group(2).rstrip(':')]
            add('B', 'ether.fi Liquid BTC [C1]', ven, m, float(mt.group(4)), 'btc_total', 'on-chain month-end positions (data/top5/etherfi/positions_monthly.csv)', 'high', 'Ethereum',
                f'{mt.group(3)} collateral' + (' via ITB' if mt.group(1) else ''))
# B5 IPOR Fusion BTC vaults (Tesseract TESS, BTCD / TAU carry, other): api.ipor.io/fusion/vaults, last point before 2026-09-20 23:59 UTC
for slug, b, ch, note in [('aave-v3', 23.102, 'Base', 'TESS cbBTC Debt Vault cbETH Loop'), ('aave-v3', 10.043 + 0.5 + 0.669, 'Ethereum', 'TESS WBTC WSR LOOP, TESS wBTC USDe loop, Reservoir BTC Yield'),
                          ('sparklend', 12.0, 'Ethereum', 'TESS WBTC Lending Vault'), ('morpho-blue', 4.504 + 3.016 + 5.001 + 1.077 + 0.629, 'Ethereum', 'WBTC/USDC collateral: TESS Lending, wBTC Dollar Carry, wBTC Debt Vault Loop, TAU InfiniFi, Reservoir'),
                          ('morpho-blue', 1.945, 'Ethereum', 'wBTC Dollar Carry: WBTC supplied to a Morpho market')]:
    add('B', 'IPOR Fusion BTC vaults (Tesseract / BTCD-TAU [C1], other [C6])', slug, '2026-09', b, 'btc_borrowed' if 'supplied' in note else 'btc_total',
        'IPOR API marketBalances (DEPOSIT/COLLATERAL) at 2026-09-20 23:29 UTC; 62.5 of the vaults 65.9 BTC', 'high', ch, note, segment='money_market')
for m in MLAB:  # history: map rows x 09-20 money-market share (62.5 / 65.9)
    if m == '2026-09':
        continue
    h = sum(HIST[p].get(m, 0.0) for p in ('Tesseract TESS wBTC debt-loop vaults (IPOR Fusion)', 'BTCD Labs / TAU BTC dollar-carry vaults (IPOR Fusion)', 'IPOR Fusion (other BTC vaults)'))
    add('B', 'IPOR Fusion BTC vaults (Tesseract / BTCD-TAU [C1], other [C6])', 'aave-v3/morpho-blue/sparklend', m, h * 62.48 / 65.94, 'btc_total',
        'ESTIMATE: map monthly BTC of the three IPOR rows x the 09-20 money-market share (0.948)', 'low', 'Ethereum/Base', segment='money_market')
# B6.. snapshot positions from the 2026-09-21 carry scan (data/top5/selection/carry_products_scan.csv), Morpho API and Blockscout
for prod, slug, b, col, how, conf, ch, note in [
        ('Upshift (BTC vaults) [C6]', 'morpho-blue', 46.68, 'btc_total', 'on-chain: Upshift Sentora BTC loan contracts 0x37aD..754E (28.37) and 0xE504..183E (18.32), Morpho API 09-23 / carry scan 09-21', 'high', 'Ethereum', 'WBTC collateral (also = the Sentora curator WBTC vault)'),
        ('Upshift (BTC vaults) [C6]', 'aave-v4', 41.03, 'btc_total', 'on-chain: Upshift Gamma BTC via operator EOA 0x8e0a..8731, Aave v4 spoke 0x94e7..c485, carry scan 09-21', 'medium', 'Ethereum', 'WBTC collateral'),
        ('Concrete (BTC vaults) [C6]', 'aave-v3', 29.29, 'btc_total', 'on-chain: Concrete ctWBTC v2 0xf72b..a1c4 on Aave v3 Core, carry scan 09-21', 'high', 'Ethereum', 'WBTC collateral'),
        ('Yearn (BTC vaults) [C6, lend-only]', 'morpho-blue', 38.95, 'btc_total', 'Morpho API 09-23: Yearn WBTC MetaMorpho 0x2bB0..B77E (47.51; depositor = Yearn v3 WBTC vault, which the v2 yVault routes into)', 'medium', 'Ethereum', 'idle-market supply'),
        ('Yearn (BTC vaults) [C6, lend-only]', 'morpho-blue', 8.56, 'btc_borrowed', 'same vault: 8.56 WBTC supplied to the LBTC/WBTC market', 'medium', 'Ethereum', 'lent'),
        ('Yearn (BTC vaults) [C6, lend-only]', 'morpho-blue', 14.16, 'btc_total', 'on-chain: Yearn Katana WBTC yVault strategy 0x0432..8d43, Morpho vbWBTC/vbUSDC (Morpho API 09-23)', 'high', 'Katana', 'vbWBTC collateral'),
        ('Moonwell vaults (cbBTC) [C6, lend-only]', 'morpho-blue', 5.36, 'btc_total', 'Morpho API 09-23: Moonwell Frontier cbBTC allocation (idle market 5.36 + LBTC/cbBTC 8.11)', 'medium', 'Base', 'idle-market supply'),
        ('Moonwell vaults (cbBTC) [C6, lend-only]', 'morpho-blue', 8.50, 'btc_borrowed', 'same vault: LBTC/cbBTC market supply (map row 13.86 - 5.36)', 'medium', 'Base', 'lent'),
        ('Harvest (BTC) [C6, lend-only]', 'morpho-blue/dolomite/other', 14.14, 'btc_borrowed', 'ASSUMED: Harvest Autopilot vaults lend on Morpho, Dolomite, Arcadia (lending_products.csv); venue split not measured', 'low', 'Base/Arbitrum/Ethereum', 'upper bound = the map row'),
        ('Superform (BTC) [C6, lend-only]', 'morpho-blue/euler-v2/aave', 11.64, 'btc_borrowed', 'ASSUMED: SuperVaults allocate to lending vaults; venue split not measured', 'low', 'Ethereum/Base', 'upper bound = the map row'),
        ('Vesper (WBTC) [C6, lend-only]', 'aave-v3/compound', 4.89, 'btc_total', 'ASSUMED: Vesper pools lend WBTC on money markets; not measured', 'low', 'Ethereum', 'upper bound = the map row')]:
    add('B', prod, slug, '2026-09', b, col, how, conf, ch, note, segment='money_market')
for prod, mapname in [('Moonwell vaults (cbBTC) [C6, lend-only]', 'Moonwell vaults (cbBTC)'), ('Seamless vaults (cbBTC) [C6, history]', 'Seamless vaults (cbBTC)')]:
    for m in MLAB:
        if m == '2026-09':
            continue
        add('B', prod, 'morpho-blue', m, HIST[mapname].get(m, 0.0), 'btc_total/btc_borrowed', 'map monthly BTC of the row: MetaMorpho cbBTC vaults on Base, all of it supplied to Morpho (split between idle and lent not measured)',
            'medium', 'Base', segment='money_market')

# ---------- D: curator vaults (09-20; vault venues from the DefiLlama curator registry, Morpho API vault list and IPOR / Upshift reads) ----------
CURD = [  # slug, btc inside money-market totals (column), btc counted in a map product (product), note
    ('gauntlet', 224.02, 0.0, '', 'Morpho vaults: Vault Bridge WBTC 183.7 (Katana bridge, idle market), WBTC Core 30.6, cbBTC Core 7.5, LBTC Core 1.1 (Morpho API)'),
    ('hyperithm', 256.0, 505.7, 'Accountable YieldApp [C5]', 'Monad: aHyperBTC 106.9 (Euler collateral vault) + Euler Earn / EVK cbBTC ~69 + Morpho V2 Apex 92.2 - overlap with other depositors; cbBTC 505.7 = the Accountable Hyperithm vault (in Accountable borrowed). mHyperBTC 284 excluded (C1)'),
    ('tulipa-capital', 0.0, 125.08, 'Lagoon (BTC vaults) [C6]', 'Lagoon Flagship cbBTC (co-curated with 9Summits: listed under both curators); venue of its cbBTC not measured'),
    ('9summits', 0.0, 125.08, 'Lagoon (BTC vaults) [C6] (same vault as Tulipa)', 'duplicate of the Tulipa row: one Lagoon vault'),
    ('yearn-curating', 47.51, 0.0, 'Yearn (BTC vaults) [C6] (depositor)', 'Yearn WBTC MetaMorpho 47.5 (its depositor is Yearn v3, counted in the map Yearn row); rest 33.7 WBTC not located'),
    ('telos-consilium', 7.94, 0.0, '', 'Euler vaults (eulerVaultOwners); DefiLlama euler-v2 Ethereum holds only 7.9 WBTC, so most of the 71.1 WBTC is outside the money-market totals'),
    ('ultrayield-curator', 0.0, 54.65, 'UltraYield vaults (cbBTC) [C6] + Upshift UBTC [C6]', 'Ethereum cbBTC 44.0 = the map UltraYield vaults row; HL UBTC 10.7 = the Upshift/Hyperbeat UBTC vault'),
    ('sentora-curator', 47.2, 47.2, 'Upshift (BTC vaults) [C6]', 'Sentora-curated Upshift Sentora BTC vault: WBTC collateral on Morpho (counted once: here as inside money markets and in Upshift)'),
    ('gami-labs', 9.62, 0.0, '', 'Gami Gearbox WBTC (Gearbox pool, in the money-market set); Robinhood-chain WBTC 7.35 not located'),
    ('anthias-labs', 13.85, 13.85, 'Moonwell vaults (cbBTC) [C6]', 'Moonwell Frontier cbBTC MetaMorpho on Base (also listed under Block Analitica)'),
    ('block-analitica', 13.85, 13.85, 'Moonwell vaults (cbBTC) [C6] (same vault as Anthias)', 'duplicate of the Anthias row'),
    ('damm-capital', 0.0, 0.0, '', 'DAMM flagship funds (erc4626), not lending vaults; deployment not measured'),
    ('odyssey-digital-am', 0.0, 8.62, 'Lagoon (BTC vaults) [C6]', 'Odyssey funds on Lagoon'),
    ('k3-capital', 7.58, 0.0, '', 'Euler vaults on Ethereum (euler-v2 Ethereum WBTC 6.7 idle + 1.3 borrowed)'),
    ('clearstar', 8.02, 0.0, '', 'Euler / Morpho vaults on Base and HyperEVM'),
    ('alphagrowth', 4.98, 0.0, '', 'Euler vaults on Base (euler-v2 Base LBTC 1.37 + cbBTC)'),
    ('steakhouse-financial', 3.14, 0.0, '', 'Morpho vaults'),
    ('re7-labs', 1.93, 0.0, '', 'Morpho vaults (Re7 WBTC Ethereum 0.94, World Chain 0.43)'),
    ('mev-capital', 0.0, 0.0, '', 'Sui WBTC 1.6: venue not measured'),
    ('tau-labs', 1.08, 1.08, 'BTCD / TAU carry vaults [C1]', 'TAU InfiniFi BTC Carry (IPOR Fusion): WBTC collateral on Morpho'),
]
for slug, inside, counted, prod, note in CURD:
    if inside:
        add('D', 'inside the money-market totals (Morpho / Euler supply)', slug, '2026-09', inside, 'btc_total (curator row)', 'curator registry + Morpho API vault list / Euler chain totals', 'medium', note=note)
    if counted:
        add('D', prod, slug, '2026-09', counted, 'btc_total (curator row)', 'curator registry vault list matched to map rows', 'medium', note=note)

# ---------- write ----------
F = ['product_already_counted', 'protocol', 'btc', 'method', 'confidence', 'month', 'group', 'segment', 'slug', 'chain', 'in_column', 'note']
rows.sort(key=lambda r: ({'A': 1, 'B': 0, 'C': 2, 'D': 3}[r['group']], r['month'] != '2026-09', r['product_already_counted'], r['month'], r['slug'], r['chain']))
with open(os.path.join(D, 'mm_overlap.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=F, lineterminator='\n'); w.writeheader()
    for r in rows:
        w.writerow({**r, 'btc': round(r['btc'], 4)})

# ---------- summary: snapshot and monthly not-yet-counted ----------
out = {}
def ov(month, seg=None, col=None, group=None):
    return sum(r['btc'] for r in rows if r['month'] == month and (seg is None or r['segment'] == seg) and (col is None or r['in_column'] == col)
               and (group is None or r['group'] == group))
for m in MLAB:
    rec = {}
    for seg in ('money_market', 'cdp', 'venue'):
        tt = sum(float(r['btc_total']) for (s, mm), r in MM.items() if mm == m and r['segment'] == seg)
        bb = sum(float(r['btc_borrowed']) for (s, mm), r in MM.items() if mm == m and r['segment'] == seg)
        rec[seg] = dict(btc_total=tt, btc_borrowed=bb,
                        ov_total=ov(m, seg, 'btc_total'), ov_borrowed=ov(m, seg, 'btc_borrowed'), ov_mixed=ov(m, seg, 'btc_total/btc_borrowed'),
                        ov_A_total=ov(m, seg, 'btc_total', 'A'), ov_B_total=ov(m, seg, 'btc_total', 'B'), ov_C_total=ov(m, seg, 'btc_total', 'C'),
                        ov_C_borrowed=ov(m, seg, 'btc_borrowed', 'C'), ov_B_borrowed=ov(m, seg, 'btc_borrowed', 'B'), ov_A_borrowed=ov(m, seg, 'btc_borrowed', 'A'))
    out[m] = rec
cur = {s: 0.0 for s in ('inside', 'counted')}
for slug, inside, counted, prod, note in CURD:
    cur['inside'] += inside; cur['counted'] += counted
out['curator_0920'] = cur
json.dump(out, open(os.path.join(D, 'out', 'overlap_summary.json'), 'w'), indent=0)
x = out['2026-09']['money_market']
print('MM 09-20 total', round(x['btc_total'], 1), 'overlap in total', round(x['ov_total'], 1), 'A', round(x['ov_A_total'], 1), 'B', round(x['ov_B_total'], 1), 'C', round(x['ov_C_total'], 1),
      '| borrowed', round(x['btc_borrowed'], 1), 'ov', round(x['ov_borrowed'], 1), 'mixed', round(x['ov_mixed'], 1))
for seg in ('cdp', 'venue'):
    y = out['2026-09'][seg]; print(seg, round(y['btc_total'], 1), 'overlap', round(y['ov_total'], 1))
print('curator', cur)
print('rows', len(rows))
