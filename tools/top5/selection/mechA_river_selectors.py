"""Compare function selectors of River SmartVault implementations across chains (mechA)."""
import sys,json; sys.path.insert(0,'.')
from mechA_rpc import *
RPCS.update({'bob':'https://rpc.gobob.xyz','bsc':'https://bsc-dataseed.bnbchain.org'})
def selectors(ch,addr):
    code=rpc(ch,'eth_getCode',[addr,'latest'])[2:]
    b=bytes.fromhex(code); out=set(); i=0
    while i<len(b):
        op=b[i]
        if op==0x63 and i+4<len(b): out.add(b[i+1:i+5].hex())
        if 0x60<=op<=0x7f: i+=op-0x5f
        i+=1
    return out,len(b)
impls={'bsc_PV':('bsc','0x248a7de9f2f610f84317472fa83a8ef7d7c8bdf3'),'base_SV':('base','0xd56936bf6c9f877477ccca1602809331d945890c'),'bob_PV_new':('bob','0x78c78d5a33775a7a70f61f9dad08ded8658fc583'),'eth_PV':('eth','0xcc128ed8b4ee7a3c7ed4fc273c8fb7a2d258076d')}
abi=json.load(open('../raw/mechA/river_sv_base_impl.json'))['abi']
names={}
for x in abi:
    if x.get('type')=='function':
        sig=x['name']+'('+','.join(i['type'] if not i['type'].startswith('tuple') else '('+','.join(c['type'] for c in i['components'])+')' for i in x['inputs'])+')'
        names[sel(sig)]=sig
extra=['getMintFactor()','mintFactor()','getMintingFactor()','mintingFactor()','getLTV()','ltv()','getCollateralRatio()','collateralRatio()','debtFactor()','getDebtFactor()','updateMintFactor(uint256)','setMintFactor(uint256)','getMintAmount()','getIdleDebt()','transferDebtToken(address,uint256)']
for e in extra: names[sel(e)]=e
S={k:selectors(*v) for k,v in impls.items()}
for k,(s_,n) in S.items(): print(k,'codesize',n,'selectors',len(s_))
base=S['base_SV'][0]
for k in S:
    if k=='base_SV': continue
    only=S[k][0]-base; missing=base-S[k][0]
    print(k,'extra vs base:',[names.get(x,x) for x in sorted(only)])
    print(k,'missing vs base:',[names.get(x,x) for x in sorted(missing)])
