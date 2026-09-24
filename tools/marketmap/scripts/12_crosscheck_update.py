"""Post-build step: apply the 2026-09-23 cross-check against DefiLlama's BTC yields list to the map in data/.

1. Adds what the map missed and what has more than $1M of liquidity on https://defillama.com/yields?token=family:btc
   (read 2026-09-23): DEX pools, the GMX BTC-only pool, the Across WBTC pool and Multipli xWBTC. Values are the pools'
   own DefiLlama TVL series (yields.llama.fi/chart/{pool}): the 2026-09-20 point for the snapshot, the last-day point for
   month-ends. Parts already counted elsewhere are left out (see the share of each pool below).
2. Flags lending: products whose BTC is lent out (a lending market, a lending-only vault or a credit fund) stay in the map
   and are listed in data/lending_products.csv, so the site can show the market with or without them. Adds Wildcat
   (lending to market makers, over $1M; snapshot only, see WILDCAT).
3. Recomputes category_history_monthly.csv and category_flows_monthly.csv from the product rows.

Idempotent: rows added by an earlier run are replaced. Pool charts are cached in tools/marketmap/raw/pool_charts/.
Usage: python3 tools/marketmap/scripts/12_crosscheck_update.py [repo root]
"""
import csv, datetime, json, os, sys, time, urllib.request

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
DATA = os.path.join(ROOT, 'data')
CACHE = os.path.join(ROOT, 'tools', 'marketmap', 'raw', 'pool_charts')
SNAP, SNAP_PRICE = '2026-09-20', 81178
MARK = 'DefiLlama yields pool, cross-check 2026-09-23'
CATS = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
KRAKEN_UNI_BTC = 268  # the Kraken vault's own WBTC/kBTC Uniswap position, counted in the Kraken row

