# ether.fi Liquid BTC (Veda BoringVault 0x5f46...0726): Spark position + total shares (Ethereum + Optimism) x accountant rate, at 2026-09-20 12:00 UTC
import addrinfo; addrinfo.RPC[1]='https://gateway.tenderly.co/public/mainnet'
from addrinfo import ecall, name_of
from blockat import block_at
V='0x5f46d540b6eD704C3c8789105F30E075AA900726'; SPARK='0xC13e21B648A5Ee794902342038FF3aDAB66BE987'; TELLER='0x8ea0168200bc8554d859bd707a8829588861a068'
T=1789905600; B=hex(26018582)
x=ecall(1,SPARK,'0xbf92857c'+V[2:].lower().rjust(64,'0'),B); h=x[2:]; w=[int(h[i:i+64],16) for i in range(0,len(h),64)]
print('name',name_of(1,V)); print('Spark coll $%.2fM debt $%.2fM HF %.3f'%(w[0]/1e14,w[1]/1e14,w[5]/1e18))
T_={'spWBTC':('0x4197ba364AE6698015AE5c1468f54087602715b2',8),'spcbBTC':('0xb3973D459df38ae57797811F2A1fd061DA1BC123',8),'vdPYUSD':('0x3357D2DB7763D6Cd3a99f0763EbF87e0096D95f9',6),'vdUSDC':('0x7B70D04099CB9cfb1Db7B6820baDAfB4C5C70A67',6)}
for k,(t,d) in T_.items(): print(k,int(ecall(1,t,'0x70a08231'+V[2:].lower().rjust(64,'0'),B),16)/10**d)
acc='0x'+ecall(1,TELLER,'0x4fb3ccc5')[-40:]  # accountant()
rate=int(ecall(1,acc,'0x679aefce',B),16)/1e8   # getRate()
s_eth=int(ecall(1,V,'0x18160ddd',B),16)/1e8
bo=block_at(10,T); s_op=int(ecall(10,V,'0x18160ddd',hex(bo)) or '0x0',16)/1e8
print('accountant',acc,'rate',rate,'shares ETH',s_eth,'OP',s_op,'total BTC',(s_eth+s_op)*rate)
