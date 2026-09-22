"""Sentora V2 cap history (IncreaseAbsoluteCap / DecreaseAbsoluteCap) for RLUSD Main and Paypal USD Main, via eth_getLogs.
Cap ids are keccak(idData); idData embeds market params, so kBTC-market caps are recognised by the kBTC address in idData.
Output raw/v2_cap_events.json"""
import json, os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
import klib
from klib import topic, words
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
V = {'senRLUSDv2': ('0x6dC58a0FdfC8D694e571DC59B9A52EEEa780E6bf', 24587448, 18), 'senPYUSDmain': ('0xb576765fB15505433aF24FEe2c0325895C559FB2', 24025034, 6),
     'senPYUSDPRIMEv2': ('0xC21b08C16458202593D4D9B26b9984Ee67b38BbD', 24900000, 6)}
EV = {topic('IncreaseAbsoluteCap(bytes32,bytes,uint256)'): 'IncreaseAbsoluteCap', topic('DecreaseAbsoluteCap(address,bytes32,bytes,uint256)'): 'DecreaseAbsoluteCap',
      topic('IncreaseRelativeCap(bytes32,bytes,uint256)'): 'IncreaseRelativeCap', topic('SetPerformanceFee(uint256)'): 'SetPerformanceFee',
      topic('SetManagementFee(uint256)'): 'SetManagementFee', topic('SetForceDeallocatePenalty(address,uint256)'): 'SetForceDeallocatePenalty'}
URL = 'https://mainnet.gateway.tenderly.co'
END = 26029000
def fetch(args):
    addr, b = args
    for t in range(8):
        r = klib._post(URL, {'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{'address': addr, 'fromBlock': hex(b), 'toBlock': hex(min(END, b + 49999)), 'topics': [list(EV)]}]})
        if isinstance(r, dict) and 'result' in r: return r['result']
        klib.time.sleep(2 + t)
    raise RuntimeError(str(r)[:200])
out = []
for name, (addr, start, dec) in V.items():
    with cf.ThreadPoolExecutor(2) as ex:
        for res in ex.map(fetch, [(addr, b) for b in range(start, END, 50000)]):
            for l in res:
                ev = EV[l['topics'][0]]; data = l['data'][2:]
                w = words(l['data'])
                rec = dict(vault=name, block=int(l['blockNumber'], 16), event=ev, tx=l['transactionHash'])
                if 'AbsoluteCap' in ev or 'RelativeCap' in ev:
                    rec['newCap'] = w[1] / 10 ** dec if 'Absolute' in ev else w[1] / 1e18
                    rec['kbtc'] = '73e0c0d45e048d25fc26fa3159b0aa04bfa4db98' in data.lower()
                    rec['prime'] = '19ebb35279a16207ec4ba82799cc64715065f7f6' in data.lower()
                    rec['collateral_cap'] = 'collateralToken' in bytes.fromhex(data[256:]).decode('latin-1', 'ignore') if len(data) > 256 else None
                    rec['tag'] = bytes.fromhex(data).decode('latin-1', 'ignore').replace('\x00', '')[:80]
                else:
                    rec['value'] = w[-1]
                out.append(rec)
json.dump(out, open(os.path.join(RAW, 'v2_cap_events.json'), 'w'), indent=1)
for r in out:
    if r.get('kbtc') or r.get('prime') or 'Fee' in r['event'] or 'Penalty' in r['event']:
        print(r['vault'], r['block'], r['event'], r.get('newCap'), r.get('value'), 'kbtc' if r.get('kbtc') else '', 'prime' if r.get('prime') else '', repr(r.get('tag', ''))[:60])
print(len(out))
