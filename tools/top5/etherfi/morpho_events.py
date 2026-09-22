import lib,collections
MB='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
res=lib.load('vault_topic_logs.json'); names=lib.load('event_names.json')
V='0x'+lib.enc_addr('0x5f46d540b6eD704C3c8789105F30E075AA900726')
ev=[l for l in res if l['address']==MB]
ids=collections.defaultdict(list)
for l in sorted(ev,key=lambda x:(int(x['blockNumber'],16),int(x['logIndex'],16))):
    n=names[l['topics'][0]].split('(')[0]; b=int(l['blockNumber'],16)
    ids[l['topics'][1]].append((b,n,l['data'],l['topics']))
mk={}
for i,evs in ids.items():
    p=lib.c(MB,'idToMarketParams(bytes32)',i[2:])
    lt,ct,orc,irm=[lib.a(p,j) for j in range(4)]; lltv=lib.u(p,4)/1e18
    lsym=lib.s(lib.c(lt,'symbol()')); csym=lib.s(lib.c(ct,'symbol()'))
    mk[i]={'loan':lt,'coll':ct,'oracle':orc,'irm':irm,'lltv':lltv,'lsym':lsym,'csym':csym,'ldec':lib.u(lib.c(lt,'decimals()')),'cdec':lib.u(lib.c(ct,'decimals()'))}
    print(i,csym,'/',lsym,lltv,orc,len(evs),evs[0][0],evs[-1][0])
lib.save('morpho_markets.json',mk)
for i,evs in ids.items():
    m=mk[i]
    for b,n,d,t in evs:
        d=d[2:]; vals=[int(d[j:j+64],16) for j in range(0,len(d),64)]
        if n=='SupplyCollateral': amt=vals[-1]/10**m['cdec']; s=f"+coll {amt:.4f} {m['csym']}"
        elif n=='WithdrawCollateral': amt=vals[-1]/10**m['cdec']; s=f"-coll {amt:.4f} {m['csym']}"
        elif n=='Borrow': s=f"+debt {vals[-2]/10**m['ldec']:.2f} {m['lsym']}"
        elif n=='Repay': s=f"-debt {vals[0]/10**m['ldec']:.2f} {m['lsym']}"
        elif n=='Liquidate': s=f"LIQUIDATE caller={t[2][-40:]} borrower={t[3][-40:]} repaid={vals[0]/10**m['ldec']:.2f} seized={vals[2]/10**m['cdec']:.6f} baddebt={vals[3]}"
        else: s=n
        print(b,m['csym'],m['lsym'],s)
