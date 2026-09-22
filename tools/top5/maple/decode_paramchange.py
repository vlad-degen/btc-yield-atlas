#!/usr/bin/env python3
"""Decode Core paramChange(string key, bytes value) logs; for key 'grades' decode the tier table
(value encoding per BitcoinAgent.updateParam: uint8 length followed by (uint32 stakeRate, uint32 percentage) pairs,
per the contract source). Block timestamps fetched from RPC."""
import json, sys, urllib.request, datetime
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def rpc(method, params):
    req = urllib.request.Request("https://rpc.coredao.org", data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"content-type": "application/json", "User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))["result"]
for line in open(sys.argv[1]):
    lg = json.loads(line)
    d = bytes.fromhex(lg["data"][2:])
    ko = int.from_bytes(d[0:32], "big"); vo = int.from_bytes(d[32:64], "big")
    kl = int.from_bytes(d[ko:ko+32], "big"); key = d[ko+32:ko+32+kl].decode()
    vl = int.from_bytes(d[vo:vo+32], "big"); val = d[vo+32:vo+32+vl]
    bn = int(lg["blockNumber"], 16)
    ts = int(rpc("eth_getBlockByNumber", [hex(bn), False])["timestamp"], 16)
    dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    print(dt, bn, key, val.hex(), lg["transactionHash"])
