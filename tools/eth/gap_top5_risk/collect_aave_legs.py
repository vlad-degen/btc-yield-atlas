"""Per-reserve legs for every Aave/Spark account at every month-end + T: user configuration bitmap ->
borrowed / collateral reserves; variable debt and aToken balances, oracle prices, reserve borrow rates.
Fills gaps in data/eth/economic-dollar-loans.csv (legs not captured there). Output raw aave_legs_raw.json"""
import json
from glib import *
from collect_positions import POOL_ACCTS
POOLS = {'Aave': '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2', 'Spark': '0xc13e21b648a5ee794902342038ff3adab66be987'}
def main():
    M = months()
    # oracle + token maps at T (reserve token addresses are stable for these assets)
    meta = {}
    for name, pool in POOLS.items():
        prov = dec_addr(words(batch([c(pool, 'ADDRESSES_PROVIDER()')], tag='prov')[0])[0])
        orc = dec_addr(words(batch([c(prov, 'getPriceOracle()')], tag='orc')[0])[0])
        meta[name] = {'provider': prov, 'oracle': orc, 'reserves': {}}
    out = {'meta': meta, 'months': []}
    for m, ts, b in M:
        rec = {'month': m, 'block': b, 'timestamp': ts, 'accounts': []}
        for prod, venue, pool, acct in POOL_ACCTS:
            r = batch([c(pool, 'getReservesList()', '', b), c(pool, 'getUserConfiguration(address)', enc_addr(acct), b)], tag=f'cfg_{m}')
            if not r[0]: continue
            w = words(r[0]); n = w[1]; res = [dec_addr(x) for x in w[2:2 + n]]
            cfg = words(r[1])[0] if r[1] else 0
            used = [(i, a, (cfg >> (2 * i)) & 1, (cfg >> (2 * i + 1)) & 1) for i, a in enumerate(res) if (cfg >> (2 * i)) & 3]
            if not used: continue
            R = meta[venue]['reserves']
            need = [a for _, a, _, _ in used if a not in R]
            if need:
                rr = batch([c(pool, 'getReserveData(address)', enc_addr(a), TB) for a in need] + [c(a, 'symbol()', '', TB) for a in need] + [c(a, 'decimals()', '', TB) for a in need], tag='resmeta')
                k = len(need)
                for j, a in enumerate(need):
                    wd = words(rr[j]); sym = rr[k + j]
                    try: sym = dec_string(sym)
                    except Exception: sym = '?'
                    if a.lower() == '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2': sym = 'MKR'
                    R[a] = {'symbol': sym, 'decimals': words(rr[2 * k + j])[0], 'aToken': dec_addr(wd[8]), 'vDebt': dec_addr(wd[10])}
            calls = []
            for i, a, bor, col in used:
                calls.append(c(meta[venue]['oracle'], 'getAssetPrice(address)', enc_addr(a), b))
                calls.append(c(pool, 'getReserveData(address)', enc_addr(a), b))
                calls.append(c(R[a]['vDebt'], 'balanceOf(address)', enc_addr(acct), b) if bor else c(R[a]['aToken'], 'balanceOf(address)', enc_addr(acct), b))
                calls.append(c(R[a]['aToken'], 'balanceOf(address)', enc_addr(acct), b))
            rr = batch(calls, tag=f'legs_{m}')
            legs = []
            for j, (i, a, bor, col) in enumerate(used):
                pr, rd, debt, coll = rr[4 * j:4 * j + 4]
                dec = R[a]['decimals']
                legs.append({'asset': a, 'symbol': R[a]['symbol'], 'borrowing': bool(bor), 'collateral': bool(col),
                             'priceUSD': words(pr)[0] / 1e8 if pr else None,
                             'variableBorrowAPR': words(rd)[4] / 1e27 if rd else None,
                             'debt': (words(debt)[0] / 10 ** dec) if (bor and debt) else 0,
                             'supplied': words(coll)[0] / 10 ** dec if coll else 0})
            rec['accounts'].append({'product': prod, 'venue': venue, 'account': acct, 'legs': legs})
        out['months'].append(rec)
        print(m, len(rec['accounts']), flush=True)
    json.dump(out, open(RAW / 'aave_legs_raw.json', 'w'), indent=1)
if __name__ == '__main__':
    main()
