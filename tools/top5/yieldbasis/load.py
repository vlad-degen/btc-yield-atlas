import json,datetime,collections
R='../raw/api/'
NAMES={0:'v1-WBTC',1:'v1-cbBTC',2:'v1-tBTC',3:'v2-WBTC',4:'v2-cbBTC',5:'v2-tBTC',6:'v1-WETH',7:'v3-WBTC',8:'v3-cbBTC',9:'v3-tBTC',10:'v3-WETH'}
def day(t): return datetime.datetime.fromtimestamp(t,datetime.UTC).strftime('%Y-%m-%d')
def snaps():
    d=json.load(open(R+'market_snapshots.json'))['data']
    by=collections.defaultdict(dict)
    for r in d:
        dec=r['assetDecimals']
        pps=int(r['ppsRaw'])/1e18
        wd=int(r['withdrawableRaw'])/10**dec if r['withdrawableRaw'] else None
        spps=int(r['stakedPpsRaw'])/1e18 if r['stakedPpsRaw'] else None
        swd=int(r['stakedWithdrawableRaw'])/10**dec if r['stakedWithdrawableRaw'] else None
        by[int(r['marketId'])][day(r['bucketStart'])]=dict(pps=pps,wd=wd,spps=spps,swd=swd,tot=int(r['liquidityTotalAssetRaw'])/1e18,px=int(r['assetPriceUsdRaw'])/1e18,admin_usd=int(r['adminFeesUsdRaw'] or 0)/1e18,pend_usd=int(r['pendingFeesUsdRaw'] or 0)/1e18,crv=(int(r['crvUsdBalanceRaw'])/1e18 if r['crvUsdBalanceRaw'] else None),ast=(int(r['assetBalanceRaw'])/10**dec if r['assetBalanceRaw'] else None),blk=r['sampleBlockNumber'],ts=r['sampleBlockTimestamp'])
    return by
def series(name,key):
    d=json.load(open(R+name+'.json'))['data']
    by=collections.defaultdict(dict)
    for r in d: by[int(r['marketId'])][day(r['bucketStart'])]=r
    return by
