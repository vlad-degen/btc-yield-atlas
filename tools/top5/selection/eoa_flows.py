# Light check of large EOA borrowers: counterparties of recent stablecoin/BTC transfers (Blockscout names), to see if any is a product wallet
import sys, collections
from addrinfo import getjson
def flows(ch,addr,pages=3):
    base={1:'https://eth.blockscout.com',8453:'https://base.blockscout.com'}[ch]
    url=base+'/api/v2/addresses/%s/token-transfers?type=ERC-20'%addr; nxt=None; items=[]
    for p in range(pages):
        import urllib.parse
        j=getjson(url+('&'+urllib.parse.urlencode(nxt) if nxt else ''))
        items+=j.get('items',[]); nxt=j.get('next_page_params')
        if not nxt: break
    c=collections.defaultdict(float); first=last=None
    for t in items:
        tok=t['token']; v=int(t['total']['value'] or 0)/10**int(tok.get('decimals') or 18)
        fr=t['from']; to=t['to']
        other=to if fr['hash'].lower()==addr.lower() else fr
        d='out' if fr['hash'].lower()==addr.lower() else 'in'
        nm=other.get('name') or (other.get('ens_domain_name')) or other['hash'][:12]
        c[(d,tok['symbol'],nm,other['hash'][:12],other.get('is_contract'))]+=v
        last=last or t['timestamp']; first=t['timestamp']
    print('==',addr,'transfers',len(items),'from',first,'to',last)
    for k,v in sorted(c.items(),key=lambda kv:-kv[1])[:12]: print('   ',k,round(v,2))
if __name__=='__main__':
    ch=int(sys.argv[1])
    for a in sys.argv[2:]: flows(ch,a)
