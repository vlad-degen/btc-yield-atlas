import json,glob,datetime,sys
for f in sys.argv[1:]:
    d=json.load(open(f))
    print('==',d.get('name'))
    for chain,v in d.get('chainTvls',{}).items():
        t=v.get('tokens') or []
        tu=v.get('tokensInUsd') or []
        tv=v.get('tvl') or []
        if not tv: continue
        last=tv[-1]
        if last['totalLiquidityUSD']<1000: continue
        s=f"  {chain}: tvl={last['totalLiquidityUSD']:.0f} @ {datetime.datetime.utcfromtimestamp(last['date']).date()}"
        if t:
            s+=' tokens='+str({k:round(x,3) for k,x in t[-1]['tokens'].items() if x})
        if tu:
            s+=' usd='+str({k:round(x) for k,x in tu[-1]['tokens'].items() if x>1000})
        print(s)
