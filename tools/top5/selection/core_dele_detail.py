import json,sys,datetime
logs=json.load(open(sys.argv[1]))['logs']['delegated']
target=sys.argv[2].lower()
B0,T0=18000000,1727301502
def bd(b): return datetime.datetime.fromtimestamp(T0+(b-B0)*3,datetime.timezone.utc).strftime('%Y-%m-%d')
exp={l['topics'][1]:int(l['blockNumber'],16) for l in json.load(open(sys.argv[1]))['logs']['btcExpired']}
def parse_script(h):
    b=bytes.fromhex(h); i=0; ops=[]
    while i<len(b):
        op=b[i]; i+=1
        if 1<=op<=75: ops.append(b[i:i+op].hex()); i+=op
        else: ops.append({0xb1:'CLTV',0x75:'DROP',0xac:'CHECKSIG',0xae:'CHECKMULTISIG',0x76:'DUP',0xa9:'HASH160',0x88:'EQUALVERIFY',0x87:'EQUAL'}.get(op, f'OP_{op:02x}' if not 0x51<=op<=0x60 else f'OP_{op-0x50}'))
    return ops
rows=[]
for l in logs:
    if '0x'+l['topics'][3][-40:]!=target: continue
    data=l['data'][2:]; w=[data[i:i+64] for i in range(0,len(data),64)]
    off=int(w[0],16)//32; ln=int(w[off],16); script=''.join(w[off+1:])[:ln*2]
    amt=int(w[2],16)/1e8
    ops=parse_script(script)
    lt=int.from_bytes(bytes.fromhex(ops[0]),'little') if isinstance(ops[0],str) and len(ops[0])<=10 else None
    ltd=datetime.datetime.fromtimestamp(lt,datetime.timezone.utc).strftime('%Y-%m-%d') if lt and lt>500000000 else lt
    b=int(l['blockNumber'],16)
    txid=l['topics'][1]
    rows.append((b,bd(b),amt,ltd,'0x'+l['topics'][2][-40:],txid, exp.get(txid), ' '.join(o if isinstance(o,str) and len(o)<20 else (o[:10]+'..' if isinstance(o,str) else o) for o in ops[1:])))
rows.sort()
for r in rows: print(r[1], f"{r[2]:9.4f}", 'lock->',r[3], 'cand',r[4][:10],'btctxid(LE?)',r[5][:18], 'expBlk',r[6] and bd(r[6]), '|', r[7])
print('n',len(rows),'sum',sum(r[2] for r in rows))