# Share of each pool that is new to the map: 1 = all of it; 0.5 = one side is a staking token already counted at its issuer
# (LBTC, eBTC, uniBTC, pumpBTC, stBTC); Curve and Ekubo pools less the LP that Stake DAO, Convex, Beefy or Troves hold
# (counted in those rows); 'kraken' = less the Kraken vault's position; BTC/ETH pools count their BTC half.
C6_NAME = 'LP, emissions, farming, DeFi vaults'
ADD = [
    ('Uniswap v3 BTC-pair pools (over $1M)', 'uniswap-v3', 'C6', 'DEX LP (BTC pairs)', [
        ('7b78fe2f-6f67-46ef-8a42-1e36de8d0dfc', 'kraken', 'WBTC/kBTC 0.01%'),
        ('c0bbcf6c-9454-4773-a19f-c6486484c287', 1, 'WBTC/cbBTC 0.01%'),
        ('40769df5-74ce-4d6c-886f-ac4d5f771227', 1, 'WBTC/SolvBTC 0.05%'),
        ('b4ef32d6-04da-400c-bd82-8342a5b094a6', 1, 'tBTC/WBTC 0.01%'),
        ('a855fac3-6d35-4bb9-9b0b-b73820025a7c', 0.5, 'uniBTC/WBTC 0.05%'),
        ('712d2037-a22b-4e5f-897f-ad7532a725fb', 1, 'WBTC/FBTC 0.3%'),
        ('96421b44-5695-46ff-b88f-8ef71e8f0593', 1, 'tBTC/WBTC 0.05%'),
        ('ea24c06e-aac9-4ee8-9bf0-04f16535c632', 1, 'WBTC/cbBTC 0.01% (Arbitrum)'),
        ('b84fda77-bad7-41f3-a3e5-9bf974b6d796', 0.5, 'WBTC/stBTC 0.05%')]),
    ('Uniswap v4 BTC-pair pools (over $1M)', 'uniswap-v4', 'C6', 'DEX LP (BTC pairs)', [
        ('1ba55596-294c-4aa5-b1fa-615e8dd3ccdd', 1, 'WBTC/cbBTC 0.01%'),
        ('634d5a69-2160-456c-82f6-55ff7781de57', 1, 'WBTC/cbBTC 0.01% (second pool)'),
        ('bbc7744d-97f8-538a-a61f-3c82ba6c0c6d', 1, 'BTC.b/cbBTC 0.01%'),
        ('4df86e5d-161e-4221-b74b-bae9cc194991', 1, 'tBTC/cbBTC 0.01%'),
        ('bcbf0f11-17c5-5182-ab62-534b045d367a', 0.5, 'LBTC/cbBTC 0.02%')]),
    ('Fluid DEX BTC pools (over $1M)', 'fluid-dex', 'C6', 'DEX LP (BTC pairs)', [
        ('8e47b0df-d495-4224-bd98-6cf693e88745', 1, 'WBTC/cbBTC'),
        ('a3fd94a1-2b63-4753-b10a-1436b58768c9', 0.5, 'eBTC/cbBTC'),
        ('a346d9ce-65df-4681-b9fa-777b91d8d72a', 0.5, 'WBTC/LBTC')]),
    ('Curve BTC pools (over $1M, LP not staked via Convex or Stake DAO)', 'curve-dex', 'C6', 'DEX LP (BTC pairs)', [
        ('3dadbe45-e87f-43a5-820a-20c908bef612', round(1 - 0.86 / 12.33, 3), 'tBTC/WBTC 2BTC-f, less Stake DAO'),
        ('1a97c851-f2e5-4408-9113-ef80f1c1fea6', round(2 / 3, 3), 'cbBTC/WBTC/LBTC (Monad), less the LBTC third'),
        ('25e631a3-bdba-43a8-81ff-46000465212f', 0.5, 'pumpBTC/WBTC'),
        ('9beef608-8e7b-455b-97a1-84247be6631d', round(1 - (0.33 + 0.78) / 1.40, 3), 'WBTC/tBTC 2BTC-ng (Arbitrum), less Stake DAO and Beefy')]),
    ('Ekubo BTC pools (Starknet, over $1M)', 'ekubo', 'C6', 'DEX LP (BTC pairs)', [
        ('42284cfd-a59f-4128-8677-bbaeb0519148', round(1 - 1.32 / 4.25, 3), 'WBTC/strkBTC, less Troves'),
        ('fd90352e-6772-472c-a0d4-cdef49027da5', 1, 'SolvBTC/strkBTC')]),
    ('Aerodrome Slipstream cbBTC/LBTC (Base)', 'aerodrome-slipstream', 'C6', 'DEX LP (BTC pairs)', [
        ('ff009fa1-2dda-43e0-a0e2-302787e736c8', 0.5, 'cbBTC/LBTC CL1')]),
    ('Orca BTC pools (Solana, over $1M)', 'orca-dex', 'C6', 'DEX LP (BTC pairs)', [
        ('8ed557d7-4ba3-4072-bcf3-e3a5c0172764', 1, 'cbBTC/FBTC'),
        ('42dc3364-dd6b-47e7-a2e3-f4907bb3b5d2', 1, 'cbBTC/WBTC')]),
    ('Bancor v3 WBTC pool', 'bancor-v3', 'C6', 'DEX LP (single-sided WBTC)', [
        ('a4bbf4e6-9b70-4774-817b-410f3f7c0b9b', 1, 'WBTC')]),
    ('Chainflip AMM (native BTC)', 'chainflip-amm', 'C6', 'DEX LP (native BTC)', [
        ('55b7d4ba-fe9a-4a26-ac49-965b6344a490', 1, 'BTC')]),
    ('Hydration Omnipool tBTC (Polkadot)', 'hydration-dex', 'C6', 'DEX LP (single-sided tBTC)', [
        ('eab4ef8c-f35c-434b-a2ea-f8136f1cbc29', 1, 'tBTC in the Omnipool')]),
    ('BeraPaw Kodiak WBTC/WETH (Berachain)', 'berapaw', 'C6', 'DEX LP (BTC/ETH), staked for PoL rewards', [
        ('47444258-5cc2-4e33-95a7-1bc5df79b83b', 0.5, 'KODI WBTC/WETH, BTC half')]),
    ('GMX v2 BTC-only pool (GM BTC/USD, WBTC.b)', 'gmx-v2-perps', 'C6', 'Perp LP: counterparty to traders', [
        ('ffb4e407-6507-4615-b776-a0d99cfc1bbb', 1, 'GM BTC/USD [WBTC.b-WBTC.b] (Arbitrum)')]),
    ('Across WBTC pool (bridge liquidity)', 'across', 'C6', 'Bridge LP: relayer fees', [
        ('07d1a9bf-eafe-4a25-8dcc-c687a1d2478a', 1, 'WBTC LP')]),
    ('Multipli xWBTC', 'multipli.fi', 'C3', 'Delta-neutral fund access (mechanism per Multipli, not verified)', [
        ('884fbcac-b615-438e-952b-430da7f191f2', 1, 'xWBTC')]),
]
WHY = {
    'uniswap-v3': 'BTC-pair DEX pools over $1M (in scope since the 2026-09-23 cross-check); trading fees in BTC.',
    'uniswap-v4': 'BTC-pair DEX pools over $1M (in scope since the 2026-09-23 cross-check); trading fees in BTC.',
    'fluid-dex': 'BTC-pair DEX pools over $1M; Fluid pools double as smart collateral, so part of this BTC also backs loans.',
    'curve-dex': 'BTC-pair DEX pools over $1M; the LP staked through Convex or Stake DAO is already counted in those rows.',
    'ekubo': 'BTC-pair DEX pools over $1M on Starknet; the LP held by Troves is counted in the Troves row.',
    'aerodrome-slipstream': 'BTC-pair DEX pool over $1M; AERO emissions on top of fees.',
    'orca-dex': 'BTC-pair DEX pools over $1M on Solana.',
    'bancor-v3': 'Single-sided WBTC pool over $1M; pays almost nothing since Bancor v3 wound down.',
    'chainflip-amm': 'Native BTC liquidity for cross-chain swaps; was excluded with all DEX LPs until 2026-09-23.',
    'hydration-dex': 'Single-sided tBTC in the Hydration Omnipool, over $1M; HDX rewards on top.',
    'berapaw': 'Kodiak WBTC/WETH LP staked in BeraPaw for PoL rewards; only the BTC half is counted.',
    'gmx-v2-perps': 'BTC-only GM pool: LPs earn trading, borrowing and funding fees and take the other side of traders; paid in BTC.',
    'across': 'Single-sided WBTC for bridge fills; relayer fees plus ACX rewards.',
    'multipli.fi': 'xWBTC routes WBTC to institutional delta-neutral strategies (Multipli names Nomura, Fasanara and Edge Capital).',
}
# Lending: the BTC is lent out. These stay in the map; data/lending_products.csv lists them for the site's lending switch.
LEND = {
    'Hilbert Xapo Byzantine BTC Credit Fund': 'BTC loans to institutions (credit fund).',
    'Accountable YieldApp (cbBTC/wcBTC)': 'cbBTC lent to verified borrowers, uncollateralized (the largest vault lends to Hyperithm).',
    'Two Prime Axiom WBTC Vault (Pareto)': 'WBTC lent to institutions through Two Prime.',
    'Solv RWA (SolvBTC)': 'SolvBTC allocated to RWA credit.',
    'Native Credit Pool (BTC part)': 'BTC lent to Native PMM market makers.',
    'Zest v2 (sBTC supply)': 'sBTC supplied to a lending market (Zest).',
    'Yearn (BTC vaults)': 'WBTC yVaults lend on money markets (Morpho, Aave and others).',
    'Harvest (BTC)': 'Vaults lend on Morpho, Dolomite and Arcadia (Autopilot).',
    'Superform (BTC)': 'SuperVaults allocate to lending vaults.',
    'Vesper (WBTC)': 'Pools lend WBTC on money markets.',
    'Moonwell vaults (cbBTC)': 'Morpho lending vaults.',
    'DeltaPrime (BTC)': 'Deposit pools lend BTC to leveraged borrowers.',
    'Extra Finance (cbBTC)': 'Lending pool for leveraged farmers.',
    'Radpie (BTC)': 'BTC supplied to Radiant, a money market.',
    'Wildcat (BTC)': 'BTC lent to market makers (Wintermute and others), uncollateralized.',
    # in the history only (below the listing threshold today)
    'Seamless vaults (cbBTC)': 'Morpho lending vaults (Seamless).',
}
# Wildcat: DefiLlama's own series counts only undrawn BTC, so the snapshot uses the total supplied that DefiLlama's BTC pool
# page showed on 2026-09-23 (Wintermute cbBTC $10.49M and WBTC $3.04M, Auros $0.14M, Hyperithm $0.07M; 4 to 4.5%),
# converted at that day's BTC price ($85,362, coins.llama.fi). No history: its old history rows are undrawn balances only.
WILDCAT_USD_0923, BTC_0923 = 13740578, 85362.09


