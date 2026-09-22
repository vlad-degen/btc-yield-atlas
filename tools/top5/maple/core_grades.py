#!/usr/bin/env python3
"""Read Core dual-staking tier table (BitcoinAgent.getGrades / gradeActive) from Core RPC,
at 'latest' and optionally at historical block numbers (needs archive support).
BitcoinAgent system contract: 0x0000000000000000000000000000000000001013.
DualStakingGrade { uint32 stakeRate; uint32 percentage } -- stakeRate is CORE per BTC
(units per docs: CORE:BTC ratio), percentage is in basis points of the max BTC reward (10000=100%)."""
import json, sys, urllib.request
RPC = "https://rpc.coredao.org"
AGENT = "0x0000000000000000000000000000000000001013"
def rpc(method, params):
    req = urllib.request.Request(RPC, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"content-type": "application/json", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"})
    return json.load(urllib.request.urlopen(req, timeout=30))
def call(data, block="latest"):
    r = rpc("eth_call", [{"to": AGENT, "data": data}, block])
    return r.get("result"), r.get("error")
def grades(block="latest"):
    res, err = call("0xb77ea2d7", block)
    if err or not res or res == "0x": return None, err
    b = bytes.fromhex(res[2:])
    n = int.from_bytes(b[32:64], "big")
    out = []
    for i in range(n):
        w = b[64 + 64 * i: 64 + 64 * (i + 1)]
        out.append((int.from_bytes(w[:32], "big"), int.from_bytes(w[32:], "big")))
    return out, None
def active(block="latest"):
    res, err = call("0x1146feb8", block)
    return (int(res, 16) if res and res != "0x" else None), err
if __name__ == "__main__":
    blocks = sys.argv[1:] or ["latest"]
    for bl in blocks:
        blk = bl if bl == "latest" else hex(int(bl))
        g, e = grades(blk); a, e2 = active(blk)
        ts = None
        if bl != "latest":
            bb = rpc("eth_getBlockByNumber", [blk, False]).get("result") or {}
            ts = int(bb.get("timestamp", "0x0"), 16)
        print(json.dumps({"block": bl, "ts": ts, "gradeActive": a, "grades": g, "err": e or e2}))
