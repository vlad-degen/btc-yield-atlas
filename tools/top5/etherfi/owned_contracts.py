# contracts whose ownership was transferred to the vault (ITB position managers etc.)
import lib,time
ev=lib.load('vault_topic_logs_dedup.json'); names=lib.load('event_names.json')
V='5f46d540b6ed704c3c8789105f30e075aa900726'
own=set(l['address'] for l in ev if (names.get(l['topics'][0]) or '').startswith('OwnershipTransfer') and l['topics'][-1].endswith(V))
own|={'0x11fd9e49c41738b7500748f7b94b4dbb0e8c13d2','0x7aaf9539b7359470def1920ca41b5aaa05c13726','0xfbca329e2ee0c44d8f115a4b8f7ceda9e109f436'}
res={}
for a in sorted(own):
    try: d=lib.get('https://eth.blockscout.com/api/v2/addresses/'+a); nm=d.get('name'); cr=d.get('creator_address_hash')
    except Exception: nm=cr=None
    time.sleep(1)
    vals={}
    for sig in ['owner()','loanManager()','yieldStrategy()','pendingOwner()']:
        r=lib.c(a,sig); vals[sig]=lib.a(r) if r and r!='0x' else None
    res[a]={'name':nm,'creator':cr,**vals}
lib.save('owned_contracts.json',res)
