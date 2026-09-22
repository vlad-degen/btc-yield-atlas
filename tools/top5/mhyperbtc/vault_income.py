# Income of the dollar (and BTC) vault positions: daily position assetsUsd x vault share-price growth (Morpho API), monthly
import json,urllib.request,time,datetime,collections
def gql(q,v=None):
    for i in range(4):
        req=urllib.request.Request('https://api.morpho.org/graphql',data=json.dumps({'query':q,'variables':v or {}}).encode(),headers={'content-type':'application/json','user-agent':'Mozilla/5.0'})
        try: return json.load(urllib.request.urlopen(req,timeout=120))
        except urllib.error.HTTPError as e: err=e.read()[:1500].decode()
        except Exception as e: err=str(e)
        time.sleep(3)
    return {'errors':err}
S,E=1761955200,1790035200; opt='{startTimestamp:%d,endTimestamp:%d,interval:DAY}'%(S,E)
mp=json.load(open('raw/morpho_pos_history.json'))
def dayof(x): return datetime.datetime.fromtimestamp(int(x),datetime.UTC).strftime('%Y-%m-%d')
sp={}
for kind in ('v2','v1'):
    for k,v in mp[kind].items():
        c,a=k.split(':')
        if kind=='v2': q='query($a:String!,$c:Int!){vaultV2ByAddress(address:$a,chainId:$c){historicalState{sharePrice(options:%s){x y}}}}'%opt
        else: q='query($a:String!,$c:Int!){vaultByAddress(address:$a,chainId:$c){historicalState{sharePriceNumber(options:%s){x y}}}}'%opt
        r=gql(q,{'a':a,'c':int(c)})
        try:
            h=(r['data'].get('vaultV2ByAddress') or r['data'].get('vaultByAddress'))['historicalState']
            ser=h.get('sharePrice') or h.get('sharePriceNumber')
            sp[k]={dayof(p['x']):float(p['y']) for p in ser if p['y'] is not None}
        except Exception as e: print('fail',k,v['vault']['name'],str(r)[:200]); sp[k]={}
json.dump(sp,open('raw/vault_shareprice.json','w'))
inc=collections.defaultdict(lambda:collections.defaultdict(float))
for kind in ('v2','v1'):
    for k,v in mp[kind].items():
        name=v['vault']['name']; h=v['hist']['data']
        h=(h.get('vaultV2PositionByAddress') or {}).get('history') if 'vaultV2PositionByAddress' in h else (h.get('vaultPosition') or {}).get('historicalState')
        pos={dayof(p['x']):float(p['y'] or 0) for p in (h or {}).get('assetsUsd') or []}
        s=sp.get(k,{})
        for d,val in pos.items():
            if val<1000: continue
            d1=(datetime.date.fromisoformat(d)+datetime.timedelta(days=1)).isoformat()
            if d in s and d1 in s and s[d]>0:
                g=s[d1]/s[d]-1
                if abs(g)<0.01:
                    leg='btc' if 'cbBTC' in name else 'usd'
                    inc[d[:7]][leg+'_income']+=val*g; inc[d[:7]][leg+'_assetdays']+=val
json.dump(inc,open('raw/vault_income_monthly.json','w'),indent=0)
for m in sorted(inc):
    r=inc[m]
    print(m,'USD vaults: avg $%.2fM, income $%.0f (%.2f%% APR) | BTC vaults avg $%.2fM income $%.0f (%.2f%%)'%(r['usd_assetdays']/30/1e6,r['usd_income'],100*365*r['usd_income']/r['usd_assetdays'] if r['usd_assetdays'] else 0,r['btc_assetdays']/30/1e6,r['btc_income'],100*365*r['btc_income']/r['btc_assetdays'] if r['btc_assetdays'] else 0))
