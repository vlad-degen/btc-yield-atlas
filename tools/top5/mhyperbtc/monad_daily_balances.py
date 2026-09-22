# Reconstruct daily (00:00 UTC) token balances of the strategy wallet on Monad from Transfer logs (no archive state on public Monad RPC)
import json,datetime,collections,sys
sys.path.insert(0,'scripts')
W='0x933adedd85824da75ec8a334a7907e69e7c02833'
TOK={'0x0555e30da8f98308edb960aa94c0db47230d2b9c':('WBTC',8),'0xd18b7ec58cdf4876f6afebd3ed1730e4ce10414b':('cbBTC',8),'0xecac9c5f704e954931349da37f60e39f515c11c1':('LBTC',8),
 '0xb0f70c0bd6fd87dbeb7c10dc692a2a6106817072':('BTC.b',8),'0x5d37f9b272ca7cda2a05245b9a503746eefac88f':('3BTC_LP',18),'0xd2634e05ebed90bd0a6c0e93d48d7bd8036653b1':('triBTC',18),
 '0x6a144d277412b35696f29d8de3d141cde68f4d2f':('hyperEcbBTC',8),'0x1f5e388861a32226c716e922ce748a6fee5e8e57':('aMoncbBTC',8),'0x1dd98ede37480c2e0827a107c68f442aa516e7fc':('vdMonGHO',18),
 '0x754704bc059f8c67012fed69bc8a327a5aafb603':('USDC',6),'0x00000000efe302beaa2b3e6e1b18d08d69a9012a':('AUSD',6),'0xe7cd86e13ac4309349f30b3435a9d337750fc82d':('USDT0',6),'0xfc421ad3c883bf9e7c4f42de845c4e4405799e73':('GHO',18)}
d=json.load(open('raw/sma1_monad_logs.json'))
ev=[]
seen=set()
for l in d['logs']:
    a=l['address'].lower()
    if a not in TOK or len(l['topics'])<3: continue
    key=(l['transactionHash'],l['logIndex'])
    if key in seen: continue
    seen.add(key)
    fr='0x'+l['topics'][1][-40:]; to='0x'+l['topics'][2][-40:]; v=int(l['data'][:66],16)/10**TOK[a][1]
    ts=int(l['blockTimestamp'],16); s=TOK[a][0]
    if fr==W: ev.append((ts,s,-v))
    if to==W: ev.append((ts,s,v))
ev.sort()
bal=collections.defaultdict(float); out={}; i=0
day=datetime.datetime(2025,11,20,tzinfo=datetime.timezone.utc)
while day<=datetime.datetime(2026,9,22,tzinfo=datetime.timezone.utc):
    T=int(day.timestamp())
    while i<len(ev) and ev[i][0]<T: bal[ev[i][1]]+=ev[i][2]; i+=1
    out[day.strftime('%Y-%m-%d')]={k:round(v,8) for k,v in bal.items() if abs(v)>1e-6}
    day+=datetime.timedelta(days=1)
json.dump(out,open('raw/monad_daily_balances.json','w'),indent=0)
for k in list(out)[::14]: print(k,{s:round(v,2) for s,v in out[k].items() if abs(v)>0.01})
