# Incentives received by the strategy wallet, valued at claim-date prices (DefiLlama), monthly. Katana: Merkl totals allocated over the Katana-active period (estimate)
import json,datetime,collections,csv
R='raw/'
def load_px(fn):
    d=json.load(open(R+fn))['coins']; v=list(d.values())[0]['prices']
    return {datetime.datetime.fromtimestamp(p['timestamp'],datetime.UTC).strftime('%Y-%m-%d'):p['price'] for p in v}
PX={'WMON':load_px('px_monad_0x3bd359c1119da7da1d913d1c4d2b7c46.json'),'MORPHO':load_px('px_ethereum_0x58D97B57BB95320F9a05dC918Aef6.json'),
    'PENDLE':load_px('px_ethereum_0x808507121B80c02388fAd14726482.json'),'CRV':load_px('px_ethereum_0xD533a949740bb3306d119CC777fa9.json'),'KAT':load_px('px_coingecko_katana-network-token.json')}
def price(sym,day):
    if sym in ('USDS','USDT','USDC','PYUSD','AUSD','vbUSDC'): return 1.0
    if sym in ('EURC','EURCV'): return 1.15
    if sym=='EUL': return 1.43
    if sym=='FLUID': return 4.0
    if sym=='BARD': return 0.0
    s=PX.get(sym,{}); d=datetime.date.fromisoformat(day)
    for i in range(10):
        k=(d-datetime.timedelta(days=i)).isoformat()
        if k in s: return s[k]
    return None
MERKL='0x3ef3d8ba38ebe18db133cec108f4d14ce00dd9ae'
out=collections.defaultdict(lambda:collections.defaultdict(float))
# Monad WMON (+ AUSD, USDC, rEUL) from Merkl distributor
d=json.load(open(R+'sma1_monad_logs.json'))
SYM={'0x3bd359c1119da7da1d913d1c4d2b7c461115433a':('WMON',18),'0x00000000efe302beaa2b3e6e1b18d08d69a9012a':('AUSD',6),'0x754704bc059f8c67012fed69bc8a327a5aafb603':('USDC',6)}
seen=set()
for l in d['logs']:
    a=l['address'].lower()
    if a not in SYM or len(l['topics'])<3: continue
    if '0x'+l['topics'][1][-40:]!=MERKL: continue
    k=(l['transactionHash'],l['logIndex'])
    if k in seen: continue
    seen.add(k)
    s,dc=SYM[a]; v=int(l['data'][:66],16)/10**dc; day=datetime.datetime.fromtimestamp(int(l['blockTimestamp'],16),datetime.UTC).strftime('%Y-%m-%d')
    out[day[:7]]['monad_'+s+'_usd']+=v*price(s,day); out[day[:7]]['monad_'+s+'_units']+=v
# Ethereum reward-token inflows
L=json.load(open(R+'sma1_eth_transfers.json'))
W='0x933adedd85824da75ec8a334a7907e69e7c02833'
SRC={MERKL:'merkl','0x93b4b9bd266ffa8af68e39edfa8cfe2a62011ce0':'crv_accountant','0xf239f9266e891956e3eb55fa4ede65c187ad0f86':'bard','0x4d7e09f73843bd4735aaf7a74b6d877bac75a531':'eul','0x7060fe0dd3e31be01efac6b28c8d38018fd163b0':'fluid'}
for x in L:
    fr=x['from']['hash'].lower(); to=x['to']['hash'].lower()
    if to!=W or fr not in SRC: continue
    t=x['token']
    if int(t.get('holders_count') or 0)<50: continue
    s=t['symbol']; v=int(x['total']['value'])/10**int(x['total']['decimals'] or 18); day=x['timestamp'][:10]
    p=price(s.upper() if s.upper() in PX else s,day) or 0
    out[day[:7]]['eth_'+s+'_usd']+=v*p
# Katana (Merkl API totals; claim timing unknown -> allocated pro-rata to Katana debt-days, estimate)
kat={'KAT':2413285.7,'MORPHO':8164.3,'vbUSDC':9668.8}
rows=list(csv.DictReader(open(R+'balance_sheet_daily.csv')))
kd={r['date']:float(r.get('katana_morpho_usd_debt') or 0) for r in rows}
tot=sum(kd.values())
for day,debt in kd.items():
    if debt<=0: continue
    w=debt/tot
    for s,u in kat.items(): out[day[:7]]['katana_'+s+'_usd_est']+=u*w*(price(s,day) or 0)
json.dump(out,open(R+'incentives_monthly.json','w'),indent=0)
for m in sorted(out):
    r=out[m]; tot=sum(v for k,v in r.items() if k.endswith('_usd') or k.endswith('_usd_est'))
    print(m,'total $%.0f'%tot,{k:round(v) for k,v in r.items() if (k.endswith('usd') or k.endswith('est')) and v>100})
