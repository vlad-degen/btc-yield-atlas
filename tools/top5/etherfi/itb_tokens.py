import lib,collections
own=lib.load('owned_contracts.json')
T=lib.topic('Transfer(address,address,uint256)')
allmeta=lib.load('tokens_meta.json')
res={}
for a,info in own.items():
    A='0x'+lib.enc_addr(a)
    out=lib.logs(None,[T,A],23000000,26030000,step=1000000)
    inn=lib.logs(None,[T,None,A],23000000,26030000,step=1000000)
    toks=collections.Counter()
    for l in out+inn:
        if len(l['topics'])==3: toks[l['address']]+=1
    res[a]={'out':out,'in':inn}
    print(a,info['name'],len(out),len(inn))
    for t,cn in toks.items():
        if t not in allmeta:
            allmeta[t]={'symbol':lib.s(lib.c(t,'symbol()')),'decimals':lib.u(lib.c(t,'decimals()')),'name':lib.s(lib.c(t,'name()'))}
        print('   ',t,allmeta[t]['symbol'],cn, 'bal_now',(lib.bal(t,a) or 0)/10**(allmeta[t]['decimals'] or 18))
lib.save('itb_transfers.json',res); lib.save('tokens_meta_all.json',allmeta)