def fetch_chart(pid):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, pid + '.json')
    if not os.path.exists(p):
        for attempt in range(4):
            req = urllib.request.Request('https://yields.llama.fi/chart/' + pid, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                body = urllib.request.urlopen(req, timeout=60).read()
                json.loads(body)
                open(p, 'wb').write(body)
                break
            except Exception:
                time.sleep(8 * (attempt + 1))
        else:
            raise SystemExit('could not fetch pool chart ' + pid)
    return {r['timestamp'][:10]: r['tvlUsd'] for r in json.load(open(p))['data'] if r.get('tvlUsd') is not None}


def month_end_value(series, month):
    y, m = int(month[:4]), int(month[5:])
    last = (datetime.date(y + m // 12, m % 12 + 1, 1) - datetime.timedelta(days=1))
    if month == SNAP[:7]:
        return series.get(SNAP, 0.0)
    for back in range(7):  # the point stamped on the last day, else the latest in the week before
        d = (last - datetime.timedelta(days=back)).isoformat()
        if d in series:
            return series[d]
    return 0.0


EOL = {}  # keep each file's line endings (the history files use CRLF)


def rd(name):
    with open(os.path.join(DATA, name), 'rb') as f:
        EOL[name] = '\r\n' if b'\r\n' in f.readline() else '\n'
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))


def wr(name, rows, fields):
    if name not in EOL:
        rd(name)
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator=EOL[name])
        w.writeheader()
        w.writerows(rows)


