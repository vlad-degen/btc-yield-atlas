import lib,time,json
addrs={'RolesAuthority owner':'0xcea8039076e35a825854c5c2f85659430b06ec96','role10/11 A':'0x41dfc53b13932a2690c9790527c1967d8579a6ae','role10/11 B':'0x71e2d6c34f569cc4df5802d675b208fb8ae3bcd6',
'role14/16/20':'0x9af1298993dc1f397973c62a5d47a284cf76844d','strategist1':'0x18deea881548a592285d9ba63f0f67dc97e28e99','strategist2':'0x607d0c7e3578802eb46d388cb86cfba8ff657306',
'strategist3':'0xc8111d00351765c64d301cdfc1848bf5ff2e23a2','r14a':'0x13edfc1b04d003c2a142e92fad838b925672b07f','r14b':'0x4a21d84eb5b8bd5254e6a2d0ca11aa64ed1b6b66','r14c':'0x7859baa3e12b6480b15b77b069d8d0279ebc74ea',
'pauser5':'0xe71f8927ab95042b6f7b82e515065d38b0bfaf6c','role100':'0x0551e6700a0c7c5a1633e912710ed80c88facc07','manager':'0xafa8c08bedb2ec1bbeb64a7ffa44c604e7cca68d',
'payout(now)':'0xf6bd950c66869a32170bf26a38c8b7c6d6eca863','payout(2025)':'0x68ec1fdd4bb202b2e07ae751cb5553644aa48cfa','payout(Dec24)':'0xa9962a5bfbea6918e958dee0647e99fd7863b95a',
'solver':'0xed41172438897bcb22c9dd72b9f9bbf9a8bf8929','queue':'0x77a2fd42f8769d8063f2e75061fc200014e41edf','solverEOA':'0xf8553c8552f906c19286f21711721e206ee4909e','solverEOA2':'0xd23086c4e450caaf55704ebc03875a04b4716ca2','solverEOA3':'0xdb8345450b0e4d28514a1c18ee1110c417b5b0a2','ITB deployer':'0x50b37e1cb515110be21a2c91fa3052c413e42737','ITB deployer2':'0x69906e25d9ca08217b654b214132ae4107003f1a'}
out={}
for lab,a in addrs.items():
    code=lib.rpc('eth_getCode',[a,'latest'])
    info={'addr':a,'is_contract':len(code)>2}
    if len(code)>2:
        r=lib.c(a,'getThreshold()'); info['threshold']=lib.u(r) if r and r!='0x' else None
        r=lib.c(a,'getOwners()')
        if r and r!='0x' and len(r)>130:
            h=r[2:]; n=int(h[64:128],16); info['owners']=['0x'+h[128+64*i+24:128+64*(i+1)] for i in range(n)]
        r=lib.c(a,'getMinDelay()'); info['minDelay']=lib.u(r) if r and r!='0x' else None
        r=lib.c(a,'owner()'); info['owner']=lib.a(r) if r and r!='0x' else None
        r=lib.c(a,'manageRoot(address)',lib.enc_addr('0x18deea881548a592285d9ba63f0f67dc97e28e99'))
        if lab=='manager': info['root_strat1']=r
        try:
            d=lib.get('https://eth.blockscout.com/api/v2/addresses/'+a); info['bs_name']=d.get('name'); info['impl']=[x.get('name') for x in d.get('implementations') or []]
            time.sleep(1)
        except Exception as e: pass
    else:
        info['nonce']=int(lib.rpc('eth_getTransactionCount',[a,'latest']),16)
    out[lab]=info
    print(lab,json.dumps(info)[:400])
lib.save('governance.json',out)
