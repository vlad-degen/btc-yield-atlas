import json, datetime
from collections import defaultdict
from rpc import *
V='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'; CV='0x4df7557734b382eb542bea6c74786d398df4cc19'; D='0x53d239feef1fc7c8cf80bc6e920796d33db0c027'
ORA='0x22b3d92703ee73af5e31a6ba56cca2fdced6c412'
tt=json.load(open('../raw/aera_token_transfers.json'))
bytx=defaultdict(list)
for x in tt: bytx[x['transaction_hash']].append(x)
rows=[]; claims=[]
for h,xs in bytx.items():
    usdc_out=sum(int(x['total']['value']) for x in xs if x['token']['symbol']=='USDC' and x['to']['hash'].lower()==CV)/1e6
    bg_in=sum(int(x['total']['value']) for x in xs if x['token']['symbol']=='BGBTC' and x['from']['hash'].lower()==CV)/1e8
    cl=sum(int(x['total']['value']) for x in xs if x['token']['symbol']=='USDC' and x['from']['hash'].lower()==D)/1e6
    ts=xs[0]['timestamp']; blk=xs[0]['block_number']
    if cl: claims.append((ts,blk,cl,h))
    if usdc_out or bg_in: rows.append(dict(ts=ts,block=blk,usdc=usdc_out,bgbtc=bg_in,tx=h,claim_same_tx=cl))
rows.sort(key=lambda r:r['block']); claims.sort(key=lambda r:r[1])
for r in rows:
    try: r['oracle']=int(eth_call('morph',ORA,sel('price()'),hex(r['block'])),16)/1e34
    except Exception as e: r['oracle']=None
    r['px']=r['usdc']/r['bgbtc'] if r['bgbtc'] else None
    r['prem_bps']=(r['px']/r['oracle']-1)*1e4 if r['px'] and r['oracle'] else None
json.dump(dict(swaps=rows,claims=claims),open('../raw/aera_swaps_claims.json','w'),indent=1)
tot_u=sum(r['usdc'] for r in rows); tot_b=sum(r['bgbtc'] for r in rows)
wavg=sum(r['prem_bps']*r['usdc'] for r in rows if r['prem_bps'] is not None)/sum(r['usdc'] for r in rows if r['prem_bps'] is not None)
print('swaps',len(rows),'usdc',round(tot_u,2),'bgbtc',round(tot_b,6),'avg px',round(tot_u/tot_b,1),'usdc-weighted premium vs RedStone BTC (bps)',round(wavg,1))
print('claims',len(claims),'usdc',round(sum(c[2] for c in claims),2), 'claims in same tx as swap', sum(1 for r in rows if r['claim_same_tx']))
for r in rows[:5]+rows[-5:]: print(r['ts'][:16], round(r['usdc'],2), r['bgbtc'], round(r['px'],1), round(r['oracle'],1), round(r['prem_bps'],1))
import statistics
print('premium bps min/median/max', round(min(r['prem_bps'] for r in rows),1), round(statistics.median(r['prem_bps'] for r in rows),1), round(max(r['prem_bps'] for r in rows),1))
