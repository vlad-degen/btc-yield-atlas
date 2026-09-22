# Yield Basis: per market BTC deposited (asset share of Curve pool owned by LEVAMM), crvUSD debt, allocation; crvUSD source
import json,sys
from addrinfo import ecall, rpc, dec_str, getjson
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return '0x'+k.hexdigest()[:8]
def u(h,i=0): h=h[2:]; return int(h[64*i:64*(i+1)],16)
def a(h,i=0): h=h[2:]; return '0x'+h[64*i+24:64*(i+1)]
import addrinfo; addrinfo.RPC[1]='https://gateway.tenderly.co/public/mainnet'
C=1; FACT='0x370a449FeBb9411c95bf897021377fe0B7D100c0'; CRVUSD='0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E'
BLK=sys.argv[1] if len(sys.argv)>1 else 'latest'
def call(to,sig,args='',blk=None): return ecall(C,to,sel(sig)+args,blk or BLK)
def bal(tok,who): return u(call(tok,'balanceOf(address)',who[2:].lower().rjust(64,'0')))
n=u(call(FACT,'market_count()'))
print('block',BLK,'markets',n,'stablecoin',a(call(FACT,'STABLECOIN()')),'mint_factory',a(call(FACT,'mint_factory()')),'admin',a(call(FACT,'admin()')))
rows=[]
for i in range(n):
    m=call(FACT,'markets(uint256)',hex(i)[2:].rjust(64,'0'))
    asset,pool,amm,lt=a(m,0),a(m,1),a(m,2),a(m,3)
    sym=dec_str(call(asset,'symbol()')); dec=u(call(asset,'decimals()'))
    lpbal=bal(pool,amm); lpsup=u(call(pool,'totalSupply()'))
    share=lpbal/lpsup if lpsup else 0
    asset_in_pool=bal(asset,pool)/10**dec; crv_in_pool=bal(CRVUSD,pool)/1e18
    debt=u(call(amm,'get_debt()'))/1e18
    alloc=u(call(lt,'stablecoin_allocation()'))/1e18; allocd=u(call(lt,'stablecoin_allocated()'))/1e18
    ltcrv=bal(CRVUSD,lt)/1e18; ammcrv=bal(CRVUSD,amm)/1e18
    killed=u(call(amm,'is_killed()'))
    ltname=dec_str(call(lt,'symbol()')); ltsup=u(call(lt,'totalSupply()'))/1e18
    p=call(pool,'price_oracle()'); po=u(p)/1e18 if p else None
    r=dict(i=i,asset=sym,pool=pool,amm=amm,lt=lt,lt_sym=ltname,btc_attrib=asset_in_pool*share,crvusd_in_lp_attrib=crv_in_pool*share,debt_crvusd=debt,
           lp_share=share,stablecoin_allocation=alloc,stablecoin_allocated=allocd,lt_crvusd_idle=ltcrv,amm_killed=killed,lt_supply=ltsup,price_oracle=po)
    rows.append(r)
    print(f"{i} {sym:6} {ltname:10} lt={lt} amm={amm} share={share:.3f} asset={r['btc_attrib']:.2f} crvUSDinLP={r['crvusd_in_lp_attrib']/1e6:.2f}M debt={debt/1e6:.2f}M alloc={alloc/1e6:.1f}M allocated={allocd/1e6:.1f}M idle={ltcrv/1e6:.2f}M killed={killed} p={po}")
json.dump(rows,open('../raw/yb/yb_markets_%s.json'%BLK,'w'),indent=1)
btc=[r for r in rows if 'BTC' in (r['asset'] or '').upper()]
print('BTC markets total asset',sum(r['btc_attrib'] for r in btc),'debt',sum(r['debt_crvusd'] for r in btc)/1e6,'M')
# crvUSD mint factory debt ceiling for YB factory
mf=a(call(FACT,'mint_factory()'))
for sig in ['debt_ceiling(address)','debt_ceiling_residual(address)']:
    try: print(sig, u(call(mf,sig,FACT[2:].lower().rjust(64,'0')))/1e18)
    except Exception as e: print(sig,'err',e)
print('crvUSD balance of factory',bal(CRVUSD,FACT)/1e18)
# Depositor value: LT preview_withdraw(totalSupply) in asset units (BTC) per BTC market
tot=0
for r in btc:
    sup=u(call(r['lt'],'totalSupply()'))
    if sup==0: continue
    pw=call(r['lt'],'preview_withdraw(uint256)',hex(sup)[2:].rjust(64,'0'))
    dec=u(call(ecall(C,r['lt'],sel('ASSET_TOKEN()'),BLK) and a(call(r['lt'],'ASSET_TOKEN()')),'decimals()'))
    v=u(pw)/10**dec if pw else None
    r['depositor_value_btc']=v; tot+=v or 0
    print(r['i'],r['asset'],'LT supply',sup/1e18,'preview_withdraw(all)',v)
print('TOTAL BTC depositor value (preview_withdraw)',tot)
json.dump(rows,open('../raw/yb/yb_markets_%s.json'%BLK,'w'),indent=1)
