"""List holders of River SmartVault share tokens via Blockscout (Base, BOB, Ethereum, Hemi) and
classify each holder (EOA/Safe/contract, name, creator, first funding). Output raw/mechA/river_holders.json"""
import sys,json,urllib.request,time
BS={'base':'https://base.blockscout.com','bob':'https://explorer.gobob.xyz','eth':'https://eth.blockscout.com','hemi':'https://explorer.hemi.xyz'}
VAULTS={'base':['0xCe07D2B5CC6Ff466BF497ceEa8eD168fB0Eb8F97','0xd72dCb68fF80aB8666f7A800BE438212581914c6'],
        'bob':['0xEdE84f536448cC822a9318548Aa8618183743c4f','0xd62E2F6b6616271001DCd0988AD2D73DEeE1b491','0x4f4EbFAeEa78d7ebc13c4aAb481fd8E36D9DC1Be'],
        'eth':['0xDd7eCb0dc1686020A8a23EE55126D7596a2eA03b','0x11054D3584F94B542379Ff4Cf9e7897D50AE8317']}
def get(url):
    for i in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60))
        except Exception as e: last=e; time.sleep(2)
    return {'error':str(last)}
def classify(ch,addr):
    d=get(f"{BS[ch]}/api/v2/addresses/{addr}")
    o={'address':addr,'is_contract':d.get('is_contract'),'name':d.get('name'),'ens':d.get('ens_domain_name'),
       'public_tags':[t.get('display_name') for t in (d.get('public_tags') or [])],'creator':d.get('creator_address_hash'),
       'creation_tx':d.get('creation_transaction_hash') or d.get('creation_tx_hash'),'implementations':d.get('implementations')}
    if d.get('is_contract'):
        sc=get(f"{BS[ch]}/api/v2/smart-contracts/{addr}")
        o['contract_name']=sc.get('name')
        if (sc.get('name') or '').lower().startswith(('gnosissafe','safeproxy')):
            owners=None
    return o
def holders(ch,v):
    d=get(f"{BS[ch]}/api/v2/tokens/{v}/holders")
    return [(x['address']['hash'],int(x['value'])/1e18) for x in d.get('items',[])]
def transfers(ch,v):
    d=get(f"{BS[ch]}/api/v2/tokens/{v}/transfers")
    return [(x['timestamp'],x['from']['hash'],x['to']['hash'],int(x['total']['value'])/1e18,x['transaction_hash']) for x in d.get('items',[])]
if __name__=='__main__':
    out={}
    for ch,vs in VAULTS.items():
        for v in vs:
            H=holders(ch,v); T=transfers(ch,v)
            out[v]={'chain':ch,'holders':[],'transfers':T}
            print('==',ch,v)
            for h,bal in H:
                c=classify(ch,h); c['shares']=bal; out[v]['holders'].append(c)
                print('  holder',h,round(bal,6),c['is_contract'],c.get('contract_name') or c.get('name'),c['public_tags'],'creator',c['creator'])
            for t in T[:12]: print('  xfer',t)
    json.dump(out,open('../raw/mechA/river_holders.json','w'),indent=1)
