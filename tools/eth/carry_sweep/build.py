"""Step 3: assemble the carry sweep. Every position where ETH-family collateral backs dollar debt (>= 100 ETH) from
  (a) data/eth/lending_split_accounts.csv, cells A2+B2 (Aave v3 Core/Prime/Spark/Base/Arbitrum, Morpho, Compound v3, Fluid, Aave v4), and
  (b) the venue sweeps in raw/eth/carry-sweep-2026-10-08/venues/ (Curve, Liquity family, Sky/Maker, Euler, Dolomite, Silo, Gearbox,
      other Aave deployments, Compound/Fluid L2, the 100 to 187 ETH band of the split venues, HyperEVM),
classified by owner type (classify.py, classify2.py, classify_venues.py, counterparties.py, registries.py, manual reads below).
Writes data/eth/carry_sweep.csv and prints the summary used in research/eth/en/CARRY-SWEEP.md."""
import collections, csv, glob, json, os
from common import ROOT, RAW, load

# ---------- products and other identified owners (manual, from the reads in this folder; evidence in the row) ----------
# klass: counted | product | private | leverage | personal | wallet
P = {}
def prod(chain, acct, product, klass, open_, holders, map_row, evidence):
    P['%d:%s' % (chain, acct.lower())] = dict(product=product, klass=klass, open=open_, holders=holders, map_row=map_row, evidence=evidence)

# counted carry products (data/eth/netmap/carry_lending_snapshot.json accounts, plus Liquity ETH Carry and Rocksolid)
snap = json.load(open(os.path.join(ROOT, 'data/eth/netmap/carry_lending_snapshot.json')))
for pid, accts in snap['accounts'].items():
    for a in accts:
        for ch in (1, 8453, 42161, 143):
            prod(ch, a, 'carry:' + pid, 'counted', 'yes', '', 'carry:' + pid, 'listed in carry_lending_snapshot.json')
prod(1, '0xb9e806e8f2d94c015ffefa90cd24ecce18f1663c', 'carry:liquity-carry (IPOR rETH Liquity LP Carry)', 'counted', 'yes', '', 'carry:liquity-carry', 'IPOR PlasmaVault; Ebisu/Liquity v2 wstETH trove owner')
prod(1, '0x41cfe42d221a591c6308dcea419015ba8570b380', 'Yearn yvWETH-2: Spark wstETH/USDS lender-borrower strategy', 'product', 'yes', 131, 'yearn-finance (lending)',
     'TokenizedStrategy "Spark wstETH/USDS (yvUSD) Lender Borrower"; asset wstETH; vault 0xac37729b (WETH-2 yVault, 131 holders)')
prod(1, '0xc868bfb240ed207449afe71d2ecc781d5e10c85c', 'Lagoon 9Summits Flagship ETH (9SETH)', 'product', 'yes', 121, 'lagoon (farming)',
     'vault 0x07ed467a safe() = this Safe at T; Safe 3-of-6 with Zodiac Roles; weETH on Spark against USDS')
prod(1, '0x24d2486f5b2c2c225b6be8b4f72d46349cbf4458', 'YieldNest ynETHx (Flex Strategy LVG1)', 'product', 'yes', 1102, 'yieldnest (restaking)',
     'Safe; 71 wstETH transfers with FlexStrategy proxy 0x115b5064 and 70 ynRWAx transfers with FlexStrategyLeverageKeeper; ynETHx 1,102 holders')
prod(1, '0xe39cd9b36b9a86a8227ec3f5159b610bf2a30e69', 'Lagoon DAMM Ethereum Fund (DAMMeth)', 'product', 'whitelist', 8, 'lagoon (farming)',
     'vault 0x3c63f3ce safe() = this Safe; 8 share holders')
prod(1, '0xee6b63e2ca34ce2be4cce15137ec59b9e5a733bb', 'Lagoon Mt Pelerin ETH strategy pool', 'product', 'yes', 3, 'lagoon (farming)',
     'vault 0xb118de49 safe() = this Safe; 3 share holders')
prod(1, '0xeb72e4df998c9435a4cb44020faf18e101648fc6', 'Upshift Treehouse Growth Vault v2 (gtETH)', 'product', 'yes', '', 'upshift (farming)',
     'Upshift API: subaccount of vault 0xd8091978; owner() = vault')
prod(1, '0x15d869a5a117480ff219d6dc62a42c794cbaccba', 'Upshift KPK LsETH', 'product', 'yes', '', 'upshift (farming)',
     'Upshift API: subaccount of vault 0x00e95754; owner() = vault')
