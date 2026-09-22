import lib
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'
ACC='0xea23ac6d7d11f6b181d6b98174d334478adae6b0'
T=lib.topic('Transfer(address,address,uint256)')
START=21189184
head=int(lib.rpc('eth_blockNumber',[]),16)
print('head',head)
sh=lib.logs(V,None,START,head,step=1000000,verbose=True)
lib.save('vault_all_logs_rpc.json',sh); print('vault logs',len(sh))
acc=lib.logs(ACC,None,START,head,step=1000000,verbose=True)
lib.save('acc_logs_rpc.json',acc); print('acc logs',len(acc))
out=lib.logs(None,[T,'0x'+lib.enc_addr(V)],START,head,step=250000,verbose=True)
inn=lib.logs(None,[T,None,'0x'+lib.enc_addr(V)],START,head,step=250000,verbose=True)
lib.save('vault_erc20_out.json',out); lib.save('vault_erc20_in.json',inn)
print('out',len(out),'in',len(inn))
