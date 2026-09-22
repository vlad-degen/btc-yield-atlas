import json, urllib.request, sys
RPCS={'mezo':'https://rpc-http.mezo.boar.network','ethereum':'https://ethereum-rpc.publicnode.com','base':'https://base-rpc.publicnode.com','optimism':'https://optimism-rpc.publicnode.com',
'arbitrum':'https://arbitrum-one-rpc.publicnode.com','bsc':'https://bsc-rpc.publicnode.com','sonic':'https://rpc.soniclabs.com','berachain':'https://rpc.berachain.com',
'bob':'https://rpc.gobob.xyz','ink':'https://rpc-gel.inkonchain.com','scroll':'https://rpc.scroll.io','mezo':'https://rpc-http.mezo.boar.network'}
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'}
def rpc(chain, method, params):
    req=urllib.request.Request(RPCS.get(chain,chain), data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(), headers=UA)
    r=json.load(urllib.request.urlopen(req, timeout=30))
    if 'error' in r: raise Exception(r['error'])
    return r['result']
def call(chain, to, data, block='latest'):
    return rpc(chain,'eth_call',[{'to':to,'data':data},block])
SEL={'totalSupply':'0x18160ddd','decimals':'0x313ce567','symbol':'0x95d89b41','getRate':'0x679aefce','name':'0x06fdde03','asset':'0x38d52e0f','totalAssets':'0x01e1d114'}
def u(chain,to,fn):
    r=call(chain,to,SEL[fn]); return int(r,16) if r and r!='0x' else None
def bal(chain, token, holder):
    r=call(chain,token,'0x70a08231'+holder[2:].lower().rjust(64,'0')); return int(r,16)
def s(chain,to,fn='symbol'):
    r=call(chain,to,SEL[fn])
    try:
        b=bytes.fromhex(r[2:]); 
        if len(b)>=96:
            l=int.from_bytes(b[32:64],'big'); return b[64:64+l].decode(errors='ignore')
        return b.rstrip(b'\0').decode(errors='ignore')
    except Exception as e: return r
