"""HyperEVM (chain 999) ETH-family collateral backing dollar debt at the snapshot (block 47,507,894).

Note: https://rpc.hyperliquid.xyz/evm answers eth_call with the latest state whatever block tag is passed, so the lending-split capture
raw/eth/lending-split-2026-10-08/morpho_eth_999.json (read through it) holds scan-day state, not snapshot state. Here every read goes
through archive endpoints (stakely, rpc.hyperlend.finance) at the snapshot block.

1. HyperLend (Aave v3 fork, pool 0x00A8...1A8b): every account that ever received the UETH aToken (Transfer logs, aToken deployment ->
   snapshot), read at the snapshot as in aave_other.py. HypurrFi pooled market: UETH supply 67 at the snapshot, no position can reach 100.
2. Morpho Blue on HyperEVM (0x68e3...57cD; Felix vanilla markets UETH/USDT0, UETH/USDhl and the rest): every ETH-family collateral market,
   users from the Morpho API (positions now plus collateral withdrawals / liquidations after the snapshot), read at the snapshot.
3. Felix CDP (feUSD, Liquity v2 fork): branches are WHYPE, UBTC, kHYPE, wstHYPE (usefelix docs); no ETH branch.

Output: raw/eth/carry-sweep-2026-10-08/venues/hyperevm.json
"""
import json, os, random, time
from concurrent.futures import ThreadPoolExecutor
import sweep_lib as S
import lib as L
from lib import mcall, rpc, a32, words, fam, form, log, is_stable, getjson
import aave_other as X

CH = 999
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
LOG_EPS = ['https://hyperliquid-json-rpc.stakely.io', 'https://rpc.hyperliquid.xyz/evm', 'https://rpc.hyperlend.finance']
CACHE = os.path.join(S.VOUT, 'hyperevm_ueth_atoken_recipients.json')


def logs1000(addr, topics, fb, tb, workers=24):
    rngs = [(b, min(tb, b + 999)) for b in range(fb, tb + 1, 1000)]
    def one(ix):
        lo, hi = rngs[ix]
        for i in range(30):
            u = LOG_EPS[(ix + i) % len(LOG_EPS)]
            try:
                r = L.post_raw(u, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{'address': addr, 'fromBlock': hex(lo), 'toBlock': hex(hi), 'topics': topics}]}, timeout=40)
                if 'error' in r: raise Exception(str(r['error'])[:100])
                return r['result']
            except Exception:
                time.sleep(0.5 + random.random() * (1 + i))
        raise Exception('logs failed %d-%d' % (lo, hi))
    out = []; t0 = time.time()
    with ThreadPoolExecutor(workers) as ex:
        for k, r in enumerate(ex.map(one, range(len(rngs)))):
            out += r
            if k % 5000 == 0: log('   logs window', k, 'of', len(rngs), 'logs', len(out), '%.0fs' % (time.time() - t0))
    return out


