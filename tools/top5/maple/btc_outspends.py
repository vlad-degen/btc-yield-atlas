#!/usr/bin/env python3
"""For each Core BTC stake of the Maple-attributed cluster, look up the Bitcoin staking tx on mempool.space
(txid byte-reversed vs the Core event), identify the locked output (value == staked amount), and check whether/when it
was spent and to which addresses. Output: ../raw/core/maple_btc_outspends.csv"""
import csv, json, urllib.request, time, datetime
UA = {'User-Agent': 'Mozilla/5.0'}
def get(u):
    for i in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(5); continue
            raise
        except Exception: time.sleep(2)
    return None
CL = {'0xadfaaa5f085cf52d4fabbdf3181521f1ae9cab7c', '0x74bb2c9ffa90aeb2d3e7b958d418a36ab31acd52', '0xfd818e3544a8a72632ab53324eae6370bbe9bad7', '0x87f34109e4782736b6869daff588626ffb4764d3', '0x2ed725c8ee00fd5a3043bf54716dff85abb29353'}
rows = [r for r in csv.DictReader(open('../raw/core/btc_stakes.csv')) if r['delegator'] in CL and r['block']]
out = []
for r in rows:
    tid = bytes.fromhex(r['txid'][2:])[::-1].hex()
    tx = get(f'https://mempool.space/api/tx/{tid}')
    if not tx: out.append([r['txid'], tid, r['btc'], '', '', '', '', '', '']); continue
    sats = round(float(r['btc']) * 1e8)
    vout = next((i for i, o in enumerate(tx['vout']) if o['value'] == sats), None)
    addr = tx['vout'][vout].get('scriptpubkey_address') if vout is not None else ''
    sp = get(f'https://mempool.space/api/tx/{tid}/outspend/{vout}') if vout is not None else None
    spent = sp.get('spent') if sp else None
    st = sp.get('status', {}).get('block_time') if sp and spent else None
    dest = ''
    if spent:
        stx = get(f"https://mempool.space/api/tx/{sp['txid']}")
        if stx: dest = ';'.join(f"{o.get('scriptpubkey_address')}:{o['value']/1e8}" for o in stx['vout'][:3])
    out.append([r['txid'], tid, r['btc'], datetime.datetime.fromtimestamp(tx['status']['block_time'], datetime.timezone.utc).strftime('%Y-%m-%d') if tx.get('status', {}).get('block_time') else '', addr, spent, datetime.datetime.fromtimestamp(st, datetime.timezone.utc).strftime('%Y-%m-%d') if st else '', sp.get('txid') if sp and spent else '', dest])
    time.sleep(0.25)
with open('../raw/core/maple_btc_outspends.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['core_txid', 'btc_txid', 'btc', 'stake_date_btc', 'lock_address', 'spent', 'spent_date', 'spend_txid', 'spend_outputs'])
    w.writerows(out)
print(len(out))