cur, hist, cath = rd('market_map_current.csv'), rd('market_map_history_monthly.csv'), rd('category_history_monthly.csv')
cur_fields, hist_fields = list(cur[0].keys()), list(hist[0].keys())
months = sorted({r['month'] for r in cath})
# month-end BTC price used by the map: net USD over net BTC of the month (all rows share one price)
price = {}
for m in months:
    u = sum(float(r['tvl_usd_net']) for r in cath if r['month'] == m)
    b = sum(float(r['tvl_btc_net']) for r in cath if r['month'] == m)
    price[m] = u / b
c5_name = next(r['category_name'] for r in cur if r['category_code'] == 'C5')

# drop rows from an earlier run, the old excluded Chainflip row and Wildcat's undrawn-only history
added = {a[0] for a in ADD}
cur = [r for r in cur if MARK not in r['source'] and not (r['category_code'] == 'EXCL' and r['product'] == 'Chainflip AMM (native BTC)')]
hist = [r for r in hist if r['product'] not in added and r['product'] != 'Wildcat (BTC)']

# 1. lending: add Wildcat, then list every lending product for the site
wbtc = WILDCAT_USD_0923 / BTC_0923
cur.append({'product': 'Wildcat (BTC)', 'slug': 'wildcat-protocol', 'category_code': 'C5', 'category_name': c5_name,
            'subcategory': 'Uncollateralized credit to market makers', 'tvl_usd': str(round(wbtc * SNAP_PRICE)), 'tvl_btc': str(round(wbtc, 2)),
            'source': f'{MARK} (total supplied on the 2026-09-23 page)', 'method': 'lend-borrow (page)', 'offchain': '0',
            'double_count_note': 'Snapshot only; DefiLlama history counts only undrawn BTC.', 'include_net': '1',
            'justification': 'Lending: ' + LEND['Wildcat (BTC)']})
cat_of = {r['product']: r['category_code'] for r in hist}
cat_of.update({r['product']: r['category_code'] for r in cur})
names = {r['product'] for r in cur}
lend_rows = [{'product': n, 'category_code': cat_of.get(n, ''), 'in_snapshot': 'yes' if n in names else 'history only', 'reason': why}
             for n, why in LEND.items()]
