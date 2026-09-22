import lib,collections
V='0x'+lib.enc_addr('0x5f46d540b6eD704C3c8789105F30E075AA900726')
T=lib.topic('Transfer(address,address,uint256)')
A=lib.topic('Approval(address,address,uint256)')
head=int(lib.rpc('eth_blockNumber',[]),16)
res=[]
for pos in [1,2,3]:
    tp=[None]*pos+[V]
    r=lib.logs(None,tp,21189184,head,step=250000)
    r=[l for l in r if l['topics'][0] not in (T,A)]
    print(pos,len(r)); res+=r
lib.save('vault_topic_logs.json',res)
c=collections.Counter((l['address'],l['topics'][0]) for l in res)
for k,v in c.most_common(): print(k,v)
