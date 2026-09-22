"""Write overlap.md, notes.md and jump_candidates.csv from the build outputs (run after 10_build.py)."""
import json, os, sys, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import D, RAW, PRICE_SNAP
from products import P
S = json.load(open(os.path.join(RAW, 'build_summary.json')))
cur = list(csv.DictReader(open(os.path.join(D, 'market_map_current.csv'))))
cat = list(csv.DictReader(open(os.path.join(D, 'category_history_monthly.csv'))))
hist = list(csv.DictReader(open(os.path.join(D, 'market_map_history_monthly.csv'))))
flows = list(csv.DictReader(open(os.path.join(D, 'category_flows_monthly.csv'))))
YC = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
NAMES = {'C1': 'Carry (BTC collateral + USD loan)', 'C2': 'Staking & restaking', 'C3': 'Basis & delta-neutral', 'C4': 'Options selling',
         'C5': 'Credit to institutions', 'C6': 'LP / emissions / farming / DeFi vaults'}
f0 = lambda x: f'{x:,.0f}'
fm = lambda x: f'${x/1e6:,.1f}M'
fb = lambda x: f'${x/1e9:,.2f}B'
num = lambda s: float(s) if s not in ('', None) else 0.0
PBY = {p['id']: p for p in P}

# ---------- current totals ----------
def tot(filter_):
    u = sum(num(r['tvl_usd']) for r in cur if filter_(r)); b = sum(num(r['tvl_btc']) for r in cur if filter_(r)); return u, b
isy = lambda r: r['category_code'] in YC and r['tvl_usd'] != '' and not r['product'].endswith('(memo)')
G = tot(isy); N = tot(lambda r: isy(r) and r['include_net'] == '1')
Gon = tot(lambda r: isy(r) and r['offchain'] == '0'); Non = tot(lambda r: isy(r) and r['include_net'] == '1' and r['offchain'] == '0')
bycat = {c: (tot(lambda r, c=c: isy(r) and r['category_code'] == c), tot(lambda r, c=c: isy(r) and r['category_code'] == c and r['include_net'] == '1')) for c in YC}
c0 = [r for r in cur if r['category_code'] == 'C0']
c0_mm = [r for r in c0 if r['product'].startswith('Money-market')][0]
c0_cur = sum(num(r['tvl_btc']) for r in c0 if r['product'].startswith('Curator'))
c0_cdp = sum(num(r['tvl_btc']) for r in c0 if r['product'].startswith('CDP'))
c0_venue = sum(num(r['tvl_btc']) for r in c0 if r['product'].startswith('Lending venue'))

bab_fp = S['babylon_current_fp']; bab_tot = sum(bab_fp.values())
bab_g = S['babylon_current_groups']
GROUP_PRODUCT = {'GTBTC (Gate Earn)': 'Gate GTBTC', 'Bedrock uniBTC': 'Bedrock uniBTC', 'Lombard LBTC': 'Lombard LBTC', 'SolvBTC LSTs': 'SolvBTC LSTs',
                 'PumpBTC': 'PumpBTC', 'Lorenzo stBTC': 'Lorenzo stBTC', 'Chakra': 'Chakra', 'alloBTC': 'alloBTC', 'B2 Buzz': 'B2 Buzz Farming'}
ov_cur = S['babylon_overlap_monthly'].get('2026-09', {})
ov_sum = sum(ov_cur.values())
figment = bab_fp.get('Figment', 0.0)
core_btc = PBY['core-staking']['btc']
# nesting (current)
nest = S['nesting_current']
nest_rows = []
for iss, hs in nest.items():
    for h, u in hs.items():
        if u >= 5e5: nest_rows.append((PBY[iss]['product'], PBY[h]['product'], u))
nest_rows.sort(key=lambda x: -x[2])
excl_rows = [r for r in cur if isy(r) and r['include_net'] == '0']

# ---------- history: gross / net / overlap per month ----------
months = sorted({r['month'] for r in cat})
gm = {m: sum(num(r['tvl_btc_gross']) for r in cat if r['month'] == m) for m in months}
nm = {m: sum(num(r['tvl_btc_net']) for r in cat if r['month'] == m) for m in months}
gu = {m: sum(num(r['tvl_usd_gross']) for r in cat if r['month'] == m) for m in months}
nu = {m: sum(num(r['tvl_usd_net']) for r in cat if r['month'] == m) for m in months}
bab_split = collections.defaultdict(float); nest_split = collections.defaultdict(float); other_ex = collections.defaultdict(float)
for r in hist:
    if r['include_net'] == '1': continue
    b = num(r['tvl_btc'])
    if 'stake attributed to listed' in r['product']: bab_split[r['month']] += b
    elif 'held inside other listed' in r['product'] or 'credit cover for Lombard' in r['product']: nest_split[r['month']] += b
    else: other_ex[r['month']] += b
bom = S['babylon_overlap_monthly']
share = {(r['month'], r['category_code']): num(r['share_net']) for r in cat}
netb = {(r['month'], r['category_code']): num(r['tvl_btc_net']) for r in cat}
netu = {(r['month'], r['category_code']): num(r['tvl_usd_net']) for r in cat}
rank = {m: sorted(YC, key=lambda c: -netu[(m, c)]) for m in months}
second_changes = [(months[i], rank[months[i - 1]][1], rank[months[i]][1]) for i in range(1, len(months)) if rank[months[i]][1] != rank[months[i - 1]][1]]

