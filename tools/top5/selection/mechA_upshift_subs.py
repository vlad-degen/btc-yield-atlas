import sys,json
sys.path.insert(0,'.')
from mechA_morpho_user import user
subs=sys.argv[2].split(',')
chain=int(sys.argv[1])
out={}
for a in subs:
    r=user(a,chain)
    if isinstance(r,str): print(a,r); continue
    u=(r.get('data') or {}).get('userByAddress')
    if not u: continue
    mp=[p for p in u['marketPositions'] if (p['state']['collateralUsd'] or 0)>1000 or (p['state']['borrowAssetsUsd'] or 0)>1000 or (p['state']['supplyAssetsUsd'] or 0)>1000]
    vp=[p for p in u['vaultPositions'] if (p['state']['assetsUsd'] or 0)>1000]
    if mp or vp:
        out[a]={'markets':mp,'vaults':vp}
        print(a)
        for p in mp: print('   M', p['market']['collateralAsset'] and p['market']['collateralAsset']['symbol'],'/',p['market']['loanAsset']['symbol'], p['market']['marketId'][:12], 'coll',p['state']['collateral'],'collUsd',round(p['state']['collateralUsd'] or 0),'borUsd',round(p['state']['borrowAssetsUsd'] or 0),'supUsd',round(p['state']['supplyAssetsUsd'] or 0))
        for p in vp: print('   V', p['vault']['name'], p['vault']['address'], round(p['state']['assetsUsd']))
json.dump(out,open(sys.argv[3],'w'),indent=1)
