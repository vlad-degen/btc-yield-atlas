# Yield Basis BTC markets: depositor value in BTC via LT.pricePerShare()*totalSupply, and staked share
import json,sys
import addrinfo; addrinfo.RPC[1]='https://gateway.tenderly.co/public/mainnet'
from addrinfo import ecall
from Crypto.Hash import keccak
def sel(s): k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def u(h): return int(h[2:66],16)
BLK=sys.argv[1]
rows=json.load(open('../raw/yb/yb_markets_%s.json'%BLK))
tot=0; totphys=0; totdebt=0
for r in rows:
    if 'BTC' not in r['asset'].upper(): continue
    pps=u(ecall(1,r['lt'],sel('pricePerShare()'),BLK))/1e18
    sup=u(ecall(1,r['lt'],sel('totalSupply()'),BLK))/1e18
    staker=ecall(1,r['lt'],sel('staker()'),BLK); staker='0x'+staker[-40:]
    st=u(ecall(1,r['lt'],sel('balanceOf(address)')+staker[2:].rjust(64,'0'),BLK))/1e18 if int(staker,16) else 0
    v=pps*sup; r['value_btc_pps']=v; r['staked_frac']=st/sup if sup else 0
    tot+=v; totphys+=r['btc_attrib']; totdebt+=r['debt_crvusd']
    print(f"{r['i']} {r['asset']:6} {r['lt']} pps={pps:.4f} supply={sup:.2f} value={v:.2f} BTC-eq  physBTC={r['btc_attrib']:.2f} debt={r['debt_crvusd']/1e6:.2f}M staked={st/sup*100 if sup else 0:.1f}%")
print(f'TOTAL BTC markets: depositor value {tot:.1f} BTC-eq; physical BTC in pools {totphys:.1f}; crvUSD debt {totdebt/1e6:.2f}M')
json.dump(rows,open('../raw/yb/yb_markets_%s.json'%BLK,'w'),indent=1)
