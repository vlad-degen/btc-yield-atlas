#!/usr/bin/env python3
"""Pull logs from Core RPC in chunks. Usage: core_logs.py <address> <topic0> <fromBlock> <toBlock> <chunk> <out.jsonl>"""
import json, sys, urllib.request, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def rpc(method, params):
    req = urllib.request.Request("https://rpc.coredao.org", data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"content-type": "application/json", "User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))
addr, topic, fb, tb, chunk, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
n = 0
with open(out, "w") as f:
    b = fb
    while b <= tb:
        e = min(b + chunk - 1, tb)
        for attempt in range(4):
            try:
                r = rpc("eth_getLogs", [{"address": addr, "fromBlock": hex(b), "toBlock": hex(e), "topics": [[topic]]}])
                break
            except Exception as ex:
                time.sleep(2); r = {"error": str(ex)}
        if "error" in r:
            # shrink chunk on error
            if chunk > 5000:
                chunk //= 2; continue
            print("ERR", b, e, r["error"], file=sys.stderr); b = e + 1; continue
        for lg in r["result"]:
            f.write(json.dumps(lg) + "\n"); n += 1
        b = e + 1
print("logs", n)
