import json, sys
from rpc import *
BLK = sys.argv[1] if len(sys.argv)>1 else 'latest'
M='0xad10d07901dc3195c3cb5e78e061f4ea8d9b4905'
MID='37d156e96a4230c1fe9545579086e4b40d08b4aae8b3c78ee91031f2a22c1a5c'
V='0x85a1d961f1d1bbd9b4a6d96106c5bf9ae91f0510'
G='0x9131eb40bd0bdce73c72755f1bb2cf39a9453341'
AD='0x2214a206b3647523c6aeca1dc91b8824a7108e62'
BG='0x31011317764e097b28d159a8145b92bfa453f606'
USDC='0xcfb1186f4e93d60e60a8bdd997427d1f33bc372b'
PFC='0x89963ff339c4a6194ea77381c204884e4503f8fb'
PROV='0x047623636f1c7997f5b49ecaadb865681734d89a'
ORA='0x22b3d92703ee73af5e31a6ba56cca2fdced6c412'
IRM='0xfb69467de332e03ff502b85bb2249d2f721f3319'
FEED='0xb81131b6368b3f0a83af09db4e39ac23da96c2db'
out={}
def w(r): h=r[2:]; return [int(h[i:i+64],16) for i in range(0,len(h),64)]
def c(to,sig,args=''): return ca(to,sig,args,BLK)
# Morpho market
out['marketParams']=[dec_addr(c(M,'idToMarketParams(bytes32)',MID),i) for i in range(4)]+[dec_uint(c(M,'idToMarketParams(bytes32)',MID),4)/1e18]
mk=w(c(M,'market(bytes32)',MID)); out['market']=dict(zip(['totalSupplyAssets','totalSupplyShares','totalBorrowAssets','totalBorrowShares','lastUpdate','fee'],mk))
for who,n in [(V,'aera'),(AD,'adapter')]:
    p=w(c(M,'position(bytes32,address)',MID+enc_addr(who)))
    out['pos_'+n]=dict(zip(['supplyShares','borrowShares','collateral'],p))
out['oracle_price']=dec_uint(c(ORA,'price()'))
out['oracle_scale']=dec_uint(c(ORA,'SCALE_FACTOR()'))
out['oracle_feeds']=[dec_addr(c(ORA,s)) for s in ['BASE_FEED_1()','BASE_FEED_2()','QUOTE_FEED_1()','QUOTE_FEED_2()','BASE_VAULT()','QUOTE_VAULT()']]
out['rateAtTarget']=dec_uint(c(IRM,'rateAtTarget(bytes32)',MID))
# borrowRateView(marketParams, market)
mp=c(M,'idToMarketParams(bytes32)',MID)[2:]
mkraw=c(M,'market(bytes32)',MID)[2:]
out['borrowRateView']=dec_uint(c(IRM,'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))',mp+mkraw))
# feed
try:
    out['feed_desc']=dec_str(c(FEED,'description()'))
    lr=w(c(FEED,'latestRoundData()')); out['feed_latest']=lr; out['feed_decimals']=dec_uint(c(FEED,'decimals()'))
    out['feed_id']=c(FEED,'getDataFeedId()')
except Exception as e: out['feed_err']=str(e)
# gtusdc
g={}
for s,t in [('name()','s'),('symbol()','s'),('asset()','a'),('decimals()','u'),('totalAssets()','u'),('_totalAssets()','u'),('totalSupply()','u'),('owner()','a'),('curator()','a'),('adaptersLength()','u'),('liquidityAdapter()','a'),('performanceFee()','u'),('performanceFeeRecipient()','a'),('managementFee()','u'),('managementFeeRecipient()','a'),('maxRate()','u'),('virtualShares()','u'),('adapterRegistry()','a'),('receiveSharesGate()','a'),('sendSharesGate()','a'),('receiveAssetsGate()','a'),('sendAssetsGate()','a'),('lastUpdate()','u'),('firstTotalAssets()','u')]:
    try:
        r=c(G,s); g[s]=dec_str(r) if t=='s' else dec_uint(r) if t=='u' else dec_addr(r)
    except Exception as e: g[s]='ERR '+str(e)[:80]
