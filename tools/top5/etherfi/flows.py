import lib,sys,collections
meta=lib.load('tokens_meta.json')
V='5f46d540b6ed704c3c8789105f30e075aa900726'
out=lib.load('vault_erc20_out.json'); inn=lib.load('vault_erc20_in.json')
b0,b1=int(sys.argv[1]),int(sys.argv[2])
minamt=float(sys.argv[3]) if len(sys.argv)>3 else 0.5
rows=[]
for l,d in [(x,'OUT') for x in out]+[(x,'IN ') for x in inn]:
    if len(l['topics'])!=3: continue
    b=int(l['blockNumber'],16)
    if not(b0<=b<=b1): continue
    t=l['address'].lower(); m=meta.get(t,{}); dec=m.get('decimals') or 18
    amt=int(l['data'],16)/10**dec
    if amt<minamt: continue
    cp=l['topics'][2][-40:] if d=='OUT' else l['topics'][1][-40:]
    rows.append((b,d,m.get('symbol'),round(amt,4),'0x'+cp,l['transactionHash'][:12]))
for r in sorted(rows): print(*r)