prod(42161, '0xfb1898bb5955fdd11704e397104c6a0e0725eb17', 'Upshift NEMO USDC Prime (nUSDC) operator', 'product', 'yes', '', 'none (dollar vault; ETH sits in money markets)',
     'Upshift API: EOA operator of NEMO USDC Prime 0x955256b3; wstETH on Aave Arbitrum against USDC; also trades on Derive (ROCKSOLID-NEMO-SENTORA.md)')
for a, n, h in (('0x3a6be494884e4019a2a727dd217accf2320ca641', 'Digital Asset Vault', 8), ('0x934ae3e313e041059c84a1c705ec7e5df9d2e9ce', 'Bitcoin Dome', 6),
                ('0x7546cfc0d3d733271a7c585aef13b548ba8de01e', 'Digital Asset Vault V2', 4)):
    prod(1, a, 'Enzyme fund "%s" (Aave v3 debt external position)' % n, 'product', 'manager-gated', h, 'enzyme-finance (farming)',
         'ExternalPositionProxy type 13 (Aave v3 debt); getVaultProxy() = Enzyme vault; all three vaults owned by 0xa218a923; %d share holders' % h)
prod(1, '0x378d18ecd80430895df2c034327edac16b3f1372', 'IPOR TESS wstETH Debt Vault', 'product', 'closed', 4, 'fusion-by-ipor (farming)',
     'PlasmaVault; publicDepositOpened = false (CARRY-DISCOVERY.md); 4 holders')
# leverage tokens (dollar debt against ETH, but a leveraged long, not carry)
prod(1, '0x65c4c0517025ec0843c9146af266a2c5a2d148a2', 'Index Coop ETH2X', 'leverage', 'yes', 327, 'index-coop (counted 0)', 'SetToken; WETH collateral, USDC debt')
prod(42161, '0x26d7d3728c6bb762a5043a1d0cef660988bca43c', 'Index Coop ETH2x (Arbitrum)', 'leverage', 'yes', '', 'index-coop (counted 0)', 'SetToken "Index Coop Ethereum 2x Index"')
prod(42161, '0xf715724abba480d4d45f4cb52bef5ce5e3513ccc', 'Toros ETHBULL3X', 'leverage', 'yes', '', 'none', 'dHEDGE/Toros pool "Ethereum Bull 3X"')
# private mandates, treasuries and single-owner contracts
prod(1, '0x7ee29373f075ee1d83b1b93b4fe94ae242df5178', 'Concrete Delta weETH (one principal)', 'private', 'no', 1, 'excluded', 'gap scan: Safe holds 100% of shares')
for a, n in (('0xa122687285dc5012141055a801045f069112e7c6', 1), ('0x4f87de7d21aef48090958f7342e1f69dff790545', 2), ('0xa56da9bb528fedf8379b02e95fbbdad34d45846f', 3)):
    for ch in (1, 8453):
        prod(ch, a, 'rSHARE vault #%d manager (private)' % n, 'private', 'no', '', 'excluded', 'gap scan: manager of a private rSHARE WETH vault')
prod(1, '0xd164a2e919ba9e3e51efde85ceba29dc2aa21781', 'MakinaX managed account (one client Safe)', 'private', 'no', '', 'none',
     'Safe 1-of-2 with module 0x621a2f40 (MakinaXModule clone, registry 0x2967ef24 MakinaXRegistry, safe() = this Safe); no share token')
prod(8453, '0xd1895f2019c2152fc2b9022d57f19198c4cfcabc', 'Private Aave wrapper (owner Safe 0x6b27512a)', 'private', 'no', '', 'none',
     'unverified TUP; impl functions supply/borrow/repay/whitelist/minHealth; owner() = Safe; no share token; created 2025-02 by EOA 0x4ff634ef')
prod(10, '0xb32cb14f2a5b17d1f1343749e302316be5133321', 'Private Aave wrapper (owner EOA 0x2869b95d)', 'private', 'no', '', 'none',
     'same function set as the Base wrapper 0xd1895f20; owner() = EOA; no share token')
prod(1, '0x5be9a4959308a0d0c7bc0870e319314d8d957dbb', 'Dolomite Safe with WLFI/USD1 book (treasury)', 'private', 'no', '', 'none',
     'Safe 3-of-5; WETH and mETH beside USD1, USDC and 1.99B WLFI collateral; USD1/USDC debt; ETH is 3.5 to 18.5% of collateral value')
prod(1, '0x7b852ebc448b3638f971bac2c463db6578634f11', 'Safe 1-of-1 (Aave, Compound, Liquity v2 troves)', 'wallet', 'no', '', 'none',
     'Safe 1-of-1 of 0xe5ebcde1; no vault counterparty')

