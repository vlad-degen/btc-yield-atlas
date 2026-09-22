# Build a daily table of Morpho positions of the strategy wallet: BTC collateral, dollar debt, vault holdings
import json,datetime,collections,csv
d=json.load(open('raw/morpho_pos_history.json'))
BTC={'WBTC','cbBTC','LBTC','triBTC'}
rows=collections.defaultdict(lambda:collections.defaultdict(float))
def ser(h,key):
    return {p['x']:p['y'] for p in (h or {}).get(key) or [] if p['y'] is not None}
for k,v in d['markets'].items():
    cid=k.split(':')[0]; m=v['market']; ca=(m['collateralAsset'] or {}).get('symbol'); la=m['loanAsset']['symbol']
    hs=v['hist']['data']['marketPosition']['historicalState']
    col=ser(hs,'collateral'); colu=ser(hs,'collateralUsd'); bu=ser(hs,'borrowAssetsUsd'); ba=ser(hs,'borrowAssets'); su=ser(hs,'supplyAssetsUsd')
    for x in set(col)|set(bu)|set(su):
        day=datetime.datetime.fromtimestamp(x,datetime.UTC).strftime('%Y-%m-%d'); r=rows[day]
        dec={'WBTC':8,'cbBTC':8,'LBTC':8,'triBTC':8}.get(ca,18)
        c=float(col.get(x) or 0)/10**dec
        if ca in BTC and c>0:
            r[f'btc_coll_{cid}']+=c; r[f'btc_coll_usd_{cid}']+=float(colu.get(x) or 0)
            if la in BTC: r[f'btc_debt_{cid}']+=float(ba.get(x) or 0)/1e8
            else: r[f'usd_debt_btccoll_{cid}']+=float(bu.get(x) or 0)
        elif c>0:
            r[f'stable_coll_usd_{cid}']+=float(colu.get(x) or 0); r[f'usd_debt_stablecoll_{cid}']+=float(bu.get(x) or 0)
        r[f'mkt_supply_usd_{cid}']+=float(su.get(x) or 0)
        if (bu.get(x) or 0)>1000 or c>0: r['active_'+cid+'_'+(ca or '')+'/'+la]=1
for k,v in list(d['v2'].items())+list(d['v1'].items()):
    cid=k.split(':')[0]; name=v['vault']['name']
    h=v['hist']['data']
    h=(h.get('vaultV2PositionByAddress') or {}).get('history') if 'vaultV2PositionByAddress' in h else (h.get('vaultPosition') or {}).get('historicalState')
    au=ser(h,'assetsUsd')
    for x,y in au.items():
        if y and y>1000:
            day=datetime.datetime.fromtimestamp(x,datetime.UTC).strftime('%Y-%m-%d')
            key='vault_btc_usd_' if 'cbBTC' in name else 'vault_usd_'
            rows[day][key+cid]+=y; rows[day]['v:'+cid+':'+name]=y
json.dump(rows,open('raw/morpho_daily.json','w'),indent=0)
for day in sorted(rows):
    r=rows[day]
    if day.endswith('-01') or day.endswith('-15') or day=='2026-09-21':
        print(day,{k:round(v,2) for k,v in r.items() if not k.startswith('active') and not k.startswith('v:')}, [k[7:] for k in r if k.startswith('active')], [(k[2:],round(v/1e6,2)) for k,v in r.items() if k.startswith('v:')])
