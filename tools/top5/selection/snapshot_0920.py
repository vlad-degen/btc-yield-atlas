# Re-read Bitget (Morph), mHyperBTC (Morpho+Spark), Upshift Sentora BTC legs at 2026-09-20 12:00 UTC where archive RPC allows
import addrinfo; addrinfo.RPC[1]='https://gateway.tenderly.co/public/mainnet'
from addrinfo import ecall
from blockat import block_at
T=1789905600
def words(h): h=h[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
# Bitget on Morph
bm=block_at(2818,T)
MORPHO='0xad10d07901dc3195c3cb5e78e061f4ea8d9b4905'; MKT='37d156e96a4230c1fe9545579086e4b40d08b4aae8b3c78ee91031f2a22c1a5c'; AERA='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'
try:
    p=words(ecall(2818,MORPHO,'0x93c52062'+MKT+AERA[2:].rjust(64,'0'),hex(bm))); m=words(ecall(2818,MORPHO,'0x5c60e39a'+MKT,hex(bm)))
    print('Bitget @Morph block',bm,'bgBTC',p[2]/1e8,'USDC debt',p[1]*m[2]/m[3]/1e6)
except Exception as e: print('Bitget hist failed',e)
# Ethereum Morpho Blue positions
B=hex(26018582); MB='0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
def mpos(mkt,user,cd=8,ld=6):
    p=words(ecall(1,MB,'0x93c52062'+mkt[2:]+user[2:].lower().rjust(64,'0'),B)); m=words(ecall(1,MB,'0x5c60e39a'+mkt[2:],B))
    return p[2]/10**cd, (p[1]*m[2]/m[3] if m[3] else 0)/10**ld
print('mHyperBTC Morpho cbBTC/USDT', mpos('0x4fe72543c5c95cd6b5f3cb516cd235ba882e2e705fe3424db6f99dfe5811d0d3','0x933adedd85824da75ec8a334a7907e69e7c02833'))
SP='0xC13e21B648A5Ee794902342038FF3aDAB66BE987'
u='0x933adedd85824da75ec8a334a7907e69e7c02833'
print('mHyperBTC Spark spcbBTC',int(ecall(1,'0xb3973D459df38ae57797811F2A1fd061DA1BC123','0x70a08231'+u[2:].rjust(64,'0'),B),16)/1e8)
w=words(ecall(1,SP,'0xbf92857c'+u[2:].rjust(64,'0'),B)); print('mHyperBTC Spark debt $%.2fM'%(w[1]/1e14))
K=[('0x15bb2a6af0c909eed19fb1f2ceeead34ecbdcba626de752c6b09389ee14eec32','0x0774b5B15B0CEe5E2e14814CCF4d4611fF78CcF5',18),('0x15bb2a6af0c909eed19fb1f2ceeead34ecbdcba626de752c6b09389ee14eec32','0x7fB9f8F775e3Ff458ce5D9d146f36e9e4639205E',18),
   ('0xe51f9aaad25d0e755429cf77076b3c2d37cb1228ed81f8a5482f2102c220eef5','0xd18DF3c05D2D11BDeDBd9F7501f651e43b9bd986',6),('0xe51f9aaad25d0e755429cf77076b3c2d37cb1228ed81f8a5482f2102c220eef5','0x1E8f4752209A50eFE5b6126f5c534dC7018d9489',6),
   ('0xa921ef34e2fc7a27ccc50ae7e4b154e16c9799d3387076c421423ef52ac4df99','0x5EE1E2e3540eFCE54Fc477d6648537e07080f884',6)]
tc=td=0
for mk,us,ld in K:
    c,d=mpos(mk,us,8,ld); tc+=c; td+=d; print('Kraken leg',us[:10],round(c,2),round(d/1e6,2))
AV='0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'; KA='0xF523259262979a26095474974b56443AD34c53B7'
aw=int(ecall(1,'0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8','0x70a08231'+KA[2:].lower().rjust(64,'0'),B),16)/1e8
w=words(ecall(1,AV,'0xbf92857c'+KA[2:].lower().rjust(64,'0'),B))
print('Kraken Aave',aw,'WBTC debt $%.2fM'%(w[1]/1e14)); print('Kraken total BTC posted',round(tc+aw,2),'debt $%.2fM'%(td/1e6+w[1]/1e14))
