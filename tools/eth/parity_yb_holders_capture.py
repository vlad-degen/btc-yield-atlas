"""Read-only LT transfer discovery and archived balances, with reconciliation."""
import sys,json,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/eth'))
import strategy_universe_deep_capture as c
c.RAW=ROOT/'raw/eth/parity-sweep-2026-10-05';A=c.CONTRACTS['yb_weth']
h=json.loads((c.RAW/'yb_monthly_frozen.json').read_text())['records']
start=max(r['block'] for r in h if r['method']=='eth_getCode' and r['response'].get('result')=='0x')+1
rows=[]
topic='0x'+c.keccak(b'Transfer(address,address,uint256)').hex()
for b in range(start,c.BLOCK+1,50000):rows.append({'label':'yb_transfers_'+str(b),'method':'eth_getLogs','params':[{'address':A,'fromBlock':hex(b),'toBlock':hex(min(b+49999,c.BLOCK)),'topics':[topic]}]})
old=json.loads((c.RAW/'yb_LT_transfer_history_tenderly.json').read_text())['records'];cached={r['label']:r for r in old if 'result' in r['response']}
def one(r):return cached.get(r['label']) or c.rpc(r['label']+'_single',[r],url='https://gateway.tenderly.co/public/mainnet')[0]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:records=list(executor.map(one,rows))
(c.RAW/'yb_LT_transfer_history_complete.json').write_text(json.dumps({'financialTimestamp':c.T,'records':records},indent=2)+'\n')
if any('result' not in r['response'] for r in records):raise RuntimeError('Incomplete transfer history; no holder claim is produced')
addresses=set()
for r in records:
 for log in r['response']['result']:
  for t in log['topics'][1:3]:
   a='0x'+t[-40:]
   if int(a,16):addresses.add(a)
rows=[c.call('yb_LT_balance_'+a,A,'balanceOf(address)',c.enc_addr(a)) for a in sorted(addresses)]
balances=c.rpc('yb_LT_holder_balances_T',rows)
if any('result' not in r['response'] for r in balances):raise RuntimeError('Incomplete archived balances; no holder count is produced')
p=json.loads((ROOT/'data/eth/strategy_universe_deep.json').read_text());pool=next(p for p in p['products'] if p['id']=='yb_weth_pool')
positive=[{'address':r['label'].removeprefix('yb_LT_balance_'),'shares':int(r['response']['result'],16)/1e18} for r in balances if int(r['response']['result'],16)>0]
positive.sort(key=lambda r:-r['shares']);total=sum(r['shares'] for r in positive);expected=pool['shareSupply']
result={'timestamp':c.T,'contract':A,'addresses':positive,'holderCount':len(positive),'totalShares':total,'expectedShares':expected,'reconciled':abs(total-expected)<1e-7,'scope':'Direct LT holding addresses, including the gauge and contracts; not gauge beneficiaries or unique investors','sourcePaths':['raw/eth/parity-sweep-2026-10-05/yb_LT_transfer_history_complete.json','raw/eth/parity-sweep-2026-10-05/yb_LT_holder_balances_T.json']}
(ROOT/'data/eth/yb_LT_holders_T.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:result[k] for k in ['holderCount','totalShares','expectedShares','reconciled']})
if not result['reconciled']:raise RuntimeError('LT balances do not reconcile; displayed count must remain unverified')
