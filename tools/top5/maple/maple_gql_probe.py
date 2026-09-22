#!/usr/bin/env python3
"""Probe Maple's public GraphQL API (api.maple.finance/v2/graphql) for the off-chain
'BTC Yield' pool metadata record (id 67e542004191822941f9e703, linked from Core's
2025-05-02 blog post). Introspection is disabled, so field names are discovered via
Apollo's 'Did you mean' suggestions."""
import json, sys, urllib.request, re
URL = "https://api.maple.finance/v2/graphql"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def gql(q):
    req = urllib.request.Request(URL, data=json.dumps({"query": q}).encode(), headers={"content-type": "application/json", "User-Agent": UA})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        return json.load(e)
def probe(typeq, fields):
    ok, sugg = [], set()
    for f in fields:
        d = gql(typeq % f)
        if 'errors' not in d:
            ok.append(f)
        else:
            for e in d['errors']:
                m = e['message']
                if 'must have a selection' in m or 'of type' in m and 'must have' in m:
                    ok.append(f + ' {..}')
                for s in re.findall(r'"([A-Za-z_0-9]+)"', m.split('Did you mean')[1]) if 'Did you mean' in m else []:
                    sugg.add(s)
    return ok, sugg
if __name__ == '__main__':
    PID = "67e542004191822941f9e703"
    base = '{ poolMeta(id: "%s") { %%s } }' % PID
    cands = sys.argv[1:] or []
    ok, sugg = probe(base, cands)
    print('OK:', ok); print('SUGG:', sorted(sugg))
