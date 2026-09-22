import lib,collections,json
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'.lower()
out=lib.load('vault_erc20_out.json'); inn=lib.load('vault_erc20_in.json')
cnt=collections.defaultdict(lambda:[0,0,10**12,0])
for l,d in [(x,'out') for x in out]+[(x,'in') for x in inn]:
    if len(l['topics'])!=3: continue  # skip ERC721
    t=l['address'].lower(); b=int(l['blockNumber'],16)
    c=cnt[t]; c[0 if d=='in' else 1]+=1; c[2]=min(c[2],b); c[3]=max(c[3],b)
meta={}
for t,c in sorted(cnt.items(),key=lambda x:x[1][2]):
    sym=lib.s(lib.c(t,'symbol()')); dec=lib.u(lib.c(t,'decimals()')); nm=lib.s(lib.c(t,'name()'))
    b=lib.bal(t,V)
    meta[t]={'symbol':sym,'name':nm,'decimals':dec,'in':c[0],'out':c[1],'first':c[2],'last':c[3],'bal_now':b}
    print(t,sym,nm,dec,c,b)
lib.save('tokens_meta.json',meta)