PERSONAL_IMPL = {'0xd80a503a2c2a5dddd8be53fb75bd48f0bb465ed4': 'Summer.fi DPM', '0xfe02a32cbe0cb9ad9a945576a5bb53a3c123a3a3': 'Instadapp DSA',
                 '0x857f3b524317c0c403ec40e01837f1b160f9e7ab': 'Instadapp DSA', '0xbfb0b82dda093c84b00b3c3c053c5e5b2e42550f': 'Summer.fi DPM',
                 '0x0dabcba4376f167db717d7f56adca62e950f0221': 'Summer.fi DPM'}
CBSW = {'0x00000110dcdedc9581cb5ecb8467282f2926534d', '0x000100abaad02f1cfc8bbe32bd5a564817339e72'}
PERSONAL_ACCT = {'1:0x7b930deddee8f5fd80a99f734bf9fe0d9eb215b9': 'Argent wallet', '1:0x62ac25f1883ea454febcfcb2015293c4ea407f06': 'single-user flash-loan leverage contract',
                 '42161:0xe1e8914d69f7d4f93ce510e910939aa643f2b191': 'single-owner wstETH/USDC leverage bot', '1:0xd1a2d9df5db842da2ee81075fa441602b2352915': None}


def kind_of(key, v, c2):
    if v['kind0'] in ('EOA', 'EIP-7702'): return v['kind0']
    pr = v.get('probe', {}); bs = v.get('bs') or {}
    nm = ' '.join([bs.get('name') or ''] + [x or '' for x in bs.get('impl') or []])
    if 'getOwners' in pr:
        s = c2.get(key, {})
        return 'Safe %s-of-%s' % (s.get('threshold', '?'), len(s.get('owners', []))) if s else 'Safe'
    if 'cache' in pr and 'authority' in pr: return 'DSProxy'
    if v.get('eip1167') in PERSONAL_IMPL: return PERSONAL_IMPL[v['eip1167']]
    if 'AccountImplementation' in nm: return 'Summer.fi DPM'
    if 'InstaAccount' in nm or (v.get('codelen') == 45 and set(pr) == {'version'}): return 'Instadapp DSA'
    if v.get('impl1967') in CBSW or 'CoinbaseSmartWallet' in nm: return 'Coinbase Smart Wallet'
    for w in ('Ambire', 'Avocado', 'Kernel', 'UserWallet'):
        if w in nm: return w
    if v.get('codelen') == 45 and 'AmbireAccount' in nm: return 'Ambire'
    return 'contract: ' + (bs.get('name') or (bs.get('impl') or [None])[0] or 'unnamed')


SMART = ('DSProxy', 'Summer.fi DPM', 'Instadapp DSA', 'Coinbase Smart Wallet', 'Ambire', 'Avocado', 'Kernel', 'UserWallet')


