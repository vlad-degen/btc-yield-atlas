"""Sky/Maker vaults with ETH-family collateral (ETH-A/B/C, WSTETH-A/B, RETH-A) at T.
Urns from the DssCdpManager (cdpi, urns, ilks, owns) plus every urn that ever called Vat.frob for these ilks (anonymous LogNote,
topic1 = ilk, topic2 = urn), so vaults opened outside the CDP manager are covered too. ink/art from Vat.urns at T; debt = art x rate.
ETH value: WETH 1, wstETH and rETH at the Aave v3 Core oracle ratio to WETH at T. Owner: CDP manager owns(cdp) when the urn is a CDP
manager urn, otherwise the urn address itself. Output venues/maker.json."""
from vcommon import *  # noqa
from liquity_scan import eth_rates

VAT = '0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B'
MGR = '0x5ef30b9986345249bc32d8928B7ee64DE9435E39'
JOINS = {'ETH-A': '0x2F0b23f53734252Bda2277357e97e1517d6B042A', 'ETH-B': '0x08638eF1A205bE6762A8b935F5da9b700Cf7322c',
         'ETH-C': '0xF04a5cC80B1E94C69B48f5ee68a08CD2F09A7c3E', 'WSTETH-A': '0x10CD5fbe1b404B7E19Ef964B63939907bdaf42E2',
         'WSTETH-B': '0x248cCBf4864221fC0E840F29BB042ad5bFC89B5c', 'RETH-A': '0xC6424e862f1462281B0a5FAc078e4b63006bDEBF'}
VAT_DEPLOY = 8928152
MIN = 100.0

def bs_logs(address, t0, t1, fb, tb):
    """Blockscout etherscan-style getLogs (1,000 per page); pages forward from the last block seen."""
    out = {}; b = fb
    while True:
        url = ('https://eth.blockscout.com/api?module=logs&action=getLogs&address=%s&fromBlock=%d&toBlock=%d&topic0=%s&topic1=%s&topic0_1_opr=and'
               % (address, b, tb, t0, t1))
        j = getjson(url)
        res = j.get('result') or []
        if not isinstance(res, list): raise Exception(str(j)[:200])
        for lg in res: out[(lg['transactionHash'], lg['logIndex'])] = lg
        if len(res) < 1000: break
        nb = int(res[-1]['blockNumber'], 16)
        if nb == b: raise Exception('more than 1000 logs in one block')
        b = nb
    return list(out.values())

def b32(s): return '0x' + s.encode().hex().ljust(64, '0')

