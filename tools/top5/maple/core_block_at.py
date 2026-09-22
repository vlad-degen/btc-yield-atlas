#!/usr/bin/env python3
"""Binary-search the Core block number for a UTC date via rpc.coredao.org."""
import json, sys, urllib.request, datetime
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def rpc(method, params):
    req = urllib.request.Request("https://rpc.coredao.org", data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"content-type": "application/json", "User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=30))["result"]
def ts(n): return int(rpc("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)
def block_at(t):
    hi = int(rpc("eth_blockNumber", []), 16); lo = 1
    while lo < hi:
        mid = (lo + hi) // 2
        if ts(mid) < t: lo = mid + 1
        else: hi = mid
    return lo
if __name__ == "__main__":
    for d in sys.argv[1:]:
        t = int(datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).timestamp())
        print(d, block_at(t))
