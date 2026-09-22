# Address classification helpers: eth_getCode (EOA / contract / EIP-7702 delegated), Blockscout names, Safe owners/threshold, EIP-1967 impl
import json, urllib.request, time
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
RPC={1:'https://ethereum-rpc.publicnode.com',8453:'https://base-rpc.publicnode.com',42161:'https://arbitrum-one-rpc.publicnode.com',
     747474:'https://rpc.katana.network',143:'https://rpc.monad.xyz',5042:'https://rpc.mainnet.arc.io',999:'https://rpc.hyperliquid.xyz/evm',
     2818:'https://rpc.morphl2.io',4217:'https://rpc.mainnet.tempo.xyz',480:'https://worldchain-mainnet.g.alchemy.com/public',10:'https://optimism-rpc.publicnode.com',
     137:'https://polygon-bor-rpc.publicnode.com',57073:'https://rpc-gel.inkonchain.com',43114:'https://avalanche-c-chain-rpc.publicnode.com',56:'https://bsc-rpc.publicnode.com'}
BS={1:'https://eth.blockscout.com',8453:'https://base.blockscout.com',42161:'https://arbitrum.blockscout.com',10:'https://optimism.blockscout.com',
    57073:'https://explorer.inkonchain.com',2818:'https://explorer.morphl2.io',747474:'https://explorer.katanarpc.com',137:'https://polygon.blockscout.com'}
ALT={'https://ethereum-rpc.publicnode.com':['https://gateway.tenderly.co/public/mainnet','https://eth.drpc.org'],
     'https://base-rpc.publicnode.com':['https://gateway.tenderly.co/public/base','https://base.drpc.org'],
     'https://arbitrum-one-rpc.publicnode.com':['https://gateway.tenderly.co/public/arbitrum','https://arbitrum.drpc.org']}
def post(url,payload,retries=8):
    body=json.dumps(payload).encode(); urls=[url]+ALT.get(url,[])
    for i in range(retries):
        u=urls[i%len(urls)]
        try:
            req=urllib.request.Request(u,data=body,headers={'content-type':'application/json','user-agent':UA})
            return json.load(urllib.request.urlopen(req,timeout=60))
        except Exception as e:
            time.sleep(1.5*(i+1)); last=e
    raise Exception('rpc failed %s %s'%(url,last))
def rpc(chain,method,params):
    r=post(RPC[chain],{'jsonrpc':'2.0','id':1,'method':method,'params':params})
    if 'error' in r: raise Exception(str(r['error']))
    return r['result']
def ecall(chain,to,data,block='latest'):
    try: return rpc(chain,'eth_call',[{'to':to,'data':data},block])
    except Exception as e: return None
def getjson(url,retries=8):
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={'user-agent':UA,'accept':'application/json'})
            return json.load(urllib.request.urlopen(req,timeout=60))
        except Exception as e:
            last=e; time.sleep(min(30,3*(i+1)))
    print('WARN getjson failed',url[:120],last,flush=True)
    return {'_error':str(last)}
def kind(chain,addr):
    code=rpc(chain,'eth_getCode',[addr,'latest'])
    if code in ('0x',None,''): return 'EOA',code
    if code.startswith('0xef0100'): return 'EIP7702-EOA(delegate 0x'+code[8:48]+')',code
    return 'contract',code
SAFE_THR='0xe75235b8'; SAFE_OWN='0xa0e67e2b'
def safe_info(chain,addr):
    t=ecall(chain,addr,SAFE_THR); o=ecall(chain,addr,SAFE_OWN)
    if not t or t=='0x' or not o or len(o)<130: return None
    h=o[2:]; n=int(h[64:128],16); owners=['0x'+h[128+64*i+24:128+64*(i+1)] for i in range(n)]
    return {'threshold':int(t,16),'owners':owners}
def bs_info(chain,addr):
    if chain not in BS: return {}
    j=getjson(BS[chain]+'/api/v2/addresses/'+addr)
    if '_error' in j: return {'bs_error':j['_error'][:80]}
    impl=[(i.get('name'),i.get('address_hash') or i.get('address')) for i in (j.get('implementations') or [])]
    tags=[t.get('display_name') for t in (j.get('public_tags') or [])]
    meta=j.get('metadata') or {}
    mtags=[t.get('name') for t in (meta.get('tags') or [])] if isinstance(meta,dict) else []
    return {'bs_name':j.get('name'),'bs_contract':j.get('is_contract'),'impl':impl,'tags':tags+mtags,'proxy':j.get('proxy_type'),'ens':j.get('ens_domain_name'),'creator':j.get('creator_address_hash')}
def dec_str(h):
    if not h or h=='0x': return None
    h=h[2:]
    try:
        if len(h)==64: return bytes.fromhex(h).rstrip(b'\0').decode()
        off=int(h[:64],16)*2; ln=int(h[off:off+64],16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors='replace')
    except Exception: return None
def name_of(chain,addr):
    return dec_str(ecall(chain,addr,'0x06fdde03'))
def owner_of(chain,addr):
    r=ecall(chain,addr,'0x8da5cb5b')
    return '0x'+r[-40:] if r and len(r)>=66 else None
def classify(chain,addr):
    k,code=kind(chain,addr)
    d={'chain':chain,'addr':addr,'kind':k,'codelen':(len(code)-2)//2 if code else 0}
    if k=='contract':
        s=safe_info(chain,addr)
        if s: d['safe']=s
        d['name()']=name_of(chain,addr); d['owner()']=owner_of(chain,addr)
    d.update(bs_info(chain,addr))
    return d
