import sys,json
from addrinfo import getjson,BS
def holdings(chain,addr,minusd=50000):
    j=getjson(BS[chain]+'/api/v2/addresses/%s/tokens?type=ERC-20'%addr)
    out=[]
    for it in j.get('items',[]):
        t=it['token']; dec=int(t.get('decimals') or 18); v=int(it['value'])/10**dec
        px=float(t.get('exchange_rate') or 0); usd=v*px
        out.append((t.get('symbol'),t.get('name'),round(v,4),round(usd),t.get('address_hash') or t.get('address')))
    return out
if __name__=='__main__':
    ch=int(sys.argv[1])
    for a in sys.argv[2:]:
        print('==',a)
        for h in holdings(ch,a):
            if h[3]>1000 or h[3]==0: print('  ',h)
