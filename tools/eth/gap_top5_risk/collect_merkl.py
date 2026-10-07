"""Merkl v4 campaigns (creator, token, amount, window) for every opportunity that paid the five products' accounts,
plus opportunity metadata. Output raw merkl_campaigns.json"""
import json
from glib import *
OPPS = {'2433802672589613459': 'Sentora RLUSD Main V2', '16103329905303288034': 'Sentora PRIME Main V2 (PYUSD)', '18030207387280065324': 'Paypal USD Main V2',
        '6397446418992379567': 'ETHFI opp A', '12102526591740948527': 'ETHFI opp B', '2333904021624385905': 'rEUL opp',
        '13207567167701080626': 'BOLD opp (Liquity vault)', '16088678467640585746': 'USDS opp (Avant)', '15682151196496106260': 'MORPHO opp (Avant)'}
out = {'opportunities': {}, 'campaigns': []}
for oid, name in OPPS.items():
    o = http_json(f'https://api.merkl.xyz/v4/opportunities/{oid}', f'merkl_opp_{oid}')
    out['opportunities'][oid] = {k: (o or {}).get(k) for k in ['id', 'chainId', 'type', 'identifier', 'name', 'status', 'apr', 'tvl', 'dailyRewards', 'protocol', 'tokens']}
    seen = set()
    for page in range(10):
        d = http_json(f'https://api.merkl.xyz/v4/campaigns?opportunityId={oid}&items=100&page={page}', f'merkl_campaigns_{oid}_p{page}')
        if not isinstance(d, list) or not d: break
        new = 0
        for c_ in d:
            if c_['id'] in seen: continue
            seen.add(c_['id']); new += 1
            p = c_.get('params', {}) or {}; tok = c_.get('rewardToken', {}) or {}
            dec = tok.get('decimals') or p.get('decimalsRewardToken') or 18
            out['campaigns'].append(dict(opportunityId=oid, opportunity=name, id=c_['id'], campaignId=c_.get('campaignId'), start=int(c_['startTimestamp']), end=int(c_['endTimestamp']),
                                         token=tok.get('symbol'), tokenAddress=tok.get('address'), tokenPrice=tok.get('price'), amount=int(c_['amount']) / 10 ** int(dec),
                                         creator=c_.get('creatorAddress') or (c_.get('creator') or {}).get('address'), creatorTags=(c_.get('creator') or {}).get('tags'),
                                         whitelist=p.get('whitelist'), blacklist=p.get('blacklist'), distributionMethod=(c_.get('distributionMethodParameters') or {}).get('distributionMethod'),
                                         createdAt=c_.get('createdAt'), apr=c_.get('apr'), computeChainId=c_.get('computeChainId')))
        if new == 0 or len(d) < 100: break
    print(name, len(seen))
json.dump(out, open(RAW / 'merkl_campaigns.json', 'w'), indent=1)
