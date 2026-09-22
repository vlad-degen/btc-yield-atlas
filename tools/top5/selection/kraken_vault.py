# Kraken Bitcoin Vault (Veda BoringVault "Advanced Strategies BTC", sentoraBTC) size on Ink at snapshot + Morpho loan-manager legs on Ethereum
import sys
from blockat import block_at
from addrinfo import ecall, rpc
VAULT='0x7dee0120739b7ec048b469939efb178adbbb19b2'; ACC='0x4Bb6C416a00561ad6657110b76552c42d55Ff1d6'
INK=57073; T=1789905600
b=block_at(INK,T)
sup=int(ecall(INK,VAULT,'0x18160ddd',hex(b)),16); dec=int(ecall(INK,VAULT,'0x313ce567'),16)
rate=int(ecall(INK,ACC,'0x282a8700',hex(b)),16)  # getRate()
print('Ink block',b,'shares',sup/10**dec,'rate',rate/10**dec,'BTC',sup*rate/10**(2*dec))
bl=int(rpc(INK,'eth_blockNumber',[]),16)
sup2=int(ecall(INK,VAULT,'0x18160ddd'),16); rate2=int(ecall(INK,ACC,'0x282a8700'),16)
print('Ink latest',bl,'shares',sup2/10**dec,'BTC',sup2*rate2/10**(2*dec))
