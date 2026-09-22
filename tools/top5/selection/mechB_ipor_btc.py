import json
d=json.load(open('../raw/mechB/ipor_fusion_vaults.json'))
V=d['vaults']
print(len(V),'vaults; creationDate',d.get('creationDate'))
print('keys', list(V[0].keys()))
btc=[v for v in V if 'BTC' in (v.get('asset') or '').upper()]
print(len(btc),'BTC vaults')
rows=[]
for v in btc:
    h=v.get('history') or []
    last=max(h, key=lambda x:x['blockNumber']) if h else {}
    tvl=float(last.get('tvl') or 0)
    borrows=[(m['protocol'],m['marketId'],round(float(m['balanceUsd'])/1e6,3)) for m in last.get('marketBalances',[]) if m['balanceType']=='BORROW' and abs(float(m['balanceUsd']))>1000]
    deps=[(m['protocol'],m['marketId'][:10],round(float(m['balanceUsd'])/1e6,3)) for m in last.get('marketBalances',[]) if m['balanceType']!='BORROW' and abs(float(m['balanceUsd']))>1000]
    rows.append((tvl, v['chainId'], v['name'], v['address'], v['asset'], last.get('blockTimestamp'), last.get('totalBalance'), borrows, deps))
for r in sorted(rows, key=lambda r:-r[0]):
    print(f"{r[1]}|{r[2]}|{r[3]}|{r[4]}|TVL ${r[0]/1e6:.3f}M|bal {r[6]}|{r[5]}\n    BORROW {r[7]}\n    DEP {r[8]}")
