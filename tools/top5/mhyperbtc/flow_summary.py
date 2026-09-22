# Summarise ERC-20 flows of a wallet by token and counterparty; only whitelisted real tokens (spam/poisoning filtered)
import json,collections,sys
fn=sys.argv[1]; W=sys.argv[2].lower(); minh=int(sys.argv[3]) if len(sys.argv)>3 else 10
L=json.load(open(fn))
agg=collections.defaultdict(lambda:[0.0,0,None,None])
names={}
for x in L:
    t=x['token']; sym=t.get('symbol') or '?'
    try: hc=int(t.get('holders_count') or 0)
    except: hc=0
    if hc<minh or not sym.isascii(): continue
    try: amt=int(x['total']['value'])/10**int(x['total']['decimals'] or t['decimals'] or 18)
    except: continue
    fr=x['from']['hash'].lower(); to=x['to']['hash'].lower()
    if fr==W: d='OUT'; cp=to; cpo=x['to']
    elif to==W: d='IN'; cp=fr; cpo=x['from']
    else: continue
    names[cp]=(cpo.get('name'), cpo.get('is_contract'))
    k=(sym,d,cp); a=agg[k]; a[0]+=amt; a[1]+=1; ts=x['timestamp'][:10]
    a[2]=min(a[2] or ts,ts); a[3]=max(a[3] or ts,ts)
for (sym,d,cp),(amt,n,f,l) in sorted(agg.items(),key=lambda kv:(kv[0][0],kv[0][1],-kv[1][0])):
    nm,ic=names[cp]
    print(f'{sym:22s} {d:3s} {amt:18,.2f} n={n:4d} {f}..{l} {cp} {"C" if ic else "E"} {nm or ""}')
