import sys, json, urllib.request, time
BS={'Ethereum':'https://eth.blockscout.com','Base':'https://base.blockscout.com','Arbitrum One':'https://arbitrum.blockscout.com','Monad':None,'Arc':None,'World Chain':'https://worldchain-mainnet.explorer.alchemy.com'}
def info(chain, a):
    base=BS.get(chain)
    if not base: return None
    req=urllib.request.Request(f"{base}/api/v2/addresses/{a}", headers={'User-Agent':'Mozilla/5.0'})
    try: d=json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e: return {'err':str(e)}
    tags=[t.get('name') or t.get('display_name') for t in ((d.get('metadata') or {}).get('tags') or [])]
    impl=[i.get('name') for i in (d.get('implementations') or [])]
    return {'is_contract':d.get('is_contract'),'name':d.get('name'),'impl':impl,'ens':d.get('ens_domain_name'),'tags':tags,'proxy':d.get('proxy_type')}
if __name__=='__main__':
    res=json.load(open('../raw/mechB/morpho_btc_top_borrowers.json'))
    seen={}
    out=[]
    for ch,mk,a,_,b,c in res:
        if b<1.5e6 or ch not in ('Ethereum','Base','Arbitrum One') : continue
        k=(ch,a)
        if k not in seen:
            seen[k]=info(ch,a); time.sleep(0.3)
        out.append((ch,mk,a,round(b/1e6,2),seen[k]))
        print(ch,mk,a,round(b/1e6,2),seen[k])
    json.dump(out, open('../raw/mechB/morpho_btc_top_borrowers_info.json','w'))
