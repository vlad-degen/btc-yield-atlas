"""Identify River vault depositors: code type, Safe owners, where their BTC-wrapper came from (mechA).
Base via Blockscout token-transfers; BOB via RPC getLogs on uniBTC Transfer(to=holder). Output raw/mechA/river_identify.json"""
import sys,json,urllib.request,time; sys.path.insert(0,'.')
from mechA_rpc import *
RPCS.update({'bob':'https://rpc.gobob.xyz'})
def get(url):
    for i in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60))
        except Exception as e: last=e; time.sleep(2)
    return {'error':str(last)}
def kind(ch,a_):
    code=rpc(ch,'eth_getCode',[a_,'latest'])
    if len(code)<=2: return 'EOA',None
    if code.startswith('0xef0100'): return 'EOA+7702('+'0x'+code[8:48]+')',None
    ow=c(ch,a_,'getOwners()'); th=u(c(ch,a_,'getThreshold()'))
    if ow and not ow.startswith('ERR'):
        w=words(ow); n=int(w[1],16); return 'Safe %s-of-%d'%(th,n),['0x'+w[2+i][24:] for i in range(n)]
    return 'contract(len %d)'%len(code),None
TR='0x'+k256(b'Transfer(address,address,uint256)').hex()
def bob_in(token,holder,frm=20_000_000):
    head=int(rpc('bob','eth_blockNumber',[]),16); out=[]; b=frm; step=2_000_000
    while b<=head:
        e=min(b+step-1,head)
        r=post(RPCS['bob'],{'jsonrpc':'2.0','id':1,'method':'eth_getLogs','params':[{'address':token,'topics':[TR,None,'0x'+holder[2:].lower().rjust(64,'0')],'fromBlock':hex(b),'toBlock':hex(e)}]})
        if 'error' in r: step//=4; continue
        out+=r['result']; b=e+1
    return [(int(l['blockNumber'],16),'0x'+l['topics'][1][-40:],int(l['data'],16)/1e8,l['transactionHash']) for l in out]
HOLD={'base':['0xc652551a8430A81F5F1A22bFD917b13aC13e56bF','0x183B1c4480FAe0A3eb9601451dA4D2AC13d0A748','0x21579F32Bf0d81a457796891B59911F79A9DB126','0x2B4bB93f1934d53555867D7cBE546ad7e730b802','0xcDBcf2D91e2A7E1A9306C86fF94b502cf6877a41','0x317d2da746d1360F4c113E7962a33394DB2A1A4e'],
      'bob':['0xb9c0eb31d5393c91efbe027e031041072883ce90','0xaf44d5ea9852e6281e7719c8e3f344dd2a2c4a31','0x0b8e10cdc6d00520c16629dd30e6f6c6a597ab0c','0xda96616d8005a6ffb776afcbcfb40d3bbdcd8eeb','0x317d2da746d1360f4c113e7962a33394db2a1a4e']}
if __name__=='__main__':
    out={}
    for ch,hs in HOLD.items():
        for h in hs:
            k,owners=kind(ch,h); o={'chain':ch,'holder':h,'kind':k,'owners':owners}
            if ch=='base':
                d=get(f'https://base.blockscout.com/api/v2/addresses/{h}/token-transfers?type=ERC-20')
                o['erc20_transfers']=[(x['timestamp'][:10],x['token']['symbol'],x['from']['hash'],x['from'].get('name'),x['to']['hash'],int(x['total']['value'])/10**int(x['token']['decimals'] or 0)) for x in d.get('items',[])][:25]
                t=get(f'https://base.blockscout.com/api/v2/addresses/{h}/transactions')
                o['txs']=[(x['timestamp'][:10],x['from']['hash'],(x['to'] or {}).get('hash'),x.get('method'),int(x['value'])/1e18) for x in t.get('items',[])][:15]
            else:
                o['uniBTC_in']=bob_in('0x236f8c0a61da474db21b693fb2ea7aab0c803894',h)
            out[h]=o
            print('==',ch,h,k,owners)
            for key in ('erc20_transfers','txs','uniBTC_in'):
                for r in (o.get(key) or [])[:12]: print('   ',key,r)
    json.dump(out,open('../raw/mechA/river_identify.json','w'),indent=1)
