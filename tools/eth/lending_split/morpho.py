"""Morpho Blue, every chain in the Morpho API: markets whose collateral is the side's family (pair split exact per market), and markets whose
loan asset is the side's family (lender supply and the part lent out).

Usage: python3 morpho.py <eth|btc> <chainId> [...]
Per collateral market: every position with collateral now (API, all pages) plus every user who withdrew collateral or was liquidated after
the snapshot (API transactions), read on chain at the snapshot block: position(id,user) -> collateral and borrow shares; market() -> totals.
Collateral valued in native units (ETH or BTC) at the token's rate: API priceUsd(token) / priceUsd(WETH or WBTC), read on the scan day.
"""
import sys
from lib import *

BLUE = {it['chain']['id']: it['address'] for it in gql('{ morphoBlues{ items{ address chain{id} } } }')['data']['morphoBlues']['items']}


def markets(ch):
    out = []; skip = 0
    while True:
        q = '''{ markets(first:500, skip:%d, where:{chainId_in:[%d]}){ items{ marketId lltv oracle{address} collateralAsset{address symbol decimals priceUsd}
               loanAsset{address symbol decimals priceUsd} state{ collateralAssets collateralAssetsUsd supplyAssetsUsd borrowAssetsUsd } } pageInfo{countTotal} } }''' % (skip, ch)
        j = gql(q)
        if not j.get('data'): log('gql err', str(j)[:200]); break
        out += j['data']['markets']['items']; skip += 500
        if skip >= j['data']['markets']['pageInfo']['countTotal']: break
    return out


def positions(ch, mid, ts):
    users = set(); skip = 0
    while True:
        q = '''{ marketPositions(first:1000, skip:%d, orderBy:Collateral, orderDirection:Desc, where:{marketUniqueKey_in:["%s"], chainId_in:[%d], collateral_gte:"1"}){ items{ user{address} } pageInfo{countTotal} } }''' % (skip, mid, ch)
        j = gql(q)
        if not j.get('data'): log('pos err', str(j)[:200]); break
        its = j['data']['marketPositions']['items']; users |= {i['user']['address'].lower() for i in its}; skip += 1000
        if skip >= j['data']['marketPositions']['pageInfo']['countTotal'] or not its: break
    ex = set(); skip = 0
    while True:
        q = '''{ marketTransactions(first:1000, skip:%d, where:{marketUniqueKey_in:["%s"], chainId_in:[%d], timestamp_gte:%d, type_in:[WithdrawCollateral, Liquidation]}){ items{ user{address} } pageInfo{countTotal} } }''' % (skip, mid, ch, ts + 1)
        j = gql(q)
        if not j.get('data'): log('tx err', str(j)[:200]); break
        its = j['data']['marketTransactions']['items']; ex |= {i['user']['address'].lower() for i in its}; skip += 1000
        if skip >= j['data']['marketTransactions']['pageInfo']['countTotal'] or not its: break
    return users, ex


