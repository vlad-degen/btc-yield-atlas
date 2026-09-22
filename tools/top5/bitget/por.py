"""Chainlink BGBTC PoR feed history on Ethereum (proxy getRoundData walk-back)."""
from rpc import *
import json, datetime
P='0xADcc914F882965Ef1B2f1043522b3B81ED081491'
def w(r): h=r[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
dec=dec_uint(eth_call('eth',P,sel('decimals()')))
desc=dec_str(eth_call('eth',P,sel('description()')))
lr=w(eth_call('eth',P,sel('latestRoundData()')))
rid=lr[0]; phase=rid>>64; agg_r=rid & ((1<<64)-1)
print(desc,'decimals',dec,'latest round',rid,'phase',phase,'aggRound',agg_r)
rows=[]
calls=[('eth_call',[{'to':P,'data':sel('getRoundData(uint80)')+enc_uint((phase<<64)|r)},'latest']) for r in range(max(1,agg_r-400),agg_r+1)]
for i in range(0,len(calls),50):
    res=batch('eth',calls[i:i+50])
    for r in res:
        if isinstance(r,tuple) or not r or r=='0x': continue
        x=w(r); rows.append(dict(round=x[0]&((1<<64)-1),answer=x[1]/10**dec,updatedAt=x[3],date=datetime.datetime.utcfromtimestamp(x[3]).strftime('%Y-%m-%d %H:%M')))
json.dump(rows,open('../raw/por_rounds.json','w'),indent=0)
prev=None
for r in rows:
    if r['answer']!=prev: print(r['date'], r['round'], r['answer']); prev=r['answer']
print('n rounds',len(rows),'first',rows[0]['date'] if rows else None)
