# Bitget bgBTC Onchain Earn: read Aera vault position in Morpho (Morph chain) via RPC
from addrinfo import ecall, rpc, name_of
MORPHO='0xad10d07901dc3195c3cb5e78e061f4ea8d9b4905'
MKT='37d156e96a4230c1fe9545579086e4b40d08b4aae8b3c78ee91031f2a22c1a5c'
AERA='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'
CH=2818
def words(h): h=h[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
p=words(ecall(CH,MORPHO,'0x93c52062'+MKT+AERA[2:].rjust(64,'0')))
m=words(ecall(CH,MORPHO,'0x5c60e39a'+MKT))
params=ecall(CH,MORPHO,'0x2c3c9157'+MKT)  # idToMarketParams
w=params[2:]; loan='0x'+w[24:64]; coll='0x'+w[88:128]; oracle='0x'+w[152:192]; lltv=int(w[256:320],16)/1e18
debt=p[1]*m[2]/m[3] if m[3] else 0
print('block',int(rpc(CH,'eth_blockNumber',[]),16))
print('loan',loan,name_of(CH,loan),'coll',coll,name_of(CH,coll),'lltv',lltv)
cd=int(ecall(CH,coll,'0x313ce567'),16); ld=int(ecall(CH,loan,'0x313ce567'),16)
print('Aera collateral',p[2]/10**cd,'debt',debt/10**ld)
print('market totalSupply',m[0]/10**ld,'totalBorrow',m[2]/10**ld,'util',m[2]/m[0])
px=int(ecall(CH,oracle,'0xa035b1fe'),16)  # price() scaled 1e36*loanDec/collDec
price=px/10**(36+ld-cd)
print('oracle price',price,'LTV',debt/10**ld/(p[2]/10**cd*price))
print('bgBTC totalSupply on Morph',int(ecall(CH,coll,'0x18160ddd'),16)/10**cd)
print('Aera name',name_of(CH,AERA))
# idle bgBTC and Gauntlet USDC Prime shares held by the Aera vault
bal=int(ecall(CH,coll,'0x70a08231'+AERA[2:].rjust(64,'0')),16)/10**cd
print('idle bgBTC in Aera vault',bal)
for v in ['0x9131EB40bD0bDcE73c72755f1BB2Cf39a9453341','0x9131a0846B9E5dF90323d7d5eFeA549128F66596']:
    try:
        n=name_of(CH,v); sh=int(ecall(CH,v,'0x70a08231'+AERA[2:].rjust(64,'0')),16); ts=int(ecall(CH,v,'0x18160ddd'),16)
        ta=int(ecall(CH,v,'0x01e1d114'),16); d=int(ecall(CH,v,'0x313ce567'),16)
        print(v,n,'Aera share %.1f%%'%(sh/ts*100),'vault totalAssets',ta/10**6 if d<=18 else ta,'decimals',d, 'Aera assets ~', ta*sh/ts/1e6)
    except Exception as e: print(v,'err',e)
