#!/usr/bin/env python3
"""Pull all normal transactions for given Core addresses via scan.coredao.org's public web API
(POST /api/chain/address_transaction) and summarise large CORE value transfers."""
import json, sys, urllib.request, datetime, collections, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
H = {"content-type": "application/json", "User-Agent": UA, "Origin": "https://scan.coredao.org", "Referer": "https://scan.coredao.org/"}
def post(path, body):
    req = urllib.request.Request("https://scan.coredao.org" + path, data=json.dumps(body).encode(), headers=H)
    return json.load(urllib.request.urlopen(req, timeout=60))
out = []
for a in sys.argv[2:]:
    p = 1
    while True:
        d = post("/api/chain/address_transaction", {"addressHash": a, "pageNum": p, "pageSize": 100})
        recs = d["data"]["records"]
        for r in recs:
            out.append({k: r.get(k) for k in ("hash", "blockNumber", "fromHash", "toHash", "value", "status", "method", "timestamp", "createTime")} | {"addr": a})
        if len(recs) < 100: break
        p += 1; time.sleep(0.3)
json.dump(out, open(sys.argv[1], "w"))
print(len(out))
