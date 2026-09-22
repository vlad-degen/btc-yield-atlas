#!/usr/bin/env python3
"""Pull logs for a contract + topic0 filtered by indexed address in topic position N (1..3).
Usage: core_logs_by_addr.py <contract> <topic0> <pos> <addr1,addr2,...> <from> <to> <chunk> <out.jsonl>"""
import json, sys, urllib.request, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def rpc(method, params):
    req = urllib.request.Request("https://rpc.coredao.org", data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"content-type": "application/json", "User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))
c, t0, pos, addrs, fb, tb, chunk, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4].split(','), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), sys.argv[8]
topics = [[t0]] + [None] * (pos - 1) + [["0x" + "0" * 24 + a.lower()[2:] for a in addrs]]
n = 0
with open(out, "w") as f:
    b = fb
    while b <= tb:
        e = min(b + chunk - 1, tb)
        try:
            r = rpc("eth_getLogs", [{"address": c, "fromBlock": hex(b), "toBlock": hex(e), "topics": topics}])
        except Exception as ex:
            r = {"error": str(ex)}
        if "error" in r:
            if chunk > 5000: chunk //= 2; continue
            print("ERR", b, e, r["error"], file=sys.stderr); b = e + 1; continue
        for lg in r["result"]: f.write(json.dumps(lg) + "\n"); n += 1
        b = e + 1
print("logs", n)
