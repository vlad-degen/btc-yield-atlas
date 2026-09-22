import json, urllib.request, urllib.parse, time
BS='https://explorer-api.morphl2.io'
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
def get(path, params=None, retries=6):
    url=BS+path+('?'+urllib.parse.urlencode(params) if params else '')
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={'user-agent':UA,'accept':'application/json'})
            return json.load(urllib.request.urlopen(req,timeout=90))
        except Exception as e:
            print('bs exc',url[:150],e); time.sleep(3*(i+1))
    raise Exception('bs failed '+url)
def v2_all(path, params=None, maxpages=200):
    params=dict(params or {}); out=[]
    for _ in range(maxpages):
        r=get(path,params); out+=r.get('items',[])
        n=r.get('next_page_params')
        if not n: break
        params.update(n)
    return out
def getlogs(address, fromBlock=0, toBlock='latest', **topics):
    """etherscan-compatible logs on Blockscout: ascending, max 1000 per call; page forward"""
    out=[]; fb=fromBlock
    while True:
        p={'module':'logs','action':'getLogs','address':address,'fromBlock':fb,'toBlock':toBlock}
        p.update(topics)
        r=get('/api',p)
        res=r.get('result') or []
        if not isinstance(res,list): print(r); break
        if len(res)<1000:
            out+=res; break
        last=int(res[-1]['blockNumber'],16)
        if int(res[0]['blockNumber'],16)==last: raise Exception('>1000 logs in one block')
        out+=[x for x in res if int(x['blockNumber'],16)<last]
        fb=last
    seen=set(); ded=[]
    for x in out:
        k=(x['transactionHash'],x['logIndex'])
        if k in seen: continue
        seen.add(k); ded.append(x)
    return ded

def getlogs_w(address, fromBlock, toBlock, **topics):
    """windowed: split block range until each window returns <1000 logs (robust to Blockscout ordering)"""
    p={'module':'logs','action':'getLogs','address':address,'fromBlock':fromBlock,'toBlock':toBlock}
    p.update(topics)
    r=get('/api',p); res=r.get('result') or []
    if not isinstance(res,list): print(r); return []
    if len(res)<1000: return res
    mid=(fromBlock+toBlock)//2
    return getlogs_w(address,fromBlock,mid,**topics)+getlogs_w(address,mid+1,toBlock,**topics)
