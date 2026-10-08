"""Dolomite carry sweep at T (2026-10-02 23:59:59 UTC).

1. DolomiteMargin per chain (DefiLlama config): every market at T: token, symbol, total par x current index (supply, borrow),
   getMarketPrice (USD, 36 - decimals). ETH-family supply is the venue upper bound for ETH collateral.
2. Accounts: Dolomite subgraph (subgraph.api.dolomite.io, time travel at the T block) MarginAccount with hasBorrowValue = true.
3. On chain at T: getAccountBalances((owner, number)) for each account; ETH-family positive balances are ETH collateral
   (ETH-equivalent by Aave Core symbol ratio, else Dolomite oracle USD / 2,666.40); negative stablecoin balances are dollar debt,
   other negative balances other debt (Dolomite oracle USD). eth_backing_dollar = eth_collateral x dollar_debt / total_debt.
   eth_share_of_collateral_value flags accounts that also post large non-ETH collateral (the formula above gives all ETH to the dollar debt).
   A Dolomite position is (owner, accountNumber); the owner is the address that holds the position (EOA, contract or isolation-mode vault).
Usage: python3 dolomite_scan.py [chainId ...]
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from chains import *

MARGIN = {42161: '0x6bd780e7fdf01d77e4d475c821f1e7ae05409072', 1: '0x003Ca23Fd5F0ca87D01F6eC6CD14A8AE60c2b97D', 80094: '0x003Ca23Fd5F0ca87D01F6eC6CD14A8AE60c2b97D',
          5000: '0xE6Ef4f0B2455bAB92ce7cC78E35324ab58917De8', 196: '0x836b557Cf9eF29fcF49C776841191782df34e4e5', 1101: '0x836b557Cf9eF29fcF49C776841191782df34e4e5',
          3637: '0x003Ca23Fd5F0ca87D01F6eC6CD14A8AE60c2b97D'}
SGN = {42161: 'arbitrum', 1: 'ethereum', 80094: 'berachain-mainnet', 5000: 'mantle', 196: 'x-layer'}
SGU = 'https://subgraph.api.dolomite.io/api/public/1301d2d1-7a9d-4be4-9e9a-061cb8611549/subgraphs/dolomite-%s/latest/gn'


def sg(ch, q):
    body = json.dumps({'query': q}).encode()
    for i in range(8):
        j = getjson(SGU % SGN[ch], data=body, headers={'content-type': 'application/json'})
        if j.get('data') is not None: return j['data']
        time.sleep(3 * (i + 1))
    raise Exception('dolomite subgraph failed %s' % str(j)[:300])


def markets(ch, B):
    m = MARGIN[ch]
    n = U(call1(ch, m, S('getNumMarkets()'), B))
    ids = list(range(n))
    r = mcall(ch, [(m, S(x) + u32(i)) for i in ids for x in ('getMarketTokenAddress(uint256)', 'getMarketTotalPar(uint256)', 'getMarketCurrentIndex(uint256)', 'getMarketPrice(uint256)')], B)
    mk = {}
    for i in ids:
        t, tp, ci, px = r[4 * i:4 * i + 4]
        mk[i] = dict(token=A(t), par_borrow=U(tp, 0), par_supply=U(tp, 1), idx_borrow=U(ci, 0), idx_supply=U(ci, 1), price=U(px) if px else None)
    toks = sorted({x['token'] for x in mk.values() if x['token']})
    r = mcall(ch, [(t, S(x)) for t in toks for x in ('symbol()', 'decimals()')], B)
    tm = {t: (dec_str(r[2 * j]), U(r[2 * j + 1]) if r[2 * j + 1] else 18) for j, t in enumerate(toks)}
    for i, x in mk.items():
        x['sym'], x['dec'] = tm.get(x['token'], (None, 18))
        x['supply'] = x['par_supply'] * x['idx_supply'] / 1e18 / 10 ** x['dec']
        x['borrow'] = x['par_borrow'] * x['idx_borrow'] / 1e18 / 10 ** x['dec']
        x['usd_per_unit'] = (x['price'] * 10 ** x['dec'] / 1e36) if x['price'] else None
        x['is_eth'] = is_eth_sym(x['sym']); x['is_stable'] = is_stable_sym(x['sym'])
        r_ = eth_rate(x['sym'])
        x['eth_per_unit'] = r_ if r_ is not None else ((x['usd_per_unit'] / ETH_USD) if (x['is_eth'] and x['usd_per_unit']) else None)
    return mk


def dec_balances(h):
    """getAccountBalances -> (marketIds, tokens, par[(sign, value)], wei[(sign, value)])"""
    w = L.words(h); offs = [x // 32 for x in w[:4]]
    def arr(o, k):
        n = w[o]; return [w[o + 1 + k * i:o + 1 + k * (i + 1)] for i in range(n)]
    ids = [x[0] for x in arr(offs[0], 1)]
    wei = [(x[0], x[1]) for x in arr(offs[3], 2)]
    return ids, wei


def scan(ch):
    B = bT(ch)
    mk = markets(ch, B)
    eth_sup = sum(x['supply'] * (x['eth_per_unit'] or 0) for x in mk.values() if x['is_eth'])
    st_bor = sum(x['borrow'] for x in mk.values() if x['is_stable'])
    meta = dict(chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, margin=MARGIN[ch], markets=len(mk), eth_family_supply_eth=eth_sup, stable_borrow_units=st_bor,
                eth_markets=[dict(id=i, sym=x['sym'], supply=x['supply'], eth=x['supply'] * (x['eth_per_unit'] or 0)) for i, x in mk.items() if x['is_eth'] and x['supply'] > 0],
                stable_markets=[dict(id=i, sym=x['sym'], borrow=x['borrow']) for i, x in mk.items() if x['is_stable'] and x['borrow'] > 0])
    log('dolomite', ch, 'block', B, 'markets', len(mk), 'ETH-family supply %.0f ETH' % eth_sup, 'stable borrow $%.2fM' % (st_bor / 1e6))
    if ch not in SGN:
        meta['note'] = 'no subgraph; accounts not enumerated'; return meta, []
    # accounts with any borrow at T
    accts = []; last = ''
    while True:
        q = '{marginAccounts(first: 1000, orderBy: id, block: {number: %d}, where: {hasBorrowValue: true, id_gt: "%s"}) {id user {id} accountNumber borrowTokens {symbol} supplyTokens {symbol}}}' % (B, last)
        rows = sg(ch, q)['marginAccounts']
        accts += rows
        if len(rows) < 1000: break
        last = rows[-1]['id']
    cand = [a for a in accts if any(is_stable_sym(t['symbol']) for t in a['borrowTokens'])]
    log('  accounts with borrow', len(accts), 'with stable borrow', len(cand))
    m = MARGIN[ch]
    r = mcall(ch, [(m, S('getAccountBalances((address,uint256))') + a32(a['user']['id']) + u32(int(a['accountNumber']))) for a in cand], B, size=50)
    rows = []; dsum = 0.0; esum_all = 0.0
    for a, h in zip(cand, r):
        if not h: continue
        ids, wei = dec_balances(h)
        ec = 0.0; dd = 0.0; od = 0.0; oc = 0.0; coll = []; debts = []
        for i, (sign, v) in zip(ids, wei):
            if not v: continue
            x = mk[i]; units = v / 10 ** x['dec']
            if sign:  # positive
                if x['is_eth']:
                    e = units * (x['eth_per_unit'] or 0); ec += e
                    coll.append(dict(sym=x['sym'], market_id=i, units=units, eth_eq=e))
                else: oc += units * (x['usd_per_unit'] or 0)
            else:
                usd = units * (x['usd_per_unit'] or (1.0 if x['is_stable'] else 0))
                if x['is_stable']: dd += usd
                else: od += usd
                debts.append(dict(sym=x['sym'], market_id=i, units=units, usd=usd))
        if not dd: continue
        dsum += dd; esum_all += ec
        share = dd / (dd + od)
        rows.append(dict(venue='dolomite', chain=ch, chain_name=CHAIN_NAME.get(ch), block=B, market='DolomiteMargin %s' % MARGIN[ch], market_label='account #%s' % a['accountNumber'],
                         account=a['user']['id'].lower(), account_number=a['accountNumber'], owner=None, eth_collateral=ec, collateral=coll, other_collateral_usd=oc,
                         debts=debts, dollar_debt_usd=dd, other_debt_usd=od, eth_backing_dollar=ec * share,
                         eth_share_of_collateral_value=(ec * ETH_USD / (ec * ETH_USD + oc)) if ec * ETH_USD + oc else 0))
    st_usd = sum(x['borrow'] * (x['usd_per_unit'] or 1.0) for x in mk.values() if x['is_stable'])
    meta.update(stable_borrow_usd=st_usd, debt_read_usd=dsum, coverage=dsum / st_usd if st_usd else None, accounts_with_stable_debt=len(rows),
                eth_collateral_of_stable_borrowers=esum_all, eth_backing_dollar_total=sum(r['eth_backing_dollar'] for r in rows))
    log('  stable debt read $%.2fM of $%.2fM' % (dsum / 1e6, st_usd / 1e6), 'ETH coll of stable borrowers %.0f' % esum_all, 'backing %.0f' % meta['eth_backing_dollar_total'])
    return meta, rows


def main():
    only = [int(x) for x in sys.argv[1:]]
    parts = load('venues/dolomite_parts.json', {})
    for ch in MARGIN:
        if only and ch not in only: continue
        try:
            m, rows = scan(ch)
        except Exception as e:
            log('dolomite', ch, 'FAILED', e); m, rows = dict(chain=ch, error=str(e)), []
        parts[str(ch)] = dict(meta=m, rows=rows)
        save('venues/dolomite_parts.json', parts)
    allrows = [r for p in parts.values() for r in p['rows']]
    pos = sorted([r for r in allrows if r['eth_backing_dollar'] >= 100], key=lambda r: -r['eth_backing_dollar'])
    def ck(r):
        r['account_code'], r['account_delegate'] = code_kind(r['chain'], r['account'], r['block']); return r
    with ThreadPoolExecutor(8) as ex: pos = list(ex.map(ck, pos))
    meta = [p['meta'] for p in parts.values()]
    summary = dict(venue='dolomite', snapshot='2026-10-02 23:59:59 UTC', eth_usd=ETH_USD,
                   eth_collateral_of_stable_borrowers=sum(m.get('eth_collateral_of_stable_borrowers') or 0 for m in meta),
                   eth_backing_dollar_total=sum(m.get('eth_backing_dollar_total') or 0 for m in meta),
                   positions_ge100=len(pos), positions_ge100_eth=sum(r['eth_backing_dollar'] for r in pos), method=__doc__.strip())
    save('venues/dolomite.json', dict(meta=[summary] + meta, positions=pos))
    log('dolomite positions >= 100', len(pos), 'ETH %.0f' % summary['positions_ge100_eth'])


if __name__ == '__main__':
    main()
