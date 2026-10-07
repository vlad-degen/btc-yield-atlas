"""Destination share prices at T-30d (block 25893051, 2026-09-02 23:59:59 UTC, the study's 30-day start block) for trailing APRs at T."""
import json
from glib import *
from collect_positions import DEST, EARN_ORACLE, USDT, EB_POOL
B30 = 25893051
calls = [c(a, 'convertToAssets(uint256)', enc_uint(10 ** sd), B30) for n, (a, sd, ad) in DEST.items()]
calls += [c(EARN_ORACLE, 'getReport(address)', enc_addr(USDT), B30), c(EB_POOL, 'get_virtual_price()', '', B30), c('0x656341ef90b622c6634e0573772ffb7f3669b9f3', 'get_virtual_price()', '', B30)]
calls += [('0x0', '0x', 0)][:0]
res = batch(calls, tag='dest_30d')
blk = klib.rpc('eth', 'eth_getBlockByNumber', [hex(B30), False])
keys = list(DEST) + ['earnUSD_report', 'curve_ebUSD_USDC_vp', 'yb_lp_vp']
json.dump({'block': B30, 'timestamp': int(blk['timestamp'], 16), 'reads': [{'key': k, 'to': cc[0], 'data': cc[1], 'result': v} for k, cc, v in zip(keys, calls, res)]}, open(RAW / 'dest_30d_raw.json', 'w'), indent=1)
print(int(blk['timestamp'], 16), res)