# ---------- jump candidates ----------
with open(os.path.join(D, 'jump_candidates.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'product', 'slug', 'btc_part_usd_before', 'btc_part_usd_after', 'usd_7d_later', 'change'])
    for j in sorted(S['jumps'], key=lambda x: (x['product'], x['date'])):
        w.writerow([j['date'], j['product'], j['slug'], j['from_usd'], j['to_usd'], j['after_7d_usd'], j['change']])

# ================= overlap.md =================
L = []
L.append('# Double counting: Babylon, LSTs and nested vaults (snapshot 2026-09-20)\n')
L.append('BTC price for conversion: $81,178 (Binance BTCUSDT close 2026-09-20). "Gross" = every product row in C1-C6; '
         '"net" = each BTC counted once, at the outermost product the holder owns (the rule in plan 0.3: count where the BTC earns, at the top level).\n')
L.append('## 1. Totals\n')
L.append('| Measure | USD | BTC |\n|---|---:|---:|')
L.append(f'| Gross, on-chain rows | {fb(Gon[0])} | {f0(Gon[1])} |')
L.append(f'| Net, on-chain rows | {fb(Non[0])} | {f0(Non[1])} |')
L.append(f'| Gross incl. disclosed off-chain AUM | {fb(G[0])} | {f0(G[1])} |')
L.append(f'| **Net incl. disclosed off-chain AUM (central)** | **{fb(N[0])}** | **{f0(N[1])}** |')
lo = N[1] - figment - core_btc
L.append(f'| Net, low end of range (see section 5) | {fb(lo * PRICE_SNAP)} | {f0(lo)} |')
L.append(f'| Gross minus net (removed overlap) | {fb(G[0] - N[0])} | {f0(G[1] - N[1])} |\n')
L.append('Not in these totals: C0 context (money-market collateral, curator BTC lending vaults, CDPs), excluded wrappers, '
         'Coinbase CBYF (size unknown, left blank). Maple BTC Yield is 0 today (wound down 11-2025) with an on-chain history.\n')
L.append('By category (current):\n')
L.append('| Category | Gross BTC | Net BTC | Net USD | Net share |\n|---|---:|---:|---:|---:|')
for c in YC:
    (gu_, gb_), (nu_, nb_) = bycat[c]
    L.append(f'| {c} {NAMES[c]} | {f0(gb_)} | {f0(nb_)} | {fm(nu_)} | {nu_ / N[0] * 100:.1f}% |')
L.append(f'| **Total** | **{f0(G[1])}** | **{f0(N[1])}** | **{fm(N[0])}** | 100% |\n')

L.append('## 2. Babylon vs LSTs\n')
L.append(f'Babylon TVL on DefiLlama at 2026-09-20: {f0(num([r for r in cur if r["product"].startswith("Babylon") and "other stakers" in r["product"]][0]["tvl_btc"]) + ov_sum)} BTC '
         f'(equals the sum of active delegations to *active* finality providers: {f0(bab_tot)} BTC in the Babylon LCD `btc_delegations/ACTIVE` list, 1,398 delegations, 217 staker keys).\n')
L.append('**Method.** Babylon exposes no per-product breakdown, so stake is attributed through finality providers (FPs) whose '
         'operator names a product (Lombard*, Solv*, RockX-Bedrock, PumpBTC, lorenzo, Chakra, Allo, BSquared*, Gate Earn). '
         'Sources: `staking-api.babylonlabs.io/v2/stats`, `/v2/finality-providers`; `babylon-rest.publicnode.com/babylon/btcstaking/v1/btc_delegations/ACTIVE`. '
         'Delegations to *inactive* FPs are not in Babylon\'s active TVL (and not in DefiLlama), so they are not an overlap.\n')
L.append('Composition of active Babylon stake by finality provider (BTC):\n')
L.append('| Finality provider | BTC | Share | Maps to listed product? |\n|---|---:|---:|---|')
FPMAP = {'Gate Earn': 'GTBTC (Gate)', 'RockX-Bedrock': 'Bedrock uniBTC', 'Lombard Finance': 'Lombard LBTC', 'Solv Protocol': 'SolvBTC LSTs',
         'Kraken': 'no: Kraken exchange staking (custodial)', 'Kraken02': 'no: Kraken exchange staking (custodial)', 'Binance Finality Provider': 'no: Binance',
         'OKX Earn': 'no: OKX Earn (CeFi)', 'Figment': 'unattributed institutional (upper-bound case)'}
for k, v in list(bab_fp.items())[:12]:
    L.append(f'| {k} | {f0(v)} | {v / bab_tot * 100:.1f}% | {FPMAP.get(k, "no")} |')
rest = bab_tot - sum(list(bab_fp.values())[:12])
L.append(f'| other {len(bab_fp) - 12} FPs | {f0(rest)} | {rest / bab_tot * 100:.1f}% | no |\n')
L.append('Overlap table (current):\n')
L.append('| Listed product | Product BTC (gross) | BTC it stakes in Babylon (active) | Treatment |\n|---|---:|---:|---|')
prodbtc = {}
for r in cur:
    for g, pn in GROUP_PRODUCT.items():
        if r['product'].startswith(pn): prodbtc[g] = prodbtc.get(g, 0) + num(r['tvl_btc'])
for g in ['GTBTC (Gate Earn)', 'Bedrock uniBTC', 'Lombard LBTC', 'SolvBTC LSTs', 'PumpBTC', 'Lorenzo stBTC', 'B2 Buzz']:
    L.append(f'| {GROUP_PRODUCT[g]} | {f0(prodbtc.get(g, 0))} | {f0(bab_g.get(g, 0))} | ' + ('removed from the Babylon row, counted in the product |' if bab_g.get(g, 0) >= 0.5 else 'no active stake today |'))
L.append(f'| **Total removed from Babylon** | | **{f0(ov_sum)}** | Babylon net = {f0(bab_tot - ov_sum)} BTC |\n')
L.append(f'- Kraken (FPs "Kraken" + "Kraken02") is {f0(bab_fp.get("Kraken", 0) + bab_fp.get("Kraken02", 0))} BTC, '
         f'{(bab_fp.get("Kraken", 0) + bab_fp.get("Kraken02", 0)) / bab_tot * 100:.0f}% of Babylon. It is custodial exchange staking; it stays in the Babylon row. '
         'Whether any of it is the kBTC reserve behind the Kraken Bitcoin Vault (6,492.7 BTC) cannot be checked from public data; no overlap is assumed.')
L.append('- Lombard: only 42 BTC remain on an active Lombard FP. A further 2,500 BTC sit on the *inactive* "Lombard x P2P.org" FP; this stake is outside Babylon\'s active TVL and outside DefiLlama\'s Babylon number, so it is not double counted.')
L.append(f'- Figment ({f0(figment)} BTC) is an institutional operator; Lombard used separate "Lombard x Figment" FPs, so plain Figment stake is not attributed. It is the upper-bound case in section 5.\n')

L.append('## 3. Nested holdings (LST held inside another listed product)\n')
L.append('Each yield-bearing BTC token held by another listed product is counted once, at the holder (outer product), and removed from the issuer row. '
         'Holdings come from the holders\' DefiLlama token breakdowns (symbols LBTC, BTCOC, UNIBTC/BRBTC, PUMPBTC, SOLVBTC.BBN/XSOLVBTC, SOLVBTC.TRADING, BFBTC, '
         'GTBTC, MHYPERBTC, EBTC, AVBTC, STBTC, ASBTC).\n')
L.append('| Issuer (removed from) | Holder (counted in) | USD | BTC |\n|---|---|---:|---:|')
for iss, h, u in nest_rows:
    L.append(f'| {iss} | {h} | {fm(u)} | {f0(u / PRICE_SNAP)} |')
L.append(f'| Symbiotic (removed from) | Lombard Vaults (BTCe credit leg) | {fm(S["symb_in_lv_current"])} | {f0(S["symb_in_lv_current"] / PRICE_SNAP)} |')
L.append('| (holders under $0.5M omitted from this table; included in the numbers) | | | |\n')
L.append('**LBTC -> LBTCv -> BTCe (counted once).** LBTC supply is backed by 8,499 BTC at the 09-20 point. Lombard Vaults (LBTCv; BTCe is a wrapper over LBTCv) hold '
         '71 LBTC, 580 BTCOC (the LBTC-backed token of the BTCe credit strategy), 188 cbBTC and 75 BTC.b. The 580 BTCOC is the same LBTC that Symbiotic reports '
         'as 583 LBTC in the "Lombard-Flow Traders" vault (slashable cover for Flow Traders\' loan on Cap). Treatment: 651 LBTC-equivalent removed from LBTC; the Symbiotic '
         'LBTC removed from Symbiotic; the whole Lombard Vaults balance (919 BTC) counted once in C5. LBTC\'s own covered-call program is counted in the LBTC row (C4); '
         'the off-chain memo row is not added.\n')
L.append('**SolvBTC LSTs vs Solv Basis.** No overlap in the net: the two rows count different token supplies (SolvBTC.BBN backing: locked FBTC + native BTC; '
         'SolvBTC.TRADING supply for the basis fund). The base SolvBTC wrapper, which backs both, is excluded as a wrapper. Solv Strategies (SolvBTC in LP/farming) and '
         'Solv RWA are separate supplies too. Only 31 BTC of Solv stake is active in Babylon (removed from Babylon).\n')
L.append('**uniBTC vs Babylon.** 153 BTC is staked in Babylon via the RockX-Bedrock FP (removed from Babylon). Most uniBTC sits in Symbiotic (2,624 uniBTC) and '
         'Mellow (107): counted at those holders and removed from the uniBTC row.\n')
L.append('**Other rows kept out of the net** (gross only):\n')
for r in excl_rows:
    if 'held inside' in r['product'] or 'stake attributed' in r['product'] or 'credit cover' in r['product']: continue
    L.append(f'- {r["product"]}: {f0(num(r["tvl_btc"]))} BTC. {r["double_count_note"]}')
L.append('- Syntetika hBTC disclosed AUM (~$16.1M) and the Lombard covered call are memo rows: the same money is already in the on-chain Syntetika and LBTC rows.\n')

L.append('## 4. Overlap over time\n')
L.append(f'Babylon history source: `raw/{S["babylon_hist_source"]}` (stake of product-linked staker keys / FPs, rebuilt from phase-1 (v1) and phase-2 (v2) '
         'delegations; stake end = block height of the transaction spending the staking output, from mempool.space, for stakes >= 2 BTC). '
         'Attributed stake is capped at the product\'s own DefiLlama BTC and at Babylon\'s total. Excludes the products whose history is pending (Kraken vault, Bitget, ether.fi Liquid BTC), Core and off-chain rows.\n')
L.append('| Month | Gross BTC | Net BTC | Babylon stake removed (LSTs) | Nested LST removed | Other gross-only rows |\n|---|---:|---:|---:|---:|---:|')
for m in months:
    L.append(f'| {m} | {f0(gm[m])} | {f0(nm[m])} | {f0(bab_split.get(m, 0))} | {f0(nest_split.get(m, 0))} | {f0(other_ex.get(m, 0))} |')
L.append('')
L.append('Babylon stake attributed to listed products, by product (BTC, month-end):\n')
pids = sorted({k for v in bom.values() for k in v})
L.append('| Month | ' + ' | '.join(PBY[p]['product'] for p in pids) + ' |\n|---|' + '---:|' * len(pids))
for m in months:
    L.append(f'| {m} | ' + ' | '.join(f0(bom.get(m, {}).get(p, 0)) for p in pids) + ' |')
L.append('')
L.append('## 5. Range and unresolved overlaps\n')
L.append(f'- **Central net: {f0(N[1])} BTC ({fb(N[0])}).**')
L.append(f'- **Low net: {f0(lo)} BTC.** Subtracts (a) all plain-Figment Babylon stake ({f0(figment)} BTC) as if it belonged to listed LSTs, and '
         f'(b) all Core staking ({f0(core_btc)} BTC) as if it were b14g\'s BTC (b14g reports 3,181 BTC on Bitcoin, more than Core\'s whole staked BTC, so b14g cannot be entirely Core stake; the true overlap is somewhere in 0-2,210).')
L.append('- **Not netted, no evidence either way:** Kraken exchange staking in Babylon (32,932 BTC) vs the Kraken Bitcoin Vault (6,492.7 BTC, kBTC-based); '
         'Maple BTC Yield vs Core staking (Maple staked on Core in 2025; Core rows are current only); Yearn/Beefy/Stake DAO Curve-LP vaults that may sit inside Convex (a few million USD); '
         'ether.fi eBTC (276 BTC, yields pool) vs Veda "other BTC vaults" (eBTC is a Veda BoringVault, but Veda\'s Ethereum WBTC balance, 1,449 BTC, is much larger than eBTC).')
L.append('- **Historical months:** the Babylon attribution follows the staker keys that ever delegated to a product-branded FP (321 keys, top keys per product covering ~99% of their branded stake), '
         'including their phase-1 stakes (v1 API). Keys a product never used with a branded FP are missed, so the historical LST overlap is a lower bound and the historical net an upper bound. '
         'Stakes under 2 BTC that ended early use an approximate end height.')
L.append('- **Campaign wrappers:** Royco v1 (up to 15,177 BTC in 2025-04, mostly LBTC/WBTC/xSolvBTC/uniBTC) and YieldNest (nested in Kernel) are gross-only. '
         'If Royco\'s deposits had not been counted anywhere else, the 2025-02..04 net would be 11-15k BTC higher.')
open(os.path.join(D, 'overlap.md'), 'w').write('\n'.join(L) + '\n')

# ================= notes.md =================
cf = collections.defaultdict(lambda: collections.Counter())
for r in flows:
    cf[r['category_code']].update({'d_usd': num(r['delta_usd_net']), 'flow_btc': num(r['net_flow_btc']), 'flow_usd': num(r['net_flow_usd']), 'price': num(r['price_effect_usd'])})
cf10 = collections.defaultdict(lambda: collections.Counter())
for r in flows:
    if r['month'] >= '2024-11': cf10[r['category_code']].update({'d_usd': num(r['delta_usd_net']), 'flow_btc': num(r['net_flow_btc']), 'flow_usd': num(r['net_flow_usd']), 'price': num(r['price_effect_usd'])})
N_ = []
N_.append('# BTC-yield market map: method, exclusions, gaps\n')
N_.append('Snapshot 2026-09-20; history 2024-09 to 2026-09 (month-end). Produced 2026-09-21 from APIs only (DefiLlama, Babylon, Core, Binance, mempool.space). '
          'Values marked ESTIMATE or flagged in `market_map_current.csv` are not measured on-chain.\n')
N_.append('## Files\n')
for f, d in [('market_map_current.csv', 'one row per product (overlapping products split into a gross-only part and a net part); C0 context and excluded wrappers listed at the bottom'),
             ('market_map_history_monthly.csv', 'month x product (same splits), plus an `include_net` column'),
             ('category_history_monthly.csv', 'month x category: gross/net USD and BTC, net share'),
             ('category_flows_monthly.csv', 'month x category: change in net USD split into net flow (BTC change at average price) and price effect (price change on average BTC)'),
             ('c1_pending_proxy_history.csv', 'DefiLlama proxies for the C1 products, for comparison with the merged on-chain histories'),
             ('jump_candidates.csv', 'automatically detected step changes in DefiLlama series (persistent >35% one-day moves over $25M) for review'),
             ('overlap.md', 'double-counting analysis, gross vs net'), ('scripts/', 're-runnable pipeline, see "Re-run" below'), ('raw/', 'all API pulls')]:
    N_.append(f'- `{f}`: {d}.')
N_.append('\n## Conventions\n')
N_.append('- **Snapshot point:** DefiLlama daily point stamped 2026-09-20 00:00 UTC; USD from `tokensInUsd`, BTC = USD / $81,178 (Binance close 2026-09-20). '
          'Values supplied from on-chain work (Kraken 6,492.7 BTC; Yield Basis 1,326.2 BTC of depositor equity; Bitget 801.7 bgBTC; ether.fi Liquid BTC ~232 BTC; Maple 0) are BTC and are converted at $81,178. Their month-end histories are merged from inputs/c1_histories.csv (on-chain).')
N_.append('- **Month-end point:** DefiLlama point stamped 00:00 UTC on the 1st of the next month (= end of the last day), converted at the Binance close of the last day. '
          'The 2026-09 row is the 09-20 snapshot. Yields-pool series use the point stamped on the last day.')
N_.append('- **BTC part only:** sum of BTC-denominated symbols in the protocol-level (or chain-level) `tokensInUsd` breakdown (list in `scripts/lib.py`: BTC, WBTC, cbBTC, BTCB, BTC.b, kBTC, LBTC, tBTC, FBTC, SolvBTC and variants, xSolvBTC, uniBTC/brBTC, enzoBTC, stBTC, bgBTC, sBTC, UBTC, eBTC, LBTCv, pumpBTC, M-BTC/mBTC, YBTC, cirBTC, xBTC, zBTC, bfBTC, lfBTC-*, RBTC, avBTC, mHyperBTC, BTCOC, BTC-only Curve LPs, etc.). '
          'Mixed LP tokens (tricrypto, WBTC/WETH) count at an estimated BTC share (1/3 or 1/2); they are a few million USD in total. '
          'Protocols without a token breakdown that are BTC-only (Hermetica, Lorenzo stBTC, Chakra, alloBTC, pSTAKE, LISA) use total TVL (method `total`).')
N_.append('- **DefiLlama TVL convention:** idle balances; lent-out balances are excluded unless noted. For Accountable and Zest v2 (lending-type yield products) '
          'the `-borrowed` keys are added, so the row is total supplied BTC.')
N_.append('- **Flows vs price:** for months t-1 -> t, net flow = (B_t - B_{t-1}) x (P_{t-1} + P_t)/2 and price effect = (P_t - P_{t-1}) x (B_{t-1} + B_t)/2; the two add up to the USD change exactly.\n')
N_.append('## Universe\n')
N_.append('1. DefiLlama `/protocols` (8,317 protocols): every protocol in Restaked BTC, Anchor BTC, Basis Trading, Leveraged Farming, Onchain Capital Allocator, Yield, Staking Pool, '
          'Restaking, CDP, Yield Aggregator, Governance Incentives, Risk Curators (plus Farm, Options, Options Vault, CeDeFi, Uncollateralized Lending, Liquid Restaking, '
          'Dual-Token Stablecoin and BTC-named Bridge/Liquid Staking entries) was pulled via `/protocol/{slug}` (1994 files). Lending-category protocols were pulled only where they '
          'are yield products (Maple, Zest, Accountable, Native Credit Pool, BTC lending venues); plain money markets are C0 context.')
N_.append('2. Kept: protocols whose BTC-token part is >= ~$0.25M today or reached >= $3M at any month-end since 2024-09 (history screen catches dead products such as Corn, Royco, DeSyn, Pell, Kernel).')
N_.append('3. Added from the catalog/dossiers: Kraken Bitcoin Vault, Bitget bgBTC Earn, ether.fi Liquid BTC, Maple BTC Yield (on-chain history), Core staking (Core API), '
          'Midas mHyperBTC/mRe7BTC/mBTC, Tesseract and BTCD carry vaults, ether.fi eBTC (DefiLlama yields pools), off-chain funds.')
N_.append(f'4. Classified into C1-C6 by the plan\'s taxonomy; any product with a dollar loan against BTC is C1. {sum(1 for r in cur if r["category_code"] in YC)} C1-C6 rows today '
          f'({sum(1 for r in cur if r["category_code"] in YC and r["include_net"] == "1")} in the net).\n')
N_.append('## Key classification decisions\n')
for t in [
    '**Lombard LBTC** switches category: C2 (Babylon LST) through 2026-07, C4 (Bitwise covered call, live 13.08.2026) from 2026-08. Lombard staker keys still had ~10.1k BTC in Babylon at end-June 2026 (all of LBTC) and ~130 BTC at end-July.',
    '**Lombard Vaults (LBTCv/BTCe)**: C6 (DeFi money-market/points vault) through 2026-06; C5 from 2026-07 (BTCe credit leg since 23.07.2026: LBTC as slashable cover for a loan on Cap).',
    '**Yield Basis** is C1 (hybrid: user BTC plus borrowed crvUSD into a 2x LP), per the plan rule "dollar debt under BTC -> C1".',
    '**Avalon CeDeFi** (USDT debt against lfBTC) is C0, not C1: it is a pool for four institutional Safes, the USDT went to Binance deposit addresses, DefiLlama says it is 100% team-deposited and it has been static since 11-2024. It is not a product with outside depositors (top-5 check).',
    '**Hermetica hBTC** stays C1 although the strategy was wound down 18.06.2026 (46.9 BTC left).',
    '**River Omni-CDP** is C0, not a yield product: users post bfBTC/uniBTC/UBTC to mint satUSD. The BTC holder earns nothing from River (only the LST\'s own yield), so it is borrowing context; counting it would double count bfBTC and uniBTC.',
    '**Mezo Earn** (veBTC) is C6 per the plan. Mezo Borrow (MUSD CDP) is C0.',
    '**Zest v2** sBTC supply is C6 (incentive-driven), per the plan; it is removed from the C0 money-market number to avoid counting it twice. Zest\'s "STBTC" ($10.9M) is excluded: the yields API lists it as stSTXbtc (an STX token) while the protocol breakdown prices it as BTC.',
    '**Accountable** (cbBTC/wcBTC) is C5 (uncollateralized credit); also removed from the C0 number.',
    '**Curator BTC vaults** (Gauntlet, Steakhouse, Re7, Sentora WBTC, Hyperithm cbBTC on Monad, etc.) are C0: BTC lending at ~0% (plan: "BTC-vaults Morpho under ~0%"). Sentora\'s and Veda\'s kBTC on Ink are the Kraken vault and are counted only in the Kraken row.',
    '**BitFi** bfBTC: both DefiLlama slugs (EVM chains; AILayer) are C3 (BitFi CeDeFi basis/staking; mechanism not verified). AILayer farm (84.6M on Bitcoin) is treated as the same BTC as bfBTC on AILayer and kept out of the net.',
    '**Vishwa** (865 BTC) and **ObeliskBTC** are placed in C2 with a flag: yield mechanism not disclosed.',
    '**Midas mHyperBTC** is C1 (its strategy wallet posts cbBTC on Morpho/Spark and borrows USDT/USDS; Midas transparency API) and uses the three DefiLlama yields pools ($30.5M in total; the Hyperithm curator entry shows only the Ethereum part). Pool histories start 06-2026, so earlier months are missing.',
    '**Two Prime Axiom** is on-chain (Pareto) but not tracked by DefiLlama; recorded from the dossier (150 WBTC) with offchain=1.',
    '**Xapo Byzantine** (ESTIMATE): $100M phase-1 allocation used = 1,231.9 BTC at $81,178. The 3,000 BTC "seed" (2024) is the upper bound. Reason: the $100M is the fund-level allocation tied to the current mandate; the 2024 seed has no later confirmation and the fund page (launch 15.09.2024, net yield 2.94%) publishes no AUM.',
    '**Starboard Sygnum BTC Alpha**: 750 BTC (disclosed "750+", a lower bound).',
    '**Coinbase CBYF**: size not disclosed; blank, not in totals. **Maple BTC Yield**: 0 today; its 2025 history (up to 1,758 BTC) is reconstructed on-chain from Core CLTV stakes and merged.',
]:
    N_.append(f'- {t}')
N_.append('\n## Exclusions\n')
N_.append('- Bare wrappers and bridges: WBTC, cbBTC, BTCB, kBTC, FBTC, enzoBTC, base SolvBTC, tBTC, BTC.b, bgBTC, sBTC, UBTC (Unit), xBTC (OKX), cirBTC, Nexus BTC, YBTC (Bitlayer), '
          "Merlin's Seal (M-BTC bridge custody), Katana vault bridge, bridge entries for Core/Echo/Mezo/exSat/BOB.")
N_.append('- Yield-tokenization venues (Pendle, Spectra, RateX, Nemo): their BTC is the LSTs already counted.')
N_.append('- USD-denominated products backed partly by BTC (Ethena, Falcon), DEX LPs (out of scope; Chainflip AMM listed as excluded), StackingDAO (STX staking), BTCST (hashrate).')
N_.append(f'- **C0 context (not yield):** money-market BTC collateral {fb(num(c0_mm["tvl_usd"]))} ({f0(num(c0_mm["tvl_btc"]))} BTC; DefiLlama yields pools 09-20: '
          f'{fb(S["mm_total_0920"])} less Zest v2 and Accountable). Separately listed and not additive with it: curator BTC lending vaults {f0(c0_cur)} BTC, '
          f'CDP collateral {f0(c0_cdp)} BTC (includes River {f0(num([r for r in c0 if "River" in r["product"]][0]["tvl_btc"]))} BTC), BTC lending venues {f0(c0_venue)} BTC.\n')
N_.append('## History results\n')
N_.append('| Month | ' + ' | '.join(f'{c} net BTC (share)' for c in YC) + ' | Net BTC | Net USD |\n|---|' + '---:|' * (len(YC) + 2))
for m in months:
    N_.append(f'| {m} | ' + ' | '.join(f'{f0(netb[(m, c)])} ({share[(m, c)] * 100:.1f}%)' for c in YC) + f' | {f0(nm[m])} | {fb(nu[m])} |')
N_.append('')
lead = S['leaders']
N_.append(f'- **Leading category:** C2 (staking & restaking) leads the net in every month from 2024-09 to 2026-09, so the leader never changed '
          f'(gross gives the same answer). Its net share went from {share[("2024-10", "C2")] * 100:.0f}% (2024-10) to a peak of {max(share[(m, "C2")] for m in months) * 100:.0f}% '
          f'and {share[("2026-09", "C2")] * 100:.0f}% now; the drop in 2026-08 is LBTC moving to C4.')
N_.append('- **Second place:** ' + ('; '.join(f'{m}: {a} -> {b}' for m, a, b in second_changes) if second_changes else
          f'{rank[months[0]][1]} in every month') + f'. Third place: ' + ', '.join(sorted({rank[m][2] for m in months})) + '. C4 appears only from 2026-08 (LBTC reclassified); '
          f'C1 peaked at {max(share[(m, "C1")] for m in months) * 100:.1f}% of the net (before the pending Kraken/Bitget/ether.fi histories are merged; with them C1 would be ~10% in 2026-09).')
N_.append('- 2024-09 is incomplete for C2: DefiLlama lists Babylon only from 2024-10-22.')
N_.append('\n"Net flow" is the change in BTC units, so it also contains DefiLlama listing/delisting effects: Babylon listed 2024-10-22 (+~23k BTC in 2024-10), GTBTC listed 2025-11 (+~3k), '
          'Mezo Earn 2026-05, Vishwa 2025-09; DeSyn delisted 2025-11-28 (-~10k BTC in C6); Solv Basis re-scoped 2024-12 (-~7k BTC in C3). Read the category flows with these in mind.\n')
N_.append('Flows vs price, net basis, 2024-09 -> 2026-09 (USD change = net flow + price effect):\n')
N_.append('| Category | USD change | Net flow BTC | Net flow USD | Price effect USD |\n|---|---:|---:|---:|---:|')
for c in YC + ['ALL']:
    v = cf[c]
    N_.append(f'| {c} | {fm(v["d_usd"])} | {f0(v["flow_btc"])} | {fm(v["flow_usd"])} | {fm(v["price"])} |')
N_.append('\nSame from 2024-10 (first month with Babylon on DefiLlama):\n')
N_.append('| Category | USD change | Net flow BTC | Net flow USD | Price effect USD |\n|---|---:|---:|---:|---:|')
for c in YC + ['ALL']:
    v = cf10[c]
    N_.append(f'| {c} | {fm(v["d_usd"])} | {f0(v["flow_btc"])} | {fm(v["flow_usd"])} | {fm(v["price"])} |')
N_.append('\n## Sanity checks\n')
ok = all(v['net_le_gross'] and v['rows_sum_eq_gross'] and v['rows_net_eq_net'] for k, v in S['checks'].items() if k != 'current_vs_history')
cvh = S['checks']['current_vs_history']
N_.append(f'- Category sums = total and product rows sum to category totals, every month: {"pass" if ok else "FAIL"}. Net <= gross every month: {"pass" if ok else "FAIL"}.')
N_.append(f'- 2026-09 history row vs current snapshot, like for like (products with a history): {fb(cvh["history_2026_09_gross"])} vs {fb(cvh["current_like_for_like_gross"])} (gross) - equal.')
pend = [r for r in cur if r['category_code'] in YC and r['tvl_usd'] != '' and (r['method'] in ('on-chain', 'on-chain API', 'disclosed')) and not r['product'].endswith('(memo)')]
N_.append(f'- Current rows without history (not in the monthly files): ' + '; '.join(f'{r["product"]} {f0(num(r["tvl_btc"]))} BTC' for r in pend) +
          f'. Total {f0(sum(num(r["tvl_btc"]) for r in pend))} BTC. Current gross = 2026-09 history gross + these rows.')
N_.append('- **Merging the pending C1 histories:** put `inputs/c1_histories.csv` (columns month, product_id, tvl_btc; ids `kraken-vault`, `bitget-bgbtc-earn`, `etherfi-liquid-btc`) and re-run `10_build.py` and `11_write_reports.py`; '
          'the rows enter history, category totals, shares and flows. DefiLlama proxies are in `c1_pending_proxy_history.csv` (Veda Ink kBTC for Kraken from 2026-05; aera-v3 bgBTC for Bitget from 2026-08; '
          'ether.fi-liquid BTC for ether.fi, which before 2025-05 covers more than the Liquid BTC vault).')
N_.append('\n## DefiLlama methodology jumps and data breaks (review before charting)\n')
for t in [
    'Solv Basis Trading: $735M at end-11-2024 -> $28M at end-12-2024 (one-day drop 2024-12-26, $689M -> $2M) and several flips in 2024-09 and 2025-05: the adapter was re-scoped; C3 in 2024-09..11 is inflated relative to later months.',
    'Royco v1: +$1.25B on 2025-02-03 (Boyco) and -> 0 on 2025-05-08. Gross only (see overlap.md).',
    'DeSyn Liquid Strategy: $1.07B -> 0 on 2025-11-28 (delisting/re-scope); DeSyn Safe -> 0 on 2025-08-08; DeSyn Basis -> 0 on 2024-11-09. C6 falls by ~10k BTC at end-11-2025 for this reason, not flows.',
    'Lombard LBTC: one-day dip 2026-07-15 ($591M -> $251M) and recovery 2026-07-17; month-ends unaffected. Methodology now caps Bitcoin-address BTC at the Lombard ledger balance and adds LFBTC.',
    'Babylon: -48% on 2026-03-12 then back by 2026-03-25 (data gap; month-ends unaffected); +36% on 2024-12-11 (cap-3) and +41% on 2025-04-26 (phase-2 registration) are real flows.',
    'Abrupt drops to ~0 that look like delistings or shutdowns: Kernel (2025-07-11), Pell (2025-12-30), CoinWind (2025-10-04), Flamincome (2025-07-17), Hemi staking (2025-12-02), Chakra (2025-09-03), Solv Others (2025-11-18).',
    'Zircuit staking flips between ~$1M and ~$55M many times (data glitch); month-end values for 2025-06..11 are unreliable (< 700 BTC either way).',
    f'Full list: `jump_candidates.csv` ({len(S["jumps"])} candidate step changes; many are real flows).',
]:
    N_.append(f'- {t}')
N_.append('\n## Gaps and unverifiable items\n')
for t in [
    'Coinbase CBYF AUM not disclosed (blank). Maple BTC Yield history is an on-chain attribution (medium-high confidence).',
    'Kraken Bitcoin Vault, Bitget bgBTC Earn, ether.fi Liquid BTC: current values from parallel on-chain work; monthly histories pending (not in the history files yet).',
    'Core BTC staking: current value only (Core staking API, read 2026-09-21: 2,210.3 BTC, 1,814 stakers); no history endpoint found. Possible overlap with b14g and Maple.',
    'Stacks Dual Stacking: no public enrollment figure found; sBTC is excluded as a wrapper and Dual Stacking is not in the totals.',
    'Midas pools (mHyperBTC, mRe7BTC) and Tesseract pools: DefiLlama yields history starts mid-2026; earlier months are missing. Tesseract pools stopped updating 2026-09-16 (value carried to 09-20).',
    'Veda "other BTC vaults" (1,581 BTC today, up to ~10.8k BTC in 2025) are not identified by vault; placed in C6.',
    'Concrete: DefiLlama yields lists ~$38M of Berachain BTC vaults (APY 0) that are not in Concrete\'s protocol TVL; not counted.',
    'Babylon attribution is by finality-provider name; stake that LSTs delegate to generic operators without a product-linked key is not attributed (upper-bound case in overlap.md).',
    'Mechanisms not verified: Vishwa, ObeliskBTC, BitFi bfBTC, Solv RWA (constant $8.32M in DefiLlama), D2 Finance, DeSyn, CoinWind.',
    'Small protocols (< $0.25M BTC today and < $3M at every month-end) are not listed.',
]:
    N_.append(f'- {t}')
N_.append('\n## Re-run\n')
N_.append('```\ncd scratchpad/v3/marketmap\npython3 scripts/01_candidates.py            # candidate slugs from raw/protocols.json\n'
          'python3 scripts/02_fetch_protocols.py        # DefiLlama /protocol/{slug} (cached in raw/proto; delete to refresh)\n'
          'python3 scripts/02b_fetch_parallel.py raw/extra_small_slugs.json   # small/dead protocols for the history screen\n'
          'python3 scripts/03_fetch_btc_price.py        # Binance daily closes\n'
          'python3 scripts/04_fetch_babylon.py          # Babylon stats, FPs, active delegations\n'
          'python3 scripts/06_babylon_lst_fp_history.py # Babylon stake by product-branded FP, month-end (fallback)\n'
          'python3 scripts/06c_babylon_lst_staker_history.py  # Babylon stake by product-linked staker keys (phase 1 + 2)\n'
          'python3 scripts/07_fetch_yield_pools.py      # Midas / Tesseract / eBTC pools + charts\n'
          'python3 scripts/08_history_screen.py         # BTC part at every month-end for every fetched protocol\n'
          'python3 scripts/10_build.py                  # all CSVs\npython3 scripts/11_write_reports.py          # overlap.md, notes.md, jump_candidates.csv\n```')
N_.append('Product list and classification live in `scripts/products.py`; the BTC symbol list in `scripts/lib.py`.')
open(os.path.join(D, 'notes.md'), 'w').write('\n'.join(N_) + '\n')
print('ok', G, N, lo)
