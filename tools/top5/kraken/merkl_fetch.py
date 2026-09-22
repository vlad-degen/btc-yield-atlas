"""Merkl campaign history for the Sentora vaults the Kraken BTC vault deploys into.
Output raw/merkl_campaigns.json : list of campaigns (opportunity, start, end, token, amount, maxApr, whitelist, creator)."""
import json, subprocess, os, datetime
OPPS = {
    '2433802672589613459': 'Sentora RLUSD Main',
    '18030207387280065324': 'Paypal USD Main',
    '13915712898351585707': 'Paypal USD Main (VEDA_WL)',
    '6613264294859538569': 'Paypal USD Main (WHITELIST_PER_PROTOCOL)',
    '16103329905303288034': 'Sentora PRIME Main',
    '7367976340087662064': 'Sentora Huma PST Main',
}
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
def get(url):
    r = subprocess.run(['curl', '-s', '-m', '60', url], capture_output=True)
    return json.loads(r.stdout.decode())
out = []
for oid, name in OPPS.items():
    seen = set()
    for page in range(0, 5):
        d = get(f'https://api.merkl.xyz/v4/campaigns?opportunityId={oid}&items=100&page={page}')
        if not isinstance(d, list) or not d:
            break
        new = 0
        for c in d:
            if c['id'] in seen:
                continue
            seen.add(c['id']); new += 1
            p = c.get('params', {})
            tok = c.get('rewardToken', {}) or {}
            dec = tok.get('decimals') or p.get('decimalsRewardToken') or 18
            out.append(dict(opp=oid, vault=name, id=c['id'], start=int(c['startTimestamp']), end=int(c['endTimestamp']),
                            token=tok.get('symbol') or p.get('symbolRewardToken'), amount=int(c['amount']) / 10 ** int(dec),
                            creator=c.get('creatorAddress'), whitelist=p.get('whitelist'), blacklist=p.get('blacklist'),
                            maxApr=(p.get('apr') or p.get('maxApr') or c.get('maxApr')), hooks=p.get('hooks'),
                            params={k: v for k, v in p.items() if k not in ('whitelist', 'blacklist')}))
        if new == 0 or len(d) < 100:
            break
    print(name, len(seen))
json.dump(out, open(os.path.join(RAW, 'merkl_campaigns.json'), 'w'), indent=1)
for r in sorted(out, key=lambda r: (r['vault'], r['start'])):
    print(r['vault'][:28].ljust(28), datetime.datetime.utcfromtimestamp(r['start']).strftime('%Y-%m-%d'),
          datetime.datetime.utcfromtimestamp(r['end']).strftime('%Y-%m-%d'), r['token'], round(r['amount']),
          'WL' if r['whitelist'] else '', str(r['whitelist'])[:90], r['creator'][:8] if r['creator'] else None)