def main():
    b = vblk(1)
    rates, wpx = eth_rates()
    rate_of = {'ETH': 1.0, 'WSTETH': rates['WSTETH'], 'RETH': rates['RETH']}
    ilks = {k: b32(k) for k in JOINS}
    # CDP manager urns
    n = U(call1(1, MGR, sel('cdpi()'), b)); log('cdpi', n)
    ids = list(range(1, n + 1))
    il = mcall(1, [(MGR, cd('ilks(uint256)', i)) for i in ids], b, size=500)
    want = {v.lower(): k for k, v in ilks.items()}
    sel_ids = [i for i, x in zip(ids, il) if x and x.lower() in want]
    ur = mcall(1, [(MGR, cd('urns(uint256)', i)) for i in sel_ids], b, size=500)
    ow = mcall(1, [(MGR, cd('owns(uint256)', i)) for i in sel_ids], b, size=500)
    urns = {}
    for i, x, u, o in zip(sel_ids, [il[i - 1] for i in sel_ids], ur, ow):
        urns[(want[x.lower()], A(u))] = dict(cdp=i, owner=A(o))
    log('cdp manager urns', len(urns))
    # urns from Vat.frob LogNote
    frob = '0x' + sel('frob(bytes32,address,address,address,int256,int256)')[2:].ljust(64, '0')
    for k, ilk in (ilks.items() if not os.environ.get('NOLOGS') else []):
        try:
            logs = bs_logs(VAT, frob, ilk, VAT_DEPLOY, b)
        except Exception as e:
            log('logs fail', k, e); continue
        for lg in logs:
            u = '0x' + lg['topics'][2][-40:]
            urns.setdefault((k, u), dict(cdp=None, owner=None))
        log(k, 'frob logs', len(logs))
    keys = sorted(urns)
    st = mcall(1, [(VAT, cd('urns(bytes32,address)', ilks[k], u)) for k, u in keys], b, size=500)
    ir = {k: words(call1(1, VAT, cd('ilks(bytes32)', ilks[k]), b)) for k in ilks}
    jr = {}
    for k, j in JOINS.items():
        r = mcall(1, [(j, sel('ilk()')), (j, sel('gem()'))], b)
        gem = A(r[1])
        jr[k] = dict(join=j, ilk_ok=(r[0] or '').lower() == ilks[k].lower(), gem=gem,
                     gem_in_join=U(call1(1, gem, cd('balanceOf(address)', j), b)) / 1e18)
    pos = []; agg = {k: dict(ink=0.0, art=0.0, n=0) for k in ilks}
    for (k, u), s in zip(keys, st):
        w = words(s) if s else [0, 0]
        ink = w[0] / 1e18; art = w[1]
        rate = ir[k][1]; debt = art * rate / 1e45
        agg[k]['ink'] += ink; agg[k]['art'] += art / 1e18; agg[k]['n'] += 1 if w[0] else 0
        sym = k.split('-')[0]
        eth = ink * rate_of[sym]
        if eth < MIN: continue
        info = urns[(k, u)]
        pos.append(dict(venue='Sky/Maker', chain=1, block=b, market=k, urn=u, cdp=info['cdp'], account=info['owner'] or u,
                        owner_source='CDP manager owns(cdp)' if info['cdp'] else 'urn address (not a CDP manager urn)',
                        collateral_symbol={'ETH': 'WETH', 'WSTETH': 'wstETH', 'RETH': 'rETH'}[sym], collateral_units=ink, eth_collateral=eth,
                        dollar_debt_usd=debt, eth_backing_dollar=eth if debt > 0 else 0.0, manager=None))
    ks = kinds(1, [p['account'] for p in pos] + [p['urn'] for p in pos], b)
    for p in pos:
        p['kind'] = ks[p['account'].lower()]; p['urn_kind'] = ks[p['urn'].lower()]
    pos.sort(key=lambda p: -p['eth_collateral'])
    meta = []
    for k in ilks:
        sym = k.split('-')[0]; Art = ir[k][0] / 1e18; rate = ir[k][1] / 1e27
        tot_ink_join = jr[k]['gem_in_join']
        meta.append(dict(venue='Sky/Maker', chain=1, block=b, ilk=k, eth_per_unit=rate_of[sym], join=jr[k],
                         total_collateral_units_in_join=tot_ink_join, total_collateral_eth=tot_ink_join * rate_of[sym],
                         total_debt_usd=Art * rate, rate=rate, urns_scanned=sum(1 for x in keys if x[0] == k), urns_with_ink=agg[k]['n'],
                         enumerated_collateral=agg[k]['ink'], enumerated_debt=agg[k]['art'] * rate,
                         coverage_collateral=agg[k]['ink'] / tot_ink_join if tot_ink_join else None,
                         coverage_debt=agg[k]['art'] / Art if Art else None))
        log(k, 'join %.1f' % tot_ink_join, 'cov %.4f' % (meta[-1]['coverage_collateral'] or 0), 'debt %.0f' % (Art * rate))
    summary = dict(eth_rates=rate_of, total_collateral_eth=sum(m['total_collateral_eth'] for m in meta),
                   total_debt_usd=sum(m['total_debt_usd'] for m in meta), positions_ge_100=len(pos),
                   eth_in_positions_ge_100=sum(p['eth_collateral'] for p in pos),
                   eth_in_positions_ge_100_with_debt=sum(p['eth_collateral'] for p in pos if p['dollar_debt_usd'] > 0),
                   debt_in_positions_ge_100=sum(p['dollar_debt_usd'] for p in pos),
                   note='positions with zero debt are kept (eth_backing_dollar = 0) so idle collateral is visible')
    vsave('maker.json', {'summary': summary, 'meta': meta, 'positions': pos})
    log(json.dumps(summary, indent=1))

if __name__ == '__main__':
    main()
