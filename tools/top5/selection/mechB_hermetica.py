import json, urllib.request
H={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'}
D='SP1S1HSFH0SQQGWKB69EYFNY0B1MHRMGXR3J1FH4D'
def ro(fn, c='state-hbtc-v1', args=[]):
    req=urllib.request.Request(f'https://api.hiro.so/v2/contracts/call-read/{D}/{c}/{fn}', data=json.dumps({'sender':D,'arguments':args}).encode(), headers=H)
    r=json.load(urllib.request.urlopen(req, timeout=40))
    return r
def dec(h):
    # minimal clarity decode for uint/bool/ok wrappers
    b=bytes.fromhex(h[2:])
    def p(i):
        t=b[i]
        if t==1: return int.from_bytes(b[i+1:i+17],'big'), i+17
        if t==0: return int.from_bytes(b[i+1:i+17],'big',signed=True), i+17
        if t==3: return True,i+1
        if t==4: return False,i+1
        if t==7: v,j=p(i+1); return ('ok',v),j
        if t==8: v,j=p(i+1); return ('err',v),j
        if t==9: return None,i+1
        if t==10: v,j=p(i+1); return ('some',v),j
        if t==12:
            n=int.from_bytes(b[i+1:i+5],'big'); j=i+5; out={}
            for _ in range(n):
                l=b[j]; k=b[j+1:j+1+l].decode(); j+=1+l; v,j=p(j); out[k]=v
            return out,j
        if t==6 or t==5:
            return b[i:i+60].hex(), len(b)
        return ('type',t,b[i:i+40].hex()), len(b)
    return p(0)[0]
for fn in ['get-share-price','get-total-assets','get-net-assets','get-deposit-enabled','get-redeem-enabled','get-vault-enabled','get-deposit-cap','get-trading-enabled','get-deposit-state','get-redeem-state']:
    try:
        r=ro(fn); print(fn, dec(r['result']) if r.get('okay') else r)
    except Exception as e: print(fn,'ERR',e)
