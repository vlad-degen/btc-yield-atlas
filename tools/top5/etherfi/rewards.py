import lib,collections,json,bisect
MERKL='0x3ef3d8ba38ebe18db133cec108f4d14ce00dd9ae'
URD='0x330eefa8a787552dc5cad3c3ca644844b1e61ddb'
own=lib.load('owned_contracts.json')
users=['0x5f46d540b6eD704C3c8789105F30E075AA900726']+list(own.keys())
C=lib.topic('Claimed(address,address,uint256)')
rows=[]
for u in users:
    U='0x'+lib.enc_addr(u)
    for dist in [MERKL,URD]:
        for tp in ([C,U],[C,None,U]):
            try: lg=lib.logs(dist,tp,21189184,'latest',step=2000000)
            except Exception as e: print('err',e); lg=[]
            for l in lg:
                rows.append((int(l['blockNumber'],16),dist,u,l['topics'],l['data'],l['transactionHash']))
seen=set(); out=[]
meta={}
for b,dist,u,t,d,tx in sorted(rows):
    if (tx,d,tuple(t)) in seen: continue
    seen.add((tx,d,tuple(t)))
    vals=[int(d[2+i:2+i+64],16) for i in range(0,len(d)-2,64)]
    if dist==MERKL:  # Claimed(user indexed, token indexed, amount)
        user=t[1][-40:]; tok='0x'+t[2][-40:]; amt=vals[0]
    else:  # URD Claimed(account indexed, reward indexed, amount)
        user=t[1][-40:]; tok='0x'+t[2][-40:]; amt=vals[0]
    if tok not in meta: meta[tok]=(lib.s(lib.c(tok,'symbol()')),lib.u(lib.c(tok,'decimals()')) or 18)
    s,dec=meta[tok]
    ts=int(lib.rpc('eth_getBlockByNumber',[hex(b),False])['timestamp'],16)
    out.append({'block':b,'date':lib.dt(ts),'dist':'merkl' if dist==MERKL else 'morpho-urd','user':'0x'+user,'token':s,'amount':amt/10**dec,'tx':tx})
    print(lib.dt(ts),'merkl' if dist==MERKL else 'urd','0x'+user[:8],s,round(amt/10**dec,4))
lib.save('reward_claims.json',out)
agg=collections.defaultdict(float)
for r in out: agg[(r['token'],r['user'][:10])]+=r['amount']
print(dict(agg))