def main():
    r1 = load('classify_raw.json'); rv = load('classify_venues.json', {}); c2 = load('classify2.json'); reg = load('registries.json')
    ok = load('owner_kinds.json', {})
    allr = {**rv, **r1}
    gap = {r['address'].lower(): r for r in csv.DictReader(open(os.path.join(ROOT, 'data/eth/gap_borrower_scan.csv')))}
    split_rows = list(csv.DictReader(open(os.path.join(ROOT, 'data/eth/lending_split_accounts.csv'))))
    pos = []
    for r in split_rows:
        if r['side'] != 'eth': continue
        e = float(r['A2'] or 0) + float(r['B2'] or 0)
        if e < 100: continue
        pos.append(dict(source='lending split', venue=r['venue'], chain=int(r['chain']), account=r['account'].split('@')[0].lower(), sub=r['account'],
                        eth=e, debt=float(r['stable_debt_attr_usd'] or 0), gap_who=r['gap_scan_who'], gap_cat=r['gap_scan_category']))
    seen = {(p['venue'], p['chain'], p['account']) for p in pos}
    for f in sorted(glob.glob(os.path.join(RAW, 'venues', '*.json'))):
        b = os.path.basename(f)
        if b.startswith('blocks') or b.endswith('_rows.json') or b.endswith('_parts.json') or 'summary' in b: continue
        for p in json.load(open(f)).get('positions', []):
            e = p.get('eth_backing_dollar') or 0
            if e < 100: continue
            a = p['account'].split('@')[0].lower(); ch = int(p['chain'])
            venue = p.get('venue') or b.split('.')[0]
            if (venue, ch, a) in seen and b == 'lowband_existing.json': continue
            mk = p.get('market') or p.get('market_label') or p.get('controller') or ''
            pos.append(dict(source='venue sweep: ' + b.replace('.json', ''), venue=venue + (' ' + str(mk) if mk and not str(mk).startswith('0x') else ''),
                            chain=ch, account=a, sub=p['account'], eth=e, debt=p.get('dollar_debt_usd') or 0, gap_who='', gap_cat=''))
    rows = []
    for p in pos:
        key = '%d:%s' % (p['chain'], p['account'])
        v = allr.get(key, {'kind0': '?'})
        kind = kind_of(key, v, c2) if v.get('kind0') != '?' else 'unknown'
        g = gap.get(p['account'], {})
        info = P.get(key)
        hits = reg.get(p['account'], [])
        if not info and key in PERSONAL_ACCT:
            info = dict(product=PERSONAL_ACCT[key] or '', klass='personal', open='no', holders='', map_row='', evidence='code read (dig.py)')
            if key == '1:0xd1a2d9df5db842da2ee81075fa441602b2352915':
                info = dict(product='carry:makina-deth (Caliber)', klass='counted', open='yes', holders='', map_row='carry:makina-deth', evidence='Makina Caliber; carry_lending_snapshot')
        if not info and hits:
            h = hits[0]
            info = dict(product=h['product'], klass='product', open='?', holders='', map_row='', evidence='registry match: %s %s' % (h['source'], h['vault']))
        if not info:
            if any(kind.startswith(s) for s in SMART):
                own = ok.get(key, {})
                info = dict(product='', klass='personal', open='no', holders='', map_row='',
                            evidence='per-user smart account' + (' (owner is a contract %s)' % own['owner'][:10] if own.get('kind') == 'contract' else ''))
            elif kind.startswith('Safe') or kind in ('EOA', 'EIP-7702'):
                lab = ((c2.get(key) or {}).get('es') or {}).get('title', '')
                lab = lab.split(' | ')[0] if lab and not lab.startswith('Address') else ''
                ev = '; '.join(x for x in (g.get('who') or p['gap_who'], lab) if x)
                info = dict(product='', klass='wallet', open='no', holders='', map_row='', evidence=ev or 'no label; no vault counterparty in latest ERC-20 transfers (Ethereum) or registry match')
            else:
                info = dict(product='', klass='unknown contract', open='?', holders='', map_row='', evidence=kind)
        counted = 'yes' if info['klass'] == 'counted' else ('excluded (private)' if info['klass'] == 'private' and 'excluded' in info['map_row'] else 'no')
        rows.append(dict(source=p['source'], venue=p['venue'], chain=p['chain'], account=p['sub'], owner_kind=kind, owner_class=info['klass'],
                         product=info['product'], open_to_depositors=info['open'], share_holders=info['holders'], eth_backing_dollar_debt=round(p['eth'], 2),
                         dollar_debt_usd=round(p['debt']), atlas_counts_as_carry=counted, atlas_row_now=info['map_row'],
                         gap_scan_category=g.get('category') or p['gap_cat'], evidence=info['evidence']))
    rows.sort(key=lambda r: -r['eth_backing_dollar_debt'])
    out = os.path.join(ROOT, 'data/eth/carry_sweep.csv')
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print('rows', len(rows), '->', out)
    # ---------- summary ----------
    for src in ('lending split', 'venue sweep'):
        rs = [r for r in rows if r['source'].startswith(src)]
        tot = sum(r['eth_backing_dollar_debt'] for r in rs)
        print('\n==', src, 'positions', len(rs), 'ETH %.0f' % tot)
        by = collections.Counter(); n = collections.Counter()
        for r in rs:
            k = r['owner_class']
            if k == 'wallet': k = 'wallet: ' + ('Safe' if r['owner_kind'].startswith('Safe') else r['owner_kind'])
            by[k] += r['eth_backing_dollar_debt']; n[k] += 1
        for k, x in by.most_common(): print('  %-28s %4d %10.0f ETH %5.1f%%' % (k, n[k], x, 100 * x / tot))
    print('\n== products and other identified owners')
    agg = collections.defaultdict(lambda: [0, 0, set(), None])
    for r in rows:
        if r['owner_class'] in ('product', 'counted', 'private', 'leverage'):
            a = agg[(r['owner_class'], r['product'])]; a[0] += r['eth_backing_dollar_debt']; a[1] += r['dollar_debt_usd']; a[2].add(r['venue'] + '@' + str(r['chain'])); a[3] = r
    for (k, pname), (e, d, vs, r) in sorted(agg.items(), key=lambda x: (x[0][0], -x[1][0])):
        print('  %-9s %-62s %9.0f ETH $%6.2fM  holders=%s open=%s row=%s  %s' % (k, pname[:62], e, d / 1e6, r['share_holders'], r['open_to_depositors'], r['atlas_row_now'], sorted(vs)))


if __name__ == '__main__':
    main()