def deploy_block(addr, B):
    lo, hi = 0, B
    while hi - lo > 1:
        m = (lo + hi) // 2
        for i in range(10):
            try:
                c = L.post_raw('https://rpc.hyperlend.finance', {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getCode', 'params': [addr, hex(m)]})['result']; break
            except Exception: time.sleep(2 + i)
        if c and c != '0x': hi = m
        else: lo = m
    return hi


def hyperlend(B):
    ch, pool = X.POOLS['hyperlend']
    res, orc, unit = X.reserves_at(ch, pool, B)
    ref = S.ref_price(res)
    own = [r for r in res if r['fam'] == 'own' and r['supply'] > 0]
    stab = [r for r in res if r['fam'] == 'stable' and r['debt'] > 0]
    meta = dict(venue='hyperlend', chain=ch, pool=pool, block=B, ref_eth_price=ref, eth_family_reserves={r['sym']: round(r['supply'], 4) for r in own},
                eth_family_supply_native=round(sum(r['supply'] * r['price'] / ref for r in own), 3), stable_debt_usd=round(sum(r['debt_usd'] for r in stab)))
    users = set(); notes = []
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    for r in own:
        if r['aToken'] in cache:
            users |= set(cache[r['aToken']]['recipients']); continue
        start = deploy_block(r['aToken'], B)
        log('  hyperlend', r['sym'], 'aToken', r['aToken'], 'deployed', start)
        lg = logs1000(r['aToken'], [TRANSFER], start, B)
        rec = sorted({'0x' + l['topics'][2][-40:] for l in lg if len(l['topics']) > 2})
        cache[r['aToken']] = dict(sym=r['sym'], from_block=start, to_block=B, logs=len(lg), recipients=rec)
        json.dump(cache, open(CACHE, 'w'))
        users |= set(rec); notes.append('%s aToken Transfer logs %d -> %d: %d logs' % (r['sym'], start, B, len(lg)))
    users.discard('0x' + '0' * 40)
    rows, ref = X.read_accounts(ch, pool, B, res, unit, sorted(users))
    back_all = 0.0
    for r in rows:
        D = sum(d['usd'] for d in r['debts'].values()); st = sum(d['usd'] for d in r['debts'].values() if d['fam'] == 'stable')
        if D > 0: back_all += sum(c['native'] for c in r['colls'].values() if c['enabled']) * st / D
    read = sum(c['native'] for r in rows for c in r['colls'].values())
    pos = S.aave_rows_positions('hyperlend', ch, B, rows, ref, 100)
    meta.update(enumeration='; '.join(notes) or 'cached recipients', candidates=len(users), accounts_holding=len(rows),
                coverage_eth_family_supply=round(read / meta['eth_family_supply_native'], 4) if meta['eth_family_supply_native'] else None,
                eth_backing_dollar_total=round(back_all, 2), positions_ge100=len(pos), positions_ge100_eth=round(sum(p['eth_backing_dollar'] for p in pos), 2))
    json.dump(dict(meta=meta, reserves=res, rows=rows), open(os.path.join(S.VOUT, 'hyperevm_hyperlend_rows.json'), 'w'), indent=1, default=str)
    log('  hyperlend', meta)
    return meta, pos


def morpho(B):
    import morpho as M  # tools/eth/lending_split/morpho.py: Morpho API helpers (markets, positions)
    blue = M.BLUE[CH]
    ms = M.markets(CH)
    pr = {}
    for m in ms:
        for a in (m['collateralAsset'], m['loanAsset']):
            if a and a.get('priceUsd'): pr[a['symbol'].upper()] = float(a['priceUsd'])
    ref = pr.get('WETH') or pr.get('UETH') or S.ETH_PX
    cms = [m for m in ms if m['collateralAsset'] and m['loanAsset'] and fam(m['collateralAsset']['symbol'], 'eth') == 'own']
    ids = [m['marketId'] for m in cms]
    mt = mcall(CH, [(blue, '0x5c60e39a' + i[2:]) for i in ids], B)
    peruser = {}; mk = []
    for m, x in zip(cms, mt):
        w = words(x) if x else [0] * 6; tba, tbs = w[2], w[3]
        cs = m['collateralAsset']['symbol']; cd = m['collateralAsset']['decimals']; ls = m['loanAsset']['symbol']; ld = m['loanAsset']['decimals']
        rate = float(m['collateralAsset']['priceUsd'] or 0) / ref if m['collateralAsset'].get('priceUsd') else 1.0
        lp = float(m['loanAsset']['priceUsd'] or 0)
        users, ex = M.positions(CH, m['marketId'], S.SNAP_TS)
        us = sorted(users | ex)
        ps = mcall(CH, [(blue, '0x93c52062' + m['marketId'][2:] + a32(u)) for u in us], B) if us else []
        csum = dsum = 0.0; st = is_stable(ls); back = 0.0
        for u, y in zip(us, ps):
            if not y: continue
            ww = words(y); coll = ww[2]; bsh = ww[1]
            if coll == 0: continue
            debt = (bsh * tba // tbs) if tbs else 0
            cu = coll / 10**cd; du = debt / 10**ld; nat = cu * rate
            csum += cu; dsum += du
            d = peruser.setdefault(u, dict(coll=0.0, syms=set(), st=0.0, oth=0.0, back=0.0, markets=[]))
            d['coll'] += nat; d['syms'].add(cs); d['markets'].append('%s/%s' % (cs, ls))
            if du > 0:
                if st: d['st'] += du * lp; d['back'] += nat; back += nat
                else: d['oth'] += du * lp
        mk.append(dict(market=m['marketId'], pair='%s/%s' % (cs, ls), rate=rate, users=len(us), collateral_units_at_snapshot=round(csum, 4),
                       collateral_native=round(csum * rate, 3), debt_units=round(dsum, 2), total_borrow_units=round(tba / 10**ld, 2), eth_backing_dollar=round(back, 3)))
        log('  morpho999', cs, '/', ls, 'users', len(us), 'coll %.2f debt %.0f of %.0f' % (csum, dsum, tba / 10**ld))
    pos = [S.pos('morpho', CH, B, u, d['coll'], d['syms'], d['st'], d['oth'], d['back'], markets=d['markets']) for u, d in peruser.items() if d['back'] >= 100]
    meta = dict(venue='morpho', chain=CH, blue=blue, block=B, eth_price_ref_scan_day=ref, markets=mk,
                eth_backing_dollar_total=round(sum(x['eth_backing_dollar'] for x in mk), 3), collateral_native_total=round(sum(x['collateral_native'] for x in mk), 3),
                note='users from the Morpho API (positions now + WithdrawCollateral/Liquidation after the snapshot); state at the snapshot block via archive RPC')
    return meta, pos


def main():
    B = S.block_at(CH)
    metas = []; pos = []
    m2, p2 = morpho(B); metas.append(m2); pos += p2
    hf_res, _, _ = X.reserves_at(CH, X.POOLS['hypurrfi'][1], B)
    hf_ref = S.ref_price(hf_res)
    metas.append(dict(venue='hypurrfi', chain=CH, pool=X.POOLS['hypurrfi'][1], block=B,
                      eth_family_reserves={r['sym']: round(r['supply'], 4) for r in hf_res if r['fam'] == 'own'},
                      eth_family_supply_native=round(sum(r['supply'] * r['price'] / hf_ref for r in hf_res if r['fam'] == 'own'), 3),
                      note='ETH-family supply under 100 ETH: no position can reach 100; not enumerated'))
    metas.append(dict(venue='felix-cdp', chain=CH, note='Felix feUSD CDP branches WHYPE, UBTC, kHYPE, wstHYPE (usefelix.gitbook.io docs); no ETH-family branch'))
    m1, p1 = hyperlend(B); metas.insert(0, m1); pos += p1
    kinds = S.code_kinds((CH, B, p['account']) for p in pos)
    for p in pos: p['code_kind'] = kinds[(CH, p['account'])]
    pos.sort(key=lambda p: -p['eth_backing_dollar'])
    S.write('hyperevm', metas, pos)


if __name__ == '__main__':
    main()