def scan(side, ch):
    B = block_at(ch, side); blue = BLUE[ch]; ts = SNAP[side]['ts']
    ms = markets(ch)
    def f(sym): return fam(sym, side)
    refsym = ('WETH',) if side == 'eth' else ('WBTC', 'CBBTC', 'BTCB')
    pr = {}
    for m in ms:
        for a in (m['collateralAsset'], m['loanAsset']):
            if a and a.get('priceUsd'): pr[a['symbol'].upper()] = float(a['priceUsd'])
    ref_now = next((pr[s] for s in refsym if s in pr), None)
    if ref_now is None:
        ref_now = float(getjson('https://coins.llama.fi/prices/current/coingecko:%s' % ('ethereum' if side == 'eth' else 'bitcoin'))['coins']['coingecko:%s' % ('ethereum' if side == 'eth' else 'bitcoin')]['price'])
    coll_ms = [m for m in ms if m['collateralAsset'] and m['loanAsset'] and f(m['collateralAsset']['symbol']) == 'own']
    loan_ms = [m for m in ms if m['collateralAsset'] is not None and m['loanAsset'] and f(m['loanAsset']['symbol']) == 'own'] + \
              [m for m in ms if m['collateralAsset'] is None and m['loanAsset'] and f(m['loanAsset']['symbol']) == 'own']
    allm = {m['marketId']: m for m in coll_ms + loan_ms}
    ids = list(allm)
    mt = mcall(ch, [(blue, '0x5c60e39a' + i[2:]) for i in ids], B)
    tot = {}
    for i, x in zip(ids, mt):
        w = words(x) if x else [0] * 6
        tot[i] = dict(tsa=w[0], tss=w[1], tba=w[2], tbs=w[3])
    loans = []
    for m in loan_ms:
        t = tot[m['marketId']]; d = m['loanAsset']['decimals']; s = m['loanAsset']['symbol']
        rate = (float(m['loanAsset']['priceUsd'] or 0) / ref_now) if m['loanAsset'].get('priceUsd') else 1.0
        if t['tsa'] == 0: continue
        loans.append(dict(market=m['marketId'], loan_sym=s, coll_sym=(m['collateralAsset'] or {}).get('symbol'), form=form(s, side), rate=rate,
                          supply=t['tsa'] / 10**d, borrow=t['tba'] / 10**d, supply_native=t['tsa'] / 10**d * rate, borrow_native=t['tba'] / 10**d * rate))
    rows = []; mk = []
    for m in coll_ms:
        cs = m['collateralAsset']['symbol']; cd = m['collateralAsset']['decimals']; ls = m['loanAsset']['symbol']; ld = m['loanAsset']['decimals']
        if float(m['state']['collateralAssetsUsd'] or 0) < 1000 and tot[m['marketId']]['tba'] == 0: continue
        rate = float(m['collateralAsset']['priceUsd'] or 0) / ref_now if m['collateralAsset'].get('priceUsd') else 1.0
        lp = float(m['loanAsset']['priceUsd'] or 0)
        users, ex = positions(ch, m['marketId'], ts)
        us = sorted(users | ex)
        ps = mcall(ch, [(blue, '0x93c52062' + m['marketId'][2:] + a32(u)) for u in us], B)
        t = tot[m['marketId']]; n = 0; csum = 0; dsum = 0
        for u, x in zip(us, ps):
            if not x: continue
            w = words(x)
            coll = w[2]; bsh = w[1]
            if coll == 0: continue
            debt = (bsh * t['tba'] // t['tbs']) if t['tbs'] else 0
            cu = coll / 10**cd; du = debt / 10**ld
            rows.append(dict(user=u, market=m['marketId'], coll_sym=cs, loan_sym=ls, loan_fam=f(ls), form=form(cs, side), coll_units=cu, coll_native=cu * rate,
                             debt_units=du, debt_usd=du * lp, debt_native=(du * lp / ref_now)))
            n += 1; csum += cu; dsum += du
        mk.append(dict(market=m['marketId'], pair=cs + '/' + ls, lltv=int(m['lltv']) / 1e18, rate=rate, loan_price_now=lp, positions_now=len(users), reducers_after=len(ex),
                       positions_at_snapshot=n, collateral_units=csum, collateral_native=csum * rate, debt_read_units=dsum, total_borrow_units=t['tba'] / 10**ld,
                       api_collateral_now=int(m['state']['collateralAssets'] or 0) / 10**cd))
        log(ch, cs, '/', ls, m['marketId'][:10], 'positions', n, 'coll %.1f native %.1f' % (csum, csum * rate), 'debt read %.4g of %.4g' % (dsum, t['tba'] / 10**ld))
    save('morpho_%s_%d.json' % (side, ch), dict(side=side, chain=ch, block=B, blue=blue, ref_price_now=ref_now, markets=mk, loan_markets=loans, rows=rows))
    log('== chain', ch, 'coll markets', len(mk), 'native %.0f' % sum(x['collateral_native'] for x in mk), 'loan supply native %.0f borrow %.0f' % (
        sum(l['supply_native'] for l in loans), sum(l['borrow_native'] for l in loans)))


if __name__ == '__main__':
    side = sys.argv[1]
    for c in sys.argv[2:]:
        try: scan(side, int(c))
        except Exception as e: log('chain', c, 'failed', str(e)[:300])
