import lib,json,sys
chain=sys.argv[1]; src=sys.argv[2]; out=sys.argv[3]
bals=lib.load(src)  # {addr: shares(float) or raw int}
res={}
addrs=[a for a,v in bals.items() if v and v>0]
codes={}
for a in addrs:
    try: codes[a]=lib.rpc('eth_getCode',[a,'latest'],chain)
    except Exception: codes[a]=None
known={'0x77a2fd42f8769d8063f2e75061fc200014e41edf':'Veda BoringOnChainQueue','0xed41172438897bcb22c9dd72b9f9bbf9a8bf8929':'Veda BoringSolver','0x989468982b08aefa46e37cd0086142a86fa466d7':'AtomicSolverV3',
       '0x66753c4e3fc84f1ed0e3c267c927284e9d90c572':'Aave v4 Hub (OP)'}
for a in addrs:
    c=codes[a] or '0x'
    if len(c)<=2: typ='EOA'
    elif c.startswith('0xef0100'): typ='EOA (EIP-7702 smart wallet)'
    else:
        typ='contract'
        thr=lib.c(a,'getThreshold()',chain=chain)
        if thr and thr!='0x' and lib.u(thr): typ='Safe multisig'
    res[a]={'shares':bals[a],'type':known.get(a.lower(),typ),'code_len':(len(c)-2)//2}
lib.save(out,res)
import collections
print(collections.Counter(v['type'] for v in res.values()))
