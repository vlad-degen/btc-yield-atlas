"""Fetch raw on-chain data from Morph Blockscout (explorer-api.morphl2.io) used by the other scripts.
Run order: fetch_all.py -> state_now.py > ../raw/state_now.json -> weekly.py -> yields.py -> swaps.py -> ltv_path.py
           -> por.py -> eth_supply.py -> build_tvl.py -> build_misc.py -> governance.py ; build_events.py (from bitget/ dir)"""
import json, datetime
from collections import defaultdict
from bs import *
from morphoev import decode
M='0xad10d07901dc3195c3cb5e78e061f4ea8d9b4905'; MID='0x37d156e96a4230c1fe9545579086e4b40d08b4aae8b3c78ee91031f2a22c1a5c'
V='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'; G='0x9131eb40bd0bdce73c72755f1bb2cf39a9453341'
PFC='0x89963ff339c4a6194ea77381c204884e4503f8fb'; D='0x53d239feef1fc7c8cf80bc6e920796d33db0c027'
BG='0x31011317764e097b28d159a8145b92bfa453f606'; OMNI='0x9EB53a82d9f390dBe94b6B8b15ca32B523195cA4'
R='../raw/'
# 1. Morpho market events (bgBTC/USDC) -> decoded
logs=getlogs_w(M,24000000,27400000,topic1=MID); json.dump(logs,open(R+'morpho_logs_market.json','w'))
json.dump([decode(l) for l in logs],open(R+'morpho_market_decoded.json','w'))
# 2. Aera vault price history (PriceAndFeeCalculatorV2, vault-indexed)
json.dump(getlogs_w(PFC,24000000,27400000,topic1='0x'+V[2:].rjust(64,'0')),open(R+'pfc_logs_vault.json','w'))
# 3. token transfers / holders
json.dump(v2_all(f'/api/v2/addresses/{V}/token-transfers'),open(R+'aera_token_transfers.json','w'))
json.dump(v2_all(f'/api/v2/addresses/{OMNI}/token-transfers'),open(R+'omnibus_token_transfers.json','w'))
json.dump(v2_all(f'/api/v2/tokens/{V}/holders'),open(R+'aera_holders.json','w'))
json.dump(v2_all(f'/api/v2/tokens/{G}/holders'),open(R+'gtusdc_holders.json','w'))
json.dump(v2_all(f'/api/v2/tokens/{BG}/holders'),open(R+'bgbtc_morph_holders.json','w'))
# 4. reward distributor (unverified contract 0x53d2...): decode campaigns
dl=getlogs_w(D,24000000,27400000); json.dump(dl,open(R+'distributor_logs.json','w'))
def W(d): d=d[2:]; return [int(d[i:i+64],16) for i in range(0,len(d),64)]
def A(t): return '0x'+t[-40:]
# topic0 meanings inferred from calldata/usage: f53e8e27=CampaignCreated(id,creator,token | amount,start,end); 15fe459f=RewardDeposited(id,funder | amount)
# cc8d87b5=RootUpdated(id,epoch | root,?,cumulativeTotal); e15f7abb=Claimed(id,user,? | amount,...)
camps={}; deps=defaultdict(list); roots=defaultdict(list); claims=defaultdict(lambda: defaultdict(int)); ncl=defaultdict(int)
for l in dl:
    t=l['topics'][0][:10]; w=W(l['data']); ts=int(l['timeStamp'],16)
    if t=='0xf53e8e27': camps[int(l['topics'][1],16)]=dict(creator=A(l['topics'][2]),token=A(l['topics'][3]),amount=w[0],start=w[1],end=w[2])
    elif t=='0x15fe459f': deps[int(l['topics'][1],16)].append((ts,A(l['topics'][2]),w[0]))
    elif t=='0xcc8d87b5': roots[int(l['topics'][1],16)].append((ts,w))
    elif t=='0xe15f7abb': cid=int(l['topics'][1],16); claims[cid][A(l['topics'][2])]+=w[0]; ncl[cid]+=1
rows=[]
for cid,c in sorted(camps.items()):
    usdc=c['token']=='0xcfb1186f4e93d60e60a8bdd997427d1f33bc372b'; dec=6 if usdc else 18
    rows.append(dict(id=cid,token='USDC' if usdc else c['token'],amount=c['amount']/10**dec,start=c['start'],end=c['end'],creator=c['creator'],
        deposited=sum(x[2] for x in deps[cid])/10**dec,funders=list(set(x[1] for x in deps[cid])),claimed=sum(claims[cid].values())/10**dec,
        aera_claimed=claims[cid].get(V,0)/10**dec,n_claims=ncl[cid],n_claimers=len(claims[cid]),last_root_total=(roots[cid][-1][1][-1]/10**dec if roots[cid] else None)))
json.dump(rows,open(R+'campaigns.json','w'),indent=1)
print('done', len(logs), len(dl), len(rows))
