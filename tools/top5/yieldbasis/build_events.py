# events.csv: YB DAO proposals (execution dates from api.yieldbasis.com), Curve DAO votes (prices.curve.finance),
# on-chain credit-line changes (archive bisect), market creations, stress/market events; with BTC-market TVL before/after
import json,csv,datetime,collections
from load import *
S=snaps()
tv=collections.defaultdict(float)
for mid,s in S.items():
    if 'WETH' in NAMES[mid]: continue
    for d,x in s.items(): tv[d]+=x['tot']
def tvl(d,off):
    t=(datetime.date.fromisoformat(d)+datetime.timedelta(days=off)).isoformat()
    ks=[k for k in tv if k<=t]
    return round(tv[max(ks)],1) if ks else None
ev=[]
def add(date,event,typ,src): ev.append(dict(date=date,event=event,type=typ,source=src))
P=json.load(open('../raw/api/proposals.json'))['data']
for p in P:
    ex=p.get('executed') or {}
    d=datetime.datetime.fromtimestamp(ex['blockTimestamp'],datetime.UTC).strftime('%Y-%m-%d') if ex.get('blockTimestamp') else None
    st=datetime.datetime.fromtimestamp(int(p['startDate']),datetime.UTC).strftime('%Y-%m-%d')
    title=(p['title'] or p['summary'][:80]).strip()
    add(d or st,'YB DAO #%d %s: %s%s'%(p['incrementalId'],'executed' if d else 'created (not executed)',title,'' if d else ' [start %s]'%st),'YB governance','api.yieldbasis.com/v1/governance/proposals (onchain Aragon DAO 0x42F2…95Fa)')
C=json.load(open('../raw/curve_dao_proposals.json'))
for p in C:
    m=(p.get('metadata') or '')
    if p['start_date']>1740000000 and any(k in m.lower() for k in ['yield basis','yieldbasis','yb ','yb-',' yb','credit line']):
        d=(p.get('execution_date') or p['dt'])[:10]
        fr=int(p['votes_for']); ag=int(p['votes_against'])
        add(d,'Curve DAO vote %d %s (%.2f%% yes): %s'%(p['vote_id'],'executed' if p.get('executed') else 'NOT executed/failed',fr/(fr+ag)*100 if fr+ag else 0,m[:160]),'Curve governance','prices.curve.finance/v1/dao/proposals; gov.curve.finance')
for c in json.load(open('../raw/credit_line_changes.json')):
    add(c['time'][:10],'crvUSD debt ceiling for YB Factory set to %dM crvUSD (block %d)'%(c['debt_ceiling']//10**6,c['block']),'credit line (onchain)','archive eth_call crvUSD ControllerFactory.debt_ceiling(0x370a…00c0)')
for k,v in json.load(open('../raw/creation.json')).items():
    if k!='Factory': add(v['date'][:10],'Market %s LT deployed (%s)'%(k,v['addr']),'market launch','Blockscout creation tx %s'%v['tx'])
extra=[
('2024-12-27','Basis Yield AG (Swiss AG, Zug) registered','corporate','docs.yieldbasis.com/pdf/mica-whitepaper.pdf'),
('2025-02-18','Private token round $5M at $50M valuation (DefiLlama raises); whitepaper: $6M total from SevenX, Delphi Ventures, AntAlpha, Amber, Aquarius, Bitscale, Mirana, Chorus One, Karatage, NoLimitsHoldings +20 angels','funding','api.llama.fi/protocol/yield-basis; MiCA whitepaper'),
('2025-09-11','Public sale (Legion x Kraken) subscription 11-12 Sep: 25M YB (2.5%) at $0.20, $5M, $200M FDV; USDC; Kraken listing at TGE','token sale','MiCA whitepaper Part E'),
('2025-09-15','YB token and Factory deployed','token','docs.yieldbasis.com/user/governance/yb-token; Blockscout'),
('2025-09-24','Launch: 3 markets with $1M cap each (2M crvUSD); UI overloaded, pools filled within a minute','market launch','news.curve.finance/yieldbasis-on-curve-whats-happened-so-far'),
('2025-10-10','BTC crash (daily close 121.7k->110.8k); v1 book PPS -2% to -5% on the day, redemption value held ~1.00; recovered within ~4 days','stress','api.yieldbasis.com market snapshots'),
('2025-10-15','YB TGE / emissions start 10:00 UTC; YB first price $0.677 (DefiLlama); 5M YB airdrop to veCRV voters','token','news.curve.finance; coins.llama.fi'),
('2025-12-04','Fee switch live: first veYB epoch ($409k); 17.55 BTC accrued fees distributed over 4 weeks','fee switch','api.yieldbasis.com fee epochs; PR Newswire 302633982'),
('2026-01-15','DefiLlama protocol TVL peak $247.3M','TVL','api.llama.fi/protocol/yield-basis'),
('2026-02-05','BTC crash to $62.7k; Cryptoswap price_scale stuck ~88.8k; TRD -19.5% (v2-WBTC), -18.5% (cbBTC), -16.9% (tBTC); TRD < -1% for 76-77 consecutive days (Jan 30-Apr 16)','stress','api.yieldbasis.com snapshots; archive price_scale'),
('2026-03-26','HybridVault audits (MixBytes, ChainSecurity)','security','docs.yieldbasis.com/user/reference/audits'),
('2026-05-19','Docs: bug bounty still "in preparation"','security','docs.yieldbasis.com/user/reference/audits'),
('2026-06-06','BTC -21% in June (73.5k Jun 1 -> 59.5k Jun 29); v3 TRD up to -4.7% (tBTC), closed by ~Jul 6','stress','api.yieldbasis.com snapshots'),
('2026-07-24','ChainSecurity audit #10 (AMM+LT hardening, YBLendingOracle)','security','docs.yieldbasis.com/user/reference/audits'),
('2026-09-07','v3-cbBTC outflow: TVL 643 -> 326 BTC in 3 days (Sep 7-9)','flows','api.yieldbasis.com snapshots'),
('2026-09-21','BTC $86.6k vs WBTC/tBTC pool price_scale ~$69.6k (+24% lag): TRD -6.0% (WBTC), -5.8% (tBTC); 100-share exit haircut -8%/-11%','stress','eth_call preview_withdraw / price_scale at block 26,029,7xx'),
]
for e in extra: add(*e)
ev.sort(key=lambda e:e['date'])
for e in ev:
    e['btc_tvl_d_minus1']=tvl(e['date'],-1); e['btc_tvl_d_plus7']=tvl(e['date'],7)
with open('../events.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['date','event','type','source','btc_tvl_d_minus1','btc_tvl_d_plus7']); w.writeheader(); [w.writerow(e) for e in ev]
print(len(ev))