g['adapters']=[dec_addr(c(G,'adapters(uint256)',enc_uint(i))) for i in range(g['adaptersLength()'])]
g['balance_aera']=dec_uint(c(G,'balanceOf(address)',enc_addr(V)))
g['convertToAssets_1e18']=dec_uint(c(G,'convertToAssets(uint256)',enc_uint(10**18)))
g['usdc_idle']=dec_uint(c(USDC,'balanceOf(address)',enc_addr(G)))
g['liquidityData']=c(G,'liquidityData()')
out['gtusdc']=g
# adapter
out['adapter_realAssets']=dec_uint(c(AD,'realAssets()'))
out['adapter_marketIdsLength']=dec_uint(c(AD,'marketIdsLength()'))
out['adapter_marketIds']=[c(AD,'marketIds(uint256)',enc_uint(i)) for i in range(out['adapter_marketIdsLength'])]
# Aera
a={}
a['totalSupply']=dec_uint(c(V,'totalSupply()'))
a['bgbtc_idle']=dec_uint(c(BG,'balanceOf(address)',enc_addr(V)))
a['usdc_idle']=dec_uint(c(USDC,'balanceOf(address)',enc_addr(V)))
try: a['vaultState']=w(c(PFC,'getVaultState(address)',enc_addr(V)))
except Exception as e: a['vaultState']='ERR '+str(e)[:100]
try: a['unitsToToken_1e18']=dec_uint(c(PFC,'convertUnitsToToken(address,address,uint256)',enc_addr(V)+enc_addr(BG)+enc_uint(10**18)))
except Exception as e: a['unitsToToken_1e18']='ERR '+str(e)[:100]
try: a['vaultAccountant']=dec_addr(c(PFC,'vaultAccountant(address)',enc_addr(V)))
except Exception as e: a['vaultAccountant']='ERR'
try: a['valueAtLastUpdate']=dec_uint(c(PFC,'getVaultValueAtLastUpdate(address)',enc_addr(V)))
except Exception as e: a['valueAtLastUpdate']='ERR'
try: a['priceTs']=dec_uint(c(PFC,'getVaultPriceTimestamp(address)',enc_addr(V)))
except Exception as e: a['priceTs']='ERR'
for s in ['NUMERAIRE()','owner()','protocolFeeRecipient()','ORACLE_REGISTRY()']:
    try: a['pfc_'+s]=dec_addr(c(PFC,s))
    except Exception as e: a['pfc_'+s]='ERR'
try: a['pfc_protocolFees']=w(c(PFC,'protocolFees()'))
except Exception as e: a['pfc_protocolFees']='ERR'
for s,t in [('depositCap()','u'),('depositRefundTimeout()','u'),('maxDeposit()','u'),('owner()','a'),('solvingGate()','a'),('getRelevantAmount()','u')]:
    try: r=c(PROV,s); a['prov_'+s]=dec_uint(r) if t=='u' else dec_addr(r)
    except Exception as e: a['prov_'+s]='ERR '+str(e)[:60]
for s in ['getSyncRedeemDetails()','getCancellationDetails()','getSyncRedeemEpochState()']:
    try: a['prov_'+s]=w(c(PROV,s))
    except Exception as e: a['prov_'+s]='ERR '+str(e)[:60]
try: a['prov_tokensDetails_bgbtc']=w(c(PROV,'tokensDetails(address)',enc_addr(BG)))
except Exception as e: a['prov_tokensDetails_bgbtc']='ERR '+str(e)[:60]
out['aera']=a
out['bgbtc_totalSupply_morph']=dec_uint(c(BG,'totalSupply()'))
out['block']=BLK
print(json.dumps(out,indent=1))