with open(os.path.join(DATA, 'lending_products.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['product', 'category_code', 'in_snapshot', 'reason'], lineterminator='\n')
    w.writeheader(); w.writerows(lend_rows)

# 2. add the missed pools
for product, slug, cat, sub, pools in ADD:
    series = {}
    shares, parts = [], []
    for pid, share, label in pools:
        s = fetch_chart(pid)
        if share == 'kraken':
            snap_btc = s.get(SNAP, 0.0) / SNAP_PRICE
            share = round(max(0.0, 1 - KRAKEN_UNI_BTC / snap_btc), 3) if snap_btc else 0.0
        series[pid] = (s, share)
        parts.append(f'{label} x{share:g}' if share != 1 else label)
    snap_usd = sum(s.get(SNAP, 0.0) * share for s, share in series.values())
    cur.append({'product': product, 'slug': slug, 'category_code': cat,
                'category_name': C6_NAME if cat == 'C6' else 'Basis & delta-neutral', 'subcategory': sub,
                'tvl_usd': str(round(snap_usd)), 'tvl_btc': str(round(snap_usd / SNAP_PRICE, 2)),
                'source': f'{MARK} ({SNAP} point)', 'method': 'yields-pool', 'offchain': '0',
                'double_count_note': 'Pools: ' + '; '.join(parts) + '.', 'include_net': '1', 'justification': WHY[slug]})
    for m in months:
        usd = sum(month_end_value(s, m) * share for s, share in series.values())
        if usd > 0:
            hist.append({'month': m, 'product': product, 'category_code': cat, 'tvl_usd': str(round(usd)),
                         'tvl_btc': str(round(usd / (SNAP_PRICE if m == SNAP[:7] else price[m]), 3)), 'include_net': '1'})

# keep the file layout: categories in their block order, largest first
order = {c: i for i, c in enumerate(['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C0', 'EXCL'])}
cur.sort(key=lambda r: (order.get(r['category_code'], 9), -float(r['tvl_usd'] or 0)))
hist.sort(key=lambda r: r['month'])  # stable: keeps the product order within a month
wr('market_map_current.csv', cur, cur_fields)
wr('market_map_history_monthly.csv', hist, hist_fields)

# 3. category history and flows, same method as 10_build.py
g = {(m, c): [0.0, 0.0, 0.0, 0.0] for m in months for c in CATS}
for r in hist:
    if r['category_code'] not in CATS:
        continue
    x = g[(r['month'], r['category_code'])]
    u, b = float(r['tvl_usd']), float(r['tvl_btc'])
    x[0] += u; x[1] += b
    if r['include_net'] == '1':
        x[2] += u; x[3] += b
out = []
for m in months:
    tot = sum(g[(m, c)][3] for c in CATS)
    for c in CATS:
        ug, bg, un, bn = g[(m, c)]
        out.append({'month': m, 'category_code': c, 'tvl_usd_gross': str(round(ug)), 'tvl_btc_gross': str(round(bg, 2)),
                    'tvl_usd_net': str(round(un)), 'tvl_btc_net': str(round(bn, 2)), 'share_net': str(round(bn / tot, 4) if tot else 0.0)})
wr('category_history_monthly.csv', out, ['month', 'category_code', 'tvl_usd_gross', 'tvl_btc_gross', 'tvl_usd_net', 'tvl_btc_net', 'share_net'])

net = {(r['month'], r['category_code']): (float(r['tvl_usd_net']), float(r['tvl_btc_net'])) for r in out}
for m in months:
    net[(m, 'ALL')] = (sum(net[(m, c)][0] for c in CATS), sum(net[(m, c)][1] for c in CATS))
P = {m: net[(m, 'ALL')][0] / net[(m, 'ALL')][1] for m in months}
flows = []
for i in range(1, len(months)):
    m0, m1 = months[i - 1], months[i]
    for c in CATS + ['ALL']:
        (u0, b0), (u1, b1) = net[(m0, c)], net[(m1, c)]
        flow, pe = (b1 - b0) * (P[m0] + P[m1]) / 2, (P[m1] - P[m0]) * (b0 + b1) / 2
        flows.append({'month': m1, 'category_code': c, 'delta_usd_net': str(round(u1 - u0)), 'net_flow_btc': str(round(b1 - b0, 2)),
                      'net_flow_usd': str(round(flow)), 'price_effect_usd': str(round(pe)), 'residual_usd': str(round(u1 - u0 - flow - pe))})
wr('category_flows_monthly.csv', flows, ['month', 'category_code', 'delta_usd_net', 'net_flow_btc', 'net_flow_usd', 'price_effect_usd', 'residual_usd'])

inc = [r for r in cur if r['include_net'] == '1' and r['category_code'] in CATS]
print('net products', len(inc), 'net BTC', round(sum(float(r['tvl_btc']) for r in inc)))
for a in ADD:
    r = next(x for x in cur if x['product'] == a[0])
    print(f"  + {r['tvl_btc']:>8} BTC  {a[0]}")
