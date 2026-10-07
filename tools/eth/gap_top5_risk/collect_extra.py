"""Extra fixed-block reads: Chainlink SAVUSD/AVUSD exchange-rate feed (Avant destination) at month-ends, T and T-30d;
Liquid's balance in Paypal USD Main V2 at T. Output raw extra_raw.json"""
import json
from glib import *
FEED = '0x9fbb7d07ae32b3f75c2a5805c2153243a2532589'
out = {'savusd_feed': FEED, 'savusd': []}
for m, ts, b in months() + [('T-30d', 1788393599, 25893051)]:
    x = batch([c(FEED, 'latestRoundData()', '', b)], tag='savusd')[0]
    out['savusd'].append({'period': m, 'block': b, 'raw': x, 'rate': words(x)[1] / 1e18 if x else None, 'updatedAt': words(x)[3] if x else None})
L = '0xf0bb20865277abd641a307ece5ee04e79073416c'; PUM = '0xb576765fb15505433af24fee2c0325895c559fb2'
r = batch([c(PUM, 'balanceOf(address)', enc_addr(L)), c(PUM, 'totalAssets()'), c(PUM, 'totalSupply()')], tag='pum')
out['paypalUsdMainV2'] = {'address': PUM, 'liquidShares': words(r[0])[0] / 1e18, 'totalAssets': words(r[1])[0] / 1e6, 'totalSupply': words(r[2])[0] / 1e18}
json.dump(out, open(RAW / 'extra_raw.json', 'w'), indent=1)
print(out['paypalUsdMainV2'], out['savusd'][-3:])
